# ADA 2026 AI Topics QA / Status Notes

- Build timestamp: 2026-05-31T15:40:07.604851+00:00
- Records screened: 2081
- Lexical candidates: 137
- Retained records: 136
- Direct AI/ML records: 105
- Predictive-only AI-adjacent records: 31
- Source mode: local ADA archive. No external webpage screenshots were required or collected.
- False-positive handling: AI/AN and adrenal-insufficiency AI contexts were excluded when no other AI/ML term supported inclusion.
- Topic classifier fix: topic_area now evaluates the visible abstract title first, then Introduction/Objectives, then full abstract text only as fallback, preventing incidental secondary terms such as retinal, kidney, obesity, or GDM language from overriding the title-level topic.
- Auditability: retained CSV/JSON include abstract number, media ID, agenda ID, local locator, EventPilot URL, trigger snippet, abstract sections, summary, category, role, and topic area.
- PDF/export status: `ada-2026-ai-topics-ci-report-05.31.26.pdf` regenerated successfully with 9 slides/pages using the cohere-style-ci exporter and `CHROME_PATH=C:/Program Files/Google/Chrome/Application/chrome.exe`; exporter reported no overflow warnings.
- PDF text QA: `pypdf` extracted 12,230 characters and found the cover title text.
- Render QA: exporter skipped native render-review because `pdftoppm` is not installed; PyMuPDF render-review PNGs and contact sheet were regenerated in `screenshots/render-review/` and visually checked for obvious clipping/overlap.
