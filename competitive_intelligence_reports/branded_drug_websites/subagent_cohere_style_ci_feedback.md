# CI-skill sidecar assessment: branded drug website inventory

Date: 2026-07-07

## Task assessed

U.S. branded prescription drug HCP/patient website inventory built from FDA/NDC sources plus website discovery.

## Guidance inspected

- `_skills_to_install/cohere-style-ci/SKILL.md`
- `_skills_to_install/cohere-style-ci/references/style-guide.md`
- `_skills_to_install/cohere-style-ci/agents/openai.yaml`
- Existing dirty diff for `_skills_to_install/cohere-style-ci/SKILL.md`, `_skills_to_install/cohere-style-ci/references/style-guide.md`, and `_skills_to_install/cohere-style-ci/scripts/export_html_slides_pdf.mjs`

## Assessment

A minimal skill edit was warranted.

The existing CI skill already covered adjacent work: HCP and patient product-website PRO-vs-label audits, claim/label/evidence separation, source-owner-first biomedical CI research, source logs, screenshot status, and explicit handling of ambiguous or excluded evidence. That guidance is useful for the current task, but it did not explicitly cover the inventory-specific distinction between FDA/NDC product seed records and open-web HCP/patient website discovery.

That distinction is important for this task because FDA/NDC/DailyMed/Drugs@FDA records can establish product existence, labeler/manufacturer, route/form/strength, Rx/OTC or marketing status, and label basis, but they do not establish that a current branded HCP or patient website exists. Website discovery needs separate evidence fields, including discovered URL, audience classification, access date, screenshot status, and screen-out status for no-site, redirected, unbranded, access-gated, generic/manufacturer-corporate, or ambiguous candidates.

## Skill edit made

Added one bullet to `_skills_to_install/cohere-style-ci/SKILL.md` under the HCP/patient product-website guidance. The addition instructs future runs to:

- keep FDA/NDC/regulatory seed records separate from website-discovery evidence
- preserve product identifiers and regulatory fields alongside discovered HCP/patient URLs
- record discovery method, access date, screenshot status, audience classification, and ambiguity/exclusion reason
- avoid treating FDA or NDC records as proof that a branded HCP or patient site exists
- retain no-site and ambiguous cases as explicit status rows rather than dropping them silently

## No other skill edits

No changes were made to the style guide, exporter script, or agent metadata. The existing dirty changes in those files appeared unrelated to this inventory-specific guidance and were left intact.
