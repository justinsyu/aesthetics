import csv
import html
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = Path(r"C:\Users\Justin\Desktop\ada-2026")
SOURCE_JSON = SOURCE_DIR / "ada26_publications.json"
SUMMARY_JSON = SOURCE_DIR / "data" / "ada26_summary.json"

CSV_OUT = ROOT / "ada_2026_ai_records.csv"
NOTES_OUT = ROOT / "source_notes.md"
HTML_OUT = ROOT / "ada_2026_ai_topics_cohere_ci.html"
BG_OUT = ROOT / "tan_slide_background.png"


TOPICS = [
    "Generative AI, agents, and clinical decision support",
    "Predictive risk, progression, and utilization models",
    "CGM analytics, glycemic forecasting, and AID algorithms",
    "Nutrition, behavior, digital coaching, and remote care",
    "Omics, biomarkers, endotypes, and drug discovery",
    "Imaging, retinopathy, wounds, and visual AI",
    "Population health, EHR/RWD, equity, and implementation",
]


EXPLICIT_PATTERNS = [
    ("LLM / generative AI", re.compile(r"\b(large language models?|LLMs?|generative AI|genAI|ChatGPT|GPT|Open\s*AI|OpenAI|retrieval[- ]augmented generation|RAG-assisted|agentic AI)\b", re.I)),
    ("Artificial intelligence", re.compile(r"\b(artificial intelligence|AI[- ](?:assisted|audited|based|derived|driven|enabled|guided|ready)|AI/ML|multimodal AI|with AI|using AI|analyzed with AI|agentic AI|in silico AI)\b", re.I)),
    ("Machine learning", re.compile(r"\b(machine[- ]learning|ML[- ]based|ML models?|random[- ]forest|gradient boosting|XGBoost|Super Learning|support vector machine|elastic net|DDRTree|dimensionality reduction)\b", re.I)),
    ("Deep learning / neural networks", re.compile(r"\b(deep[- ]learning|neural networks?|transformer(?: model| personalization| architecture)?|foundation model)\b", re.I)),
    ("NLP / text mining", re.compile(r"\b(natural language (?:processing|queries)|\bNLP\b|text mining|qualitative theme generation)\b", re.I)),
    ("Computer vision / image AI", re.compile(r"\b(computer vision|AI-derived retinal|retinal imaging biomarkers|autonomous AI .*eye|image(?:s)? .*analyzed with AI)\b", re.I)),
]


ADJACENT_PATTERNS = [
    ("Automated insulin delivery / closed loop", re.compile(r"\b(automated insulin delivery|advanced hybrid closed[- ]loop|hybrid closed[- ]loop|fully closed[- ]loop|closed[- ]loop system|open[- ]source automated insulin delivery|bionic pancreas|autonomous bolus|AID system|AID use|using AID|AID algorithms?)\b", re.I)),
    ("Device algorithm / glycemic automation", re.compile(r"\b(next[- ]generation algorithm|adaptive algorithms?|model predictive control|glycemic control algorithm|automated glycemic control|automated AGP interpretation|generative framework for automated AGP)\b", re.I)),
    ("Digital twin / digital biomarkers", re.compile(r"\b(digital twins?|digital biomarkers?)\b", re.I)),
]


FALSE_POSITIVE_HINTS = [
    re.compile(r"\baromatase inhibitor", re.I),
    re.compile(r"\bdecision tree simulated\b", re.I),
    re.compile(r"\blow lean mass\b", re.I),
]


def clean_title(row):
    title = row.get("title", "").strip()
    abstract_number = row.get("abstract_number", "").strip()
    prefix = f"{abstract_number} - "
    if abstract_number and title.startswith(prefix):
        title = title[len(prefix) :]
    return " ".join(title.split())


def full_text(row):
    sections = row.get("sections") or {}
    section_text = " ".join(str(v) for v in sections.values())
    return "\n".join(
        [
            clean_title(row),
            row.get("abstract_text", "") or "",
            section_text,
        ]
    )


def context_snippet(text, match):
    start = max(0, match.start() - 110)
    end = min(len(text), match.end() + 190)
    snippet = " ".join(text[start:end].split())
    return snippet


def classify(row):
    text = full_text(row)
    if any(rx.search(text) for rx in FALSE_POSITIVE_HINTS) and not re.search(
        r"\b(artificial intelligence|machine[- ]learning|AI[- ]|OpenAI|GPT|large language|deep[- ]learning)\b",
        text,
        re.I,
    ):
        return None

    matches = []
    snippets = []
    for label, rx in EXPLICIT_PATTERNS:
        found = rx.search(text)
        if found:
            matches.append(label)
            snippets.append(context_snippet(text, found))

    if matches:
        return {
            "classification": "explicit AI/ML",
            "ai_role": role_for(row, text, explicit=True),
            "matched_terms": "; ".join(dict.fromkeys(matches)),
            "source_excerpt": snippets[0],
        }

    adjacent = []
    adjacent_snippets = []
    for label, rx in ADJACENT_PATTERNS:
        found = rx.search(text)
        if found:
            adjacent.append(label)
            adjacent_snippets.append(context_snippet(text, found))

    if adjacent:
        return {
            "classification": "AI-adjacent algorithmic/digital",
            "ai_role": role_for(row, text, explicit=False),
            "matched_terms": "; ".join(dict.fromkeys(adjacent)),
            "source_excerpt": adjacent_snippets[0],
        }

    return None


def role_for(row, text, explicit):
    lower = text.lower()
    if re.search(r"\b(llm|llms|large language|generative ai|gpt|openai|chatgpt|agentic)\b|retrieval[- ]augmented generation|\brag\b|decision support", lower):
        return "Substantive AI tool/workflow/evaluation"
    if re.search(r"automated insulin delivery|closed-loop|aid system|aid use|bionic pancreas|glycemic control algorithm", lower):
        return "AI-adjacent algorithmic diabetes technology"
    if re.search(r"ai-readi|dataset|knowledge portal", lower):
        return "AI infrastructure or implementation"
    if re.search(r"machine[- ]learning|deep[- ]learning|random[- ]forest|gradient boosting|super learning|elastic net|ddrtree|dimensionality reduction", lower):
        return "AI as analytic method"
    if explicit:
        return "Substantive AI method or enabled workflow"
    return "AI-adjacent algorithmic workflow"


def topic_clusters(row, classification):
    text = full_text(row).lower()
    clusters = []
    if re.search(r"llm|large language|generative ai|gpt|openai|rag|agentic|decision support|treatment decisions|protocol adherence|agp interpretation|natural language", text):
        clusters.append(TOPICS[0])
    if re.search(r"predict|risk|progression|utilization|acute care|hospital|mortality|synthetic control|propensity|super learning|g6pd|cardiovascular|kidney|renal|liver|mortality|readmission|blood pressure|hba1c", text):
        clusters.append(TOPICS[1])
    if re.search(r"cgm|continuous glucose|glucose prediction|glycemic|insulin delivery|closed-loop|aid system|aid use|bionic pancreas|omnipod|minimed|control-iq|twiist|camaps|ile?t|bolus|pump|agp", text):
        clusters.append(TOPICS[2])
    if re.search(r"nutrition|meal|diet|fiber|behavior|coaching|remote|engagement|mobile|smart-ring|epro|digital biomarker|community health|wellness|weight loss|obesity", text):
        clusters.append(TOPICS[3])
    if re.search(r"omics|proteomic|genetic|gene|islet|beta-cell|kinome|drug discovery|virtual screening|molecular|endotype|biomarker|glp-1|actr|myoblast|senescence|rna|single-cell|multiomics", text):
        clusters.append(TOPICS[4])
    if re.search(r"retinal|retinopathy|eye|imaging|image|vision|wound|foot ulcer|ulcer|visual|myoblast.*images", text):
        clusters.append(TOPICS[5])
    if re.search(r"ehr|real-world|medicare|medicaid|population|race|equity|rural|implementation|workflow|referral|disparit|clinic|provider|survey|social determinants|sdoh|health system|primary care", text):
        clusters.append(TOPICS[6])
    if not clusters:
        clusters.append(TOPICS[1] if classification == "explicit AI/ML" else TOPICS[2])
    return "; ".join(dict.fromkeys(clusters))


def notable(records, predicate, limit=5):
    selected = [r for r in records if predicate(r)]
    return selected[:limit]


def esc(value):
    return html.escape(str(value or ""), quote=True)


def short_title(title, limit=86):
    title = " ".join(title.split())
    if len(title) <= limit:
        return title
    return title[: limit - 1].rstrip() + "..."


def write_csv(records):
    fields = [
        "abstract_number",
        "title",
        "classification",
        "ai_role",
        "matched_terms",
        "topic_clusters",
        "source_excerpt",
        "session_type",
        "session_date",
        "session_start",
        "session_location",
        "local_source_path",
        "mediaurl",
        "authors",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field, "") for field in fields})


def write_notes(records, source_count, summary):
    class_counts = Counter(r["classification"] for r in records)
    role_counts = Counter(r["ai_role"] for r in records)
    topic_counts = Counter()
    for r in records:
        for topic in r["topic_clusters"].split("; "):
            topic_counts[topic] += 1

    lines = [
        "# ADA 2026 AI Topics Source Notes",
        "",
        f"Source corpus: `{SOURCE_JSON}`",
        "",
        f"Source metadata: ADA 2026 publication archive with {source_count:,} records; scraped timestamp in `ada26_summary.json` is `{summary.get('scraped_at', 'not available')}`.",
        "",
        "Run mode: full local-corpus scan. No fresh web re-check or webpage screenshot audit was performed; the local ADA archive is treated as the source-of-truth corpus for this conference summary.",
        "",
        "Classification summary:",
        "",
        f"- Explicit AI/ML records retained: {class_counts.get('explicit AI/ML', 0)}",
        f"- AI-adjacent algorithmic or digital-health records retained: {class_counts.get('AI-adjacent algorithmic/digital', 0)}",
        f"- Total companion table records: {len(records)}",
        "",
        "Explicit AI/ML terms included artificial intelligence, standalone AI in source-framed AI phrases, AI-enabled / AI-assisted / AI-based / AI-driven variants, AI/ML, machine learning, named ML methods, deep learning, neural-network terms, LLM / large language model, generative AI / GenAI, GPT/OpenAI, retrieval-augmented generation, NLP / natural-language queries, and computer-vision or image-AI terms.",
        "",
        "Adjacent terms included automated insulin delivery, hybrid or fully closed-loop systems, AID algorithms, digital twins, digital biomarkers, predictive algorithms, and automated AGP interpretation where the source described an algorithmic workflow without explicit AI/ML wording.",
        "",
        "Ordinary statistical modeling, regression, simulation, generic diabetes-technology adoption, clinical surveys, and nonspecific automation were excluded unless the source framed the work as AI/ML or as an algorithmic diabetes-technology workflow.",
        "",
        "AI-role counts:",
        "",
    ]
    for role, count in role_counts.most_common():
        lines.append(f"- {role}: {count}")
    lines.extend(["", "Topic-cluster counts are non-exclusive:", ""])
    for topic, count in topic_counts.most_common():
        lines.append(f"- {topic}: {count}")
    lines.extend(
        [
            "",
            "The topic clusters in the deck and companion CSV are non-exclusive and intended for descriptive competitive-intelligence synthesis, not formal topic modeling.",
            "",
            f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        ]
    )
    NOTES_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def metric(label, value, note):
    return f"""
      <div class="metric">
        <div class="value">{esc(value)}</div>
        <div class="label">{esc(label)}</div>
        <div class="note">{esc(note)}</div>
      </div>"""


def bar_rows(counter, max_items=7):
    items = counter.most_common(max_items)
    if not items:
        return ""
    max_val = max(v for _, v in items)
    colors = ["lime", "blue", "red", "orange", "purple", "ink", "muted"]
    rows = []
    for idx, (label, value) in enumerate(items):
        width = max(6, round((value / max_val) * 100))
        rows.append(
            f'<div class="bar-item"><div class="bar-label">{esc(label)}</div><div class="bar-track"><div class="bar-fill {colors[idx % len(colors)]}" style="width:{width}%"></div></div><div class="bar-value">{value}</div></div>'
        )
    return "\n".join(rows)


def card_list(records):
    rows = []
    for r in records:
        rows.append(
            f'<tr><td>{esc(r["abstract_number"])}</td><td>{esc(short_title(r["title"], 72))}</td><td>{esc(r["ai_role"])}</td></tr>'
        )
    return "\n".join(rows)


def write_html(records, source_count, summary):
    class_counts = Counter(r["classification"] for r in records)
    role_counts = Counter(r["ai_role"] for r in records)
    topic_counts = Counter()
    session_counts = Counter(r["session_type"] for r in records)
    explicit_records = [r for r in records if r["classification"] == "explicit AI/ML"]
    adjacent_records = [r for r in records if r["classification"] != "explicit AI/ML"]
    for r in records:
        for topic in r["topic_clusters"].split("; "):
            topic_counts[topic] += 1

    gen = notable(records, lambda r: TOPICS[0] in r["topic_clusters"])
    pred = notable(records, lambda r: TOPICS[1] in r["topic_clusters"] and r["classification"] == "explicit AI/ML")
    aid = notable(records, lambda r: TOPICS[2] in r["topic_clusters"] and r["classification"] != "explicit AI/ML")
    behavior = notable(records, lambda r: TOPICS[3] in r["topic_clusters"])
    omics = notable(records, lambda r: TOPICS[4] in r["topic_clusters"])
    imaging = notable(records, lambda r: TOPICS[5] in r["topic_clusters"])

    scraped_at = summary.get("scraped_at", "not available")
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ADA 2026 AI Topics Summary</title>
  <style>
    :root {{
      --paper:#f4efe3;
      --ink:#171717;
      --muted:#5e5a50;
      --line:#2a2924;
      --lime:#c7f000;
      --blue:#7aa7ff;
      --red:#ff6b5f;
      --orange:#f1a33b;
      --purple:#ad8cff;
      --card:#fffaf0;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:#d8d0bf; color:var(--ink); font-family:Inter, Arial, sans-serif; }}
    .deck {{ width:1600px; margin:0 auto; }}
    .slide {{ position:relative; width:1600px; height:900px; overflow:hidden; padding:64px 72px 58px; page-break-after:always; background:var(--paper); border:1px solid #bfb6a4; }}
    .slide-bg-img {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:0; opacity:.55; }}
    .content {{ position:relative; z-index:1; height:100%; display:flex; flex-direction:column; gap:26px; }}
    .eyebrow {{ font-size:18px; font-weight:800; text-transform:uppercase; letter-spacing:.08em; color:#3e3a33; }}
    h1 {{ margin:0; font-family:"Space Grotesk", Inter, Arial, sans-serif; font-size:76px; line-height:.98; max-width:1260px; letter-spacing:0; }}
    h2 {{ margin:0; font-family:"Space Grotesk", Inter, Arial, sans-serif; font-size:42px; line-height:1.05; max-width:1320px; letter-spacing:0; }}
    h3 {{ margin:0 0 10px; font-size:24px; line-height:1.12; letter-spacing:0; }}
    p, li {{ font-size:22px; line-height:1.26; margin:0; color:#2f2d28; }}
    ul {{ margin:0; padding-left:26px; display:flex; flex-direction:column; gap:10px; }}
    .lede {{ font-size:31px; line-height:1.22; max-width:1180px; color:#323028; }}
    .grid {{ display:grid; gap:22px; }}
    .two {{ grid-template-columns:1fr 1fr; }}
    .three {{ grid-template-columns:1fr 1fr 1fr; }}
    .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:18px; }}
    .metric, .panel, .callout {{ border:2px solid var(--line); background:rgba(255,250,240,.86); border-radius:8px; padding:22px; }}
    .metric .value {{ font-family:"Space Grotesk", Inter, Arial, sans-serif; font-size:54px; line-height:1; font-weight:800; }}
    .metric .label {{ margin-top:9px; font-size:18px; font-weight:800; text-transform:uppercase; }}
    .metric .note {{ margin-top:8px; color:var(--muted); font-size:18px; line-height:1.24; }}
    .bar-list {{ display:flex; flex-direction:column; gap:12px; }}
    .bar-item {{ display:grid; grid-template-columns:460px 1fr 58px; gap:15px; align-items:center; font-size:22px; }}
    .bar-track {{ height:24px; border:1.5px solid var(--line); background:#eee4ce; }}
    .bar-fill {{ height:100%; background:var(--lime); }}
    .bar-fill.blue {{ background:var(--blue); }} .bar-fill.red {{ background:var(--red); }} .bar-fill.orange {{ background:var(--orange); }} .bar-fill.purple {{ background:var(--purple); }} .bar-fill.ink {{ background:#1d1c18; }} .bar-fill.muted {{ background:#9e988c; }}
    .bar-label {{ font-weight:700; line-height:1.12; }} .bar-value {{ font-weight:800; text-align:right; font-size:24px; }}
    table {{ width:100%; border-collapse:collapse; font-size:18px; line-height:1.14; }}
    th, td {{ border-bottom:1.5px solid rgba(42,41,36,.35); text-align:left; padding:9px 9px 9px 0; vertical-align:top; }}
    th {{ font-size:15px; text-transform:uppercase; letter-spacing:.08em; color:#4a463c; }}
    .pill-row {{ display:flex; gap:12px; flex-wrap:wrap; }}
    .pill {{ border:1.5px solid var(--line); border-radius:999px; padding:9px 13px; background:#f8f1db; font-size:18px; font-weight:800; }}
    .callout {{ font-size:25px; line-height:1.25; font-weight:750; background:#eef8bd; }}
    .slide-num {{ position:absolute; right:72px; bottom:35px; font-size:15px; color:#5d574d; z-index:2; }}
    .small {{ font-size:19px; color:#4b463d; line-height:1.3; }}
    .footer-note {{ margin-top:auto; font-size:17px; color:#5b554b; }}
    @page {{ size:1600px 900px; margin:0; }}
    @media print {{ body {{ background:white; }} .deck {{ margin:0; }} .slide {{ border:0; }} }}
  </style>
</head>
<body>
<main class="deck">
  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">ADA 2026 abstracts and posters | local-corpus AI topic scan</div>
      <h1>AI topics cluster around glucose automation, prediction, GenAI, and discovery workflows</h1>
      <p class="lede">Full scan of {source_count:,} ADA 2026 publication records from the local archive, separating explicit AI/ML records from adjacent algorithmic diabetes-technology records.</p>
      <div class="metrics">
        {metric("total source records screened", source_count, "ADA local publication archive")}
        {metric("explicit AI/ML records", class_counts.get("explicit AI/ML", 0), "direct AI, ML, LLM, NLP, or image-AI language")}
        {metric("AI-adjacent records", class_counts.get("AI-adjacent algorithmic/digital", 0), "AID, closed-loop, algorithm, or digital-biomarker language")}
        {metric("retained records", len(records), "deduped companion CSV rows")}
      </div>
      <div class="callout">The strongest explicit signal is applied ML in prediction and omics; the broadest adjacent signal is automated insulin delivery and closed-loop glucose management.</div>
      <div class="footer-note">Source: {esc(SOURCE_JSON)} | scraped {esc(scraped_at)} | generated {esc(generated)}</div>
    </div>
    <div class="slide-num">01 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">Scope and classification</div>
      <h2>Explicit AI/ML is the primary readout; AID and closed-loop records are a separate adjacent layer</h2>
      <div class="grid two">
        <div class="panel"><h3>Explicit AI/ML</h3><ul><li>Artificial intelligence, AI-based / AI-enabled / AI-derived, AI/ML, machine learning, deep learning, neural-network, LLM, GPT/OpenAI, GenAI, RAG, NLP, and image-AI terms.</li><li>Used for conference-topic interpretation and method/tool assessment.</li><li>Includes both substantive AI products and AI as an analytic method.</li></ul></div>
        <div class="panel"><h3>AI-adjacent algorithmic/digital</h3><ul><li>Automated insulin delivery, hybrid or fully closed-loop systems, AID algorithms, digital twins, digital biomarkers, predictive algorithms, and automated AGP interpretation without explicit AI/ML terms.</li><li>Reported separately to avoid overstating AI volume.</li><li>Generic modeling, simulations, surveys, and diabetes-technology adoption were excluded unless the source framed an AI or algorithmic workflow.</li></ul></div>
      </div>
      <div class="callout">Run mode: full local-corpus scan. No fresh web re-check or source screenshot audit was performed.</div>
    </div>
    <div class="slide-num">02 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">Topic map</div>
      <h2>Topic clusters show a device-heavy adjacent layer and a broad explicit AI/ML research layer</h2>
      <div class="grid two">
        <div class="panel"><h3>Non-exclusive topic clusters</h3><div class="bar-list">{bar_rows(topic_counts)}</div></div>
        <div class="panel"><h3>AI role taxonomy</h3><div class="bar-list">{bar_rows(role_counts, 6)}</div></div>
      </div>
      <div class="pill-row">
        <span class="pill">{class_counts.get("explicit AI/ML", 0)} explicit AI/ML</span>
        <span class="pill">{class_counts.get("AI-adjacent algorithmic/digital", 0)} adjacent algorithmic/digital</span>
        <span class="pill">{session_counts.get("Oral Presentations", 0)} oral presentations</span>
        <span class="pill">{session_counts.get("Late Breaking Poster Session", 0)} late-breaking posters</span>
      </div>
    </div>
    <div class="slide-num">03 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">Generative AI and agents</div>
      <h2>LLM work is visible, but most examples remain constrained to bounded support tasks</h2>
      <div class="grid two">
        <div class="panel"><h3>What appeared</h3><ul><li>Diabetes self-management agents, evidence-citing treatment decisions, pharmacotherapy recommendation testing, dietary advice, carbohydrate counting, and previsit workflow efficiency.</li><li>RAG-assisted interpretation and natural-language queries also appeared in research infrastructure contexts.</li><li>Several studies included human validation or expert-comparison framing rather than autonomous clinical authority.</li></ul></div>
        <div class="panel"><h3>Representative records</h3><table><thead><tr><th>ID</th><th>Topic</th><th>Role</th></tr></thead><tbody>{card_list(gen)}</tbody></table></div>
      </div>
    </div>
    <div class="slide-num">04 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">Prediction and clinical risk</div>
      <h2>Applied ML is used for risk stratification, utilization, glycemic trajectories, and precision screening</h2>
      <div class="grid two">
        <div class="panel"><h3>Common use cases</h3><ul><li>Acute-care utilization, inpatient hypoglycemia, HbA1c trajectories, T2D prediction, diabetes complications, G6PD carrier flagging, and race-specific insulin-sensitivity estimation.</li><li>Population-scale EHR and claims-linked cohorts are a recurring data source.</li><li>Fairness, calibration, and subgroup validation appear as explicit methodological concerns in selected abstracts.</li></ul></div>
        <div class="panel"><h3>Representative records</h3><table><thead><tr><th>ID</th><th>Topic</th><th>Role</th></tr></thead><tbody>{card_list(pred)}</tbody></table></div>
      </div>
    </div>
    <div class="slide-num">05 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">CGM, forecasting, and AID</div>
      <h2>Automated insulin delivery is the largest adjacent algorithmic footprint</h2>
      <div class="grid two">
        <div class="panel"><h3>Readout</h3><ul><li>The adjacent layer is dominated by automated insulin delivery, hybrid closed-loop, advanced hybrid closed-loop, open-source AID, and device-algorithm studies.</li><li>Explicit AI/ML overlaps with CGM through real-time glucose prediction, CGM pattern interpretation, and AI-enabled continuous-glucose-monitoring platforms.</li><li>This layer should be read as algorithmic diabetes technology, not as uniformly explicit AI research.</li></ul></div>
        <div class="panel"><h3>Representative adjacent records</h3><table><thead><tr><th>ID</th><th>Topic</th><th>Role</th></tr></thead><tbody>{card_list(aid)}</tbody></table></div>
      </div>
    </div>
    <div class="slide-num">06 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">Behavior, nutrition, and remote care</div>
      <h2>AI-enabled behavior work connects meal data, engagement patterns, and remote-care operations</h2>
      <div class="grid two">
        <div class="panel"><h3>Behavior and nutrition</h3><ul><li>AI-based meal logging, GenAI dietary advice, fiber-intake behavior change, carbohydrate estimation, and smart-ring nutrition analysis appeared as practical digital-health use cases.</li><li>Digital biomarkers and ePRO integration broadened the signal into early-phase obesity-trial operations.</li></ul></div>
        <div class="panel"><h3>Representative records</h3><table><thead><tr><th>ID</th><th>Topic</th><th>Role</th></tr></thead><tbody>{card_list(behavior)}</tbody></table></div>
      </div>
    </div>
    <div class="slide-num">07 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">Omics, biomarkers, and discovery</div>
      <h2>AI/ML is being applied upstream in diabetes endotyping and metabolic drug discovery</h2>
      <div class="grid two">
        <div class="panel"><h3>Research layer</h3><ul><li>Examples include deep-learning multiomics, kinase-activity inference, AI-guided natural inhibitor identification, machine-learning platforms for ActR2 antibody design, AI-assisted structure-based drug discovery, and AI-ready datasets.</li><li>Several records are method-heavy, where AI is the analytic engine rather than the clinical intervention.</li></ul></div>
        <div class="panel"><h3>Representative records</h3><table><thead><tr><th>ID</th><th>Topic</th><th>Role</th></tr></thead><tbody>{card_list(omics)}</tbody></table></div>
      </div>
    </div>
    <div class="slide-num">08 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">Imaging and implementation</div>
      <h2>Smaller clusters point to deployable visual AI and operational workflow uses</h2>
      <div class="grid two">
        <div class="panel"><h3>Imaging and visual AI</h3><ul><li>AI-derived retinal biomarkers, autonomous AI for diabetic eye exams, image analysis with AI, CT imaging biomarkers, and high-content image analysis appear across clinical and discovery settings.</li><li>The imaging signal is smaller than CGM or prediction, but closer to concrete workflow deployment.</li></ul></div>
        <div class="panel"><h3>Representative records</h3><table><thead><tr><th>ID</th><th>Topic</th><th>Role</th></tr></thead><tbody>{card_list(imaging)}</tbody></table></div>
      </div>
      <div class="callout">Implementation-oriented records include rural-care innovation, DKA protocol adherence, health-system AI workflows, and human-reviewed qualitative theme generation.</div>
    </div>
    <div class="slide-num">09 / 10</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="content">
      <div class="eyebrow">Outputs and caveats</div>
      <h2>The companion CSV is the record-level source map for the topic summary</h2>
      <div class="grid two">
        <div class="panel"><h3>Delivered artifacts</h3><ul><li><strong>ada_2026_ai_records.csv</strong>: retained records with classification, AI role, topic clusters, source excerpt, session metadata, and local source path.</li><li><strong>source_notes.md</strong>: corpus, scrape timestamp, inclusion rules, counts, and caveats.</li><li><strong>ada_2026_ai_topics_cohere_ci.html/pdf</strong>: Cohere-style CI summary deck.</li></ul></div>
        <div class="panel"><h3>Interpretation caveats</h3><ul><li>Counts are lexical and rule-based; they are suitable for descriptive CI triage, not formal bibliometrics.</li><li>Topic clusters are non-exclusive, so cluster counts sum above retained-record counts.</li><li>AID and closed-loop records are reported separately because they are algorithmic diabetes technology even when not source-framed as AI/ML.</li></ul></div>
      </div>
      <div class="callout">Bottom line: ADA 2026 presents AI as both a research method and a care-delivery technology layer, with the most commercial-near activity around glucose automation, prediction, decision support, and digital coaching.</div>
    </div>
    <div class="slide-num">10 / 10</div>
  </article>
</main>
</body>
</html>
"""
    HTML_OUT.write_text(html_text, encoding="utf-8")


def main():
    if not SOURCE_JSON.exists():
        raise FileNotFoundError(SOURCE_JSON)
    rows = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8")) if SUMMARY_JSON.exists() else {}

    bg_source = ROOT / "tan_slide_background.png"
    if not bg_source.exists():
        repo_bg = Path(r"C:\Users\Justin\Desktop\linkedin-posts-mac\outputs\ada_2026_ai_topics\tan_slide_background.png")
        if repo_bg.exists() and repo_bg != BG_OUT:
            shutil.copyfile(repo_bg, BG_OUT)

    records = []
    seen = set()
    for row in rows:
        abstract_number = str(row.get("abstract_number", "")).strip()
        if not abstract_number or abstract_number in seen:
            continue
        result = classify(row)
        if not result:
            continue
        title = clean_title(row)
        record = {
            "abstract_number": abstract_number,
            "title": title,
            "classification": result["classification"],
            "ai_role": result["ai_role"],
            "matched_terms": result["matched_terms"],
            "topic_clusters": topic_clusters(row, result["classification"]),
            "source_excerpt": result["source_excerpt"],
            "session_type": row.get("session_type", ""),
            "session_date": row.get("session_date", ""),
            "session_start": row.get("session_start", ""),
            "session_location": row.get("session_location", ""),
            "local_source_path": f"{SOURCE_JSON}#{abstract_number}",
            "mediaurl": row.get("mediaurl", ""),
            "authors": row.get("authors", ""),
        }
        records.append(record)
        seen.add(abstract_number)

    write_csv(records)
    write_notes(records, len(rows), summary)
    write_html(records, len(rows), summary)

    print(f"records={len(records)}")
    print(Counter(r["classification"] for r in records))
    print(CSV_OUT)
    print(HTML_OUT)


if __name__ == "__main__":
    main()
