# NHANES 2021-August 2023-only ophthalmology-related deck notes

## Review of the existing report

- The existing `report.html` correctly separates current-cycle eye-related functioning/symptom measures from historical 2005-2008 ophthalmology examination modules.
- For a 2021-August 2023-only deck, remove all historical visual acuity, retinal imaging, FDT visual field, cataract, glaucoma, AMD, and diabetic-retinopathy estimates from the analytic story.
- The new deck should not use "latest public cycle" as a headline claim unless reverified at build time. Use "NHANES August 2021-August 2023 public files only" instead.
- The defensible current-cycle framing is: NHANES supports nationally representative estimates of seeing difficulty, blurred vision with head movement, diabetes risk context, disability indicators, and PHQ-9 outcomes, but not ophthalmic disease prevalence or examination-confirmed visual impairment.
- Keep the tone descriptive and noncausal. Use "was higher among", "was estimated at", and "was observed among" rather than burden, unmet need, diagnosis, or treatment language.

## Proposed concise slide sequence

### 01 / Scope and central constraint

- Suggested title: `Current-cycle NHANES captures seeing function, not ophthalmic disease`
- Purpose: open with the analytic boundary, not a broad ophthalmology prevalence claim.
- Main content: 2021-August 2023 public files include functioning, balance/symptom, diabetes, and depression screener variables; they do not include public ophthalmology examination, visual acuity, retinal imaging, FDT visual field, cataract, glaucoma, AMD, or diabetic-retinopathy outcomes.
- Visual: large title plus three metrics: `2021-August 2023`, `8,136 adults with adult seeing-function data`, `6,053 participants aged 20-69 with BAQ321B data`.

### 02 / Data architecture and eligible populations

- Suggested title: `The analysis is questionnaire-based and component-specific`
- Show a compact table by file: `DEMO_L`, `FNQ_L`, `BAQ_L`, `DIQ_L`, `DPQ_L`.
- Required columns: file, construct, denominator, weight, key variable(s).
- Important rows:
  - `FNQ410`: adult difficulty seeing even with glasses/contact lenses, age 18+, `WTINT2YR`.
  - `FNQ021`: youth difficulty seeing even with glasses/contact lenses, age 5-17, `WTINT2YR`.
  - `BAQ321B`: blurred vision when moving head, age 20-69, `WTINT2YR`.
  - `DIQ010`: doctor ever told participant had diabetes, adults, `WTINT2YR`.
  - `DPQ010-DPQ090`: PHQ-9 score >=10, adults with DPQ data, `WTMEC2YR`.

### 03 / Adult seeing difficulty prevalence

- Suggested title: `More than one third of adults reported at least some seeing difficulty`
- Lead estimates:
  - Some difficulty or worse: 37.09% (95% CI, 34.63%-39.55%); weighted n about 93.7 million; unweighted n=8,136.
  - A lot of difficulty or cannot do at all: 3.72% (95% CI, 3.08%-4.35%); weighted n about 9.4 million; unweighted n=8,136.
- Visual: paired horizontal bars with 95% CI text. Label the severe threshold clearly so the audience does not conflate it with all seeing difficulty.
- Interpretive note: the item is functional difficulty even with glasses/contact lenses; it is not a visual acuity test and does not identify etiology.

### 04 / Age and demographic gradients in seeing difficulty

- Suggested title: `Severe seeing difficulty varied by age, sex, and race/ethnicity`
- Highlight selectively, without overclaiming:
  - Age 80+: 8.23% vs age 18-39: 2.13%; absolute difference 6.10 percentage points.
  - Female: 4.57% vs male: 2.81%.
  - Other/multiracial: 5.77%, Other Hispanic: 5.20%, Non-Hispanic White: 3.42%, Non-Hispanic Black: 4.02%, Mexican American: 3.75%, Non-Hispanic Asian: 1.62%.
- Visual: small multiples or a dot-and-whisker chart. Include unweighted n and suppress/flag sparse estimates if precision rules require it.
- Wording guardrail: call these subgroup estimates, not disparities, unless statistical testing and covariate adjustment are added.

### 05 / Blurred vision with head movement

- Suggested title: `Blurred vision with head movement was reported by about one in ten adults aged 20-69`
- Lead estimate: 10.14% (95% CI, 9.09%-11.18%); weighted n about 21.1 million; unweighted n=6,053.
- Subgroup signals:
  - Female: 12.58% vs male: 7.61%.
  - Other Hispanic: 17.79% vs Non-Hispanic White: 8.37%.
  - Age groups: 20-39, 8.85%; 40-54, 11.57%; 55-69, 10.56%.
- Visual: one main metric plus a two-panel stratified bar/dot chart.
- Interpretive note: BAQ321B is embedded in a dizziness/light-headedness/balance section and asks about blurring when moving the head; do not present it as an ophthalmic diagnosis.

### 06 / Severe seeing difficulty and PHQ-9

- Suggested title: `Moderate-to-severe depressive symptoms were more frequent among adults with severe seeing difficulty`
- Lead contrast:
  - PHQ-9 score >=10 among adults with severe seeing difficulty: 32.03% (95% CI, 25.51%-38.55%); n=211.
  - Without severe seeing difficulty: 12.02% (95% CI, 10.44%-13.60%); n=5,238.
  - Absolute difference: 20.01 percentage points; prevalence ratio: 2.66.
- Visual: two bars with CI brackets and a small difference callout.
- Wording guardrail: this is a cross-sectional association. Do not imply directionality between seeing difficulty and depressive symptoms.

### 07 / Diabetes risk context

- Suggested title: `Diagnosed diabetes was more common among adults with severe seeing difficulty`
- Lead contrast:
  - Severe seeing difficulty: 24.96%.
  - No severe seeing difficulty: 10.63%.
  - Absolute difference: 14.33 percentage points; prevalence ratio: 2.35.
- Visual: paired bars and a methods footnote that DIQ010 is self-reported doctor diagnosis.
- Interpretive note: diabetes is ophthalmology-relevant risk context, but 2021-August 2023 public files do not identify diabetic retinopathy or diabetic eye disease.

### 08 / Methods and reproducibility

- Suggested title: `Methods used survey design, component weights, and prespecified binary definitions`
- Include:
  - Public CDC XPT files linked by `SEQN`.
  - `WTINT2YR` for interview/questionnaire outcomes; `WTMEC2YR` for DPQ/PHQ-9 estimates.
  - `SDMVSTRA` and `SDMVPSU` for Taylor-linearized standard errors.
  - Adult severe seeing difficulty: `FNQ410 in {3, 4}`; some-or-more: `FNQ410 in {2, 3, 4}`.
  - Youth severe seeing difficulty: `FNQ021 in {3, 4}`.
  - Blurred vision with head movement: `BAQ321B = 1` among age 20-69.
  - PHQ-9 score >=10 from valid `DPQ010-DPQ090` values 0-3.
  - Report weighted prevalence, 95% CI, weighted population count, and unweighted analytic n.
- Visual: compact methods grid, not dense paragraphs.

### 09 / Interpretation and limits

- Suggested title: `Findings support current function and symptom context, not disease prevalence`
- Three-column close:
  - Supports: current national estimates for seeing difficulty, severe seeing difficulty, blurred vision with head movement, PHQ-9 context, and diabetes context.
  - Requires caution: self-report, cross-sectional associations, component-specific denominators, DPQ/MEC subsample weights, low unweighted n in severe-seeing subgroups.
  - Should not imply: visual acuity impairment, refractive error, cataract, glaucoma, AMD, diabetic retinopathy, retinal lesions, visual-field loss, incidence, progression, or causal effects.
- Visual: dark caveat panel plus source footnotes.

## Current-cycle estimates worth using

- Adult seeing difficulty, some or more: 37.09% (95% CI, 34.63%-39.55%); weighted n=93,706,999; unweighted n=8,136.
- Adult severe seeing difficulty: 3.72% (95% CI, 3.08%-4.35%); weighted n=9,393,195; unweighted n=8,136.
- Youth severe seeing difficulty, age 5-17: 1.08% (95% CI, 0.76%-1.39%); weighted n=598,967; unweighted n=2,782.
- Blurred vision with head movement, age 20-69: 10.14% (95% CI, 9.09%-11.18%); weighted n=21,083,876; unweighted n=6,053.
- Diagnosed diabetes among adults: 11.15% (95% CI, 9.87%-12.43%); weighted n=27,416,508; unweighted n=7,876.
- PHQ-9 score >=10 among adults with severe seeing difficulty: 32.03% vs 12.02% without severe seeing difficulty.
- Diagnosed diabetes among adults with severe seeing difficulty: 24.96% vs 10.63% without severe seeing difficulty.

## Data-quality and source-verification cautions

- Do not use `data/processed/summary_estimates.csv` for current-cycle PHQ-9 claims; it contains implausible 100% PHQ rows and appears inconsistent with `output/current_eye_related_estimates.csv` and the new current-cycle deep-dive output.
- Treat the new `output/current_2021_2023_*` files as useful but recently added; before building final slides, rerun or independently verify the script that produced them.
- Do not headline the `Enhanced disability by severe seeing difficulty` contrast. The enhanced disability indicator includes seeing difficulty in its definition, so the 100% estimate among severe-seeing participants is expected and partly tautological.
- Include precision rules before finalizing subgroup slides: minimum unweighted n, sparse numerator/event flags, relative standard error or confidence interval width, and design degrees of freedom.
- Verify whether any additional public 2021-August 2023 component releases affect available variables before final HTML build; CDC release notes state that additional files may be posted after processing and disclosure review.

## Source anchors

- NHANES August 2021-August 2023 release notes: https://wwwn.cdc.gov/nchs/nhanes/ContinuousNhanes/releasenotes.aspx?Cycle=2021-2023
- Functioning questionnaire `FNQ_L`: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/FNQ_L.htm
- Balance questionnaire `BAQ_L`: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BAQ_L.htm
- Depression screener `DPQ_L`: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DPQ_L.htm
- Diabetes questionnaire `DIQ_L`: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DIQ_L.htm
- CDC VEHSS NHANES source page for historical eye-exam context and limitations: https://www.cdc.gov/vision-health-data/data-sources/national-health-nutrition-examination-survey.html
