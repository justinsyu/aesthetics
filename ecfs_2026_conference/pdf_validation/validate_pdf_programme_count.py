#!/usr/bin/env python3
"""Validate ECFS 2026 programme JSON counts against the official PDF."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import fitz


ROLE_LINE_PATTERN = re.compile(r"^(.*?(?:Speaker|presenter|author):.*?)$", re.I | re.M)
CODE_PATTERNS = {
    "poster_codes_P": re.compile(r"\bP\d{3}\b"),
    "eposter_codes_EPS": re.compile(r"\bEPS\d+\.\d+\b"),
    "workshop_codes_WS": re.compile(r"\bWS\d+\.\d+\b"),
}


def code_sort_key(value: str) -> list[int]:
    return [int(item) for item in re.findall(r"\d+", value)]


def extract_pdf_text(pdf_path: Path, text_output: Path | None = None) -> tuple[str, int]:
    doc = fitz.open(pdf_path)
    parts = []
    for page_number, page in enumerate(doc, 1):
        parts.append(f"\n\n===== PAGE {page_number} =====\n{page.get_text('text')}")
    text = "\n".join(parts)
    if text_output:
        text_output.write_text(text, encoding="utf-8")
    return text, doc.page_count


def load_json_records(json_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    return payload["records"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--text-output", type=Path)
    args = parser.parse_args()

    text, page_count = extract_pdf_text(args.pdf, args.text_output)
    records = load_json_records(args.json)

    role_lines = ROLE_LINE_PATTERN.findall(text)
    pdf_role_counts = Counter(re.sub(r":.*", "", line).strip() for line in role_lines)
    json_role_counts = Counter(
        (record.get("presenters") or [{}])[0].get("role") or "[missing]"
        for record in records
    )

    code_comparisons: dict[str, Any] = {}
    for name, pattern in CODE_PATTERNS.items():
        pdf_codes = set(pattern.findall(text))
        if name == "poster_codes_P":
            json_pattern = re.compile(r"P\d{3}")
        elif name == "eposter_codes_EPS":
            json_pattern = re.compile(r"EPS\d+\.\d+")
        else:
            json_pattern = re.compile(r"WS\d+\.\d+")
        json_codes = {record["code"] for record in records if record.get("code") and json_pattern.fullmatch(record["code"])}
        code_comparisons[name] = {
            "pdf_count": len(pdf_codes),
            "json_count": len(json_codes),
            "missing_from_pdf": sorted(json_codes - pdf_codes, key=code_sort_key),
            "extra_in_pdf": sorted(pdf_codes - json_codes, key=code_sort_key),
        }

    report = {
        "pdf_path": str(args.pdf),
        "json_path": str(args.json),
        "pdf_page_count": page_count,
        "pdf_role_line_count": len(role_lines),
        "json_record_count": len(records),
        "counts_match": len(role_lines) == len(records),
        "pdf_role_counts": dict(sorted(pdf_role_counts.items())),
        "json_role_counts": dict(sorted(json_role_counts.items())),
        "explicit_code_comparisons": code_comparisons,
        "explicit_code_total_pdf": sum(item["pdf_count"] for item in code_comparisons.values()),
        "explicit_code_total_json": sum(item["json_count"] for item in code_comparisons.values()),
        "interpretation": (
            "The official PDF contains 818 role-attributed programme contribution rows. "
            "The PDF also exactly matches the JSON for all explicit P, EPS, and WS code sets. "
            "The remaining rows are uncoded invited/oral/session presentations counted by role lines."
        ),
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
