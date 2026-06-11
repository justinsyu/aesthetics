# Optimal/Common Approach for Vestrum Wet AMD Analyses

Updated: 2026-06-03

## Recommended Default Design

Use an eye-level retrospective cohort in the Vestrum Health Retina Database. For a treatment-outcomes analysis, define nAMD by diagnosis plus anti-VEGF treatment, use first anti-VEGF injection as index, require baseline VA, define a pre-index treatment-history window, and specify fixed follow-up/visit windows. This is the most reusable pattern across Ciulla 2018/2020/2022, Moshfeghi 2021, SIERRA-AMD, Emami 2024, and recent persistence/gap work.

The optimal common analysis should report results by baseline VA stratum and treatment exposure, with attrition shown separately from clinical outcomes. Because most published Vestrum papers do not provide full ICD/NDC/HCPCS lists, any new analysis should document those lists internally and, if possible, publish them in an appendix.

## Choose the Design by Question

- First-year VA or intensity: use treatment-naive eyes, first injection as index, baseline VA strata, and injection-count exposure. Ciulla 2020 supports 1-year VA by injection count/agent; Moshfeghi 2021 adds required index VA, month-12 VA closest to months 11-12, and at least quarterly VA.
- Long-term treatment burden: use first injection as index, annual/cumulative injection counts, visit and noninjection-visit counts, dosing intervals, and years 1-4 or 1-5 outcomes where follow-up exists. SIERRA-AMD and Ciulla 2022 are the strongest templates.
- Persistence, gaps, switching, or reinitiation: require a clear pre-index history window and at least 24 months follow-up when feasible. Use a `>=180-day` gap for nonpersistence/treatment gaps; Ko 2026 also uses a hierarchical post-gap outcome order of switch, reinitiation, then discontinuation.
- Agent comparison or modern durability: use first treatment with the agent for treatment-naive eyes, switch date for treatment-experienced eyes, and adjust or stratify by baseline or switch-date VA. Rowe 2026 measures durability as the interval between the final two injections and the proportion extended >50 days, but accessible methods are abstract-level only.
- Conversion or prevention: for dry-to-wet conversion, require both diagnostic-code change and anti-VEGF initiation when feasible, with conversion date as the earliest of those events. Luttrull 2023 is more operationally explicit than the fellow-eye conversion literature.
- Functional or adverse-event endpoints: use endpoint-specific definitions. Emami 2024 defines driving vision loss as VA worse than 20/40 sustained for at least 6 consecutive months; Kaufmann 2025 frames SMH by diagnosis plus injection type and timing relative to prior injection, but full algorithms were not accessible.

## Core Operational Choices

- Index date: first anti-VEGF injection for treated nAMD outcomes; switch date for switching analyses; first nAMD diagnosis for epidemiology, untreated-eye burden, or noninjected SIERRA-style cohorts.
- Treatment-naive rule: choose one rule and justify it. Published options include no prior anti-VEGF ever, no anti-VEGF for >180 days before index, or no anti-VEGF during a 12-month pre-index period. For modern persistence/comparator work, a 12-month pre-index window is easiest to align with Ko 2026; add a >180-day sensitivity if comparability to SIERRA/gap analyses matters.
- VA conversion: convert Snellen/logMAR to ETDRS-equivalent letters using a stated rule, commonly `85 + 50 x log(Snellen fraction)` or `85 - 50 x logMAR`. Use the Gregori approximation only when matching Luttrull-style conversion work. Report whether VA was distance-corrected, near-corrected, pinhole, or mixed real-world VA; if possible, require consistent VA method per patient as in Moshfeghi 2021.
- Baseline VA strata: stratify at minimum as 20/40 or better, 20/41-20/70, 20/71-20/200, and 20/201 or worse, because baseline VA strongly affects observed gain/loss.
- Follow-up and attrition: define fixed windows before analysis. Good reusable rules include 12-month outcomes, month-12 VA closest to months 11-12, quarterly VA availability, 24-month persistence follow-up, and separate 6-, 12-, and 24-month attrition cohorts as in Ciulla 2018.
- Treatment exposure: report annual injection counts, cumulative counts, inter-injection intervals, and gap status. Common bins include `<=6` vs `>6` injections/year, 1-5/6-7/>=8 injections in year 1, and cumulative annual counts for longer-term analyses.

## Outcomes Previously Studied

Published Vestrum wet AMD work has evaluated first-year and long-term VA change, injection frequency/intensity, visit and noninjection visit burden, bilateral treatment patterns, dosing intervals, loss to follow-up, fellow-eye conversion, dry-to-wet conversion/prevention, medication associations with conversion, persistence/switching/reinitiation, treatment gaps, maintenance of driving vision, submacular hemorrhage rates, and early faricimab durability/VA outcomes.

## Evidence and Access Caveats

The major reproducibility gap is not a lack of outcome definitions; it is that the underlying diagnosis and drug code lists are usually unpublished. For any future Vestrum analysis, publish a supplement with ICD-9/ICD-10 disease codes, anti-VEGF NDC/HCPCS/procedure codes, exclusion-code lists, and exact VA/follow-up window rules.

Several potentially useful supplements remain blocked or incomplete in the current evidence set: Moshfeghi 2021 supplement download returned a proof-of-work stub, Rowe 2026 Sage supplemental files returned 403 and PubMed lists PMCID availability for Apr 9 2027, and Kaufmann 2025/AJO supplemental snippets did not expose ICD/HCPCS/NDC lists. Treat those papers as useful endpoint/design comparators, not fully reproducible algorithm sources.
