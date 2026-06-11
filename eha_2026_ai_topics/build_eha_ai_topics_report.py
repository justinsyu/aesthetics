import csv
import hashlib
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eha_2026_ai_topics"
SOURCES = OUT / "sources"
SCREENSHOTS = OUT / "screenshots"
DATA_DIR = Path(r"C:\Users\Justin\Desktop\eha-2026\data")
SOURCE_JSONL = DATA_DIR / "eha_2026_abstracts.jsonl"
SOURCE_JSON = DATA_DIR / "eha_2026_abstracts.json"
SOURCE_CSV = DATA_DIR / "eha_2026_abstracts.csv"
SUMMARY_JSON = DATA_DIR / "summary.json"


TERM_RULES = [
    ("artificial intelligence", re.compile(r"\bartificial intelligence\b", re.I)),
    ("generative AI", re.compile(r"\bgenerative AI\b", re.I)),
    ("AI-framed method", re.compile(
        r"(?<![A-Za-z0-9.-])AI[- ](?:based|assisted|designed|driven|guided|generated|enabled|powered|immunology)\b|"
        r"\bAI\s+(?:classification|platform|model|algorithm|tool|software|system|workflow|pipeline|agent)\b",
        re.I,
    )),
    ("AI", re.compile(r"(?<![A-Za-z0-9.-])AI(?![A-Za-z0-9])")),
    ("machine learning", re.compile(r"\bmachine learning\b", re.I)),
    ("deep learning", re.compile(r"\bdeep learning\b", re.I)),
    ("neural network", re.compile(r"\bneural networks?\b", re.I)),
    ("foundation model", re.compile(r"\bfoundation models?\b", re.I)),
    ("large language model", re.compile(r"\blarge language models?\b|\bLLMs?\b", re.I)),
    ("NLP", re.compile(r"\bnatural language processing\b|\bNLP\b", re.I)),
    ("radiomics", re.compile(r"\bradiomics?\b", re.I)),
    ("computer vision", re.compile(r"\bcomputer vision\b", re.I)),
    ("digital pathology", re.compile(r"\bdigital pathology\b", re.I)),
    ("image analysis", re.compile(r"\bimage analysis\b|\bimage-based\b|\bautomated image\b", re.I)),
    ("classifier", re.compile(r"\bclassifiers?\b|\bclassification model\b", re.I)),
    ("random forest", re.compile(r"\brandom forests?\b", re.I)),
    ("gradient boosting", re.compile(r"\bgradient boosting\b|\bXGBoost\b", re.I)),
    ("support vector machine", re.compile(r"\bsupport vector machines?\b|\bSVM\b", re.I)),
    ("computational model", re.compile(r"\bcomputational model(?:ing)?\b|\bcomputational approach\b", re.I)),
    ("predictive model", re.compile(r"\bpredictive models?\b|\bprediction models?\b", re.I)),
    ("algorithmic prediction", re.compile(r"\balgorithm(?:ic)?\b.{0,80}\b(predict|classif|diagnos|risk|prognos|detect)", re.I | re.S)),
    ("automated diagnosis", re.compile(r"\bautomated\b.{0,80}\b(diagnos|detect|classif)", re.I | re.S)),
]

WEAK_ONLY_TERMS = {"AI", "classifier", "computational model", "predictive model", "algorithmic prediction", "automated diagnosis"}
ORDINARY_STATS_RULES = [
    re.compile(r"\bregression model\b", re.I),
    re.compile(r"\bcox model\b", re.I),
    re.compile(r"\blogistic regression\b", re.I),
    re.compile(r"\blinear regression\b", re.I),
]
STRONG_AI_RULE = re.compile(
    r"\b(machine learning|artificial intelligence|generative AI|AI[- ](?:based|assisted|designed|driven|guided|generated|enabled|powered)|neural|random forest|"
    r"gradient boosting|XGBoost|SVM|radiomic|NLP|LLM|digital pathology|computer vision)\b",
    re.I,
)
NON_AI_CONTEXT_RULES = [
    re.compile(r"\bnTFHL-AI\b"),
    re.compile(r"\bsevere AI\b", re.I),
    re.compile(r"\bAI,\s*FA,\s*DM\b"),
    re.compile(r"\bAI\s*\(Gemini\)\s+was\s+used\s+for\s+data\s+analysis\s+only\b", re.I),
    re.compile(r"\bAI-assisted coding tools\b", re.I),
    re.compile(r"\bin the era of AI\b", re.I),
]

DISPLAY_LABELS = {
    "Clinical prediction and risk stratification": "Clinical prediction and risk",
    "Digital pathology, imaging, and morphology": "Digital pathology and imaging",
    "NLP, LLMs, and text/data extraction": "NLP, LLMs, and data extraction",
    "Treatment response and precision therapy": "Treatment response and therapy",
    "Genomics, multi-omics, and biomarker discovery": "Omics and biomarker discovery",
    "Novel technologies, techniques and digital analytical tools in hematology": "Digital analytical tools",
    "Myeloproliferative neoplasms": "Myeloproliferative disease",
    "Thrombosis and hemostasis": "Thrombosis and hemostasis",
    "AI or machine-learning method not specified": "AI/ML method not specified",
    "Text extraction, triage, or generative AI": "Text extraction and language models",
    "Treatment response or therapy selection": "Treatment response and therapy",
    "Biomarker or omics discovery": "Biomarker and omics discovery",
    "Other AI-related use case": "Other AI-related use",
}

WEAK_TERM_AUDIT_EXCLUSIONS = [
    ("PB2730", "Optim.AI product-name match without explicit AI-method framing"),
    ("PB4498", "ordinary automated RT-qPCR assay"),
    ("PB3824", "AI used only for general data analysis after Cox modeling"),
    ("PB3862", "nTFHL-AI lymphoma subtype abbreviation"),
    ("PB3305", "AI-assisted coding tools used only to optimize Python scripts"),
    ("PS1893", "severe AI clinical abbreviation"),
    ("PB3470", "AI in a comorbidity abbreviation list"),
    ("PS2375", "ordinary automated retinal camera workflow"),
    ("PF471", "nonspecific phrase 'era of AI' without an AI method"),
    ("PF1209", "automated imaging and phenotyping algorithm without explicit AI or ML framing"),
]


def esc(value):
    return html.escape(str(value or ""), quote=True)


def clip(value, max_len):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    return value if len(value) <= max_len else value[: max_len - 3].rstrip() + "..."


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text_of(record):
    fields = [
        "title",
        "topic_name",
        "keywords",
        "background",
        "aims",
        "methods",
        "results",
        "summary_conclusion",
        "abstract_text",
        "description_text",
    ]
    return "\n".join(str(record.get(field) or "") for field in fields)


def raw_terms(text):
    return [label for label, rx in TERM_RULES if rx.search(text)]


def relevance_decision(terms, text):
    if not terms:
        return False, "No screened AI-related term was identified."
    if re.search(r"\bAI-assisted coding tools\b", text, re.I):
        return False, "Excluded after weak-term audit because AI was used only as a coding or script-optimization aid, not as an AI-related conference method or topic."
    if any(rx.search(text) for rx in NON_AI_CONTEXT_RULES) and not (set(terms) - WEAK_ONLY_TERMS):
        return False, "Excluded after weak-term audit because the matched text used AI as a non-AI abbreviation, a general writing/coding aid, or a nonspecific contextual phrase rather than an AI-related conference method."
    if all(term in WEAK_ONLY_TERMS for term in terms):
        return False, "Only weak model or classifier language was present without explicit AI or machine-learning framing."
    ordinary_stats_only = (
        all(term in {"predictive model", "algorithmic prediction"} for term in terms)
        and any(rx.search(text) for rx in ORDINARY_STATS_RULES)
        and not STRONG_AI_RULE.search(text)
    )
    if ordinary_stats_only:
        return False, "The record described ordinary regression or Cox modeling without explicit AI or machine-learning framing."
    return True, "Retained after lexical screening and relevance check for explicit AI, machine-learning, image-analysis, language-model, or comparable method framing."


def first_match(text, rules, fallback):
    for label, rx in rules:
        if re.search(rx, text, re.I):
            return label
    return fallback


def cluster_for(text):
    return first_match(
        text,
        [
            ("NLP, LLMs, and text/data extraction", r"natural language processing|\bNLP\b|large language model|\bLLMs?\b|text mining|language model|retrieval[- ]augmented|\bRAG\b|ChatGPT|DeepSeek"),
            ("Digital pathology, imaging, and morphology", r"digital pathology|image analysis|image-based|computer vision|radiomics|morpholog|microscop|smear|segmentation"),
            ("Clinical prediction and risk stratification", r"predict|prediction|prognos|risk strat|survival|relapse|mortality|outcome"),
            ("Diagnosis and classification", r"diagnos|classif|detect|screening|differenti"),
            ("Treatment response and precision therapy", r"response|therapy|treatment|personaliz|precision|drug|resistance"),
            ("Genomics, multi-omics, and biomarker discovery", r"genomic|transcriptomic|proteomic|multi-omic|single-cell|biomarker|mutation|sequencing"),
            ("Operational workflow and digital tools", r"workflow|remote|digital|app|electronic|automation|triage|decision support"),
        ],
        "Other AI / computational methods",
    )


def use_case_for(text):
    return first_match(
        text,
        [
            ("Text extraction, triage, or generative AI", r"natural language processing|\bNLP\b|large language model|\bLLMs?\b|ChatGPT|DeepSeek|triage|abstraction|annotation"),
            ("Prognosis or risk stratification", r"prognos|risk strat|survival|relapse|mortality|outcome|predict"),
            ("Diagnosis or classification", r"diagnos|classif|detect|screen"),
            ("Treatment response or therapy selection", r"response|treatment|therapy|drug|resistance|personaliz"),
            ("Image, pathology, or morphology analysis", r"image|pathology|morpholog|radiomic|microscop|smear|segmentation"),
            ("Biomarker or omics discovery", r"biomarker|genomic|transcriptomic|proteomic|multi-omic|single-cell|sequencing"),
        ],
        "Other AI-related use case",
    )


def method_type_for(text):
    return first_match(
        text,
        [
            ("NLP or large language model", r"natural language processing|\bNLP\b|large language model|\bLLMs?\b|language model|ChatGPT|DeepSeek"),
            ("Deep learning or neural network", r"deep learning|neural network|transformer|foundation model|LSTM"),
            ("Radiomics or image analysis", r"radiomic|image analysis|computer vision|digital pathology|segmentation"),
            ("Tree-based machine learning", r"random forest|gradient boosting|XGBoost"),
            ("Classical machine learning", r"machine learning|support vector machine|SVM|classifier"),
            ("Computational or predictive model", r"computational model|predictive model|prediction model|algorithm"),
        ],
        "AI or machine-learning method not specified",
    )


def disease_area(record, text):
    haystack = f"{record.get('title') or ''}\n{record.get('keywords') or ''}\n{record.get('topic_name') or ''}\n{text}"
    if re.search(r"\bAML\b", haystack) or re.search(r"acute myeloid leukemia", haystack, re.I):
        return "Acute myeloid leukemia"
    if re.search(r"\bALL\b", haystack) or re.search(r"acute lymphoblastic leukemia", haystack, re.I):
        return "Acute lymphoblastic leukemia"
    if re.search(r"\bMDS\b", haystack) or re.search(r"myelodysplastic", haystack, re.I):
        return "Myelodysplastic syndromes"
    if re.search(r"\bMPN\b", haystack) or re.search(r"myeloproliferative|myelofibrosis|polycythemia|essential thrombocyth", haystack, re.I):
        return "Myeloproliferative neoplasms"
    if re.search(r"\bMM\b", haystack) or re.search(r"multiple myeloma|plasma cell", haystack, re.I):
        return "Multiple myeloma"
    if re.search(r"\bCLL\b", haystack) or re.search(r"chronic lymphocytic leukemia", haystack, re.I):
        return "CLL"
    if re.search(r"lymphoma|DLBCL|Hodgkin|mantle cell|follicular", haystack, re.I):
        return "Lymphoma"
    if re.search(r"\bCAR[- ]?T\b", haystack, re.I) or re.search(r"cell therapy|cellular therapy", haystack, re.I):
        return "CAR-T and cell therapy"
    if re.search(r"transplant|HSCT|stem cell transplant", haystack, re.I):
        return "Transplantation"
    if re.search(r"sickle cell|thalassemia|hemoglobinopath", haystack, re.I):
        return "Hemoglobinopathies"
    if re.search(r"thrombo|hemostasis|haemostasis|coagulation|bleeding|hemophilia", haystack, re.I):
        return "Thrombosis and hemostasis"
    if re.search(r"anemia|anaemia|erythro|red blood cell", haystack, re.I):
        return "Anemia and red cells"
    topic = record.get("topic_name") or "Other hematology"
    return re.sub(r"^\d+\.\s*", "", topic).split(" - ")[0]


def evidence_excerpt(record):
    joined = " ".join(
        str(record.get(field) or "")
        for field in ["methods", "results", "summary_conclusion", "background", "aims"]
        if record.get(field)
    )
    return clip(joined, 640)


def read_records():
    with SOURCE_JSONL.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def normalize_authors(value):
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value or "")


def build_records():
    retained = []
    candidates = []
    for record in read_records():
        text = text_of(record)
        terms = raw_terms(text)
        if not terms:
            continue
        retained_flag, rationale = relevance_decision(terms, text)
        candidate = {
            "content_id": record.get("content_id") or "",
            "abstract_number": record.get("abstract_number") or "",
            "eha_abstract_id": record.get("eha_abstract_id") or "",
            "title": record.get("title") or "",
            "presentation_type": record.get("presentation_type") or record.get("marker_name") or "",
            "topic_name": record.get("topic_name") or "",
            "matched_terms": "; ".join(terms),
            "retained": "yes" if retained_flag else "no",
            "relevance_rationale": rationale,
            "href": record.get("href") or "",
        }
        candidates.append(candidate)
        if not retained_flag:
            continue
        normalized = {
            "record_ref": record.get("abstract_number") or record.get("eha_abstract_id") or str(record.get("content_id") or ""),
            "content_id": record.get("content_id") or "",
            "abstract_number": record.get("abstract_number") or "",
            "eha_abstract_id": record.get("eha_abstract_id") or "",
            "title": record.get("title") or "",
            "presentation_type": record.get("presentation_type") or record.get("marker_name") or "",
            "session_title": record.get("session_title") or "",
            "topic_name": record.get("topic_name") or "",
            "date": record.get("date") or "",
            "authors": normalize_authors(record.get("authors")),
            "keywords": record.get("keywords") or "",
            "href": record.get("href") or "",
            "matched_terms": "; ".join(terms),
            "ai_cluster": cluster_for(text),
            "disease_area": disease_area(record, text),
            "use_case": use_case_for(text),
            "method_type": method_type_for(text),
            "evidence_excerpt": evidence_excerpt(record),
            "relevance_rationale": rationale,
        }
        retained.append(normalized)
    retained.sort(key=lambda row: (row["ai_cluster"], row["disease_area"], row["record_ref"]))
    candidates.sort(key=lambda row: (row["retained"], row["abstract_number"], row["eha_abstract_id"]))
    return retained, candidates


def count_by(records, key):
    return Counter(row[key] or "Unspecified" for row in records).most_common()


def pct(n, d):
    return f"{(n / d * 100):.1f}%"


def display_label(label):
    return DISPLAY_LABELS.get(label, label)


def record_label(count):
    return "record" if count == 1 else "records"


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bar_rows(counts, limit=7):
    max_count = counts[0][1] if counts else 1
    rows = []
    for label, value in counts[:limit]:
        width = max(7, value / max_count * 100)
        rows.append(
            f'<div class="bar-row"><div class="bar-label">{esc(display_label(label))}</div>'
            f'<div class="bar-track"><span style="width:{width:.1f}%"></span></div>'
            f'<div class="bar-count">{value}</div></div>'
        )
    return "\n".join(rows)


def cite(ref):
    return f'<a class="cite" href="{esc(ref["href"])}" title="{esc(ref["label"])}">{ref["n"]}</a>'


def make_refs(records, summary):
    refs = [
        {
            "n": 1,
            "label": "EHA 2026 local abstract corpus summary",
            "source": "EHA Library scrape summary",
            "date": summary.get("scraped_at", ""),
            "href": summary.get("source_url", ""),
            "evidence": f'{summary.get("detail_rows")} detail rows; {summary.get("listing_rows")} listing rows; {summary.get("detail_errors")} detail errors.',
        }
    ]
    picked = representative_records(records, 9)
    seen = {rec["content_id"] for rec in picked}
    for key in ["ai_cluster", "disease_area", "method_type"]:
        for label, _ in count_by(records, key)[:4]:
            rec = next((row for row in records if row[key] == label), None)
            if rec and rec["content_id"] not in seen:
                picked.append(rec)
                seen.add(rec["content_id"])
    for rec in records:
        if len(picked) >= 10:
            break
        if rec["content_id"] not in seen:
            picked.append(rec)
            seen.add(rec["content_id"])
    for rec in picked[:10]:
        refs.append(
            {
                "n": len(refs) + 1,
                "label": f'{rec["record_ref"]} {rec["eha_abstract_id"]}'.strip(),
                "source": rec["title"],
                "date": rec["date"] or rec["presentation_type"],
                "href": rec["href"],
                "evidence": f'{rec["ai_cluster"]}; {rec["disease_area"]}; matched terms: {rec["matched_terms"]}.',
                "content_id": rec["content_id"],
            }
        )
    return refs


def representative_records(records, limit=9):
    picked = []
    seen = set()
    for cluster, _ in count_by(records, "ai_cluster"):
        for rec in [row for row in records if row["ai_cluster"] == cluster][:2]:
            if rec["content_id"] in seen:
                continue
            picked.append(rec)
            seen.add(rec["content_id"])
            if len(picked) >= limit:
                return picked
    return picked


def example_table(records, refs_by_id):
    rows = []
    for rec in representative_records(records):
        ref = refs_by_id.get(rec["content_id"])
        citation = cite(ref) if ref else ""
        rows.append(
            "<tr>"
            f'<td class="ref-cell">{esc(rec["record_ref"])}</td>'
            f"<td>{esc(rec['disease_area'])}</td>"
            f"<td>{esc(rec['ai_cluster'])}{citation}</td>"
            f"<td>{esc(rec['method_type'])}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def references_table(refs):
    rows = []
    for ref in refs:
        rows.append(
            "<tr>"
            f'<td class="ref-cell">{ref["n"]}</td>'
            f'<td><a href="{esc(ref["href"])}">{esc(clip(ref["source"], 112))}</a></td>'
            f"<td>{esc(ref['date'] or 'Local record')}</td>"
            f"<td>{esc(clip(ref['evidence'], 142))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def topic_summary_cards(cluster_counts):
    descriptions = {
        "Clinical prediction and risk stratification": "Records in this cluster most often describe machine-learning or AI-framed models for prognosis, relapse, response, survival, or other risk-related outcomes.",
        "Digital pathology, imaging, and morphology": "This cluster includes image analysis, radiomics, morphology, microscopy, smear analysis, and related computational pathology or imaging approaches.",
        "Diagnosis and classification": "These records use AI-related methods to classify samples, distinguish diagnostic subgroups, or support detection tasks.",
        "NLP, LLMs, and text/data extraction": "This cluster includes language-model, NLP, triage, annotation, education, and data-abstraction applications.",
        "Treatment response and precision therapy": "These records address response prediction, treatment selection, resistance, or therapy-related decision support.",
        "Genomics, multi-omics, and biomarker discovery": "These records apply AI-related methods to genomic, transcriptomic, single-cell, or biomarker-focused analyses.",
        "Operational workflow and digital tools": "These records describe AI-related workflow, digital health, application, or implementation-oriented uses.",
        "Other AI / computational methods": "These records met inclusion criteria but did not map cleanly to the prespecified topic clusters.",
    }
    cards = []
    for label, count in cluster_counts[:6]:
        cards.append(
            f'<div class="topic-card"><div class="chip">{esc(display_label(label))}</div>'
            f'<div class="topic-count">{count} {record_label(count)}</div>'
            f"<p>{esc(descriptions.get(label, 'Records met inclusion criteria for AI-related methods.'))}</p></div>"
        )
    return "\n".join(cards)


def build_html(records, candidates, summary):
    total = int(summary.get("detail_rows") or len(records))
    retained_count = len(records)
    candidate_count = len(candidates)
    cluster_counts = count_by(records, "ai_cluster")
    disease_counts = count_by(records, "disease_area")
    use_case_counts = count_by(records, "use_case")
    method_counts = count_by(records, "method_type")
    presentation_counts = count_by(records, "presentation_type")
    refs = make_refs(records, summary)
    refs_by_id = {ref.get("content_id"): ref for ref in refs if ref.get("content_id")}
    corpus_ref = refs[0]
    slides = 8
    top_cluster_ref = next((ref for ref in refs[1:] if cluster_counts and cluster_counts[0][0] in ref["evidence"]), corpus_ref)
    top_disease_ref = next((ref for ref in refs[1:] if disease_counts and disease_counts[0][0] in ref["evidence"]), corpus_ref)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1600">
<title>EHA 2026 AI-related topics</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Space+Grotesk:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--ink:#10120f;--muted:#555b52;--paper:#f6f1e8;--card:#fffaf0;--line:#20241c;--lime:#d7ff5f;--orange:#ffb86b;--blue:#b8d8ff;--pink:#ffd3e0;--gray:#d6d0c2;--shadow:0 18px 48px rgba(16,18,15,.08);--radius:22px}}
*{{box-sizing:border-box}}html,body{{margin:0;font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:var(--ink);background:#14140f;font-size:18px;line-height:1.35;-webkit-font-smoothing:antialiased}}body{{overflow-x:hidden}}a{{color:inherit;text-decoration:none}}.slide{{width:1600px;height:900px;position:relative;overflow:hidden;background:var(--paper);padding:42px 0 26px}}.slide:before{{content:"";position:absolute;inset:0;background:radial-gradient(circle at 16px 16px,rgba(16,18,15,.08) 1.1px,transparent 1.2px);background-size:28px 28px;opacity:.34}}.slide.dark{{background:#11130f;color:var(--paper)}}.slide.dark:before{{background:radial-gradient(circle at 16px 16px,rgba(215,255,95,.18) 1.1px,transparent 1.2px);background-size:30px 30px;opacity:.25}}.wrap{{position:relative;z-index:1;width:1360px;height:100%;margin:0 auto}}h1,h2,h3{{font-family:"Space Grotesk",Inter,sans-serif;margin:0;font-weight:500;letter-spacing:0}}h1{{font-size:66px;line-height:1.02;max-width:1320px}}h2{{font-size:50px;line-height:1.06;margin-bottom:20px;max-width:1260px}}h3{{font-size:24px;line-height:1.12;margin-bottom:12px}}p{{margin:0;color:var(--muted)}}.dark p,.dark .note{{color:rgba(246,241,232,.72)}}.dek{{font-size:24px;line-height:1.32;max-width:1240px;margin:18px 0 22px;color:var(--muted)}}.dark .dek{{color:rgba(246,241,232,.82)}}.chip,.eyebrow{{display:inline-flex;align-items:center;border:1.5px solid var(--line);border-radius:999px;background:var(--lime);padding:7px 11px;font-size:14px;line-height:1.1;text-transform:uppercase;font-weight:700;letter-spacing:.02em;white-space:nowrap;color:var(--ink)}}.eyebrow{{margin-bottom:18px}}.dark .chip,.dark .eyebrow{{color:var(--ink)}}.grid{{display:grid;gap:20px}}.cols-3{{grid-template-columns:repeat(3,1fr)}}.cols-2{{grid-template-columns:repeat(2,1fr)}}.card{{background:rgba(255,250,240,.92);border:1.5px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:22px}}.dark .card{{background:#1a1d17;border-color:rgba(246,241,232,.45);box-shadow:none}}.metric{{min-height:132px}}.metric .num{{font-family:"Space Grotesk";font-size:58px;line-height:1;font-weight:500}}.metric .label{{font-size:16px;color:var(--muted);margin-top:9px;line-height:1.25}}.dark .metric .label{{color:rgba(246,241,232,.68)}}.callout{{background:#11130f;color:var(--paper);padding:22px 28px;border-radius:var(--radius);border:1.5px solid var(--line);margin-top:20px}}.callout p,.callout li{{color:rgba(246,241,232,.82)}}ul{{margin:0;padding:0}}li{{list-style:none;position:relative;margin:0 0 9px 0;padding-left:20px;font-size:19px;line-height:1.28;color:inherit}}li:before{{content:"";width:8px;height:8px;border-radius:50%;background:var(--lime);position:absolute;left:0;top:.58em}}.bar-row{{display:grid;grid-template-columns:minmax(340px,430px) 1fr 60px;gap:14px;align-items:center;margin:11px 0}}.bar-label{{font-size:18px;line-height:1.16}}.bar-track{{height:20px;border:1.5px solid var(--line);border-radius:999px;background:rgba(255,250,240,.62);overflow:hidden}}.bar-track span{{display:block;height:100%;background:linear-gradient(90deg,var(--lime),var(--orange))}}.bar-count{{font-size:18px;text-align:right;font-variant-numeric:tabular-nums}}.split{{display:grid;grid-template-columns:1.02fr .98fr;gap:24px;align-items:start}}.note{{font-size:15px;line-height:1.32;color:var(--muted);margin-top:14px;max-width:1260px}}.table{{width:100%;border-collapse:separate;border-spacing:0;font-size:15px;line-height:1.22;overflow:hidden;border:1.5px solid var(--line);border-radius:18px;background:rgba(255,250,240,.94)}}.table th,.table td{{padding:10px 12px;border-bottom:1px solid rgba(27,31,23,.22);vertical-align:top;text-align:left;font-weight:400}}.table th{{background:#11130f;color:var(--paper);font-weight:500}}.table tr:last-child td{{border-bottom:0}}.table .ref-cell,.refs th:first-child,.refs td:first-child{{text-align:center;vertical-align:middle;font-variant-numeric:tabular-nums}}.examples th:nth-child(1),.examples td:nth-child(1){{width:112px}}.examples th:nth-child(2),.examples td:nth-child(2){{width:250px}}.examples th:nth-child(4),.examples td:nth-child(4){{width:245px}}.refs{{font-size:13px;line-height:1.16}}.refs th:nth-child(1),.refs td:nth-child(1){{width:62px}}.refs th:nth-child(3),.refs td:nth-child(3){{width:168px}}.refs th:nth-child(4),.refs td:nth-child(4){{width:420px}}.cite{{font-size:.58em;vertical-align:super;margin-left:2px;color:inherit;text-decoration:none;font-weight:500}}.topic-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:8px}}.topic-card{{background:rgba(255,250,240,.94);border:1.5px solid var(--line);border-radius:20px;padding:18px;min-height:172px}}.topic-count{{font-family:"Space Grotesk";font-size:28px;line-height:1;margin:16px 0 10px;font-weight:500}}.topic-card p{{font-size:15px;line-height:1.28;color:var(--muted)}}.pill-row{{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 8px}}.slide-num{{position:absolute;z-index:2;right:42px;bottom:26px;font-size:12px;text-transform:uppercase;color:rgba(16,18,15,.48);font-weight:500}}.dark .slide-num{{color:rgba(246,241,232,.55)}}code{{font-family:Consolas,monospace;font-size:.92em}}@media screen{{body{{display:flex;flex-direction:column;align-items:center;gap:34px;padding:36px 0}}.slide{{max-width:100vw;max-height:100vh;box-shadow:0 24px 80px rgba(0,0,0,.45)}}}}@media print{{@page{{size:1600px 900px;margin:0}}body{{background:#fff}}.slide{{page-break-after:always}}.slide:last-child{{page-break-after:auto}}}}
</style>
</head>
<body>
<article class="slide">
  <div class="wrap">
    <div class="eyebrow">EHA 2026 | AI-related abstracts and posters</div>
    <h1>AI-related methods are documented across {retained_count} EHA 2026 records</h1>
    <p class="dek">A full local-corpus screen of {total:,} EHA 2026 detail records retained {retained_count} records ({pct(retained_count, total)}) with explicit AI, machine-learning, language-model, image-analysis, radiomics, or comparable method language.{cite(corpus_ref)}</p>
    <div class="grid cols-3">
      <div class="card metric"><div class="num">{total:,}</div><div class="label">Local EHA detail records screened{cite(corpus_ref)}</div></div>
      <div class="card metric"><div class="num">{candidate_count}</div><div class="label">Lexical candidates identified before relevance checks{cite(corpus_ref)}</div></div>
      <div class="card metric"><div class="num">{retained_count}</div><div class="label">AI-related records retained in the evidence set{cite(corpus_ref)}</div></div>
    </div>
    <div class="callout">
      <h3>Summary</h3>
      <ul>
        <li>The largest retained cluster was {esc(cluster_counts[0][0])}, with {cluster_counts[0][1]} records.{cite(top_cluster_ref)}</li>
        <li>The most frequent disease area was {esc(disease_counts[0][0])}, with {disease_counts[0][1]} retained records.{cite(top_disease_ref)}</li>
        <li>Record-level CSV and JSON exports preserve abstract IDs, URLs, matched terms, derived classifications, and evidence excerpts.</li>
      </ul>
    </div>
  </div><div class="slide-num">01 / {slides}</div>
</article>

<article class="slide dark">
  <div class="wrap">
    <div class="eyebrow">Methods | Local corpus</div>
    <h2>Screening used explicit AI-method language and relevance checks</h2>
    <div class="grid cols-2">
      <div class="card"><h3>Inclusion logic</h3><ul>
        <li>Records were retained when source text matched terms for artificial intelligence, machine learning, deep learning, neural networks, NLP, LLMs, radiomics, image analysis, digital pathology, classifiers, or AI-framed prediction.</li>
        <li>Ordinary regression, Cox, logistic, or linear models were excluded when no AI or machine-learning framing was present.</li>
        <li>Weak-only model or classifier language was excluded unless accompanied by stronger AI-method terminology.</li>
      </ul></div>
      <div class="card"><h3>Archive basis</h3><ul>
        <li>The local scrape summary lists {summary.get("listing_rows")} listing rows, {summary.get("detail_rows")} detail rows, and {summary.get("detail_errors")} detail errors.{cite(corpus_ref)}</li>
        <li>The retained set represents {pct(retained_count, total)} of screened local detail records.{cite(corpus_ref)}</li>
        <li>Derived cluster labels support review triage and should not be interpreted as a formal conference taxonomy.</li>
      </ul></div>
    </div>
    <p class="note">Source basis: local EHA 2026 archive files in <code>{esc(str(DATA_DIR))}</code>. No live website recrawl or external webpage screenshot collection was required for this local-archive run.</p>
  </div><div class="slide-num">02 / {slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Topic clusters | Retained set</div>
    <h2>Prediction-oriented and image-oriented applications account for most retained records</h2>
    <div class="split">
      <div class="card">
        {bar_rows(cluster_counts, 8)}
      </div>
      <div class="card"><h3>Interpretation</h3><ul>
        <li>Clinical prediction and risk stratification includes prognosis, relapse, treatment response, survival, and other outcome-oriented models.</li>
        <li>Digital pathology, imaging, and morphology includes image analysis, radiomics, microscopy, morphology, smear analysis, and segmentation.</li>
        <li>Language-model records include clinical annotation, data abstraction, triage, education, and decision-support evaluations.</li>
      </ul></div>
    </div>
  </div><div class="slide-num">03 / {slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Disease areas | Retained set</div>
    <h2>AI-related records span malignant and non-malignant hematology categories</h2>
    <div class="grid cols-2">
      <div class="card"><h3>Disease area distribution</h3>{bar_rows(disease_counts, 8)}</div>
      <div class="card"><h3>Presentation type distribution</h3>{bar_rows(presentation_counts, 5)}
        <p class="note">Presentation type reflects the local EHA record metadata and not an independent prioritization of clinical importance.</p>
      </div>
    </div>
  </div><div class="slide-num">04 / {slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Methods and use cases</div>
    <h2>Retained records describe heterogeneous computational methods and clinical tasks</h2>
    <div class="grid cols-2">
      <div class="card"><h3>Method language</h3>{bar_rows(method_counts, 7)}</div>
      <div class="card"><h3>Use-case language</h3>{bar_rows(use_case_counts, 7)}</div>
    </div>
    <p class="note">The method and use-case categories are rule-based labels derived from abstract text. They are provided to support reproducible review, not to adjudicate model validity or clinical readiness.</p>
  </div><div class="slide-num">05 / {slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Topic summaries</div>
    <h2>Cluster-level summaries should be read as an evidence inventory</h2>
    <div class="topic-grid">
      {topic_summary_cards(cluster_counts)}
    </div>
  </div><div class="slide-num">06 / {slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Representative records</div>
    <h2>Examples show how retained records map to source-verifiable rows</h2>
    <table class="table examples">
      <thead><tr><th>REF</th><th>Disease area</th><th>AI-related topic</th><th>Method type</th></tr></thead>
      <tbody>{example_table(records, refs_by_id)}</tbody>
    </table>
    <p class="note">The table is a representative sample. The companion retained CSV and JSON files contain the full record set, matched terms, source URLs, and evidence excerpts.</p>
  </div><div class="slide-num">07 / {slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">References 1-{len(refs)}</div>
    <h2>References</h2>
    <table class="table refs">
      <thead><tr><th>REF</th><th>Source</th><th>Date basis</th><th>Evidence basis</th></tr></thead>
      <tbody>{references_table(refs)}</tbody>
    </table>
  </div><div class="slide-num">08 / {slides}</div>
</article>
<script>
const slides = Array.from(document.querySelectorAll('.slide'));
let cur = 0;
const go = (i) => {{
  cur = Math.max(0, Math.min(slides.length - 1, i));
  slides[cur].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
}};
document.addEventListener('keydown', (e) => {{
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown') {{
    e.preventDefault(); go(cur + 1);
  }} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp') {{
    e.preventDefault(); go(cur - 1);
  }} else if (e.key === 'Home') {{
    e.preventDefault(); go(0);
  }} else if (e.key === 'End') {{
    e.preventDefault(); go(slides.length - 1);
  }}
}});
</script>
</body>
</html>
"""


def write_source_log(records, candidates, summary, refs, manifest):
    cluster_counts = count_by(records, "ai_cluster")
    disease_counts = count_by(records, "disease_area")
    method_counts = count_by(records, "method_type")
    terms = ", ".join(label for label, _ in TERM_RULES)
    lines = [
        "# EHA 2026 AI-Related Topics Source Log",
        "",
        f"Generated: {manifest['created_at']}",
        "",
        "## Source Corpus",
        "",
        f"- Local JSONL: `{SOURCE_JSONL}`",
        f"- Local JSON: `{SOURCE_JSON}`",
        f"- Local CSV: `{SOURCE_CSV}`",
        f"- Local summary: `{SUMMARY_JSON}`",
        f"- EHA source URL recorded in summary: {summary.get('source_url')}",
        f"- Scraped at: {summary.get('scraped_at')}",
        f"- Listing rows: {summary.get('listing_rows')}",
        f"- Detail rows screened: {summary.get('detail_rows')}",
        f"- Detail errors recorded by scrape summary: {summary.get('detail_errors')}",
        "",
        "## Screening Method",
        "",
        f"Keyword rules screened: {terms}.",
        "",
        "Records were retained when the local source text contained explicit AI, machine-learning, language-model, image-analysis, radiomics, digital-pathology, classifier, or comparable AI-method framing. Records were excluded when only ordinary statistical model language appeared without AI or machine-learning framing, or when only weak classifier/model language appeared without stronger method support.",
        "",
        "## Counts",
        "",
        "- Prior retained records before weak-term audit: 187",
        f"- Retained records after weak-term audit: {len(records)}",
        f"- Records removed by weak-term audit: {187 - len(records)}",
        f"- Records screened: {summary.get('detail_rows')}",
        f"- Lexical candidates: {len(candidates)}",
        f"- Retained AI-related records: {len(records)}",
        f"- Retained share of screened corpus: {pct(len(records), int(summary.get('detail_rows') or len(records)))}",
        "",
        "## Weak-Term Audit Exclusions",
        "",
    ]
    lines += [f"- {ref}: {reason}." for ref, reason in WEAK_TERM_AUDIT_EXCLUSIONS]
    lines += [
        "",
        "## Topic Clusters",
        "",
    ]
    lines += [f"- {label}: {count}" for label, count in cluster_counts]
    lines += ["", "## Disease Areas", ""]
    lines += [f"- {label}: {count}" for label, count in disease_counts]
    lines += ["", "## Method Types", ""]
    lines += [f"- {label}: {count}" for label, count in method_counts]
    lines += ["", "## Final Cited References", ""]
    for ref in refs:
        lines.append(f"- REF {ref['n']}: {ref['source']} | {ref['date'] or 'Local record'} | {ref['href']}")
    lines += [
        "",
        "## Local Archive Evidence Role",
        "",
        "No external webpage screenshots were required for this run because the user specified a local conference archive. The retained CSV and JSON files serve as the row-level evidence appendix, preserving abstract numbers, EHA IDs, local source URLs, matched terms, classifications, and evidence excerpts.",
        "",
    ]
    (SOURCES / "source-log.md").write_text("\n".join(lines), encoding="utf-8")


def write_qa(records, candidates, summary, export_note="Not yet exported"):
    lines = [
        "# EHA 2026 AI Topics QA / Status Notes",
        "",
        f"- Build timestamp: {datetime.now(timezone.utc).isoformat()}",
        "- Retained records before weak-term audit: 187",
        f"- Retained records after weak-term audit: {len(records)}",
        f"- Records removed by weak-term audit: {187 - len(records)}",
        f"- Records screened: {summary.get('detail_rows')}",
        f"- Lexical candidates: {len(candidates)}",
        f"- Retained records: {len(records)}",
        f"- Retained share: {pct(len(records), int(summary.get('detail_rows') or len(records)))}",
        "- Source mode: local EHA 2026 archive. No external webpage screenshots were required or collected.",
        "- False-positive handling: the AI acronym now uses an exact non-word, non-hyphen, non-period leading boundary; weak-only classifier/model/automation terms, ordinary regression/Cox/logistic/linear model records, non-AI abbreviations, coding-only AI use, and ordinary automated assays were excluded when no explicit AI or machine-learning framing was present.",
        "- Auditability: retained CSV/JSON include abstract number, EHA abstract ID, source URL, matched terms, relevance rationale, derived classifications, and source evidence excerpt.",
        "- Formatting QA: the References table centers values in the first REF column; chip text uses the only bold styling in main body sections; body copy avoids strong tags.",
        f"- PDF/export status: {export_note}",
        "",
    ]
    (SOURCES / "qa_status.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    SOURCES.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    records, candidates = build_records()
    retained_csv = SOURCES / "retained_ai_records.csv"
    retained_json = SOURCES / "retained_ai_records.json"
    candidate_csv = SOURCES / "candidate_screen.csv"
    report_html = OUT / "report.html"
    report_pdf = OUT / "eha-2026-ai-topics-ci-report-05.31.26.pdf"

    retained_fields = [
        "record_ref",
        "content_id",
        "abstract_number",
        "eha_abstract_id",
        "title",
        "presentation_type",
        "session_title",
        "topic_name",
        "date",
        "authors",
        "keywords",
        "href",
        "matched_terms",
        "ai_cluster",
        "disease_area",
        "use_case",
        "method_type",
        "evidence_excerpt",
        "relevance_rationale",
    ]
    candidate_fields = [
        "content_id",
        "abstract_number",
        "eha_abstract_id",
        "title",
        "presentation_type",
        "topic_name",
        "matched_terms",
        "retained",
        "relevance_rationale",
        "href",
    ]
    write_csv(retained_csv, records, retained_fields)
    retained_json.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(candidate_csv, candidates, candidate_fields)

    html_doc = build_html(records, candidates, summary)
    report_html.write_text(html_doc, encoding="utf-8")

    refs = make_refs(records, summary)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_mode": "Full local archive screen: all requested EHA 2026 records scanned",
        "source_jsonl": str(SOURCE_JSONL),
        "source_jsonl_sha256": sha256(SOURCE_JSONL),
        "source_json": str(SOURCE_JSON),
        "source_json_sha256": sha256(SOURCE_JSON),
        "source_csv": str(SOURCE_CSV),
        "source_csv_sha256": sha256(SOURCE_CSV),
        "summary_json": str(SUMMARY_JSON),
        "summary_json_sha256": sha256(SUMMARY_JSON),
        "records_screened": summary.get("detail_rows"),
        "lexical_candidates": len(candidates),
        "retained_records": len(records),
        "retained_share": pct(len(records), int(summary.get("detail_rows") or len(records))),
        "category_counts": dict(count_by(records, "ai_cluster")),
        "disease_area_counts": dict(count_by(records, "disease_area")),
        "method_type_counts": dict(count_by(records, "method_type")),
        "presentation_type_counts": dict(count_by(records, "presentation_type")),
        "artifacts": {
            "retained_csv": str(retained_csv),
            "retained_json": str(retained_json),
            "candidate_screen_csv": str(candidate_csv),
            "source_log": str(SOURCES / "source-log.md"),
            "reference_screenshots_csv": str(SOURCES / "reference-screenshots.csv"),
            "report_html": str(report_html),
            "report_pdf": str(report_pdf),
            "qa_status": str(SOURCES / "qa_status.md"),
        },
    }
    (SOURCES / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (SOURCES / "reference-screenshots.csv").write_text("label,path,caption\n", encoding="utf-8")
    write_source_log(records, candidates, summary, refs, manifest)
    write_qa(records, candidates, summary)
    (SOURCES / "export_status.json").write_text(
        json.dumps(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "report_html": str(report_html),
                "report_pdf": str(report_pdf),
                "export_status": "pending external PDF export",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (OUT / "subagent_ai_record_audit.md").write_text(
        "\n".join(
            [
                "# AI Record Audit Subagent Note",
                "",
                "Scope: EHA 2026 local archive AI-topic screening.",
                "",
                f"- Screened records: {summary.get('detail_rows')}",
                f"- Lexical candidates: {len(candidates)}",
                f"- Retained records: {len(records)}",
                "- Audit approach: explicit keyword screening followed by rule-based relevance checks for weak-only model terms and ordinary statistical modeling false positives.",
                "- Evidence retained: abstract numbers, EHA IDs, URLs, matched terms, classifications, and excerpts in `sources/retained_ai_records.csv` and `sources/retained_ai_records.json`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (OUT / "subagent_cohere_style_ci_feedback.md").write_text(
        "\n".join(
            [
                "# Cohere-Style CI Feedback Applicability",
                "",
                "Applicable: yes, narrowly.",
                "",
                "This run reinforces that local conference-archive CI work should keep retained records, candidate screens, source logs, manifests, QA notes, HTML reports, and PDF exports together in one run folder. It also adds two useful formatting reminders for future biomedical CI reports: center reference identifiers in References tables, and keep chip emphasis scoped so body text remains neutral and unbolded.",
                "",
                "No skill file was modified because this worker's ownership is limited to `eha_2026_ai_topics`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"retained": len(records), "candidates": len(candidates), "html": str(report_html)}, indent=2))


if __name__ == "__main__":
    main()
