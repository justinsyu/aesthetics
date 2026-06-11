# Source Log and Run Notes

- Run mode: Full run: all requested local conference records scanned
- Generated at: 2026-06-01T15:19:23.342Z
- Records scanned: 2079
- Included records: 29
- Excluded lexical candidates: 59
- Evidence basis: local JSON and MD records from `C:\Users\Justin\Desktop\endo-2026\data`
- Retrieval basis: per-record `retrieved_at` and `source_urls` fields from the archive; no live web refresh was performed.

## Source Files
- conference_records.json SHA-256: 3150326ec3bbf5bd9dd8cac8d3e1f9ae0b1b96dbf1873b0fdaf84b34a7aaa333
- conference_records.md SHA-256: 755218d4fe0b3310f8bac68056433e065602fb13b66e33cc8ca3a4a3de413594
- validation-report.json record count: 2079

## Search Terms
- artificial intelligence
- AI
- machine learning
- ML
- deep learning
- neural network
- algorithm
- automated
- prediction model
- image analysis
- radiomics
- NLP
- chatbot
- LLM
- large language model
- retrieval-augmented generation
- RAG
- digital pathology
- computer-aided
- EfficientNet
- ResNet
- support vector machine
- SVM
- random forest
- kNN

## False-Positive Rules
- Standalone AI excluded when context indicated adrenal insufficiency, aromatase inhibitor, or assay index rather than artificial intelligence.
- Standalone ML excluded when it appeared only in author names, credentials, or citations; author fields were not used for term matching.
- Child presentation records were not included solely because an umbrella session title contained AI unless the record's own title, abstract, summary, or structured sections contained an AI-related term.
- Automated insulin delivery, automated registries, EMR protocols, assay automation, and scheduling automation were excluded unless the same record stated AI, ML, neural-network, or AI-based control-system language.
- Generic clinical prediction/risk models and ordinary statistical algorithms were excluded unless the record stated machine learning, deep learning, neural-network architecture, named ML methods, or AI-based control systems.
- AI/ChatGPT language- or grammar-editing disclosures only were kept in the excluded/borderline JSON and not counted as AI-related topics.
- Radiomics/computer-vision terms were retained only when used as a diagnostic or image-analysis method, not when mentioned only as a possible future modality.

## Topic Cluster Counts
- Imaging AI and quantitative image analysis: 9
- AI implementation, education, and governance: 7
- ML prediction and computational phenotyping: 6
- AI-enabled glucose-control systems: 4
- Generative AI, LLMs, and decision support: 3

## Caveats
- The output is based on the local archive retrieved May 30, 2026; no claims are made about changes after that retrieval timestamp.
- Lexical/rule-based inclusion is inclusive and intended for analyst review; borderline automation records are labeled as automation or AI-adjacent rather than as artificial intelligence methods.
- Some archive records are metadata-only because detail fetches returned 403; those records can only support title/session metadata, not abstract-level claims.