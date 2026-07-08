# Cohere-style CI sidecar check: follow-up review of `no_branded_site_found_after_manual_review_pass`

Date: 2026-07-08

## Task assessed

Follow-up audit of drugs classified as `no_branded_site_found_after_manual_review_pass` in `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/`, with the specific goal of checking whether the sidecar skill needs a new reusable lesson after the manual-review pass.

## Files inspected

- `_skills_to_install/cohere-style-ci/SKILL.md`
- `competitive_intelligence_reports/branded_drug_websites/manual_review_cohere_style_ci_feedback.md`
- `competitive_intelligence_reports/branded_drug_websites/subagent_cohere_style_ci_feedback.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/manual_review_addendum.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/methodology.md`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/run_summary.json`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/unresolved_after_manual_review.csv`
- `competitive_intelligence_reports/branded_drug_websites/2026-07-08_0000/generic_like_scope_review_after_manual_review.csv`

## Assessment

No additional `_skills_to_install/cohere-style-ci/SKILL.md` edit was warranted for this follow-up.

The existing skill already covers the relevant reusable rule for U.S. branded prescription-drug HCP or patient website inventories built from FDA, NDC, DailyMed, Drugs@FDA, label, or other product-list seed sources. It already requires:

- keeping regulatory or NDC seed records separate from website-discovery evidence
- recording application, NDC, label, product strength, form, route, Rx/OTC status, marketing status, labeler or manufacturer, source-supported indication or class, discovered HCP and patient URLs, discovery method, access date, screenshot status, audience classification, and exclusion or ambiguity reason
- treating FDA or NDC records as product-existence and regulatory-status evidence rather than proof that a branded HCP or patient website exists
- retaining no-site, redirected, unbranded, access-gated, generic/manufacturer-corporate, and ambiguous candidates as explicit status rows

The manual-review addendum already adds the follow-on operational guardrails that mattered in this case, including direct URL fetch checks, visible HCP/professional evidence, patient-facing evidence, parked or domain-for-sale exclusions, and explicit handling of generic-like scope-review cases. The follow-up review of rows classified as no branded site found after the manual-review pass did not expose a clearly new, non-duplicative reusable lesson beyond those existing rules.

## Result

- Skill edit made: no.
- Rationale: the follow-up confirms the existing FDA/NDC-versus-website-discovery guidance and the manual-review addendum already cover the reusable lesson for this workflow.
