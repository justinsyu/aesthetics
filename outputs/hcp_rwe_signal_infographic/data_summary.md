# RWE signal terms infographic data summary

Input source: `outputs/hcp_promotional_message_audit/site_level_rwe_signals_with_promotional_context.md` and `outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv`.

## Denominators
- Total audited HCP/drug URL rows: 681
- Confirmed site-level RWE-positive rows: 149 (21.9%)
- Maybe RWE rows: 121
- Confirmed no RWE rows: 390
- Normalized RWE term hits across RWE-positive rows: 264

## Signal families on RWE-positive rows
- Postmarketing: 55 / 149 (36.9%)
- Real-world / RWE variants: 50 / 149 (33.6%)
- Registries: 45 / 149 (30.2%)
- Observational / retrospective: 39 / 149 (26.2%)
- Claims / EHR / database: 28 / 149 (18.8%)
- Phase 4 / extension: 10 / 149 (6.7%)

## Top normalized terms
- postmarketing: 51
- registry: 45
- real-world: 43
- observational: 27
- real-world evidence: 26
- retrospective: 19
- claims: 15

## Key caveat
These counts are observed site-language signals, not validated RWE claims. Only 1 of 149 RWE-positive rows had an extracted strongest promotional message containing explicit RWE wording.
