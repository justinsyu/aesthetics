#!/usr/bin/env python3
"""Refresh high-value GLP-1 obesity CI sources beyond OpenData."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import os
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "high_value_ci_sources.json"
PRODUCT_CONFIG = ROOT / "config" / "glp1_product_dictionary.json"
ASSET_CONFIG = ROOT / "config" / "glp1_asset_dictionary.json"
STATE_MEDICAID_PDL_CONFIG = ROOT / "config" / "state_medicaid_pdl_sources.json"
HIGH_VALUE_METHODOLOGY = ROOT / "HIGH_VALUE_METHODOLOGY.md"
OUT = ROOT / "generated_data" / "high_value_ci"
CORE_MATCHES = ROOT / "generated_data" / "glp1_product_matches.csv"
MANUAL_INPUTS = ROOT / "manual_inputs" / "high_value_ci"
TEMPLATES = ROOT / "input_templates" / "high_value_ci"
USER_AGENT = "linkedin-posts-mac-glp1-high-value-ci/2026-05-28 contact:local-refresh"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def write_template_csv(path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()


def normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"[^A-Z0-9]+", " ", text.upper())
    return re.sub(r"\s+", " ", text).strip()


def get_json(url: str, source_log: list[dict[str, Any]], purpose: str, timeout: int = 60) -> Any | None:
    body = get_bytes(url, source_log, purpose, timeout=timeout)
    if body is None:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        source_log[-1]["json_error"] = "decode_failed"
        return None


def get_bytes(url: str, source_log: list[dict[str, Any]], purpose: str, timeout: int = 60, retries: int = 2) -> bytes | None:
    started = utc_now()
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "text/html,application/json,*/*",
            "User-Agent": USER_AGENT,
        },
    )
    if "patentsview" in urllib.parse.urlparse(url).netloc.lower() and os.environ.get("PATENTSVIEW_API_KEY"):
        request.add_header("X-Api-Key", os.environ["PATENTSVIEW_API_KEY"])
    last_error: str | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                status = getattr(response, "status", None)
                content_type = response.headers.get("Content-Type", "")
            break
        except urllib.error.HTTPError as exc:
            body = exc.read()
            last_error = str(exc)
            if exc.code in {429, 500, 502, 503, 504} and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            source_log.append(
                {
                    "purpose": purpose,
                    "url": url,
                    "retrieved_at": started,
                    "status": "error",
                    "http_status": exc.code,
                    "error": str(exc),
                    "response_sha256": sha256_bytes(body),
                    "attempts": attempt + 1,
                }
            )
            return None
        except Exception as exc:  # noqa: BLE001 - keep concrete network failure trace.
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            source_log.append(
                {
                    "purpose": purpose,
                    "url": url,
                    "retrieved_at": started,
                    "status": "error",
                    "error": last_error,
                    "attempts": attempt + 1,
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
            "attempts": attempt + 1,
        }
    )
    return body


def get_http_content_length(url: str, source_log: list[dict[str, Any]], purpose: str, timeout: int = 60) -> int | None:
    started = utc_now()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            length = response.headers.get("Content-Length")
            status = getattr(response, "status", None)
    except Exception as exc:  # noqa: BLE001 - trace but allow fallback path.
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
            "content_length": length or "",
        }
    )
    return int(length) if length and length.isdigit() else None


def get_range_bytes(
    url: str,
    start: int,
    end: int,
    source_log: list[dict[str, Any]],
    purpose: str,
    timeout: int = 60,
) -> bytes | None:
    started = utc_now()
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Range": f"bytes={start}-{end}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            content_range = response.headers.get("Content-Range", "")
            content_length = response.headers.get("Content-Length", "")
            if status != 206:
                source_log.append(
                    {
                        "purpose": purpose,
                        "url": url,
                        "retrieved_at": started,
                        "status": "error",
                        "http_status": status,
                        "error": "server did not honor Range request",
                        "content_length": content_length,
                        "range_start": start,
                        "range_end": end,
                    }
                )
                return None
            body = response.read()
    except Exception as exc:  # noqa: BLE001 - trace but allow fallback path.
        source_log.append(
            {
                "purpose": purpose,
                "url": url,
                "retrieved_at": started,
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
                "range_start": start,
                "range_end": end,
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
            "bytes": len(body),
            "range_start": start,
            "range_end": end,
            "content_range": content_range,
            "response_sha256": sha256_bytes(body),
        }
    )
    return body


def product_terms() -> list[str]:
    products = read_json(PRODUCT_CONFIG)
    terms: set[str] = set()
    for product in products["products"]:
        terms.add(product["canonical_product"])
        terms.add(product.get("ingredient", ""))
        terms.update(product.get("brand_terms", []))
        terms.update(product.get("ingredient_terms", []))
    if ASSET_CONFIG.exists():
        assets = read_json(ASSET_CONFIG)
        for asset in assets.get("assets", []):
            terms.add(asset.get("asset", ""))
            terms.add(asset.get("sponsor", ""))
            terms.add(asset.get("mechanism", ""))
            terms.update(asset.get("aliases", []))
    return sorted({term for term in terms if term})


def term_hits(text: str, terms: list[str]) -> list[str]:
    normalized = normalize_text(text)
    return [term for term in terms if normalize_text(term) in normalized]


def join_values(values: Any) -> str:
    if not values:
        return ""
    if isinstance(values, list):
        return "; ".join(str(value) for value in values)
    return str(values)


def safe_field_name(value: str) -> str:
    field = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    return field or "field"


def source_row_hash(row: dict[str, Any]) -> str:
    return sha256_bytes(json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def append_source_fields(target: dict[str, Any], row: dict[str, Any], prefix: str = "field_", max_fields: int = 40) -> None:
    for key in sorted(row.keys())[:max_fields]:
        value = row.get(key)
        if value is None:
            continue
        target[f"{prefix}{safe_field_name(str(key))}"] = str(value)[:1000]


def decode_text(body: bytes) -> str:
    for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            return body.decode(encoding)
        except UnicodeDecodeError:
            continue
    return body.decode("utf-8", errors="replace")


def sniff_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample[:4096], delimiters=",|\t;").delimiter
    except csv.Error:
        if "|" in sample:
            return "|"
        if "\t" in sample:
            return "\t"
        return ","


def iter_delimited_rows_from_text(text: str) -> list[dict[str, str]]:
    delimiter = sniff_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    return [dict(row) for row in reader]


def extract_zip_members_with_tar(body: bytes) -> dict[str, bytes]:
    tar_path = shutil.which("tar")
    if not tar_path:
        return {}
    with tempfile.TemporaryDirectory(prefix="glp1_ci_zip_") as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "source.zip"
        extract_path = tmp_path / "extract"
        extract_path.mkdir()
        zip_path.write_bytes(body)
        result = subprocess.run(
            [tar_path, "-xf", str(zip_path), "-C", str(extract_path)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return {}
        members: dict[str, bytes] = {}
        for path in sorted(item for item in extract_path.rglob("*") if item.is_file()):
            relative = path.relative_to(extract_path).as_posix()
            if relative.lower().endswith((".csv", ".txt")):
                members[relative] = path.read_bytes()
        return members


def date_key_from_name(value: str) -> str:
    matches = re.findall(r"(20\d{2})[_-]?(20\d{6}|20\d{4}|\d{8})", value)
    if matches:
        return max("".join(match) for match in matches)
    dates = re.findall(r"20\d{6}", value)
    return max(dates) if dates else value


def product_query_terms() -> list[str]:
    products = read_json(PRODUCT_CONFIG)
    queries: list[str] = []
    for product in products["products"]:
        queries.append(product["canonical_product"])
        queries.extend(product.get("brand_terms", []))
        queries.append(product.get("ingredient", ""))
    return sorted({query for query in queries if query})


def normalize_ndc(value: Any) -> str:
    return re.sub(r"\D+", "", "" if value is None else str(value))


def ndc_product_lookup() -> dict[str, set[str]]:
    lookup: dict[str, set[str]] = {}
    if not CORE_MATCHES.exists():
        return lookup
    with CORE_MATCHES.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            product = row.get("canonical_product") or row.get("match_term") or ""
            if not product or product.startswith("ingredient:"):
                continue
            for field in ["ndc", "product_ndc", "package_ndc"]:
                ndc = normalize_ndc(row.get(field))
                if len(ndc) == 11:
                    lookup.setdefault(ndc, set()).add(product)
    return lookup


def parse_zip_central_directory_entries(central_directory: bytes) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    offset = 0
    header_struct = struct.Struct("<4sHHHHHHIIIHHHHHII")
    while offset + header_struct.size <= len(central_directory):
        fields = header_struct.unpack_from(central_directory, offset)
        if fields[0] != b"PK\x01\x02":
            break
        compression_method = fields[4]
        compressed_size = fields[8]
        uncompressed_size = fields[9]
        filename_length = fields[10]
        extra_length = fields[11]
        comment_length = fields[12]
        local_header_offset = fields[16]
        name_start = offset + header_struct.size
        name_end = name_start + filename_length
        filename = central_directory[name_start:name_end].decode("utf-8", errors="replace")
        entries.append(
            {
                "filename": filename,
                "compression_method": compression_method,
                "compressed_size": compressed_size,
                "uncompressed_size": uncompressed_size,
                "local_header_offset": local_header_offset,
            }
        )
        offset = name_end + extra_length + comment_length
    return entries


def find_zip64_eocd_offset(tail: bytes, tail_start: int, locator_offset_in_tail: int) -> int | None:
    locator = tail[locator_offset_in_tail : locator_offset_in_tail + 20]
    if len(locator) < 20 or locator[:4] != b"PK\x06\x07":
        return None
    return struct.unpack_from("<Q", locator, 8)[0]


def fetch_zip_central_directory(url: str, source_log: list[dict[str, Any]], purpose_prefix: str) -> list[dict[str, Any]]:
    length = get_http_content_length(url, source_log, f"{purpose_prefix}:head")
    if not length:
        return []
    tail_size = min(length, 1024 * 1024)
    tail_start = length - tail_size
    tail = get_range_bytes(url, tail_start, length - 1, source_log, f"{purpose_prefix}:eocd_tail")
    if not tail:
        return []
    eocd_index = tail.rfind(b"PK\x05\x06")
    if eocd_index < 0 or eocd_index + 22 > len(tail):
        return []
    disk_entries, total_entries, cd_size_32, cd_offset_32 = struct.unpack_from("<HHII", tail, eocd_index + 8)
    cd_size = cd_size_32
    cd_offset = cd_offset_32
    if cd_size_32 == 0xFFFFFFFF or cd_offset_32 == 0xFFFFFFFF or total_entries == 0xFFFF:
        locator_index = tail.rfind(b"PK\x06\x07", 0, eocd_index)
        zip64_eocd_offset = find_zip64_eocd_offset(tail, tail_start, locator_index) if locator_index >= 0 else None
        if zip64_eocd_offset is None:
            return []
        zip64_eocd = get_range_bytes(url, zip64_eocd_offset, zip64_eocd_offset + 75, source_log, f"{purpose_prefix}:zip64_eocd")
        if not zip64_eocd or zip64_eocd[:4] != b"PK\x06\x06":
            return []
        cd_size = struct.unpack_from("<Q", zip64_eocd, 40)[0]
        cd_offset = struct.unpack_from("<Q", zip64_eocd, 48)[0]
    central_directory = get_range_bytes(url, cd_offset, cd_offset + cd_size - 1, source_log, f"{purpose_prefix}:central_directory")
    if not central_directory:
        return []
    return parse_zip_central_directory_entries(central_directory)


def fetch_stored_zip_member(url: str, entry: dict[str, Any], source_log: list[dict[str, Any]], purpose_prefix: str) -> bytes | None:
    if int(entry.get("compression_method", -1)) != 0:
        return None
    local_offset = int(entry["local_header_offset"])
    local_header = get_range_bytes(url, local_offset, local_offset + 29, source_log, f"{purpose_prefix}:local_header")
    if not local_header or local_header[:4] != b"PK\x03\x04":
        return None
    filename_length, extra_length = struct.unpack_from("<HH", local_header, 26)
    data_start = local_offset + 30 + filename_length + extra_length
    data_end = data_start + int(entry["compressed_size"]) - 1
    return get_range_bytes(url, data_start, data_end, source_log, f"{purpose_prefix}:member_payload:{entry['filename']}")


def collect_clinicaltrials(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    base_url = source["base_url"].rstrip("/")
    for query in source.get("queries", []):
        params = {
            "format": "json",
            "pageSize": str(max_records),
            "query.term": query,
        }
        url = f"{base_url}/studies?{urllib.parse.urlencode(params)}"
        data = get_json(url, source_log, f"clinicaltrials_gov:{query}")
        time.sleep(sleep_seconds)
        for study in (data or {}).get("studies", []):
            protocol = study.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            design = protocol.get("designModule", {})
            conditions = protocol.get("conditionsModule", {})
            arms = protocol.get("armsInterventionsModule", {})
            sponsor = protocol.get("sponsorCollaboratorsModule", {})
            nct_id = identification.get("nctId")
            if not nct_id or nct_id in seen:
                continue
            seen.add(nct_id)
            interventions = arms.get("interventions") or []
            rows.append(
                {
                    "source_id": source["id"],
                    "category": source["category"],
                    "query": query,
                    "nct_id": nct_id,
                    "title": identification.get("briefTitle"),
                    "overall_status": status.get("overallStatus"),
                    "phase": join_values(design.get("phases")),
                    "study_type": design.get("studyType"),
                    "start_date": (status.get("startDateStruct") or {}).get("date"),
                    "primary_completion_date": (status.get("primaryCompletionDateStruct") or {}).get("date"),
                    "last_update_posted": (status.get("lastUpdatePostDateStruct") or {}).get("date"),
                    "conditions": join_values(conditions.get("conditions")),
                    "interventions": join_values([item.get("name") for item in interventions if item.get("name")]),
                    "lead_sponsor": (sponsor.get("leadSponsor") or {}).get("name"),
                    "url": f"https://clinicaltrials.gov/study/{nct_id}",
                    "source_status": "collected",
                }
            )
    return rows


def collect_pubmed(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    base_url = source["base_url"].rstrip("/")
    for query in source.get("queries", []):
        params = {"db": "pubmed", "retmode": "json", "retmax": str(max_records), "sort": "pub date", "term": query}
        search_url = f"{base_url}/esearch.fcgi?{urllib.parse.urlencode(params)}"
        search = get_json(search_url, source_log, f"pubmed_esearch:{query}")
        time.sleep(sleep_seconds)
        ids = (search or {}).get("esearchresult", {}).get("idlist", [])
        if not ids:
            continue
        summary_params = {"db": "pubmed", "retmode": "json", "id": ",".join(ids)}
        summary_url = f"{base_url}/esummary.fcgi?{urllib.parse.urlencode(summary_params)}"
        summary = get_json(summary_url, source_log, f"pubmed_esummary:{query}")
        time.sleep(sleep_seconds)
        result = (summary or {}).get("result", {})
        for pmid in result.get("uids", []):
            if pmid in seen:
                continue
            seen.add(pmid)
            item = result.get(pmid, {})
            rows.append(
                {
                    "source_id": source["id"],
                    "category": source["category"],
                    "query": query,
                    "pmid": pmid,
                    "title": item.get("title"),
                    "journal": item.get("fulljournalname"),
                    "pubdate": item.get("pubdate"),
                    "authors": join_values([author.get("name") for author in item.get("authors", [])[:8]]),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "source_status": "collected",
                }
            )
    return rows


def collect_dailymed(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    base_url = source["base_url"].rstrip("/")
    for drug_name in source.get("queries", []):
        params = {"drug_name": drug_name, "pagesize": str(max_records)}
        url = f"{base_url}/spls.json?{urllib.parse.urlencode(params)}"
        data = get_json(url, source_log, f"dailymed_labels:{drug_name}")
        time.sleep(sleep_seconds)
        for item in (data or {}).get("data", []):
            setid = item.get("setid")
            key = setid or json.dumps(item, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "source_id": source["id"],
                    "category": source["category"],
                    "query": drug_name,
                    "setid": setid,
                    "title": item.get("title"),
                    "published_date": item.get("published_date"),
                    "effective_time": item.get("effective_time"),
                    "url": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}" if setid else "",
                    "source_status": "collected",
                }
            )
    return rows


def collect_sec(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    base_url = source["base_url"].rstrip("/")
    wanted_forms = {"10-K", "10-Q", "8-K", "20-F", "6-K", "S-1", "424B5"}
    terms = product_terms()
    for company in source.get("companies", []):
        cik = str(company["cik"]).zfill(10)
        url = f"{base_url}/submissions/CIK{cik}.json"
        data = get_json(url, source_log, f"sec_edgar_submissions:{company['ticker']}")
        time.sleep(sleep_seconds)
        recent = ((data or {}).get("filings") or {}).get("recent") or {}
        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        primary_docs = recent.get("primaryDocument", [])
        added = 0
        text_fetched = 0
        for idx, form in enumerate(forms):
            if form not in wanted_forms:
                continue
            accession = accession_numbers[idx]
            accession_path = accession.replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_path}/{primary_docs[idx]}" if idx < len(primary_docs) else ""
            row = {
                "source_id": source["id"],
                "category": source["category"],
                "company": company["name"],
                "ticker": company["ticker"],
                "cik": cik,
                "form": form,
                "filing_date": filing_dates[idx] if idx < len(filing_dates) else "",
                "report_date": report_dates[idx] if idx < len(report_dates) else "",
                "accession_number": accession,
                "primary_document": primary_docs[idx] if idx < len(primary_docs) else "",
                "url": filing_url,
                "source_status": "collected_metadata",
            }
            if source.get("fetch_text") and filing_url and text_fetched < int(source.get("text_max_per_company", 0)):
                body = get_bytes(filing_url, source_log, f"sec_edgar_filing_text:{company['ticker']}:{accession}", timeout=90)
                time.sleep(sleep_seconds)
                if body is not None:
                    text = strip_html_text(decode_text(body))
                    hits = term_hits(text, terms)
                    row.update(
                        {
                            "source_status": "collected_with_text",
                            "filing_text_sha256": sha256_bytes(body),
                            "filing_text_bytes": len(body),
                            "filing_text_matched_terms": join_values(hits),
                            "filing_text_snippet": evidence_snippet(text, hits or ["obesity", "manufacturing", "supply", "launch", "trial"]),
                        }
                    )
                    text_fetched += 1
                else:
                    row["source_status"] = "metadata_text_fetch_failed"
            rows.append(row)
            added += 1
            if added >= max_records:
                break
    return rows


def strip_html_text(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def evidence_snippet(text: str, terms: list[str], radius: int = 220) -> str:
    lowered = text.lower()
    for term in terms:
        if not term:
            continue
        idx = lowered.find(str(term).lower())
        if idx >= 0:
            start = max(0, idx - radius)
            end = min(len(text), idx + len(str(term)) + radius)
            return text[start:end]
    return text[: min(len(text), radius * 2)]


def collect_data_gov_resources(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    resources = resolve_data_gov_resources(source, source_log, max_records, sleep_seconds)
    zip_resources = [
        resource
        for resource in resources
        if str(resource.get("url", "")).lower().endswith(".zip") or str(resource.get("format", "")).lower() == "zip"
    ]
    if zip_resources:
        attempted_results: list[dict[str, Any]] = []
        ordered = sorted(zip_resources, key=lambda resource: date_key_from_name(f"{resource.get('name', '')} {resource.get('url', '')}"), reverse=True)
        for resource in ordered[: int(source.get("max_zip_attempts", 3))]:
            parsed = parse_cms_formulary_zip(source, resource, source_log, max_records, sleep_seconds)
            if not parsed:
                continue
            statuses = {row.get("source_status") for row in parsed}
            if statuses not in ({"bulk_zip_unsupported_compression"}, {"bulk_zip_range_member_unavailable"}):
                return parsed
            attempted_results.extend(parsed)
        if attempted_results:
            return attempted_results
    return resources or public_catalog_rows(source)


def resolve_data_gov_resources(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    url = source["base_url"]
    body = get_bytes(url, source_log, f"{source['id']}:landing_page")
    time.sleep(sleep_seconds)
    if body is None:
        return []
    rows: list[dict[str, Any]] = []
    for link in extract_links_from_html(body, url):
        lower = link.lower()
        if not any(token in lower for token in ["data.cms.gov", "download.cms.gov", ".zip", ".csv", ".pdf"]):
            continue
        rows.append(
            {
                "source_id": source["id"],
                "category": source["category"],
                "resource_id": "",
                "name": link.rsplit("/", 1)[-1],
                "format": "zip" if lower.endswith(".zip") else "pdf" if lower.endswith(".pdf") else "resource_link",
                "url": link,
                "last_modified": "",
                "created": "",
                "description": "Discovered from public Part D formulary catalog landing page",
                "source_status": "discovered_bulk_resource",
            }
        )
        if len(rows) >= max_records:
            break
    return rows


def is_cms_relevant_zip_member(member_name: str) -> bool:
    lower_name = member_name.lower()
    if "pharmacy networks" in lower_name:
        return False
    return any(
        token in lower_name
        for token in [
            "formulary",
            "beneficiary cost",
            "excluded drugs",
            "indication based",
            "partial gap",
            "plan information",
            "senior savings",
        ]
    )


def parse_cms_formulary_zip_by_range(
    source: dict[str, Any],
    resource: dict[str, Any],
    source_log: list[dict[str, Any]],
    max_records: int,
) -> list[dict[str, Any]]:
    url = str(resource.get("url") or "")
    entries = fetch_zip_central_directory(url, source_log, f"{source['id']}:latest_zip_range")
    relevant_entries = [
        entry
        for entry in entries
        if str(entry.get("filename", "")).lower().endswith(".zip") and is_cms_relevant_zip_member(str(entry.get("filename", "")))
    ]
    if not relevant_entries:
        return []
    rows: list[dict[str, Any]] = []
    unsupported_members: list[str] = []
    members_scanned = 0
    terms = product_terms()
    ndc_lookup = ndc_product_lookup()
    for entry in sorted(relevant_entries, key=lambda item: str(item["filename"])):
        nested_body = fetch_stored_zip_member(url, entry, source_log, f"{source['id']}:latest_zip_range")
        if nested_body is None:
            unsupported_members.append(str(entry.get("filename", "")))
            continue
        nested_hash = sha256_bytes(nested_body)
        try:
            with zipfile.ZipFile(io.BytesIO(nested_body)) as nested_archive:
                for nested_info in sorted(nested_archive.infolist(), key=lambda item: item.filename):
                    nested_member = nested_info.filename
                    if not nested_member.lower().endswith((".csv", ".txt")) or nested_member.endswith("/"):
                        continue
                    members_scanned += 1
                    full_member = f"{entry['filename']}!{nested_member}"
                    try:
                        text = decode_text(nested_archive.read(nested_info))
                    except NotImplementedError:
                        unsupported_members.append(full_member)
                        continue
                    for row_number, row in enumerate(iter_delimited_rows_from_text(text), start=1):
                        ndc = normalize_ndc(row.get("NDC") or row.get("ndc"))
                        hits = sorted(ndc_lookup.get(ndc, set())) if ndc else []
                        if not hits:
                            hits = term_hits(" ".join(str(value) for value in row.values()), terms)
                        if not hits:
                            continue
                        output = {
                            "source_id": source["id"],
                            "category": source["category"],
                            "source_status": "collected_parsed_bulk_match",
                            "catalog_resource_name": resource.get("name", ""),
                            "catalog_resource_id": resource.get("resource_id", ""),
                            "url": url,
                            "archive_member": full_member,
                            "outer_archive_member": entry["filename"],
                            "source_row_number": row_number,
                            "source_row_sha256": source_row_hash(row),
                            "source_zip_sha256": nested_hash,
                            "matched_dictionary_terms": join_values(hits),
                            "match_basis": "ndc_crosswalk" if ndc and ndc in ndc_lookup else "lexical",
                            "parser": "http_range_zipfile",
                        }
                        append_source_fields(output, row)
                        rows.append(output)
                        if len(rows) >= max_records:
                            return rows
        except zipfile.BadZipFile:
            unsupported_members.append(str(entry.get("filename", "")))
    if rows:
        return rows
    if members_scanned:
        return [
            {
                "source_id": source["id"],
                "category": source["category"],
                "source_status": "parsed_bulk_no_dictionary_matches",
                "catalog_resource_name": resource.get("name", ""),
                "catalog_resource_id": resource.get("resource_id", ""),
                "url": url,
                "members_scanned": members_scanned,
                "unsupported_members": join_values(unsupported_members[:20]),
                "note": "Recent Part D formulary nested ZIP files were parsed via HTTP range requests, but no configured GLP-1 dictionary terms were found in delimited member rows.",
            }
        ]
    return [
        {
            "source_id": source["id"],
            "category": source["category"],
            "source_status": "bulk_zip_range_member_unavailable",
            "catalog_resource_name": resource.get("name", ""),
            "catalog_resource_id": resource.get("resource_id", ""),
            "url": url,
            "members_scanned": 0,
            "unsupported_members": join_values(unsupported_members[:20]),
            "note": "Relevant Part D formulary nested ZIP members were discovered, but none could be read through HTTP range extraction.",
        }
    ]


def parse_cms_formulary_zip(
    source: dict[str, Any],
    resource: dict[str, Any],
    source_log: list[dict[str, Any]],
    max_records: int,
    sleep_seconds: float,
) -> list[dict[str, Any]]:
    url = str(resource.get("url") or "")
    range_rows = parse_cms_formulary_zip_by_range(source, resource, source_log, max_records)
    if range_rows:
        return range_rows
    if not source.get("allow_full_zip_download", False):
        return [
            {
                "source_id": source["id"],
                "category": source["category"],
                "source_status": "bulk_zip_range_unavailable",
                "catalog_resource_name": resource.get("name", ""),
                "catalog_resource_id": resource.get("resource_id", ""),
                "url": url,
                "note": "CMS formulary ZIP is large; HTTP range extraction did not produce parseable nested formulary rows, and full ZIP download is disabled for the routine deterministic refresh.",
            }
        ]
    body = get_bytes(url, source_log, f"{source['id']}:latest_zip")
    time.sleep(sleep_seconds)
    if body is None:
        return []
    rows: list[dict[str, Any]] = []
    members_scanned = 0
    unsupported_members: list[str] = []
    tar_fallback_members_read = 0
    source_zip_hash = sha256_bytes(body)
    terms = product_terms()
    ndc_lookup = ndc_product_lookup()

    def is_relevant_zip_member(member_name: str) -> bool:
        lower_name = member_name.lower()
        if "pharmacy networks" in lower_name:
            return False
        return any(
            token in lower_name
            for token in [
                "formulary",
                "beneficiary cost",
                "excluded drugs",
                "indication based",
                "partial gap",
                "plan information",
                "senior savings",
            ]
        )

    def append_matches_from_text(text: str, archive_member: str, parser: str = "zipfile") -> None:
        start_count = len(rows)
        for row_number, row in enumerate(iter_delimited_rows_from_text(text), start=1):
            ndc = normalize_ndc(row.get("NDC") or row.get("ndc"))
            hits = sorted(ndc_lookup.get(ndc, set())) if ndc else []
            if not hits:
                hits = term_hits(" ".join(str(value) for value in row.values()), terms)
            if not hits:
                continue
            output = {
                "source_id": source["id"],
                "category": source["category"],
                "source_status": "collected_parsed_bulk_match",
                "catalog_resource_name": resource.get("name", ""),
                "catalog_resource_id": resource.get("resource_id", ""),
                "url": url,
                "archive_member": archive_member,
                "source_row_number": row_number,
                "source_row_sha256": source_row_hash(row),
                "source_zip_sha256": source_zip_hash,
                "matched_dictionary_terms": join_values(hits),
                "match_basis": "ndc_crosswalk" if ndc and ndc in ndc_lookup else "lexical",
                "parser": parser,
            }
            append_source_fields(output, row)
            rows.append(output)
            if len(rows) >= max_records:
                return
        if len(rows) == start_count:
            return

    def append_matches_from_zip_payload(zip_body: bytes, parent_member: str) -> None:
        nonlocal members_scanned
        try:
            with zipfile.ZipFile(io.BytesIO(zip_body)) as nested_archive:
                for nested_info in sorted(nested_archive.infolist(), key=lambda item: item.filename):
                    nested_member = nested_info.filename
                    nested_lower = nested_member.lower()
                    if not nested_lower.endswith((".csv", ".txt")) or nested_lower.endswith("/"):
                        continue
                    members_scanned += 1
                    full_member = f"{parent_member}!{nested_member}"
                    try:
                        text = decode_text(nested_archive.read(nested_info))
                    except NotImplementedError:
                        unsupported_members.append(full_member)
                        continue
                    append_matches_from_text(text, full_member)
                    if len(rows) >= max_records:
                        return
        except zipfile.BadZipFile:
            unsupported_members.append(parent_member)

    try:
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            for info in sorted(archive.infolist(), key=lambda item: item.filename):
                member = info.filename
                lower = member.lower()
                if lower.endswith("/"):
                    continue
                if lower.endswith(".zip"):
                    if not is_relevant_zip_member(member):
                        continue
                    members_scanned += 1
                    try:
                        nested_body = archive.read(info)
                    except NotImplementedError:
                        unsupported_members.append(member)
                        continue
                    append_matches_from_zip_payload(nested_body, member)
                    if len(rows) >= max_records:
                        return rows
                    continue
                if not lower.endswith((".csv", ".txt")):
                    continue
                try:
                    text = decode_text(archive.read(member))
                except NotImplementedError:
                    unsupported_members.append(member)
                    continue
                members_scanned += 1
                append_matches_from_text(text, member)
                if len(rows) >= max_records:
                    return rows
    except zipfile.BadZipFile:
        return [
            {
                "source_id": source["id"],
                "category": source["category"],
                "source_status": "bulk_zip_unreadable",
                "catalog_resource_name": resource.get("name", ""),
                "url": url,
                "source_zip_sha256": source_zip_hash,
            }
        ]
    if unsupported_members:
        for member, member_body in extract_zip_members_with_tar(body).items():
            if member not in unsupported_members:
                continue
            tar_fallback_members_read += 1
            text = decode_text(member_body)
            append_matches_from_text(text, member, parser="tar_fallback")
            if len(rows) >= max_records:
                return rows
    if tar_fallback_members_read and not rows:
        return [
            {
                "source_id": source["id"],
                "category": source["category"],
                "source_status": "parsed_bulk_no_dictionary_matches",
                "catalog_resource_name": resource.get("name", ""),
                "catalog_resource_id": resource.get("resource_id", ""),
                "url": url,
                "members_scanned": members_scanned,
                "tar_fallback_members_read": tar_fallback_members_read,
                "source_zip_sha256": source_zip_hash,
                "note": "Latest Part D formulary ZIP was downloaded and parsed with tar fallback, but no configured GLP-1 dictionary terms were found in delimited member rows.",
            }
        ]
    if members_scanned and unsupported_members and members_scanned == len(unsupported_members):
        return [
            {
                "source_id": source["id"],
                "category": source["category"],
                "source_status": "bulk_zip_unsupported_compression",
                "catalog_resource_name": resource.get("name", ""),
                "catalog_resource_id": resource.get("resource_id", ""),
                "url": url,
                "members_scanned": members_scanned,
                "unsupported_members": join_values(unsupported_members[:20]),
                "source_zip_sha256": source_zip_hash,
                "note": "ZIP was downloaded and hashed, but all delimited member files used compression unsupported by Python zipfile in this environment.",
            }
        ]
    if rows:
        return rows
    return [
        {
            "source_id": source["id"],
            "category": source["category"],
            "source_status": "parsed_bulk_no_dictionary_matches",
            "catalog_resource_name": resource.get("name", ""),
            "catalog_resource_id": resource.get("resource_id", ""),
            "url": url,
            "members_scanned": members_scanned,
            "source_zip_sha256": source_zip_hash,
            "note": "Latest Part D formulary ZIP was downloaded and parsed, but no configured GLP-1 dictionary terms were found in delimited member rows.",
        }
    ]


def extract_links_from_html(body: bytes, base_url: str) -> list[str]:
    text = body.decode("utf-8", errors="replace")
    hrefs = re.findall(r"href=[\"']([^\"']+)[\"']", text, flags=re.IGNORECASE)
    links: list[str] = []
    for href in hrefs:
        href = html.unescape(href)
        if href.startswith("#") or href.lower().startswith(("mailto:", "javascript:")):
            continue
        links.append(urllib.parse.urljoin(base_url, href))
    return links


def collect_faers_resources(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    api_rows = collect_openfda_faers_counts(source, source_log, max_records, sleep_seconds)
    if api_rows:
        return api_rows
    url = source["base_url"]
    body = get_bytes(url, source_log, f"{source['id']}:landing_page")
    time.sleep(sleep_seconds)
    if body is None:
        return public_catalog_rows(source)
    rows: list[dict[str, Any]] = []
    for link in extract_links_from_html(body, url):
        lower = link.lower()
        if not (lower.endswith(".zip") or "faers" in lower or "ascii" in lower):
            continue
        rows.append(
            {
                "source_id": source["id"],
                "category": source["category"],
                "name": link.rsplit("/", 1)[-1],
                "url": link,
                "format": "zip_or_page",
                "source_status": "discovered_bulk_resource",
            }
        )
        if len(rows) >= max_records:
            break
    return rows or public_catalog_rows(source)


def collect_openfda_faers_counts(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    api_url = source.get("openfda_api_url", "https://api.fda.gov/drug/event.json")
    rows: list[dict[str, Any]] = []
    queries = source.get("queries") or product_query_terms()
    for query in queries:
        params = {
            "search": f'patient.drug.medicinalproduct:"{query}"',
            "count": "patient.reaction.reactionmeddrapt.exact",
            "limit": str(min(max_records, 100)),
        }
        url = f"{api_url}?{urllib.parse.urlencode(params)}"
        data = get_json(url, source_log, f"{source['id']}:openfda_reaction_counts:{query}")
        time.sleep(sleep_seconds)
        results = (data or {}).get("results") or []
        for result in results:
            rows.append(
                {
                    "source_id": source["id"],
                    "category": source["category"],
                    "source_status": "collected_openfda_faers_count",
                    "query": query,
                    "reaction_meddra_pt": result.get("term"),
                    "report_count": result.get("count"),
                    "count_field": "patient.reaction.reactionmeddrapt.exact",
                    "url": url,
                    "note": "FAERS/openFDA spontaneous adverse-event report counts are reporting signals, not incidence or causality.",
                }
            )
    return rows


def collect_fda_drug_enforcement(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    api_url = source["base_url"]
    for query in source.get("queries") or product_query_terms():
        params = {
            "search": query,
            "limit": str(min(max_records, 100)),
        }
        url = f"{api_url}?{urllib.parse.urlencode(params)}"
        data = get_json(url, source_log, f"{source['id']}:openfda_enforcement:{query}")
        time.sleep(sleep_seconds)
        for result in (data or {}).get("results") or []:
            recall_number = result.get("recall_number") or ""
            event_id = result.get("event_id") or ""
            key = recall_number or event_id or source_row_hash(result)
            if key in seen:
                continue
            seen.add(key)
            openfda = result.get("openfda") or {}
            row = {
                "source_id": source["id"],
                "category": source["category"],
                "source_status": "collected_openfda_enforcement",
                "query": query,
                "recall_number": recall_number,
                "event_id": event_id,
                "status": result.get("status"),
                "classification": result.get("classification"),
                "recall_initiation_date": result.get("recall_initiation_date"),
                "report_date": result.get("report_date"),
                "termination_date": result.get("termination_date"),
                "recalling_firm": result.get("recalling_firm"),
                "reason_for_recall": result.get("reason_for_recall"),
                "product_description": result.get("product_description"),
                "distribution_pattern": result.get("distribution_pattern"),
                "brand_name": join_values(openfda.get("brand_name")),
                "generic_name": join_values(openfda.get("generic_name")),
                "manufacturer_name": join_values(openfda.get("manufacturer_name")),
                "url": url,
                "note": "openFDA drug enforcement records are recall/enforcement signals and require review before inferring manufacturing or supply risk.",
            }
            rows.append(row)
            if len(rows) >= max_records * max(1, len(source.get("queries", []))):
                break
    return rows or public_catalog_rows(source)


def collect_public_pricing_opendata_extract(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not CORE_MATCHES.exists():
        return public_catalog_rows(source)
    wanted = set(source.get("source_dataset_ids", []))
    with CORE_MATCHES.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            dataset_id = row.get("dataset_id", "")
            if dataset_id not in wanted:
                continue
            output = {
                "source_id": source["id"],
                "category": source["category"],
                "source_status": "collected_from_opendata_refresh",
                "source_dataset_id": dataset_id,
                "canonical_product": row.get("canonical_product", ""),
                "match_term": row.get("match_term", ""),
                "match_field": row.get("match_field", ""),
                "source_url": row.get("source_url", ""),
                "source_record_id": row.get("source_record_id", ""),
                "source_response_sha256": row.get("source_response_sha256", ""),
                "source_updated_at": row.get("source_updated_at", ""),
                "pricing_context_note": "Public pricing proxy only; does not represent commercial net price, rebates, or realized gross-to-net.",
            }
            for field in [
                "as_of_date",
                "effective_date",
                "nadac_per_unit",
                "pricing_unit",
                "pharmacy_type_indicator",
                "brand_name",
                "generic_name",
                "product_name",
                "wac_increase_date",
                "price",
                "unit_price",
                "package_price",
                "drug_name",
                "active_ingredient",
                "year",
                "quarter",
            ]:
                if row.get(field):
                    output[field] = row.get(field)
            rows.append(output)
            if len(rows) >= max_records:
                break
    source_log.append(
        {
            "purpose": f"{source['id']}:generated_extract",
            "url": str(CORE_MATCHES.relative_to(ROOT)),
            "retrieved_at": utc_now(),
            "status": "ok",
            "bytes": CORE_MATCHES.stat().st_size,
            "response_sha256": sha256_file(CORE_MATCHES),
        }
    )
    return rows or public_catalog_rows(source)


def collect_state_medicaid_pdl_public_registry(
    source: dict[str, Any],
    source_log: list[dict[str, Any]],
    max_records: int,
    sleep_seconds: float,
) -> list[dict[str, Any]]:
    if not STATE_MEDICAID_PDL_CONFIG.exists():
        return public_catalog_rows(source)
    registry = read_json(STATE_MEDICAID_PDL_CONFIG)
    terms = product_terms()
    rows: list[dict[str, Any]] = []
    for entry in registry.get("states", [])[:max_records]:
        url = entry.get("url", "")
        body = get_bytes(url, source_log, f"{source['id']}:{entry.get('state', '')}", timeout=60) if url else None
        time.sleep(sleep_seconds)
        row = {
            "source_id": source["id"],
            "category": source["category"],
            "state": entry.get("state", ""),
            "program": entry.get("program", ""),
            "source_owner": entry.get("source_owner", ""),
            "document_type": entry.get("document_type", ""),
            "url": url,
            "registry_sha256": sha256_file(STATE_MEDICAID_PDL_CONFIG),
            "source_status": "registry_url_error" if body is None else "registry_page_fetched",
            "note": "Public state Medicaid PDL pages are fragmented; fetched pages provide source hashes and lexical triage, not final product-level preferred-status attribution.",
        }
        if body is not None:
            text = strip_html_text(decode_text(body))
            links = extract_links_from_html(body, url)
            hits = term_hits(text, terms)
            row.update(
                {
                    "page_sha256": sha256_bytes(body),
                    "page_bytes": len(body),
                    "matched_dictionary_terms": join_values(hits),
                    "evidence_snippet": evidence_snippet(text, hits),
                    "discovered_document_links": join_values([link for link in links if link.lower().endswith((".pdf", ".xls", ".xlsx", ".csv"))][:20]),
                }
            )
        rows.append(row)
    return rows or public_catalog_rows(source)


def collect_patentsview(source: dict[str, Any], source_log: list[dict[str, Any]], max_records: int, sleep_seconds: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    api_failure_rows: list[dict[str, Any]] = []
    endpoints = [
        source.get("query_url", "https://search.patentsview.org/api/v1/patent/"),
    ]
    fields = [
        "patent_id",
        "patent_number",
        "patent_title",
        "patent_date",
        "patent_abstract",
        "assignees.assignee_organization",
        "inventors.inventor_first_name",
        "inventors.inventor_last_name",
    ]
    for query in source.get("queries", []):
        data = None
        url = ""
        for endpoint in endpoints:
            if not endpoint:
                continue
            q = {"_or": [{"_text_any": {"patent_title": query}}, {"_text_any": {"patent_abstract": query}}]}
            params = {
                "q": json.dumps(q, separators=(",", ":")),
                "f": json.dumps(fields, separators=(",", ":")),
            "o": json.dumps({"size": min(max_records, 100), "per_page": min(max_records, 100)}, separators=(",", ":")),
            }
            url = f"{endpoint}?{urllib.parse.urlencode(params)}"
            data = get_json(url, source_log, f"patentsview_uspto:{query}")
            time.sleep(sleep_seconds)
            if data is not None:
                break
        if data is None:
            api_failure_rows.append(
                {
                    "source_id": source["id"],
                    "category": source["category"],
                    "query": query,
                    "url": url,
                    "source_status": "api_response_unparsed",
                    "note": "PatentsView endpoint responded but did not return parseable JSON in this run.",
                }
            )
            continue
        for patent in (data or {}).get("patents", []):
            patent_number = patent.get("patent_number") or patent.get("patent_id")
            if not patent_number or patent_number in seen:
                continue
            seen.add(patent_number)
            assignees = patent.get("assignees") or []
            inventors = patent.get("inventors") or []
            rows.append(
                {
                    "source_id": source["id"],
                    "category": source["category"],
                    "query": query,
                    "patent_number": patent_number,
                    "title": patent.get("patent_title"),
                    "patent_date": patent.get("patent_date"),
                    "abstract": patent.get("patent_abstract"),
                    "assignees": join_values([item.get("assignee_organization") for item in assignees if item.get("assignee_organization")]),
                    "inventors": join_values(
                        [
                            " ".join(part for part in [item.get("inventor_first_name"), item.get("inventor_last_name")] if part)
                            for item in inventors
                        ]
                    ),
                    "url": f"https://patents.justia.com/patent/{patent_number}",
                    "source_status": "collected",
                }
            )
    if rows:
        return rows
    fallback_rows: list[dict[str, Any]] = []
    for resource in source.get("bulk_fallback_resources", []):
        fallback_rows.append(
            {
                "source_id": source["id"],
                "category": source["category"],
                "dataset": resource.get("dataset"),
                "name": resource.get("name"),
                "url": resource.get("url"),
                "source_status": "collected_bulk_fallback",
                "note": "PatentSearch API did not return parseable patent records; official USPTO ODP PatentsView bulk fallback resource captured for deterministic downstream ingestion.",
                "api_attempts": len(api_failure_rows),
            }
        )
    return fallback_rows or api_failure_rows or public_catalog_rows(source)


def public_catalog_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source_id": source["id"],
            "category": source["category"],
            "status": source["status"],
            "base_url": source.get("base_url"),
            "documentation_url": source.get("documentation_url"),
            "refresh_cadence": source.get("refresh_cadence"),
            "ci_use": source.get("ci_use"),
            "collection_note": source.get("collection_note", ""),
            "source_status": "cataloged_for_ingestion",
        }
    ]


def build_source_inventory(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in config.get("public_collectors", []):
        rows.append(
            {
                "source_id": source["id"],
                "source_type": "public",
                "category": source["category"],
                "status": source["status"],
                "refresh_cadence": source.get("refresh_cadence"),
                "base_url": source.get("base_url"),
                "documentation_url": source.get("documentation_url"),
                "ci_use": source.get("ci_use"),
            }
        )
    for source in config.get("gated_ingestion_specs", []):
        rows.append(
            {
                "source_id": source["id"],
                "source_type": "gated",
                "category": source["category"],
                "status": source["status"],
                "refresh_cadence": source.get("minimum_refresh_cadence"),
                "base_url": "",
                "documentation_url": "",
                "ci_use": source.get("ci_use"),
            }
        )
    return rows


def build_gated_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in config.get("gated_ingestion_specs", []):
        rows.append(
            {
                "source_id": source["id"],
                "category": source["category"],
                "status": source["status"],
                "example_sources": join_values(source.get("example_sources")),
                "ci_use": source.get("ci_use"),
                "required_fields": join_values(source.get("required_fields")),
                "minimum_refresh_cadence": source.get("minimum_refresh_cadence"),
            }
        )
    return rows


def write_gated_templates(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in config.get("gated_ingestion_specs", []):
        fields = list(source.get("required_fields", []))
        path = TEMPLATES / f"{source['id']}.csv"
        write_template_csv(path, fields)
        rows.append(
            {
                "source_id": source["id"],
                "template_path": str(path.relative_to(ROOT)),
                "required_fields": join_values(fields),
                "sha256": sha256_file(path),
            }
        )
    return rows


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def validate_manual_inputs(config: dict[str, Any], terms: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in config.get("gated_ingestion_specs", []):
        required = list(source.get("required_fields", []))
        path = MANUAL_INPUTS / f"{source['id']}.csv"
        if not path.exists():
            rows.append(
                {
                    "source_id": source["id"],
                    "category": source["category"],
                    "input_path": str(path.relative_to(ROOT)),
                    "status": "missing_input",
                    "rows": 0,
                    "missing_fields": "",
                    "matched_dictionary_terms": "",
                    "sha256": "",
                }
            )
            continue
        fields, input_rows = read_csv_rows(path)
        missing = [field for field in required if field not in fields]
        matched_terms = sorted(
            {
                term
                for row in input_rows
                for term in term_hits(" ".join(str(value) for value in row.values()), terms)
            }
        )
        rows.append(
            {
                "source_id": source["id"],
                "category": source["category"],
                "input_path": str(path.relative_to(ROOT)),
                "status": "schema_error" if missing else "validated",
                "rows": len(input_rows),
                "missing_fields": join_values(missing),
                "matched_dictionary_terms": join_values(matched_terms),
                "sha256": sha256_file(path),
            }
        )
    return rows


def normalize_manual_input_records(config: dict[str, Any], terms: list[str]) -> dict[str, list[dict[str, Any]]]:
    normalized: dict[str, list[dict[str, Any]]] = {}
    for source in config.get("gated_ingestion_specs", []):
        source_id = source["id"]
        required = list(source.get("required_fields", []))
        path = MANUAL_INPUTS / f"{source_id}.csv"
        output_rows: list[dict[str, Any]] = []
        if path.exists():
            fields, input_rows = read_csv_rows(path)
            missing = [field for field in required if field not in fields]
            if not missing:
                file_hash = sha256_file(path)
                for index, row in enumerate(input_rows, start=1):
                    output_rows.append(
                        {
                            "source_id": source_id,
                            "category": source["category"],
                            "source_status": "validated_manual_input",
                            "input_path": str(path.relative_to(ROOT)),
                            "input_sha256": file_hash,
                            "input_row_number": index,
                            "matched_dictionary_terms": join_values(term_hits(" ".join(str(value) for value in row.values()), terms)),
                            **row,
                        }
                    )
            else:
                output_rows.append(
                    {
                        "source_id": source_id,
                        "category": source["category"],
                        "source_status": "missing_required_fields",
                        "input_path": str(path.relative_to(ROOT)),
                        "missing_fields": join_values(missing),
                    }
                )
        if not output_rows:
            output_rows.append(
                {
                    "source_id": source_id,
                    "category": source["category"],
                    "source_status": "template_only",
                    "template_path": str((TEMPLATES / f"{source_id}.csv").relative_to(ROOT)),
                }
            )
        normalized[source_id] = output_rows
    return normalized


def summarize_records(records: dict[str, list[dict[str, Any]]], source_log: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_id, source_rows in sorted(records.items()):
        statuses = {row.get("source_status") for row in source_rows}
        status = "collected" if source_rows else "cataloged_or_no_records"
        if statuses == {"cataloged_for_ingestion"}:
            status = "cataloged_for_ingestion"
        elif statuses == {"discovered_bulk_resource"}:
            status = "discovered_bulk_resources"
        elif statuses == {"collected_parsed_bulk_match"}:
            status = "collected_parsed_bulk_matches"
        elif statuses == {"parsed_bulk_no_dictionary_matches"}:
            status = "parsed_bulk_no_dictionary_matches"
        elif statuses == {"bulk_zip_unsupported_compression"}:
            status = "bulk_zip_unsupported_compression"
        elif statuses == {"bulk_zip_range_unavailable"}:
            status = "bulk_zip_range_unavailable"
        elif statuses == {"bulk_zip_range_member_unavailable"}:
            status = "bulk_zip_range_member_unavailable"
        elif statuses == {"collected_openfda_faers_count"}:
            status = "collected_openfda_faers_counts"
        elif statuses == {"collected_openfda_enforcement"}:
            status = "collected_openfda_enforcement"
        elif statuses == {"collected_from_opendata_refresh"}:
            status = "collected_from_opendata_refresh"
        elif statuses == {"registry_page_fetched"}:
            status = "registry_pages_fetched"
        elif statuses == {"collected_with_text"}:
            status = "collected_with_text"
        elif statuses == {"collected_bulk_fallback"}:
            status = "collected_bulk_fallback"
        elif statuses == {"api_response_unparsed"}:
            status = "api_response_unparsed"
        rows.append(
            {
                "source_id": source_id,
                "records": len(source_rows),
                "status": status,
                "unique_urls": len({row.get("url") for row in source_rows if row.get("url")}),
            }
        )
    logged = {}
    for entry in source_log:
        key = entry["purpose"].split(":", 1)[0]
        logged.setdefault(key, {"requests": 0, "errors": 0})
        logged[key]["requests"] += 1
        if entry.get("status") != "ok":
            logged[key]["errors"] += 1
    for key, values in sorted(logged.items()):
        rows.append(
            {
                "source_id": f"{key}_requests",
                "records": values["requests"],
                "status": "request_errors" if values["errors"] else "requests_ok",
                "unique_urls": "",
            }
        )
    return rows


def write_brief(path: Path, run_at: str, records: dict[str, list[dict[str, Any]]], config: dict[str, Any]) -> None:
    lines = [
        "# High-Value GLP-1 Obesity CI Additions",
        "",
        f"Run timestamp: {run_at}",
        "",
        "## Public Collectors",
        "",
    ]
    for source in config.get("public_collectors", []):
        rows = records.get(source["id"], [])
        statuses = {row.get("source_status") for row in rows}
        if statuses == {"cataloged_for_ingestion"}:
            status_label = "cataloged for ingestion"
        elif statuses == {"discovered_bulk_resource"}:
            status_label = "bulk resources discovered"
        elif statuses == {"collected_parsed_bulk_match"}:
            status_label = "parsed bulk matches collected"
        elif statuses == {"parsed_bulk_no_dictionary_matches"}:
            status_label = "latest bulk file parsed; no dictionary matches"
        elif statuses == {"bulk_zip_unsupported_compression"}:
            status_label = "latest bulk file hashed; compression unsupported"
        elif statuses == {"bulk_zip_range_member_unavailable"}:
            status_label = "latest bulk nested files discovered; range member extraction unavailable"
        elif statuses == {"bulk_zip_range_unavailable"}:
            status_label = "latest bulk file range extraction unavailable"
        elif statuses == {"collected_openfda_faers_count"}:
            status_label = "openFDA FAERS reaction counts collected"
        elif statuses == {"collected_openfda_enforcement"}:
            status_label = "openFDA drug enforcement records collected"
        elif statuses == {"collected_from_opendata_refresh"}:
            status_label = "public pricing proxy rows extracted from OpenData refresh"
        elif statuses == {"registry_page_fetched"}:
            status_label = "state Medicaid public registry pages fetched"
        elif statuses == {"collected_with_text"}:
            status_label = "metadata and filing text snippets collected"
        elif statuses == {"collected_bulk_fallback"}:
            status_label = "bulk fallback resources captured"
        elif statuses == {"api_response_unparsed"}:
            status_label = "API endpoint checked; response unparsed"
        else:
            status_label = "collected"
        lines.append(f"- `{source['id']}` ({source['category']}): {len(rows)} rows, {status_label}; {source['ci_use']}")
    lines.extend(["", "## Gated / Manual Ingestion Specs", ""])
    for source in config.get("gated_ingestion_specs", []):
        lines.append(f"- `{source['id']}` ({source['category']}): {source['status']}; template `input_templates/high_value_ci/{source['id']}.csv`; required fields: {join_values(source.get('required_fields'))}.")
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "- Public API records are collected evidence and can be refreshed deterministically.",
            "- Gated sources are configured as ingestion requirements only; they are not represented as collected until licensed or client-provided files are added.",
            "- Outputs remain hypothesis-generating and require analyst adjudication before external use.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-network", action="store_true", help="Write inventory and gated specs without public API calls.")
    parser.add_argument("--max-records", type=int, default=100, help="Maximum records per query/company.")
    parser.add_argument("--sleep-seconds", type=float, default=0.2, help="Polite delay between public API requests.")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    run_at = utc_now()
    config = read_json(CONFIG)
    source_log: list[dict[str, Any]] = []
    terms = product_terms()
    records: dict[str, list[dict[str, Any]]] = {}
    template_rows = write_gated_templates(config)
    manual_validation_rows = validate_manual_inputs(config, terms)
    manual_records = normalize_manual_input_records(config, terms)

    for source in config.get("public_collectors", []):
        source_id = source["id"]
        if args.skip_network:
            records[source_id] = public_catalog_rows(source)
            continue
        if source_id == "clinicaltrials_gov":
            rows = collect_clinicaltrials(source, source_log, args.max_records, args.sleep_seconds)
        elif source_id == "pubmed_literature":
            rows = collect_pubmed(source, source_log, args.max_records, args.sleep_seconds)
        elif source_id == "dailymed_labels":
            rows = collect_dailymed(source, source_log, args.max_records, args.sleep_seconds)
        elif source_id == "sec_edgar_submissions":
            rows = collect_sec(source, source_log, args.max_records, args.sleep_seconds)
        elif source_id == "public_pricing_opendata_extract":
            rows = collect_public_pricing_opendata_extract(source, source_log, args.max_records)
        elif source_id == "fda_drug_enforcement":
            rows = collect_fda_drug_enforcement(source, source_log, args.max_records, args.sleep_seconds)
        elif source_id == "state_medicaid_pdl_public_registry":
            rows = collect_state_medicaid_pdl_public_registry(source, source_log, args.max_records, args.sleep_seconds)
        elif source_id == "cms_partd_formulary_puf":
            rows = collect_data_gov_resources(source, source_log, args.max_records, args.sleep_seconds)
        elif source_id == "fda_faers_quarterly":
            rows = collect_faers_resources(source, source_log, args.max_records, args.sleep_seconds)
        elif source_id == "patentsview_uspto":
            rows = collect_patentsview(source, source_log, args.max_records, args.sleep_seconds)
        else:
            rows = public_catalog_rows(source)
        for row in rows:
            row["matched_dictionary_terms"] = join_values(term_hits(" ".join(str(value) for value in row.values()), terms))
        records[source_id] = rows

    write_json(OUT / "source_log.json", source_log)
    write_csv(OUT / "source_inventory.csv", build_source_inventory(config))
    write_csv(OUT / "gated_ingestion_requirements.csv", build_gated_rows(config))
    write_csv(OUT / "gated_ingestion_templates.csv", template_rows)
    write_csv(OUT / "manual_ingest_validation.csv", manual_validation_rows)
    write_csv(OUT / "collection_summary.csv", summarize_records(records, source_log))
    for source_id, rows in records.items():
        write_json(OUT / f"{source_id}.json", rows)
        write_csv(OUT / f"{source_id}.csv", rows)
    for source_id, rows in manual_records.items():
        write_json(OUT / f"gated_{source_id}.json", rows)
        write_csv(OUT / f"gated_{source_id}.csv", rows)
    write_brief(OUT / "high_value_signal_brief.md", run_at, records, config)

    outputs = sorted(path for path in OUT.glob("*") if path.is_file())
    script_paths = [
        ROOT / "scripts" / "refresh_high_value_glp1_ci.py",
        ROOT / "scripts" / "verify_high_value_outputs.py",
    ]
    manifest = {
        "run_at": run_at,
        "script": str(Path(__file__).relative_to(ROOT)),
        "script_sha256": sha256_file(Path(__file__)),
        "scripts": {
            path.stem: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
            }
            for path in script_paths
            if path.exists()
        },
        "python_version": sys.version,
        "skip_network": args.skip_network,
        "max_records": args.max_records,
        "sleep_seconds": args.sleep_seconds,
        "config": {
            "high_value_ci_sources": {
                "path": str(CONFIG.relative_to(ROOT)),
                "sha256": sha256_file(CONFIG),
                "version": config.get("version"),
            },
            "glp1_product_dictionary": {
                "path": str(PRODUCT_CONFIG.relative_to(ROOT)),
                "sha256": sha256_file(PRODUCT_CONFIG),
            },
            "glp1_asset_dictionary": {
                "path": str(ASSET_CONFIG.relative_to(ROOT)),
                "sha256": sha256_file(ASSET_CONFIG),
                "version": read_json(ASSET_CONFIG).get("version") if ASSET_CONFIG.exists() else None,
            },
            "state_medicaid_pdl_sources": {
                "path": str(STATE_MEDICAID_PDL_CONFIG.relative_to(ROOT)),
                "sha256": sha256_file(STATE_MEDICAID_PDL_CONFIG) if STATE_MEDICAID_PDL_CONFIG.exists() else "",
                "version": read_json(STATE_MEDICAID_PDL_CONFIG).get("version") if STATE_MEDICAID_PDL_CONFIG.exists() else None,
            },
            "core_glp1_product_matches": {
                "path": str(CORE_MATCHES.relative_to(ROOT)),
                "sha256": sha256_file(CORE_MATCHES) if CORE_MATCHES.exists() else "",
                "exists": CORE_MATCHES.exists(),
            },
            "high_value_methodology": {
                "path": str(HIGH_VALUE_METHODOLOGY.relative_to(ROOT)),
                "sha256": sha256_file(HIGH_VALUE_METHODOLOGY) if HIGH_VALUE_METHODOLOGY.exists() else "",
                "exists": HIGH_VALUE_METHODOLOGY.exists(),
            },
            "manual_inputs_dir": {
                "path": str(MANUAL_INPUTS.relative_to(ROOT)),
                "exists": MANUAL_INPUTS.exists(),
            },
            "input_templates_dir": {
                "path": str(TEMPLATES.relative_to(ROOT)),
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
    print(f"Wrote high-value GLP-1 CI outputs to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
