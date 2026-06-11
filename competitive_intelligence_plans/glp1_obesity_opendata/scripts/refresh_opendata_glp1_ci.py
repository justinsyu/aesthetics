#!/usr/bin/env python3
"""Refresh deterministic OpenData GLP-1 obesity CI artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
OUT = ROOT / "generated_data"
SOURCES_CONFIG = CONFIG_DIR / "opendata_sources.json"
PRODUCT_CONFIG = CONFIG_DIR / "glp1_product_dictionary.json"
METHODOLOGY = ROOT / "METHODOLOGY.md"
USER_AGENT = "linkedin-posts-mac-glp1-opendata-ci/2026-05-28"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def script_manifest_entries() -> dict[str, dict[str, Any]]:
    script_paths = [
        ROOT / "scripts" / "refresh_opendata_glp1_ci.py",
        ROOT / "scripts" / "build_slide_deck.py",
        ROOT / "scripts" / "verify_refreshed_outputs.py",
    ]
    return {
        path.stem: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
        }
        for path in script_paths
        if path.exists()
    }


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False))
            handle.write("\n")


def normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def get_url(url: str, source_log: list[dict[str, Any]], purpose: str, timeout: int = 45) -> bytes | None:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json,text/csv,text/plain,*/*",
            "User-Agent": USER_AGENT,
        },
    )
    started = utc_now()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            status = getattr(response, "status", None)
            content_type = response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        source_log.append(
            {
                "purpose": purpose,
                "url": url,
                "retrieved_at": started,
                "status": "error",
                "http_status": exc.code,
                "error": str(exc),
                "response_sha256": sha256_bytes(body),
            }
        )
        return None
    except Exception as exc:  # noqa: BLE001 - source log needs concrete network failure.
        source_log.append(
            {
                "purpose": purpose,
                "url": url,
                "retrieved_at": started,
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        return None

    source_log.append(
        {
            "purpose": purpose,
            "url": url,
            "retrieved_at": started,
            "status": "ok",
            "http_status": status,
            "content_type": content_type,
            "bytes": len(body),
            "response_sha256": sha256_bytes(body),
        }
    )
    return body


def get_json(url: str, source_log: list[dict[str, Any]], purpose: str) -> Any | None:
    body = get_url(url, source_log, purpose)
    if body is None:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        source_log.append(
            {
                "purpose": f"{purpose}:json_decode",
                "url": url,
                "retrieved_at": utc_now(),
                "status": "error",
                "error": "Response was not valid JSON.",
                "response_sha256": sha256_bytes(body),
            }
        )
        return None


def dataset_url(api_base: str, dataset_id: str, suffix: str = "") -> str:
    provider, slug = dataset_id.split("/", 1)
    return f"{api_base}/datasets/{provider}/{slug}{suffix}"


def build_match_terms(product_config: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, dict[str, Any]]]:
    terms: list[dict[str, str]] = []
    product_lookup: dict[str, dict[str, Any]] = {}
    for product in product_config["products"]:
        canonical = product["canonical_product"]
        product_lookup[canonical] = product
        for field, term_type in [
            ("brand_terms", "brand"),
            ("ingredient_terms", "ingredient"),
            ("manufacturer_terms", "manufacturer"),
        ]:
            for term in product.get(field, []):
                terms.append(
                    {
                        "canonical_product": canonical,
                        "term": term,
                        "normalized_term": normalize_text(term),
                        "term_type": term_type,
                    }
                )
    terms.sort(key=lambda item: (item["term_type"], item["normalized_term"], item["canonical_product"]))
    return terms, product_lookup


def match_row(row: dict[str, Any], terms: list[dict[str, str]]) -> list[dict[str, str]]:
    text_fields = {
        key: normalize_text(value)
        for key, value in row.items()
        if value is not None and not isinstance(value, (dict, list))
    }
    matches: list[dict[str, str]] = []
    for term in terms:
        normalized = term["normalized_term"]
        if not normalized:
            continue
        for field, value in text_fields.items():
            if normalized in value:
                matches.append({**term, "match_field": field, "match_value": row.get(field)})
                break

    has_product_match = any(match["term_type"] in {"brand", "ingredient"} for match in matches)
    if not has_product_match:
        return []
    brand_matches = [match for match in matches if match["term_type"] == "brand"]
    if brand_matches:
        brand_products = {match["canonical_product"] for match in brand_matches}
        return [match for match in matches if match["canonical_product"] in brand_products]

    ingredient_matches = [match for match in matches if match["term_type"] == "ingredient"]
    by_term: dict[str, list[dict[str, str]]] = {}
    for match in ingredient_matches:
        by_term.setdefault(match["normalized_term"], []).append(match)

    resolved: list[dict[str, str]] = []
    for normalized_term, term_matches in by_term.items():
        products = sorted({match["canonical_product"] for match in term_matches})
        if len(products) == 1:
            resolved.extend(term_matches)
            continue
        representative = sorted(term_matches, key=lambda item: (item["term"], item["match_field"]))[0]
        resolved.append(
            {
                **representative,
                "canonical_product": f"ingredient:{representative['term'].lower()}",
                "term_type": "ingredient_ambiguous",
                "normalized_term": normalized_term,
            }
        )
    return resolved


def clean_source_row(row: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in row.items():
        if key is None:
            continue
        clean_key = str(key)
        if not clean_key:
            continue
        cleaned[clean_key] = value
    return cleaned


def data_rows_from_api_response(data: Any) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    if not isinstance(data, dict):
        return [], [], []
    columns = data.get("columns") or []
    types = data.get("types") or []
    rows = data.get("rows") or data.get("data") or data.get("results") or []
    if rows and isinstance(rows[0], list) and columns:
        mapped = [dict(zip(columns, row, strict=False)) for row in rows]
    elif rows and isinstance(rows[0], dict):
        mapped = rows
        if not columns:
            columns = sorted({key for row in mapped for key in row.keys()})
    else:
        mapped = []
    return columns, types, mapped


def decode_csv_bytes(body: bytes) -> io.StringIO:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return io.StringIO(body.decode(encoding), newline="")
        except UnicodeDecodeError:
            continue
    return io.StringIO(body.decode("utf-8", errors="replace"), newline="")


def sniff_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t|")
    except csv.Error:
        class DefaultDialect(csv.excel):
            delimiter = ","

        return DefaultDialect


def iter_csv_rows(body: bytes) -> tuple[list[dict[str, Any]], int]:
    text = decode_csv_bytes(body)
    sample = text.read(4096)
    text.seek(0)
    dialect = sniff_dialect(sample)
    reader = csv.DictReader(text, dialect=dialect)
    rows = [dict(row) for row in reader]
    return rows, len(rows)


def iter_zip_source_rows(body: bytes) -> tuple[list[dict[str, Any]], int, list[str]]:
    rows: list[dict[str, Any]] = []
    members_scanned: list[str] = []
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        for name in sorted(archive.namelist()):
            lower = name.lower()
            if not lower.endswith((".csv", ".txt", ".json", ".xlsx")):
                continue
            members_scanned.append(name)
            member_body = archive.read(name)
            if lower.endswith(".xlsx"):
                member_rows, _, _ = iter_xlsx_source_rows(member_body)
                for row in member_rows:
                    row["_zip_member"] = name
                rows.extend(member_rows)
                continue
            if lower.endswith(".json"):
                try:
                    parsed = json.loads(member_body.decode("utf-8"))
                except Exception:
                    continue
                candidate_rows = parsed.get("results") if isinstance(parsed, dict) else parsed
                if isinstance(candidate_rows, list):
                    rows.extend([row for row in candidate_rows if isinstance(row, dict)])
                continue
            member_rows, _ = iter_csv_rows(member_body)
            for row in member_rows:
                row["_zip_member"] = name
            rows.extend(member_rows)
    return rows, len(rows), members_scanned


def column_index_from_cell_ref(cell_ref: str) -> int:
    letters = re.sub(r"[^A-Za-z]", "", cell_ref)
    index = 0
    for letter in letters.upper():
        index = index * 26 + (ord(letter) - ord("A") + 1)
    return max(index - 1, 0)


def xml_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def iter_xlsx_source_rows(body: bytes) -> tuple[list[dict[str, Any]], int, list[str]]:
    rows: list[dict[str, Any]] = []
    members_scanned: list[str] = []
    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        names = set(archive.namelist())
        if "xl/workbook.xml" not in names:
            return [], 0, []

        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in names:
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall("main:si", ns):
                shared_strings.append(xml_text(item))

        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_targets = {
            rel.attrib["Id"]: rel.attrib.get("Target", "")
            for rel in rels_root.findall("pkgrel:Relationship", ns)
            if rel.attrib.get("Id")
        }
        sheet_paths: list[tuple[str, str]] = []
        for sheet in workbook_root.findall("main:sheets/main:sheet", ns):
            rel_id = sheet.attrib.get(f"{{{ns['rel']}}}id")
            target = rel_targets.get(rel_id or "")
            if not target:
                continue
            path = target if target.startswith("xl/") else f"xl/{target.lstrip('/')}"
            sheet_paths.append((sheet.attrib.get("name", path), path))

        for sheet_name, path in sheet_paths:
            if path not in names:
                continue
            members_scanned.append(path)
            sheet_root = ET.fromstring(archive.read(path))
            parsed_rows: list[list[str]] = []
            for row_node in sheet_root.findall(".//main:sheetData/main:row", ns):
                values: list[str] = []
                for cell in row_node.findall("main:c", ns):
                    cell_ref = cell.attrib.get("r", "")
                    idx = column_index_from_cell_ref(cell_ref)
                    while len(values) <= idx:
                        values.append("")
                    cell_type = cell.attrib.get("t")
                    if cell_type == "inlineStr":
                        value = xml_text(cell.find("main:is", ns))
                    else:
                        raw_value = xml_text(cell.find("main:v", ns))
                        if cell_type == "s" and raw_value:
                            try:
                                value = shared_strings[int(raw_value)]
                            except (ValueError, IndexError):
                                value = raw_value
                        else:
                            value = raw_value
                    values[idx] = value
                if any(value != "" for value in values):
                    parsed_rows.append(values)
            if not parsed_rows:
                continue
            headers = [header.strip() or f"column_{index + 1}" for index, header in enumerate(parsed_rows[0])]
            for row_values in parsed_rows[1:]:
                row = {
                    headers[index]: row_values[index] if index < len(row_values) else ""
                    for index in range(len(headers))
                }
                row["_xlsx_sheet"] = sheet_name
                rows.append(row)

    return rows, len(rows), members_scanned


def source_rows_from_body(body: bytes, source_url: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lower = urllib.parse.urlparse(source_url).path.lower()
    if body[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            names = set(archive.namelist())
        if lower.endswith(".xlsx") or "xl/workbook.xml" in names:
            rows, count, members = iter_xlsx_source_rows(body)
            return rows, {"parser": "xlsx", "row_count": count, "members_scanned": members}
    if lower.endswith(".zip") or body[:2] == b"PK":
        rows, count, members = iter_zip_source_rows(body)
        return rows, {"parser": "zip", "row_count": count, "members_scanned": members}
    if lower.endswith(".json") or lower.endswith(".jsonl"):
        parsed = json.loads(body.decode("utf-8"))
        candidate_rows = parsed.get("results") if isinstance(parsed, dict) else parsed
        rows = [row for row in candidate_rows if isinstance(row, dict)] if isinstance(candidate_rows, list) else []
        return rows, {"parser": "json", "row_count": len(rows)}
    rows, count = iter_csv_rows(body)
    return rows, {"parser": "csv", "row_count": count}


def scan_source_for_matches(
    dataset_id: str,
    source_url: str,
    source_log: list[dict[str, Any]],
    terms: list[dict[str, str]],
    include_large: bool,
    large_source: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if large_source and not include_large:
        return [], {
            "dataset_id": dataset_id,
            "source_url": source_url,
            "status": "skipped_large_source",
            "reason": "Run with --include-large-source-downloads to scan this source.",
        }

    body = get_url(source_url, source_log, f"upstream_source:{dataset_id}", timeout=120)
    if body is None:
        return [], {"dataset_id": dataset_id, "source_url": source_url, "status": "source_fetch_failed"}

    try:
        rows, parse_meta = source_rows_from_body(body, source_url)
    except Exception as exc:  # noqa: BLE001 - capture parser failure in output.
        return [], {
            "dataset_id": dataset_id,
            "source_url": source_url,
            "status": "parse_failed",
            "error": f"{type(exc).__name__}: {exc}",
        }

    matches: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        row_matches = match_row(row, terms)
        cleaned_row = clean_source_row(row)
        for match in row_matches:
            matches.append(
                {
                    "dataset_id": dataset_id,
                    "source_url": source_url,
                    "source_row_number": index,
                    "canonical_product": match["canonical_product"],
                    "match_term": match["term"],
                    "match_term_type": match["term_type"],
                    "match_field": match["match_field"],
                    "match_value": match.get("match_value"),
                    "source_row": cleaned_row,
                }
            )

    return matches, {
        "dataset_id": dataset_id,
        "source_url": source_url,
        "status": "scanned",
        "rows_scanned": parse_meta.get("row_count"),
        "matches": len(matches),
        **parse_meta,
    }


def compact_match_for_csv(match: dict[str, Any]) -> dict[str, Any]:
    source_row = match.get("source_row", {})
    compact = {
        "dataset_id": match.get("dataset_id"),
        "canonical_product": match.get("canonical_product"),
        "match_term": match.get("match_term"),
        "match_term_type": match.get("match_term_type"),
        "match_field": match.get("match_field"),
        "match_value": match.get("match_value"),
        "source_row_number": match.get("source_row_number"),
        "source_url": match.get("source_url"),
        "source_response_sha256": match.get("source_response_sha256"),
        "source_updated_at": match.get("source_updated_at"),
        "match_rule_version": match.get("match_rule_version"),
        "source_record_id": match.get("source_record_id"),
    }
    for key, value in source_row.items():
        if key is None:
            continue
        key = str(key)
        normalized_key = re.sub(r"[^A-Za-z0-9]+", "_", key).strip("_").lower()
        if normalized_key and normalized_key not in compact:
            compact[normalized_key] = value
    return compact


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("$", "").replace(",", "").replace("%", "")
    try:
        return float(text)
    except ValueError:
        return None


def unique_source_rows_for_matches(matches: list[dict[str, Any]]) -> set[tuple[str, Any]]:
    return {
        (str(match.get("dataset_id")), match.get("source_row_number"))
        for match in matches
        if match.get("source_row_number") is not None
    }


def shortage_classification(row: dict[str, Any]) -> str:
    status = normalize_text(row.get("status"))
    availability = normalize_text(row.get("availability"))
    if status == "CURRENT" and availability == "LIMITED AVAILABILITY":
        return "current_limited_availability"
    if status == "CURRENT" and availability == "AVAILABLE":
        return "current_available"
    if status == "TO BE DISCONTINUED":
        return "to_be_discontinued"
    if status == "CURRENT":
        return "current_other"
    return normalize_text(row.get("status") or "unknown").lower().replace(" ", "_") or "unknown"


def build_product_signal_summary(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    row_records_by_group: dict[tuple[str, str], dict[Any, dict[str, Any]]] = {}
    metric_fields = {
        "total_spending": ["Total Spending ($)", "total_spending", "total spending ($)"],
        "total_claims": ["Total Claims", "total_claims"],
        "total_beneficiaries": ["Total Beneficiaries", "total_beneficiaries"],
        "total_dosage_units": ["Total Dosage Units", "total_dosage_units"],
        "avg_spending_per_claim": ["Avg Spending per Claim ($)", "avg_spending_per_claim"],
        "avg_spending_per_dosage_unit": ["Avg Spending per Dosage Unit ($)", "avg_spending_per_dosage_unit"],
    }
    for match in matches:
        key = (match["dataset_id"], match["canonical_product"])
        group = groups.setdefault(
            key,
            {
                "dataset_id": match["dataset_id"],
                "canonical_product": match["canonical_product"],
                "matched_source_rows": 0,
                "match_records": 0,
                "match_terms": set(),
                "source_url": match.get("source_url"),
                "sum_total_spending": 0.0,
                "sum_total_claims": 0.0,
                "sum_total_beneficiaries": 0.0,
                "sum_total_dosage_units": 0.0,
                "avg_spending_per_claim_values": [],
                "avg_spending_per_dosage_unit_values": [],
                "year_metrics": {},
            },
        )
        group["match_records"] += 1
        group["match_terms"].add(match["match_term"])
        row_key = (match["dataset_id"], match["canonical_product"], match.get("source_row_number"))
        row_records_by_group.setdefault(key, {})[row_key] = match.get("source_row", {})
    for key, group in groups.items():
        source_rows = list(row_records_by_group.get(key, {}).values())
        group["matched_source_rows"] = len(source_rows)
        group["_source_rows"] = source_rows
        has_overall_row = any(normalize_text(row.get("Mftr_Name") or row.get("Manufacturer")) == "OVERALL" for row in source_rows)
        numeric_rows = [
            row
            for row in source_rows
            if not has_overall_row or normalize_text(row.get("Mftr_Name") or row.get("Manufacturer")) == "OVERALL"
        ]
        group["numeric_rows_used"] = len(numeric_rows)
        group["numeric_row_rule"] = "overall_rows_only" if has_overall_row else "all_matched_rows"
        for row in numeric_rows:
            metric_values: dict[str, float | None] = {}
            for metric, aliases in metric_fields.items():
                metric_values[metric] = None
                for alias in aliases:
                    if alias in row:
                        metric_values[metric] = parse_number(row.get(alias))
                        break
            for metric, target in [
                ("total_spending", "sum_total_spending"),
                ("total_claims", "sum_total_claims"),
                ("total_beneficiaries", "sum_total_beneficiaries"),
                ("total_dosage_units", "sum_total_dosage_units"),
            ]:
                if metric_values[metric] is not None:
                    group[target] += metric_values[metric]
            for metric, target in [
                ("avg_spending_per_claim", "avg_spending_per_claim_values"),
                ("avg_spending_per_dosage_unit", "avg_spending_per_dosage_unit_values"),
            ]:
                if metric_values[metric] is not None:
                    group[target].append(metric_values[metric])
            year_metrics = group["year_metrics"]
            for field, value in row.items():
                field_text = str(field)
                metric_match = re.fullmatch(
                    r"(Tot_Spndng|Tot_Clms|Tot_Benes|Tot_Dsg_Unts|Avg_Spnd_Per_Clm|Avg_Spnd_Per_Dsg_Unt_Wghtd)_(\d{4})",
                    field_text,
                )
                if not metric_match:
                    continue
                parsed = parse_number(value)
                if parsed is None:
                    continue
                source_metric, year = metric_match.groups()
                year_record = year_metrics.setdefault(
                    year,
                    {
                        "total_spending": 0.0,
                        "total_claims": 0.0,
                        "total_beneficiaries": 0.0,
                        "total_dosage_units": 0.0,
                        "avg_spending_per_claim_values": [],
                        "avg_spending_per_dosage_unit_values": [],
                    },
                )
                if source_metric == "Tot_Spndng":
                    year_record["total_spending"] += parsed
                elif source_metric == "Tot_Clms":
                    year_record["total_claims"] += parsed
                elif source_metric == "Tot_Benes":
                    year_record["total_beneficiaries"] += parsed
                elif source_metric == "Tot_Dsg_Unts":
                    year_record["total_dosage_units"] += parsed
                elif source_metric == "Avg_Spnd_Per_Clm":
                    year_record["avg_spending_per_claim_values"].append(parsed)
                elif source_metric == "Avg_Spnd_Per_Dsg_Unt_Wghtd":
                    year_record["avg_spending_per_dosage_unit_values"].append(parsed)

    summary: list[dict[str, Any]] = []
    for group in groups.values():
        claim_values = group.pop("avg_spending_per_claim_values")
        unit_values = group.pop("avg_spending_per_dosage_unit_values")
        year_metrics = group.pop("year_metrics")
        source_rows = group.pop("_source_rows")
        group["match_terms"] = sorted(group["match_terms"])
        if group["dataset_id"] == "fda/drug-shortages":
            classifications: dict[str, int] = {}
            for row in source_rows:
                classification = shortage_classification(row)
                classifications[classification] = classifications.get(classification, 0) + 1
            group["shortage_classifications"] = classifications
            group["current_limited_availability_rows"] = classifications.get("current_limited_availability", 0)
            group["current_available_rows"] = classifications.get("current_available", 0)
            group["to_be_discontinued_rows"] = classifications.get("to_be_discontinued", 0)
        group["mean_avg_spending_per_claim"] = round(sum(claim_values) / len(claim_values), 4) if claim_values else None
        group["mean_avg_spending_per_dosage_unit"] = round(sum(unit_values) / len(unit_values), 4) if unit_values else None
        for field in ["sum_total_spending", "sum_total_claims", "sum_total_beneficiaries", "sum_total_dosage_units"]:
            group[field] = round(group[field], 4)
        years = sorted(year_metrics)
        group["years_observed"] = years
        group["cumulative_annual_spending"] = round(sum(year_metrics[year]["total_spending"] for year in years), 4)
        group["cumulative_annual_claims"] = round(sum(year_metrics[year]["total_claims"] for year in years), 4)
        group["cumulative_annual_beneficiaries"] = round(sum(year_metrics[year]["total_beneficiaries"] for year in years), 4)
        group["cumulative_annual_dosage_units"] = round(sum(year_metrics[year]["total_dosage_units"] for year in years), 4)
        if years:
            latest_year = years[-1]
            latest = year_metrics[latest_year]
            group["latest_year"] = int(latest_year)
            group["latest_year_total_spending"] = round(latest["total_spending"], 4)
            group["latest_year_total_claims"] = round(latest["total_claims"], 4)
            group["latest_year_total_beneficiaries"] = round(latest["total_beneficiaries"], 4)
            group["latest_year_total_dosage_units"] = round(latest["total_dosage_units"], 4)
            latest_claim_values = latest["avg_spending_per_claim_values"]
            latest_unit_values = latest["avg_spending_per_dosage_unit_values"]
            group["latest_year_mean_avg_spending_per_claim"] = round(sum(latest_claim_values) / len(latest_claim_values), 4) if latest_claim_values else None
            group["latest_year_mean_avg_spending_per_dosage_unit"] = round(sum(latest_unit_values) / len(latest_unit_values), 4) if latest_unit_values else None
            if len(years) > 1:
                prior_year = years[-2]
                prior = year_metrics[prior_year]
                group["prior_year"] = int(prior_year)
                group["prior_year_total_spending"] = round(prior["total_spending"], 4)
                group["prior_year_total_claims"] = round(prior["total_claims"], 4)
                group["latest_prior_period_relation"] = "strict_yoy" if int(latest_year) - int(prior_year) == 1 else "latest_vs_prior_observed"
                group["latest_prior_periods_consecutive"] = int(latest_year) - int(prior_year) == 1
                group["latest_vs_prior_spending_change"] = round(latest["total_spending"] - prior["total_spending"], 4)
                group["latest_vs_prior_claims_change"] = round(latest["total_claims"] - prior["total_claims"], 4)
                group["latest_vs_prior_spending_pct_change"] = round(((latest["total_spending"] - prior["total_spending"]) / prior["total_spending"]) * 100, 4) if prior["total_spending"] else None
                group["latest_vs_prior_claims_pct_change"] = round(((latest["total_claims"] - prior["total_claims"]) / prior["total_claims"]) * 100, 4) if prior["total_claims"] else None
            else:
                group["prior_year"] = None
                group["prior_year_total_spending"] = None
                group["prior_year_total_claims"] = None
                group["latest_prior_period_relation"] = None
                group["latest_prior_periods_consecutive"] = None
                group["latest_vs_prior_spending_change"] = None
                group["latest_vs_prior_claims_change"] = None
                group["latest_vs_prior_spending_pct_change"] = None
                group["latest_vs_prior_claims_pct_change"] = None
        else:
            group["latest_year"] = None
            group["latest_year_total_spending"] = None
            group["latest_year_total_claims"] = None
            group["latest_year_total_beneficiaries"] = None
            group["latest_year_total_dosage_units"] = None
            group["latest_year_mean_avg_spending_per_claim"] = None
            group["latest_year_mean_avg_spending_per_dosage_unit"] = None
            group["prior_year"] = None
            group["prior_year_total_spending"] = None
            group["prior_year_total_claims"] = None
            group["latest_prior_period_relation"] = None
            group["latest_prior_periods_consecutive"] = None
            group["latest_vs_prior_spending_change"] = None
            group["latest_vs_prior_claims_change"] = None
            group["latest_vs_prior_spending_pct_change"] = None
            group["latest_vs_prior_claims_pct_change"] = None
        summary.append(group)
    summary.sort(key=lambda row: (row["dataset_id"], row["canonical_product"]))
    return summary


def build_signal_specs() -> list[dict[str, Any]]:
    return [
        {
            "signal_id": "competitor_utilization_momentum",
            "description": "GLP-1 product uptake and spend over time by payer channel and geography when available.",
            "datasets": ["cms/sdud", "cms/part-d-spending", "cms/medicaid-spending"],
            "primary_measures": [
                "number_of_prescriptions",
                "total_claims",
                "total_beneficiaries",
                "units_reimbursed",
                "total_amount_reimbursed",
                "total_spending",
                "avg_spending_per_claim",
                "avg_spending_per_dosage_unit"
            ],
            "refresh_cadence": "monthly for SDUD metadata, quarterly for SDUD large scan, annually for spending-by-drug releases"
        },
        {
            "signal_id": "payer_reimbursement_pressure",
            "description": "Price, reimbursement, rebate, and IRA negotiation pressure around GLP-1 and adjacent metabolic drugs.",
            "datasets": ["cms/nadac", "cms/ful", "cms/drug-rebate-products", "cms/ira-drug-prices", "ca-hcai/wac-increases"],
            "primary_measures": ["nadac_per_unit", "federal_upper_limit", "rebate_category", "market_date", "wac_increase", "maximum_fair_price"],
            "refresh_cadence": "monthly to quarterly depending on source"
        },
        {
            "signal_id": "regulatory_product_lifecycle",
            "description": "Approved GLP-1 products, dosage forms, NDCs, application numbers, reference flags, shortages, recalls, and lifecycle changes.",
            "datasets": ["fda/drugs-at-fda", "fda/ndc-directory", "fda/orange-book", "fda/nme-approvals", "fda/drug-shortages", "fda/drug-recalls"],
            "primary_measures": ["application_number", "approval_date", "dosage_form", "route", "strength", "product_ndc", "marketing_status", "shortage_status", "recall_classification"],
            "refresh_cadence": "weekly for NDC/shortage/recall context, monthly for Orange Book"
        },
        {
            "signal_id": "market_opportunity_access_context",
            "description": "Population burden and coverage context for obesity GLP-1 launch and access planning.",
            "datasets": ["cdc/brfss", "owid/obesity", "census/health-insurance-coverage", "cms/medicaid-chip-enrollment"],
            "primary_measures": ["obesity_prevalence", "diabetes_prevalence", "uninsured_rate", "medicaid_enrollment"],
            "refresh_cadence": "annual to monthly depending on source"
        },
        {
            "signal_id": "insurer_behavior_access_context",
            "description": "Issuer denial behavior, appeals, marketplace footprint, premiums, cost-sharing, and insurer financial context.",
            "datasets": ["cms/transparency-in-coverage", "cms/marketplace-plans", "cms/mlr-data"],
            "primary_measures": ["claims_denied", "denial_rate", "appeals_overturned", "premium", "deductible", "issuer_mlr"],
            "refresh_cadence": "annual plan-year and CMS filing releases"
        }
    ]


def source_hash_lookup(source_log: list[dict[str, Any]]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for entry in source_log:
        if entry.get("status") == "ok" and entry.get("response_sha256"):
            lookup[str(entry.get("url"))] = str(entry["response_sha256"])
    return lookup


def infer_source_record_id(row: dict[str, Any]) -> str:
    candidates = [
        "Product NDC",
        "product_ndc",
        "NDC",
        "ndc",
        "Application Number",
        "Application No",
        "appl_no",
        "Application_Number",
        "Drug Name",
        "Drug_Name",
        "Brnd_Name",
        "Brand Name",
        "Trade Name",
        "Gnrc_Name",
        "Generic Name",
        "Mftr_Name",
        "Manufacturer",
        "State",
        "Year",
        "Quarter",
    ]
    parts = [f"{key}={row.get(key)}" for key in candidates if row.get(key) not in (None, "")]
    if parts:
        return "|".join(parts)
    return sha256_bytes(json.dumps(clean_source_row(row), sort_keys=True, ensure_ascii=False).encode("utf-8"))


def enrich_matches(
    matches: list[dict[str, Any]],
    source_log: list[dict[str, Any]],
    inventory: list[dict[str, Any]],
    product_dictionary_version: str,
) -> list[dict[str, Any]]:
    hashes = source_hash_lookup(source_log)
    metadata_by_id = {item["id"]: item.get("metadata") or {} for item in inventory}
    enriched: list[dict[str, Any]] = []
    for match in matches:
        source_url = match.get("source_url")
        row = match.get("source_row", {})
        enriched.append(
            {
                **match,
                "source_response_sha256": hashes.get(str(source_url)),
                "source_updated_at": metadata_by_id.get(match["dataset_id"], {}).get("updated_at"),
                "match_rule_version": product_dictionary_version,
                "source_record_id": infer_source_record_id(row),
            }
        )
    return enriched


def build_record_trace_map(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, match in enumerate(matches, start=1):
        records.append(
            {
                "trace_id": f"glp1-open-data-match-{index:06d}",
                "dataset_id": match.get("dataset_id"),
                "source_url": match.get("source_url"),
                "source_response_sha256": match.get("source_response_sha256"),
                "source_updated_at": match.get("source_updated_at"),
                "source_row_number": match.get("source_row_number"),
                "source_record_id": match.get("source_record_id"),
                "canonical_product": match.get("canonical_product"),
                "match_term": match.get("match_term"),
                "match_term_type": match.get("match_term_type"),
                "match_field": match.get("match_field"),
                "match_value": match.get("match_value"),
                "match_rule_version": match.get("match_rule_version"),
            }
        )
    return records


def build_source_coverage_matrix(
    sources: dict[str, Any],
    inventory: list[dict[str, Any]],
    source_scan_summaries: list[dict[str, Any]],
    matches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    inventory_by_id = {item["id"]: item for item in inventory}
    scan_by_id = {item["dataset_id"]: item for item in source_scan_summaries}
    rows: list[dict[str, Any]] = []
    for dataset in sorted(sources["datasets"], key=lambda item: item["id"]):
        dataset_id = dataset["id"]
        inv = inventory_by_id.get(dataset_id, {})
        scan = scan_by_id.get(dataset_id, {})
        dataset_matches = [match for match in matches if match["dataset_id"] == dataset_id]
        unique_rows = unique_source_rows_for_matches(dataset_matches)
        metadata = inv.get("metadata") or {}
        rows.append(
            {
                "dataset_id": dataset_id,
                "priority": dataset.get("priority"),
                "signal_families": ";".join(dataset.get("signal_families", [])),
                "refresh_default": dataset.get("refresh_default"),
                "large_source": dataset.get("large_source"),
                "metadata_status": inv.get("metadata_status"),
                "columns_status": inv.get("columns_status"),
                "source_url": metadata.get("source_url"),
                "source_updated_at": metadata.get("updated_at"),
                "catalog_rows": metadata.get("rows"),
                "source_scan_status": scan.get("status", "not_scanned"),
                "rows_scanned": scan.get("rows_scanned"),
                "lexical_match_records": scan.get("matches"),
                "unique_matched_source_rows": len(unique_rows) if dataset_matches else None,
                "parser": scan.get("parser"),
                "skip_or_error": scan.get("reason") or scan.get("error"),
            }
        )
    return rows


def build_unmatched_dictionary_terms(terms: list[dict[str, str]], matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matched = {(match.get("canonical_product"), normalize_text(match.get("match_term"))) for match in matches}
    rows: list[dict[str, Any]] = []
    for term in terms:
        key = (term["canonical_product"], term["normalized_term"])
        count = sum(1 for match in matches if (match.get("canonical_product"), normalize_text(match.get("match_term"))) == key)
        if key not in matched:
            rows.append(
                {
                    "canonical_product": term["canonical_product"],
                    "term": term["term"],
                    "term_type": term["term_type"],
                    "normalized_term": term["normalized_term"],
                    "match_count": count,
                    "review_note": "No exact canonical-product match in scanned sources; may still be present in skipped large sources or ingredient-ambiguous records.",
                }
            )
    rows.sort(key=lambda row: (row["canonical_product"], row["term_type"], row["term"]))
    return rows


def build_match_qc_sample(matches: list[dict[str, Any]], limit_per_dataset: int = 8) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for match in sorted(matches, key=lambda item: (item["dataset_id"], item["canonical_product"], item["source_row_number"], item["match_term"])):
        dataset_id = match["dataset_id"]
        if counts.get(dataset_id, 0) >= limit_per_dataset:
            continue
        counts[dataset_id] = counts.get(dataset_id, 0) + 1
        rows.append(
            {
                "dataset_id": dataset_id,
                "canonical_product": match.get("canonical_product"),
                "match_term": match.get("match_term"),
                "match_term_type": match.get("match_term_type"),
                "match_field": match.get("match_field"),
                "match_value": match.get("match_value"),
                "source_record_id": match.get("source_record_id"),
                "source_url": match.get("source_url"),
                "review_status": "pending_analyst_review",
                "false_positive_note": "",
            }
        )
    return rows


def build_signal_delta_summary(product_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in product_summary:
        if row.get("latest_year") is None or row.get("prior_year") is None:
            continue
        rows.append(
            {
                "dataset_id": row.get("dataset_id"),
                "canonical_product": row.get("canonical_product"),
                "latest_period": row.get("latest_year"),
                "prior_period": row.get("prior_year"),
                "latest_spending": row.get("latest_year_total_spending"),
                "prior_spending": row.get("prior_year_total_spending"),
                "spending_absolute_change": row.get("latest_vs_prior_spending_change"),
                "spending_percent_change": row.get("latest_vs_prior_spending_pct_change"),
                "latest_claims": row.get("latest_year_total_claims"),
                "prior_claims": row.get("prior_year_total_claims"),
                "claims_absolute_change": row.get("latest_vs_prior_claims_change"),
                "claims_percent_change": row.get("latest_vs_prior_claims_pct_change"),
                "period_relation": row.get("latest_prior_period_relation"),
                "periods_consecutive": row.get("latest_prior_periods_consecutive"),
                "direction": "spending_increase" if (row.get("latest_vs_prior_spending_change") or 0) > 0 else "spending_decrease_or_flat",
                "confidence": "candidate_source_derived_requires_review",
                "numeric_row_rule": row.get("numeric_row_rule"),
            }
        )
    rows.sort(key=lambda item: (item["dataset_id"], -(item["latest_spending"] or 0), item["canonical_product"]))
    return rows


def build_validation_report(
    run_at: str,
    sources: dict[str, Any],
    inventory: list[dict[str, Any]],
    source_scan_summaries: list[dict[str, Any]],
    source_log: list[dict[str, Any]],
    product_summary: list[dict[str, Any]],
    include_large: bool,
    include_samples: bool,
    scan_all_sources: bool = False,
) -> dict[str, Any]:
    source_errors = [entry for entry in source_log if entry.get("status") != "ok"]
    zero_row_scans = [scan for scan in source_scan_summaries if scan.get("status") == "scanned" and not scan.get("rows_scanned")]
    large_sources_executed = include_large or scan_all_sources
    skipped_p0 = [
        dataset
        for dataset in sources["datasets"]
        if dataset.get("priority") == "P0"
        and dataset.get("large_source")
        and not large_sources_executed
    ]
    missing_metadata = [item["id"] for item in inventory if item.get("metadata_status") != "ok"]
    missing_columns = [item["id"] for item in inventory if item.get("columns_status") != "ok"]
    warnings: list[dict[str, Any]] = []
    if skipped_p0:
        warnings.append({"code": "skipped_large_p0_sources", "count": len(skipped_p0), "datasets": [item["id"] for item in skipped_p0]})
    if zero_row_scans:
        warnings.append({"code": "zero_row_source_scans", "count": len(zero_row_scans), "datasets": [item["dataset_id"] for item in zero_row_scans]})
    ingredient_ambiguous = [row for row in product_summary if str(row.get("canonical_product", "")).startswith("ingredient:")]
    if ingredient_ambiguous:
        warnings.append({"code": "ingredient_ambiguous_records", "count": len(ingredient_ambiguous)})
    non_consecutive = [
        row for row in product_summary
        if row.get("latest_prior_period_relation") == "latest_vs_prior_observed"
    ]
    if non_consecutive:
        warnings.append({"code": "non_consecutive_prior_period_comparisons", "count": len(non_consecutive)})
    return {
        "run_at": run_at,
        "status": "review_required" if warnings or source_errors else "passed",
        "include_large_source_downloads": include_large,
        "scan_all_sources": scan_all_sources,
        "include_samples": include_samples,
        "checks": {
            "pinned_datasets": len(sources["datasets"]),
            "metadata_failures": missing_metadata,
            "columns_failures": missing_columns,
            "source_log_entries": len(source_log),
            "source_errors": len(source_errors),
            "source_scan_count": len(source_scan_summaries),
            "zero_row_source_scans": zero_row_scans,
            "product_summary_rows": len(product_summary),
        },
        "warnings": warnings,
        "source_errors": source_errors,
    }


def write_validation_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Refresh Validation Report",
        "",
        f"Run timestamp: {report['run_at']}",
        f"Status: {report['status']}",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- {warning['code']}: {warning}")
    else:
        lines.append("- None.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_run_comparison(previous_manifest: dict[str, Any] | None, current_run_at: str, outputs_dir: Path) -> dict[str, Any]:
    current_outputs = {
        str(path.relative_to(ROOT)): {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(outputs_dir.glob("*"))
        if path.is_file() and path.name not in {"run_manifest.json", "run_comparison.json"}
    }
    previous_outputs = {
        item["path"]: {"bytes": item.get("bytes"), "sha256": item.get("sha256")}
        for item in (previous_manifest or {}).get("outputs", [])
    }
    rows: list[dict[str, Any]] = []
    for path in sorted(set(previous_outputs) | set(current_outputs)):
        previous = previous_outputs.get(path)
        current = current_outputs.get(path)
        rows.append(
            {
                "path": path,
                "previous_sha256": previous.get("sha256") if previous else None,
                "current_sha256": current.get("sha256") if current else None,
                "previous_bytes": previous.get("bytes") if previous else None,
                "current_bytes": current.get("bytes") if current else None,
                "status": "new" if previous is None else "removed" if current is None else "unchanged" if previous.get("sha256") == current.get("sha256") else "changed",
            }
        )
    return {
        "previous_run_at": (previous_manifest or {}).get("run_at"),
        "current_run_at": current_run_at,
        "previous_script_sha256": (previous_manifest or {}).get("script_sha256"),
        "current_script_sha256": sha256_file(Path(__file__)),
        "output_comparison": rows,
    }


def write_analyst_signal_brief(
    path: Path,
    run_at: str,
    product_summary: list[dict[str, Any]],
    validation_report: dict[str, Any],
) -> None:
    spending_rows = [
        row for row in product_summary
        if row.get("latest_year_total_spending") and row.get("dataset_id") in {"cms/part-d-spending", "cms/medicaid-spending"}
        and not str(row.get("canonical_product", "")).startswith("ingredient:")
    ]
    top_rows = sorted(spending_rows, key=lambda row: row.get("latest_year_total_spending") or 0, reverse=True)[:12]
    shortage_rows = [row for row in product_summary if row.get("dataset_id") == "fda/drug-shortages"]
    lines = [
        "# Analyst Signal Brief: GLP-1 Obesity OpenData",
        "",
        f"Run timestamp: {run_at}",
        "",
        "## Status",
        "",
        f"- Validation status: `{validation_report['status']}`.",
        "- This brief is source-derived from deterministic lexical matches and requires analyst review before use as final CI.",
        "- CMS annual spending signals are usable for product-level spend/claim screening where brand-specific rows exist.",
        "- Large P0 sources remain metadata-only unless the run is executed with `--include-large-source-downloads`.",
        "",
        "## Largest Latest-Year Public Payer Spending Signals",
        "",
    ]
    for row in top_rows:
        relation = row.get("latest_prior_period_relation")
        change_label = "YoY spending change" if relation == "strict_yoy" else "Latest-vs-prior-observed spending change"
        lines.append(
            f"- `{row['dataset_id']}` / {row['canonical_product']}: "
            f"{row['latest_year']} spending ${row['latest_year_total_spending']:,.0f}; "
            f"claims {row['latest_year_total_claims']:,.0f}; "
            f"{change_label} {row.get('latest_vs_prior_spending_pct_change')}%; "
            f"rule `{row.get('numeric_row_rule')}`."
        )
    lines.extend(["", "## Supply and Lifecycle Watch", ""])
    if shortage_rows:
        limited = [
            row for row in shortage_rows
            if row.get("current_limited_availability_rows", 0)
        ]
        watch = [
            row for row in shortage_rows
            if not row.get("current_limited_availability_rows", 0)
        ]
        for row in sorted(limited, key=lambda item: item["canonical_product"]):
            lines.append(
                f"- FDA limited-availability candidate: {row['canonical_product']} "
                f"({row['current_limited_availability_rows']} unique source rows; {row['match_records']} lexical match records)."
            )
        for row in sorted(watch, key=lambda item: item["canonical_product"]):
            lines.append(
                f"- FDA shortage-watch candidate: {row['canonical_product']} "
                f"({row['matched_source_rows']} unique source rows; classifications {row.get('shortage_classifications', {})})."
            )
    else:
        lines.append("- No FDA shortage candidate matches in this run.")
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- Source rows are candidate matches, not adjudicated findings.",
            "- Manufacturer names and ingredient-only matches are not enough for definitive brand attribution.",
            "- Public CMS spending is gross public-program spending context and not manufacturer net revenue.",
            "- Spending direction fields describe spending change, not claims change.",
            "- Non-consecutive annual comparisons are labeled as latest-vs-prior-observed rather than strict YoY.",
            "- The next execution step is analyst review of `match_qc_sample.csv`, then a large-source scan for `cms/sdud`, `cms/nadac`, and `cms/drug-rebate-products` if network/runtime constraints permit.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_summary(
    path: Path,
    run_at: str,
    inventory: list[dict[str, Any]],
    search_results: list[dict[str, Any]],
    source_scan_summaries: list[dict[str, Any]],
    matches: list[dict[str, Any]],
    product_summary: list[dict[str, Any]],
) -> None:
    ok_meta = sum(1 for item in inventory if item.get("metadata_status") == "ok")
    scanned = [item for item in source_scan_summaries if item.get("status") == "scanned"]
    skipped = [item for item in source_scan_summaries if item.get("status") == "skipped_large_source"]
    scanned_dataset_ids = {scan["dataset_id"] for scan in source_scan_summaries}
    not_scanned = [item for item in inventory if item["id"] not in scanned_dataset_ids]
    metadata_only_large = [item for item in not_scanned if item.get("large_source") and item.get("refresh_default") == "metadata_only"]
    product_counts: dict[str, int] = {}
    dataset_counts: dict[str, int] = {}
    for match in matches:
        product_counts[match["canonical_product"]] = product_counts.get(match["canonical_product"], 0) + 1
        dataset_counts[match["dataset_id"]] = dataset_counts.get(match["dataset_id"], 0) + 1
    unique_dataset_counts: dict[str, int] = {}
    for dataset_id in sorted(dataset_counts):
        unique_dataset_counts[dataset_id] = len(unique_source_rows_for_matches([match for match in matches if match["dataset_id"] == dataset_id]))

    lines = [
        "# GLP-1 Obesity OpenData Refresh Summary",
        "",
        f"Run timestamp: {run_at}",
        "",
        "## Coverage",
        "",
        f"- Pinned datasets: {len(inventory)}",
        f"- Metadata retrieved successfully: {ok_meta}",
        f"- Pinned search queries run: {len(search_results)}",
        f"- Upstream sources scanned: {len(scanned)}",
        f"- Upstream sources not scanned: {len(skipped) + len(not_scanned)}",
        f"- Large upstream source scans skipped by default: {len(skipped) + len(metadata_only_large)}",
        f"- Lexical product match records: {len(matches)}",
        f"- Unique matched source rows: {len(unique_source_rows_for_matches(matches))}",
        f"- Product-by-dataset summary rows: {len(product_summary)}",
        "",
        "## Match Counts by Dataset",
        "",
    ]
    if dataset_counts:
        for dataset_id, count in sorted(dataset_counts.items()):
            lines.append(f"- `{dataset_id}`: {count} lexical match records; {unique_dataset_counts.get(dataset_id, 0)} unique source rows")
    else:
        lines.append("- No product matches generated in this run.")
    lines.extend(["", "## Match Counts by Product", ""])
    if product_counts:
        for product, count in sorted(product_counts.items()):
            lines.append(f"- {product}: {count}")
    else:
        lines.append("- No product matches generated in this run.")
    lines.extend(
        [
            "",
            "## Review Notes",
            "",
            "- Treat product matches as a deterministic candidate set, not final interpreted CI findings.",
            "- Use `--scan-all-sources --include-large-source-downloads` when the deliverable requires every pinned source URL to execute, including sources marked metadata-only in the default run.",
            "- Review `source_log.json` for failed requests before relying on a refresh.",
            "- Update `config/glp1_product_dictionary.json` when new GLP-1/incretin brands, ingredients, or sponsors enter scope.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-large-source-downloads", action="store_true")
    parser.add_argument("--scan-all-sources", action="store_true", help="Scan every pinned dataset with a source_url, including metadata-only sources.")
    parser.add_argument("--include-samples", action="store_true", help="Fetch limit=2 sample rows from each OpenData dataset.")
    parser.add_argument("--sleep-seconds", type=float, default=0.15, help="Polite delay between OpenData API requests.")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    run_at = utc_now()
    previous_manifest = read_json(OUT / "run_manifest.json") if (OUT / "run_manifest.json").exists() else None
    source_log: list[dict[str, Any]] = []
    sources = read_json(SOURCES_CONFIG)
    products = read_json(PRODUCT_CONFIG)
    api_base = sources["api_base"].rstrip("/")
    terms, _ = build_match_terms(products)

    inventory: list[dict[str, Any]] = []
    dataset_meta_by_id: dict[str, dict[str, Any]] = {}
    for dataset in sorted(sources["datasets"], key=lambda item: item["id"]):
        dataset_id = dataset["id"]
        meta_url = dataset_url(api_base, dataset_id, "/meta")
        columns_url = dataset_url(api_base, dataset_id, "/columns")
        meta = get_json(meta_url, source_log, f"opendata_metadata:{dataset_id}")
        time.sleep(args.sleep_seconds)
        columns_response = get_json(columns_url, source_log, f"opendata_columns:{dataset_id}")
        time.sleep(args.sleep_seconds)
        sample = None
        if args.include_samples:
            sample_url = dataset_url(api_base, dataset_id, "?limit=2")
            sample = get_json(sample_url, source_log, f"opendata_sample:{dataset_id}")
            time.sleep(args.sleep_seconds)
        sample_columns, sample_types, sample_rows = data_rows_from_api_response(sample)
        column_records = columns_response if isinstance(columns_response, list) else columns_response.get("columns", []) if isinstance(columns_response, dict) else []
        metadata_status = "ok" if isinstance(meta, dict) else "error"
        if isinstance(meta, dict):
            dataset_meta_by_id[dataset_id] = meta
        inventory.append(
            {
                **dataset,
                "catalog_url": f"{sources['catalog_base'].rstrip('/')}/{dataset_id}",
                "metadata_status": metadata_status,
                "metadata": {
                    key: meta.get(key)
                    for key in [
                        "provider",
                        "slug",
                        "name",
                        "description",
                        "status",
                        "rows",
                        "row_count",
                        "updated_at",
                        "source_url",
                        "license",
                        "category",
                    ]
                }
                if isinstance(meta, dict)
                else None,
                "columns_status": "ok" if columns_response is not None else "error",
                "columns": column_records,
                "sample_included": args.include_samples,
                "sample_columns": sample_columns,
                "sample_types": sample_types,
                "sample_rows": sample_rows,
            }
        )

    search_results: list[dict[str, Any]] = []
    for query in sources["search_queries"]:
        url = f"{api_base}/search?{urllib.parse.urlencode({'q': query, 'limit': 10})}"
        result = get_json(url, source_log, f"opendata_search:{query}")
        time.sleep(args.sleep_seconds)
        search_results.append({"query": query, "url": url, "result": result})

    all_matches: list[dict[str, Any]] = []
    source_scan_summaries: list[dict[str, Any]] = []
    for dataset in sorted(sources["datasets"], key=lambda item: item["id"]):
        if dataset.get("refresh_default") != "source_scan" and not args.scan_all_sources:
            continue
        dataset_id = dataset["id"]
        meta = dataset_meta_by_id.get(dataset_id, {})
        source_url = meta.get("source_url")
        if not source_url:
            source_scan_summaries.append({"dataset_id": dataset_id, "status": "missing_source_url"})
            continue
        matches, summary = scan_source_for_matches(
            dataset_id=dataset_id,
            source_url=source_url,
            source_log=source_log,
            terms=terms,
            include_large=args.include_large_source_downloads or args.scan_all_sources,
            large_source=bool(dataset.get("large_source")),
        )
        all_matches.extend(matches)
        source_scan_summaries.append(summary)

    all_matches = enrich_matches(all_matches, source_log, inventory, products.get("version", "unknown"))
    signal_specs = build_signal_specs()
    compact_matches = [compact_match_for_csv(match) for match in all_matches]
    product_signal_summary = build_product_signal_summary(all_matches)
    record_trace_map = build_record_trace_map(all_matches)
    source_coverage_matrix = build_source_coverage_matrix(sources, inventory, source_scan_summaries, all_matches)
    unmatched_terms = build_unmatched_dictionary_terms(terms, all_matches)
    match_qc_sample = build_match_qc_sample(all_matches)
    signal_delta_summary = build_signal_delta_summary(product_signal_summary)
    validation_report = build_validation_report(
        run_at,
        sources,
        inventory,
        source_scan_summaries,
        source_log,
        product_signal_summary,
        args.include_large_source_downloads,
        args.include_samples,
        args.scan_all_sources,
    )

    write_json(OUT / "dataset_inventory.json", inventory)
    write_json(OUT / "opendata_search_results.json", search_results)
    write_json(OUT / "glp1_product_matches.json", all_matches)
    write_csv(OUT / "glp1_product_matches.csv", compact_matches)
    write_json(OUT / "product_signal_summary.json", product_signal_summary)
    write_csv(OUT / "product_signal_summary.csv", product_signal_summary)
    write_jsonl(OUT / "record_trace_map.jsonl", record_trace_map)
    write_csv(OUT / "source_coverage_matrix.csv", source_coverage_matrix)
    write_csv(OUT / "unmatched_dictionary_terms.csv", unmatched_terms)
    write_csv(OUT / "match_qc_sample.csv", match_qc_sample)
    write_csv(OUT / "signal_delta_summary.csv", signal_delta_summary)
    write_json(OUT / "refresh_validation_report.json", validation_report)
    write_validation_markdown(OUT / "refresh_validation_report.md", validation_report)
    write_json(OUT / "source_scan_summaries.json", source_scan_summaries)
    write_json(OUT / "signal_specs.json", signal_specs)
    write_json(OUT / "source_log.json", source_log)
    write_summary(OUT / "refresh_summary.md", run_at, inventory, search_results, source_scan_summaries, all_matches, product_signal_summary)
    write_analyst_signal_brief(OUT / "analyst_signal_brief.md", run_at, product_signal_summary, validation_report)
    (OUT / "methodology_snapshot.md").write_text(METHODOLOGY.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    run_comparison = build_run_comparison(previous_manifest, run_at, OUT)
    write_json(OUT / "run_comparison.json", run_comparison)

    outputs = sorted(path for path in OUT.glob("*") if path.is_file())
    manifest = {
        "run_at": run_at,
        "script": str(Path(__file__).relative_to(ROOT)),
        "script_sha256": sha256_file(Path(__file__)),
        "scripts": script_manifest_entries(),
        "python_version": sys.version,
        "include_large_source_downloads": args.include_large_source_downloads,
        "scan_all_sources": args.scan_all_sources,
        "include_samples": args.include_samples,
        "config": {
            "opendata_sources": {
                "path": str(SOURCES_CONFIG.relative_to(ROOT)),
                "sha256": sha256_file(SOURCES_CONFIG),
                "version": sources.get("version"),
            },
            "glp1_product_dictionary": {
                "path": str(PRODUCT_CONFIG.relative_to(ROOT)),
                "sha256": sha256_file(PRODUCT_CONFIG),
                "version": products.get("version"),
            },
            "methodology": {
                "path": str(METHODOLOGY.relative_to(ROOT)),
                "sha256": sha256_file(METHODOLOGY),
            },
        },
        "outputs": [
            {
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in outputs
            if path.name != "run_manifest.json"
        ],
    }
    write_json(OUT / "run_manifest.json", manifest)
    print(f"Wrote GLP-1 OpenData CI refresh outputs to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
