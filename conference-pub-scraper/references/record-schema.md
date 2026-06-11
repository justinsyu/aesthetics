# Canonical Record Schema

Use this schema as a target. Add conference-specific fields when needed, but keep these meanings stable.

## Required Or Strongly Preferred Fields

- `uid`: Stable local identifier. Generate from source IDs when possible.
- `conference`: Conference name and year.
- `title`: Presentation, poster, or abstract title.
- `record_type`: Oral, poster, ePoster, workshop item, invited talk, abstract, case, session contribution, etc.
- `source_urls`: Object or list containing detail page, session page, PDF URL, image URL, API endpoint, or other source evidence.
- `parse_status`: `complete`, `partial`, `pdf_text_only`, `ocr_partial`, `metadata_only`, or `failed`.

## Metadata Fields

- `abstract_id`, `presentation_id`, `poster_id`, `session_id`, `display_code`
- `authors`, `authors_text`
- `affiliations`, `affiliations_text`
- `presenter`, `presenter_role`
- `session_title`, `session_type`, `session_code`
- `track`, `topic`, `category`
- `room`, `date`, `time`, `timezone`

## Abstract Fields

- `sections`: Object mapping source section labels to text.
- `abstract_text`: Full text, preserving source order.
- `summary`: Short preview for list displays.
- `structure`: Human-readable structure class, such as `Structured abstract`, `Unstructured abstract`, `No abstract`.
- `missing_sections`: Expected section labels not found, if relevant.

## Evidence Fields

- `source_urls.detail`: HTML detail page for the presentation/abstract.
- `source_urls.session`: HTML session page containing the record.
- `source_urls.pdf`: PDF abstract book, poster book, proceedings, or programme.
- `source_urls.api`: API endpoint or JSON feed used for extraction.
- `source_urls.image`: Poster/chart/image URL when content is image-based.
- `source_page`: PDF page number or page range. Required when the only durable source is a PDF.
- `source_block`: Heading, source line range, DOM selector, or text block identifier when useful.
- `api_endpoint`: Backward-compatible field for source APIs if not nested in `source_urls`.
- `retrieved_at`
- `image_assets`: list of `{url, local_path, caption, ocr_text, parse_note}`.

## Normalization Rules

- Preserve original source IDs exactly.
- Normalize whitespace, but do not rewrite scientific notation, units, author initials, or abstract labels.
- Keep HTML entities decoded in text fields and escaped only when rendering HTML.
- Store arrays as arrays when data is structured; also keep `*_text` fields when convenient for search/export.
- Do not drop records only because abstract text is missing; mark them `metadata_only`.

## Sample Record

```json
{
  "uid": "example-2026-P001",
  "conference": "Example Congress 2026",
  "title": "Example structured poster abstract",
  "record_type": "Poster",
  "display_code": "P001",
  "authors_text": "Doe J; Smith A",
  "presenter": "Jane Doe",
  "session_title": "Poster Viewing 1",
  "track": "Clinical Research",
  "date": "2026-06-01",
  "time": "10:00",
  "sections": {
    "Background": "Source wording.",
    "Methods": "Source wording.",
    "Results": "Source wording.",
    "Conclusions": "Source wording."
  },
  "abstract_text": "Background: Source wording. Methods: Source wording. Results: Source wording. Conclusions: Source wording.",
  "structure": "Structured abstract",
  "source_urls": {
    "detail": "https://example.org/programme/presentations/001",
    "session": "https://example.org/programme/sessions/10",
    "pdf": "https://example.org/abstract-book.pdf"
  },
  "source_page": 42,
  "parse_status": "complete",
  "retrieved_at": "2026-05-30T00:00:00Z"
}
```

## Sample Source Log Entry

```json
{
  "url": "https://example.org/abstract-book.pdf",
  "status": 200,
  "content_type": "application/pdf",
  "retrieved_at": "2026-05-30T00:00:00Z",
  "extraction_method": "pymupdf_text",
  "record_count": 250,
  "notes": "Searchable PDF; page references retained."
}
```
