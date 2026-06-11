# EHA 2026 AI Topics QA / Status Notes

- Build timestamp: 2026-05-31T16:08:42.888734+00:00
- Retained records before weak-term audit: 187
- Retained records after weak-term audit: 177
- Records removed by weak-term audit: 10
- Records screened: 4293
- Lexical candidates: 246
- Retained records: 177
- Retained share: 4.1%
- Source mode: local EHA 2026 archive. No external webpage screenshots were required or collected.
- False-positive handling: the AI acronym now uses an exact non-word, non-hyphen, non-period leading boundary; weak-only classifier/model/automation terms, ordinary regression/Cox/logistic/linear model records, non-AI abbreviations, coding-only AI use, and ordinary automated assays were excluded when no explicit AI or machine-learning framing was present.
- Auditability: retained CSV/JSON include abstract number, EHA abstract ID, source URL, matched terms, relevance rationale, derived classifications, and source evidence excerpt.
- Formatting QA: the References table centers values in the first REF column; chip text uses the only bold styling in main body sections; body copy avoids strong tags.
- PDF/export status: exported successfully with 8 slides/pages after singular-count correction; exporter reported no overflow warnings. Native pdftoppm render check was unavailable, so PyMuPDF render-review PNGs and a contact sheet were created. PDF text extraction returned 8,543 characters and cover title text substrings were found: True. HTML singular/plural QA found no `1 records` string.
