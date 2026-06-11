# Detailed Methods Extraction: IRIS Registry Wet AMD / nAMD Studies

Date updated: 2026-06-03.

This file expands `methods_comparison.md` with operational definitions, code references, and supplement pointers. Full text was reviewed where available in `extracted_text/`; otherwise extraction is based on saved PubMed XML/abstracts, publisher landing pages, and public posters/presentations.

## Core Wet AMD / nAMD Items

### Rao 2018 - Real-world vision by single anti-VEGF drug type

- Source detail: abstract/metadata only; PubMed saved at `sources/rao_2018_real_world_vision_single_antivegf_pubmed.xml`.
- Design/data source: retrospective, nonrandomized comparative IRIS Registry study.
- Cohort: IRIS Registry nAMD patients treated with bevacizumab, ranibizumab, or aflibercept monotherapy for 1 year during 2013-2016.
- Exposure/index: anti-VEGF drug type; patients divided into monotherapy groups.
- Outcomes: logMAR VA at 1 year; mean logMAR VA change from baseline to 1 year; >=3-line VA improvement/loss.
- Covariates/statistics: stepwise multivariable ANCOVA; abstract reports adjustment for age, baseline VA, diabetes, posterior vitreous detachment, number of injections, race, and insurance.
- Code/appendix detail: no diagnostic/procedure code table found in accessible material; use DOI `10.1016/j.ophtha.2017.10.010` / PubMed `29146306` for publisher version.

### Ho 2020 - Baseline VA at wet AMD diagnosis

- Source detail: abstract/metadata only; PubMed saved at `sources/ho_2020_baseline_va_wet_amd_pubmed.xml`.
- Design/data source: retrospective IRIS Registry study.
- Cohort: patients diagnosed with nAMD in one or both eyes between January 2013 and June 2017.
- Inclusion/exposure: study eyes received at least 2 anti-VEGF injections less than 45 days apart.
- Outcomes: percentage of eyes with 20/40 VA or better at diagnosis; association of VA at diagnosis with longer-term VA outcomes; abstract reports 1- and 2-year VA framing.
- Code/appendix detail: no code table found in accessible material; use DOI `10.3928/23258160-20201104-05` / PubMed `33231696`.

### MacCumber 2020 - Brolucizumab initiation profiles

- Source detail: full poster PDF downloaded and extracted at `downloads/maccumber_2020_retina_society_brolucizumab_profiles.pdf` and `extracted_text/maccumber_2020_retina_society_brolucizumab_profiles.txt`.
- Design/data source: retrospective IRIS Registry profile of early brolucizumab initiators.
- Inclusion: >=1 brolucizumab J-code or EHR text mention between October 8, 2019 and March 31, 2020; age >=18 on index date; wet AMD diagnosis any time from January 1, 2013 to index.
- Exclusion: brolucizumab in a clinical trial; missing specific eye treated on index date.
- Index: earliest brolucizumab injection.
- Outcomes: baseline patient and eye characteristics; prior anti-VEGF treatment; 12-month pre-index anti-VEGF intervals; early post-index brolucizumab injections/follow-up.
- Operational details: poster reports prior-anti-VEGF interval as last interval and average of last 2/3 intervals in days/weeks.

### Khurana 2020 poster / Khurana 2023 manuscript - LTFU in nAMD

- Source detail: poster PDF added at `downloads/khurana_2020_retina_society_ltfu_namd_poster.pdf`; manuscript abstract saved at `sources/khurana_2023_ltfu_namd_pubmed.xml`.
- Poster cohort: nAMD diagnosed January 1, 2013-December 31, 2015 and treated with anti-VEGF January 1, 2013-December 31, 2018.
- Poster exclusions: PDR, DME, RVO, myopic degeneration, idiopathic CNV.
- Poster outcome: LTFU defined as a visit >12 months from last intravitreal injection.
- Manuscript cohort: 156,327 treatment-naive nAMD patients treated with anti-VEGF from 2013-2015 and followed through 2019.
- Manuscript outcomes: LTFU defined as no follow-up within 12 months from last intravitreal injection; nonpersistence defined as no follow-up within 6 months from last intravitreal injection.
- Covariates/statistics: multivariable logistic regression; poster reports baseline demographic/clinical factors including age, sex, race/ethnicity, eye involvement, baseline vision, region, insurance, and provider ZIP-code household income.
- Code/appendix detail: no formal ICD/CPT table found in accessible poster/abstract; use DOI `10.1016/j.ophtha.2023.02.021` / PubMed `36858288`.

### Leng 2021 / Wykoff 2024 - Long-term anti-VEGF outcomes up to 6 years

- Source detail: presentation PDF at `downloads/leng_2021_asrs_long_term_antivegf_namd_presentation.pdf`; full manuscript text at `extracted_text/wykoff_2024_six_year_antivegf_namd_fulltext.txt`.
- Design/data source: retrospective, noncomparative/noninterventional IRIS Registry cohort.
- Cohort: patients with nAMD treated with intravitreal anti-VEGF during July 1, 2013-June 30, 2018.
- Index: first documented anti-VEGF injection in IRIS during index period.
- Inclusion: age >=50 at index; first nAMD diagnosis within 180 days before or on first anti-VEGF injection; no pre-index anti-VEGF in IRIS; practice data contribution >=6 months before index.
- VA cohort: 3 intravitreal anti-VEGF doses within 180 days of starting treatment; >=2 years follow-up; baseline VA within 180 days pre-index; >=1 VA after year 1 +/-60 days.
- Exclusion: unknown laterality of nAMD diagnosis or anti-VEGF treatment.
- VA measurement: annual intervals up to 6 years +/-60 days; Snellen converted to approximate ETDRS letters using ETDRS = 85 + 50 x log(Snellen fraction); logMAR also used for statistical analyses.
- Treatment gap: >18 weeks and <=52 weeks without anti-VEGF injection.
- Discontinuation: >52 weeks without anti-VEGF injection.
- Switching: at least 3 consecutive injections of a different anti-VEGF agent from original/prior agent.
- Vision loss definitions: considerable vision loss = >=10 ETDRS-letter loss from baseline; sustained poor vision = Snellen VA 20/200 or worse at 2 readings at least 3 months apart with no subsequent improvement beyond 20/100; eyes with baseline VA 20/200 or worse excluded from sustained-poor-vision analysis.
- Statistics: descriptive summaries; t, chi-square, Wilcoxon tests; adjusted linear regression for year-1 VA change; Kaplan-Meier and Cox proportional hazards for time to CVL/SPV; variables included age, sex, race, payer, physician specialty, glaucoma, cataract.
- Code/appendix detail: nAMD ICD-9/10 codes are in Table S1, cited by the article as available at `www.ophthalmologyscience.org`; local full text points to this but the code table was not present in extracted text.

### Khanani 2022 - Brolucizumab safety, IRIS + Komodo

- Source detail: full PMC text saved at `extracted_text/khanani_2022_brolucizumab_safety_fulltext.txt`; supplement URL is `https://pmc.ncbi.nlm.nih.gov/articles/instance/8613703/bin/jamaophthalmol-e214585-s001.pdf`.
- Design/data source: retrospective cohort in IRIS Registry and Komodo Healthcare Map.
- Cohort/index period: adult nAMD patients initiating and receiving >=1 brolucizumab injection; IRIS index period October 8, 2019-June 5, 2020; Komodo October 8, 2019-April 30, 2020.
- Index: earliest brolucizumab injection, identified by procedure code or EHR note.
- Pre/post periods: 36-month pre-index period; up to 180 days post-index.
- Exclusion: prior brolucizumab before index period.
- Outcomes: any IOI and/or retinal vascular occlusion; retinal vasculitis and/or retinal vascular occlusion; risk factors. Outcomes presented at patient-eye level.
- Event definition: ICD-10-CM diagnostic codes; infectious IOI/endophthalmitis excluded from the IOI construct. Incident events included no same event in pre-index, different subevent code pre/post, same subevent <=2 times in 12 months pre-index, or same event with moderate/severe VA drop (>=3 lines) after event.
- Follow-up: IRIS follow-up defined as last recorded visit or last day that the index-injection practice contributed IRIS data, whichever later; Komodo follow-up from claims.
- Statistics: descriptive statistics; GEE multivariable models for inter-eye correlation; candidate baseline characteristics narrowed by univariate significance and clinical relevance; age/sex forced in base models; ORs reported.
- Code/appendix detail: eTable 1 includes inclusion/exclusion criteria; eTable 2 includes adverse-event definitions; eTables 3-4 include baseline characteristics. Supplement was identified but direct binary download returned NCBI “Preparing to download” HTML in this environment; use the PMC supplement URL above.

### Hunt 2022 - Environmental factors and AMD

- Source detail: full PMC text saved at `extracted_text/hunt_2022_environmental_factors_amd_fulltext.txt`.
- Scope: adjacent to wet AMD; broad AMD risk-factor analysis includes exudative and active exudative AMD categories.
- Design/data source: IRIS Registry linked to environmental variables by ZIP/geography.
- Cohort: IRIS Registry patients age >=55; classified into no AMD, nonexudative AMD, inactive exudative AMD, or active exudative AMD.
- Operational definitions: AMD phenotype based on ICD-coded disease categories; environmental factors geocoded to patient location.
- Outcomes: odds of any AMD, any exudative AMD, active exudative AMD.
- Statistics: mixed-effects logistic regression with ZIP-code-level random effects.
- Code/appendix detail: full extracted text contains high-level disease-category definitions but no compact diagnostic code table; use DOI `10.1016/j.xops.2022.100195` / PMC `PMC9754968`.

### ASRS 2022 / Gong 2024 - Conversion from nonexudative/unilateral exudative AMD

- Source detail: public ASRS abstract PDF at `downloads/asrs_2022_conversion_rates_poster.pdf`; manuscript abstract saved at `sources/gong_2024_fellow_eye_conversion_pubmed.xml`.
- ASRS cohort: IRIS Registry 2016-2019; 2,664,789 patients with dry AMD in at least one eye.
- ASRS outcome: conversion time from dry/nonexudative to wet/exudative AMD.
- ASRS covariates: age, sex, race, geographic region, smoking status, dry AMD stage, wet AMD stage, and fellow-eye disease status.
- ASRS statistics: descriptive statistics and Cox proportional hazards HRs.
- Manuscript cohort: unilateral exudative AMD patients, 2016-2019.
- Manuscript methods: patient and disease characteristics including initial AMD stage; Cox proportional hazards and logistic regression.
- Code/appendix detail: no diagnostic-code table found in accessible abstract/poster; use DOI `10.3928/23258160-20240125-01` / PubMed `38319061`.

### MacCumber 2023 - Anti-VEGF agents for wet AMD

- Source detail: abstract/metadata only; PubMed saved at `sources/maccumber_2023_cjo_antivegf_wet_amd_pubmed.xml`.
- Design/data source: retrospective IRIS Registry study.
- Cohort: wet AMD patients age >=50 with >=1 anti-VEGF injection and >=1.5 years follow-up.
- Follow-up strata: >=1.5 years, >=2.5 years, >=3.5 years.
- Outcomes: anti-VEGF treatment patterns; injection interval <8 weeks at end of years 1/2/3; VA change in ETDRS letters; discontinuation.
- Discontinuation definition: no injection for >6 months.
- Code/appendix detail: no full methods/code appendix found in accessible material; use DOI `10.1016/j.jcjo.2021.10.008` / PubMed `34863677`.

### Gallivan 2023 - VIEW 1/2 trial emulation

- Source detail: full PMC text saved at `extracted_text/gallivan_2023_view_emulation_fulltext.txt`.
- Design/data source: retrospective, noninterventional IRIS Registry cohort designed to emulate VIEW RCT eligibility, regimens, and endpoint.
- Cohort: anti-VEGF injection of aflibercept or ranibizumab between January 1, 2013 and December 31, 2018.
- Index: first injection date.
- Inclusion: anti-VEGF injection with known laterality; ICD nAMD diagnosis in same eye within 6 months before first injection; age >=50; nonmissing gender/race; baseline VA 20/40 to 20/320 within 30 days before index.
- Injection definition: concurrent CPT 67028 plus HCPCS J0178, J2778, J3490, or J3590 on same date.
- Treatment arms: monthly aflibercept 2Q4, aflibercept 2Q8 after 3 initial monthly doses, or monthly ranibizumab RQ4; treatment windows defined in Table 3 of article.
- VA endpoint: best documented Snellen VA converted to logMAR and ETDRS-equivalent letters; 1-year VA within 365 +/-14 days; maintaining vision = <15-letter / <3-line loss from baseline.
- Missing endpoint handling: complete case, multiple imputation unadjusted, and multiple imputation adjusted by transportability weight.
- Codes in article Table A: nAMD ICD-9 362.52; ICD-10 H35.32, H35.3210, H35.3220, H35.3230, H35.3290, H35.3211, H35.3221, H35.3231, H35.3291, H35.3212, H35.3222, H35.3232, H35.3292, H35.3213, H35.3223, H35.3233, H35.3293.
- Other code examples: prior nAMD treatment/surgery CPT 67220, 67221; prior vitrectomy CPT 67107, 67108, 67113, 67036, 67039, 67040, 67041, 67042, 67043; intraocular/periocular surgery CPT 66710, 66730, 66750, 66755, 66756, 66984, 66982, 66170, 66250, 66172, 66183, 66179, 66180, 66184, 66185; DME/DR/RVO/myopic CNV codes are lengthy and visible in local lines 284-296 of `extracted_text/gallivan_2023_view_emulation_fulltext.txt`.
- Appendix/source detail: Table A and attrition Table B are included in the local extracted full text; article also links Supplementary Material 1 and 2 at PMC instance URLs, but direct supplement download was blocked by NCBI’s download-preparation page in this environment.

### Fevrier 2024 - CATT clinical trial emulation

- Source detail: full PMC text saved at `extracted_text/fevrier_2024_catt_emulation_fulltext.txt`.
- Design/data source: retrospective IRIS Registry cohort plus deidentified CATT patient-level clinical trial data.
- Cohort: all treatment-naive nAMD eyes receiving first anti-VEGF injection between October 1, 2015 and December 31, 2019 based on ICD-10 and CPT coding.
- Treatment-naive: no anti-VEGF injections in structured EHR data (CPT/HCPCS) for 1 year before index.
- Index: first injection date.
- PRN regimen definition: clinical encounter with retina specialist every 4-6 weeks for 1 year after index plus >=1 retina-specialist encounter not associated with anti-VEGF injection.
- Drug/regimen restriction: bevacizumab-only or ranibizumab-only for 1 year after index; if both eyes treated, study eye was the eye with earlier index date.
- Eligibility attrition examples: nAMD documentation within 1 year pre-index; age >=50; >=1 year pre-index data; VA 20/25 to 20/320; retina-specialist visits every 4-6 weeks; only bevacizumab/ranibizumab; exclusions for DR/DME, vitreous hemorrhage, RD/macular hole, vitrectomy, intraocular surgery within 2 months, uncontrolled glaucoma (IOP >=25 mmHg on >=2 readings in prior year), prior PDT/anti-VEGF, subfoveal GA ICD code, non-AMD CNV, and other ocular diseases compromising VA.
- VA measurement: best documented Snellen VA for the clinical encounter, converted to approximated ETDRS letters using 85 + 50 x log(Snellen fraction), rounded to nearest letter.
- Matching/weighting: exact matching 1:1 on age, gender, and baseline VA; age within 5 years except >=90 category; VA within 5 letters. IPSW also applied.
- Outcomes: 1-year VA change in approximated ETDRS letters compared with CATT treatment arms.
- Code/appendix detail: exact code lists are not printed in the extracted article; it states cohort was based on ICD-10 and CPT/HCPCS coding. Use PMC `PMC11179401` / DOI `10.1016/j.xops.2024.100524`.

### MacCumber 2023 - Brolucizumab interval extension

- Source detail: abstract/metadata only; PubMed saved at `sources/maccumber_2023_brolucizumab_interval_extension_pubmed.xml`.
- Cohort: adults in US IRIS Registry with nAMD who switched from another anti-VEGF to brolucizumab-only treatment for >=12 months from October 8, 2019-November 26, 2021.
- Index/exposure: first brolucizumab injection; prior injection interval defined as time between last known prior anti-VEGF injection and first/index brolucizumab injection.
- Outcome: extender at 12 months required both >=2-week extension in brolucizumab interval versus pre-switch interval and stable (<10 letters gained/lost) or improved (>=10 letters gained) VA at 12 months versus index.
- Statistics: univariable and multivariable analyses of demographic/clinical factors.
- Code/appendix detail: no full code table found in accessible material; use DOI `10.1016/j.ophtha.2023.03.017` / PubMed `36990322`.

### MacCumber 2023 - 1-year brolucizumab outcomes

- Source detail: abstract/metadata only; PubMed saved at `sources/maccumber_2023_one_year_brolucizumab_pubmed.xml`.
- Cohort: adults with nAMD in US IRIS Registry receiving brolucizumab exclusively for 12 months; 2,308 eyes of 2,079 patients.
- Index: first brolucizumab injection.
- Inclusion/exposure: index injection followed by >=2 additional brolucizumab injections over 12 months without switch to another anti-VEGF agent.
- Outcomes: change in best-recorded VA; for treatment-experienced eyes, difference between brolucizumab interval at 12 months and pre-switch anti-VEGF interval; incident adverse events.
- Interval definitions: pre-switch interval = time between prior anti-VEGF and index brolucizumab injection; brolucizumab interval = time between injection closest to day 365 and preceding injection.
- Code/appendix detail: no full code table found in accessible material; use DOI `10.1016/j.ophtha.2023.04.012` / PubMed `37086857`.

### Rahimy 2023 - GA progression with nAMD fellow eye

- Source detail: full PMC text saved at `extracted_text/rahimy_2023_ga_progression_with_namd_fellow_eye_fulltext.txt`.
- Scope: adjacent to wet AMD; GA-primary study with fellow-eye nAMD and new-onset nAMD outcomes.
- Design/data source: retrospective IRIS Registry analysis over 24 months.
- Cohort: 256,635 GA patients from January 2016-December 2017.
- Grouping: cohort 1 GA:GA; cohort 2 GA:nAMD; each stratified by subfoveal vs nonsubfoveal involvement.
- Exclusions: history of retinal disease other than AMD.
- Sensitivity analysis: retina-specialist-managed patients with imaging record within 30 days of diagnosis.
- Outcomes: VA change, new-onset nAMD, progression from nonsubfoveal to subfoveal GA.
- Operational limitations: based on ICD-10 codes; no image review/reading center; Snellen VA converted to ETDRS letters.
- Code/appendix detail: supplementary data present in local full text but no compact code table extracted; use DOI `10.1016/j.xops.2023.100318` / PMC `PMC10232896`.

### Zarbin 2024 - 2-year brolucizumab safety

- Source detail: Springer full-text page saved at `extracted_text/zarbin_2024_brolucizumab_safety_fulltext.txt`.
- Design/data source: retrospective IRIS Registry study.
- Cohort: 18,312 eyes / 15,998 patients treated with >=1 intravitreal brolucizumab injection between October 8, 2019 and October 7, 2021.
- Index: first brolucizumab injection.
- Follow-up: <=2 years after index; full cohort plus first-year and second-year launch subcohorts.
- Outcomes: adverse event of interest count/percent, time to event from index, number of prior brolucizumab injections before event, VA at/immediately after event and 6 months after event.
- Adverse events: IOI, retinal vasculitis, retinal vascular occlusion, and related ocular AE groupings identified from IRIS data.
- Statistics: outcomes at patient-eye level; relative risk over time stratified by age, sex, prior anti-VEGF status, and launch-year subcohort; Cox proportional hazards adjusted for clustering when both eyes from same patient.
- Code/appendix detail: supplement link not visible in local HTML extraction; DOI `10.1007/s40123-024-00920-3`.

### Leng 2024 - nAMD + GA anti-VEGF treatment presentation

- Source detail: presentation PDF at `downloads/leng_2024_arvo_namd_ga_antivegf_presentation.pdf`.
- Design/data source: retrospective IRIS Registry cohort.
- Cohort: first ICD-10 code for GA between July 1, 2016 and December 31, 2021; any nAMD ICD-10 code in same eye as GA diagnosis.
- Index/follow-up: pre-index and post-index periods; presentation defines baseline VA as nearest to index and within 6 months before index.
- Exclusions: missing age/sex; <12 months post-index data; <6 months pre-index data; >=1 exclusionary glaucoma procedure pre-index.
- Cohorts: GA after nAMD, GA before nAMD, or coincident GA/nAMD diagnosis.
- VA outcome definition: yearly VA; treatment year = 52 +/-8 weeks; VA nearest end of treatment year selected; if equidistant, later measurement selected; if >1 same-day VA, best measurement used; converted ETDRS letters.
- Treatment outcomes: timing of index/non-index injections, discontinuation within <1 year, anti-VEGF injection intervals, index anti-VEGF agent.
- Safety outcomes: adverse events within 120 days of an injection in the treated eye without prior history; diagnosis-code based; IOP elevation defined as >6 mmHg increase from baseline with concurrent reading >=25 mmHg.
- Code/appendix detail: presentation names ICD-10/ICD-10-CM use but does not list exact codes.

### Ali 2025 / Tabano 2026 - FARETINA-AMD faricimab outcomes

- Source detail: ARVO abstract saved at `extracted_text/iovs_2023_faretina_amd_abstract.txt`; PubMed abstracts saved at `sources/ali_2025_faricimab_early_outcomes_pubmed.xml` and `sources/tabano_2026_one_year_faricimab_pubmed.xml`.
- Design/data source: retrospective FARETINA-AMD study using IRIS Registry data.
- 2023 ARVO operational details: faricimab starts identified February-August 2022; rules-based text search using regular-expression keywords identified faricimab use; required >=12 months EHR data before initiation and known laterality; injection interval/BDVA analyses required >=4 faricimab injections; extended interval defined as any interval >6 weeks.
- 2025 manuscript cohort: nAMD patients initiating faricimab February 2022-June 2023.
- 2026 manuscript cohort: nAMD patients initiating faricimab February 2022-March 2023; treatment-naive and previously treated strata.
- Outcomes: BDVA/VA, central subfield thickness (CST), injection number/intervals, CST <=280 micrometers, dosing frequency in first versus second 6 months.
- Code/appendix detail: no diagnostic/procedure/NDC code table found in accessible abstracts; use DOIs `10.3928/23258160-20250304-02` and `10.3928/23258160-20260302-02`.

### Acharya 2025 - Disparities in presentation and anti-VEGF initiation

- Source detail: abstract/metadata only; PubMed saved at `sources/acharya_2025_disparities_antivegf_initiation_pubmed.xml`.
- Cohort: newly diagnosed nAMD patients from October 2016-October 2021 in AAO IRIS Registry.
- Outcomes: presenting VA; anti-VEGF treatment initiation defined as >=1 anti-VEGF injection within 12 months after first presentation with nAMD.
- Statistics: multivariable Poisson regression; covariates in abstract include race, ethnicity, age, region, and presenting VA strata.
- Code/appendix detail: no full diagnostic/procedure code table found in accessible material; use DOI `10.1016/j.ophtha.2025.07.024` / PubMed `40738331`.

### Barikian 2026 - Anti-VEGF exposure and 1-year outcomes

- Source detail: abstract/metadata only; PubMed saved at `sources/barikian_2026_antivegf_exposure_outcomes_pubmed.xml`.
- Cohort: treatment-naive nAMD eyes from patients age >=55 with baseline BCVA >=20/400; nAMD diagnosed January 1, 2013-December 31, 2019.
- Exposure: >=7 versus <7 intravitreal anti-VEGF injections through year 1.
- Outcomes: BCVA change from baseline by treatment exposure; baseline predictors of >=7 injections; magnitude of BCVA change by baseline factors and exposure at year 1.
- Statistics: logistic regression.
- Code/appendix detail: no code table found in accessible material; use DOI `10.1016/j.oret.2025.06.016` / PubMed `40614931`.

## Adjacent / Caveated Items

### Zhang 2026 - Infectious endophthalmitis after biologic injections

- Source detail: Springer full-text page saved at `extracted_text/zhang_2026_endophthalmitis_biologics_fulltext.txt`.
- Scope: adjacent; includes wet AMD/nAMD as one indication subgroup among biologic intravitreal injection patients.
- Cohort: subjects receiving commercially available intravitreal anti-VEGF and anti-complement biologic drugs; as of December 31, 2024, 1,998,399 individuals had >=1 IVT injection and 13,074 subjects / 13,317 eyes had infectious endophthalmitis.
- Drug exposure: brolucizumab, aflibercept 2 mg/8 mg, faricimab, ranibizumab, bevacizumab, anti-complement drugs, and others as commercially available.
- Outcomes: infectious endophthalmitis incidence per IVT injection; cumulative endophthalmitis rate by subject injection count; BCVA before and after event; legal blindness and 0-letter VA; evisceration/enucleation.
- Operational definitions: legally blind defined as <=35 letters or <=20/200; very severe impairment operationalized as 0 letters, practically CF/HM or worse; cumulative incidence reported after 10 and 60 IVT injections.
- Limitations/source detail: biologic agents identifiable through J-codes; procedural details, sterility protocols, microbial culture results, and some medication details unavailable in EHR. Supplementary file noted in local full text but direct PDF not retrieved.

### Ashourizadeh 2026 - Cataract surgery and conversion from dry AMD to nAMD

- Source detail: Research Square page saved at `extracted_text/ashourizadeh_2026_cataract_conversion_preprint.txt`.
- Scope: adjacent; dry AMD cohort with nAMD conversion outcome.
- Design/data source: retrospective time-to-event IRIS Registry study.
- Cohort: age >=55 with early/intermediate dry AMD and phakic status; no prior nAMD or anti-VEGF before cohort entry.
- Exposure: cataract surgery as time-varying exposure.
- Outcome: conversion to nAMD over 7 years.
- Statistics: propensity score matching and Cox proportional hazards regression.
- Code/appendix detail: no extracted diagnostic/procedure code table from Research Square page; use DOI `10.21203/rs.3.rs-5505014/v2`.

## Reusable Design Pattern With Operational Detail

For a new IRIS Registry wet AMD/nAMD study, the most reproducible pattern is:

- Define nAMD/wet AMD by laterality-specific ICD diagnosis and tie it to same-eye anti-VEGF treatment. Gallivan 2023 provides explicit nAMD ICD examples: ICD-9 362.52 and ICD-10 H35.32/H35.3210/H35.3220/H35.3230/H35.3290 plus activity/stage variants H35.3211-3213, H35.3221-3223, H35.3231-3233, H35.3291-3293.
- Define injections using structured procedure/drug evidence where possible. Gallivan 2023 required CPT 67028 plus same-day HCPCS J0178, J2778, J3490, or J3590 for aflibercept/ranibizumab-type anti-VEGF exposure; faricimab early work also used rules-based EHR text search to capture a newly launched drug.
- Use a clear index date. Common choices: first anti-VEGF injection, first drug-specific injection, first nAMD presentation, or dry AMD cohort entry for conversion studies.
- Require lookback to reduce prevalent-treatment bias. Examples: Wykoff required >=6 months practice data pre-index; Fevrier required >=1 year pre-index anti-VEGF-free data; FARETINA required >=12 months EHR data before faricimab initiation.
- Use specific VA windows and conversion rules. Wykoff used baseline VA within 180 days pre-index and annual VA +/-60 days; Gallivan used 1-year VA at day 365 +/-14 days; Fevrier used best documented Snellen VA for the encounter converted to ETDRS letters by 85 + 50 x log(Snellen fraction).
- Define treatment adequacy/burden up front. Examples: Barikian uses >=7 injections in year 1; Wykoff requires 3 injections within 180 days for VA cohort and defines gaps as >18 to <=52 weeks and discontinuation as >52 weeks; MacCumber 2023 CJO defines discontinuation as no injection for >6 months.
- Account for two-eye correlation. Khanani used GEE; Zarbin used Cox models adjusted for clustering when both eyes from the same patient.
- Use time-to-event methods for conversion, discontinuation, and vision-loss endpoints. Examples: Gong/ASRS conversion uses Cox PH; Wykoff uses Kaplan-Meier/Cox for >=10-letter loss and sustained poor vision.

## Appendix / Long Code List Pointers

- VIEW emulation code list: local `extracted_text/gallivan_2023_view_emulation_fulltext.txt`, lines around Table A, includes nAMD ICD-9/10 and exclusion-code examples. Use the article at `https://pmc.ncbi.nlm.nih.gov/articles/PMC10748734/` for formatted table.
- Brolucizumab safety AE code definitions: Khanani 2022 supplement eTable 2 at `https://pmc.ncbi.nlm.nih.gov/articles/instance/8613703/bin/jamaophthalmol-e214585-s001.pdf`; local full text identifies eTable contents, but direct PDF retrieval returned NCBI download-preparation HTML here.
- Wykoff 2024 nAMD diagnosis codes: Table S1 cited as available at `www.ophthalmologyscience.org`; local extracted article notes this but did not include the table.
- Faricimab FARETINA operational capture: ARVO abstract at `extracted_text/iovs_2023_faretina_amd_abstract.txt` states faricimab was captured using rules-based text search with regular-expression keywords; no public keyword/NDC table found.
