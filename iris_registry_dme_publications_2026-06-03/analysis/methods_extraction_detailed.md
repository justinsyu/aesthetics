# Detailed Methods Extraction: IRIS Registry DME Publications

Updated: June 3, 2026.

This addendum expands `methods_extraction.csv` with article-level operational details where the full text, article preview, PubMed XML, PMC HTML, or saved poster/presentation text exposed them. When the available source pointed to a supplement but the supplement was too large or could not be downloaded as a real file in this environment, the supplement location is listed instead.

## Source Availability Notes

| Item | Full text / methods availability |
|---|---|
| Cantrell 2020 | PubMed XML and Elsevier metadata saved; ScienceDirect article page blocked locally. Open-access API returned metadata only. |
| Malhotra 2021 | ScienceDirect preview and PubMed XML available; full methods beyond preview require publisher access. Preview confirms a supplemental material page at AAO Journal. |
| Greenlee 2022 | PubMed XML available; Healio page blocked locally. |
| Maturi 2024 | PMC full-text HTML available and reviewed. Supplement links are listed in PMC; NCBI downloads returned preparation stubs locally. |
| Kuo 2024 | ScienceDirect open abstract/preview and PubMed XML available; direct PDF endpoints blocked locally. The article preview notes supplementary material at Ophthalmology Retina. |
| Singh 2024 initial dosing | PMC/BMC full text available and reviewed. Supplement links were identified, but NCBI downloads returned preparation stubs locally. |
| Borkar/Singh 2025 faricimab manuscripts | PubMed XML available; Healio pages blocked locally. Conference PDFs provide more detailed FARETINA-DME operational definitions. |
| Zhang 2026 | PubMed XML and Springer full text available; supplementary PDF contains the long disease-code table. |
| Conference PDFs | Saved and text-extracted when accessible. These contain the most specific FARETINA-DME VA/CST windows and safety code definitions. |

## AAO-Listed Core DME Items

### AAO 2017 PA017 Treatment-Pattern Presentation

- Source: `source_pages/iris_registry_annual_meeting.html`.
- Public detail available: AAO listing identifies the presentation as "Treatment Patterns for Diabetic Macular Edema in the United States: Analysis of the IRIS Registry"; purpose was "to characterize treatment patterns surrounding incident diabetic macular edema in the United States."
- Operational details not exposed: no public downloadable abstract/presentation file was found on the AAO page; no diagnostic-code or outcome-definition appendix was exposed.
- Use for comparison: treat as precursor/public presentation metadata for the later Cantrell 2020 manuscript unless the AAO meeting archive file is obtained separately.

### Cantrell 2020: Treatment Patterns for Diabetic Macular Edema

- Source files: `downloads/cantrell_2020_treatment_patterns_dme/`; AAO listing in `source_pages/iris_registry_research.html`.
- Public full-text status: PubMed XML and Elsevier metadata saved; ScienceDirect HTML/PDF blocked locally. The saved Elsevier XML indicates open-access metadata but did not include body text.
- Data source: AAO IRIS Registry.
- Study type: retrospective registry analysis.
- Cohort: newly diagnosed / incident DME in IRIS Registry.
- Cohort size reported in accessible article metadata/abstract summaries: 13,410 treatment-naive patients with DME.
- Treatment operationalization available from accessible sources:
  - DME treatment pattern categories: anti-VEGF, laser, corticosteroid, combination, and no immediate treatment/observation.
  - Initial treatment window captured in accessible secondary descriptions: within 28 days of initial DME diagnosis.
  - Initial 28-day management counts reported from the article: observation/no immediate treatment 9,990; anti-VEGF 2,086; laser 1,133; corticosteroid 133; combined therapy 68.
- Missing from accessible source: diagnostic ICD code list, full inclusion/exclusion rules, VA conversion rules, and statistical methods.
- Where to obtain missing details: publisher article at https://doi.org/10.1016/j.ophtha.2019.10.019.

### Malhotra 2021: Disparities at Anti-VEGF Initiation for DME

- Source files: `downloads/malhotra_2021_disparities_initiation_anti_vegf_dme/`; ScienceDirect preview at https://www.sciencedirect.com/science/article/abs/pii/S0161642021001962.
- Full-text status: preview and PubMed abstract available; full text not available locally.
- Study design: retrospective cross-sectional study.
- Data source: Academy IRIS Registry.
- Cohort: patients initiating anti-VEGF injection treatment for DME between 2012 and 2020. PubMed/preview cohort: n = 203,707 original query; preview result text reports 203,673 analyzed.
- Exposures/predictors: race, ethnicity, insurance status, and geographic location.
- Outcomes:
  - Baseline / presenting visual acuity at anti-VEGF initiation.
  - Diabetic retinopathy severity at anti-VEGF initiation.
- Statistical approach: multivariate regression analyses.
- Effect measures reported in the abstract-level source: incidence rate ratios for injection use and odds ratios for longitudinal VA outcomes.
- Diagnostic-code details: not exposed in preview/PubMed. The ScienceDirect preview states supplemental material is available at AAO Journal.
- Where to obtain supplement/code details: supplemental material link on the ScienceDirect page / AAO Journal page for DOI https://doi.org/10.1016/j.ophtha.2021.03.010.

### Greenlee 2022: Socioeconomic Disparities, Anti-VEGF Use, and VA Outcomes

- Source files: `downloads/greenlee_2022_socioeconomic_disparities_dme/`.
- Full-text status: PubMed XML available; Healio full page blocked locally.
- Study design: retrospective cohort study.
- Data source: AAO IRIS Registry.
- Cohort: patients diagnosed with DME who received at least one anti-VEGF injection between 2012 and 2020; PubMed abstract n = 203,707.
- Exposures/predictors: race, ethnicity, insurance status, and geographic location.
- Outcomes:
  - Anti-VEGF injection use during a 60-month period.
  - Longitudinal visual acuity outcomes.
- Statistical approach: multivariate regression analyses.
- Diagnostic-code details: not exposed in PubMed abstract.
- Where to obtain missing details: publisher article DOI https://doi.org/10.3928/23258160-20220615-01.

### Maturi 2024: Race/Insurance Status, DR/DME Treatment Outcomes

- Source files: `downloads/maturi_2024_race_insurance_dr_dme/`; extracted text in `text/maturi_2024_race_insurance_dr_dme.txt`; PMC full text https://pmc.ncbi.nlm.nih.gov/articles/PMC11102718/.
- Study design: retrospective analysis.
- Data source: AAO IRIS Registry; full text describes the registry as an aggregated deidentified database with >454 million patient visits from 75.4 million unique patients since 2013 and ~15,920 contributing clinicians.
- Query period: January 1, 2014 to December 31, 2018.
- Initial disease query: DR search yielded 2,148,019 unique patients and 4,031,143 unique eyes with DR with or without DME.
- Final cohort: 43,274 eyes.
- Unit of analysis: one eye per patient; if both eyes met criteria, laterality was randomly selected.
- Inclusion criteria:
  - DR diagnosis after age 18.
  - Anti-VEGF treatment only after DR diagnosis.
  - Documented baseline VA and 1-year and 2-year follow-up VA.
- Exclusions:
  - Concurrent diagnoses that could require anti-VEGF, including AMD, CRVO, or choroidal neovascularization.
  - Unspecified laterality.
  - Cataract surgery in the first year of DR treatment.
  - Undocumented VA or baseline VA worse than 20/400 (>1.3 logMAR).
  - Missing 1-year or 2-year follow-up VA.
  - Race/ethnicity listed as other, unknown, or Asian.
  - Focal laser and/or intravitreal steroid in conjunction with anti-VEGF, because sample size was insufficient.
- Diagnostic definitions:
  - ICD-10-CM codes were used to determine DR severity and DME presence.
  - The article states code definitions are in the supplemental material.
  - Supplement location: PMC lists `sj-xlsx-1-vrd-10.1177_24741264231221607.xlsx`; live supplement URL is `https://pmc.ncbi.nlm.nih.gov/articles/instance/11102718/bin/sj-xlsx-1-vrd-10.1177_24741264231221607.xlsx` and SAGE supplement landing is `https://journals.sagepub.com/doi/suppl/10.1177/24741264231221607`.
  - Local note: attempts to save the XLSX returned an NCBI "Preparing to download" stub, preserved in `downloads/maturi_2024_race_insurance_dr_dme/`.
- Treatment categories:
  - Off-label bevacizumab.
  - Ranibizumab.
  - Aflibercept.
  - Combination therapy.
  - A patient receiving more than one anti-VEGF drug within the first 365 days after first injection was categorized as combination.
- VA operationalization:
  - Snellen VA converted to approximate ETDRS letters using `85 + 50 x log(Snellen fraction)`.
  - Baseline VA categories in the table: 20/40 or better, 20/41-20/70, 20/71-20/400.
- Outcomes:
  - Mean VA change at 1 year and 2 years.
  - Proportion treated with bevacizumab.
  - Supplemental figures cover >=15-letter loss and treatment-pattern outcomes by race/insurance.
- Statistical approach:
  - Multivariable linear regression for VA outcomes.
  - Multivariable logistic regression for anti-VEGF drug use.
  - Race and insurance status were independent variables; models controlled for disease severity and VA.

### Kuo 2024: Long-Term DME Treatment Patterns up to 6 Years

- Source files: `downloads/kuo_2024_long_term_treatment_patterns_dme/`; ScienceDirect preview https://www.sciencedirect.com/science/article/pii/S2468653024002665.
- Full-text status: open ScienceDirect preview and PubMed XML available; direct PDF endpoint blocked locally. The preview indicates supplemental material at Ophthalmology Retina.
- Study design: retrospective IRIS Registry analysis.
- Data source: AAO IRIS Registry.
- Cohort: treatment-naive patients with DME initiating anti-VEGF intravitreal therapy.
- Index period: January 1, 2015 to March 31, 2021.
- Treatment-naive definition: no previous intravitreal therapy in the prior 12 months.
- Final cohort: 190,345 eyes.
- Outcomes:
  - Baseline characteristics.
  - Annualized number of injections.
  - Injection interval.
  - Anti-VEGF agent utilization.
  - Change in VA up to 6 years.
  - Discontinuation and reinitiation.
- Operational details exposed in preview:
  - Discontinuation result reported as 51.7% discontinued IVT after a mean of 6 months; 32.8% reinitiated anti-VEGF IVT.
  - Average interval: 10 weeks in year 1, 13.2 weeks in year 2, then ~12.2-12.6 weeks in years 3-6.
  - VA stratification includes good baseline vision (>20/25) versus worse baseline vision (<20/25).
- More specific operational definitions:
  - The ASRS 2022 and ARVO 2022 conference materials appear to be precursors to this manuscript and expose definitions: switch = >=3 consecutive injections of a different anti-VEGF agent; discontinuation = no anti-VEGF IVT for >=12 months; DME documentation within 2 months pre-index; >=1 BVA recording within 60 days pre-index; no anti-VEGF in 12-month pre-index; no IVT steroid in 12-month pre-index.
- Where to obtain article supplement: Ophthalmology Retina supplemental-material link from the ScienceDirect page for DOI https://doi.org/10.1016/j.oret.2024.05.017.

## Additional Primary DME / FARETINA-DME Materials

### Singh 2024: Initial Anti-VEGF Dosing in DME

- Source files: `downloads/singh_2024_initial_dosing_dme/`; extracted text in `text/singh_2024_initial_dosing_dme.txt`; PMC full text https://pmc.ncbi.nlm.nih.gov/articles/PMC11684133/.
- Study design: retrospective database study.
- Data source: AAO IRIS Registry.
- Index period: January 1, 2015 to December 31, 2020.
- Data cutoff: December 31, 2021.
- Index date: earliest documented anti-VEGF injection date during the index period.
- Follow-up: time from index date to data cutoff.
- Inclusion:
  - Age >=18 years.
  - Documented DME within 2 months of index.
  - At least 12 months of data before index.
  - >=1 VA recording at or within 60 days before index.
  - Anti-VEGF injections during index period.
  - No anti-VEGF injections in the prior 12 months.
- Exclusions:
  - Intravitreal steroids within 12 months before index.
  - Brolucizumab at any point in the study period.
  - <100 days follow-up.
- Cohort attrition from full text:
  - 2,017,445 eyes with anti-VEGF injections in index period and no anti-VEGF in prior 12 months.
  - 1,046,296 eyes with >=12 months pre-index data.
  - 257,514 eyes with DME documentation within 2 months before/on index.
  - 233,702 eyes with >=1 VA record within 60 days before index.
  - 217,696 final included eyes after brolucizumab and follow-up exclusions.
  - Initial-dose cohort: 77,769 eyes; non-initial-dose cohort: 139,927 eyes.
- Initial-dose definition:
  - Three anti-VEGF injections of the same agent within 100 days of index.
  - Non-initial cohort: eligible eyes not meeting that definition.
- Treatment outcomes:
  - Injection frequency and number by follow-up year.
  - Intervals between injections by follow-up year.
  - Treatment discontinuation: >365 days of contribution to IRIS Registry without an additional anti-VEGF injection after last recorded injection.
  - Reinitiation: anti-VEGF treatment record >=1 year after the last injection.
  - Switch: different anti-VEGF agent record >=1 year after the last injection; the statistical section handled switches <1 year separately.
- VA operationalization:
  - VA and change from baseline VA evaluated annually for up to 6 years.
  - Used best VA in approximate ETDRS letters.
  - Converted from Snellen using `ETDRS = 85 + 50 x log(Snellen fraction)` or from logMAR values.
- Statistical approach:
  - Chi-square tests with Yates correction for categorical variables.
  - Welch t tests for continuous variables.
  - Cox proportional hazards models for time to discontinuation, reinitiation, or switch.
  - GEE-adjusted models for characteristics associated with receiving initial doses; patient-eye analysis grouped at patient level to account for nonindependence of eyes.
  - Linear regression / generalized linear model with Gaussian family and identity link for VA change.
  - Adjusted models included age, race/ethnicity, insurance, baseline VA, history of glaucoma/cataracts, initial anti-VEGF agent, and switches where appropriate.
- Supplements:
  - PMC lists Supplementary Material 1, 2, and 3 at:
    - `https://pmc.ncbi.nlm.nih.gov/articles/instance/11684133/bin/12886_2024_3797_MOESM1_ESM.docx`
    - `https://pmc.ncbi.nlm.nih.gov/articles/instance/11684133/bin/12886_2024_3797_MOESM2_ESM.docx`
    - `https://pmc.ncbi.nlm.nih.gov/articles/instance/11684133/bin/12886_2024_3797_MOESM3_ESM.docx`
  - Local note: attempted downloads returned NCBI "Preparing to download" stubs; these are preserved in `downloads/singh_2024_initial_dosing_dme/`.

### Borkar 2025: Early Faricimab Outcomes in DME

- Source files: `downloads/borkar_2025_early_faricimab_dme/`; PubMed XML only; relevant conference details in `asrs_2023_borkar_early_faricimab_presentation` and `arvo_2024_borkar_faricimab_poster`.
- Study design: FARETINA-DME retrospective study.
- Data source: US IRIS Registry.
- Cohort: patients with DME initiating faricimab from February 2022 to June 2023.
- Cohorts:
  - Previously anti-VEGF-treated: 4,514 patients / 6,204 eyes.
  - Treatment-naive: 691 patients / 851 eyes.
- Outcomes in abstract:
  - VA at index and faricimab injection 4.
  - CST at index and follow-up/injection 4.
  - Treatment-naive and previously treated groups analyzed separately.
- Operational definitions from related FARETINA-DME conference files:
  - Index date = first faricimab injection.
  - Treatment-naive = no evidence of anti-VEGF injections up to 12 months before faricimab initiation.
  - Patients with <12 months prior medical data, unknown laterality, or missing demographics excluded.
  - >=4 faricimab injections required for injection interval / BDVA analyses in early presentation.

### Singh 2025: One-Year Real-World Outcomes and Durability With Faricimab in DME

- Source files: `downloads/singh_2025_one_year_faricimab_dme/`; PubMed XML only; relevant operational details in 2024-2025 FARETINA-DME PDFs.
- Study design: FARETINA-DME retrospective study.
- Data source: IRIS Registry.
- Cohort: patients diagnosed with DME initiating faricimab from February 2022 to March 2023.
- Cohorts:
  - Treatment-naive: 786 patients / 970 eyes.
  - Previously anti-VEGF-treated: 4,862 patients / 6,728 eyes.
- Outcomes:
  - VA at injection 7.
  - CST change at injection 7.
  - Proportion achieving/maintaining CST <=280 um at injection 7.
  - Dosing frequency in first versus second 6 months.
- Operational definitions from FARETINA-DME presentations:
  - Index date = first faricimab injection.
  - Treatment-naive = no anti-VEGF injections in prior 12 months.
  - Real-world VA records included corrected and uncorrected measures and pinhole measurements.
  - VA assessments captured around a -6 to +7 day window around injection visits.
  - CST subgroup required baseline CST 0-30 days before index, >=2 CST measures in <=180 days before index, and >=2 CST measures in 180 days post-index; CST measurements 1-14 days after injection excluded.

### FARETINA-DME Conference Materials: Reusable Operational Definitions

Applicable source files:

- `downloads/asrs_2023_borkar_early_faricimab_presentation/asrs_2023_borkar_early_faricimab_presentation_1.pdf`
- `downloads/arvo_2024_borkar_faricimab_poster/`
- `downloads/asrs_2024_leng_12_month_faricimab_presentation/asrs_2024_leng_12_month_faricimab_presentation_1.pdf`
- `downloads/hawaiian_eye_2025_borkar_faricimab_presentation/hawaiian_eye_2025_borkar_faricimab_presentation_1.pdf`
- `downloads/macula_society_2026_borkar_two_year_faricimab_presentation/macula_society_2026_borkar_two_year_faricimab_presentation_1.pdf`

Common definitions extracted:

- Study design: noninterventional, retrospective, observational real-world study using IRIS Registry data; after March 2023, FARETINA-DME transitioned to IRIS Registry data ingested directly by Verana Health.
- Index date: first faricimab injection during the study period.
- Laterality: documented DME and known laterality required.
- Treatment-naive definition: no evidence of anti-VEGF injections up to 12 months before faricimab initiation.
- Prior anti-VEGF treatment: lookback of available medical record data >=12 months before faricimab initiation; medical data lookback includes records for anti-VEGF samples.
- Common exclusions: <12 months prior medical data, unknown laterality, missing demographics; 12-month analyses exclude documentation of nAMD on index date for DME-only cohorts.
- VA:
  - Real-world VA records include corrected, uncorrected, and pinhole measurements.
  - VA analyses require >=2 VA measures on/after first faricimab injection.
  - VA assessments around injection visits use a -6 to +7 day window.
  - Approximate ETDRS letter score is used in 24-month presentation figures.
- CST:
  - Baseline CST window: 0-30 days before index.
  - Serial CST requirement: >=2 CST measurements in <=180 days before index and >=2 CST measurements in 180 days post-index.
  - CST measurements 1-14 days after injection excluded.
  - CST outcomes include mean CST change, CST <=280 um disease-control threshold, and >=10% CST reduction versus baseline.
  - CST availability is limited; ARVO 2024 reported approximately 16% of faricimab patient-eyes had CST available, and 2025 updates reported ~17.8%.
- Injection interval/durability:
  - Early analyses included eyes with >=4 faricimab injections for interval/BDVA analyses.
  - Extended faricimab interval defined as injection >6 weeks after the previous faricimab injection.
  - Treatment interval bands in Retina Society 2023: <8 weeks = 0-7 weeks; >=8 to <12 weeks = 8-11 weeks; >=12 weeks = >11 weeks.
- Safety / AE ICD-10 code definitions in FARETINA materials:
  - Endophthalmitis: H44.0, H44.19, H20.05.
  - Iridocyclitis and iritis: H20.00, H20.01, H20.02, H20.1, H20.9.
  - Retinal vasculitis: H3506, H35061, H35062, H35063, H35069.
  - Uveitis: H30.0, H30.1, H30.2, H30.8, H30.9, H44.1.
  - Vitritis: H43.89.
  - AE definitions required first diagnosis after faricimab initiation with no diagnosis in the prior 12 months.
  - Presentations caution that AEs derived from ICD-10 codes may not accurately reflect real-world incidence/prevalence.

## Long-Term Anti-VEGF Conference Precursors

### ASRS 2022 Leng: 6-Year Anti-VEGF Treatment Patterns

- Source: `text/asrs_2022_leng_long_term_patterns_presentation.txt`.
- Data source: deidentified IRIS Registry EMR data.
- Index period: January 1, 2015 to December 31, 2019.
- Cohort: patients with DME initiating anti-VEGF IVT.
- Inclusion/exclusion:
  - All eyes with anti-VEGF injections in index period and no anti-VEGF injections 12 months pre-index.
  - No IVT steroid use in 12-month pre-index.
  - >=12 months of data pre-index.
  - Documentation of DME within 2 months pre-index.
  - Age >=18 and known sex at index.
  - >=1 BVA recording at or within 60 days pre-index.
- Outcomes:
  - Anti-VEGF agent type and utilization.
  - Switches: >=3 consecutive injections of a different anti-VEGF agent from original agent.
  - Discontinuations: no anti-VEGF IVT for >=12 months.
  - Reinitiation after discontinuation.
  - Stratification by baseline BVA and initial anti-VEGF agent; on-label agents were ranibizumab and aflibercept, off-label agent was bevacizumab.
- Limitation explicitly noted: unable to differentiate treatment discontinuation from loss to follow-up.

### ASRS 2022 Kuo and ARVO 2022 Kim Posters

- Source files:
  - `text/asrs_2022_kuo_va_frequency_poster.txt`
  - `text/arvo_2022_kim_discontinuation_switching_poster.txt`
- These appear to use the same underlying long-term DME anti-VEGF cohort as ASRS 2022 Leng / Kuo 2024.
- Specific operational details are most clearly exposed in the ASRS 2022 Leng presentation and should be reused for comparison:
  - Treatment-naive by 12-month anti-VEGF lookback.
  - DME documentation within 2 months pre-index.
  - BVA within 60 days pre-index.
  - Switch and discontinuation definitions above.

## Linked Claims + IRIS DME Analyses

### ARVO 2026 Cooper: Linked CVS Claims + IRIS EHR

- Source: `text/arvo_2026_cooper_linked_claims_iris_poster.txt`.
- Study design: retrospective observational study using linked US administrative claims and IRIS Registry EHR data.
- Data sources:
  - CVS Health claims.
  - AAO IRIS Registry EHR.
- Cohort definition:
  - >=2 medical claims for DME between January 2021 and June 2025.
  - >=1 faricimab injection between February 2022 and June 2024.
  - Index date: first faricimab injection.
  - Continuous medical/pharmacy insurance coverage >=12 months pre-index and post-index.
  - Linked IRIS data required for VA/CST clinical outcomes.
- Follow-up:
  - 12 months baseline.
  - 12 months follow-up.
- Cohort grouping:
  - Remained on faricimab during follow-up.
  - Switched to anti-VEGF therapy during follow-up.
- Outcomes:
  - Baseline characteristics and treatment patterns during 12 months follow-up.
  - VA and CST change from baseline to 12 months among patients with available data at both time points.
  - Faricimab and anti-VEGF injections during follow-up.
  - HCRU and costs: retina specialist visits, faricimab/anti-VEGF costs, DME-related costs, and all-cause medical/pharmacy costs.
- Statistical approach:
  - One-way ANOVA with a single fixed-effect factor.
  - No formal adjustment for multiple comparisons across outcomes/subgroups.
  - Baseline HCRU/costs reflect the 12 months before index.

### ISPOR 2026 Linked Claims + IRIS Abstract

- Source: `downloads/ispor_2026_faricimab_claims_iris_abstract/`.
- Study design: abstract-level linked clinical/economic analysis.
- Data source: administrative claims plus IRIS Registry data.
- Content overlaps with ARVO 2026 Cooper; the poster contains more operational detail and should be treated as the richer source for definitions.

## Secondary / Subgroup IRIS Items

### Gong 2021: PDR Treatment Trends With DME Status

- Source files: `downloads/gong_2021_pdr_dme_status/`; PMC HTML saved.
- Study design: retrospective cohort analysis.
- Data source: IRIS Registry.
- Cohort: newly diagnosed proliferative diabetic retinopathy.
- Cohort size: 141,317 patients.
- Role of DME: DME status variable/subgroup, not a primary DME cohort.
- Diagnostic definitions:
  - PDR codes explicitly reported: ICD-10 `E08.35`, `E09.35`, `E10.35`, `E11.35`, `E13.35`; ICD-9 `362.02`.
  - DME was captured as a status variable, but the exact DME code list was not exposed in the accessible abstract/metadata text.
- Outcomes:
  - Treatment patterns over time: intravitreal injection only, PRP only, both, and observation.
  - Intravitreal drug data and DME status.
- Statistical approach:
  - Tukey and chi-square tests for comparisons.
  - Mann-Kendall tests and Theil-Sen slopes for temporal trends.
- Missing: intravitreal injection/PRP CPT or procedure codes, exact DME code list, and VA outcome definitions were not exposed in the accessible source text.

### Ambrosino 2025: Sickle Cell Trait/Disease and Diabetic Retinopathy Risk

- Source files: `downloads/ambrosino_2025_sickle_cell_dr_dme_outcome/`; PMC HTML saved.
- Study design: retrospective IRIS Registry analysis.
- Data source: IRIS Registry.
- Cohort: patients with documented type 1 or type 2 diabetes between 2013 and 2021, stratified by sickle cell disease/trait status; race-stratified random sample among patients without sickle cell diagnosis.
- Role of DME: DME was an outcome/diabetic ocular complication, not the primary cohort-defining disease.
- Extracted data:
  - Demographics, insurance, census region, smoking status.
  - Diabetic ocular complications: PDR and DME.
  - Ocular procedures: focal laser, PRP, vitrectomy, intravitreal injection, nonretinal laser procedures, membrane peel.
  - VA closest to index date (initial diabetes diagnosis) per eye, using categories: >=20/40, 20/40-20/60, <20/60, count fingers, hand motion, light perception, no light perception.
- Statistical approach:
  - Chi-square tests for categorical outcomes.
  - Multivariate logistic regression adjusted for demographic factors, insurance, census region, and smoking status.
  - T tests for logMAR VA means.
  - Sensitivity analysis with propensity score weighting truncated at 99th percentile.

### Zhang 2026: Endophthalmitis After IVT Biologic Drugs

- Source files: `downloads/zhang_2026_endophthalmitis_ivt_dme_dr_subgroup/`; PubMed XML and saved text available.
- Full text: https://link.springer.com/article/10.1007/s40123-026-01371-8.
- Study design: retrospective registry analysis.
- Data source: IRIS Registry.
- Cohort: subjects receiving commercially available IVT anti-VEGF and anti-complement biologic drugs.
- Data cutoff: December 31, 2024.
- Registry period reported in results: August 8, 2013 to December 31, 2024.
- Role of DME: DME/DR was an indication subgroup, not a primary DME cohort.
- Cohort scale in PubMed abstract:
  - 1,998,399 individuals received at least one IVT injection.
  - 13,074 subjects / 13,317 eyes diagnosed with infectious endophthalmitis.
- Outcomes:
  - Incidence of infectious endophthalmitis per IVT injection and per subject.
  - BCVA before the last biologic injection before endophthalmitis, worst BCVA after diagnosis, and final BCVA after diagnosis.
  - Legal blindness before/after event; legal blindness defined as <=35 letters or <=20/200.
  - 0-letter VA was interpreted as count fingers/hand motion or worse; light perception/no light perception is not recorded in IRIS, per the article.
  - Evisceration/enucleation after endophthalmitis.
  - Disease subgroup incidence, including DME/DR.
- Detailed code definitions:
  - IVT biologic exposure was identified using HCPCS J-codes; the exact biologic J-code list is not shown in the main article text.
  - Infectious endophthalmitis diagnosis codes: ICD-9 `360.00`, `360.01`, `360.03`, `360.19`; ICD-10 `H44.0`, `H44.001`, `H44.002`, `H44.003`, `H44.19`.
  - Enucleation/evisceration codes: ICD-9 `65101`, `65103`, `65105`; ICD-10 `Z90.01`.
  - Disease-stratified analysis required a single disease category at first IVT injection; eyes with overlapping disease codes, such as both nAMD and DME, were excluded from disease-stratified analysis.
  - DME/DR and other disease-code lists are too long to reproduce in this comparison; obtain them from Supplementary file 1 PDF, Table S1: https://static-content.springer.com/esm/art%3A10.1007%2Fs40123-026-01371-8/MediaObjects/40123_2026_1371_MOESM1_ESM.pdf.
- Statistical approach: chi-square pairwise comparisons with Holm-adjusted p-values.

## Excluded False Positive

### Ko 2025: Socioeconomic Disparities in Intravitreal Injection Use and Agent Selection

- Source files: `downloads/socioeconomic_2025_ivi_agent_selection_dme_subgroup/`.
- Reason excluded: PubMed search hit included DME, but the study used the NIH All of Us database, not the IRIS Registry.
- Useful operational details if comparing non-IRIS methods:
  - Disease identification: ICD-9/ICD-10-CM diagnosis codes.
  - IVI outcome: CPT-4 codes.
  - Anti-VEGF type: RxNorm codes.
