from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import sys
import time
import ssl
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

STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
]
MAX_PER_STATE = 55

RELEVANT = re.compile(
    r"(p&t|p%26t|pharmacy|therapeutic|committee|meeting|agenda|minutes|recommend|"
    r"recommendation|decision|pdl|preferred|prior.?authorization|\bpa\b|drug|dur|"
    r"board|formulary|criteria|class|clinical|handout|packet|monograph|testimony|"
    r"manufacturer|public.?comment|bylaw|policy|procedure|review|memorandum|memo|"
    r"update|notice|limitation|pdf|schedule|material|presentation)",
    re.I,
)
SKIP = re.compile(
    r"(facebook|twitter|linkedin|instagram|youtube|mailto:|tel:|javascript:|#|"
    r"\.jpg$|\.jpeg$|\.png$|\.gif$|\.svg$|\.css$|\.js$)",
    re.I,
)

URL_RE = re.compile(r"https?://[^\s'\"<>\)]+")
SSL_CONTEXT = ssl._create_unverified_context()


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
    absolute = absolute.rstrip("\\")
    parts = urllib.parse.urlsplit(absolute)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/:%")
    query = urllib.parse.quote(urllib.parse.unquote(parts.query), safe="=&?/:;%+")
    parts = parts._replace(path=path, query=query, fragment="")
    return urllib.parse.urlunsplit(parts)


def extension_for(url: str, content_type: str | None, body: bytes) -> str:
    path = urllib.parse.urlsplit(url).path.lower()
    if path.endswith(".pdf") or body.startswith(b"%PDF"):
        return ".pdf"
    if "json" in (content_type or "").lower() or path.endswith(".json"):
        return ".json"
    if "html" in (content_type or "").lower() or b"<html" in body[:2000].lower():
        return ".html"
    if "text" in (content_type or "").lower() or path.endswith(".txt"):
        return ".txt"
    return ".bin"


def fetch(url: str) -> tuple[int | None, str | None, bytes | None, str | None]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 P&T rationale research bot; contact: local research",
            "Accept": "text/html,application/pdf,application/json,text/plain,*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12, context=SSL_CONTEXT) as resp:
            return resp.status, resp.headers.get("Content-Type"), resp.read(), None
    except urllib.error.HTTPError as exc:
        body = exc.read()[:5000] if exc.fp else b""
        return exc.code, exc.headers.get("Content-Type") if exc.headers else None, body, f"HTTP {exc.code}"
    except Exception as exc:
        return None, None, None, f"{type(exc).__name__}: {exc}"


def markdown_links_by_state() -> dict[str, list[str]]:
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


def relevant_link(url: str, label: str, seed_host: str) -> bool:
    parts = urllib.parse.urlsplit(url)
    if parts.netloc and seed_host and parts.netloc != seed_host:
        seed_root = ".".join(seed_host.split(".")[-2:])
        url_root = ".".join(parts.netloc.split(".")[-2:])
        if seed_root != url_root:
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


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    selected_states = [s for s in STATES if len(sys.argv) == 1 or s.lower() in {arg.lower() for arg in sys.argv[1:]}]
    for state in selected_states:
        (RAW_DIR / state_slug(state)).mkdir(parents=True, exist_ok=True)
        (TEXT_DIR / state_slug(state)).mkdir(parents=True, exist_ok=True)

    seeds_by_state = markdown_links_by_state()
    date_links = meeting_date_links_by_state()
    for state, urls in date_links.items():
        seeds_by_state[state].extend(urls)

    manifest: list[dict[str, str | int | None]] = []
    seen_global: set[tuple[str, str]] = set()

    for state in selected_states:
        queue: deque[tuple[str, int, str]] = deque()
        seen_state: set[str] = set()
        for url in dict.fromkeys(seeds_by_state[state]):
            normalized = normalize_url(url)
            if normalized:
                queue.append((normalized, 0, "seed"))

        collected = 0
        while queue and collected < MAX_PER_STATE:
            url, depth, source_role = queue.popleft()
            if url in seen_state:
                continue
            seen_state.add(url)

            status, content_type, body, error = fetch(url)
            url_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
            path_hint = slugify(Path(urllib.parse.urlsplit(url).path).name or urllib.parse.urlsplit(url).netloc)
            ext = extension_for(url, content_type, body or b"") if body else ".error.txt"
            basename = f"{state_slug(state)}__{path_hint}__{url_hash}{ext}"
            raw_path = RAW_DIR / state_slug(state) / basename
            text_path = TEXT_DIR / state_slug(state) / f"{Path(basename).stem}.txt"

            if body is not None:
                raw_path.write_bytes(body)
                extracted = extract_text(raw_path, ext, body)
                text_path.write_text(
                    f"STATE: {state}\\nURL: {url}\\nSTATUS: {status}\\nCONTENT_TYPE: {content_type}\\nSOURCE_ROLE: {source_role}\\n\\n{extracted}\\n",
                    encoding="utf-8",
                    errors="replace",
                )
                collected += 1
            else:
                raw_path.write_text(error or "download failed", encoding="utf-8")
                text_path.write_text(
                    f"STATE: {state}\\nURL: {url}\\nSTATUS: {status}\\nCONTENT_TYPE: {content_type}\\nSOURCE_ROLE: {source_role}\\nERROR: {error}\\n",
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

            if body and depth < 1:
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

            time.sleep(0.05)

    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = ["state", "url", "source_role", "crawl_depth", "status", "content_type", "error", "raw_path", "text_path"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(manifest)

    print(f"manifest_rows={len(manifest)}")
    print(f"successful_downloads={sum(1 for row in manifest if row.get('status') and int(row['status']) < 400)}")
    print(f"states={','.join(selected_states)}")


if __name__ == "__main__":
    main()
