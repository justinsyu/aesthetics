import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOWNLOADS = ROOT / "downloads"
TEXT = ROOT / "extracted_text"
RETRIEVAL_DATE = "2026-06-03"


def d(name):
    return str((DOWNLOADS / name).resolve())


def t(name):
    return str((TEXT / name).resolve())


rows = [
    {
        "id": "core-01",
        "source_scope": "Core Vestrum website qualifying publication",
        "title": "Increasing Incidence and Prevalence of Common Retinal Diseases in Retina Practices Across the United States",
        "year": "2021",
        "full_text_status": "Full article not publicly downloaded; Healio blocked scripted access. Institutional abstract/methods page and WIO poster evidence reviewed.",
        "source_urls": "https://www.healio.com/ophthalmology/journals/osli/2021-1-52-1/%7B65045259-a9c1-4583-8dd8-a5214905e298%7D/increasing-incidence-and-prevalence-of-common-retinal-diseases-in-retina-practices-across-the-united-states; https://scholars.mssm.edu/en/publications/increasing-incidence-and-prevalence-of-common-retinal-diseases-in-2; https://avenue.live/wio/2020/presentations/rosenblatt-increasing-prevalence-and-changing-incidence-of-common-retinal-diseases-in-retina-practices-across-the-united-states.pdf",
        "local_evidence_files": d("01_MountSinai_Rosenblatt_Incidence_Prevalence_Common_Retinal_Diseases_2021.html") + "; " + t("01_MountSinai_Rosenblatt_Incidence_Prevalence_Common_Retinal_Diseases_2021.txt"),
        "database_version_or_size": "Journal abstract: Vestrum Health Database across 58 retina practices; 3,086,791 eyes examined. Public WIO poster reports a larger evaluated-eye denominator and >300 retina specialists, so final journal abstract denominator should be treated as authoritative unless the full article clarifies denominator handling.",
        "dme_definition_detail": "Eyes with diagnoses of DME in Vestrum Health Database. The WIO poster says inclusion used diagnosis codes for disease categories, but it does not publish the actual DME code list.",
        "diagnostic_codes_reported": "No. No public ICD/code list found in accessible journal abstract, institutional pages, Vestrum media page, or WIO poster.",
        "treatment_definition_detail": "Not applicable; epidemiology/incidence-prevalence study rather than a treatment-outcomes cohort.",
        "procedure_drug_codes_reported_or_location": "Not applicable; no treatment/procedure/drug code definitions reported.",
        "index_date_or_time_origin": "Not reported in accessible abstract-level source; disease incidence/prevalence counted during 2014-2019.",
        "follow_up_and_attrition_rules": "Study period January 2014-December 2019. Attrition/follow-up rules not available in accessible abstract-level source.",
        "inclusion_criteria": "Eyes with diagnoses of wet AMD, dry AMD, DME, DR without DME, BRVO, or CRVO in Vestrum retina practices during the study period.",
        "exclusion_criteria": "Not available in accessible abstract-level source.",
        "unit_and_bilateral_handling": "Eye-level counts; bilateral handling not available in accessible abstract-level source.",
        "outcome_operational_definitions": "Incidence and prevalence by retinal-disease diagnosis category. Accessible sources do not provide formulas for annual incidence/prevalence denominators beyond eyes examined and disease-category counts.",
        "va_method": "Not central to this accessible epidemiology extraction.",
        "baseline_va_strata": "Not applicable in accessible source.",
        "treatment_intensity_definition": "Not applicable.",
        "statistical_methods": "Incidence/prevalence estimation; detailed statistical testing not available from accessible source.",
        "appendix_or_supplement_location": "No public appendix/code list found. WIO poster available at https://avenue.live/wio/2020/presentations/rosenblatt-increasing-prevalence-and-changing-incidence-of-common-retinal-diseases-in-retina-practices-across-the-united-states.pdf.",
        "limitations_relevant_to_methods": "DME operational definition is diagnosis-based but code list is not public. Accessible source is abstract-level, limiting method granularity.",
    },
    {
        "id": "core-02",
        "source_scope": "Core Vestrum website qualifying publication",
        "title": "Evaluation of Patients Receiving Intravitreal Anti-VEGF for Diabetic Macular Edema in Clinical Practice in the United States",
        "year": "2020/2021",
        "full_text_status": "Full PDF and PMC full-text HTML reviewed. PMC supplemental link visible, but direct scripted supplement download returned proof-of-work HTML.",
        "source_urls": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9979048/; https://journals.sagepub.com/doi/abs/10.1177/2474126420953067; https://3333112.fs1.hubspotusercontent-na1.net/hubfs/3333112/PitcherD-VESTRUM-DME-JVRD-September-30-2020Evaluation%20of%20Patients%20Receiving%20Intravitreal.pdf",
        "local_evidence_files": d("02_Pitcher_Evaluation_Intravitreal_AntiVEGF_DME_JVRD_2020.pdf") + "; " + d("02_PMC9979048_Pitcher_DME_fulltext.html") + "; " + t("02_Pitcher_Evaluation_Intravitreal_AntiVEGF_DME_JVRD_2020.txt") + "; " + t("02_PMC9979048_Pitcher_DME_fulltext.txt"),
        "database_version_or_size": "Vestrum Health treatment and outcomes database; records from 251 retina specialists at 54 private US clinics; fields included demographics, procedures, diseases diagnosed, medications prescribed, and outcomes such as VA; SQL queries used.",
        "dme_definition_detail": "Eyes newly diagnosed with DME in the Vestrum EMR and administered a first anti-VEGF injection. The article does not define DME with a public ICD/code list.",
        "diagnostic_codes_reported": "No. DME identified from Vestrum diagnosis fields, but actual diagnostic codes are not reported.",
        "treatment_definition_detail": "First anti-VEGF injection identified from Vestrum procedure/medication data using SQL queries. Agents named in article/keywords include aflibercept, bevacizumab, and ranibizumab.",
        "procedure_drug_codes_reported_or_location": "No CPT/J-code/NDC list reported. Supplementary_materials.docx is linked from PMC at https://pmc.ncbi.nlm.nih.gov/articles/instance/9979048/bin/Supplementary_materials.docx but appears to be a small baseline supplement, not a code dictionary; direct local download was blocked by NCBI proof-of-work HTML.",
        "index_date_or_time_origin": "Index date was first anti-VEGF injection between 2012-01-01 and 2015-04-30.",
        "follow_up_and_attrition_rules": "Observed 12-24 months after index injection. Required VA on index date, at month 12, and at least once during each quarter. Month-12 VA was the reading closest to 12 months within months 11-12. Excluded treatment break >11 months at any point during 24 months after index injection.",
        "inclusion_criteria": "Newly diagnosed DME eyes; first anti-VEGF injection in the index window; VA on index date; quarterly VA and month-12 VA; accepted VA measurement method.",
        "exclusion_criteria": "Missing required quarterly VA readings, missing sex identification, treatment break >11 months during follow-up, and inconsistent/unsupported VA measurement methodology.",
        "unit_and_bilateral_handling": "Eye-level analysis; bilateral-eye handling not clearly reported.",
        "outcome_operational_definitions": "Main outcomes were injection frequency and mean VA change in ETDRS letters over year 1 and year 2. Cohorts were year 1 and year 2, each split into <=6 versus >6 injections per year. Year-2 analyses compared maintained versus reduced/increased injection frequency.",
        "va_method": "Accepted VA measurements were distance corrected, near corrected, or pinhole. Same VA methodology required for each patient. Approximate ETDRS letters = 85 - (50 * logMAR).",
        "baseline_va_strata": "Not the main stratification.",
        "treatment_intensity_definition": "<=6 versus >6 anti-VEGF injections per year.",
        "statistical_methods": "Descriptive statistics; paired t-tests within cohorts; independent t-tests assuming unequal variance between cohorts; Microsoft Excel; p < 0.05.",
        "appendix_or_supplement_location": "PMC article links Supplementary_materials.docx at https://pmc.ncbi.nlm.nih.gov/articles/instance/9979048/bin/Supplementary_materials.docx. No public code-list appendix found.",
        "limitations_relevant_to_methods": "Large attrition from 155,240 assessed DME eyes to 3,028 year-1 and 1,292 year-2 eyes due to first-treatment, VA, sex, quarterly follow-up, and treatment-break rules.",
    },
    {
        "id": "core-04",
        "source_scope": "Core Vestrum website qualifying publication",
        "title": "Visual Acuity Outcomes and Anti-VEGF Therapy Intensity in Diabetic Macular Edema: A Real-World Analysis of 28,658 Patient Eyes",
        "year": "2020/2021",
        "full_text_status": "PMC full-text HTML reviewed; PMC PDF endpoint blocked by proof-of-work HTML.",
        "source_urls": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7848066/",
        "local_evidence_files": d("04_PMC7848066_Visual_Acuity_DME_fulltext.html") + "; " + t("04_PMC7848066_Visual_Acuity_DME_fulltext.txt"),
        "database_version_or_size": "Vestrum Health Retina Database; nearly 1.5 million unique patients, >11 million encounters, 350 US retina specialists; weekly refresh; practice geography and urban/suburban/rural mix reported.",
        "dme_definition_detail": "Treatment-naive DME/DMO patient eyes in Vestrum EMR receiving anti-VEGF and meeting follow-up criteria. The article notes non-standardized diagnostic criteria for DMO as a limitation.",
        "diagnostic_codes_reported": "No. No public ICD/code list or diagnosis dictionary reported.",
        "treatment_definition_detail": "Anti-VEGF medications extracted from in-office/outpatient medication/treatment data. Initial agents: aflibercept, bevacizumab, ranibizumab. Switchers assessed in sensitivity analysis.",
        "procedure_drug_codes_reported_or_location": "No CPT/J-code/NDC list reported.",
        "index_date_or_time_origin": "Initial anti-VEGF treatment between January 2013 and July 2018.",
        "follow_up_and_attrition_rules": "Required 1-year follow-up data within months 11-12. One-year injection frequency evaluated from 1 to 13 injections; 32 eyes with >13 injections were not assigned a separate cohort and were excluded from further subgroup analyses.",
        "inclusion_criteria": "Treatment-naive DMO/DME eyes receiving at least one anti-VEGF injection and having 1-year follow-up in months 11-12.",
        "exclusion_criteria": "Other retinal diagnoses excluded. Sensitivity analysis excluded bilateral-treatment cases and switchers from initial therapy.",
        "unit_and_bilateral_handling": "Patient-eye level. Bilateral cases included in primary analysis; sensitivity analysis excluded patients receiving bilateral treatment.",
        "outcome_operational_definitions": "Mean 1-year VA change overall, by initial anti-VEGF medication, by injection frequency, by baseline VA, by injection frequency plus baseline VA, and by calendar-year medication utilization trends.",
        "va_method": "Snellen VA converted to approximate ETDRS letters using 85 + 50 * log(Snellen fraction), citing Gregori et al.",
        "baseline_va_strata": "20/40 or better; worse than 20/40 to 20/70; 20/70 to 20/200; 20/200 or worse.",
        "treatment_intensity_definition": "Number of anti-VEGF injections during year 1; histogrammed from 1-13 injections.",
        "statistical_methods": "Descriptive baseline summaries; mean VA change with 95% CIs and nominal paired t-test p values; sensitivity analyses excluding bilateral cases and switchers.",
        "appendix_or_supplement_location": "No public supplement or code-list appendix found in saved PMC full text.",
        "limitations_relevant_to_methods": "No public DME code list; real-world VA and diagnostic criteria not standardized; nonrandom medication selection.",
    },
    {
        "id": "core-05",
        "source_scope": "Core Vestrum website qualifying publication",
        "title": "Real-world Outcomes of Anti-VEGF Therapy in Diabetic Macular Edema in the United States",
        "year": "2018",
        "full_text_status": "Full PDF and PubMed page reviewed.",
        "source_urls": "https://pubmed.ncbi.nlm.nih.gov/31047187/; https://www.sciencedirect.com/science/article/pii/S2468653018302653; https://3333112.fs1.hubspotusercontent-na1.net/hubfs/3333112/RealworldOutcomesofAntiVascularEndothelialGrowthFactorTherapyinDiabeticMacularEdemaintheUnitedStates.pdf",
        "local_evidence_files": d("05_Ciulla_Bracha_Pollack_Williams_Realworld_AntiVEGF_DME_2018.pdf") + "; " + t("05_Ciulla_Bracha_Pollack_Williams_Realworld_AntiVEGF_DME_2018.txt"),
        "database_version_or_size": "Vestrum Health Retina Database; >240 private-practice retina physicians; >800,000 unique patients; >4.5 million encounters; weekly refresh.",
        "dme_definition_detail": "Treatment-naive DME patient eyes in Vestrum EMR that met initial anti-VEGF and follow-up criteria.",
        "diagnostic_codes_reported": "No. No public diagnostic code list reported.",
        "treatment_definition_detail": "Initial intravitreal anti-VEGF grouped as aflibercept, bevacizumab, or ranibizumab. Other extracted treatments were corticosteroids, macular laser, and PRP laser. Corticosteroids specified as triamcinolone with or without preservative and 0.7-mg dexamethasone implant.",
        "procedure_drug_codes_reported_or_location": "No CPT/J-code/NDC list reported.",
        "index_date_or_time_origin": "DME diagnosis/initial anti-VEGF treatment; eligible treatment between January 2011 and March 2017, with follow-up available before March 2018.",
        "follow_up_and_attrition_rules": "Mutually exclusive 6-, 12-, and 24-month cohorts. Eyes with VA measurements through 6 months but no follow-up beyond were 6-month cohort; through 12 months but none beyond were 12-month cohort; through 24 months were 24-month cohort. Death, relocation, or transfer of care classified as lost to follow-up.",
        "inclusion_criteria": "Treatment-naive DME eyes with >=3 monthly anti-VEGF injections during first 4 months from diagnosis/initial treatment.",
        "exclusion_criteria": "Not framed as a detailed exclusion list; cohort selected by treatment-naive DME, loading-injection rule, and follow-up availability.",
        "unit_and_bilateral_handling": "Patient-eye level. Bilaterally treated eyes analyzed independently; 10.4% of patients had bilateral treatment.",
        "outcome_operational_definitions": "VA change and number of anti-VEGF injections, corticosteroid injections, macular laser sessions, and PRP laser sessions, stratified by initial anti-VEGF agent and baseline VA.",
        "va_method": "ETDRS approximation = 85 + 50 * log(Snellen fraction). VA measurements were not standardized in this retrospective uncontrolled review.",
        "baseline_va_strata": "20/201 or worse; 20/71-20/200; 20/41-20/70; 20/40 or better.",
        "treatment_intensity_definition": "At least 3 monthly injections within first 4 months; number of treatments counted in each follow-up cohort.",
        "statistical_methods": "Descriptive summaries; mean change from baseline with 95% CIs and nominal paired t-test p values; stratified by baseline VA.",
        "appendix_or_supplement_location": "No public supplement or code-list appendix found.",
        "limitations_relevant_to_methods": "Classified by initial anti-VEGF agent and did not account for switching; retrospective selection bias; loading-injection criterion limits generalizability.",
    },
    {
        "id": "context-06",
        "source_scope": "Broader relevant Vestrum-DME context",
        "title": "Evolving Treatment Patterns in Diabetic Macular Edema Between 2015 and 2020",
        "year": "2023",
        "full_text_status": "Full PDF reviewed; PMC public full text identified.",
        "source_urls": "https://www.asrs.org/content/documents/sodhi-et-al-2023-evolving-treatment-patterns-in-diabetic-macular-edema-between-2015-and-2020.pdf; https://pmc.ncbi.nlm.nih.gov/articles/PMC10170625/",
        "local_evidence_files": d("06_Sodhi_Evolving_Treatment_Patterns_DME_2015_2020_ASRS.pdf") + "; " + t("06_Sodhi_Evolving_Treatment_Patterns_DME_2015_2020_ASRS.txt"),
        "database_version_or_size": "Vestrum Health Retina Database; aggregated longitudinal EMRs from demographically/geographically diverse US retina specialist panel.",
        "dme_definition_detail": "Newly diagnosed DME in Vestrum EMR. Article states ICD coding could not distinguish clinically significant vs center-involving DME, and imaging data were not available to verify/quantify DME severity.",
        "diagnostic_codes_reported": "No. ICD code list not reported.",
        "treatment_definition_detail": "Treatment categories: anti-VEGF, steroid, focal laser, any combination, and untreated. Combination therapy defined as any combination of anti-VEGF, steroids, or focal laser used at any time; simultaneous versus sequential combination not distinguished. Anti-VEGF agent distribution reported by bevacizumab, ranibizumab, and aflibercept.",
        "procedure_drug_codes_reported_or_location": "No CPT/J-code/NDC list reported.",
        "index_date_or_time_origin": "New DME diagnosis.",
        "follow_up_and_attrition_rules": "Records January 2015-October 2021; treatment-pattern years January 2015-October 2020; main cohort required >=1 year follow-up; 5-year cumulative subset required follow-up from 2015 through 2021.",
        "inclusion_criteria": "Eyes with newly diagnosed DME.",
        "exclusion_criteria": "Eyes with <1 year follow-up; eyes with pathology other than DME that might receive intravitreal or macular focal laser therapy, including AMD, RVO, and myopic CNV.",
        "unit_and_bilateral_handling": "Per-eye analysis; bilateral eyes treated independently.",
        "outcome_operational_definitions": "Year-over-year and 5-year cumulative treatment distribution, untreated proportion, anti-VEGF agent distribution, and mean VA change from baseline.",
        "va_method": "Baseline age/sex/Snellen VA captured; results expressed as ETDRS letters. No explicit Snellen-to-ETDRS formula printed in this article.",
        "baseline_va_strata": "VA outcomes also stratified by baseline VA within cohorts, but exact strata are not emphasized in the first-pass extraction.",
        "treatment_intensity_definition": "Treatment class distribution and anti-VEGF injection counts over annual and 5-year windows.",
        "statistical_methods": "Descriptive statistics; equality-of-proportions testing using Stata 17; p < .05.",
        "appendix_or_supplement_location": "No appendix/code supplement located.",
        "limitations_relevant_to_methods": "ICD coding could not distinguish DME subtype/severity; imaging unavailable; combination therapy timing not distinguished.",
    },
    {
        "id": "context-07",
        "source_scope": "Broader relevant Vestrum-DME context",
        "title": "Longer-Term Anti-VEGF Outcomes in Neovascular AMD, Diabetic Macular Edema, and Vein Occlusion-Related Macular Edema",
        "year": "2022",
        "full_text_status": "Open-access full PDF reviewed.",
        "source_urls": "https://www.sciencedirect.com/science/article/pii/S2468653022001506; https://pubmed.ncbi.nlm.nih.gov/35381391/; https://scholarworks.indianapolis.iu.edu/items/087c0836-ef68-417b-8015-a84a0b0c1bee",
        "local_evidence_files": d("07_Ciulla_Longer_Term_AntiVEGF_Outcomes_DME_nAMD_RVO_2022.pdf") + "; " + t("07_Ciulla_Longer_Term_AntiVEGF_Outcomes_DME_nAMD_RVO_2022.txt"),
        "database_version_or_size": "Vestrum Health Retina Database; approximately 1.5 million unique patients, >11 million encounters, 350 US retina specialists; weekly database updates.",
        "dme_definition_detail": "Treatment-naive DME eyes among disease cohorts receiving at least one anti-VEGF injection.",
        "diagnostic_codes_reported": "No. No public disease-code list reported.",
        "treatment_definition_detail": "Anti-VEGF agents captured, but analysis intentionally not stratified by aflibercept, ranibizumab, or bevacizumab because prior Vestrum studies found no meaningful 1-year VA differences by agent or after excluding switchers.",
        "procedure_drug_codes_reported_or_location": "No CPT/J-code/NDC list reported.",
        "index_date_or_time_origin": "First anti-VEGF treatment between 2014 and 2019.",
        "follow_up_and_attrition_rules": "Eligible with follow-up data through >=12 months. Distinct 1-, 2-, 3-, 4-, and 5-year cohorts for nAMD/DME; 1-, 2-, and 3-year cohorts for BRVO/CRVO. Cohorts were not mutually exclusive.",
        "inclusion_criteria": "Treatment-naive nAMD, DME, BRVO-ME, or CRVO-ME patients receiving at least 1 anti-VEGF injection and meeting follow-up criteria.",
        "exclusion_criteria": "Patients with other retinal diagnoses excluded.",
        "unit_and_bilateral_handling": "Patient-eye level. The paper cites prior same-database analyses showing no meaningful VA outcome differences when bilateral-treatment patients were excluded.",
        "outcome_operational_definitions": "Mean VA change from baseline; mean/median injection frequency; injection-frequency histograms; VA change stratified by injection count and baseline VA.",
        "va_method": "Snellen converted to approximate ETDRS letters using 85 + 50 * log(Snellen fraction).",
        "baseline_va_strata": "At 3 years: 20/40 or better; worse than 20/40 to 20/70; 20/70 to 20/200; 20/200 or worse.",
        "treatment_intensity_definition": "DME injection bins: 1-year bins from <=2 through >=12 injections; 3-year bins from <=4 through >=27; 5-year bins from <=9 through >=44.",
        "statistical_methods": "Descriptive statistics; paired t-tests for mean VA change; 95% CIs; nominal p values.",
        "appendix_or_supplement_location": "No appendix/code supplement located.",
        "limitations_relevant_to_methods": "No code lists; prior outside-practice treatment cannot be fully ruled out; longer follow-up cohorts are selected by continued observation.",
    },
    {
        "id": "context-08",
        "source_scope": "Broader relevant Vestrum-DME context",
        "title": "Bevacizumab-First Treatment Protocol AC Versus Real-World Treatment for Diabetic Macular Edema: Cost Analysis",
        "year": "2024",
        "full_text_status": "Full PDF reviewed; PMC public full text identified.",
        "source_urls": "https://journals.sagepub.com/doi/pdf/10.1177/24741264241275283?download=true; https://pmc.ncbi.nlm.nih.gov/articles/PMC11556346/",
        "local_evidence_files": d("08_Grewal_Bevacizumab_First_Protocol_AC_vs_Real_World_DME_Cost_2024.pdf") + "; " + t("08_Grewal_Bevacizumab_First_Protocol_AC_vs_Real_World_DME_Cost_2024.txt"),
        "database_version_or_size": "Vestrum Health retina database; actual real-world utilization harvested for visits, fundus photos, OCT, injections, and drug mix.",
        "dme_definition_detail": "Vestrum treatment-naive eyes with DME diagnosis at presentation and baseline VA 20/50-20/320, matched to Protocol AC.",
        "diagnostic_codes_reported": "No. No public DME code list reported.",
        "treatment_definition_detail": "Anti-VEGF monotherapy only. Modeled agents: bevacizumab, aflibercept 2 mg, ranibizumab 0.3 mg. Faricimab, aflibercept 8 mg, and biosimilars were not modeled.",
        "procedure_drug_codes_reported_or_location": "Yes, for cost modeling: intravitreal injection CPT 67028; new E/M 99204; established E/M 99214; OCT CPT 92134; fundus photo CPT 92250; aflibercept 2 mg J0178; ranibizumab 0.3 mg J2778; bevacizumab 1.25 mg J9035. Costs from 2022 CMS Physician Fee Schedule and December 2022 Medicare Part B ASP.",
        "index_date_or_time_origin": "Anti-VEGF initiation in 2016.",
        "follow_up_and_attrition_rules": "2-year follow-up. 1,556 DME eyes with baseline VA 20/50-20/320 initiated anti-VEGF in 2016; 494 excluded for steroid/laser treatment in addition to anti-VEGF; 1,062 included; VA-gain-matched subset n=346 created by progressively excluding eyes with lowest VA improvement/highest loss.",
        "inclusion_criteria": "Treatment-naive DME eyes, baseline VA 20/50-20/320, anti-VEGF monotherapy, treatment start in 2016, at least 2 years follow-up.",
        "exclusion_criteria": "AMD, RVO, or myopic CNV at any point during follow-up; intravitreal or periocular steroids; focal laser during study period.",
        "unit_and_bilateral_handling": "Eye-level cost/utilization model; bilateral handling not central to reported cost method.",
        "outcome_operational_definitions": "Modeled 2-year costs of visits, imaging, injections, and drug use; VA gain; real-world versus Protocol AC cost comparison; VA-gain matched secondary analysis.",
        "va_method": "Baseline VA matched to Protocol AC range. Real-world mean baseline VA 53.9 letters (~20/80) improved to 59.8 letters (~20/63) at year 2.",
        "baseline_va_strata": "Restricted to 20/50-20/320 rather than broad strata.",
        "treatment_intensity_definition": "Number of visits, OCTs, fundus photos, injections, and drug mix over 2 years. Protocol AC OCT every visit and annual fundus photos; real-world imaging use based on Vestrum.",
        "statistical_methods": "Cost model. Primary analysis assumed E/M at every injection with modifier 25 and allowed fundus photos billed with OCT. One-way sensitivity analyses removed E/M billing at injection visits and removed fundus photos billed with OCT.",
        "appendix_or_supplement_location": "No separate appendix/code supplement located. CPT/J-code cost components are in Table 1 of the article/PDF.",
        "limitations_relevant_to_methods": "Cost inputs depend on billing assumptions; anti-VEGF monotherapy selection excludes steroid/laser-treated DME; no DME diagnostic code list.",
    },
    {
        "id": "context-09",
        "source_scope": "Broader relevant Vestrum-DME context",
        "title": "Cost-Effectiveness of Step Therapy in Diabetic Macular Edema: Protocol AC and Real-World Data",
        "year": "2025",
        "full_text_status": "Full PDF reviewed; appendix methods and appendix tables embedded near end of ASRS PDF.",
        "source_urls": "https://www.asrs.org/content/documents/leung-et-al-2025-cost-effectiveness-of-treatments-for-diabetic-macular-edema-simulated-bevacizumab-first-step-therapy.pdf; https://journals.sagepub.com/doi/10.1177/24741264251359888",
        "local_evidence_files": d("09_Leung_Cost_Effectiveness_DME_Step_Therapy_2025.pdf") + "; " + t("09_Leung_Cost_Effectiveness_DME_Step_Therapy_2025.txt"),
        "database_version_or_size": "Vestrum Retinal Health database stated here as >1.8 million patients, >350 private-practice retina specialists, >69 sites in 35 states.",
        "dme_definition_detail": "No new patient-level Vestrum extraction; inherits real-world cohort definition from cost analysis: treatment-naive DME, baseline VA 20/50-20/320, anti-VEGF monotherapy starting in 2016.",
        "diagnostic_codes_reported": "No. No public DME code list reported.",
        "treatment_definition_detail": "Compared simulated Protocol AC bevacizumab-first step therapy to Vestrum real-world treatment regimen. Both groups assumed 5.6%/year switching from bevacizumab to FDA-approved therapy in lifetime assumptions.",
        "procedure_drug_codes_reported_or_location": "Uses direct medical values from Grewal/context-08, inflated to 2025 and discounted 3% annually. Appendix Methods contains drug costs and adverse-event cost details; PPV CPT 67036 used for endophthalmitis management.",
        "index_date_or_time_origin": "Treatment initiation in modeled scenarios; Vestrum comparator inherited from anti-VEGF initiation in 2016.",
        "follow_up_and_attrition_rules": "Markov model with 2-year and 17-year lifetime horizons; treated eye assumed to be the better-seeing eye.",
        "inclusion_criteria": "Modeled Vestrum cohort inherited from context-08: treatment-naive DME, VA 20/50-20/320, anti-VEGF monotherapy starting in 2016.",
        "exclusion_criteria": "Inherited: AMD, vascular occlusion, myopic CNV before or during follow-up; intravitreal or periocular steroids prior to or during study; focal laser prior to or during study.",
        "unit_and_bilateral_handling": "Modeled patient/eye pathway; treated eye assumed better-seeing eye.",
        "outcome_operational_definitions": "Formal healthcare costs, informal healthcare costs, non-healthcare/societal costs, QALYs, ICUR, and probability of cost-effectiveness. Endophthalmitis was the only modeled adverse event.",
        "va_method": "Vision-loss categories: mild 6/12-6/18 (~20/40-20/60), moderate worse than 6/18 and better than 6/60 (~20/63-20/200), severe worse than 6/60 (worse than ~20/200). Utility = 0.374 * visual acuity in better-seeing eye + 0.514; death utility 0; bilateral no-light-perception utility 0.26.",
        "baseline_va_strata": "Reference case: Protocol AC baseline 60 ETDRS letters (~20/63), Vestrum baseline 54 ETDRS letters (~20/80).",
        "treatment_intensity_definition": "Protocol AC and Vestrum injection/visit patterns modeled for 2 years. Years 3-17 reference case continued year-2 injection frequency; low-cost scenario reduced to 3 visits/injections/year; high-cost scenario 10% higher than reference.",
        "statistical_methods": "Theoretical Markov model from 2025 US societal perspective; followed Second Panel and CHEERS; 3% annual discounting; low/high-cost scenarios; Python second-order Monte Carlo probabilistic sensitivity analysis with 100,000 iterations.",
        "appendix_or_supplement_location": "Appendix Methods and Appendix Tables 1-3 are embedded near the end of the ASRS PDF, not separate files. Use the ASRS PDF for scenario ranges and total adjusted societal cost tables.",
        "limitations_relevant_to_methods": "Economic model, not a new patient-level Vestrum cohort; assumptions about long-term VA, injections, costs, and productivity drive results.",
    },
    {
        "id": "context-10",
        "source_scope": "Broader relevant Vestrum-DME context",
        "title": "Visual Acuity and Durability Outcomes of Faricimab Compared With Other Anti-VEGF Agents Within Routine Clinical Practice for Diabetic Macular Edema",
        "year": "2026",
        "full_text_status": "PubMed abstract and SAGE indexed page reviewed. Full text remained gated/blocked locally; PMC full text listed as available 2027-04-09. SAGE supplemental DOCX downloads blocked with HTTP 403.",
        "source_urls": "https://pubmed.ncbi.nlm.nih.gov/41971251/; https://journals.sagepub.com/doi/full/10.1177/24741264261428771",
        "local_evidence_files": d("10_PubMed_Macha_Faricimab_vs_Other_AntiVEGF_DME_2026.html") + "; " + t("10_PubMed_Macha_Faricimab_vs_Other_AntiVEGF_DME_2026.txt"),
        "database_version_or_size": "Deidentified EMRs in Vestrum Health database; January 2021-December 2023. SAGE data statement says Vestrum/CorEvitas provided database search and collation at no cost.",
        "dme_definition_detail": "Patients with DME treated with faricimab, bevacizumab, ranibizumab, or aflibercept. Detailed DME code definition not publicly available in abstract/SAGE indexed text.",
        "diagnostic_codes_reported": "No. No public ICD/code list available.",
        "treatment_definition_detail": "Treatment-naive eyes receiving faricimab, bevacizumab, ranibizumab, or aflibercept through 6 injections; treatment-experienced switch cohorts from aflibercept, bevacizumab, or ranibizumab to faricimab through 2 injections.",
        "procedure_drug_codes_reported_or_location": "No CPT/J-code/NDC list publicly available from abstract. SAGE lists five supplemental DOCX files that may contain table-level details, but local scripted download was blocked: sj-docx-1 through sj-docx-5-vrd-10.1177_24741264261428771.docx.",
        "index_date_or_time_origin": "Treatment-naive injection series start; faricimab switch for treatment-experienced cohort.",
        "follow_up_and_attrition_rules": "Treatment-naive eyes followed through 6 injections; treatment-experienced switch eyes followed through 2 injections.",
        "inclusion_criteria": "DME eyes in Vestrum treated with faricimab, bevacizumab, ranibizumab, or aflibercept during January 2021-December 2023.",
        "exclusion_criteria": "Detailed exclusions not publicly available from abstract/SAGE indexed text.",
        "unit_and_bilateral_handling": "Eye-level counts in abstract; bilateral handling not publicly available.",
        "outcome_operational_definitions": "Mean VA change by injection sequence; mean days between injections; durability threshold of >=50 mean days between injections 5 and 6; switch-cohort VA change after 2 injections.",
        "va_method": "VA change reported in letters. Detailed VA conversion method not publicly available from abstract.",
        "baseline_va_strata": "Results stratified by baseline VA, but exact strata are not visible in the public abstract.",
        "treatment_intensity_definition": "Mean days between injections; >=50-day durability threshold between injections 5 and 6.",
        "statistical_methods": "Abstract reports statistical comparisons including p < .01 for durability and one switch comparison; exact tests/models not publicly available.",
        "appendix_or_supplement_location": "SAGE article page lists five supplemental DOCX files: sj-docx-1-vrd-10.1177_24741264261428771.docx through sj-docx-5-vrd-10.1177_24741264261428771.docx. They are available from the SAGE article page but were blocked from local scripted download.",
        "limitations_relevant_to_methods": "Full methods and supplements are not locally accessible; extraction is abstract/indexed-page level only. PMID 41971251; DOI 10.1177/24741264261428771; PMCID PMC13068784 available 2027-04-09.",
    },
]


def write_csv(path, data):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_report():
    lines = [
        "# Vestrum DME Detailed Methods Comparison",
        "",
        f"Retrieval/update date: {RETRIEVAL_DATE}",
        "",
        "## What Changed in This Pass",
        "",
        "This pass reviewed the saved full texts and newly available public full-text/PMC pages where possible, then expanded the methods comparison to capture operational definitions. The most important finding is that the Vestrum DME papers generally do not publish reusable diagnostic ICD lists or drug NDC dictionaries. DME and treatment exposure are usually identified from Vestrum EMR diagnosis, procedure, medication, and treatment fields, with article-level operational windows and exclusion rules disclosed.",
        "",
        "Where code lists or long definitions are available only in appendices or supplements, the table points to the source location instead of reproducing pages of codes. For this corpus, the only explicit reusable code-level details found were cost-model CPT/J-code inputs in the 2024/2025 economic papers. The 2026 faricimab article has SAGE supplemental DOCX files listed, but local scripted access was blocked.",
        "",
        "## Detailed Comparison",
        "",
        "| ID | Publication | DME Definition and Codes | Treatment/Exposure Definition | Outcomes and Operational Rules | Supplement/Appendix Location |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['title']} ({row['year']}) | {row['dme_definition_detail']} Codes: {row['diagnostic_codes_reported']} | {row['treatment_definition_detail']} Codes/source: {row['procedure_drug_codes_reported_or_location']} | {row['outcome_operational_definitions']} VA: {row['va_method']} Follow-up: {row['follow_up_and_attrition_rules']} | {row['appendix_or_supplement_location']} |"
        )

    lines.extend([
        "",
        "## Cross-Article Findings",
        "",
        "- DME diagnosis is consistently EMR/diagnosis-field based, but public articles do not provide a reusable DME ICD code list.",
        "- Anti-VEGF exposure is usually defined through Vestrum medication/procedure/treatment fields and named agents rather than published J-code or NDC dictionaries.",
        "- The best operational VA definitions are in the Ciulla/Pollack/Williams line of papers: Snellen converted to approximate ETDRS letters using `85 + 50 * log(Snellen fraction)`. Pitcher uses `85 - (50 * logMAR)` and additionally requires same VA methodology per patient.",
        "- The most reproducible one-year anti-VEGF outcomes template remains core-04: treatment-naive DME/DMO, first anti-VEGF index, months 11-12 follow-up, exclusion of other retinal diagnoses, baseline VA strata, injection-frequency strata, and bilateral/switcher sensitivity analyses.",
        "- The most reproducible treatment-pattern template is context-06: diagnosis-indexed newly diagnosed DME, >=1 year follow-up, exclusion of competing retinal pathologies, treatment categories including untreated, anti-VEGF, steroid, focal laser, and combinations.",
        "- The most explicit code-level definitions are economic, not clinical: context-08 and context-09 report CPT/J-codes and cost assumptions for injections, visits, OCT, fundus photography, aflibercept, ranibizumab, bevacizumab, and endophthalmitis management.",
        "",
        "## Recommended Operational Fields for Future Vestrum DME Studies",
        "",
        "1. Publish or append the DME diagnosis-code dictionary, including how DME is distinguished from DR without DME and whether center-involving or clinically significant DME can be identified.",
        "2. Publish the anti-VEGF, steroid, laser, OCT, and visit code/field logic, or provide an appendix URL for the full list when it is too long for the article body.",
        "3. State whether treatment-naive means no prior treatment in Vestrum only or no known treatment anywhere, and define the lookback window.",
        "4. Define the index date precisely: first DME diagnosis, first anti-VEGF injection, first treatment class, or switch date.",
        "5. Define VA measurement hierarchy and conversion formula, and require consistent VA methodology if longitudinal comparability is central.",
        "6. Prespecify follow-up windows such as months 11-12 for one-year VA and define allowable gaps, loss-to-follow-up, death, relocation, and transfer handling.",
        "7. Define bilateral-eye handling and include a sensitivity analysis excluding bilateral cases when patient-level dependence could affect inference.",
        "8. Stratify by baseline VA and treatment intensity; these are the most consistent modifiers of real-world DME VA outcomes across Vestrum papers.",
        "",
        "## Files",
        "",
        "- Detailed methods CSV: `methods_extraction_detailed.csv`",
        "- Detailed methods JSON: `methods_extraction_detailed.json`",
        "- First-pass methods CSV retained: `methods_extraction.csv`",
        "- Source log retained/updated separately: `source_log.csv` and `source_log.json`",
    ])
    (ROOT / "vestrum_dme_methods_comparison_detailed.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_source_log():
    path = ROOT / "source_log.json"
    if not path.exists():
        return
    source_rows = json.loads(path.read_text(encoding="utf-8"))
    for row in source_rows:
        if row.get("id") == "core-02":
            row["local_files"] += "; " + d("02_PMC9979048_Pitcher_DME_fulltext.html") + "; " + t("02_PMC9979048_Pitcher_DME_fulltext.txt")
            row["access_status"] += " PMC full text was also saved in the detailed pass. PMC supplement link was identified, but direct download returned proof-of-work HTML."
            row["current_access_url"] = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9979048/"
        if row.get("id") == "context-10":
            row["current_access_url"] = "https://pubmed.ncbi.nlm.nih.gov/41971251/"
            row["access_status"] = "PubMed page saved with PMID 41971251. SAGE full text/PDF and five supplemental DOCX files were listed publicly but direct local download returned HTTP 403; PMC full text is embargoed until 2027-04-09."
            row["notes"] = "Detailed pass corrected DOI/PMID metadata: DOI 10.1177/24741264261428771; PMCID PMC13068784 available 2027-04-09."
    write_json(ROOT / "source_log.json", source_rows)
    with (ROOT / "source_log.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(source_rows[0].keys()))
        writer.writeheader()
        writer.writerows(source_rows)


def main():
    write_csv(ROOT / "methods_extraction_detailed.csv", rows)
    write_json(ROOT / "methods_extraction_detailed.json", rows)
    write_report()
    update_source_log()
    print(json.dumps({
        "detailed_rows": len(rows),
        "created_or_updated": [
            str((ROOT / "methods_extraction_detailed.csv").resolve()),
            str((ROOT / "methods_extraction_detailed.json").resolve()),
            str((ROOT / "vestrum_dme_methods_comparison_detailed.md").resolve()),
            str((ROOT / "source_log.csv").resolve()),
            str((ROOT / "source_log.json").resolve()),
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
