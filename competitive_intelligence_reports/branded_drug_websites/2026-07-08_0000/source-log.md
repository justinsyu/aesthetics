# Source Log

Run date: 2026-07-08

## Primary Public Sources

- FDA National Drug Code Directory page: https://www.fda.gov/drugs/drug-approvals-and-databases/national-drug-code-directory
- FDA NDC text download used by builder: https://www.accessdata.fda.gov/cder/ndctext.zip
- FDA Orange Book Data Files page: https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files
- FDA Orange Book data download used by builder: https://www.fda.gov/media/76860/download?attachment
- FDA Purple Book downloads page reviewed for biologics/biosimilars scope context: https://purplebooksearch.fda.gov/downloads

## Local Seed Sources

- `outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv`
- `outputs/hcp_promotional_message_audit/hcp_site_promotional_messages.csv`
- `competitive_intelligence_reports/patient_pro_not_in_label/2026-07-05_patient_site_pro_label_audit/sources/patient-retained-rows.json`

## Generated Raw Files

- `raw/ndctext.zip`
- `raw/orange_book.zip`

## Generated Scripts

- `build_branded_drug_website_inventory.py`
- `build_inventory_from_fda_and_existing_seeds.py`
- `manual_review_remaining_websites.py`
- `apply_manual_review_overrides.py`
- `verify_and_merge_nonblocked_candidates.py`

## Generated Deliverables

- `master_branded_drug_website_inventory.csv`
- `hcp_branded_drug_websites.csv`
- `patient_branded_drug_websites.csv`
- `manual_review_queue.csv`
- `hcp_seed_unmatched_or_out_of_scope_review.csv`
- `patient_seed_unmatched_or_out_of_scope_review.csv`
- `working/branded_rx_universe_candidates_all.csv`
- `working/branded_rx_universe_high_confidence.csv`
- `working/branded_rx_universe_medium_review.csv`
- `run_summary.json`
- `master_branded_drug_website_inventory_manual_reviewed.csv`
- `hcp_branded_drug_websites_manual_reviewed.csv`
- `patient_branded_drug_websites_manual_reviewed.csv`
- `manual_review_search_results.csv`
- `manual_review_summary.json`
- `manual_review_addendum.md`
- `manual_review_curated_overrides.csv`
- `unresolved_after_manual_review.csv`
- `generic_like_scope_review_after_manual_review.csv`
- `audit_no_site_followup_misses.py`
- `audit_no_site_sibling_inheritance.py`
- `audit_no_site_direct_blocked_domains.py`
- `no_site_followup_findings.md`
- `no_site_followup_candidate_misses.csv`
- `no_site_followup_best_candidate_misses.csv`
- `no_site_followup_audit_status.csv`
- `no_site_followup_summary.json`
- `no_site_followup_sibling_inheritance_candidates.csv`
- `no_site_followup_sibling_inheritance_summary.json`
- `no_site_followup_direct_blocked_domain_candidates.csv`
- `no_site_followup_direct_blocked_domain_summary.json`
- `no_site_followup_probable_missed_direct_domains.csv`
- `no_site_followup_blocked_brand_domain_candidates.csv`
- `nonblocked_candidate_verification.csv`
- `nonblocked_candidate_applied_rows.csv`
- `nonblocked_candidate_merge_summary.json`
- `nonblocked_candidate_merge_addendum.md`
