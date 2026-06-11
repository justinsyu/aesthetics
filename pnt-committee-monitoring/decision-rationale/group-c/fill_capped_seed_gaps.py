import csv
import json
import re
import time
import urllib.error
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

import collect_group_c as collector


OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
TEXT = OUT / "text"
MANIFEST_CSV = OUT / "manifest.csv"
MANIFEST_JSON = OUT / "manifest.json"
REPORT_JSON = OUT / "gap-fill-report.json"

FIELDS = [
    "state",
    "url",
    "label",
    "seed_type",
    "depth",
    "discovered_from",
    "status",
    "http_status",
    "content_type",
    "raw_path",
    "text_path",
    "title",
    "error",
]

STOPPED_REASON = "Broad crawl stopped per user before this seed URL was downloaded."
MAX_LINKS_PER_SEED_PAGE = 12
MIN_LINK_SCORE = 7


def read_rows():
    with MANIFEST_CSV.open(newline="", encoding="utf-8") as handle:
        return [{field: row.get(field, "") for field in FIELDS} for row in csv.DictReader(handle)]


def write_rows(rows):
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    MANIFEST_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def rel(path):
    return str(path.relative_to(OUT)).replace("\\", "/")


def next_index(rows, state):
    slug = collector.SLUGS[state]
    highest = 0
    for row in rows:
        raw_path = row.get("raw_path") or ""
        match = re.search(rf"{re.escape(slug)}__(\d+)__", raw_path)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def extract_saved_text(ext, raw_path, data):
    title, text, links = "", "", []
    if ext == ".pdf":
        text = collector.extract_pdf(raw_path)
    elif ext == ".docx":
        text = collector.extract_docx(raw_path)
    elif ext in {".html", ".htm", ".txt", ".csv"}:
        parser = collector.Parser()
        parser.feed(data.decode("utf-8", "ignore"))
        title, text, links = parser.title, parser.text, parser.links
        if not text and ext in {".txt", ".csv"}:
            text = collector.clean(data.decode("utf-8", "ignore"))
    return title, text, links


def save_url(row, rows, state, idx):
    final_url, code, ctype, data = collector.fetch(row["url"])
    row["url"], row["http_status"], row["content_type"] = final_url, str(code), ctype
    row["error"] = ""
    ext = collector.ext_for(final_url, ctype)
    name = f"{collector.SLUGS[state]}__{idx:03d}__{collector.slugify(final_url)}"
    if not name.endswith(ext):
        name += ext
    raw_path = RAW / collector.SLUGS[state] / name
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(data)
    row["raw_path"] = rel(raw_path)
    title, text, links = extract_saved_text(ext, raw_path, data)
    row["title"] = title
    if text:
        text_path = TEXT / collector.SLUGS[state] / re.sub(r"\.[^.]+$", ".txt", name)
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(
            f"Source URL: {final_url}\nState: {state}\nLabel: {row.get('label', '')}\n"
            f"Content-Type: {ctype}\nTitle: {title}\n\n{text}\n",
            encoding="utf-8",
        )
        row["text_path"] = rel(text_path)
    else:
        row["text_path"] = ""
        if ext not in {".xlsx", ".xls"}:
            row["error"] = row["error"] or f"saved but no extracted text for {ext}"
        else:
            row["error"] = "saved but no text extractor for spreadsheet"
    row["status"] = "saved"
    return final_url, links


def link_candidates(seed_url, links, seen):
    candidates = []
    seed_host = urllib.parse.urlparse(seed_url).netloc.lower()
    for href, link_text in links:
        next_url = collector.norm(urllib.parse.urljoin(seed_url, href))
        parsed = urllib.parse.urlparse(next_url)
        if parsed.scheme not in {"http", "https"} or next_url in seen:
            continue
        # Keep this bounded to the source page's obvious documents/pages.
        same_host = parsed.netloc.lower() == seed_host
        score = collector.link_score(next_url, link_text)
        path_ext = Path(parsed.path).suffix.lower()
        is_doc = path_ext in collector.DOC_EXT
        if same_host and score >= MIN_LINK_SCORE and (is_doc or score >= 10):
            candidates.append((score, next_url, collector.clean(link_text)[:140]))
    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates[:MAX_LINKS_PER_SEED_PAGE]


def mark_blocked(row, exc):
    row["status"] = "blocked"
    row["raw_path"] = ""
    row["text_path"] = ""
    row["title"] = ""
    row["content_type"] = ""
    if isinstance(exc, urllib.error.HTTPError):
        row["http_status"] = str(exc.code)
    else:
        row["http_status"] = ""
    row["error"] = f"{type(exc).__name__}: {exc}"


def main():
    rows = read_rows()
    targets = [
        (idx, row)
        for idx, row in enumerate(rows)
        if row.get("status") == "uncollected_seed_gap" and STOPPED_REASON in row.get("error", "")
    ]
    seen = {collector.norm(row.get("url", "")) for row in rows if row.get("url")}
    next_by_state = defaultdict(int)
    for state in collector.TARGET_STATES:
        next_by_state[state] = next_index(rows, state)

    report = {
        "attempted_seed_gaps": len(targets),
        "saved_seed_pages": Counter(),
        "blocked_seed_pages": Counter(),
        "saved_same_page_links": Counter(),
        "blocked_same_page_links": Counter(),
        "remaining_gap_reasons": Counter(),
    }

    for _, row in targets:
        state = row["state"]
        idx = next_by_state[state]
        next_by_state[state] += 1
        try:
            final_url, links = save_url(row, rows, state, idx)
            report["saved_seed_pages"][state] += 1
            seen.add(collector.norm(final_url))
            for _, next_url, link_text in link_candidates(final_url, links, seen):
                link_row = {
                    "state": state,
                    "url": next_url,
                    "label": link_text,
                    "seed_type": "same-page-document-link",
                    "depth": "1",
                    "discovered_from": final_url,
                    "status": "",
                    "http_status": "",
                    "content_type": "",
                    "raw_path": "",
                    "text_path": "",
                    "title": "",
                    "error": "",
                }
                seen.add(next_url)
                idx = next_by_state[state]
                next_by_state[state] += 1
                try:
                    save_url(link_row, rows, state, idx)
                    report["saved_same_page_links"][state] += 1
                except Exception as exc:
                    mark_blocked(link_row, exc)
                    report["blocked_same_page_links"][state] += 1
                    report["remaining_gap_reasons"][f"{state}: {link_row['error']}"] += 1
                rows.append(link_row)
                time.sleep(0.15)
        except Exception as exc:
            mark_blocked(row, exc)
            report["blocked_seed_pages"][state] += 1
            report["remaining_gap_reasons"][f"{state}: {row['error']}"] += 1
        write_rows(rows)
        time.sleep(0.2)

    serializable = {
        key: dict(value) if isinstance(value, Counter) else value
        for key, value in report.items()
    }
    REPORT_JSON.write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")
    write_rows(rows)
    print(json.dumps(serializable, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
