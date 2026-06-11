# EHA 2026 AI-related abstract/poster scan

Generated: 2026-05-31T04:48:39.882Z

## Source corpus

- Local JSONL: `C:\Users\Justin\Desktop\eha-2026\data\eha_2026_abstracts.jsonl`
- Local summary: `C:\Users\Justin\Desktop\eha-2026\data\summary.json`
- EHA source URL recorded in summary: https://library.ehaweb.org/eha/#!*menu=6*browseby=3*sortby=2*ce_id=2934
- Listing rows: 4293
- Detail rows screened: 4293
- Detail errors recorded by scrape summary: 0

## Inclusion and exclusion logic

Records were retained when source text matched one or more AI-related method terms across title, topic, keywords, abstract sections, or description text. Terms screened: artificial intelligence, AI, machine learning, deep learning, neural network, foundation model, large language model, NLP, radiomics, computer vision, digital pathology, image analysis, classifier, random forest, gradient boosting, support vector machine, computational model, predictive model, algorithmic prediction, automated diagnosis.

Records were excluded when they only appeared to describe ordinary statistical models, regression, Cox models, or logistic/linear regression without explicit AI, machine-learning, deep-learning, NLP, radiomics, image-analysis, classifier, or comparable AI-method framing.

## Results

- Retained AI-related records: 187
- Share of local detail corpus: 4.4%

## Topic clusters

- Clinical prediction and risk stratification: 115
- Digital pathology, imaging, and morphology: 56
- Diagnosis and classification: 12
- Treatment response and precision therapy: 3
- NLP, LLMs, and text/data extraction: 1

## Top disease areas

- Acute myeloid leukemia: 58
- Lymphoma: 30
- Multiple myeloma: 20
- Myeloproliferative neoplasms: 15
- Novel technologies, techniques and digital analytical tools in hematology: 14
- Thrombosis / hemostasis: 11
- Acute lymphoblastic leukemia: 8
- Hemoglobinopathies: 7
- Transplantation: 7
- Anemia / red cells: 5

## Limitations

- This is a deterministic local-corpus screen, not a live recrawl of EHA pages.
- Topic clusters, disease areas, use cases, and method types are rule-based analyst classifications for review.
- Records using advanced statistics but no explicit AI/ML framing may be excluded by design.
- Some abstracts may have embargoed or empty abstract sections in the local scrape; available metadata was still screened.

## Output files

- `ai_related_records.csv`
- `ai_related_records.json`
- `eha_2026_ai_topics_cohere_ci.html`
- `eha_2026_ai_topics_cohere_ci.pdf`
- `screenshots/slide_01.png` through `screenshots/slide_08.png`

## Export and QA

PDF export completed with the local `cohere-style-ci` exporter using Chrome. The exporter reported 8 slides and no overflow warnings. PDF-to-image render checking was skipped because `pdftoppm` was not installed; HTML slide screenshots were generated and visually spot-checked.
