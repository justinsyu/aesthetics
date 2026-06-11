from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "raw"
TEXT_DIR = ROOT / "text"
MANIFEST_CSV = ROOT / "manifest.csv"
MANIFEST_JSON = ROOT / "manifest.json"

CAP_REASON = "Not downloaded before broad crawling was stopped by user request"
FIELDS = [
    "state",
    "url",
    "manifest_status",
    "http_status",
    "content_type",
    "source_role",
    "error_or_gap_reason",
    "raw_path",
    "text_path",
]

DOC_EXT = re.compile(r"\.(pdf|docx?|xlsx?|pptx?)(?:$|[?#])", re.I)
DOWNLOAD_DOC = re.compile(r"/media/\d+/download(?:$|[?#])", re.I)
RELEVANT_DOC = re.compile(
    r"(p&t|p%26t|pharmacy|therapeutic|committee|meeting|agenda|minutes|pac|pdl|"
    r"preferred|prior.?authorization|\bpa\b|drug|dur|formulary|criteria|class|"
    r"clinical|packet|recommend|decision|rationale|guideline|schedule|manual|changes|"
    r"provider|chapter|manufacturer|public.?comment)",
    re.I,
)
SKIP = re.compile(r"(mailto:|tel:|javascript:|#|\.css$|\.js$|\.png$|\.jpg$|\.svg$)", re.I)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.text: list[str] = []
        self._href: str | None = None
        self._label: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            attrs_d = dict(attrs)
            self._href = attrs_d.get("href")
            self._label = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            self.links.append((self._href, " ".join(self._label).strip()))
            self._href = None
            self._label = []

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._href is not None:
            self._label.append(data)


def slugify(value: str, max_len: int = 92) -> str:
    value = urllib.parse.unquote(value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (value or "source")[:max_len].strip("-")


def state_slug(state: str) -> str:
    return slugify(state, 32)


def extension_for(url: str, content_type: str | None, body: bytes) -> str:
    path = urllib.parse.urlsplit(url).path.lower()
    ctype = (content_type or "").lower()
    if path.endswith(".pdf") or body.startswith(b"%PDF"):
        return ".pdf"
    if "html" in ctype or b"<html" in body[:2000].lower():
        return ".html"
    if "json" in ctype:
        return ".json"
    if "text" in ctype:
        return ".txt"
    return ".bin"


def normalize_url(url: str, base: str | None = None) -> str | None:
    if not url or SKIP.search(url):
        return None
    absolute = urllib.parse.urljoin(base or "", html.unescape(url.strip()))
    parts = urllib.parse.urlsplit(absolute)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None
    return urllib.parse.urlunsplit(parts._replace(fragment=""))


def same_registered_domain(left: str, right: str) -> bool:
    lhost = urllib.parse.urlsplit(left).netloc.lower()
    rhost = urllib.parse.urlsplit(right).netloc.lower()
    if lhost == rhost:
        return True
    return ".".join(lhost.split(".")[-2:]) == ".".join(rhost.split(".")[-2:])


def fetch(url: str) -> tuple[str, str, bytes | None, str | None]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 local P&T rationale research",
            "Accept": "text/html,application/pdf,text/plain,application/json,*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return str(resp.status), resp.headers.get("Content-Type", ""), resp.read(), None
    except urllib.error.HTTPError as exc:
        body = exc.read()[:5000] if exc.fp else b""
        return str(exc.code), exc.headers.get("Content-Type", "") if exc.headers else "", body, f"HTTP {exc.code}"
    except Exception as exc:
        return "", "", None, f"{type(exc).__name__}: {exc}"


def output_paths(state: str, url: str, content_type: str, body: bytes) -> tuple[Path, Path, str]:
    url_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    name = Path(urllib.parse.urlsplit(url).path).name or urllib.parse.urlsplit(url).netloc
    ext = extension_for(url, content_type, body)
    stem = f"{state_slug(state)}__{slugify(name)}__{url_hash}"
    return RAW_DIR / state_slug(state) / f"{stem}{ext}", TEXT_DIR / state_slug(state) / f"{stem}.txt", ext


def extract_text(raw_path: Path, ext: str, body: bytes) -> str:
    if ext == ".pdf":
        try:
            doc = fitz.open(raw_path)
            chunks = []
            for page_no, page in enumerate(doc, 1):
                chunks.append(f"\n\n--- Page {page_no} ---\n")
                chunks.append(page.get_text())
            return "".join(chunks).strip()
        except Exception as exc:
            return f"[PDF text extraction failed: {type(exc).__name__}: {exc}]"
    decoded = body.decode("utf-8", errors="replace")
    if ext == ".html":
        parser = LinkParser()
        parser.feed(decoded)
        return re.sub(r"\s+", " ", html.unescape(" ".join(parser.text))).strip()
    return decoded


def save_source(state: str, url: str, source_role: str) -> dict[str, str]:
    (RAW_DIR / state_slug(state)).mkdir(parents=True, exist_ok=True)
    (TEXT_DIR / state_slug(state)).mkdir(parents=True, exist_ok=True)
    status, content_type, body, error = fetch(url)
    if error or body is None:
        return {
            "state": state,
            "url": url,
            "manifest_status": "blocked_or_failed",
            "http_status": status,
            "content_type": content_type,
            "source_role": source_role,
            "error_or_gap_reason": error or "No response body",
            "raw_path": "",
            "text_path": "",
        }

    raw_path, text_path, ext = output_paths(state, url, content_type, body)
    raw_path.write_bytes(body)
    text = extract_text(raw_path, ext, body)
    text_path.write_text(
        f"STATE: {state}\nURL: {url}\nSTATUS: {status}\nCONTENT_TYPE: {content_type}\n"
        f"SOURCE_ROLE: {source_role}\n\n{text}\n",
        encoding="utf-8",
    )
    return {
        "state": state,
        "url": url,
        "manifest_status": "collected",
        "http_status": status,
        "content_type": content_type,
        "source_role": source_role,
        "error_or_gap_reason": "",
        "raw_path": str(raw_path.relative_to(ROOT)).replace("\\", "/"),
        "text_path": str(text_path.relative_to(ROOT)).replace("\\", "/"),
    }


def obvious_same_page_documents(seed_url: str, body: bytes, content_type: str) -> list[str]:
    if "html" not in content_type.lower() and b"<html" not in body[:2000].lower():
        return []
    parser = LinkParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    found: list[str] = []
    seen: set[str] = set()
    for href, label in parser.links:
        normalized = normalize_url(href, seed_url)
        if not normalized or normalized in seen:
            continue
        haystack = f"{urllib.parse.unquote(normalized)} {label}"
        if not same_registered_domain(normalized, seed_url):
            continue
        if (DOC_EXT.search(normalized) or DOWNLOAD_DOC.search(normalized)) and RELEVANT_DOC.search(haystack):
            seen.add(normalized)
            found.append(normalized)
        if len(found) >= 15:
            break
    return found


def main() -> None:
    rows = list(csv.DictReader(MANIFEST_CSV.open(newline="", encoding="utf-8-sig")))
    existing_urls = {r["url"] for r in rows}
    targets = [
        r
        for r in rows
        if r["manifest_status"] == "uncollected_seed_gap"
        and CAP_REASON in r["error_or_gap_reason"]
    ]
    collected_seed_pages = [
        r
        for r in rows
        if r["manifest_status"] == "collected"
        and r["state"] == "West Virginia"
        and r["url"] == "https://bms.wv.gov/pharmaceutical-and-therapeutics-pt-committee-meetings"
        and r["raw_path"]
    ]

    replacements: dict[str, dict[str, str]] = {}
    additions: list[dict[str, str]] = []

    for target in targets:
        result = save_source(target["state"], target["url"], target["source_role"])
        replacements[target["url"]] = result

        if result["manifest_status"] != "collected" or not result["raw_path"]:
            continue
        raw_path = ROOT / result["raw_path"]
        body = raw_path.read_bytes()
        for linked_url in obvious_same_page_documents(target["url"], body, result["content_type"]):
            if linked_url in existing_urls or linked_url in replacements:
                continue
            linked = save_source(target["state"], linked_url, f"same-page document linked from {target['url']}")
            additions.append(linked)
            existing_urls.add(linked_url)

    for target in collected_seed_pages:
        raw_path = ROOT / target["raw_path"]
        if not raw_path.exists():
            continue
        body = raw_path.read_bytes()
        for linked_url in obvious_same_page_documents(target["url"], body, target["content_type"]):
            if linked_url in existing_urls or linked_url in replacements:
                continue
            linked = save_source(target["state"], linked_url, f"same-page document linked from {target['url']}")
            additions.append(linked)
            existing_urls.add(linked_url)

    updated: list[dict[str, str]] = []
    for row in rows:
        updated.append(replacements.get(row["url"], row))
    updated.extend(additions)

    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(updated)
    MANIFEST_JSON.write_text(json.dumps(updated, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({"targets": len(targets), "collected_or_failed": len(replacements), "linked_additions": len(additions)}, indent=2))


if __name__ == "__main__":
    main()
