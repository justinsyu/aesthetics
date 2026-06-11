from __future__ import annotations

import csv
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote


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

THERAPY_TERMS = [
    "acute migraine",
    "adhd",
    "anticoagulant",
    "antidepressant",
    "antipsychotic",
    "asthma",
    "biologic",
    "biosimilar",
    "cancer",
    "cgrp",
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


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


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
    return seeds


def parse_header(text: str) -> dict[str, str]:
    header: dict[str, str] = {}
    for line in text.splitlines()[:8]:
        if ":" in line:
            key, value = line.split(":", 1)
            header[key.strip().lower()] = value.strip()
    return header


def saved_rows() -> list[ManifestRow]:
    rows: list[ManifestRow] = []
    for text_path in sorted(TEXT.glob("*/*.txt")):
        content = text_path.read_text(encoding="utf-8", errors="replace")
        header = parse_header(content)
        state = header.get("state") or text_path.parent.name.title()
        url = header.get("url", "")
        role = header.get("role", "")
        title = header.get("title", "")
        doc_path = ""
        maybe_doc_dir = DOCS / text_path.parent.name
        stem = text_path.stem
        matches = sorted(maybe_doc_dir.glob(stem + ".*"))
        if matches:
            doc_path = str(matches[0].relative_to(OUT))
        rows.append(
            ManifestRow(
                state=state,
                url=url,
                source_role=role,
                status="saved_current_state",
                file_path=doc_path,
                text_path=str(text_path.relative_to(OUT)),
                title_or_label=title or role,
                reason="File was present in group-b at finalization time; no additional download attempted.",
            )
        )
    return rows


def add_uncollected_seed_rows(rows: list[ManifestRow]) -> list[ManifestRow]:
    seeds = read_seed_urls()
    saved_urls = {row.url for row in rows if row.url}
    out = list(rows)
    for state in STATES:
        for url, role in sorted(seeds[state].items()):
            if url in saved_urls:
                continue
            out.append(
                ManifestRow(
                    state=state,
                    url=url,
                    source_role=role,
                    status="seed_not_downloaded_current_state",
                    file_path="",
                    text_path="",
                    title_or_label=role,
                    reason="Seed source was not present in the current group-b document/text folders when broad crawling was stopped.",
                )
            )
    return out


def term_hits(texts: list[str], terms: list[str]) -> list[str]:
    haystack = "\n".join(texts).lower()
    return sorted({term for term in terms if term.lower() in haystack})


def snippet(text: str, term: str) -> str:
    match = re.search(re.escape(term), text, flags=re.I)
    if not match:
        return ""
    start = max(0, match.start() - 120)
    end = min(len(text), match.end() + 180)
    return clean(text[start:end])


def compact_doc_label(row: ManifestRow) -> str:
    label = row.title_or_label or row.source_role or row.url
    label = clean(unquote(label))
    return label[:140]


def write_summary(rows: list[ManifestRow]) -> None:
    saved = [row for row in rows if row.status == "saved_current_state"]
    gaps = [row for row in rows if row.status != "saved_current_state"]
    texts_by_state: dict[str, list[str]] = {state: [] for state in STATES}
    text_rows_by_state: dict[str, list[tuple[ManifestRow, str]]] = {state: [] for state in STATES}
    for row in saved:
        if row.text_path:
            path = OUT / row.text_path
            if path.exists():
                text = path.read_text(encoding="utf-8", errors="replace")
                texts_by_state.setdefault(row.state, []).append(text)
                text_rows_by_state.setdefault(row.state, []).append((row, text))

    lines: list[str] = []
    lines.append("# Group B decision-rationale current-state summary")
    lines.append("")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("Scope: Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, and Maryland.")
    lines.append("")
    lines.append("Broad crawling was stopped by request. This finalizes the current `group-b` folder only: documents and extracted text already present are treated as collected evidence, and seed URLs that are not present are listed as uncollected gaps. No new network downloads were attempted during finalization.")
    lines.append("")
    lines.append("## Current Collection")
    lines.append("")
    lines.append(f"- Collected text files present: {len(saved)}")
    lines.append(f"- Seed URLs not present in current collection: {len(gaps)}")
    lines.append("- Manifest files: `manifest.json` and `manifest.csv`")
    lines.append("- Source copies: `documents/`")
    lines.append("- Extracted text: `text/`")
    lines.append("")

    lines.append("## Documents Collected By State")
    lines.append("")
    for state in STATES:
        state_saved = [row for row in saved if row.state.lower() == state.lower()]
        state_gaps = [row for row in gaps if row.state.lower() == state.lower()]
        lines.append(f"### {state}")
        lines.append("")
        lines.append(f"- Current collected files: {len(state_saved)}")
        lines.append(f"- Seed URLs not downloaded/currently absent: {len(state_gaps)}")
        if state_saved:
            for row in state_saved[:16]:
                lines.append(f"- `{row.file_path}` / `{row.text_path}` - {compact_doc_label(row)}")
            if len(state_saved) > 16:
                lines.append(f"- Additional current collected files: {len(state_saved) - 16}; see manifest.")
        else:
            lines.append("- No source documents are currently present in `group-b` for this state.")
        if state_gaps:
            lines.append("- Uncollected seed URLs:")
            for row in state_gaps[:10]:
                lines.append(f"  - {row.url} ({row.source_role})")
            if len(state_gaps) > 10:
                lines.append(f"  - Additional seed gaps: {len(state_gaps) - 10}; see manifest.")
        lines.append("")

    lines.append("## Extracted Patterns From Current Evidence")
    lines.append("")
    lines.append("- The current collected evidence is Hawaii-heavy because the interrupted rerun left only Hawaii files in the generated folders. Cross-state conclusions should therefore be treated as incomplete until the missing seed URLs are recollected.")
    lines.append("- In the current Hawaii evidence, decision-making signals are more operational than deliberative: state-plan language, DUR meeting notices/agendas, drug coverage pages, PA criteria, dose lists, OTC/formulary pages, provider memos, and plan-summary pages are visible.")
    lines.append("- The strongest rationale fields available in current text are clinical/administrative criteria: diagnosis requirements, prior authorization, preferred/non-preferred status, quantity or dose limits, safety/utilization language, and coverage requirements.")
    lines.append("- Product-by-product deliberation rationale, vote records, comparative evidence summaries, rebate/net-cost logic, and final decision logs are not consistently available in the current collected files.")
    lines.append("- Idaho files currently present add useful process evidence on clinical-evidence review, safety/efficacy, prior authorization requirements, P&T bylaws, drug-class review schedule, and written submissions from pharmaceutical manufacturers.")
    lines.append("- Manufacturer-facing process evidence is limited in the current Hawaii/Idaho evidence. The remaining non-collected seed list indicates likely sources for public testimony, written submissions, P&T recommendations, final decisions, and PA/PDL changes, but those sources are marked as uncollected gaps here.")
    lines.append("")

    lines.append("## Therapy/Product/Class Mentions Found")
    lines.append("")
    for state in STATES:
        therapies = term_hits(texts_by_state.get(state, []), THERAPY_TERMS)
        products = term_hits(texts_by_state.get(state, []), PRODUCT_TERMS)
        rationale = term_hits(texts_by_state.get(state, []), RATIONALE_TERMS)
        lines.append(f"### {state}")
        lines.append("")
        if therapies:
            lines.append("- Therapy/class terms found: " + ", ".join(therapies))
        else:
            lines.append("- Therapy/class terms found: unavailable in current extracted text.")
        if products:
            lines.append("- Product terms found: " + ", ".join(products))
        else:
            lines.append("- Product terms found: unavailable in current extracted text.")
        if rationale:
            lines.append("- Rationale/process terms found: " + ", ".join(rationale))
        else:
            lines.append("- Rationale/process terms found: unavailable in current extracted text.")
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
        if state == "Idaho" and therapies:
            lines.append("- Note: Idaho disease-area keyword hits include terms from general DHW site navigation; use the drug-class schedule and manufacturer-submission files for decision-rationale analysis rather than treating all navigation hits as class-review evidence.")
        lines.append("")

    lines.append("## Pharma Implications From Current State")
    lines.append("")
    lines.append("- Treat PA criteria, dose lists, provider memos, and plan-summary changes as early evidence of access friction even when no formal P&T rationale is public.")
    lines.append("- For Hawaii, current public evidence supports monitoring coverage rules and DUR agenda timing, but not detailed committee deliberation or rebate-driven decision rationale.")
    lines.append("- For Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine, and Maryland, the seed URLs identify high-value sources to recollect: meeting agendas/minutes, class review schedules, manufacturer/public-comment policies, PDL/PA criteria, recommendations, and final-decision artifacts.")
    lines.append("- Once recollected, pharma-facing analysis should separate three layers: clinical rationale visible to committees, stakeholder/manufacturer input windows, and final implementation/economic logic that may sit outside the public record.")
    lines.append("")

    lines.append("## Explicit Limitations")
    lines.append("")
    lines.append("- This summary does not claim complete ten-state coverage; only files currently present under `group-b/documents` and `group-b/text` were analyzed.")
    lines.append("- Seed URLs absent from the current folders are gaps, not evidence that the source lacks relevant data.")
    lines.append("- Keyword mentions are not final decisions. A product, disease, or class term is only a signal that the term appeared in extracted text.")
    lines.append("- No product-level rationale, approval-to-review timing, vote outcome, cost/rebate conclusion, or final coverage impact was inferred unless visible in collected text.")
    lines.append("")
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = add_uncollected_seed_rows(saved_rows())
    MANIFEST_JSON.write_text(json.dumps([asdict(row) for row in rows], indent=2), encoding="utf-8")
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ManifestRow.__annotations__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    write_summary(rows)
    print(f"saved_current={sum(1 for row in rows if row.status == 'saved_current_state')} gaps={sum(1 for row in rows if row.status != 'saved_current_state')}")


if __name__ == "__main__":
    main()
