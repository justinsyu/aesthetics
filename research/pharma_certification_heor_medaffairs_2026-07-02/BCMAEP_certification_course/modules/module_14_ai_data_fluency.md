# Module 14: AI and data fluency for medical affairs and evidence generation

Domains E (Data and AI fluency) and F (Compliance, ethics, and accountability). Approximately 7 hours.

## Learning objectives

On completion, the learner can:

1. Explain, at a working level, how large language models and common machine-learning methods function and where they fail (hallucination, bias, drift, reproducibility). (E)
2. Apply the program AI-use policy: permitted uses, validation, source verification, privacy, disclosure, and human accountability. (E, F)
3. Situate AI use within current regulatory and professional guidance, including the FDA and EMA positions on AI, the ISPOR good practices for machine learning and generative AI in HEOR, and publication-ethics positions on AI. (E, F)
4. Evaluate an AI tool, workflow, or vendor for fitness, bias, reproducibility, and governance. (E, F)

## Why this matters for the career changer

A clinician who uses a decision-support tool at the bedside asks a narrow question: does this tool help me make a better decision for this patient. An industry professional who uses AI in evidence work carries a wider set of obligations.

The output may enter a publication, a payer submission, a regulatory interaction, or a field-medical conversation, and someone must be able to defend how it was produced to an editor, a compliance officer, and an HTA reviewer. The professional is accountable not only for the decision but for the provenance of the evidence behind it.

Fluency here is not the ability to write clever prompts. It is the ability to state what a model can and cannot do, to verify what it produces, to protect confidential and patient data, to disclose assistance, and to keep a record that a reviewer can audit.

This module teaches those capabilities and defines the standard that every other module applies. It is the concept layer beneath the program AI-use policy (`governance/ai_use_policy_and_playbook.md`), which is the operative standard the capstone enforces.

The credentialing field has moved in this direction. The ACMA BCMAS curriculum has incorporated AI literacy, including a module on AI foundations and treatment of artificial intelligence as an emerging area of the field ([ACMA, BCMAS Program Information](https://medicalaffairsspecialist.org/certifications/bcmas/program-info)).

BCMAEP goes further by making AI governance an operative policy that is applied in every module and audited in the capstone. The distinction is between knowing that AI exists and being able to document that a specific use of it met a defined standard.

## 14.1 Data fluency: sources, quality, and fitness for purpose

Data fluency precedes AI fluency, because every model is a function of the data it learned from and every output is only as sound as the data behind it.

Two distinctions do most of the work. The first is structured versus unstructured data: structured data are values in defined fields (a claims table, a trial dataset, a formulary file), while unstructured data are free text or images (a publication, a label, a medical inquiry, a slide). Many AI tools in medical affairs act on unstructured text, which is harder to validate than a tabular field.

The second distinction is fitness for purpose: a dataset that is accurate for one question can be misleading for another. The relevant test is not whether data are "good" in the abstract but whether they fit the specific use.

A short set of questions establishes fitness before any analysis or AI step:

- **Provenance:** where did the data come from, who collected them, and for what original purpose?
- **Completeness and quality:** what is missing, how are missing values handled, and how were errors checked?
- **Representativeness:** whom or what do the data cover, and who is absent, since absence drives bias downstream?
- **Timeliness:** how current are the data relative to the decision they will inform?
- **Permission:** are the data allowed to be used for this purpose, and do privacy and contractual terms permit entering them into a given tool?

These questions carry directly into the fitness-for-purpose reasoning applied to real-world data sources in Module 7 and to the inputs of an economic model in Module 8.

The point for this module is that a fluent user interrogates the data before trusting anything a model does with them. A model cannot correct a defect in the data it was given; it can only propagate it, often with added confidence.

## 14.2 How machine learning works at a working level

A machine-learning model learns statistical relationships from examples rather than from explicit rules.

The learner does not need the mathematics, but does need the shape of the method, because the shape determines where it can be trusted.

- **Supervised learning** trains on inputs paired with known outputs (features and labels) and learns to predict the label for a new input. Classification predicts a category (for example, does this record indicate the condition of interest); regression predicts a quantity (for example, expected cost).
- **Unsupervised learning** finds structure in data without labels, for example grouping similar records or reducing many variables to a few.
- **Training, validation, and testing** separate the data used to fit a model from the data used to tune it and the data used to estimate how it will perform on inputs it has not seen. A model that performs well on its training data but poorly on new data is overfit; it has memorized noise rather than learning a generalizable pattern.

The single most important idea is that a model estimates patterns that held in its training data and applies them to new inputs. It does not understand the domain.

When new inputs differ from the training data, performance can degrade without warning. This is why the match between the training data and the intended use is the first thing to check, and it is the reason data fluency (14.1) comes before AI fluency.

## 14.3 How large language models work, and prompt design and retrieval

A large language model is a specific case of a learned model. It is trained on large text corpora to predict the next unit of text (a token) given the preceding context, and at use time it generates a plausible continuation one token at a time.

Instruction tuning and preference feedback then shape the raw model into one that follows instructions and produces helpful responses. The learner does not need these mechanics in detail, only their implication for accountability.

This mechanism has one consequence that governs everything else: the model produces text that is statistically likely given its training, not text retrieved from a verified source of record. It can compose a fluent sentence, a well-formed citation, or a confident numerical claim that has no basis in fact.

Treating the output as a draft to be verified, rather than as a lookup result, therefore follows directly from how the model works, not from caution alone.

Applied work has acquired a common vocabulary for the techniques used to steer these models. An ISPOR working group has defined a taxonomy of generative-AI concepts, together with the current limitations of each ([Fleurence et al., 2025, taxonomy of generative AI in HEOR](https://doi.org/10.1016/j.jval.2025.04.2167)):

- **Prompt engineering** structures the instruction to shape the output: stating the role, the task, the constraints, the format, and, where useful, an example. A precise prompt reduces vague or off-target output but does not make the output true.
- **Retrieval-augmented generation** supplies the model with source documents at query time so its answer is grounded in provided text rather than in its training alone. This reduces, but does not remove, the risk of unsupported claims, because the model can still misread or misattribute the supplied passages.
- **Fine-tuning** further trains a model on task-specific data to specialize its behavior.
- **Agents** chain multiple model calls to take multi-step actions; the more autonomous the chain, the more places an unverified step can propagate an error.

Prompt design, in practice, is less a matter of wording tricks than of supplying what the model needs: the role it should take, the exact task, the constraints and scope, the required output format, and the source material it must use. A few habits improve reliability:

- State the task and the intended audience explicitly rather than assuming the model will infer them.
- Give the model the source text to work from when accuracy matters, rather than relying on its training.
- Ask for the reasoning or the source of each claim, so each can be checked.
- Constrain the output format so it is easy to verify against a source.
- Ask the model to flag uncertainty and to say when it does not know, rather than to fill gaps.

The practical lesson is that these techniques change how a model behaves, not whether its output requires verification. Retrieval and careful prompting improve grounding and relevance; they do not transfer accountability to the tool.

## 14.4 Where AI fails: hallucination, bias, drift, and reproducibility

Four failure modes recur across machine-learning and generative-AI work, and each has a corresponding control. Naming them precisely is what allows a professional to anticipate and manage them rather than discover them after the fact.

- **Hallucination.** Because generation is probabilistic rather than retrieval-based, a model can produce fluent, confident content that is fabricated, including invented references, quotations, statistics, and study results. This is a property of the method, not an occasional defect that better wording removes. The control is verification of every factual claim and every citation against a primary source before use, which is why publication and HEOR guidance emphasize human oversight of generative output rather than acceptance of it ([Fleurence et al., 2025, generative AI for HTA](https://doi.org/10.1016/j.jval.2024.10.3846)). In practice, a model may return a citation with real-looking authors, journal, and year that does not exist; the only defense is to resolve the identifier against a primary index.
- **Bias.** A model reflects patterns in its training data, including systematic ones, so it can err differently for different subgroups, data sources, or phrasings. This matters wherever outputs affect people or shape evidence. The control is to evaluate a tool for fitness and fairness before relying on it and to check outputs for systematic error, applying a transparency standard where machine learning is used ([Padula et al., 2022, PALISADE checklist, ISPOR](https://doi.org/10.1016/j.jval.2022.03.022)).
- **Drift.** Performance degrades when the inputs a model sees diverge from the data it was trained on (data drift) or when the underlying relationship changes over time (concept drift). Deployed model versions also change, sometimes without notice, so a workflow that was validated once is not validated forever. The control is to monitor performance against a check set over time and to record the model and version in use.
- **Reproducibility.** Generative models sample from a probability distribution, so the same prompt can produce different outputs across runs and across model versions. Without recorded prompts, settings, and versions, a colleague cannot reproduce or audit the result. The control is documentation sufficient for a reviewer to understand what was done and, where relevant, repeat it; the PALISADE checklist provides a transparency structure for machine-learning work in HEOR ([Padula et al., 2022](https://doi.org/10.1016/j.jval.2022.03.022)).

The common thread is that none of these failures is fixed by the model becoming more fluent. If anything, greater fluency can mask them, because an incorrect answer that reads well is harder to catch than one that reads poorly.

Each failure is managed by a human control rather than by the model: verification for hallucination, fairness evaluation for bias, monitoring for drift, and documentation for reproducibility. These four controls are the concrete content of the program AI-use policy that follows.

## 14.5 Validation and the human in the loop

"Human in the loop" is often used loosely, sometimes to mean no more than that a person was present. In this program it has a specific meaning: a named person reviews the AI output against a defined standard before the output is used or released, and that review is recorded.

The depth of the required review scales with risk.

It ranges from a fact check on an orientation summary, to full verification, medical review, and disclosure on a released document, up to tasks that are not permitted at all.

| Risk tier | Example task | Human-in-the-loop requirement |
|---|---|---|
| Low | Literature summary to orient a search | Fact check before any claim is carried forward |
| Moderate | Evidence-table extraction; code-list draft | Verify every extracted value or definition against the source |
| High | Medical-information response; manuscript or abstract | Full reference and fact verification, medical review, and disclosure before release |
| Not permitted | Automated safety adjudication | No autonomous decision; validated systems and human accountability required (Module 6) |

Validation is not a one-time event. A workflow is validated for a defined task on a defined kind of input.

When the task, the input, or the model version changes, the validation is revisited. This is the operational meaning of the drift control in 14.4 and the reason the tool and version are recorded in the audit log (14.9).

## 14.6 Privacy, confidentiality, and intellectual property

Three data-handling risks are distinct, and each has its own rule. They are often confused, which is why they are separated here.

- **Privacy.** Patient-level data and personally identifiable information are not entered into an AI tool unless the tool is validated, approved, and contractually governed for that purpose. The privacy and confidentiality frameworks introduced in Module 3 (for example HIPAA and GDPR at a working level) apply to AI inputs exactly as they apply to any other handling of the data.
- **Confidentiality.** Proprietary or commercially sensitive company information (unpublished data, strategy, draft submissions) is treated the same way, because a general tool may retain or train on what is entered. The default is exclusion when in doubt.
- **Intellectual property.** Generated content can reproduce third-party material, and public availability of a source does not grant rights to reproduce it. Learners should treat archived third-party materials as assigned-reading links to cite, not text to reproduce, and should not paste substantial third-party content into a tool or a deliverable without permission ([BCMAEP source register, verification status and cautions](references/source_register.md)).

The unifying rule is simple to state and easy to violate under time pressure: know where inputs and outputs go, and who can see them, before entering anything. This is the data-governance question in the tool evaluation (14.10), and it is the point at which many otherwise compliant workflows fail.

## 14.7 The program AI-use policy applied

The program AI-use policy operationalizes six principles that this module explains and that every module enforces (`governance/ai_use_policy_and_playbook.md`). Each principle is the operational form of a failure mode or obligation described above.

1. **Human accountability.** A named person is accountable for every AI-assisted output. AI tools cannot be authors and cannot bear responsibility, because they cannot be responsible for the accuracy, integrity, and originality of the work ([ICMJE, Defining the Role of Authors and Contributors](https://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html)).
2. **Source verification.** Every factual claim and every citation produced with AI assistance is verified against a primary source before use. This is the control for hallucination described in 14.4.
3. **Privacy and confidentiality.** Patient-level data, personally identifiable information, and confidential or proprietary company information are not entered into an AI tool unless the tool is validated, approved, and contractually governed for that purpose, with exclusion the default when in doubt.
4. **Disclosure.** AI assistance is disclosed where the output is shared. GPP 2022 addresses the compliant incorporation of new and emerging publication tools ([DeTora et al., 2022, GPP 2022](https://doi.org/10.7326/M22-1460)), and the ICMJE recommendations require disclosure of AI-assisted technologies at submission and place responsibility for the content, including plagiarism and accuracy review, on the human authors ([ICMJE](https://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html)).
5. **Fitness, fairness, and bias.** A tool is evaluated for fitness for the specific task and for bias before it is relied upon; outputs affecting people or evidence are checked for systematic error.
6. **Reproducibility and documentation.** AI use is documented so that a colleague or reviewer can understand what was done and, where relevant, reproduce it, applying transparency standards such as the PALISADE checklist where machine learning is used ([Padula et al., 2022](https://doi.org/10.1016/j.jval.2022.03.022)).

The policy translates these principles into a task classification that is applied in every module's applied activity. "Conditional" means permitted only with the stated control ([program AI-use policy](governance/ai_use_policy_and_playbook.md)).

| Task | Classification | Required control |
|---|---|---|
| Summarizing published literature to orient a search | Permitted | Verify all facts and citations against primary sources before use |
| Drafting an outline for a work product | Permitted | Human authorship and editing; no unverified claims carried forward |
| Extracting study characteristics into an evidence table | Conditional | Verify every extracted value against the source article |
| Drafting code lists or phenotype definitions for RWE | Conditional | Validate every definition against source documentation |
| Drafting a standard medical-information response | Conditional | Verify every reference and fact; disclose AI assistance; medical review before release |
| Structuring or documenting an economic model | Conditional | Independently verify model logic and inputs; apply the PALISADE transparency checklist where machine learning is used |
| Drafting a manuscript or abstract with AI assistance | Conditional | Disclose per journal and GPP 2022; human authors accountable; AI not an author; verify all references |
| Entering patient-level or confidential company data into a general AI tool | Prohibited | Use only a validated, approved, contractually governed environment |
| Presenting AI output as fact without verification | Prohibited | Not permitted under any circumstance |
| Automated safety adjudication without human sign-off | Prohibited | Pharmacovigilance decisions require validated systems and human accountability |
| Fabricating or guessing a citation, DOI, or data point | Prohibited | Not permitted; mark a gap instead |

The correct response to a claim that cannot be verified is to mark a gap, not to guess. The classification is deliberately conservative: when a task is not clearly permitted, it is treated as conditional and the control is applied.

## 14.8 The regulatory and professional guidance landscape

Learners are expected to situate their AI use within current guidance.

The requirement is not to memorize these documents but to know they exist, what they say at a principle level, and where to find them, because the guidance is what a reviewer will expect a professional to be aware of.

- **FDA.** In January 2025 the FDA issued draft guidance, "Considerations for the Use of Artificial Intelligence To Support Regulatory Decision-Making for Drug and Biological Products," its first guidance on AI in drug and biologic development; the availability notice was published in the Federal Register on January 7, 2025 ([Federal Register, FDA AI draft guidance notice](https://www.federalregister.gov/documents/2025/01/07/2024-31542/considerations-for-the-use-of-artificial-intelligence-to-support-regulatory-decision-making-for-drug)), and the draft guidance and related materials are collected on the FDA CDER resource hub ([FDA, Artificial Intelligence in Drug Development](https://www.fda.gov/about-fda/center-drug-evaluation-and-research-cder/artificial-intelligence-drug-development); [FDA, AI draft guidance (PDF)](https://www.fda.gov/media/184830/download)). It proposes a risk-based credibility assessment for an AI model tied to a defined context of use, spanning nonclinical, clinical, postmarketing, and manufacturing phases. The practical lesson is that the level of scrutiny should scale with how much the AI output influences a decision and how consequential that decision is.
- **EMA.** The European Medicines Agency published a "Reflection paper on the use of Artificial Intelligence in the medicinal product lifecycle" (EMA/CHMP/CVMP/83833/2023) on September 30, 2024, setting out principles for applying AI and machine learning at any step of the medicine lifecycle ([EMA, use of AI in the medicinal product lifecycle](https://www.ema.europa.eu/en/use-artificial-intelligence-ai-medicinal-product-lifecycle)).
- **ISPOR (HEOR).** The PALISADE checklist is a good-practices report for machine-learning methods in HEOR and provides a transparency checklist across five application areas ([Padula et al., 2022](https://doi.org/10.1016/j.jval.2022.03.022)). Two ISPOR working-group reports address generative AI: one on the opportunities, challenges, and policy considerations for HTA, which emphasizes human oversight ([Fleurence et al., 2025, generative AI for HTA](https://doi.org/10.1016/j.jval.2024.10.3846)), and one defining a taxonomy of generative-AI concepts for HEOR with their current limitations ([Fleurence et al., 2025, taxonomy of generative AI in HEOR](https://doi.org/10.1016/j.jval.2025.04.2167)).
- **Publications.** GPP 2022 covers ethics, transparency, and the compliant incorporation of new publication tools ([DeTora et al., 2022](https://doi.org/10.7326/M22-1460)); the ICMJE recommendations place responsibility for AI-assisted content on the human authors and prohibit listing AI tools as authors ([ICMJE](https://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html)).
- **Medical affairs practice.** MAPS has published a 2024 benchmark report on digital, advanced analytics, and AI in medical affairs, surveying 32 companies, which situates AI adoption and governance in current practice ([MAPS, Digital, Advanced Analytics and AI in Medical Affairs benchmark report, 2024](https://medicalaffairs.org/wp-content/uploads/2024/10/MAPS-Digital-Advanced-Analytics-Artificial-Intelligence-Report-2024.pdf)).

A single thread runs through all five. Each body places a human, not the tool, in the position of accountability, and each ties the required scrutiny to how much the AI output influences a consequential decision.

Because the FDA, EMA, ISPOR, and publication bodies have all issued or updated AI guidance recently, the field is treated as fast-moving. The program therefore requires continuing education in AI governance each recertification cycle rather than treating this module as a one-time competency ([program AI-use policy](governance/ai_use_policy_and_playbook.md)).

## 14.9 Building the AI-use log

The AI-use log is the record that makes AI use auditable. Every learner maintains one across the portfolio, and it is capstone work product 8. Each material AI use is one row, with the fields defined in the policy ([program AI-use policy](governance/ai_use_policy_and_playbook.md)):

- **Date:** when the AI was used.
- **Work product:** which deliverable the use supported.
- **Tool:** the specific tool or model and version (this supports reproducibility and drift tracking).
- **Task:** what the AI was asked to do.
- **Data handling:** what data were entered, and confirmation that no confidential or patient data entered a non-approved tool.
- **Verification:** what was checked, against which primary source, and the result.
- **Changes made:** how the human edited or corrected the output.
- **Accountable person:** the named person responsible for the final output.
- **Disclosure:** where and how the AI use was disclosed, if the output was shared.

Two failure states are graded strictly. A portfolio that used AI without a log is returned, and a log that shows unverified claims carried into a deliverable fails the compliance and evidence dimensions of the capstone rubric.

The log is not paperwork added after the fact. It is completed as the work is done, because verification recorded at the point of use is the evidence that the six principles were followed; a log reconstructed later cannot demonstrate that verification actually preceded use.

## 14.10 Evaluating a tool, workflow, or vendor

Evaluation is where the preceding sections become a single judgment. Before relying on a tool for a task, the learner answers and documents six questions, which are the tool-evaluation deliverable and a required part of the capstone AI-use plan ([program AI-use policy](governance/ai_use_policy_and_playbook.md)):

1. **Fitness:** is the tool designed and validated for this task, or is it being used outside its intended purpose?
2. **Data governance:** where do inputs and outputs go, who can see them, and are confidentiality and privacy preserved?
3. **Accuracy and hallucination risk:** how are factual claims and citations verified, and what is the observed error rate on a check set?
4. **Bias:** could the tool systematically err for some groups or inputs, and how is that checked?
5. **Reproducibility:** can the process be described and, where needed, repeated, and are prompts and settings recorded?
6. **Accountability:** who signs off, and what is the escalation path if the tool fails?

When the tool is a purchased vendor product rather than an internally built workflow, the same six questions apply, with additional procurement considerations:

- What data the vendor retains, and whether it trains on customer inputs.
- Whether the vendor documents model versions and changes, so drift can be tracked.
- Whether performance claims are supported by evidence the buyer can inspect.
- Where liability and accountability sit contractually.

A compliant organization approves tools and use cases through an accountable function and restricts general tools to non-confidential tasks ([program AI-use policy](governance/ai_use_policy_and_playbook.md)). The learner's evaluation should reach a decision that would satisfy such a function.

The point of the evaluation is to reach a defensible decision about whether and how to use the tool, not to produce a favorable verdict.

A tool that is unfit, ungoverned for the data involved, or unverifiable should be declined for that task, and the evaluation documents why. Declining a tool for a task is a valid and often correct outcome.

## Worked example: evaluating a retrieval-augmented literature-summarization workflow

Consider a workflow that answers medical questions by retrieving passages from an internal document set and generating a summary with citations, a retrieval-augmented generation design in the ISPOR taxonomy sense ([Fleurence et al., 2025, taxonomy](https://doi.org/10.1016/j.jval.2025.04.2167)).

Applying the six questions:

- **Fitness:** the tool is intended for drafting orientation summaries, not for producing final medical-information responses, so its use is bounded to a draft.
- **Data governance:** the internal corpus and queries must remain in an approved environment; general consumer tools are excluded because confidential material is involved.
- **Accuracy:** each cited passage is checked against the source document, because retrieval grounds but does not guarantee correct attribution; an error rate is estimated on a check set of known questions.
- **Bias:** the team checks whether the tool answers well for common questions but poorly for rare indications or subpopulations underrepresented in the corpus.
- **Reproducibility:** the prompt template, model version, and retrieval settings are recorded so a reviewer can repeat the run.
- **Accountability:** a named medical reviewer signs off before any answer is released, and the escalation path is to withhold release if verification fails.

The workflow is accepted for drafting under these controls and logged accordingly; it is not accepted for unreviewed external release.

This mirrors the policy classification of a medical-information response as a conditional use requiring verification, disclosure, and medical review ([program AI-use policy](governance/ai_use_policy_and_playbook.md)). The evaluation did not ask whether the tool is impressive; it asked whether its output can be trusted for a specific purpose and who is answerable if it is not.

## Applied activity (produces capstone work product 8)

Using the assigned capstone product scenario, build two artifacts.

First, an AI-use plan for the portfolio: state, for each work product where AI will assist, the permitted task and its required control drawn from the policy classification, and the accountable person. Second, an AI-use audit log with the nine fields above, populated as you complete the other work products, showing what was entered, what was verified against which primary source, and how the output was corrected.

Then apply the six-question evaluation to one AI workflow you actually used in the portfolio (for example an evidence-table extraction, a code-list draft, or a literature summary) and record the decision and its rationale. Together these become capstone work product 8, the AI-use plan and audit log spanning the portfolio.

## AI-use focus

This module defines the standard applied everywhere else in the program. Every other module's AI-use focus box is a specific application of the six principles taught here: verify every date and regulatory fact (Modules 1 and 5); verify every extracted value in an evidence table (Module 4); validate every code list and phenotype definition (Module 7); independently verify model logic and inputs (Module 8); disclose AI assistance and secure medical review before release (Module 12).

The deliverable of this module, the AI-use plan and audit log, is the instrument that demonstrates the standard was met across the portfolio (`governance/ai_use_policy_and_playbook.md`).

## Knowledge check

1. Why does a large language model produce fabricated references even when it sounds confident? (Answer: it generates statistically plausible next tokens rather than retrieving from a source of record, so a well-formed but false citation is a property of the method, not an occasional defect; the control is verification against a primary source.)
2. A colleague enters a de-identified but proprietary trial dataset into a public consumer chatbot to draft a summary. Which principle is violated, and what should have happened? (Answer: privacy and confidentiality; proprietary company data should not enter a tool that is not validated, approved, and contractually governed, so an approved environment or exclusion was required.)
3. Distinguish data drift from a reproducibility problem. (Answer: drift is degraded performance when inputs diverge from training data or the underlying relationship changes over time; a reproducibility problem is that the same prompt can yield different outputs across runs or versions, which is why prompts, settings, and versions are recorded.)
4. What does the FDA January 2025 draft guidance propose as its central concept, and what is the practical implication? (Answer: a risk-based credibility assessment for an AI model tied to a defined context of use; scrutiny should scale with the model's influence on a decision and the decision's consequence.)
5. Can an AI tool be listed as an author on a manuscript, and why or why not? (Answer: no; ICMJE holds that AI cannot be responsible for the accuracy, integrity, and originality of the work, so responsibility rests with the human authors, and AI assistance is disclosed.)
6. Give the six questions used to evaluate an AI tool or workflow. (Answer: fitness, data governance, accuracy and hallucination risk, bias, reproducibility, and accountability.)
7. Where AI assistance was used but a factual claim cannot be verified against a primary source, what is the correct action? (Answer: mark the gap; presenting unverified output as fact and guessing or fabricating a citation are both prohibited.)
8. Why does retrieval-augmented generation reduce but not remove the need for verification? (Answer: supplying source documents grounds the answer in provided text, but the model can still misread or misattribute those passages, so cited material is still checked against the source.)

## Key readings

- [Federal Register, FDA draft guidance on AI to support regulatory decision-making (January 7, 2025 notice)](https://www.federalregister.gov/documents/2025/01/07/2024-31542/considerations-for-the-use-of-artificial-intelligence-to-support-regulatory-decision-making-for-drug)
- [EMA, Reflection paper on the use of AI in the medicinal product lifecycle](https://www.ema.europa.eu/en/use-artificial-intelligence-ai-medicinal-product-lifecycle)
- [Padula et al., 2022, PALISADE checklist for machine learning in HEOR (ISPOR)](https://doi.org/10.1016/j.jval.2022.03.022)
- [Fleurence et al., 2025, generative AI for health technology assessment (ISPOR)](https://doi.org/10.1016/j.jval.2024.10.3846)
- [Fleurence et al., 2025, taxonomy of generative AI in HEOR (ISPOR)](https://doi.org/10.1016/j.jval.2025.04.2167)
- [DeTora et al., 2022, Good Publication Practice (GPP 2022)](https://doi.org/10.7326/M22-1460)
- [ICMJE, Defining the Role of Authors and Contributors (including AI provisions)](https://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html)
- [MAPS, Digital, Advanced Analytics and AI in Medical Affairs benchmark report, 2024](https://medicalaffairs.org/wp-content/uploads/2024/10/MAPS-Digital-Advanced-Analytics-Artificial-Intelligence-Report-2024.pdf)
- Program AI-use policy and playbook (`governance/ai_use_policy_and_playbook.md`)

## Connection to the capstone

The AI-use plan and audit log produced here is capstone work product 8, and it is the only work product that spans the whole portfolio.

Every other deliverable that used AI is recorded in this log, and the six-question evaluation documents that at least one workflow was assessed for fitness, bias, reproducibility, and governance. The capstone rubric grades the portfolio for compliance and evidence integrity on the basis of this record.

A portfolio without a log is returned, and a log that carries unverified claims into a deliverable fails those dimensions.

The module thus supplies both a competency and the audit instrument that demonstrates it. A graduate who has completed this work can use AI productively and defend how they used it to a compliance officer, an editor, and an HTA reviewer, which is the outcome the credential is intended to certify.
