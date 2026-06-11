# IRIS Registry DME Publication Methods Comparison

Search date: June 3, 2026. Anchor source: AAO IRIS Registry research/publication pages, supplemented with PubMed E-utilities and directly downloadable conference/sponsor materials because newer DME IRIS materials were not all listed on the AAO page.

## What Was Saved

- `source_pages/`: AAO IRIS research and annual meeting pages, PubMed E-utilities search/summary records, and other source pages.
- `downloads/`: PubMed XML, accessible article pages, posters, presentations, and download-error files for inaccessible/blocked items.
- `text/`: text extracted from saved PDFs/HTML/XML.
- `analysis/methods_extraction.csv`: per-publication methods table.
- `analysis/methods_extraction_detailed.md`: article-by-article operational definitions, including code-list/supplement locations.
- `download_manifest.json`, `linked_attachment_manifest.json`, and `publication_seed_list.json`: audit trail for attempted downloads.

## Core AAO IRIS Registry DME Publications

The AAO IRIS Registry pages exposed five DME-relevant published papers and one AAO 2017 meeting listing:

| Item | Status |
|---|---|
| 2017 AAO PA017 treatment-pattern presentation | AAO page saved; no direct downloadable presentation file found. |
| Cantrell 2020 treatment patterns | AAO-listed manuscript; PubMed/Elsevier XML saved; publisher HTML blocked locally. |
| Malhotra 2021 disparities at anti-VEGF initiation | AAO-listed manuscript; PubMed XML saved; publisher HTML blocked locally. |
| Greenlee 2022 socioeconomic disparities and anti-VEGF/VA outcomes | AAO-listed manuscript; PubMed XML saved; publisher HTML blocked locally. |
| Maturi 2024 race/insurance and DR/DME treatment outcomes | AAO-listed manuscript; PMC full text saved. |
| Kuo 2024 long-term DME treatment patterns up to 6 years | AAO-listed manuscript; PubMed XML saved; publisher HTML blocked locally. |

## Additional DME IRIS Materials Found

Additional DME IRIS materials found outside the AAO publication list include BMC/PMC article text for the 2024 initial-dose analysis, FARETINA-DME manuscripts indexed in PubMed, FARETINA-DME posters/presentations from ASRS/ARVO/Hawaiian Eye/Macula Society, and linked claims + IRIS DME analyses presented at ARVO/ISPOR 2026.

I also saved three secondary IRIS studies where DME is an outcome/subgroup rather than the primary enrolled cohort: PDR treatment trends with DME status, sickle cell trait/disease with DME as a diabetic-retinopathy outcome, and endophthalmitis after biologic injections with a DME/DR indication subgroup. One PubMed hit was excluded as a false positive because it used the All of Us database, not IRIS.

## Common Methods Pattern

The dominant design is retrospective analysis of deidentified EHR-derived IRIS Registry data. The most common DME-specific cohort definition is:

- Adult patients/eyes with documented DME.
- Anti-VEGF treatment initiation as the index event.
- A 12-month pre-index lookback to classify treatment-naive status or prior anti-VEGF exposure.
- Laterality-known eye-level analysis when treatment, VA, and CST are evaluated.
- Baseline VA window commonly within 60 days before index for older anti-VEGF studies; faricimab studies often use VA on/after index and injection-visit windows.
- Exclusions often include prior anti-VEGF within 12 months for treatment-naive cohorts, prior intravitreal steroid use for some anti-VEGF analyses, missing laterality/demographics, insufficient pre-index medical data, and inadequate follow-up.

## Outcomes Previously Studied

- Initial DME management: observation/no treatment, anti-VEGF, laser, steroid, combination therapy.
- Anti-VEGF utilization: injection number, frequency, interval, agent type, switch, reinitiation, discontinuation.
- Visual outcomes: best-documented or best-recorded VA, ETDRS-letter conversion, VA change over 1-6 years.
- Anatomic outcomes in newer FARETINA-DME work: CST change, CST thresholds, proportion with meaningful CST reduction.
- Equity/disparity outcomes: race, ethnicity, insurance, geography, treatment intensity, baseline VA/DR severity, longitudinal VA.
- Treatment burden/economic outcomes: retina visits, injection burden, drug costs, DME-related costs in linked claims + IRIS analyses.
- Safety or adjacent outcomes: endophthalmitis incidence by indication and DME/DR subgroup; DME status/complications in PDR or diabetes subgroups.

## Most Reusable Approach For A New IRIS DME Study

The most defensible template from the saved corpus is the Kuo/Singh long-term anti-VEGF design:

1. Define the unit of analysis at the eye level and require known laterality.
2. Require documented DME near the treatment index date.
3. Use first anti-VEGF/faricimab injection as index.
4. Apply a 12-month pre-index lookback to classify treatment-naive versus previously treated.
5. Require a baseline VA window, and pre-specify VA cleaning/conversion rules.
6. Include injection counts, intervals, agent switching, discontinuation/reinitiation, and VA change as core outcomes.
7. Add CST only as a prespecified subgroup unless OCT/CST completeness is adequate, because the posters show CST availability can be limited.
8. Stratify by baseline VA, treatment-naive status, insurance, race/ethnicity, geography, and initial agent.
9. Treat discontinuation carefully: several sources warn that registry data may not distinguish successful stopping, transfer of care, and loss to follow-up.
10. Preserve missingness and selection limitations explicitly, especially for VA timing, CST capture, and data contributed through routine clinical care.

## Practical Caveats

- Several publisher pages returned 403 from the local environment; those failures are preserved as `.error.txt` files and PubMed XML was saved when available.
- Some PMC PDF URLs returned download-preparation placeholder files; the PMC HTML full text was still saved and extracted.
- The ARVO 2025 direct PDF URL identified by search returned 404; the item remains documented as identified but not downloaded.
- Sponsor/conference PDFs sometimes duplicate the same underlying FARETINA-DME study at different follow-up cuts; the CSV keeps them as separate saved files because methods and inclusion windows evolved.
