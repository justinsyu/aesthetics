---
name: cohere-style-report
description: Apply a Cohere-inspired editorial report style — Aptos throughout (Microsoft's new geometric sans, default replacement for Calibri), with Aptos Display at the cover title and section H1s, deep-maroon titles and section headings, coral eyebrow / rule / hyperlink accents, soft-beige table dividers — to long-form Word reports and adjacent artifacts. Use this skill whenever the user asks for "Cohere report style", "Research · Insights style", "Cohere editorial report", "payer-policy report style", or asks to apply this exact maroon-and-coral editorial report look to a docx. This is a different visual identity than cohere-style-lite (which uses warm coral + cream + Aptos); cohere-style-report is the longer, more formal editorial cousin — Aptos body, maroon headings, coral accents on a white page, with a fixed cover page, page header, footer, numbered tables, and a deduplicated References section. The skill also includes a mandatory transformation pass for pandoc-converted docx inputs: stripping LaTeX residue, ensuring an Executive Summary section, numbering tables, adding a Findings/Discussion/Conclusion closing section, rendering text-form diagrams as Cohere-styled PNGs, and rebuilding a dense numbered References section with deduplicated URLs. Do not reproduce Cohere logos or proprietary marks — this is a portable visual identity, not a brand reproduction.
---

# Cohere-style-report

A long-form editorial report treatment. Where `cohere-style-lite` is the warm-coral / cream family for briefs and decks, `cohere-style-report` is the maroon / coral family for formal research reports, payer-policy memos, evidence reviews, and landscape catalogues. Both skills now share **Aptos** as the typeface throughout (Microsoft's new geometric sans, the default replacement for Calibri in Office); the report skill uses **Aptos Display** for the cover title and section H1s, and Aptos for everything else (body, H2/H3, eyebrow / labels, table headers, page header, page footer, captions). It is built around five fixed structural pieces — an editorial cover page, a coral-ruled page header, a paged footer, maroon section headings with a full-width coral underline rule, and a numbered References section — and a mandatory cleanup pass that catches the typical defects in pandoc-converted manuscripts.

## When to use this skill

- The user asks for "Cohere report style", "Research · Insights style", "Cohere editorial report", or "payer-policy report style".
- The user asks to apply the visual style of a prior Cohere-style report (e.g. "the AI in Pharma research-insights one") to a new docx.
- The user has a pandoc-converted docx (Markdown or LaTeX origin) and wants it restyled into an editorial report with Aptos body, maroon headings, coral accents, and numbered tables / references.
- The user mentions an "editorial" or "research" report and Cohere has been mentioned earlier in the conversation, asking for the maroon / Aptos editorial look rather than the warm-coral / cream lite look.

Do not use this skill to reproduce Cohere's logo, wordmark, or proprietary typefaces. The visual identity here is the palette and typographic posture, not Cohere's trademarks.

## Design tokens

These tokens are the source of truth. When applying the style, use them verbatim — do not introduce arbitrary blues, greens, or rainbow accents. They are extracted from a known-good Cohere-style report (the user's reference docx); confirm against the user's source if you regenerate them.

### Color palette

| Role                 | Hex      | RGB             | Typical usage                                                          |
|----------------------|----------|-----------------|------------------------------------------------------------------------|
| Deep maroon          | `#8B2820` | 139,  40,  32   | Title, section headings (H1/H2/H3), table header background, header title  |
| Coral accent         | `#D85A3F` | 216,  90,  63   | Eyebrow text, horizontal rules, hyperlinks / citations, header & footer hairlines, H1 underline |
| Deep ink             | `#1A1A1A` | 26,   26,  26   | Body copy, footer left text                                            |
| Muted slate          | `#6B6B6B` | 107, 107, 107   | Captions, subtitle muted lines, footer page-of                         |
| Soft beige rule      | `#E8DFD3` | 232, 223, 211   | Table dividers, hairline body-cell borders                             |
| Page background      | `#FFFFFF` | white           | No fill — plain white page                                             |
| Table-header text    | `#FFFFFF` | white           | Bold Aptos white on maroon                                             |

### Typography

The skill defaults to **Aptos** as the single typeface for all text in any artifact it is applied to, with **Aptos Display** reserved for the largest display sizes (cover title and section H1s). Microsoft pairs Aptos with Aptos Display the same way; both ship with current Office. Cohere's actual typeface is proprietary; Aptos and Aptos Display are the portable defaults this skill uses, with Calibri as the fallback when neither is installed.

| Tier              | Font (with fallbacks)                                  | Size (docx)         | Treatment                                                                                                                                              |
|-------------------|--------------------------------------------------------|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| All text          | "Aptos", "Aptos Display", "Calibri", sans-serif        | varies (see below)  | Single-typeface system: **Aptos** everywhere, **Aptos Display** at display sizes (cover title, section H1s).                                            |
| Cover title       | "Aptos Display", "Aptos", "Calibri", sans-serif        | 42pt (`sz=84`)      | Bold maroon, tight tracking `spacing=-12`. Aptos Display.                                                                                              |
| H1 (sections)     | "Aptos Display", "Aptos", "Calibri", sans-serif        | 22pt (`sz=44`)      | Bold maroon, full-width coral underline rule. Aptos Display.                                                                                           |
| H2                | "Aptos", "Aptos Display", "Calibri", sans-serif        | 16pt (`sz=32`)      | Regular weight maroon. Aptos.                                                                                                                          |
| H3                | "Aptos", "Aptos Display", "Calibri", sans-serif        | 14pt (`sz=28`)      | Regular maroon. Aptos.                                                                                                                                 |
| Body              | "Aptos", "Aptos Display", "Calibri", sans-serif        | 12pt (`sz=24`)      | Regular ink, line-height ~1.4. Aptos.                                                                                                                  |
| Italic body       | Same family                                            | 12pt                | Italics for descriptions / subtitles. Aptos italic.                                                                                                    |
| Eyebrow / label   | "Aptos", "Aptos Display", "Calibri", sans-serif        | 10–11pt             | Bold coral, all caps, wide tracking. Aptos.                                                                                                            |
| Table header      | "Aptos", "Aptos Display", "Calibri", sans-serif        | 10pt                | Bold white on maroon fill. Aptos.                                                                                                                      |
| Header / footer   | "Aptos", "Aptos Display", "Calibri", sans-serif        | 9pt (`sz=18`)       | Header: maroon title left, coral "Research · Insights" right. Footer: ink title left, ink "Page X of Y" right. Title-only — no subtitle, no eyebrow.   |
| Caption           | "Aptos", "Aptos Display", "Calibri", sans-serif        | 10pt                | Italic slate. Aptos italic.                                                                                                                            |

**Aptos throughout.** The report uses a single typeface — **Aptos** — for every text element: body, headings, eyebrow / labels, table headers, page header, page footer, captions. Display-tier text (the cover title and the section H1s) uses **Aptos Display**, the heavier display companion that Microsoft ships alongside Aptos. There is no serif anywhere; there is no second sans family layered on top. Calibri is the portable fallback when Aptos / Aptos Display are not installed (e.g., older Office or non-Office viewers).

## Structural treatments

These are the recurring layout signatures that make the style cohere rather than just a color swap.

1. **Editorial cover page (five centered blocks).** The cover is the most distinctive piece of the style. Top to bottom:
   - Coral all-caps eyebrow with an interpunct separator: `RESEARCH · INSIGHTS` — bold **Aptos**, `#D85A3F`, ~10–11pt.
   - An italic category sub-line in **Aptos italic** (e.g., "AI Strategy · Pharmaceuticals").
   - A short coral horizontal rule beneath the eyebrow.
   - The large title in deep maroon, ~42pt, bold, tight tracking — **Aptos Display**.
   - An **Aptos** subtitle giving the angle of the report.
   - An italic **Aptos** description (one paragraph, often a noun phrase rather than a sentence).
   - A three-row metadata block: coral all-caps **Aptos** labels (SCOPE, COVERAGE PERIOD, REPORT DATE) over **Aptos** values.
   The cover suppresses header and footer via `<w:titlePg/>` on the cover section. Padding from the top of the page to the eyebrow should roughly equal padding from the dateline to the bottom — see Rule 1 in "Required transformations" for the verbatim calculation.

2. **Page header on every body page.** Aptos maroon document title **left-aligned** + coral "Research · Insights" **right-aligned** with a thin coral hairline below. The two text blocks sit on a single line via a right tab stop at the right page margin (`<w:tabs><w:tab w:val="right" w:pos="9360"/></w:tabs>` for portrait sections with 6.5" content width; `w:pos="12960"` for landscape sections, since landscape has a wider text area). The hairline is a paragraph bottom border, coral, `sz=6`, with `space=6`. The header text is set in **Aptos** (`<w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>`), matching the rest of the document. The cover suppresses this via `<w:titlePg/>`.

   **Header text content — title only.** The header contains *only* the document's main title — the title displayed on the cover page. It must NOT include the subtitle, the "RESEARCH · INSIGHTS" eyebrow, ": Executive summary", or any sub-heading. Example: if the cover title is "AI in pharma", the header reads exactly `AI in pharma` — not `AI in pharma: Executive summary`, not `AI in pharma — Research Insights`, not `AI in pharma | Pfizer landscape`, and not anything appended.

3. **Page footer on every body page.** Aptos document title **left-aligned** + "Page X of Y" **right-aligned** with a thin coral hairline above. The page numbers are real `PAGE` / `NUMPAGES` fields, not literal text. Same right tab-stop pattern as the header (`w:pos="9360"` for portrait, `w:pos="12960"` for landscape). The footer text is set in **Aptos** (`<w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>`), matching the rest of the document.

   **Footer text content — title only.** Same hard rule as the header: the footer's left-hand text is *only* the document's main title from the cover page. No subtitle, no ": Executive summary", no eyebrow, no sub-heading appended. If the cover title is "AI in pharma", the footer reads exactly `AI in pharma` on the left and `Page X of Y` on the right.

4. **Section headings with a full-width coral underline.** H1 (`Heading 1`) is **Aptos Display** bold maroon ~22pt with a paragraph bottom border in coral (`sz=14`, `space=6`). H2 and H3 step down to 16pt and 14pt maroon **Aptos** without an underline.

5. **Wide tables on dedicated landscape pages.** Tables with more than ~4 columns get lifted onto their own landscape page via portrait/landscape section breaks. The table's header row uses a deep-maroon background fill with bold white sans-serif text. Body cells have hairline beige borders (`#E8DFD3`, `sz=4`) and generous cell margins (`top/bottom=100`, `left/right=140` DXA). The portrait section is re-opened immediately after the table. Any wide table that's lifted to landscape MUST also (a) carry a caption styled via `TableCaption` (Rule 11), not `Heading 1`, and (b) have cell text sized per the column-count guideline (Rule 12) so no word wraps mid-token.

6. **Inline citations.** Every `[N]` citation in the body and in table cells is restyled to coral (`#D85A3F`) with a matching coral underline. The hyperlink behind the marker is preserved. Citations in body prose may be rendered superscript at half the body size; citations inside table cells stay at body size with the underline preserved (table cells are already dense and superscript renders as visual noise).

## Required transformations

These transformations are **mandatory** whenever the skill is applied to an existing document. They catch the systematic defects in pandoc-converted manuscripts and bring every report up to a consistent editorial baseline. They are not optional polish — apply each one in order.

### 1. Even cover-page padding

**Why.** The cover page is the first impression of the report. A composition with top-heavy or bottom-heavy padding reads as "Word doc that got slapped with a title", not as "editorial document." Visual balance is what tells the reader this is a real publication.

**How.** Treat the cover as a single composition that must be vertically balanced. Compute:

```
total_content_height = sum of (paragraph height) for each cover paragraph
top_padding          = (page_height - total_content_height) / 2
bottom_padding       = top_padding
```

In practice, on US Letter portrait with 1" margins, the printable region is ~13680 twentieths-of-a-point tall (15840 − 2×1440 = 12960 + adjustments). Set the eyebrow's `before` spacing so the eyebrow's top sits roughly where `top_padding` lands, then add a trailing empty paragraph (or set the dateline's `after` spacing) so the bottom edge of the dateline sits the same distance from the bottom margin.

A working starting point: `before="3600"` on the eyebrow (which produced visually balanced output in the reference docx), then a final empty paragraph or `after="600"` on the last metadata row. Measure by rendering to PDF; adjust until the white space top and bottom is visibly equal.

```xml
<!-- Eyebrow: top spacing pushes composition to vertical center -->
<w:p>
  <w:pPr>
    <w:spacing w:before="3600" w:after="120"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:b/><w:color w:val="D85A3F"/><w:spacing w:val="60"/><w:sz w:val="22"/>
    </w:rPr>
    <w:t xml:space="preserve">Research  ·  Insights</w:t>
  </w:r>
</w:p>
<!-- ... title, subtitle, description, metadata ... -->
<!-- Trailing empty paragraph to balance bottom padding -->
<w:p><w:pPr><w:spacing w:before="600"/></w:pPr></w:p>
```

### 2. Ensure an "Executive Summary" section

**Why.** Editorial reports lead with a brief overview that orients the reader to the rest of the document. Pandoc-converted manuscripts often jump straight from cover to "Introduction" or "Background", which feels academic rather than editorial.

**How.** Scan the body paragraphs (after the cover section break) for the first `Heading 1`. If that heading's text matches `Executive Summary`, `Summary`, `Overview`, or `Abstract` (case-insensitive), do nothing. Otherwise, insert a new `Heading 1` titled "Executive Summary" immediately before the first body paragraph after the cover.

```python
EXEC_NAMES = {"executive summary", "summary", "overview", "abstract"}

def ensure_executive_summary(body_paragraphs):
    first_heading = next((p for p in body_paragraphs if is_heading1(p)), None)
    if first_heading and first_heading.text.strip().lower() in EXEC_NAMES:
        return  # already present
    insert_heading1_at(body_paragraphs, "Executive Summary", position=first_body_index(body_paragraphs))
```

Do not invent body content under the new heading — if the first body paragraphs already serve as an overview, the heading is enough. If a clearly-marked overview is missing entirely, leave a note for the user; do not fabricate prose.

### 3. Number every table

**Why.** Numbered tables ("Table 1.", "Table 2.") are a hallmark of editorial reports. They make captions referenceable in body prose ("see Table 3") and give every table a deterministic identity. Pandoc inputs frequently produce tables with no caption at all, or with a descriptive caption that lacks a number.

**How.** Walk the document in reading order. Maintain a `table_counter` starting at 1. For each `<w:tbl>`:

1. Look at the paragraph immediately preceding the table. If that paragraph has the `Caption` or `TableCaption` paragraph style (or matches a regex like `^Table\s*\d`), treat it as the table's caption.
2. If a caption exists but does **not** start with `Table N.`, prepend `Table {counter}. ` to its text, then increment the counter.
3. If a caption exists and already starts with `Table N.`, renumber it to match `{counter}`, then increment the counter.
4. If no caption is present, synthesize a short descriptive title from the table's header row (or, failing that, from any heading immediately above the table) and insert a new paragraph with style `Caption` directly above the table: `Table {counter}. {synthesized title}`. Increment the counter.

Always use a period after the number (`Table 1.`, not `Table 1:` or `Table 1 —`). The caption itself is rendered in italic Aptos slate per the existing `Caption` style; the "Table N." prefix can be rendered bold maroon if desired (optional; the period-and-space separator is the load-bearing piece).

### 4. Strip LaTeX residue

**Why.** Pandoc-converted documents — especially those that traveled through LaTeX `easylist` syntax — leave readable LaTeX scraps in the body: `\begin{easylist}\el`, stray `@` characters at paragraph starts, `\@end{easylist}`, `\el`, `\end{...}`. These render in Word as visible text and immediately undermine the editorial appearance. They also break list rendering, because the paragraphs that were meant to be list items have no `<w:numPr>` attached.

**How.** Walk every `<w:t>` in the document and remove these patterns. Then convert the affected paragraphs into proper Word bullet lists by attaching a real `numId` defined in `numbering.xml`.

```python
import re

LATEX_PATTERNS = [
    re.compile(r"\\begin\{easylist\}\\el\s*"),
    re.compile(r"\\@end\{easylist\}"),
    re.compile(r"\\end\{[^}]+\}"),
    re.compile(r"\\el\b\s*"),
    re.compile(r"^@\s+"),  # stray @ at paragraph start
]

def clean_latex_residue(text):
    cleaned = text
    for pat in LATEX_PATTERNS:
        cleaned = pat.sub("", cleaned)
    return cleaned.strip()

def convert_list_items_to_bullets(paragraphs, list_num_id):
    """Paragraphs that lost their list markers when LaTeX residue was stripped
    get a proper <w:numPr> attached to their <w:pPr>."""
    for p in paragraphs:
        if was_easylist_item(p):
            attach_num_pr(p, ilvl=0, num_id=list_num_id)
```

Define a bullet numbering definition once in `numbering.xml` (decimal or bullet `lvlText="•"` works), then attach via `<w:numPr><w:ilvl w:val="0"/><w:numId w:val="200"/></w:numPr>`. Do not insert literal bullet characters (`•`) at the start of paragraph text — that fakes the list and breaks Word's outline / numbering machinery downstream.

### 5. Add Findings / Discussion / Conclusion

**Why.** Editorial reports close with a section that names what the analysis adds up to. Pandoc inputs that originated from analytical writing often have unlabeled closing prose — a final two or three paragraphs of synthesis that should sit under a heading like `Findings`, `Discussion`, or `Conclusions`, but in the source it's just continuation prose under the prior section.

**How.** Walk backward from the end of the body. Find the position of the last `Heading 1`. If the text between that heading and the end of the document is substantial (more than ~150 words), and the last heading is **not** named `Findings`, `Discussion`, `Conclusion(s)`, `Implications`, or `Takeaways`, identify the natural transition point — typically a paragraph that begins with a phrase like "Across these findings…", "Taken together…", "These trends suggest…", "In summary…" — and insert a new `Heading 1` before that paragraph.

Pick the heading name that best fits the content:

- **Findings** — for observational / pattern-summary content ("we observe that X across the cohort").
- **Discussion** — for interpretive content ("these patterns suggest Y").
- **Conclusions** — for summary judgments and recommendations ("the evidence supports Z").
- **Implications** or **Takeaways** — for forward-looking content.

Do not invent body content. Only add the heading. If you cannot identify a clear transition point, leave a comment / TODO for the user rather than guessing.

### 6. Render text-form diagrams as Cohere-styled PNGs

**Why.** Mermaid blocks, ASCII flowcharts, and markdown-style timeline lists render as code listings in Word by default. A published editorial report should show a finished diagram, not the source.

**How.** Detect any of:

- A paragraph with style `SourceCode` whose text starts with `gantt`, `flowchart`, `sequenceDiagram`, `timeline`, etc.
- A run of consecutive paragraphs that visually form an ASCII diagram (lines with `─`, `│`, `┐`, `└`, `→`).
- A markdown timeline list: a `Heading 2` or `Heading 3` named "Timeline" followed by a bullet list of `YYYY — event` rows.

For each detection, render a Cohere-styled PNG using PIL or matplotlib with the report palette (white background; maroon `#8B2820` titles; coral `#D85A3F` rule and dots; slate `#6B6B6B` dates; ink `#1A1A1A` event labels; **Aptos** typography — fall back to DejaVu Sans when Aptos is not installed). Save to `word/media/diagram_N.png` inside the unzipped docx.

Add the rels and content type:

```xml
<!-- word/_rels/document.xml.rels -->
<Relationship Id="rIdDiagram1"
  Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
  Target="media/diagram_1.png"/>

<!-- [Content_Types].xml -->
<Default Extension="png" ContentType="image/png"/>
```

Replace the source paragraph(s) with a centered inline picture, 6.5" wide on portrait pages (`cx="5943600"` EMU), height scaled by aspect ratio. The wide-inline picture pattern is in `references/docx_recipe.md` under "Embedding figures".

### 7. Add a "References" heading and render the list as a real numbered Word list

**Why.** Inline citations need a destination. Pandoc inputs that carry `[N]` markers throughout the body often have a flat list of URLs at the end without a heading — the reader has to guess that's the references section. Worse, AI-generated drafts almost always render the references list as literal `[1]`, `[2]` text runs followed by the URL, which means the gap between the number and the URL drifts as URL length varies and adjacent paragraphs collapse inconsistently.

**How — heading.** Detect inline citations by scanning the document for hyperlinks whose visible text matches `^\[\d+\]$`. If at least one is found, look at the document end for a heading named `References`, `Sources`, or `Bibliography` (case-insensitive). If none exists, insert a `Heading 1` titled "References" immediately before the first citation-list paragraph (typically the first hyperlink paragraph at the end of the body).

If there is no citation list at all but inline citations exist, build one — see Rule 8 for the deduplication and renumbering algorithm, and Rule 9 for the list-format requirements that the rebuilt section must obey.

### 8. De-duplicate and re-order citations

**Why.** AI-generated reports often have citation numbering drift: the same URL appears under `[1]`, `[16]`, and `[17]` in different parts of the document. A reader following the references can't tell that these are the same source, and the references list is artificially long. Worse, citation markers sometimes lose their hyperlink entirely.

**How.** Walk the entire document body in reading order — body paragraphs and table cells, in document order. For each hyperlink whose visible text matches `^\[\d+\]$` or any inline citation marker:

1. Extract the target URL from the hyperlink relationship.
2. If the URL is new, assign it the next sequential reference number (`next_n`, starting at 1) and add to `url_to_number` map.
3. If the URL has been seen, reuse its existing number.
4. Rewrite the citation marker's visible text to `[{number}]`.
5. Update the hyperlink's target if it was malformed (e.g., a PubMed search URL `?term=PMID` collapses to `pubmed.ncbi.nlm.nih.gov/PMID/`).

Rebuild the References section as a dense list 1..M (no gaps) where M = unique URL count. Each entry is a single hyperlink to the URL, styled with the coral underline used elsewhere. Use a real `numId` defined in `numbering.xml` for the list — don't fake the numbering with literal "1." text, because hanging-indent spacing drifts as URL length changes.

**Worked example.**

Source document body has these markers (in reading order, after de-LaTeX cleanup):

```
"...as Pfizer announced [1] in its Q3 update..."
"...Roche's collaboration [2] with InSilico..."
"...the FDA [3] published guidance..."
"...similar to Pfizer's earlier statement [16]..."
"...echoing the FDA position [17]..."
```

Source references:

```
[1]  https://pfizer.com/press/q3-2025
[2]  https://roche.com/ai-insilico
[3]  https://fda.gov/ai-guidance-2025
[16] https://pfizer.com/press/q3-2025          <- duplicate of [1]
[17] https://fda.gov/ai-guidance-2025          <- duplicate of [3]
```

After deduplication and renumbering:

```
url_to_number = {
  pfizer.com/press/q3-2025: 1,
  roche.com/ai-insilico:    2,
  fda.gov/ai-guidance-2025: 3
}
```

Body markers become:

```
"...as Pfizer announced [1] in its Q3 update..."
"...Roche's collaboration [2] with InSilico..."
"...the FDA [3] published guidance..."
"...similar to Pfizer's earlier statement [1]..."     <- was [16]
"...echoing the FDA position [3]..."                  <- was [17]
```

Rebuilt References section:

```
References
1.  https://pfizer.com/press/q3-2025
2.  https://roche.com/ai-insilico
3.  https://fda.gov/ai-guidance-2025
```

The list goes from 17 entries to 3, dense and gap-free. See `references/docx_recipe.md` "References section" for the OOXML pattern.

### 9. References section uses a real Word numbered list with colored numbers

**Why.** Faking the references list with literal `[1]`, `[2]` text runs followed by a URL produces ragged spacing — the gap between number and URL drifts every time a URL length changes, and adjacent paragraphs collapse inconsistently. A real numbered list, driven by Word's numbering machinery, parks the number in a fixed gutter via the hanging indent so multi-line URL wrap doesn't disturb alignment, and the `<w:contextualSpacing/>` paragraph property collapses the inter-paragraph spacing between adjacent reference items into a tidy block regardless of how many lines a single URL wraps to.

**How.** Three load-bearing pieces, all required:

1. **Real numbered list, not literal `[N]` text.** The numbering must be driven by `numbering.xml` via an `<w:abstractNum>` + `<w:num>` pair. Use `numId="500"` as the convention for this skill so it doesn't collide with the LaTeX-bullet `numId="200"` from Rule 4. Do NOT fake the numbering with `<w:t>[1]</w:t>` runs — the spacing between number and URL drifts as URL length varies.

2. **Colored numbers.** The number itself (the part rendered by the numbering machinery, not the paragraph content) must be **bold** and **maroon `#8B2820`**, set via `<w:rPr>` inside the `<w:lvl>` block of the abstractNum:

   ```xml
   <w:abstractNum w:abstractNumId="500">
     <w:lvl w:ilvl="0">
       <w:start w:val="1"/>
       <w:numFmt w:val="decimal"/>
       <w:lvlText w:val="%1."/>
       <w:pPr><w:ind w:left="640" w:hanging="360"/></w:pPr>
       <w:rPr><w:b/><w:color w:val="8B2820"/></w:rPr>   <!-- bold-maroon NUMBER -->
     </w:lvl>
   </w:abstractNum>
   <w:num w:numId="500"><w:abstractNumId w:val="500"/></w:num>
   ```

3. **`ReferenceItem` paragraph style for uniform spacing.** Define a new paragraph style with **Aptos** 10pt body color (`#1A1A1A`), `<w:contextualSpacing/>`, and `spacing` after 120 — so adjacent reference paragraphs collapse the inter-paragraph spacing and produce a tidy list regardless of how many lines a single URL wraps to. The hanging indent on the numId places the number in a fixed gutter so multi-line wrap doesn't disturb the alignment.

4. **Each reference paragraph contains ONLY the hyperlinked URL.** No leading literal `[N]` text — Word renders the number, the paragraph holds just the `<w:hyperlink>` block (with sub-coral color `#D85A3F` and matching coral underline). The structure is:

   ```xml
   <w:p>
     <w:pPr>
       <w:pStyle w:val="ReferenceItem"/>
       <w:numPr><w:ilvl w:val="0"/><w:numId w:val="500"/></w:numPr>
     </w:pPr>
     <w:hyperlink r:id="rIdRef1">
       <w:r>
         <w:rPr><w:color w:val="D85A3F"/><w:u w:val="single" w:color="D85A3F"/></w:rPr>
         <w:t>https://pfizer.com/press/q3-2025</w:t>
       </w:r>
     </w:hyperlink>
   </w:p>
   ```

The full OOXML — including the abstractNum/num pair, the `ReferenceItem` `<w:style>` block, and a sample reference paragraph — is in `references/docx_recipe.md` under "References section". Reminder: `numbering.xml` schema requires all `<w:abstractNum>` blocks to precede all `<w:num>` blocks; if the file already has the LaTeX bullet's `<w:abstractNumId="200">` and `<w:numId="200">`, insert the new `abstractNumId="500"` after the existing abstractNums but before the existing nums.

### 10. Table-row source citations and adjacent-duplicate cleanup

**Why.** Two systematic defects show up in AI-generated landscape tables and stay invisible until you actually read the references column:

- **(a) Source cells that name a publication but carry no link.** A table row like `Pfizer | drug discovery | 2025 | Reuters` says "the source is Reuters" but provides no clickable evidence. The reader can't verify the row, and it visually clashes with sibling rows that DO carry citations like `[5]`.
- **(b) Adjacent duplicate citations within a single cell.** When a cell originally had multiple anchor-fragment hyperlinks all pointing into the same article (e.g. `pfizer.com/press#section-1` and `pfizer.com/press#section-2`), the deduplication pass from Rule 8 collapses both to the same number — so the cell renders `[5][5]` (or worse, `[10][10][10]`). It looks like a typo and adds no information.

**How — (a) every row in a source/citation column must carry an inline citation marker.**

When restyling an existing report:

1. Walk every table that has a `Sources`, `Source`, `Citation`, or `References` column (typically the rightmost column). Match the header cell text case-insensitively.
2. For each body row in that table, check whether the source cell contains at least one `<w:hyperlink>` whose visible text matches `^\[\d+\]$` (an inline `[N]` marker).
3. If it does NOT — i.e. the source cell is plain text like "Reuters", "Bayer press", or "Merck press" naming a publication but with no link — WebSearch for the actual article using the row's company name + use case + date as the query (e.g. `Pfizer drug discovery 2025 Reuters`).
4. Append a numbered citation hyperlink to the source cell. Add the URL as a new `<Relationship>` entry in `word/_rels/document.xml.rels` and as a new unique reference at the end of the References section (consuming the next number from the dedup map in Rule 8).
5. If WebSearch can't surface a credible URL, fall back to the company's press-release homepage (e.g. `https://www.merck.com/news/`) — never fabricate a URL, and never invent a path that you have not verified actually loads.

**How — (b) adjacent duplicate citations within the same cell are forbidden.**

This rule applies to **every cell in every column**, not just the Sources column. The check is: scan each cell's run sequence; whenever two consecutive `<w:hyperlink>` elements resolve to the same `[N]` (after Rule 8's dedup pass), drop the later one. Keep ONLY the first occurrence, and delete every subsequent identical hyperlink-and-text pair (including any whitespace text run sitting between them, if it's purely separator whitespace).

Pseudo-pattern, before:

```xml
<w:tc>
  <!-- ... -->
  <w:p>
    <w:r><w:t xml:space="preserve">Pfizer-BioNTech mRNA platform </w:t></w:r>
    <w:hyperlink r:id="rIdCite5a">
      <w:r><w:rPr><w:color w:val="D85A3F"/><w:u w:val="single"/></w:rPr><w:t>[5]</w:t></w:r>
    </w:hyperlink>
    <w:hyperlink r:id="rIdCite5b">
      <w:r><w:rPr><w:color w:val="D85A3F"/><w:u w:val="single"/></w:rPr><w:t>[5]</w:t></w:r>
    </w:hyperlink>
  </w:p>
</w:tc>
```

After (drop the second `[5]` hyperlink — keep the first only):

```xml
<w:tc>
  <!-- ... -->
  <w:p>
    <w:r><w:t xml:space="preserve">Pfizer-BioNTech mRNA platform </w:t></w:r>
    <w:hyperlink r:id="rIdCite5a">
      <w:r><w:rPr><w:color w:val="D85A3F"/><w:u w:val="single"/></w:rPr><w:t>[5]</w:t></w:r>
    </w:hyperlink>
  </w:p>
</w:tc>
```

The same logic applies to `[10][10][10]` triples (keep only the first; delete the second and third) and to longer runs. The check is purely positional: consecutive sibling hyperlinks in the same paragraph that resolve to the same `[N]` collapse to a single hyperlink.

### 11. Table and figure caption sizing — never heading-tier

**Why.** Captions are labels for the artifact below them, not section dividers. Styling captions with `Heading 1` (44 half-points / 22pt + a full-width coral underline rule) dwarfs the table or figure that follows and confuses the visual hierarchy: the eye reads the caption as the start of a new section instead of as a sub-label for the artifact. The caption must read smaller than `Heading 1` and visually subordinate to the surrounding section heading, so the reader's eye flows section heading -> caption -> table/figure.

**How.** Use a dedicated `TableCaption` paragraph style for both table and figure captions. The style must be:

- **Aptos** (NOT Aptos Display — Aptos Display is reserved for the cover title and section H1s).
- **Bold**, **maroon `#8B2820`**, **11pt** (`<w:sz w:val="22"/>` — 22 half-points).
- Spacing `before="240"` and `after="160"`, with `<w:keepNext/>` and `<w:keepLines/>` so the caption stays attached to the table or figure that follows it across page breaks.
- **No heavy coral underline rule.** The coral underline is reserved for `Heading 1`. Caption identity is carried by the size and color alone.
- **Single-line fit.** The caption text must fit on one line at the document's content width. If a caption is too long to fit, edit the caption text — do not let it wrap and do not bump the size up.

The same `TableCaption` style applies to figure captions ("Figure N. ..."). Table and figure captions share the same visual tier; they should look identical except for the `Table N.` vs `Figure N.` prefix.

The OOXML pattern for the `TableCaption` style block (paste into `styles.xml`):

```xml
<w:style w:type="paragraph" w:styleId="TableCaption">
  <w:name w:val="Table Caption"/>
  <w:basedOn w:val="Normal"/>
  <w:next w:val="Normal"/>
  <w:qFormat/>
  <w:pPr>
    <w:spacing w:before="240" w:after="160"/>
    <w:keepNext/>
    <w:keepLines/>
  </w:pPr>
  <w:rPr>
    <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
    <w:b/>
    <w:color w:val="8B2820"/>
    <w:sz w:val="22"/>
    <w:szCs w:val="22"/>
  </w:rPr>
</w:style>
```

When restyling an existing report, walk every paragraph immediately preceding a `<w:tbl>` (or wrapping a figure / inline image) — if it's currently styled `Heading1`, `Heading 1`, or any heading-tier style, reassign its `<w:pStyle w:val="..."/>` to `TableCaption`. The full recipe lives in `references/docx_recipe.md` under "Table and figure caption style (`TableCaption`)".

### 12. Table cell font sizing to prevent awkward wrapping

**Why.** Table cells are narrow. A 9-column landscape table at 6.5"+1"+6.5" landscape content width (~13.5") leaves ~1.4" per column. At default 12pt body size, that's roughly 12 characters per line per column — far too few to fit common scientific or business terms ("immunology", "anti-cancer", "AlphaFold-based", "neurodegeneration"). A token that doesn't fit either wraps mid-word with a hyphen (looks unprofessional) or wraps in the middle of a token without a hyphen (looks broken). Lowering the cell text to 8pt nearly doubles the available characters per line and eliminates the wrap problem.

The remedy is to size cell text small enough that any single word fits in its column. Every word in every table cell must fit naturally — no mid-word hyphenation, no wrap that breaks a token before it's complete.

**How — column-count sizing rules.**

| Table column count | Body cell font size | Header row font size |
|--------------------|---------------------|----------------------|
| 4 columns or fewer | 11pt (`<w:sz w:val="22"/>`) — same as document body | 11pt bold |
| 5–7 columns        | 10pt (`<w:sz w:val="20"/>`) | 11pt bold |
| 8 columns or more  | 8–9pt (`<w:sz w:val="16"/>` or `<w:sz w:val="18"/>`) | one tier larger than body but never above 11pt |

For an 8-column landscape table, this resolves to: header row 9pt bold, body cells 8pt.

**Header row constraint.** The header row stays one tier larger than body cells but **never exceeds 11pt** — even on a 4-column table, the header doesn't bump to 12pt or 14pt. The maroon header fill carries the visual emphasis; size escalation isn't needed.

**Hyperlink / citation runs inside cells.** Hyperlink runs (`[N]` citations) inside cells must inherit the same size as the surrounding body cell. Don't let citation `<w:rPr>` blocks override back to the default 12pt — explicitly set `<w:sz>` on every citation hyperlink run in a table cell to match the cell body text.

**Disable doc-wide automatic hyphenation.** Do NOT include `<w:autoHyphenation/>` in `word/settings.xml`. If it's present, remove it. Hyphens are a wrapping band-aid that look unprofessional in tables and pull the eye away from real punctuation. Sizing the cell text per the column-count guideline above is the correct fix; auto-hyphenation is the wrong fix.

**OOXML pattern for cell-level `<w:sz>`** (every run inside the cell carries its own `<w:sz>` since cells don't inherit from a per-cell style):

```xml
<w:tc>
  <w:tcPr><w:tcW w:w="1440" w:type="dxa"/></w:tcPr>
  <w:p>
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
        <w:sz w:val="16"/>      <!-- 8pt body cell -->
        <w:szCs w:val="16"/>
      </w:rPr>
      <w:t>cell content</w:t>
    </w:r>
  </w:p>
</w:tc>
```

The full recipe — including the column-count sizing table, header-row sizing, in-cell hyperlink sizing, and the `settings.xml` removal pattern — lives in `references/docx_recipe.md` under "Table cell font sizing".

### 13. Every named claim in body prose must carry an inline citation

**Why.** AI-generated reports tend to over-cite the FIRST mention of a topic in a paragraph and leave the rest of the paragraph uncited, even though every named claim should be traceable. The Executive Summary is the most common offender because its job is to enumerate many sources in compressed form, which makes the missed-citation pattern especially visible. The earlier citation rules (Rules 7-10) cover tables and de-duplication, but they don't make explicit that the SAME standard applies to ALL body prose — especially the Executive Summary, Findings, and any other section that names specific companies, partnerships, deals, or metrics. This rule fills that gap: treat the Executive Summary like the table — every named partnership, deal, or outcome carries its `[N]`.

**How.** When restyling an existing report:

1. Walk every paragraph in every body section (Executive Summary, Findings, Discussion, Conclusions, body chapters — but NOT the cover page, page headers/footers, or the References list).

2. For each paragraph, identify every **named factual claim**. A "named factual claim" is any phrase that:
   - Names a specific organization or person (e.g. "Novartis", "Mayo Clinic", "the FDA").
   - Names a specific deal, study, or program (e.g. "Lilly's NVIDIA AI factory", "the SUMMIT-1 trial", "Anthem's value framework").
   - States a specific number, percentage, dollar amount, date, or quantitative outcome (e.g. "$1.7B milestone", "180h to 80h", "Q3 2025", "55% reduction").
   - Quotes or paraphrases a stated position from a source (e.g. "Roche mentions NVIDIA NeMo guardrails", "the AASM recommends ...").

3. For each such claim, check whether an inline citation `[N]` follows it (either immediately after the claim text or at the end of the sentence containing it).

4. If no citation follows, identify the source from context (often the cited source is already in the document's References list — the same study or press release that was cited elsewhere) and add the appropriate `[N]` marker. Reuse existing reference numbers wherever possible. Only mint a new reference number when the underlying source genuinely isn't in the existing References list — in that case, WebSearch for the source URL and add a new entry.

5. Within a single sentence that names multiple sources, **each source must get its own marker placed immediately after its name**. The pattern `Sowa 2016[1], Trotti 2021[2], and AASM 2021[3]` is correct; `Sowa 2016, Trotti 2021, and AASM 2021[1]` is wrong — readers can't tell which marker supports which name. This restates the per-source marker placement rule from Rule 10 — cross-reference it.

**Concrete worked example — Executive Summary paragraph.**

Before (every named partnership shares a single trailing citation, or worse, no citation at all):

> Key trends include drug discovery platforms (Novartis–Isomorphic, Takeda–Nabla/Iambic, AstraZeneca–Algen/CSPC), AI-powered R&D collaborations (Merck–Mayo, Sanofi–QuantHealth, GSK–Helix, AstraZeneca–Immunai), and advanced computing infrastructure (Lilly's NVIDIA AI factory, Merck's Google Cloud partnership, Roche's NVIDIA-powered AI hub).

After (every named partnership carries its own marker):

> Key trends include drug discovery platforms (Novartis–Isomorphic[6], Takeda–Nabla/Iambic[5][15], AstraZeneca–Algen/CSPC[8][17]), AI-powered R&D collaborations (Merck–Mayo[19], Sanofi–QuantHealth[12], GSK–Helix[11], AstraZeneca–Immunai[4]), and advanced computing infrastructure (Lilly's NVIDIA AI factory[1], Merck's Google Cloud partnership[9], Roche's NVIDIA-powered AI hub[7]).

Each named partnership now carries its own marker. The reader can trace any single claim back to a specific source.

**Renumbering cross-reference.** Any citations newly added to body prose under this rule must trigger a renumbering pass — the de-duplication and first-appearance ordering rules in Rules 7 and 8 already define this. Specifically: after adding new citations, walk the entire document again in reading order; re-derive the canonical `[1]`...`[N]` ordering based on each unique source's FIRST appearance; rewrite every marker and the References list accordingly. Do not restate the renumbering algorithm here — see Rule 8 (de-duplicate and re-order citations) and Rule 9 (rebuild the References section as a real Word numbered list).

## How to apply the style by artifact type

The skill is centered on Word documents, since that's the primary report deliverable. Other artifact types share the palette but call for proportionally different sizing.

### Word documents (.docx)

The reference implementation is in `references/docx_recipe.md`. The single most important block is the `styles.default.document.run` — once the body font is `Aptos` and color is `#1A1A1A` there, every plain `TextRun` inherits without per-run overrides.

When restyling an existing docx (the common case for this skill), the order of operations is:

1. Apply tokens: replace heading colors with maroon, body color with ink, hyperlink color with coral, default font with **Aptos** (and **Aptos Display** for the cover title / section H1s).
2. Run the thirteen required transformations above, in order.
3. Build the cover page (Rule 1 balance, with the five centered blocks).
4. Add page header + footer with coral hairlines and PAGE/NUMPAGES fields.
5. Apply H1 coral underline rule.
6. Restyle tables: maroon header, white sans bold text, hairline beige body borders, generous cell margins. Apply `TableCaption` style (Rule 11) to every table caption and figure caption — never `Heading 1`. Size cell text per the column-count guideline (Rule 12) so no token wraps mid-word.
7. Lift wide tables to dedicated landscape pages (carry the title block onto the landscape page with them — see cohere-style-lite's landscape-section guidance; the algorithm is the same here). For any landscape-lifted wide table, recheck Rules 11 (caption uses `TableCaption`, not `Heading 1`) and 12 (cell text sized per column count; remove `<w:autoHyphenation/>` from `settings.xml` if present).
8. Restyle inline citations to coral underlined. Backfill missing inline citations in body prose so every named factual claim in the Executive Summary, Findings, and other body sections carries its own `[N]` marker (Rule 13).
9. Rebuild References section using the deduplicated, real Word numbered list (numId 500, bold maroon numbers, `ReferenceItem` style — see Rules 7 and 9). Backfill missing source-cell citations and collapse adjacent duplicate `[N][N]` cell citations per Rule 10.
10. Validate by rendering to PDF.

### HTML / dashboards / posters

When the user wants the same palette on a web artifact or poster, drop the same tokens into CSS variables: `--maroon: #8B2820; --coral: #D85A3F; --ink: #1A1A1A; --slate: #6B6B6B; --beige: #E8DFD3;`. Use `"Aptos", "Aptos Display", "Calibri", sans-serif` for body, H2/H3, eyebrow, labels, table headers, and captions; use `"Aptos Display", "Aptos", "Calibri", sans-serif` for the cover title and the section H1s. Coral for links and accent rules; maroon for primary heading color; ink for body. Keep the background white.

### Slide decks (.pptx)

Less common for this skill — but if the user asks for a deck companion to a Cohere-style report, use **Aptos Display** titles in maroon, **Aptos** for body / labels / table headers, coral as the single emphasis color, white backgrounds, and coral horizontal rules under section headings. Reserve the table treatment (maroon header + white Aptos + beige body borders) for any data slides.

## Avoiding mistakes

- **Don't pair Aptos with another sans family.** Aptos is the single typeface for the entire report — Aptos for body and most text, Aptos Display for the cover title and section H1s. Mixing in a serif (Georgia, Tiempos) or a competing sans (Helvetica Neue, Inter, Lato) breaks the typographic system.
- **Don't over-use coral.** Coral is reserved for: eyebrow, citations and hyperlinks, the H1 underline, header/footer hairlines, and the rule beneath the cover eyebrow. Body text never goes coral; H1/H2/H3 are maroon, not coral.
- **Don't reintroduce a cream page background.** The lite version uses cream; this one is on white. If the user wants cream, they want cohere-style-lite, not this skill.
- **Don't skip the cover-page vertical balance.** A cover with the title block jammed against the top reads as a draft, not a report. Compute the padding.
- **Don't fake numbered lists with literal "1." text.** Use Word's `numId` machinery so the hanging indent stays consistent across long and short entries.
- **Don't leave LaTeX scraps visible.** The `\begin{easylist}` family of artifacts is the single most common defect in pandoc-converted docs and the most visible failure of this style if missed.
- **Don't style table or figure captions as `Heading 1`.** Captions are sub-labels for the artifact below, not section dividers. Use `TableCaption` (Aptos bold maroon 11pt, no underline rule) — see Rule 11.
- **Don't leave table cells at the document body 12pt size in wide tables.** A 9-column landscape table at 12pt wraps every multi-syllable word mid-token; size cells 8pt for 8+ columns, 10pt for 5–7, 11pt for 4 or fewer (Rule 12). And remove `<w:autoHyphenation/>` from `settings.xml` — hyphens are not the fix, smaller cell text is.
- **Don't include Cohere's logo, wordmark, or proprietary typeface.** This is a portable visual identity inspired by editorial conventions, not a brand reproduction. License terms below.

## License

This skill packages a portable visual identity — colors, type sizes, layout conventions — that draws inspiration from common editorial report conventions and from the look of long-form research reports. It does not reproduce Cohere's logo, wordmark, proprietary typefaces, or any other copyrighted brand asset. Users are free to apply these tokens to their own documents without attribution, but should not represent the resulting output as official Cohere materials.

## References

- `references/docx_recipe.md` — drop-in docx-js style block, cover-page builder + raw OOXML, header/footer pattern, table treatment, inline-citation styling, landscape-section pattern, numbered table caption pattern, `TableCaption` paragraph style (Rule 11), table cell font sizing by column count (Rule 12), body-prose named-claim citation backfill (Rule 13), LaTeX residue cleanup, diagram-to-PNG render pattern, References-section + citation deduplication algorithm.
- `assets/palette.svg` — palette swatches as an SVG you can include in a brand-guideline page.
