# Drug Information Optimization for AI Search

Date: July 4, 2026

Purpose: provide an AI-agent checklist for assessing how well public information about a prescription drug is positioned for generative AI search, and define controlled competitor experiments that separate clinical profile from information-distribution effects.

## Core Principle

For drug queries, AI search systems often cite neutral or quasi-neutral sources rather than manufacturer pages. The audit should therefore evaluate the full evidence supply chain: label, trial records, PubMed-indexed publications, guidelines, medical reference sites, patient-education sites, owned medical information, HCP pages, and the actual citations returned by AI search tools.

The objective is not simply higher brand visibility. For medical information, the primary objective is accurate, current, balanced, label-consistent answers.

## Agent Checklist

Score each dimension on a 0-5 scale. Use 0 for absent, inaccessible, stale, misleading, or unsafe; 3 for adequate but incomplete; and 5 for current, accessible, balanced, and well-supported.

| Dimension | Weight | Objective checks | Evidence to collect |
|---|---:|---|---|
| Drug entity definition | 5 | Brand, generic, sponsor, mechanism, indication, geography, dose form, trial acronyms, RxNorm/MeSH/Wikidata identifiers, and common aliases are unambiguous. | FDA label, DailyMed, Drugs@FDA, RxNorm, MeSH, Wikidata, official brand/HCP pages. |
| Regulatory and label retrievability | 10 | Current label, Medication Guide, boxed warnings, contraindications, limitations of use, dosing, and adverse reactions are easy to locate and align across official sources. | FDA label, DailyMed, REMS materials if applicable, approval letters, label revision dates. |
| Owned patient information | 8 | Patient pages answer common questions directly, are indexable, use plain language, preserve safety balance, and do not hide key content behind scripts or PDFs only. | Brand site, patient support site, sitemap, robots.txt, rendered HTML, page dates, screenshots. |
| Owned HCP / medical information | 8 | HCP and medical-information pages provide direct, indication-specific answers with trial design, endpoints, population, comparator, dosing, and safety caveats. | HCP site, medical information pages, PI links, clinical-data pages, downloadable resources. |
| Publications and PubMed footprint | 10 | Pivotal, head-to-head, long-term, subgroup, safety, PRO, RWE, and HEOR evidence is PubMed-indexed and clearly tied to the drug entity and indication. | PubMed queries by brand, generic, trial acronym, indication, target, and comparator; PMID list and abstracts. |
| ClinicalTrials.gov / registry quality | 7 | Trial records are current, have results where required, link to publications, and avoid ambiguity between active, completed, terminated, and expanded-access studies. | NCT records, result postings, history of changes, publication links, EU CTIS where relevant. |
| Guidelines and medical-reference coverage | 8 | Major guidelines and medical references mention the drug accurately for approved use, line of therapy, patient population, and safety constraints. | Specialty guidelines, society pages, NCCN/ASCO/ESMO/AAD/AHA/ADA or relevant equivalents, Merck Manual, StatPearls, payer policies. |
| Neutral patient/HCP source coverage | 8 | MedlinePlus, Mayo/Cleveland Clinic, patient foundations, advocacy groups, and major medical publishers explain the drug, alternatives, benefits, risks, and monitoring accurately. | MedlinePlus, Mayo Clinic, Cleveland Clinic, NPF, Cancer.gov, specialty foundations, GoodRx/Drugs.com/WebMD when relevant. |
| Structured data and crawlability | 7 | Important pages are crawlable, canonicalized, fast, and expose drug, indication, dose, safety, and date fields in machine-readable or easily parsed HTML. | robots.txt, sitemap.xml, JSON-LD/schema, canonical tags, meta titles/descriptions, noindex checks, page-speed/render checks. |
| Freshness | 7 | Public information reflects recent approvals, label changes, guideline updates, trial readouts, safety communications, publication updates, and discontinued/withdrawn claims. | Page modified dates, FDA safety updates, press releases, guideline revision dates, PubMed date filters, trial-history updates. |
| AI answer quality | 12 | AI tools return accurate, balanced, source-backed answers across patient, HCP, disease-first, class-first, comparator, safety, dosing, and trial prompts. | ChatGPT Search, Perplexity, Google AI Mode/AI Overviews if available, Claude search if available, Bing/Copilot; full prompts, timestamps, answers, citations. |
| Source controllability | 10 | The most important missing or incorrect facts can be improved through compliant owned-content updates, publication planning, registry correction, label clarity, medical-reference correction, or patient-education collaboration. | Gap matrix sorted by owned, manufacturer-influenceable, correction-only, and uncontrollable sources. |

Maximum score: 100.

## Safety Gates

Apply a cap after scoring if any safety issue is observed.

| Condition | Score cap |
|---|---:|
| AI answers commonly omit boxed warning or major contraindication | 60 |
| AI answers recommend or normalize off-label use without a clear caveat | 55 |
| Owned content materially conflicts with the current label | 50 |
| Drug entity is frequently confused with another product | 70 |
| Current label or regulatory source is hard to locate | 75 |
| AI answers cite low-quality commercial pages over label, PubMed, guideline, or medical-reference sources for safety questions | 70 |

## Required AI Search Test Set

Run each prompt in clean sessions across the same platforms, on the same date, with location and account state recorded.

1. What is [drug] used for?
2. [drug] benefits and risks
3. [drug] side effects
4. [drug] boxed warning
5. [drug] dosing
6. [drug] clinical trial results
7. [drug] vs [comparator] for [condition]
8. Which [class] drugs are approved for [condition]?
9. What do guidelines say about [drug] for [condition]?
10. [generic name] [condition] PubMed
11. [drug] patient information
12. [drug] HCP information

For competitor experiments, add:

1. For [matched population], which drugs in [class] have the strongest evidence for [endpoint]?
2. Compare [drug A] and [drug B] for [condition]. Which has stronger evidence for [endpoint]?
3. Which sources support [drug A] vs [drug B]?
4. Which drug is preferred for [condition], and what evidence supports that answer?

## Output Fields for an Agent

```yaml
drug_name:
generic_name:
sponsor:
indication_scope:
geography:
audit_date:
platforms_tested:
overall_score_100:
score_band: optimized | adequate | vulnerable | poor
safety_gate_applied: true | false
safety_gate_reason:
dimension_scores:
  drug_entity_definition:
    raw_0_to_5:
    weighted_score:
    evidence_urls:
    gaps:
    remediation:
  regulatory_label:
  owned_patient_information:
  owned_hcp_medical_information:
  publications_pubmed:
  clinical_trials_registry:
  guidelines_medical_references:
  neutral_sources:
  structured_data_crawlability:
  freshness:
  ai_answer_quality:
  source_controllability:
ai_query_results:
  - query:
    platform:
    run_datetime:
    answer_accuracy: accurate | incomplete | misleading | unsafe
    drugs_mentioned:
    citation_order:
    cited_sources:
    missing_facts:
    safety_issues:
competitor_experiment:
  matched_condition:
  matched_population:
  clinical_comparability_basis:
  confounders_controlled:
  residual_confounders:
  observed_citation_bias:
  hypothesized_information_driver:
top_10_gaps:
highest_priority_fixes:
source_controllability_matrix:
  owned_fixable:
  manufacturer_influenceable:
  correction_only:
  uncontrollable:
evidence_log:
  - source_type:
    url:
    access_date:
    key_finding:
```

## Interpretation Bands

| Score | Interpretation |
|---:|---|
| 85-100 | Strong AI-search readiness. Answers are accurate, balanced, current, and source-backed. |
| 70-84 | Adequate but exposed to selective omissions, stale sources, or weak third-party coverage. |
| 50-69 | Vulnerable. AI answers may be incomplete, poorly cited, or dependent on uncontrolled sources. |
| <50 | Poor. Material risk of inaccurate, stale, ambiguous, or unsafe AI-generated summaries. |

## Experiment Design

The experiment should not start by asking, "Which brand gets mentioned more?" It should test whether a drug with comparable or stronger evidence is less likely to appear because the public information environment is weaker, older, less structured, or less represented in neutral sources.

Minimum controls:

1. Same condition.
2. Same geography.
3. Same patient population.
4. Same line of therapy or disease stage.
5. Same endpoint type.
6. Same date cutoff.
7. Same AI platforms, prompts, session conditions, and run time.
8. Same source-quality coding.
9. Explicit adjustment for approval age, market share, indication breadth, additional indications, DTC awareness, safety controversies, and guideline timing.

Primary measures:

1. Mention share across prompts.
2. First-mentioned drug share.
3. Citation share.
4. High-quality citation share, limited to label, FDA/DailyMed, PubMed/PMC, guidelines, society pages, and major medical references.
5. Omission rate when the drug is clinically relevant.
6. Accuracy and safety-balance score.
7. Recency of cited sources.
8. Evidence-source type: owned, regulator, publication, guideline, medical reference, patient organization, consumer medical publisher, news, social/community, low-quality SEO.

## Best First Experiment: Bimzelx vs Cosentyx in Plaque Psoriasis

Recommended test: Bimzelx (bimekizumab-bkzx) vs Cosentyx (secukinumab) for adults with moderate-to-severe plaque psoriasis, focused on complete skin clearance.

Why this is a strong first experiment:

1. The disease and endpoint can be tightly matched: adult moderate-to-severe plaque psoriasis and PASI 100 / complete skin clearance.
2. There is direct head-to-head evidence. In BE RADIANT, bimekizumab produced greater complete skin clearance than secukinumab in moderate-to-severe plaque psoriasis. The PubMed abstract states that bimekizumab resulted in greater skin clearance than secukinumab, and the NEJM page reports week-48 PASI 100 rates of 67.0% vs 46.2% [PubMed](https://pubmed.ncbi.nlm.nih.gov/33891380/), [NEJM](https://www.nejm.org/doi/full/10.1056/NEJMoa2102383).
3. Public information density is imbalanced. On July 4, 2026, PubMed title/abstract searches returned 1,737 results for `secukinumab psoriasis` and 301 for `bimekizumab psoriasis`.
4. Approval-age and indication-breadth confounders are visible and can be modeled. Bimzelx was FDA-approved for adult moderate-to-severe plaque psoriasis in October 2023 [UCB](https://www.ucb-usa.com/stories-media/UCB-U-S-News/detail/article/bimzelx-approved-by-the-us-fda-for-the-treatment-of-adults-with-moderate-to-severe-plaque-psoriasis). Cosentyx was first FDA-approved in 2015 and has broader labeled indications and pediatric psoriasis use [Drugs.com approval history](https://www.drugs.com/history/cosentyx.html), [Cosentyx label](https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/125504s082lbl.pdf).

Hypothesis:

Cosentyx may receive more AI-search references in broad psoriasis or IL-17 biologic prompts because it has a longer public-source footprint, broader indication footprint, more neutral-source mentions, and greater PubMed density. Bimzelx may perform better when prompts specify adult plaque psoriasis and complete skin clearance, because the head-to-head evidence is directly relevant.

Do not claim yet:

This example does not yet prove that UCB's or Novartis's information-distribution approach caused the AI citation pattern. It is a controlled experiment candidate. Causality would require live prompt testing, source-citation capture, and comparison of cited-source ecosystems.

Suggested prompts:

1. For adults with moderate-to-severe plaque psoriasis, which IL-17 biologics have the strongest evidence for complete skin clearance? Cite sources.
2. Compare bimekizumab and secukinumab for plaque psoriasis in adults. Which has stronger evidence for PASI 100?
3. What are the FDA-approved treatment options for adult moderate-to-severe plaque psoriasis after topical therapy fails?
4. Which biologic is better supported by head-to-head evidence for complete clearance in plaque psoriasis: Bimzelx or Cosentyx?
5. What evidence supports Bimzelx compared with Cosentyx for plaque psoriasis?

Expected readout:

If broad prompts over-cite Cosentyx but endpoint-specific prompts cite BE RADIANT and shift toward Bimzelx, the result would support a source-context hypothesis: AI search may reward older and broader public footprints unless the prompt forces retrieval of the clinically discriminating evidence.

## Public Citation-Share Proof Point: Wegovy vs Zepbound

Wegovy (semaglutide) vs Zepbound (tirzepatide) is the best public example with an external AI-citation-share estimate, but it is more confounded than the psoriasis pair.

Verified facts:

1. SURMOUNT-5 reported greater weight loss with tirzepatide than semaglutide in adults with obesity or overweight without diabetes. PubMed states that tirzepatide was superior to semaglutide for body-weight and waist-circumference reduction at week 72 [PubMed](https://pubmed.ncbi.nlm.nih.gov/40353578/). Search results from the NEJM page report mean weight reduction of 20.2% with tirzepatide vs 13.7% with semaglutide [NEJM](https://www.nejm.org/doi/10.1056/NEJMoa2416394).
2. Wegovy has a major additional cardiovascular-risk-reduction indication. FDA approved Wegovy to reduce major cardiovascular events in adults with cardiovascular disease and obesity or overweight, with MACE rates of 6.5% vs 8.0% in the FDA release [FDA](https://www.fda.gov/news-events/press-announcements/fda-approves-first-treatment-reduce-risk-serious-heart-problems-specifically-adults-obesity-or).
3. 5W's 2026 weight-loss AI visibility index estimated Wegovy at 19.0% citation share and Zepbound at 16.0% across 60+ weight-loss prompts in Q1 2026 [5W](https://www.5wpr.com/ai-visibility-index/weight-loss-ai-visibility-index-2026/).

Interpretation:

This is a useful demonstration that the clinically stronger weight-loss result does not automatically dominate AI citation share. It is not a clean causality example because Wegovy has earlier launch timing, semaglutide/Ozempic spillover, broader consumer familiarity, and a cardiovascular indication. It is still a good second experiment because public AI-citation data already exist.

## Other Candidate Experiments

| Pair | Why it is useful | Main confounder |
|---|---|---|
| Kisunla (donanemab) vs Leqembi (lecanemab) in early Alzheimer disease | Similar disease-modifying category, with different approval timing and public-source footprints. | No direct head-to-head trial; Leqembi's earlier traditional approval and center adoption may dominate. |
| Yeztugo (lenacapavir) vs Apretude (cabotegravir) for injectable HIV PrEP | Dosing differentiation is clinically and operationally meaningful. | Approval timing and guideline/source lag are dominant confounders. |
| Nurtec ODT (rimegepant) vs Ubrelvy (ubrogepant) for acute migraine | Tests whether broader dual-use positioning shifts AI references even when the prompt is acute-only. | Nurtec has acute plus preventive indications, which is a structural information and label confounder. |

## Recommendation

Use two experiments:

1. Plaque psoriasis as the cleaner causal test: Bimzelx vs Cosentyx.
2. Weight management as the public citation-share demonstration: Zepbound vs Wegovy.

The psoriasis experiment is better for isolating information-distribution effects. The GLP-1 experiment is better for communicating why clinical strength alone does not determine AI-search reference share.
