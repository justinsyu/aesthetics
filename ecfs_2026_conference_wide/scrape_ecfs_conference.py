#!/usr/bin/env python3
"""Scrape the ECFS 2026 programme conference-wide from Documedias APIs.

The ECFS programme is a Vue app backed by Documedias JSON APIs. This scraper
replays the same public APIs used by the app instead of scraping rendered DOM.
It preserves a redacted raw snapshot while normalizing sessions, presentation
assignments, people, and abstract text for analysis.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
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
DAYS_API = f"{API_BASE}/program/days"
DAY_SESSIONS_API = f"{API_BASE}/program/days/{{day_id}}"
SESSION_API = f"{API_BASE}/program/sessions/{{session_id}}"
PRESENTATION_API = f"{API_BASE}/program/presentations/{{presentation_id}}"
ABSTRACT_HTML_API = (
    "https://ecfs2026.abstract.documedias.systems/api/v1/manager/abstract/"
    "multi/html/id/{abstract_ids}/template/program_preview"
)
PROGRAMME_URL = "https://ecfs2026.abstractserver.com/programme/"
SESSION_URL = PROGRAMME_URL + "#/details/sessions/{session_id}"
PRESENTATION_URL = PROGRAMME_URL + "#/details/presentations/{presentation_id}"

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
    "membership_number",
    "confirmation_link",
    "itinerary_link",
    "responsibilities_link",
}


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


def request_json(url: str, *, retries: int = 3, sleep_seconds: float = 0.5) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 ECFS conference scraper for local research archive",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as error:  # pragma: no cover - network contingency
            last_error = error
            if attempt == retries:
                break
            time.sleep(sleep_seconds * attempt)
    raise RuntimeError(f"Request failed after {retries} attempts: {url}") from last_error


def first_item(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        return payload[0] if payload else {}
    if isinstance(payload, dict) and isinstance(payload.get("value"), list):
        return payload["value"][0] if payload["value"] else {}
    if isinstance(payload, dict):
        return payload
    raise TypeError(f"Unexpected API payload: {type(payload)!r}")


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    if isinstance(value, dict):
        return {
            key: "[redacted]" if key in SENSITIVE_KEYS and item is not None else redact_sensitive(item)
            for key, item in value.items()
        }
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
    label_pattern = re.compile(
        r"\b(Methods\s+and\s+results|Objectives?|Methods?|Results|Conclusions?)\s*:\s*",
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
        else:
            key = "results"
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body_text)
        sections[key] = body_text[start:end].strip()
        if key == "methods_and_results":
            sections["methods"] = sections["methods"] or sections[key]
            sections["results"] = sections["results"] or sections[key]

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
    country = person.get("country")
    return {
        "id": person.get("id"),
        "first_name": person.get("first_name"),
        "last_name": person.get("last_name"),
        "title": person.get("title"),
        "institution": person.get("institution"),
        "department": person.get("department"),
        "city": person.get("city"),
        "state": person.get("state"),
        "country_code": person.get("country_code"),
        "country": country.get("name") if isinstance(country, dict) else None,
    }


def compact_session(session: dict[str, Any]) -> dict[str, Any]:
    day = session.get("day") or {}
    return {
        "id": session.get("id"),
        "code": session.get("code"),
        "title": html_to_text(session.get("title")),
        "date": day.get("date"),
        "day_id": session.get("day_id"),
        "start_time": session.get("start_time"),
        "end_time": session.get("end_time"),
        "duration_minutes": session.get("duration"),
        "display_type_id": session.get("display_type_id"),
        "session_group": (session.get("session_group") or {}).get("name"),
        "session_type": (session.get("session_type") or {}).get("name"),
        "room": (session.get("room") or {}).get("name"),
        "session_url": SESSION_URL.format(session_id=session.get("id")),
    }


def extract_session_people(session: dict[str, Any]) -> list[dict[str, Any]]:
    people = []
    for item in session.get("session_participations") or []:
        people.append(
            {
                "role": ((item.get("session_person") or {}).get("role") or {}).get("name"),
                "person": compact_person(item.get("person") or {}),
            }
        )
    return people


def normalize_record(
    assignment: dict[str, Any],
    session: dict[str, Any],
    abstract_lookup: dict[str, str],
    presentation_detail: dict[str, Any] | None,
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
    session_summary = compact_session(session)

    return {
        "assignment_id": assignment.get("id"),
        "session_id": assignment.get("session_id"),
        "session_code": session_summary["code"],
        "session_title": session_summary["title"],
        "session_date": session_summary["date"],
        "session_start_time": session_summary["start_time"],
        "session_end_time": session_summary["end_time"],
        "session_group": session_summary["session_group"],
        "session_type": session_summary["session_type"],
        "room": session_summary["room"],
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
        "presenters": presenters,
        "authors_text": parsed.get("authors_text", ""),
        "affiliations_text": parsed.get("affiliations_text", ""),
        "abstract_text": parsed.get("abstract_text", ""),
        "objectives": parsed.get("objectives", ""),
        "methods": parsed.get("methods", ""),
        "results": parsed.get("results", ""),
        "methods_and_results": parsed.get("methods_and_results", ""),
        "conclusion": parsed.get("conclusion", ""),
        "session_url": session_summary["session_url"],
        "presentation_url": PRESENTATION_URL.format(presentation_id=presentation.get("id")),
        "presentation_api_url": PRESENTATION_API.format(presentation_id=presentation.get("id")),
        "raw_abstract_html": parsed.get("raw_html", ""),
        "raw_assignment_redacted": redact_sensitive(assignment),
        "raw_presentation_detail_redacted": redact_sensitive(presentation_detail or {}),
    }


def chunk_abstract_ids(abstract_ids: list[str], max_url_chars: int = 7600) -> list[list[str]]:
    chunks: list[list[str]] = []
    current: list[str] = []
    for abstract_id in abstract_ids:
        proposed = current + [abstract_id]
        url = ABSTRACT_HTML_API.format(abstract_ids=",".join(proposed))
        if current and len(url) > max_url_chars:
            chunks.append(current)
            current = [abstract_id]
        else:
            current = proposed
    if current:
        chunks.append(current)
    return chunks


def fetch_abstract_html(abstract_ids: list[str]) -> tuple[dict[str, str], list[str]]:
    lookup: dict[str, str] = {}
    urls: list[str] = []
    for chunk in chunk_abstract_ids(abstract_ids):
        url = ABSTRACT_HTML_API.format(abstract_ids=",".join(chunk))
        urls.append(url)
        payload = request_json(url)
        if isinstance(payload, dict):
            lookup.update({str(key): value for key, value in payload.items()})
    return lookup, urls


def discover_sessions() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    days = request_json(DAYS_API)
    if not isinstance(days, list):
        raise TypeError("Expected /program/days to return a list")

    sessions_by_id: dict[int, dict[str, Any]] = {}
    day_session_urls: list[str] = []
    for day in days:
        day_id = day["id"]
        url = DAY_SESSIONS_API.format(day_id=day_id)
        day_session_urls.append(url)
        day_sessions = request_json(url)
        if not isinstance(day_sessions, list):
            raise TypeError(f"Expected day sessions to return a list: {url}")
        for session in day_sessions:
            sessions_by_id[session["id"]] = session
    return days, list(sessions_by_id.values()), day_session_urls


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scrape_conference(fetch_presentation_details: bool = True) -> dict[str, Any]:
    days, session_stubs, day_session_urls = discover_sessions()
    sessions: list[dict[str, Any]] = []
    presentation_ids: list[int] = []
    abstract_ids: list[str] = []

    for session_stub in sorted(session_stubs, key=lambda item: (item.get("day_id") or 0, item.get("start_time") or "", item.get("id") or 0)):
        session = first_item(request_json(SESSION_API.format(session_id=session_stub["id"])))
        sessions.append(session)
        for assignment in session.get("presentations") or []:
            presentation = assignment.get("presentation") or {}
            if presentation.get("id"):
                presentation_ids.append(int(presentation["id"]))
            if presentation.get("abstract_id"):
                abstract_ids.append(str(presentation["abstract_id"]))

    unique_abstract_ids = sorted(set(abstract_ids), key=lambda value: int(value) if value.isdigit() else value)
    abstract_lookup, abstract_urls = fetch_abstract_html(unique_abstract_ids)

    presentation_details: dict[int, dict[str, Any]] = {}
    if fetch_presentation_details:
        for presentation_id in sorted(set(presentation_ids)):
            presentation_details[presentation_id] = first_item(
                request_json(PRESENTATION_API.format(presentation_id=presentation_id))
            )

    normalized_sessions = []
    records = []
    for session in sessions:
        assignments = session.get("presentations") or []
        normalized_sessions.append(
            {
                **compact_session(session),
                "chairs_leaders_speakers": extract_session_people(session),
                "presentation_assignment_count": len(assignments),
                "raw_session_redacted": redact_sensitive(session),
            }
        )
        for assignment in assignments:
            presentation_id = (assignment.get("presentation") or {}).get("id")
            records.append(
                normalize_record(
                    assignment,
                    session,
                    abstract_lookup,
                    presentation_details.get(int(presentation_id)) if presentation_id else None,
                )
            )

    parse_status_counts: dict[str, int] = {}
    session_type_counts: dict[str, int] = {}
    for record in records:
        parse_status = record["parse_status"]
        parse_status_counts[parse_status] = parse_status_counts.get(parse_status, 0) + 1
    for session in normalized_sessions:
        session_type = session.get("session_type") or "Unknown"
        session_type_counts[session_type] = session_type_counts.get(session_type, 0) + 1

    return {
        "metadata": {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "source_programme_url": PROGRAMME_URL,
            "endpoint_strategy": [
                "GET /api/program/days to discover conference days.",
                "GET /api/program/days/{day_id} to enumerate day-level sessions.",
                "GET /api/program/sessions/{session_id} for full session detail and presentation assignments.",
                "GET /api/program/presentations/{presentation_id} for presentation detail snapshots.",
                "GET abstract multi/html/id/{abstract_ids}/template/program_preview in URL-length-bounded batches for abstract HTML.",
            ],
            "day_api_url": DAYS_API,
            "day_session_api_urls": day_session_urls,
            "session_api_url_template": SESSION_API,
            "presentation_api_url_template": PRESENTATION_API,
            "abstract_html_api_url_template": ABSTRACT_HTML_API,
            "abstract_html_api_urls_requested": abstract_urls,
            "day_count": len(days),
            "session_count": len(normalized_sessions),
            "sessions_with_presentations": sum(1 for session in normalized_sessions if session["presentation_assignment_count"]),
            "presentation_assignment_count": len(records),
            "unique_presentation_count": len(set(presentation_ids)),
            "unique_abstract_id_count": len(unique_abstract_ids),
            "abstract_html_returned_count": len(abstract_lookup),
            "parse_status_counts": parse_status_counts,
            "session_type_counts": session_type_counts,
            "redaction_note": "Contact and direct personal locator fields exposed by the programme API were redacted from raw API snapshots.",
            "caveats": [
                "The public programme API has no collection endpoint for all sessions or all presentations; the conference-wide crawl enumerates days first, then fetches each session and presentation detail by ID.",
                "Some programme presentations do not have abstract IDs or returned abstract HTML, especially non-abstract agenda items.",
                "Abstract section parsing is heuristic because the abstract endpoint returns rendered HTML snippets rather than structured objective/method/result fields.",
            ],
        },
        "days": days,
        "sessions": normalized_sessions,
        "records": records,
    }


def write_csv(records: list[dict[str, Any]], path: Path) -> None:
    fields = [
        "assignment_id",
        "session_id",
        "session_code",
        "session_title",
        "session_date",
        "session_start_time",
        "session_end_time",
        "session_group",
        "session_type",
        "room",
        "presentation_id",
        "abstract_id",
        "code",
        "title",
        "start_time",
        "end_time",
        "duration_minutes",
        "parse_status",
        "authors_text",
        "affiliations_text",
        "abstract_text",
        "objectives",
        "methods",
        "results",
        "conclusion",
        "session_url",
        "presentation_url",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path(__file__).with_name("ecfs_2026_conference_presentations.json"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path(__file__).with_name("ecfs_2026_conference_presentations.csv"),
    )
    parser.add_argument(
        "--skip-presentation-details",
        action="store_true",
        help="Skip per-presentation detail calls; session detail still includes assignment-level presentation data.",
    )
    args = parser.parse_args()

    output = scrape_conference(fetch_presentation_details=not args.skip_presentation_details)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(output["records"], args.output_csv)

    manifest = {
        "scraped_at": output["metadata"]["scraped_at"],
        "json_output": str(args.output_json),
        "json_sha256": file_sha256(args.output_json),
        "csv_output": str(args.output_csv),
        "csv_sha256": file_sha256(args.output_csv),
        "record_count": output["metadata"]["presentation_assignment_count"],
        "session_count": output["metadata"]["session_count"],
        "unique_abstract_id_count": output["metadata"]["unique_abstract_id_count"],
        "parse_status_counts": output["metadata"]["parse_status_counts"],
    }
    manifest_path = args.output_json.with_name("run_manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({**manifest, "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
