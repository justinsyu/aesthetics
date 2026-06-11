import csv
import html
import json
import re
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MANIFEST_CSV = OUT / "manifest.csv"
MANIFEST_JSON = OUT / "manifest.json"
SUMMARY = OUT / "summary.md"
GAP_FILL_REPORT = OUT / "gap-fill-report.json"
MATRIX = ROOT / "pnt-committee-monitoring" / "state-monitoring-matrix.md"
MEETINGS = ROOT / "pnt-committee-monitoring" / "meeting-dates-2025-06-2026-05.csv"

STATES = [
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
]
SLUGS = {s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") for s in STATES}
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

THERAPY_PATTERNS = {
    "ADHD / CNS stimulants": r"\b(adhd|attention deficit|stimulants?|amphetamine|methylphenidate|vyvanse|concerta|atomoxetine|guanfacine)\b",
    "Asthma / COPD / respiratory": r"\b(asthma|copd|respiratory|inhaler|bronchodilator|corticosteroid|dupixent|xolair|tezspire)\b",
    "Autoimmune / immunology": r"\b(rheumatoid|psoriasis|psoriatic|atopic dermatitis|crohn|ulcerative colitis|ibd|biologic|jak inhibitor|tnf|humira|stelara|entyvio|skyrizi|rinvoq|cosentyx|taltz)\b",
    "Cardiometabolic / anticoagulation": r"\b(cardiovascular|anticoagulant|doac|hypertension|heart failure|hyperlipidemia|cholesterol|pcsk9|eliquis|xarelto|entresto|repatha|praluent)\b",
    "Diabetes / obesity / GLP-1": r"\b(diabetes|glp-?1|sglt2|insulin|obesity|weight loss|semaglutide|tirzepatide|ozempic|wegovy|mounjaro|zepbound|trulicity|jardiance|farxiga)\b",
    "Hepatitis / HIV / infectious disease": r"\b(hepatitis|hcv|hiv|antiretroviral|prep|antiviral|epclusa|mavyret|biktarvy|descovy|truvada)\b",
    "Migraine / headache": r"\b(migraine|cgrp|gepant|triptan|aimovig|ajovy|emgality|nurtec|ubrelvy|qulipta)\b",
    "Oncology / hematology": r"\b(oncology|cancer|neoplasm|leukemia|lymphoma|myeloma|car-?t|chemotherapy|hemophilia|sickle cell)\b",
    "Opioid / substance use / pain": r"\b(opioid|opiate|substance use|sud|buprenorphine|naloxone|pain|analgesic|gabapentin|pregabalin)\b",
    "Psychiatry / behavioral health": r"\b(antipsychotic|antidepressant|depression|bipolar|schizophrenia|psychiatric|ssri|snri|latuda|vraylar|rexulti|abilify)\b",
    "Rare disease / specialty": r"\b(rare disease|orphan|spinal muscular atrophy|cystic fibrosis|enzyme replacement|gene therapy|spinraza|zgensma|trikafta)\b",
    "Ophthalmology": r"\b(ophthalmology|retina|macular|amd|diabetic macular edema|glaucoma|eylea|lucentis|vabysmo)\b",
}
RATIONALE_PATTERNS = {
    "Clinical efficacy/safety framing": r"\b(efficacy|effective|effectiveness|safety|adverse|clinical|evidence|study|trial|outcomes?)\b",
    "Comparative therapeutic value": r"\b(therapeutically equivalent|therapeutic alternative|superior|inferior|comparative|class review|drug class)\b",
    "Prior authorization / step-therapy logic": r"\b(prior authorization|pa criteria|clinical criteria|step therapy|step edit|fail(ed|ure)?|trial of|criteria)\b",
    "Utilization controls": r"\b(utilization|quantity limit|dose limit|duration limit|duplicate therapy|prospective dur|retrospective dur)\b",
    "Cost / fiscal / rebate signals": r"\b(cost|fiscal|budget|rebate|supplemental rebate|net cost|financial|expenditure|savings)\b",
    "Public comment / manufacturer input": r"\b(public comment|testimony|manufacturer|stakeholder|hearing|speaker|registration|submit comments)\b",
    "Final authority / implementation": r"\b(final decision|approved by|commissioner|director|department|implementation|effective date|claims processing|provider notice)\b",
}
PRODUCT_CANDIDATES = [
    "Aduhelm", "Aimovig", "Ajovy", "Biktarvy", "Botox", "Bydureon", "Byetta", "Cosentyx",
    "Descovy", "Dupixent", "Eliquis", "Emgality", "Entresto", "Epclusa", "Eylea",
    "Farxiga", "Humira", "Jardiance", "Latuda", "Lucentis", "Mavyret", "Mounjaro",
    "Nurtec", "Ozempic", "Praluent", "Qulipta", "Repatha", "Rexulti", "Rinvoq",
    "Skyrizi", "Spinraza", "Stelara", "Taltz", "Tezspire", "Trikafta", "Trulicity",
    "Ubrelvy", "Vabysmo", "Vraylar", "Wegovy", "Xarelto", "Xolair", "Zepbound", "Zolgensma",
]


def clean(value):
    value = html.unescape(value or "")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s+", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def norm(url):
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse(parsed._replace(fragment=""))


def rel(path):
    return str(path.relative_to(OUT)).replace("\\", "/")


def read_existing_rows():
    rows = []
    if MANIFEST_CSV.exists():
        with MANIFEST_CSV.open(newline="", encoding="utf-8") as handle:
            rows = [{field: row.get(field, "") for field in FIELDS} for row in csv.DictReader(handle)]
    return rows


def read_seed_rows():
    seeds = []
    matrix = MATRIX.read_text(encoding="utf-8")
    for state in STATES:
        match = re.search(rf"^## {re.escape(state)}\n(?P<body>.*?)(?=^## |\Z)", matrix, re.M | re.S)
        if match:
            for label, url in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", match.group("body")):
                seeds.append({
                    "state": state,
                    "url": norm(url),
                    "label": label,
                    "seed_type": "state-monitoring-matrix",
                    "depth": "0",
                    "discovered_from": "",
                })
    with MEETINGS.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            state = row.get("state", "")
            if state in STATES and row.get("source_url"):
                seeds.append({
                    "state": state,
                    "url": norm(row["source_url"]),
                    "label": f"{row.get('date_iso', '')} {row.get('committee', '')}".strip(),
                    "seed_type": "meeting-dates-csv",
                    "depth": "0",
                    "discovered_from": "",
                })
    return seeds


def recover_orphan_text_rows(rows):
    known_text = {r.get("text_path", "") for r in rows if r.get("text_path")}
    next_index = len(rows) + 1
    for text_path in sorted((OUT / "text").glob("*/*.txt")):
        text_rel = rel(text_path)
        if text_rel in known_text:
            continue
        text = text_path.read_text(encoding="utf-8", errors="ignore")
        state_match = re.search(r"^State:\s*(.+)$", text, re.M)
        url_match = re.search(r"^Source URL:\s*(.+)$", text, re.M)
        label_match = re.search(r"^Label:\s*(.*)$", text, re.M)
        state = state_match.group(1).strip() if state_match else ""
        if state not in STATES:
            state = next((s for s, slug in SLUGS.items() if slug == text_path.parent.name), "")
        raw_path = ""
        stem = text_path.stem
        raw_dir = OUT / "raw" / text_path.parent.name
        raw_matches = list(raw_dir.glob(stem + ".*"))
        if raw_matches:
            raw_path = rel(raw_matches[0])
        rows.append({
            "state": state,
            "url": norm(url_match.group(1).strip()) if url_match else "",
            "label": label_match.group(1).strip() if label_match else text_path.stem,
            "seed_type": "recovered-from-existing-text",
            "depth": "",
            "discovered_from": "",
            "status": "saved",
            "http_status": "",
            "content_type": "",
            "raw_path": raw_path,
            "text_path": text_rel,
            "title": "",
            "error": "Recovered from text file after crawl was stopped.",
        })
        next_index += 1
    return rows


def add_uncollected_seed_gaps(rows, seeds):
    seen = {(row.get("state", ""), norm(row.get("url", ""))) for row in rows if row.get("url")}
    for seed in seeds:
        key = (seed["state"], seed["url"])
        if key in seen:
            continue
        rows.append({
            **{field: "" for field in FIELDS},
            **seed,
            "status": "uncollected_seed_gap",
            "error": "Broad crawl stopped per user before this seed URL was downloaded.",
        })
        seen.add(key)
    return rows


def write_manifest(rows):
    rows.sort(key=lambda row: (STATES.index(row["state"]) if row["state"] in STATES else 99, row["status"], row["url"], row["raw_path"]))
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    MANIFEST_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def load_texts(rows):
    by_state = defaultdict(list)
    for row in rows:
        if row.get("text_path"):
            path = OUT / row["text_path"]
            if path.exists():
                by_state[row["state"]].append((row, path.read_text(encoding="utf-8", errors="ignore")))
    return by_state


def snippets(text, pattern, limit=2):
    found = []
    for match in re.finditer(pattern, text, re.I):
        snippet = clean(text[max(0, match.start() - 120): min(len(text), match.end() + 220)]).replace("\n", " ")
        if snippet and snippet not in found:
            found.append(snippet)
        if len(found) >= limit:
            break
    return found


def summarize(rows):
    by_state_rows = defaultdict(list)
    for row in rows:
        by_state_rows[row["state"]].append(row)
    texts = load_texts(rows)
    joined = {state: "\n\n".join(text for _, text in items) for state, items in texts.items()}

    rationale_counts = Counter()
    rationale_states = defaultdict(list)
    for label, pattern in RATIONALE_PATTERNS.items():
        for state, text in joined.items():
            count = len(re.findall(pattern, text, re.I))
            if count:
                rationale_counts[label] += count
                rationale_states[label].append(state)

    therapy_counts = Counter()
    therapy_states = defaultdict(list)
    therapy_snips = defaultdict(list)
    for label, pattern in THERAPY_PATTERNS.items():
        for state, text in joined.items():
            count = len(re.findall(pattern, text, re.I))
            if count:
                therapy_counts[label] += count
                therapy_states[label].append(state)
                therapy_snips[label].extend((state, snip) for snip in snippets(text, pattern, 1))

    product_hits = Counter()
    product_states = defaultdict(set)
    for product in PRODUCT_CANDIDATES:
        pattern = rf"\b{re.escape(product)}\b"
        for state, text in joined.items():
            count = len(re.findall(pattern, text, re.I))
            if count:
                product_hits[product] += count
                product_states[product].add(state)

    saved = [r for r in rows if r["status"] == "saved"]
    texted = [r for r in saved if r.get("text_path")]
    blocked = [r for r in rows if r["status"] == "blocked"]
    gaps = [r for r in rows if r["status"] == "uncollected_seed_gap"]
    unextracted = [r for r in saved if not r.get("text_path")]
    gap_fill_report = {}
    if GAP_FILL_REPORT.exists():
        gap_fill_report = json.loads(GAP_FILL_REPORT.read_text(encoding="utf-8"))

    lines = [
        "# Group C P&T/DUR/PDL Decision-Rationale Source Collection",
        "",
        f"Scope: {', '.join(STATES)}.",
        "",
        "Status: updated with a targeted capped-crawl gap fill. This pass attempted only rows that had been marked `uncollected_seed_gap` because the broad crawl stopped before the seed URL was downloaded. It did not retry pre-existing 403, timeout, DNS, invalid URL, or other blocked/error rows, and it did not perform broad crawling.",
        "",
        "## Files",
        "",
        "- `manifest.csv` / `manifest.json`: collected, blocked, recovered, and uncollected seed URLs.",
        "- `raw/<state>/`: saved source copies already collected.",
        "- `text/<state>/`: extracted text already collected.",
        "- `gap-fill-report.json`: targeted capped-gap attempt counts from the current pass.",
        "",
        "## Collection Totals",
        "",
        f"- Saved source files/pages: {len(saved)}",
        f"- Sources with extracted text: {len(texted)}",
        f"- Blocked seed/source URLs: {len(blocked)}",
        f"- Remaining capped-crawl seed gaps: {len(gaps)}",
        f"- Saved files without extracted text: {len(unextracted)}",
        "",
    ]

    if gap_fill_report:
        saved_seed = gap_fill_report.get("final_saved_seed_pages") or gap_fill_report.get("saved_seed_pages", {})
        saved_link = gap_fill_report.get("final_saved_same_page_links") or gap_fill_report.get("saved_same_page_links", {})
        blocked_seed = gap_fill_report.get("final_blocked_seed_pages") or gap_fill_report.get("blocked_seed_pages", {})
        blocked_link = gap_fill_report.get("final_blocked_same_page_links") or gap_fill_report.get("blocked_same_page_links", {})
        repair = gap_fill_report.get("repair_attempts_for_gap_fill_url_encoding", {})
        states = sorted(set(saved_seed) | set(saved_link))
        lines += [
            "## Targeted Capped-Crawl Gap Fill",
            "",
            f"- Attempted capped seed gaps: {gap_fill_report.get('attempted_seed_gaps', 0)}",
            "- Final newly saved counts by state, including seed pages and bounded same-page document links:",
        ]
        for state in states:
            lines.append(
                f"  - {state}: {saved_seed.get(state, 0)} seed page(s), "
                f"{saved_link.get(state, 0)} same-page linked document/page(s)."
            )
        if repair:
            repair_total = sum(repair.values())
            lines.append(f"- Repaired URL-encoding/host issues from the targeted pass: {repair_total} save(s).")
        if blocked_seed or blocked_link:
            lines.append("- Final non-addressable targeted-pass gaps:")
            for state in sorted(set(blocked_seed) | set(blocked_link)):
                lines.append(f"  - {state}: {blocked_seed.get(state, 0)} seed page(s), {blocked_link.get(state, 0)} same-page link(s).")
        lines.append("")

    lines += [
        "## State Coverage",
        "",
        "| State | Saved | Text extracted | Blocked | Uncollected seed gaps | Notes |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for state in STATES:
        state_rows = by_state_rows[state]
        s_saved = [r for r in state_rows if r["status"] == "saved"]
        s_texted = [r for r in s_saved if r.get("text_path")]
        s_blocked = [r for r in state_rows if r["status"] == "blocked"]
        s_gaps = [r for r in state_rows if r["status"] == "uncollected_seed_gap"]
        note = "Collected text available" if s_texted else "No extracted text; use blocked/source list"
        if state == "Massachusetts" and s_blocked:
            note = "Mass.gov returned HTTP 403 during collection"
        lines.append(f"| {state} | {len(s_saved)} | {len(s_texted)} | {len(s_blocked)} | {len(s_gaps)} | {note} |")

    lines += ["", "## Collected Documents by State", ""]
    for state in STATES:
        state_rows = by_state_rows[state]
        saved_state = [r for r in state_rows if r["status"] == "saved"]
        lines += [f"### {state}", ""]
        if saved_state:
            for row in saved_state[:5]:
                label = clean(row.get("label") or row.get("title") or row.get("raw_path") or row.get("url"))
                lines.append(f"- `{row.get('raw_path')}`; text: `{row.get('text_path') or 'not extracted'}`; {label}")
            if len(saved_state) > 5:
                lines.append(f"- Additional saved items: {len(saved_state) - 5}; see `manifest.csv`.")
        else:
            lines.append("- No local documents collected before the crawl was stopped.")
        state_gaps = [r for r in state_rows if r["status"] in {"blocked", "uncollected_seed_gap"}]
        if state_gaps:
            lines.append("- Blocked/uncollected seed URLs:")
            for row in state_gaps[:5]:
                reason = row.get("error") or row.get("status")
                lines.append(f"  - {row.get('url')} - {reason}")
            if len(state_gaps) > 5:
                lines.append(f"  - Additional blocked/uncollected URLs: {len(state_gaps) - 5}; see `manifest.csv`.")
        lines.append("")

    lines += [
        "## Extracted Decision-Rationale Patterns",
        "",
        "These are term-supported patterns from extracted text only; they are directional and should be re-run after the remaining seed gaps are collected.",
        "",
    ]
    if rationale_counts:
        for label, count in rationale_counts.most_common():
            lines.append(f"- **{label}**: {count} term hits across {len(rationale_states[label])} state(s): {', '.join(rationale_states[label])}.")
    else:
        lines.append("- No rationale term patterns found in extracted text.")

    lines += [
        "",
        "Interpretation for pharma monitoring:",
        "",
        "- Public artifacts most often expose clinical, utilization-management, and implementation language; detailed net-cost/rebate rationale is usually a gap.",
        "- Meeting packets, recommendations, provider notices, PDL/PA criteria, and minutes need to be tracked together because recommendation and implementation can be separated.",
        "- Public-comment or testimony instructions are strategically important because they are often the only public engagement window captured in these materials.",
        "",
        "## Therapy / Disease / Class Mentions Found",
        "",
    ]
    if therapy_counts:
        for label, count in therapy_counts.most_common(10):
            lines.append(f"- **{label}**: {count} term hits in {', '.join(therapy_states[label])}.")
            for state, snip in therapy_snips[label][:1]:
                lines.append(f"  - {state}: \"{snip[:320]}\"")
    else:
        lines.append("- No configured therapy-area terms were found in extracted text.")

    lines += ["", "## Product Mentions Found", ""]
    if product_hits:
        for product, count in product_hits.most_common(15):
            states = ", ".join(sorted(product_states[product]))
            lines.append(f"- {product}: {count} hit(s) in {states}.")
        if len(product_hits) > 15:
            lines.append(f"- Additional configured product hits: {len(product_hits) - 15}; see extracted text files for details.")
    else:
        lines.append("- No configured brand/product terms were found. This does not mean products were absent; the partial dataset and term list are limited.")

    lines += [
        "",
        "## Explicit Limitations",
        "",
        "- Collection is incomplete for this group because the broad crawl was intentionally stopped.",
        "- This update filled only seed gaps caused by the crawl cap; it did not retry pre-existing blocked/error rows.",
        "- Massachusetts source pages/documents were attempted but returned HTTP 403 in the local collector.",
        "- No `uncollected_seed_gap` rows remain in the current Group C manifest; remaining gaps are blocked/error rows such as HTTP 403, DNS failure, timeout, or HTTP 404.",
        "- Text extraction was not available for every saved file; see `manifest.csv` for saved-but-unextracted rows.",
        "- Product-level conclusions, exact votes, final coverage decisions, approval-to-review speed, rebate logic, and net-cost rationale are unavailable unless explicitly present in extracted text.",
        "- Counts are search-term counts, not validated clinical categorizations.",
        "",
        "## High-Value Next Pass",
        "",
        "- For remaining blocked/error rows, use source-owner pages, alternate official mirrors, or manual browser retrieval where permitted rather than automated broad crawling.",
        "- Prioritize meeting packets/material PDFs, minutes, PDL recommendation documents, PA/protocol criteria, provider notices, and public-comment instructions.",
        "- Normalize extracted rows into: state, date, body, drug/class, action/recommendation, rationale text, final authority, effective date, comment/manufacturer window, source URL, and gap flags.",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    rows = read_existing_rows()
    rows = recover_orphan_text_rows(rows)
    rows = add_uncollected_seed_gaps(rows, read_seed_rows())
    write_manifest(rows)
    summarize(rows)
    print(f"rows={len(rows)} saved={sum(1 for r in rows if r['status']=='saved')} text={sum(1 for r in rows if r['status']=='saved' and r.get('text_path'))} blocked={sum(1 for r in rows if r['status']=='blocked')} gaps={sum(1 for r in rows if r['status']=='uncollected_seed_gap')}")


if __name__ == "__main__":
    main()
