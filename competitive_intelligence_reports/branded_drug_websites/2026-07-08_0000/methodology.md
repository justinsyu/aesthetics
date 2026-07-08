# U.S. Branded Prescription Drug HCP/Patient Website Inventory Methodology

Run date: 2026-07-08

## Scope

Included:

- U.S. marketed branded prescription drugs.
- Biologics, biosimilars, rare-disease drugs, specialty products, and cell/gene therapies when present in the FDA/NDC prescription-drug universe.

Excluded or moved to review:

- Vaccines.
- OTC-only products.
- Diagnostics and device-only products.
- Generic-style or private-label products where brand status was unclear.
- HCP seed rows that could not be matched to the high-confidence FDA/NDC branded prescription-drug universe.

## Source Hierarchy

1. FDA NDC Directory text download, preserved as `raw/ndctext.zip`.
2. FDA Orange Book data file, preserved as `raw/orange_book.zip`.
3. Existing broad HCP drug website seed from `outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv`.
4. Existing HCP promotional-message extraction from `outputs/hcp_promotional_message_audit/hcp_site_promotional_messages.csv`.
5. Existing patient retained-row examples from `competitive_intelligence_reports/patient_pro_not_in_label/2026-07-05_patient_site_pro_label_audit/sources/patient-retained-rows.json`.
6. Deterministic patient-site probes derived from known HCP URL patterns.

## Universe Construction

The builder reads FDA NDC `product.txt` and retains rows where:

- `PRODUCTTYPENAME` is `HUMAN PRESCRIPTION DRUG`.
- `ENDMARKETINGDATE` is blank or after 2026-07-08.
- The proprietary name is present.
- Vaccine, diagnostic, test, reagent, and common non-drug patterns are absent.

Rows are normalized to one brand/generic pair. A row is high-confidence when:

- NDC marketing category or application number indicates NDA, BLA, or NDA authorized generic, or
- It matches an Orange Book NDA `RX` trade-name/ingredient pair.

Generic-like or private-label rows without high-confidence brand support are retained in `working/branded_rx_universe_medium_review.csv` rather than promoted into the master inventory.

## Website Classification

HCP site discovery used the existing 681-row HCP site audit as a seed. The builder:

- Matched seed brand names to FDA normalized brand keys.
- Inferred missing or mismatched seed brands from URL and promotional-message text when those signals matched a high-confidence FDA brand slug.
- Moved unmatched, vaccine, diagnostic, or otherwise out-of-scope seed rows to `hcp_seed_unmatched_or_out_of_scope_review.csv`.

Patient site discovery used deterministic probes derived from scoped HCP URLs, such as:

- `hcp.brand.com` to `www.brand.com`
- `brandhcp.com` to `brand.com`
- `/hcp` paths to the site root
- common `/patient`, `/patients`, and `/patient-support` paths

A patient URL was retained only when patient-facing terms were visible and the brand was visible or the final URL host contained the brand slug. This is not a full search-engine crawl.

## Output Files

- `master_branded_drug_website_inventory.csv`: One row per high-confidence FDA-backed branded prescription brand/generic pair.
- `hcp_branded_drug_websites.csv`: In-scope HCP branded drug website URLs matched to the FDA-backed universe.
- `patient_branded_drug_websites.csv`: Patient URLs found by deterministic probe and matched to the FDA-backed universe.
- `manual_review_queue.csv`: Brands needing search-engine/manual follow-up for missing HCP or patient evidence.
- `hcp_seed_unmatched_or_out_of_scope_review.csv`: Inherited HCP seed rows excluded from the scoped HCP deliverable or needing review.
- `patient_seed_unmatched_or_out_of_scope_review.csv`: Patient retained-row seed examples that did not match the scoped FDA universe.
- `working/branded_rx_universe_medium_review.csv`: Candidate branded prescription products with uncertain brand status.

## Run Counts

- FDA NDC product rows read: 115,038.
- Active human prescription NDC rows retained before brand/generic aggregation: 11,148.
- Unique candidate brand/generic pairs: 4,124.
- High-confidence brand/generic pairs in master inventory: 2,426.
- Medium-confidence brand/generic pairs retained for review: 1,698.
- HCP seed rows assessed: 681.
- In-scope HCP seed rows retained: 556.
- Unique in-scope HCP URLs retained: 551.
- HCP seed rows moved to unmatched/out-of-scope review: 125.
- Patient candidate URLs probed: 2,653.
- Unique in-scope patient URLs retained: 184.
- Master classification counts:
  - Both HCP and patient found: 185.
  - HCP found, patient not found by seed/probe: 343.
  - No branded site found in seed/probe: 1,898.
- Manual review queue rows: 2,241.

## Limitations

This run creates a comprehensive FDA-backed product universe and a broad known-HCP-site inventory from the existing 681-row seed, but unresolved brands have not all been manually searched. The `manual_review_queue.csv` file is the next worklist for converting this into a fully hand-verified all-brand inventory.

FDA NDC data are labeler-submitted marketed-listing records. They support product-existence and marketed-listing status for this workflow, but they do not prove that a branded HCP or patient website exists.

