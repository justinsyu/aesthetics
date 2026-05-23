# TA1120 — Avelumab + axitinib for untreated advanced RCC
## Cost-Effectiveness Clarification Questions from the EAG Health Economist

Prepared for the EAG, STA.
Recipient: Merck.

---

## A. Model auditability and executable model

### HE-Merck-1 | Executable model
**Recipient:** Merck
**Topic:** Executable model
**Question:** Provide the fully executable, unprotected Microsoft Excel cost-effectiveness model used to generate all results in Section B.3 (including Tables 75–79 and all scenario analyses), with all VBA macros visible and editable, all named ranges accessible, all sheets unhidden, all cells unprotected, and the PAS price for avelumab as a single editable input cell. Provide a separate version with the PAS price set to zero (list price) so the EAG can verify the deflator logic.
**Rationale:** NICE PMG36 requires that the EAG be able to fully interrogate, reproduce and re-run the company base case, PSA, OWSA and all scenarios. Section B.3.12 confirms an Excel workbook was used, but the submission does not state that protection has been removed or that PAS inputs are unlocked for EAG use.

### HE-Merck-2 | R/Stata scripts and analytical code
**Recipient:** Merck
**Topic:** Off-model code
**Question:** Provide the complete R/Stata code (and any other software scripts) used for: (i) parametric survival modelling of OS, PFS and TTD (Sections B.3.3.2 and B.3.3.3); (ii) the Bayesian NMA in `gemtc` (Section B.2.10.4), including JAGS/BUGS model files, MCMC seeds, burn-in, thinning and convergence diagnostics; (iii) the EQ-5D-5L to EQ-5D-3L crosswalk and the linear mixed-effects regression models for utilities (Section B.3.4.2, Table 57); and (iv) any IPD reconstruction from comparator KM curves used in the NMA.
**Rationale:** Survival extrapolations, the NMA and utility regressions are all key drivers of the ICER. Without the scripts, the EAG cannot verify covariates, distributional assumptions, priors, or convergence and cannot reproduce confidential cells in Tables 41–54.

### HE-Merck-3 | User guide and changelog versus TA645
**Recipient:** Merck
**Topic:** Model documentation
**Question:** Provide a user guide for the submitted Excel model and a structured changelog listing every model change relative to the TA645 model (cell-level if possible), including changes to: model structure, cycle length, time horizon, survival curve selection, utility regression specification, AE costing, subsequent therapy distributions and unit costs, end-of-life cost source, RDI handling and general-population mortality cap. Identify which changes are driven by new data (final JAVELIN Renal 101 analysis, SACT) and which are methodological choices made by the company.
**Rationale:** This is an MA review of TA645. PMG36 requires that the EAG can determine which changes vs the original appraisal reflect new evidence and which reflect new modelling choices.

### HE-Merck-4 | Random seeds and PSA reproducibility
**Recipient:** Merck
**Topic:** Reproducibility
**Question:** Confirm and document the random seed(s) used for the 5,000-iteration PSA reported in Table 77 and confirm that re-running the submitted model with that seed reproduces the exact incremental costs, QALYs and ICERs in Table 77 (and the CEACs in Figures 31–33). If different software was used to generate any PSA outputs outside Excel, provide those scripts and seeds.
**Rationale:** Section B.3.9.1 reports mean PSA results across 5,000 iterations but does not document seeds or convergence assessment beyond a visual inspection statement; reproducibility is a PMG36 requirement.

---

## B. Decision problem and scope concordance

### HE-Merck-5 | Comparator coverage for intermediate-/poor-risk
**Recipient:** Merck
**Topic:** Scope concordance — comparators
**Question:** Section B.3.10 and Table 79 present the intermediate-/poor-risk results but explicitly caution that the comparisons "cannot, and thus do not, take into consideration the inherent heterogeneity within this subgroup". Confirm whether Merck considers the intermediate-/poor-risk subgroup to be in or out of scope for decision-making, and provide a fully specified base case (PSA, OWSA, scenarios) for each of the seven scope-listed comparators (cabozantinib, nivolumab + ipilimumab, lenvatinib + pembrolizumab, cabozantinib + nivolumab, pazopanib, sunitinib, tivozanib) with the same level of detail as the favourable-risk base case.
**Rationale:** The NICE final scope (issued September 2024) lists seven comparators in this subgroup. PMG36 requires the company to address the full scope. Restricting full uncertainty analysis to favourable-risk leaves a material portion of the relevant decision unaddressed.

### HE-Merck-6 | PD-L1 subgroup
**Recipient:** Merck
**Topic:** Scope concordance — subgroups
**Question:** The final scope lists "PD-L1 status" as a subgroup. Section B.3.2.1 states this was not explored in the cost-effectiveness modelling on the basis of "clinical expert opinion". Provide either: (i) a cost-effectiveness analysis (deterministic + PSA) for the PD-L1+ subgroup using JAVELIN Renal 101 PD-L1+ OS/PFS/TTD curves (Table 20), or (ii) the full evidence base (number of clinical experts, structured elicitation method, transcripts/summaries) underpinning the decision not to model this subgroup.
**Rationale:** Scope departures require explicit, evidenced justification under PMG36.

### HE-Merck-7 | Updated decision-problem table
**Recipient:** Merck
**Topic:** Decision problem
**Question:** Provide an updated Table 1 (decision problem) that clearly flags as departures from the scope: (i) restriction of the cost-effectiveness base case to the favourable-risk subgroup rather than the all-comers population; (ii) exclusion of PD-L1 status subgroup analysis from the economic model; and (iii) any other deviation. Provide an explicit reference-case checklist (PMG36 Section 4) listing each item as Met / Partially met / Not met with the page reference and justification.
**Rationale:** Section B.1.1 states the submission is consistent with the final scope, but Sections B.3.2.1 and B.3.10 reveal material restrictions to the base case that warrant explicit acknowledgement.

---

## C. Model structure

### HE-Merck-8 | Partitioned survival versus state-transition
**Recipient:** Merck
**Topic:** Model structure
**Question:** Provide the justification for retaining a partitioned survival (PartSA) structure rather than a state-transition Markov or semi-Markov approach, with explicit reference to NICE DSU TSD 19. In particular, address: (i) the structural assumption that OS is independent of PFS; (ii) how this assumption is validated for an IO+TKI combination with potentially long-tailed OS but shorter PFS; and (iii) provide a state-transition scenario analysis (multistate model with PFS→PD, PFS→Death and PD→Death transitions) for comparison.
**Rationale:** DSU TSD 19 recommends that PartSA models be cross-checked against a state-transition structure, particularly where post-progression survival is long and disconnected from progression dynamics, as is the case in IO-treated aRCC.

### HE-Merck-9 | Half-cycle correction
**Recipient:** Merck
**Topic:** Model structure
**Question:** Section B.3.2.2.3 states a 1-week cycle length was used and a half-cycle correction was not applied because of the short cycle length. Provide a scenario applying a half-cycle correction (Simpson's rule or life-table) to costs and outcomes and report its impact on the ICER versus each comparator.
**Rationale:** Even with a short cycle, the cumulative effect across a 40-year horizon is non-trivial; standard practice is to apply or test the correction.

### HE-Merck-10 | Time horizon scenarios
**Recipient:** Merck
**Topic:** Time horizon
**Question:** Table 78 reports 20- and 30-year time horizon scenarios. Provide additional scenarios at 15 years and a sensitivity analysis showing the cumulative incremental costs, LYs and QALYs by year over the full 40-year horizon (incremental QALY accrual profile by year). Report what proportion of incremental QALYs accrue after the end of trial follow-up (~5.67 years) and after 10, 15 and 20 years.
**Rationale:** Section B.3.13 acknowledges substantial extrapolation despite 68-month median follow-up. The committee needs to see how much of the QALY gain is being driven by extrapolation versus observed data, particularly given the long-tail OS dynamics with IO therapy.

---

## D. Survival extrapolation — OS, PFS, TTD

### HE-Merck-11 | Unredacted statistical fit and landmark tables
**Recipient:** Merck
**Topic:** Survival extrapolation transparency
**Question:** Provide unredacted AIC/BIC values and landmark 1-, 2-, 5-, 10-, 15- and 20-year survival estimates for every candidate distribution (Exponential, Weibull, Gompertz, log-logistic, log-normal, generalised gamma) for: avelumab + axitinib OS and PFS; sunitinib OS and PFS; avelumab TTD; axitinib TTD; sunitinib TTD — in both the favourable-risk and intermediate-/poor-risk populations (i.e., redacted cells in Tables 45–54 and Appendix O equivalents).
**Rationale:** Tables 45–54 contain XXXXX redactions for AIC/BIC and landmark estimates that prevent the EAG from assessing whether the selected distribution is supported by the goodness-of-fit evidence. The EAG requires the full numerical evidence base. PAS prices are confidential but AIC/BIC and survival proportions are not.

### HE-Merck-12 | Clinical plausibility overrides
**Recipient:** Merck
**Topic:** Curve selection rationale
**Question:** For each instance where the selected distribution is not the best-fitting model on AIC and BIC, provide a structured justification for the override, including: (i) the specific clinical plausibility argument and which clinical expert(s) endorsed it; (ii) the long-term landmark survival prediction the expert(s) anchored on; (iii) external evidence cited; and (iv) any structured elicitation protocol used. This applies in particular to: avelumab + axitinib OS (log-normal selected; log-logistic ranked 1 on AIC/BIC, Table 41); sunitinib OS (generalised gamma selected; Weibull ranked 1 on AIC/BIC, Table 43); avelumab + axitinib PFS (log-normal selected — best fit, but justify against generalised gamma); avelumab and axitinib TTD (generalised gamma selected; Gompertz/exponential ranked 1, Tables 49, 51).
**Rationale:** Section B.3.3 invokes clinical expert opinion repeatedly to overrule statistical fit. DSU TSD 14 requires that such overrides be transparent, evidenced and reproducible.

### HE-Merck-13 | Sunitinib OS curve choice and unrealistic PSA tails
**Recipient:** Merck
**Topic:** Sunitinib OS extrapolation
**Question:** Section B.3.9.1 states "some probabilistic draws of the generalised gamma model for the sunitinib arm (used to model OS) result in unrealistic extrapolations, and therefore the mean LYG is higher than what is seen for the deterministic analysis" (Table 77: PSA LYG 6.90 vs deterministic 6.45 for sunitinib). Provide: (i) the proportion of PSA iterations that produced "unrealistic" sunitinib OS; (ii) the definition used to classify an iteration as unrealistic; (iii) a re-run of the PSA with a curve choice (e.g., Weibull) that does not generate these implausible tails; and (iv) a base case scenario using the best-fitting distribution (Weibull, Table 43).
**Rationale:** A curve known to generate implausible PSA tails biases the PSA mean upward in the sunitinib arm, mechanically reducing the avelumab + axitinib incremental QALY gain and inflating cost-effectiveness. This is a material driver of the ICER.

### HE-Merck-14 | Independent OS/PFS extrapolation and intersection
**Recipient:** Merck
**Topic:** PartSA curve integrity
**Question:** Confirm that for every base case and scenario combination of OS and PFS curves, PFS does not exceed OS at any cycle for any arm. Provide a check across the full 40-year horizon and identify any cycles requiring adjustment. State how the model handles such intersections (truncation, refitting, or other).
**Rationale:** Independent fitting of OS and PFS within a PartSA framework can produce PFS > OS in tails; this needs documented handling per DSU TSD 19.

### HE-Merck-15 | General-population mortality cap
**Recipient:** Merck
**Topic:** Background mortality
**Question:** Section B.3.3.2 states curves were capped so that the probability of death is never lower than the age- and sex-adjusted general population. Provide: (i) the source life table (ONS year), (ii) the sex split used, (iii) the algebra of the cap (instantaneous hazard vs survival proportion), and (iv) the cycle at which each base-case OS curve is first bound by the general-population mortality cap.
**Rationale:** The point at which the cap binds materially influences long-term OS and the magnitude of extrapolated QALY gain.

### HE-Merck-16 | Treatment switching in JAVELIN Renal 101
**Recipient:** Merck
**Topic:** Subsequent therapy and OS
**Question:** Section B.3.5.4 indicates 86.23% of JAVELIN Renal 101 favourable-risk sunitinib-arm patients received subsequent nivolumab. State whether this constitutes treatment switching as defined in DSU TSD 16 and, if so, provide adjusted OS for the sunitinib arm using a two-stage (Latimer) and/or RPSFT/IPCW approach. Provide a scenario in the base case using switching-adjusted sunitinib OS.
**Rationale:** Substantial subsequent IO use in the control arm of a trial used to inform an extrapolated OS comparison may bias the comparator OS upward in a UK setting where subsequent IO is partially available; DSU TSD 16 mandates exploration of switching adjustment.

### HE-Merck-17 | TTD versus deterministic capping at stopping rule
**Recipient:** Merck
**Topic:** Treatment duration
**Question:** Confirm whether the JAVELIN Renal 101 protocol included a stopping rule for avelumab (e.g., a 2-year maximum, or to disease progression only) and whether TTD in the model is governed by the parametric extrapolation alone or by a deterministic cap. If no stopping rule is applied in the base case, provide scenario analyses with a 2-year and a 3-year deterministic cap on avelumab treatment (consistent with TA858 and TA964 precedent) and report the impact on costs, QALYs and the ICER.
**Rationale:** Most recent NICE IO appraisals in aRCC have considered stopping-rule scenarios; the submission does not appear to.

### HE-Merck-18 | TTD versus PFS relationship
**Recipient:** Merck
**Topic:** TTD coherence
**Question:** Confirm whether TTD can exceed PFS in any cycle for any arm in the base case or any scenario (e.g., generalised gamma TTD vs log-normal PFS for avelumab + axitinib). Provide a check and any adjustment logic. Quantify the proportion of treatment-arm patients still receiving drug at 5, 10 and 15 years under each base case curve.
**Rationale:** Long generalised-gamma TTD tails can imply patients on treatment well beyond progression, which is inconsistent with the model's assumption (B.3.2.2.1) that treatment stops on or before progression.

---

## E. Clinical equivalence assumptions

### HE-Merck-19 | TKI equivalence (sunitinib = pazopanib = tivozanib)
**Recipient:** Merck
**Topic:** Comparator efficacy assumption
**Question:** Section B.3.3 assumes OS, PFS and TTD are identical across sunitinib, pazopanib and tivozanib, leaving only drug acquisition cost as a distinguishing feature. Provide: (i) the NMA-derived hazard ratios (with credible intervals) for OS and PFS for pazopanib and tivozanib versus sunitinib in the favourable-risk subgroup (or, if not available in favourable-risk, the all-comers HRs with a justification of generalisability); (ii) a PSA with HRs drawn from the NMA posterior; and (iii) a deterministic sensitivity analysis varying each comparator HR across the 95% CrI bounds. Report whether the ICER changes ranking among comparators under any plausible HR.
**Rationale:** The current modelling reduces these three comparators to a one-dimensional acquisition-cost comparison and assumes zero uncertainty on TKI relative efficacy. The Manz et al. NMA cited (B.3.3) shows TKIs do not differ "significantly", which is not equivalent to identical effect; the 95% CI must be quantified.

### HE-Merck-20 | AE rate equivalence between TKIs
**Recipient:** Merck
**Topic:** Comparator AE equivalence
**Question:** Table 68 applies a single AE cost (£523.73) to sunitinib, tivozanib and pazopanib. Provide AE incidence rates from the pivotal trials of tivozanib (TIVO-1) and pazopanib (COMPARZ or pivotal RCT) for the grade ≥3 events in Table 56, and a scenario in which AE costs and frequencies are treatment-specific.
**Rationale:** Pazopanib has a distinct hepatic AE profile and tivozanib a distinct hypertension profile; pooling AE costs masks comparator-specific resource use.

---

## F. Utilities and HRQoL

### HE-Merck-21 | Utility values and confidence intervals
**Recipient:** Merck
**Topic:** Utility transparency
**Question:** Provide unredacted progression-free and post-progression utility values (mean, SE, 95% CI), the full variance-covariance matrix from the Model 1 and Model 2 regressions (Table 57), the number of observations contributing to each health state, and the number of unique patients in the favourable-risk subgroup contributing EQ-5D-5L data. State the proportion of post-progression observations available and whether any health state utility was extrapolated from a small sample.
**Rationale:** Utility values are redacted in Tables 57, 58 and 60. Without these the EAG cannot assess the precision of the QALY estimates or test the regression specification.

### HE-Merck-22 | Treatment status in utility model
**Recipient:** Merck
**Topic:** Utility regression specification
**Question:** Model 2 (Table 57) explored an on-treatment indicator and found a non-significant negative effect (p=0.142). Provide: (i) the corresponding utility values used to generate Table 78's "Model 2" scenario; (ii) a structured argument for selecting Model 1 over Model 2 as base case, given that on-treatment quality of life is conceptually distinct and that Model 2 would penalise the active arm with longer treatment durations; and (iii) provide a scenario where Model 2 is the base case.
**Rationale:** Selecting Model 1 over Model 2 systematically favours the longer-TTD arm (avelumab + axitinib). The choice should be evidenced rather than defaulted.

### HE-Merck-23 | Age adjustment
**Recipient:** Merck
**Topic:** Age-related utility decrement
**Question:** Confirm that the Ara & Brazier (2010) multiplier is applied to the cohort's age in each cycle (not the baseline age) and that male/female utility coefficients reflect the cohort sex split. Provide a scenario using the more recent Hernández-Alava et al. EQ-5D-3L UK general population norms and report sensitivity.
**Rationale:** Page 126 of the submission shows the Ara & Brazier formula but does not state whether the multiplier is recalculated cycle-by-cycle.

### HE-Merck-24 | AE disutility exclusion
**Recipient:** Merck
**Topic:** AE disutility
**Question:** Section B.3.4.4 excludes explicit AE disutilities on the grounds that they are captured in the EQ-5D-derived health state utilities. The EQ-5D-5L was administered every 6 weeks (Section B.3.4.1) — provide evidence that high-grade, short-duration AEs (e.g., infusion reactions, immune-mediated events) were observed within the EQ-5D sampling window. Provide a scenario adding AE disutilities for grade ≥3 events sourced from published literature (e.g., Lloyd 2006, Beusterien 2010) and report the ICER impact.
**Rationale:** Six-weekly EQ-5D collection is unlikely to capture transient AEs; the assumption that disutility is fully internalised is empirically untested.

### HE-Merck-25 | Cross-TA utility consistency
**Recipient:** Merck
**Topic:** Utility precedent
**Question:** Table 59 lists prior aRCC TA utilities. Note that the post-progression utility used in the current submission appears higher than the upper bound of prior TAs (Section B.3.4.3 mentions XXXXX vs 0.7600 from TA417). Provide a scenario adopting (a) the TA858 lenvatinib + pembrolizumab utility values (redacted in Table 59 — request company-confidential disclosure to EAG), and (b) the TA964 cabozantinib + nivolumab utility values, and report the ICER impact. Identify the population definition used to derive utilities in each prior TA (1L versus 2L+, all comers vs IMDC-risk subgroup).
**Rationale:** Cross-TA consistency is required under PMG36; using a utility above prior precedent in a long-tailed model favours the intervention.

---

## G. Costs

### HE-Merck-26 | BNF, NHS Reference Cost and PSSRU vintages
**Recipient:** Merck
**Topic:** Cost sources
**Question:** Confirm the BNF access date for all drug prices in Table 61 and subsequent therapy unit costs in Table 70. Confirm the NHS National Cost Collection year (Table 64 uses 2022/23; Table 67 uses 2021/22 — explain the inconsistency). Confirm the PSSRU year (Table 66 uses 2023). Provide a re-costed scenario using consistently 2022/23 reference costs and PSSRU 2023 with inflation indices documented, and state the inflation index used (e.g., NHSCII).
**Rationale:** The submission uses inconsistent reference cost vintages across cost categories (Tables 64, 65, 66, 67), potentially biasing total costs.

### HE-Merck-27 | RDI handling
**Recipient:** Merck
**Topic:** Relative dose intensity
**Question:** Table 63 applies RDIs (avelumab 91.7%, axitinib 83.7%, sunitinib 81.9%, tivozanib 94.0%, pazopanib 86.0%) to drug acquisition costs. State explicitly: (i) whether RDI is applied to acquisition cost only or also to administration cost; (ii) whether RDI is applied to per-cycle drug cost or to wastage-adjusted cost; (iii) for IV avelumab dosed as 4×200mg vials with no wastage, justify how RDI<100% reduces cost when the vial count is integer; and (iv) provide a scenario with RDI=100% for all treatments (per the EMA/BNF licensed dose schedule) and report the ICER.
**Rationale:** The OWSA (Section B.3.9.2) reports that axitinib RDI has the largest single impact on results. The mechanism by which RDI reduces avelumab acquisition (a flat-dose IV with no wastage) needs to be explicit.

### HE-Merck-28 | Avelumab dosing schedule
**Recipient:** Merck
**Topic:** Avelumab dosing
**Question:** Provide a scenario analysis using a 10 mg/kg every-2-week (Q2W) dose and a Q3W weight-based dose if these are within the marketing authorisation, and reconcile with the 800 mg flat Q2W base case (Section B.3.2.3.1). Report the cost impact for an average UK patient weight.
**Rationale:** Although the SmPC specifies 800 mg Q2W, sensitivity to dose schedule changes is standard in IO appraisals.

### HE-Merck-29 | Axitinib generic pricing scenario
**Recipient:** Merck
**Topic:** Generic axitinib
**Question:** Table 78 reports axitinib price reductions of 50–90%. Provide: (i) the redacted XXXXXXX date in Section B.3.5.1.1 stating when branded axitinib loses exclusivity in the UK; (ii) evidence supporting the 88.89% sunitinib branded-to-generic decrement as a proxy for axitinib; and (iii) a probabilistic scenario in which axitinib price is sampled from a distribution reflecting actual generic-entry uncertainty over the model horizon. State whether NICE should base its recommendation on list price, current generic, or anticipated future generic price (per PMG36 Section 4.4).
**Rationale:** The company's interpretation in Section B.3.13 relies heavily on anticipated future generic pricing. Decisions must be made on prices in force at the time of guidance, so this requires explicit handling.

### HE-Merck-30 | Subsequent therapy reallocation rationale
**Recipient:** Merck
**Topic:** Subsequent therapy distribution
**Question:** Table 69 removes subsequent nivolumab from the avelumab + axitinib arm (86.23% in sunitinib arm in JAVELIN Renal 101) and re-allocates to other treatments. Provide: (i) the re-allocation algorithm explicitly (proportional rescaling vs other); (ii) the proportion of avelumab + axitinib favourable-risk patients in JAVELIN Renal 101 who actually received subsequent nivolumab in the trial — and confirm that this is removed entirely; (iii) the impact of subsequent treatment cost asymmetry (£38,287 ave+axi vs £74,883 sunitinib, Table 72) on the incremental cost — what proportion of the total incremental cost is attributable to subsequent therapy savings in the intervention arm? (iv) a scenario where subsequent therapy distributions are equal across arms based on observed UK practice (UK ROC); and (v) a scenario aligned with the TA645 assumption.
**Rationale:** Removing nivolumab from one arm but not the other and re-allocating yields a £36,596 (49%) cost saving in the intervention arm, which is a material — and potentially structural — driver of the ICER. Section B.3.5.4 acknowledges the assumption but does not quantify its impact.

### HE-Merck-31 | Subsequent therapy dosing assumptions
**Recipient:** Merck
**Topic:** Subsequent therapy duration and dosing
**Question:** Table 71 cites mean TTD values for subsequent therapies sourced from TA542 and TA498. Provide: (i) justification that mean TTD values from prior 2018 appraisals remain valid in 2024–25 UK practice; (ii) confirmation that the £59,850 nivolumab subsequent cost reflects list price (PAS confidential); and (iii) confirmation that the cost per single course assumes no further subsequent line beyond 2L+ and the impact of allowing third-line treatment.
**Rationale:** Subsequent treatment costs are applied as a one-off lump on PFS exit and their magnitude (Table 72) shows they are decisive in the cost difference between arms.

### HE-Merck-32 | Resource use frequencies
**Recipient:** Merck
**Topic:** HCRU
**Question:** Table 65 sources HCRU frequencies from TA581 (2019). Provide validation from UK clinical experts (in 2024) confirming current frequencies for CT scans (0.08/week in PFS, 0 in PD), GP visits, blood tests, and community nurse visits in current NHS practice for IMDC favourable-risk aRCC. Provide a scenario using current published UK resource use studies or the UK ROC dataset (Frazer 2024).
**Rationale:** Resource use in active disease has likely changed since 2019 with the shift to IO-containing regimens; reliance on TA581 frequencies is unverified.

### HE-Merck-33 | AE costs uniformity
**Recipient:** Merck
**Topic:** AE unit costs
**Question:** Table 67 assigns a single £801.11 non-elective short stay cost to all grade ≥3 AEs. Provide a scenario using AE-specific HRG cost weightings (e.g., RA01 for diarrhoea, LB28 for ALT elevation, EB04Z for hypertension management) and report the ICER impact, particularly for the hypertension differential between arms (27.7% vs 17.5%, Table 56).
**Rationale:** The single-cost assumption is structurally biased against the arm with more high-cost-real-AE incidence and ignores material differences in AE management costs.

### HE-Merck-34 | End-of-life cost source
**Recipient:** Merck
**Topic:** EoL cost
**Question:** Table 73 uses Round et al. (2015) inflated by PSSRU index to £7,482.71. Provide a scenario using more recent end-of-life cost estimates (e.g., Marie Curie / Nuffield Trust 2022, or Georghiou & Bardsley) and a scenario consistent with the end-of-life cost in TA858 / TA964 (cross-TA consistency).
**Rationale:** 2015 EoL costs may not reflect current pathways and the assumption is shared across both arms but at different timing, so the magnitude matters.

---

## H. Treatment stopping rules and waning

### HE-Merck-35 | Treatment effect waning
**Recipient:** Merck
**Topic:** Waning
**Question:** Provide treatment-effect waning scenarios in which the OS hazard ratio between avelumab + axitinib and sunitinib converges to 1 by year 5, year 7 and year 10 after treatment discontinuation (linear taper), and an alternative scenario in which only post-progression OS is subject to waning. Report the ICER impact for each.
**Rationale:** PMG36 and recent NICE precedent (TA858, TA964) require explicit waning analyses for IO+TKI combinations because durability of immunotherapy benefit beyond treatment discontinuation is uncertain. The submission does not appear to include a waning scenario.

---

## I. Results presentation

### HE-Merck-36 | Unredacted base case ICERs
**Recipient:** Merck
**Topic:** ICER transparency
**Question:** Provide unredacted deterministic and probabilistic ICERs versus each comparator (favourable-risk and intermediate-/poor-risk) at the avelumab PAS price, in line with the standard NICE practice of disclosing PAS-discounted ICERs to the EAG (Tables 75–77, 79). Provide also list-price ICERs and the disaggregated incremental costs and QALYs by category (drug acquisition, administration, AE, monitoring, subsequent therapy, EoL) and by health state (PFS, PD), as required by NICE template Appendix J.
**Rationale:** Tables 75–79 redact most ICERs and incremental NMBs. The EAG must see the actual numerical outputs to verify consistency and reproduce results.

### HE-Merck-37 | Internal consistency check
**Recipient:** Merck
**Topic:** ICER consistency
**Question:** Confirm that the ICERs reported in the executive summary, Section B.3.8 body text, Table 75 (deterministic), Table 77 (probabilistic), and any scenario tables in Appendix O are mutually consistent. State which is the primary base case for decision-making (deterministic vs probabilistic at PAS price) and reconcile any discrepancies. Note that Section B.3.9.1 acknowledges total costs/QALYs for ave + axi "vary slightly across the results presented" — quantify this variation.
**Rationale:** Pairwise PSA arrangement can produce inconsistent total costs and QALYs in the same arm across comparisons, which complicates committee interpretation.

### HE-Merck-38 | Deterministic versus probabilistic divergence
**Recipient:** Merck
**Topic:** PSA validity
**Question:** Quantify the divergence between deterministic and probabilistic LYG/QALY for the sunitinib arm (deterministic 6.45 vs PSA 6.90 LYG, a 7% increase). Provide the source of divergence (curve choice, parameter correlation, distribution sampling) and rerun PSA with curves that do not generate implausible tails (see HE-Merck-13). State which result the EAG should treat as the company base case.
**Rationale:** A 7% disagreement between deterministic and probabilistic means is itself diagnostic of structural issues in the survival sampling.

---

## J. Sensitivity and scenario analyses

### HE-Merck-39 | Comprehensive OWSA tornado
**Recipient:** Merck
**Topic:** OWSA scope
**Question:** Figures 37–39 show only the top 10 parameters. Provide expanded tornado plots showing the top 30 parameters by INMB impact, with the full list of OWSA parameters varied, their base values, ranges, distributional assumptions, and source. Confirm that correlated parameters (survival coefficients) were excluded as stated, and provide a sensitivity table with the ranges used (10% of mean default — provide justification for parameters lacking variance data).
**Rationale:** PMG36 expects an exhaustive OWSA; the simplifying assumption "SE = 10% of mean" needs to be transparent for every parameter affected.

### HE-Merck-40 | CEAC at multiple thresholds
**Recipient:** Merck
**Topic:** Probabilistic cost-effectiveness
**Question:** Provide the unredacted probability that avelumab + axitinib is cost-effective at £20,000, £30,000, £50,000 (severity 1.2× multiplier proxy) per QALY for each comparator (sunitinib, tivozanib, pazopanib) at PAS price. Provide the underlying scatter plots and the proportion of PSA iterations in each quadrant of the CE plane.
**Rationale:** Figures 31–36 present the CEACs and CE planes but the underlying probabilities are not reported numerically.

### HE-Merck-41 | Non-reference-case discount rates
**Recipient:** Merck
**Topic:** Discount rate
**Question:** Table 78 reports 1.5% and 6.0% discount rate scenarios. State explicitly that the 3.5% reference-case rate is the base case and that the 1.5% scenario is not justified as a primary analysis (per PMG36 Section 4.5, which permits 1.5% only under specific severity/restoration-of-health criteria, not applicable to first-line aRCC with a 65.41% proportional QALY shortfall and no severity modifier per Section B.3.6).
**Rationale:** PMG36 restricts the use of 1.5% to defined circumstances; presenting it as a scenario should not imply primacy.

---

## K. Subgroups

### HE-Merck-42 | Favourable-risk subgroup full uncertainty
**Recipient:** Merck
**Topic:** Subgroup uncertainty
**Question:** Confirm whether all PSA, OWSA and scenario analyses in Section B.3.9 reflect the favourable-risk subgroup specifically (n=190 in JAVELIN Renal 101), or are drawn from the ITT population in any way (e.g., AE rates in Table 56 are stated to be ITT). Re-run the PSA with all parameters sampled from the favourable-risk subgroup where applicable.
**Rationale:** AE rates are ITT-derived (Table 56) and applied to a favourable-risk base case — this is an inconsistency that may bias the comparator AE cost.

### HE-Merck-43 | Intermediate-/poor-risk subgroup analyses
**Recipient:** Merck
**Topic:** Subgroup analyses
**Question:** Provide for each of the seven intermediate-/poor-risk comparators a full deterministic ICER (Table 79 unredacted), PSA, OWSA tornado, scenario set (matching the favourable-risk scenario set in Table 78), CEAC and CE plane. Confirm whether the warning in Section B.3.10 about heterogeneity also applies to TKI comparisons within this subgroup or only to IO comparisons.
**Rationale:** Section B.3.10 caveats the subgroup but still provides headline ICERs; the EAG and committee need full uncertainty characterisation to take any decision on this subgroup.

### HE-Merck-44 | ITT analysis
**Recipient:** Merck
**Topic:** ITT analysis
**Question:** Section B.3.2.1 states ITT results are provided in Appendix O. Confirm whether the ITT analysis is a sensitivity or a decision-relevant analysis, and report the headline ICER and incremental QALY for each scope-listed comparator at PAS price.
**Rationale:** Although the company de-prioritises ITT, the NICE final scope population is "Adults with untreated advanced renal cell carcinoma" without subgroup restriction; the ITT case remains decision-relevant.

---

## L. Validation

### HE-Merck-45 | Model validation
**Recipient:** Merck
**Topic:** Validation
**Question:** Section B.3.12 describes internal QC and three clinical expert consultations. Provide: (i) the completed ISPOR-SMDM validation checklist (face validity, internal validity, cross-validity vs prior TA645 model, external validity vs SACT, UK ROC, NDRS and other UK registry data); (ii) calibration plots of modelled sunitinib OS (favourable-risk) versus the SACT first-line TKI monotherapy cohort (Frazer et al. 2024) and the IMDC original favourable-risk cohort; and (iii) named clinical experts, declared conflicts of interest, the elicitation method used, and full transcripts/summaries of their input.
**Rationale:** PMG36 and the NICE TA template Appendix J require structured validation; the current description is informal and unverifiable.

### HE-Merck-46 | External calibration to SACT
**Recipient:** Merck
**Topic:** External validity
**Question:** The SACT dataset on avelumab + axitinib was collected under the CDF managed access agreement (Section B.2.8). Provide the SACT-derived OS and TTD for the avelumab + axitinib favourable-risk subgroup (or all-comers, as available) and compare against the modelled curves at 6, 12, 18, 24, 36 and 48 months (consistent with Tables 23, 24). Discuss any discrepancy and its implications for the favourable-risk extrapolation.
**Rationale:** The MA review exists precisely to test trial extrapolations against real-world UK data; this calibration must be made explicit in the economic model.

---

## M. NICE reference case and cross-TA consistency

### HE-Merck-47 | Cross-TA comparison
**Recipient:** Merck
**Topic:** Cross-TA consistency
**Question:** Provide a structured cross-TA comparison table benchmarking the key model inputs of this submission against TA645 (prior avelumab + axitinib), TA858 (lenvatinib + pembrolizumab), TA964 (cabozantinib + nivolumab) and TA780 (nivolumab + ipilimumab) on the following dimensions: model structure, cycle length, time horizon, OS/PFS curves, utility values (PF, PD), AE handling, RDI, subsequent therapy approach, EoL cost, discounting, and treatment waning. Identify and justify each departure from prior precedent.
**Rationale:** Cross-TA consistency is a routine EAG requirement to identify outlier modelling choices.

---

## N. Managed access and equality

### HE-Merck-48 | Routine vs managed access entry and exit criteria
**Recipient:** Merck
**Topic:** Recommendation modality
**Question:** State explicitly whether Merck is seeking: (a) routine commissioning recommendation (favourable-risk and/or intermediate-/poor-risk), (b) Cancer Drugs Fund / managed access reinstatement, or (c) something else. If managed access is sought, define the proposed data collection set, the exit criteria for the new MA review, and the decision-uncertainty rationale.
**Rationale:** TA645 placed avelumab + axitinib in the CDF; the current MA review must resolve that uncertainty. The submission does not explicitly state the requested commissioning modality in the cost-effectiveness section.

---

## O. Reproducibility and final checks

### HE-Merck-49 | Full results reproducibility
**Recipient:** Merck
**Topic:** Reproducibility
**Question:** Confirm that, using the submitted executable model with the supplied seeds and inputs, the EAG can reproduce, cell-exact: Table 75 (deterministic), Table 76 (NHB), Table 77 (probabilistic), Table 78 (scenarios) and Table 79 (intermediate-/poor-risk subgroup). State any results that are not fully reproducible from the model alone and provide the supporting workbook/script files for those.
**Rationale:** Standard PMG36 requirement.

### HE-Merck-50 | Severity modifier and proportional QALY shortfall
**Recipient:** Merck
**Topic:** Severity
**Question:** Section B.3.6 calculates absolute and proportional QALY shortfalls of 8.04 and 65.41% for favourable-risk and confirms no severity modifier applies. Provide the equivalent calculation for the intermediate-/poor-risk subgroup and the ITT population (referenced as in Appendix O). Confirm the source of expected lifetime QALYs for the equivalent general population (Schneider R-Shiny tool inputs) and identify the disease-cohort QALY input — recompute using the modelled QALYs from the current submission rather than literature.
**Rationale:** Severity weighting may differ across subgroups and affect the decision threshold; the calculation logic must be transparent.

---

### Question count
- HE-Merck: 50

Total clarification questions: 50
