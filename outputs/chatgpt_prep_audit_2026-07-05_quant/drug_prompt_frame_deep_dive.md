# Deep Dive: Why Yeztugo and Apretude Appear Under Different AI-Search Prompt Frames

Date: July 5, 2026

Products: Yeztugo / lenacapavir and Apretude / cabotegravir for HIV pre-exposure prophylaxis (PrEP)

Evidence base: the 100-prompt no-login ChatGPT audit, OCR-visible scoring outputs, FDA labels, CDC and WHO guidance, manufacturer HCP and patient pages, PubMed count checks, and selected public medical-reference or implementation sources.

## Executive Interpretation

The audit does not show that one product is categorically better optimized for AI search. It shows that each product has a different source ecosystem that is activated by different prompt frames.

Yeztugo is advantaged when prompts contain or imply a simple product-selection attribute: newer, twice-yearly, every 6 months, fewer clinic visits, longest acting, or best injectable. This is not primarily a label-wording finding. The FDA and DailyMed label record contains the core dosing object, and the same concept is repeated across CDC guidance, WHO guidance, the HCP site, the patient site, launch communications, medical news, and consumer-facing explainers. The audit pattern is therefore consistent with a compact retrieval hook rather than with a conclusion about clinical superiority.

Apretude is advantaged when prompts ask for established injectable PrEP, efficacy evidence, safety, HCP use, clinical studies, or source-seeking information. This is not because Apretude has a more compact consumer frame. It is consistent with cabotegravir's incumbent source-depth advantages: FDA approval in December 2021 as the first injectable PrEP option, more years of indexing, inclusion in CDC PrEP guidance, National HIV Curriculum workflow detail, the HPTN 083/084 trial ecosystem, mature HCP pages, and implementation or real-world evidence follow-ons.

The report separates verified source facts from audit-supported inferences. The audit can show which product appeared first under defined prompt frames. It cannot prove why a model selected that ordering, and it should not be read as causal evidence about ranking algorithms, source weighting, or product performance.

The practical conclusion is that generative-search optimization for medical information is not one task. It has at least three separate tasks:

1. Make the product easy to retrieve for simple patient language.
2. Make the product easy to cite for HCP and source-seeking prompts.
3. Make the product difficult to oversimplify by embedding safety, monitoring, and comparative-rigor caveats into the same pages that AI systems are likely to retrieve.

## What The Audit Found

The quantitative OCR-visible audit found 99 score-eligible responses among 100 screenshots. Apretude / cabotegravir was first-mentioned overall in 52 responses, Yeztugo / lenacapavir in 44, and 3 had no visible first mention. The stratum pattern was more informative than the aggregate count:

| Prompt stratum | Yeztugo first | Apretude first | Interpretation |
|---|---:|---:|---|
| Neutral injectable PrEP | 5 | 9 | Apretude benefited from older/default injectable-PrEP recognition and broader evidence retrieval. |
| Efficacy/control | 6 | 9 | Cabotegravir's HPTN evidence footprint remained highly retrievable. |
| Safety/monitoring | 3 | 9 | Apretude's safety and HCP source ecosystem was more frequently activated. |
| Convenience/access | 4 | 9 | OCR-visible first mention favored Apretude, although Yeztugo won the clearest fewer-visits and privacy-style prompts in the earlier structured cleanup observations. |
| HCP/medical information | 6 | 8 | Both appeared frequently, with Apretude slightly favored by established HCP sources. |
| Source/citation-seeking | 6 | 8 | Apretude benefited from curriculum, label, and clinical evidence retrieval. |
| Adversarial/edge | 14 | 0 | Yeztugo was first-mentioned in prompts that activated newer, twice-yearly, replacement, or "best injectable" framing. |

This means the key phenomenon is not simple underrepresentation. A more useful working term is prompt-frame capture. The product whose public source ecosystem most directly matches the wording and implied decision frame of the prompt was more likely to appear early in the visible answer.

## Verified Source Facts Versus Inferences

The following facts are directly source-supported:

- FDA approved Apretude in December 2021 as the first injectable treatment for HIV PrEP, with two initiation injections one month apart followed by every-2-month dosing [FDA](https://www.fda.gov/news-events/press-announcements/fda-approves-first-injectable-treatment-hiv-pre-exposure-prevention).
- CDC clinical guidance includes injectable cabotegravir workflows, including antigen/antibody and HIV-1 RNA testing, every-2-month injection visits after initiation, and management of the cabotegravir pharmacologic tail after discontinuation [CDC clinical guidance](https://www.cdc.gov/hivnexus/hcp/prep/index.html).
- The National HIV Curriculum describes PrEP monitoring across oral PrEP, cabotegravir-IM, and lenacapavir-SQ, and includes workflow-level details such as HIV testing frequency, HIV RNA use, STI screening, and discontinuation considerations [National HIV Curriculum](https://www.hiv.uw.edu/pdf/prevention/preexposure-prophylaxis-prep/core-concept/all).
- DailyMed describes Yeztugo continuation dosing as 927 mg subcutaneously every 6 months, given as 2 injections, with dosing-window, delayed-injection, missed-injection, and drug-interaction instructions [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1c241af1-ce62-4b0a-9eb7-f6b626174f01).
- CDC's 2025 lenacapavir recommendation states that FDA approved injectable lenacapavir in June 2025, administered every 6 months, based on PURPOSE 1 and PURPOSE 2, and strongly recommends it as a PrEP option for persons weighing at least 35 kg who would benefit from PrEP [CDC MMWR](https://www.cdc.gov/mmwr/volumes/74/wr/mm7435a1.htm).
- HIV.gov repeats the public-health frame that twice-a-year lenacapavir may help some people overcome adherence or regular-visit challenges, while noting that all FDA-approved PrEP options are highly effective when taken as prescribed [HIV.gov](https://www.hiv.gov/blog/cdc-recommends-new-injectable-hiv-prep).

The following are inferences from the audit pattern and source map:

- Apretude's first-mention strength in neutral, efficacy, safety, HCP, and source-seeking prompts is plausibly related to incumbent source depth and clinical workflow coverage.
- Yeztugo's first-mention strength in newer, twice-yearly, replacement, best-injectable, and some convenience prompts is plausibly related to a compact, repeatedly reinforced retrieval hook.
- These explanations are probabilistic. They do not establish that any individual source caused a specific ChatGPT answer, and they do not imply that first mention is a measure of best clinical fit.

## 1. Label Wording: Necessary But Not Sufficient

Both labels contain the safety elements that AI answers often omitted. Both labels include warnings about drug resistance in undiagnosed HIV infection and require HIV testing. Yeztugo's label states that individuals must be tested before initiation and with each subsequent injection, and it describes once every 6-month continuation injection dosing in the highlights and dosing sections [FDA Yeztugo label](https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/220020s000lbl.pdf). DailyMed repeats the continuation schedule, dosing window, delayed-injection instructions, missed-injection handling, and drug-interaction modifications in crawlable label text [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1c241af1-ce62-4b0a-9eb7-f6b626174f01). Apretude's label likewise contains a resistance warning and describes continuation injection at month 4 and every 2 months onward [FDA Apretude label](https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/215499s008lbl.pdf).

The difference is not that Yeztugo has a safer or more complete label. The source-map difference is that Yeztugo's label contains a short, distinctive retrieval object: "every 6 months." Apretude's label contains a clinically important but less differentiating object: every 2 months after initiation. Apretude's administration pathway also includes more visible operational complexity: optional oral lead-in, two initiation injections, every-2-month continuation, missed-dose oral bridging, and long-tail or residual-concentration considerations.

Implication: label wording is most likely to help AI retrieval when the label contains a compact attribute that later sources repeat. For safety, both manufacturers need the same improvement: ensure testing, acute-HIV, resistance, STI, and discontinuation-tail concepts are repeated in crawlable pages outside the PDF label.

## 2. Public-Health And Guideline Reinforcement

Yeztugo has unusually strong reinforcement from neutral public-health sources for its key attribute. CDC's 2025 MMWR recommendation states that lenacapavir, administered every 6 months, is strongly recommended as a PrEP option for persons weighing at least 35 kg who would benefit from PrEP. The same CDC page links the six-month schedule to potential adherence improvement [CDC MMWR](https://www.cdc.gov/mmwr/volumes/74/wr/mm7435a1.htm). HIV.gov repeats that CDC strongly recommends lenacapavir every six months and notes that the dosing interval may help some people overcome adherence or regular-visit challenges [HIV.gov](https://www.hiv.gov/blog/cdc-recommends-new-injectable-hiv-prep). WHO also recommends long-acting injectable lenacapavir as an additional HIV prevention choice and describes it as administered twice a year [WHO](https://www.who.int/publications/i/item/9789240111608).

Apretude has strong public-health and educational coverage, but much of it is older, more clinical, and less news-like. The National HIV Curriculum has a detailed cabotegravir page with dosing, missed injection handling, contraindications, adverse reactions, and HPTN 083/084 material [National HIV Curriculum](https://www.hiv.uw.edu/page/treatment/drugs/cabotegravir). CDC and HIV.gov now discuss cabotegravir as an existing option administered every 2 months, while lenacapavir is the newer addition.

Implication: neutral-source reinforcement is not just about being cited. It can shape the answer frame. Yeztugo's neutral-source frame is "new option that may reduce adherence and visit burden." Apretude's neutral-source frame is "established injectable PrEP with specific clinical management requirements."

## 3. Publication And Trial-Evidence Footprint

The publication ecosystem favors cabotegravir in breadth and maturity. PubMed count checks run on July 5, 2026 returned:

| Query | PubMed count |
|---|---:|
| `"cabotegravir" AND (PrEP OR preexposure OR pre-exposure)` | 350 |
| `"lenacapavir" AND (PrEP OR preexposure OR pre-exposure)` | 118 |
| `"HPTN 083" AND cabotegravir` | 29 |
| `"HPTN 084" AND cabotegravir` | 18 |
| `"PURPOSE 1" AND lenacapavir` | 9 |
| `"PURPOSE 2" AND lenacapavir` | 8 |
| `"Apretude"` | 16 |
| `"Yeztugo"` | 8 |

These counts are directional rather than definitive because PubMed query syntax and indexing vary. They support the inference that Apretude has a stronger source base for HCP, source-seeking, efficacy, and safety prompts. Cabotegravir has more indexed PrEP literature, older pivotal trials, and more follow-on analyses. HPTN 083 and HPTN 084 are durable named retrieval anchors. The Apretude HCP site prominently cites Landovitz et al. in NEJM and Delany-Moretlwe et al. in The Lancet, and presents trial-size and hazard-ratio reductions versus daily oral Truvada [Apretude HCP](https://apretudehcp.com/).

Lenacapavir has a smaller but high-salience publication footprint. PURPOSE 1 and PURPOSE 2 produced strong efficacy signals, NEJM publications, and broad public-health attention. Gilead's approval communication ties the product to PURPOSE 1/2, at least 99.9% remaining HIV negative, and twice-yearly dosing [Gilead](https://www.gilead.com/news/news-details/2025/yeztugo-lenacapavir-is-now-the-first-and-only-fda-approved-hiv-prevention-option-offering-6-months-of-protection). That gives Yeztugo a strong retrieval object, but not yet the same depth of implementation or long-term source material.

Implication: Apretude's advantage is evidence-density and maturity. Yeztugo's advantage is salience and attribute clarity. Both matter, but they answer different prompts.

## 4. Owned Content Architecture

Yeztugo's owned content is highly aligned with broad user prompts. The patient site repeats "twice-yearly PrEP," "one office visit, every six months," and "the longest-acting PrEP option available." It also includes DTC transcript text that repeats "twice-yearly," "one office visit every six months," and "2 injections per office visit every 6 months" [Yeztugo patient site](https://www.yeztugo.com/). The HCP site repeats "the only twice-yearly dosing" and directly states 2 subcutaneous injections every 6 months, then connects that claim to CDC, IAS-USA, NYSDOH AI, and WHO guidance [Yeztugo HCP](https://www.yeztugohcp.com/).

Apretude's owned HCP content is richer but less reducible to one consumer phrase. It emphasizes "4 years of real-world experience," over 5,000 patient-years of clinical-trial data, real-world populations, active patients, US doses administered, HPTN 083 and HPTN 084 efficacy, adherence, safety, access, and expert perspectives [Apretude HCP](https://apretudehcp.com/). The patient site states every-other-month dosing, initiation injections, provider administration, oral cabotegravir lead-in, and the need to stay under provider care [Apretude patient site](https://apretude.com/).

Implication: Yeztugo's owned content is better at simple prompt matching. Apretude's owned content is better at professional substantiation. The gap for Apretude is not lack of content. It is lack of an equally compact, patient-language answer object that is linked to its legitimate strengths.

## 5. Real-World Evidence And Implementation Signals

Apretude has a more developed implementation-evidence story. ViiV reported CROI 2025 implementation data with zero HIV acquisitions in two implementation studies and described more than 99% effectiveness in nearly 4,000 people in ongoing real-world and implementation studies [ViiV](https://viivhealthcare.com/en-us/media-center/news/press-releases/2025/march/new-implementation-study-data/). The Apretude HCP site also foregrounds real-world experience and real-world populations [Apretude HCP](https://apretudehcp.com/).

Yeztugo's real-world implementation evidence is necessarily newer. Its current source ecosystem is stronger on approval, public-health recommendation, dosing interval, and pivotal-trial outcomes than on mature real-world implementation.

Implication: Apretude has source assets that should support "established," "real-world," and "clinic workflow" prompts when those concepts are explicit. If those prompts do not retrieve Apretude prominently, the likely issue is source distribution, wording, or prompt-frame fit rather than absence of underlying material.

## 6. KOL And Investigator Visibility

Both products have credible investigator and expert networks, but the public signals differ.

Apretude's KOL visibility is embedded in named trial publications and long-running HPTN infrastructure. HPTN 083 and HPTN 084 are recognizable trial brands with investigators such as Landovitz and Delany-Moretlwe repeatedly attached in HCP and publication references. This is consistent with stronger source-seeking and HCP retrieval because those prompts often surface stable named studies and established publication trails.

Yeztugo's KOL visibility is more concentrated around breakthrough narratives and PURPOSE trial leaders. Public coverage of PURPOSE 1 prominently featured Linda-Gail Bekker and the trial's effect in young women in South Africa and Uganda. Gilead's approval communication also quotes Carlos del Rio on the potential of twice-yearly injection to address adherence and stigma barriers [Gilead](https://www.gilead.com/news/news-details/2025/yeztugo-lenacapavir-is-now-the-first-and-only-fda-approved-hiv-prevention-option-offering-6-months-of-protection).

Implication: KOL influence is probably not the direct cause of first mention in ChatGPT. The more defensible inference is that KOL-linked publications, conference materials, media quotes, and professional education reinforce source salience. Apretude has durable academic salience. Yeztugo has higher recent media and public-health salience.

## Product-Specific Diagnosis

### Yeztugo / Lenacapavir

What is working:

- The product has a highly compressible answer object: twice-yearly, every 6 months, longest acting, fewer visits.
- The same object appears in FDA and DailyMed label text, patient content, HCP content, CDC, WHO, HIV.gov, Gilead launch communications, and third-party sources.
- The launch and guideline window created a dense, fresh source cluster.
- PURPOSE 1/2 provide memorable efficacy language that is easy for models to reuse.
- The patient site exposes DTC transcript language in crawlable text, which may increase phrase repetition.

What is not working as well:

- The strong convenience frame can crowd out safety context. The audit found incomplete HIV testing, RNA/acute-HIV, resistance, and no-head-to-head caveats in many visible answers.
- The source mix can drift toward consumer, SEO, or advocacy comparison pages in edge prompts.
- Mature real-world implementation evidence is less developed than Apretude's.
- The "newer" and "best injectable" frame can lead to oversimplified answers unless comparison pages explicitly separate dosing convenience from efficacy and suitability.

Priority improvements:

1. Pair every simple convenience statement with compact safety and testing modules in crawlable HTML.
2. Publish or maintain a comparison-neutral medical-information page on lenacapavir and cabotegravir evidence, including no direct head-to-head trial and cross-trial limits.
3. Build real-world implementation pages as evidence accumulates, especially for persistence, missed visits, testing workflows, access, and switching from cabotegravir.
4. Encourage neutral medical references to include the same safety caveats that appear in the label, not only the twice-yearly attribute.

### Apretude / Cabotegravir

What is working:

- The product has a deeper PrEP publication footprint and durable named trial anchors.
- FDA approval in December 2021 gave Apretude several additional years for indexing, curriculum coverage, guideline incorporation, real-world implementation follow-up, and citation accumulation.
- HPTN 083 and HPTN 084 are well-established in labels, HCP pages, curricula, and medical references.
- CDC guidance and the National HIV Curriculum contain workflow-level cabotegravir detail, including testing, injection cadence, missed or discontinued injection considerations, and clinical follow-up.
- Mature HCP content is structured around clinical studies, real-world evidence, safety, adherence, access, and patient choice.
- Real-world and implementation evidence gives Apretude a credible "established use" frame.
- Source-seeking and HCP prompts can retrieve authoritative cabotegravir sources.

What is not working as well:

- The patient-facing answer object is less distinctive after a twice-yearly competitor enters the market. "Every other month" is clear but no longer uniquely convenient.
- The strongest differentiators are scattered across professional proof points: trial size, experience, patient-years, doses administered, real-world studies, patient choice, and implementation. These are credible but not compressed into a single lay decision frame.
- Apretude's "established option" advantage is not consistently tied to user-language prompts such as "best injection," "fewer visits," "privacy," or "I do not want a daily pill."
- The existing HCP depth may not translate into neutral consumer or public-health answer frames unless third-party sources repeat it.

Priority improvements:

1. Create a crawlable, balanced comparison page that answers: "When might an established every-2-month injectable PrEP option fit better than a newer twice-yearly option?"
2. Convert the real-world evidence and 4-year experience story into neutral-source-compatible language, with concise public summaries and clear citations.
3. Align patient, navigator, HCP, medical-information, and access pages around the same nonpromotional decision object: established injectable PrEP, more years of clinical use, large HPTN evidence base, real-world implementation experience, and clinic workflows.
4. Publish practical implementation content that neutral sources can cite: missed visits, oral bridging, testing workflows, adolescent use, discontinuation, access logistics, and who may prefer closer clinical contact.

## Manufacturer-Specific Framework

The two manufacturers do not need the same AI-search playbook.

| Manufacturer | Current source advantage | Main retrieval risk | Practical response |
|---|---|---|---|
| Gilead / Yeztugo | Compact, repeated hook: once every 6 months, twice-yearly, first/only/longest-acting, fewer visits, PURPOSE 1/2, CDC/WHO recommendation. | Convenience framing can outrun safety, testing, no-head-to-head, and implementation caveats. | Preserve the compact hook, but couple it to HIV testing, resistance, discontinuation-tail, missed-injection, drug-interaction, and comparison-limit language in every high-retrieval page. |
| ViiV / Apretude | Incumbent source depth: first injectable PrEP approval, years of indexing, CDC guidance, National HIV Curriculum detail, HPTN 083/084, mature HCP content, and implementation evidence. | Evidence depth may not compress into a simple patient-language frame when the prompt asks for newest or least frequent dosing. | Create a neutral decision object around established injectable PrEP, larger mature evidence base, real-world implementation experience, and clinically supported follow-up. Make it visible in patient, navigator, HCP, and medical-information content. |

## Framework For Manufacturers

Use the following framework to diagnose and improve AI-search performance for any drug pair.

### 1. Prompt-Frame Fit

Identify the prompt frames where the product should be clinically relevant:

- disease-first prompts
- class-first prompts
- dosing or convenience prompts
- efficacy prompts
- safety prompts
- HCP medical-information prompts
- source/citation prompts
- adversarial prompts such as "newer," "best," "replacement," or "should switch."

For each frame, ask whether the product has a compact answer object that matches real user language.

### 2. Evidence-Density Fit

Measure whether the source ecosystem supports the prompt:

- label and regulatory pages
- guidelines and public-health pages
- PubMed-indexed pivotal trials
- named trial acronyms
- medical curricula and review articles
- real-world evidence and implementation studies
- patient and HCP pages
- source-updated neutral references.

This is where Apretude performs well.

### 3. Attribute-Clarity Fit

Measure whether the product has a short, repeated, source-consistent differentiator:

- dosing interval
- route and site of administration
- population
- monitoring requirement
- onset or lead-in
- real-world use
- access or workflow advantage

This is where Yeztugo performs well.

### 4. Source-Authority Fit

For each important claim, classify whether the claim is repeated by:

- label/FDA/DailyMed
- CDC/WHO/guidelines
- medical curriculum or society education
- PubMed/PMC/major journals
- manufacturer HCP or medical information
- patient advocacy or consumer medical sources
- news or SEO comparison pages

The target is not to eliminate manufacturer content. The target is to ensure that neutral sources carry the same medically balanced facts.

### 5. Safety-Coupling Fit

The audit showed that ChatGPT can cite sources and still omit safety context. Every high-retrieval page should couple its main benefit with:

- HIV testing before start and during use
- acute-HIV or RNA-testing nuance where relevant
- resistance risk
- STI and comprehensive prevention context
- missed-dose and discontinuation implications
- no direct head-to-head or cross-trial caveats for comparator pages

### 6. Controllability And Action Plan

Classify gaps by controllability:

| Gap type | Examples | Manufacturer action |
|---|---|---|
| Owned fixable | HCP FAQ, patient FAQ, medical-information page, schema, sitemap, label links | Update crawlable pages and harmonize wording. |
| Manufacturer-influenceable | Publications, congress materials, medical education, KOL-authored reviews, implementation studies | Publish and distribute evidence in citable formats. |
| Correction-only | Medical reference errors, stale third-party pages, guideline omissions | Submit corrections or provide source packets. |
| Uncontrollable | AI ranking, news cycle, social posts, competitor launch salience | Monitor prompts, identify recurring source pathways, and respond with better evidence assets. |

## Practical Playbook For Both Manufacturers

### For Gilead / Yeztugo

- Preserve the simple twice-yearly retrieval object, but attach safety and comparative-rigor caveats to it everywhere.
- Build more neutral, nonpromotional comparison and implementation content before consumer/SEO pages become the dominant AI source layer.
- Develop real-world evidence and operational guidance quickly enough that HCP prompts do not rely mainly on launch claims.
- Ensure switching-from-cabotegravir and no-head-to-head content is easy to find, because "replacement" prompts were strongly associated with Yeztugo first mentions.

### For ViiV / Apretude

- Do not compete with "twice yearly" as a slogan. Build a different answer object: established injectable PrEP, large HPTN evidence base, real-world implementation experience, and clinically supported follow-up.
- Make that object available in patient-language pages, not only HCP pages.
- Create comparison-neutral content that explicitly explains why fewer visits is only one decision factor.
- Push real-world implementation evidence into neutral channels that AI systems already retrieve: curriculum pages, public-health explainers, clinical reviews, and patient-support organizations.

## Bottom Line

Yeztugo appeared first most often in prompt frames that asked for the newest, least frequent, or most convenient injectable PrEP option. Apretude had more overall first mentions in the OCR-visible audit, a pattern consistent with its deeper established evidence and source ecosystem. The manufacturer opportunity on both sides is to close the gap between visibility and medically complete answers. The best AI-search optimization strategy is therefore not more brand density. It is better alignment between prompt frames, authoritative source distribution, compact product attributes, and safety-coupled comparison content.
