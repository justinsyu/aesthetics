# No-Login ChatGPT AI-Search Screen: Injectable HIV PrEP

Date: July 4, 2026

Objective: identify a prescription drug that appears to outperform a close competitor in no-login ChatGPT search-style answers, then assess what the outperforming drug is doing well from a generative AI search optimization perspective.

## Short Answer

The best empirical candidate from this screen is Yeztugo (lenacapavir) vs Apretude (cabotegravir) for injectable HIV pre-exposure prophylaxis (PrEP).

The clinical profile is similar enough for a useful experiment because both are long-acting injectable PrEP options and current evidence does not establish a definitive efficacy winner without a head-to-head randomized trial. In the no-login ChatGPT runs, Yeztugo appeared to outperform Apretude on broad and practical PrEP-injection prompts because it owns a simple, source-repeated retrieval object: twice-yearly PrEP, every six months, longest-acting PrEP option.

This is not a pure "same product profile" comparison. Yeztugo's six-month dosing is a real differentiator, not only an information-design artifact. That is why the cleanest claim is: Yeztugo appears to outperform Apretude in AI-search answers for convenience-oriented injectable-PrEP prompts while available evidence supports broadly comparable efficacy.

## Test Conditions

- Platform: ChatGPT web, no login, Temporary Chat.
- Access mode: browser session at `https://chatgpt.com/?temporary-chat=true`.
- Date: July 4, 2026.
- Method: fresh temporary chat per prompt where feasible. Extracted answer text and cited URLs from the page DOM.
- Limitation: this was a small manual screen, not a statistically powered repeated-run study. ChatGPT answers can vary by time, geography, model routing, and retrieval state.

## Observed No-Login ChatGPT Outputs

| Prompt | Answer direction | Data pulled | Cited sources |
|---|---|---|---|
| `What is the best PrEP injection if I don't want to take a daily pill? Cite sources.` | Yeztugo first. ChatGPT described Yeztugo as the longest-acting option and the least burdensome if both products are appropriate. Apretude was second and described as established. | Yeztugo: every 6 months, 2 injections per year after starting, highly effective, 96-100% trial efficacy language. Apretude: every 2 months, >99% effective when taken as prescribed, regular clinic visits and HIV testing. | [CDC PrEP clinical guidance](https://www.cdc.gov/hivnexus/hcp/prep/index.html), [CDC MMWR lenacapavir recommendation](https://www.cdc.gov/mmwr/volumes/74/wr/mm7435a1.htm). |
| `Which injectable PrEP is better: Apretude or Yeztugo? Cite the sources you used.` | Balanced on efficacy, but Yeztugo received the practical recommendation edge because of the six-month schedule. ChatGPT stated no direct head-to-head trial. | Yeztugo: FDA approval in 2025, every 6 months, subcutaneous two-injection regimen, 96-100% clinical-trial efficacy framing. Apretude: FDA approval in 2021, every 2 months, intramuscular injection, more years of real-world experience, superior to daily oral PrEP. | [Reuters on Yeztugo FDA approval](https://www.reuters.com/business/healthcare-pharmaceuticals/us-fda-approves-gileads-twice-yearly-injection-hiv-prevention-2025-06-18/), [FDA Apretude approval](https://www.fda.gov/news-events/press-announcements/fda-approves-first-injectable-treatment-hiv-pre-exposure-prevention), [University of Washington National HIV PrEP Curriculum](https://www.hivprep.uw.edu/page/treatment/drugs/cabotegravir/prescribing-information), [Drugs.com Yeztugo prescribing summary](https://www.drugs.com/pro/yeztugo.html). |
| `Are Yeztugo and Apretude equally effective for HIV PrEP? Cite evidence.` | Similar efficacy, no definitive head-to-head winner. ChatGPT said it is more accurate to say "comparably effective" than "equally effective." | Yeztugo: PURPOSE 1 had 0 infections among 2,134 participants receiving lenacapavir; PURPOSE 2 had 2 infections among 2,179 participants; about 99.9% remained HIV-negative. Apretude: HPTN 083 reduced HIV incidence by 69% vs daily oral Truvada; HPTN 084 reduced HIV incidence by 90% vs daily oral Truvada. Indirect comparison: Apretude ~96-98% efficacy vs no PrEP; Yeztugo ~95-100%; similar efficacy conclusion. | [Gilead investor release on Yeztugo approval](https://investors.gilead.com/news/news-details/2025/Yeztugo-Lenacapavir-Is-Now-the-First-and-Only-FDA-Approved-HIV-Prevention-Option-Offering-6-Months-of-Protection/default.aspx), [FDA Apretude approval](https://www.fda.gov/news-events/press-announcements/fda-approves-first-injectable-treatment-hiv-pre-exposure-prevention), [Managed Healthcare Executive indirect comparison](https://www.managedhealthcareexecutive.com/view/indirect-comparison-shows-apretude-and-yeztugo-have-similar-efficacy-ias-2025). |

Supporting screenshot: `outputs/chatgpt-yeztugo-apretude-efficacy-prompt.png`.

## Why Yeztugo Appears To Outperform In ChatGPT

### 1. It has a compact answer object

Yeztugo's public materials repeatedly state the same simple proposition: twice-yearly PrEP, one office visit every six months, two injections per visit after starter dosing. The official site states "twice-yearly PrEP is here," "one office visit, every six months," and "the longest-acting PrEP option available" [Yeztugo](https://www.yeztugo.com/). This is exactly the type of concise entity-attribute-benefit structure that retrieval systems can reuse.

Apretude also has a clear proposition, but it is less differentiating after Yeztugo's launch: every other month after initiation injections [Apretude](https://apretude.com/). Its best differentiators are maturity, real-world experience, and clinical-trial depth. Those are valuable, but they are less direct answers to prompts such as "best PrEP injection if I don't want a daily pill."

### 2. Neutral public-health sources reinforce the differentiator

The first ChatGPT run cited CDC sources, not manufacturer pages. CDC states that injectable lenacapavir is administered every six months and that its addition provides another PrEP option. CDC also says the six-month dosing may help some people overcome adherence or regular-care-visit challenges [CDC MMWR](https://www.cdc.gov/mmwr/volumes/74/wr/mm7435a1.htm), [CDC letter](https://www.cdc.gov/nchhstp/director-letters/New-Injectable-HIV-PrEP%20.html).

This matters because pharma-owned claims alone are often not what ChatGPT cites. Yeztugo's advantage is that its differentiator is repeated by public-health and medical-news sources.

### 3. The launch language is source-consistent across channels

Gilead's public launch language uses the same phrasing: "first and only FDA-approved HIV prevention option offering 6 months of protection" and ">=99.9% of participants remained HIV negative" [Gilead](https://www.gilead.com/news/news-details/2025/yeztugo-lenacapavir-is-now-the-first-and-only-fda-approved-hiv-prevention-option-offering-6-months-of-protection). ChatGPT pulled similar concepts from Gilead investor materials in the efficacy prompt.

That creates a consistent retrieval path:

1. Brand site: twice-yearly / every six months / longest-acting.
2. Manufacturer news: first and only / 6 months of protection / PURPOSE 1 and PURPOSE 2.
3. CDC/WHO/public-health sources: six-month dosing and guideline recommendation.
4. Medical news: FDA approval and trial efficacy.

### 4. The comparator's strength is less prompt-aligned

Apretude's HCP page has strong trial and real-world-experience language: first long-acting injectable PrEP, more than 3 years of real-world experience, over 5,000 patient-years of clinical-trial data, and more than 200,000 US doses administered [Apretude HCP](https://apretudehcp.com/). It also reports >3x and 12x reductions in HIV incidence vs daily oral Truvada in HPTN 083 and HPTN 084.

Those facts are clinically meaningful, but they answer a different question: "Which option is more established?" or "What is the evidence base for Apretude?" They do not beat Yeztugo on the broad convenience query.

## What Yeztugo Is Doing Right For Generative AI Search

| GEO pattern | Yeztugo evidence | Why it helps AI search |
|---|---|---|
| Distinctive entity attribute | Twice-yearly PrEP, every six months, longest-acting PrEP option [Yeztugo](https://www.yeztugo.com/). | Makes the drug easy to retrieve for "best injection," "longest acting," "avoid daily pill," and "fewer visits" prompts. |
| Consistent phrase repetition | Official site, HCP site, Gilead release, CDC, WHO, and medical-news coverage all use six-month/twice-yearly framing. | Reduces ambiguity and gives models multiple aligned sources. |
| Neutral-source reinforcement | CDC and WHO public-health sources describe or recommend injectable lenacapavir and emphasize the every-six-month dosing [CDC](https://www.cdc.gov/mmwr/volumes/74/wr/mm7435a1.htm), [WHO](https://www.who.int/news/item/14-07-2025-who-recommends-injectable-lenacapavir-for-hiv-prevention). | Increases the chance ChatGPT cites non-manufacturer sources while still surfacing the brand's key differentiator. |
| Direct-answer owned pages | Yeztugo has pages for what it is, study results, taking Yeztugo, side effects, and HCP innovation/dosing pages. | Provides structured answer targets for patient and HCP queries. |
| Trial naming and endpoint clarity | PURPOSE 1 and PURPOSE 2 are repeatedly connected to high efficacy and HIV-negative participant rates. | Makes trial evidence easy to associate with the brand and generic. |
| Recent high-salience news event | FDA approval, CDC recommendation, WHO recommendation, and IAS-related coverage occurred in a tight public window. | Creates a fresh, high-authority source cluster around the same differentiator. |

## Recommended Next Experiment

Run a 20-prompt repeated test across no-login ChatGPT, Perplexity, Google AI Mode/AI Overviews if available, and Bing/Copilot.

Use two prompt families:

1. Convenience prompts:
   - `What is the best PrEP injection if I don't want to take a daily pill? Cite sources.`
   - `What is the longest-acting PrEP injection available in the United States? Cite sources.`
   - `Which PrEP option requires the fewest clinic visits? Cite sources.`

2. Efficacy-control prompts:
   - `Are Yeztugo and Apretude equally effective for HIV PrEP? Cite evidence.`
   - `Which injectable PrEP has stronger efficacy evidence: Yeztugo or Apretude? Cite sources.`
   - `Compare Yeztugo and Apretude for efficacy, dosing, safety, and follow-up requirements. Use public medical sources.`

Code each answer for:

1. First drug mentioned.
2. Recommendation or practical edge.
3. Citation count by drug.
4. Citation source type: public-health, FDA/regulatory, manufacturer, medical news, academic, curriculum/guideline, consumer medical.
5. Whether the answer says no head-to-head trial.
6. Whether it distinguishes efficacy from convenience/adherence.
7. Whether safety and HIV-testing requirements are included.

Expected pattern:

Yeztugo should dominate convenience prompts. Efficacy-control prompts should be more balanced and should state that direct head-to-head evidence is not available. If that pattern holds, Yeztugo is not necessarily "clinically better" in the broad efficacy sense. It is better optimized for AI-search retrieval because the differentiator is simple, consistent, repeated, recent, and endorsed by neutral public-health sources.
