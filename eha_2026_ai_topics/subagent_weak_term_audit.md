# Weak-Term Audit Subagent Note

Scope: retained EHA 2026 AI-related records after parent QA flagged possible `AI` acronym false positives.

- Before audit retained count: 187.
- After audit retained count: 177.
- Removed records: 10.
- Weak-only retained records after regeneration: 0.
- Boundary change: `AI` now requires a non-letter, non-number, non-period, non-hyphen leading boundary, which excludes product-name and subtype-abbreviation matches such as `Optim.AI` and `nTFHL-AI`.
- Relevance change: weak-only terms such as `AI`, `automated diagnosis`, `computational model`, `predictive model`, `algorithmic prediction`, and `classifier` no longer retain a record unless explicit AI/ML/language-model/image-analysis/radiomics/digital-pathology or AI-framed method language is present.
- False-positive classes removed: ordinary automated assays, ordinary automated retinal imaging workflows, coding-only AI use, generic data-analysis AI use, non-AI clinical abbreviations, and nonspecific `era of AI` language.

The retained set continues to include records with explicit AI-framed method language, including AI-based, AI-assisted, AI-designed, AI-driven, AI-guided, AI-generated, generative AI, machine learning, large language models, NLP, image analysis, radiomics, and digital pathology.
