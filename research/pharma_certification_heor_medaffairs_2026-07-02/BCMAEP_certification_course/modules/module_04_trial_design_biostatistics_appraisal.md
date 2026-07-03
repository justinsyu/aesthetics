# Module 4: Clinical trial design, biostatistics, and critical literature appraisal

Domain B (Scientific and clinical foundations). Approximately 8 hours.

## Learning objectives

On completion, the learner can:

1. Classify study designs (randomized controlled trials, observational designs, single-arm and externally controlled trials, adaptive and master-protocol designs) and state their strengths and threats to validity. (B)
2. Interpret common statistical measures: effect sizes, confidence intervals, p-values, hazard ratios, number needed to treat, and multiplicity. (B)
3. Evaluate endpoints, including surrogate endpoints, patient-reported outcomes, and clinical outcome assessments. (B)
4. Critically appraise a publication and identify bias, confounding, and overinterpretation. (B)

## Why this matters for the career changer

A clinician reads a trial to decide whether to act on its conclusion for a patient. An industry evidence professional reads the same trial to a different standard: whether the design can support the claim being made, whether the analysis controls the errors it is exposed to, and whether the result will withstand review by regulators, health technology assessment (HTA) committees, journal peer reviewers, and skeptical prescribers.

The task shifts from consuming a conclusion to auditing how that conclusion was produced, and to stating plainly what the evidence does and does not establish. A well-appraised study is not one that is praised or dismissed; it is one whose supported claims and residual uncertainties have both been named.

This appraisal discipline is the foundation that later functions draw on: regulatory strategy (Module 5), pharmacovigilance (Module 6), real-world evidence (Module 7), and the clinical value arguments assembled for payers (Modules 8 and 9). This module develops the vocabulary and the habits of structured appraisal, and it produces the critical appraisal and evidence table that anchor the capstone (work product 3).

## 4.1 What counts as a clinical trial, and why classification is the first appraisal step

Appraisal begins with correct classification, because the design sets the ceiling on the inferences that are legitimate. Whether a study is interventional or observational, randomized or single-arm, prospective or retrospective determines which causal claims it can support and which specific biases it must defend against.

Reading the abstract's conclusion before establishing the design is the most common appraisal error. The disciplined sequence is to establish the design first, then read the result through the constraints that design imposes.

The NIH clinical-trial definition case studies are a useful drill for this step: for each scenario, the reader decides whether the study meets the interventional clinical-trial definition before checking the answer ([NIH, Clinical Trial Definition Case Studies](https://grants.nih.gov/policy/clinical-trials/CT-Definition-Case-Studies_1-4-18.pdf)). The classification is not a labeling exercise; it triggers registration, protocol, analysis-plan, and regulatory-documentation obligations, and it signals to the reader which validity framework applies.

A working taxonomy for appraisal:

- **Randomized controlled trials (RCTs).** Participants are randomly allocated to interventions, which, on average, balances measured and unmeasured confounders across arms. This is the design's central advantage.
- **Cohort studies.** Groups defined by exposure are followed for outcomes; prospective cohorts reduce some biases that retrospective cohorts cannot.
- **Case-control studies.** Groups defined by outcome are compared for prior exposure; efficient for rare outcomes but vulnerable to selection and recall bias.
- **Cross-sectional studies.** Exposure and outcome are measured at one time; they describe association, not temporal sequence.
- **Single-arm trials.** All participants receive the intervention; there is no concurrent comparator, so the counterfactual must come from external information.
- **Externally controlled trials.** A treated group is compared with a control constructed from historical or real-world sources rather than concurrent randomization.
- **Adaptive and master-protocol designs.** The design permits prespecified modification, or studies multiple interventions or subpopulations under one protocol.

## 4.2 The hierarchy of evidence and its limits

The conventional evidence hierarchy places systematic reviews of RCTs above individual RCTs, above observational studies, above case series and expert opinion. The hierarchy is a useful default for ranking internal validity, but it is a heuristic, not a rule.

A large, well-conducted RCT with a fragile surrogate endpoint and heavy loss to follow-up can be less informative than a rigorously designed observational study with a well-specified causal question. The reader should rank a given study on its actual conduct and its fitness for the specific decision, not on its design label alone.

The hierarchy also does not settle external validity. A trial can be internally valid (its effect estimate is unbiased for the population studied) yet not applicable to the population a payer or clinician cares about. Appraisal separates these two questions and reports both:

- **Internal validity:** is the effect estimate unbiased for the study's own population?
- **External validity (generalizability):** does the estimate transport to the population, setting, and comparators of the decision at hand?

## 4.3 Randomization, allocation concealment, blinding, and the control group

Randomization is the mechanism that lets an RCT support a causal claim: it makes the arms exchangeable in expectation, so that observed differences can be attributed to the intervention rather than to confounding. Three features determine whether that promise is realized.

- **Allocation concealment** prevents those enrolling participants from foreseeing the next assignment; its absence permits selection bias even when a valid randomization list exists.
- **Blinding** (of participants, treating clinicians, outcome assessors, and analysts) limits performance and detection bias. Open-label designs are sometimes unavoidable but raise the bar for using objective, blindly adjudicated endpoints.
- **The choice of comparator** (placebo, active control, or standard of care) determines what question the trial answers. A placebo-controlled trial establishes efficacy against no treatment; it does not establish relative efficacy against an existing therapy.

The reader should also identify the analysis population.

- An **intention-to-treat** analysis preserves the randomization by analyzing participants as assigned, regardless of adherence; it is generally the primary analysis for superiority questions.
- A **per-protocol** analysis conditions on adherence and can reintroduce confounding; it is better read as supportive, and it takes on a specific role in noninferiority testing (section 4.5).

## 4.4 The estimand: specifying the question before the analysis

An estimand is a precise statement of the treatment effect the trial intends to estimate, defined before the analysis method is chosen. A complete estimand specifies five attributes:

1. The **treatment condition** being compared.
2. The **target population** of interest.
3. The **endpoint (variable)** measured on each participant.
4. The **strategy for handling intercurrent events**, such as treatment discontinuation, use of rescue medication, or death.
5. The **population-level summary**, such as a difference in means or a hazard ratio.

Intercurrent events are the crux. A trial that does not state how it handles them can report an effect that answers a different question than the one the label will claim. The reader should identify the estimand, confirm that the primary analysis matches it, and confirm that sensitivity analyses probe the intercurrent-event assumptions.

## 4.5 Comparative frames: superiority, noninferiority, and equivalence

The comparative frame determines how the result is interpreted.

- **Superiority** trials test whether the intervention is better than the comparator. Failure to reject the null does not prove equivalence; absence of evidence of a difference is not evidence of no difference.
- **Noninferiority** trials test whether the intervention is not worse than an active comparator by more than a prespecified margin. The margin must be justified clinically and statistically, and the inference rests on two assumptions: assay sensitivity (the trial could have detected a difference had one existed) and constancy (the active comparator's effect is similar to that seen in its own prior trials). A noninferiority conclusion is only as credible as these assumptions.
- **Equivalence** trials test whether the effect falls within a symmetric margin on both sides, a frame common for pharmacokinetic comparisons.

For noninferiority, the reader checks the one-sided confidence interval against the margin, not the p-value against 0.05, and confirms that the margin was fixed before unblinding. A per-protocol analysis is often examined alongside intention-to-treat, because dropout can bias a noninferiority result toward the null and thus toward a false noninferiority claim.

## 4.6 Effect measures and their uncertainty

Effect size, precision, and multiplicity are read together; no single number is sufficient.

- **Relative measures** (relative risk, odds ratio, hazard ratio) express the ratio of outcome frequency or event rate between arms. A hazard ratio summarizes the instantaneous relative risk over follow-up under a proportional-hazards assumption; when hazards are not proportional, a single hazard ratio can mislead, and the reader should examine the survival curves and the time course.
- **Absolute measures** (absolute risk reduction, risk difference) express the arithmetic difference in outcome frequency and are necessary to judge clinical relevance.
- **The number needed to treat** is the reciprocal of the absolute risk reduction (NNT = 1 / ARR). It is only interpretable alongside the time horizon and the baseline risk from which it was derived. A large relative effect on a rare outcome can correspond to a small absolute benefit and a large NNT.
- **Confidence intervals** express precision. A 95% confidence interval is the range of effect values compatible with the data at that level; its width, and whether it crosses the null, is more informative than a dichotomous significant-or-not reading. Report and interpret the interval, not only the point estimate.
- **P-values** quantify the compatibility of the data with the null hypothesis. A small p-value does not measure effect size, clinical importance, or the probability that the hypothesis is true, and a non-significant result is not evidence of no effect.
- **Multiplicity** arises when a trial tests many endpoints, subgroups, or interim looks; each additional test inflates the family-wise probability of a false-positive finding. Credible trials prespecify a testing hierarchy or split the alpha across comparisons.

Secondary and subgroup findings that fall outside the prespecified, multiplicity-controlled analysis are hypothesis-generating, not confirmatory, however striking they appear.

## 4.7 A taxonomy of bias and confounding

Bias is a systematic error in design, conduct, or analysis that moves an estimate away from the truth; it is not corrected by a larger sample. Naming the specific bias is more useful than the general word.

- **Selection bias** arises when the compared groups differ systematically at entry or when who is analyzed depends on the outcome.
- **Performance bias** arises when groups receive different co-interventions or care because their assignment is known.
- **Detection bias** arises when outcomes are ascertained differently by group, which unblinded assessment invites.
- **Attrition bias** arises when loss to follow-up is differential and related to the outcome.
- **Reporting bias** arises when the reported analyses or outcomes are selected on their results; comparison of the publication with its registered protocol and analysis plan is the check.
- **Confounding** arises when a third factor is associated with both exposure and outcome; randomization addresses it in expectation, whereas observational designs must address it by design and analysis (Module 7).

## 4.8 Adaptive, Bayesian, and master-protocol designs

Prespecified adaptation can make development more efficient without sacrificing validity, provided the adaptation rules and their error control are fixed in advance.

- **Adaptive designs** may permit sample-size re-estimation, dropping of arms, or response-adaptive randomization.
- **Bayesian designs** update a prior with accumulating data and can support borrowing of information across sources.
- **Master protocols** study more than one question under a single infrastructure: basket trials (one intervention across several conditions defined by a shared feature), umbrella trials (several interventions within one condition), and platform trials (interventions enter and leave over time against a common control).

The FDA Complex Innovative Trial Design (CID) meeting program publishes worked cases that expose the design assumptions and the simulations sponsors used to justify error control, including a master-protocol case in chronic pain ([FDA, CID master-protocol case](https://www.fda.gov/media/155403/download?attachment=)), linked from the program page ([FDA, Complex Innovative Trial Design Meeting Program](https://www.fda.gov/drugs/development-resources/complex-innovative-trial-design-meeting-program)).

Quantitative modeling and simulation increasingly underpin these designs; the FDA model-informed drug development materials describe how such models support dose selection, trial design, and evidence synthesis ([FDA, Application of Model-Informed Drug Development in Study Design and Analysis](https://www.fda.gov/files/about%20fda/published/Application-of-Model-Informed-Drug-Development-in-Study-Design-and-Analysis.pdf)). For an adaptive design, the appraisal question is whether the adaptation was prespecified and whether the type I error rate is preserved across the possible analysis paths.

## 4.9 Single-arm and externally controlled trials

When a concurrent randomized control is infeasible (for example in a small rare-disease population, discussed in Module 5), sponsors may use a single-arm trial with an external control drawn from historical trials, registries, or real-world data. The inference then depends entirely on whether the external control is comparable to the treated group; differences in era, standard of care, measurement, and patient selection can bias the estimate in either direction.

The FDA CID program includes an external- and synthetic-control case in alopecia areata that makes these assumptions explicit ([FDA, CID alopecia external-control case](https://www.fda.gov/media/188560/download?attachment=)).

A disciplined way to reason about a non-randomized comparison is to specify the randomized trial one would ideally have run, then ask how the available data depart from it. This target-trial framework makes the eligibility criteria, treatment strategies, assignment, follow-up, and outcome definitions explicit, and it surfaces the biases (immortal-time bias, prevalent-user bias, and confounding by indication) that arise when those elements are not aligned ([Hernán and Robins, 2016](https://doi.org/10.1093/aje/kwv254)). Module 7 develops these methods in full; here the point is that an external control shifts the burden of proof onto the comparability argument, and the reader must judge that argument on its merits.

## 4.10 Endpoints: surrogate endpoints, patient-reported outcomes, and clinical outcome assessments

An endpoint is only as good as its link to a benefit that patients value.

- **Clinical (final) endpoints** measure how a patient feels, functions, or survives.
- **Surrogate endpoints** are markers (laboratory values, imaging, or other measurements) intended to predict a clinical benefit. A surrogate is credible only to the extent that its treatment-induced change reliably predicts the treatment-induced change in the clinical outcome; a marker merely correlated with prognosis is not automatically a valid surrogate for treatment effect. Surrogate endpoints are central to accelerated approval (Module 5), where clinical benefit is confirmed later.
- **Clinical outcome assessments (COAs)**, including patient-reported (PRO), clinician-reported, observer-reported, and performance outcomes, measure symptoms and function directly. Their interpretation depends on instrument validation, the prespecified analysis, and a defensible threshold for a meaningful within-patient change.

In small rare-disease populations, endpoint selection is often the pivotal design decision; the FDA LEADER 3D teaching cases illustrate how an endpoint is chosen to capture clinically meaningful change when the population constrains trial size ([FDA, LEADER 3D odevixibat case](https://www.fda.gov/media/186133/download?attachment=)).

## 4.11 Missing data and sensitivity analysis

Missing data threaten validity because the reason data are missing is often related to the outcome. The reader should ask how much data are missing, whether the amount differs by arm, and what assumption the primary analysis makes about the missing values.

A credible analysis states its missing-data assumption, uses a primary method consistent with the estimand, and reports sensitivity analyses that test whether the conclusion holds under less favorable assumptions. A result that survives only under the most optimistic missing-data assumption is fragile and should be reported as such.

## 4.12 Critical appraisal: a structured approach and common failure modes

A structured appraisal answers, in order:

1. What was the question (estimand and comparator)?
2. What was the design, and does it fit the question?
3. How were participants selected and allocated?
4. How was bias controlled (allocation concealment, blinding, analysis population)?
5. What were the endpoints, and were they prespecified?
6. What is the effect size, with its confidence interval and its absolute counterpart?
7. Was multiplicity controlled?
8. How much data were missing, and how was that handled?
9. What do the results, and only the results, support?

Reporting standards for the relevant design give item-level checklists that make an appraisal reproducible; comparing a publication against the appropriate checklist is a fast way to surface omissions.

Common failure modes to flag: conclusions that outrun the estimand; a relative effect reported without its absolute counterpart; emphasis on a non-significant secondary or subgroup finding; a surrogate endpoint treated as a clinical benefit; a per-protocol result presented as if it preserved randomization; and a single-arm result compared informally with an unrelated trial as though the comparison were randomized. Correct appraisal states the finding with its uncertainty and names what remains unproven.

## 4.13 Appraising a body of evidence: systematic reviews and synthesis

Most decisions rest on more than one study, so appraisal extends from the single trial to the body of evidence. A systematic review identifies, selects, and appraises the relevant studies against a prespecified protocol; a meta-analysis, where appropriate, combines their estimates quantitatively.

The reader appraises a synthesis on features distinct from those of a single trial:

- **Search and selection.** Was the search comprehensive and reproducible, and were inclusion criteria set before results were known?
- **Risk of bias across studies.** Were the included studies appraised individually, and does the synthesis account for their quality?
- **Heterogeneity.** Do the studies estimate a common effect, or do populations, comparators, and endpoints differ enough that a pooled estimate is hard to interpret?
- **Publication and reporting bias.** Could studies with unfavorable results be missing from the evidence base?

An indirect or network comparison, which infers relative effects between treatments that were never compared head to head, adds a further assumption of transitivity across the connected trials; this method is developed for HTA in Module 9. The general rule carries over from the single study: a synthesis is only as trustworthy as the weakest link its assumptions depend on.

## Worked example: appraising an externally controlled design

Use the FDA CID alopecia areata case, which discloses an external- and synthetic-control design ([FDA, CID alopecia external-control case](https://www.fda.gov/media/188560/download?attachment=)).

Working from the public case, the learner appraises the design rather than the product:

- Identify the comparator, and why a concurrent randomized control was not used.
- List the ways the external control could differ from the treated group (era, standard of care, measurement, and selection).
- Specify the simulation scenarios a sponsor should run to demonstrate error control.
- Translate the disclosed design categories into a briefing-package outline.
- Frame the comparability argument as a target trial, and name the biases that would arise if its elements are not aligned ([Hernán and Robins, 2016](https://doi.org/10.1093/aje/kwv254)).

FDA notes that each CID case focuses on the specific submitted design and does not cover the full development program's evidence needs ([FDA, Complex Innovative Trial Design Meeting Program](https://www.fda.gov/drugs/development-resources/complex-innovative-trial-design-meeting-program)); the exercise is to reason about the design, not to endorse it.

## Applied activity (produces capstone work product 3)

Using an assigned trial publication for the capstone product scenario (case J in the case library), produce a structured critical appraisal and an evidence table.

The appraisal states the estimand and comparator, classifies the design, assesses internal and external validity, reports the primary effect with its confidence interval and its absolute counterpart, notes multiplicity and missing-data handling, and closes with a plain-language summary of what the evidence supports and what it does not, suitable for internal use.

The evidence table records study characteristics, design, population, endpoints, effect estimates, and validity notes in a reusable format. Together these become the critical appraisal and evidence table of the capstone (work product 3), and the evidence table feeds the integrated evidence generation plan (Module 10).

## AI-use focus

Permitted: use an AI assistant to extract study characteristics (design, population, endpoints, effect estimates) from a source article and to draft the first version of the evidence table.

Required controls: verify every extracted value against the source article before use, because language models can transcribe numbers, confidence intervals, and endpoint definitions incorrectly or invent them; do not enter confidential or embargoed manuscripts into a tool that is not validated and approved; record the AI use in your audit log (tool, task, what you verified, who is accountable). The appraisal judgment, especially the assessment of bias and the statement of what the evidence supports, remains a human responsibility. This applies the program AI-use policy (`governance/ai_use_policy_and_playbook.md`).

## Knowledge check

1. Why is classifying the design the first step in appraisal? (Answer: the design sets the ceiling on the causal claims a study can support and determines which specific biases it must defend against; reading the conclusion first invites overinterpretation. See the NIH case studies.)
2. A trial reports a hazard ratio of 0.70 (95% CI 0.55 to 0.89) but the survival curves cross. What is the concern? (Answer: a single hazard ratio assumes proportional hazards; crossing curves suggest the assumption is violated, so the summary estimate can mislead and the time course must be examined.)
3. An intervention reduces relative risk by 40%, but the NNT is 200 over five years. What does this show? (Answer: a large relative effect on a low-baseline-risk outcome can yield a small absolute benefit; relative and absolute measures must be read together, with the time horizon.)
4. What must hold for a noninferiority conclusion to be credible? (Answer: a clinically justified, prespecified margin; assay sensitivity; and constancy of the active comparator's effect. The inference uses the one-sided confidence interval against the margin, and dropout must be scrutinized because it can bias toward a false noninferiority claim.)
5. Why is a striking subgroup finding outside the prespecified analysis treated as hypothesis-generating? (Answer: multiplicity inflates the family-wise false-positive probability; only prespecified, multiplicity-controlled analyses are confirmatory.)
6. When a single-arm trial uses an external control, where does the burden of proof shift? (Answer: onto the argument that the external control is comparable to the treated group; the target-trial framework makes the assumptions and biases explicit.)
7. Name three specific biases and one design or analysis feature that addresses each. (Answer examples: selection bias, addressed by concealed randomization; detection bias, addressed by blinded outcome assessment; attrition bias, addressed by intention-to-treat analysis and missing-data sensitivity analyses.)

## Key readings

- [NIH, Clinical Trial Definition Case Studies](https://grants.nih.gov/policy/clinical-trials/CT-Definition-Case-Studies_1-4-18.pdf) (design classification drill)
- [FDA, Complex Innovative Trial Design Meeting Program](https://www.fda.gov/drugs/development-resources/complex-innovative-trial-design-meeting-program), with the [alopecia external-control case](https://www.fda.gov/media/188560/download?attachment=) and the [master-protocol chronic pain case](https://www.fda.gov/media/155403/download?attachment=)
- [Hernán and Robins, 2016, target-trial emulation](https://doi.org/10.1093/aje/kwv254) (reasoning about non-randomized comparisons)
- [FDA, Application of Model-Informed Drug Development in Study Design and Analysis](https://www.fda.gov/files/about%20fda/published/Application-of-Model-Informed-Drug-Development-in-Study-Design-and-Analysis.pdf) (modeling and simulation in design)
- [FDA, LEADER 3D odevixibat case](https://www.fda.gov/media/186133/download?attachment=) (endpoint selection in a small population)

## Connection to the capstone

The critical appraisal and evidence table produced here are work product 3 of the capstone. The appraisal discipline carries directly into Module 5 (judging whether the evidence meets a regulatory standard), Module 6 (reading safety data), Module 7 (appraising real-world evidence), and Modules 8 and 9 (assembling and defending the clinical value argument before payers and HTA committees). The evidence table is a reusable input to the integrated evidence generation plan (Module 10).
