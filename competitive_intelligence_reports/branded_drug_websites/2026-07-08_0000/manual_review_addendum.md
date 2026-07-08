# Manual Review Addendum

Run date: 2026-07-08

## Purpose

This addendum documents the follow-on review of the 2,241-row `manual_review_queue.csv` created by the first FDA/NDC-backed branded prescription-drug website inventory.

The review attempted to find missing HCP and patient branded drug websites using:

- Direct brand-domain probes, including common HCP, pro, patient, savings, and support URL patterns.
- Bing result review using brand + HCP, healthcare professional, prescribing information, patient, official website, support, and savings query variants.
- HTML/text audience classification for HCP and patient evidence.
- A curated QA override layer for high-profile search-visible misses identified during representative checks.

## Reviewed Outputs

Use these files as the current reviewed deliverables:

- `master_branded_drug_website_inventory_manual_reviewed.csv`
- `hcp_branded_drug_websites_manual_reviewed.csv`
- `patient_branded_drug_websites_manual_reviewed.csv`
- `manual_review_search_results.csv`
- `unresolved_after_manual_review.csv`
- `generic_like_scope_review_after_manual_review.csv`
- `manual_review_curated_overrides.csv`
- `manual_review_summary.json`

The original first-pass files remain in the folder for reproducibility.

## Results

- Manual-review input rows: 2,241.
- Rows with at least one new URL found during the review: 825.
- Rows retained as generic-like or nonbranded scope-review cases: 90.
- Rows with no new URL found by the review pass: 1,326.
- New HCP URLs found in the review pass: 567.
- New patient URLs found in the review pass: 633.
- Curated QA overrides applied: 9.

Final reviewed master classification:

- Both HCP and patient found: 683.
- HCP found, patient not found: 412.
- Patient found, HCP not found: 135.
- No branded site found after review pass: 1,196.

Reviewed unique URL files:

- HCP URLs: 1,072.
- Patient URLs: 771.
- Unresolved rows after review: 1,743.

## False-Positive Controls Added During QA

The initial automated review over-accepted some direct HCP candidate domains for generic-like rows. The final reviewed outputs use stricter controls:

- Direct candidate URLs must fetch successfully unless added through the explicit curated override file.
- URL shape alone is not sufficient for a site to be retained.
- HCP pages require visible HCP/professional evidence, or visible brand text plus an HCP/professional URL signal.
- Patient pages require patient-facing evidence or an explicit curated official patient-site search result.
- Parked or domain-for-sale signals are excluded.
- Generic-like rows where proprietary and generic/proper names overlap are moved into `generic_like_scope_review_after_manual_review.csv` instead of promoted as branded website hits.

Representative QA examples:

- `AIRSUPRA`, `ACCRUFER`, `ELIQUIS`, `Ozempic`, `WEGOVY`, `neffy`, `Myfembree`, and `MYQORZO` resolved to credible HCP and/or patient URLs.
- `ACD-A` and `Acetaminophen` were not promoted as branded site hits after the stricter controls.
- `Jardiance`, `Mounjaro`, `Trulicity`, `Zepbound`, and `Xarelto` received curated QA overrides where search-visible official pages or blocked branded HCP URLs were missed by the automated classifier.

## Remaining Limitations

The reviewed files are substantially expanded, but they should still be treated as a structured review pass rather than a legal-certainty statement that every unresolved product lacks a website. Some official manufacturer sites block simple HTTP fetches, require JavaScript, route through country or audience gates, or appear only under manufacturer product portals. Those cases remain visible in `unresolved_after_manual_review.csv` and `generic_like_scope_review_after_manual_review.csv`.

Rows classified as `no_branded_site_found_after_manual_review_pass` mean no matching official branded HCP or patient URL was found by the direct URL probes, Bing result review, and QA override process used in this run.

