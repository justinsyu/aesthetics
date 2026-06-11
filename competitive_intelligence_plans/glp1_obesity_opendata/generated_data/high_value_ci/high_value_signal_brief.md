# High-Value GLP-1 Obesity CI Additions

Run timestamp: 2026-05-28T19:17:34+00:00

## Public Collectors

- `clinicaltrials_gov` (clinical_pipeline): 312 rows, collected; Pipeline trial starts, status changes, phase movement, sponsor positioning, enrollment criteria, outcomes, and comparator designs.
- `pubmed_literature` (scientific_kol): 270 rows, collected; Publication velocity, safety/tolerability papers, comparative efficacy publications, KOL author networks, and guideline-adjacent evidence.
- `dailymed_labels` (safety_tolerability): 26 rows, collected; Current label updates, indication language, contraindications, warnings, dosing, and adverse-reaction wording.
- `sec_edgar_submissions` (company_disclosures): 552 rows, collected; Earnings releases, 10-K/10-Q/8-K updates, risk factors, manufacturing disclosures, trial updates, launch commentary, and partnership disclosures.
- `public_pricing_opendata_extract` (pricing_gross_to_net): 100 rows, public pricing proxy rows extracted from OpenData refresh; Public pricing proxies from refreshed OpenData matches, including CA WAC increase rows, NADAC acquisition-cost rows, and IRA price benchmark rows. These are not net price or rebate estimates.
- `fda_drug_enforcement` (supply_manufacturing): 70 rows, openFDA drug enforcement records collected; OpenFDA drug recall/enforcement actions for GLP-1 brands and active ingredients, including ongoing recalls, classification, recalling firm, reason, and product description.
- `state_medicaid_pdl_public_registry` (formulary_access): 2 rows, state Medicaid public registry pages fetched; Deterministic registry of official state Medicaid PDL or PA pages where public source URLs are known; page hashes and GLP-1 lexical hits support follow-on manual criteria extraction.
- `cms_partd_formulary_puf` (formulary_access): 1 rows, latest bulk nested files discovered; range member extraction unavailable; Medicare Part D formulary placement, prior authorization, step therapy, quantity limits, plan footprint, and pharmacy-network pricing context.
- `fda_faers_quarterly` (safety_tolerability): 1259 rows, openFDA FAERS reaction counts collected; Adverse-event reporting patterns, disproportionality hypotheses, tolerability watchlists, and label-signal triage.
- `patentsview_uspto` (ip_lifecycle): 4 rows, bulk fallback resources captured; Patent-family, assignee, inventor, and claim-theme discovery around incretin, peptide, oral GLP-1, amylin, and combination obesity assets.

## Gated / Manual Ingestion Specs

- `paid_rx_claims` (claims_rx_demand): requires_license_or_client_data; template `input_templates/high_value_ci/paid_rx_claims.csv`; required fields: fill_date; product_or_ndc; quantity; days_supply; payer_type; plan_or_channel; patient_id_hash; diagnosis_code_optional; geography_optional.
- `commercial_pbm_policy` (formulary_access): requires_license_or_manual_policy_corpus; template `input_templates/high_value_ci/commercial_pbm_policy.csv`; required fields: payer; plan; product; coverage_status; tier_optional; pa_required; step_required; quantity_limit; policy_effective_date; source_url_or_file.
- `gross_to_net_pricing` (pricing_gross_to_net): requires_license_or_client_data; template `input_templates/high_value_ci/gross_to_net_pricing.csv`; required fields: product; date; price_type; price; unit; channel_optional; source.
- `state_medicaid_pdl_policy` (formulary_access): public_but_state_fragmented; template `input_templates/high_value_ci/state_medicaid_pdl_policy.csv`; required fields: state; program; product; preferred_status; pa_required; criteria_text; effective_date; source_url_or_file.
- `manufacturing_supply_watch` (supply_manufacturing): mixed_public_and_manual_review; template `input_templates/high_value_ci/manufacturing_supply_watch.csv`; required fields: company; facility_or_supplier; event_type; event_date; product_or_modality; risk_summary; source_url_or_file.

## Interpretation Boundary

- Public API records are collected evidence and can be refreshed deterministically.
- Gated sources are configured as ingestion requirements only; they are not represented as collected until licensed or client-provided files are added.
- Outputs remain hypothesis-generating and require analyst adjudication before external use.
