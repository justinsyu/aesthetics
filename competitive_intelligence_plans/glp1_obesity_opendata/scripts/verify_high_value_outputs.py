#!/usr/bin/env python3
"""Verify high-value GLP-1 obesity CI refresh outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated_data" / "high_value_ci"
CONFIG = ROOT / "config" / "high_value_ci_sources.json"
TEMPLATES = ROOT / "input_templates" / "high_value_ci"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle).fieldnames or [])


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest() -> list[str]:
    manifest = read_json(OUT / "run_manifest.json")
    required_config_keys = {"high_value_methodology", "core_glp1_product_matches", "state_medicaid_pdl_sources"}
    missing_keys = required_config_keys - set(manifest.get("config", {}))
    if missing_keys:
        raise AssertionError(f"manifest missing high-value traceability keys: {sorted(missing_keys)}")
    for item in manifest["config"].values():
        if not item.get("sha256"):
            continue
        path = ROOT / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise AssertionError(f"config hash mismatch: {item['path']}")
    for item in manifest["outputs"]:
        path = ROOT / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise AssertionError(f"output hash mismatch: {item['path']}")
    script_path = ROOT / manifest["script"]
    if sha256_file(script_path) != manifest["script_sha256"]:
        raise AssertionError("script hash mismatch")
    for name, item in manifest.get("scripts", {}).items():
        path = ROOT / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise AssertionError(f"script hash mismatch: {name}")
    return ["manifest hashes match current high-value CI files"]


def verify_source_inventory() -> list[str]:
    config = read_json(CONFIG)
    inventory = read_csv(OUT / "source_inventory.csv")
    gated = read_csv(OUT / "gated_ingestion_requirements.csv")
    templates = read_csv(OUT / "gated_ingestion_templates.csv")
    validation = read_csv(OUT / "manual_ingest_validation.csv")
    public_ids = {source["id"] for source in config["public_collectors"]}
    gated_ids = {source["id"] for source in config["gated_ingestion_specs"]}
    inventory_ids = {row["source_id"] for row in inventory}
    gated_output_ids = {row["source_id"] for row in gated}
    missing = (public_ids | gated_ids) - inventory_ids
    if missing:
        raise AssertionError(f"source inventory missing ids: {sorted(missing)}")
    if gated_ids - gated_output_ids:
        raise AssertionError(f"gated requirements missing ids: {sorted(gated_ids - gated_output_ids)}")
    template_ids = {row["source_id"] for row in templates}
    validation_ids = {row["source_id"] for row in validation}
    if gated_ids - template_ids:
        raise AssertionError(f"gated templates missing ids: {sorted(gated_ids - template_ids)}")
    if gated_ids - validation_ids:
        raise AssertionError(f"manual validation missing ids: {sorted(gated_ids - validation_ids)}")
    for source in config["gated_ingestion_specs"]:
        path = TEMPLATES / f"{source['id']}.csv"
        if not path.exists():
            raise AssertionError(f"missing gated input template: {path}")
        header = csv_header(path)
        missing_fields = [field for field in source["required_fields"] if field not in header]
        if missing_fields:
            raise AssertionError(f"template {source['id']} missing fields: {missing_fields}")
        gated_csv = OUT / f"gated_{source['id']}.csv"
        gated_json = OUT / f"gated_{source['id']}.json"
        if not gated_csv.exists() or not gated_json.exists():
            raise AssertionError(f"missing normalized gated output for {source['id']}")
        rows = read_csv(gated_csv)
        if not rows:
            raise AssertionError(f"empty normalized gated output for {source['id']}")
        header = csv_header(gated_csv)
        for field in ["source_id", "category", "source_status"]:
            if field not in header:
                raise AssertionError(f"normalized gated output missing {field}: {source['id']}")
        validated = [row for row in validation if row["source_id"] == source["id"] and row["status"] == "validated"]
        if validated:
            for field in ["input_sha256", "input_row_number", "matched_dictionary_terms"]:
                if field not in header:
                    raise AssertionError(f"validated gated output missing {field}: {source['id']}")
            expected = sum(int(row["rows"]) for row in validated)
            observed = sum(1 for row in rows if row.get("source_status") == "validated_manual_input")
            if observed != expected:
                raise AssertionError(f"validated gated row-count mismatch for {source['id']}: expected {expected}, observed {observed}")
    required_categories = {
        "clinical_pipeline",
        "formulary_access",
        "claims_rx_demand",
        "pricing_gross_to_net",
        "safety_tolerability",
        "supply_manufacturing",
        "scientific_kol",
        "ip_lifecycle",
        "company_disclosures",
    }
    observed = {row["category"] for row in inventory}
    if required_categories - observed:
        raise AssertionError(f"missing high-value categories: {sorted(required_categories - observed)}")
    return ["source inventory and gated templates/normalized outputs cover all requested high-value CI categories"]


def verify_public_outputs() -> list[str]:
    manifest = read_json(OUT / "run_manifest.json")
    config = read_json(CONFIG)
    findings: list[str] = []
    collected_or_discovered_required = {
        "cms_partd_formulary_puf",
        "fda_faers_quarterly",
        "patentsview_uspto",
        "public_pricing_opendata_extract",
        "fda_drug_enforcement",
        "state_medicaid_pdl_public_registry",
    }
    for source in config["public_collectors"]:
        csv_path = OUT / f"{source['id']}.csv"
        json_path = OUT / f"{source['id']}.json"
        if not csv_path.exists() or not json_path.exists():
            raise AssertionError(f"missing public collector output for {source['id']}")
        rows = read_csv(csv_path)
        if not rows:
            raise AssertionError(f"empty public collector output for {source['id']}")
        if manifest.get("skip_network") and not all(row.get("source_status") == "cataloged_for_ingestion" for row in rows):
            raise AssertionError(f"{source['id']} should be catalog-only in skip-network mode")
        if not manifest.get("skip_network") and source["id"] in collected_or_discovered_required:
            statuses = {row.get("source_status") for row in rows}
            if statuses == {"cataloged_for_ingestion"}:
                raise AssertionError(f"{source['id']} regressed to catalog-only output")
        if source["id"] == "cms_partd_formulary_puf" and "url" not in csv_header(csv_path):
            raise AssertionError("cms_partd_formulary_puf missing URL field")
        if source["id"] == "fda_faers_quarterly" and "url" not in csv_header(csv_path):
            raise AssertionError("fda_faers_quarterly missing URL field")
        if source["id"] == "sec_edgar_submissions":
            statuses = {row.get("source_status") for row in rows}
            if "collected_with_text" not in statuses:
                raise AssertionError("sec_edgar_submissions lacks fetched filing text evidence")
            header = csv_header(csv_path)
            for field in ["filing_text_sha256", "filing_text_bytes", "filing_text_snippet"]:
                if field not in header:
                    raise AssertionError(f"sec_edgar_submissions missing {field} field")
        if source["id"] == "public_pricing_opendata_extract":
            statuses = {row.get("source_status") for row in rows}
            if "collected_from_opendata_refresh" not in statuses:
                raise AssertionError("public_pricing_opendata_extract lacks OpenData-derived pricing rows")
            observed_datasets = {row.get("source_dataset_id") for row in rows}
            required_dataset = set(source.get("source_dataset_ids", []))
            if not (observed_datasets & required_dataset):
                raise AssertionError("public_pricing_opendata_extract has no configured source dataset rows")
            for field in ["source_dataset_id", "canonical_product", "source_response_sha256", "pricing_context_note"]:
                if field not in csv_header(csv_path):
                    raise AssertionError(f"public_pricing_opendata_extract missing {field} field")
        if source["id"] == "fda_drug_enforcement":
            statuses = {row.get("source_status") for row in rows}
            if "collected_openfda_enforcement" not in statuses:
                raise AssertionError("fda_drug_enforcement lacks openFDA enforcement rows")
            header = csv_header(csv_path)
            for field in ["recall_number", "classification", "status", "reason_for_recall", "product_description", "url"]:
                if field not in header:
                    raise AssertionError(f"fda_drug_enforcement missing {field} field")
        if source["id"] == "state_medicaid_pdl_public_registry":
            statuses = {row.get("source_status") for row in rows}
            if "registry_page_fetched" not in statuses:
                raise AssertionError("state_medicaid_pdl_public_registry lacks fetched public registry pages")
            header = csv_header(csv_path)
            for field in ["state", "program", "url", "page_sha256", "registry_sha256", "note"]:
                if field not in header:
                    raise AssertionError(f"state_medicaid_pdl_public_registry missing {field} field")
        if not manifest.get("skip_network") and source["id"] == "cms_partd_formulary_puf":
            statuses = {row.get("source_status") for row in rows}
            allowed = {
                "collected_parsed_bulk_match",
                "parsed_bulk_no_dictionary_matches",
                "bulk_zip_unsupported_compression",
                "bulk_zip_range_unavailable",
                "bulk_zip_range_member_unavailable",
                "discovered_bulk_resource",
            }
            if not (statuses & allowed):
                raise AssertionError(f"cms_partd_formulary_puf lacks parsed, hashed, or discovered bulk evidence: {sorted(statuses)}")
            if "collected_parsed_bulk_match" in statuses:
                header = csv_header(csv_path)
                parsed_rows = [row for row in rows if row.get("source_status") == "collected_parsed_bulk_match"]
                for field in [
                    "field_ndc",
                    "field_tier_level_value",
                    "field_prior_authorization_yn",
                    "field_step_therapy_yn",
                    "field_quantity_limit_yn",
                    "field_quantity_limit_amount",
                    "field_quantity_limit_days",
                    "match_basis",
                ]:
                    if field not in header:
                        raise AssertionError(f"cms_partd_formulary_puf parsed output missing {field} field")
                    if any(not row.get(field) for row in parsed_rows):
                        raise AssertionError(f"cms_partd_formulary_puf parsed output has blank {field} values")
            if statuses == {"bulk_zip_unsupported_compression"} and "source_zip_sha256" not in csv_header(csv_path):
                raise AssertionError("cms_partd_formulary_puf unsupported-compression row missing source_zip_sha256")
        if not manifest.get("skip_network") and source["id"] == "fda_faers_quarterly":
            statuses = {row.get("source_status") for row in rows}
            if "collected_openfda_faers_count" not in statuses:
                raise AssertionError("fda_faers_quarterly lacks openFDA reaction-count output")
            header = csv_header(csv_path)
            for field in ["query", "reaction_meddra_pt", "report_count", "count_field"]:
                if field not in header:
                    raise AssertionError(f"fda_faers_quarterly missing {field} field")
        if source["id"] == "patentsview_uspto" and "source_status" not in csv_header(csv_path):
            raise AssertionError("patentsview_uspto missing source_status field")
        if not manifest.get("skip_network") and source["id"] == "patentsview_uspto":
            statuses = {row.get("source_status") for row in rows}
            if not (statuses & {"collected", "collected_bulk_fallback"}):
                raise AssertionError("patentsview_uspto lacks parsed patent records or official USPTO bulk fallback resources")
        findings.append(f"{source['id']}: {len(rows)} rows")
    return findings


def patentsview_bulk_fallback_present() -> bool:
    path = OUT / "patentsview_uspto.csv"
    if not path.exists():
        return False
    return any(row.get("source_status") == "collected_bulk_fallback" for row in read_csv(path))


def verify_traceability() -> list[str]:
    manifest = read_json(OUT / "run_manifest.json")
    source_log = read_json(OUT / "source_log.json")
    if not manifest.get("skip_network"):
        if not source_log:
            raise AssertionError("networked high-value run has empty source log")
        errors = [entry for entry in source_log if entry.get("status") != "ok"]
        if errors and patentsview_bulk_fallback_present():
            allowed_errors = [
                entry
                for entry in errors
                if str(entry.get("purpose", "")).startswith("patentsview_uspto:") and entry.get("url")
            ]
            errors = [entry for entry in errors if entry not in allowed_errors]
        if errors:
            enforcement_rows = read_csv(OUT / "fda_drug_enforcement.csv") if (OUT / "fda_drug_enforcement.csv").exists() else []
            if any(row.get("source_status") == "collected_openfda_enforcement" for row in enforcement_rows):
                allowed_errors = [
                    entry
                    for entry in errors
                    if str(entry.get("purpose", "")).startswith("fda_drug_enforcement:") and entry.get("url")
                ]
                errors = [entry for entry in errors if entry not in allowed_errors]
        if errors:
            raise AssertionError(f"source log contains request errors: {len(errors)}")
        for entry in source_log:
            if entry.get("status") != "ok":
                continue
            has_response_evidence = entry.get("response_sha256") or entry.get("content_length")
            if not entry.get("url") or not has_response_evidence:
                raise AssertionError(f"source log entry lacks URL/hash: {entry.get('purpose')}")
        if patentsview_bulk_fallback_present():
            return ["source log contains URL and SHA-256 evidence for successful requests; PatentsView API errors are traceable and backed by official USPTO bulk fallback resources"]
        return ["source log contains URL and SHA-256 evidence for public API requests"]
    return ["skip-network run correctly produced catalog/spec artifacts without public API source log entries"]


def main() -> int:
    required = [
        OUT / "run_manifest.json",
        OUT / "source_inventory.csv",
        OUT / "gated_ingestion_requirements.csv",
        OUT / "gated_ingestion_templates.csv",
        OUT / "manual_ingest_validation.csv",
        OUT / "collection_summary.csv",
        OUT / "high_value_signal_brief.md",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise AssertionError(f"missing high-value outputs: {missing}")
    findings: list[str] = []
    findings.extend(verify_manifest())
    findings.extend(verify_source_inventory())
    findings.extend(verify_public_outputs())
    findings.extend(verify_traceability())
    print("High-value CI verification passed.")
    for finding in findings:
        print(f"- {finding}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
