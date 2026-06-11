# GLP-1 Obesity OpenData Refresh Summary

Run timestamp: 2026-05-28T21:14:03+00:00

## Coverage

- Pinned datasets: 21
- Metadata retrieved successfully: 21
- Pinned search queries run: 12
- Upstream sources scanned: 21
- Upstream sources not scanned: 0
- Large upstream source scans skipped by default: 0
- Lexical product match records: 18956
- Unique matched source rows: 15785
- Product-by-dataset summary rows: 124

## Match Counts by Dataset

- `cms/drug-rebate-products`: 4292 lexical match records; 1828 unique source rows
- `cms/medicaid-spending`: 84 lexical match records; 30 unique source rows
- `cms/nadac`: 3026 lexical match records; 2966 unique source rows
- `cms/part-d-spending`: 73 lexical match records; 26 unique source rows
- `cms/sdud`: 10252 lexical match records; 10252 unique source rows
- `fda/drug-recalls`: 97 lexical match records; 70 unique source rows
- `fda/drug-shortages`: 16 lexical match records; 10 unique source rows
- `fda/drugs-at-fda`: 199 lexical match records; 109 unique source rows
- `fda/ndc-directory`: 641 lexical match records; 402 unique source rows
- `fda/nme-approvals`: 19 lexical match records; 6 unique source rows
- `fda/orange-book`: 257 lexical match records; 86 unique source rows

## Match Counts by Product

- Adlyxin: 200
- Bydureon: 862
- Byetta: 782
- Mounjaro: 3484
- Ozempic: 2353
- Rybelsus: 1679
- Saxenda: 318
- Soliqua: 508
- Trulicity: 2932
- Victoza: 1013
- Wegovy: 1828
- Xultophy: 406
- Zepbound: 1739
- ingredient:exenatide: 44
- ingredient:liraglutide: 521
- ingredient:semaglutide: 153
- ingredient:tirzepatide: 134

## Review Notes

- Treat product matches as a deterministic candidate set, not final interpreted CI findings.
- Use `--scan-all-sources --include-large-source-downloads` when the deliverable requires every pinned source URL to execute, including sources marked metadata-only in the default run.
- Review `source_log.json` for failed requests before relying on a refresh.
- Update `config/glp1_product_dictionary.json` when new GLP-1/incretin brands, ingredients, or sponsors enter scope.
