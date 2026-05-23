# TA1120 — Statistician clarification questions

**Reviewer role:** EAG Statistician
**Appraisal:** TA1120 — Avelumab + axitinib for untreated advanced RCC (MA review of TA645)
**Source:** Merck submission (Document B, 07 November 2024 / v3.0 21 February 2025)
**Reference frameworks cited:** NICE DSU TSD 14, 16, 17, 19, 20, 21 (as relevant)

---

## A. Proportional hazards testing

### STAT-Merck-1 — Reporting of PH tests
**Recipient:** Merck
**Topic:** Completeness of PH diagnostics for OS, PFS and the NMA inputs
**Question:** For every endpoint (OS, PFS, TTD) and every comparator KM curve included in the NMA (JAVELIN Renal 101, CABOSUN, CheckMate 9ER, CheckMate 214, CLEAR), provide a complete set of PH diagnostics:
(a) Grambsch–Therneau global Schoenfeld residual test (chi-square, df, p-value) and per-treatment-arm tests, with the time transformation (KM, identity, log, rank) stated and justified.
(b) Log-cumulative hazard ( log[−log S(t)] ) plots against log(time), with crossings and parallelism explicitly annotated.
(c) Scaled Schoenfeld residual plots with smoothed lines and 95% bands.
(d) The smoothed log-HR(t) from a Cox model with a time-varying coefficient (Therneau–Grambsch parameterisation) for the avelumab + axitinib vs sunitinib contrast in (i) ITT, (ii) IMDC favourable-risk, (iii) IMDC intermediate-/poor-risk, and (iv) PD-L1+ subgroups at the final analysis cut.
**Rationale:** Document B Appendix N is referenced (Section B.2.10.2) but only one summary sentence appears in Document B — "On balance, the PH assumption was considered reasonable... owing to the number of comparisons required and the subjectivity associated with assessing the PH assumption." NICE DSU TSD 14 and TSD 21 require explicit quantitative and visual PH testing as the precondition for selecting between PH and non-PH/flexible models; "subjectivity" is not a valid statistical justification.

### STAT-Merck-2 — PH assumption used to enable PH NMA despite likely violation
**Recipient:** Merck
**Topic:** Internal consistency of the PH decision
**Question:** Reconcile the position that the PH assumption is reasonable "for the purpose of estimating relative effects for the model" (Section B.2.10.2 / B.2.10.6) with (a) the visual non-proportionality apparent in the JAVELIN Renal 101 OS KM curves (favourable-risk OS curves cross/separate only after ~30 months — Section B.2.6.1.1), and (b) the well-documented delayed-effect signature of IO+TKI vs TKI seen in CheckMate 214, CheckMate 9ER and CLEAR. State the formal statistical criterion (test, threshold) that defined "reasonable" in this submission, and provide pairwise PH test results for every contrast in the NMA.
**Rationale:** TSD 14 / TSD 19 / TSD 21. Selecting a constant-HR NMA when delayed treatment effects are biologically plausible and visually apparent risks systematic mis-estimation of long-term relative effects against IO+IO and IO+TKI competitors.

### STAT-Merck-3 — Asymmetric handling of PH "fail" vs "fail-to-reject"
**Recipient:** Merck
**Topic:** Decision rule consistency
**Question:** State the pre-specified rule by which a Schoenfeld test result was treated as evidence in favour of PH or against PH, including the multiple-testing strategy across endpoints and subgroups. Provide a table cross-referencing PH test p-values to the curve-selection decisions (independent vs joint fits, constant-HR vs time-varying HR NMA).
**Rationale:** Without a pre-specified rule, post-hoc curve selection biases extrapolation in favour of the sponsor's arm. TSD 14, §3.

---

## B. Survival distribution selection and extrapolation

### STAT-Merck-4 — Full AIC/BIC tables and joint vs independent fits
**Recipient:** Merck
**Topic:** Reporting completeness of parametric survival model (PSM) goodness-of-fit
**Question:** Provide the numerical AIC and BIC values (currently redacted as "XXXXX" in Tables 45, 47, 49, 51, 53 — favourable-risk PFS, sunitinib PFS, avelumab TTD, axitinib TTD, sunitinib TTD) for **all** candidate distributions (exponential, Weibull, Gompertz, log-normal, log-logistic, gamma, generalised gamma) and for **joint** as well as independent fits. Repeat for OS and PFS in the intermediate-/poor-risk and ITT populations (Appendix O).
**Rationale:** TSD 14 requires both joint and independent fits and a transparent goodness-of-fit table to justify departures. The OS difference between Weibull (best by AIC/BIC for sunitinib) and the selected generalised gamma is large at 10 years (15.5% vs 18.6%) and the choice materially affects ICERs.

### STAT-Merck-5 — Log-normal OS for avelumab + axitinib: justification beyond AIC/BIC
**Recipient:** Merck
**Topic:** Base-case OS curve choice (favourable-risk)
**Question:** The log-normal was selected for avelumab + axitinib OS but a different distribution (generalised gamma) was selected for sunitinib OS, despite the Weibull being ranked AIC/BIC-best for sunitinib (Tables 41, 43). Provide: (a) a side-by-side plot of all six fitted curves over the trial follow-up and to year 40 for both arms, (b) Cox–Snell residual plots, (c) the resulting implied HR(t) profile for each pairing, and (d) external validation against SACT favourable-risk OS and the Nathan et al. EAMS cohort. Justify why curves implying different baseline hazard shapes for sunitinib in the same risk group (different choices for OS vs PFS) are clinically plausible.
**Rationale:** Mixing distribution families across arms generates time-varying implicit HRs which contradict the submission's stated PH conclusion; this needs explicit reconciliation under TSD 14 §3.4 and TSD 21.

### STAT-Merck-6 — PSA instability of the generalised gamma sunitinib OS fit
**Recipient:** Merck
**Topic:** Convergence and PSA stability
**Question:** Section B.3.9.1 reports that "some probabilistic draws of the generalised gamma model for the sunitinib arm (used to model OS) result in unrealistic extrapolations, and therefore the mean LYG is higher than what is seen for the deterministic analysis". State: (a) how many of the 5,000 PSA draws produced extrapolations classified as unrealistic; (b) the criterion used to define "unrealistic"; (c) whether any draws were excluded or constrained; (d) the maximum likelihood point estimate, Hessian, and condition number; (e) the parameter correlation matrix and Cholesky decomposition used; (f) provide alternative PSA results truncating mean survival to general-population life expectancy and using a more stable distribution (e.g. Weibull, which had the best AIC/BIC).
**Rationale:** Implausible PSA draws inflate the comparator's modelled survival and reduce the ICER, advantaging the intervention. TSD 14 §7 and the NICE reference case require PSA to be a valid characterisation of joint parameter uncertainty.

### STAT-Merck-7 — Curve-crossing in OS favourable-risk
**Recipient:** Merck
**Topic:** Plausibility of long-term extrapolations
**Question:** The KM curves for OS in the favourable-risk subgroup only separate from ~30 months (Section B.2.6.1.1; Figure 6). Show: (a) the modelled cumulative hazard ratio of avelumab + axitinib vs sunitinib over 0–40 years under the base-case (log-normal/generalised gamma) pairing; (b) whether the modelled HR ever reverses (HR>1) during the lifetime horizon; (c) the impact on the ICER of imposing HR≥1 at all times after year T, where T is the end of trial follow-up.
**Rationale:** Independent extrapolation can imply implausible long-term effects (TSD 14 §3.4; TSD 21).

### STAT-Merck-8 — External validation against UK real-world data
**Recipient:** Merck
**Topic:** Validation against SACT and EAMS cohorts
**Question:** For each base-case OS and PFS curve, overlay (a) the trial KM, (b) the chosen parametric extrapolation, and (c) the SACT CDF cohort KM and Nathan et al. EAMS KM (with 95% CIs). Provide the absolute discrepancy at 12, 24, 36 and 48 months by IMDC subgroup, and the supporting calibration metric (e.g., observed-vs-expected ratio with 95% CI).
**Rationale:** Section B.2.8 reports SACT and Nathan et al. real-world OS/PFS but these are not used to validate the modelled curves; TSD 14 §6 and the NICE reference case require external validation where data permit.

---

## C. NMA methodology

### STAT-Merck-9 — FE vs RE choice in single-study-per-edge network
**Recipient:** Merck
**Topic:** Fixed-effects justification
**Question:** Both OS and PFS NMAs reported essentially identical DIC for fixed- and random-effects (OS: 9.99 vs 9.99; PFS: 9.99 vs 9.97 — Section B.2.10.5). Explain how a fixed-effects model was preferred on the basis of a 0.02 DIC difference. Provide the posterior summary for τ (between-trial heterogeneity SD) under (i) the non-informative uniform prior used in the submission, (ii) a half-normal(0, 0.5) prior and (iii) a log-normal(−2.56, 1.74) Turner-class informative prior for survival HRs (per TSD 17). Report pD, total residual deviance vs number of data points, and report between-study heterogeneity I².
**Rationale:** TSD 17 explicitly cautions against fixed-effects models in single-study-per-edge networks and recommends informative priors on τ for sparse networks.

### STAT-Merck-10 — Constant-HR NMA versus flexible NMA
**Recipient:** Merck
**Topic:** Time-varying HR / fractional polynomial NMA
**Question:** Given the visual non-proportionality apparent in JAVELIN Renal 101, CheckMate 214, CheckMate 9ER and CLEAR, conduct a fractional polynomial NMA per TSD 19 (FP1 and FP2 across the recommended power grid, with FE and RE models) using the published KM data. Present (a) DIC/DIC component comparison vs the PH NMA, (b) plotted HR(t) for each comparator, (c) re-projected long-term mean survival, and (d) the impact on the cost-effectiveness ICERs in the intermediate-/poor-risk subgroup.
**Rationale:** TSD 19 specifies FP NMA as the appropriate response when PH is violated; the dismissal "deemed unlikely to yield markedly different conclusions" (Section B.2.10.6) is not an empirical demonstration.

### STAT-Merck-11 — MCMC convergence diagnostics
**Recipient:** Merck
**Topic:** Convergence reporting
**Question:** For every NMA model (FE/RE × OS/PFS × subgroup), provide: number of chains, burn-in, post-burn-in iterations, thinning interval, Brooks–Gelman–Rubin R-hat for each monitored parameter, effective sample size (ESS), trace plots, density plots, autocorrelation plots and the criterion that triggered the "increased burn-in where there was evidence MCMC had not converged" (Section B.2.10.4).
**Rationale:** TSD 17 requires this minimum diagnostic set; Section B.2.10.4 only states "minimum 50,000" without specifying that this criterion was met for every reported analysis.

### STAT-Merck-12 — Network heterogeneity and inconsistency
**Recipient:** Merck
**Topic:** Within-network heterogeneity in IMDC intermediate-/poor-risk subgroup
**Question:** Section B.2.10.3 states I² and inconsistency cannot be evaluated because the network has no loops and one trial per edge. Provide a node-splitting / unrelated-mean-effects sensitivity analysis where feasible, and a quantitative assessment of effect modifiers across trials (proportion poor vs intermediate, PD-L1+, prior nephrectomy, time of recruitment, region) — both narratively and with meta-regression where possible. Indicate, by quantitative imbalance metrics, which comparisons are most at risk of bias.
**Rationale:** TSD 17 §7 and TSD 20 require explicit handling of effect-modifier imbalance in single-edge networks.

### STAT-Merck-13 — Equivalence assumption for TKI monotherapies
**Recipient:** Merck
**Topic:** Pazopanib/tivozanib = sunitinib assumption
**Question:** The base case sets pazopanib and tivozanib equal to sunitinib for OS, PFS and TTD across favourable- and intermediate-/poor-risk subgroups (Sections B.3.3.2.1, B.3.3.2.2, B.3.3.3). Provide: (a) the formal evidence base — including the Manz 2019 NMA — disaggregated by IMDC risk group, with HRs and 95% CIs; (b) an HR-prior elicitation that allows ≠1; (c) a probabilistic sensitivity analysis where each TKI's relative effect to sunitinib is sampled from an informative prior. Justify why subjecting pazopanib and tivozanib to identical OS curves (including identical PSA draws) is consistent with the joint parameter uncertainty principle.
**Rationale:** TSD 17, TSD 20. Setting HR≡1 with no uncertainty understates ICER variance.

---

## D. Treatment switching adjustment

### STAT-Merck-14 — Post-progression therapy and OS adjustment
**Recipient:** Merck
**Topic:** Subsequent therapy distortion of OS estimates
**Question:** Table 69 shows that 86.23% of sunitinib-arm favourable-risk patients received subsequent nivolumab (or grouped IO equivalents), whereas avelumab + axitinib patients received none in the modelled distribution. Given that JAVELIN Renal 101 did not permit protocolised crossover but did allow subsequent therapy, has the company performed an adjustment to the comparator OS to account for the receipt of post-progression IO that would not be available in NHS practice in the same proportions? Provide:
(a) The full subsequent therapy pattern in JAVELIN Renal 101 by arm, IMDC subgroup and data cut.
(b) RPSFTM, two-stage estimation (TSE) and IPCW adjusted OS HRs for the favourable-risk and intermediate-/poor-risk subgroups, with bootstrap CIs (≥1,000 replicates).
(c) The covariates included in the IPCW switching model and the stabilised weight distribution (mean, SD, range, % >5, % <0.2).
(d) Justification for the choice between "with re-censoring" vs "without re-censoring" for TSE (TSD 16 recommends with re-censoring as the base case).
**Rationale:** TSD 16. Without adjustment, comparator OS includes treatment effect from non-NHS-routine downstream IO, which biases the ICER in favour of avelumab + axitinib.

### STAT-Merck-15 — Bootstrap CIs around adjusted HRs
**Recipient:** Merck
**Topic:** Uncertainty propagation for switching adjustments
**Question:** For any TSE, RPSFTM or IPCW analysis produced in response to STAT-Merck-14, confirm that CIs are derived via a full-pipeline non-parametric bootstrap (resampling at the patient level, re-fitting both the switching/PS model and the outcome model). Report the number of replicates, percentile vs BCa method, and the bootstrap distribution of the adjusted HR.
**Rationale:** TSD 16 §6.

---

## E. Censoring rules and PFS estimation

### STAT-Merck-16 — FDA vs EMA censoring rules and BICR vs investigator
**Recipient:** Merck
**Topic:** PFS censoring rule sensitivity
**Question:** Provide side-by-side PFS analyses (median, HR, 95% CI, 12/24/36-month event-free rates) for the favourable-risk and intermediate-/poor-risk subgroups under: (a) FDA censoring rules; (b) EMA censoring rules; (c) BICR assessment at IA1/IA2; (d) investigator assessment at FA. Quantify BICR-investigator concordance (kappa or weighted kappa, % discordance for progression events). Justify the decision to rely on investigator-assessed PFS at the FA in the base case given that "BICR activities subsequently ended" (Section B.2.4.2).
**Rationale:** Open-label trial. TSD 14 §2.2; the JAVELIN sponsor's reliance on investigator-assessed PFS post-IA2 introduces risk of informative censoring and assessment bias.

---

## F. Stratification and inference

### STAT-Merck-17 — Stratified vs unstratified HR divergence in favourable-risk
**Recipient:** Merck
**Topic:** Stratification factor handling
**Question:** In the favourable-risk OS analysis the stratified HR is 0.73 (95% CI 0.48, 1.10; p=0.1290) and the unstratified HR is 0.78 (95% CI 0.52, 1.17; p=0.2281) — Table 14. State (a) the stratification variables and the number of strata in each subgroup analysis; (b) cell counts per stratum (is any stratum sparse?); (c) which CI was used in the economic model; (d) sensitivity analyses using profile likelihood and bootstrap CIs for the HR.
**Rationale:** Stratified HRs in subgroup analyses with small cells (n=94 vs n=96) can be unstable. TSD 14 §3.

### STAT-Merck-18 — Repeated CI methodology and alpha spending
**Recipient:** Merck
**Topic:** Multiplicity across data cuts and endpoints
**Question:** Provide the complete alpha-spending schedule across IA1, IA2, IA3 and FA for OS and PFS, in both PD-L1+ and PD-L1-unselected populations (Section B.2.4.2). State the repeated CI (RCI) construction used at the FA and how this propagates into point and interval estimates used in the cost-effectiveness model.
**Rationale:** The stated four-look Lan–DeMets O'Brien-Fleming design needs explicit reporting per TSD 14 §3.6.

---

## G. Subgroups

### STAT-Merck-19 — Multiplicity adjustment and interaction tests
**Recipient:** Merck
**Topic:** Subgroup inference rigour
**Question:** The submission states subgroup analyses by IMDC risk were "exploratory with no adjustment for multiplicity" and that intermediate and poor subgroups were "pooled in a post hoc analysis" (Section B.2.5, Table 12). Provide: (a) the treatment-by-IMDC subgroup interaction p-values for OS and PFS; (b) the number of pre-specified vs post-hoc subgroup analyses; (c) the power calculation for OS within the favourable-risk subgroup at the FA event count; (d) Bonferroni- or hierarchical-adjusted p-values for the key subgroup-level claims.
**Rationale:** The base-case ICER for the appraisal rests entirely on a subgroup (favourable-risk) that was not pre-specified for confirmatory testing. TSD 14, NICE methods guide §3.5.

### STAT-Merck-20 — Subgroups where the IO arm performs worse
**Recipient:** Merck
**Topic:** Adverse subgroup signals
**Question:** Provide a forest plot of OS and PFS HRs for **every** pre-specified subgroup in JAVELIN Renal 101 (age, sex, region, ECOG PS, IMDC risk, MSKCC risk, PD-L1 status, prior nephrectomy, number of organ sites, baseline LDH, sarcomatoid features) for the FA data cut. Identify any subgroup where the HR for avelumab + axitinib exceeds 1 (favouring sunitinib) or where the lower 95% CI is below the null in a direction unfavourable to the intervention, and address potential effect heterogeneity.
**Rationale:** TSD 14, TSD 20. Identifying decision-relevant heterogeneity for adverse subgroups (e.g. PD-L1– intermediate risk) supports a more complete view of efficacy.

### STAT-Merck-21 — PD-L1 subgroup discordance
**Recipient:** Merck
**Topic:** PD-L1 results
**Question:** Table 20 reports almost all PD-L1+ effect estimates as redacted "XXX". Provide the unredacted PD-L1+ OS and PFS HRs and 95% CIs in favourable-risk and intermediate-/poor-risk, along with the PD-L1– counterpart estimates, and an interaction p-value for treatment × PD-L1 status. Justify the omission of PD-L1 from cost-effectiveness modelling against the regulator's primary endpoint definition (PD-L1+).
**Rationale:** The original regulatory primary endpoint was defined in PD-L1+; ignoring it without justification weakens construct validity (TSD 14 §3.5).

---

## H. PSA implementation

### STAT-Merck-22 — Correlated sampling of survival parameters
**Recipient:** Merck
**Topic:** Cholesky decomposition / joint sampling
**Question:** Confirm that PSMs for OS, PFS and TTD are PSA-sampled using a Cholesky decomposition of the variance–covariance matrix from the underlying ML fits (not independent univariate draws on each shape/scale parameter). Provide the variance–covariance matrices for each PSM. State how generalised gamma's three correlated parameters (Q, sigma, mu) are sampled jointly. Demonstrate this with a paired scatter plot of sampled parameters.
**Rationale:** Independent draws on correlated survival parameters produce nonsense fits — directly relevant to the "unrealistic extrapolations" reported in B.3.9.1.

### STAT-Merck-23 — Propagation of NMA uncertainty into PSA
**Recipient:** Merck
**Topic:** Joint MCMC-to-PSA pipeline
**Question:** For the intermediate-/poor-risk cost-effectiveness analysis, describe how the MCMC posterior of each pairwise HR from the NMA enters the PSA — i.e. whether the full posterior chain is sampled in each PSA iteration (preserving correlation across treatments) or whether univariate log-normal draws are used. Provide a covariance check between the sampled pairwise HRs.
**Rationale:** TSD 17, TSD 20. Independent univariate draws break the multivariate posterior structure and bias decision uncertainty estimates.

### STAT-Merck-24 — PSA stopping criterion
**Recipient:** Merck
**Topic:** PSA iteration adequacy
**Question:** 5,000 PSA iterations are reported. Demonstrate convergence by plotting the running mean of incremental costs, incremental QALYs and ICER vs iteration number for each pairwise comparison, and the running half-width of the 95% interval around the INMB.
**Rationale:** Stability "by visual inspection" (B.3.9.1) is not formally established.

---

## I. Sample size and design

### STAT-Merck-25 — Power of OS as a secondary endpoint within the favourable-risk subgroup
**Recipient:** Merck
**Topic:** Statistical power for the decision-relevant comparison
**Question:** Provide the achieved power calculation for the favourable-risk OS comparison at the FA, given n=94 vs n=96 patients and 96 observed deaths. Provide the minimum detectable HR at 80% and 90% power. State the company's interpretation of the non-significant stratified OS HR of 0.73 (p=0.1290) in light of this power.
**Rationale:** The favourable-risk subgroup drives the base-case ICER. A clinical-effectiveness conclusion that is not formally significant must be transparently reconciled with the modelled OS gain (3.7 LYG, 1.53 QALY).

---

## K. Covariate selection (utility regression)

### STAT-Merck-26 — Utility regression model selection
**Recipient:** Merck
**Topic:** Stepwise/pre-specification
**Question:** For the EQ-5D-5L→EQ-5D-3L mapped utility regression (Table 57), state: (a) whether the covariate set (progression status, treatment status) was pre-specified or selected by AIC/BIC/backward elimination; (b) what other covariates were tested (age, sex, IMDC risk, AE status, baseline utility); (c) residual diagnostics and intracluster correlation from the linear mixed model; (d) sensitivity to using a Hernández-Alava response-mapping (not value-set mapping) which is the current DSU-recommended approach for EQ-5D-5L→3L.
**Rationale:** TSD 14 / DSU Hernández-Alava 2017 guidance.

---

## L. TTD modelling

### STAT-Merck-27 — Differential TTD curve choice
**Recipient:** Merck
**Topic:** Distribution choice per drug
**Question:** Per Table 55, generalised gamma is selected for avelumab, axitinib and sunitinib TTD despite the AIC/BIC tables (Tables 49, 51, 53) ranking exponential or Gompertz first. Justify why generalised gamma is preferred for all three drugs simultaneously, given that this distribution has three parameters and well-known convergence/stability issues at small sample sizes (n=94 favourable-risk arm). Provide a sensitivity analysis using the AIC/BIC-best distribution per drug (and a single best common distribution) and show the impact on incremental costs.
**Rationale:** TTD is the dominant driver of cost (OWSA shows axitinib RDI as the largest INMB driver, Figure 37) — distribution choice has direct ICER impact.

### STAT-Merck-28 — Independent vs joint avelumab/axitinib TTD
**Recipient:** Merck
**Topic:** Bivariate correlation in TTD
**Question:** Avelumab and axitinib TTD are modelled independently (Sections B.3.3.3). State the empirical correlation between time-to-avelumab-discontinuation and time-to-axitinib-discontinuation in JAVELIN Renal 101 (Spearman, with 95% CI), and show whether independent extrapolation overestimates expected cost of doublet treatment over the lifetime horizon. Provide a bivariate or copula-based sensitivity analysis.
**Rationale:** TSD 14. Patients discontinuing one component frequently discontinue both (footnote to Table 11 reports 411/442 = 93% discontinue both).

---

## M. Curve-crossing handling

### STAT-Merck-29 — PFS curve crossing and visual goodness-of-fit
**Recipient:** Merck
**Topic:** Long-term PFS plausibility
**Question:** In the favourable-risk PFS comparison, the log-normal extrapolation for avelumab + axitinib (selected as base case) and the generalised gamma for sunitinib produce small absolute differences at year 10 (Tables 46, 48 — partially redacted). Provide the modelled PFS curves and PFS HR(t) trajectory over 0–40 years, and conduct a sensitivity analysis (a) imposing PFS(t)_aveaxi ≥ PFS(t)_sun at all t after end of follow-up, and (b) truncating each curve at a clinically informed mortality cap by IMDC risk.
**Rationale:** TSD 14 §3.4; small PFS differences at long horizons compound the QALY/LY gain.

---

## N. Visual goodness-of-fit and residuals

### STAT-Merck-30 — KM/extrapolation overlays and Cox–Snell residuals
**Recipient:** Merck
**Topic:** Standard PSM diagnostic plots
**Question:** For each PSM (OS, PFS, TTD by treatment, in each population), supply: (a) a single figure with KM and all six parametric overlays over both observed follow-up and the 40-year horizon; (b) Cox–Snell residual plots with 45° reference line; (c) hazard plots (smoothed empirical hazard vs parametric hazard); (d) deviance/martingale residual plots. Provide the underlying data so the EAG can reproduce.
**Rationale:** TSD 14 §3 standard reporting.

---

# Summary

Total questions: 30

Highest-priority items the EAG should pursue first:
1. **STAT-Merck-14** — Subsequent therapy distortion of comparator OS. The base-case model has 86% of the comparator arm receiving subsequent IO (Table 69) with no formal switching adjustment; if uncorrected, this fundamentally biases the OS comparison against avelumab + axitinib's incremental survival claim. (TSD 16)
2. **STAT-Merck-6** — PSA "unrealistic extrapolations" of the generalised gamma sunitinib OS. The submission openly acknowledges PSA instability that inflates comparator LY (B.3.9.1). This needs full diagnostic resolution before any cost-effectiveness conclusion is taken at face value.
3. **STAT-Merck-2 / STAT-Merck-10** — PH validity and the constant-HR NMA. JAVELIN curves separate only after ~30 months and competing IO+IO/IO+TKI delayed-effect signatures argue for FP NMA (TSD 19). The intermediate-/poor-risk results (subgroup table 79) rely entirely on this NMA.
4. **STAT-Merck-19 / STAT-Merck-25** — Subgroup inference rigour and power. The base case is the favourable-risk subgroup, which is exploratory, unpowered, post-hoc-pooled-elsewhere, with a non-significant OS HR (p=0.13). All downstream cost-effectiveness conclusions depend on accepting this subgroup's effect estimate as decision-grade evidence.
5. **STAT-Merck-13** — TKI equivalence assumption with no uncertainty. Pazopanib and tivozanib are set equal to sunitinib without any HR uncertainty, suppressing PSA variance and likely biasing the ICER.
6. **STAT-Merck-22 / STAT-Merck-23** — Joint parameter sampling. Cholesky-correctness of PSMs in PSA and propagation of MCMC NMA posteriors into the cost-effectiveness model are foundational to all probabilistic outputs.
