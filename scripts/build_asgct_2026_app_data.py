from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz


PDF_PATH = Path(r"C:\Users\Justin\Downloads\2026ASGCTAbstractPublication.pdf")
OUT_PATH = Path("docs/asgct-2026/assets/data/asgct-summary.json")
JS_OUT_PATH = Path("docs/asgct-2026/assets/data/asgct-summary.js")

THERAPY_PATTERNS = {
    "AAV / viral vector": r"\b(AAV|adeno-associated|lentiviral|adenoviral|viral vector|capsid|vectorized|VSV|oncolytic)\b",
    "RNA / oligo": r"\b(siRNA|RNA|mRNA|miRNA|oligonucleotide|ASO|antisense|splice|circRNA|exNA)\b",
    "Genome editing": r"\b(CRISPR|Cas9|Cas12|base edit|prime edit|gene edit|editing|zinc finger|TALEN)\b",
    "Cell therapy": r"\b(CAR[- ]?T|TCR|cell therapy|stem cell|HSC|HSPC|iPSC|NK cell|T cell|B cell)\b",
    "Gene regulation": r"\b(gene regulation|transcription factor|promoter|enhancer|epigen|CRISPRi|CRISPRa)\b",
    "Non-viral delivery": r"\b(lipid nanoparticle|LNP|nanoparticle|exosome|electroporation|polymer|tLNP|lipid)\b",
    "Manufacturing / analytics": r"\b(manufactur|CMC|potency|quality|assay|analytics|purification|scale[- ]?up|biodistribution|characterization)\b",
}

DISEASE_PATTERNS = {
    "Neurology": r"\b(neuro|brain|CNS|epilep|Dravet|Huntington|Parkinson|Alzheimer|deafness|hearing|spinal|muscular atrophy|ALS|Duchenne|DMD|prion)\b",
    "Oncology": r"\b(cancer|tumou?r|leukemia|lymphoma|myeloma|carcinoma|sarcoma|melanoma|oncolog|glioblastoma)\b",
    "Ophthalmology": r"\b(retina|ocular|eye|vision|blindness|photoreceptor|RPE|macular|Leber|choroideremia)\b",
    "Hematology": r"\b(hemophilia|sickle|thalassemia|blood|hematopoietic|anemia|coagulation|factor IX|factor VIII)\b",
    "Rare / metabolic": r"\b(lysosomal|metabolic|Fabry|Gaucher|MPS|Pompe|OTC|PKU|rare disease)\b",
    "Immunology / inflammation": r"\b(autoimmune|immunology|inflammation|inflammatory|T cell|B cell|cytokine|lupus|SLE)\b",
    "Cardiometabolic": r"\b(cardiac|heart|cardiomyopathy|diabetes|obesity|metabolic syndrome|lipid)\b",
}

ORG_HINTS = {
    "Industry": r"\b(Inc\.|Therapeutics|Pharmaceuticals|Biopharma|BioTherapeutics|Bio|Genetics|Genomics|Pharma|Company|Corporation|Ltd\.|LLC|GmbH)\b",
    "Academic / medical center": r"\b(University|Hospital|Institute|College|School|Medical Center|Children's|Clinic|CHU|NHS|Research Center)\b",
    "Government / nonprofit": r"\b(NIH|FDA|CDC|Foundation|Consortium|Association|National Institutes|Agency)\b",
}

COUNTRIES = (
    "United States",
    "United Kingdom",
    "Canada",
    "Australia",
    "Germany",
    "France",
    "China",
    "Japan",
    "Spain",
    "Italy",
    "Netherlands",
    "Switzerland",
    "Austria",
    "Belgium",
    "Brazil",
    "Denmark",
    "Finland",
    "India",
    "Ireland",
    "Israel",
    "Norway",
    "Singapore",
    "South Korea",
    "Sweden",
)

SECTION_LABELS = (
    "Introduction",
    "Background",
    "Objective",
    "Objectives",
    "Methods",
    "Materials and Methods",
    "Results",
    "Discussion",
    "Conclusion",
    "Conclusions",
    "Figure Legend",
    "Funding",
    "Acknowledgement",
    "Acknowledgements",
    "References",
)

TRIAL_ID_PATTERNS = (
    r"\bNCT\d{8}\b",
    r"\bEudraCT\s*\d{4}-\d{6}-\d{2}\b",
    r"\bISRCTN\d+\b",
    r"\bACTRN\d+\b",
    r"\bChiCTR[A-Z0-9]+\b",
    r"\bCTRI/\d{4}/\d{2}/\d+\b",
    r"\bEUCT\s*\d{4}-\d{6}-\d{2}\b",
)

PHASE_PATTERN = re.compile(
    r"\b(?:Phase|phase)\s*(?:I{1,3}|IV|V|1|2|3|4|1/2|2/3|I/II|II/III|Ia|Ib|IIa|IIb|IIIa|IIIb)(?:\s*[/-]\s*(?:I{1,3}|IV|1|2|3|4|II|III))?\b"
)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_pdf_text(value: str) -> str:
    replacements = {
        "\u00a0": " ",
        "\uf0b7": "-",
        "\uf0d8": "-",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return normalize_space(value)


def extract_lines(pdf_path: Path) -> tuple[list[dict[str, Any]], int]:
    doc = fitz.open(pdf_path)
    lines: list[dict[str, Any]] = []
    for page_index in range(1, doc.page_count):
        page = doc.load_page(page_index)
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                spans = line["spans"]
                text = normalize_pdf_text("".join(span["text"] for span in spans))
                if not text:
                    continue
                lines.append(
                    {
                        "page": page_index + 1,
                        "text": text,
                        "x": float(line["bbox"][0]),
                        "y": float(line["bbox"][1]),
                        "maxSize": max(span["size"] for span in spans),
                        "isBold": any("Bold" in span["font"] for span in spans),
                        "isItalic": any("Italic" in span["font"] for span in spans),
                    }
                )
    return lines, doc.page_count


def is_abstract_start(line: dict[str, Any]) -> re.Match[str] | None:
    if not line["isBold"] or line["maxSize"] < 12.4 or line["x"] > 100:
        return None
    match = re.match(r"^(\d{1,4})\s+(.+)$", line["text"])
    if not match:
        return None
    abstract_id = int(match.group(1))
    if abstract_id <= 0 or abstract_id == 2026:
        return None
    title_start = match.group(2)
    if re.match(r"^(mg|mL|weeks?|months?|years?|participants?|of|and|to)\b", title_start, re.I):
        return None
    return match


def is_category_line(line: dict[str, Any]) -> bool:
    text = line["text"]
    if not line["isBold"] or line["maxSize"] < 15 or line["x"] > 100:
        return False
    if not re.match(r"^[A-Z0-9]", text):
        return False
    if is_abstract_start(line):
        return False
    if is_section_label(text):
        return False
    if len(text) > 180 or re.search(r"[.;=]", text):
        return False
    return bool(re.search(r"[A-Za-z]", text))


def is_title_continuation(line: dict[str, Any]) -> bool:
    if not line["isBold"] or line["maxSize"] < 12 or line["x"] > 100:
        return False
    if is_category_line(line):
        return False
    if is_section_label(line["text"]):
        return False
    return True


def is_section_label(text: str) -> bool:
    return extract_section_label(text) is not None


def extract_section_label(text: str) -> tuple[str, str] | None:
    for label in sorted(SECTION_LABELS, key=len, reverse=True):
        pattern = rf"^({re.escape(label)})\b(?:\s*[:\-]\s*|\s+)?(.*)$"
        match = re.match(pattern, text, re.I)
        if not match:
            continue
        canonical = "Conclusion" if match.group(1).lower() == "conclusions" else match.group(1).title()
        if canonical == "Materials And Methods":
            canonical = "Materials and Methods"
        remainder = normalize_space(match.group(2))
        return canonical, remainder
    return None


def finalize_record(record: dict[str, Any]) -> dict[str, Any]:
    record["title"] = normalize_space(" ".join(record.pop("titleParts")))
    record["authors"] = normalize_space(" ".join(record.pop("authorLines")))
    record["affiliations"] = normalize_space(" ".join(record.pop("affiliationLines")))
    record["body"] = "\n".join(record.pop("bodyLines")).strip()
    return record


def parse_records(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current_category = "Unclassified"
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    stage = "outside"
    category_pending = False

    for line in lines:
        if is_category_line(line):
            current_category = line["text"]
            category_pending = True
            if current and stage == "title":
                stage = "authors"
            continue

        if (
            category_pending
            and line["isBold"]
            and line["maxSize"] >= 15
            and line["x"] <= 100
            and not is_abstract_start(line)
            and not is_section_label(line["text"])
            and len(line["text"]) <= 140
            and not re.search(r"[.;=]", line["text"])
        ):
            current_category = normalize_space(f"{current_category} {line['text']}")
            continue

        if current and stage == "title" and is_title_continuation(line):
            current["titleParts"].append(line["text"])
            continue

        start_match = is_abstract_start(line)
        if start_match:
            category_pending = False
            if current:
                records.append(finalize_record(current))
            current = {
                "id": int(start_match.group(1)),
                "section": current_category,
                "category": current_category,
                "page": line["page"],
                "titleParts": [start_match.group(2)],
                "authorLines": [],
                "affiliationLines": [],
                "bodyLines": [],
            }
            stage = "title"
            continue

        if current is None:
            continue

        if stage in {"title", "authors"}:
            if is_section_label(line["text"]):
                stage = "body"
            elif line["isItalic"] or (line["maxSize"] <= 10.5 and re.match(r"^\d+", line["text"])):
                stage = "affiliations"
            else:
                stage = "authors"

        if stage == "authors":
            current["authorLines"].append(line["text"])
            continue

        if stage == "affiliations":
            if is_section_label(line["text"]):
                stage = "body"
            elif line["isItalic"] or line["maxSize"] <= 10.5:
                current["affiliationLines"].append(line["text"])
                continue
            else:
                stage = "body"

        current["bodyLines"].append(line["text"])

    if current:
        records.append(finalize_record(current))

    return dedupe_records(records)


def dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for record in records:
        key = (record["id"], record["title"].lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def split_people(value: str) -> list[str]:
    people = []
    for part in re.split(r",\s+|;\s+", value):
        cleaned = normalize_space(re.sub(r"\s*\d+(?:\s+\d+)*$", "", part))
        if cleaned:
            people.append(cleaned)
    return people


def split_affiliations(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"\s*(?=\d+[A-Z])", value)
    affiliations = []
    for part in parts:
        cleaned = normalize_space(re.sub(r"^\d+\s*", "", part))
        if cleaned:
            affiliations.append(cleaned)
    return affiliations


def structured_sections(body: str) -> list[dict[str, str]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    def ensure_section(label: str) -> dict[str, Any]:
        nonlocal current
        current = {"label": label, "lines": []}
        sections.append(current)
        return current

    for raw_line in body.splitlines():
        line = normalize_space(raw_line)
        if not line:
            continue
        label_match = extract_section_label(line)
        if label_match:
            label, remainder = label_match
            current = ensure_section(label)
            if remainder:
                current["lines"].append(remainder)
            continue
        if current is None:
            current = ensure_section("Body")
        current["lines"].append(line)

    return [
        {"label": section["label"], "text": normalize_space(" ".join(section["lines"]))}
        for section in sections
        if normalize_space(" ".join(section["lines"]))
    ]


def extract_trial_ids(text: str) -> list[str]:
    found: list[str] = []
    for pattern in TRIAL_ID_PATTERNS:
        found.extend(re.findall(pattern, text, re.I))
    return sorted({normalize_space(item).upper().replace(" ", "") if item.upper().startswith("NCT") else normalize_space(item) for item in found})


def extract_phase_mentions(text: str) -> list[str]:
    return sorted({normalize_space(match.group(0)) for match in PHASE_PATTERN.finditer(text)}, key=str.lower)


def split_record(record: dict[str, Any]) -> dict[str, Any]:
    title = normalize_space(record["title"])
    authors = normalize_space(record["authors"])
    affiliations = normalize_space(record["affiliations"])
    sections = structured_sections(record["body"])
    abstract_body = normalize_space(" ".join(section["text"] for section in sections)) or normalize_space(record["body"])
    full_text = "\n".join([title, authors, affiliations, abstract_body])

    author_list = split_people(authors)
    first_author = author_list[0] if author_list else "Unknown"

    org_type = "Unclassified"
    for label, pattern in ORG_HINTS.items():
        if re.search(pattern, affiliations, re.I):
            org_type = label
            break

    countries = [country for country in COUNTRIES if country in affiliations]
    body_for_classification = " ".join([title, abstract_body[:9000], affiliations[:1500]])
    therapies = [label for label, pattern in THERAPY_PATTERNS.items() if re.search(pattern, body_for_classification, re.I)]
    diseases = [label for label, pattern in DISEASE_PATTERNS.items() if re.search(pattern, body_for_classification, re.I)]
    trial_ids = extract_trial_ids(full_text)
    phase_mentions = extract_phase_mentions(full_text)
    section_map: dict[str, str] = {}
    for section in sections:
        label = section["label"]
        if label in section_map:
            section_map[label] = normalize_space(f"{section_map[label]} {section['text']}")
        else:
            section_map[label] = section["text"]
    extraction_warnings = []
    if not sections:
        extraction_warnings.append("missing structured sections")
    for required in ("Introduction", "Methods", "Results", "Conclusion"):
        if required not in section_map:
            extraction_warnings.append(f"missing {required.lower()} section")

    return {
        "uid": f"asgct-2026-{record['id']}-{record['page']}",
        "id": record["id"],
        "abstractId": record["id"],
        "idBand": "main" if record["id"] < 1000 else str(record["id"] // 1000 * 1000),
        "section": record["section"],
        "category": record.get("category") or record["section"],
        "title": title,
        "authors": authors,
        "authorsRaw": authors,
        "authorList": author_list,
        "firstAuthor": first_author,
        "affiliations": affiliations,
        "affiliationsRaw": affiliations,
        "affiliationList": split_affiliations(affiliations),
        "affiliationRecords": [{"index": index + 1, "text": value} for index, value in enumerate(split_affiliations(affiliations))],
        "organizationType": org_type,
        "countries": countries[:6],
        "therapyAreas": therapies or ["Other / not classified"],
        "therapies": therapies or ["Other / not classified"],
        "diseaseAreas": diseases or ["Other / not classified"],
        "diseases": diseases or ["Other / not classified"],
        "trialIds": trial_ids,
        "nctIds": trial_ids,
        "hasClinicalTrialId": bool(trial_ids),
        "phaseMentions": phase_mentions,
        "phases": phase_mentions,
        "mentionsPhase": bool(phase_mentions),
        "page": record["page"],
        "abstractSections": sections,
        "sections": section_map,
        "body": abstract_body,
        "abstractText": abstract_body,
        "abstractTextLength": len(abstract_body),
        "rawBody": record["body"],
        "extractionWarnings": extraction_warnings,
    }


def counter_rows(counter: Counter, limit: int | None = None) -> list[dict[str, Any]]:
    return [{"name": key, "count": value} for key, value in counter.most_common(limit)]


def build_summary(records: list[dict[str, Any]], page_count: int) -> dict[str, Any]:
    parsed = [split_record(record) for record in records]
    sections = Counter(item["section"] for item in parsed)
    therapies = Counter(label for item in parsed for label in item["therapyAreas"])
    diseases = Counter(label for item in parsed for label in item["diseaseAreas"])
    org_types = Counter(item["organizationType"] for item in parsed)
    countries = Counter(country for item in parsed for country in item["countries"])

    by_section: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "section": "",
            "count": 0,
            "clinicalTrialMentions": 0,
            "phaseMentions": 0,
            "therapyCounts": Counter(),
            "diseaseCounts": Counter(),
        }
    )
    for item in parsed:
        row = by_section[item["section"]]
        row["section"] = item["section"]
        row["count"] += 1
        row["clinicalTrialMentions"] += int(item["hasClinicalTrialId"])
        row["phaseMentions"] += int(item["mentionsPhase"])
        row["therapyCounts"].update(item["therapyAreas"])
        row["diseaseCounts"].update(item["diseaseAreas"])

    section_rows = []
    for row in sorted(by_section.values(), key=lambda value: value["count"], reverse=True):
        section_rows.append(
            {
                "section": row["section"],
                "count": row["count"],
                "clinicalTrialMentions": row["clinicalTrialMentions"],
                "phaseMentions": row["phaseMentions"],
                "topTherapy": row["therapyCounts"].most_common(1)[0][0] if row["therapyCounts"] else "Other",
                "topDisease": row["diseaseCounts"].most_common(1)[0][0] if row["diseaseCounts"] else "Other",
            }
        )

    samples = []
    seen_sections = set()
    for item in parsed:
        if item["section"] in seen_sections:
            continue
        samples.append(item)
        seen_sections.add(item["section"])
        if len(samples) >= 12:
            break

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFile": PDF_PATH.name,
        "sourcePageCount": page_count,
        "note": "Structured metadata, full abstract text, and aggregate classifications derived from the PDF.",
        "nationalTotals": {
            "abstracts": len(parsed),
            "sections": len(sections),
            "therapyCategories": len(therapies),
            "diseaseCategories": len(diseases),
            "withStructuredSections": sum(1 for item in parsed if item["sections"]),
            "withClinicalTrialIds": sum(1 for item in parsed if item["hasClinicalTrialId"]),
        },
        "categories": [
            {"key": "therapy", "name": "Therapy modality", "count": sum(therapies.values()), "rows": counter_rows(therapies, 12), "color": "#1b60e9"},
            {"key": "disease", "name": "Disease signal", "count": sum(diseases.values()), "rows": counter_rows(diseases, 12), "color": "#237b7f"},
            {"key": "organization", "name": "Organization type", "count": sum(org_types.values()), "rows": counter_rows(org_types), "color": "#925c54"},
        ],
        "sectionRows": section_rows[:28],
        "topSections": counter_rows(sections, 15),
        "countryRows": counter_rows(countries, 12),
        "sampleRecords": samples,
        "abstracts": parsed,
    }


def main() -> None:
    lines, page_count = extract_lines(PDF_PATH)
    records = parse_records(lines)
    summary = build_summary(records, page_count)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(summary, indent=2, ensure_ascii=False)
    OUT_PATH.write_text(json_text, encoding="utf-8")
    JS_OUT_PATH.write_text(f"window.ASGCT_SUMMARY = {json_text};\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} with {summary['nationalTotals']['abstracts']} parsed abstracts.")


if __name__ == "__main__":
    main()
