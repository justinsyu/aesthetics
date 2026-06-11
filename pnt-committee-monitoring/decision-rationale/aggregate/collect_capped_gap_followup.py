from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile

import fitz


ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT / "capped-crawl-gap-inventory.json"
OUT = ROOT / "capped-crawl-followup"
RAW = OUT / "raw"
TEXT = OUT / "text"
MANIFEST_JSON = OUT / "manifest.json"
MANIFEST_CSV = OUT / "manifest.csv"
SUMMARY = OUT / "summary.md"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"
TIMEOUT = 35
MAX_DEPTH = 1
MAX_LINKS_PER_SEED = 18
MAX_SUCCESS_PER_STATE = 70

DOC_EXTS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".rtf"}
SKIP_RE = re.compile(
    r"(facebook|twitter|x\.com|linkedin|instagram|youtube|mailto:|tel:|javascript:|"
    r"\.jpg$|\.jpeg$|\.png$|\.gif$|\.svg$|\.css$|\.js$|\.ico$|privacy|accessibility|"
    r"careers|contact-us|contactus|login|sign-in|subscribe|rss|sitemap)",
    re.I,
)
RELEVANT_RE = re.compile(
    r"(p&t|p%26t|pharmacy|therapeutic|committee|advisory|board|meeting|agenda|minutes|"
    r"packet|materials|recommend|recommendation|decision|pdl|preferred|prior.?authorization|"
    r"\bpa\b|criteria|drug|dur|formulary|class|clinical|handout|monograph|testimony|"
    r"manufacturer|public.?comment|bylaw|policy|procedure|review|memo|memorandum|update|"
    r"notice|bulletin|coverage|changes|rationale|rebate|cost|schedule|drug-list|druglist)",
    re.I,
)

THERAPY_TERMS = {
    "diabetes_glp1_obesity": r"\b(diabetes|glp-?1|sglt2|insulin|obesity|weight loss|semaglutide|tirzepatide|ozempic|wegovy|mounjaro|zepbound|trulicity|jardiance|farxiga)\b",
    "immunology_biologics": r"\b(rheumatoid|psoriasis|psoriatic|atopic dermatitis|crohn|ulcerative colitis|ibd|biologic|biosimilar|tnf|humira|stelara|entyvio|skyrizi|rinvoq|cosentyx|taltz|dupixent)\b",
    "oncology_rare_specialty": r"\b(oncology|cancer|leukemia|lymphoma|myeloma|car-?t|hemophilia|sickle cell|cystic fibrosis|rare disease|orphan|gene therapy|cell therapy|trikafta)\b",
    "cns_behavioral_migraine": r"\b(adhd|stimulant|antipsychotic|antidepressant|depression|bipolar|schizophrenia|alzheimer|migraine|cgrp|seizure|epilepsy)\b",
    "oud_pain": r"\b(opioid|opiate|buprenorphine|naloxone|suboxone|sublocade|methadone|pain|analgesic|gabapentin|pregabalin|substance use)\b",
    "respiratory_allergy": r"\b(asthma|copd|respiratory|inhaler|bronchodilator|xolair|tezspire|allergy|cystic fibrosis)\b",
    "infectious_disease": r"\b(hepatitis|hcv|hiv|antiretroviral|prep|antiviral|vaccine|rsv|covid|influenza)\b",
    "cardio_renal_metabolic": r"\b(cardiovascular|heart failure|anticoagulant|hypertension|hyperlipidemia|cholesterol|pcsk9|renal|kidney|pah|attr)\b",
}
RATIONALE_TERMS = {
    "clinical_efficacy_safety": r"\b(efficacy|effective|effectiveness|safety|adverse|clinical|evidence|study|trial|outcome)\b",
    "comparative_class_review": r"\b(therapeutically equivalent|therapeutic alternative|comparative|class review|drug class|preferred agent|non-preferred)\b",
    "pa_step_criteria": r"\b(prior authorization|pa criteria|clinical criteria|step therapy|step edit|trial of|failed|failure|criteria)\b",
    "utilization_controls": r"\b(utilization|quantity limit|dose limit|duration limit|duplicate therapy|prospective dur|retrospective dur)\b",
    "cost_rebate": r"\b(cost|fiscal|budget|rebate|supplemental rebate|net cost|financial|expenditure|savings)\b",
    "public_manufacturer_input": r"\b(public comment|testimony|manufacturer|stakeholder|hearing|speaker|registration|submit comments)\b",
    "final_implementation": r"\b(final decision|approved by|commissioner|director|department|implementation|effective date|claims processing|provider notice)\b",
}


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._in_title = False
        self._skip = 0
        self._href: str | None = None
        self._anchor: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        if tag in {"script", "style", "noscript"}:
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "a" and attrs_d.get("href"):
            self._href = attrs_d["href"]
            self._anchor = []
        if tag in {"p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4"} and not self._skip:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._href:
            self.links.append((self._href, clean(" ".join(self._anchor))))
            self._href = None
            self._anchor = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._href:
            self._anchor.append(data)
        if not self._skip:
            self.text_parts.append(data)

    @property
    def title(self) -> str:
        return clean(" ".join(self.title_parts))

    @property
    def text(self) -> str:
        return clean(" ".join(self.text_parts))


def clean(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s+", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def state_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def slugify(value: str, limit: int = 86) -> str:
    value = urllib.parse.unquote(value)
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._").lower()
    return (value or "source")[:limit].strip("-._")


def normalize(url: str, base: str | None = None) -> str | None:
    url = html.unescape((url or "").strip())
    if not url or SKIP_RE.search(url):
        return None
    absolute = urllib.parse.urljoin(base or "", url)
    parts = urllib.parse.urlsplit(absolute)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None
    quoted_path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/%:@")
    quoted_query = urllib.parse.quote(urllib.parse.unquote(parts.query), safe="=&?/%:@,+")
    return urllib.parse.urlunsplit(parts._replace(path=quoted_path, query=quoted_query, fragment=""))


def same_research_domain(url: str, seed_url: str) -> bool:
    host = urllib.parse.urlsplit(url).netloc.lower()
    seed_host = urllib.parse.urlsplit(seed_url).netloc.lower()
    if host == seed_host:
        return True
    host_root = ".".join(host.split(".")[-2:])
    seed_root = ".".join(seed_host.split(".")[-2:])
    return bool(host_root and seed_root and host_root == seed_root)


def relevant_link(url: str, label: str, seed_url: str) -> bool:
    if not same_research_domain(url, seed_url):
        return False
    haystack = f"{urllib.parse.unquote(url)} {label}"
    return bool(RELEVANT_RE.search(haystack))


def extension_for(url: str, content_type: str | None, body: bytes | None) -> str:
    path = urllib.parse.urlsplit(url).path.lower()
    ext = Path(path).suffix.lower()
    body = body or b""
    ctype = (content_type or "").lower()
    if ext in DOC_EXTS:
        return ext
    if body.startswith(b"%PDF") or "pdf" in ctype:
        return ".pdf"
    if "json" in ctype or path.endswith(".json"):
        return ".json"
    if "html" in ctype or b"<html" in body[:3000].lower():
        return ".html"
    if "csv" in ctype:
        return ".csv"
    if "text" in ctype:
        return ".txt"
    return ".bin"


def fetch(url: str) -> tuple[str, int | None, str, bytes | None, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/pdf,application/json,text/plain,*/*",
        },
    )
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=context) as resp:
            return resp.geturl(), getattr(resp, "status", 200), resp.headers.get("Content-Type", ""), resp.read(), ""
    except urllib.error.HTTPError as exc:
        body = exc.read()[:12000] if exc.fp else b""
        return url, exc.code, exc.headers.get("Content-Type", "") if exc.headers else "", body, f"HTTP {exc.code}"
    except Exception as exc:
        return url, None, "", None, f"{type(exc).__name__}: {exc}"


def extract_text(path: Path, ext: str, body: bytes) -> tuple[str, str, list[tuple[str, str]]]:
    if ext == ".pdf":
        try:
            pieces: list[str] = []
            with fitz.open(path) as doc:
                for idx, page in enumerate(doc, 1):
                    text = page.get_text("text")
                    if text.strip():
                        pieces.append(f"\n\n--- Page {idx} ---\n{text}")
            return clean("\n".join(pieces)), "", []
        except Exception as exc:
            return f"[PDF text extraction failed: {type(exc).__name__}: {exc}]", "", []
    if ext == ".docx":
        try:
            pieces = []
            with ZipFile(path) as zf:
                for name in ["word/document.xml", "word/footnotes.xml", "word/endnotes.xml"]:
                    if name in zf.namelist():
                        xml = zf.read(name).decode("utf-8", "ignore")
                        xml = re.sub(r"<w:tab\s*/>", "\t", xml)
                        xml = re.sub(r"</w:p>", "\n", xml)
                        pieces.append(re.sub(r"<[^>]+>", " ", xml))
            return clean("\n".join(pieces)), "", []
        except Exception as exc:
            return f"[DOCX text extraction failed: {type(exc).__name__}: {exc}]", "", []
    if ext == ".xlsx":
        try:
            pieces = []
            with ZipFile(path) as zf:
                for name in zf.namelist():
                    if name.startswith("xl/worksheets/") or name == "xl/sharedStrings.xml":
                        xml = zf.read(name).decode("utf-8", "ignore")
                        pieces.append(re.sub(r"<[^>]+>", " ", xml))
            return clean("\n".join(pieces)), "", []
        except Exception as exc:
            return f"[XLSX text extraction failed: {type(exc).__name__}: {exc}]", "", []
    decoded = body.decode("utf-8", "replace")
    if ext == ".html":
        parser = Parser()
        parser.feed(decoded)
        return parser.text, parser.title, parser.links
    if ext == ".json":
        try:
            return json.dumps(json.loads(decoded), indent=2, sort_keys=True), "", []
        except Exception:
            return decoded, "", []
    return decoded, "", []


def out_name(state: str, url: str, ext: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    hint = Path(parsed.path).name or parsed.netloc
    if parsed.query:
        hint = f"{hint}-{hashlib.sha1(parsed.query.encode()).hexdigest()[:8]}"
    url_hash = hashlib.sha1(url.encode("utf-8", "ignore")).hexdigest()[:10]
    return f"{state_slug(state)}__{slugify(hint)}__{url_hash}{ext}"


def load_targets() -> list[dict[str, str]]:
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    targets = []
    seen = set()
    for row in data:
        url = normalize(row.get("url", ""))
        status = row.get("status", "")
        if not url or "not_downloaded" not in status and "uncollected" not in status:
            continue
        key = (row.get("group", ""), row.get("state", ""), url)
        if key in seen:
            continue
        seen.add(key)
        targets.append({**row, "url": url})
    return targets


def write_rows(rows: list[dict[str, object]]) -> None:
    fields = [
        "group",
        "state",
        "url",
        "source_role",
        "depth",
        "seed_url",
        "status",
        "http_status",
        "content_type",
        "raw_path",
        "text_path",
        "title",
        "error_or_gap_reason",
        "text_chars",
        "therapy_hits",
        "rationale_hits",
    ]
    MANIFEST_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def hit_keys(text: str, patterns: dict[str, str]) -> list[str]:
    return [key for key, pattern in patterns.items() if re.search(pattern, text, re.I)]


def collect() -> list[dict[str, object]]:
    OUT.mkdir(parents=True, exist_ok=True)
    for folder in [RAW, TEXT]:
        if folder.exists():
            shutil.rmtree(folder)
    RAW.mkdir(parents=True, exist_ok=True)
    TEXT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    queue: deque[dict[str, object]] = deque()
    targets = load_targets()
    for target in targets:
        queue.append({
            "group": target["group"],
            "state": target["state"],
            "url": target["url"],
            "source_role": "capped-crawl seed follow-up",
            "depth": 0,
            "seed_url": target["url"],
        })
    seen_urls: set[str] = set()
    discovered_counts: Counter[str] = Counter()
    success_counts: Counter[str] = Counter()

    while queue:
        item = queue.popleft()
        url = str(item["url"])
        state = str(item["state"])
        seed_url = str(item["seed_url"])
        if url in seen_urls:
            continue
        if success_counts[state] >= MAX_SUCCESS_PER_STATE:
            rows.append({
                **item,
                "status": "skipped_state_success_cap",
                "http_status": "",
                "content_type": "",
                "raw_path": "",
                "text_path": "",
                "title": "",
                "error_or_gap_reason": f"Skipped after {MAX_SUCCESS_PER_STATE} successful follow-up records for {state}.",
                "text_chars": 0,
                "therapy_hits": "",
                "rationale_hits": "",
            })
            continue
        seen_urls.add(url)
        final_url, http_status, content_type, body, error = fetch(url)
        ext = extension_for(final_url, content_type, body) if body is not None and not error else ".error.txt"
        state_dir_raw = RAW / state_slug(state)
        state_dir_text = TEXT / state_slug(state)
        state_dir_raw.mkdir(parents=True, exist_ok=True)
        state_dir_text.mkdir(parents=True, exist_ok=True)
        filename = out_name(state, final_url, ext)
        raw_path = state_dir_raw / filename
        text_path = state_dir_text / f"{Path(filename).stem}.txt"
        title = ""
        text = ""
        links: list[tuple[str, str]] = []

        if body is not None:
            raw_path.write_bytes(body)
            if error:
                text = clean(body.decode("utf-8", "replace")) or error
            else:
                text, title, links = extract_text(raw_path, ext, body)
                success_counts[state] += 1
            text_path.write_text(
                "\n".join([
                    f"STATE: {state}",
                    f"GROUP: {item['group']}",
                    f"URL: {final_url}",
                    f"SEED_URL: {seed_url}",
                    f"SOURCE_ROLE: {item['source_role']}",
                    f"STATUS: {http_status or ''}",
                    f"CONTENT_TYPE: {content_type or ''}",
                    f"TITLE: {title}",
                    "",
                    text,
                ]),
                encoding="utf-8",
                errors="replace",
            )

        therapy = hit_keys(text, THERAPY_TERMS)
        rationale = hit_keys(text, RATIONALE_TERMS)
        row = {
            **item,
            "url": final_url,
            "status": "collected" if body is not None and not error else "failed",
            "http_status": http_status or "",
            "content_type": content_type,
            "raw_path": str(raw_path.relative_to(OUT)).replace("\\", "/") if body is not None else "",
            "text_path": str(text_path.relative_to(OUT)).replace("\\", "/") if body is not None else "",
            "title": title,
            "error_or_gap_reason": error,
            "text_chars": len(text),
            "therapy_hits": "; ".join(therapy),
            "rationale_hits": "; ".join(rationale),
        }
        rows.append(row)
        write_rows(rows)

        if not error and int(item["depth"]) < MAX_DEPTH and links:
            scored: list[tuple[int, str, str]] = []
            for href, label in links:
                link = normalize(href, final_url)
                if not link or link in seen_urls:
                    continue
                if not relevant_link(link, label, seed_url):
                    continue
                lower = f"{urllib.parse.unquote(link)} {label}".lower()
                score = 0
                for term in ["agenda", "minutes", "packet", "criteria", "recommendation", "decision", "pdl", "prior authorization", "public comment", "manufacturer", "rebate", "cost"]:
                    if term in lower:
                        score += 3
                if Path(urllib.parse.urlsplit(link).path).suffix.lower() in DOC_EXTS:
                    score += 5
                scored.append((score, link, label))
            for _, link, label in sorted(scored, reverse=True)[:MAX_LINKS_PER_SEED]:
                key = f"{state}|{seed_url}"
                if discovered_counts[key] >= MAX_LINKS_PER_SEED:
                    break
                discovered_counts[key] += 1
                queue.append({
                    "group": item["group"],
                    "state": state,
                    "url": link,
                    "source_role": f"linked from capped seed: {label or final_url}",
                    "depth": int(item["depth"]) + 1,
                    "seed_url": seed_url,
                })
        time.sleep(0.1)

    write_rows(rows)
    return rows


def summarize(rows: list[dict[str, object]]) -> None:
    by_state = defaultdict(list)
    for row in rows:
        by_state[str(row["state"])].append(row)
    status_counts = Counter(str(row["status"]) for row in rows)
    collected = [row for row in rows if row["status"] == "collected"]
    therapy_counts = Counter()
    rationale_counts = Counter()
    for row in collected:
        for key in str(row.get("therapy_hits", "")).split("; "):
            if key:
                therapy_counts[key] += 1
        for key in str(row.get("rationale_hits", "")).split("; "):
            if key:
                rationale_counts[key] += 1
    lines = [
        "# Targeted Capped-Crawl Follow-Up",
        "",
        f"Generated: {time.strftime('%B %d, %Y')}",
        "",
        "This pass targeted only URLs that prior manifests marked as capped or uncollected seed gaps. It did not intentionally retry earlier 403, 404, timeout, invalid URL, or other access-failure rows.",
        "",
        "## Totals",
        "",
        f"- Manifest rows in this follow-up: {len(rows)}",
        f"- Collected source/text records: {len(collected)}",
        f"- Failed records from targeted capped-gap URLs or first-level links: {status_counts.get('failed', 0)}",
        f"- Skipped by state success cap: {status_counts.get('skipped_state_success_cap', 0)}",
        "",
        "## Collection By State",
        "",
        "| State | Collected | Failed | Therapy hit groups | Rationale hit groups |",
        "|---|---:|---:|---|---|",
    ]
    for state in sorted(by_state):
        state_rows = by_state[state]
        state_collected = [r for r in state_rows if r["status"] == "collected"]
        state_failed = [r for r in state_rows if r["status"] == "failed"]
        t = Counter()
        r = Counter()
        for row in state_collected:
            for key in str(row.get("therapy_hits", "")).split("; "):
                if key:
                    t[key] += 1
            for key in str(row.get("rationale_hits", "")).split("; "):
                if key:
                    r[key] += 1
        lines.append(
            f"| {state} | {len(state_collected)} | {len(state_failed)} | "
            f"{', '.join(k for k, _ in t.most_common(4)) or 'none'} | "
            f"{', '.join(k for k, _ in r.most_common(4)) or 'none'} |"
        )
    lines += [
        "",
        "## Most Frequent Therapy Signals",
        "",
    ]
    for key, count in therapy_counts.most_common():
        lines.append(f"- {key}: {count} collected records")
    lines += [
        "",
        "## Most Frequent Rationale Signals",
        "",
    ]
    for key, count in rationale_counts.most_common():
        lines.append(f"- {key}: {count} collected records")
    lines += [
        "",
        "## Residual Failures",
        "",
    ]
    failed = [row for row in rows if row["status"] == "failed"]
    if failed:
        for row in failed[:80]:
            lines.append(f"- {row['state']}: `{row['url']}` - {row['error_or_gap_reason'] or row['http_status']}")
    else:
        lines.append("- None in this follow-up pass.")
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = collect()
    summarize(rows)


if __name__ == "__main__":
    main()
