# ADA 2026 AI Topics Strict QA Notes

- PASS: Counts are internally consistent across generated JSON/CSV/MD/source-log/run-manifest artifacts: 135 retained records, 108 direct AI/ML records, 27 predictive-only AI-adjacent records, and 2 excluded false-positive candidates.
- PASS: Predictive-only records are labeled as `AI-adjacent predictive modeling` and are separated from direct AI/ML counts.
- PASS: Topic classification uses visible title first, then Introduction/Objectives, then full abstract only as fallback.
- PASS: Standalone AI/ML acronym matches require local artificial-intelligence or machine-learning wording before inclusion.
- PASS: Generated retained inventory includes source URLs, local locators, trigger snippets, matched contexts, abstract sections, and classification rationale.
- CAVEAT: This QA pass uses the local ADA corpus only; no live source URLs were refreshed.
- PASS: `ada_2026_ai_topics_ci_report.pdf` exported successfully with 9 pages/slides and no exporter overflow warnings.
- PASS: `pypdf` extracted 14,267 characters from the PDF and found the cover title text.
- PASS: PyMuPDF fallback render-review screenshots were generated for all 9 PDF pages because the exporter reported `pdftoppm` was not installed.
- PASS: Browser-export screenshots and render-review screenshots are nonblank and have the expected 16:9 dimensions; `screenshots/browser-export-contact-sheet.png` was regenerated from the current render-review set.
