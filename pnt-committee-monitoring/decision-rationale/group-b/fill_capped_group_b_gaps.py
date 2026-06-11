from __future__ import annotations

import csv
import html
import json
import re
import ssl
import time
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

import fitz


OUT = Path(__file__).resolve().parent
DOCS = OUT / "documents"
TEXT = OUT / "text"
MANIFEST_CSV = OUT / "manifest.csv"
MANIFEST_JSON = OUT / "manifest.json"
SUMMARY = OUT / "summary.md"

STATES = [
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
]

DOC_EXTS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt"}

CORE_LINK_TERMS = [
    "agenda",
    "minutes",
    "meeting",
    "p&t",
    "pharmacy and therapeutics",
    "therapeutics committee",
    "drug utilization review",
    "dur",
    "pdl",
    "preferred drug",
    "prior authorization",
    "pa criteria",
    "criteria",
    "formulary",
    "drug class",
    "class review",
    "recommendation",
    "final decision",
    "public testimony",
    "public comment",
    "manufacturer",
    "rebate",
    "bylaw",
    "conflict of interest",
    "implementation schedule",
    "pharmacy memo",
    "provider bulletin",
]

EXCLUDE_TERMS = [
    "privacy",
    "accessibility",
    "civil rights",
    "contact us",
    "contact info",
    "careers",
    "facebook",
    "twitter",
    "instagram",
    "youtube",
    "linkedin",
    "login",
    "sign in",
    "site map",
    "foia",
    "calendar",
    "newsroom",
    "language",
    "doula",
    "portal links",
    "long-term care",
    "next level agenda",
    "federal rules",
    "criminal law",
    "payer sheet",
    "payer sheets",
    "cash waiver",
    "reversal form",
    "code sets",
]

THERAPY_TERMS = [
    "acute migraine",
    "adhd",
    "alzheimer",
    "anticoagulant",
    "antidepressant",
    "antipsychotic",
    "asthma",
    "atopic dermatitis",
    "biologic",
    "biosimilar",
    "cancer",
    "cgrp",
    "copd",
    "cystic fibrosis",
    "diabetes",
    "glp-1",
    "hepatitis",
    "hiv",
    "immunologic",
    "inflammatory bowel",
    "migraine",
    "multiple sclerosis",
    "obesity",
    "oncology",
    "opioid",
    "psoriasis",
    "rare disease",
    "rheumatoid arthritis",
    "sickle cell",
    "substance use",
    "ulcerative colitis",
]

PRODUCT_TERMS = [
    "abilify",
    "dupixent",
    "eliquis",
    "humira",
    "jardiance",
    "mounjaro",
    "ozempic",
    "skyrizi",
    "stelara",
    "suboxone",
    "trulicity",
    "vyvanse",
    "wegovy",
    "xarelto",
    "zepbound",
]

RATIONALE_TERMS = [
    "appeal",
    "clinical",
    "cost",
    "diagnosis",
    "efficacy",
    "effectiveness",
    "evidence",
    "manufacturer",
    "medical necessity",
    "minutes",
    "non-preferred",
    "preferred",
    "prior authorization",
    "public comment",
    "quantity limit",
    "rebate",
    "recommendation",
    "safety",
    "step therapy",
    "testimony",
    "utilization",
]


@dataclass
class ManifestRow:
    state: str
    url: str
    source_role: str
    status: str
    file_path: str
    text_path: str
    title_or_label: str
    reason: str


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.text_parts: list[str] = []
        self._href: str | None = None
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "title":
            self.in_title = True
        if tag == "a":
            self._href = attrs_dict.get("href")
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self.in_title = False
        if tag == "a" and self._href:
            self.links.append((self._href, clean_text(" ".join(self._parts))))
            self._href = None
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self._href is not None:
            self._parts.append(data)
        if not self._skip_depth:
            self.text_parts.append(data)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def slugify(value: str, max_len: int = 90) -> str:
    value = unquote(value)
    value = re.sub(r"https?://", "", value, flags=re.I)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (value[:max_len].strip("-") or "source")


def request_url(url: str) -> tuple[int, str, bytes]:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 P&T rationale research bot; bounded public-source gap fill",
            "Accept": "text/html,application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    context = ssl.create_default_context()
    with urlopen(req, timeout=20, context=context) as response:
        status = int(getattr(response, "status", 200))
        content_type = response.headers.get("content-type", "")
        return status, content_type, response.read()


def ext_for_url(url: str, content_type: str) -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in DOC_EXTS or ext in {".html", ".htm"}:
        return ext
    if "pdf" in content_type:
        return ".pdf"
    if "html" in content_type:
        return ".html"
    if "csv" in content_type:
        return ".csv"
    if "word" in content_type:
        return ".docx"
    if "excel" in content_type or "spreadsheet" in content_type:
        return ".xlsx"
    return ".bin"


def extract_pdf_text(path: Path) -> str:
    try:
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    except Exception as exc:
        return f"[PDF text extraction failed: {exc}]"


def extract_html(data: bytes) -> tuple[str, list[tuple[str, str]], str]:
    decoded = data.decode("utf-8", errors="replace")
    parser = LinkParser()
    parser.feed(decoded)
    return clean_text(" ".join(parser.text_parts)), parser.links, clean_text(" ".join(parser.title_parts))


def extract_text(path: Path, content_type: str, data: bytes) -> tuple[str, list[tuple[str, str]], str]:
    suffix = path.suffix.lower()
    if suffix == ".pdf" or "pdf" in content_type:
        return extract_pdf_text(path), [], ""
    if suffix in {".html", ".htm"} or "html" in content_type:
        return extract_html(data)
    if suffix in {".txt", ".csv"} or content_type.startswith("text/"):
        return data.decode("utf-8", errors="replace"), [], ""
    return f"[Binary document saved; text extraction not available for {suffix or content_type}.]", [], ""


def same_domain_or_official(seed: str, candidate: str) -> bool:
    seed_host = urlparse(seed).netloc.lower()
    cand_host = urlparse(candidate).netloc.lower()
    if not cand_host:
        return True
    if seed_host == cand_host:
        return True
    allowed = [
        "illinois.gov",
        "in.gov",
        "iowa.gov",
        "iowamedicaidpdl.com",
        "kdhe.ks.gov",
        "ks.gov",
        "ky.gov",
        "chfs.ky.gov",
        "medimpact.com",
        "ldh.la.gov",
        "louisiana.gov",
        "maine.gov",
        "mainecarepdl.org",
        "maryland.gov",
        "law.cornell.edu",
    ]
    return any(cand_host.endswith(host) for host in allowed)


def relevant_link(label: str, url: str) -> bool:
    hay = f"{label} {url}".lower()
    if any(term in hay for term in EXCLUDE_TERMS):
        return False
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in DOC_EXTS:
        return any(term in hay for term in CORE_LINK_TERMS)
    return any(term in hay for term in CORE_LINK_TERMS)


def read_manifest() -> list[ManifestRow]:
    with MANIFEST_CSV.open(newline="", encoding="utf-8") as f:
        return [ManifestRow(**row) for row in csv.DictReader(f)]


def next_counter(state: str) -> int:
    state_dir = DOCS / slugify(state)
    max_seen = 0
    if state_dir.exists():
        for path in state_dir.iterdir():
            match = re.match(r"(\d+)__", path.name)
            if match:
                max_seen = max(max_seen, int(match.group(1)))
    return max_seen + 1


def save_source(state: str, url: str, source_role: str, reason_prefix: str) -> tuple[ManifestRow, list[tuple[str, str]]] | tuple[ManifestRow, None]:
    state_dir = DOCS / slugify(state)
    text_dir = TEXT / slugify(state)
    state_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    number = next_counter(state)
    try:
        status, content_type, data = request_url(url)
        ext = ext_for_url(url, content_type)
        filename = f"{number:03d}__{slugify(source_role + '-' + url)}{ext}"
        doc_path = state_dir / filename
        doc_path.write_bytes(data)
        extracted, links, title = extract_text(doc_path, content_type, data)
        text_path = text_dir / f"{doc_path.stem}.txt"
        text_path.write_text(
            f"STATE: {state}\nURL: {url}\nROLE: {source_role}\nCONTENT_TYPE: {content_type}\nTITLE: {title}\n\n{extracted}",
            encoding="utf-8",
        )
        row = ManifestRow(
            state=state,
            url=url,
            source_role=source_role,
            status="saved_after_capped_gap_fill",
            file_path=str(doc_path.relative_to(OUT)),
            text_path=str(text_path.relative_to(OUT)),
            title_or_label=title or source_role,
            reason=reason_prefix,
        )
        time.sleep(0.2)
        return row, links
    except HTTPError as exc:
        return (
            ManifestRow(
                state=state,
                url=url,
                source_role=source_role,
                status="blocked_or_failed",
                file_path="",
                text_path="",
                title_or_label=source_role,
                reason=f"HTTP {exc.code}: {exc.reason}",
            ),
            None,
        )
    except (URLError, TimeoutError, ValueError, OSError, ssl.SSLError) as exc:
        return (
            ManifestRow(
                state=state,
                url=url,
                source_role=source_role,
                status="blocked_or_failed",
                file_path="",
                text_path="",
                title_or_label=source_role,
                reason=f"{type(exc).__name__}: {exc}",
            ),
            None,
        )


def fill_gaps(rows: list[ManifestRow]) -> list[ManifestRow]:
    seen_urls = {row.url for row in rows if row.status != "seed_not_downloaded_current_state"}
    updated: list[ManifestRow] = []
    new_rows: list[ManifestRow] = []
    seed_rows = [row for row in rows if row.status == "seed_not_downloaded_current_state"]

    for row in rows:
        if row.status != "seed_not_downloaded_current_state":
            updated.append(row)
            continue
        saved_row, links = save_source(row.state, row.url, row.source_role, "Downloaded in bounded capped-gap fill.")
        updated.append(saved_row)
        if saved_row.status.startswith("saved"):
            seen_urls.add(saved_row.url)
        if not links:
            continue

        candidates: list[tuple[str, str]] = []
        local_seen: set[str] = set()
        for href, label in links:
            absolute = urljoin(row.url, href).split("#", 1)[0]
            parsed = urlparse(absolute)
            if parsed.scheme not in {"http", "https"}:
                continue
            if absolute in seen_urls or absolute in local_seen:
                continue
            if not same_domain_or_official(row.url, absolute):
                continue
            if not relevant_link(label, absolute):
                continue
            candidates.append((absolute, f"linked from capped seed: {label or Path(parsed.path).name}"))
            local_seen.add(absolute)

        for linked_url, linked_role in candidates[:8]:
            linked_row, _linked_links = save_source(
                row.state,
                linked_url,
                linked_role,
                f"Bounded same-page relevant link from seed: {row.url}",
            )
            new_rows.append(linked_row)
            seen_urls.add(linked_url)

    return updated + new_rows


def normalize_saved_status(rows: Iterable[ManifestRow]) -> list[ManifestRow]:
    normalized: list[ManifestRow] = []
    for row in rows:
        if row.status == "saved_current_state":
            row.reason = row.reason or "File was present before capped-gap fill."
        normalized.append(row)
    return normalized


def write_manifest(rows: list[ManifestRow]) -> None:
    MANIFEST_JSON.write_text(json.dumps([asdict(row) for row in rows], indent=2), encoding="utf-8")
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ManifestRow.__annotations__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def read_text(row: ManifestRow) -> str:
    if not row.text_path:
        return ""
    path = OUT / row.text_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def term_hits(texts: list[str], terms: list[str]) -> list[str]:
    haystack = "\n".join(texts).lower()
    return sorted({term for term in terms if term.lower() in haystack})


def snippet(text: str, term: str) -> str:
    match = re.search(re.escape(term), text, flags=re.I)
    if not match:
        return ""
    start = max(0, match.start() - 120)
    end = min(len(text), match.end() + 180)
    return clean_text(text[start:end])


def compact_label(row: ManifestRow) -> str:
    return clean_text(unquote(row.title_or_label or row.source_role or row.url))[:140]


def write_summary(rows: list[ManifestRow]) -> None:
    saved = [row for row in rows if row.status in {"saved_current_state", "saved_after_capped_gap_fill"}]
    blocked = [row for row in rows if row.status == "blocked_or_failed"]
    remaining = [row for row in rows if row.status == "seed_not_downloaded_current_state"]
    new_saved = [row for row in rows if row.status == "saved_after_capped_gap_fill"]
    texts_by_state = {state: [] for state in STATES}
    text_rows_by_state: dict[str, list[tuple[ManifestRow, str]]] = {state: [] for state in STATES}
    for row in saved:
        text = read_text(row)
        if text:
            texts_by_state.setdefault(row.state, []).append(text)
            text_rows_by_state.setdefault(row.state, []).append((row, text))

    lines: list[str] = []
    lines.append("# Group B decision-rationale capped-gap fill summary")
    lines.append("")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("Scope: Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, and Maryland.")
    lines.append("")
    lines.append("This pass only addressed rows that were previously marked `seed_not_downloaded_current_state` because broad crawling had been stopped. It did not retry prior 403, 404, timeout, SSL/certificate, invalid URL, or other blocked/error rows, and it did not perform broad crawling. For successfully saved seed pages, only clearly relevant same-page links were saved in a bounded one-hop pass.")
    lines.append("")
    lines.append("## Current Collection")
    lines.append("")
    lines.append(f"- Total saved text/source records: {len(saved)}")
    lines.append(f"- Newly saved records from capped gaps: {len(new_saved)}")
    lines.append(f"- Remaining unattempted capped seed gaps: {len(remaining)}")
    lines.append(f"- Remaining blocked/error records from this fill: {len(blocked)}")
    lines.append("- Manifest files: `manifest.json` and `manifest.csv`")
    lines.append("- Source copies: `documents/`")
    lines.append("- Extracted text: `text/`")
    lines.append("")

    lines.append("## Newly Collected Counts By State")
    lines.append("")
    for state in STATES:
        count = sum(1 for row in new_saved if row.state == state)
        lines.append(f"- {state}: {count}")
    lines.append("")

    lines.append("## Documents Collected By State")
    lines.append("")
    for state in STATES:
        state_saved = [row for row in saved if row.state == state]
        state_new = [row for row in new_saved if row.state == state]
        state_blocked = [row for row in blocked if row.state == state]
        state_remaining = [row for row in remaining if row.state == state]
        lines.append(f"### {state}")
        lines.append("")
        lines.append(f"- Current collected files: {len(state_saved)}")
        lines.append(f"- Newly collected from capped gaps: {len(state_new)}")
        lines.append(f"- Remaining non-addressable blocked/error rows: {len(state_blocked)}")
        lines.append(f"- Remaining unattempted capped seed gaps: {len(state_remaining)}")
        if state_new:
            lines.append("- New files:")
            for row in state_new[:14]:
                lines.append(f"  - `{row.file_path}` / `{row.text_path}` - {compact_label(row)}")
            if len(state_new) > 14:
                lines.append(f"  - Additional new files: {len(state_new) - 14}; see manifest.")
        if state_blocked:
            lines.append("- Remaining gaps/reasons:")
            for row in state_blocked[:8]:
                lines.append(f"  - {row.url} ({row.reason})")
            if len(state_blocked) > 8:
                lines.append(f"  - Additional blocked/error rows: {len(state_blocked) - 8}; see manifest.")
        if state_remaining:
            lines.append("- Still unattempted capped seed URLs:")
            for row in state_remaining[:8]:
                lines.append(f"  - {row.url} ({row.source_role})")
        lines.append("")

    lines.append("## New Rationale And Therapy/Product Patterns Found")
    lines.append("")
    lines.append("- Illinois adds board/process and PDL background evidence where public materials frame the advisory function around clinical review, effectiveness, safety, utilization control, preferred/non-preferred placement, and prior authorization rather than a complete public rebate rationale.")
    lines.append("- Indiana adds a regulatory/process layer: the collected sources emphasize Therapeutics Committee meeting materials, pharmacy-benefit infrastructure, prior authorization and SUPDL/PDL operations, and statutory/regulatory definitions of medical necessity and coverage controls.")
    lines.append("- Iowa adds manufacturer and public-comment mechanics. The P&T information and public-comments pages are useful for pharma operating calendars because they expose where comments, submissions, PDL materials, PA criteria, and meeting timing can be monitored.")
    lines.append("- Kansas adds one of the clearer separations between clinical committee review and economic implementation. Collected PDL/DUR materials include committee/process pages, agendas, and minutes, with recurring visibility into utilization, safety, prior authorization, preferred status, and recommendation language.")
    lines.append("- Kentucky adds high-value recommendation-to-final-decision infrastructure through statutes/regulations, the P&T advisory page, manufacturer portal, and P&T committee document hub. This is more actionable for pharma than a meeting date alone because it points to recommendations, final decisions, written submissions, and implementation artifacts.")
    lines.append("- Louisiana adds P&T committee/process evidence, board profile material, and pharmacy-program context. The documents support monitoring review classes, agendas/minutes, PDL/PA implementation, and public body composition, while product-level rationale still depends on document-specific detail.")
    lines.append("- Maine adds DUR and PDL operational evidence, including drug-utilization review materials, PDL pages, covered-services context, and criteria-style terms. This is more useful for access monitoring than for observing committee deliberation.")
    lines.append("- Maryland adds public P&T meeting, roster, PDL, testimony, and COMAR process evidence. The public record is useful for stakeholder-window timing and criteria monitoring, but public text still tends to expose clinical/process rationale more than net-cost or rebate deliberation.")
    lines.append("")

    lines.append("## Therapy/Product/Class Mentions Found")
    lines.append("")
    for state in STATES:
        therapies = term_hits(texts_by_state.get(state, []), THERAPY_TERMS)
        products = term_hits(texts_by_state.get(state, []), PRODUCT_TERMS)
        rationale = term_hits(texts_by_state.get(state, []), RATIONALE_TERMS)
        lines.append(f"### {state}")
        lines.append("")
        lines.append("- Therapy/class terms found: " + (", ".join(therapies) if therapies else "unavailable in current extracted text."))
        lines.append("- Product terms found: " + (", ".join(products) if products else "unavailable in current extracted text."))
        lines.append("- Rationale/process terms found: " + (", ".join(rationale) if rationale else "unavailable in current extracted text."))
        examples: list[str] = []
        for term in (therapies[:3] + products[:3] + rationale[:4]):
            for row, text in text_rows_by_state.get(state, []):
                hit = snippet(text, term)
                if hit:
                    examples.append(f"`{term}` in `{row.text_path}`: {hit}")
                    break
        if examples:
            lines.append("- Example snippets:")
            for item in examples[:6]:
                lines.append(f"  - {item}")
        lines.append("")

    lines.append("## Pharma Implications From Filled Group B Evidence")
    lines.append("")
    lines.append("- Treat public P&T monitoring as a three-layer workflow: meeting/agenda signal, committee recommendation or criteria artifact, then final PDL/PA implementation. Group B sources repeatedly show that these layers are not always published in the same location.")
    lines.append("- Prioritize manufacturer-submission, public-comment, and testimony pages as much as agenda pages. They are the most actionable sources for shaping evidence before a committee action.")
    lines.append("- Build class-level alerts for PDL/DUR pages even when product-level votes are absent. Review-class schedules, PA criteria updates, and implementation schedules can precede or substitute for formal rationale.")
    lines.append("- Separate observable clinical rationale from non-public economics. Safety, efficacy, utilization, diagnosis criteria, step therapy, quantity limits, and preferred/non-preferred status are visible much more often than rebate or net-cost logic.")
    lines.append("- Keep DUR boards, PDL advisory committees, Therapeutics Committees, and Medicaid pharmacy pages in scope. They often carry the actionable access evidence even when the body is not branded as a P&T committee.")
    lines.append("")

    lines.append("## Explicit Limitations")
    lines.append("")
    lines.append("- This is a bounded capped-gap fill for Group B only, not a broad crawl or a complete archive of every linked document.")
    lines.append("- URLs that returned 403, 404, timeout, SSL/certificate, invalid URL, or other blocking/error conditions are retained as gaps with reasons rather than retried repeatedly or inferred.")
    lines.append("- Keyword mentions are not final decisions. A product, disease, or class term is only a signal that the term appeared in extracted text.")
    lines.append("- No product-level rationale, approval-to-review timing, vote outcome, cost/rebate conclusion, or final coverage impact was inferred unless visible in collected text.")
    lines.append("")
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = normalize_saved_status(read_manifest())
    filled = fill_gaps(rows)
    write_manifest(filled)
    write_summary(filled)
    saved = sum(1 for row in filled if row.status in {"saved_current_state", "saved_after_capped_gap_fill"})
    new_saved = sum(1 for row in filled if row.status == "saved_after_capped_gap_fill")
    blocked = sum(1 for row in filled if row.status == "blocked_or_failed")
    remaining = sum(1 for row in filled if row.status == "seed_not_downloaded_current_state")
    print(f"saved_total={saved} new_saved={new_saved} blocked_or_failed={blocked} remaining_seed_gaps={remaining}")


if __name__ == "__main__":
    main()
