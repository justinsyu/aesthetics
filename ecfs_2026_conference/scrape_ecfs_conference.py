#!/usr/bin/env python3
"""Scrape ECFS 2026 conference programme presentations and abstracts.

The programme is a Vue app backed by Documedias JSON APIs. This collector uses
the conference day index, expands every listed session, and batch-fetches the
abstract HTML used on presentation detail pages.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


API_BASE = "https://ecfs2026.planner.documedias.systems/api"
ABSTRACT_API_BASE = "https://ecfs2026.abstract.documedias.systems/api/v1/manager/abstract"
PROGRAMME_URL = "https://ecfs2026.abstractserver.com/programme/"
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
            "User-Agent": "Mozilla/5.0 ECFS 2026 conference scraper",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def first_item(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        return payload[0]
    if isinstance(payload, dict) and isinstance(payload.get("value"), list):
        return payload["value"][0]
    raise TypeError(f"Unexpected API payload: {type(payload)!r}")


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
        "background": "",
        "objectives": "",
        "methods": "",
        "results": "",
        "methods_and_results": "",
        "conclusion": "",
    }
    label_pattern = re.compile(
        r"\b(Background|Methods\s+and\s+results|Objectives?|Methods?|Results|Conclusions?)\s*:\s*",
        re.I,
    )
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
        elif label.startswith("background"):
            key = "background"
        else:
            key = label
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body_text)
        value = body_text[start:end].strip()
        sections[key] = value
        if key == "methods_and_results":
            sections["methods"] = sections["methods"] or value
            sections["results"] = sections["results"] or value

    required = ("objectives", "methods", "results", "conclusion")
    missing_sections = [key for key in required if not sections[key]]

    return {
        "authors_text": authors,
        "affiliations_text": affiliations,
        "abstract_text": body_text,
        "background": sections["background"],
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


def get_days() -> list[dict[str, Any]]:
    return request_json(f"{API_BASE}/program/days")


def get_options() -> dict[str, Any]:
    return request_json(f"{API_BASE}/program/options")


def get_day_sessions(day_id: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "program_mode": "list",
            "program_sort": "date",
            "filter_display_type": "1,3",
            "filter_group": "is_not_child",
        }
    )
    return request_json(f"{API_BASE}/program/days/{day_id}?{params}")


def get_session_detail(session_id: int) -> dict[str, Any]:
    return first_item(request_json(f"{API_BASE}/program/sessions/{session_id}"))


def fetch_abstract_html(abstract_ids: list[int], batch_size: int = 80) -> tuple[dict[str, str], list[dict[str, Any]]]:
    lookup: dict[str, str] = {}
    batches: list[dict[str, Any]] = []
    unique_ids = list(dict.fromkeys(str(item) for item in abstract_ids if item))
    for start in range(0, len(unique_ids), batch_size):
        batch = unique_ids[start : start + batch_size]
        url = f"{ABSTRACT_API_BASE}/multi/html/id/{','.join(batch)}/template/program_preview"
        payload = request_json(url)
        lookup.update({str(key): value for key, value in payload.items()})
        batches.append({"url": url, "requested_count": len(batch), "returned_count": len(payload)})
    return lookup, batches


def build_maps(options: dict[str, Any]) -> dict[str, dict[int, str]]:
    maps: dict[str, dict[int, str]] = {}
    for key in ("session_group", "session_type", "room"):
        values = options.get(key) or []
        maps[key] = {item.get("id"): item.get("name") for item in values if item.get("id") is not None}
    return maps


def normalize_record(
    session: dict[str, Any],
    assignment: dict[str, Any],
    abstract_lookup: dict[str, str],
    maps: dict[str, dict[int, str]],
) -> dict[str, Any]:
    presentation = assignment.get("presentation") or {}
    abstract_id = presentation.get("abstract_id")
    raw_abstract_html = abstract_lookup.get(str(abstract_id), "") if abstract_id else ""
    parsed = parse_abstract_html(raw_abstract_html) if raw_abstract_html else {}
    participations = assignment.get("presentation_participations") or []
    presenters = [
        {
            "role": ((item.get("presentation_person") or {}).get("role") or {}).get("name"),
            "person": compact_person(item.get("person") or {}),
        }
        for item in participations
    ]

    missing_default = ["objectives", "methods", "results", "conclusion"]
    parse_status = parsed.get("parse_status")
    if not parse_status:
        parse_status = "missing_abstract_id" if not abstract_id else "missing_abstract_html"

    return {
        "assignment_id": assignment.get("id"),
        "presentation_id": presentation.get("id"),
        "abstract_id": abstract_id,
        "code": assignment.get("code") or presentation.get("code"),
        "title": html_to_text(presentation.get("title")),
        "session": {
            "id": session.get("id"),
            "code": session.get("code"),
            "title": html_to_text(session.get("title")),
            "date": (session.get("day") or {}).get("date"),
            "start_time": session.get("start_time"),
            "end_time": session.get("end_time"),
            "session_group_id": session.get("session_group_id"),
            "session_group": maps["session_group"].get(session.get("session_group_id")),
            "session_type_id": session.get("session_type_id"),
            "session_type": maps["session_type"].get(session.get("session_type_id")),
            "room_id": session.get("room_id"),
            "room": (session.get("room") or {}).get("name") or maps["room"].get(session.get("room_id")),
            "url": SESSION_URL.format(session_id=session.get("id")),
        },
        "start_time": assignment.get("start_time"),
        "end_time": assignment.get("end_time"),
        "duration_minutes": assignment.get("duration"),
        "including_discussion_minutes": assignment.get("including"),
        "display_type_id": presentation.get("display_type_id"),
        "format_id": presentation.get("format_id"),
        "abstract_type_id": presentation.get("abstract_type_id"),
        "abstract_status_id": presentation.get("abstract_status_id"),
        "abstract_theme_id": presentation.get("abstract_theme_id"),
        "score_avg": presentation.get("score_avg"),
        "score_range": presentation.get("score_range"),
        "parse_status": parse_status,
        "missing_sections": parsed.get("missing_sections", missing_default),
        "presenters": presenters,
        "authors_text": parsed.get("authors_text", ""),
        "affiliations_text": parsed.get("affiliations_text", ""),
        "abstract_text": parsed.get("abstract_text", ""),
        "background": parsed.get("background", ""),
        "objectives": parsed.get("objectives", ""),
        "methods": parsed.get("methods", ""),
        "results": parsed.get("results", ""),
        "methods_and_results": parsed.get("methods_and_results", ""),
        "conclusion": parsed.get("conclusion", ""),
        "presentation_url": PRESENTATION_URL.format(presentation_id=presentation.get("id")),
        "raw_abstract_html": parsed.get("raw_html", ""),
        "raw_assignment_redacted": redact_sensitive(assignment),
    }


def scrape_conference(delay_seconds: float = 0.0) -> dict[str, Any]:
    days = get_days()
    options = get_options()
    maps = build_maps(options)
    indexed_sessions: list[dict[str, Any]] = []
    session_details: list[dict[str, Any]] = []
    session_errors: list[dict[str, Any]] = []

    for day in days:
        sessions = get_day_sessions(day["id"])
        indexed_sessions.extend(sessions)
        for session_summary in sessions:
            session_id = session_summary["id"]
            try:
                session_details.append(get_session_detail(session_id))
            except Exception as exc:  # noqa: BLE001 - keep scrape manifest complete.
                session_errors.append({"session_id": session_id, "error": repr(exc)})
            if delay_seconds:
                time.sleep(delay_seconds)

    records_seed: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for session in session_details:
        for assignment in session.get("presentations") or []:
            if (assignment.get("presentation") or {}).get("id"):
                records_seed.append((session, assignment))

    abstract_ids = [
        (assignment.get("presentation") or {}).get("abstract_id")
        for _, assignment in records_seed
        if (assignment.get("presentation") or {}).get("abstract_id")
    ]
    abstract_lookup, abstract_batches = fetch_abstract_html(abstract_ids)

    records = [
        normalize_record(session, assignment, abstract_lookup, maps)
        for session, assignment in records_seed
    ]
    records.sort(
        key=lambda item: (
            item["session"].get("date") or "",
            item.get("start_time") or "",
            item["session"].get("code") or "",
            item.get("code") or "",
            item.get("presentation_id") or 0,
        )
    )

    parse_status_counts: dict[str, int] = {}
    session_type_counts: dict[str, int] = {}
    for record in records:
        parse_status_counts[record["parse_status"]] = parse_status_counts.get(record["parse_status"], 0) + 1
        session_type = record["session"].get("session_type") or "Unspecified"
        session_type_counts[session_type] = session_type_counts.get(session_type, 0) + 1

    unique_presentation_ids = sorted({record["presentation_id"] for record in records if record["presentation_id"]})
    unique_abstract_ids = sorted({record["abstract_id"] for record in records if record["abstract_id"]})

    return {
        "metadata": {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "source_programme_url": PROGRAMME_URL,
            "coverage_basis": "All sessions returned by /program/days/{day_id} with list-mode display filters, then expanded through /program/sessions/{session_id}.",
            "days_endpoint": f"{API_BASE}/program/days",
            "day_sessions_endpoint_template": f"{API_BASE}/program/days/{{day_id}}?program_mode=list&program_sort=date&filter_display_type=1,3&filter_group=is_not_child",
            "session_detail_endpoint_template": f"{API_BASE}/program/sessions/{{session_id}}",
            "abstract_html_endpoint_template": f"{ABSTRACT_API_BASE}/multi/html/id/{{abstract_ids}}/template/program_preview",
            "day_count": len(days),
            "indexed_session_count": len(indexed_sessions),
            "expanded_session_count": len(session_details),
            "sessions_with_presentations_count": len([s for s in session_details if s.get("presentations")]),
            "session_error_count": len(session_errors),
            "record_count": len(records),
            "unique_presentation_count": len(unique_presentation_ids),
            "unique_abstract_count": len(unique_abstract_ids),
            "parse_status_counts": parse_status_counts,
            "session_type_record_counts": dict(sorted(session_type_counts.items())),
            "abstract_batch_count": len(abstract_batches),
            "abstract_batches": abstract_batches,
            "session_errors": session_errors,
            "redaction_note": "Contact and direct personal locator fields exposed by the programme API were redacted from raw API snapshots.",
        },
        "days": days,
        "sessions": [
            {
                "id": session.get("id"),
                "code": session.get("code"),
                "title": html_to_text(session.get("title")),
                "date": (session.get("day") or {}).get("date"),
                "start_time": session.get("start_time"),
                "end_time": session.get("end_time"),
                "session_group": maps["session_group"].get(session.get("session_group_id")),
                "session_type": maps["session_type"].get(session.get("session_type_id")),
                "room": (session.get("room") or {}).get("name") or maps["room"].get(session.get("room_id")),
                "presentation_count": len(session.get("presentations") or []),
                "url": SESSION_URL.format(session_id=session.get("id")),
            }
            for session in session_details
        ],
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("ecfs_2026_conference_presentations.json"),
    )
    parser.add_argument("--delay-seconds", type=float, default=0.0)
    args = parser.parse_args()

    output = scrape_conference(delay_seconds=args.delay_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "record_count": output["metadata"]["record_count"],
                "unique_abstract_count": output["metadata"]["unique_abstract_count"],
                "parse_status_counts": output["metadata"]["parse_status_counts"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
