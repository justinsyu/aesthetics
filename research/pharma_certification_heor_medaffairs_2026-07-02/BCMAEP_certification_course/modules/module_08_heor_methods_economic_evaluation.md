# Module 8: HEOR methods: economic evaluation, modeling, and outcomes research

Domain C (Real-world evidence, health economics, and value). Approximately 9 hours.

## Learning objectives

On completion, the learner can:

1. Distinguish the types of economic evaluation (cost-effectiveness, cost-utility, cost-benefit, cost-consequence, and cost-minimization) and select the type appropriate to a decision. (C)
2. Build and interpret a simple decision-analytic model (a decision tree and a Markov cohort model), including the incremental cost-effectiveness ratio (ICER) and the quality-adjusted life-year (QALY). (C)
3. Conduct and interpret one-way and probabilistic sensitivity analysis, and distinguish budget-impact analysis from cost-effectiveness analysis. (C)
4. Critique a published economic evaluation using the CHEERS 2022 reporting standard and a structured critique. (C)

## Why this matters for the career changer

A clinician asks whether a treatment works. A payer or HTA committee asks a second question the clinician rarely has to: is the additional health it produces worth the additional resources it consumes, given that a health budget spent here cannot be spent elsewhere. Economic evaluation is the formal answer to that question, and it is where a large part of medical affairs and market access work is decided. The career changer's task is not to become a modeler overnight but to read an economic model critically, to compute and interpret an ICER, to know why a favorable cost-effectiveness result does not guarantee affordability, and to state a value argument that a committee will find credible. This module builds those skills and feeds the cost-effectiveness summary in the capstone (work product 6).

## 8.1 Types of economic evaluation

All economic evaluations compare at least two options on both costs and consequences. They differ in how consequences are measured.

- **Cost-minimization analysis** applies only when the consequences of the options are equivalent, so the comparison reduces to cost. It is valid only after equivalence is established, not assumed.
- **Cost-effectiveness analysis (CEA)** measures consequences in a natural clinical unit (for example life-years gained, or events avoided). Results are expressed as cost per unit of effect.
- **Cost-utility analysis (CUA)** measures consequences in QALYs, which combine length and quality of life into one unit and so allow comparison across different diseases. CUA is a subtype of CEA and is the form most HTA bodies request.
- **Cost-benefit analysis (CBA)** values consequences in money, which permits comparison beyond health but requires monetizing health outcomes, a step many find contestable.
- **Cost-consequence analysis (CCA)** reports costs and a disaggregated list of consequences side by side without combining them, leaving the trade-off to the reader.

| Evaluation type | Outcome measure | Typical use |
|---|---|---|
| Cost-minimization | None (consequences assumed equivalent) | Options with proven equivalent effect |
| Cost-effectiveness | Natural clinical unit (life-years, events) | A single dominant clinical outcome |
| Cost-utility | QALYs | Cross-disease comparison; most HTA submissions |
| Cost-benefit | Monetary value of outcomes | Comparison beyond health |
| Cost-consequence | Disaggregated list of consequences | Multiple outcomes left for the reader |

Selecting the type follows from the decision and the decision maker. When a jurisdiction's HTA body evaluates in cost per QALY, a cost-utility analysis is required to engage with it; the choice is not a matter of preference. These evaluation types, and the decision situations that select among them, are the standard categories of pharmacoeconomic analysis.

## 8.2 Perspective, the reference case, and the impact inventory

Two analyses of the same intervention can reach different conclusions because they count different costs. The **perspective** defines whose costs and outcomes are included: a health care sector perspective counts medical costs to the health system; a societal perspective adds costs borne outside the health system, such as lost productivity and unpaid caregiving.

The Second Panel on Cost-Effectiveness in Health and Medicine addressed the resulting inconsistency by recommending that a study report a reference case from two perspectives, the health care sector perspective and the societal perspective, so results are comparable across studies, and by introducing an impact inventory: an explicit table of the health and non-health consequences counted under each perspective, so that what is included and excluded is visible rather than buried ([Sanders et al., 2016](https://doi.org/10.1001/jama.2016.12195)). The Second Panel also recommends discounting both future costs and future health outcomes, at a base-case rate of 3% per year, so that consequences occurring at different times are expressed in comparable present-value terms ([Sanders et al., 2016](https://doi.org/10.1001/jama.2016.12195)).

## 8.3 Cost identification, measurement, and valuation

Costs enter a model in three steps, each of which the perspective governs.

- **Identification.** List the resources each option consumes. Direct medical costs (drugs, procedures, hospitalization, monitoring) are counted under any perspective; direct non-medical costs (for example patient travel) and indirect costs (lost productivity, caregiving) are counted only under a societal perspective.
- **Measurement.** Quantify each resource in natural units (for example bed-days, clinic visits, milligrams).
- **Valuation.** Attach a unit cost to each resource, using a consistent price year and reporting the currency and year so results can be compared and updated.

Two costs occurring in different years are not directly comparable until both are discounted to present value, which is why the reference-case discounting in section 8.2 is applied to costs as well as to health outcomes ([Sanders et al., 2016](https://doi.org/10.1001/jama.2016.12195)). As a concrete illustration, a $10,000 cost occurring in year 5, discounted at 3% per year, has a present value of $10,000 divided by 1.03 raised to the fifth power, which is approximately $8,626; future QALYs are discounted by the same factor. Consistency between the perspective declared and the costs actually counted is one of the first things a critique should check.

## 8.4 Measuring health outcomes: clinical outcome assessments and patient-reported outcomes

Outcomes research studies the end results of care as they matter to patients and payers, and it supplies the effectiveness and quality-of-life inputs that an economic evaluation converts into QALYs. Outcomes are measured with clinical outcome assessments, which include clinician-reported, observer-reported, performance, and patient-reported outcome (PRO) measures; PROs capture symptoms, function, and health-related quality of life directly from the patient without clinician interpretation. Two links to the economic model matter:

- PRO and health-status data are the raw material from which health-state preferences (utilities) are derived, so the credibility of a QALY depends on the quality and relevance of the underlying outcome measure ([Sanders et al., 2016](https://doi.org/10.1001/jama.2016.12195)).
- Real-world outcomes (effectiveness, adherence, and PROs collected in routine care) feed the effectiveness inputs of the model and carry the validity concerns of Module 7.

An economic result is therefore only as sound as the outcome measurement beneath it: a poorly validated instrument, or a surrogate endpoint of uncertain relevance, weakens every downstream QALY and ICER. Where the effectiveness input is a surrogate endpoint rather than a final outcome, the model's translation of that surrogate into survival or QALYs becomes a central assumption to test, because an unvalidated surrogate can carry an unquantified error into every result.

## 8.5 Decision trees and Markov cohort models

A decision-analytic model represents the possible consequences of each option as pathways with probabilities, then attaches a cost and a health outcome to each pathway.

A **decision tree** branches from a decision node through chance nodes to outcomes. The expected value of an option is the probability-weighted average across its branches. Trees are well suited to decisions resolved over a short, fixed horizon (for example a single acute episode), and they become unwieldy when events recur or a condition evolves over time.

A **Markov cohort model** represents a chronic condition as a set of mutually exclusive health states (for example progression-free, progressed, dead) with transition probabilities that move a hypothetical cohort among the states over repeated cycles of fixed length. Each state carries a cost and a health-state preference (utility) per cycle; summing over cycles yields total costs and total QALYs.

As a minimal illustration, take three states (progression-free, progressed, dead) with a one-year cycle, and suppose the annual transition probabilities from progression-free are 0.70 to remain, 0.20 to progress, and 0.10 to die, and that a progressed patient has a 0.80 chance of remaining progressed and 0.20 of dying. A cohort that begins fully progression-free is distributed, after one cycle, as 70% progression-free, 20% progressed, and 10% dead. In the second cycle, the 70% progression-free again split 0.70 / 0.20 / 0.10, and the 20% progressed split 0.80 / 0.20 into progressed and dead, so the cohort becomes roughly 49% progression-free, 30% progressed, and 21% dead. Assigning each state a per-cycle utility (for example 0.8 progression-free, 0.5 progressed, 0 dead) and a per-cycle cost, then summing the utility-weighted and cost-weighted time across all cycles to the model horizon (often lifetime for a chronic disease), yields the total QALYs and total costs for that option. The half-cycle correction and an adequate horizon are standard refinements.

Markov cohort models are the workhorse for chronic disease, but they assume that transition probabilities do not depend on how a patient arrived in a state. Where that assumption fails, or where individual histories matter, other structures are used, including partitioned-survival models, individual-level microsimulation, and discrete-event simulation. The choice of structure is itself a modeling assumption that a critique should examine. Regardless of structure, model credibility rests on validation: face validity (whether experts find the structure and results plausible), internal validity (whether the implemented model reproduces its own inputs), and external validity (whether it predicts outcomes it was not built to fit).

## 8.6 Health-state preferences and the QALY

A QALY is one year of life in full health. Time spent in a health state is weighted by a utility on a scale where 1 represents full health and 0 represents death; states rated worse than death can take negative values. For example, two years lived at a utility of 0.5 contribute 2 x 0.5 = 1.0 QALY. Utilities are elicited from preference-based instruments and are the mechanism by which quality of life, not only survival, enters the analysis. Because the utility values often drive the result, their source and instrument are a focus of any critique, and the reference-case discipline exists so that these choices are transparent and comparable rather than tuned to a desired result ([Sanders et al., 2016](https://doi.org/10.1001/jama.2016.12195)).

## 8.7 The ICER, the cost-effectiveness plane, and decision thresholds

The **incremental cost-effectiveness ratio** compares an option with its next-best alternative:

ICER = (cost of B minus cost of A) / (QALYs with B minus QALYs with A) = incremental cost / incremental QALYs.

The ICER is the additional cost per additional QALY gained by choosing B over A. It is helpful to place the comparison on the **cost-effectiveness plane**, whose axes are incremental cost (vertical) and incremental effect (horizontal):

- An option that is more effective and less costly (lower-right quadrant) is **dominant** and needs no ratio; it should be adopted.
- An option that is less effective and more costly (upper-left quadrant) is **dominated** and should be rejected.
- The common case is more effective and more costly (upper-right quadrant), where the decision turns on whether the ICER falls below the threshold.

A cost-effectiveness threshold represents what the decision maker is willing to pay for a QALY, which in turn reflects the health expected to be displaced elsewhere when the budget is spent here. NICE applies a threshold conventionally in the range of £20,000 to £30,000 per QALY gained ([NICE, health technology evaluations manual, PMG36](https://www.nice.org.uk/guidance/pmg36/resources/nice-technology-appraisal-and-highly-specialised-technologies-guidance-the-manual-pdf-72286779244741)); in the US, the Institute for Clinical and Economic Review evaluates value against thresholds it commonly cites between $100,000 and $150,000 per QALY gained ([ICER, Guide to Understanding Health Technology Assessment](https://icer.org/wp-content/uploads/2020/10/ICER-Guide-to-Understanding-Health-Technology-Assessment-6.19.18.pdf)).

A limitation of the ICER is that it is a ratio: it is undefined when the incremental QALYs are zero and can mislead when they are negative. The **net monetary benefit (NMB)** avoids this by expressing the result on a single monetary scale at a chosen threshold (lambda):

NMB = (incremental QALYs x lambda) minus incremental cost.

A positive NMB means the option is cost-effective at that threshold. For an option with 1.2 incremental QALYs and $30,000 incremental cost (the illustration used later in this module), at a threshold of $100,000 per QALY the NMB is (1.2 x $100,000) minus $30,000 = $90,000, which is positive; at a threshold of $20,000 per QALY the NMB is (1.2 x $20,000) minus $30,000 = minus $6,000, which is negative. Because NMB is well behaved when increments are small or negative, it is the quantity usually summarized across a probabilistic sensitivity analysis. When more than two options are compared, they are ranked by cost and each ICER is computed against the next non-dominated option; an option bettered by a mixture of two others is said to be extendedly dominated and is removed from the efficiency frontier.

## 8.8 Sensitivity and uncertainty analysis

A single ICER conceals the uncertainty in its inputs. Two complementary analyses expose it.

- **One-way (deterministic) sensitivity analysis** varies one input at a time across a plausible range while holding the others fixed, and records the effect on the ICER. Displayed as a tornado diagram, it identifies which inputs the conclusion is most sensitive to, which is where further evidence is most valuable.
- **Probabilistic sensitivity analysis (PSA)** assigns each uncertain input a probability distribution and samples them jointly across many simulations (for example a Monte Carlo run of several thousand iterations), producing a distribution of incremental cost and incremental QALY pairs. Summarized as a cost-effectiveness acceptability curve, PSA reports the probability that the intervention is cost-effective at each threshold, which is more informative for a decision maker than a single point estimate.

These methods address parameter uncertainty, the imprecision in each input. Parameter uncertainty should be distinguished from structural uncertainty (whether the model form is correct, explored by running alternative structures) and from heterogeneity (real variation in effect across patient subgroups, handled by subgroup analysis rather than treated as uncertainty). Conflating the three leads to misstated confidence in the result.

## 8.9 Budget impact versus cost-effectiveness

These two analyses answer different questions and are routinely confused.

- **Cost-effectiveness analysis** asks whether the intervention delivers acceptable value per unit of health gained. Its output is a ratio (cost per QALY) compared with a threshold. It is largely independent of how many patients are treated.
- **Budget-impact analysis** asks whether the payer can afford the intervention within a defined population and time horizon (commonly one to five years). Its output is a total expenditure, the number of treated patients multiplied by the net cost per patient, net of any offsetting savings, and it is not divided by QALYs and not compared with a per-QALY threshold.

The two can diverge. An intervention can be highly cost-effective yet impose a budget impact so large that a payer restricts access, and a modestly cost-effective intervention in a small population can be trivially affordable. HTA and payer submissions therefore present both, and formulary submission formats request them as distinct sections ([AMCP, Format for Formulary Submissions guidance](https://www.amcp.org/resource/amcp-format-formulary-submissions-guidance)).

## 8.10 Value frameworks and elements of value

Cost per QALY captures health gain but not every consideration a decision maker may weigh. Value frameworks make the additional considerations explicit and differ by jurisdiction:

- Some frameworks give additional weight to disease severity or to conditions with high unmet need, so that a given QALY gain is valued more in a severe condition.
- Some incorporate considerations beyond the health system, such as productivity and caregiver burden, which correspond to the societal-perspective items in the Second Panel impact inventory ([Sanders et al., 2016](https://doi.org/10.1001/jama.2016.12195)).
- Frameworks also differ in how they treat budget impact and uncertainty as separate deliberative factors.

The practical point for the career changer is that the elements a framework counts, and how it weights them, are set by the specific body, so the value argument must be built to the framework of the target jurisdiction. Published value-assessment and HTA methods documents set out these elements for their respective processes ([ICER, Guide to Understanding Health Technology Assessment](https://icer.org/wp-content/uploads/2020/10/ICER-Guide-to-Understanding-Health-Technology-Assessment-6.19.18.pdf); [NICE, health technology evaluations manual, PMG36](https://www.nice.org.uk/guidance/pmg36/resources/nice-technology-appraisal-and-highly-specialised-technologies-guidance-the-manual-pdf-72286779244741)).

## 8.11 Reporting and critique: CHEERS

A published economic evaluation is credible only if it is reported completely enough to be appraised and reproduced. The Consolidated Health Economic Evaluation Reporting Standards 2022 (CHEERS 2022) provide a 28-item checklist covering the model structure, inputs, perspective, time horizon, discounting, assumptions, uncertainty analysis, and conflicts of interest ([Husereau et al., 2022](https://doi.org/10.1186/s12913-021-07460-7)). A structured critique proceeds item by item:

- is the perspective stated and consistent with the counted costs;
- is the comparator the relevant standard of care;
- are the effectiveness inputs from a credible source (see Module 7 on the quality of real-world effectiveness estimates);
- are utilities from a preference-based instrument;
- is uncertainty characterized with one-way and probabilistic analyses; and
- are funding and conflicts of interest disclosed.

Missing or vague reporting on any of these is itself a finding.

## 8.12 Common errors in economic evaluation

The recurrent errors a reviewer looks for, each mapping to a section above, are:

- claiming cost-minimization without first establishing equivalence of consequences (8.1);
- choosing a comparator that is not the relevant standard of care (8.11);
- declaring one perspective while counting costs from another (8.2, 8.3);
- setting a time horizon too short to capture downstream costs and benefits (8.5);
- reporting a single point ICER with no probabilistic uncertainty (8.8);
- confusing the two questions, by treating a large budget impact as evidence of poor value or a low ICER as evidence of affordability (8.9); and
- using utilities from an unstated or poorly matched instrument (8.6).

Naming the response to each in a submission is what distinguishes a defensible analysis from an advocacy document.

## 8.13 Communicating the result

A committee, and an internal leadership audience, need the result stated plainly. A clear summary states:

- the comparator used;
- the ICER against a named threshold;
- the two or three inputs that drive the result;
- the probability of cost-effectiveness from the probabilistic analysis; and
- the separate budget-impact figure with its assumptions.

Overstating certainty, or presenting a favorable point estimate without its uncertainty, undermines credibility with a technical reviewer and, in a nonpromotional setting, breaches the standards of Module 3. The skills for translating this content to a non-technical executive audience without distorting it are developed in Module 15.

## Worked example: computing and interpreting an ICER (anchor case F)

Anchor case F is the pharmacoeconomic critique case in the case library. The following inputs are illustrative and are used only to demonstrate the arithmetic and its interpretation; they are not drawn from a specific product.

Consider a new drug B compared with standard care A over a defined horizon, from a health care sector perspective, with costs and QALYs discounted at 3% ([Sanders et al., 2016](https://doi.org/10.1001/jama.2016.12195)).

| Option | Total cost | Total QALYs |
|---|---|---|
| A (standard care) | $20,000 | 3.0 |
| B (new drug) | $50,000 | 4.2 |

- Incremental cost = $50,000 minus $20,000 = $30,000.
- Incremental QALYs = 4.2 minus 3.0 = 1.2.
- **ICER = $30,000 / 1.2 = $25,000 per QALY gained.**

Because B is both more costly and more effective, it sits in the upper-right quadrant of the cost-effectiveness plane, so the decision turns on the threshold. At $25,000 per QALY, drug B falls below the US thresholds noted in section 8.7 and below the upper end of the NICE range, so on cost-effectiveness grounds it would generally be considered good value.

Sensitivity analysis is required before that conclusion is trusted. A one-way analysis records the ICER as each input moves across its plausible range:

| Input varied (range) | At the low end | At the high end |
|---|---|---|
| Incremental QALY (0.6 to 1.8) | 0.6 QALY, ICER $50,000/QALY | 1.8 QALY, ICER $16,667/QALY |
| Drug B total cost ($44,000 to $56,000) | $44,000, ICER $20,000/QALY | $56,000, ICER $30,000/QALY |
| Comparator total cost ($14,000 to $26,000) | $14,000, ICER $30,000/QALY | $26,000, ICER $20,000/QALY |

The conclusion is most sensitive to the incremental QALY, which is therefore where additional evidence would be most valuable; across the ranges shown, the ICER remains below common thresholds. A probabilistic sensitivity analysis would go further and report the probability that B is cost-effective at each threshold.

Now contrast the budget impact. Suppose 8,000 patients are eligible and treated in the first year, and the net cost per patient (drug cost minus offset savings) is $30,000. The first-year budget impact is 8,000 x $30,000 = $240 million, regardless of the favorable ICER. This is the divergence in section 8.9: B is cost-effective per QALY yet may still exceed what the payer can absorb in a single year, which is why the value story must address both the ratio and the total. Weighing the cost-effectiveness ratio against the total budget impact in this way is central to managed-care assessment.

## Worked example: reading a committee's cost-effectiveness reasoning (anchor case D)

The illustrative computation above shows the arithmetic; anchor case D shows how a committee actually weighs it. The Australian Pharmaceutical Benefits Advisory Committee published a public summary document for pembrolizumab in early triple-negative breast cancer, prepared under the committee's submission guidelines ([PBAC, Public Summary Document, pembrolizumab early triple-negative breast cancer, 2023](https://www.pbs.gov.au/industry/pbac/psd/2023/03/pembrolizumab-early-tnbc-psd-03-2023.pdf?variant=3); [PBAC, Guidelines for preparing a submission, version 5](https://pbac.pbs.gov.au/content/information/files/pbac-guidelines-version-5.pdf)). Working only from the public document, a learner can trace how the committee reasoned about the elements of this module: which comparator it accepted, how it treated the ICER and the assumptions behind it, where it judged the economic model uncertain (for example extrapolation of benefit beyond the trial follow-up, or the choice of utilities), and how it considered budget impact separately from cost-effectiveness. The exercise is to map each committee concern to the section of this module it corresponds to, then state what additional evidence would have reduced the uncertainty. PBAC methods are jurisdiction-specific and should not be generalized to other HTA bodies.

## Applied activity (produces capstone work product 6, cost-effectiveness summary)

Using the assigned capstone product scenario (case J), build an introductory spreadsheet cost-effectiveness model comparing the product with the relevant comparator:

- define the perspective and time horizon;
- enter costs and QALYs for each option;
- compute the incremental cost, the incremental QALYs, and the ICER, and place the result on the cost-effectiveness plane;
- run a one-way sensitivity analysis on the two or three inputs most likely to change the conclusion and present a tornado diagram; and
- add a separate first-year budget-impact estimate for the eligible population.

Write a one-page interpretation memo that states the ICER against a named threshold, identifies the drivers of uncertainty, and explains why the budget-impact figure is a distinct consideration from the ICER. This model and memo become the cost-effectiveness summary within the HTA or payer submission outline (capstone work product 6, developed further in Module 9).

## AI-use focus

Permitted: use an AI assistant to help structure a model (state definitions, cost and outcome categories), to draft model documentation and the interpretation memo, and to draft the CHEERS critique outline.

Required controls: independently verify the model logic and every input; an AI assistant will produce plausible transition probabilities, utilities, and costs that are not traceable to any source, and each must be replaced with a value cited to a real source before use. Recompute the ICER by hand or in a checked formula rather than trusting a generated number. Distinguish spreadsheet models, which are transparent and auditable and suit an introductory analysis, from programmed models, which handle greater complexity but require more validation. Record every AI contribution in the audit log. The ISPOR good-practice reports on machine learning and on generative AI in health economics and outcomes research set the validation, transparency, and reproducibility expectations that govern this use ([Padula et al., 2022, PALISADE checklist](https://doi.org/10.1016/j.jval.2022.03.022); [Fleurence et al., 2025, generative AI for HTA](https://doi.org/10.1016/j.jval.2024.10.3846)). This applies the program AI-use policy (`governance/ai_use_policy_and_playbook.md`).

## Knowledge check

1. When is cost-minimization analysis the appropriate type, and what must be established first? (Answer: only when the consequences of the compared options are equivalent, so the comparison reduces to cost; equivalence must be established by evidence, not assumed.)
2. Compute the ICER for a treatment that costs $60,000 and yields 5.0 QALYs versus a comparator that costs $24,000 and yields 3.5 QALYs. (Answer: incremental cost $36,000, incremental QALYs 1.5, ICER = $36,000 / 1.5 = $24,000 per QALY gained.)
3. On the cost-effectiveness plane, what does it mean for an option to be dominant, and does it require an ICER? (Answer: it is more effective and less costly than the comparator, lower-right quadrant; it should be adopted and needs no ratio.)
4. Why can an intervention be cost-effective yet still be restricted by a payer? (Answer: cost-effectiveness is value per QALY against a threshold and is largely independent of the number treated, whereas budget impact is total expenditure over a defined population and horizon; a favorable ICER can coexist with a budget impact the payer cannot absorb.)
5. How do patient-reported outcomes connect to a cost-utility analysis? (Answer: PRO and health-status data are the basis from which health-state preferences, the utilities that weight time in each state, are derived, so a QALY is only as credible as the outcome measurement beneath it.)
6. What do the two reference-case perspectives recommended by the Second Panel include, and what is the impact inventory for? (Answer: a health care sector perspective and a societal perspective; the impact inventory is an explicit table of the health and non-health consequences counted under each perspective, making inclusions and exclusions visible; see Sanders et al., 2016.)
7. What does a probabilistic sensitivity analysis add beyond a one-way analysis? (Answer: it varies all uncertain inputs jointly using their distributions across many simulations and yields the probability that the intervention is cost-effective at each threshold, rather than the effect of one input at a time.)
8. Name three CHEERS 2022 items you would check when appraising a published cost-utility analysis. (Answer examples: whether the perspective is stated and consistent with the counted costs; whether the comparator is the relevant standard of care; whether uncertainty is characterized with one-way and probabilistic analyses; whether the source of effectiveness inputs and utilities is credible; whether funding and conflicts of interest are disclosed; see Husereau et al., 2022.)
9. A cost of $10,000 occurs in year 5. At a 3% annual discount rate, what is its approximate present value, and why does discounting matter? (Answer: $10,000 divided by 1.03 raised to the fifth power, approximately $8,626; discounting expresses future costs and health outcomes in comparable present-value terms so that the timing of consequences does not distort the comparison; see Sanders et al., 2016.)
10. At a threshold of $100,000 per QALY, compute the net monetary benefit of an option with 1.2 incremental QALYs and $30,000 incremental cost, and state what its sign means. (Answer: NMB = (1.2 x $100,000) minus $30,000 = $90,000; a positive NMB means the option is cost-effective at that threshold, and the net monetary benefit is preferred to the ICER when incremental QALYs are near zero or negative.)
11. A drug has a net cost per patient of $25,000, and 12,000 eligible patients are treated in year 1. What is the first-year budget impact, and is it the same as the drug's cost-effectiveness? (Answer: 12,000 x $25,000 = $300 million; no, budget impact is total expenditure over a defined population and horizon and is distinct from the cost per QALY that determines cost-effectiveness.)
12. An analysis is declared from a societal perspective but counts only direct medical costs. What is the flaw? (Answer: the declared perspective and the counted costs are inconsistent; a societal perspective requires including costs borne outside the health system, such as lost productivity and caregiving, as set out in the Second Panel impact inventory; see Sanders et al., 2016.)

## Key readings

- [Sanders GD, Neumann PJ, Basu A, et al. Recommendations for Conduct, Methodological Practices, and Reporting of Cost-effectiveness Analyses: Second Panel on Cost-Effectiveness in Health and Medicine. JAMA. 2016;316(10):1093-1103](https://doi.org/10.1001/jama.2016.12195)
- [Husereau D, Drummond M, Augustovski F, et al. Consolidated Health Economic Evaluation Reporting Standards 2022 (CHEERS 2022) Statement. 2022](https://doi.org/10.1186/s12913-021-07460-7)
- [ICER, Guide to Understanding Health Technology Assessment](https://icer.org/wp-content/uploads/2020/10/ICER-Guide-to-Understanding-Health-Technology-Assessment-6.19.18.pdf) and [NICE, health technology evaluations manual (PMG36)](https://www.nice.org.uk/guidance/pmg36/resources/nice-technology-appraisal-and-highly-specialised-technologies-guidance-the-manual-pdf-72286779244741) (thresholds and decision rules)
- [AMCP, Format for Formulary Submissions guidance](https://www.amcp.org/resource/amcp-format-formulary-submissions-guidance) (how cost-effectiveness and budget-impact evidence are presented to payers)
- [PBAC, Public Summary Document, pembrolizumab early triple-negative breast cancer, 2023](https://www.pbs.gov.au/industry/pbac/psd/2023/03/pembrolizumab-early-tnbc-psd-03-2023.pdf?variant=3) and [PBAC, Guidelines for preparing a submission, version 5](https://pbac.pbs.gov.au/content/information/files/pbac-guidelines-version-5.pdf) (a committee's cost-effectiveness reasoning)
## Connection to the capstone

The cost-effectiveness model and interpretation memo built here are the cost-effectiveness summary inside the HTA or payer submission outline (capstone work product 6), which Module 9 develops into a full submission argument for a chosen jurisdiction. The effectiveness inputs to this model trace back to the RWE feasibility reasoning of Module 7 and to the evidence matrix of Module 10: an ICER is only as credible as the effectiveness estimate that feeds it, which is why the economic and evidence-generation work products are assessed as one integrated portfolio.
