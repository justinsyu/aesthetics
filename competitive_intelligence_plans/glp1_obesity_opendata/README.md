# GLP-1 Obesity OpenData Competitive Intelligence

This package contains a deterministic refresh workflow for public-data signals relevant to a pipeline GLP-1 treatment for obesity.

It uses OpenData as the source catalog and records traceability for every dataset, query, source URL, and generated output. The workflow is designed for recurring refreshes and later methodology review.

## Files

- `METHODOLOGY.md` - analytic method, source hierarchy, signal definitions, caveats, and refresh rules.
- `HIGH_VALUE_METHODOLOGY.md` - complementary high-value source methodology, matching rules, CMS formulary parsing approach, and verification gates.
- `config/opendata_sources.json` - pinned OpenData dataset inventory and intended CI use.
- `config/glp1_product_dictionary.json` - deterministic product/ingredient matching dictionary.
- `config/glp1_asset_dictionary.json` - deterministic pipeline asset, mechanism, sponsor, and alias dictionary.
- `config/high_value_ci_sources.json` - complementary high-value public collectors and gated-source ingestion specs.
- `config/state_medicaid_pdl_sources.json` - deterministic registry of official state Medicaid PDL/PA pages that can be fetched and source-hashed without credentials.
- `scripts/refresh_opendata_glp1_ci.py` - reproducible metadata and signal refresh script.
- `scripts/refresh_high_value_glp1_ci.py` - reproducible high-value CI source registry and public-collector refresh script.
- `scripts/build_slide_deck.py` - reproducible HTML deck builder from generated outputs.
- `scripts/verify_refreshed_outputs.py` - independent deterministic verifier for CMS, FDA, shortage, delta, and manifest checks.
- `scripts/verify_high_value_outputs.py` - independent verifier for high-value CI source coverage, gated specs, logs, and manifest hashes.
- `generated_data/` - generated outputs from the latest run.

## Refresh

Run from the repository root:

```powershell
python competitive_intelligence_plans\glp1_obesity_opendata\scripts\refresh_opendata_glp1_ci.py
```

Include small OpenData sample rows from each dataset endpoint:

```powershell
python competitive_intelligence_plans\glp1_obesity_opendata\scripts\refresh_opendata_glp1_ci.py --include-samples
```

Optional large-source scan for Medicaid SDUD and other large files:

```powershell
python competitive_intelligence_plans\glp1_obesity_opendata\scripts\refresh_opendata_glp1_ci.py --include-large-source-downloads
```

Full execution of every pinned dataset with a source URL:

```powershell
python competitive_intelligence_plans\glp1_obesity_opendata\scripts\refresh_opendata_glp1_ci.py --scan-all-sources --include-large-source-downloads
```

Run independent verification after refresh:

```powershell
python competitive_intelligence_plans\glp1_obesity_opendata\scripts\verify_refreshed_outputs.py
```

Refresh high-value CI additions beyond OpenData:

```powershell
python competitive_intelligence_plans\glp1_obesity_opendata\scripts\refresh_high_value_glp1_ci.py
```

The high-value refresh collects bounded public API tables where available, including ClinicalTrials.gov, PubMed, DailyMed, SEC EDGAR metadata and filing-text snippets, openFDA FAERS reaction-count summaries, and openFDA drug enforcement/recall records. It also resolves recent CMS Part D formulary ZIPs from the public catalog, extracts public pricing proxy rows from the verified OpenData match table, fetches configured state Medicaid PDL/PA registry pages, and attempts deterministic HTTP-range parsing of nested formulary files; if range extraction is unavailable or tested ZIPs use unsupported compression, the run records the attempted source and status rather than presenting unparsed data as collected rows. Full CMS ZIP downloads are disabled by default because single monthly packages can exceed 2 GB.

When network/API access is unavailable, write deterministic source inventory and gated-ingestion specs only:

```powershell
python competitive_intelligence_plans\glp1_obesity_opendata\scripts\refresh_high_value_glp1_ci.py --skip-network
```

Verify high-value outputs:

```powershell
python competitive_intelligence_plans\glp1_obesity_opendata\scripts\verify_high_value_outputs.py
```

Manual/gated source templates are written to `input_templates/high_value_ci/`. Put licensed or manually curated CSV inputs in `manual_inputs/high_value_ci/<source_id>.csv`; the refresh validates required fields and writes `generated_data/high_value_ci/manual_ingest_validation.csv`.

The default run avoids very large source downloads and OpenData sample data calls. It still produces a current metadata inventory, `/columns` schema snapshot, source log, search result log, and product-level matches from manageable upstream source files.

## Outputs

- `generated_data/run_manifest.json` - run timestamp, config hashes, script hashes, Python version, and output hashes.
- `generated_data/source_log.json` - one traceability record per OpenData API request and upstream source fetch.
- `generated_data/dataset_inventory.json` - OpenData metadata and schema summary for pinned datasets; sample response status is included only when `--include-samples` is used.
- `generated_data/opendata_search_results.json` - pinned search-query results for dataset discovery traceability.
- `generated_data/glp1_product_matches.json` / `.csv` - normalized matched public-data rows for GLP-1 products.
- `generated_data/product_signal_summary.json` / `.csv` - deduplicated product-by-dataset match counts and numeric rollups where available.
- `generated_data/signal_delta_summary.csv` - latest-vs-prior period changes where annual source fields exist, including strict YoY versus latest-prior-observed labeling.
- `generated_data/source_coverage_matrix.csv` - dataset-level execution status, source URL, row counts, lexical match records, unique matched source rows, and skipped-source reasons.
- `generated_data/refresh_validation_report.json` / `.md` - execution checks, warnings, zero-row scans, skipped P0 sources, and source failures.
- `generated_data/record_trace_map.jsonl` - one trace record per match with source hash, source update date, matched field/value, stable source-record identifier, and rule version.
- `generated_data/match_qc_sample.csv` - deterministic positive-match review sample.
- `generated_data/unmatched_dictionary_terms.csv` - configured terms not matched in scanned sources.
- `generated_data/run_comparison.json` - current output hashes compared with the previous run manifest when present.
- `generated_data/analyst_signal_brief.md` - first-pass source-derived signal brief with caveats and review status.
- `generated_data/signal_specs.json` - refreshable signal definitions and datasets required for each signal.
- `generated_data/refresh_summary.md` - human-readable run summary and next review items.
- `generated_data/high_value_ci/` - complementary public collector outputs, gated ingestion requirements, source logs, summaries, and manifest for non-OpenData CI layers.
- `input_templates/high_value_ci/` - schema templates for licensed or manual claims, PBM policy, pricing, Medicaid PDL, and manufacturing/supply inputs.

## Traceability Rules

Every generated row retains the source dataset id, source URL or API endpoint, match term, match field, and original source row when feasible. Generated files include SHA-256 hashes in the run manifest so changes can be compared across refreshes.
