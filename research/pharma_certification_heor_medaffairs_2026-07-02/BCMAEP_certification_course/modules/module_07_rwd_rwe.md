# Module 7: Real-world data and real-world evidence

Domain C (Real-world evidence, health economics, and value). Approximately 7 hours.

## Learning objectives

On completion, the learner can:

1. Distinguish real-world data (RWD) sources, including claims, electronic health records, registries, and patient-generated data, and judge their fitness for a stated purpose. (C)
2. Explain real-world evidence (RWE) study designs, including target-trial emulation, comparative-effectiveness cohorts, and externally controlled designs, and their acceptability to regulators and health technology assessment (HTA) bodies. (C)
3. Identify the principal threats to validity in RWE (confounding, selection, and misclassification) and the design and analytic methods that address them. (C)
4. State when RWE can support a regulatory or access decision and when it cannot. (C)

## Why this matters for the career changer

A clinician reads a randomized trial and asks whether its result applies to the patient in front of them. An evidence professional in industry works one layer further out: much of the evidence that payers, HTA bodies, and regulators request after approval cannot come from a new randomized trial, because the trial would be too slow, too small, unethical, or infeasible. That evidence is generated instead from data produced during routine care. The task is to decide which real-world data source can answer a specific question, which study design turns that data into a credible causal comparison, and how far a regulator or payer will accept the result. Getting the right evidence after approval is a recognized and distinct problem, and it is not solved by defaulting to whatever data are easiest to obtain ([Vreman et al., 2020](https://doi.org/10.3389/fphar.2020.569535)). This module builds the reasoning that a later integrated evidence plan (Module 10) depends on.

## 7.1 Real-world data and the source taxonomy

Real-world data are data relating to patient health status or the delivery of health care that are collected outside the setting of a conventional randomized trial. Real-world evidence is the clinical evidence about the use, benefits, or risks of a product that is derived from analysis of such data. The distinction matters: data are not evidence until a study design and an analysis convert them into an answer to a defined question.

The main source categories differ in what they capture and what they omit:

- **Administrative claims.** Generated for billing. They capture enrollment, diagnoses, procedures, and dispensed prescriptions across large populations and long follow-up, but they record what was billed, not what was clinically observed, and they lack laboratory values, vital signs, and results.
- **Electronic health records (EHR).** Generated during care. They capture clinical detail (laboratory results, vital signs, clinician notes, imaging) but are fragmented across systems, incomplete when a patient receives care elsewhere, and irregular in timing.
- **Product and disease registries.** Assembled deliberately for a defined population. They can capture disease-specific variables and long-term outcomes but depend on site participation and consistent data entry.
- **Patient-generated health data.** From wearables, applications, and patient-reported outcome instruments. They capture the patient's experience and between-visit measurements but vary in validation and completeness.
- **Linked and composite sources.** Mortality files, pharmacy dispensing, genomic data, and social or administrative data linked to the above to fill specific gaps.

The strengths and limitations follow directly from why each source exists:

| Source | Primary strength | Principal limitation |
|---|---|---|
| Administrative claims | Large population, long continuous follow-up | No clinical results; records billing, not observation |
| Electronic health records | Clinical detail | Fragmented across systems; incomplete; irregular timing |
| Product and disease registries | Disease-specific variables, long-term outcomes | Depend on site participation and consistent entry |
| Patient-generated health data | Between-visit and patient-experience measures | Variable validation and completeness |
| Linked and composite sources | Fill specific gaps (mortality, genomics) | Linkage error; access and privacy constraints |

No single source is complete, and the deficits are structural rather than incidental: claims omit clinical results because billing does not require them, and EHR data are incomplete because care is delivered across unconnected systems. The reason integrated evidence generation now spans the product lifecycle, from development through post-approval, is that different decisions require different data assembled deliberately rather than opportunistically ([Schneeweiss & Miksad, 2025](https://doi.org/10.1002/cpt.3603)).

To study a question across several databases, the sources are often transformed to a common data model, a standardized structure and vocabulary that lets the same analytic code run on each database so results can be compared or pooled. Common data models support multi-database and distributed analyses, in which patient-level data need not leave each site, which eases privacy constraints. The cost is that work shifts onto the mapping step, and an error in mapping a source to the model propagates to every study that uses it.

## 7.2 Fitness for purpose

A source is not good or bad in the abstract; it is fit or unfit for a specific question. Two dimensions organize the judgment.

**Relevance** asks whether the data contain what the question requires:

- the target population, at sufficient size;
- the exposure and a suitable comparator, both identifiable;
- the outcome, measured in an interpretable and consistent way;
- the covariates needed to control confounding; and
- follow-up long enough to observe the outcome.

**Reliability** asks whether the recorded values can be trusted:

- accuracy of key variables against a reference where one exists;
- completeness, including how missing data arise and how much is missing;
- consistency of definitions across sites and over calendar time; and
- provenance that is documented and auditable from collection through transformation to analysis.

The practical drill for any proposed study is to write the question first (population, exposure, comparator, outcome, and time), then test each candidate source against relevance and reliability. A claims database with five years of follow-up may be fit to study a hospitalization outcome and unfit to study a laboratory-defined response that it never records. Stating the mismatch is part of the deliverable, not a failure of it.

## 7.3 From association to a causal question: target-trial emulation

The central methodological advance in modern RWE is to stop asking loosely "what does the database show" and instead specify the randomized trial one would run if it were feasible, then emulate that trial's protocol in the observational data. This target-trial framework forces the analyst to state the protocol elements before touching the data, which removes several avoidable biases at the design stage ([Hernán & Robins, 2016](https://doi.org/10.1093/aje/kwv254)). The elements to specify in advance are:

- eligibility criteria;
- the treatment strategies being compared;
- the assignment procedure (and how the observational data approximate it);
- the start of follow-up, or time zero;
- the outcome and its measurement;
- the causal contrast of interest (the estimand); and
- the analysis plan.

Two errors that target-trial emulation prevents are worth naming, because they recur:

- **Immortal time bias.** When follow-up begins before the exposure is defined, treated persons must survive long enough to become treated, which manufactures an apparent survival advantage. Aligning eligibility, treatment assignment, and the start of follow-up at a single time zero removes it.
- **Prevalent-user bias.** Studying patients already established on a treatment excludes those who stopped early because of harm or non-response, flattering the treatment. Emulating a trial that enrolls new users at initiation avoids it.

To see immortal time bias concretely: suppose "treated" is defined by receiving the drug at any point during follow-up, and follow-up is counted from diagnosis. A patient who dies at month 2 cannot have received a drug first dispensed at month 4, so early deaths are, by construction, assigned to the untreated group. The treated group is guaranteed to have survived until its first dispensing, and its apparent survival advantage is an artifact of the definition, not an effect of the drug. Anchoring time zero at treatment initiation for both groups removes the artifact.

The framework does not require that the emulated trial ever be run. Its value is discipline: it converts a vague comparison into an explicit protocol whose assumptions can be inspected and criticized.

## 7.4 Causal-inference assumptions in plain terms

A causal effect can be estimated from observational data only under conditions that should be stated and defended, not left implicit. Three assumptions do the work.

- **Exchangeability (no unmeasured confounding).** After adjusting for measured covariates, the treated and untreated groups are comparable in their outcome risk. This is the assumption most often violated, because it can never be fully verified from the data, and it is why unmeasured confounding is addressed by sensitivity analysis rather than assumed away.
- **Positivity.** Every type of patient has a non-zero probability of receiving each treatment being compared. If a subgroup never receives one option, its effect in that subgroup is not estimable from the data.
- **Consistency and a well-defined intervention.** The treatment must be specified precisely enough that "the effect of treatment" is a single, well-defined quantity. A vague exposure (for example "on therapy") produces an ambiguous effect. The target-trial framework enforces this by requiring the treatment strategies to be written as a protocol would write them ([Hernán & Robins, 2016](https://doi.org/10.1093/aje/kwv254)).

Naming these assumptions is not academic. Each one maps to a design or reporting choice, and a study that does not address them is not credible regardless of how large the database is.

## 7.5 Comparative-effectiveness RWE and design options

Beyond emulating a target trial in existing data, several designs sit on a spectrum from fully observational to fully randomized:

- **Observational cohort, new-user active-comparator.** The default rigorous design: enroll patients at initiation of the study drug or an active comparator, follow both forward, and adjust for measured confounders. The active comparator reduces confounding by indication because both groups are treatment candidates.
- **Registry-based or hybrid studies.** A registry provides the population and long-term outcomes; a study element (for example a randomized treatment assignment, or a pre-specified data collection) is added. These combine real-world follow-up with some of the rigor of a trial.
- **Pragmatic trials.** Randomized, so confounding is handled by design, but conducted in routine-care settings with broad eligibility and routinely collected outcomes, which improves relevance to practice at some cost to internal control.

The choice moves along a trade-off: designs closer to a randomized trial give stronger causal claims and weaker feasibility or generalizability, and designs closer to routine data give the reverse. Matching the design to the specific residual question, rather than to convenience, is the same principle that governs post-approval evidence generation generally ([Vreman et al., 2020](https://doi.org/10.3389/fphar.2020.569535)).

## 7.6 External and synthetic control arms

When randomization is infeasible, for example in a small rare-disease population or where withholding an active treatment is not ethical, a single-arm study can be compared against an external control constructed from historical trial data, registry data, or other real-world data. A synthetic control arm is a specific case in which patient-level external data are selected and weighted to resemble the single-arm population.

External controls are attractive and hazardous for the same reason: the comparator is not randomized, so any difference in the populations, in how outcomes were measured, or in the standard of care over calendar time can be mistaken for a treatment effect. The design questions that determine credibility are:

- whether the external population meets the same eligibility criteria;
- whether the outcome is measured the same way and at the same times;
- whether time zero is defined comparably in both arms; and
- whether the analysis adjusts for measured differences and quantifies sensitivity to unmeasured ones.

The US FDA has engaged with externally controlled designs through its Complex Innovative Trial Design meeting program, whose public case materials let a learner see how a regulator reasons about these assumptions ([FDA, Complex Innovative Trial Design Meeting Program](https://www.fda.gov/drugs/development-resources/complex-innovative-trial-design-meeting-program)).

Because the credibility of an external control rests on unverifiable assumptions, a defensible analysis quantifies how fragile its conclusion is. A tipping-point analysis asks how large a difference between the arms (for example in unmeasured prognosis) would be needed to overturn the result; if a small, plausible bias would reverse the conclusion, the evidence is weak regardless of the point estimate.

## 7.7 Threats to validity and the methods that address them

Three threats dominate the appraisal of any RWE study.

- **Confounding.** A factor associated with both the treatment choice and the outcome distorts the comparison. Confounding by indication, where sicker patients receive a particular treatment, is the most common. Design responses include new-user and active-comparator designs; analytic responses include multivariable adjustment, propensity-score matching, weighting, and stratification, and, for time-varying confounding, methods such as marginal structural models. Only measured confounders can be adjusted, which is why unmeasured confounding must be addressed by sensitivity analysis (for example a quantitative bias analysis or a negative-control outcome) rather than assumed away.
- **Selection bias.** The way persons enter or leave the data, differential loss to follow-up, or conditioning on a variable affected by treatment can create a spurious association. Defining eligibility and time zero as in a target trial reduces it.
- **Misclassification.** Exposures, outcomes, and covariates measured in routine data are imperfect. A billing code is not a validated diagnosis. Validation of the algorithm that defines each variable, and reporting its sensitivity and specificity, is part of a credible study.

To make confounding by indication concrete: if clinicians preferentially give a new drug to healthier patients, the drug can appear to lower mortality even with no true effect, because its recipients would have had lower mortality regardless of treatment. Adjustment removes this distortion only for the health markers that are measured; residual differences in unmeasured severity persist. This is why a negative-control outcome, or a quantitative bias analysis that asks how strong an unmeasured confounder would have to be to explain the result, is reported rather than a claim that confounding was fully controlled.

Outcomes in routine data often require purpose-built real-world endpoints, for example real-world progression-free survival or time to treatment discontinuation, because the trial endpoint (such as blinded independent radiologic review) is not recorded during routine care. These endpoints must be validated against the clinical endpoint they stand in for, and their definition documented, because an endpoint that is convenient to extract is not necessarily the one the decision requires.

## 7.8 Transparency and reproducibility

Transparency is a validity method in its own right, not an administrative formality. Pre-specifying the protocol and the analysis, and registering the study before results are known, prevent the selection of the single most favorable comparison from among the many a large database permits; that selection is itself a form of bias. To let an independent analyst reproduce and criticize the result, a report should include:

- the data source and its version;
- the full variable definitions and code lists;
- the cohort-selection counts at each step (an attrition diagram); and
- the analysis code.

A study that cannot be reproduced from its own report cannot be appraised, and an evidence plan should therefore commit to these reporting standards at the design stage rather than after the analysis is complete.

Access to real-world data is also governed by privacy and contractual constraints. Patient-level data carry confidentiality and data-protection obligations (for example HIPAA and GDPR, covered in Module 3), and a feasibility assessment must confirm that the intended analysis is permitted under the data's governance terms before a design is finalized. A study that is methodologically sound but not permissible under the data agreement cannot proceed.

## 7.9 Regulator and HTA acceptability

RWE occupies different positions across decision makers, and a career changer should resist a single blanket claim about "acceptance."

For **regulators**, RWE is routinely accepted for safety and natural-history questions and, increasingly, for effectiveness questions where a randomized trial is infeasible and the data and design are strong; it is accepted least readily as the sole basis for a new effectiveness claim where a trial was feasible. The recurring principle is that the evidence generated after approval should be matched to the specific residual question, not produced generically ([Vreman et al., 2020](https://doi.org/10.3389/fphar.2020.569535)). The extent of regulatory use is visible in practice: the FDA has published a compendium of 73 examples of real-world evidence used in medical device regulatory decisions over fiscal years 2020 to 2025, which a learner can review to see what evidence quality and context the agency found sufficient ([FDA, Examples of Real-World Evidence Used in Medical Device Regulatory Decisions, FY 2020-2025](https://www.fda.gov/media/191805/download)).

For **HTA bodies and payers**, RWE is used to characterize the treated population, to estimate real-world effectiveness and adherence, to inform economic models, and to support managed-entry agreements, but comparative-effectiveness claims from non-randomized data are scrutinized for the threats in section 7.7. Where evidence is promising but immature, some payers use a managed-entry or coverage-with-evidence-development agreement: the product is reimbursed on the condition that specified real-world evidence is collected to resolve the residual uncertainty, with the coverage decision revisited once it matures. Such agreements make the design and governance of the post-decision RWE study part of the access decision itself, not an afterthought. HTA methods guides set out how observational evidence is weighed alongside trial evidence and where its limitations bear on a decision ([NICE, health technology evaluations manual, PMG36](https://www.nice.org.uk/guidance/pmg36/resources/nice-technology-appraisal-and-highly-specialised-technologies-guidance-the-manual-pdf-72286779244741); [ICER, Guide to Understanding Health Technology Assessment](https://icer.org/wp-content/uploads/2020/10/ICER-Guide-to-Understanding-Health-Technology-Assessment-6.19.18.pdf)). For settings with different data and capacity constraints, the iDSI toolkit frames how evidence is assembled and appraised for coverage decisions ([iDSI, Health Technology Assessment Toolkit](https://f1000research.com/documents/8-703/pdf)).

A separate question from internal validity is transportability: whether an effect estimated in one population applies to the target population of a decision. The two differ when the effect depends on characteristics distributed differently in the study and target populations, so a well-conducted study can still fail to answer the local question. HTA bodies weigh this directly when a trial or study population differs from the local treated population, which is one reason the same evidence is received differently across jurisdictions.

The operating conclusion is conditional: RWE can support a decision when the question suits observational data, the source is fit for purpose, a credible causal design is used, and the residual biases are quantified and judged tolerable for the decision at hand. It cannot substitute for a feasible randomized trial of a new effectiveness claim simply because it is faster or cheaper.

## 7.10 Matching the evidence to the decision

The reasoning in sections 7.1 to 7.9 can be summarized as a triage from the question to a preferred source and design. The table below is a starting orientation, not a rule; the fitness-for-purpose test always overrides it for a specific question.

| Evidence question | Typically suited source | Typically suited design |
|---|---|---|
| Incidence, prevalence, natural history | Registry, claims, EHR | Descriptive cohort |
| Treatment patterns and adherence | Claims, EHR | Longitudinal descriptive cohort |
| Safety signal or rare adverse event | Claims, linked mortality, registries | Cohort or self-controlled design |
| Comparative effectiveness where a trial is infeasible | EHR or claims with rich covariates | New-user active-comparator cohort (target-trial emulation) |
| Effect of a single-arm therapy in a rare disease | Historical trial or registry external data | Externally controlled single-arm |
| Effectiveness where a trial is feasible | Prospective data collection | Randomized or pragmatic trial |

The organizing logic is the same throughout: match the design to the specific residual question and to what the data can credibly support ([Vreman et al., 2020](https://doi.org/10.3389/fphar.2020.569535); [Schneeweiss & Miksad, 2025](https://doi.org/10.1002/cpt.3603)).

## 7.11 Common failure modes

A reviewer of an RWE proposal looks for the recurrent errors, each of which maps to a section above:

- choosing the data source before writing the question, so convenience drives the analysis (7.2);
- defining the outcome by an unvalidated code list, introducing misclassification (7.7);
- beginning follow-up before the exposure is defined, introducing immortal time bias (7.3);
- comparing patients already established on treatment, introducing prevalent-user bias (7.3);
- adjusting for a variable on the causal pathway or affected by treatment, introducing overadjustment or collider bias (7.7); and
- running many comparisons and reporting the most favorable, without pre-specification (7.8).

Naming these in the plan, with the response to each, is how a reviewer confirms they were considered rather than overlooked.

## Worked example: reasoning about an external control (anchor case B)

Anchor case B in the case library is the FDA Complex Innovative Trial Design case in alopecia areata, in which a single-arm study is compared against an external control ([FDA, Complex Innovative Trial Design alopecia external-control case](https://www.fda.gov/media/188560/download?attachment=)). Working only from the public case, apply the target-trial logic of sections 7.3 and 7.4.

1. **Specify the emulated trial.** State the eligibility criteria, the treatment strategy and its comparator, time zero, the outcome and its measurement, and the causal contrast, exactly as a randomized protocol would.
2. **Test the assumptions.** Is exchangeability plausible given how the external cohort was selected, and which confounders are measured? Does positivity hold, or are there patient types who could never appear in one arm? Is the intervention well defined?
3. **Test the external control against relevance and reliability.** Does the external population meet the same eligibility criteria? Is the outcome (for example a defined regrowth threshold) measured the same way and at the same times? Was the standard of care in the external data contemporaneous, or drawn from an earlier period when management differed?
4. **Enumerate the threats and the response to each.** Confounding from non-randomized selection, misclassification of the outcome across data sources, and selection from differential follow-up; for each, name the design or analytic response and the residual uncertainty.
5. **Identify the sensitivity analyses.** What would a regulator want simulated: the effect of plausible unmeasured confounding, alternative outcome definitions, and alternative weighting of the external cohort?

FDA notes that each such case focuses on the specific submitted design and does not cover the full development-program evidence needs ([FDA, Complex Innovative Trial Design Meeting Program](https://www.fda.gov/drugs/development-resources/complex-innovative-trial-design-meeting-program)); treat the exercise as reasoning about one design decision, not as a template for a program.

## Applied activity (produces input to capstone work product 5)

Using the assigned capstone product scenario (case J in the case library), take one evidence question from the product's gap list that cannot be answered by a randomized trial, and draft a one- to two-page RWE feasibility note that:

- (a) writes the question as a target-trial protocol (population, exposure, comparator, outcome, time zero);
- (b) selects a candidate RWD source and justifies its fitness for purpose on relevance and reliability;
- (c) names the study design (for example new-user active-comparator cohort, or externally controlled single-arm) and the two or three principal threats to validity with the method for each;
- (d) confirms the intended analysis is permitted under the data source's governance and privacy terms; and
- (e) states plainly whether the result could support the intended regulatory or access decision, and its main residual uncertainty.

This note becomes an input to the integrated evidence generation plan (capstone work product 5).

## AI-use focus

Permitted: use an AI assistant to draft candidate code lists and phenotype definitions (for example the diagnosis and procedure codes that operationalize an outcome), to triage the methods literature, and to summarize a data source's documented contents.

Required controls: validate every code list and phenotype definition against the source data dictionary and, where available, a published validation study, because an unverified algorithm silently introduces misclassification; do not enter identifiable patient-level data or confidential protocols into a tool that is not validated and approved; record the AI use in your audit log (tool, task, what was verified, who is accountable). As a concrete example, if an assistant proposes a set of diagnosis codes to define an outcome, each code must be checked against the coding manual and the study's clinical definition before use, and codes the assistant omitted or invented must be corrected; an unchecked list is a source of misclassification, not a shortcut. Good-practice reports for machine learning and for generative AI in health economics and outcomes research set out the validation, transparency, and reproducibility expectations that apply here ([Padula et al., 2022, PALISADE checklist](https://doi.org/10.1016/j.jval.2022.03.022); [Fleurence et al., 2025, generative AI for HTA](https://doi.org/10.1016/j.jval.2024.10.3846)). This applies the program AI-use policy (`governance/ai_use_policy_and_playbook.md`).

## Knowledge check

1. What is the difference between real-world data and real-world evidence? (Answer: RWD are the data collected outside a conventional randomized trial, such as claims, EHR, registries, and patient-generated data; RWE is the clinical evidence about a product's use, benefits, or risks derived by applying a study design and analysis to those data. Data become evidence only through a design that answers a defined question.)
2. A claims database records dispensed prescriptions and hospitalizations but no laboratory values. For which of these questions is it fit: (a) rate of a hospitalization outcome, or (b) proportion achieving a laboratory-defined response? (Answer: fit for (a); unfit for (b), because it never records the laboratory value that defines the outcome. Fitness is judged against the specific question.)
3. What does specifying a target trial accomplish before any data are analyzed? (Answer: it forces explicit eligibility, treatment strategies, assignment, time zero, outcome, and causal contrast, which prevents design-stage biases such as immortal time bias and prevalent-user bias; see Hernán & Robins, 2016.)
4. State the three causal-inference assumptions and why exchangeability is the hardest to satisfy. (Answer: exchangeability or no unmeasured confounding, positivity, and consistency with a well-defined intervention; exchangeability cannot be verified from the data alone, so its violation by unmeasured confounders must be probed with sensitivity analysis.)
5. Name the three principal threats to validity in RWE and one method that addresses each. (Answer: confounding, addressed by new-user active-comparator design and propensity-score methods, with sensitivity analysis for unmeasured confounding; selection bias, addressed by defining eligibility and time zero as in a target trial; misclassification, addressed by validating the variable-defining algorithm and reporting its accuracy.)
6. For a question about the natural history of a rare disease, which source and design would you triage to first, and why? (Answer: a disease registry or claims/EHR with a descriptive cohort, because the question is descriptive rather than causal and needs disease-specific variables and follow-up rather than a randomized comparator; confirm with the fitness-for-purpose test.)
7. Give one question for which a regulator commonly accepts RWE and one for which it is accepted least readily. (Answer: commonly accepted for safety and natural-history questions and for effectiveness where a trial is infeasible; accepted least readily as the sole basis for a new effectiveness claim where a randomized trial was feasible.)
8. Why is transparency, such as pre-registration and reproducible reporting, treated as a validity method rather than an administrative formality? (Answer: pre-specification and full reporting prevent selection of the most favorable of many possible analyses, which is a form of bias; they let an independent analyst reproduce and criticize the result.)
9. What is the difference between internal validity and transportability, and why can a valid study still fail to answer a decision maker's question? (Answer: internal validity concerns whether the effect is estimated without bias in the study population; transportability concerns whether that effect applies to the different target population of the decision; a study can be internally valid yet not transportable when the effect depends on characteristics distributed differently in the two populations.)
10. An external control study reports a favorable result, but a tipping-point analysis shows that a small, plausible difference in unmeasured baseline severity would reverse it. How should this affect the strength of the conclusion? (Answer: it weakens it substantially; a conclusion that a small plausible bias can overturn is fragile regardless of the point estimate, and the result should be presented with that fragility stated rather than as a firm effect.)

## Key readings

- [Hernán MA, Robins JM. Using Big Data to Emulate a Target Trial When a Randomized Trial Is Not Available. Am J Epidemiol. 2016;183(8):758-764](https://doi.org/10.1093/aje/kwv254)
- [Vreman RA, Leufkens HGM, Kesselheim AS. Getting the Right Evidence After Drug Approval. Front Pharmacol. 2020;11:569535](https://doi.org/10.3389/fphar.2020.569535)
- [Schneeweiss S, Miksad R. Bench to Budget: Integrated Evidence Generation for Medications. Clin Pharmacol Ther. 2025;117(4):869-871](https://doi.org/10.1002/cpt.3603)
- [FDA, Complex Innovative Trial Design Meeting Program](https://www.fda.gov/drugs/development-resources/complex-innovative-trial-design-meeting-program) (external and synthetic control case materials)
- [NICE, health technology evaluations manual (PMG36)](https://www.nice.org.uk/guidance/pmg36/resources/nice-technology-appraisal-and-highly-specialised-technologies-guidance-the-manual-pdf-72286779244741) and [ICER, Guide to Understanding Health Technology Assessment](https://icer.org/wp-content/uploads/2020/10/ICER-Guide-to-Understanding-Health-Technology-Assessment-6.19.18.pdf) (how HTA bodies weigh observational evidence)
- [Padula WV, Kreif N, Vanness DJ, et al. Machine Learning Methods in Health Economics and Outcomes Research: The PALISADE Checklist. Value Health. 2022;25(7):1063-1080](https://doi.org/10.1016/j.jval.2022.03.022) (validation and reporting expectations for computational and AI-assisted work)

## Connection to the capstone

The RWE feasibility note produced here feeds the integrated evidence generation plan (capstone work product 5), where it becomes one row of the evidence matrix that maps each evidence question to a data source, a design, an owner, and a decision point (Module 10). The fitness-for-purpose and validity reasoning also supports the economic model inputs in Module 8 and the value argument for the HTA or payer submission in Modules 8 and 9, because a cost-effectiveness or budget-impact result is only as credible as the effectiveness estimate that feeds it.
