import csv
import json
from collections import Counter
from pathlib import Path

import build_branded_drug_website_inventory as base
from build_inventory_from_fda_and_existing_seeds import read_csv, write_csv


RUN_DIR = Path(__file__).resolve().parent


def main():
    master_path = RUN_DIR / "master_branded_drug_website_inventory_manual_reviewed.csv"
    hcp_path = RUN_DIR / "hcp_branded_drug_websites_manual_reviewed.csv"
    patient_path = RUN_DIR / "patient_branded_drug_websites_manual_reviewed.csv"
    search_path = RUN_DIR / "manual_review_search_results.csv"
    overrides_path = RUN_DIR / "manual_review_curated_overrides.csv"

    master = read_csv(master_path)
    hcp = read_csv(hcp_path)
    patient = read_csv(patient_path)
    search = read_csv(search_path)
    overrides = read_csv(overrides_path)

    master_by_brand = {base.norm_key(row["brand_name"]): row for row in master}
    search_by_brand = {base.norm_key(row["brand_name"]): row for row in search}
    hcp_urls = {row["hcp_url"].rstrip("/").lower() for row in hcp}
    patient_urls = {row["patient_url"].rstrip("/").lower() for row in patient}

    applied = []
    for override in overrides:
        key = base.norm_key(override["brand_name"])
        master_row = master_by_brand.get(key)
        if not master_row:
            continue
        search_row = search_by_brand.get(key)
        if override["audience"] == "hcp":
            if not master_row["hcp_website_url"]:
                master_row["hcp_website_url"] = override["url"]
                master_row["hcp_website_count_for_brand"] = "1"
                if override["url"].rstrip("/").lower() not in hcp_urls:
                    hcp.append(
                        {
                            "brand_name": master_row["brand_name"],
                            "original_seed_brand_name": "",
                            "brand_metadata_method": override["method"],
                            "generic_name": master_row["generic_name"],
                            "company": master_row["manufacturer_or_labeler"],
                            "hcp_url": override["url"],
                            "hcp_url_original": override["url"],
                            "hcp_access_status": "curated_qa_override",
                            "hcp_retrieved_at": "2026-07-08",
                            "rwe_assessment": "not assessed",
                            "rwe_signals": "",
                            "promotional_message_verbatim": "",
                            "message_theme": "",
                            "fda_exact_brand_match_status": "matched_to_master_inventory",
                            "fda_source_confidence": master_row["fda_source_confidence"],
                            "fda_application_numbers": master_row["application_numbers"],
                            "scope_status": "in_scope_fda_matched_rx_brand",
                            "scope_exclusion_or_review_reason": override["notes"],
                        }
                    )
                    hcp_urls.add(override["url"].rstrip("/").lower())
                if search_row:
                    search_row["new_hcp_url"] = override["url"]
                    search_row["new_hcp_evidence"] = override["evidence"]
                    search_row["new_hcp_confidence"] = override["confidence"]
                    search_row["new_hcp_method"] = override["method"]
                    search_row["new_hcp_fetch_status"] = "curated_qa_override"
            applied.append(override)
        elif override["audience"] == "patient":
            if not master_row["patient_website_url"]:
                master_row["patient_website_url"] = override["url"]
                master_row["patient_website_count_for_brand"] = "1"
                if override["url"].rstrip("/").lower() not in patient_urls:
                    patient.append(
                        {
                            "brand_name": master_row["brand_name"],
                            "generic_name": master_row["generic_name"],
                            "company": master_row["manufacturer_or_labeler"],
                            "patient_url": override["url"],
                            "patient_audience_evidence": override["evidence"],
                            "patient_discovery_method": override["method"],
                        }
                    )
                    patient_urls.add(override["url"].rstrip("/").lower())
                if search_row:
                    search_row["new_patient_url"] = override["url"]
                    search_row["new_patient_evidence"] = override["evidence"]
                    search_row["new_patient_confidence"] = override["confidence"]
                    search_row["new_patient_method"] = override["method"]
                    search_row["new_patient_fetch_status"] = "curated_qa_override"
            applied.append(override)
        has_hcp = bool(master_row["hcp_website_url"])
        has_patient = bool(master_row["patient_website_url"])
        if has_hcp and has_patient:
            master_row["website_classification"] = "both_hcp_and_patient_found"
            master_row["confidence"] = "high"
            master_row["uncertainty_notes"] = ""
        elif has_hcp:
            master_row["website_classification"] = "hcp_found_patient_not_found"
            master_row["confidence"] = "partial_manual_review"
            master_row["uncertainty_notes"] = "HCP URL found; patient URL not found by manual review pass."
        elif has_patient:
            master_row["website_classification"] = "patient_found_hcp_not_found"
            master_row["confidence"] = "partial_manual_review"
            master_row["uncertainty_notes"] = "Patient URL found; HCP URL not found by manual review pass."

    for row in search:
        if row["new_hcp_url"] or row["new_patient_url"]:
            row["review_status"] = "new_url_found"
            if "curated_qa_override" not in row.get("notes", ""):
                row["notes"] = (row.get("notes", "") + " Curated QA override applied.").strip()

    unresolved = [
        row
        for row in master
        if row["website_classification"]
        in {
            "hcp_found_patient_not_found",
            "patient_found_hcp_not_found",
            "no_branded_site_found_after_manual_review_pass",
        }
    ]

    write_csv(master_path, master)
    write_csv(hcp_path, hcp)
    write_csv(patient_path, patient)
    write_csv(search_path, search)
    write_csv(RUN_DIR / "unresolved_after_manual_review.csv", unresolved)

    summary = json.loads((RUN_DIR / "manual_review_summary.json").read_text(encoding="utf-8"))
    summary["curated_qa_overrides_applied"] = len(applied)
    summary["new_hcp_urls_found"] = sum(1 for row in search if row.get("new_hcp_url"))
    summary["new_patient_urls_found"] = sum(1 for row in search if row.get("new_patient_url"))
    summary["review_status_counts"] = dict(Counter(row["review_status"] for row in search))
    summary["manual_reviewed_master_classification_counts"] = dict(
        Counter(row["website_classification"] for row in master)
    )
    summary["manual_reviewed_hcp_unique_urls"] = len(
        {row["hcp_url"].rstrip("/").lower() for row in hcp}
    )
    summary["manual_reviewed_patient_unique_urls"] = len(
        {row["patient_url"].rstrip("/").lower() for row in patient}
    )
    summary["unresolved_after_manual_review_rows"] = len(unresolved)
    (RUN_DIR / "manual_review_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
