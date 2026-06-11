#!/usr/bin/env python3
"""Build curated ASCO 2026 congress intelligence data from local raw files.

The script reads the local ASCO-2026-Abstracts corpus and writes normalized,
source-linked extracts under this plan folder. Raw ASCO files are never edited.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SECTION_NAMES = ("Background", "Methods", "Results", "Conclusions", "Conclusion", "Trial Design", "Study Design")

SESSION_WEIGHTS = {
    "Plenary Session": 30,
    "Oral Abstract Session": 22,
    "Rapid Oral Abstract Session": 18,
    "Clinical Science Symposium": 16,
    "Poster Session": 8,
    "Publication Only": 2,
}

TUMOR_TRACK_RULES = [
    ("Quality Care/Health Services Research", "Quality care / health services research"),
    ("Care Delivery/Models of Care", "Care delivery / models of care"),
    ("Symptom Science and Palliative Care", "Symptom science / palliative care"),
    ("Developmental Therapeutics", "Developmental therapeutics"),
    ("Gastrointestinal Cancer", "Gastrointestinal cancer"),
    ("Lung Cancer", "Lung cancer"),
    ("Breast Cancer", "Breast cancer"),
    ("Genitourinary Cancer", "Genitourinary cancer"),
    ("Gynecologic Cancer", "Gynecologic cancer"),
    ("Hematologic Malignancies", "Hematologic malignancies"),
    ("Melanoma/Skin Cancers", "Melanoma / skin cancers"),
    ("Central Nervous System Tumors", "Central nervous system tumors"),
    ("Head and Neck Cancer", "Head and neck cancer"),
    ("Sarcoma", "Sarcoma"),
    ("Pediatric Oncology", "Pediatric oncology"),
    ("Prevention, Risk Reduction, and Genetics", "Prevention / genetics"),
    ("Cancer Prevention", "Prevention / genetics"),
    ("Medical Education", "Medical education"),
]

TUMOR_KEYWORD_RULES = [
    (r"\b(nsclc|sclc|lung cancer|thoracic)\b", "Lung cancer"),
    (r"\b(breast cancer|tnbc|her2|estrogen receptor|hr\+)\b", "Breast cancer"),
    (r"\b(colorectal|colon cancer|rectal|pancreatic|gastric|gastroesophageal|hcc|hepatocellular|biliary|cholangiocarcinoma)\b", "Gastrointestinal cancer"),
    (r"\b(prostate|urothelial|bladder|renal cell|kidney cancer|testicular)\b", "Genitourinary cancer"),
    (r"\b(ovarian|endometrial|cervical|gynecologic)\b", "Gynecologic cancer"),
    (r"\b(lymphoma|leukemia|myeloma|cll|aml|mds)\b", "Hematologic malignancies"),
    (r"\b(melanoma|cutaneous|skin cancer)\b", "Melanoma / skin cancers"),
    (r"\b(glioblastoma|glioma|brain tumor|cns)\b", "Central nervous system tumors"),
    (r"\b(sarcoma|desmoid)\b", "Sarcoma"),
    (r"\b(head and neck|oropharyngeal|nasopharyngeal)\b", "Head and neck cancer"),
    (r"\b(pediatric|children|adolescent)\b", "Pediatric oncology"),
]

EVIDENCE_KEYWORDS = {
    "clinical trial": [r"\bphase\s*(?:i|ii|iii|1|2|3|1/2|2/3)\b", r"\brandomi[sz]ed\b", r"\btrial\b"],
    "real-world evidence": [r"\breal[- ]world\b", r"\brwe\b", r"\bregistry\b", r"\bclaims\b", r"\belectronic health record"],
    "HEOR / value": [r"\bcost\b", r"\beconomic\b", r"\bbudget impact\b", r"\bvalue\b", r"\bhta\b", r"\bpayer\b", r"\breimbursement\b"],
    "PRO / QoL": [r"\bquality of life\b", r"\bhrqol\b", r"\bqol\b", r"\bpatient[- ]reported\b", r"\bpro\b", r"\bsymptom burden\b"],
    "safety": [r"\bsafety\b", r"\badverse event", r"\btoxicity\b", r"\btolerability\b", r"\bgrade [345]\b"],
    "biomarker / translational": [r"\bbiomarker\b", r"\bctdna\b", r"\bmrd\b", r"\bgenomic\b", r"\bmutation\b", r"\bpd-l1\b", r"\begfr\b", r"\bkras\b"],
    "AI / digital": [r"\bartificial intelligence\b", r"\bmachine learning\b", r"\bdeep learning\b", r"\bai[- ]based\b", r"\bdigital\b", r"\btelehealth\b"],
    "access / equity": [r"\baccess\b", r"\bequity\b", r"\bdisparit", r"\binsurance\b", r"\bfinancial toxicity\b", r"\bsocial determinant"],
    "care delivery": [r"\bcare delivery\b", r"\bmodels? of care\b", r"\bimplementation\b", r"\bremote monitoring\b", r"\bpalliative care\b"],
    "epidemiology / burden": [r"\bincidence\b", r"\bprevalence\b", r"\bmortality\b", r"\bburden\b", r"\bpopulation-based\b"],
}

ENDPOINT_KEYWORDS = {
    "OS": [r"\boverall survival\b", r"\bOS\b"],
    "PFS": [r"\bprogression[- ]free survival\b", r"\bPFS\b"],
    "EFS": [r"\bevent[- ]free survival\b", r"\bEFS\b"],
    "DFS/RFS": [r"\bdisease[- ]free survival\b", r"\bDFS\b", r"\brecurrence[- ]free survival\b", r"\bRFS\b"],
    "ORR/response": [r"\boverall response rate\b", r"\bobjective response rate\b", r"\bORR\b", r"\bresponse rate\b"],
    "DoR": [r"\bduration of response\b", r"\bDoR\b"],
    "MRD": [r"\bminimal residual disease\b", r"\bMRD\b"],
    "pCR": [r"\bpathologic complete response\b", r"\bpCR\b"],
    "safety": [r"\bsafety\b", r"\badverse event", r"\btoxicity\b", r"\btolerability\b"],
    "QoL/PRO": [r"\bquality of life\b", r"\bHRQoL\b", r"\bQoL\b", r"\bpatient[- ]reported\b", r"\bPRO\b"],
    "cost/resource": [r"\bcost\b", r"\bresource use\b", r"\bhospitali[sz]ation\b", r"\bdrug spending\b", r"\bfinancial toxicity\b"],
}

MODALITY_KEYWORDS = {
    "immunotherapy": [r"\bimmunotherapy\b", r"\banti[- ]?pd[- ]?1\b", r"\bpd-1\b", r"\bpd-l1\b", r"\bcheckpoint\b"],
    "targeted therapy": [r"\btargeted therap", r"\btyrosine kinase inhibitor\b", r"\bTKI\b", r"\bEGFR\b", r"\bALK\b", r"\bKRAS\b", r"\bBRAF\b"],
    "antibody-drug conjugate": [r"\bantibody[- ]drug conjugate\b", r"\bADC\b", r"\bvedotin\b", r"\bderuxtecan\b"],
    "cell therapy": [r"\bCAR[- ]?T\b", r"\bT[- ]cell\b", r"\bcell therapy\b"],
    "bispecific": [r"\bbispecific\b", r"\bbi-specific\b"],
    "radiopharmaceutical": [r"\bradioligand\b", r"\bradiopharmaceutical\b", r"\bLu-177\b", r"\byttrium"],
    "chemotherapy": [r"\bchemotherapy\b", r"\bcarboplatin\b", r"\bpaclitaxel\b", r"\bgemcitabine\b"],
    "radiation": [r"\bradiation\b", r"\bradiotherapy\b", r"\bsbrt\b"],
    "surgery": [r"\bsurgery\b", r"\bsurgical\b", r"\bresection\b"],
}

ROLE_DEFINITIONS = {
    "medical_affairs": "MSL/scientific exchange, KOL, biomarker, safety, mechanism, evidence caveats",
    "heor": "QoL, PRO, RWE, burden, cost, resource use, equity, model input",
    "market_access": "payer value, access, comparator, economic, QoL, safety, administration burden",
    "commercial": "positioning, differentiation, high-prominence data, competitive efficacy and safety",
    "launch": "launch readiness, pivotal/registrational evidence, scenario planning, field readiness",
}


def repair_mojibake(value: str) -> str:
    if not value:
        return ""
    value = value.replace("\r", "\n")
    marker_count = lambda text: sum(text.count(marker) for marker in ("â", "Â", "�"))
    best = value
    if marker_count(value):
        for encoding in ("latin1", "cp1252"):
            try:
                candidate = value.encode(encoding).decode("utf-8")
            except UnicodeError:
                continue
            if marker_count(candidate) < marker_count(best):
                best = candidate
    return best.replace("\xa0", " ")


class TextExtractor(HTMLParser):
    def __init__(self, skip_tables: bool = False) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_tables = skip_tables
        self.table_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self.table_depth += 1
        if self.skip_tables and self.table_depth:
            return
        if tag in {"p", "br", "div", "tr"}:
            self.parts.append("\n")
        elif tag in {"td", "th", "li"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self.table_depth:
            self.table_depth -= 1
        if self.skip_tables and self.table_depth:
            return
        if tag in {"p", "div", "tr", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_tables and self.table_depth:
            return
        self.parts.append(data)

    def text(self) -> str:
        return normalize_space(repair_mojibake(html.unescape("".join(self.parts))))


class TableExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.current_row: list[str] | None = None
        self.current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.current_row = []
        elif tag in {"td", "th"}:
            self.current_cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self.current_cell is not None:
            if self.current_row is not None:
                self.current_row.append(normalize_space(repair_mojibake(html.unescape("".join(self.current_cell)))))
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            if any(cell for cell in self.current_row):
                self.rows.append(self.current_row)
            self.current_row = None

    def handle_data(self, data: str) -> None:
        if self.current_cell is not None:
            self.current_cell.append(data)


def normalize_space(value: str) -> str:
    value = re.sub(r"[ \t\f\v]+", " ", value)
    value = re.sub(r" *\n+ *", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def html_to_text(fragment: str, skip_tables: bool = False) -> str:
    parser = TextExtractor(skip_tables=skip_tables)
    parser.feed(fragment or "")
    parser.close()
    return parser.text()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ms_to_utc_iso(value: Any) -> str:
    if not isinstance(value, int):
        return ""
    return datetime.fromtimestamp(value / 1000, timezone.utc).isoformat()


def asco_url(record: dict[str, Any]) -> str:
    content_url = record.get("contentUrl") or {}
    path = content_url.get("path") or f"/abstracts-presentations/{record.get('contentId', '')}"
    fqdn = content_url.get("fqdn")
    if fqdn:
        return f"https://{fqdn}{path}"
    return f"https://www.asco.org{path}"


def file_map_by_content_id(paths: list[Path]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in paths:
        parts = path.stem.split("_", 3)
        if len(parts) >= 3 and parts[2].isdigit():
            result[parts[2]] = path
    return result


def extract_labeled_divs(body_html: str, class_name: str) -> list[str]:
    pattern = re.compile(
        rf"<div[^>]*class=[\"'][^\"']*\b{re.escape(class_name)}\b[^\"']*[\"'][^>]*>(.*?)</div>",
        re.IGNORECASE | re.DOTALL,
    )
    return [html_to_text(match.group(1), skip_tables=False) for match in pattern.finditer(body_html or "")]


def remove_table_blocks(body_html: str) -> str:
    body_html = re.sub(r"<table\b.*?</table>", " ", body_html or "", flags=re.IGNORECASE | re.DOTALL)
    body_html = re.sub(
        r"<div[^>]*class=[\"'][^\"']*\btable_(?:caption|footer)\b[^\"']*[\"'][^>]*>.*?</div>",
        " ",
        body_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return body_html


def extract_sections(body_html: str) -> dict[str, str]:
    text = html_to_text(remove_table_blocks(body_html), skip_tables=True)
    label_pattern = re.compile(rf"\b({'|'.join(re.escape(name) for name in SECTION_NAMES)})\s*:", re.IGNORECASE)
    matches = list(label_pattern.finditer(text))
    sections: dict[str, list[str]] = defaultdict(list)
    if not matches:
        return {"unclassified": text} if text else {}
    prefix = normalize_space(text[: matches[0].start()])
    if prefix:
        sections["unclassified"].append(prefix)
    for index, match in enumerate(matches):
        label = match.group(1).lower()
        if label in {"conclusion", "conclusions"}:
            key = "conclusions"
        elif label in {"trial design", "study design"}:
            key = "methods"
        else:
            key = label
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = normalize_space(text[match.end() : end])
        if value:
            sections[key].append(value)
    return {key: "\n\n".join(values) for key, values in sections.items() if any(values)}


def extract_tables(body_html: str) -> list[dict[str, Any]]:
    table_blocks = list(re.finditer(r"<table\b.*?</table>", body_html or "", flags=re.IGNORECASE | re.DOTALL))
    captions = extract_labeled_divs(body_html, "table_caption")
    footers = extract_labeled_divs(body_html, "table_footer")
    tables: list[dict[str, Any]] = []
    for index, match in enumerate(table_blocks, start=1):
        parser = TableExtractor()
        parser.feed(match.group(0))
        parser.close()
        rows = parser.rows
        col_count = max((len(row) for row in rows), default=0)
        tables.append(
            {
                "table_number": index,
                "caption": captions[index - 1] if index - 1 < len(captions) else "",
                "footer": footers[index - 1] if index - 1 < len(footers) else "",
                "row_count": len(rows),
                "column_count": col_count,
                "rows": rows,
                "extraction_confidence": "high" if rows and col_count else "low",
            }
        )
    return tables


def first_related(record: dict[str, Any]) -> dict[str, Any]:
    related = record.get("relatedMaterials") or []
    return related[0] if related else {}


def session_type(record: dict[str, Any]) -> str:
    related = first_related(record)
    return related.get("sessionType") or "Publication Only"


def track_title(record: dict[str, Any]) -> str:
    titles = []
    for material in record.get("relatedMaterials") or []:
        title = material.get("title")
        if title and title not in titles:
            titles.append(repair_mojibake(title).strip())
    return " | ".join(titles)


def classify_tumor_area(track: str, combined_text: str) -> str:
    for needle, label in TUMOR_TRACK_RULES:
        if needle.lower() in track.lower():
            return label
    text = combined_text.lower()
    for pattern, label in TUMOR_KEYWORD_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return "Unclassified / cross-tumor"


def matched_labels(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    labels = []
    for label, patterns in keyword_map.items():
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            labels.append(label)
    return labels


def classify_phase(text: str) -> str:
    checks = [
        ("Phase 3", r"\bphase\s*(?:iii|3|2/3|ii/iii)\b"),
        ("Phase 2", r"\bphase\s*(?:ii|2|1/2|i/ii)\b"),
        ("Phase 1", r"\bphase\s*(?:i|1)\b"),
    ]
    for label, pattern in checks:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    if re.search(r"\btrial\b", text, re.IGNORECASE):
        return "Trial phase not specified"
    return ""


def classify_design(text: str) -> list[str]:
    rules = {
        "randomized": r"\brandomi[sz]ed\b",
        "prospective": r"\bprospective\b",
        "retrospective": r"\bretrospective\b",
        "observational": r"\bobservational\b",
        "real-world": r"\breal[- ]world\b",
        "meta-analysis": r"\bmeta[- ]analysis\b|\bsystematic review\b",
        "survey": r"\bsurvey\b",
        "case series": r"\bcase series\b",
        "modeling": r"\bmodel(?:ing|ling)\b|\bsimulation\b",
    }
    return [label for label, pattern in rules.items() if re.search(pattern, text, re.IGNORECASE)]


def line_of_therapy(text: str) -> list[str]:
    rules = {
        "first-line": r"\bfirst[- ]line\b|\b1L\b",
        "second-line": r"\bsecond[- ]line\b|\b2L\b",
        "third-line+": r"\bthird[- ]line\b|\b3L\b|\bpreviously treated\b|\brefractory\b|\brelapsed\b",
        "neoadjuvant": r"\bneoadjuvant\b",
        "adjuvant": r"\badjuvant\b",
        "maintenance": r"\bmaintenance\b",
    }
    return [label for label, pattern in rules.items() if re.search(pattern, text, re.IGNORECASE)]


def nct_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"\bNCT\d{8}\b", text, flags=re.IGNORECASE)))


def trial_acronyms(title: str, body_text: str) -> list[str]:
    candidates = set()
    for source in (title, body_text[:1200]):
        for match in re.finditer(r"\b[A-Z][A-Z0-9-]{2,}(?:\s?[A-Z0-9-]{2,}){0,2}\b", source):
            token = match.group(0).strip()
            if token in {"ASCO", "USA", "DNA", "RNA", "CDX", "RECIST"}:
                continue
            if any(char.isdigit() for char in token) or len(token) >= 4:
                candidates.add(token)
    return sorted(candidates)[:12]


def score_priority(
    abstract_number: str,
    session: str,
    phase: str,
    design: list[str],
    evidence_types: list[str],
    endpoints: list[str],
    modalities: list[str],
    text: str,
    table_count: int,
) -> tuple[int, str]:
    score = 10 + SESSION_WEIGHTS.get(session, 2)
    reasons = [f"session={session}"]
    if abstract_number.upper().startswith("LBA"):
        score += 15
        reasons.append("late-breaking abstract")
    elif abstract_number.lower().startswith("e"):
        score -= 3
        reasons.append("electronic/publication-only numbering")
    if phase == "Phase 3":
        score += 20
        reasons.append("phase 3")
    elif phase == "Phase 2":
        score += 10
        reasons.append("phase 2")
    elif phase == "Phase 1":
        score += 4
        reasons.append("early phase")
    if "randomized" in design:
        score += 8
        reasons.append("randomized design")
    if "real-world" in design or "real-world evidence" in evidence_types:
        score += 4
        reasons.append("real-world evidence")
    endpoint_weights = {
        "OS": 8,
        "PFS": 7,
        "EFS": 7,
        "DFS/RFS": 5,
        "ORR/response": 4,
        "DoR": 4,
        "MRD": 4,
        "pCR": 4,
        "safety": 5,
        "QoL/PRO": 5,
        "cost/resource": 4,
    }
    for endpoint in endpoints:
        score += endpoint_weights.get(endpoint, 0)
    if endpoints:
        reasons.append("endpoints=" + ", ".join(endpoints[:5]))
    novelty_patterns = {
        "first-in-human": 7,
        "pivotal": 8,
        "registrational": 8,
        "primary analysis": 6,
        "final analysis": 5,
        "interim analysis": 3,
        "long-term follow-up": 3,
        "new combination": 4,
    }
    for phrase, weight in novelty_patterns.items():
        if re.search(rf"\b{re.escape(phrase)}\b", text, re.IGNORECASE):
            score += weight
            reasons.append(phrase)
    if modalities:
        score += min(6, len(modalities) * 2)
        reasons.append("modality=" + ", ".join(modalities[:3]))
    if table_count:
        score += min(4, table_count)
        reasons.append(f"{table_count} parsed table(s)")
    if "safety" in evidence_types and "safety" not in endpoints:
        score += 3
    if "HEOR / value" in evidence_types or "PRO / QoL" in evidence_types:
        score += 4
    return max(0, min(100, score)), "; ".join(reasons)


def role_scores(
    priority: int,
    session: str,
    phase: str,
    design: list[str],
    evidence_types: list[str],
    endpoints: list[str],
    modalities: list[str],
    track: str,
    text: str,
) -> dict[str, tuple[int, str]]:
    prominent = session in {"Plenary Session", "Oral Abstract Session", "Rapid Oral Abstract Session", "Clinical Science Symposium"}
    base = int(priority * 0.35)
    scores: dict[str, list[Any]] = {
        role: [base, [f"priority base {base}"]] for role in ROLE_DEFINITIONS
    }
    if prominent:
        for role in scores:
            scores[role][0] += 8
            scores[role][1].append("prominent session")
    if phase in {"Phase 2", "Phase 3"}:
        for role in ("medical_affairs", "commercial", "launch", "market_access"):
            scores[role][0] += 8 if phase == "Phase 3" else 5
            scores[role][1].append(phase.lower())
    if "randomized" in design:
        for role in ("medical_affairs", "market_access", "commercial", "launch"):
            scores[role][0] += 6
            scores[role][1].append("randomized comparator")
    if any(endpoint in endpoints for endpoint in ("OS", "PFS", "EFS", "ORR/response", "DoR", "pCR", "MRD")):
        for role in ("medical_affairs", "commercial", "launch", "market_access"):
            scores[role][0] += 8
            scores[role][1].append("efficacy endpoint")
    if "safety" in endpoints or "safety" in evidence_types:
        for role in ("medical_affairs", "market_access", "commercial"):
            scores[role][0] += 7
            scores[role][1].append("safety signal")
    if "biomarker / translational" in evidence_types:
        scores["medical_affairs"][0] += 8
        scores["medical_affairs"][1].append("biomarker/translational")
    if any(item in evidence_types for item in ("HEOR / value", "PRO / QoL", "real-world evidence", "access / equity", "epidemiology / burden")):
        for role in ("heor", "market_access"):
            scores[role][0] += 14
            scores[role][1].append("HEOR/access evidence")
    if any(endpoint in endpoints for endpoint in ("QoL/PRO", "cost/resource")):
        for role in ("heor", "market_access", "launch"):
            scores[role][0] += 8
            scores[role][1].append("QoL/cost/resource endpoint")
    if re.search(r"\b(pivotal|registrational|approval|label|launch|field training|readiness)\b", text, re.IGNORECASE):
        scores["launch"][0] += 12
        scores["launch"][1].append("launch-readiness term")
    if re.search(r"\b(comparator|versus|vs\.?|head-to-head|standard of care)\b", text, re.IGNORECASE):
        for role in ("market_access", "commercial", "launch"):
            scores[role][0] += 7
            scores[role][1].append("comparative positioning")
    if re.search(r"\b(cost|payer|reimbursement|access|financial toxicity|administration|hospitali[sz]ation)\b", text, re.IGNORECASE):
        scores["market_access"][0] += 10
        scores["market_access"][1].append("payer/access term")
    if "Quality Care/Health Services Research" in track or "Care Delivery" in track or "Symptom Science" in track:
        scores["heor"][0] += 10
        scores["heor"][1].append("HEOR-relevant track")
    if modalities:
        for role in ("medical_affairs", "commercial", "launch"):
            scores[role][0] += 4
            scores[role][1].append("therapy modality")
    return {role: (min(100, int(score)), "; ".join(reasons)) for role, (score, reasons) in scores.items()}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("rb") as handle:
        return sum(1 for _ in handle)


def load_index_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        return max(0, sum(1 for _ in csv.DictReader(handle)))


def build_outputs(raw_dir: Path, output_dir: Path) -> dict[str, Any]:
    json_dir = raw_dir / "abstracts_json"
    html_dir = raw_dir / "abstracts_html"
    json_paths = sorted(json_dir.glob("*.json"))
    html_paths = sorted(html_dir.glob("*.html"))
    json_by_content = file_map_by_content_id(json_paths)
    html_by_content = file_map_by_content_id(html_paths)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = read_json(raw_dir / "manifest.json") if (raw_dir / "manifest.json").exists() else {}
    download_manifest = read_json(raw_dir / "download_manifest.json") if (raw_dir / "download_manifest.json").exists() else {}

    fact_rows: list[dict[str, Any]] = []
    section_rows: list[dict[str, Any]] = []
    table_rows: list[dict[str, Any]] = []
    table_json_rows: list[dict[str, Any]] = []
    topic_rows: list[dict[str, Any]] = []
    normalized_json_rows: list[dict[str, Any]] = []
    source_inventory_rows: list[dict[str, Any]] = []
    role_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)

    stats: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_dir": str(raw_dir),
        "output_dir": str(output_dir),
        "manifest_reported_total": (manifest.get("pagination") or {}).get("reportedTotal"),
        "download_manifest": {
            "expected_total": download_manifest.get("expected_total") or download_manifest.get("expectedTotal"),
            "downloaded_total": download_manifest.get("downloaded_total") or download_manifest.get("downloadedTotal"),
        },
        "json_file_count": len(json_paths),
        "html_file_count": len(html_paths),
        "jsonl_record_count": count_lines(raw_dir / "asco_2026_abstracts.jsonl"),
        "abstracts_jsonl_record_count": count_lines(raw_dir / "abstracts.jsonl"),
        "index_row_count": load_index_count(raw_dir / "abstracts_index.csv"),
    }

    top_level_sources = [
        raw_dir / "manifest.json",
        raw_dir / "download_manifest.json",
        raw_dir / "asco_2026_abstracts.jsonl",
        raw_dir / "abstracts.jsonl",
        raw_dir / "abstracts_index.csv",
    ]
    for path in top_level_sources:
        if path.exists():
            source_inventory_rows.append(
                {
                    "source_type": "top_level",
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )

    session_counter: Counter[str] = Counter()
    track_counter: Counter[str] = Counter()
    tumor_counter: Counter[str] = Counter()
    phase_counter: Counter[str] = Counter()
    section_counter: Counter[str] = Counter()
    priority_tier_counter: Counter[str] = Counter()
    missing_html: list[str] = []
    records_with_summary = 0
    records_with_body = 0
    records_with_sections = 0
    records_with_tables = 0
    total_tables = 0

    for json_path in json_paths:
        record = read_json(json_path)
        content_id = str(record.get("contentId") or "")
        html_path = html_by_content.get(content_id)
        if not html_path:
            missing_html.append(content_id)
        abstract_number = str(record.get("abstractNumber") or "")
        uid = str(record.get("uid") or f"PRESENTATION{content_id}")
        title = repair_mojibake(str(record.get("title") or ""))
        summary = repair_mojibake(str(record.get("summary") or ""))
        body_html = repair_mojibake(str(record.get("body") or ""))
        body_text = html_to_text(remove_table_blocks(body_html), skip_tables=True)
        sections = extract_sections(body_html)
        tables = extract_tables(body_html)
        table_count = len(tables)
        table_footers = extract_labeled_divs(body_html, "table_footer")
        session = session_type(record)
        track = track_title(record)
        combined = "\n".join([title, summary, track, body_text])
        tumor_area = classify_tumor_area(track, combined)
        evidence_types = matched_labels(combined, EVIDENCE_KEYWORDS)
        endpoints = matched_labels(combined, ENDPOINT_KEYWORDS)
        modalities = matched_labels(combined, MODALITY_KEYWORDS)
        phase = classify_phase(combined)
        design = classify_design(combined)
        lines = line_of_therapy(combined)
        ncts = nct_ids(combined)
        acronyms = trial_acronyms(title, body_text)
        priority_score, priority_rationale = score_priority(
            abstract_number,
            session,
            phase,
            design,
            evidence_types,
            endpoints,
            modalities,
            combined,
            table_count,
        )
        if priority_score >= 70:
            priority_tier = "high"
        elif priority_score >= 40:
            priority_tier = "medium"
        else:
            priority_tier = "watch"
        role_scored = role_scores(priority_score, session, phase, design, evidence_types, endpoints, modalities, track, combined)
        related = first_related(record)
        publish = record.get("publishDate") or {}
        updated = record.get("lastUpdated") or {}
        person = record.get("primaryPerson") or {}
        taxonomy = record.get("taxonomy") or {}
        source_url = asco_url(record)
        local_html_path = str(html_path) if html_path else ""
        json_hash = sha256_file(json_path)
        html_hash = sha256_file(html_path) if html_path else ""

        if summary:
            records_with_summary += 1
        if body_text:
            records_with_body += 1
        if sections:
            records_with_sections += 1
        if table_count:
            records_with_tables += 1
            total_tables += table_count

        session_counter[session] += 1
        track_counter[track or "(none)"] += 1
        tumor_counter[tumor_area] += 1
        phase_counter[phase or "(none)"] += 1
        priority_tier_counter[priority_tier] += 1
        for section_name in sections:
            section_counter[section_name] += 1

        fact = {
            "uid": uid,
            "contentId": content_id,
            "presentationId": record.get("presentationId") or content_id,
            "abstractNumber": abstract_number,
            "abstractNumberPrefix": re.match(r"^[A-Za-z]+", abstract_number).group(0) if re.match(r"^[A-Za-z]+", abstract_number) else "",
            "title": title,
            "meetingYear": (record.get("meeting") or {}).get("year") or "",
            "meetingName": record.get("meetingName") or "",
            "url": source_url,
            "localJsonPath": str(json_path),
            "localHtmlPath": local_html_path,
            "jsonSha256": json_hash,
            "htmlSha256": html_hash,
            "sessionType": session,
            "sessionTitle": related.get("title") or "",
            "sessionContentId": related.get("contentId") or "",
            "track": track,
            "publishDateUtc": ms_to_utc_iso(publish.get("start")),
            "lastUpdatedUtc": ms_to_utc_iso(updated.get("start")),
            "sourceTimeZone": publish.get("timeZone") or updated.get("timeZone") or "",
            "primaryPerson": repair_mojibake(person.get("displayName") or ""),
            "primaryPersonRole": person.get("role") or "",
            "hasAbstract": bool(record.get("hasAbstract")),
            "hasPosters": bool(record.get("hasPosters")),
            "hasSlides": bool(record.get("hasSlides")),
            "hasVideos": bool(record.get("hasVideos")),
            "summaryPresent": bool(summary),
            "bodyCharCount": len(body_text),
            "bodyTextSha256": hashlib.sha256(body_text.encode("utf-8")).hexdigest() if body_text else "",
            "tableCount": table_count,
            "taxonomySubjects": "; ".join(taxonomy.get("subjectsThes") or []),
            "taxonomyDrugs": "; ".join(taxonomy.get("drugsThes") or []),
            "taxonomyGenes": "; ".join(taxonomy.get("genesThes") or []),
            "taxonomyOrgs": "; ".join(taxonomy.get("orgThes") or []),
        }
        fact_rows.append(fact)

        for section_name, section_text in sections.items():
            section_rows.append(
                {
                    "uid": uid,
                    "contentId": content_id,
                    "abstractNumber": abstract_number,
                    "section": section_name,
                    "text": section_text,
                    "charCount": len(section_text),
                    "sourceJsonPath": str(json_path),
                    "sourceHtmlPath": local_html_path,
                }
            )
        for footer_index, footer_text in enumerate(table_footers, start=1):
            section_rows.append(
                {
                    "uid": uid,
                    "contentId": content_id,
                    "abstractNumber": abstract_number,
                    "section": f"table_footer_{footer_index}",
                    "text": footer_text,
                    "charCount": len(footer_text),
                    "sourceJsonPath": str(json_path),
                    "sourceHtmlPath": local_html_path,
                }
            )
            section_counter["table_footer"] += 1

        for table in tables:
            row = {
                "uid": uid,
                "contentId": content_id,
                "abstractNumber": abstract_number,
                "tableNumber": table["table_number"],
                "caption": table["caption"],
                "footer": table["footer"],
                "rowCount": table["row_count"],
                "columnCount": table["column_count"],
                "extractionConfidence": table["extraction_confidence"],
                "cellsJson": json.dumps(table["rows"], ensure_ascii=False),
                "sourceJsonPath": str(json_path),
                "sourceHtmlPath": local_html_path,
            }
            table_rows.append(row)
            table_json_rows.append({**{key: row[key] for key in row if key != "cellsJson"}, "rows": table["rows"]})

        topic = {
            "uid": uid,
            "contentId": content_id,
            "abstractNumber": abstract_number,
            "title": title,
            "sessionType": session,
            "track": track,
            "tumorArea": tumor_area,
            "studyPhase": phase,
            "studyDesign": "; ".join(design),
            "lineOfTherapy": "; ".join(lines),
            "evidenceTypes": "; ".join(evidence_types),
            "endpoints": "; ".join(endpoints),
            "modalities": "; ".join(modalities),
            "nctIds": "; ".join(ncts),
            "trialAcronyms": "; ".join(acronyms),
            "priorityScore": priority_score,
            "priorityTier": priority_tier,
            "priorityRationale": priority_rationale,
            "medicalAffairsScore": role_scored["medical_affairs"][0],
            "heorScore": role_scored["heor"][0],
            "marketAccessScore": role_scored["market_access"][0],
            "commercialScore": role_scored["commercial"][0],
            "launchScore": role_scored["launch"][0],
            "sourceUrl": source_url,
        }
        topic_rows.append(topic)
        normalized_json_rows.append({**fact, **topic, "sections": sections, "tableMetadata": [{k: v for k, v in table.items() if k != "rows"} for table in tables]})

        for role, (score, rationale) in role_scored.items():
            if score >= 30:
                role_rows[role].append(
                    {
                        "role": role,
                        "roleDefinition": ROLE_DEFINITIONS[role],
                        "roleRelevanceScore": score,
                        "roleRationale": rationale,
                        "priorityScore": priority_score,
                        "priorityTier": priority_tier,
                        "uid": uid,
                        "contentId": content_id,
                        "abstractNumber": abstract_number,
                        "title": title,
                        "sessionType": session,
                        "track": track,
                        "tumorArea": tumor_area,
                        "studyPhase": phase,
                        "studyDesign": "; ".join(design),
                        "evidenceTypes": "; ".join(evidence_types),
                        "endpoints": "; ".join(endpoints),
                        "modalities": "; ".join(modalities),
                        "lineOfTherapy": "; ".join(lines),
                        "nctIds": "; ".join(ncts),
                        "primaryPerson": fact["primaryPerson"],
                        "tableCount": table_count,
                        "sourceUrl": source_url,
                        "sourceJsonPath": str(json_path),
                        "sourceHtmlPath": local_html_path,
                    }
                )

        source_inventory_rows.append(
            {
                "source_type": "abstract_json",
                "path": str(json_path),
                "size_bytes": json_path.stat().st_size,
                "sha256": json_hash,
            }
        )
        if html_path:
            source_inventory_rows.append(
                {
                    "source_type": "abstract_html",
                    "path": str(html_path),
                    "size_bytes": html_path.stat().st_size,
                    "sha256": html_hash,
                }
            )

    for rows in role_rows.values():
        rows.sort(key=lambda row: (row["roleRelevanceScore"], row["priorityScore"]), reverse=True)
    topic_rows.sort(key=lambda row: row["priorityScore"], reverse=True)

    fact_fields = [
        "uid",
        "contentId",
        "presentationId",
        "abstractNumber",
        "abstractNumberPrefix",
        "title",
        "meetingYear",
        "meetingName",
        "url",
        "localJsonPath",
        "localHtmlPath",
        "jsonSha256",
        "htmlSha256",
        "sessionType",
        "sessionTitle",
        "sessionContentId",
        "track",
        "publishDateUtc",
        "lastUpdatedUtc",
        "sourceTimeZone",
        "primaryPerson",
        "primaryPersonRole",
        "hasAbstract",
        "hasPosters",
        "hasSlides",
        "hasVideos",
        "summaryPresent",
        "bodyCharCount",
        "bodyTextSha256",
        "tableCount",
        "taxonomySubjects",
        "taxonomyDrugs",
        "taxonomyGenes",
        "taxonomyOrgs",
    ]
    section_fields = ["uid", "contentId", "abstractNumber", "section", "text", "charCount", "sourceJsonPath", "sourceHtmlPath"]
    table_fields = [
        "uid",
        "contentId",
        "abstractNumber",
        "tableNumber",
        "caption",
        "footer",
        "rowCount",
        "columnCount",
        "extractionConfidence",
        "cellsJson",
        "sourceJsonPath",
        "sourceHtmlPath",
    ]
    topic_fields = [
        "uid",
        "contentId",
        "abstractNumber",
        "title",
        "sessionType",
        "track",
        "tumorArea",
        "studyPhase",
        "studyDesign",
        "lineOfTherapy",
        "evidenceTypes",
        "endpoints",
        "modalities",
        "nctIds",
        "trialAcronyms",
        "priorityScore",
        "priorityTier",
        "priorityRationale",
        "medicalAffairsScore",
        "heorScore",
        "marketAccessScore",
        "commercialScore",
        "launchScore",
        "sourceUrl",
    ]
    role_fields = [
        "role",
        "roleDefinition",
        "roleRelevanceScore",
        "roleRationale",
        "priorityScore",
        "priorityTier",
        "uid",
        "contentId",
        "abstractNumber",
        "title",
        "sessionType",
        "track",
        "tumorArea",
        "studyPhase",
        "studyDesign",
        "evidenceTypes",
        "endpoints",
        "modalities",
        "lineOfTherapy",
        "nctIds",
        "primaryPerson",
        "tableCount",
        "sourceUrl",
        "sourceJsonPath",
        "sourceHtmlPath",
    ]

    write_csv(output_dir / "abstract_fact.csv", fact_rows, fact_fields)
    write_csv(output_dir / "abstract_text_section.csv", section_rows, section_fields)
    write_csv(output_dir / "abstract_table.csv", table_rows, table_fields)
    write_jsonl(output_dir / "abstract_table.jsonl", table_json_rows)
    write_csv(output_dir / "topic_session_classification.csv", topic_rows, topic_fields)
    write_jsonl(output_dir / "normalized_abstracts.jsonl", normalized_json_rows)
    write_csv(output_dir / "source_inventory.csv", source_inventory_rows, ["source_type", "path", "size_bytes", "sha256"])
    for role, rows in role_rows.items():
        write_csv(output_dir / "role_specific" / f"{role}_priority_abstracts.csv", rows, role_fields)

    scoring_config = {
        "session_weights": SESSION_WEIGHTS,
        "priority_thresholds": {"high": ">=70", "medium": "40-69", "watch": "<40"},
        "role_output_threshold": "roleRelevanceScore >= 30",
        "role_definitions": ROLE_DEFINITIONS,
        "keyword_maps": {
            "evidence_types": EVIDENCE_KEYWORDS,
            "endpoints": ENDPOINT_KEYWORDS,
            "modalities": MODALITY_KEYWORDS,
        },
    }
    with (output_dir / "priority_scoring_config.json").open("w", encoding="utf-8") as handle:
        json.dump(scoring_config, handle, indent=2, ensure_ascii=False, sort_keys=True)

    role_counts = {role: len(rows) for role, rows in sorted(role_rows.items())}
    stats.update(
        {
            "processed_record_count": len(fact_rows),
            "records_with_body_text": records_with_body,
            "records_with_summary": records_with_summary,
            "records_with_any_section": records_with_sections,
            "section_row_count": len(section_rows),
            "section_counts": dict(section_counter),
            "records_with_tables": records_with_tables,
            "table_count": total_tables,
            "table_rows_written": len(table_rows),
            "missing_html_count": len(missing_html),
            "missing_html_content_ids": missing_html[:100],
            "session_type_counts": dict(session_counter.most_common()),
            "top_track_counts": dict(track_counter.most_common(30)),
            "tumor_area_counts": dict(tumor_counter.most_common()),
            "study_phase_counts": dict(phase_counter.most_common()),
            "priority_tier_counts": dict(priority_tier_counter.most_common()),
            "role_output_counts": role_counts,
            "output_files": {
                "abstract_fact": str(output_dir / "abstract_fact.csv"),
                "abstract_text_section": str(output_dir / "abstract_text_section.csv"),
                "abstract_table": str(output_dir / "abstract_table.csv"),
                "topic_session_classification": str(output_dir / "topic_session_classification.csv"),
                "normalized_abstracts": str(output_dir / "normalized_abstracts.jsonl"),
                "source_inventory": str(output_dir / "source_inventory.csv"),
                "role_specific_dir": str(output_dir / "role_specific"),
            },
        }
    )
    with (output_dir / "validation_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2, ensure_ascii=False, sort_keys=True)
    write_validation_markdown(output_dir / "validation_summary.md", stats)
    write_data_dictionary(output_dir / "data_dictionary.md")
    return stats


def write_validation_markdown(path: Path, stats: dict[str, Any]) -> None:
    lines = [
        "# ASCO 2026 data-processing validation summary",
        "",
        f"Generated at: `{stats['created_at']}`",
        "",
        "## Source reconciliation",
        "",
        f"- Manifest reported total: `{stats.get('manifest_reported_total')}`",
        f"- Download manifest expected/downloaded: `{(stats.get('download_manifest') or {}).get('expected_total')}` / `{(stats.get('download_manifest') or {}).get('downloaded_total')}`",
        f"- Per-abstract JSON files: `{stats.get('json_file_count')}`",
        f"- Per-abstract HTML files: `{stats.get('html_file_count')}`",
        f"- `asco_2026_abstracts.jsonl` lines: `{stats.get('jsonl_record_count')}`",
        f"- `abstracts.jsonl` lines: `{stats.get('abstracts_jsonl_record_count')}`",
        f"- `abstracts_index.csv` rows: `{stats.get('index_row_count')}`",
        f"- Missing HTML mappings: `{stats.get('missing_html_count')}`",
        "",
        "## Extraction counts",
        "",
        f"- Processed records: `{stats.get('processed_record_count')}`",
        f"- Records with clean body text: `{stats.get('records_with_body_text')}`",
        f"- Records with summary text: `{stats.get('records_with_summary')}`",
        f"- Records with extracted sections: `{stats.get('records_with_any_section')}`",
        f"- Section rows written: `{stats.get('section_row_count')}`",
        f"- Records with parsed HTML tables: `{stats.get('records_with_tables')}`",
        f"- Parsed HTML tables: `{stats.get('table_count')}`",
        "",
        "## Priority tiers",
        "",
    ]
    for tier, count in (stats.get("priority_tier_counts") or {}).items():
        lines.append(f"- {tier}: `{count}`")
    lines.extend(["", "## Role-specific outputs", ""])
    for role, count in (stats.get("role_output_counts") or {}).items():
        lines.append(f"- {role}: `{count}`")
    lines.extend(["", "## Session type counts", ""])
    for session, count in (stats.get("session_type_counts") or {}).items():
        lines.append(f"- {session}: `{count}`")
    lines.extend(["", "## Top tumor/topic areas", ""])
    for area, count in list((stats.get("tumor_area_counts") or {}).items())[:20]:
        lines.append(f"- {area}: `{count}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_data_dictionary(path: Path) -> None:
    content = """# ASCO 2026 curated data dictionary

Generated outputs are source-linked extracts derived from the local `ASCO-2026-Abstracts` corpus. Raw source files are not modified.

## `abstract_fact.csv`

One row per ASCO abstract. Key fields include `uid`, `contentId`, `presentationId`, `abstractNumber`, `title`, `meetingYear`, `meetingName`, source `url`, local raw file paths and hashes, `sessionType`, `track`, publication/update timestamps, first speaker, content availability flags, body length, body hash, table count, and available ASCO taxonomy fields.

## `abstract_text_section.csv`

Long-format section extraction. One row per extracted section per abstract. Sections include `background`, `methods`, `results`, `conclusions`, `unclassified`, and `table_footer_N` rows where ASCO HTML table footers were present.

## `abstract_table.csv` and `abstract_table.jsonl`

Parsed HTML table extraction. CSV contains one table per row with caption, footer, dimensions, confidence, and `cellsJson`. JSONL preserves the same table rows as nested arrays.

## `topic_session_classification.csv`

One row per abstract with rule-based classification from available ASCO fields and abstract text: session, track, tumor/topic area, study phase, design, line of therapy, evidence type, endpoints, modalities, NCT IDs, trial acronym candidates, priority score/tier, audience scores, and source URL.

## `role_specific/*.csv`

Role-filtered priority lists for Medical Affairs, HEOR, Market Access, Commercial, and Launch. Records are included when the role relevance score is at least 30 and are sorted by role relevance and overall priority.

## `source_inventory.csv`

SHA-256 source inventory for top-level ASCO files and per-abstract JSON/HTML files used by the pipeline.

## `priority_scoring_config.json`

Transparent scoring weights and keyword dictionaries used by the current processing run. Scores are triage aids, not analyst-approved conclusions.
"""
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    plan_dir = script_path.parents[1]
    repo_root = script_path.parents[3]
    parser = argparse.ArgumentParser(description="Process local ASCO 2026 abstracts into curated CI data outputs.")
    parser.add_argument("--raw-dir", type=Path, default=repo_root / "ASCO-2026-Abstracts", help="Local ASCO-2026-Abstracts corpus directory.")
    parser.add_argument("--output-dir", type=Path, default=plan_dir / "generated_data", help="Curated output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = build_outputs(args.raw_dir.resolve(), args.output_dir.resolve())
    print(json.dumps({k: stats[k] for k in ("processed_record_count", "records_with_tables", "table_count", "priority_tier_counts", "role_output_counts")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
