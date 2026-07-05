# No-Login ChatGPT Audit: Injectable HIV PrEP Phase 1

Date: July 5, 2026

Pair: Yeztugo / lenacapavir vs Apretude / cabotegravir

Surface: ChatGPT web, no-login Temporary Chat

Model selector observed: `ChatGPT`

Thinking setting observed: no explicit thinking control was visible or activated in the no-login UI.

## Status

This is a phase 1 empirical audit, not the completed 100-prompt study. It includes 46 robust no-login ChatGPT captures and 4 early partial captures generated before the completion detector was fixed.

Raw-response evidence is preserved as full-page screenshots in:

`outputs/chatgpt_prep_audit_2026-07-05/screenshots/`

The fixed completion detector waited for the visible `Stop answering` state to disappear and for response text length to stabilize before saving each screenshot.

## Prompt Coverage Completed

| Stratum | Prompt IDs completed robustly | Count |
|---|---:|---:|
| Neutral injectable-PrEP | 1, 6-10 | 6 |
| Efficacy/control | 16-30 | 15 |
| Safety/monitoring | 31-35 | 5 |
| Patient convenience/access | 45-49 | 5 |
| HCP/medical-information | 59-63 | 5 |
| Source/citation-seeking | 73-77 | 5 |
| Adversarial/edge | 87-91 | 5 |
| Early partial captures | 2-5 | 4 |

## First-Mention Results

Across the 46 robust captures, first mention was modestly tilted toward Yeztugo/lenacapavir.

| First-mentioned entity family | Count | Share |
|---|---:|---:|
| Yeztugo / lenacapavir | 26 | 57% |
| Apretude / cabotegravir | 20 | 43% |

This is not, by itself, strong evidence of systematic underrepresentation. The stronger signal is in citation/source behavior and the kinds of prompts where the model shifts.

## Main Empirical Findings

### 1. Yeztugo wins when the prompt activates a simple convenience retrieval object

When prompts referred to convenience, clinic burden, long-acting PrEP, fewer visits, or broad patient decision-making, ChatGPT often led with Yeztugo or cited Yeztugo-focused sources. The repeated answer object was:

- twice-yearly PrEP
- every 6 months
- longest-acting PrEP
- fewer clinic visits

This was clearest in prompts 45-49. Yeztugo had the first mention in prompts 45 and 46, while Apretude/cabotegravir led when the prompt explicitly asked about established workflows or generic injection-frequency theory.

Interpretation: Yeztugo's public information is highly retrievable because the differentiator is concise, repeated, and source-aligned.

### 2. Apretude is not absent, but its strengths are less naturally retrieved

Apretude appeared consistently, especially in efficacy-control, safety, and HCP prompts. However, the model tended to retrieve Apretude around:

- first long-acting injectable PrEP
- older approval / more established use
- HPTN 083 / HPTN 084 evidence
- every-2-month dosing

Those are credible strengths, but they are less likely to dominate broad patient prompts such as "best injection" or "avoid daily pills." Apretude performs better when the prompt asks about experience, established workflows, or cabotegravir-specific evidence.

### 3. Citation quality was uneven, even for medical-information prompts

The model often did not cite the strongest available sources. Examples:

- Prompt 20 cited Reddit for absolute clinical trial outcomes.
- Prompt 45 cited Reddit for patient-convenience comparison.
- Prompt 74 asked for FDA labels but cited MedLibrary rather than FDA label pages.
- Prompt 73 included a Gilead press release about an investigational once-weekly oral Yeztugo product, which was off-target for injectable PrEP comparison.
- Prompts 61 and 62 leaned heavily on Drugs.com and Yeztugo HCP material rather than FDA labels or DailyMed.

Interpretation: asking ChatGPT to cite sources does not guarantee label-grade or medical-information-grade sourcing. Manufacturers should not only optimize owned pages. They should ensure authoritative label, medical information, and public-health sources are easy to retrieve for the exact comparison questions.

### 4. Comparative rigor improved only when the prompt forced it

Prompts that explicitly asked about head-to-head evidence or cross-trial limitations generally produced better caveats. Prompts that asked for "stronger evidence," "highly effective," or "balanced evidence summary" often used superiority-like wording even when also noting indirect comparisons.

Observed issue: several efficacy prompts did not explicitly say there is no direct Yeztugo-vs-Apretude head-to-head trial unless the prompt forced that framing.

Implication: disadvantaged manufacturers should publish and distribute comparison-neutral medical-information pages that explicitly state:

- what is known for each product
- what is not known
- why cross-trial comparisons are limited
- why dosing convenience is not the same as proven superior HIV prevention

### 5. Safety and monitoring were incomplete in many otherwise useful responses

Several responses omitted key safety-monitoring concepts unless directly asked. The most consistently captured safety concepts were HIV testing and resistance risk, but not every relevant prompt included them.

Examples:

- Prompt 31, a safety-profile comparison, did not flag HIV testing or resistance in the automated flags.
- Convenience prompts 45-49 frequently discussed adherence and access but often omitted HIV testing and resistance context.
- HCP prompt 63 did well on HIV testing and RNA testing, but several other HCP prompts did not cite labels or CDC guidance.

Implication: medical-information optimization should not just improve mention share. It should improve the probability that AI answers include minimum safe-use context.

## Why Yeztugo Appears To Outperform In AI Search

The signal is not that ChatGPT concluded Yeztugo is clinically superior. The signal is that Yeztugo is easier for ChatGPT to retrieve and cite in common user-framed questions.

Likely drivers:

1. Clear public phrasing: "twice-yearly," "every 6 months," "longest-acting."
2. Source repetition across official brand, HCP, Gilead, CDC/WHO/public-health, medical news, and consumer medical sources.
3. A recent, high-salience launch event that produced many aligned public pages.
4. A direct patient-relevant differentiator that maps to common prompt language: "I do not want a daily pill" or "fewer visits."
5. A structured official HCP/patient web footprint that ChatGPT repeatedly retrieved.

## Guidance For The Potentially Disadvantaged Manufacturer

For Apretude/ViiV, the immediate opportunity is not to compete with "twice yearly" as a slogan. It is to make Apretude's legitimate strengths more retrievable and better balanced in AI answers.

Recommended actions:

1. Build an indexable, source-rich comparison FAQ for clinicians and patients.
   - Include Apretude and lenacapavir.
   - Explicitly separate dosing convenience, established clinical experience, efficacy evidence, safety, HIV testing, resistance, and access.
   - State that no direct head-to-head trial establishes superiority.

2. Create a medical-information page on "how to interpret injectable PrEP evidence."
   - Explain HPTN 083/084, PURPOSE 1/2, cross-trial limitations, and why adherence and visit burden are not the same as biological efficacy.
   - Use plain headings that match likely prompts.

3. Improve retrievability of label-grade facts.
   - Ensure official prescribing information, FDA label links, dosing tables, monitoring requirements, and HIV-testing requirements are exposed in crawlable HTML, not only PDFs.
   - Add FAQ/schema markup where compliant.

4. Publish or amplify real-world implementation evidence in neutral channels.
   - ChatGPT retrieved "established experience" only weakly. Apretude's longer market history needs accessible public evidence, not just implicit age.

5. Seed neutral-source correction and update pathways.
   - Encourage updates in CDC/HIV curriculum, clinician quick guides, and public-health explainers that mention both injectable options and distinguish product selection factors.

6. Avoid promotional superiority framing.
   - The useful answer is not "Apretude is better." It is "Apretude remains a highly effective established injectable option, with different implementation strengths, and no head-to-head evidence proves lenacapavir superiority."

## Recommended Next Step

Complete the remaining 54 prompts from the 100-prompt bank using the fixed detector and the same no-login ChatGPT method. Then score each answer against the 100-point rubric:

- core factual accuracy
- safety and monitoring
- comparative rigor
- source quality and citations
- balance and visibility

The next run should write a structured CSV/JSON summary outside the Playwright page context, because the current Playwright MCP execution environment can save screenshots but does not expose file APIs for JSONL logging.
