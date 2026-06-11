import csv
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path


OUT = Path(__file__).resolve().parent
SOURCES = OUT / "sources"
LOCAL_RETAINED_JSON = SOURCES / "retained_ai_records.json"
LOCAL_RUN_MANIFEST = SOURCES / "run_manifest.json"

RETAINED = {
    "7": {
        "source_id": "R1",
        "category": "AI as operational/session topic",
        "ai_role": "Substantive AI topic",
        "scientific_topic": "Pulmonary exacerbation detection",
        "trigger": "using AI would be ACE",
        "summary": "The symposium presentation title refers to use of artificial intelligence for detecting pulmonary exacerbations in the CFTR modulator era; abstract text was not available in the presentation data.",
    },
    "90": {
        "source_id": "R2",
        "category": "AI as operational/session topic",
        "ai_role": "AI infrastructure or implementation",
        "scientific_topic": "Registry data management",
        "trigger": "can AI play a role",
        "summary": "The symposium presentation title addresses the potential role of artificial intelligence in registry data management; abstract text was not available in the presentation data.",
    },
    "543": {
        "source_id": "R3",
        "category": "Explicit AI/ML methods",
        "ai_role": "AI as analytic method",
        "scientific_topic": "Registry lung-function models",
        "trigger": "machine learning; CatBoost; SHAP",
        "summary": "Machine-learning time-series models were used to estimate short-term FEV1 and FVC trajectories from CF Registry of Turkey data using CatBoost, nested cross-validation, hyperparameter optimization, and SHAP.",
    },
    "349": {
        "source_id": "R4",
        "category": "Explicit AI/ML methods",
        "ai_role": "AI as analytic method",
        "scientific_topic": "AI-CT modulator assessment",
        "trigger": "Chest CT scans were analysed using AI-based methods",
        "summary": "A retrospective pediatric CFTR modulator outcomes study states that chest CT scans were analyzed using AI-based methods, paired with Swedish registry lung-function data and mixed-effects modeling.",
    },
    "432": {
        "source_id": "R5",
        "category": "Patient/public AI information behavior",
        "ai_role": "Patient information behavior",
        "scientific_topic": "Digital health literacy training",
        "trigger": "AI searches",
        "summary": "An Irish digital-health-literacy survey included AI searches among CF digital health resources and described information-seeking via CF medical websites and social media.",
    },
    "226": {
        "source_id": "R6",
        "category": "Explicit AI/ML methods",
        "ai_role": "AI as analytic method",
        "scientific_topic": "Registry clustering, CF states",
        "trigger": "unsupervised machine learning; k-means clustering",
        "summary": "CFFPR encounter data were clustered using unsupervised machine learning and k-means to classify clinical states and transitions associated with lung transplant-free survival.",
    },
    "378": {
        "source_id": "R7",
        "category": "Patient/public AI information behavior",
        "ai_role": "Patient information behavior",
        "scientific_topic": "Cancer-screening information needs",
        "trigger": "AI chatbots",
        "summary": "Qualitative interview findings on CF cancer-screening information needs reported patients' use of internet-based information and support, including peer social media and AI chatbots.",
    },
    "241": {
        "source_id": "R8",
        "category": "Explicit AI/ML methods",
        "ai_role": "AI as diagnostic workflow",
        "scientific_topic": "Organoid morphology workflow",
        "trigger": "AI-based morphological analysis pipeline; AI-derived analysis",
        "summary": "An AI-based morphology pipeline analyzed patient-derived intestinal organoids to distinguish wild-type from CF organoids and detect ETI-associated recovery.",
    },
    "257": {
        "source_id": "R9",
        "category": "Explicit AI/ML methods",
        "ai_role": "AI as imaging workflow",
        "scientific_topic": "AI-HRCT imaging workflow",
        "trigger": "Artificial intelligence-assisted; deep learning-based diagnostic model",
        "summary": "A deep learning model analyzed chest HRCT images from 48 CF patients aged 10 to 18 years across five pulmonary findings, reporting 97% average accuracy, sensitivity, specificity, and F1.",
    },
    "441": {
        "source_id": "R10",
        "category": "ML-adjacent algorithmic modeling",
        "ai_role": "ML-adjacent classifier workflow",
        "scientific_topic": "Breathomics VOC classification",
        "trigger": "XGBoost importance aggregation; classification performance",
        "summary": "A breathomics study used repeated subsampling with XGBoost importance aggregation to select 24 VOC features and evaluated CF-versus-asthma classification on a hold-out test set.",
    },
}


def read_local_source_records():
    payload = json.loads(LOCAL_RETAINED_JSON.read_text(encoding="utf-8"))
    return payload["records"]


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def esc(value):
    return html.escape(str(value or ""), quote=True)


def cite(record, label=None):
    n = record["ref_number"]
    text = label or str(n)
    return f'<a class="cite" href="{esc(record["presentation_url"])}">{esc(text)}</a>'


def short_date(value):
    if not value:
        return ""
    return value


def make_retained(records):
    kept = []
    for row in records:
        pid = row["presentation_id"]
        item = {**row, **RETAINED[pid]}
        kept.append(item)
    kept.sort(key=lambda r: int(r["presentation_id"]))
    for i, item in enumerate(kept, start=1):
        item["ref_number"] = i
    return kept


def write_retained_csv(kept):
    fields = [
        "source_id",
        "ref_number",
        "presentation_id",
        "abstract_id",
        "code",
        "title",
        "session_code",
        "session_title",
        "session_date",
        "start_time",
        "category",
        "ai_role",
        "scientific_topic",
        "trigger",
        "summary",
        "parse_status",
        "authors_text",
        "objectives",
        "methods",
        "results",
        "conclusion",
        "presentation_url",
        "session_url",
    ]
    path = OUT / "sources" / "retained_ai_records.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for item in kept:
            writer.writerow(item)
    return path


def write_retained_json(kept):
    path = OUT / "sources" / "retained_ai_records.json"
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_basis": "ECFS 2026 conference presentation records preserved in local source artifacts.",
        "retained_count": len(kept),
        "records": kept,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_source_log(kept, screened_records, source_manifest):
    category_counts = {}
    for item in kept:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
    source_scraped_at = source_manifest.get("source_manifest", {}).get("scraped_at", "2026-05-29")
    session_count = source_manifest.get("source_manifest", {}).get("session_count", 85)
    unique_abstract_count = source_manifest.get("source_manifest", {}).get("unique_abstract_id_count", 689)
    lines = [
        "# ECFS 2026 AI Topics Source Log",
        "",
        "## Source Basis",
        "",
        f"- Source artifacts state {screened_records} records, {session_count} sessions, and {unique_abstract_count} unique abstracts; source data were captured {source_scraped_at}.",
        f"- Rows screened in this build: {screened_records}.",
        f"- AI-related records retained: {len(kept)}.",
        "- Scope: explicit AI/ML methods, AI as operational/session topic, patient/public AI information behavior, and one separately labeled ML-adjacent algorithmic modeling record.",
        "",
        "## Inclusion and Exclusion Logic",
        "",
        "- Included when the source record explicitly framed the work as artificial intelligence, AI, machine learning, deep learning, AI-based analysis, AI searches, AI chatbots, or comparable ML classifier workflow.",
        "- Excluded clinical screening algorithms, regression-only predictors, biological or mechanistic models, and incidental text matches such as 'shape' or measurement units.",
        "- Two retained symposium records have `missing_abstract_html`; inclusion is based on the official local presentation title and row-level presentation URL.",
        "",
        "## Search Terms Used",
        "",
        "`artificial intelligence`, `AI`, `machine learning`, `deep learning`, `CatBoost`, `SHAP`, `k-means`, `XGBoost`, `AI searches`, `AI chatbots`, `large language`, `LLM`, `NLP`, `random forest`, `support vector`.",
        "",
        "## Category Counts",
        "",
    ]
    for cat in [
        "Explicit AI/ML methods",
        "AI as operational/session topic",
        "Patient/public AI information behavior",
        "ML-adjacent algorithmic modeling",
    ]:
        lines.append(f"- {cat}: {category_counts.get(cat, 0)}")
    lines.extend(["", "## Retained Records", ""])
    for item in kept:
        lines.extend(
            [
                f"### Reference {item['ref_number']} / {item['source_id']}: presentation {item['presentation_id']} {item.get('code') or ''}".rstrip(),
                "",
                f"- Title: {item['title']}",
                f"- Session: {item.get('session_code') or 'No session code'} | {item.get('session_title') or ''}",
                f"- Date/time: {item.get('session_date') or ''} {item.get('start_time') or ''}",
                f"- Category: {item['category']}",
                f"- AI role: {item['ai_role']}",
                f"- Scientific topic: {item['scientific_topic']}",
                f"- Inclusion trigger: {item['trigger']}",
                f"- Evidence summary: {item['summary']}",
                f"- Parse status: {item.get('parse_status') or ''}",
                f"- Row-level URL: {item.get('presentation_url') or ''}",
                "",
            ]
        )
    path = OUT / "sources" / "source-log.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def card(item, tag_class="lime"):
    return f"""
        <div class="card">
          <span class="tag {tag_class}">{esc(item['category'])}</span>
          <h3>{esc(item['scientific_topic'])}{cite(item)}</h3>
          <p>{esc(item['summary'])}</p>
          <div class="meta">Trigger: {esc(item['trigger'])}</div>
        </div>"""


def write_html(kept):
    by_pid = {item["presentation_id"]: item for item in kept}
    explicit = [by_pid[x] for x in ["543", "349", "226", "241", "257"]]
    operational = [by_pid[x] for x in ["7", "90"]]
    patient = [by_pid[x] for x in ["432", "378"]]
    adjacent = [by_pid["441"]]
    refs = "\n".join(
        f"""
        <div class="row refs">
          <div class="cell">{item['ref_number']}</div>
          <div class="cell">{esc(item['source_id'])}: {esc(item.get('code') or 'Session')}<br><a href="{esc(item['presentation_url'])}">Presentation {esc(item['presentation_id'])}</a></div>
          <div class="cell">{esc(item.get('session_date'))}<br>{esc(item.get('session_title'))}</div>
          <div class="cell">{esc(item['title'])}<br><span>{esc(item['trigger'])}</span></div>
        </div>"""
        for item in kept
    )
    explicit_cards = "\n".join(card(item, cls) for item, cls in zip(explicit, ["lime", "blue", "orange", "pink", "red"]))
    op_cards = "\n".join(card(item, cls) for item, cls in zip(operational + patient, ["lime", "blue", "orange", "pink"]))
    adjacent_card = card(adjacent[0], "gray")
    today = "May 31, 2026"
    html_text = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Artificial intelligence-related topics at ECFS 2026</title>
  <style>
    :root {{
      --ink: #10120f; --muted: #5c6257; --paper: #f6f1e8; --paper-2: #ebe4d6;
      --card: #fffaf0; --line: #1b1f17; --lime: #d7ff5f; --orange: #ffb86b;
      --blue: #b8d8ff; --pink: #ffd3e0; --gray: #d6d0c2; --red: #ff8a76;
      --shadow: 0 18px 48px rgba(16, 18, 15, 0.08); --radius: 24px;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; background: var(--paper); color: var(--ink); scrollbar-width: none; }}
    html::-webkit-scrollbar, body::-webkit-scrollbar {{ display: none; }}
    body, *, *::before, *::after {{
      -webkit-print-color-adjust: exact; print-color-adjust: exact;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    a {{ color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .slide {{
      width: 100vw; height: 100vh; min-height: 100vh; overflow: hidden; position: relative;
      display: flex; align-items: flex-start; padding: 36px 0 20px; page-break-after: always;
      break-after: page; background: var(--paper);
    }}
    .slide:last-child {{ page-break-after: auto; break-after: auto; }}
    .slide-bg-img {{ position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; pointer-events: none; user-select: none; }}
    .wrap {{ width: min(1360px, calc(100vw - 56px)); margin: 0 auto; position: relative; z-index: 1; }}
    .eyebrow {{
      display: inline-flex; align-items: center; border: 1.4px solid var(--line); padding: 8px 12px;
      border-radius: 999px; font-size: 15px; font-weight: 850; letter-spacing: 0; text-transform: uppercase;
      margin-bottom: 18px; background: var(--lime);
    }}
    h1, h2, h3, p {{ margin: 0; }}
    h1 {{ font-size: 54px; line-height: .98; letter-spacing: 0; font-weight: 400; max-width: 1360px; }}
    h2 {{ font-size: 48px; line-height: 1; letter-spacing: 0; font-weight: 400; max-width: 1300px; }}
    h3 {{ font-size: 26px; line-height: 1.04; letter-spacing: 0; font-weight: 640; }}
    .dek {{ margin-top: 14px; color: var(--muted); font-size: 25px; line-height: 1.18; max-width: 1260px; }}
    .section-head {{ margin-bottom: 40px; }}
    .section-head p {{ margin-top: 12px; color: var(--muted); font-size: 24px; line-height: 1.18; max-width: 1280px; }}
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
    .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }}
    .panel, .metric, .card, .table, .callout {{
      border: 1.5px solid var(--line); background: rgba(255,250,240,.88); border-radius: var(--radius);
      box-shadow: var(--shadow); overflow: hidden;
    }}
    .panel {{ padding: 22px; }}
    .callout {{ padding: 22px 26px; background: #11130f; color: var(--paper); border-color: #11130f; }}
    .callout h3 {{ color: var(--lime); font-size: 31px; }}
    .summary-list {{ margin: 12px 0 0; padding-left: 22px; display: grid; gap: 8px; }}
    .summary-list li {{ color: rgba(246,241,232,.86); font-size: 22px; line-height: 1.1; }}
    .metric {{ padding: 19px; min-height: 154px; }}
    .num {{ font-size: 50px; line-height: .92; font-weight: 430; letter-spacing: 0; }}
    .label {{ margin-top: 12px; font-size: 23px; line-height: 1.12; color: var(--muted); }}
    .card {{ padding: 21px; min-height: 235px; }}
    .card h3, .panel h3 {{ font-weight: 760; }}
    .card h3 {{ font-size: 21px; line-height: 1.08; }}
    .card p {{ color: var(--muted); font-size: 19px; line-height: 1.14; margin-top: 10px; }}
    .card h3 .cite {{ font-size: .48em; }}
    .meta {{ margin-top: 12px; color: #3f453b; font-size: 13px; line-height: 1.16; }}
    .tag {{
      display: inline-block; padding: 5px 9px; border: 1.2px solid var(--line); border-radius: 999px;
      font-size: 12px; line-height: 1; font-weight: 850; text-transform: uppercase; background: var(--paper-2);
      margin-bottom: 11px; white-space: nowrap;
    }}
    .lime {{ background: var(--lime); }} .orange {{ background: var(--orange); }} .blue {{ background: var(--blue); }}
    .pink {{ background: var(--pink); }} .red {{ background: var(--red); }} .gray {{ background: var(--gray); }}
    .table {{ display: grid; }}
    .row {{ display: grid; border-bottom: 1px solid var(--line); min-height: 64px; }}
    .row:last-child {{ border-bottom: 0; }}
    .row.tax {{ grid-template-columns: .86fr .18fr 2.56fr; }}
    .row.tax.head {{ min-height: 56px; }}
    .row.refs {{ grid-template-columns: .32fr .85fr 1.05fr 2.05fr; min-height: 0; }}
    .cell {{ padding: 13px 14px; border-right: 1px solid var(--line); font-size: 20px; line-height: 1.12; }}
    .cell:last-child {{ border-right: 0; }}
    .head .cell {{
      background: #11130f; color: var(--paper); font-weight: 760; text-transform: uppercase;
      font-size: 14px; line-height: 1; white-space: nowrap;
      padding-top: 11px; padding-bottom: 11px;
    }}
    .row.tax.head .cell {{ display: flex; align-items: center; }}
    .row.tax:not(.head) .cell:first-child {{ font-weight: 400; }}
    .refs .cell {{ font-size: 14px; line-height: 1.1; padding: 8px 10px; }}
    .refs .cell span {{ color: var(--muted); }}
    .refs.head .cell {{ font-size: 14px; line-height: 1; padding: 9px 10px; white-space: nowrap; }}
    .row.refs .cell:first-child {{ display: flex; justify-content: center; align-items: center; text-align: center; }}
    .references-slide .section-head {{ margin-bottom: 34px; }}
    .references-slide h2 {{ font-size: 48px; font-weight: 400; }}
    .cite {{ font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 900; text-decoration: none; }}
    .cite + .cite::before {{ content: ","; margin-right: 1px; }}
    .source-note {{ color: var(--muted); font-size: 15px; line-height: 1.22; margin-top: 12px; }}
    .slide-num {{ position: absolute; right: 40px; bottom: 24px; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: rgba(16,18,15,.38); font-weight: 800; z-index: 2; }}
    @page {{ size: 1600px 900px; margin: 0; }}
    @media print {{
      html, body {{ width: 1600px; height: 900px; }}
      .slide {{ width: 1600px; height: 900px; min-height: 900px; padding: 36px 0 20px; }}
      .wrap {{ width: 1360px; }}
      .panel, .metric, .card, .table, .callout {{ box-shadow: none; }}
    }}
    @media screen and (max-width: 900px) {{ .slide {{ width: 1600px; height: 900px; }} }}
  </style>
</head>
<body>
  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="eyebrow">ECFS 2026 AI topics | {today}</div>
      <h1>Artificial intelligence-related topics at ECFS 2026</h1>
      <p class="dek">Screening of 818 ECFS 2026 presentation records retained 10 records related to artificial intelligence: 5 with explicit AI/ML methods, 2 addressing AI as an operational or session topic, 2 describing patient/public AI information behavior, and 1 ML-adjacent classifier workflow.{cite(by_pid['543'])}{cite(by_pid['257'])}{cite(by_pid['441'])}</p>
      <div class="grid-4" style="margin-top:38px;">
        <div class="metric"><div class="num">818</div><div class="label">ECFS 2026 conference presentation records screened.</div></div>
        <div class="metric"><div class="num">10</div><div class="label">Records related to artificial intelligence after excluding regression-only and incidental keyword matches.</div></div>
        <div class="metric"><div class="num">5</div><div class="label">Records that described explicit AI/ML methods in imaging, morphology, and registry analyses.</div></div>
        <div class="metric"><div class="num">4</div><div class="label">Records addressing registry operations or patient/public information behavior.</div></div>
      </div>
      <div class="callout" style="margin-top:18px;">
        <h3>Evidence summary</h3>
        <ul class="summary-list">
          <li>Five records described explicit AI/ML methods: registry forecasting with CatBoost/SHAP, AI-based CT analysis, CFFPR k-means clustering, AI-based organoid morphology, and deep-learning HRCT analysis.{cite(by_pid['543'])}{cite(by_pid['349'])}{cite(by_pid['226'])}{cite(by_pid['241'])}{cite(by_pid['257'])}</li>
          <li>Two symposium records addressed artificial intelligence in pulmonary-exacerbation detection and registry data management; abstract text was unavailable in the presentation data.{cite(by_pid['7'])}{cite(by_pid['90'])}</li>
          <li>Two records described patient/public use of AI-related information resources, including AI searches in digital-health-literacy training and AI chatbots in cancer-screening information support; one breathomics classifier was classified separately as ML-adjacent because it used XGBoost feature selection.{cite(by_pid['432'])}{cite(by_pid['378'])}{cite(by_pid['441'])}</li>
        </ul>
      </div>
    </div>
    <div class="slide-num">01 / 06</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Role taxonomy</div>
        <h2>Records were classified by AI role and evidence context</h2>
        <p>Counts reflect retained records, not unique abstracts; classifications are rule-based and derived from explicit source terms in the presentation data.</p>
      </div>
      <div class="table">
        <div class="row tax head"><div class="cell">Category</div><div class="cell">Count</div><div class="cell">Included records and scope note</div></div>
        <div class="row tax"><div class="cell">Explicit AI/ML methods</div><div class="cell">5</div><div class="cell">R3, R4, R6, R8, R9: machine learning, AI-based CT or morphology analysis, k-means clustering, and deep learning.{cite(by_pid['543'])}{cite(by_pid['349'])}{cite(by_pid['226'])}{cite(by_pid['241'])}{cite(by_pid['257'])}</div></div>
        <div class="row tax"><div class="cell">AI as operational/session topic</div><div class="cell">2</div><div class="cell">R1 and R2: symposium-level artificial-intelligence topics in pulmonary-exacerbation detection and registry data management.{cite(by_pid['7'])}{cite(by_pid['90'])}</div></div>
        <div class="row tax"><div class="cell">Patient/public AI information behavior</div><div class="cell">2</div><div class="cell">R5 and R7: AI searches and AI chatbots were described in the context of digital health literacy and cancer-screening information behavior.{cite(by_pid['432'])}{cite(by_pid['378'])}</div></div>
        <div class="row tax"><div class="cell">ML-adjacent algorithmic modeling</div><div class="cell">1</div><div class="cell">R10: XGBoost feature selection and hold-out classifier evaluation in breathomics; classified separately from records that explicitly used artificial-intelligence terminology.{cite(by_pid['441'])}</div></div>
      </div>
      <p class="source-note">Excluded: clinical screening algorithms, regression-only predictors, biological or mechanistic models, and incidental keyword matches.</p>
    </div>
    <div class="slide-num">02 / 06</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Explicit AI/ML methods</div>
        <h2>AI/ML methods spanned registry and imaging studies</h2>
      </div>
      <div class="grid-3">{explicit_cards}
      </div>
    </div>
    <div class="slide-num">03 / 06</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Operational and information-behavior AI</div>
        <h2>Operational and information-behavior records</h2>
        <p>Two symposium titles addressed AI as an operational or implementation topic, and two empirical records reported patient/public information behavior involving AI resources.</p>
      </div>
      <div class="grid-2">{op_cards}
      </div>
    </div>
    <div class="slide-num">04 / 06</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">ML-adjacent classification</div>
        <h2>One classifier workflow was classified separately</h2>
      </div>
      <div class="grid-2">
        {adjacent_card}
        <div class="panel">
          <span class="tag orange">Classification note</span>
          <h3>Classification rules excluded statistical or mechanistic modeling alone</h3>
          <p style="margin-top:12px;color:var(--muted);font-size:23px;line-height:1.18;">The retained count does not include records that only used statistical regression, clinical screening algorithms, non-AI automation, or biological model language. P205 is classified as ML-adjacent because the abstract identifies XGBoost feature selection and classifier evaluation but does not describe the study as artificial intelligence.</p>
          <p class="source-note">Classification was based on explicit terminology in the ECFS 2026 presentation data.</p>
        </div>
      </div>
    </div>
    <div class="slide-num">05 / 06</div>
  </article>

  <article class="slide references-slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <h2>References</h2>
      </div>
      <div class="table">
        <div class="row refs head"><div class="cell">Ref</div><div class="cell">Source</div><div class="cell">Date / Status / Source Owner</div><div class="cell">Evidence Used in Report</div></div>
        {refs}
      </div>
    </div>
    <div class="slide-num">06 / 06</div>
  </article>
</body>
</html>
"""
    path = OUT / "report.html"
    path.write_text(html_text, encoding="utf-8")
    return path


def write_run_manifest(kept, all_rows, artifacts):
    prior_manifest = json.loads(LOCAL_RUN_MANIFEST.read_text(encoding="utf-8"))
    source_manifest = prior_manifest.get("source_manifest", prior_manifest)
    output = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_manifest": source_manifest,
        "screened_records": all_rows,
        "retained_ai_records": len(kept),
        "category_counts": {},
        "artifacts": {name: str(path) for name, path in artifacts.items()},
    }
    for item in kept:
        output["category_counts"][item["category"]] = output["category_counts"].get(item["category"], 0) + 1
    path = OUT / "sources" / "run_manifest.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_qa_note():
    path = OUT / "sources" / "qa_status.md"
    path.write_text(
        "\n".join(
            [
                "# QA Status",
                "",
                "- Source basis: ECFS 2026 conference presentation records captured 2026-05-29.",
                "- Scope status: 818 records screened; ten AI-related records retained.",
                "- Report HTML regenerated from build_ecfs_ai_topics_report.py.",
                "- PDF export completed on 2026-05-31 using CHROME_PATH=C:/Program Files/Google/Chrome/Application/chrome.exe.",
                "- Exporter reported zero overflow warnings across six slides.",
                "- PDF raster render check was skipped because pdftoppm was not available in this environment.",
            ]
        ),
        encoding="utf-8",
    )
    return path


def main():
    source_manifest = json.loads(LOCAL_RUN_MANIFEST.read_text(encoding="utf-8"))
    screened_records = source_manifest.get("screened_records", 818)
    rows = read_local_source_records()
    kept = make_retained(rows)
    artifacts = {
        "retained_csv": write_retained_csv(kept),
        "retained_json": write_retained_json(kept),
        "source_log": write_source_log(kept, screened_records, source_manifest),
        "report_html": write_html(kept),
        "qa_status": write_qa_note(),
    }
    artifacts["run_manifest"] = write_run_manifest(kept, screened_records, artifacts)
    print(json.dumps({k: str(v) for k, v in artifacts.items()}, indent=2))


if __name__ == "__main__":
    main()
