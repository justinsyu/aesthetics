# Cohere-style CI sidecar check: non-blocked direct-domain follow-up and merge review

Date: 2026-07-08

## Task assessed

Review of non-blocked follow-up direct-domain candidates for `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/` and the merge step for confirmed patient/HCP branded websites into the reviewed inventories.

## Files inspected

- `_skills_to_install/cohere-style-ci/SKILL.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/manual_review_addendum.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/no_site_followup_findings.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/no_site_followup_summary.json`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/no_site_followup_direct_blocked_domain_summary.json`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/no_site_followup_direct_blocked_domain_candidates.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/no_site_followup_probable_missed_direct_domains.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/hcp_branded_drug_websites_manual_reviewed.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/patient_branded_drug_websites_manual_reviewed.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/master_branded_drug_website_inventory_manual_reviewed.csv`

## Assessment

No additional `_skills_to_install/cohere-style-ci/SKILL.md` edit was warranted.

The current skill already covers the durable inventory rule for branded drug website work: keep FDA/NDC or other regulatory seed records separate from website-discovery evidence, preserve audience and exclusion status, and keep blocked, redirected, unbranded, access-gated, generic/manufacturer-corporate, and ambiguous cases explicit rather than collapsing them into confirmed website hits.

The follow-up artifacts do not introduce a distinct reusable lesson beyond that guidance and the existing manual-review addendum. The direct-domain follow-up remains a candidate-verification workflow, not a new class of source rule. The summaries show the expected split between fetchable candidate domains and blocked domains, and the search-result follow-up identifies only a small set of possible missed sites that still require row-level verification before merging.

## Result

- Skill edit made: no.
- Rationale: no clearly new, non-duplicative reusable lesson was found beyond the existing FDA/NDC-vs-website-discovery rule and the manual-review addendum.
