# Methodology: GLP-1 Obesity OpenData Competitive Intelligence

Prepared: 2026-05-28

## Objective

Create a repeatable public-data workflow that identifies potentially useful signals and competitive intelligence for a company with a pipeline GLP-1 treatment for obesity.

The workflow prioritizes deterministic, refreshable sources from the OpenData catalog and preserves traceability from every derived signal back to the dataset, endpoint, source URL, product dictionary term, and retrieval run.

## Scope

Included:

- Approved and marketed incretin products relevant to obesity, diabetes, and adjacent cardiometabolic use.
- Public FDA product, NDC, approval, shortage, recall, Orange Book, and NME datasets.
- Public CMS Medicare/Medicaid spending, reimbursement, utilization, pricing, rebate, plan, denial, and marketplace datasets.
- Public CDC/OWID/Census population-health and coverage datasets for burden and access context.
- Dataset-discovery search logs from OpenData.

Excluded unless added later:

- Non-public claims, EHR, formulary, prior authorization, paid prescription, promotional spend, and sales data.
- ClinicalTrials.gov and company/investor web monitoring. These are recommended complements but are not part of the OpenData-only refresh package.
- Individual-level patient inference. All signals are aggregate and hypothesis-generating.

## Source Hierarchy

1. OpenData metadata and API endpoints for catalog traceability.
2. Upstream source files listed in OpenData metadata where data volume is manageable.
3. OpenData `/columns` endpoints for machine-readable schema confirmation.
4. Optional OpenData sampled data endpoints for row-shape confirmation when rate limits permit.
5. OpenData search results for dataset-discovery provenance.

When an upstream source file and an OpenData normalized endpoint differ, the source log must record both. Analyst review decides whether the normalized or original representation is preferable for a given signal.

## Deterministic Product Matching

The workflow uses `config/glp1_product_dictionary.json` as the only match vocabulary. Matching is case-insensitive and normalized by removing punctuation and excess whitespace.

Match classes:

- `brand` - marketed product names, including obesity and diabetes brands.
- `ingredient` - active ingredient names.
- `manufacturer` - sponsor/manufacturer names used only as supporting context, not as a stand-alone product match.

Rows are retained when a brand or ingredient term appears in configured product-name, brand-name, generic-name, active-ingredient, product-description, or trade-name fields. Brand-name matches take precedence over ingredient matches for product attribution. Ingredient-only rows that map to multiple brands are retained as `ingredient:<term>` records so they remain traceable without inflating brand-level product summaries. Manufacturer matches are retained only when a brand/ingredient match is also present in the same row, unless a future methodology revision explicitly permits manufacturer-only capture.

## Core Refreshable Signals

1. Competitor utilization momentum
   - Primary datasets: `cms/sdud`, `cms/part-d-spending`, `cms/medicaid-spending`.
   - Measures: prescriptions, claims, units, beneficiaries, reimbursed amount, total spending, spend per claim, spend per dosage unit.
   - Grain: product, ingredient, payer channel, state/quarter when available, year when available.

2. Payer and reimbursement pressure
   - Primary datasets: `cms/nadac`, `cms/ful`, `cms/drug-rebate-products`, `cms/ira-drug-prices`.
   - Measures: acquisition cost, reimbursement ceiling, rebate category, effective price fields, product category, approval/market dates.
   - Grain: NDC, product, ingredient, date/quarter.

3. Regulatory and product lifecycle
   - Primary datasets: `fda/drugs-at-fda`, `fda/ndc-directory`, `fda/orange-book`, `fda/nme-approvals`, `fda/drug-shortages`, `fda/drug-recalls`.
   - Measures: dosage form, route, strength, application number, applicant, approval date, TE/reference flags, shortage/recall status.
   - Grain: application/product/NDC.

4. Market opportunity and access context
   - Primary datasets: `cdc/brfss`, `owid/obesity`, `census/health-insurance-coverage`, `cms/medicaid-chip-enrollment`.
   - Measures: obesity/diabetes prevalence, coverage/uninsured rates, Medicaid/CHIP enrollment.
   - Grain: geography and year.

5. Insurer behavior and commercial access context
   - Primary datasets: `cms/transparency-in-coverage`, `cms/marketplace-plans`, `cms/mlr-data`.
   - Measures: claim denial rates, appeals, plan/county footprint, premiums, cost sharing, insurer financial context.
   - Grain: issuer, state/county, plan year.

## Refresh Procedure

1. Load pinned dataset inventory and product dictionary.
2. Hash the script and config files.
3. Query OpenData metadata for every pinned dataset.
4. Query `/columns` for each dataset to pin machine column names and types.
5. Optionally query a small deterministic sample from each dataset endpoint for row-shape validation.
6. Run pinned OpenData search queries and save ranked results.
7. Fetch manageable upstream source files from metadata `source_url` fields.
8. Parse supported CSV/JSON/XLSX/ZIP source files and retain rows that match the product dictionary.
9. Write normalized JSON/CSV match outputs.
10. Write source log, dataset inventory, signal specs, refresh summary, and run manifest with SHA-256 output hashes.

Default runs scan the sources marked `source_scan` in `config/opendata_sources.json`. Full execution runs use `--scan-all-sources --include-large-source-downloads` and must scan every pinned dataset with a `source_url`, including sources normally marked metadata-only for the default deck run.

## Count Semantics

Generated outputs distinguish lexical match records from unique source rows. A single source row can produce multiple lexical records when more than one configured term matches, so regulatory-count and coverage summaries must not describe lexical records as unique FDA rows. Dataset-level coverage uses `lexical_match_records` and `unique_matched_source_rows`; product summaries use `match_records` and `matched_source_rows`. Unique source-row counts are based on the dataset plus source-row number, not `source_record_id`, because some upstream records do not expose stable product-level identifiers and can collide or be blank.

Annual deltas compare the latest observed annual field to the prior observed annual field. When those years are consecutive, `period_relation` is `strict_yoy`; otherwise it is `latest_vs_prior_observed`. The `direction` field describes spending change, not claims change.

FDA shortage findings are classified from source status and availability fields. Brand-level limited-availability statements require `Current / Limited Availability`; `Current / Available` rows are retained only as watch candidates, and ingredient-level rows remain separate from brand attribution.

## Refresh Cadence

- Weekly: metadata inventory, source log, FDA NDC/shortage/recall context, CMS pricing context.
- Monthly: payer/pricing and CMS plan/access context.
- Quarterly: Medicaid SDUD large-source scan.
- Annually or on CMS release: Part D and Medicaid spending by drug.
- Ad hoc: after major competitor readouts, approval decisions, label changes, shortages, or payer-policy events.

## QA Checks

Required before using outputs in external deliverables:

- Confirm all expected pinned datasets returned metadata.
- Confirm source files used for product matching have non-empty source URLs and successful retrieval status.
- Review unmatched known product terms after every major GLP-1 approval or brand launch.
- Spot-check at least one matched row per dataset against the upstream source or OpenData page.
- Compare row counts and output hashes against the prior run.
- Run `scripts/verify_refreshed_outputs.py` to re-download CMS spending sources, reconcile CMS product totals, validate FDA row-count semantics, check shortage classification, and confirm manifest hashes.
- For full-run deliverables, confirm `run_manifest.json` has `scan_all_sources: true` and that `source_coverage_matrix.csv` contains no `not_scanned` rows for datasets with source URLs.
- Document any methodology changes in this file and update the product dictionary version.

## Known Limitations

- OpenData datasets have different update lags. CMS annual drug spending generally lags by year; some Medicaid and FDA feeds update more frequently.
- Product matching is lexical and can miss misspellings, abbreviations, or new brands not in the dictionary.
- Some CMS datasets suppress small cells or round counts for privacy.
- Public aggregate spending does not equal manufacturer net revenue.
- OpenData API SQL requires authentication; this workflow defaults to public metadata, `/columns`, search endpoints, and upstream source files.
- Anonymous OpenData data GET endpoints have low rate limits. The default script run does not request sample rows; use `--include-samples` when row-shape validation is needed.
- Marketplace plan and denial datasets do not expose product-specific formulary or prior authorization rules.
- Population-health burden datasets are not drug-linked and should be used as contextual opportunity signals, not utilization evidence.

## Complementary High-Value CI Layer

The OpenData refresh is the public baseline. A complementary high-value CI module adds the source classes needed for strategic GLP-1 obesity work:

- Clinical pipeline and trial movement: ClinicalTrials.gov, CTIS/ICTRP where available, company trial registries, and pipeline aliases from `config/glp1_asset_dictionary.json`.
- Formulary and access: Medicare Part D formulary PUFs, Medicaid PDLs, PBM policies, commercial coverage policies, prior authorization criteria, step therapy, quantity limits, and exclusions.
- Claims and Rx demand: licensed claims/Rx fills for commercial, Medicare Advantage, cash-pay, persistence, switch, discontinuation, and diagnosis-linked demand signals.
- Pricing and gross-to-net: WAC/list price, NADAC, FUL, SSR/Red Book/Medi-Span where licensed, cash prices, coupons, rebate proxies, and contracting indicators.
- Safety and tolerability: labels, DailyMed, FAERS, trial AE tables, PubMed/case reports, safety communications, and discontinuation/tolerability narratives.
- Supply and manufacturing: FDA shortages, recalls, 483/warning-letter/import-alert signals, facility registrations, supplier/CMO announcements, and company capacity statements.
- Scientific and KOL: PubMed, congress abstracts, guidelines, KOL publication networks, and disease-obesity treatment discourse.
- IP and lifecycle: Orange Book, patents, patent-family monitoring, PTAB/IPR, litigation, exclusivity, formulation/device lifecycle, and label-expansion milestones.
- Company disclosures: SEC filings, investor decks, earnings transcripts, press releases, pipeline pages, and manufacturing/access commentary.

Public collectors and gated sources must remain separate. Public API records can be refreshed and source-logged directly. Paid, proprietary, credentialed, or manually provided sources are represented as ingestion requirements until the underlying files or credentials exist; generated outputs must not imply those restricted sources were collected.

Manual inputs use `manual_inputs/high_value_ci/<source_id>.csv` and must conform to templates in `input_templates/high_value_ci/`. Refresh validation records missing inputs, schema errors, row counts, file hashes, and dictionary-term matches in `generated_data/high_value_ci/manual_ingest_validation.csv`. Missing gated inputs are acceptable only as explicit missing-input statuses, not as collected evidence.

## Revision Log

- 2026-05-28: Added XLSX source parsing, explicit lexical-record versus unique-source-row count semantics, shortage availability classification, period-relation labeling, and deterministic verifier checks.
- 2026-05-28: Initial deterministic OpenData methodology and refresh package created.
