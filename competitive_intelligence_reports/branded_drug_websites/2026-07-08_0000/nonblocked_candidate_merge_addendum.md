# Non-Blocked Candidate Review Addendum

Run date: 2026-07-08

## Scope

This pass reviewed `no_site_followup_probable_missed_direct_domains.csv`, the set of direct-domain candidates that returned non-blocked HTTP 200 responses during the follow-up review of brands previously classified as `no_branded_site_found_after_manual_review_pass`.

The blocked 403 candidate set was not merged in this pass.

## Final Merge Results

- Non-blocked candidate rows reviewed: 244
- Accepted candidate rows after verification: 114
- Accepted HCP rows: 52
- Accepted patient rows: 62
- Applied unique brand/audience rows: 112
- Rows landed in official HCP/patient list extracts: 111
- HCP list rows after merge: 1,121
- Patient list rows after merge: 833
- Master classification counts after merge:
  - `both_hcp_and_patient_found`: 699
  - `hcp_found_patient_not_found`: 446
  - `patient_found_hcp_not_found`: 181
  - `no_branded_site_found_after_manual_review_pass`: 1,100

## QA Decisions Applied

- Promoted clearly HCP-only pages discovered from patient-domain candidates into the HCP list rather than rejecting them outright. Examples: `DEFENCATH`, `Cleviprex`, `Kanjinti`.
- Fixed HCP URL selection so explicit HCP domains/paths are preferred over shorter root domains when both are accepted for the same brand. Examples: `BESREMi`, `SPEVIGO`.
- Accepted `Yutrepia` HCP and patient sites after confirming the parked-page signal was a false positive from embedded page payload text, while the visible page title and audience signals were valid.
- Rejected weak standalone or unusable pages that did not support an actual patient/HCP site assignment. Examples: `Vancocin`, `JANUVIA` 404 URL, `Zevalin` maintenance page.
- Kept out-of-scope non-vaccine/non-OTC/non-diagnostic exclusions out of the official lists where direct domains were found but the brand/site did not fit the requested Rx drug website scope. Examples: `Cardiolite`, `LOCAMETZ`, `NephroScan`, `LIPIODOL`, `LASTACAFT`, `Betadine`, `Xyzal`, `Avance Nerve Graft`.

## Updated Official Files

- `master_branded_drug_website_inventory_manual_reviewed.csv`
- `hcp_branded_drug_websites_manual_reviewed.csv`
- `patient_branded_drug_websites_manual_reviewed.csv`
- `unresolved_after_manual_review.csv`
- `nonblocked_candidate_verification.csv`
- `nonblocked_candidate_applied_rows.csv`
- `nonblocked_candidate_merge_summary.json`

## Remaining Caveats

Some accepted standalone patient domains rely on direct branded-domain evidence plus drug-product page signals where the fetched static HTML did not expose richer patient copy. These were retained only when the domain/title clearly supported a branded drug destination and did not trip HCP-only, maintenance/error, parked-domain, diagnostic, device, OTC, or generic-supply exclusions.
