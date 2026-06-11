# ECFS 2026 AI Record Audit

Source reviewed: `ecfs_2026_conference_wide/ecfs_2026_conference_presentations.csv`.

Inclusion rule: records were counted only when AI/ML was explicit in the title, session topic, methods, or patient/public information behavior. Ordinary clinical screening algorithms, regression-only predictors, biological/preclinical "models", and incidental words such as "model", "shape", or "mL" were excluded.

## Included AI-related records

| ID / code | Category | Rationale |
|---|---|---|
| 7 | AI operational/session topic | Symposium talk title: "Detection of pulmonary exacerbations in the CFTR modulator era using AI would be ACE!" Abstract text unavailable. |
| 90 | AI operational/session topic | Symposium talk title: "Data management in registries - can AI play a role?" Abstract text unavailable. |
| 543 / P194 | Explicit AI/ML methods | Machine learning time-series prediction of FEV1/FVC trajectories using CF Registry of Turkey data; CatBoost, nested cross-validation, hyperparameter optimization, and SHAP. |
| 349 / P434 | Explicit AI/ML methods | Chest CT scans analyzed using AI-based methods in a longitudinal CFTR modulator outcomes study. |
| 432 / P493 | Patient/public AI information behavior | Digital health literacy survey explicitly includes CF digital health tools such as AI searches, alongside telehealth, remote monitoring, and online forums. |
| 226 / EPS11.05 | Explicit AI/ML methods | Unsupervised machine learning on CFFPR encounter data; k-means clustering used to identify clinical states and transitions. |
| 378 / WS11.3 | Patient/public AI information behavior | Qualitative interviews highlight patients' evolving use of internet-based information and support, including peer social media and AI chatbots. |
| 241 / WS13.5 | Explicit AI/ML methods | AI-based morphology pipeline for patient-derived intestinal organoids in challenging CF diagnosis; compares AI-derived classification with ROMA. |
| 257 / WS16.2 | Explicit AI/ML methods | Artificial intelligence-assisted HRCT analysis; deep learning diagnostic model for five pulmonary findings. |
| 441 / P205 | ML-adjacent algorithmic modeling | Breathomics classifier with XGBoost importance aggregation for feature selection and hold-out ROC AUC evaluation. |

## Audit note

The AI-related ECFS 2026 set is intentionally narrow: 10 records. The highest-confidence method records are P194, EPS11.05, WS13.5, and WS16.2. P434 is included because it explicitly states AI-based CT analysis, though the abstract does not name the model family. P205 is included as ML-adjacent because XGBoost is used for feature selection in a classifier workflow. Records mentioning only statistical regression, clinical screening, "model" in biological systems, or incidental terms were not included.
