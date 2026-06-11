# Targeted Capped-Crawl Follow-Up

Generated: May 28, 2026

This pass targeted only URLs that prior manifests marked as capped or uncollected seed gaps. It did not intentionally retry earlier 403, 404, timeout, invalid URL, or other access-failure rows.

## Totals

- Manifest rows in this follow-up: 550
- Collected source/text records: 537
- Failed records from targeted capped-gap URLs or first-level links: 13
- Skipped by state success cap: 0

## Collection By State

| State | Collected | Failed | Therapy hit groups | Rationale hit groups |
|---|---:|---:|---|---|
| Illinois | 34 | 0 | infectious_disease, oncology_rare_specialty, cardio_renal_metabolic, cns_behavioral_migraine | final_implementation, clinical_efficacy_safety, public_manufacturer_input, comparative_class_review |
| Indiana | 41 | 0 | oud_pain, diabetes_glp1_obesity, infectious_disease, immunology_biologics | public_manufacturer_input, pa_step_criteria, clinical_efficacy_safety, utilization_controls |
| Iowa | 35 | 0 | diabetes_glp1_obesity, oncology_rare_specialty, infectious_disease, oud_pain | clinical_efficacy_safety, cost_rebate, public_manufacturer_input, final_implementation |
| Kansas | 30 | 1 | oncology_rare_specialty, diabetes_glp1_obesity, cns_behavioral_migraine, cardio_renal_metabolic | clinical_efficacy_safety, utilization_controls, pa_step_criteria, public_manufacturer_input |
| Kentucky | 57 | 1 | respiratory_allergy, diabetes_glp1_obesity, cardio_renal_metabolic, cns_behavioral_migraine | clinical_efficacy_safety, pa_step_criteria, final_implementation, utilization_controls |
| Louisiana | 52 | 0 | oud_pain, respiratory_allergy, diabetes_glp1_obesity, infectious_disease | final_implementation, clinical_efficacy_safety, pa_step_criteria, public_manufacturer_input |
| Maine | 51 | 0 | oud_pain, infectious_disease, cns_behavioral_migraine, respiratory_allergy | final_implementation, clinical_efficacy_safety, pa_step_criteria, utilization_controls |
| Maryland | 8 | 4 | oud_pain, respiratory_allergy, infectious_disease, diabetes_glp1_obesity | clinical_efficacy_safety, final_implementation, pa_step_criteria, cost_rebate |
| Minnesota | 2 | 0 | none | none |
| Mississippi | 19 | 0 | oud_pain, immunology_biologics, oncology_rare_specialty, respiratory_allergy | cost_rebate, public_manufacturer_input, clinical_efficacy_safety, final_implementation |
| Montana | 29 | 1 | diabetes_glp1_obesity, immunology_biologics, respiratory_allergy, oud_pain | final_implementation, clinical_efficacy_safety, public_manufacturer_input, comparative_class_review |
| Nebraska | 68 | 0 | oud_pain, cns_behavioral_migraine, respiratory_allergy, oncology_rare_specialty | utilization_controls, pa_step_criteria, clinical_efficacy_safety, public_manufacturer_input |
| Nevada | 24 | 0 | oud_pain, respiratory_allergy, diabetes_glp1_obesity, immunology_biologics | public_manufacturer_input, utilization_controls, final_implementation, clinical_efficacy_safety |
| New Hampshire | 22 | 0 | respiratory_allergy, cardio_renal_metabolic, oud_pain, infectious_disease | clinical_efficacy_safety, pa_step_criteria, final_implementation, comparative_class_review |
| New Jersey | 0 | 3 | none | none |
| West Virginia | 19 | 3 | oud_pain, diabetes_glp1_obesity, immunology_biologics, cardio_renal_metabolic | final_implementation, clinical_efficacy_safety, pa_step_criteria, comparative_class_review |
| Wisconsin | 39 | 0 | infectious_disease, immunology_biologics, oud_pain, cns_behavioral_migraine | pa_step_criteria, cost_rebate, final_implementation, public_manufacturer_input |
| Wyoming | 7 | 0 | diabetes_glp1_obesity, respiratory_allergy, infectious_disease, cardio_renal_metabolic | clinical_efficacy_safety, comparative_class_review, pa_step_criteria, final_implementation |

## Most Frequent Therapy Signals

- oud_pain: 267 collected records
- diabetes_glp1_obesity: 232 collected records
- infectious_disease: 223 collected records
- respiratory_allergy: 221 collected records
- cns_behavioral_migraine: 195 collected records
- oncology_rare_specialty: 192 collected records
- immunology_biologics: 188 collected records
- cardio_renal_metabolic: 177 collected records

## Most Frequent Rationale Signals

- final_implementation: 359 collected records
- clinical_efficacy_safety: 352 collected records
- pa_step_criteria: 325 collected records
- public_manufacturer_input: 299 collected records
- cost_rebate: 234 collected records
- utilization_controls: 232 collected records
- comparative_class_review: 200 collected records

## Residual Failures

- Maryland: `https://health.maryland.gov/mmcp/pap/docs/P%26T%20MEETING/Web%20agenda%20for%20PT%20November%202025.pdf` - HTTP 404
- Maryland: `https://health.maryland.gov/mmcp/pap/pages/Public-Meeting-Announcement-and-Procedures-for-Public-Testimony.aspx` - HTTP 404
- Maryland: `https://health.maryland.gov/mmcp/pap/pages/pharmacy-therapeutics-committee-members.aspx` - HTTP 404
- Maryland: `https://health.maryland.gov/mmcp/pap/pages/public-meeting-announcement-and-procedures-for-public-testimony.aspx` - HTTP 404
- New Jersey: `https://nj.gov/humanservices/dmahs/boards/durb/members/` - HTTP 404
- New Jersey: `https://www.nj.gov/humanservices/dmahs/boards/durb/` - TimeoutError: The read operation timed out
- New Jersey: `https://www.nj.gov/humanservices/dmahs/boards/durb/meeting/` - HTTP 404
- West Virginia: `https://dhhr.wv.gov/bms/BMS%20Pharmacy/Pages/Preferred-Drug-List.aspx` - HTTP 404
- West Virginia: `https://dhhr.wv.gov/bms/BMS%20Pharmacy/PharmTheraComm/Pages/default.aspx` - HTTP 404
- West Virginia: `https://dhhr.wv.gov/bms/provider/documents/manuals/chapter_518_pharmacy_services.pdf` - HTTP 404
- Kansas: `http://www.kancare.ks.gov/policies-and-reports/kdhe-eligibility-policy/policy-log` - HTTP 403
- Kentucky: `https://www.chfs.ky.gov/agencies/dms/dpo/ppb/Documents/KyCommissionerDecisionsMay2023.pdf` - URLError: <urlopen error [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted>
- Montana: `https://dphhs.mt.gov/childcareprovidersdashboard` - HTTP 404
