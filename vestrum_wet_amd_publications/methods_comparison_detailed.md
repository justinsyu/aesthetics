# Vestrum Wet AMD Publications - Detailed Methods Comparison

Updated: 2026-06-03

Scope: Vestrum Health website-indexed and supplemental web-discovered publications, posters, and presentations that used the Vestrum database to evaluate wet AMD/neovascular AMD (nAMD), including papers that also included DME, RVO, or dry AMD where nAMD was a study population or outcome.

## Cross-Study Method Patterns

- Most Vestrum nAMD outcomes studies define cohorts clinically as nAMD diagnosis plus anti-VEGF treatment history plus VA/follow-up availability. Published articles usually do not expose the underlying ICD-9/ICD-10 diagnosis-code lists or NDC/HCPCS drug-code lists.
- The most common index date is the first anti-VEGF injection. SIERRA-AMD additionally allowed first nAMD diagnosis as index for non-injected eyes, and Rowe 2026 uses switch date for treatment-experienced switch analyses.
- Treatment-naive definitions vary. Common windows include no prior treatment at all, no anti-VEGF for >180 days before index, or no anti-VEGF during a 12-month pre-index period.
- VA is typically converted to ETDRS-equivalent letters. Two formulas/approaches recur: `85 + 50 x log(Snellen fraction)`, equivalent logMAR formulas such as `85 - 50 x logMAR`, and the Gregori approximation used by Luttrull 2023.
- The most reusable operational endpoints are first-year VA change by injection count, long-term VA by cumulative injection frequency, treatment gaps/persistence using a `>=180-day` gap, driving vision loss defined as VA worse than 20/40 sustained `>=6` months, and dry-to-wet conversion requiring both diagnostic-code change and anti-VEGF initiation.
- For a new Vestrum wet AMD analysis, the best-supported design is an eye-level cohort with a clearly stated index injection, baseline VA strata, treatment-naive window, VA conversion rule, minimum follow-up/visit windows, injection-count or gap/persistence exposure, and explicit attrition handling.

## Publication-Level Details

### 1. Real-world Outcomes of Anti-VEGF Therapy in Neovascular Age-Related Macular Degeneration in the United States (2018)

- ID: ciulla_2018_namd_real_world_outcomes
- Set: Vestrum website indexed
- Publication type: Manuscript
- Source URL(s): https://www.sciencedirect.com/science/article/pii/S246865301730297X; https://pubmed.ncbi.nlm.nih.gov/31047372/
- Full-text status: Full text saved locally from Vestrum/HubSpot PDF and reviewed.
- Local evidence: downloads/ciulla_2018_namd_real_world_outcomes_hubspot.pdf; texts/ciulla_2018_namd_real_world_outcomes_hubspot.txt; texts/ciulla_2018_namd_real_world_outcomes_pubmed_31047372.txt
- Design/data source: Retrospective cohort using aggregated, longitudinal, deidentified EMR data from the Vestrum Health Retina Database. Database fields included demographics, VA, OCT/central macular thickness, diagnostic tests/images, diagnoses, surgical utilization, outcomes/adverse events, and medication/treatment data, with weekly updates.
- Population/inclusion: Treatment-naive nAMD patients diagnosed Jan 2011-Jul 2013. Required at least 3 monthly anti-VEGF injections in the first 4 months from diagnosis/treatment initiation.
- Index/exposure definition: Index was diagnosis/treatment initiation period; exposure was real-world anti-VEGF injection frequency after an initial 3-month loading pattern.
- Follow-up/windows: Mutually exclusive follow-up/attrition cohorts were used: completed 6 months but then lost to follow-up, completed 12 months but then lost to follow-up, or completed 24 months ending before Jul 2015.
- Exclusions: No previous nAMD treatment. Death, relocation, and changing provider were treated as loss to follow-up for analysis. Other granular exclusions were not reported in the accessible full text.
- Diagnosis/case definition and codes: nAMD diagnosis recorded in Vestrum EMR; no ICD-9/ICD-10 code list was reported.
- Treatment/drug definition: Anti-VEGF injections captured from Vestrum EMR. Specific drug-code lists such as NDC or HCPCS were not reported.
- Outcome operational definitions: VA was analyzed as ETDRS-equivalent letters converted from Snellen using `85 + 50 x log(Snellen fraction)`. VA was not protocol-standardized. Baseline VA strata included 20/40 or better, approximately 20/41-20/70, 20/71-20/200, and 20/201 or worse. Outcomes were mean VA change and injection counts by follow-up cohort and baseline VA stratum.
- Statistical methods: Descriptive statistics and paired comparisons of VA change from baseline; article reports P values/95% CIs for selected comparisons.
- Code lists, appendices, or supplements: No appendix with ICD/NDC/HCPCS lists found in the full text. Source methods are in the saved PDF/text.
- Methods limitations: Best detail available for attrition handling and VA conversion, but diagnosis and drug identification algorithms are not reproducible from published code lists.

### 2. Visual Acuity Outcomes in Patients Receiving Frequent Treatment of Neovascular Age-Related Macular Degeneration in Clinical Practice (2021)

- ID: moshfeghi_2021_frequent_treatment
- Set: Vestrum website indexed / ASRS 2018 presentation follow-up
- Publication type: Manuscript; associated with Vestrum-linked ASRS 2018 presentation coverage
- Source URL(s): https://pmc.ncbi.nlm.nih.gov/articles/PMC9979036/; https://pubmed.ncbi.nlm.nih.gov/36909242/
- Full-text status: PMC article metadata/methods text saved and reviewed. Direct browser access was challenged; PMC XML/text was available locally. Supplement download endpoint returned an HHS proof-of-work stub, not a usable DOCX.
- Local evidence: texts/moshfeghi_2021_frequent_treatment_PMC9979036_bioc.txt; source_pages/pmc_fetch_https_eutils_ncbi_nlm_nih_gov_entrez_eutils_efetch_fcgi_db_pmc_id_9979036_rettyp.txt; metadata/moshfeghi_2021_supplement_extract_record.json
- Design/data source: Retrospective analysis of the Vestrum Health treatment and outcomes database, described as data from 251 retina specialists at 54 US private clinics.
- Population/inclusion: Newly diagnosed nAMD patients whose first/index anti-VEGF injection was bevacizumab, ranibizumab, or aflibercept between Jan 1 2012 and Apr 30 2015.
- Index/exposure definition: Index date was first anti-VEGF injection. Treatment intensity was grouped by injection frequency, including eyes with >10 injections over 2 years and annual subgroups of `<=6` versus `>6` injections/year.
- Follow-up/windows: Evaluated 1- and 2-year outcomes. Required VA on index date, at month 12, and at least once each quarter. Month-12 VA used the closest reading between months 11 and 12.
- Exclusions: Excluded missing sex, treatment breaks >11 months during the 24-month period, and eyes/patients without required VA or quarterly follow-up. Required consistent VA measurement method within a patient.
- Diagnosis/case definition and codes: New nAMD diagnosis in Vestrum EMR plus anti-VEGF initiation. No ICD-9/ICD-10 code list was reported in accessible text.
- Treatment/drug definition: Index anti-VEGF was bevacizumab, ranibizumab, or aflibercept. No NDC/HCPCS list was reported.
- Outcome operational definitions: VA accepted only if distance-corrected, near-corrected, or pinhole, with a consistent method per patient. ETDRS letters were calculated as `85 - (50 x logMAR)`. Outcomes were VA change by injection-frequency group and frequent-treatment subgroup over 1 and 2 years.
- Statistical methods: Comparative descriptive analyses of VA outcomes by treatment-frequency subgroup; accessible text did not expose a full statistical-analysis appendix.
- Code lists, appendices, or supplements: PMC lists a supplement at https://pmc.ncbi.nlm.nih.gov/articles/instance/9979036/bin/Supplement.docx, but scripted download returned a proof-of-work HTML stub. Available descriptions indicate supplemental tables rather than code lists.
- Methods limitations: Strong operational detail for VA and injection-frequency windows; code lists and complete supplement contents were not accessible in this run.

### 3. Visual Acuity Outcomes and Anti-VEGF Therapy Intensity in Neovascular Age-Related Macular Degeneration Patients: A Real-World Analysis of 49,485 Eyes (2020)

- ID: ciulla_2020_va_intensity_49485
- Set: Vestrum website indexed
- Publication type: Manuscript
- Source URL(s): https://www.sciencedirect.com/science/article/pii/S2468653019302805; https://pubmed.ncbi.nlm.nih.gov/31324588/
- Full-text status: PubMed/local abstract and metadata reviewed. Full ScienceDirect page/PDF was not saved due access/script limitations.
- Local evidence: texts/ciulla_2020_va_intensity_49485_pubmed_31324588.txt; source_pages/ciulla_2020_va_intensity_49485_pubmed_31324588.xml
- Design/data source: Retrospective analysis of aggregated, longitudinal, deidentified EMR data in the Vestrum Health Retina Database.
- Population/inclusion: Treatment-naive nAMD eyes receiving anti-VEGF injections from Jan 1 2012 through Oct 31 2016, with follow-up data available before Oct 31 2017. Reported cohort size was 49,485 eyes.
- Index/exposure definition: Index was anti-VEGF treatment start. Primary exposure was number of anti-VEGF injections during the first year; analyses also stratified by anti-VEGF agent.
- Follow-up/windows: One-year outcome window after treatment initiation.
- Exclusions: Treatment-naive requirement; additional granular exclusions were not available in accessible abstract/PubMed text.
- Diagnosis/case definition and codes: nAMD diagnosis and treatment-naive status in Vestrum EMR; no ICD code list reported in accessible records.
- Treatment/drug definition: Anti-VEGF type and treatment counts extracted from EMR; no NDC/HCPCS list reported in accessible records.
- Outcome operational definitions: Mean VA change at 1 year stratified by injection count and anti-VEGF agent. Abstract reports a linear relationship for 4-10 injections/year, with loss/plateau patterns at `<=4` and `>=10` injections/year.
- Statistical methods: Accessible record provides stratified mean VA outcomes but not complete model details.
- Code lists, appendices, or supplements: No code-list appendix found in accessible records. Full article may contain more detail at ScienceDirect.
- Methods limitations: Good high-level benchmark for first-year injection intensity and VA, but reproducibility is limited by lack of accessible full methods and code lists.

### 4. SIERRA-AMD: A Retrospective, Real-World Evidence Study of Patients with Neovascular Age-Related Macular Degeneration in the United States (2020)

- ID: khanani_2020_sierra_amd
- Set: Vestrum website indexed
- Publication type: Manuscript
- Source URL(s): https://www.sciencedirect.com/science/article/pii/S246865301930569X; https://pubmed.ncbi.nlm.nih.gov/31812631/
- Full-text status: Open-access ScienceDirect web text reviewed. Scripted save of the ScienceDirect HTML failed, but PubMed XML/text and source link are saved.
- Local evidence: texts/khanani_2020_sierra_amd_pubmed_31812631.txt; source_pages/khanani_2020_sierra_amd_pubmed_31812631.xml; metadata/additional_fulltext_fetch_records.json
- Design/data source: Retrospective, multicenter, noninterventional RWE study using anonymized patient data routinely collected over 5 years from 58 US retina centers into a central EMR-derived database.
- Population/inclusion: Patients age >=50 with nAMD in at least 1 eye. Primary treated cohort included 98,821 eyes from 79,885 patients receiving intravitreal anti-VEGF therapy. nAMD diagnosis years were Jan 1 2012-Dec 31 2015.
- Index/exposure definition: Index date was first anti-VEGF injection, or first nAMD diagnosis if no anti-VEGF. Treatment-naive was defined as no anti-VEGF for more than 180 days before index. Treated cohort required at least 1 anti-VEGF injection within 180 days after index.
- Follow-up/windows: Study period Jan 1 2012-Jun 30 2016. Longitudinal outcomes were evaluated through years 1-4 where follow-up was available.
- Exclusions: Granular exclusion list was not visible in the ScienceDirect text available through web view beyond the age, nAMD, and treatment-history requirements.
- Diagnosis/case definition and codes: nAMD diagnosis in EMR. No ICD-9/ICD-10 list was reported in the accessible article text.
- Treatment/drug definition: Intravitreal anti-VEGF therapy captured in EMR. No drug-code list was reported in accessible article text.
- Outcome operational definitions: VA logMAR converted to ETDRS letters. Outcomes included baseline VA, VA change from baseline, annual anti-VEGF injections, total clinic visits, noninjection clinic visits, bilateral treatment, dosing intervals, and time from first-eye to second-eye treatment. Noninjection visit was a clinic visit without anti-VEGF administration. Fixed regimen was `>=80%` of nonloading injections in a year at 4, 8, or 12 weeks +/-15 days after the prior injection. Dosing intervals included q8w and `>=12-week` categories.
- Statistical methods: Reported means/SDs and least-squares mean VA changes with 95% CIs across years; detailed model specification was not fully exposed in the web text captured by this run.
- Code lists, appendices, or supplements: ScienceDirect article states supplemental material is available at www.ophthalmologyretina.org; subagent review identified Supplemental Table S1 as patient attrition. No ICD/NDC/HCPCS lists found in accessible text.
- Methods limitations: Best broad design for burden and visit-pattern comparisons; missing published code lists remain a limitation.

### 5. Increasing Incidence and Prevalence of Common Retinal Diseases in Retina Practices Across the United States (2021)

- ID: rosenblatt_2021_incidence_prevalence
- Set: Vestrum website indexed
- Publication type: Manuscript / poster-derived epidemiology analysis
- Source URL(s): https://pubmed.ncbi.nlm.nih.gov/33471912/; https://stanfordhealthcare.org/publications/807/807898.html
- Full-text status: PubMed/abstract records reviewed. Direct poster PDF URL found previously is now 404 in scripted fetch. Publisher/full text not saved.
- Local evidence: texts/rosenblatt_2021_incidence_prevalence_pubmed_33471912.txt; source_pages/rosenblatt_2021_incidence_prevalence_pubmed_33471912.xml; metadata/additional_fulltext_fetch_records.json
- Design/data source: Retrospective Vestrum Health Retina Database epidemiology study across US retina practices.
- Population/inclusion: Eyes examined in retina practices from Jan 2014-Dec 2019. PubMed abstract reports 3,086,791 eyes examined; poster/abstract snippets report larger evaluated-eye counts depending on denominator/source.
- Index/exposure definition: Condition-specific diagnosis year/date in Vestrum EMR; not an anti-VEGF treatment exposure study.
- Follow-up/windows: Annual and cumulative analyses for Jan 2014-Dec 2019.
- Exclusions: Not detailed in accessible abstract/PubMed text.
- Diagnosis/case definition and codes: Included diagnosis categories: wet AMD, dry AMD including geographic atrophy, diabetic macular edema, diabetic retinopathy without DME, branch retinal vein occlusion, and central retinal vein occlusion. Accessible text says diagnosis codes were used, but specific ICD-9/ICD-10 codes were not listed.
- Treatment/drug definition: Not applicable for primary incidence/prevalence endpoints.
- Outcome operational definitions: Incidence was newly diagnosed eyes within a year/period. Prevalence was distinct eyes seen with the associated condition. Poster snippets indicate stratification by age and geography.
- Statistical methods: Descriptive epidemiologic rates/counts; accessible text does not expose advanced model details.
- Code lists, appendices, or supplements: No code-list appendix found. Attempted poster URL logged as 404 in metadata/additional_fulltext_fetch_records.json.
- Methods limitations: Useful for disease-burden context, but not a detailed nAMD outcomes algorithm paper and published diagnostic code lists were not accessible.

### 6. Characterizing Progression to Neovascular Age-Related Macular Degeneration in Fellow Eyes of Patients with Neovascular Age-Related Macular Degeneration (2021)

- ID: starr_2021_fellow_eye_progression
- Set: Vestrum website indexed
- Publication type: Manuscript
- Source URL(s): https://pubmed.ncbi.nlm.nih.gov/34038686/; https://mayoclinic.elsevierpure.com/en/publications/characterizing-progression-to-neovascular-amd-in-fellow-eyes-of-p/
- Full-text status: PubMed/abstract and institutional record reviewed. Publisher full text/PDF was not accessible locally; previous source pages include bot/check stubs.
- Local evidence: texts/starr_2021_fellow_eye_progression_pubmed_34038686.txt; source_pages/starr_2021_fellow_eye_progression_pubmed_34038686.xml
- Design/data source: Retrospective cohort using EHRs from retinal centers across the United States in the Vestrum Database.
- Population/inclusion: Patients with unilateral nAMD treated with anti-VEGF therapy; reported cohort included 22,553 unilateral nAMD patients.
- Index/exposure definition: Index was diagnosis/treatment initiation in the first eye. Exposure/risk process was fellow-eye follow-up after unilateral nAMD.
- Follow-up/windows: Conversion assessed over multiple years; abstract reports year-specific conversion at years 1, 2, and 3.
- Exclusions: Accessible text does not report detailed exclusions beyond unilateral nAMD at baseline and anti-VEGF treatment in first eye.
- Diagnosis/case definition and codes: First-eye unilateral nAMD and fellow-eye conversion to nAMD in Vestrum EHR. No ICD code list was reported in accessible text.
- Treatment/drug definition: Anti-VEGF therapy in first eye and injection burden after fellow-eye conversion captured from EHR; no NDC/HCPCS list reported.
- Outcome operational definitions: Primary outcome was fellow-eye conversion to nAMD. Abstract reports 8,522/22,553 patients (38%) converted; year 1 12%, year 2 9%, year 3 8%. VA was measured at fellow-eye conversion and 1 year after conversion, with injection burden after conversion.
- Statistical methods: Accessible text reports descriptive conversion and VA/injection comparisons; full model details unavailable.
- Code lists, appendices, or supplements: No appendix or code list found in accessible records. Full publisher article may contain additional details.
- Methods limitations: Important for fellow-eye endpoint framing, but operational conversion algorithm is less explicit than Luttrull 2023.

### 7. Longer-Term Anti-VEGF Therapy Outcomes in Neovascular Age-Related Macular Degeneration, Diabetic Macular Edema, and Retinal Vein Occlusion-Related Macular Edema (2022)

- ID: ciulla_2022_longer_term_outcomes
- Set: Supplemental web-discovered relevant Vestrum nAMD item
- Publication type: Manuscript
- Source URL(s): https://pubmed.ncbi.nlm.nih.gov/35381391/; https://www.sciencedirect.com/science/article/pii/S2468653022000435
- Full-text status: Full text PDF/text saved locally and reviewed.
- Local evidence: downloads/ciulla_2022_longer_term_outcomes.pdf; texts/ciulla_2022_longer_term_outcomes.txt; texts/ciulla_2022_longer_term_outcomes_pubmed_35381391.txt
- Design/data source: Retrospective Vestrum Health Retina Database analysis. Full text describes about 1.5M patients, more than 11M encounters, and about 350 retina specialists, with demographics, geography, central macular thickness, VA, diagnostic testing/images, ocular/systemic diagnoses, medical/surgical treatments, and adverse events.
- Population/inclusion: Treatment-naive patients with nAMD, DME, BRVO-ME, or CRVO-ME who received at least 1 anti-VEGF injection between 2014 and 2019 and had at least 12 months of follow-up. nAMD cohort sizes included 67,666 eyes at 1 year, 21,305 at 3 years, and 5,208 at 5 years.
- Index/exposure definition: Index was first anti-VEGF injection. Exposure was cumulative injection number over each yearly horizon.
- Follow-up/windows: nAMD/DME outcomes at 1, 3, and 5 years; BRVO/CRVO outcomes at 1, 2, and 3 years. Distinct yearly cohorts were assessed based on available follow-up.
- Exclusions: Excluded other retinal diagnoses in the disease-specific analyses; detailed code lists not reported.
- Diagnosis/case definition and codes: Diagnosis categories from Vestrum EMR; no ICD code list reported.
- Treatment/drug definition: Anti-VEGF injection use captured from EMR; agent-specific results were not emphasized because prior Vestrum work found similar outcomes after switching. No NDC/HCPCS list reported.
- Outcome operational definitions: VA converted from Snellen using `85 + 50 x log(Snellen fraction)`. Outcomes were mean VA change with 95% CI and nominal P values, mean/median injections, injection-frequency histograms, and stratifications by baseline VA/injection count. nAMD mean injections were 7.6, 19.5, and 32.7 at 1/3/5 years; mean VA changes were +3.1, -0.2, and -2.2 letters.
- Statistical methods: Descriptive yearly analyses with 95% CIs and nominal P values; eye-level analysis.
- Code lists, appendices, or supplements: No ICD/NDC/HCPCS appendix found in full text.
- Methods limitations: Good benchmark for long-term treatment intensity and VA trajectory; code lists and granular disease-algorithm validation are not published.

### 8. Levodopa Is Associated with Reduced Development of Neovascular Age-Related Macular Degeneration (2023)

- ID: hyman_2023_levodopa_namd
- Set: Supplemental web-discovered relevant Vestrum nAMD item
- Publication type: Manuscript
- Source URL(s): https://pmc.ncbi.nlm.nih.gov/articles/PMC10524303/; https://pubmed.ncbi.nlm.nih.gov/37146684/
- Full-text status: Open-access PMC BioC full text saved and reviewed.
- Local evidence: texts/hyman_2023_levodopa_namd_PMC10524303_bioc.txt; texts/hyman_2023_levodopa_namd_pubmed_37146684.txt
- Design/data source: Two Vestrum retrospective eye-level analyses plus an IBM MarketScan case-control analysis. Vestrum was described as about 1.5M unique patients and 11M encounters.
- Population/inclusion: Vestrum query 1: new-onset nAMD eyes from Jan 2014-May 2020. Vestrum query 2: non-neovascular AMD eyes from Jan 2014-Jun 2021.
- Index/exposure definition: Exposure was L-DOPA use before or on AMD/nAMD diagnosis versus no L-DOPA. Query 1 excluded L-DOPA after nAMD diagnosis and assessed injection counts. Query 2 excluded L-DOPA after dry AMD diagnosis and assessed conversion to nAMD. MarketScan exposure used L-DOPA-related drug names and claims with positive days supply/quantity/strength, with 24-month cumulative dose tertiles.
- Follow-up/windows: Query 1 required 2 years of follow-up and measured injections at years 1 and 2. Query 2 required at least 1 year of follow-up and measured conversion across years 1-5.
- Exclusions: Query 1 excluded eyes without 2-year follow-up and eyes receiving L-DOPA only after nAMD diagnosis. Query 2 excluded eyes without 1-year follow-up and eyes receiving L-DOPA only after AMD diagnosis.
- Diagnosis/case definition and codes: New-onset nAMD and non-neovascular AMD diagnoses in Vestrum EMR; specific ICD code lists were not enumerated in the article.
- Treatment/drug definition: L-DOPA exposure in MarketScan used generic drug names including Levodopa, Carbidopa/Levodopa, and Carbidopa/Entacapone/Levodopa plus claim-level NDC-style fields. Exact NDC list was not supplied. Vestrum anti-VEGF injections were counted but drug-code lists were not provided.
- Outcome operational definitions: Query 1 outcome was number of intravitreal injections at years 1 and 2 after nAMD diagnosis. Query 2 outcome was conversion from non-neovascular AMD to nAMD at years 1-5. Covariates included age, sex, smoking, AREDS use, dry AMD stage, and L-DOPA status.
- Statistical methods: Welch t-test for age where variances differed, chi-square for sex, unpaired t-test for injection counts, and logistic regression in R for conversion with sex, age, smoking, dry AMD stage, L-DOPA status, and AREDS as independent variables.
- Code lists, appendices, or supplements: No exact ICD or NDC list found in the article. If exact MarketScan NDC implementation is needed, it is not available in the accessible article/PMC files.
- Methods limitations: Strong example for medication-exposure hypothesis generation, but less directly reusable for anti-VEGF treatment-outcome design because exact drug/code lists are not published.

### 9. Vision Protection Therapy for Prevention of Neovascular Age-Related Macular Degeneration (2023)

- ID: luttrull_2023_vpt_prevention
- Set: Supplemental web-discovered relevant Vestrum nAMD item
- Publication type: Manuscript
- Source URL(s): https://pmc.ncbi.nlm.nih.gov/articles/PMC10550910/; https://www.nature.com/articles/s41598-023-43605-w
- Full-text status: Open-access PMC BioC full text saved and reviewed. Supplement pointer identified.
- Local evidence: texts/luttrull_2023_vpt_prevention_PMC10550910_bioc.txt; texts/luttrull_2023_vpt_prevention_pubmed_37794027.txt
- Design/data source: Retrospective Vestrum analysis comparing one VPT practice with all other Vestrum practices using standard care alone. Vestrum performed filtering, inclusion/exclusion, and propensity scoring. Database described as more than 320 geographically diverse retina subspecialty practices.
- Population/inclusion: Dry AMD cohort from Jan 2017-Jul 2023. Included age >=50 and ICD-10 coding for dry AMD.
- Index/exposure definition: Exposure was treatment at a VPT practice versus standard care alone in other Vestrum practices.
- Follow-up/windows: Conversion and VA outcomes assessed during the available Jan 2017-Jul 2023 Vestrum period.
- Exclusions: Excluded prior/current intravitreal steroids or VEGF inhibitors for any indication, nAMD fellow eye, diabetes mellitus, retinal vascular occlusion, prior conventional macular photocoagulation or other macular scarring, ocular histoplasmosis, high/degenerative myopia, idiopathic macular telangiectasia, and central serous chorioretinopathy.
- Diagnosis/case definition and codes: Used ICD-10 because ICD-10 stratifies dry AMD severity. Dry-to-wet conversion required two factors: diagnostic coding changed from dry AMD to wet AMD and anti-VEGF therapy began. The article cites H35.30 in relation to wet AMD coding; full dry AMD severity code lists are not expanded in the text.
- Treatment/drug definition: Anti-VEGF initiation was part of the wet-conversion definition. Specific anti-VEGF drug-code lists were not reported.
- Outcome operational definitions: Primary endpoint was conversion from dry AMD to wet AMD; conversion date was the earliest of diagnostic-code change or anti-VEGF initiation. VA was converted to approximate ETDRS letters using the Gregori method, e.g., Snellen 20/20 = 85, 20/40 = 70, 20/80 = 55, 20/160 = 40.
- Statistical methods: Propensity score matching on age, AREDS vitamin use, hypertension, smoking, and ICD-10 dry AMD severity. Nearest-neighbor 1:10 VPT:SCA matching, 5 propensity strata, R MatchIt package, and bootstrap CIs accounting for inter-eye correlation.
- Code lists, appendices, or supplements: Supplementary Information is linked from the PMC article at https://pmc.ncbi.nlm.nih.gov/articles/PMC10550910/#MOESM1 and the Nature article page. The accessible article says all generated/analyzed data are included in the article and supplement, but it does not provide pages of ICD/NDC lists.
- Methods limitations: Most explicit operational conversion definition among reviewed items; verify the cited H35.30 code family before reusing it because the published text may abbreviate/oversimplify the exact ICD-10 implementation.

### 10. Maintenance of Vision Needed to Drive After Anti-VEGF Therapy in Neovascular Age-Related Macular Degeneration and Diabetic Macular Edema (2024)

- ID: emami_2024_driving_vision
- Set: Supplemental web-discovered relevant Vestrum nAMD item
- Publication type: Manuscript
- Source URL(s): https://pubmed.ncbi.nlm.nih.gov/37866681/; https://www.sciencedirect.com/science/article/abs/pii/S2468653023005122
- Full-text status: PubMed/abstract reviewed. Full ScienceDirect text/PDF not accessible in this run.
- Local evidence: texts/emami_2024_driving_vision_pubmed_37866681.txt; source_pages/emami_2024_driving_vision_pubmed_37866681.xml
- Design/data source: Retrospective observational clinical-practice cohort using Vestrum Health data.
- Population/inclusion: Initial diagnosis of nAMD or DME from Jan 1 2014-Jun 30 2019 and at least 1 year of treatment/follow-up. VA analyses required 4 years of treatment/follow-up. Driving-vision analysis required baseline Snellen VA 20/40 or better in the better-seeing eye and maintenance of that threshold for at least 6 months during year 1 after index treatment.
- Index/exposure definition: Index was first anti-VEGF treatment. Exposure was first-year injection frequency, categorized as 1-5, 6-7, or >=8 injections in year 1.
- Follow-up/windows: Driving-vision maintenance evaluated over 4 years after index anti-VEGF treatment.
- Exclusions: Accessible abstract does not list granular exclusions beyond required diagnosis, follow-up, treatment, and baseline/year-1 driving-vision criteria.
- Diagnosis/case definition and codes: nAMD or DME diagnosis in Vestrum Health data; no ICD code list reported in accessible text.
- Treatment/drug definition: Anti-VEGF treatment captured from Vestrum Health data; no drug-code appendix found in accessible records.
- Outcome operational definitions: Driving vision loss was the first clinic visit with VA worse than 20/40 sustained for at least 6 consecutive months. Outcomes included mean VA change over time/by baseline VA and Kaplan-Meier probability of maintaining driving vision, stratified by first-year injection count.
- Statistical methods: Kaplan-Meier estimates for maintaining driving vision and Cox proportional hazards models for baseline clinical factors and first-year injection frequency associated with risk of losing driving vision.
- Code lists, appendices, or supplements: No diagnostic-code, HCPCS, or NDC appendix found in accessible indexed text. Full ScienceDirect article may contain additional details.
- Methods limitations: Excellent reusable operational endpoint for patient-functional vision; full methods and code lists were not accessible.

### 11. Submacular Hemorrhage Rates Following Anti-VEGF Injections for Exudative Age-Related Macular Degeneration (2025)

- ID: kaufmann_2025_submacular_hemorrhage
- Set: Supplemental web-discovered relevant Vestrum nAMD item
- Publication type: Manuscript
- Source URL(s): https://pubmed.ncbi.nlm.nih.gov/39455036/; https://www.sciencedirect.com/science/article/pii/S0002939424004860
- Full-text status: PubMed/abstract reviewed. ScienceDirect/AJO full text and supplemental materials not accessible in this run.
- Local evidence: texts/kaufmann_2025_submacular_hemorrhage_pubmed_39455036.txt; source_pages/kaufmann_2025_submacular_hemorrhage_pubmed_39455036.xml
- Design/data source: Retrospective clinical cohort using Vestrum data. Abstract/source snippets describe all patients in the database from Jan 2015-Nov 2023 and a database scale of 74 private retina centers, about 2.6M patients, and 19.9M encounters as of Jan 2024.
- Population/inclusion: nAMD/exudative AMD eyes receiving anti-VEGF injections. Analysis included 140,915 eyes, 9,107 with submacular hemorrhage.
- Index/exposure definition: Exposure was injection type; SMH timing was assessed relative to prior anti-VEGF injection.
- Follow-up/windows: Database period Jan 2015-Nov 2023. VA assessed before SMH and at 12 months after SMH; PPV assessed within 30 days of SMH and VA at 12 months after PPV.
- Exclusions: Accessible abstract does not list granular exclusions.
- Diagnosis/case definition and codes: nAMD/exudative AMD diagnosis plus accompanying SMH diagnosis in Vestrum data. No ICD code list for nAMD or SMH reported in accessible records.
- Treatment/drug definition: Injection types explicitly included bevacizumab, brolucizumab-dbll, aflibercept, ranibizumab, and faricimab-svoa. No NDC/HCPCS list reported in accessible records.
- Outcome operational definitions: Primary outcome was rate of SMH per injection type. Secondary outcomes were time from SMH diagnosis to last anti-VEGF injection, number of injections before SMH, treatment interval at time of SMH, VA before and 12 months after SMH, PPV within 30 days of SMH, and VA before PPV and 12 months after PPV.
- Statistical methods: Chi-square test of proportions for SMH prevalence/rates and 2-sample independent t-tests for VA data.
- Code lists, appendices, or supplements: ScienceDirect/AJO page indicates supplemental material may be available at the journal site, but accessible snippets did not expose ICD/HCPCS/NDC lists. Use the AJO/ScienceDirect source URL for supplement retrieval if institutional/browser access is available.
- Methods limitations: Good adverse-event/outcome design template; exact SMH/nAMD diagnosis algorithms and supplement contents remain inaccessible.

### 12. Real-World Persistence, Switching, and Reinitiation in Patients with nAMD and DME Treated with Faricimab or Other Anti-VEGF Therapies (2026)

- ID: ko_2026_persistence_switching_reinitiation
- Set: Supplemental web-discovered relevant Vestrum nAMD item
- Publication type: AMCP poster
- Source URL(s): https://medically.gene.com/global/en/unrestricted/ophthalmology/AMCP-2026/amcp-2026-poster-ko-real-world-persistence-switching-an.html; https://medically.gene.com/content/dam/pdmahub/restricted/ophthalmology/amcp-2026/AMCP-2026-poster-ko-real-world-persistence-switching-and-reinitiation-in-patients.pdf
- Full-text status: Poster PDF saved locally and reviewed.
- Local evidence: downloads/ko_2026_persistence_switching_reinitiation_1.pdf; texts/ko_2026_persistence_switching_reinitiation_1.txt
- Design/data source: Noninterventional retrospective secondary use of Vestrum EHR data from Jan 1 2021-May 31 2025.
- Population/inclusion: Eyes with nAMD or DME diagnosis and at least 2 faricimab or anti-VEGF injections between Jan 1 2022 and May 31 2023. Required at least 12 months of pre-index data and at least 24 months of follow-up.
- Index/exposure definition: Index date was first faricimab or anti-VEGF injection. Treatment-naive was no anti-VEGF injection during the 12-month pre-index period; prior anti-VEGF-treated was at least 1 anti-VEGF injection in that period. Persistence was receipt of index treatment without a gap >=180 days.
- Follow-up/windows: At least 24 months post-index follow-up. Sensitivity analysis added eyes reinitiating faricimab after a >=180-day gap to persistent eyes.
- Exclusions: Poster does not expose a detailed exclusion list beyond diagnosis, injection count, pre-index data, and follow-up requirements.
- Diagnosis/case definition and codes: nAMD or DME diagnosis in Vestrum EHR; no ICD code list reported on poster.
- Treatment/drug definition: Faricimab compared with other anti-VEGF therapies. Other anti-VEGF list included aflibercept 2 mg, bevacizumab, brolucizumab, and ranibizumab/biosimilars. No NDC/HCPCS list reported.
- Outcome operational definitions: Post-gap outcomes among nonpersistent eyes were mutually exclusive and hierarchical: switching to anti-VEGF, then reinitiating faricimab, then discontinuing faricimab/all anti-VEGF therapies. Outcomes included persistence, switching, reinitiation, discontinuation, and descriptive patient/eye characteristics.
- Statistical methods: Poster reports descriptive comparative results. Detailed model methods were not presented.
- Code lists, appendices, or supplements: No appendix or code list found in the poster/PDF. Poster PDF is saved locally.
- Methods limitations: Very useful operational definition for persistence/gaps; reasons for discontinuation are not captured and coding/missing-data limitations are noted on poster.

### 13. Treatment Gaps Linked to Worse Long-Term Vision Outcomes in Wet AMD (2026)

- ID: moshfeghi_2026_treatment_gaps
- Set: Supplemental web-discovered relevant Vestrum nAMD item
- Publication type: ARVO presentation coverage / article transcript
- Source URL(s): https://www.retinalphysician.com/issues/2026/may-june/arvo32/
- Full-text status: Retinal Physician web coverage saved and reviewed; underlying ARVO poster/full abstract not found in this run.
- Local evidence: texts/moshfeghi_2026_treatment_gaps_1.txt; texts/moshfeghi_2026_treatment_gaps_2.txt; texts/moshfeghi_2026_treatment_gaps_3.txt
- Design/data source: Retrospective Vestrum Health Database analysis reported in conference coverage.
- Population/inclusion: Treatment-naive wet AMD/nAMD patients managed with intravitreal anti-VEGF therapy.
- Index/exposure definition: Exposure was having a treatment gap of at least 180 days versus no such gap. The 180-day threshold was described as clinically meaningful relative to expected anti-VEGF duration.
- Follow-up/windows: Follow-up reported across years 1-7.
- Exclusions: Detailed inclusion/exclusion criteria were not available in coverage.
- Diagnosis/case definition and codes: Wet AMD/nAMD diagnosis in Vestrum database; no ICD code list reported in coverage.
- Treatment/drug definition: Intravitreal anti-VEGF therapy; no agent list or drug-code list reported in coverage.
- Outcome operational definitions: Outcomes were prevalence of >=180-day treatment gaps over time and VA trajectories comparing gap versus no-gap patients. Coverage reports about 40% had a gap by year 1, up to 80% by year 7, and gap patients had less early improvement and more decline.
- Statistical methods: Coverage does not report formal statistical models.
- Code lists, appendices, or supplements: No diagnostic-code, drug-code, or appendix details found in available coverage. Underlying ARVO abstract/poster should be retrieved if available through ARVO or the authors.
- Methods limitations: Good triangulation for a 180-day gap definition, but insufficient as a standalone methods source.

### 14. Visual Acuity and Durability Outcomes of Faricimab Compared With Other Anti-VEGF Agents Within Routine Clinical Practice for Neovascular Age-Related Macular Degeneration (2026)

- ID: rowe_2026_faricimab_comparison
- Set: Supplemental web-discovered relevant Vestrum nAMD item
- Publication type: Manuscript
- Source URL(s): https://journals.sagepub.com/doi/10.1177/24741264261428749; https://pubmed.ncbi.nlm.nih.gov/41971250/
- Full-text status: PubMed/abstract reviewed. Sage full text/PDF and supplemental DOCX files returned 403 in scripted access. PubMed lists PMCID PMC13068786 as available Apr 9 2027; direct PMC route was 403/not available in this run.
- Local evidence: texts/rowe_2026_faricimab_comparison_pubmed_41971250.txt; source_pages/rowe_2026_faricimab_comparison_pubmed_41971250.xml; metadata/additional_fulltext_fetch_records.json
- Design/data source: Retrospective Vestrum Health treatment and outcomes EMR analysis.
- Population/inclusion: nAMD eyes treated with bevacizumab, ranibizumab, aflibercept, or faricimab from Jan 2021-Dec 2023. Included treatment-naive and treatment-experienced/switch cohorts.
- Index/exposure definition: For treatment-naive eyes, index was first treatment with the relevant agent and outcomes were followed through 6 injections. For switched eyes, switch date/agent was used and outcomes were followed through 2 injections after switch.
- Follow-up/windows: Short-term outcomes through 6 injections in treatment-naive eyes and through 2 injections in switched eyes. Durability used interval between final two injections in each analysis window.
- Exclusions: Detailed exclusions not available in accessible abstract/PubMed text.
- Diagnosis/case definition and codes: nAMD diagnosis in Vestrum EMR; no ICD code list visible in accessible text.
- Treatment/drug definition: Agents were bevacizumab, ranibizumab, aflibercept, and faricimab. No NDC/HCPCS list visible in accessible text.
- Outcome operational definitions: Outcomes were mean VA change and mean days between injections. Durability also measured the proportion of eyes extended >50 days between the final 2 injections. Interpretation adjusted/accounted for baseline VA and switch-date VA differences.
- Statistical methods: Accessible abstract notes adjusted/stratified interpretation for baseline and switch-date VA differences, but does not expose model details.
- Code lists, appendices, or supplements: Sage lists supplemental DOCX materials, but scripted access returned 403. Use the Sage DOI supplement area if browser or institutional access is available: https://journals.sagepub.com/doi/suppl/10.1177/24741264261428749. PMCID PMC13068786 is listed by PubMed as available Apr 9 2027.
- Methods limitations: Potentially important modern faricimab comparator design, but current extraction is abstract-level only until Sage supplement/full text or PMCID access becomes available.

