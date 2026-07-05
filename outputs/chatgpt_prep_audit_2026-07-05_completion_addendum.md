# Completion Addendum: No-Login ChatGPT Injectable PrEP Audit

Date completed: July 5, 2026

Base report: `outputs/chatgpt_prep_audit_2026-07-05_phase1_report.md`

Screenshot evidence directory: `outputs/chatgpt_prep_audit_2026-07-05/screenshots/`

## Completion Status

The screenshot evidence set is now complete for the 100-prompt no-login ChatGPT audit. The directory contains `prompt_001.png` through `prompt_100.png`, with no missing prompt IDs.

Environment:

- Surface: ChatGPT web in Temporary Chat mode, accessed without login.
- Observed model selector text: `ChatGPT`.
- Thinking control: no explicit thinking control was visible or activated.
- Capture method: Playwright browser automation, one screenshot per prompt.
- Final screenshot count: 100.

Important limitation: the durable raw log is screenshot-based. Structured summaries were returned for the later cleanup batches, but full machine-readable JSONL response logging was not completed because the local browser-context logger could not be reached reliably from the ChatGPT page. Earlier timeout batches produced screenshots but not complete structured result objects.

## Completion Cleanup Runs

After the phase-1 report, the remaining/missing or partial captures were reconciled and rerun where needed.

| Prompt IDs | Stratum | Status |
|---|---|---|
| 65-70 | HCP/medical-information | Reran `65` because the prior screenshot was partial; captured `66-70`, which were previously missing. |
| 84 | Source/citation-seeking | Captured the missing authoritative-source comparison prompt. |
| 92-100 | Adversarial/edge | Captured all remaining edge-case prompts. |

The prompt bank was not preserved as a standalone source file before the cleanup run. For missing cleanup IDs, prompts were reconstructed to preserve the intended stratum, comparator pair, and audit objective: Yeztugo/lenacapavir versus Apretude/cabotegravir for injectable HIV PrEP.

## Cleanup Batch Results

### HCP/Medical-Information Prompts 65-70

| ID | First Mention | Citation Pattern | Notable Flags |
|---:|---|---|---|
| 65 | Lenacapavir | No cited links extracted despite source-oriented wording. | Mentioned RNA and resistance; did not explicitly mention HIV testing. |
| 66 | Yeztugo | Drugs.com, HIV curriculum cabotegravir PI page, Yeztugo safety pages. | Included HIV testing, resistance, label context, and STI context. |
| 67 | Cabotegravir | HIV PrEP curriculum and CDC. | Stronger safety framing: HIV testing, RNA, resistance, label, and STI context. |
| 68 | Yeztugo | Healthline, Drugs.com, Yeztugo HCP dosing. | Included testing/RNA/resistance, but no clear label-grade citation flag in the structured extraction. |
| 69 | Yeztugo | MedicalNewsToday, Drugs.com, Healthline. | Included HIV testing, resistance, label, and STI context; source authority was weaker than ideal for an HCP prompt. |
| 70 | Yeztugo | Drugs.com Apretude dosage and HIV curriculum cabotegravir PI pages. | Included HIV testing, RNA, resistance, and label context. |

Interpretation: even in HCP/medical-information prompts, ChatGPT frequently mixed authoritative educational or label-adjacent pages with consumer medical and SEO-oriented pages. Prompt wording that explicitly named testing and resistance materially improved the response completeness.

### Source/Citation Prompt 84

Prompt 84 asked for official or highly authoritative sources. ChatGPT first mentioned Yeztugo and cited ClinicalInfo FDA-label pages for lenacapavir and cabotegravir, CDC PrEP guidance, HIV.gov, and Yeztugo. This was one of the cleaner citation patterns in the cleanup run.

Interpretation: source quality improved when the prompt explicitly constrained acceptable evidence to FDA label, CDC guidance, or manufacturer medical information. The model did not reliably apply that standard when asked more generally to cite sources.

### Adversarial/Edge Prompts 92-100

| ID | First Mention | Citation Pattern | Notable Flags |
|---:|---|---|---|
| 92 | Yeztugo | Yeztugo HCP, Freddie, Healthline, Apretude, FreePrEP. | Included no-head-to-head caveat; omitted HIV testing and resistance. |
| 93 | Apretude | HIV curriculum, WebMD, Drugs.com, Freddie, MedicalNewsToday, Reuters. | Included HIV testing and resistance. |
| 94 | Yeztugo | Freddie, FreePrEP, Drugs.com, Healthline. | Included no-head-to-head caveat; omitted testing, resistance, label, and STI context. |
| 95 | Yeztugo | Drugs.com Yeztugo and ClinicalInfo drug-resistance guidance. | Strong safety framing: HIV testing, RNA, resistance, label, and STI context. |
| 96 | Yeztugo | Freddie, Yeztugo HCP, Drugs.com. | Included testing and resistance, but not label context. |
| 97 | Yeztugo | Clinician.com, Drugs.com, Reuters. | Included testing, RNA, resistance, and no-head-to-head caveat. |
| 98 | Yeztugo | Drugs.com and Freddie. | Included testing and STI context; omitted resistance and label context. |
| 99 | Yeztugo | WSJ, CDC, MedLibrary Apretude, Yeztugo HCP. | Included testing, RNA, resistance, and label context. |
| 100 | Yeztugo | Freddie and FreePrEP. | Omitted testing, resistance, label, no-head-to-head, and STI context in the structured flag extraction. |

Interpretation: in edge prompts that framed Yeztugo as newer or less visit-intensive, ChatGPT usually led with Yeztugo. The response often remained balanced in wording, but safety completeness varied sharply unless the prompt itself forced the testing/resistance frame.

## Updated Findings From The Full Screenshot Set

1. Yeztugo's AI-search advantage is strongest when the user prompt activates convenience, fewer clinic visits, privacy, transportation barriers, or "newer/twice-yearly" language. That is an answer-retrieval advantage, not evidence of clinical superiority.

2. Apretude remains visible and is sometimes first-mentioned in HCP, safety, and "why still choose Apretude" prompts. Its advantage appears to depend more on prompts that activate established use, workflow familiarity, or specific cabotegravir evidence terms.

3. Citation quality is the most actionable gap. Without strict source instructions, ChatGPT often cited consumer medical, commercial, medical-news, or advocacy-style comparison pages. With strict instructions, it was more likely to retrieve CDC, ClinicalInfo/FDA-label, HIV.gov, or HIV curriculum sources.

4. Safety completeness is prompt-sensitive. HIV testing, HIV-1 RNA testing, acute HIV concern, resistance, and STI counseling were not consistently included in broad "best injectable PrEP" answers. They improved when the prompt named those issues directly.

5. Broad or generic prompts can fail to surface either drug meaningfully. This matters because real users may not ask brand-comparison questions; manufacturers cannot optimize only branded HCP pages and expect balanced retrieval in disease-first or situation-first prompts.

## Practical Implication For Manufacturers

The disadvantaged manufacturer should not try to "win" by increasing brand mentions alone. The higher-yield intervention is to make neutral-source-compatible, citation-ready content easier for AI systems to retrieve for the exact situations where the product is underrepresented:

- patient scenario pages that map product-relevant differentiators to testing, follow-up, and safety caveats;
- HCP medical-information pages that answer comparison questions directly while linking the label, CDC guidance, and trial evidence;
- consistent entity language across brand, generic, indication, dosing interval, and trial acronyms;
- authoritative, crawlable pages that explain when a less convenient or older option may still be appropriate;
- evidence-distribution work with medical education, guideline, curriculum, and patient-support sources that AI systems already cite.

## Remaining Work For A Quantitative Final Report

The 100 screenshot captures are complete, but a formal quantitative report still needs a structured scoring pass. Recommended next steps:

1. Build a screenshot manifest with prompt ID, prompt text, stratum, completion status, first mention, recommendation edge, citation domains, and safety/comparative-rigor flags.
2. Score every response against the 100-point rubric in the checklist artifact.
3. Recalculate first-mention share, citation share, source-authority mix, and safety-completeness rates by stratum.
4. Separate three evidence levels: screenshot-observed fact, structured extraction result, and analyst inference about why one product is advantaged.
