# Cohere-style CI sidecar check: manual review of remaining U.S. branded drug websites

Date: 2026-07-08

## Task assessed

Manual review of remaining U.S. branded prescription drugs for HCP and patient websites, using the existing `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/` run artifacts as the starting inventory.

## Files inspected

- `_skills_to_install/cohere-style-ci/SKILL.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/run_summary.json`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/methodology.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/source-log.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/master_branded_drug_website_inventory.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/manual_review_queue.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/hcp_branded_drug_websites.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/patient_branded_drug_websites.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/hcp_seed_unmatched_or_out_of_scope_review.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/patient_seed_unmatched_or_out_of_scope_review.csv`

## Artifact observations

- The run retained 2,426 high-confidence FDA-backed branded prescription brand/generic pairs in the master inventory.
- The manual review queue contains 2,241 rows.
- The queue is split into 1,898 rows where no branded site was found in the existing seed or deterministic probe and 343 rows where an HCP site was found but a patient site was not found by seed or probe.
- The queue preserves search-ready HCP and patient queries, manufacturer or labeler, generic name, and reason code.
- The run summary and methodology already preserve the key evidence boundary: FDA/NDC data support product existence and marketed-listing status, but do not prove that a branded HCP or patient website exists.

## Skill assessment

No additional `_skills_to_install/cohere-style-ci/SKILL.md` edit was warranted for this follow-on task.

The current skill already includes the durable rule for U.S. branded prescription-drug HCP or patient website inventories built from FDA, NDC, DailyMed, Drugs@FDA, label, or other product-list seed sources. That rule already requires separating regulatory or NDC seed records from website-discovery evidence, preserving application/NDC/label/product fields, recording discovered HCP and patient URLs, discovery method, access date, screenshot status, audience classification, and exclusion or ambiguity reason, and retaining no-site, redirected, unbranded, access-gated, generic/manufacturer-corporate, and ambiguous candidates as explicit status rows.

The manual-review follow-on applies that rule rather than introduce a clearly new, non-duplicative reusable lesson.

## Result

- Skill edit made: no.
- Rationale: no clearly new, non-duplicative reusable lesson was found beyond the FDA/NDC-vs-website-discovery rule already present in `_skills_to_install/cohere-style-ci/SKILL.md`.
