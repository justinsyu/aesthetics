#!/usr/bin/env python3
"""Build a Cohere-tan slide deck from GLP-1 OpenData and high-value CI outputs."""

from __future__ import annotations

import csv
import html
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated_data"
HIGH_VALUE_GEN = GEN / "high_value_ci"
DECK = ROOT / "slide_deck"
OUT = DECK / "glp1_obesity_opendata_ci_deck.html"
TOTAL_SLIDES = 19


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def money(value: Any) -> str:
    amount = float(value or 0)
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.0f}M"
    return f"${amount:,.0f}"


def number(value: Any) -> str:
    amount = float(value or 0)
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"{amount / 1_000:.0f}K"
    return f"{amount:,.0f}"


def pct(value: Any) -> str:
    if value in (None, ""):
        return "n/a"
    return f"{float(value):+.0f}%"


def cite(num: int) -> str:
    return f'<a class="cite" href="#source-{num}">{num}</a>'


def index_rows(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows if row.get(key)}


def status_label(value: str) -> str:
    return value.replace("_", " ")


def metric_card(value: str, label: str, note: str, tone: str = "") -> str:
    return f"""
    <div class="metric {tone}">
      <div class="num">{esc(value)}</div>
      <div class="label">{esc(label)}</div>
      <p>{esc(note)}</p>
    </div>
    """


def format_bar_value(value_key: str, value: float) -> str:
    if "percent" in value_key or "pct" in value_key:
        return f"{value:+.0f}%"
    if "spending" in value_key:
        return money(value)
    return number(value)


def bar_rows(
    rows: list[dict[str, Any]],
    value_key: str,
    label_key: str,
    sub_key: str | None = None,
    max_rows: int = 8,
) -> str:
    selected = rows[:max_rows]
    max_value = max(float(row.get(value_key) or 0) for row in selected) if selected else 1
    colors = ["lime", "blue", "orange", "pink", "red", "gray", "blue", "orange"]
    parts: list[str] = []
    for idx, row in enumerate(selected):
        value = float(row.get(value_key) or 0)
        width = max(4, (value / max_value) * 100)
        sub = esc(row.get(sub_key, "")) if sub_key else ""
        parts.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{esc(row.get(label_key))}</div>
              <div>
                <div class="track"><div class="bar {colors[idx % len(colors)]}" style="width:{width:.1f}%"></div></div>
                <div class="bar-note"><span>{sub}</span><span>{esc(row.get('dataset_label', ''))}</span></div>
              </div>
              <div class="bar-value">{format_bar_value(value_key, value)}</div>
            </div>
            """
        )
    return "\n".join(parts)


def source_link(label: str, href: str, num: int, note: str) -> str:
    return f"""
    <p id="source-{num}"><strong>{num}. <a href="{esc(href)}">{esc(label)}</a></strong><br />{esc(note)}</p>
    """


def compact_source_card(title: str, count: int, status: str, role: str, tone: str) -> str:
    return f"""
    <div class="mini-card">
      <div><span class="pill {tone}">{esc(status)}</span></div>
      <h3>{esc(title)}</h3>
      <div class="mini-num">{esc(number(count))}</div>
      <p>{esc(role)}</p>
    </div>
    """


def access_gap_card(source_id: str, status: str, category: str, examples: str, template_path: str) -> str:
    return f"""
    <div class="gap-card">
      <div><span class="pill orange">{esc(status_label(status))}</span></div>
      <h3>{esc(source_id)}</h3>
      <p><strong>{esc(category)}</strong> | {esc(examples)}</p>
      <p class="template-note">Template: {esc(template_path)}</p>
    </div>
    """


def evidence_card(title: str, meta: str, detail: str, note: str, tone: str = "lime") -> str:
    return f"""
    <div class="evidence-card">
      <div><span class="pill {esc(tone)}">{esc(meta)}</span></div>
      <h3>{esc(title)}</h3>
      <p>{esc(detail)}</p>
      <p class="evidence-note">{esc(note)}</p>
    </div>
    """


def evidence_row(label: str, value: str, note: str = "") -> str:
    return f"""
    <div class="evidence-row">
      <div class="evidence-label">{esc(label)}</div>
      <div class="evidence-value">{esc(value)}</div>
      <div class="evidence-sub">{esc(note)}</div>
    </div>
    """


def trim_text(value: str, limit: int = 120) -> str:
    text = " ".join((value or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def contains_any(value: str, terms: list[str]) -> bool:
    haystack = (value or "").lower().replace("-", "")
    return any(term.lower().replace("-", "") in haystack for term in terms)


def parse_us_date(value: str) -> datetime:
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return datetime.min


def parse_month_day_year(value: str) -> datetime:
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return datetime.min


def sponsor_bucket(value: str) -> str:
    sponsor = value or "Other"
    lower = sponsor.lower()
    if "eli lilly" in lower:
        return "Lilly"
    if "novo nordisk" in lower:
        return "Novo"
    if "innovent" in lower:
        return "Innovent"
    if "boehringer" in lower:
        return "Boehringer"
    if "chia tai" in lower:
        return "Chia Tai"
    return sponsor.split(",")[0][:22]


def example_sources(config: dict[str, Any], source_id: str) -> str:
    for spec in config.get("gated_ingestion_specs", []):
        if spec.get("id") == source_id:
            return ", ".join(spec.get("example_sources", [])[:5])
    return ""


def slide_num(num: int) -> str:
    return f'<div class="slide-num">{num:02d} / {TOTAL_SLIDES:02d}</div>'


def main() -> int:
    manifest = read_json(GEN / "run_manifest.json")
    validation = read_json(GEN / "refresh_validation_report.json")
    summary = read_json(GEN / "product_signal_summary.json")
    coverage = read_csv(GEN / "source_coverage_matrix.csv")
    deltas = read_csv(GEN / "signal_delta_summary.csv")
    high_value_config = read_json(ROOT / "config" / "high_value_ci_sources.json")
    high_value_manifest = read_json(HIGH_VALUE_GEN / "run_manifest.json")
    high_value_collection = read_csv(HIGH_VALUE_GEN / "collection_summary.csv")
    high_value_inventory = read_csv(HIGH_VALUE_GEN / "source_inventory.csv")
    manual_validation = read_csv(HIGH_VALUE_GEN / "manual_ingest_validation.csv")
    clinical_trials = read_csv(HIGH_VALUE_GEN / "clinicaltrials_gov.csv")
    pubmed_rows = read_csv(HIGH_VALUE_GEN / "pubmed_literature.csv")
    dailymed_rows = read_csv(HIGH_VALUE_GEN / "dailymed_labels.csv")
    sec_rows = read_csv(HIGH_VALUE_GEN / "sec_edgar_submissions.csv")
    pricing_rows = read_csv(HIGH_VALUE_GEN / "public_pricing_opendata_extract.csv")
    enforcement_rows = read_csv(HIGH_VALUE_GEN / "fda_drug_enforcement.csv")
    faers_rows = read_csv(HIGH_VALUE_GEN / "fda_faers_quarterly.csv")
    state_pdl_rows = read_csv(HIGH_VALUE_GEN / "state_medicaid_pdl_public_registry.csv")
    patentsview_rows = read_csv(HIGH_VALUE_GEN / "patentsview_uspto.csv")
    cms_formulary_rows = read_csv(HIGH_VALUE_GEN / "cms_partd_formulary_puf.csv")

    source_by_dataset = {row["dataset_id"]: row for row in coverage}
    high_value_by_source = index_rows(high_value_collection, "source_id")
    high_value_inventory_by_source = index_rows(high_value_inventory, "source_id")

    partd_source = source_by_dataset["cms/part-d-spending"]["source_url"]
    medicaid_source = source_by_dataset["cms/medicaid-spending"]["source_url"]
    ndc_source = source_by_dataset["fda/ndc-directory"]["source_url"]
    shortage_source = source_by_dataset["fda/drug-shortages"]["source_url"]
    opendata_docs = "https://tryopendata.ai/docs"
    fda_glp1_supply_context = "https://www.fda.gov/drugs/drug-alerts-and-statements/fda-clarifies-policies-compounders-national-glp-1-supply-begins-stabilize"

    scanned = [row for row in coverage if row["source_scan_status"] == "scanned"]
    total_rows_scanned = sum(int(row["rows_scanned"] or 0) for row in scanned)
    total_lexical_matches = sum(int(row["lexical_match_records"] or 0) for row in scanned)
    total_unique_rows = sum(int(row["unique_matched_source_rows"] or 0) for row in scanned)
    source_url_not_scanned = [row for row in coverage if row["source_url"] and row["source_scan_status"] == "not_scanned"]
    scan_all_sources = bool(manifest.get("scan_all_sources"))
    run_scope_label = "Full OpenData execution plus high-value layer" if scan_all_sources else "Default OpenData execution plus high-value layer"
    run_status_copy = (
        "The May 28, 2026 OpenData full run completed every pinned source URL with no source-request errors. A complementary high-value public-source layer was also collected and source-logged."
        if scan_all_sources
        else "The May 28, 2026 default OpenData run completed with no source-request errors. A complementary high-value public-source layer was also collected and source-logged."
    )
    review_gate_copy = (
        f"Validation remains {validation['status']} with no skipped source URLs in the OpenData full execution path; analyst review is still required before external use."
        if scan_all_sources
        else f"Validation remains {validation['status']} because {len(source_url_not_scanned)} pinned source URLs were not scanned in default mode."
    )
    coverage_title = (
        "OpenData baseline completed; high-value public sources collected; gated inputs remain separate"
        if scan_all_sources
        else "OpenData baseline is in default mode; high-value public sources collected; gated inputs remain separate"
    )
    coverage_note = (
        "OpenData full run means every pinned dataset with a source URL was downloaded, parsed, and logged; zero lexical matches are still informative. Credentialed and manual sources are tracked on a separate access slide."
        if scan_all_sources
        else "Metadata-only does not mean source failure; it means the default deck run did not download those source files. Credentialed and manual sources are tracked on a separate access slide."
    )

    payer_rows = [
        row for row in summary
        if row["dataset_id"] in {"cms/part-d-spending", "cms/medicaid-spending"}
        and not str(row["canonical_product"]).startswith("ingredient:")
        and row.get("latest_year_total_spending")
    ]
    payer_rows.sort(key=lambda row: float(row.get("latest_year_total_spending") or 0), reverse=True)
    for row in payer_rows:
        row["dataset_label"] = "Part D" if row["dataset_id"] == "cms/part-d-spending" else "Medicaid"
        row["sub"] = f"{row['latest_year']} | {number(row.get('latest_year_total_claims'))} claims"

    delta_rows = [
        row for row in deltas
        if row["dataset_id"] in {"cms/part-d-spending", "cms/medicaid-spending"}
        and not row["canonical_product"].startswith("ingredient:")
    ]
    delta_rows.sort(key=lambda row: float(row.get("spending_percent_change") or 0), reverse=True)
    for row in delta_rows:
        row["dataset_label"] = "Part D" if row["dataset_id"] == "cms/part-d-spending" else "Medicaid"
        relation = "YoY" if row.get("period_relation") == "strict_yoy" else "Prior observed"
        row["delta_label"] = f"{pct(row.get('spending_percent_change'))} spend | {pct(row.get('claims_percent_change'))} claims | {relation}"

    fda_datasets = ["fda/ndc-directory", "fda/drugs-at-fda", "fda/orange-book", "fda/nme-approvals"]
    fda_unique_by_dataset = {
        dataset: int(source_by_dataset[dataset].get("unique_matched_source_rows") or 0)
        for dataset in fda_datasets
    }
    fda_lexical_by_dataset = {
        dataset: int(source_by_dataset[dataset].get("lexical_match_records") or 0)
        for dataset in fda_datasets
    }
    shortage_rows = [row for row in summary if row["dataset_id"] == "fda/drug-shortages"]
    limited_shortage_rows = [row for row in shortage_rows if int(row.get("current_limited_availability_rows") or 0) > 0]
    watch_shortage_rows = [row for row in shortage_rows if int(row.get("current_limited_availability_rows") or 0) == 0]
    warning_labels = [warning["code"].replace("_", " ") for warning in validation["warnings"]]

    public_high_value_sources = [
        ("clinicaltrials_gov", "ClinicalTrials.gov", "Trial status, phase movement, sponsor positioning, enrollment criteria, outcomes, and comparators.", "lime"),
        ("pubmed_literature", "PubMed", "Publication velocity, tolerability papers, comparative efficacy, author networks, and guideline-adjacent evidence.", "blue"),
        ("dailymed_labels", "DailyMed labels", "Current label language, warnings, dosing, contraindications, and adverse-reaction wording.", "pink"),
        ("sec_edgar_submissions", "SEC EDGAR", "Competitor filings, risk factors, trial updates, launch commentary, and manufacturing disclosures.", "orange"),
        ("public_pricing_opendata_extract", "Public pricing proxy", "OpenData-derived WAC, NADAC, and IRA price benchmark rows; not commercial net price.", "blue"),
        ("fda_drug_enforcement", "FDA enforcement", "OpenFDA recall/enforcement records for manufacturing and supply-watch triage.", "red"),
        ("state_medicaid_pdl_public_registry", "State Medicaid PDL registry", "Fetched official state Medicaid PDL or PA pages where public URLs are configured.", "orange"),
        ("cms_partd_formulary_puf", "CMS Part D formulary PUF", "Status/access record only in this run; nested formulary members were discovered but not parsed.", "lime"),
        ("fda_faers_quarterly", "openFDA FAERS", "Reaction-count reporting patterns for tolerability watchlists; not incidence or causality.", "red"),
        ("patentsview_uspto", "PatentsView / USPTO", "Fallback-only USPTO bulk resources captured; parsed patent intelligence awaits API recovery.", "gray"),
    ]
    high_value_public_cards = "".join(
        compact_source_card(
            title=title,
            count=int(high_value_by_source.get(source_id, {}).get("records") or 0),
            status=status_label(high_value_by_source.get(source_id, {}).get("status") or "not collected"),
            role=role,
            tone=tone,
        )
        for source_id, title, role, tone in public_high_value_sources
    )
    high_value_public_core_cards = "".join(
        compact_source_card(
            title=title,
            count=int(high_value_by_source.get(source_id, {}).get("records") or 0),
            status=status_label(high_value_by_source.get(source_id, {}).get("status") or "not collected"),
            role=role,
            tone=tone,
        )
        for source_id, title, role, tone in public_high_value_sources[:6]
    )
    high_value_public_extension_cards = "".join(
        compact_source_card(
            title=title,
            count=int(high_value_by_source.get(source_id, {}).get("records") or 0),
            status=status_label(high_value_by_source.get(source_id, {}).get("status") or "not collected"),
            role=role,
            tone=tone,
        )
        for source_id, title, role, tone in public_high_value_sources[6:]
    )
    high_value_public_total = sum(int(high_value_by_source.get(source_id, {}).get("records") or 0) for source_id, *_ in public_high_value_sources)
    gated_access_cards = "".join(
        access_gap_card(
            source_id=row["source_id"],
            status=row["status"],
            category=row["category"],
            examples=example_sources(high_value_config, row["source_id"]),
            template_path=f"input_templates/high_value_ci/{row['source_id']}.csv",
        )
        for row in manual_validation
    )
    high_value_public_docs = high_value_inventory_by_source["clinicaltrials_gov"]["documentation_url"]
    cms_formulary_docs = high_value_inventory_by_source["cms_partd_formulary_puf"]["documentation_url"]
    openfda_docs = high_value_inventory_by_source["fda_faers_quarterly"]["documentation_url"]

    observable_terms = [
        "semaglutide", "tirzepatide", "liraglutide", "retatrutide", "orforglipron",
        "cagrisema", "cagrilintide", "survodutide", "pemvidutide", "mazdutide",
        "petrelintide", "maritide", "vk2735", "danuglipron", "met097",
    ]
    active_statuses = {"RECRUITING", "ACTIVE_NOT_RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION"}
    phase_rank = {"PHASE3": 0, "PHASE2; PHASE3": 1, "PHASE2": 2, "PHASE1; PHASE2": 3, "PHASE1": 4, "PHASE4": 5, "NA": 6, "": 7}
    trial_examples = [
        row for row in clinical_trials
        if row.get("overall_status") in active_statuses
        and contains_any(" ".join([row.get("title", ""), row.get("interventions", ""), row.get("lead_sponsor", "")]), observable_terms)
    ]
    trial_examples.sort(key=lambda row: (
        phase_rank.get(row.get("phase", ""), 9),
        row.get("primary_completion_date") or "9999",
        row.get("nct_id", ""),
    ))
    obesity_terms = ["obesity", "overweight", "weight management", "weight loss", "sleep apnea"]
    phase3_active_trials = [
        row for row in clinical_trials
        if row.get("phase") == "PHASE3"
        and row.get("overall_status") in active_statuses
        and contains_any(" ".join([row.get("title", ""), row.get("conditions", ""), row.get("interventions", "")]), obesity_terms)
        and contains_any(" ".join([row.get("title", ""), row.get("interventions", ""), row.get("lead_sponsor", "")]), observable_terms)
    ]
    phase3_sponsors = Counter(sponsor_bucket(row.get("lead_sponsor", "")) for row in phase3_active_trials)
    phase3_summary_rows = (
        evidence_row(
            "Active Phase 3",
            str(len(phase3_active_trials)),
            "Obesity/overweight-adjacent registry rows with observable incretin asset terms.",
        )
        + "".join(
            evidence_row(label, str(count), "Top sponsor split within the active Phase 3 filtered set.")
            for label, count in phase3_sponsors.most_common(5)
        )
    )
    trial_cards = "".join(
        evidence_card(
            title=f"{row.get('phase') or 'phase n/a'} | {row.get('overall_status')}",
            meta=row.get("nct_id", ""),
            detail=trim_text(row.get("title", ""), 126),
            note=f"{row.get('lead_sponsor')} | primary completion {row.get('primary_completion_date') or 'n/a'} | {trim_text(row.get('interventions', ''), 76)}",
            tone="lime",
        )
        for row in trial_examples[:4]
    )
    pubmed_examples = [
        row for row in pubmed_rows
        if contains_any(row.get("title", ""), observable_terms)
    ]
    pubmed_examples.sort(key=lambda row: (row.get("pubdate", ""), row.get("pmid", "")), reverse=True)
    pubmed_cards = "".join(
        evidence_card(
            title=trim_text(row.get("title", ""), 120),
            meta=f"PMID {row.get('pmid', '')}",
            detail=f"{row.get('journal')} | {row.get('pubdate')}",
            note=trim_text(row.get("authors", ""), 96),
            tone="blue",
        )
        for row in pubmed_examples[:6]
    )
    dailymed_examples = sorted(
        dailymed_rows,
        key=lambda row: (parse_month_day_year(row.get("published_date", "")), row.get("query", "")),
        reverse=True,
    )
    dailymed_cards = "".join(
        evidence_card(
            title=row.get("query", ""),
            meta=row.get("published_date", ""),
            detail=trim_text(row.get("title", ""), 120),
            note=f"Set ID {row.get('setid', '')}",
            tone="pink",
        )
        for row in dailymed_examples[:4]
    )
    dailymed_recency_rows = "".join(
        evidence_row(
            row.get("query", ""),
            row.get("published_date", ""),
            trim_text(row.get("title", ""), 84),
        )
        for row in dailymed_examples[:5]
    )
    faers_totals = defaultdict(int)
    faers_top_term: dict[str, tuple[str, int]] = {}
    for row in faers_rows:
        query = row.get("query", "")
        count = int(row.get("report_count") or 0)
        faers_totals[query] += count
        current = faers_top_term.get(query)
        if current is None or count > current[1]:
            faers_top_term[query] = (row.get("reaction_meddra_pt", ""), count)
    faers_total_rows = "".join(
        evidence_row(
            query,
            number(total),
            f"Top term: {faers_top_term.get(query, ('n/a', 0))[0]} ({number(faers_top_term.get(query, ('', 0))[1])}).",
        )
        for query, total in sorted(faers_totals.items(), key=lambda item: item[1], reverse=True)[:5]
    )
    faers_queries = ["Wegovy", "Ozempic", "Mounjaro", "Zepbound"]
    faers_cards = ""
    for query in faers_queries:
        selected = [row for row in faers_rows if row.get("query") == query]
        selected.sort(key=lambda row: int(row.get("report_count") or 0), reverse=True)
        top = selected[:3]
        faers_cards += evidence_card(
            title=query,
            meta="top FAERS terms",
            detail=", ".join(f"{row.get('reaction_meddra_pt')} ({number(row.get('report_count'))})" for row in top),
            note="Spontaneous-report counts only; not incidence or causality.",
            tone="red",
        )
    sec_focus_terms = ["Mounjaro", "Zepbound", "Wegovy", "Orforglipron", "Retatrutide", "semaglutide", "tirzepatide"]
    sec_examples = [
        row for row in sec_rows
        if contains_any(row.get("filing_text_matched_terms", ""), sec_focus_terms)
    ]
    sec_examples.sort(key=lambda row: (row.get("filing_date", ""), row.get("company", ""), row.get("form", "")), reverse=True)
    sec_cards = "".join(
        evidence_card(
            title=f"{row.get('company')} {row.get('form')}",
            meta=row.get("filing_date", ""),
            detail=f"Matched terms: {trim_text(row.get('filing_text_matched_terms', ''), 120)}",
            note=f"Accession {row.get('accession_number')} | text SHA-256 {row.get('filing_text_sha256', '')[:12]}...",
            tone="orange",
        )
        for row in sec_examples[:4]
    )
    pricing_examples = [row for row in pricing_rows if row.get("nadac_per_unit")]
    pricing_examples.sort(key=lambda row: (float(row.get("nadac_per_unit") or 0), row.get("canonical_product", "")), reverse=True)
    pricing_top_rows_html = "".join(
        evidence_row(
            label=row.get("canonical_product", ""),
            value=f"${float(row.get('nadac_per_unit') or 0):,.2f} / {row.get('pricing_unit') or 'unit'}",
            note=f"{row.get('source_dataset_id')} | as of {row.get('as_of_date')} | {row.get('match_term')}",
        )
        for row in pricing_examples[:3]
    )
    pricing_by_product_date: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in pricing_examples:
        pricing_by_product_date[(row.get("canonical_product", ""), row.get("as_of_date", ""))].append(float(row.get("nadac_per_unit") or 0))
    pricing_by_product: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for (product, as_of_date), values in pricing_by_product_date.items():
        if product and as_of_date and values:
            pricing_by_product[product].append((as_of_date, sum(values) / len(values)))
    pricing_moves: list[tuple[str, str, float, str, float, float]] = []
    for product, dated_values in pricing_by_product.items():
        dated_values.sort(key=lambda item: parse_us_date(item[0]))
        if len(dated_values) >= 2:
            first_date, first_value = dated_values[0]
            latest_date, latest_value = dated_values[-1]
            pricing_moves.append((product, first_date, first_value, latest_date, latest_value, latest_value - first_value))
    pricing_moves.sort(key=lambda item: abs(item[5]), reverse=True)
    pricing_movement_rows = "".join(
        evidence_row(
            product,
            f"${first_value:,.2f} -> ${latest_value:,.2f}",
            f"{first_date} to {latest_date}; delta {move:+.2f} per unit proxy.",
        )
        for product, first_date, first_value, latest_date, latest_value, move in pricing_moves[:5]
    )
    ongoing_enforcement = [row for row in enforcement_rows if row.get("status") == "Ongoing"]
    ongoing_enforcement_counts = Counter((row.get("classification") or "Unclassified") for row in ongoing_enforcement)
    enforcement_summary_rows = "".join(
        evidence_row(label, str(count), "Ongoing openFDA drug enforcement records in the collected GLP-1 query set.")
        for label, count in ongoing_enforcement_counts.most_common()
    )
    ongoing_enforcement.sort(key=lambda row: (
        0 if row.get("classification") == "Class I" else 1,
        row.get("recall_initiation_date", ""),
        row.get("recall_number", ""),
    ))
    enforcement_cards = "".join(
        evidence_card(
            title=row.get("brand_name") or row.get("generic_name") or row.get("query", ""),
            meta=f"{row.get('classification')} | {row.get('status')}",
            detail=trim_text(row.get("reason_for_recall", ""), 122),
            note=f"{row.get('recalling_firm')} | initiated {row.get('recall_initiation_date')} | {row.get('recall_number')}",
            tone="red",
        )
        for row in ongoing_enforcement[:4]
    )
    state_pdl_cards = "".join(
        evidence_card(
            title=f"{row.get('state')} | {row.get('program')}",
            meta=row.get("source_status", ""),
            detail=trim_text(row.get("discovered_document_links") or row.get("url", ""), 110),
            note=f"Page bytes {number(row.get('page_bytes'))}; lexical hits require follow-on criteria extraction.",
            tone="orange",
        )
        for row in state_pdl_rows[:2]
    )
    cms_formulary_status_cards = "".join(
        evidence_card(
            title=row.get("catalog_resource_name", "CMS Part D formulary PUF"),
            meta=status_label(row.get("source_status", "")),
            detail=trim_text(row.get("note", ""), 126),
            note=f"Members scanned {row.get('members_scanned')}; parsed formulary rows unavailable in this run.",
            tone="gray",
        )
        for row in cms_formulary_rows[:1]
    )
    patentsview_cards = "".join(
        evidence_card(
            title=row.get("name", ""),
            meta=row.get("dataset", ""),
            detail=trim_text(row.get("note", ""), 118),
            note=f"API attempts {row.get('api_attempts')}; fallback resource URL captured.",
            tone="gray",
        )
        for row in patentsview_rows[:2]
    )

    coverage_rows = "".join(
        f'<div class="cell status">{esc(row["dataset_id"])}</div>'
        f'<div class="cell">{esc(row["priority"])}</div>'
        f'<div class="cell">{esc(row["source_scan_status"])}</div>'
        f'<div class="cell">{esc((row.get("lexical_match_records") or "metadata") + ((" / " + row.get("unique_matched_source_rows")) if row.get("unique_matched_source_rows") else ""))}</div>'
        f'<div class="cell">{esc(row["signal_families"].split(";")[0])}</div>'
        for row in coverage if row["priority"] == "P0"
    )
    limited_shortage_chips = "".join(
        f'<span class="pill red">{esc(row["canonical_product"])}: {esc(row["current_limited_availability_rows"])} limited</span>'
        for row in limited_shortage_rows
    )
    watch_shortage_chips = "".join(
        f'<span class="pill orange">{esc(row["canonical_product"])}: watch / available</span>'
        for row in watch_shortage_rows
    )
    warning_chips = "".join(f'<span class="pill red">{esc(label)}</span>' for label in warning_labels)

    html_text = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>GLP-1 Obesity OpenData CI Execution Results</title>
  <style>
    :root {{
      --ink: #10120f;
      --muted: #5c6257;
      --paper: #f6f1e8;
      --paper-2: #ebe4d6;
      --card: #fffaf0;
      --line: #1b1f17;
      --lime: #d7ff5f;
      --orange: #ffb86b;
      --blue: #b8d8ff;
      --pink: #ffd3e0;
      --gray: #d6d0c2;
      --red: #ff8a76;
      --shadow: 0 18px 48px rgba(16, 18, 15, 0.08);
      --radius: 26px;
      --slide-pad-top: 64px;
      --slide-pad-bottom: 34px;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ scrollbar-width: none; }}
    html::-webkit-scrollbar, body::-webkit-scrollbar {{ display: none; }}
    body {{ margin: 0; background: var(--paper); color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.36; }}
    a {{ color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .cite {{ font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 850; text-decoration: none; }}
    .wrap {{ width: min(1360px, calc(100vw - 48px)); margin: 0 auto; }}
    .slide {{ min-height: 100vh; height: 100vh; display: flex; align-items: flex-start; padding: var(--slide-pad-top) 0 var(--slide-pad-bottom); position: relative; page-break-after: always; break-after: page; overflow: hidden; background: var(--paper); }}
    .slide > * {{ position: relative; z-index: 1; }}
    .slide-bg-img {{ position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; pointer-events: none; user-select: none; }}
    .slide:last-child {{ page-break-after: auto; break-after: auto; }}
    h1 {{ font-size: 82px; line-height: .92; letter-spacing: -0.045em; font-weight: 500; margin: 0; max-width: 1260px; }}
    h2 {{ font-size: 50px; line-height: .98; letter-spacing: -0.04em; font-weight: 500; margin: 0; }}
    h3 {{ margin: 0; font-size: 26px; line-height: 1.05; letter-spacing: -0.03em; font-weight: 550; }}
    p {{ margin: 0; }}
    .eyebrow {{ display: inline-flex; align-items: center; border: 1.4px solid var(--line); padding: 8px 12px; border-radius: 999px; font-size: 14px; font-weight: 850; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 18px; background: var(--lime); }}
    .section-head {{ margin-bottom: 24px; }}
    .section-head p {{ margin-top: 12px; color: var(--muted); font-size: 20px; max-width: 1260px; }}
    .hero-grid {{ display: grid; grid-template-columns: 1.05fr .95fr; gap: 22px; margin-top: 34px; }}
    .panel, .metric, .card {{ border: 1.5px solid var(--line); background: rgba(255,250,240,.84); border-radius: var(--radius); box-shadow: var(--shadow); }}
    .panel {{ overflow: hidden; }}
    .panel.dark {{ background: #11130f; color: var(--paper); }}
    .panel.dark p, .panel.dark .muted {{ color: rgba(246,241,232,.72); }}
    .panel-pad {{ padding: 26px; }}
    .big-copy {{ color: var(--muted); font-size: 26px; line-height: 1.27; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
    .metric {{ padding: 18px; min-height: 145px; }}
    .metric p {{ color: var(--muted); font-size: 14px; margin-top: 9px; line-height: 1.3; }}
    .metric.dark {{ background: #11130f; color: var(--paper); }}
    .metric.dark .label, .metric.dark p {{ color: rgba(246,241,232,.72); }}
    .num {{ font-size: 44px; line-height: .95; font-weight: 600; letter-spacing: -0.05em; }}
    .label {{ margin-top: 10px; font-size: 15px; color: var(--muted); }}
    .card {{ padding: 21px; min-height: 166px; }}
    .card p {{ color: var(--muted); font-size: 16px; margin-top: 10px; }}
    .mini-card, .gap-card {{ border: 1.5px solid var(--line); background: rgba(255,250,240,.88); border-radius: 22px; box-shadow: var(--shadow); padding: 17px; min-height: 176px; }}
    .mini-card h3, .gap-card h3 {{ margin-top: 10px; font-size: 22px; }}
    .mini-card p, .gap-card p {{ color: var(--muted); font-size: 13px; margin-top: 8px; line-height: 1.28; }}
    .mini-num {{ font-size: 38px; line-height: .92; letter-spacing: -0.05em; margin-top: 10px; font-weight: 650; }}
    .evidence-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }}
    .evidence-grid.three {{ grid-template-columns: repeat(3, 1fr); }}
    .evidence-card {{ border: 1.4px solid var(--line); background: rgba(255,250,240,.88); border-radius: 18px; padding: 14px; min-height: 154px; }}
    .evidence-card h3 {{ margin-top: 8px; font-size: 22px; line-height: 1.05; }}
    .evidence-card p {{ color: var(--muted); font-size: 13px; line-height: 1.24; margin-top: 7px; }}
    .evidence-note {{ color: rgba(16,18,15,.58) !important; font-size: 12px !important; }}
    .evidence-list {{ display: grid; gap: 9px; }}
    .evidence-row {{ display: grid; grid-template-columns: 160px 170px 1fr; gap: 12px; align-items: center; border: 1.2px solid rgba(16,18,15,.28); border-radius: 14px; padding: 10px 12px; background: rgba(255,250,240,.78); }}
    .evidence-label {{ font-size: 17px; font-weight: 850; letter-spacing: -0.02em; }}
    .evidence-value {{ font-size: 16px; font-weight: 850; color: var(--ink); }}
    .evidence-sub {{ font-size: 12px; color: var(--muted); }}
    .access-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
    .template-note {{ font-size: 12px !important; color: rgba(16,18,15,.54) !important; }}
    .pill {{ display: inline-block; padding: 5px 9px; border: 1.2px solid var(--line); border-radius: 999px; font-size: 12px; font-weight: 850; letter-spacing: .03em; text-transform: uppercase; margin: 2px 3px 2px 0; white-space: nowrap; background: var(--paper-2); }}
    .pill.lime {{ background: var(--lime); }}
    .pill.orange {{ background: var(--orange); }}
    .pill.blue {{ background: var(--blue); }}
    .pill.pink {{ background: var(--pink); }}
    .pill.red {{ background: var(--red); }}
    .pill.gray {{ background: var(--gray); }}
    .bars {{ display: grid; gap: 14px; }}
    .bar-row {{ display: grid; grid-template-columns: 185px 1fr 118px; gap: 15px; align-items: center; }}
    .bar-label {{ font-size: 18px; font-weight: 850; letter-spacing: -0.02em; }}
    .track {{ position: relative; height: 28px; border: 1px solid rgba(16,18,15,.24); border-radius: 999px; background: rgba(16,18,15,.07); overflow: hidden; }}
    .bar {{ position: absolute; inset: 0 auto 0 0; border-radius: 999px; min-width: 6px; }}
    .lime {{ background: var(--lime); }}
    .orange {{ background: var(--orange); }}
    .blue {{ background: var(--blue); }}
    .pink {{ background: var(--pink); }}
    .gray {{ background: var(--gray); }}
    .red {{ background: var(--red); }}
    .bar-value {{ color: var(--muted); font-size: 16px; font-weight: 850; text-align: right; }}
    .bar-note {{ font-size: 12px; color: var(--muted); margin-top: 5px; display: flex; justify-content: space-between; gap: 10px; }}
    .table {{ display: grid; border: 1.4px solid var(--line); border-radius: 20px; overflow: hidden; background: var(--card); }}
    .table.cols-5 {{ grid-template-columns: 1.2fr .65fr .75fr .75fr 1.1fr; }}
    .cell {{ padding: 9px 11px; border-right: 1px solid rgba(16,18,15,.25); border-bottom: 1px solid rgba(16,18,15,.2); font-size: 13px; min-height: 36px; }}
    .cell:nth-child(5n) {{ border-right: 0; }}
    .head {{ background: #11130f; color: var(--paper); font-weight: 850; text-transform: uppercase; letter-spacing: .04em; font-size: 11px; }}
    .status {{ font-weight: 850; }}
    .source-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px 28px; font-size: 14px; color: var(--muted); }}
    .source-list p {{ break-inside: avoid; }}
    .source-list strong {{ color: var(--ink); }}
    .note {{ margin-top: 12px; font-size: 13px; color: var(--muted); }}
    .callout {{ border-left: 8px solid var(--orange); padding: 14px 0 14px 20px; color: var(--muted); font-size: 22px; line-height: 1.28; }}
    .slide-num {{ position: absolute; right: 40px; bottom: 28px; font-size: 11px; letter-spacing: .16em; text-transform: uppercase; color: rgba(16,18,15,.38); font-weight: 800; }}
    @media print {{
      @page {{ size: 1600px 900px; margin: 0; }}
      body, *, *::before, *::after {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
      .slide {{ width: 1600px; height: 900px; min-height: 900px; padding: var(--slide-pad-top) 0 var(--slide-pad-bottom); box-shadow: none; }}
      .wrap {{ width: 1360px; }}
      .panel, .metric, .card, .mini-card, .gap-card {{ box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="eyebrow">{esc(run_scope_label)}</div>
      <h1>GLP-1 obesity competitive intelligence refresh results</h1>
      <div class="hero-grid">
        <div class="panel panel-pad"><p class="big-copy">A deterministic refresh workflow now converts OpenData source files, high-value public collectors, product matching rules, and validation checks into traceable candidate intelligence for obesity-relevant GLP-1 products.{cite(1)}{cite(2)}{cite(8)}</p></div>
        <div class="panel dark panel-pad"><h3>Run status</h3><p class="big-copy">{esc(run_status_copy)}{cite(2)}{cite(8)}</p></div>
      </div>
    </div>
    {slide_num(1)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Execution coverage</div><h2>The refresh produced a traceable data package, not only a static analysis</h2><p>Counts reflect generated execution artifacts from the current run manifests and validation reports.{cite(2)}{cite(8)}</p></div>
      <div class="grid-4">
        {metric_card(str(validation['checks']['pinned_datasets']), 'OpenData pinned datasets', 'Datasets in the OpenData source inventory')}
        {metric_card(str(len(scanned)), 'OpenData sources scanned', f'{total_rows_scanned:,} upstream rows parsed')}
        {metric_card(str(total_lexical_matches), 'Lexical match records', f'{total_unique_rows} unique matched source rows')}
        {metric_card(number(high_value_public_total), 'High-value public rows', 'Collected or fallback records in the added CI layer')}
      </div>
      <div class="grid-3" style="margin-top:16px">
        <div class="card"><h3>Manifested outputs</h3><p>{len(manifest['outputs'])} OpenData generated files and {len(high_value_manifest['outputs'])} high-value files have output hashes in run manifests.{cite(2)}{cite(8)}</p></div>
        <div class="card"><h3>Review gate</h3><p>{esc(review_gate_copy)} Public high-value outputs are also hypothesis-generating until analyst review.{cite(2)}{cite(8)}</p></div>
        <div class="card"><h3>Credential boundary</h3><p>Claims, commercial PBM policy, gross-to-net pricing, Medicaid PDL, and manufacturing watch inputs remain template-only until source files or credentials are supplied.{cite(8)}</p></div>
      </div>
    </div>
    {slide_num(2)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Source coverage</div><h2>{esc(coverage_title)}</h2><p>The OpenData coverage matrix records refresh mode, parsed rows, and match counts by dataset. High-value sources are separated later in the deck.{cite(2)}</p></div>
      <div class="table cols-5"><div class="cell head">Dataset</div><div class="cell head">Priority</div><div class="cell head">Status</div><div class="cell head">Lexical / unique</div><div class="cell head">Signal role</div>{coverage_rows}</div>
      <p class="note">{esc(coverage_note)}</p>
    </div>
    {slide_num(3)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Public payer screen</div><h2>Latest-year spending signals identify the products dominating public payer exposure</h2><p>CMS Part D and Medicaid annual files are gross public-program spending context, not manufacturer net revenue; rows are candidate source-derived and require analyst review.{cite(3)}{cite(4)}</p></div>
      <div class="panel panel-pad"><div class="bars">{bar_rows(payer_rows, "latest_year_total_spending", "canonical_product", "sub", 8)}</div></div>
    </div>
    {slide_num(4)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Momentum screen</div><h2>Fastest annual public-spend growth is concentrated in obesity and newer incretin brands</h2><p>Percent changes compare the latest annual field against the prior observed annual field; non-consecutive periods are labeled in the bar notes.{cite(3)}{cite(4)}</p></div>
      <div class="panel panel-pad"><div class="bars">{bar_rows(delta_rows, "spending_percent_change", "canonical_product", "delta_label", 7)}</div></div>
      <p class="note">Large percentage increases can reflect low prior-year baselines and should be interpreted with claims, units, and payer-channel context.</p>
    </div>
    {slide_num(5)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Regulatory and lifecycle traceability</div><h2>FDA sources add product identity, NDC, approval, and Orange Book context to payer signals</h2><p>FDA rows are full scanned-source candidate matches used to support product mapping and lifecycle review, not final regulatory interpretation.{cite(5)}</p></div>
      <div class="grid-3">
        {metric_card(str(fda_unique_by_dataset.get('fda/ndc-directory', 0)), 'NDC unique source rows', f"{fda_lexical_by_dataset.get('fda/ndc-directory', 0)} lexical match records", 'dark')}
        {metric_card(str(fda_unique_by_dataset.get('fda/drugs-at-fda', 0)), 'Drugs@FDA unique rows', f"{fda_lexical_by_dataset.get('fda/drugs-at-fda', 0)} lexical match records")}
        {metric_card(str(fda_unique_by_dataset.get('fda/orange-book', 0)), 'Orange Book unique rows', f"{fda_lexical_by_dataset.get('fda/orange-book', 0)} lexical match records")}
      </div>
      <div class="grid-2" style="margin-top:18px">
        <div class="card"><h3>Attribution rule</h3><p>Brand matches take precedence. Ingredient-only records that map to multiple brands remain separately labeled as ambiguous rather than being forced into brand totals.{cite(2)}</p></div>
        <div class="card"><h3>Trace map</h3><p>Every candidate match carries dataset, source URL, source hash, update date, matched field/value, source record identifier, and match-rule version.{cite(2)}</p></div>
      </div>
    </div>
    {slide_num(6)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Supply watch and validation</div><h2>The first run surfaces FDA shortage candidates and explicit execution warnings</h2><p>Supply signals are lexical candidates from FDA shortage data and should be interpreted with FDA's GLP-1 compounding and supply-stabilization context; validation warnings describe execution scope and parser health.{cite(6)}{cite(7)}{cite(2)}</p></div>
      <div class="grid-2">
        <div class="panel panel-pad"><h3>Shortage availability classification</h3><div style="margin-top:18px">{limited_shortage_chips}{watch_shortage_chips}</div><p class="note">Victoza is the only brand-level limited-availability signal in the current matches. Saxenda remains a watch candidate because the matched record is Current / Available.</p></div>
        <div class="panel dark panel-pad"><h3>Validation warnings</h3><div style="margin-top:18px">{warning_chips}</div><p class="note" style="color:rgba(246,241,232,.72)">No source-request errors were recorded; warnings indicate scope limits and review gates rather than failed refresh execution.</p></div>
      </div>
    </div>
    {slide_num(7)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Refresh architecture</div><h2>The workflow is designed to be rerun and audited</h2><p>The package stores data-source provenance, deterministic matching rules, output hashes, and review samples for recurring refreshes.{cite(1)}{cite(2)}{cite(8)}</p></div>
      <div class="grid-4">
        <div class="card"><h3>1. Inventory</h3><p>Pinned OpenData and high-value source registries define source URLs, priorities, signal families, access basis, and refresh cadence.</p></div>
        <div class="card"><h3>2. Retrieve</h3><p>Metadata, columns, source files, public APIs, bounded bulk reads, and fallback resources are logged with source evidence.</p></div>
        <div class="card"><h3>3. Match</h3><p>Versioned product and asset dictionaries support brand-first matching, ambiguous ingredient retention, and row-level trace records.</p></div>
        <div class="card"><h3>4. Validate</h3><p>Coverage matrices, source logs, parser warnings, missing-input flags, match QC samples, and output hashes gate interpretation.</p></div>
      </div>
      <div class="callout" style="margin-top:20px">This makes the deck refreshable: rerun the scripts, rebuild the deck, review warnings, and compare output hashes before interpreting changes.</div>
    </div>
    {slide_num(8)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">High-value public source layer</div><h2>Core public collectors broaden the signal set beyond the OpenData baseline</h2><p>The high-value layer is refreshable and source-logged. Counts are current collected rows, not analyst-validated findings.{cite(8)}{cite(9)}{cite(10)}{cite(11)}</p></div>
      <div class="grid-3">{high_value_public_core_cards}</div>
    </div>
    {slide_num(9)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Public access, pricing, and supply extensions</div><h2>Additional public collectors add formulary, safety, state-policy, and fallback patent context</h2><p>These sources extend the CI layer into public access and supply signals while preserving clear limits around fallback records and fragmented policy evidence.{cite(8)}{cite(10)}{cite(11)}</p></div>
      <div class="grid-4">{high_value_public_extension_cards}</div>
      <p class="note">PatentsView/USPTO remains fallback-only because the PatentSearch API was attempted but did not return parseable patent rows from this environment; state Medicaid PDL pages are registry evidence, not normalized preferred-status determinations.</p>
    </div>
    {slide_num(10)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Actual public data: trial registry</div><h2>ClinicalTrials.gov exposes active competitor programs and near-term readout windows</h2><p>Rows below are selected deterministically from observable title, intervention, sponsor, condition, and phase fields, not from broad query text alone.{cite(8)}{cite(9)}</p></div>
      <div class="grid-2">
        <div><h3>Active Phase 3 screen</h3><div class="evidence-list" style="margin-top:12px">{phase3_summary_rows}</div></div>
        <div><h3>Representative active trial rows</h3><div class="evidence-grid" style="margin-top:12px">{trial_cards}</div></div>
      </div>
    </div>
    {slide_num(11)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Actual public data: literature</div><h2>PubMed metadata surfaces competitor evidence themes and publications to adjudicate</h2><p>These are publication metadata rows from the collected PubMed output; they are not abstract-level effect-size extraction or clinical interpretation.{cite(8)}</p></div>
      <div class="evidence-grid three">{pubmed_cards}</div>
    </div>
    {slide_num(12)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Actual public data: labels and FAERS</div><h2>Label refreshes and adverse-event report counts create safety and message-watch screens</h2><p>DailyMed rows are current label records. FAERS rows are spontaneous-report counts and should not be read as incidence, causality, or comparative safety rates.{cite(8)}{cite(11)}</p></div>
      <div class="grid-2">
        <div><h3>DailyMed label recency</h3><div class="evidence-list" style="margin-top:12px">{dailymed_recency_rows}</div></div>
        <div><h3>openFDA FAERS totals and top terms</h3><div class="evidence-list" style="margin-top:12px">{faers_total_rows}</div><p class="note">Totals sum the collected top reaction-count rows for each query; they are reporting-volume screens only.</p></div>
      </div>
    </div>
    {slide_num(13)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Actual public data: disclosures and price proxies</div><h2>SEC filing text and NADAC rows provide competitor-disclosure and public pricing context</h2><p>SEC examples are filing-text term matches with source hashes. NADAC rows are public acquisition-cost proxies, not manufacturer net price or rebate estimates.{cite(8)}</p></div>
      <div class="grid-2">
        <div><h3>SEC EDGAR filing-text matches</h3><div class="evidence-grid" style="margin-top:12px">{sec_cards}</div></div>
        <div><h3>Public NADAC proxy rows</h3><div class="evidence-list" style="margin-top:12px">{pricing_movement_rows}</div><div class="evidence-list" style="margin-top:12px">{pricing_top_rows_html}</div></div>
      </div>
    </div>
    {slide_num(14)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Actual public data: supply watch</div><h2>FDA enforcement records provide manufacturing and supply triage evidence</h2><p>These rows are openFDA enforcement records in the collected GLP-1 query set. Many records are compounding-linked or product-description matches, not proof of approved-brand supply impact.{cite(8)}{cite(11)}</p></div>
      <div class="grid-2">
        <div><h3>Ongoing enforcement summary</h3><div class="evidence-list" style="margin-top:12px">{enforcement_summary_rows}</div></div>
        <div><h3>Representative ongoing rows</h3><div class="evidence-grid" style="margin-top:12px">{enforcement_cards}</div></div>
      </div>
    </div>
    {slide_num(15)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Actual public data: access and IP status</div><h2>Medicaid registry, formulary, and USPTO rows identify follow-up work rather than final conclusions</h2><p>These rows are status/fallback evidence: state PDL pages were fetched and hashed, CMS nested files were discovered but not parsed, and USPTO fallback resources were captured without parsed patent intelligence.{cite(8)}{cite(10)}</p></div>
      <div class="evidence-grid three">{state_pdl_cards}{cms_formulary_status_cards}{patentsview_cards}</div>
    </div>
    {slide_num(16)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Credential and manual inputs</div><h2>Configured next sources require licenses, credentials, or curated file inputs</h2><p>These categories are configured with templates and validation checks, but they are not represented as collected evidence until source files, licenses, credentials, or documented manual inputs are provided.{cite(8)}</p></div>
      <div class="access-grid">{gated_access_cards}</div>
      <p class="note">Do not read missing-input status as absence of market activity. It is an access boundary: the deck cannot support claims-level demand, commercial access, net price, state Medicaid PDL, or manufacturing readiness conclusions without these inputs.</p>
    </div>
    {slide_num(17)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Analyst next actions</div><h2>Public-data foundation is in place; next additions are access, demand, price, and supply inputs</h2><p>The generated signal briefs label outputs as source-derived candidates requiring analyst review. For a company with an obesity GLP-1 in pipeline, the next gates should prioritize commercial decision signals over more generic open data.{cite(2)}{cite(8)}</p></div>
      <div class="grid-3">
        <div class="card"><h3>Adjudicate matches</h3><p>Review positive-match samples and high-impact rows for brand attribution, false positives, and ingredient-only ambiguity before external use.</p></div>
        <div class="card"><h3>Close market-access gaps</h3><p>Add claims demand, commercial PBM policy, gross-to-net pricing, and Medicaid PDL files because they most directly inform launch planning and payer strategy.</p></div>
        <div class="card"><h3>Monitor public signal changes</h3><p>Refresh clinical trials, labels, FAERS, literature, SEC filings, formulary PUF rows, and USPTO fallback or parsed patent records on the configured cadence.</p></div>
      </div>
      <div class="panel panel-pad" style="margin-top:18px"><h3>Interpretation boundary</h3><p class="big-copy">Current results support structured screening of public payer exposure, momentum, lifecycle mapping, safety watchlists, public formulary rows, and public pipeline context. They do not yet support final access conclusions, net-price estimates, demand forecasts, manufacturing-readiness claims, or launch recommendations without the gated inputs and analyst review.</p></div>
    </div>
    {slide_num(18)}
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Sources</div><h2>Source set and generated evidence base</h2><p>External sources are linked where available; generated artifacts are cited as the deterministic evidence base for run-level counts, validation status, access status, and traceability.</p></div>
      <div class="source-list">
        {source_link('OpenData documentation', opendata_docs, 1, 'Endpoint and catalog basis for metadata, columns, search, and dataset access.')}
        {source_link('Generated OpenData run manifest and validation artifacts', '../generated_data/run_manifest.json', 2, f"Run timestamp {manifest['run_at']}; output hashes, validation warnings, and traceability outputs.")}
        {source_link('CMS Medicare Part D Spending by Drug source file', partd_source, 3, 'Annual Part D drug spending, claims, beneficiaries, and unit metrics.')}
        {source_link('CMS Medicaid Spending by Drug source file', medicaid_source, 4, 'Annual Medicaid drug spending, claims, and unit metrics.')}
        {source_link('FDA National Drug Code Directory source file', ndc_source, 5, 'NDC product identifiers, labelers, routes, dosage forms, and active ingredients.')}
        {source_link('FDA Drug Shortages source file', shortage_source, 6, 'Status and availability fields used for shortage-watch classification.')}
        {source_link('FDA GLP-1 compounding and supply update', fda_glp1_supply_context, 7, 'FDA context on GLP-1 supply stabilization and compounding policies.')}
        {source_link('Generated high-value CI run manifest and methodology', '../generated_data/high_value_ci/run_manifest.json', 8, f"Run timestamp {high_value_manifest['run_at']}; source inventory, gated templates, output hashes, and high-value validation basis.")}
        {source_link('ClinicalTrials.gov API documentation', high_value_public_docs, 9, 'Public trial registry API basis for pipeline records.')}
        {source_link('CMS Part D formulary PUF catalog', cms_formulary_docs, 10, 'Public catalog basis for parsed monthly formulary rows.')}
        {source_link('FDA FAERS documentation', openfda_docs, 11, 'Public adverse-event reporting context; reporting counts are not incidence or causality.')}
      </div>
    </div>
    {slide_num(19)}
  </article>
</body>
</html>
"""
    DECK.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_text, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
