# ECFS 2026 AI Topics Source Log

## Source Basis

- Source artifacts state 818 records, 85 sessions, and 689 unique abstracts; source data were captured 2026-05-29T14:28:01.644993+00:00.
- Rows screened in this build: 818.
- AI-related records retained: 10.
- Scope: explicit AI/ML methods, AI as operational/session topic, patient/public AI information behavior, and one separately labeled ML-adjacent algorithmic modeling record.

## Inclusion and Exclusion Logic

- Included when the source record explicitly framed the work as artificial intelligence, AI, machine learning, deep learning, AI-based analysis, AI searches, AI chatbots, or comparable ML classifier workflow.
- Excluded clinical screening algorithms, regression-only predictors, biological or mechanistic models, and incidental text matches such as 'shape' or measurement units.
- Two retained symposium records have `missing_abstract_html`; inclusion is based on the official local presentation title and row-level presentation URL.

## Search Terms Used

`artificial intelligence`, `AI`, `machine learning`, `deep learning`, `CatBoost`, `SHAP`, `k-means`, `XGBoost`, `AI searches`, `AI chatbots`, `large language`, `LLM`, `NLP`, `random forest`, `support vector`.

## Category Counts

- Explicit AI/ML methods: 5
- AI as operational/session topic: 2
- Patient/public AI information behavior: 2
- ML-adjacent algorithmic modeling: 1

## Retained Records

### Reference 1 / R1: presentation 7

- Title: Detection of pulmonary exacerbations in the CFTR modulator era using AI would be ACE!
- Session: S06 | Symposium 06 - Detection and treatment of pulmonary exacerbations
- Date/time: 2026-06-04 11:44
- Category: AI as operational/session topic
- AI role: Substantive AI topic
- Scientific topic: Pulmonary exacerbation detection
- Inclusion trigger: using AI would be ACE
- Evidence summary: The symposium presentation title refers to use of artificial intelligence for detecting pulmonary exacerbations in the CFTR modulator era; abstract text was not available in the presentation data.
- Parse status: missing_abstract_html
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/7

### Reference 2 / R2: presentation 90

- Title: Data management in registries – can AI play a role?
- Session: S15 | Symposium 15 - Moving forward with registries
- Date/time: 2026-06-05 09:22
- Category: AI as operational/session topic
- AI role: AI infrastructure or implementation
- Scientific topic: Registry data management
- Inclusion trigger: can AI play a role
- Evidence summary: The symposium presentation title addresses the potential role of artificial intelligence in registry data management; abstract text was not available in the presentation data.
- Parse status: missing_abstract_html
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/90

### Reference 3 / R6: presentation 226 EPS11.05

- Title: Clinical state transitions identified by unsupervised machine learning are associated with improved lung transplant-free survival in cystic fibrosis
- Session: EPS11 | ePoster Session 11 - Telehealth and digital tools in care and education
- Date/time: 2026-06-05 14:24
- Category: Explicit AI/ML methods
- AI role: AI as analytic method
- Scientific topic: Registry clustering, CF states
- Inclusion trigger: unsupervised machine learning; k-means clustering
- Evidence summary: CFFPR encounter data were clustered using unsupervised machine learning and k-means to classify clinical states and transitions associated with lung transplant-free survival.
- Parse status: parsed
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/226

### Reference 4 / R8: presentation 241 WS13.5

- Title: Development of an unbiased and sensitive AI-based morphological pipeline for challenging cystic fibrosis diagnoses
- Session: WS13 | Workshop 13 - From allele to human: the complexity of CFTR
- Date/time: 2026-06-05 16:00
- Category: Explicit AI/ML methods
- AI role: AI as diagnostic workflow
- Scientific topic: Organoid morphology workflow
- Inclusion trigger: AI-based morphological analysis pipeline; AI-derived analysis
- Evidence summary: An AI-based morphology pipeline analyzed patient-derived intestinal organoids to distinguish wild-type from CF organoids and detect ETI-associated recovery.
- Parse status: parsed
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/241

### Reference 5 / R9: presentation 257 WS16.2

- Title: Artificial intelligence-assisted chest HRCT analysis in cystic fibrosis patients
- Session: WS16 | Workshop 16 - Further optimising measures of cystic fibrosis pulmonary disease
- Date/time: 2026-06-05 17:15
- Category: Explicit AI/ML methods
- AI role: AI as imaging workflow
- Scientific topic: AI-HRCT imaging workflow
- Inclusion trigger: Artificial intelligence-assisted; deep learning-based diagnostic model
- Evidence summary: A deep learning model analyzed chest HRCT images from 48 CF patients aged 10 to 18 years across five pulmonary findings, reporting 97% average accuracy, sensitivity, specificity, and F1.
- Parse status: parsed
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/257

### Reference 6 / R4: presentation 349 P434

- Title: Impact of CFTR modulator therapy on pulmonary structure and lung function in children and adolescents with cystic fibrosis
- Session: No session code | Poster Viewing 1
- Date/time: 2026-06-04 14:00
- Category: Explicit AI/ML methods
- AI role: AI as analytic method
- Scientific topic: AI-CT modulator assessment
- Inclusion trigger: Chest CT scans were analysed using AI-based methods
- Evidence summary: A retrospective pediatric CFTR modulator outcomes study states that chest CT scans were analyzed using AI-based methods, paired with Swedish registry lung-function data and mixed-effects modeling.
- Parse status: parsed
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/349

### Reference 7 / R7: presentation 378 WS11.3

- Title: Cancer screening information, promotion and care for people with cystic fibrosis: patient and clinician perspectives from qualitative interview studies
- Session: WS11 | Workshop 11 - The changing face of cystic fibrosis wellbeing, risk and reproductive realities
- Date/time: 2026-06-05 15:30
- Category: Patient/public AI information behavior
- AI role: Patient information behavior
- Scientific topic: Cancer-screening information needs
- Inclusion trigger: AI chatbots
- Evidence summary: Qualitative interview findings on CF cancer-screening information needs reported patients' use of internet-based information and support, including peer social media and AI chatbots.
- Parse status: parsed
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/378

### Reference 8 / R5: presentation 432 P493

- Title: How to deliver digital health literacy training to PwCF, families, and caregivers: results of an Irish survey
- Session: No session code | Poster Viewing 1
- Date/time: 2026-06-04 14:00
- Category: Patient/public AI information behavior
- AI role: Patient information behavior
- Scientific topic: Digital health literacy training
- Inclusion trigger: AI searches
- Evidence summary: An Irish digital-health-literacy survey included AI searches among CF digital health resources and described information-seeking via CF medical websites and social media.
- Parse status: parsed
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/432

### Reference 9 / R10: presentation 441 P205

- Title: Breath VOC signature differentiates cystic fibrosis from bronchial asthma using PTR-TOF-MS breathomics
- Session: No session code | Poster Viewing 1
- Date/time: 2026-06-04 14:00
- Category: ML-adjacent algorithmic modeling
- AI role: ML-adjacent classifier workflow
- Scientific topic: Breathomics VOC classification
- Inclusion trigger: XGBoost importance aggregation; classification performance
- Evidence summary: A breathomics study used repeated subsampling with XGBoost importance aggregation to select 24 VOC features and evaluated CF-versus-asthma classification on a hold-out test set.
- Parse status: parsed
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/441

### Reference 10 / R3: presentation 543 P194

- Title: Machine learning-based prediction of longitudinal lung function trajectories in patients not using modulators from national CF registry data in Turkey
- Session: No session code | Poster Viewing 1
- Date/time: 2026-06-04 14:00
- Category: Explicit AI/ML methods
- AI role: AI as analytic method
- Scientific topic: Registry lung-function models
- Inclusion trigger: machine learning; CatBoost; SHAP
- Evidence summary: Machine-learning time-series models were used to estimate short-term FEV1 and FVC trajectories from CF Registry of Turkey data using CatBoost, nested cross-validation, hyperparameter optimization, and SHAP.
- Parse status: parsed
- Row-level URL: https://ecfs2026.abstractserver.com/programme/#/details/presentations/543
