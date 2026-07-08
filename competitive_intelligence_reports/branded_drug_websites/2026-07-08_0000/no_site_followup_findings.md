# Follow-Up Review of `No Branded Site Found` Rows

Run date: 2026-07-08

## Scope

This review focused only on the 1,196 rows in `master_branded_drug_website_inventory_manual_reviewed.csv` classified as:

`no_branded_site_found_after_manual_review_pass`

The purpose was to determine whether the previous review missed HCP or patient websites.

## Bottom Line

Yes, the prior pass missed some websites.

The most reliable misses fall into two groups:

1. Variant or formulation rows whose base brand already has an HCP and/or patient URL in the reviewed master.
2. Direct brand domains that fetch successfully with visible brand text or that are blocked to simple HTTP but resolve as branded domains.

I did not merge these candidates into the master inventory. The files below identify likely misses for row-level verification before any inventory update.

## Generated Follow-Up Files

- `no_site_followup_sibling_inheritance_candidates.csv`
- `no_site_followup_sibling_inheritance_summary.json`
- `no_site_followup_candidate_misses.csv`
- `no_site_followup_best_candidate_misses.csv`
- `no_site_followup_audit_status.csv`
- `no_site_followup_summary.json`
- `no_site_followup_direct_blocked_domain_candidates.csv`
- `no_site_followup_direct_blocked_domain_summary.json`
- `no_site_followup_probable_missed_direct_domains.csv`
- `no_site_followup_blocked_brand_domain_candidates.csv`

## Follow-Up Counts

Sibling/base-brand inheritance audit:

- No-site rows reviewed: 1,196.
- Sibling-inheritance candidate rows: 51.
- Candidate rows with suggested HCP URL: 46.
- Candidate rows with suggested patient URL: 21.

Search-result audit:

- No-site rows audited: 1,196.
- Candidate rows: 13.
- Best candidate rows: 4.
- Brands with candidates: 4.

Direct-domain audit:

- No-site rows audited: 1,196.
- Candidate rows: 1,371.
- Brands with candidates: 296.
- Status counts: 811 fetched with HTTP 200, 560 blocked with HTTP 403.
- Filtered probable direct-domain misses: 244 rows across 193 brands.
- Filtered blocked branded-domain candidates: 123 rows across 65 brands.

The direct-domain files are intentionally broad and include noise. Treat them as a candidate net, not confirmed truth.

## High-Confidence Likely Misses

These rows should be reclassified or manually verified first.

| No-site row | Likely correction | Basis |
|---|---|---|
| Actemra ACTPen | Inherit ACTEMRA HCP and patient URLs | Base brand ACTEMRA has HCP + patient URLs in master. |
| Xolair PFS | Inherit XOLAIR HCP and patient URLs | Base brand XOLAIR has HCP + patient URLs in master. |
| UPTRAVI Titration Pack | Inherit UPTRAVI HCP and patient URLs | Base brand UPTRAVI has HCP + patient URLs in master. |
| REBIF REBIDOSE | Inherit REBIF HCP and patient URLs | Base brand REBIF has HCP + patient URLs in master. |
| Darzalex IV | Inherit or map to DARZALEX HCP URL | DARZALEX/Darzalex Faspro sibling rows have HCP URL. |
| Tecentriq Hybreza | Inherit TECENTRIQ HCP URL | Base brand TECENTRIQ has HCP URL. |
| EGRIFTA SV | Review against EGRIFTA WR HCP + patient URLs | Same generic/manufacturer sibling has HCP + patient URLs. |
| ProAir Digihaler | Review against ProAir RespiClick HCP URL | Same brand family/manufacturer has HCP URL. |
| KISQALI FEMARA CO-PACK | Review against KISQALI HCP + patient URLs | Base brand KISQALI has HCP + patient URLs. |
| Sandostatin | Review against Sandostatin LAR Depot HCP URL | Same brand family/generic/manufacturer has HCP URL. |
| Lunsumio Velo | Review against Lunsumio HCP URL | Base brand Lunsumio has HCP URL. |
| PREZCOBIX PED | Review against PREZCOBIX HCP URL | Base brand PREZCOBIX has HCP URL. |
| NovoLog Mix 70/30 | Review against NovoLog NovoMedLink HCP URL | Same insulin aspart family has HCP URL. |
| TOUJEO Max | Review against TOUJEO HCP URL | Base brand TOUJEO has HCP URL. |
| BICILLIN CR / BICILLIN C-R 900/300 | Review against BICILLIN L-A HCP URL | Same Bicillin family/Pfizer HCP surface. |

## Direct-Domain Misses To Verify

These were missed because the earlier classifier required visible static-page evidence or discarded blocked domains.

| No-site row | Candidate URL | Candidate audience | Evidence |
|---|---|---|---|
| EYLEA HD | `https://www.eyleahdhcp.com/` | HCP | Direct branded domain fetched with brand-related content. |
| EYLEA HD | `https://www.eyleahd.com/` | Patient | Direct branded domain fetched with visible brand and patient text. |
| AMONDYS 45 | `https://www.amondys45.com/` | Patient/mixed | Direct branded domain fetched with visible brand, HCP, patient, and PI text. |
| BRENZAVVY | `https://brenzavvy.com/` | Patient | Direct branded domain fetched with visible brand and patient text. |
| AURLUMYN | `https://aurlumyn.com/` | Patient/mixed | Direct branded domain fetched with visible brand, HCP, patient, and PI text. |
| CYRAMZA | `https://cyramza.lilly.com/` | Mixed / blocked | Branded Lilly domain resolves but blocks simple HTTP. |
| ALYFTREK | `https://www.alyftrek.com/` and HCP variants | Mixed / blocked | Branded domain variants resolve but block simple HTTP. |
| ALPHAGAN P | `https://www.alphaganp.com/` and HCP variants | Mixed / blocked | Branded domain variants resolve but block simple HTTP. |
| APADAZ | `https://apadaz.com/` | Patient / blocked | Branded domain resolves but blocks simple HTTP. |

The full broader list is in `no_site_followup_probable_missed_direct_domains.csv` and `no_site_followup_blocked_brand_domain_candidates.csv`.

## Candidate Noise Identified

The broad candidate files include false positives and should not be merged without verification. Common noise patterns:

- Generic-like or nonbranded rows, such as blood collection systems, electrolyte/IV fluids, oxygen, and preservation solutions.
- Redirects to manufacturer portfolio pages rather than branded HCP/patient sites.
- Domain-parking or domain-marketplace pages.
- Unrelated acronym collisions, such as ACD-A matching toy/game distribution or photo-software pages.
- Third-party disease/community pages or product-information pages that are not manufacturer-owned branded drug sites.
- Label PDFs or DailyMed pages, which may document the product but are not branded HCP/patient websites.

## Recommended Next Step

Before updating the master inventory, review the high-confidence likely misses and direct-domain misses in a browser. Merge only rows where the page is manufacturer-owned or brand-owner-controlled, U.S.-relevant, and audience-specific or clearly a branded product site.

