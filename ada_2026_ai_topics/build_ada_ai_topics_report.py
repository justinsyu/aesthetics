import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ada_2026_ai_topics"
SOURCES = OUT / "sources"
SCREENSHOTS = OUT / "screenshots"
SOURCE_JSON = Path(r"C:\Users\Justin\Desktop\ada-2026\ada26_publications.json")
SOURCE_MD = Path(r"C:\Users\Justin\Desktop\ada-2026\assets\data\ada26_publications.md")
SOURCE_SITE = Path(r"C:\Users\Justin\Desktop\ada-2026\index.html")
PLANNER_ROOT = "https://eppro02.ativ.me/web/planner.php?id=ADA26"
EVENTPILOT_URL = "https://eppro02.ativ.me/web/page.php?nav=false&page=Session&project=ADA26&id={agenda_id}&plannersession=true&eptable=agenda"


PATTERNS = {
    "artificial_intelligence": re.compile(r"artificial intelligence", re.I),
    "ai_acronym": re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])"),
    "machine_learning": re.compile(r"machine[- ]learning", re.I),
    "ml_abbrev": re.compile(r"(?<![A-Za-z])ML(?![A-Za-z])"),
    "deep_learning": re.compile(r"deep[- ]learning", re.I),
    "large_language_models": re.compile(r"large language models?|(?<![A-Za-z])LLMs(?![A-Za-z])", re.I),
    "nlp": re.compile(r"natural language processing|(?<![A-Za-z])NLP(?![A-Za-z])", re.I),
    "computer_vision": re.compile(r"computer vision", re.I),
    "neural_network": re.compile(
        r"neural network|convolutional neural|(?<![A-Za-z])CNN(?![A-Za-z])|transformer[- ]based|\btransformer\b",
        re.I,
    ),
    "specific_ml_algorithm": re.compile(
        r"XGBoost|CatBoost|LightGBM|random forest|support vector machine|(?<![A-Za-z])SVM(?![A-Za-z])|gradient boosting",
        re.I,
    ),
    "chatbot_generative_ai": re.compile(r"chatbot|ChatGPT|generative AI|GenAI"),
    "predictive_modeling": re.compile(
        r"predictive modeling|predictive models?|prediction models?|risk prediction model|models? (?:to )?predict|"
        r"develop(?:ed)? (?:a |an )?.{0,80}model.{0,80}predict|predict(?:ing|ion).{0,80}using",
        re.I,
    ),
}

INVALID_AI_CONTEXTS = [
    re.compile(r"American Indian/Alaska Native \(AI/AN\)", re.I),
    re.compile(r"\bAI/AN\b"),
    re.compile(r"adrenal insufficiency \(AI\)", re.I),
    re.compile(r"patients with AI", re.I),
    re.compile(r"the AI group", re.I),
]

DIRECT_AI_TERMS = {
    "artificial_intelligence",
    "ai_acronym",
    "machine_learning",
    "ml_abbrev",
    "deep_learning",
    "large_language_models",
    "nlp",
    "computer_vision",
    "neural_network",
    "specific_ml_algorithm",
    "chatbot_generative_ai",
}


def esc(value):
    return html.escape(str(value or ""), quote=True)


def read_records():
    return json.loads(SOURCE_JSON.read_text(encoding="utf-8"))


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def record_text(record):
    parts = []
    for key in ("title", "abstract_text", "raw_name"):
        value = record.get(key)
        if isinstance(value, str):
            parts.append(value)
    sections = record.get("sections")
    if isinstance(sections, dict):
        parts.extend(str(value) for value in sections.values())
    return "\n".join(parts)


def ai_context_is_invalid(text):
    ai_hits = list(PATTERNS["ai_acronym"].finditer(text))
    if not ai_hits:
        return False
    for hit in ai_hits:
        snippet = text[max(0, hit.start() - 90) : hit.end() + 90]
        if not any(pattern.search(snippet) for pattern in INVALID_AI_CONTEXTS):
            return False
    return True


def term_hits(record):
    text = record_text(record)
    hits = [name for name, pattern in PATTERNS.items() if pattern.search(text)]
    if "ai_acronym" in hits and ai_context_is_invalid(text):
        hits.remove("ai_acronym")
    return hits


def first_trigger(record, hits):
    text = record_text(record).replace("\n", " ")
    for hit_name in hits:
        match = PATTERNS[hit_name].search(text)
        if match:
            start = max(0, match.start() - 115)
            end = min(len(text), match.end() + 210)
            return " ".join(text[start:end].split())
    return ""


def short_title(title):
    return re.sub(r"^\s*[\w-]+ - ", "", title or "").strip()


def planner_url(record):
    agenda_id = record.get("matched_agenda_id") or record.get("session_link_id") or ""
    if agenda_id:
        return EVENTPILOT_URL.format(agenda_id=agenda_id)
    return PLANNER_ROOT


def local_locator(record):
    return f"{SOURCE_JSON}#mediaid={record.get('mediaid')};abstract_number={record.get('abstract_number')}"


def section_value(record, section_name):
    sections = record.get("sections")
    if isinstance(sections, dict):
        for key, value in sections.items():
            if key.lower() == section_name.lower():
                return str(value)
    return ""


def clip_sentence(text, limit=310):
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "..."


def summary_for(record):
    conclusion = section_value(record, "Conclusion")
    results = section_value(record, "Results")
    methods = section_value(record, "Methods")
    intro = section_value(record, "Introduction and Objective")
    source = conclusion or results or methods or intro or record.get("abstract_text") or short_title(record.get("title"))
    return clip_sentence(source, 330)


def classify_category(record, hits):
    title_text = (record.get("title", "") + " " + record.get("abstract_text", "")).lower()
    if {"large_language_models", "chatbot_generative_ai"} & set(hits):
        return "LLM and generative AI"
    if "nlp" in hits:
        return "NLP and social listening"
    if re.search(
        r"\b(retinal|imaging|image|images|segmentation|mri|qupath)\b|food image|ct scans?|ct imaging|computed tomography|abdominal ct",
        title_text,
    ):
        return "AI imaging and computer vision"
    if any(
        term in title_text
        for term in [
            "omics",
            "genetic",
            "variant",
            "molecular",
            "drug discovery",
            "in vivo validation",
            "gwas",
            "islet",
            "beta-cell",
            "proteomic",
            "metabolomic",
            "immune repertoire",
            "extracellular vesicle",
            "single-cell",
        ]
    ):
        return "Omics, discovery, and translational science"
    if any(term in title_text for term in ["cluster", "subtyp", "phenotyp", "endotype"]):
        return "Clustering and phenotyping"
    if any(term in title_text for term in ["meal logging", "mobile app", "smart-ring", "previsit", "coaching", "dietary advice", "ai-enabled weight management", "digital engagement"]):
        return "Digital health and behavior"
    if any(term in title_text for term in ["clinical decision", "pharmacotherapy", "protocol", "misclassified", "insulin delivery"]):
        return "Clinical workflow and decision support"
    if "predictive_modeling" in hits or any(term in title_text for term in ["predict", "forecast", "risk model", "risk score"]):
        return "Predictive analytics and risk models"
    if {"machine_learning", "ml_abbrev", "deep_learning", "specific_ml_algorithm", "neural_network"} & set(hits):
        return "ML analytic methods"
    return "AI infrastructure and data resources"


def topic_from_text(text):
    if not text:
        return None
    text = text.lower()
    title_rules = [
        ("Eye and retinal complications", r"\b(retinal|retinopathy|eye exams?|ophthalmology|vision)\b"),
        ("Kidney disease", r"\b(kidney|renal|egfr|uacr|albuminuria|dkd|nephropathy)\b"),
        ("Diabetic foot and wounds", r"\b(foot ulcers?|diabetic foot|wounds?|wound healing)\b"),
        ("Gestational diabetes and pregnancy", r"\b(gestational|gdm|pregnan|first-trimester|lga)\b"),
        ("Muscle, lean mass, and sarcopenia", r"\b(sarcopenia|lean mass|skeletal muscle|myoblast|muscle function|muscle mass)\b"),
        ("Obesity and GLP-1 therapy", r"\b(obesity|overweight|weight loss|weight management|adiposity|glp-?1|glp-?1ra|semaglutide|tirzepatide|mazdutide|orforglipron)\b"),
        ("Islet and pancreatic biology", r"\b(islets?|beta-?cells?|β-?cells?|pancreas|pancreatic)\b"),
        ("Cardiovascular risk", r"\b(cardiovascular|cvd|ascvd|heart failure|coronary|atherosclerosis)\b"),
        ("Type 1 diabetes", r"\b(type 1 diabetes|t1d|stage 3 type 1|autoimmune diabetes)\b"),
        ("Type 2 diabetes", r"\b(type 2 diabetes|t2d|t2dm)\b"),
        ("Glycemia, CGM, and insulin", r"\b(hypoglycemia|hyperglycemia|glycemic|glucose|cgm|insulin|hba1c|time in range|tir)\b"),
    ]
    for label, pattern in title_rules:
        if re.search(pattern, text):
            return label
    return None


def classify_topic(record):
    title = short_title(record.get("title"))
    title_topic = topic_from_text(title)
    if title_topic:
        return title_topic

    objective_topic = topic_from_text(section_value(record, "Introduction and Objective"))
    if objective_topic:
        return objective_topic

    abstract_topic = topic_from_text(record.get("abstract_text", ""))
    if abstract_topic:
        return abstract_topic

    return "General diabetes/metabolic science"


def classify_ai_role(hits):
    hit_set = set(hits)
    if hit_set <= {"predictive_modeling"}:
        return "AI-adjacent predictive analytics"
    if "predictive_modeling" in hit_set and hit_set & DIRECT_AI_TERMS:
        return "AI/ML predictive model"
    if hit_set & {"large_language_models", "chatbot_generative_ai"}:
        return "Generative AI or LLM"
    if hit_set & {"deep_learning", "neural_network", "computer_vision"}:
        return "Deep learning or vision model"
    if hit_set & {"machine_learning", "ml_abbrev", "specific_ml_algorithm"}:
        return "Machine-learning method"
    if "nlp" in hit_set:
        return "NLP text analytics"
    return "AI-enabled workflow or resource"


def build_screen(records):
    candidate_rows = []
    retained = []
    for record in records:
        hits = term_hits(record)
        raw_hits = [name for name, pattern in PATTERNS.items() if pattern.search(record_text(record))]
        if not raw_hits:
            continue
        included = bool(hits)
        if hits == ["predictive_modeling"]:
            inclusion_tier = "predictive_only"
        elif hits:
            inclusion_tier = "direct_ai_ml"
        else:
            inclusion_tier = "excluded_context"
        base = {
            "mediaid": record.get("mediaid"),
            "abstract_number": record.get("abstract_number"),
            "title": record.get("title"),
            "raw_hits": "; ".join(raw_hits),
            "accepted_hits": "; ".join(hits),
            "included": "yes" if included else "no",
            "inclusion_tier": inclusion_tier,
            "exclusion_reason": "" if included else "AI acronym used in a non-artificial-intelligence context, such as AI/AN or adrenal insufficiency.",
            "trigger_snippet": first_trigger(record, raw_hits),
        }
        candidate_rows.append(base)
        if included:
            retained.append((record, hits))
    return candidate_rows, retained


def normalize_retained(retained):
    rows = []
    retained = sorted(retained, key=lambda item: (str(item[0].get("abstract_number") or ""), int(item[0].get("mediaid") or 0)))
    for index, (record, hits) in enumerate(retained, start=1):
        source_id = f"R{index:03d}"
        sections = record.get("sections") if isinstance(record.get("sections"), dict) else {}
        rows.append(
            {
                "source_id": source_id,
                "ref_number": index,
                "mediaid": record.get("mediaid"),
                "abstract_number": record.get("abstract_number"),
                "title": short_title(record.get("title")),
                "full_title": record.get("title"),
                "authors": record.get("authors"),
                "session_type": record.get("session_type"),
                "session_date": record.get("session_date"),
                "session_start": record.get("session_start"),
                "session_stop": record.get("session_stop"),
                "session_location": record.get("session_location"),
                "matched_agenda_id": record.get("matched_agenda_id"),
                "session_link_id": record.get("session_link_id"),
                "eventpilot_url": planner_url(record),
                "local_record_locator": local_locator(record),
                "accepted_hits": "; ".join(hits),
                "ai_role": classify_ai_role(hits),
                "category": classify_category(record, hits),
                "topic_area": classify_topic(record),
                "trigger_snippet": first_trigger(record, hits),
                "summary": summary_for(record),
                "introduction_objective": sections.get("Introduction and Objective", ""),
                "methods": sections.get("Methods", ""),
                "results": sections.get("Results", ""),
                "conclusion": sections.get("Conclusion", ""),
                "abstract_text": record.get("abstract_text", ""),
            }
        )
    return rows


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def count_rows(rows, field):
    return Counter(row[field] for row in rows)


def sample_rows(rows, predicate, limit=5):
    out = [row for row in rows if predicate(row)]
    return out[:limit]


def cite(row):
    return f'<a class="cite" href="{esc(row["eventpilot_url"])}">{esc(row["source_id"])}</a>'


def bar_list(counter, total, max_items=8):
    items = counter.most_common(max_items)
    html_rows = []
    for label, count in items:
        pct = count / total * 100 if total else 0
        html_rows.append(
            f'<div class="bar-row"><div class="bar-label">{esc(label)}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{pct:.1f}%"></div></div>'
            f'<div class="bar-count">{count}</div></div>'
        )
    return "\n".join(html_rows)


def mini_table(rows):
    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td>{cite(row)}</td>"
            f"<td>{esc(row['abstract_number'])}</td>"
            f"<td>{esc(row['title'])}</td>"
            f"<td>{esc(row['topic_area'])}</td>"
            "</tr>"
        )
    return '<table class="mini"><thead><tr><th>Ref</th><th>No.</th><th>Record</th><th>Topic</th></tr></thead><tbody>' + "\n".join(body) + "</tbody></table>"


def card_grid(rows, limit=6):
    cards = []
    for row in rows[:limit]:
        cards.append(
            f'<article class="record-card"><div class="record-top"><span>{cite(row)}</span><span>{esc(row["abstract_number"])}</span></div>'
            f'<h3>{esc(row["title"])}</h3><p>{esc(clip_sentence(row["summary"], 160))}</p>'
            f'<div class="tagline">{esc(row["category"])} | {esc(row["topic_area"])}</div></article>'
        )
    return '<div class="record-grid">' + "\n".join(cards) + "</div>"


def write_source_log(rows, candidates, records):
    category_counts = count_rows(rows, "category")
    topic_counts = count_rows(rows, "topic_area")
    role_counts = count_rows(rows, "ai_role")
    lines = [
        "# ADA 2026 AI Topics Source Log",
        "",
        "## Corpus",
        "",
        f"- Source JSON: `{SOURCE_JSON}`",
        f"- Markdown export: `{SOURCE_MD}`",
        f"- Local static search page: `{SOURCE_SITE}`",
        f"- Source planner root: {PLANNER_ROOT}",
        f"- Records screened in this build: {len(records)}.",
        f"- Lexical candidate records: {len(candidates)}.",
        f"- Retained AI/ML/predictive-model records: {len(rows)}.",
        "- Source basis: local ADA 2026 archive fields, including abstract number, media ID, matched agenda ID, session metadata, abstract sections, and EventPilot session URL pattern.",
        "",
        "## Inclusion Logic",
        "",
        "- Included records with explicit artificial intelligence, AI, machine learning, ML, deep learning, large language models, generative AI, chatbots, NLP, neural-network/transformer methods, named ML algorithms, or explicit predictive-modeling language.",
        "- Predictive-only records are retained as a separate AI-adjacent tier and should not be read as direct use of AI unless the row also has AI/ML terms.",
        "- Excluded non-AI acronym contexts, including American Indian/Alaska Native (AI/AN) and adrenal insufficiency (AI), unless another AI/ML term independently supported retention.",
        "- No web screenshots were collected because the requested source of truth is a local conference dataset; row-level evidence text and local record locators are preserved in retained CSV/JSON instead.",
        "",
        "## Search Terms",
        "",
        "`artificial intelligence`, standalone `AI`, `machine learning`, standalone `ML`, `deep learning`, `large language model(s)`, `LLMs`, `natural language processing`, `NLP`, `computer vision`, `neural network`, `CNN`, `transformer`, `XGBoost`, `CatBoost`, `LightGBM`, `random forest`, `support vector machine`, `SVM`, `gradient boosting`, `chatbot`, `ChatGPT`, `generative AI`, `GenAI`, `predictive model`, `prediction model`, `risk prediction model`, and model-to-predict phrases.",
        "",
        "## Counts",
        "",
        "### AI Role",
        "",
    ]
    for label, count in role_counts.most_common():
        lines.append(f"- {label}: {count}")
    lines.extend(["", "### Category", ""])
    for label, count in category_counts.most_common():
        lines.append(f"- {label}: {count}")
    lines.extend(["", "### Topic Area", ""])
    for label, count in topic_counts.most_common():
        lines.append(f"- {label}: {count}")
    lines.extend(["", "## Retained References", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['source_id']} | {row['abstract_number']} | Media ID {row['mediaid']}",
                "",
                f"- Title: {row['title']}",
                f"- Category: {row['category']}",
                f"- AI role: {row['ai_role']}",
                f"- Topic area: {row['topic_area']}",
                f"- Session: {row['session_type']} | {row['session_date']} {row['session_start']} | {row['session_location']}",
                f"- EventPilot URL: {row['eventpilot_url']}",
                f"- Local locator: `{row['local_record_locator']}`",
                f"- Trigger snippet: {row['trigger_snippet']}",
                f"- Summary: {row['summary']}",
                "",
            ]
        )
    path = SOURCES / "source-log.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_reference_csv(rows):
    path = SOURCES / "reference-screenshots.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["label", "path", "caption"])
        writer.writeheader()
        writer.writerow(
            {
                "label": "Local archive evidence",
                "path": "",
                "caption": "No web screenshots collected; ADA 2026 local archive fields and retained-record exports provide row-level source evidence.",
            }
        )
    return path


def write_html_report(rows, candidates, records):
    total = len(rows)
    direct_count = sum(1 for row in rows if row["ai_role"] != "AI-adjacent predictive analytics")
    predictive_only = total - direct_count
    category_counts = count_rows(rows, "category")
    topic_counts = count_rows(rows, "topic_area")
    role_counts = count_rows(rows, "ai_role")
    session_counts = count_rows(rows, "session_type")
    lb_count = sum(1 for row in rows if "Late" in str(row["session_type"]) or "ePoster" in str(row["session_type"]))

    llm_rows = sample_rows(rows, lambda row: row["category"] == "LLM and generative AI", 6)
    workflow_rows = sample_rows(rows, lambda row: row["category"] in {"Digital health and behavior", "Clinical workflow and decision support"}, 6)
    science_rows = sample_rows(rows, lambda row: row["category"] in {"Omics, discovery, and translational science", "AI imaging and computer vision", "Clustering and phenotyping"}, 6)
    predictive_rows = sample_rows(rows, lambda row: row["category"] == "Predictive analytics and risk models", 6)

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ADA 2026 AI Topics CI Report</title>
  <style>
    @page {{ size: 16in 9in; margin: 0; }}
    :root {{
      --paper: #f3eadb;
      --paper-2: #efe1c9;
      --ink: #191714;
      --muted: #6f675c;
      --line: #d0bfa4;
      --lime: #d9ff4a;
      --green: #35624d;
      --rose: #a85045;
      --blue: #3f5f8f;
      --charcoal: #201d19;
      --white: #fffaf1;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--charcoal); color: var(--ink); font-family: Inter, Arial, sans-serif; }}
    a {{ color: inherit; text-decoration: none; }}
    .deck {{ width: 16in; margin: 0 auto; }}
    .slide {{
      width: 16in; height: 9in; page-break-after: always; position: relative; overflow: hidden;
      padding: .58in .68in .5in .68in; background: var(--paper);
      display: flex; flex-direction: column; gap: .24in;
    }}
    .slide.dark {{ background: var(--charcoal); color: var(--white); }}
    .slide::before {{
      content: ""; position: absolute; inset: 0; pointer-events: none;
      background-image: radial-gradient(circle at 1px 1px, rgba(25,23,20,.18) 1px, transparent 0);
      background-size: 22px 22px; opacity: .13;
    }}
    .dark::before {{ opacity: .1; background-image: radial-gradient(circle at 1px 1px, rgba(255,250,241,.22) 1px, transparent 0); }}
    .content {{ position: relative; z-index: 1; display: flex; flex-direction: column; gap: .22in; height: 100%; }}
    .kicker {{ display: flex; align-items: center; gap: .12in; font-size: .16in; font-weight: 800; text-transform: uppercase; color: var(--green); letter-spacing: 0; }}
    .dark .kicker {{ color: var(--lime); }}
    .kicker::before {{ content: ""; width: .38in; height: .08in; background: var(--lime); border: 1px solid var(--ink); }}
    h1 {{ margin: 0; font-size: .78in; line-height: .92; letter-spacing: 0; max-width: 12.7in; }}
    h2 {{ margin: 0; font-size: .42in; line-height: 1.02; letter-spacing: 0; }}
    h3 {{ margin: 0; font-size: .19in; line-height: 1.12; letter-spacing: 0; }}
    p {{ margin: 0; font-size: .17in; line-height: 1.38; color: var(--muted); }}
    .dark p {{ color: #d9d0c1; }}
    .dek {{ font-size: .24in; line-height: 1.25; max-width: 12.2in; color: #4c463d; }}
    .dark .dek {{ color: #ece3d4; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: .18in; }}
    .metric {{ border: 1.5px solid var(--ink); background: var(--white); padding: .18in; min-height: 1.25in; display: flex; flex-direction: column; justify-content: space-between; }}
    .dark .metric {{ background: #302b25; border-color: #746a5c; }}
    .metric .value {{ font-size: .46in; font-weight: 900; line-height: .9; }}
    .metric .label {{ font-size: .15in; line-height: 1.22; color: var(--muted); }}
    .dark .metric .label {{ color: #d9d0c1; }}
    .two {{ display: grid; grid-template-columns: 1fr 1fr; gap: .24in; flex: 1; min-height: 0; }}
    .three {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .2in; flex: 1; min-height: 0; }}
    .panel {{ border: 1.5px solid var(--line); background: rgba(255,250,241,.72); padding: .2in; min-height: 0; }}
    .dark .panel {{ background: rgba(255,250,241,.06); border-color: #5c554c; }}
    .panel h3 {{ margin-bottom: .1in; }}
    .callout {{ border-left: .1in solid var(--lime); padding: .18in .22in; background: rgba(255,250,241,.78); max-width: 12.6in; }}
    .dark .callout {{ background: rgba(255,250,241,.08); }}
    .bar-row {{ display: grid; grid-template-columns: 2.55in 1fr .35in; align-items: center; gap: .12in; margin: .095in 0; }}
    .bar-label {{ font-size: .145in; line-height: 1.12; }}
    .bar-track {{ height: .14in; border: 1px solid var(--line); background: rgba(255,255,255,.48); }}
    .bar-fill {{ height: 100%; background: var(--green); }}
    .dark .bar-fill {{ background: var(--lime); }}
    .bar-count {{ font-size: .15in; font-weight: 800; text-align: right; }}
    .record-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .16in; }}
    .record-card {{ border: 1.4px solid var(--line); background: rgba(255,250,241,.78); padding: .16in; min-height: 1.55in; display: flex; flex-direction: column; gap: .075in; }}
    .dark .record-card {{ background: rgba(255,250,241,.08); border-color: #5c554c; }}
    .record-card p {{ font-size: .125in; line-height: 1.25; }}
    .record-top {{ display: flex; justify-content: space-between; align-items: center; font-size: .12in; font-weight: 800; color: var(--green); }}
    .dark .record-top {{ color: var(--lime); }}
    .tagline {{ margin-top: auto; font-size: .11in; color: var(--muted); line-height: 1.15; }}
    .dark .tagline {{ color: #cfc5b7; }}
    .cite {{ display: inline-block; background: var(--lime); color: var(--ink); border: 1px solid var(--ink); padding: .015in .055in; font-size: .105in; font-weight: 900; }}
    table.mini {{ width: 100%; border-collapse: collapse; font-size: .123in; line-height: 1.18; }}
    table.mini th, table.mini td {{ border-bottom: 1px solid var(--line); padding: .075in .05in; text-align: left; vertical-align: top; }}
    table.mini th {{ font-size: .105in; text-transform: uppercase; color: var(--muted); }}
    .foot {{ position: absolute; left: .68in; right: .68in; bottom: .26in; display: flex; justify-content: space-between; color: var(--muted); font-size: .105in; z-index: 2; }}
    .dark .foot {{ color: #c7bbaa; }}
    .pill-row {{ display: flex; flex-wrap: wrap; gap: .09in; }}
    .pill {{ border: 1px solid var(--ink); background: var(--lime); padding: .045in .085in; font-size: .12in; font-weight: 800; }}
    .method-list {{ display: grid; gap: .12in; }}
    .method-list div {{ border-left: .08in solid var(--green); padding-left: .13in; font-size: .17in; line-height: 1.3; }}
    .dark .method-list div {{ border-color: var(--lime); }}
  </style>
</head>
<body>
<main class="deck">
  <section class="slide dark">
    <div class="content">
      <div class="kicker">ADA 2026 Scientific Sessions | Local corpus scan</div>
      <h1>AI topics appear across care delivery, LLMs, imaging, omics, and predictive modeling</h1>
      <p class="dek">Screened all {len(records):,} local ADA abstract/poster records for explicit AI, ML, deep learning, LLM, NLP, computer-vision, named ML-algorithm, and predictive-modeling topics. Predictive-only records are retained but labeled separately.</p>
      <div class="metrics">
        <div class="metric"><div class="value">{total}</div><div class="label">retained AI/ML/predictive-model records</div></div>
        <div class="metric"><div class="value">{direct_count}</div><div class="label">direct AI/ML/NLP/LLM/deep-learning records</div></div>
        <div class="metric"><div class="value">{predictive_only}</div><div class="label">predictive-only AI-adjacent records</div></div>
        <div class="metric"><div class="value">{lb_count}</div><div class="label">late-breaking or ePoster retained records</div></div>
      </div>
      <div class="callout"><p>Full-run label: all records in <code>{esc(str(SOURCE_JSON))}</code> were screened. Source citations use local record IDs plus EventPilot session URLs generated from ADA agenda IDs.</p></div>
    </div>
    <div class="foot"><span>cohere-style-ci local archive adaptation</span><span>1</span></div>
  </section>

  <section class="slide">
    <div class="content">
      <div class="kicker">Screening method</div>
      <h2>Candidate matching was broad, then acronym false positives were removed</h2>
      <div class="two">
        <div class="panel">
          <h3>Screening funnel</h3>
          <div class="metrics" style="grid-template-columns: repeat(2, 1fr); margin-top:.12in;">
            <div class="metric"><div class="value">{len(records):,}</div><div class="label">records screened</div></div>
            <div class="metric"><div class="value">{len(candidates)}</div><div class="label">lexical candidates</div></div>
            <div class="metric"><div class="value">{total}</div><div class="label">retained records</div></div>
            <div class="metric"><div class="value">{len(candidates) - total}</div><div class="label">excluded acronym-context candidates</div></div>
          </div>
        </div>
        <div class="panel">
          <h3>Classification rules</h3>
          <div class="method-list">
            <div>Direct AI/ML includes artificial intelligence, standalone AI in AI context, machine learning, ML, deep learning, LLMs, generative AI, NLP, neural networks, transformers, and named ML algorithms.</div>
            <div>Predictive-only records are retained as AI-adjacent because the request asked to include predictive model topics; these are not counted as direct AI unless AI/ML language also appears.</div>
            <div>Excluded contexts include AI/AN race/ethnicity and adrenal insufficiency abbreviations. Source text remains auditable in candidate and retained exports.</div>
          </div>
        </div>
      </div>
    </div>
    <div class="foot"><span>Sources: retained CSV/JSON and candidate screen in /sources</span><span>2</span></div>
  </section>

  <section class="slide">
    <div class="content">
      <div class="kicker">Topic landscape</div>
      <h2>Predictive analytics is the largest cluster; LLMs and AI-enabled workflows form visible application clusters</h2>
      <div class="two">
        <div class="panel">
          <h3>Retained records by category</h3>
          {bar_list(category_counts, total, 9)}
        </div>
        <div class="panel">
          <h3>Retained records by AI role</h3>
          {bar_list(role_counts, total, 8)}
        </div>
      </div>
    </div>
    <div class="foot"><span>Counts are row counts, not evidence-weighted rankings</span><span>3</span></div>
  </section>

  <section class="slide dark">
    <div class="content">
      <div class="kicker">Clinical domains</div>
      <h2>AI-related work spans type 1 and type 2 diabetes, glycemia/CGM, kidney, retinal, obesity, and translational science</h2>
      <div class="two">
        <div class="panel">
          <h3>Topic areas</h3>
          {bar_list(topic_counts, total, 10)}
        </div>
        <div class="panel">
          <h3>Presentation formats</h3>
          {bar_list(session_counts, total, 6)}
          <div class="pill-row" style="margin-top:.18in;">
            <span class="pill">{sum(1 for row in rows if row['session_type'] == 'Oral Presentations')} oral</span>
            <span class="pill">{sum(1 for row in rows if row['session_type'] == 'General Poster Session')} general posters</span>
            <span class="pill">{sum(1 for row in rows if 'Late' in str(row['session_type']))} late-breaking</span>
          </div>
        </div>
      </div>
    </div>
    <div class="foot"><span>Session metadata from ADA local JSON fields</span><span>4</span></div>
  </section>

  <section class="slide">
    <div class="content">
      <div class="kicker">LLMs and generative AI</div>
      <h2>LLM work is concentrated in education, decision support, diet advice, CGM interpretation, and knowledge platforms</h2>
      {card_grid(llm_rows, 6)}
    </div>
    <div class="foot"><span>Representative LLM/generative AI records; full list in retained_ai_records.csv</span><span>5</span></div>
  </section>

  <section class="slide">
    <div class="content">
      <div class="kicker">Care workflows</div>
      <h2>AI is also positioned as workflow infrastructure for logging, screening, coaching, protocol adherence, and treatment selection</h2>
      {card_grid(workflow_rows, 6)}
    </div>
    <div class="foot"><span>Examples cite local ADA records and EventPilot URLs</span><span>6</span></div>
  </section>

  <section class="slide dark">
    <div class="content">
      <div class="kicker">Science and measurement</div>
      <h2>Deep learning, ML, and AI-assisted analysis appear in omics, molecular discovery, phenotyping, imaging, and segmentation</h2>
      {card_grid(science_rows, 6)}
    </div>
    <div class="foot"><span>Translational examples include drug discovery, omics, image segmentation, and subtype discovery</span><span>7</span></div>
  </section>

  <section class="slide">
    <div class="content">
      <div class="kicker">Predictive modeling</div>
      <h2>Predictive models are the broadest AI-adjacent theme and should be separated from direct AI claims</h2>
      <div class="two">
        <div class="panel">
          <h3>Representative predictive records</h3>
          {mini_table(predictive_rows)}
        </div>
        <div class="panel">
          <h3>Interpretation guardrails</h3>
          <div class="method-list">
            <div>Predictive-only records often describe statistical learning, prognostic models, risk scores, or simulation; they are included for landscape completeness, not as proof of AI deployment.</div>
            <div>Direct AI/ML predictive records combine predictive framing with machine-learning methods or explicit AI language, such as XGBoost, random forests, neural networks, or ML model statements.</div>
            <div>For follow-up CI, prioritize evidence quality, validation cohorts, model calibration, fairness, workflow integration, and whether records report prospective clinical impact.</div>
          </div>
        </div>
      </div>
    </div>
    <div class="foot"><span>Predictive-only tier retained by user scope</span><span>8</span></div>
  </section>

  <section class="slide dark">
    <div class="content">
      <div class="kicker">Audit trail</div>
      <h2>Every retained claim maps to local corpus IDs, source snippets, and generated exports</h2>
      <div class="three">
        <div class="panel">
          <h3>Primary artifacts</h3>
          <p><code>sources/retained_ai_records.csv</code><br><code>sources/retained_ai_records.json</code><br><code>sources/source-log.md</code></p>
        </div>
        <div class="panel">
          <h3>Record locators</h3>
          <p>Each retained row includes source ID, abstract number, media ID, matched agenda ID, local JSON locator, trigger snippet, section text, and EventPilot URL.</p>
        </div>
        <div class="panel">
          <h3>QA status</h3>
          <p>No external web collection was performed. The local archive replaces screenshot appendices; export status and limitations are recorded in <code>sources/qa_status.md</code>.</p>
        </div>
      </div>
      <div class="callout"><p>Bottom line: ADA 2026 contains a meaningful direct-AI layer, led by ML analytics, LLM/generative AI, digital care workflows, and AI-assisted imaging/discovery, plus a larger predictive-modeling layer that needs separate interpretation.</p></div>
    </div>
    <div class="foot"><span>Generated {esc(datetime.now().strftime('%Y-%m-%d %H:%M'))}</span><span>9</span></div>
  </section>
</main>
</body>
</html>
"""
    path = OUT / "report.html"
    path.write_text(html_text, encoding="utf-8")
    return path


def write_manifest(rows, candidates, records, artifacts):
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_mode": "Full local archive screen: all requested ADA 2026 records scanned",
        "source_json": str(SOURCE_JSON),
        "source_json_sha256": sha256(SOURCE_JSON),
        "source_markdown": str(SOURCE_MD),
        "source_markdown_sha256": sha256(SOURCE_MD) if SOURCE_MD.exists() else None,
        "records_screened": len(records),
        "lexical_candidates": len(candidates),
        "retained_records": len(rows),
        "direct_ai_ml_records": sum(1 for row in rows if row["ai_role"] != "AI-adjacent predictive analytics"),
        "predictive_only_records": sum(1 for row in rows if row["ai_role"] == "AI-adjacent predictive analytics"),
        "category_counts": dict(count_rows(rows, "category")),
        "topic_counts": dict(count_rows(rows, "topic_area")),
        "role_counts": dict(count_rows(rows, "ai_role")),
        "artifacts": {name: str(path) for name, path in artifacts.items()},
    }
    path = SOURCES / "run_manifest.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_qa(rows, candidates, records, export_status=None):
    export_status = export_status or "PDF export not attempted by build script; run the cohere-style-ci exporter separately."
    lines = [
        "# ADA 2026 AI Topics QA / Status Notes",
        "",
        f"- Build timestamp: {datetime.now(timezone.utc).isoformat()}",
        f"- Records screened: {len(records)}",
        f"- Lexical candidates: {len(candidates)}",
        f"- Retained records: {len(rows)}",
        f"- Direct AI/ML records: {sum(1 for row in rows if row['ai_role'] != 'AI-adjacent predictive analytics')}",
        f"- Predictive-only AI-adjacent records: {sum(1 for row in rows if row['ai_role'] == 'AI-adjacent predictive analytics')}",
        "- Source mode: local ADA archive. No external webpage screenshots were required or collected.",
        "- False-positive handling: AI/AN and adrenal-insufficiency AI contexts were excluded when no other AI/ML term supported inclusion.",
        "- Topic classifier fix: topic_area now evaluates the visible abstract title first, then Introduction/Objectives, then full abstract text only as fallback, preventing incidental secondary terms such as retinal, kidney, obesity, or GDM language from overriding the title-level topic.",
        "- Auditability: retained CSV/JSON include abstract number, media ID, agenda ID, local locator, EventPilot URL, trigger snippet, abstract sections, summary, category, role, and topic area.",
        f"- PDF/export status: {export_status}",
        "- Visual QA: run export_html_slides_pdf.mjs and inspect render-review screenshots for overflow/clipping before external distribution.",
    ]
    path = SOURCES / "qa_status.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    SOURCES.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    records = read_records()
    candidates, retained_pairs = build_screen(records)
    retained_rows = normalize_retained(retained_pairs)

    retained_fields = [
        "source_id",
        "ref_number",
        "mediaid",
        "abstract_number",
        "title",
        "full_title",
        "authors",
        "session_type",
        "session_date",
        "session_start",
        "session_stop",
        "session_location",
        "matched_agenda_id",
        "session_link_id",
        "eventpilot_url",
        "local_record_locator",
        "accepted_hits",
        "ai_role",
        "category",
        "topic_area",
        "trigger_snippet",
        "summary",
        "introduction_objective",
        "methods",
        "results",
        "conclusion",
        "abstract_text",
    ]
    candidate_fields = [
        "mediaid",
        "abstract_number",
        "title",
        "raw_hits",
        "accepted_hits",
        "included",
        "inclusion_tier",
        "exclusion_reason",
        "trigger_snippet",
    ]
    retained_csv = SOURCES / "retained_ai_records.csv"
    retained_json = SOURCES / "retained_ai_records.json"
    candidate_csv = SOURCES / "candidate_screen.csv"
    write_csv(retained_csv, retained_rows, retained_fields)
    retained_json.write_text(
        json.dumps(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_json": str(SOURCE_JSON),
                "records_screened": len(records),
                "retained_count": len(retained_rows),
                "records": retained_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_csv(candidate_csv, candidates, candidate_fields)
    source_log = write_source_log(retained_rows, candidates, records)
    reference_csv = write_reference_csv(retained_rows)
    report_html = write_html_report(retained_rows, candidates, records)
    qa_status = write_qa(retained_rows, candidates, records)
    manifest = write_manifest(
        retained_rows,
        candidates,
        records,
        {
            "retained_csv": retained_csv,
            "retained_json": retained_json,
            "candidate_screen_csv": candidate_csv,
            "source_log": source_log,
            "reference_screenshots_csv": reference_csv,
            "report_html": report_html,
            "qa_status": qa_status,
        },
    )
    print(json.dumps({
        "records_screened": len(records),
        "lexical_candidates": len(candidates),
        "retained_records": len(retained_rows),
        "direct_ai_ml_records": sum(1 for row in retained_rows if row["ai_role"] != "AI-adjacent predictive analytics"),
        "predictive_only_records": sum(1 for row in retained_rows if row["ai_role"] == "AI-adjacent predictive analytics"),
        "report_html": str(report_html),
        "manifest": str(manifest),
    }, indent=2))


if __name__ == "__main__":
    main()
