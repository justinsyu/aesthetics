# High-Value GLP-1 CI Methodology

This methodology covers the complementary high-value CI layer in `generated_data/high_value_ci/`. It extends the OpenData baseline with refreshable public APIs, public bulk resources, and gated/manual ingestion templates.

## Source Classes

- Public API collectors: ClinicalTrials.gov, PubMed, DailyMed, SEC EDGAR submissions plus bounded filing-text snippets, openFDA FAERS drug-event counts, openFDA drug enforcement records, and PatentsView when reachable.
- Public bulk, generated-public, and registry collectors: CMS Part D formulary PUF resources resolved from public catalog pages and parsed through bounded HTTP-range reads where possible; OpenData-derived public pricing proxy rows from WAC, NADAC, and IRA price benchmark sources; official state Medicaid PDL/PA registry pages where public URLs are configured.
- Gated/manual sources: claims, PBM policy, gross-to-net pricing, state Medicaid PDL policy, and manufacturing/supply watch inputs.

Public sources are source-logged with URL, retrieval timestamp, response hash or content-length evidence, and generated output hashes in `generated_data/high_value_ci/run_manifest.json`. Gated/manual sources remain `template_only`, `missing_input`, `missing_required_fields`, or `validated_manual_input` until source files are provided under `manual_inputs/high_value_ci/`.

## Matching Rules

- Text-bearing public API records use deterministic dictionary matching from `config/glp1_product_dictionary.json` and `config/glp1_asset_dictionary.json`.
- CMS Part D formulary rows are matched by exact 11-digit NDC using the current OpenData-derived GLP-1 product match table, `generated_data/glp1_product_matches.csv`.
- FAERS rows are openFDA reaction-count aggregates by product query. They are reporting signals only and must not be interpreted as incidence, comparative risk, or causality.
- FDA drug enforcement rows are openFDA recall/enforcement records by product query. They are manufacturing and supply-watch signals only and must not be interpreted as proof of current product shortage, causality, or facility-wide quality risk without analyst review.
- Public pricing extract rows are copied from the latest verified OpenData match table for configured pricing datasets. They are WAC, NADAC, and IRA benchmark context only; they do not estimate commercial net price, rebates, or realized gross-to-net.
- SEC EDGAR submission rows include metadata for recent filings and bounded text snippets from the first configured filings per company. Snippets preserve source hashes and are used for triage, not complete filing interpretation.
- State Medicaid PDL public-registry rows hash configured official pages and preserve discovered document links where visible. They are source-discovery and lexical-triage records only; final preferred/non-preferred status, PA criteria, and effective-date attribution remain manual or downstream extraction tasks.
- PatentsView records are parsed when the PatentSearch API returns JSON. If the API is unavailable, official USPTO bulk-resource landing pages are captured as `collected_bulk_fallback`, not as parsed patent intelligence.

## CMS Part D Formulary Parsing

The CMS monthly formulary package can exceed 2 GB. The routine refresh avoids full ZIP downloads by:

1. Fetching the CMS catalog landing page.
2. Selecting the latest discovered monthly ZIP URL.
3. Reading the outer ZIP central directory using HTTP range requests.
4. Downloading only relevant stored nested ZIP members, such as the basic drugs formulary file.
5. Parsing delimited nested members and matching rows by exact NDC.

The parser emits formulary ID, contract year, RxCUI, NDC, tier, quantity-limit, prior-authorization, and step-therapy fields when matched rows are found. If range extraction is unavailable, the output records the attempted source status instead of implying collection.

## Verification Gates

`scripts/verify_high_value_outputs.py` checks:

- Manifest hashes for scripts, config, methodology, core NDC crosswalk input, and generated outputs.
- Source inventory coverage across all public and gated high-value categories.
- Gated template existence and normalized gated output files.
- CMS formulary parsed-row fields or explicit non-parsed status.
- FAERS openFDA reaction-count fields.
- FDA drug enforcement fields for recall status, classification, reason, product description, and source URL.
- Public pricing proxy fields copied from the OpenData refresh with source dataset and source hash.
- SEC filing text hash/snippet fields for the configured bounded text extraction pass.
- State Medicaid public registry fields for state, program, URL, page hash, registry hash, and interpretation note.
- PatentsView parsed output or explicit USPTO bulk fallback.
- Source-log traceability, with PatentsView API failures allowed only when fallback resources are present.

## Interpretation Limits

All high-value public outputs are hypothesis-generating candidate evidence. Analyst review is required before external use. Gated/manual categories are not collected evidence until the corresponding source files, licenses, or credentials exist and validation passes.
