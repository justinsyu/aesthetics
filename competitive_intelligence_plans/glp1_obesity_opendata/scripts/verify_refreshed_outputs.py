#!/usr/bin/env python3
"""Independent deterministic checks for regenerated GLP-1 OpenData CI outputs."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated_data"
PRODUCTS = ROOT / "config" / "glp1_product_dictionary.json"
USER_AGENT = "linkedin-posts-mac-glp1-opendata-ci-verifier/2026-05-28"

CMS_TARGETS = [
    "Ozempic",
    "Trulicity",
    "Mounjaro",
    "Wegovy",
    "Rybelsus",
    "Victoza",
    "Saxenda",
    "Bydureon",
    "Byetta",
    "Soliqua",
    "Xultophy",
    "Adlyxin",
    "Zepbound",
]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(value: Any) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"[^A-Z0-9]+", " ", text.upper())
    return re.sub(r"\s+", " ", text).strip()


def number(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(str(value).replace(",", ""))


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def source_log_entry(dataset_id: str) -> dict[str, Any]:
    for entry in read_json(OUT / "source_log.json"):
        if entry.get("purpose") == f"upstream_source:{dataset_id}":
            return entry
    raise AssertionError(f"missing upstream source log entry for {dataset_id}")


def product_brand_terms() -> dict[str, list[str]]:
    data = read_json(PRODUCTS)
    return {
        product["canonical_product"]: product.get("brand_terms", [])
        for product in data["products"]
        if product["canonical_product"] in CMS_TARGETS
    }


def verify_cms_source(dataset_id: str, product_summary: list[dict[str, str]]) -> list[str]:
    entry = source_log_entry(dataset_id)
    body = fetch(entry["url"])
    actual_hash = sha256_bytes(body)
    if actual_hash != entry["response_sha256"]:
        raise AssertionError(f"{dataset_id} source hash mismatch: {actual_hash} != {entry['response_sha256']}")

    rows = list(csv.DictReader(io.StringIO(body.decode("utf-8-sig"))))
    summary_index = {
        row["canonical_product"]: row
        for row in product_summary
        if row["dataset_id"] == dataset_id
    }
    terms_by_product = product_brand_terms()
    findings = [f"{dataset_id}: source SHA-256 matches source_log.json ({actual_hash})"]

    for product in CMS_TARGETS:
        terms = {normalize(term) for term in terms_by_product.get(product, [product])}
        matched = [
            row for row in rows
            if normalize(row.get("Mftr_Name")) == "OVERALL"
            and any(term in normalize(row.get("Brnd_Name")) for term in terms)
        ]
        latest_years = sorted(
            {
                field.rsplit("_", 1)[-1]
                for row in matched
                for field, value in row.items()
                if field.startswith("Tot_Spndng_") and str(value).strip()
            }
        )
        if not latest_years:
            if product in summary_index:
                raise AssertionError(f"{dataset_id} {product}: summary row exists but no CMS source row was found")
            findings.append(f"{dataset_id}: {product} not observed in overall brand spending rows")
            continue

        latest = latest_years[-1]
        spending = sum(number(row.get(f"Tot_Spndng_{latest}")) for row in matched)
        claims = sum(number(row.get(f"Tot_Clms_{latest}")) for row in matched)
        summary = summary_index.get(product)
        if summary is None:
            raise AssertionError(f"{dataset_id} {product}: CMS row exists but generated summary is missing")
        if str(summary["latest_year"]) != latest:
            raise AssertionError(f"{dataset_id} {product}: latest year {summary['latest_year']} != {latest}")
        if abs(number(summary["latest_year_total_spending"]) - spending) > 0.01:
            raise AssertionError(f"{dataset_id} {product}: spending mismatch")
        if abs(number(summary["latest_year_total_claims"]) - claims) > 0.01:
            raise AssertionError(f"{dataset_id} {product}: claims mismatch")
        findings.append(f"{dataset_id}: {product} {latest} spending and claims reconcile")
    return findings


def verify_fda_counts(source_coverage: list[dict[str, str]], product_summary: list[dict[str, str]]) -> list[str]:
    by_dataset = {row["dataset_id"]: row for row in source_coverage}
    expected = {
        "fda/ndc-directory": (641, 402),
        "fda/drugs-at-fda": (199, 109),
        "fda/orange-book": (257, 86),
        "fda/nme-approvals": (19, 6),
    }
    findings = []
    for dataset_id, (lexical, unique) in expected.items():
        row = by_dataset[dataset_id]
        if int(row["lexical_match_records"]) != lexical:
            raise AssertionError(f"{dataset_id}: lexical_match_records mismatch")
        if int(row["unique_matched_source_rows"]) != unique:
            raise AssertionError(f"{dataset_id}: unique_matched_source_rows mismatch")
        findings.append(f"{dataset_id}: {lexical} lexical match records / {unique} unique source rows")

    nme = by_dataset["fda/nme-approvals"]
    if nme["parser"] != "xlsx" or int(nme["rows_scanned"]) < 1300:
        raise AssertionError("fda/nme-approvals did not parse as non-empty xlsx")
    nme_products = {
        row["canonical_product"]: row
        for row in product_summary
        if row["dataset_id"] == "fda/nme-approvals"
    }
    expected_products = {"Byetta", "Victoza", "Trulicity", "Adlyxin", "Ozempic", "Mounjaro"}
    if set(nme_products) != expected_products:
        raise AssertionError(f"NME product set mismatch: {sorted(nme_products)}")
    for product in expected_products:
        if int(float(nme_products[product]["matched_source_rows"])) != 1:
            raise AssertionError(f"NME {product}: expected one unique source row")
    findings.append("fda/nme-approvals: xlsx parser found the six expected GLP-1/NME candidate rows")
    return findings


def verify_shortages(product_summary: list[dict[str, str]]) -> list[str]:
    shortage_rows = [row for row in product_summary if row["dataset_id"] == "fda/drug-shortages"]
    limited_brands = sorted(
        row["canonical_product"]
        for row in shortage_rows
        if not row["canonical_product"].startswith("ingredient:")
        and int(float(row.get("current_limited_availability_rows") or 0)) > 0
    )
    if limited_brands != ["Victoza"]:
        raise AssertionError(f"brand-level limited availability mismatch: {limited_brands}")
    by_product = {row["canonical_product"]: row for row in shortage_rows}
    saxenda = by_product["Saxenda"]
    if int(float(saxenda["current_limited_availability_rows"] or 0)) != 0 or int(float(saxenda["current_available_rows"] or 0)) != 1:
        raise AssertionError("Saxenda shortage classification is not Current / Available watch-only")
    liraglutide = by_product["ingredient:liraglutide"]
    if int(float(liraglutide["current_limited_availability_rows"] or 0)) != 0:
        raise AssertionError("ingredient:liraglutide should not be a brand-level limited-availability claim")
    return [
        "fda/drug-shortages: Victoza is the only brand-level current limited-availability signal",
        "fda/drug-shortages: Saxenda remains Current / Available watch-only",
        "fda/drug-shortages: ingredient:liraglutide remains separate from brand attribution",
    ]


def verify_delta(delta_rows: list[dict[str, str]]) -> list[str]:
    required_columns = {"period_relation", "periods_consecutive", "direction"}
    missing = required_columns - set(delta_rows[0])
    if missing:
        raise AssertionError(f"signal_delta_summary missing columns: {sorted(missing)}")
    for row in delta_rows:
        if not row["direction"].startswith("spending_"):
            raise AssertionError(f"direction is not spending-specific: {row}")
        consecutive = int(row["latest_period"]) - int(row["prior_period"]) == 1
        if boolish(row["periods_consecutive"]) != consecutive:
            raise AssertionError(f"periods_consecutive mismatch: {row}")
        expected_relation = "strict_yoy" if consecutive else "latest_vs_prior_observed"
        if row["period_relation"] != expected_relation:
            raise AssertionError(f"period_relation mismatch: {row}")
    non_consecutive = [row for row in delta_rows if row["period_relation"] == "latest_vs_prior_observed"]
    if len(non_consecutive) != 1 or non_consecutive[0]["canonical_product"] != "Saxenda":
        raise AssertionError(f"unexpected non-consecutive rows: {non_consecutive}")
    return ["signal_delta_summary: period relation and spending-specific direction fields are consistent"]


def verify_manifest() -> list[str]:
    manifest = read_json(OUT / "run_manifest.json")
    for key, item in manifest.get("scripts", {}).items():
        path = ROOT / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise AssertionError(f"manifest script hash mismatch: {key}")
    for item in manifest["config"].values():
        path = ROOT / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise AssertionError(f"manifest config hash mismatch: {item['path']}")
    for item in manifest["outputs"]:
        path = ROOT / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise AssertionError(f"manifest output hash mismatch: {item['path']}")
    return ["run_manifest: script, config, methodology, and generated output hashes match current files"]


def verify_execution_scope(source_coverage: list[dict[str, str]]) -> list[str]:
    manifest = read_json(OUT / "run_manifest.json")
    validation = read_json(OUT / "refresh_validation_report.json")
    if manifest.get("scan_all_sources"):
        not_scanned = [row["dataset_id"] for row in source_coverage if row["source_url"] and row["source_scan_status"] == "not_scanned"]
        if not_scanned:
            raise AssertionError(f"scan_all_sources run left source URLs unscanned: {not_scanned}")
        source_errors = validation.get("checks", {}).get("source_errors", 0)
        if source_errors:
            raise AssertionError(f"scan_all_sources run has source errors: {source_errors}")
        return ["execution scope: full run scanned every pinned dataset with a source URL"]
    skipped = [row["dataset_id"] for row in source_coverage if row["source_scan_status"] in {"not_scanned", "skipped_large_source"}]
    return [f"execution scope: default run; {len(skipped)} pinned sources were not scanned"]


def main() -> int:
    product_summary = read_csv(OUT / "product_signal_summary.csv")
    source_coverage = read_csv(OUT / "source_coverage_matrix.csv")
    delta_rows = read_csv(OUT / "signal_delta_summary.csv")
    findings: list[str] = []
    findings.extend(verify_cms_source("cms/part-d-spending", product_summary))
    findings.extend(verify_cms_source("cms/medicaid-spending", product_summary))
    findings.extend(verify_fda_counts(source_coverage, product_summary))
    findings.extend(verify_shortages(product_summary))
    findings.extend(verify_delta(delta_rows))
    findings.extend(verify_manifest())
    findings.extend(verify_execution_scope(source_coverage))
    print("Independent verification passed.")
    for finding in findings:
        print(f"- {finding}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
