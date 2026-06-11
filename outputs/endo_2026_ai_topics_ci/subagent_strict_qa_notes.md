# Strict QA Notes

- PASS: Counts are internally consistent across `ai_topic_inventory.json`, `excluded_false_positive_candidates.json`, `run_manifest.json`, `source-log.md`, and `endo_2026_ai_topics_ci_report.html`: 29 included records and 59 excluded lexical candidates.
- PASS: Inventory rollups match the manifest by theme, track, type, and date. After the final theme correction, theme counts reconcile to 9 imaging AI/quantitative image-analysis, 7 implementation/governance, 6 ML prediction/phenotyping, 4 glucose-control systems, and 3 generative AI/LLM records.
- PASS: The excluded-candidates file contains the expected false-positive categories, including adrenal-insufficiency AI, aromatase-inhibitor AI, language/grammar-editing-only AI disclosures, generic clinical prediction/risk models, automated AID without AI/ML/control-system language, and automated workflow/registry-style records.
- PASS: The included inventory does not contain obvious adrenal-insufficiency AI, aromatase-inhibitor AI, language-editing-only AI disclosures, generic clinical prediction/risk models without ML/AI language, or automated workflow/registry records.
- PASS: The included automated insulin-delivery record `endo-2026-P-1844105` is not an AID-only false positive; its matched context includes explicit AI-driven/autonomous bolusing language.
- CAVEAT: This was a strict local-artifact QA only; no source URLs were refreshed and no files outside this folder were inspected.
- PASS: Final manual correction assigns `endo-2026-P-1830385` to ML prediction/computational phenotyping and keeps `endo-2026-P-1843894` in imaging AI/quantitative image analysis.
