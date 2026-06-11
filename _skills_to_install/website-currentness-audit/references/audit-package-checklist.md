# Website Currentness Audit Package Checklist

Use this checklist when creating or reviewing a website audit report package.

## Evidence

- Audit scope identifies the company, product or program, indication, public webpage, and audit date.
- Each observation has at least one audited-webpage source and one current primary source.
- Primary sources are official, stable, and appropriate for the claim being tested.
- ClinicalTrials.gov evidence uses the rendered study page in the deck when available.
- API responses, if used, are treated as supporting source-log material rather than the primary visual evidence.
- Screenshots show highlighted evidence text and enough surrounding context.

## Report

- Cover chip uses `WEBSITE AUDIT | <MONTH DAY, YEAR>`.
- Main title names the company and audit scope.
- Executive summary language is neutral and non-judgmental.
- Metric tiles use fragments without terminal periods.
- Evidence slides have clear spacing between title, subtitle, and cards.
- References slide table has compact headers and vertically centered values.

## Exports

- `report.html` is present.
- Main report PDF is present with the expected slide count.
- Screenshot appendix PDF is present with one appendix page per evidence source screenshot.
- `sources/source-log.md` records source URL, access date, and evidence purpose.
- `sources/reference-screenshots.csv` maps references to screenshot files.
- Export log has no overflow warnings.
- Rendered output has been visually checked.
