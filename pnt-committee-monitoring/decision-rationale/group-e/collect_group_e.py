from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
MATRIX = PROJECT / "state-monitoring-matrix.md"
DATES = PROJECT / "meeting-dates-2025-06-2026-05.csv"
RAW_DIR = ROOT / "raw"
TEXT_DIR = ROOT / "text"
MANIFEST_JSON = ROOT / "manifest.json"
MANIFEST_CSV = ROOT / "manifest.csv"
MAX_SUCCESSFUL_PER_STATE = 75

STATES = [
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]

RELEVANT = re.compile(
    r"(p&t|p%26t|pharmacy|therapeutic|committee|meeting|agenda|minutes|recommend|"
    r"recommendation|decision|pdl|preferred|prior.?authorization|\bpa\b|drug|dur|"
    r"board|formulary|criteria|class|clinical|handout|packet|monograph|testimony|"
    r"manufacturer|public.?comment|bylaw|policy|procedure|review|memorandum|memo|"
    r"update|notice|limitation|bulletin|coverage|changes|rationale|rebate|cost|"
    r"pdf|schedule|material|presentation|pharmacy-program|prescription-drug)",
    re.I,
)
SKIP = re.compile(
    r"(facebook|twitter|x\.com|linkedin|instagram|youtube|mailto:|tel:|javascript:|#|"
    r"\.jpg$|\.jpeg$|\.png$|\.gif$|\.svg$|\.css$|\.js$|\.ico$)",
    re.I,
)
URL_RE = re.compile(r"https?://[^\s'\"<>\)]+")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            attrs_d = dict(attrs)
            self._href = attrs_d.get("href")
            self._text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            self.links.append((self._href, " ".join(self._text).strip()))
            self._href = None
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)
        self.text.append(data)


def slugify(value: str, max_len: int = 92) -> str:
    value = urllib.parse.unquote(value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (value or "source")[:max_len].strip("-")


def state_slug(state: str) -> str:
    return slugify(state, 32)


def normalize_url(url: str, base: str | None = None) -> str | None:
    if not url:
        return None
    url = html.unescape(url.strip())
    if SKIP.search(url):
        return None
    absolute = urllib.parse.urljoin(base or "", url)
    parts = urllib.parse.urlsplit(absolute)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None
    parts = parts._replace(fragment="")
    return urllib.parse.urlunsplit(parts)


def extension_for(url: str, content_type: str | None, body: bytes) -> str:
    path = urllib.parse.urlsplit(url).path.lower()
    content_type = (content_type or "").lower()
    if path.endswith(".pdf") or body.startswith(b"%PDF"):
        return ".pdf"
    if "json" in content_type or path.endswith(".json"):
        return ".json"
    if "html" in content_type or b"<html" in body[:2000].lower():
        return ".html"
    if "text" in content_type or path.endswith(".txt"):
        return ".txt"
    return ".bin"


def fetch(url: str) -> tuple[int | None, str | None, bytes | None, str | None]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 P&T rationale research bot; local research",
            "Accept": "text/html,application/pdf,application/json,text/plain,*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.status, resp.headers.get("Content-Type"), resp.read(), None
    except urllib.error.HTTPError as exc:
        body = exc.read()[:5000] if exc.fp else b""
        return exc.code, exc.headers.get("Content-Type") if exc.headers else None, body, f"HTTP {exc.code}"
    except Exception as exc:
        return None, None, None, f"{type(exc).__name__}: {exc}"


def matrix_links_by_state() -> dict[str, list[str]]:
    text = MATRIX.read_text(encoding="utf-8")
    out: dict[str, list[str]] = defaultdict(list)
    for state in STATES:
        start = text.find(f"## {state}")
        if start == -1:
            continue
        next_match = re.search(r"\n## [A-Z]", text[start + 1 :])
        section = text[start : start + 1 + next_match.start()] if next_match else text[start:]
        for _, url in re.findall(r"\[([^\]]+)\]\((https?://[^\)]+)\)", section):
            out[state].append(url)
    return out


def meeting_date_links_by_state() -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    with DATES.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            state = row.get("state", "")
            if state in STATES and row.get("source_url"):
                out[state].append(row["source_url"])
    return out


def same_research_domain(url: str, seed_host: str) -> bool:
    host = urllib.parse.urlsplit(url).netloc.lower()
    seed_host = seed_host.lower()
    if host == seed_host:
        return True
    if not host or not seed_host:
        return False
    seed_root = ".".join(seed_host.split(".")[-2:])
    host_root = ".".join(host.split(".")[-2:])
    return seed_root == host_root


def relevant_link(url: str, label: str, seed_host: str) -> bool:
    if not same_research_domain(url, seed_host):
        return False
    haystack = f"{urllib.parse.unquote(url)} {label}"
    return bool(RELEVANT.search(haystack))


def extract_text(path: Path, ext: str, raw: bytes) -> str:
    if ext == ".pdf":
        try:
            doc = fitz.open(path)
            chunks = []
            for i, page in enumerate(doc, 1):
                chunks.append(f"\n\n--- Page {i} ---\n")
                chunks.append(page.get_text())
            return "".join(chunks).strip()
        except Exception as exc:
            return f"[PDF text extraction failed: {type(exc).__name__}: {exc}]"
    if ext == ".html":
        decoded = raw.decode("utf-8", errors="replace")
        parser = LinkParser()
        parser.feed(decoded)
        text = html.unescape(" ".join(parser.text))
        return re.sub(r"\s+", " ", text).strip()
    if ext == ".json":
        decoded = raw.decode("utf-8", errors="replace")
        try:
            return json.dumps(json.loads(decoded), indent=2, sort_keys=True)
        except Exception:
            return decoded
    return raw.decode("utf-8", errors="replace")


def output_name(state: str, url: str, content_type: str | None, body: bytes | None, error: str | None) -> tuple[str, str]:
    url_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    path_hint = slugify(Path(urllib.parse.urlsplit(url).path).name or urllib.parse.urlsplit(url).netloc)
    ext = extension_for(url, content_type, body or b"") if body is not None and error is None else ".error.txt"
    basename = f"{state_slug(state)}__{path_hint}__{url_hash}{ext}"
    return basename, ext


def write_manifest(manifest: list[dict[str, str | int | None]]) -> None:
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = ["state", "url", "source_role", "crawl_depth", "status", "content_type", "error", "raw_path", "text_path"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(manifest)


def existing_downloads() -> dict[str, dict[str, str | int | None]]:
    out: dict[str, dict[str, str | int | None]] = {}
    for text_path in TEXT_DIR.glob("*/*.txt"):
        try:
            header = text_path.read_text(encoding="utf-8", errors="replace")[:2000]
        except OSError:
            continue
        url_match = re.search(r"^URL: (.+)$", header, re.M)
        status_match = re.search(r"^STATUS: (.+)$", header, re.M)
        ctype_match = re.search(r"^CONTENT_TYPE: (.*)$", header, re.M)
        state_match = re.search(r"^STATE: (.+)$", header, re.M)
        if not url_match:
            continue
        raw_candidates = list((RAW_DIR / text_path.parent.name).glob(f"{text_path.stem}.*"))
        out[url_match.group(1)] = {
            "state": state_match.group(1) if state_match else "",
            "url": url_match.group(1),
            "status": int(status_match.group(1)) if status_match and status_match.group(1).isdigit() else None,
            "content_type": ctype_match.group(1) if ctype_match else None,
            "error": None,
            "raw_path": str(raw_candidates[0].relative_to(ROOT)).replace("\\", "/") if raw_candidates else "",
            "text_path": str(text_path.relative_to(ROOT)).replace("\\", "/"),
        }
    return out


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        (RAW_DIR / state_slug(state)).mkdir(parents=True, exist_ok=True)
        (TEXT_DIR / state_slug(state)).mkdir(parents=True, exist_ok=True)

    seeds_by_state = matrix_links_by_state()
    for state, urls in meeting_date_links_by_state().items():
        seeds_by_state[state].extend(urls)

    manifest: list[dict[str, str | int | None]] = []
    existing = existing_downloads()
    seen_global: set[tuple[str, str]] = set()

    for state in STATES:
        queue: deque[tuple[str, int, str]] = deque()
        seen_state: set[str] = set()
        for url in dict.fromkeys(seeds_by_state[state]):
            normalized = normalize_url(url)
            if normalized:
                queue.append((normalized, 0, "seed"))

        collected = 0
        while queue and collected < MAX_SUCCESSFUL_PER_STATE:
            url, depth, source_role = queue.popleft()
            if url in seen_state:
                continue
            seen_state.add(url)

            prior = existing.get(url)
            if prior:
                raw_path = ROOT / str(prior.get("raw_path", ""))
                text_path = ROOT / str(prior.get("text_path", ""))
                status = prior.get("status") if isinstance(prior.get("status"), int) else None
                content_type = str(prior.get("content_type") or "")
                error = None
                body = raw_path.read_bytes() if raw_path.exists() and raw_path.is_file() else None
                ext = raw_path.suffix if raw_path.exists() else ".txt"
            else:
                status, content_type, body, error = fetch(url)
                basename, ext = output_name(state, url, content_type, body, error)
                raw_path = RAW_DIR / state_slug(state) / basename
                text_path = TEXT_DIR / state_slug(state) / f"{Path(basename).stem}.txt"

            if body is not None and error is None and not prior:
                raw_path.write_bytes(body)
                extracted = extract_text(raw_path, ext, body)
                text_path.write_text(
                    f"STATE: {state}\nURL: {url}\nSTATUS: {status}\nCONTENT_TYPE: {content_type}\nSOURCE_ROLE: {source_role}\n\n{extracted}\n",
                    encoding="utf-8",
                    errors="replace",
                )
            elif body is not None and error is None and prior:
                collected += 1
            else:
                raw_path.write_text(error or "download failed", encoding="utf-8")
                text_path.write_text(
                    f"STATE: {state}\nURL: {url}\nSTATUS: {status}\nCONTENT_TYPE: {content_type}\nSOURCE_ROLE: {source_role}\nERROR: {error}\n",
                    encoding="utf-8",
                )

            manifest.append(
                {
                    "state": state,
                    "url": url,
                    "source_role": source_role,
                    "crawl_depth": depth,
                    "status": status,
                    "content_type": content_type,
                    "error": error,
                    "raw_path": str(raw_path.relative_to(ROOT)).replace("\\", "/"),
                    "text_path": str(text_path.relative_to(ROOT)).replace("\\", "/"),
                }
            )

            if body and error is None and depth < 1:
                decoded = body.decode("utf-8", errors="ignore")
                links: list[tuple[str, str]] = []
                if ext == ".html":
                    parser = LinkParser()
                    parser.feed(decoded)
                    links.extend(parser.links)
                for link in URL_RE.findall(decoded):
                    links.append((link, "embedded-url"))

                seed_host = urllib.parse.urlsplit(url).netloc
                for href, label in links:
                    linked = normalize_url(href, url)
                    if not linked or linked in seen_state:
                        continue
                    key = (state, linked)
                    if key in seen_global:
                        continue
                    if relevant_link(linked, label, seed_host):
                        seen_global.add(key)
                        queue.append((linked, depth + 1, f"linked from {url}"))

            time.sleep(0.15)
        write_manifest(manifest)

    write_manifest(manifest)

    by_state: dict[str, int] = defaultdict(int)
    for row in manifest:
        if row.get("status") and int(row["status"]) < 400:
            by_state[str(row["state"])] += 1
    print(f"manifest_rows={len(manifest)}")
    print(f"successful_downloads={sum(by_state.values())}")
    for state in STATES:
        print(f"{state}: {by_state[state]} successful")


if __name__ == "__main__":
    main()
