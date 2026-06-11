# Validation Playbook

Use layered validation. A record count alone is not enough.

## Count And Identity

- Compare scraped total to the source's advertised total, PDF table of contents, programme count, or API count.
- Count unique source IDs and unique local UIDs.
- Report duplicate IDs and near-duplicate titles.
- Explain intentional differences, such as sessions without abstracts or withdrawn records.

## Source Coverage

- Confirm every record has at least one source URL or source reference.
- For PDF-only sources, store PDF URL plus page number or page range.
- For SPA sources, preserve both session and presentation/detail URLs when possible.
- For API-derived records, store the API endpoint and the user-visible source URL if one exists.

## Content Fidelity

Spot-check records across:

- First, middle, and last records.
- Each record type.
- Each parsing mode: API, HTML, PDF text, OCR/image.
- Long abstracts, missing abstracts, and records with charts/images.
- Non-ASCII names, formulas, units, and section labels.

For each sampled record, compare:

- Title
- Authors/presenter
- Session/date/track metadata
- Abstract sections and section labels
- Source URL behavior

## GitHub Pages QA

- Run a local static server from the site root.
- Verify search, filters, clear filters, sorting, load more, details modal, source links, and downloads.
- Press Enter in search and confirm the URL and page state do not reset.
- Check desktop and mobile widths for text overflow.
- Verify a displayed record against its source URL in the browser.

## Final Report

Include:

- Total records scraped.
- Unique records/abstracts when relevant.
- Records with source URLs or PDF page references.
- Structured versus unstructured abstract counts.
- Validation method and sample size.
- Known limitations, such as OCR uncertainty or source records with missing abstracts.

Run the helper script in strict mode for final QA when the dataset is compatible:

```powershell
python path\to\conference-pub-scraper\scripts\validate_records.py records.json --strict --report-out validation-report.json
```
