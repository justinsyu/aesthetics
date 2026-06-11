# Validation Summary

Validation date: May 28, 2026

Scope: `meeting-dates-2025-06-2026-05.csv`, covering public P&T, DUR, PAC, formulary, PDL, or related Medicaid pharmacy decision-body meeting dates from June 1, 2025 through May 31, 2026.

Method:

- Five parallel validation subagents reviewed state groups against row-level source URLs and public source pages.
- Corrections were applied after all validation groups completed.
- The corrected CSV/JSON and HTML visualization were regenerated from the corrected dataset.
- The PDF export was generated separately and does not modify or strip links from the source HTML, CSV, or JSON.

Applied validation corrections:

- Added missing exact or source-deterministic rows for Delaware, Idaho, Michigan, Montana, New Hampshire, New Jersey, New Mexico, Pennsylvania, South Dakota, Tennessee, Virginia, West Virginia, Wisconsin, and Wyoming.
- Removed obsolete `no_exact_date` rows for New Jersey, New Mexico, Tennessee, Wisconsin, and Wyoming after validators identified exact public dates.
- Updated Hawaii May 13, 2026 and Louisiana May 6, 2026 from tentative/proposed to confirmed based on newly visible meeting materials.
- Updated Nevada source URLs to the current Nevada Medicaid public archive/schedule URLs.
- Retained cancelled and packet-only rows in the dataset while excluding them from plotted bubble counts.

Corrected dataset status:

- Total evidence rows: 200.
- Plotted rows: 196.
- States represented: 50.
- States with plotted dates: 50.
- Excluded rows: 4 (`cancelled` or `packet_only`).

PDF export:

- File: `meeting-calendar-2025-06-2026-05-no-active-links.pdf`.
- Export method: direct calendar-only PDF generation from corrected CSV using ReportLab; the source-reference appendix is intentionally omitted from the PDF.
- Active link verification: zero `/URI`, `/Annots`, and `/Link` entries detected in the generated PDF.
- Source URLs remain preserved as active links in `meeting-calendar-2025-06-2026-05.html` and as text fields in the CSV/JSON.
