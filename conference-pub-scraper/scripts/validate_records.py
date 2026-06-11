#!/usr/bin/env python
"""Validate conference publication JSON exports and optionally write Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALID_PARSE_STATUSES = {
    "complete",
    "partial",
    "pdf_text_only",
    "ocr_partial",
    "metadata_only",
    "failed",
}


def load_records(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("records", "presentations", "items", "abstracts"):
            if isinstance(data.get(key), list):
                records = data[key]
                break
        else:
            raise SystemExit("Could not find a records list. Expected a list or one of: records, presentations, items, abstracts.")
    else:
        raise SystemExit("JSON root must be an object or list.")
    if not all(isinstance(item, dict) for item in records):
        raise SystemExit("Every record must be a JSON object.")
    return records


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(text(item) for item in value if text(item))
    if isinstance(value, dict):
        return "; ".join(f"{key}: {text(val)}" for key, val in value.items() if text(val))
    return str(value).strip()


def record_id(record: dict[str, Any], index: int) -> str:
    for key in ("uid", "id", "presentation_id", "abstract_id", "poster_id", "display_code", "code"):
        value = text(record.get(key))
        if value:
            return value
    return f"row-{index + 1}"


def source_count(record: dict[str, Any]) -> int:
    sources = record.get("source_urls", record.get("source_url", record.get("presentation_url")))
    if isinstance(sources, str):
        return 1 if sources.strip() else 0
    if isinstance(sources, list):
        return sum(1 for item in sources if text(item))
    if isinstance(sources, dict):
        return sum(1 for item in sources.values() if text(item))
    count = 0
    for key in ("presentation_url", "session_url", "pdf_url", "image_url", "api_endpoint"):
        if text(record.get(key)):
            count += 1
    if text(record.get("source_page")):
        count += 1
    return count


def has_sections(record: dict[str, Any]) -> bool:
    sections = record.get("sections", record.get("abstract_sections"))
    return isinstance(sections, dict) and any(text(value) for value in sections.values())


def abstract_text(record: dict[str, Any]) -> str:
    for key in ("abstract_text", "summary", "abstract", "description"):
        value = text(record.get(key))
        if value:
            return value
    sections = record.get("sections", record.get("abstract_sections"))
    return text(sections)


def build_report(records: list[dict[str, Any]], expected_count: int | None) -> dict[str, Any]:
    ids = [record_id(record, index) for index, record in enumerate(records)]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    missing_title = [ids[index] for index, record in enumerate(records) if not text(record.get("title"))]
    missing_sources = [ids[index] for index, record in enumerate(records) if source_count(record) == 0]
    missing_abstract = [ids[index] for index, record in enumerate(records) if not abstract_text(record)]
    missing_abstract_strict = [
        ids[index]
        for index, record in enumerate(records)
        if not abstract_text(record) and text(record.get("parse_status")) not in {"metadata_only", "failed"}
    ]
    invalid_parse_status = [
        ids[index]
        for index, record in enumerate(records)
        if text(record.get("parse_status")) not in VALID_PARSE_STATUSES
    ]
    structured = sum(1 for record in records if has_sections(record))
    status_counts: dict[str, int] = {}
    for record in records:
        status = text(record.get("parse_status")) or "unspecified"
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "record_count": len(records),
        "expected_count": expected_count,
        "matches_expected_count": expected_count is None or len(records) == expected_count,
        "unique_id_count": len(set(ids)),
        "duplicate_ids": duplicate_ids[:50],
        "records_with_sources": len(records) - len(missing_sources),
        "records_with_structured_sections": structured,
        "records_missing_title": missing_title[:50],
        "records_missing_sources": missing_sources[:50],
        "records_missing_abstract_text": missing_abstract[:50],
        "records_missing_abstract_text_strict": missing_abstract_strict[:50],
        "records_with_invalid_parse_status": invalid_parse_status[:50],
        "parse_status_counts": dict(sorted(status_counts.items())),
    }


def strict_failures(report: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not report["matches_expected_count"]:
        failures.append("record count did not match --expected-count")
    if report["duplicate_ids"]:
        failures.append("duplicate record IDs found")
    if report["records_missing_title"]:
        failures.append("records missing title")
    if report["records_missing_sources"]:
        failures.append("records missing source evidence")
    if report["records_with_invalid_parse_status"]:
        failures.append("records missing or using invalid parse_status")
    if report["records_missing_abstract_text_strict"]:
        failures.append("records missing abstract text without metadata_only/failed parse_status")
    return failures


def write_markdown(records: list[dict[str, Any]], path: Path) -> None:
    lines: list[str] = ["# Conference Records", ""]
    for index, record in enumerate(records):
        rid = record_id(record, index)
        title = text(record.get("title")) or "Untitled record"
        lines.extend([f"## {index + 1}. {title}", "", f"- ID: {rid}"])
        for label, key in (
            ("Type", "record_type"),
            ("Presenter", "presenter"),
            ("Session", "session_title"),
            ("Track", "track"),
            ("Date", "date"),
            ("Time", "time"),
        ):
            value = text(record.get(key))
            if value:
                lines.append(f"- {label}: {value}")
        sources = text(record.get("source_urls") or record.get("source_url") or record.get("presentation_url"))
        if sources:
            lines.append(f"- Sources: {sources}")
        lines.append("")
        sections = record.get("sections", record.get("abstract_sections"))
        if isinstance(sections, dict) and sections:
            for section, value in sections.items():
                if text(value):
                    lines.extend([f"### {section}", "", text(value), ""])
        elif abstract_text(record):
            lines.extend([abstract_text(record), ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", type=Path)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--strict", action="store_true", help="Fail on missing titles, sources, invalid parse_status, and unexpected missing abstracts.")
    args = parser.parse_args()

    records = load_records(args.json_path)
    report = build_report(records, args.expected_count)
    report_text = json.dumps(report, indent=2, ensure_ascii=False)
    print(report_text)
    if args.report_out:
        args.report_out.write_text(report_text + "\n", encoding="utf-8")
    if args.markdown_out:
        write_markdown(records, args.markdown_out)

    failures = strict_failures(report) if args.strict else []
    if failures:
        print("Strict validation failed: " + "; ".join(failures), file=sys.stderr)
        return 1
    if not args.strict and (not report["matches_expected_count"] or report["duplicate_ids"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
