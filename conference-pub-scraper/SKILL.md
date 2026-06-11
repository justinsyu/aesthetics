---
name: conference-pub-scraper
description: Scrape, normalize, validate, and optionally publish conference abstracts, posters, presentations, sessions, proceedings, or programme records from a user-provided conference website, SPA, abstract server, PDF programme, proceedings PDF, or image-heavy source. Use when Codex needs to extract conference publication data, preserve source URLs/page evidence, handle abstract sections such as background/objectives/methods/results/conclusions, process PDF or image/chart content, validate record counts and source fidelity, generate JSON/Markdown exports, or build a GitHub Pages browser for the dataset.
---

# Conference Pub Scraper

## Operating Standard

Produce a reproducible archive, not a one-off scrape. Preserve enough source evidence that a user can click from any displayed record back to the conference source and verify the title, metadata, and abstract text.

Always create or update these artifacts unless the user asks for a narrower deliverable:

- Full JSON dataset with every scraped record.
- Markdown/plain-text export of the same records.
- Validation report or console summary covering count, uniqueness, source URLs, and spot checks.
- Optional GitHub Pages display when requested, with local browser QA before commit/push.

Read `references/record-schema.md` when defining fields or adapting a dataset. Read `references/validation-playbook.md` before finalizing validation or publishing.

## New Conference Runbook

1. Create a work folder for the conference and save the user-provided URLs in a source inventory.
2. Recon the site/PDFs and choose the extraction path: API, HTML/browser, PDF text, OCR/image, or combined.
3. Scrape into full JSON first. Do not build the display until record identity, counts, and source evidence are stable.
4. Write `source-log.json` with each source URL, status, content type, retrieval timestamp, extraction method, and extracted record count.
5. Normalize to the canonical schema and generate Markdown/plain text.
6. Run validation:

```powershell
python path\to\conference-pub-scraper\scripts\validate_records.py records.json --strict --report-out validation-report.json --markdown-out records.md
```

7. Spot-check records against source pages/PDF pages, then build optional GitHub Pages if requested.
8. In the final answer, report total records, unique IDs, source coverage, structured abstract count, validation samples, known limitations, and output paths.

## Source Recon

Start by identifying every place records can exist:

- HTML pages, hash routes, pagination, search result pages, session pages, presentation detail pages.
- XHR/fetch API endpoints used by a conference SPA.
- Downloadable PDFs, proceedings files, poster books, abstract books, supplements, ZIPs, or CSV/XLSX exports.
- Embedded images, chart panels, poster thumbnails, and lazy-loaded media.

For websites, inspect network calls and page state before brute-force crawling. For PDFs, download the PDF and parse locally with structured tools such as PyMuPDF, pdfplumber, or OCR when text extraction fails. For image-heavy sources, store image URLs or local paths and use OCR/vision only for visible text; do not invent chart values that are not legible.

Respect robots.txt, rate limits, login boundaries, copyright, and conference terms. If a source appears restricted or the user wants bulk downloads of copyrighted PDFs/images, surface the risk and use the minimum extraction needed for the requested archive.

## Scrape Workflow

1. Build a source inventory with URLs, route patterns, file names, and candidate IDs.
2. Decide the primary extraction path:
   - Prefer API/embedded JSON when it contains complete records.
   - Use DOM/browser extraction when the site renders complete details only after interaction.
   - Use PDF parsing when the abstract book is the authoritative complete list.
   - Combine sources when one source has count coverage and another has richer detail.
3. Normalize records to the canonical schema. Keep original source identifiers and source URLs, even when generating your own stable UID.
4. Deduplicate by stable IDs first, then by normalized title/authors/session when IDs are missing.
5. Mark parse quality explicitly: `complete`, `partial`, `pdf_text_only`, `ocr_partial`, `metadata_only`, or `failed`.
6. Preserve raw evidence fields where useful: source page number, source line/block, source URL, image URL, API endpoint, and retrieval timestamp.

## Abstract Structure

Capture structured sections as a label-to-text object. Preserve source labels rather than forcing every conference into one taxonomy. Common labels include:

- Background, Introduction, Rationale
- Objectives, Aim, Purpose
- Methods, Materials and methods
- Results, Findings
- Conclusions, Discussion, Implications

Also store a flattened `abstract_text` or `summary` for search. If section labels are missing, retain the unstructured abstract text and set `structure` accordingly.

## Images, Charts, And Posters

When a record includes images:

- Save `image_assets` entries with `url`, `local_path` if downloaded, `caption`, `ocr_text`, and `parse_note`.
- For charts, extract visible chart titles, legends, axis labels, and embedded text when readable.
- Avoid converting uncertain chart geometry into exact numeric results unless the source provides those values in text.
- Keep image evidence linked to the record so a future reviewer can inspect it.
- If OCR is needed, record the OCR engine/tool, page/image, confidence when available, and `parse_status: "ocr_partial"` unless the OCR has been manually verified.
- Prefer page-level OCR text and cropped chart OCR notes over untraceable merged text blobs.

## Validation

Before final handoff:

- Confirm total records and unique records against the most authoritative source.
- Verify every record has at least one source URL or PDF page/source reference.
- Check expected structured abstract counts when the source supports that distinction.
- Spot-check records across record types, sessions, tracks, and parsing modes.
- Compare displayed GitHub Pages content to the source link for sampled records.
- Run `scripts/validate_records.py` on the final JSON when the data shape is compatible.

Use subagents for independent validation when the environment supports them and the task has enough complexity to justify it. Give validators the dataset and source URLs, not your conclusions.

## Outputs

Use stable, portable files:

- `conference_records.json` or a conference-specific full JSON filename.
- `assets/data/presentations-index.json` for browser-friendly reduced indexes when building a site.
- `assets/data/<conference>.md` for plain-text/Markdown download.
- `source-log.json` with URL, status, content type, retrieval timestamp, extraction method, and record count per source.
- `validation-report.json` or a concise validation section in the final answer.
- Optional raw text dumps under `raw/` and source artifacts under `sources/` when useful and allowed.

For GitHub Pages displays:

- Keep the site root static: `index.html`, `assets/css`, `assets/js`, and `assets/data`.
- Match the conference's branding only enough to make the archive recognizable; keep the UI utilitarian and searchable.
- Include downloads for JSON and Markdown.
- Include source links on every record and in detail modals.
- Prevent form submissions from reloading the page.
- Validate locally with a static server, for example `python -m http.server 8000 --bind 127.0.0.1`.
- Deploy with the repository's existing convention: GitHub Actions Pages workflow, `docs/` folder, or branch-based Pages.
- Do not commit raw copyrighted source PDFs/images unless the user explicitly asks and the source terms allow it; prefer source URLs and derived record data.
- Validate locally with browser checks before commit/push.

## Helper Script

`scripts/validate_records.py` validates common JSON exports and can write a Markdown export:

```powershell
python conference-pub-scraper\scripts\validate_records.py data.json --expected-count 818 --markdown-out records.md
```

Use `--strict` for final QA. Strict mode fails on duplicate IDs, count mismatch, missing title, missing source evidence, invalid parse status, or missing abstract text unless the record is marked `metadata_only` or `failed`.

`scripts/extract_pdf_text.py` extracts page-level text from searchable PDFs:

```powershell
python conference-pub-scraper\scripts\extract_pdf_text.py abstract-book.pdf --json-out pdf-pages.json --text-out pdf-pages.txt
```

The script is intentionally schema-tolerant. Patch it for a specific conference if needed, then keep the dataset-specific change near the project rather than making this skill too narrow.
