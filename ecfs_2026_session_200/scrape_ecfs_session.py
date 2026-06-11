#!/usr/bin/env python3
"""Scrape all presentations from one ECFS 2026 programme session.

The ECFS programme is a Vue app backed by Documedias JSON APIs. This script
uses those APIs directly instead of scraping rendered DOM.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SESSION_API = "https://ecfs2026.planner.documedias.systems/api/program/sessions/{session_id}"
PRESENTATION_API = "https://ecfs2026.planner.documedias.systems/api/program/presentations/{presentation_id}"
ABSTRACT_HTML_API = (
    "https://ecfs2026.abstract.documedias.systems/api/v1/manager/abstract/"
    "multi/html/id/{abstract_ids}/template/program_preview"
)
SESSION_URL = "https://ecfs2026.abstractserver.com/programme/#/details/sessions/{session_id}"
PRESENTATION_URL = "https://ecfs2026.abstractserver.com/programme/#/details/presentations/{presentation_id}"
SENSITIVE_KEYS = {
    "email",
    "email_alternative",
    "phone",
    "alt_phone",
    "cellphone",
    "fax",
    "street",
    "zip_code",
    "participant_number",
    "external_id",
    "confirmation_link",
    "itinerary_link",
    "responsibilities_link",
}
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"br", "div", "p", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"div", "p", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        value = "".join(self.parts)
        value = re.sub(r"[ \t\r\f\v]+", " ", value)
        value = re.sub(r" *\n+ *", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()


def html_to_text(value: Any) -> str:
    if value is None:
        return ""
    parser = TextExtractor()
    parser.feed(str(value))
    return html.unescape(parser.text())


def request_json(url: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 ECFS session scraper for local research archive",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def first_item(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        return payload[0]
    if isinstance(payload, dict) and isinstance(payload.get("value"), list):
        return payload["value"][0]
    raise TypeError(f"Unexpected session API payload: {type(payload)!r}")


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    if isinstance(value, dict):
        return {
            key: "[redacted]" if key in SENSITIVE_KEYS and item is not None else redact_sensitive(item)
            for key, item in value.items()
        }
    if isinstance(value, str):
        return EMAIL_PATTERN.sub("[redacted-email]", value)
    return value


def parse_abstract_html(raw_html: str) -> dict[str, Any]:
    text = html_to_text(raw_html)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    authors = lines[0] if lines else ""
    affiliations = lines[1] if len(lines) > 1 else ""
    body_text = "\n\n".join(lines[2:]).strip() if len(lines) > 2 else text

    sections: dict[str, str] = {
        "objectives": "",
        "methods": "",
        "results": "",
        "methods_and_results": "",
        "conclusion": "",
    }
    label_pattern = re.compile(r"\b(Methods\s+and\s+results|Objectives?|Methods?|Results|Conclusions?)\s*:\s*", re.I)
    matches = list(label_pattern.finditer(body_text))
    for index, match in enumerate(matches):
        label = match.group(1).lower()
        if label.startswith("methods and results"):
            key = "methods_and_results"
        elif label.startswith("objective"):
            key = "objectives"
        elif label.startswith("method"):
            key = "methods"
        elif label.startswith("conclusion"):
            key = "conclusion"
        else:
            key = label
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body_text)
        value = body_text[start:end].strip()
        sections[key] = value
        if key == "methods_and_results":
            sections["methods"] = sections["methods"] or value
            sections["results"] = sections["results"] or value

    missing_sections = [key for key in ("objectives", "methods", "results", "conclusion") if not sections[key]]

    return {
        "authors_text": authors,
        "affiliations_text": affiliations,
        "abstract_text": body_text,
        "objectives": sections["objectives"],
        "methods": sections["methods"],
        "results": sections["results"],
        "methods_and_results": sections["methods_and_results"],
        "conclusion": sections["conclusion"],
        "parse_status": "parsed" if not missing_sections else "partial",
        "missing_sections": missing_sections,
        "raw_html": raw_html,
    }


def compact_person(person: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": person.get("id"),
        "first_name": person.get("first_name"),
        "last_name": person.get("last_name"),
        "title": person.get("title"),
        "institution": person.get("institution"),
        "department": person.get("department"),
        "city": person.get("city"),
        "country_code": person.get("country_code"),
        "country": (person.get("country") or {}).get("name") if isinstance(person.get("country"), dict) else None,
    }


def normalize_record(
    assignment: dict[str, Any],
    abstract_lookup: dict[str, str],
    presentation_detail: dict[str, Any] | None,
) -> dict[str, Any]:
    presentation = assignment.get("presentation") or {}
    abstract_id = presentation.get("abstract_id")
    raw_abstract_html = abstract_lookup.get(str(abstract_id), "") if abstract_id else ""
    parsed = parse_abstract_html(raw_abstract_html) if raw_abstract_html else {}

    participations = assignment.get("presentation_participations") or []
    people = [
        {
            "role": ((item.get("presentation_person") or {}).get("role") or {}).get("name"),
            "person": compact_person(item.get("person") or {}),
        }
        for item in participations
    ]

    return {
        "assignment_id": assignment.get("id"),
        "session_id": assignment.get("session_id"),
        "presentation_id": presentation.get("id"),
        "abstract_id": abstract_id,
        "code": assignment.get("code") or presentation.get("code"),
        "title": html_to_text(presentation.get("title")),
        "start_time": assignment.get("start_time"),
        "end_time": assignment.get("end_time"),
        "duration_minutes": assignment.get("duration"),
        "including_discussion_minutes": assignment.get("including"),
        "display_type_id": presentation.get("display_type_id"),
        "format_id": presentation.get("format_id"),
        "score_avg": presentation.get("score_avg"),
        "score_range": presentation.get("score_range"),
        "parse_status": parsed.get("parse_status", "missing_abstract_html"),
        "missing_sections": parsed.get("missing_sections", ["objectives", "methods", "results", "conclusion"]),
        "presenters": people,
        "authors_text": parsed.get("authors_text", ""),
        "affiliations_text": parsed.get("affiliations_text", ""),
        "abstract_text": parsed.get("abstract_text", ""),
        "objectives": parsed.get("objectives", ""),
        "methods": parsed.get("methods", ""),
        "results": parsed.get("results", ""),
        "methods_and_results": parsed.get("methods_and_results", ""),
        "conclusion": parsed.get("conclusion", ""),
        "presentation_url": PRESENTATION_URL.format(presentation_id=presentation.get("id")),
        "presentation_api_url": PRESENTATION_API.format(presentation_id=presentation.get("id")),
        "raw_abstract_html": parsed.get("raw_html", ""),
        "raw_assignment_redacted": redact_sensitive(assignment),
        "raw_presentation_detail_redacted": redact_sensitive(presentation_detail or {}),
    }


def scrape_session(session_id: int) -> dict[str, Any]:
    session_payload = request_json(SESSION_API.format(session_id=session_id))
    session = first_item(session_payload)
    assignments = session.get("presentations") or []
    abstract_ids = [
        str((assignment.get("presentation") or {}).get("abstract_id"))
        for assignment in assignments
        if (assignment.get("presentation") or {}).get("abstract_id")
    ]
    abstract_lookup = request_json(ABSTRACT_HTML_API.format(abstract_ids=",".join(abstract_ids))) if abstract_ids else {}
    presentation_details: dict[int, dict[str, Any]] = {}
    for assignment in assignments:
        presentation_id = (assignment.get("presentation") or {}).get("id")
        if presentation_id:
            presentation_details[presentation_id] = first_item(
                request_json(PRESENTATION_API.format(presentation_id=presentation_id))
            )

    records = [
        normalize_record(
            assignment,
            abstract_lookup,
            presentation_details.get((assignment.get("presentation") or {}).get("id")),
        )
        for assignment in assignments
    ]
    parse_status_counts: dict[str, int] = {}
    for record in records:
        status = record["parse_status"]
        parse_status_counts[status] = parse_status_counts.get(status, 0) + 1

    return {
        "metadata": {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "source_session_url": SESSION_URL.format(session_id=session_id),
            "session_api_url": SESSION_API.format(session_id=session_id),
            "abstract_html_api_url": ABSTRACT_HTML_API.format(abstract_ids=",".join(abstract_ids)),
            "record_count": len(records),
            "abstract_ids_requested": abstract_ids,
            "parse_status_counts": parse_status_counts,
            "redaction_note": "Contact and direct personal locator fields exposed by the programme API were redacted from raw API snapshots.",
        },
        "session": {
            "id": session.get("id"),
            "code": session.get("code"),
            "title": html_to_text(session.get("title")),
            "date": (session.get("day") or {}).get("date"),
            "start_time": session.get("start_time"),
            "end_time": session.get("end_time"),
            "duration_minutes": session.get("duration"),
            "session_group": (session.get("session_group") or {}).get("name"),
            "session_type": (session.get("session_type") or {}).get("name"),
            "room": (session.get("room") or {}).get("name"),
            "raw_session_redacted": redact_sensitive(session),
        },
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", type=int, default=200)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("session_200_presentations.json"))
    args = parser.parse_args()

    output = scrape_session(args.session_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "record_count": output["metadata"]["record_count"]}, indent=2))


if __name__ == "__main__":
    main()
