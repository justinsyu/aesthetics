# HTA JCA Infographic Data Brief

Source workbook: `C:\Users\Justin\Downloads\hta_ongoing-jca_en.xlsx`, parsed directly as XLSX XML with Python `zipfile` / `xml.etree.ElementTree`; no Excel GUI used.

Reference style page: `https://justinsyu.github.io/conference-data/intelligence.html`, with linked CSS `assets/css/site.css?v=layout` and `assets/css/intelligence.css?v=archive-ui-15`.

## Workbook Structure

Sheets found:

| Sheet | XML dimension | Row 6 literal header read | Detected table header row | Usable records |
|---|---:|---|---:|---:|
| Ongoing JCAs | `A1:J124` | `Directorate-General for Health and Food Safety` in A6; B6:J6 blank | 15 | 15 |
| Discontinued JCAs | `A1:H123` | `Directorate-General for Health and Food Safety` in A6; B6:H6 blank | 15 | 1 |
| Completed JCAs | `A1:J123` | `Directorate-General for Health and Food Safety` in A6; B6:J6 blank | 15 | 0 |

Important parsing note: the requested row 6 is a masthead row, not the visible data-table header row. Row 15 contains the actual table headers in all sheets. Evidence: row 10 has the list title, row 11 has extraction date text, row 13 has explanatory notes, and row 15 has field labels such as `International non-proprietary name (INN) / Common Name`.

## Normalized Columns

Literal row-6 normalized columns:

| Sheet | Normalized row-6 columns |
|---|---|
| Ongoing JCAs | `directorate_general_for_health_and_food_safety`, then 9 blank columns |
| Discontinued JCAs | `directorate_general_for_health_and_food_safety`, then 7 blank columns |
| Completed JCAs | `directorate_general_for_health_and_food_safety`, then 9 blank columns |

Detected row-15 table columns:

| Sheet | Normalized row-15 columns |
|---|---|
| Ongoing JCAs | `international_non_proprietary_name_inn_common_name`; `indication_summary`; `substance_type_classification`; `accelerated_assessment_art_14_9_reg_726_2004`; `revert_to_standard_time_table_mm_yy`; `variation_to_the_terms_of_an_existing_ma`; `orphan_product`; `date_of_ema_validation_of_the_maa`; `assessor`; `co_assessor` |
| Discontinued JCAs | `international_non_proprietary_name_inn_common_name`; `indication_summary`; `date_of_ema_validation_of_the_maa`; `date_of_jca_discontinuation`; `reason_for_discontinuation`; `links_to_relevant_documents`; `assessor`; `co_assessor` |
| Completed JCAs | `international_non_proprietary_name_inn_common_name`; `indication_summary`; `variation_to_the_terms_of_an_existing_ma`; `date_of_ema_validation_of_the_maa`; `date_of_htacg_endorsement_of_the_jca_report`; `link_to_jca_report_and_summary_report`; `link_to_the_dossier_of_the_health_technology_developer`; `date_of_publication_of_the_jca_report`; `assessor`; `co_assessor` |

## Metric Counts

Primary status counts from row-15 tables:

| Status | Count | Evidence rows |
|---|---:|---|
| Ongoing | 15 | rows 16-30 |
| Discontinued | 1 | row 16 |
| Completed | 0 | no nonblank rows after row 15 |
| Total usable records | 16 | ongoing + discontinued |

Ongoing substance type mix:

| Substance type | Count |
|---|---:|
| Chemicals | 9 |
| ATMP | 4 |
| Biologicals | 2 |

Ongoing flags:

| Field | Counts |
|---|---|
| Accelerated assessment | `N`: 15 |
| Variation to existing MA | `N`: 15 |
| Orphan product | `Y`: 7; `y`: 1; `N`: 7 |

Orphan rows marked `Y`/`y`: 17, 18, 19, 21, 22, 24, 26, 30. Row 30 uses lowercase `y`, so the flag should be normalized case-insensitively before charting.

Discontinued record:

| INN / common name | Indication | Reason |
|---|---|---|
| Sasanlimab | Treatment of bladder cancer | Withdrawal of marketing authorisation application by the health technology developer |

## Date Ranges

Workbook dates are stored as Excel serial numbers, not ISO dates, in the date columns. Converted using the standard 1900-date-system offset where serial 1 maps from `1899-12-31` behavior via base `1899-12-30`.

| Sheet | Date field | Raw serial range | Converted range |
|---|---|---:|---|
| Ongoing JCAs | Date of EMA validation of the MAA | 45743-46107 | 2025-03-27 to 2026-03-26 |
| Discontinued JCAs | Date of EMA validation of the MAA | 45799 | 2025-05-22 |
| Discontinued JCAs | Date of JCA discontinuation | 46066 | 2026-02-13 |
| Completed JCAs | EMA validation / endorsement / publication date fields | none | no records |

Source extraction dates in workbook text:

| Sheet | Extraction date text |
|---|---|
| Ongoing JCAs | `Data extracted on 14 April 2026` |
| Discontinued JCAs | `Data extracted on 02 March 2026` |
| Completed JCAs | `Data extracted on 02 March 2026` |

## Data Quirks To Handle

1. Row 6 is not the table header despite the instruction to treat it as headers. Use row 6 for provenance/masthead evidence; use row 15 for infographic data fields.
2. Excel serial dates appear in date cells: examples include `45743`, `45799`, `46066`, and `46107`.
3. Orphan flags include both uppercase `Y` and lowercase `y`; normalize to uppercase before counting.
4. Agency names have trailing spaces that split counts unless trimmed. Examples:
   - `Institute for Quality and Efficiency in Health Care, Germany ` appears in ongoing assessor/co-assessor cells.
   - `Dental and Pharmaceutical Benefits Agency, Sweden ` appears in ongoing assessor cells.
   - `Dutch National Health Care Institute, The Netherlands ` and `Danish Medicines Council, Denmark ` appear in discontinued cells.
5. Special spaces occur in indication text. Ongoing row 20 contains `breast\u202fcancer`, a narrow no-break space (`U+202F`) between `breast` and `cancer`.
6. Agency naming is not fully standardized even after trimming. Example: `National Institute for Health and Disability Insurance, Belgium` differs from `National Institute for Health and Disability, Belgium`.
7. Completed JCA tab has table headers but no post-header records in the XML.

## Compact Visual-Style Brief

The reference page is an intelligence dashboard with a dense analytic layout. Visible page evidence includes title/navigation text: `ASCO 2026 Abstract Intelligence Dashboard`, `Top Intelligence Findings`, `Session Landscape & Cancer Track Distribution`, `Treatment Paradigm Evolution`, `Drug Landscape`, `Genomic Landscape`, `Clinical Trial Landscape & Outcome Endpoints`, and `Thematic Intelligence`.

Use these design cues:

| Element | Evidence from page/CSS | Infographic translation |
|---|---|---|
| Palette | CSS variables include white background `#ffffff`, navy text/accent `#06254a`, blue `#1c71ed`, teal `#22b3cd`, periwinkle `#76a6eb`, pink `#ea18a8`, green `#00844f`, borders `#d9d9d9` / `#ebeceb` | White analytical canvas, navy headings, restrained border grid, teal/blue/pink/green status accents |
| Typography | Linked Google fonts include Inter, Manrope, Barlow, DM Sans, IBM Plex Mono, Sora, Source Sans 3; CSS uses `var(--font-body)`, `var(--font-display)`, `var(--font-mono)` | Use clean sans body, display-weight section headers, mono labels for dates/counts |
| Layout | `.dashboard-shell` uses a max-width-centered grid; `.kpi-grid` uses auto-fit KPI tiles; `.section-block` has bottom-bordered headings; `.chart-wrap`/`.chart-wrap-lg` define fixed chart heights | Build as dashboard-like panels: top KPI strip, status mix, date timeline, agency-cleaning notes, and compact source/quirk footnotes |
| Card treatment | `.card, .theme-card` use `border: 1px solid var(--border-strong)`, `background: var(--surface)`, `border-radius: 0`; KPI tiles use borders and transparent background | Prefer flat, sharp-edged evidence panels over rounded decorative cards |
| Interaction/content pattern | Page text repeatedly says users can click segments/bars/slices to inspect matching records | For static infographic, mimic drilldown with small callouts listing exact rows/examples |

Recommended infographic hierarchy:

1. Headline KPI strip: `15 ongoing`, `1 discontinued`, `0 completed`, `16 total usable records`.
2. Ongoing mix: substance type bars (`Chemicals 9`, `ATMP 4`, `Biologicals 2`).
3. Timeline: EMA validation range `2025-03-27` to `2026-03-26`; discontinued event `2026-02-13`.
4. Data-quality strip: row-6 masthead issue, Excel serial dates, lowercase orphan `y`, trailing agency spaces, `U+202F` special space.
5. Agency evidence: top ongoing assessor after trimming should combine repeated IQWiG Germany entries rather than treating trailing-space variants as distinct.
