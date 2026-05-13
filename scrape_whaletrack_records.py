#!/usr/bin/env python3
import argparse
import csv
import html
import json
import math
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests


BASE_URL = "https://whaletrack.hwdt.org"
ALL_RECORDS_URL = f"{BASE_URL}/all-records/"
GRAPHQL_URL = "https://api.coreo.io/graphql"
PROJECT_ID = 22
SURVEY_IDS = [20, 21, 1799]
DETAIL_TYPE_BY_SURVEY_ID = {
    20: "excursion-sighting-details",
    21: "sighting-details",
    1799: "watch-sighting-details",
}
SPECIES_LABELS = {
    "PW": "Long-finned pilot whale",
    "BD": "Bottlenose dolphin",
    "CB": "Cuvier's beaked whale",
    "CD": "Short-beaked common dolphin",
    "FW": "Fin whale",
    "HP": "Harbour porpoise",
    "HU": "Humpback whale",
    "KW": "Killer whale",
    "MW": "Minke whale",
    "NB": "Northern bottlenose whale",
    "OR": "Other",
    "BS": "Basking shark",
    "RD": "Risso's dolphin",
    "SD": "Striped dolphin",
    "SP": "Sperm whale",
    "SU": "Sunfish",
    "SW": "Sei whale",
    "UB": "Unidentified whale",
    "UC": "Unidentified cetacean",
    "UD": "Unidentified dolphin",
    "UN": "Unknown",
    "WB": "White-beaked dolphin",
    "WS": "Atlantic white-sided dolphin",
    "BW": "Blue Whale",
    "SB": "Sowerby's beaked whale",
}
DISPLAY_TZ = ZoneInfo("Europe/London")
COREO_TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
    "eyJrZXkiOiIzNjliY2U2ZTFmMTU1ZDgxNGRhM2I3OGE0MDI5OTNiOCIsImlhdCI6MTUwMTg1OTU5NCwiaXNzIjoiY29yZW8ifQ."
    "Y4nh5IA3bSaGCm8T6sq2lKWJYuhnVQJsOfpCSTKGzII"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; whaletrack-record-export/1.0)",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
}

LISTING_ROW_RE = re.compile(
    r"<td>(.*?)</td>\s*"
    r"<td>(.*?)</td>\s*"
    r"<td>(.*?)</td>\s*"
    r"<td>(.*?)</td>\s*"
    r"<td>(.*?)</td>\s*"
    r'<td><a class="button" href="\.\./([^"?]+)\?id=(\d+)">View\s*</a></td>',
    re.IGNORECASE | re.DOTALL,
)
RESULT_COUNT_RE = re.compile(r"of\s+([\d,]+)\s+results", re.IGNORECASE)


def clean_cell(value):
    value = re.sub(r"<[^>]*>", " ", value)
    value = html.unescape(value)
    return " ".join(value.split())


def request_with_retries(method, url, *, attempts=5, timeout=45, **kwargs):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.request(method, url, timeout=timeout, headers=HEADERS, **kwargs)
            if response.status_code in {429, 500, 502, 503, 504}:
                raise requests.HTTPError(f"HTTP {response.status_code}", response=response)
            response.raise_for_status()
            return response
        except Exception as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(min(30, 1.6 ** attempt))
    raise RuntimeError(f"Failed {method} {url}: {last_error}") from last_error


def fetch_listing_page(page):
    start = (page - 1) * 10
    data = {
        "page": str(page),
        "start": str(start),
        "species": "%",
        "datefrom": "1000-01-01",
        "dateuntil": "3000-01-01",
        "next": ">",
    }
    if page == 1:
        response = request_with_retries("GET", ALL_RECORDS_URL)
    else:
        response = request_with_retries("POST", ALL_RECORDS_URL, data=data)

    rows = []
    for match in LISTING_ROW_RE.finditer(response.text):
        species, date, record_time, total, username, detail_type, record_id = match.groups()
        detail_url = f"{BASE_URL}/{detail_type}?id={record_id}"
        rows.append(
            {
                "list_position": start + len(rows) + 1,
                "record_id": int(record_id),
                "detail_type": detail_type,
                "detail_url": detail_url,
                "listing_species": clean_cell(species),
                "listing_date": clean_cell(date),
                "listing_time": clean_cell(record_time),
                "listing_total": clean_cell(total),
                "listing_username": clean_cell(username),
            }
        )

    total_results = None
    count_match = RESULT_COUNT_RE.search(response.text)
    if count_match:
        total_results = int(count_match.group(1).replace(",", ""))

    return page, rows, total_results


def enumerate_listing_records(workers):
    first_page, first_rows, total_results = fetch_listing_page(1)
    if first_page != 1 or total_results is None:
        raise RuntimeError("Could not read the first All records page count")

    total_pages = math.ceil(total_results / 10)
    records_by_position = {row["list_position"]: row for row in first_rows}
    print(f"Listing reports {total_results} records across {total_pages} pages", flush=True)

    completed = 1
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_listing_page, page): page for page in range(2, total_pages + 1)}
        for future in as_completed(futures):
            page, rows, _ = future.result()
            if not rows and page != total_pages:
                raise RuntimeError(f"Listing page {page} returned no rows")
            for row in rows:
                records_by_position[row["list_position"]] = row
            completed += 1
            if completed % 250 == 0 or completed == total_pages:
                print(f"Fetched listing pages: {completed}/{total_pages}", flush=True)

    records = [records_by_position[pos] for pos in sorted(records_by_position)]
    if len(records) != total_results:
        raise RuntimeError(f"Expected {total_results} listing rows, parsed {len(records)}")

    seen = set()
    duplicates = []
    for row in records:
        record_id = row["record_id"]
        if record_id in seen:
            duplicates.append(record_id)
        seen.add(record_id)
    if duplicates:
        print(f"Warning: found {len(duplicates)} duplicate record IDs in listing", file=sys.stderr, flush=True)

    return records


def chunks(items, size):
    for index in range(0, len(items), size):
        yield items[index : index + size]


def survey_ids_literal():
    return "[" + ",".join(str(survey_id) for survey_id in SURVEY_IDS) + "]"


def api_all_records_where():
    return (
        "{projectId:%d, surveyId:%s, data:{deleted_at:null, timestamp:{ne:null}}}"
        % (PROJECT_ID, survey_ids_literal())
    )


def graphql_record_fields():
    return (
        "id parentId state lat lng verificationState anonymous createdAt updatedAt syncedAt deletedAt "
        "projectId userId surveyId data title description "
        "survey { id name } "
        "user { id username displayName }"
    )


def graphql_records_page_query(limit, offset):
    return (
        '{ records(limit:%d, offset:%d, order:"reverse:data.timestamp", where:%s) { %s } }'
        % (limit, offset, api_all_records_where(), graphql_record_fields())
    )


def fetch_api_count():
    query = '{ count: recordsAggregate(function:"count", where:%s) }' % api_all_records_where()
    response = request_with_retries(
        "POST",
        GRAPHQL_URL,
        params={"auth_token": COREO_TOKEN},
        json={"query": query},
        timeout=45,
    )
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], ensure_ascii=False))
    return int(payload["data"]["count"])


def fetch_api_records_page(limit, offset):
    response = request_with_retries(
        "POST",
        GRAPHQL_URL,
        params={"auth_token": COREO_TOKEN},
        json={"query": graphql_records_page_query(limit, offset)},
        timeout=90,
    )
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], ensure_ascii=False))
    return offset, payload["data"]["records"]


def display_datetime_parts(timestamp):
    if not timestamp:
        return "", ""
    normalized = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized).astimezone(DISPLAY_TZ)
    except ValueError:
        return "", ""
    return parsed.strftime("%d-%m-%Y"), parsed.strftime("%H:%M")


def listing_row_from_api_record(record, position):
    data = record.get("data") or {}
    record_id = int(record["id"])
    survey_id = record.get("surveyId")
    detail_type = DETAIL_TYPE_BY_SURVEY_ID.get(survey_id, "sighting-details")
    listing_date, listing_time = display_datetime_parts(data.get("timestamp"))
    species_code = data.get("species")
    return {
        "list_position": position,
        "record_id": record_id,
        "detail_type": detail_type,
        "detail_url": f"{BASE_URL}/{detail_type}?id={record_id}",
        "listing_species": SPECIES_LABELS.get(species_code, scalar_for_csv(species_code)),
        "listing_date": listing_date,
        "listing_time": listing_time,
        "listing_total": scalar_for_csv(data.get("count_total")),
        "listing_username": scalar_for_csv((record.get("user") or {}).get("username")),
    }


def enumerate_api_records(limit, workers):
    total_results = fetch_api_count()
    offsets = list(range(0, total_results, limit))
    records_by_offset = {}
    print(
        f"Coreo API reports {total_results} All records rows "
        f"(deleted_at = null and timestamp != null)",
        flush=True,
    )

    completed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_api_records_page, limit, offset): offset for offset in offsets}
        for future in as_completed(futures):
            offset, records = future.result()
            records_by_offset[offset] = records
            completed += 1
            if completed % 20 == 0 or completed == len(offsets):
                print(f"Fetched API pages: {completed}/{len(offsets)}", flush=True)

    ordered_details = []
    for offset in sorted(records_by_offset):
        ordered_details.extend(records_by_offset[offset])
    if len(ordered_details) != total_results:
        raise RuntimeError(f"Expected {total_results} API records, received {len(ordered_details)}")

    details = {int(record["id"]): record for record in ordered_details}
    listing_records = [
        listing_row_from_api_record(record, index + 1) for index, record in enumerate(ordered_details)
    ]
    return listing_records, details


def graphql_records_query(ids):
    id_list = ",".join(str(record_id) for record_id in ids)
    return "{ records(where:{projectId:%d, id:[%s]}) { %s } }" % (
        PROJECT_ID,
        id_list,
        graphql_record_fields(),
    )


def fetch_record_batch(ids):
    query = graphql_records_query(ids)
    response = request_with_retries(
        "POST",
        GRAPHQL_URL,
        params={"auth_token": COREO_TOKEN},
        json={"query": query},
        timeout=90,
    )
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], ensure_ascii=False))
    return payload["data"]["records"]


def fetch_record_details(record_ids, batch_size, workers):
    details = {}
    batches = list(chunks(record_ids, batch_size))
    print(f"Fetching Coreo detail data in {len(batches)} batches", flush=True)

    completed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_record_batch, batch): batch for batch in batches}
        for future in as_completed(futures):
            batch = futures[future]
            records = future.result()
            for record in records:
                details[int(record["id"])] = record
            completed += 1
            if completed % 20 == 0 or completed == len(batches):
                print(f"Fetched detail batches: {completed}/{len(batches)}", flush=True)

            returned_ids = {int(record["id"]) for record in records}
            missing = set(batch) - returned_ids
            if missing:
                print(f"Warning: detail API omitted {len(missing)} IDs in a batch", file=sys.stderr, flush=True)

    return details


def scalar_for_csv(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def is_media_key(key):
    lowered = key.lower()
    return (
        lowered.startswith("media")
        or "image" in lowered
        or "photo" in lowered
        or lowered.endswith("_url")
        or lowered.endswith("url")
    )


def write_csv(listing_records, details, output_path):
    base_fields = [
        "list_position",
        "record_id",
        "detail_type",
        "detail_url",
        "listing_species",
        "listing_date",
        "listing_time",
        "listing_total",
        "listing_username",
        "api_found",
        "latitude",
        "longitude",
        "verification_state",
        "state",
        "parent_id",
        "project_id",
        "survey_id",
        "survey_name",
        "user_id",
        "username",
        "display_name",
        "anonymous",
        "created_at",
        "updated_at",
        "synced_at",
        "deleted_at",
        "title",
        "description",
        "excluded_media_field_count",
        "excluded_media_fields",
    ]

    data_keys = set()
    for record in details.values():
        data = record.get("data") or {}
        if isinstance(data, dict):
            data_keys.update(key for key in data if not is_media_key(key))

    data_fields = [f"data_{key}" for key in sorted(data_keys)]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=base_fields + data_fields, extrasaction="ignore")
        writer.writeheader()

        for listing in listing_records:
            record_id = listing["record_id"]
            detail = details.get(record_id) or {}
            data = detail.get("data") or {}
            survey = detail.get("survey") or {}
            user = detail.get("user") or {}
            media_fields = sorted(key for key in data if is_media_key(key)) if isinstance(data, dict) else []

            row = dict(listing)
            row.update(
                {
                    "api_found": "true" if detail else "false",
                    "latitude": scalar_for_csv(detail.get("lat")),
                    "longitude": scalar_for_csv(detail.get("lng")),
                    "verification_state": scalar_for_csv(detail.get("verificationState")),
                    "state": scalar_for_csv(detail.get("state")),
                    "parent_id": scalar_for_csv(detail.get("parentId")),
                    "project_id": scalar_for_csv(detail.get("projectId")),
                    "survey_id": scalar_for_csv(detail.get("surveyId")),
                    "survey_name": scalar_for_csv(survey.get("name")),
                    "user_id": scalar_for_csv(user.get("id")),
                    "username": scalar_for_csv(user.get("username")),
                    "display_name": scalar_for_csv(user.get("displayName")),
                    "anonymous": scalar_for_csv(detail.get("anonymous")),
                    "created_at": scalar_for_csv(detail.get("createdAt")),
                    "updated_at": scalar_for_csv(detail.get("updatedAt")),
                    "synced_at": scalar_for_csv(detail.get("syncedAt")),
                    "deleted_at": scalar_for_csv(detail.get("deletedAt")),
                    "title": scalar_for_csv(detail.get("title")),
                    "description": scalar_for_csv(detail.get("description")),
                    "excluded_media_field_count": len(media_fields),
                    "excluded_media_fields": ";".join(media_fields),
                }
            )

            if isinstance(data, dict):
                for key in data_keys:
                    row[f"data_{key}"] = scalar_for_csv(data.get(key))

            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Export public Whale Track All records data to CSV.")
    parser.add_argument("--output", default="whaletrack_all_records.csv", help="CSV output path")
    parser.add_argument("--listing-workers", type=int, default=16, help="Concurrent All records page requests")
    parser.add_argument("--detail-workers", type=int, default=6, help="Concurrent Coreo GraphQL batch requests")
    parser.add_argument("--batch-size", type=int, default=250, help="Record IDs per Coreo GraphQL request")
    parser.add_argument(
        "--index-source",
        choices=["api", "listing"],
        default="api",
        help="Use the exact public API filter or enumerate the HTML listing pages first",
    )
    args = parser.parse_args()

    if args.index_source == "listing":
        listing_records = enumerate_listing_records(max(1, args.listing_workers))
        record_ids = [row["record_id"] for row in listing_records]
        details = fetch_record_details(record_ids, max(1, args.batch_size), max(1, args.detail_workers))
    else:
        listing_records, details = enumerate_api_records(
            max(1, args.batch_size),
            max(1, args.detail_workers),
        )
        record_ids = [row["record_id"] for row in listing_records]

    missing = [record_id for record_id in record_ids if record_id not in details]
    if missing:
        print(f"Warning: {len(missing)} listing records have no Coreo detail payload", file=sys.stderr, flush=True)

    output_path = Path(args.output).resolve()
    write_csv(listing_records, details, output_path)
    print(f"Wrote {len(listing_records)} rows to {output_path}", flush=True)


if __name__ == "__main__":
    main()
