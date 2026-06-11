---
name: website-currentness-audit
description: Create evidence-backed website currentness audit reports and exported PDF decks comparing public website claims against current primary sources. Use when Codex needs to audit company, product, therapy-area, clinical-trial, investor, patient, HCP, or program webpages for stale or divergent public claims versus filings, registries, labels, press releases, regulator pages, or other primary sources, with rendered source screenshots, highlighted evidence, source logs, HTML report, main PDF export, and screenshot appendix PDF.
---

# Website Currentness Audit

## Core Contract

Produce a neutral, evidence-backed audit of a public website against current primary sources. Use objective, scientific wording where appropriate. Avoid judgmental terms such as "wrong," "misleading," "failure," or "error" unless a cited source directly supports that conclusion.

Frame findings as currentness observations: "website wording differs from the current filing," "current registry status lists," "not identified on the assessed page," or "source set did not identify." Do not recommend actions unless the user explicitly asks for recommendations.

Use the bundled REGENXBIO report at `references/examples/regenxbio_wet_amd_report.html` as the example for structure, tone, citation placement, evidence-card layout, and final references table.

Use `references/audit-package-checklist.md` as a compact final review checklist when assembling or revising the full report package.

## Audit Workflow

1. Define the company, product, disease, website pages, geography, and date of the audit before collecting evidence.
2. Capture the exact public website statements being assessed from rendered browser pages, not snippets, cached previews, local HTML, or search-result text.
3. Identify current primary sources that can confirm or qualify the website statements. Prefer company SEC filings, press releases, ClinicalTrials.gov pages, regulator pages, approved labels, official program pages, and peer-reviewed or conference sources when relevant.
4. Read primary sources directly and preserve source URLs in `sources/source-log.md`. Search may locate candidates, but included claims must be extracted from opened primary sources or primary documents.
5. Treat scope as evidence. Before flagging trial-status wording, check for other ongoing trials, cohorts, planned studies, alternate product names, and program pages that could make the website wording accurate.
6. Do not treat normal lag between two primary sources as a company issue. The audit question is whether the assessed public website page remains aligned with the current cited source set.
7. Use rendered webpage screenshots for deck evidence. For ClinicalTrials.gov, use the actual study page when the evidence is visible there; reserve raw API JSON for backup notes or source logs unless the user specifically requests API evidence.
8. Before screenshotting, close or accept popups, modals, cookie banners, newsletter prompts, chat widgets, and sticky overlays. Expand relevant accordions, tabs, dropdowns, and "read more" areas so cited text is visible.
9. Highlight or draw a bounding box around the exact supporting text in every evidence screenshot. Retake screenshots that are too small, clipped, obscured, or missing the visible highlight.
10. Keep report copy concise and citation-bound. Every substantive finding, source status, enrollment number, trial status, date, or timing claim needs an inline hyperlink citation.

## Required Run Folder

Create one self-contained run folder:

```text
competitive_intelligence_reports/<topic_slug>/<YYYY-MM-DD_website_currentness>/
  assets/
  screenshots/
    evidence/
    browser-export/
    render-review/
  sources/
    source-log.md
    reference-screenshots.csv
  report.html
  <topic_slug>-ci-report-<MM.DD.YY>.pdf
  <topic_slug>-ci-screenshots-<MM.DD.YY>.pdf
```

Use stable, descriptive topic slugs, for example `regenxbio_wet_amd_website_currentness_audit`.

## Report Structure

Build a fixed 16:9 HTML deck in the tan Cohere-style CI visual system unless the user provides another visual system. Use a 1600 x 900 or equivalent slide canvas and export one PDF page per slide.

Cover slide:

- Use a title that names the assessed company/product/scope, for example `REGENXBIO Wet AMD Website Currentness Audit`.
- Use an eyebrow chip such as `WEBSITE AUDIT | MAY 26, 2026`; do not repeat company or product names in the chip when they already appear in the title.
- Use metric cards for audit scope and concrete counts. If the card body text is a label or fragment, omit periods.
- Include an `Executive summary` callout with neutral, evidence-supported bullets and inline citations.

Evidence slides:

- Title each slide with the observed comparison or source-alignment point.
- Add enough space between the slide title and subtitle/dek so the hierarchy reads clearly.
- Use side-by-side evidence cards when comparing website text with a current source.
- Label cards by reference number and source domain.
- Use screenshots of the actual rendered source pages, not API-return text, search snippets, or manually recreated proof images.
- Keep screenshots large enough to read the highlighted evidence text.

References slide:

- Fit the final cited sources into a single references table when practical.
- Vertically center body values and keep the header row compact, with balanced top and bottom padding.
- Add sufficient space between the `References` title and the table.
- Do not show local file paths, screenshot filenames, or implementation notes in viewer-facing references.

## Screenshot Appendix

Export a separate labeled screenshot appendix PDF for every final cited reference. The appendix is required even when the main deck includes evidence cards.

Name it:

```text
<topic_slug>-ci-screenshots-<MM.DD.YY>.pdf
```

Each appendix page must show a clear label that maps to the report citation, for example:

```text
Reference 3 - evidence
Reference 5 - ClinicalTrials.gov study page
```

Create `sources/reference-screenshots.csv` with `label,path,caption` columns when assembling more than a few screenshot pages. Labels in the CSV must match the appendix labels and final report citation numbering.

## Source Log

Maintain `sources/source-log.md` with:

- Reference number
- Source name and URL
- Source owner or source type
- Visible publication, filing, status, or retrieval date when relevant
- Screenshot path for each evidence image
- Exact fact or claim used in the report
- Exclusion notes for candidate sources that were reviewed but not used

If sources or slides are removed during revisions, renumber citations, source-log entries, screenshot manifests, appendix pages, and visible reference labels so no stale references remain.

## Export And QA

Before delivery:

- Export the main PDF from `report.html`.
- Export the screenshot appendix PDF.
- Confirm the main PDF page count equals the HTML slide count.
- Inspect rendered slide images in `screenshots/render-review/` for overlap, clipping, off-page content, cramped title/subtitle spacing, unreadable text, table headers that wrap awkwardly, and references that spill beyond the page.
- Inspect the screenshot appendix for readable, unobscured rendered source pages with visible highlights or bounding boxes.
- Check that every final report citation maps to a source-log entry and screenshot appendix page.
- Run `git diff --check` in the workspace when the audit lives in a git repo.
- If optional raster tools such as `pdftoppm` are missing, state that the optional raster check was skipped, but still perform available HTML/PDF render review.
