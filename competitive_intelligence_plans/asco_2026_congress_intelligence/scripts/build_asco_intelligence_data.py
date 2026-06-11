#!/usr/bin/env python3
"""Build derived ASCO 2026 abstract review data products."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
ASCO_DIR = WORKSPACE / "ASCO-2026-Abstracts"
RAW_JSONL = ASCO_DIR / "asco_2026_abstracts.jsonl"
RAW_INDEX = ASCO_DIR / "abstracts_index.csv"
RAW_MANIFEST = ASCO_DIR / "download_manifest.json"
OUT = ROOT / "generated_data"
ROLE_OUT = OUT / "role_outputs"


ROLE_KEYWORDS = {
    "Medical Affairs": [
        "biomarker",
        "mechanism",
        "safety",
        "toxicity",
        "adverse",
        "subgroup",
        "overall survival",
        "progression-free",
        "response",
        "randomized",
        "phase 3",
        "phase iii",
    ],
    "HEOR": [
        "quality of life",
        "qol",
        "patient-reported",
        "real-world",
        "retrospective",
        "cost",
        "burden",
        "resource",
        "hospitalization",
        "adherence",
        "equity",
        "disparit",
        "claims",
        "ehr",
        "medicare",
        "medicaid",
    ],
    "Market Access": [
        "cost",
        "payer",
        "coverage",
        "access",
        "value",
        "budget",
        "resource",
        "hospitalization",
        "quality of life",
        "adherence",
        "medicare",
        "medicaid",
        "formulary",
    ],
    "Commercial": [
        "phase 3",
        "phase iii",
        "randomized",
        "versus",
        "compared",
        "first-line",
        "second-line",
        "overall survival",
        "progression-free",
        "objective response",
        "late-breaking",
        "lba",
    ],
    "Launch": [
        "phase 3",
        "phase iii",
        "registrational",
        "pivotal",
        "first-line",
        "label",
        "guideline",
        "unmet",
        "readiness",
        "launch",
        "approval",
    ],
}

TRACK_ROLE_BOOSTS = {
    "Quality Care/Health Services Research": ["HEOR", "Market Access"],
    "Care Delivery/Models of Care": ["HEOR", "Market Access"],
    "Symptom Science and Palliative Care": ["HEOR", "Medical Affairs"],
}

SESSION_WEIGHTS = {
    "Plenary Session": 45,
    "Oral Abstract Session": 36,
    "Rapid Oral Abstract Session": 32,
    "Clinical Science Symposium": 28,
    "Poster Session": 18,
    "Publication Only": 8,
}

PIPELINE_STEPS = [
    {
        "name": "Ingest",
        "status": "complete",
        "description": "Raw ASCO GraphQL export and per-abstract JSON/HTML files reconciled.",
    },
    {
        "name": "Normalize",
        "status": "complete",
        "description": "Sections, tables, session fields, tracks, and searchable text extracted.",
    },
    {
        "name": "Prioritize",
        "status": "complete",
        "description": "Abstracts scored by session prominence, evidence maturity, endpoint terms, and role relevance.",
    },
    {
        "name": "Enrich",
        "status": "ready",
        "description": "Selected abstracts identified for registry, publication, label, and guideline source review.",
    },
    {
        "name": "Review",
        "status": "ready",
        "description": "Analyst review required before using extracted interpretations outside the review dataset.",
    },
]

ROLE_DESCRIPTIONS = {
    "Medical Affairs": "Clinical evidence, mechanism, safety, biomarker, and subgroup relevance.",
    "HEOR": "Real-world evidence, patient-reported outcomes, burden, resource use, and equity relevance.",
    "Market Access": "Evidence related to access, cost, resource use, value assessment, and payer-relevant endpoints.",
    "Commercial": "Comparative clinical evidence, treatment-line context, endpoint maturity, and competitive comparator relevance.",
    "Launch": "Evidence related to registrational studies, label context, guideline relevance, and evidence gaps.",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_tags(value: str) -> str:
    value = re.sub(r"(?i)<br\s*/?>", "\n", value)
    value = re.sub(r"(?i)</p\s*>", "\n", value)
    value = re.sub(r"(?i)</div\s*>", "\n", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def display_text(value: str | None) -> str:
    text = strip_tags(str(value or ""))
    text = text.replace("—", ": ")
    text = text.replace("–", "-")
    text = text.replace("‑", "-")
    return re.sub(r"\s+", " ", text).strip()


def extract_sections(body_html: str) -> dict[str, str]:
    text = strip_tags(body_html or "")
    labels = ["Background", "Methods", "Results", "Conclusions"]
    sections: dict[str, str] = {}
    matches = list(
        re.finditer(r"\b(Background|Methods|Results|Conclusions)\s*:\s*", text, re.I)
    )
    for idx, match in enumerate(matches):
        label = match.group(1).title()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[label.lower()] = text[start:end].strip()
    for label in labels:
        sections.setdefault(label.lower(), "")
    sections["plain_text"] = text
    return sections


def related_session_and_track(record: dict) -> tuple[str, str]:
    related = record.get("relatedMaterials") or []
    for item in related:
        session_type = item.get("sessionType")
        title = item.get("title")
        if session_type or title:
            return session_type or "Publication Only", title or ""
    return "Publication Only", ""


def abstract_url(record: dict) -> str:
    content_url = record.get("contentUrl") or {}
    path = content_url.get("path") or f"/abstracts-presentations/{record.get('contentId')}"
    fqdn = content_url.get("fqdn") or "www.asco.org"
    return f"https://{fqdn}{path}"


def classify_role_hits(text: str, track: str, abstract_number: str) -> dict[str, int]:
    lower = f"{text} {track} {abstract_number}".lower()
    hits: dict[str, int] = {}
    for role, terms in ROLE_KEYWORDS.items():
        hits[role] = sum(1 for term in terms if term in lower)
    for source_track, roles in TRACK_ROLE_BOOSTS.items():
        if source_track.lower() in track.lower():
            for role in roles:
                hits[role] += 3
    return hits


def evidence_tags(text: str, abstract_number: str) -> list[str]:
    lower = f"{text} {abstract_number}".lower()
    tags: list[str] = []
    checks = [
        ("Late breaking", abstract_number.upper().startswith("LBA")),
        ("Trial in progress", abstract_number.upper().startswith("TPS") or "trial in progress" in lower),
        ("Phase 3", "phase 3" in lower or "phase iii" in lower),
        ("Randomized", "randomized" in lower or "randomised" in lower),
        ("Overall survival", "overall survival" in lower or re.search(r"\bos\b", lower) is not None),
        ("Progression-free survival", "progression-free" in lower or re.search(r"\bpfs\b", lower) is not None),
        ("Objective response", "objective response" in lower or re.search(r"\borr\b", lower) is not None),
        ("Patient-reported outcomes", "patient-reported" in lower or "quality of life" in lower or "qol" in lower),
        ("Real-world evidence", "real-world" in lower or "retrospective" in lower or "claims" in lower),
        ("Biomarker", "biomarker" in lower or "ctdna" in lower or "mutation" in lower),
        ("Safety", "safety" in lower or "toxicity" in lower or "adverse event" in lower),
    ]
    for label, keep in checks:
        if keep:
            tags.append(label)
    return tags[:8]


def score_record(record: dict, sections: dict[str, str], session_type: str, track: str) -> tuple[int, list[str], dict[str, int]]:
    abstract_number = str(record.get("abstractNumber") or "")
    text = " ".join(
        [
            str(record.get("title") or ""),
            str(record.get("summary") or ""),
            sections.get("plain_text", ""),
            track,
        ]
    )
    tags = evidence_tags(text, abstract_number)
    role_hits = classify_role_hits(text, track, abstract_number)
    score = SESSION_WEIGHTS.get(session_type, 8)
    score += min(24, sum(role_hits.values()) * 2)
    score += 25 if abstract_number.upper().startswith("LBA") else 0
    score += 8 if abstract_number.upper().startswith("TPS") else 0
    score += 7 if record.get("posterBoardNumber") else 0
    if record.get("body") and "<table" in record["body"].lower():
        score += 5
    if "Phase 3" in tags:
        score += 12
    if "Randomized" in tags:
        score += 8
    if "Overall survival" in tags or "Progression-free survival" in tags:
        score += 8
    return score, tags, role_hits


def read_records() -> list[dict]:
    records = []
    with RAW_JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_dashboard_js(path: Path, payload) -> None:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    path.write_text(f"window.ASCO_DASHBOARD_DATA = {encoded};\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ROLE_OUT.mkdir(parents=True, exist_ok=True)
    records = read_records()
    normalized = []
    session_counts: Counter[str] = Counter()
    track_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()

    norm_path = OUT / "normalized_abstracts.jsonl"
    with norm_path.open("w", encoding="utf-8", newline="\n") as norm_file:
        for record in records:
            sections = extract_sections(record.get("body") or "")
            session_type, track = related_session_and_track(record)
            score, tags, role_hits = score_record(record, sections, session_type, track)
            roles = [role for role, count in role_hits.items() if count > 0]
            if not roles:
                roles = ["Medical Affairs"]
            table_count = len(re.findall(r"(?i)<table\b", record.get("body") or ""))
            item = {
                "uid": record.get("uid"),
                "contentId": record.get("contentId"),
                "presentationId": record.get("presentationId"),
                "abstractNumber": record.get("abstractNumber"),
                "title": display_text(record.get("title")),
                "primaryPerson": (record.get("primaryPerson") or {}).get("displayName"),
                "meetingName": record.get("meetingName"),
                "meetingYear": (record.get("meeting") or {}).get("year"),
                "url": abstract_url(record),
                "sessionType": display_text(session_type),
                "track": display_text(track),
                "posterBoardNumber": record.get("posterBoardNumber"),
                "summary": display_text(record.get("summary") or sections.get("background")[:420]),
                "sections": {key: display_text(sections[key]) for key in ["background", "methods", "results", "conclusions"]},
                "plainTextLength": len(sections.get("plain_text", "")),
                "tableCount": table_count,
                "hasSummary": bool(record.get("summary")),
                "hasPosterFlag": bool(record.get("hasPosters")),
                "hasSlideFlag": bool(record.get("hasSlides")),
                "hasVideoFlag": bool(record.get("hasVideos")),
                "priorityScore": score,
                "evidenceTags": [display_text(tag) for tag in tags],
                "roleRelevance": role_hits,
                "recommendedRoles": roles,
            }
            normalized.append(item)
            norm_file.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
            session_counts[session_type] += 1
            track_counts[item["track"] or "Publication only"] += 1
            for role in roles:
                role_counts[role] += 1
            for tag in tags:
                tag_counts[tag] += 1

    priority = sorted(
        normalized,
        key=lambda x: (x["priorityScore"], x["sessionType"] != "Publication Only", x["abstractNumber"] or ""),
        reverse=True,
    )

    priority_signals = []
    for item in priority[:250]:
        role = max(item["roleRelevance"], key=item["roleRelevance"].get)
        priority_signals.append(
            {
                "uid": item["uid"],
                "abstractNumber": item["abstractNumber"],
                "title": display_text(item["title"]),
                "speaker": item["primaryPerson"],
                "track": display_text(item["track"] or "Publication only"),
                "sessionType": display_text(item["sessionType"]),
                "url": item["url"],
                "score": item["priorityScore"],
                "primaryRole": role,
                "roles": item["recommendedRoles"],
                "tags": [display_text(tag) for tag in item["evidenceTags"]],
                "summary": display_text(item["summary"]),
                "sections": item["sections"],
                "tableCount": item["tableCount"],
            }
        )

    abstract_index = [
        {
            "uid": item["uid"],
            "contentId": item["contentId"],
            "abstractNumber": item["abstractNumber"],
            "title": display_text(item["title"]),
            "speaker": item["primaryPerson"],
            "track": display_text(item["track"] or "Publication only"),
            "sessionType": display_text(item["sessionType"]),
            "url": item["url"],
            "score": item["priorityScore"],
            "roleScores": item["roleRelevance"],
            "primaryRole": max(item["roleRelevance"], key=item["roleRelevance"].get),
            "roles": item["recommendedRoles"],
            "tags": [display_text(tag) for tag in item["evidenceTags"]],
            "summary": display_text(item["summary"]),
            "sections": item["sections"],
            "tableCount": item["tableCount"],
        }
        for item in sorted(normalized, key=lambda x: (x["abstractNumber"] or "", x["contentId"] or ""))
    ]

    role_payloads = {}
    role_total_counts = {}
    for role in ROLE_KEYWORDS:
        rows = [
            item
            for item in priority
            if role in item["recommendedRoles"] or item["roleRelevance"].get(role, 0) > 0
        ]
        rows = sorted(
            rows,
            key=lambda item: (
                item["roleRelevance"].get(role, 0),
                max(item["roleRelevance"], key=item["roleRelevance"].get) == role,
                item["priorityScore"],
                SESSION_WEIGHTS.get(item["sessionType"], 8),
                item["abstractNumber"] or "",
            ),
            reverse=True,
        )
        role_total_counts[role] = len(rows)
        top_rows = rows[:120]
        role_payloads[role] = [
            {
                "uid": item["uid"],
                "abstractNumber": item["abstractNumber"],
                "title": display_text(item["title"]),
                "sessionType": display_text(item["sessionType"]),
                "track": display_text(item["track"] or "Publication only"),
                "score": item["priorityScore"],
                "roleScore": item["roleRelevance"].get(role, 0),
                "url": item["url"],
                "tags": [display_text(tag) for tag in item["evidenceTags"]],
                "summary": display_text(item["summary"]),
            }
            for item in top_rows
        ]
        slug = role.lower().replace(" ", "_")
        write_json(ROLE_OUT / f"{slug}.json", role_payloads[role])
        with (ROLE_OUT / f"{slug}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["uid", "abstractNumber", "title", "sessionType", "track", "score", "roleScore", "url", "tags"],
                extrasaction="ignore",
            )
            writer.writeheader()
            for row in role_payloads[role]:
                writer.writerow({**row, "tags": "; ".join(row["tags"])})

    with (OUT / "abstract_facts.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "uid",
                "contentId",
                "abstractNumber",
                "title",
                "primaryPerson",
                "sessionType",
                "track",
                "priorityScore",
                "recommendedRoles",
                "evidenceTags",
                "url",
            ],
        )
        writer.writeheader()
        for item in normalized:
            writer.writerow(
                {
                    "uid": item["uid"],
                    "contentId": item["contentId"],
                    "abstractNumber": item["abstractNumber"],
                    "title": item["title"],
                    "primaryPerson": item["primaryPerson"],
                    "sessionType": item["sessionType"],
                    "track": item["track"],
                    "priorityScore": item["priorityScore"],
                    "recommendedRoles": "; ".join(item["recommendedRoles"]),
                    "evidenceTags": "; ".join(item["evidenceTags"]),
                    "url": item["url"],
                }
            )

    manifest = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
    manifest_filters = {
        item.get("type"): item.get("buckets", [])
        for item in manifest.get("filters", [])
    }
    manifest_tracks = [
        {"name": display_text(bucket.get("displayName") or bucket.get("key")), "count": bucket.get("doc_count") or 0}
        for bucket in manifest_filters.get("TRACK", [])
    ]

    dashboard_data = {
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "name": "ASCO 2026 Annual Meeting abstracts",
            "records": len(normalized),
            "rawJsonl": str(RAW_JSONL),
            "sourcePage": manifest.get("source_page"),
            "apiUrl": manifest.get("api_url"),
            "downloadedAtUtc": manifest.get("downloaded_at_utc"),
            "sha256": sha256(RAW_JSONL),
        },
        "metrics": [
            {"label": "Abstract records", "value": len(normalized), "tone": "lime"},
            {"label": "With HTML tables", "value": sum(1 for x in normalized if x["tableCount"]), "tone": "blue"},
            {"label": "Late-breaking", "value": sum(1 for x in normalized if str(x["abstractNumber"] or "").upper().startswith("LBA")), "tone": "orange"},
            {"label": "Role classifications", "value": len(ROLE_KEYWORDS), "tone": "pink"},
        ],
        "sessionTypes": [
            {"name": display_text(key), "count": value}
            for key, value in session_counts.most_common()
        ],
        "tracks": [
            {"name": display_text(key), "count": value}
            for key, value in track_counts.most_common()
        ],
        "tagDistribution": [
            {"name": key, "count": value}
            for key, value in tag_counts.most_common(12)
        ],
        "abstracts": abstract_index,
        "prioritySignals": priority_signals[:80],
        "audienceWorkspaces": [
            {
                "name": role,
                "count": role_total_counts.get(role, len(role_payloads[role])),
                "sampleCount": len(role_payloads[role]),
                "countLabel": "matching abstracts",
                "description": ROLE_DESCRIPTIONS[role],
                "topSignals": role_payloads[role][:6],
            }
            for role in ROLE_KEYWORDS
        ],
        "workflow": PIPELINE_STEPS,
        "sources": [
            {
                "name": "ASCO 2026 abstract corpus",
                "type": "Conference abstracts",
                "url": manifest.get("source_page"),
                "status": "7,295 record-level ASCO links retained in the abstract index",
            },
        ],
    }

    write_json(OUT / "dashboard_data.json", dashboard_data)
    write_dashboard_js(OUT / "dashboard_data.js", dashboard_data)
    write_json(OUT / "priority_signals.json", priority_signals)
    write_json(
        OUT / "source_log.json",
        {
            "createdAtUtc": dashboard_data["generatedAtUtc"],
            "rawSources": dashboard_data["sources"],
            "rawFiles": [
                {"path": str(RAW_JSONL), "sha256": sha256(RAW_JSONL)},
                {"path": str(RAW_INDEX), "sha256": sha256(RAW_INDEX)},
                {"path": str(RAW_MANIFEST), "sha256": sha256(RAW_MANIFEST)},
            ],
        },
    )
    write_json(
        OUT / "qa_summary.json",
        {
            "records": len(normalized),
            "uniqueUids": len({x["uid"] for x in normalized}),
            "withBodyText": sum(1 for x in normalized if x["plainTextLength"] > 0),
            "withTables": sum(1 for x in normalized if x["tableCount"] > 0),
            "withSummary": sum(1 for x in normalized if x["hasSummary"]),
            "prioritySignals": len(priority_signals),
            "roleOutputFiles": len(list(ROLE_OUT.glob("*.json"))) + len(list(ROLE_OUT.glob("*.csv"))),
        },
    )

    print(f"Built {len(normalized)} normalized records")
    print(f"Wrote {OUT / 'dashboard_data.json'}")
    print(f"Wrote {len(priority_signals)} priority signals")


if __name__ == "__main__":
    main()
