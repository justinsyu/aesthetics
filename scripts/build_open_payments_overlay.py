#!/usr/bin/env python3
"""Build NPI/Open Payments enrichment files for the provider map.

The locator source files mix practice rows and clinician rows. This script
extracts clinician-like names where the locator exposes them, resolves NPIs
conservatively through the NPPES API, and joins 2024 CMS Open Payments summary
totals by NPI.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "docs" / "assets" / "data"
OUT_DIR = DATA_DIR / "open_payments"
NPPES_CACHE_PATH = ROOT / "outputs" / "open_payments_enrichment_cache" / "nppes_lookup_cache.json"

OPEN_PAYMENTS_SUMMARY_URL = (
    "https://download.cms.gov/openpayments/SMRY_RPTS_P01232026_01102026/"
    "PBLCTN_SMRY_BY_CR_BY_NTR_OF_PYMT_PGYR2024_P01232026_01102026.csv"
)

SOURCE_FILES = {
    "botox": DATA_DIR / "botox_cosmetic_alle_providers.csv",
    "dysport": DATA_DIR / "dysport_usa_providers.csv",
    "xeomin": DATA_DIR / "xeomin_aesthetic_providers.csv",
}

PRODUCT_LABELS = {
    "botox": "BOTOX Cosmetic",
    "dysport": "Dysport",
    "xeomin": "Xeomin",
}

CREDENTIAL_RE = re.compile(
    r"\b("
    r"MD|M\.D\.|DO|D\.O\.|DDS|DMD|NP|APRN|ARNP|DNP|RNP|FNP|FNP-C|"
    r"PA-C|PA|RN|BSN|MSN|CANS|PMHNP-S|PMHNP|LA|OTHER"
    r")\b\.?",
    re.IGNORECASE,
)

NON_NAME_RE = re.compile(r"[^A-Za-z .'\-]")


def clean(value: object) -> str:
    return str(value or "").strip()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_zip(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    return digits[:5]


def normalize_city(value: str) -> str:
    return normalize_space(value).upper()


def normalize_name(value: str) -> str:
    value = re.sub(r"\([^)]*\)", " ", value or "")
    value = CREDENTIAL_RE.sub(" ", value)
    value = NON_NAME_RE.sub(" ", value)
    value = normalize_space(value).strip(" ,")
    if value.isupper():
        value = value.title()
    return value


def split_name(full_name: str) -> tuple[str, str] | None:
    parts = [part for part in normalize_name(full_name).split(" ") if part]
    if len(parts) < 2:
        return None
    return parts[0], parts[-1]


def split_dysport_specialists(value: str) -> list[str]:
    value = clean(value)
    if not value:
        return []
    parts = re.split(r"\s*(?:;|\||/|\band\b)\s*", value)
    return [part.strip() for part in parts if part.strip()]


def parse_xeomin_providers(value: str) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, dict):
        return []
    return [clean(name) for name in parsed.values() if clean(name)]


def locator_id(product_key: str, row: dict[str, str], index: int) -> str:
    source_id = row.get("id") or row.get("account_id") or row.get("provider_organization_id") or str(index)
    return f"{product_key}-{source_id}"


def row_location(product_key: str, row: dict[str, str], index: int) -> dict[str, str]:
    if product_key == "botox":
        practice = clean(row.get("display_name"))
        address = " ".join([clean(row.get("address1")), clean(row.get("address2"))]).strip()
    elif product_key == "dysport":
        practice = clean(row.get("practice_name")) or clean(row.get("specialists"))
        address = " ".join([clean(row.get("address")), clean(row.get("address_optional"))]).strip()
    else:
        practice = clean(row.get("name")) or clean(row.get("legal_account_name"))
        address = clean(row.get("street")) or clean(row.get("address_text"))

    return {
        "locator_record_id": locator_id(product_key, row, index),
        "product_key": product_key,
        "product": PRODUCT_LABELS[product_key],
        "practice_name": practice,
        "address": address,
        "city": clean(row.get("city")),
        "state": clean(row.get("state")).upper(),
        "zip": clean(row.get("zip")),
        "latitude": clean(row.get("latitude")),
        "longitude": clean(row.get("longitude")),
    }


def extract_candidates() -> tuple[list[dict[str, str]], dict[str, dict[str, object]], Counter]:
    candidates: list[dict[str, str]] = []
    locations: dict[str, dict[str, object]] = {}
    stats: Counter = Counter()

    for product_key, path in SOURCE_FILES.items():
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for index, row in enumerate(reader):
                location = row_location(product_key, row, index)
                locations[location["locator_record_id"]] = {
                    **location,
                    "candidate_count": 0,
                    "matched_provider_count": 0,
                    "paid_provider_count": 0,
                    "payment_total_2024": 0.0,
                    "payment_transactions_2024": 0,
                    "providers": [],
                }

                raw_names: list[str] = []
                if product_key == "dysport":
                    raw_names = split_dysport_specialists(row.get("specialists", ""))
                    if not raw_names and (row.get("first_name") or row.get("last_name")):
                        raw_names = [f"{clean(row.get('first_name'))} {clean(row.get('last_name'))}".strip()]
                elif product_key == "xeomin":
                    raw_names = parse_xeomin_providers(row.get("providers_json", ""))

                if not raw_names:
                    stats[(product_key, "no_clinician")] += 1
                    continue

                for raw_name in raw_names:
                    provider_name = normalize_name(raw_name)
                    name_parts = split_name(provider_name)
                    if not name_parts:
                        stats[(product_key, "dropped_name")] += 1
                        continue

                    first_name, last_name = name_parts
                    candidate = {
                        **location,
                        "raw_provider_name": raw_name,
                        "provider_name": provider_name,
                        "provider_first_name": first_name,
                        "provider_last_name": last_name,
                    }
                    candidates.append(candidate)
                    locations[location["locator_record_id"]]["candidate_count"] += 1
                    stats[(product_key, "clinician_candidate")] += 1

    return candidates, locations, stats


def load_nppes_cache() -> dict[str, object]:
    if not NPPES_CACHE_PATH.exists():
        return {}
    return json.loads(NPPES_CACHE_PATH.read_text(encoding="utf-8"))


def save_nppes_cache(cache: dict[str, object]) -> None:
    NPPES_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    NPPES_CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def nppes_key(first_name: str, last_name: str, state: str) -> str:
    return "|".join([first_name.upper(), last_name.upper(), state.upper()])


def fetch_nppes(first_name: str, last_name: str, state: str, retries: int = 3) -> dict[str, object]:
    params = {
        "version": "2.1",
        "enumeration_type": "NPI-1",
        "first_name": first_name,
        "last_name": last_name,
        "state": state,
        "limit": "25",
    }
    url = "https://npiregistry.cms.hhs.gov/api/?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - cache error context for auditability
            if attempt == retries - 1:
                return {"error": str(exc), "result_count": 0, "results": []}
            time.sleep(0.8 * (attempt + 1))
    return {"result_count": 0, "results": []}


def build_nppes_cache(candidates: list[dict[str, str]], max_workers: int, max_lookups: int | None, skip: bool) -> dict[str, object]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = load_nppes_cache()
    if skip:
        return cache
    lookup_items = {}
    for row in candidates:
        if not row["state"]:
            continue
        key = nppes_key(row["provider_first_name"], row["provider_last_name"], row["state"])
        lookup_items[key] = (row["provider_first_name"], row["provider_last_name"], row["state"])

    pending = [
        (key, values)
        for key, values in lookup_items.items()
        if key not in cache or (isinstance(cache.get(key), dict) and cache[key].get("error"))
    ]
    if max_lookups is not None:
        pending = pending[:max_lookups]

    if not pending:
        return cache

    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_nppes, first, last, state): key
            for key, (first, last, state) in pending
        }
        for future in as_completed(futures):
            key = futures[future]
            cache[key] = future.result()
            completed += 1
            if completed % 250 == 0:
                save_nppes_cache(cache)
                print(f"NPPES lookups completed: {completed}/{len(pending)}")

    save_nppes_cache(cache)
    return cache


def result_name(result: dict[str, object]) -> str:
    basic = result.get("basic") or {}
    return normalize_space(
        " ".join(
            [
                clean(basic.get("first_name")),
                clean(basic.get("middle_name")),
                clean(basic.get("last_name")),
            ]
        )
    )


def result_taxonomy(result: dict[str, object]) -> str:
    for taxonomy in result.get("taxonomies") or []:
        if taxonomy.get("primary"):
            return clean(taxonomy.get("desc"))
    taxonomies = result.get("taxonomies") or []
    return clean(taxonomies[0].get("desc")) if taxonomies else ""


def result_addresses(result: dict[str, object]) -> list[dict[str, str]]:
    addresses = []
    for address in result.get("addresses") or []:
        addresses.append(
            {
                "city": normalize_city(address.get("city", "")),
                "state": clean(address.get("state")).upper(),
                "zip5": normalize_zip(address.get("postal_code", "")),
            }
        )
    return addresses


def choose_nppes_match(row: dict[str, str], response: dict[str, object]) -> dict[str, object]:
    results = response.get("results") or []
    if not results:
        return {
            "npi": "",
            "npi_match_status": "no_nppes_match",
            "npi_match_confidence": "none",
            "npi_match_basis": "",
            "nppes_provider_name": "",
            "nppes_primary_taxonomy": "",
        }

    city = normalize_city(row["city"])
    zip5 = normalize_zip(row["zip"])
    scored = []
    for result in results:
        addresses = result_addresses(result)
        city_match = bool(city and any(address["city"] == city for address in addresses))
        zip_match = bool(zip5 and any(address["zip5"] == zip5 for address in addresses))
        score = 1 + (2 if zip_match else 0) + (1 if city_match else 0)
        scored.append((score, zip_match, city_match, result))

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, zip_match, city_match, best = scored[0]
    ties = [item for item in scored if item[0] == best_score]

    if len(results) == 1:
        confidence = "high" if (zip_match or city_match) else "medium"
        status = "matched"
    elif len(ties) == 1 and (zip_match or city_match):
        confidence = "high" if zip_match else "medium"
        status = "matched"
    else:
        return {
            "npi": "",
            "npi_match_status": "ambiguous_nppes_match",
            "npi_match_confidence": "none",
            "npi_match_basis": f"{len(results)} NPPES results for name/state",
            "nppes_provider_name": "",
            "nppes_primary_taxonomy": "",
        }

    basis = ["first/last/state"]
    if city_match:
        basis.append("city")
    if zip_match:
        basis.append("zip")

    return {
        "npi": clean(best.get("number")),
        "npi_match_status": status,
        "npi_match_confidence": confidence,
        "npi_match_basis": "+".join(basis),
        "nppes_provider_name": result_name(best),
        "nppes_primary_taxonomy": result_taxonomy(best),
    }


def open_payments_name_key(first_name: str, last_name: str) -> str:
    return "|".join([normalize_name(first_name).upper(), normalize_name(last_name).upper()])


def stream_open_payments() -> tuple[dict[str, dict[str, object]], dict[str, set[str]]]:
    payments: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "open_payments_name": "",
            "open_payments_2024_total_amount": 0.0,
            "open_payments_2024_transaction_count": 0,
            "open_payments_2024_nature_codes": Counter(),
        }
    )
    name_index: dict[str, set[str]] = defaultdict(set)

    with urllib.request.urlopen(OPEN_PAYMENTS_SUMMARY_URL, timeout=120) as response:
        text_stream = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
        reader = csv.DictReader(text_stream)
        for row in reader:
            npi = clean(row.get("Covered_Recipient_NPI"))
            if not npi:
                continue
            first = clean(row.get("Covered_Recipient_Profile_First_Name"))
            middle = clean(row.get("Covered_Recipient_Profile_Middle_Name"))
            last = clean(row.get("Covered_Recipient_Profile_Last_Name"))
            name_key = open_payments_name_key(first, last)
            if name_key != "|":
                name_index[name_key].add(npi)
            if not payments[npi]["open_payments_name"]:
                payments[npi]["open_payments_name"] = normalize_space(" ".join([first, middle, last]))
            amount = float(row.get("Total_Amount") or 0)
            txns = int(float(row.get("Number_of_Transaction") or 0))
            nature = clean(row.get("Nature_Of_Payment_Type_Code")) or "unknown"
            payments[npi]["open_payments_2024_total_amount"] += amount
            payments[npi]["open_payments_2024_transaction_count"] += txns
            payments[npi]["open_payments_2024_nature_codes"][nature] += amount

    for payment in payments.values():
        nature_codes = payment.pop("open_payments_2024_nature_codes")
        payment["open_payments_2024_top_nature_codes"] = [
            {"code": code, "amount": round(amount, 2)}
            for code, amount in nature_codes.most_common(5)
        ]
        payment["open_payments_2024_total_amount"] = round(payment["open_payments_2024_total_amount"], 2)

    return dict(payments), name_index


def choose_open_payments_name_match(row: dict[str, str], name_index: dict[str, set[str]]) -> dict[str, object]:
    key = open_payments_name_key(row["provider_first_name"], row["provider_last_name"])
    npis = sorted(name_index.get(key, []))
    if not npis:
        return {
            "npi": "",
            "npi_match_status": "no_open_payments_name_match",
            "npi_match_confidence": "none",
            "npi_match_basis": "",
            "nppes_provider_name": "",
            "nppes_primary_taxonomy": "",
        }
    if len(npis) > 1:
        return {
            "npi": "",
            "npi_match_status": "ambiguous_open_payments_name_match",
            "npi_match_confidence": "none",
            "npi_match_basis": f"{len(npis)} Open Payments NPIs for first/last name",
            "nppes_provider_name": "",
            "nppes_primary_taxonomy": "",
        }
    return {
        "npi": npis[0],
        "npi_match_status": "matched_open_payments_unique_name",
        "npi_match_confidence": "medium",
        "npi_match_basis": "open_payments_first/last_unique",
        "nppes_provider_name": "",
        "nppes_primary_taxonomy": "",
    }


def write_outputs(
    candidates: list[dict[str, str]],
    locations: dict[str, dict[str, object]],
    cache: dict[str, object],
) -> Counter:
    print("Streaming CMS Open Payments summary for NPI/name index")
    payments, open_payments_name_index = stream_open_payments()
    rows = []
    stats = Counter()

    for row in candidates:
        key = nppes_key(row["provider_first_name"], row["provider_last_name"], row["state"])
        match = choose_nppes_match(row, cache.get(key, {"results": []}))
        if not match["npi"]:
            match = choose_open_payments_name_match(row, open_payments_name_index)
        if match["npi"]:
            stats["npi_matched_candidate_rows"] += 1
        else:
            stats[match["npi_match_status"]] += 1
        rows.append({**row, **match})

    for row in rows:
        npi = row.get("npi", "")
        payment = payments.get(
            npi,
            {
                "open_payments_2024_total_amount": 0.0,
                "open_payments_2024_transaction_count": 0,
                "open_payments_2024_top_nature_codes": [],
            },
        )
        row.update(
            {
                "open_payments_2024_total_amount": payment["open_payments_2024_total_amount"],
                "open_payments_2024_transaction_count": payment["open_payments_2024_transaction_count"],
                "open_payments_2024_top_nature_codes": json.dumps(payment["open_payments_2024_top_nature_codes"], separators=(",", ":")),
            }
        )
        if row["open_payments_2024_total_amount"]:
            stats["paid_candidate_rows"] += 1

        location = locations[row["locator_record_id"]]
        location["providers"].append(
            {
                "name": row["provider_name"],
                "rawName": row["raw_provider_name"],
                "npi": npi,
                "npiStatus": row["npi_match_status"],
                "npiConfidence": row["npi_match_confidence"],
                "matchBasis": row["npi_match_basis"],
                "nppesName": row["nppes_provider_name"],
                "openPaymentsName": payment.get("open_payments_name", ""),
                "taxonomy": row["nppes_primary_taxonomy"],
                "paymentTotal2024": row["open_payments_2024_total_amount"],
                "paymentTransactions2024": row["open_payments_2024_transaction_count"],
                "topNatureCodes2024": json.loads(row["open_payments_2024_top_nature_codes"]),
            }
        )
        if npi:
            location["matched_provider_count"] += 1
        if row["open_payments_2024_total_amount"]:
            location["paid_provider_count"] += 1
            location["payment_total_2024"] += row["open_payments_2024_total_amount"]
            location["payment_transactions_2024"] += row["open_payments_2024_transaction_count"]

    for location in locations.values():
        location["payment_total_2024"] = round(float(location["payment_total_2024"]), 2)
        location["providers"] = sorted(
            location["providers"],
            key=lambda item: (item["paymentTotal2024"], item["name"]),
            reverse=True,
        )
        if location["payment_total_2024"]:
            stats["paid_locations"] += 1
        if location["candidate_count"]:
            stats["locations_with_clinician_candidates"] += 1

    row_csv = OUT_DIR / "provider_npi_open_payments_matches.csv"
    fieldnames = [
        "locator_record_id",
        "product_key",
        "product",
        "practice_name",
        "raw_provider_name",
        "provider_name",
        "provider_first_name",
        "provider_last_name",
        "npi",
        "npi_match_status",
        "npi_match_confidence",
        "npi_match_basis",
        "nppes_provider_name",
        "nppes_primary_taxonomy",
        "open_payments_2024_total_amount",
        "open_payments_2024_transaction_count",
        "open_payments_2024_top_nature_codes",
        "address",
        "city",
        "state",
        "zip",
        "latitude",
        "longitude",
    ]
    with row_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    overlay_json = OUT_DIR / "provider_open_payments_overlay.json"
    compact_locations = {
        key: value
        for key, value in locations.items()
        if value["candidate_count"] or value["payment_total_2024"]
    }
    payload = {
        "metadata": {
            "generatedBy": "scripts/build_open_payments_overlay.py",
            "paymentYear": 2024,
            "openPaymentsSource": OPEN_PAYMENTS_SUMMARY_URL,
            "npiSource": "https://npiregistry.cms.hhs.gov/api/",
            "matchNotes": [
                "BOTOX Cosmetic locator rows do not expose individual clinician names in the current extract, so they are retained as practice locations without NPI matching.",
                "Dysport and Xeomin clinician names are matched to NPPES by first name, last name, and state when available, with higher confidence when city or ZIP also matches.",
                "When NPPES is unavailable or ambiguous, unique exact first/last-name matches in the Open Payments covered-recipient summary are used as medium-confidence NPI matches for paid providers.",
                "Open Payments totals are 2024 CMS general-payment summary totals grouped by covered recipient and nature of payment.",
            ],
            "stats": dict(stats),
        },
        "locations": compact_locations,
    }
    overlay_json.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    stats["candidate_rows"] = len(rows)
    stats["locations_total"] = len(locations)
    stats["locations_in_overlay_json"] = len(compact_locations)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-workers", type=int, default=8)
    parser.add_argument("--max-lookups", type=int, default=None, help="Limit new NPPES API lookups for testing.")
    parser.add_argument("--skip-nppes", action="store_true", help="Do not make new NPPES API calls; use cached NPPES data and Open Payments names.")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates, locations, extraction_stats = extract_candidates()
    print("Extraction stats:", dict(extraction_stats))
    print(f"Clinician candidate rows: {len(candidates):,}")

    cache = build_nppes_cache(candidates, max_workers=args.max_workers, max_lookups=args.max_lookups, skip=args.skip_nppes)
    stats = write_outputs(candidates, locations, cache)

    summary = {
        "extraction": {str(key): value for key, value in extraction_stats.items()},
        "enrichment": dict(stats),
    }
    (OUT_DIR / "provider_open_payments_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
