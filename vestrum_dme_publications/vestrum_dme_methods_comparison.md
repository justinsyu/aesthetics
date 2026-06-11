# Vestrum Health DME Publication Methods Comparison

Detailed update: the expanded operational-definition review is now in `vestrum_dme_methods_comparison_detailed.md`, with the field-level table in `methods_extraction_detailed.csv` and `methods_extraction_detailed.json`. Use those detailed files as the authoritative methods comparison for diagnostic-code availability, treatment/exposure definitions, outcome algorithms, supplement/appendix locations, and full-text access caveats.

Retrieval date: 2026-06-03

## Scope and Inclusion

The saved Vestrum Health media page contains five DME-tagged entries. Four are qualifying Vestrum database analyses that evaluate DME or DME-containing retinal-disease cohorts. One DME-tagged item, the Schachat 2020 Ophthalmology Retina year-4 commentary, was logged but excluded because it is not a primary Vestrum database analysis of DME patients.

The core Vestrum website set is the main answer to the request. I also saved and extracted several newer Vestrum-DME publications found outside the retrieved Vestrum media page because they add useful methods context for treatment patterns, longer-term outcomes, economics, and newer anti-VEGF agents.

## Deliverables in This Folder

- `source_log.json` and `source_log.csv`: authoritative source URLs, local files, access status, retrieval date, and caveats.
- `download_manifest.json`: corrected manifest generated from the same source log.
- `methods_extraction.csv`: publication-level methods/outcomes extraction.
- `downloads/`: saved PDFs, HTML landing pages, and access-evidence files.
- `extracted_text/`: text extracted from saved manuscripts, abstracts, or webpages where available.
- `vestrum_dme_media_items.json`: parsed DME-tagged Vestrum media cards.
- `vestrum_media_page.html`: saved Vestrum media-page HTML.

## Access Caveats

Several original Vestrum document URLs now redirect away from the original PDFs to a CoreVitas/PPD page, so the final saved PDFs for the Pitcher 2020/2021 and Ciulla 2018 papers came from HubSpot mirrors. The Vestrum card for the 2020/2021 visual-acuity paper has a filename suggesting neovascular AMD and lists 26,658 eyes, but the published BJO article and PMC full text state DME/DMO and 28,658 patient eyes.

Healio blocked scripted access to the 2021 incidence/prevalence article, so I saved an institutional abstract/methods page instead. The PMC PDF endpoint for the BJO paper returned proof-of-work HTML, so I saved the PMC full text HTML and kept the PDF-endpoint response as access evidence. A ScholarWorks item page for the BJO paper was saved, but its downloadable bitstream appeared unrelated and was not retained. SAGE blocked the 2026 faricimab full text/PDF, so that extraction is based on PubMed only.

`methods_windows_raw.txt` is retained as a raw scratch extraction only. Do not use it as a final source because it contains a known unrelated manuscript block from an earlier bad ScholarWorks bitstream attempt.

## Core Vestrum Website Publications

| ID | Publication | Design and Cohort | Key Methods | Outcomes Studied |
| --- | --- | --- | --- | --- |
| core-01 | Increasing Incidence and Prevalence of Common Retinal Diseases in Retina Practices Across the United States (2021) | Retrospective study; Eyes with DME identified among eyes with common retinal diseases; exact diagnostic-code/clinical definition not available in saved abstract-level source; DME: 270,703 eyes | Study period: January 2014 to December 2019. Index/follow-up: Not extracted from accessible abstract-level source; Disease incidence/prevalence assessed over 2014-2019. Unit: Eye. | Incidence and prevalence of common retinal diseases; DME as one disease category |
| core-02 | Evaluation of Patients Receiving Intravitreal Anti-VEGF for Diabetic Macular Edema in Clinical Practice in the United States (2020/2021) | Retrospective analysis of deidentified EMRs; Eyes newly diagnosed with DME in the Vestrum database and administered a first anti-VEGF injection; Year-1 cohort 3,028 eyes; year-2 cohort 1,292 eyes | Study period: Index first anti-VEGF injection from 2012-01-01 to 2015-04-30; observation through 2017-04-30. Index/follow-up: First anti-VEGF injection; 12 and 24 months after index injection; month-12 VA closest to 12 months in months 11-12; required VA at index, month 12, and at least once each quarter. Unit: Eye. | VA change and anti-VEGF injection frequency/intensity over 1 and 2 years |
| core-04 | Visual Acuity Outcomes and Anti-VEGF Therapy Intensity in Diabetic Macular Edema: A Real-World Analysis of 28,658 Patient Eyes (2020/2021) | Retrospective analysis; Treatment-naive DME/DMO patient eyes receiving anti-VEGF and meeting follow-up criteria; 28,658 patient eyes | Study period: Anti-VEGF injections between January 2013 and July 2018. Index/follow-up: Initial anti-VEGF treatment in the study period; One year; required follow-up in months 11-12. Unit: Patient eye. | Mean 1-year VA change; injection frequency; VA change by medication, baseline VA, and treatment intensity |
| core-05 | Real-world Outcomes of Anti-VEGF Therapy in Diabetic Macular Edema in the United States (2018) | Retrospective, uncontrolled review; Treatment-naive DME patients treated with anti-VEGF and meeting initial injection/follow-up criteria; 6-month cohort 4,613 eyes; 12-month cohort 5,840 eyes; 24-month cohort 5,155 eyes | Study period: Treatment-naive DME diagnosis/treatment from January 2011 to March 2017; follow-up available before March 2018. Index/follow-up: DME diagnosis and initial anti-VEGF treatment period; Mutually exclusive 6-, 12-, and 24-month cohorts based on available follow-up/loss to follow-up. Unit: Patient eye. | VA outcomes and number of anti-VEGF treatments; corticosteroid, macular laser, and panretinal photocoagulation utilization captured |

## Broader Relevant Vestrum-DME Publications Saved for Context

| ID | Publication | Why It Matters | Methods Signal |
| --- | --- | --- | --- |
| context-06 | Evolving Treatment Patterns in Diabetic Macular Edema Between 2015 and 2020 (2023) | Useful for diagnosis-indexed treatment-pattern studies and untreated/combo therapy endpoints. | Retrospective review; Newly diagnosed DME eyes; Treatment distribution, anti-VEGF/steroid/laser utilization, untreated proportion, baseline and follow-up VA change |
| context-07 | Longer-Term Anti-VEGF Outcomes in Neovascular AMD, Diabetic Macular Edema, and Vein Occlusion-Related Macular Edema (2022) | Best context for multi-year DME anti-VEGF outcome windows and durability of real-world gains. | Retrospective analysis; Treatment-naive DME eyes among nAMD, DME, BRVO-ME, and CRVO-ME cohorts; VA change over longer-term follow-up and injection frequency |
| context-08 | Bevacizumab-First Treatment Protocol AC Versus Real-World Treatment for Diabetic Macular Edema: Cost Analysis (2024) | Template for using Vestrum as utilization/cost input rather than only VA outcome database. | Cost analysis comparing modeled Protocol AC bevacizumab-first strategy versus Vestrum real-world utilization; Treatment-naive DME eyes with baseline VA matched to Protocol AC and anti-VEGF monotherapy; Costs, visits, imaging, injection counts, drug mix, VA gain |
| context-09 | Cost-Effectiveness of Step Therapy in Diabetic Macular Edema: Protocol AC and Real-World Data (2025) | Shows how Vestrum DME outcomes/utilization can support HEOR endpoints and sensitivity analyses. | Theoretical Markov cost-effectiveness model from a US societal perspective; DME population modeled from Protocol AC and Vestrum real-world data; Costs, QALYs, incremental cost-utility ratio, probability of cost-effectiveness, healthcare and societal cost categories |
| context-10 | Visual Outcomes and Dosing Frequencies of Patients with Diabetic Macular Edema Treated with Faricimab Versus Other Anti-VEGF Agents (2026) | Useful as current evidence that Vestrum can evaluate newer agents and durability intervals, but insufficient for detailed design extraction without full text. | Retrospective database analysis based on abstract; DME eyes treated with faricimab, bevacizumab, ranibizumab, or aflibercept; treatment-naive and treatment-experienced switch cohorts; Mean VA change and mean days between injections/dosing frequency |

## Cross-Study Methods Patterns

The most common analytic frame is a retrospective patient-eye-level study of deidentified Vestrum EMR data. The treatment-outcomes papers generally define a DME eye, identify an index treatment date, require baseline VA and follow-up VA in a fixed window, then stratify by treatment intensity, baseline VA, and sometimes initial agent.

The strongest one-year anti-VEGF outcome template is the 28,658-eye BJO analysis. It avoids the stricter loading-dose requirement from the 2018 paper, requires 1-year follow-up in months 11-12, excludes other retinal diagnoses, uses patient-eye analysis with bilateral-eye sensitivity, converts Snellen VA to approximate ETDRS letters, and stratifies by baseline VA and injection frequency. The Pitcher paper is better when the research question is specifically treatment intensity over 1-2 years because it requires quarterly VA and compares <=6 versus >6 injections per year.

Baseline VA stratification is essential. Across the anti-VEGF outcome papers, better baseline VA produces ceiling effects and sometimes letter loss, while worse baseline VA produces larger gains. Injection frequency is also central: lower real-world injection intensity is repeatedly associated with smaller VA gains than trial protocols.

For treatment-pattern questions, the diagnosis-indexed Sodhi approach is more appropriate than treatment-indexed anti-VEGF outcome cohorts because it captures untreated eyes, focal laser, steroid use, anti-VEGF monotherapy, and combinations. For economics, Grewal and Leung show how Vestrum can supply real-world visits, imaging, injections, agent mix, and VA outcomes for cost or cost-effectiveness models.

## Outcomes Previously Studied

- Epidemiology: incidence and prevalence of DME among other retinal diseases.
- Treatment utilization: anti-VEGF, focal laser, steroids, combinations, untreated eyes, visits, OCT/fundus imaging, and agent mix.
- Visual outcomes: VA change at 6, 12, and 24 months; longer-term 3- and 5-year VA outcomes; VA by baseline VA strata.
- Treatment intensity/durability: number of injections, <=6 versus >6 injections, injection-frequency histograms, days between injections, and treatment-intensity trajectories.
- Agent comparisons: aflibercept, bevacizumab, ranibizumab, and faricimab, with switcher and treatment-experienced analyses where available.
- Economic outcomes: modeled cost, cost-effectiveness, QALYs, utilization-based costs, and sensitivity/probabilistic analyses.

## Recommended Future Vestrum DME Study Template

1. Define the research question first: epidemiology, treatment patterns, anti-VEGF outcomes, durability, agent comparison, or economic utilization. Use diagnosis-indexed cohorts for treatment-pattern questions and treatment-indexed cohorts for anti-VEGF outcome questions.
2. Identify treatment-naive or newly diagnosed DME eyes, and exclude other retinal diagnoses likely to confound treatment or outcome attribution, especially AMD, RVO, and myopic CNV when the endpoint is DME-specific anti-VEGF response.
3. Use eye as the primary unit of analysis, but prespecify how bilateral eyes will be handled. A sensitivity analysis excluding bilateral cases is a defensible minimum.
4. For anti-VEGF outcomes, set the index date as the first anti-VEGF injection. Require baseline VA and a fixed follow-up window such as months 11-12 for one-year outcomes. Add quarterly VA requirements only when the question depends on treatment-intensity trajectory.
5. Convert Snellen VA to approximate ETDRS letters using a documented formula, and report limitations from non-protocolized real-world VA testing.
6. Prespecify baseline VA strata because ceiling effects are consistent and can dominate crude mean VA change.
7. Stratify by injection frequency/treatment intensity. A practical minimum is injection count over 12 months; richer analyses can use frequency bins, <=6 versus >6 injections, or days between injections.
8. For agent comparisons, report switcher sensitivity analyses and avoid causal wording unless methods adjust for treatment-selection bias.
9. Use descriptive statistics and mean change with 95% CI for core outcome summaries. Paired t-tests are common in prior papers, but modern comparative studies should consider multivariable or propensity methods if causal agent comparisons are intended.
10. For HEOR work, capture visits, imaging, injections, medication mix, and VA change directly from Vestrum, then document cost sources and run one-way plus probabilistic sensitivity analyses.

## Key Methodological Caveats

All Vestrum DME studies reviewed here are retrospective or model-based uses of retrospective real-world data. The main risks are nonrandom treatment selection, variable VA collection methods, possible treatment outside contributing practices, loss-to-follow-up selection, bilateral-eye dependence, inconsistent anatomic/OCT abstraction, and cohort definitions that can select for more adherent or more actively treated patients.

## File Map

- Source log JSON: `source_log.json`
- Source log CSV: `source_log.csv`
- Corrected download manifest: `download_manifest.json`
- Methods extraction CSV: `methods_extraction.csv`
- Raw Vestrum media HTML: `vestrum_media_page.html`
- Parsed media cards: `vestrum_dme_media_items.json`
