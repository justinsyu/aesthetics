# HTA JCA infographic source notes

Source workbook: `C:\Users\Justin\Downloads\hta_ongoing-jca_en.xlsx`

Generated outputs are self-contained under `outputs/hta_jca_infographic/`.

## Parsing notes

- Parsed the `.xlsx` directly with Python `zipfile` and `xml.etree.ElementTree`; no `openpyxl` or `pandas` dependency was used.
- The task specified row 6 as the table header. In this downloaded workbook, row 6 is the `Directorate-General for Health and Food Safety` masthead on each sheet; the actual table header row is row 15 on Ongoing, Discontinued, and Completed sheets. The parser detects the row containing `International non-proprietary name` and `Indication - Summary` and records `header_row_used` in `normalized_data.json`.
- Excel serial dates were converted using the 1899-12-30 workbook date origin.
- `Y`/`y` orphan flags were normalized to uppercase.
- Assessor and co-assessor names were stripped of trailing spaces.
- Non-breaking, narrow no-break, figure, and thin spaces in indication text were normalized to regular spaces.

## Verified metric story

- Ongoing JCAs: 15
- Discontinued JCAs: 1
- Completed JCAs: 0
- Oncology-related ongoing JCAs: 13 of 15
- Substance mix: {'ATMP': 4, 'Chemicals': 9, 'Biologicals': 2}
- Orphan split: 8 yes / 7 no
- Accelerated assessments: 0
- Variations to existing MA: 0
- Reverts to standard timetable: 0
- EMA validation window: 27 Mar 2025 to 26 Mar 2026
- Top lead assessor: Institute for Quality and Efficiency in Health Care, Germany with 4 ongoing lead assessments

## Styling reference

The HTML borrows dashboard patterns from `https://justinsyu.github.io/conference-data/intelligence.html`: white/navy base, flat bordered KPI cards, section rules, dot-accent headings, compact chart blocks, Inter body type, and Newsreader-style display headings. The page uses live text and CSS/SVG-like layout primitives rather than a rasterized screenshot so the exported PDF remains text-selectable.

- The final single-page layout uses a compact EMA validation timeline instead of a full active-register table; full normalized indication and assessor records are preserved in `normalized_data.json`.
