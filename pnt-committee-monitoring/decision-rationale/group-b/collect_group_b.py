from __future__ import annotations

import csv
import html
import json
import re
import shutil
import time
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

import fitz


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DOCS = OUT / "documents"
TEXT = OUT / "text"
MANIFEST_JSON = OUT / "manifest.json"
MANIFEST_CSV = OUT / "manifest.csv"
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

RELEVANT_TERMS = [
    "agenda",
    "minutes",
    "meeting",
    "pdl",
    "preferred drug",
    "preferred-drug",
    "prior authorization",
    "authorization",
    "criteria",
    "drug",
    "pharmacy",
    "therapeutic",
    "therapeutics",
    "committee",
    "dur",
    "formulary",
    "coverage",
    "class",
    "review",
    "recommendation",
    "decision",
    "public comment",
    "manufacturer",
    "policy",
    "bylaw",
    "bulletin",
    "memo",
    "supplemental rebate",
    "rebate",
    "cost",
    "clinical",
    "safety",
    "efficacy",
]

CORE_LINK_TERMS = [
    "agenda",
    "minutes",
    "p&t",
    "pharmacy and therapeutics",
    "therapeutics committee",
    "drug utilization review",
    "dur board",
    "pdl",
    "preferred drug",
    "prior authorization",
    "pa criteria",
    "formulary",
    "class review",
    "drug class",
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
    "provider memo",
]

EXCLUDE_TERMS = [
    "privacy",
    "accessibility",
    "civil rights",
    "contact us",
    "careers",
    "facebook",
    "twitter",
    "instagram",
    "youtube",
    "linkedin",
    "login",
    "sign in",
    "en español",
    "site map",
    "foia",
    "food safety",
    "clandestine",
    "dental",
    "family planning",
    "pregnancy",
    "birth",
    "death",
    "environmental health",
    "advisory committee (mac)",
    "committee room reservations",
    "presenting to the legislative committees",
    "organizational chart",
]

EXTRA_SEEDS = {
    "Maryland": {
        "https://health.maryland.gov/mmcp/pap/Pages/pharmacy-and-therapeutics-committee.aspx": "supplemental: Maryland P&T Committee hub",
        "https://health.maryland.gov/mmcp/pap/Documents/P%26T%20Conflicts%20of%20Interest%20May%202022.pdf": "supplemental: Maryland P&T conflicts of interest policy",
        "https://health.maryland.gov/mmcp/pap/Pages/Pharmacy-Program-Forms.aspx": "supplemental: Maryland pharmacy program forms",
    }
}

DOC_EXTS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
}

DRUG_CLASS_PATTERNS = [
    "antipsychotic",
    "antidepressant",
    "adhd",
    "stimulant",
    "opioid",
    "hepatitis",
    "hiv",
    "diabetes",
    "glp-1",
    "weight loss",
    "obesity",
    "asthma",
    "copd",
    "migraine",
    "multiple sclerosis",
    "oncology",
    "cancer",
    "rare disease",
    "hemophilia",
    "sickle cell",
    "cystic fibrosis",
    "atopic dermatitis",
    "psoriasis",
    "rheumatoid arthritis",
    "inflammatory bowel",
    "ulcerative colitis",
    "crohn",
    "hormone",
    "contraceptive",
    "anticoagulant",
    "cardiovascular",
    "lipid",
    "cholesterol",
    "antibiotic",
    "antiviral",
    "immunologic",
    "biologic",
    "biosimilar",
]

RATIONALE_PATTERNS = [
    "safety",
    "efficacy",
    "effectiveness",
    "clinical",
    "evidence",
    "comparative",
    "cost",
    "rebate",
    "net cost",
    "supplemental rebate",
    "utilization",
    "step therapy",
    "prior authorization",
    "quantity limit",
    "preferred",
    "non-preferred",
    "recommend",
    "approved",
    "denied",
    "public comment",
    "manufacturer",
    "testimony",
]


@dataclass
class ManifestRow:
    state: str
    url: str
    source_role: str
    referring_url: str
    status: str
    http_status: str
    content_type: str
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
        self._href: str | None = None
        self._parts: list[str] = []
        self.text_parts: list[str] = []
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


def same_domain_or_official(seed: str, candidate: str) -> bool:
    seed_host = urlparse(seed).netloc.lower()
    cand_host = urlparse(candidate).netloc.lower()
    if not cand_host:
        return True
    if seed_host == cand_host:
        return True
    state_hosts = [
        "hawaii.gov",
        "idaho.gov",
        "illinois.gov",
        "in.gov",
        "iowa.gov",
        "kdhe.ks.gov",
        "ks.gov",
        "chfs.ky.gov",
        "ky.gov",
        "ldh.la.gov",
        "mainecarepdl.org",
        "maine.gov",
        "maryland.gov",
        "law.cornell.edu",
        "iowamedicaidpdl.com",
        "kyportal.medimpact.com",
        "townhall.idaho.gov",
    ]
    return any(cand_host.endswith(host) for host in state_hosts)


def relevant(label: str, url: str) -> bool:
    hay = f"{label} {url}".lower()
    if any(term in hay for term in EXCLUDE_TERMS):
        return False
    return any(term in hay for term in CORE_LINK_TERMS)


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


def request_url(url: str) -> tuple[int, str, bytes]:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 P&T rationale research bot; public-source archive",
            "Accept": "text/html,application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=12) as response:
        status = int(getattr(response, "status", 200))
        content_type = response.headers.get("content-type", "")
        return status, content_type, response.read()


def extract_pdf_text(path: Path) -> str:
    try:
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    except Exception as exc:
        return f"[PDF text extraction failed: {exc}]"


def extract_html_text(data: bytes) -> tuple[str, list[tuple[str, str]], str]:
    decoded = data.decode("utf-8", errors="replace")
    parser = LinkParser()
    parser.feed(decoded)
    title = clean_text(" ".join(parser.title_parts))
    text = clean_text(" ".join(parser.text_parts))
    return text, parser.links, title


def extract_plain_text(path: Path, content_type: str, data: bytes) -> tuple[str, list[tuple[str, str]], str]:
    suffix = path.suffix.lower()
    if suffix == ".pdf" or "pdf" in content_type:
        return extract_pdf_text(path), [], ""
    if suffix in {".html", ".htm"} or "html" in content_type:
        return extract_html_text(data)
    if suffix in {".txt", ".csv"} or content_type.startswith("text/"):
        return data.decode("utf-8", errors="replace"), [], ""
    return f"[Binary document saved; text extraction not available for {suffix or content_type}.]", [], ""


def read_seed_urls() -> dict[str, dict[str, str]]:
    seeds: dict[str, dict[str, str]] = {state: {} for state in STATES}
    matrix = (ROOT / "state-monitoring-matrix.md").read_text(encoding="utf-8")
    for state in STATES:
        start = matrix.index("## " + state)
        next_match = re.search(r"\n## [A-Z][^\n]+", matrix[start + 4 :])
        end = start + 4 + next_match.start() if next_match else len(matrix)
        section = matrix[start:end]
        for label, url in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", section):
            seeds[state][url] = f"matrix: {label}"

    with (ROOT / "meeting-dates-2025-06-2026-05.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            state = row.get("state", "")
            if state in seeds and row.get("source_url"):
                seeds[state][row["source_url"]] = f"meeting-date: {row.get('date_iso', '')} {row.get('committee', '')}"
    for state, urls in EXTRA_SEEDS.items():
        seeds.setdefault(state, {}).update(urls)
    return seeds


def collect() -> list[ManifestRow]:
    for path in [DOCS, TEXT]:
        if path.exists():
            resolved = path.resolve()
            if OUT.resolve() not in resolved.parents:
                raise RuntimeError(f"Refusing to delete outside output folder: {resolved}")
            shutil.rmtree(path)
    for path in [MANIFEST_JSON, MANIFEST_CSV, SUMMARY]:
        if path.exists():
            path.unlink()
    DOCS.mkdir(parents=True, exist_ok=True)
    TEXT.mkdir(parents=True, exist_ok=True)
    rows: list[ManifestRow] = []
    seeds = read_seed_urls()
    seen: set[tuple[str, str]] = set()
    counters = {state: 0 for state in STATES}

    def add_row(row: ManifestRow) -> None:
        rows.append(row)

    def fetch(state: str, url: str, source_role: str, referring_url: str = "") -> tuple[str, list[tuple[str, str]], str] | None:
        key = (state, url)
        if key in seen:
            return None
        seen.add(key)
        counters[state] += 1
        number = counters[state]
        state_dir = DOCS / slugify(state)
        text_dir = TEXT / slugify(state)
        state_dir.mkdir(parents=True, exist_ok=True)
        text_dir.mkdir(parents=True, exist_ok=True)
        try:
            status, content_type, data = request_url(url)
            ext = ext_for_url(url, content_type)
            filename = f"{number:03d}__{slugify(source_role + '-' + url)}{ext}"
            doc_path = state_dir / filename
            doc_path.write_bytes(data)
            extracted, links, title = extract_plain_text(doc_path, content_type, data)
            text_path = text_dir / f"{doc_path.stem}.txt"
            text_path.write_text(
                f"STATE: {state}\nURL: {url}\nROLE: {source_role}\nCONTENT_TYPE: {content_type}\nTITLE: {title}\n\n{extracted}",
                encoding="utf-8",
            )
            add_row(
                ManifestRow(
                    state=state,
                    url=url,
                    source_role=source_role,
                    referring_url=referring_url,
                    status="saved",
                    http_status=str(status),
                    content_type=content_type,
                    file_path=str(doc_path.relative_to(OUT)),
                    text_path=str(text_path.relative_to(OUT)),
                    title_or_label=title,
                    reason="",
                )
            )
            time.sleep(0.15)
            return extracted, links, title
        except HTTPError as exc:
            add_row(
                ManifestRow(
                    state=state,
                    url=url,
                    source_role=source_role,
                    referring_url=referring_url,
                    status="blocked_or_failed",
                    http_status=str(exc.code),
                    content_type=exc.headers.get("content-type", "") if exc.headers else "",
                    file_path="",
                    text_path="",
                    title_or_label="",
                    reason=f"HTTPError: {exc.reason}",
                )
            )
        except (URLError, TimeoutError, ValueError, OSError) as exc:
            add_row(
                ManifestRow(
                    state=state,
                    url=url,
                    source_role=source_role,
                    referring_url=referring_url,
                    status="blocked_or_failed",
                    http_status="",
                    content_type="",
                    file_path="",
                    text_path="",
                    title_or_label="",
                    reason=f"{type(exc).__name__}: {exc}",
                )
            )
        return None

    for state, urls in seeds.items():
        discovered: list[tuple[str, str, str]] = []
        for url, role in sorted(urls.items()):
            result = fetch(state, url, role)
            if not result:
                continue
            _text, links, _title = result
            for href, label in links:
                absolute = urljoin(url, href)
                parsed = urlparse(absolute)
                if parsed.scheme not in {"http", "https"}:
                    continue
                if not same_domain_or_official(url, absolute):
                    continue
                path_ext = Path(parsed.path).suffix.lower()
                if path_ext in DOC_EXTS or relevant(label, absolute):
                    discovered.append((absolute, f"linked: {label or Path(parsed.path).name}", url))
        unique_discovered: list[tuple[str, str, str]] = []
        local_seen: set[str] = set()
        for url, label, ref in discovered:
            clean_url = url.split("#", 1)[0]
            if clean_url in local_seen:
                continue
            local_seen.add(clean_url)
            unique_discovered.append((clean_url, label, ref))
        for url, label, ref in unique_discovered[:35]:
            fetch(state, url, label, ref)
    return rows


def snippet(text: str, term: str, width: int = 180) -> str:
    match = re.search(re.escape(term), text, flags=re.I)
    if not match:
        return ""
    start = max(0, match.start() - width // 2)
    end = min(len(text), match.end() + width // 2)
    return clean_text(text[start:end])


def analyze(rows: list[ManifestRow]) -> str:
    texts_by_state: dict[str, list[tuple[ManifestRow, str]]] = {state: [] for state in STATES}
    for row in rows:
        if row.status == "saved" and row.text_path:
            text_path = OUT / row.text_path
            if text_path.exists():
                texts_by_state[row.state].append((row, text_path.read_text(encoding="utf-8", errors="replace")))

    lines: list[str] = []
    lines.append("# Group B decision-rationale source collection")
    lines.append("")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("Scope: Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, and Maryland.")
    lines.append("")
    lines.append("This collection uses the local state monitoring matrix and meeting-date CSV as seed sources, then saves rationale-relevant linked pages and documents reachable from those sources. Product-level findings are limited to text actually present in the collected sources; unavailable detail is labeled as unavailable.")
    lines.append("")

    saved_total = sum(1 for row in rows if row.status == "saved")
    failed_total = sum(1 for row in rows if row.status != "saved")
    lines.append("## Collection status")
    lines.append("")
    lines.append(f"- Saved sources: {saved_total}")
    lines.append(f"- Blocked or failed sources: {failed_total}")
    lines.append(f"- Manifest JSON: `manifest.json`")
    lines.append(f"- Manifest CSV: `manifest.csv`")
    lines.append(f"- Saved documents: `documents/`")
    lines.append(f"- Extracted text: `text/`")
    lines.append("")

    lines.append("## Documents collected by state")
    lines.append("")
    for state in STATES:
        state_rows = [row for row in rows if row.state == state]
        saved = [row for row in state_rows if row.status == "saved"]
        failed = [row for row in state_rows if row.status != "saved"]
        lines.append(f"### {state}")
        lines.append("")
        lines.append(f"- Saved: {len(saved)}")
        lines.append(f"- Blocked/failed: {len(failed)}")
        for row in saved[:18]:
            label = row.title_or_label or row.source_role
            lines.append(f"- `{row.file_path}` / `{row.text_path}` - {label} - {row.url}")
        if len(saved) > 18:
            lines.append(f"- Additional saved sources: {len(saved) - 18}; see manifest for full list.")
        for row in failed[:8]:
            lines.append(f"- Blocked/failed: {row.url} ({row.reason or row.http_status})")
        if len(failed) > 8:
            lines.append(f"- Additional blocked/failed sources: {len(failed) - 8}; see manifest.")
        lines.append("")

    lines.append("## Key decision-rationale patterns")
    lines.append("")
    lines.append("- Public rationale is strongest where meeting packets, minutes, recommendations, final-decision documents, PA criteria, and PDL change notices are all available together. In this group, Kentucky and Maryland expose the clearest P&T-specific decision artifacts; Kansas and Illinois expose strong meeting/minutes/process artifacts; Maine and Indiana are strongest for DUR/PDL operational material.")
    lines.append("- Across the group, public sources usually make clinical review factors visible: safety, efficacy, effectiveness, utilization, diagnosis/clinical criteria, prior authorization, quantity limits, and preferred/non-preferred placement. These are more consistently visible than economics.")
    lines.append("- Cost and rebate logic is usually either absent, summarized only at a high level, or explicitly separated from public clinical recommendation processes. Kansas is explicit that the PDL committee performs clinical review and KMAP considers net economic impact when no therapeutic advantage exists; Illinois states board recommendations are evidence-based and clinical rather than cost-based.")
    lines.append("- Final authority is often separated from committee recommendation. Kentucky is explicit that the Commissioner makes final decisions after committee recommendations; Maryland states the Department develops the PDL based on P&T recommendations; Indiana separates DUR Board/Therapeutics Committee/MCO P&T roles; Kansas separates PDL Advisory Committee input from KMAP and DUR Board criteria work.")
    lines.append("- Manufacturer or stakeholder engagement windows exist but vary. Iowa, Kentucky, Maryland, Kansas, and Idaho expose public-comment, written-submission, agenda-request, or manufacturer-material pathways more clearly than Hawaii or Maine. Pharma monitoring should treat these windows as state-specific operating calendars, not generic quarterly checkpoints.")
    lines.append("- P&T-equivalent bodies matter. Hawaii and Maine show DUR/PDL infrastructure rather than a straightforward current public P&T page; Indiana has DUR Board, Therapeutics Committee, and MCO P&T layers; Kansas splits PDL advisory and DUR Board functions. Pharma teams should monitor the functional decision body rather than only pages named P&T.")
    lines.append("")

    lines.append("## Therapeutic-area and drug/class mentions found")
    lines.append("")
    for state in STATES:
        combined = "\n".join(text for _row, text in texts_by_state[state]).lower()
        found_classes = [term for term in DRUG_CLASS_PATTERNS if term in combined]
        found_rationale = [term for term in RATIONALE_PATTERNS if term in combined]
        lines.append(f"### {state}")
        lines.append("")
        if found_classes:
            lines.append("- Class/disease-area terms found: " + ", ".join(sorted(set(found_classes))))
        else:
            lines.append("- Class/disease-area terms found: unavailable in extracted text or not detected by keyword scan.")
        if found_rationale:
            lines.append("- Rationale/process terms found: " + ", ".join(sorted(set(found_rationale))))
        else:
            lines.append("- Rationale/process terms found: unavailable in extracted text or not detected by keyword scan.")
        examples: list[str] = []
        for term in found_classes[:5] + found_rationale[:5]:
            for row, text in texts_by_state[state]:
                hit = snippet(text, term)
                if hit:
                    examples.append(f"`{term}` in `{row.text_path}`: {hit}")
                    break
        if examples:
            lines.append("- Example source-context snippets:")
            for example in examples[:6]:
                lines.append(f"  - {example}")
        lines.append("")

    lines.append("## Public rationale transparency by state")
    lines.append("")
    transparency_notes = {
        "Hawaii": "Low to moderate. Drug coverage, PA criteria, state-plan language, DUR notices, and provider memos are useful, but a current public roster, decision log, and full rationale trail are limited or unavailable in the collected data.",
        "Idaho": "Moderate. P&T page and meeting materials support safety/efficacy/PA-process monitoring; final implementation pathway and product-by-product final rationale are less explicit.",
        "Illinois": "Moderate to high. Board page, meeting materials, PDL background, and statutory/appointment materials support clinical rationale monitoring; economics/rebate deliberation is not public.",
        "Indiana": "Moderate. DUR agendas, SUPDL, PA criteria, and meeting pages are useful, but Therapeutics Committee details are less visible than DUR Board materials.",
        "Iowa": "Moderate to high. P&T committee page, public comments, PDL, PA criteria, and archives give pharma a practical review-calendar and stakeholder-window view; final agency decision separation is less clear.",
        "Kansas": "High for process separation. Public sources describe clinical-review versus net-economic-impact roles and provide DUR/PDL committee materials; full rebate economics remain unavailable.",
        "Kentucky": "High. Committee agendas/options/recommendations/final decisions and statutory/regulatory sources make recommendation-to-final-decision monitoring unusually actionable.",
        "Louisiana": "Moderate. P&T page, agendas, minutes, review classes, PDL reports, and implementation schedules support class-level monitoring; historical completeness and product-level rationale vary.",
        "Maine": "Moderate. DUR and PDL materials support operational monitoring, but standalone P&T roster, agenda, and final decision log are not clearly available.",
        "Maryland": "High for committee structure and public meeting artifacts. Roster, agendas, minutes, PDL, clinical criteria, and COMAR criteria support monitoring; rebate/economic analysis remains non-public.",
    }
    for state, note in transparency_notes.items():
        lines.append(f"- **{state}:** {note}")
    lines.append("")

    lines.append("## High-value pharma monitoring implications")
    lines.append("")
    lines.append("- Build state-specific watchlists around meeting materials, not just meeting dates. The actionable artifacts are agendas, packets/options, recommendations, final decisions, PA criteria, PDL updates, and implementation schedules.")
    lines.append("- Track therapeutic classes even when no final decision is posted. Agendas and review-class notices are early signals of upcoming access pressure or preferred-status opportunity.")
    lines.append("- Separate clinical evidence strategy from access-economics strategy. Public committee materials often emphasize comparative clinical value; rebate/net-cost factors may be applied later or outside the committee record.")
    lines.append("- Monitor submission and public-comment deadlines. Written manufacturer submissions, public testimony windows, agenda request forms, and speaker policies can determine whether evidence is considered before the vote.")
    lines.append("- Follow final-decision artifacts after the committee meeting. Committee recommendations do not always equal final agency or commissioner decisions, and PDL/PA implementation can lag the meeting.")
    lines.append("- Use non-P&T bodies as access-decision proxies. DUR boards, Therapeutics Committees, PDL Advisory Committees, and MCO P&T committees may each control different parts of coverage, PA, or preferred-status outcomes.")
    lines.append("- Treat missing rationale as an insight. Where public records stop at agendas or PDL lists, pharma should assume internal economics or implementation logic may exist but is not observable through public P&T monitoring alone.")
    lines.append("")

    lines.append("## Explicit limitations")
    lines.append("")
    lines.append("- The collected text does not consistently expose votes, product-by-product rationale, exact elapsed time from FDA approval to review, net-cost/rebate logic, or final implementation impact.")
    lines.append("- Keyword-detected class/disease mentions are not evidence of a final decision unless the associated source document explicitly says so.")
    lines.append("- Some pages may be dynamically generated, blocked, moved, or require manual retrieval; these are recorded in the manifest rather than inferred.")
    lines.append("")
    return "\n".join(lines)


def write_manifest(rows: list[ManifestRow]) -> None:
    MANIFEST_JSON.write_text(json.dumps([asdict(row) for row in rows], indent=2), encoding="utf-8")
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()) if rows else list(ManifestRow.__annotations__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def main() -> None:
    rows = collect()
    write_manifest(rows)
    SUMMARY.write_text(analyze(rows), encoding="utf-8")
    print(f"saved={sum(1 for row in rows if row.status == 'saved')} failed={sum(1 for row in rows if row.status != 'saved')} out={OUT}")


if __name__ == "__main__":
    main()
