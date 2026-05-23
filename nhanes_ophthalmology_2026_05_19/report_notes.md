# NHANES ophthalmology outcomes slide report skeleton

## Working frame

- Artifact: concise HTML slide report, not final HTML in this notes pass
- Visual target: tan editorial slide system with cream paper field, black ink, compact citation markers, dark analytic panels, and lime/blue/orange/pink/red only as data accents
- Voice: neutral, scientific, Value in Health-style wording; descriptive and noncausal unless a model and estimand explicitly support causal language
- Scope: NHANES public-use vision and ophthalmology examination data; emphasize that ophthalmology imaging/field data are historical public-use data, not current clinical surveillance
- Core message: NHANES can support nationally representative estimates of selected ophthalmic outcomes, but interpretation depends on component-specific eligibility, eye-level definitions, gradability, field-test reliability, and combined-cycle survey weighting

## Suggested slide sequence

### 01 / Analytic question and scope

- Open with the population-health question rather than a disease-market frame
- Suggested title: `What NHANES can tell us about ophthalmology outcomes`
- Content: define the report as a descriptive summary of examination-based ophthalmology outcomes in the US civilian, noninstitutionalized population within component-eligible age groups
- Visual note: large title, one dark panel for scope limits, three small metric placeholders for `data years`, `eligible ages`, and `outcome domains`

### 02 / Data architecture

- Show the distinction between the broader vision examination and the ophthalmology components
- Vision examination: 1999-2008; distance visual acuity, objective refraction, keratometry, lensometry where applicable, and near vision for older adults
- Ophthalmology components: 2005-2008; retinal imaging and Frequency Doubling Technology visual fields among adults aged 40 years and older
- Visual note: two-lane timeline, with a narrower 2005-2008 lane nested under the longer 1999-2008 vision lane

### 03 / Outcome map

- Organize outcomes by measurement source, not by clinical narrative
- Candidate rows: visual acuity impairment, refractive error, diabetic retinopathy, age-related macular degeneration, visual field loss, and glaucoma-suggestive imaging/field findings
- Each row should show: data component, eligible denominator, eye-level rule, participant-level rule, and required quality filter
- Language guardrail: use `glaucoma-suggestive findings` unless a validated case definition is prespecified; do not imply adjudicated clinical glaucoma from FDT or cup-to-disc findings alone

### 04 / Visual acuity and refractive outcomes

- Present distance visual acuity using presenting acuity and, where available by protocol, acuity incorporating objective refraction
- Define impairment thresholds before analysis, such as worse than 20/40, and specify better-seeing eye, worse-seeing eye, or eye-specific reporting
- Distinguish presenting impairment, correctable impairment, and uncorrectable impairment if the selected variables permit that contrast
- Visual note: compact stacked bars by age group with a footnote clarifying threshold and eye rule

### 05 / Retinal imaging outcomes

- Describe nonmydriatic retinal imaging as the source for diabetic retinopathy, age-related macular degeneration, and selected retinal findings
- State that two 45-degree digital retinal images were obtained per eye, centered on the macula and optic nerve, with grading by reading-center protocols
- Show gradable denominators separately from disease-negative counts
- Visual note: matrix layout with disease domains as columns and denominator states as rows

### 06 / Visual field outcomes

- Describe Frequency Doubling Technology testing as a screening-style visual field component rather than full clinical perimetry
- Include the Humphrey Matrix N-30-5 protocol, 19 visual field locations, two tests per eye, and reliability indicators
- Report abnormal visual field status only after applying reliability and completeness rules
- Visual note: small schematic grid for field-test logic, paired with a concise denominator flow

### 07 / Glaucoma-suggestive construct

- Present a prespecified construct if the deck includes glaucoma-related estimates
- Candidate inputs: optic disc/cup-to-disc measures, re-read imaging variables where used, FDT final eye status, self-reported glaucoma history, and medication variables if incorporated
- Required wording: `glaucoma-suggestive imaging and visual-field findings`, `probable glaucoma by prespecified algorithm`, or another explicit definition; avoid unsupported diagnosis language
- Visual note: decision-tree panel showing which inputs qualify a participant-level positive finding

### 08 / Survey design and estimation

- State that estimates must account for NHANES complex survey design, including sample weights, strata, and primary sampling units
- Use examination weights for examination-derived outcomes; use the most restrictive relevant weight when combining questionnaire and examination variables
- For 2005-2008 ophthalmology outcomes, combine the two 2-year cycles using adjusted exam weights
- For 1999-2008 vision outcomes, construct combined-cycle weights following NCHS guidance, including the 1999-2002 four-year weight handling where applicable
- Visual note: method card with `weighted prevalence`, `95% CI`, `unweighted n`, and `precision flag`

### 09 / Missingness, gradability, and reliability

- Show a denominator cascade: interviewed, MEC examined, component eligible, component attempted, gradable or reliable data, analytic sample
- Retinal imaging: separate missing images, ungradable images, incomplete fields, and disease-negative findings
- Visual fields: separate not done, incomplete, insufficient, unreliable, and positive/normal final status
- Do not classify missing, ungradable, insufficient, or unreliable tests as disease-negative
- Visual note: flow diagram with counts/percentages once analysis is available

### 10 / Interpretation and limitations

- Use measured language around representativeness, historical data years, cross-sectional design, component-specific eligibility, and measurement limits
- Suggested title: `Interpretation depends on measurement and denominator choices`
- Content: summarize what the estimates can support, what they should not be used to claim, and which sensitivity analyses are needed
- Visual note: three-column closing slide: `supports`, `requires caution`, `should not imply`

### 11 / Methods appendix

- Reserve one appendix-style slide for final definitions and reproducibility details
- Include data files, cycle years, variable lists, weights, survey design variables, outcome algorithms, denominator rules, precision criteria, software, and source links
- Visual note: dense but readable table with compact source markers; no long URLs in body slides

## Methods details the final deck must include

- Data source and cycles: NHANES continuous public-use data; vision examination 1999-2008; retinal imaging and FDT visual fields 2005-2008
- Target population: US civilian, noninstitutionalized population represented by NHANES, restricted to component-eligible ages and completed examination status
- Eligibility by component: vision examination eligibility by cycle and age; retinal imaging and FDT eligibility among adults aged 40 years and older; near-vision eligibility among adults aged 50 years and older where used
- Exclusion rules: inability to see light with both eyes open, severe eye infection, eye patches or eye-specific limitations, and component-specific not-done reasons
- Component linkage: use `SEQN` to link demographics, questionnaire, vision examination, retinal imaging, visual field, diabetes/laboratory, medication, and other covariate files
- Visual acuity definitions: presenting visual acuity variables, objective-refraction acuity variables, threshold selected for impairment, and whether the analysis uses better-eye, worse-eye, either-eye, or eye-specific definitions
- Refractive error definitions: spherical equivalent formula, myopia/hyperopia/astigmatism thresholds, and whether cataract surgery or refractive surgery variables are used for sensitivity analyses
- Retinal imaging definitions: diabetic retinopathy algorithm, AMD algorithm, other retinal lesions if shown, eye-level to participant-level aggregation, and gradability requirements
- Glaucoma-related definitions: explicit algorithm and terminology, including whether it uses FDT final eye status, optic disc/cup-to-disc variables, 2012 re-read variables, self-report, medication, or combinations
- FDT visual field definitions: N-30-5 screening protocol, two tests per eye, 19 field locations, 2-2-1 algorithm if used, false-positive and blind-spot reliability criteria, technician-noted fixation, insufficient and unreliable status handling
- Denominator handling: component-eligible denominator, attempted-exam denominator, gradable/reliable denominator, analytic complete-case denominator, and whether estimates are among all eligible participants or only those with gradable/reliable exams
- Missingness plan: treatment of missing, not done, partial, ungradable, insufficient, and unreliable results; sensitivity analyses for complete-case assumptions and gradability-related selection
- Weighting plan: MEC examination weights for examination outcomes; adjusted multi-cycle weights for combined cycles; special handling of 1999-2002 four-year weights when building 1999-2008 vision estimates
- Survey design: include `SDMVSTRA`, `SDMVPSU`, and appropriate weights; use survey-aware procedures for prevalence estimates, regression, standard errors, and confidence intervals
- Precision rules: report weighted prevalence with 95% confidence intervals and unweighted analytic n; flag or suppress estimates with small unweighted denominators, sparse events, high relative standard error, or NCHS-defined reliability concerns
- Subgroup plan: prespecify age categories, sex, race/ethnicity categories available in the cycle, diabetes status, insurance/access variables if used, and avoid post hoc subgroup overinterpretation
- Modeling plan: if associations are included, state the model family, covariate adjustment set, estimand, survey design handling, and that cross-sectional associations do not establish temporality
- Reproducibility: list data file names, variable names, code version/date, software and package versions, outcome-definition table, and source URLs
- Source transparency: use compact citation markers on slides and a source appendix rather than visible long URLs in main analytic slides

## Language guidance

- Prefer: `was associated with`, `was estimated at`, `among component-eligible adults`, `examination-based estimate`, `weighted prevalence`, `gradable images`, `reliable visual field result`
- Avoid: `burden proves`, `patients suffer from`, `dramatic unmet need`, `diagnosed glaucoma` unless diagnosis is directly measured or algorithm-defined, `national trend` unless cycle comparability and trend tests are specified
- Use `historical NHANES examination data` when referring to ophthalmology imaging and visual field components
- Keep slide titles declarative and neutral, with no terminal periods

## Visual construction notes for the final HTML pass

- Use fixed 16:9 `article.slide` sections at 1600 x 900
- Use tan PNG-backed slide backgrounds for final PDF parity, with selectable text above the background layer
- Keep tables compact and readable; split dense methods across appendix slides rather than shrinking text below readable size
- Use dark panels for methodological caveats, cream panels for outcome tables, and lime/blue/orange/pink/red accents only to distinguish data categories
- Include slide numbers and compact citations, but no visible implementation labels or author/social attribution unless separately requested
- Browser-check every slide for overlap, clipping, excessive empty panel space, and title punctuation before export

## Source anchors for final methods footnotes

- CDC VEHSS NHANES data source page: https://www.cdc.gov/vision-health-data/data-sources/national-health-nutrition-examination-survey.html
- CDC NHANES Vision 2007-2008 codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/VIX_E.htm
- CDC NHANES Retinal Imaging 2007-2008 codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/OPXRET_E.htm
- CDC NHANES FDT 2005-2006 codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/OPXFDT_D.htm
- CDC NHANES Survey Methods and Analytic Guidelines: https://wwwn.cdc.gov/nchs/nhanes/AnalyticGuidelines.aspx
