# Link and download inventory

Primary Vestrum page: https://www.vestrumhealth.com/media.php

Note: several Vestrum-hosted historical PDF paths now 301 redirect to the CorEvitas/PPD Vestrum real-world-data landing page rather than serving the original PDF. I saved those redirect targets and used PubMed/PMC/other stable records where available. Publisher pages from Healio, Sage, HCPLive, Bayer, and ScienceDirect sometimes returned 403 or bot-check pages to scripted downloads; those failures are logged in metadata/download_records.json and metadata/supplemental_fetch_records.json.

## Included and extracted

- 2018 - Real-world Outcomes of Anti-VEGF Therapy in nAMD in the United States (Manuscript)
  - Source: https://www.sciencedirect.com/science/article/pii/S246865301730297X
  - Local: downloads/ciulla_2018_namd_real_world_outcomes_hubspot.pdf; source_pages/ciulla_2018_namd_real_world_outcomes_pubmed_31047372.xml
  - Set: Vestrum website indexed

- 2021 - Visual Acuity Outcomes in Patients Receiving Frequent Treatment of nAMD in Clinical Practice (Manuscript; ASRS 2018 presentation was Vestrum-linked)
  - Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC9979036/
  - Local: source_pages/pmc_fetch_https_eutils_ncbi_nlm_nih_gov_entrez_eutils_efetch_fcgi_db_pmc_id_9979036_rettyp.txt
  - Set: Vestrum website indexed / ASRS presentation follow-up

- 2020 - Visual Acuity Outcomes and Anti-VEGF Therapy Intensity in nAMD Patients: 49,485 Eyes (Manuscript)
  - Source: https://www.sciencedirect.com/science/article/pii/S2468653019302805
  - Local: source_pages/ciulla_2020_va_intensity_49485_pubmed_31324588.xml
  - Set: Vestrum website indexed

- 2020 - SIERRA-AMD (Manuscript)
  - Source: https://www.sciencedirect.com/science/article/pii/S246865301930569X
  - Local: source_pages/khanani_2020_sierra_amd_pubmed_31812631.xml
  - Set: Vestrum website indexed

- 2021 - Increasing Incidence and Prevalence of Common Retinal Diseases in U.S. Retina Practices (Manuscript)
  - Source: https://pubmed.ncbi.nlm.nih.gov/33471912/
  - Local: source_pages/vestrum_media_page.html; source_pages/rosenblatt_2021_incidence_prevalence_*.xml attempted
  - Set: Vestrum website indexed

- 2021 - Characterizing Progression to Neovascular AMD in Fellow Eyes (Manuscript)
  - Source: https://pubmed.ncbi.nlm.nih.gov/34038686/
  - Local: source_pages/vestrum_media_page.html; downloads/starr_2021_fellow_eye_progression_* attempted
  - Set: Vestrum website indexed

- 2022 - Longer-Term Anti-VEGF Therapy Outcomes in nAMD, DME, and RVO-related ME (Manuscript)
  - Source: https://pubmed.ncbi.nlm.nih.gov/35381391/
  - Local: downloads/ciulla_2022_longer_term_outcomes.pdf
  - Set: Supplemental web-discovered

- 2023 - Levodopa Is Associated with Reduced Development of nAMD (Manuscript)
  - Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC10524303/
  - Local: source_pages/hyman_2023_levodopa_namd_PMC10524303_bioc.json
  - Set: Supplemental web-discovered

- 2023 - Vision Protection Therapy for Prevention of nAMD (Manuscript)
  - Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC10550910/
  - Local: source_pages/luttrull_2023_vpt_prevention_PMC10550910_bioc.json
  - Set: Supplemental web-discovered

- 2024 - Maintenance of Vision Needed to Drive after Anti-VEGF Therapy in nAMD and DME (Manuscript)
  - Source: https://pubmed.ncbi.nlm.nih.gov/37866681/
  - Local: source_pages/emami_2024_driving_vision_pubmed_37866681.xml attempted
  - Set: Supplemental web-discovered

- 2025 - Submacular Hemorrhage Rates Following Anti-VEGF Injections for Exudative AMD (Manuscript)
  - Source: https://pubmed.ncbi.nlm.nih.gov/39455036/
  - Local: source_pages/kaufmann_2025_submacular_hemorrhage_pubmed_39455036.xml attempted
  - Set: Supplemental web-discovered

- 2026 - Real-World Persistence, Switching, and Reinitiation in nAMD and DME (AMCP poster)
  - Source: https://medically.gene.com/content/dam/pdmahub/restricted/ophthalmology/amcp-2026/AMCP-2026-poster-ko-real-world-persistence-switching-and-reinitiation-in-patients.pdf
  - Local: downloads/ko_2026_persistence_switching_reinitiation_1.pdf
  - Set: Supplemental web-discovered

- 2026 - Treatment Gaps Linked to Worse Long-Term Vision Outcomes in Wet AMD (ARVO presentation article/transcript)
  - Source: https://www.retinalphysician.com/issues/2026/may-june/arvo32/
  - Local: downloads/moshfeghi_2026_treatment_gaps_1.html; downloads/moshfeghi_2026_treatment_gaps_2.html; downloads/moshfeghi_2026_treatment_gaps_3.html
  - Set: Supplemental web-discovered

- 2026 - Visual Acuity and Durability Outcomes of Faricimab Compared With Other Anti-VEGF Agents in nAMD (Manuscript)
  - Source: https://journals.sagepub.com/doi/abs/10.1177/24741264261428749
  - Local: source_pages/rowe_2026_faricimab_comparison_pubmed_41971250.xml
  - Set: Supplemental web-discovered


## Excluded Vestrum media candidates

- Ophthalmology Retina Enters Year 4 | Some Comments on Neovascular AMD and DME
  - Reason: Editorial/commentary; does not itself evaluate Vestrum wet AMD patients.
  - URL: https://www.vestrumhealth.com/vestrum-health-documents/SomeCommentsonNeovascularAgeRelatedMacularDegenerationandDiabeticMacularEdemaAndrewPSchachatMD.pdf

- Real-World Papers, Prophylaxis for Intravitreal Injections...
  - Reason: Editorial/commentary; discusses Vestrum real-world nAMD paper but is not a database analysis.
  - URL: https://www.vestrumhealth.com/vestrum-health-documents/RealWorldPapersProphylaxisforIntravitrealInjectionsFluoresceinAngiographyandNeovascularAgeRelatedMacularDegenerationandAntiVascularEndothelialGrowthFactorSafety.pdf

- Visual Acuity Outcomes and Anti-VEGF Therapy Intensity in Diabetic Macular Edema
  - Reason: Vestrum media page card is disease/topic DME despite URL filename containing nAMD; excluded from wet AMD set.
  - URL: https://www.vestrumhealth.com/vestrum-health-documents/VisualAcuityOutcomesandAntiVascularEndothelialGrowthFactorTherapyIntensityinNeovascularAgeRelatedMacularDegenerationPatients.pdf

- Epidemiology of Retinal Diseases - AMD, DED most common retinal conditions in the United States
  - Reason: News/video item appears to summarize epidemiology findings; saved as source context via URL if needed but not a primary wet AMD database publication.
  - URL: https://www.healio.com/news/ophthalmology/20200726/video-iluvien-delays-dr-progression-in-patients-lost-to-followup

- The progression of retinal disease in eyes of patients lost to follow-up for at least 6 months
  - Reason: Vestrum card is tagged DR and title is not wet AMD despite link URL containing amd/ded; not in wet AMD set.
  - URL: https://www.modernretina.com/view/amd-ded-most-common-retinal-conditions-in-us
## Detailed Methods Update (2026-06-03)

Additional review focused on full text and supplemental methods where accessible. New/updated outputs:

- `methods_comparison.md`: expanded publication-level methods extraction with operational definitions, code availability, appendix/supplement pointers, and source limitations.
- `methods_comparison.csv`: same detailed extraction in wide CSV format.
- `methods_comparison_detailed.md` and `methods_comparison_detailed.csv`: duplicate detailed versions for explicit discoverability.
- `optimal_common_approach_summary.md`: revised synthesis of the most common/reusable Vestrum wet AMD design choices.
- `metadata/additional_fulltext_fetch_records.json`: logged additional attempts to fetch Moshfeghi 2021 supplement, Rowe 2026 PMCID route, SIERRA-AMD ScienceDirect HTML, and Rosenblatt poster PDF.

Access limitations recorded in the comparison:

- Many Vestrum nAMD papers do not publish ICD/NDC/HCPCS lists in accessible full text.
- Moshfeghi 2021 supplement endpoint returned an HHS proof-of-work HTML stub rather than a usable DOCX during scripted download.
- Rowe 2026 PubMed lists PMCID `PMC13068786` as available Apr 9 2027; Sage full text/supplements were not script-accessible in this run.
- Rosenblatt poster PDF URL returned 404 during the detailed retry.
- ScienceDirect pages were intermittently accessible through browser/web text view but not reliably downloadable by script.
