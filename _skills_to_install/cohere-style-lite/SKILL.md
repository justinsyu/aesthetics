---
name: cohere-style-lite
description: Apply a Cohere-inspired warm-coral / cream / forest visual identity to artifacts — Word documents, slide decks, HTML reports, PDFs, posters, and dashboards. Typography is Aptos throughout (Microsoft's new geometric sans, the default replacement for Calibri in Office), with Aptos Display reserved for the largest headings and cover titles. Use this skill whenever the user asks for "Cohere style", "Cohere theme", "Cohere look", "warm coral and cream", or references Cohere's brand aesthetic. Also use it when the user asks to restyle an existing artifact and mentions Cohere by name, even briefly. This is a lightweight visual treatment — it captures the color tokens and typographic feel (Aptos / Aptos Display) without using any proprietary Cohere logos, mark, or copyrighted assets.
---

# Cohere-style-lite

A compact visual treatment inspired by Cohere's brand language: warm coral primary, cream backgrounds, near-black text, restrained geometric sans typography (Aptos throughout, with Aptos Display at the largest sizes). It is designed to make research documents, white papers, slide decks, and dashboards feel confident, modern, and editorial without using any proprietary marks.

## When to use this skill

- The user explicitly asks for "Cohere style", "Cohere theme", "Cohere look", or references Cohere's aesthetic.
- The user asks to restyle an existing artifact (docx, pptx, html, pdf) and mentions Cohere by name.
- The user describes the look in adjacent terms — "warm coral and cream", "editorial AI white-paper feel" — and Cohere has been mentioned earlier in the conversation.
- The user wants a fresh artifact built in this style from scratch.

Do not use this skill to recreate Cohere's logo, wordmark, or proprietary fonts. The visual identity is the color palette and typographic posture, not Cohere's trademarks.

## The design tokens

These tokens are the source of truth. When applying the style, use them verbatim — do not introduce arbitrary blues, greens, or rainbow accents.

### Color palette

| Role            | Hex      | RGB              | Typical usage                                               |
|-----------------|----------|------------------|-------------------------------------------------------------|
| Primary coral   | `#FF7759` | 255, 119,  89    | H1 headings, accent rules, key callouts, primary buttons    |
| Sub-coral       | `#D85A3F` | 216,  90,  63    | H2 headings, hyperlinks, secondary accents                  |
| Forest accent   | `#39594D` | 57,   89,  77    | H3 headings, table-header text on cream, chart axis labels  |
| Deep ink        | `#1A1A1A` | 26,   26,  26    | Body copy                                                   |
| Muted slate     | `#6B6B6B` | 107, 107, 107    | Captions, abbreviation glosses, table footnotes             |
| Warm cream BG   | `#FAF6F1` | 250, 246, 241    | Page background, table-header fills, callout boxes          |
| Soft beige rule | `#E8DFD3` | 232, 223, 211    | Table dividers, hairline rules, card borders                |

### Typography

The look depends on a geometric humanist sans with slightly tightened tracking on display sizes. Cohere's actual typeface is proprietary, so this skill defaults to **Aptos** (Microsoft's new geometric sans, the default replacement for Calibri in Office) for body and headings, paired with **Aptos Display** at the largest sizes (H1, cover title).

| Tier            | Font (with fallbacks)                                  | Size (docx / pptx / html)        | Treatment                                  |
|-----------------|--------------------------------------------------------|----------------------------------|--------------------------------------------|
| Display H1      | "Aptos Display", "Aptos", "Calibri", sans-serif        | 22pt / 40pt / 2.75rem            | Bold, character-spacing −10 (tight)        |
| H2              | "Aptos", "Aptos Display", "Calibri", sans-serif        | 14pt / 28pt / 1.75rem            | Bold, character-spacing −6                 |
| H3              | "Aptos", "Aptos Display", "Calibri", sans-serif        | 11pt / 20pt / 1.25rem            | Bold, character-spacing −4                 |
| Body            | "Aptos", "Aptos Display", "Calibri", sans-serif        | 10pt / 14pt / 1rem               | Regular, line-height 1.45                  |
| Caption / muted | Same family                                            | 9pt  / 11pt / 0.875rem           | Italic or regular, color = Muted slate     |

Use only one display family. Do not pair a serif with the sans — that is a different brand language. The skill defaults to **Aptos** (Microsoft's new geometric sans, the default replacement for Calibri in Office) for all text, with **Aptos Display** reserved for the largest H1 / cover-title sizes. Calibri is the portable fallback when Aptos is unavailable.

### Structural treatments

These are the recurring layout signatures that make the style feel coherent rather than just a recolor.

- **H1 with coral underline rule.** Set the H1 in primary coral. Place a 1.5pt rule beneath it in the same coral, with ~6pt of space between the text and the rule.
- **Cream-filled table headers with a coral underline.** Table header rows use the cream background, forest-accent text in bold, and a 1pt coral rule along the bottom of the header row. Body cells have no fill; rows are separated only by hairline beige rules.
- **Coral hyperlinks.** Hyperlinks use sub-coral (`#D85A3F`) with a matching underline. They never use default browser blue.
- **Generous whitespace.** Margins are wide. The page should feel uncrowded. For docx, use 0.75–1" margins. For HTML, use a 760–880px content column with 1.5–2rem vertical rhythm between sections.
- **Cream page background.** When the medium supports it (docx, pptx, html, pdf), set the page background to warm cream rather than pure white. Pure white reads as generic; cream is the most distinctive single move in the palette.
- **Editorial cover page.** Long-form artifacts (white papers, evidence reviews, briefs, decks) lead with a cover page rather than diving straight into an H1. The cover stack is a five-line composition centered on the page: a forest, all-caps, wide-tracked eyebrow ("EVIDENCE BRIEF", "RESEARCH NOTE", "WHITE PAPER"); a large coral title with tight tracking; a short coral underline rule; an italic ink-colored subtitle giving the angle of the piece; and a slate, all-caps, wide-tracked dateline at the bottom. The body content begins on a new page after a section break.

## Cover page (editorial lead-in)

For any artifact long enough to be called a *report*, *brief*, *review*, *white paper*, or *deck* — anything past about 3 pages — open with a Cohere-style cover page. The cover composition is fixed and deliberately spare: it should communicate "serious editorial document," not "title slide."

The five lines, top to bottom:

1. **Eyebrow** — short label categorizing the document (e.g. "EVIDENCE BRIEF", "RESEARCH NOTE", "WHITE PAPER", "EVIDENCE REVIEW"). Forest accent (`#39594D`), bold, all caps, character-spacing +60 (very wide), 11pt in docx.
2. **Title** — the document's actual title. Primary coral (`#FF7759`), bold, character-spacing −16 (tight), large display size: 32pt in docx, 56–72pt in pptx, 3.5–4rem in HTML.
3. **Coral underline rule** — a single coral horizontal rule, 1.5–2pt thick, set as a paragraph bottom border with ~6pt of space above and 18pt below. The rule is short relative to the page width because it sits below a centered title; let it match the natural width of the title block.
4. **Subtitle** — the angle, scope, or one-line takeaway. Italic, deep ink (`#1A1A1A`), 14pt in docx, 18–20pt in pptx, 1.25rem in HTML. Often a noun phrase ("A registry-led evidence map of interventional trials, May 2021 – May 2026") rather than a sentence.
5. **Dateline** — month and year, e.g. "May 2026". Muted slate (`#6B6B6B`), all caps optional, character-spacing +30 (wide), 12pt in docx. Sits well below the subtitle, near the lower third of the page.

All five lines are centered horizontally. Pad the eyebrow ~3" from the top of the page (use `before:4000` twentieths-of-a-point in docx) so the title block sits comfortably in the upper-middle of the page rather than at the very top.

Then insert a section break (with `<w:titlePg/>` so the cover page does not show a header/footer) and start the body content. Do NOT repeat the document title as an H1 on page 2 — the cover page is the title.

The portable XML for a docx cover page is in `references/docx_recipe.md` under "Cover page". For pptx, see `references/pptx_recipe.md`. For HTML, see `references/html_recipe.md`.

## Citations, references, and wide tables

Long-form research documents often depend on dense citations and multi-column evidence tables. Three structural conventions handle these affordances without breaking the reading flow.

### Inline citation styling

When the source artifact uses bracketed inline citations like `[1]` or `[12]`, restyle the citation marker in sub-coral (`#D85A3F`, the same color as H2 headings and hyperlinks). The superscript treatment depends on context:

- **In running body prose**: render citations as superscript, typographically tight like a footnote marker. Remove any underline — at superscript size, an underline reads as visual noise rather than affordance.
- **In table cells**: keep citations at body size (not superscript). Table cells are already dense and small; superscript would shrink them further. Preserve the underline so the citation reads as a clickable link even at reduced size.

Hyperlinks behind the citation marker must be preserved. Clicking a citation should still navigate to the referenced source URL. See `references/docx_recipe.md` "Inline citations", `references/html_recipe.md` for CSS patterns, and `references/pptx_recipe.md` for slide citations.

### Distributing citations across sentences

The most frequent citation error in AI-generated research documents is a **paragraph that names multiple sources by author or study name, but carries only one citation marker at the end**. Readers cannot tell which claim corresponds to which source.

**The anti-pattern:** "The core treatment reviews are: Sowa 2016, Trotti et al. Cochrane 2021, and Maski et al. AASM 2021. The adjacent reviews are Boulanger et al. 2024..." followed by a single `[3]` at the paragraph's end. The `[3]` does not clarify which source backs which claim. Often it links to the wrong source entirely — the paragraph may end with a sentence about source B, but the trailing citation links to source A.

**The rule:** every source that is named explicitly by author name, study title, or review name in running prose must have its own inline citation marker placed immediately after the name. The pattern is "Sowa 2016[1]" or "Trotti et al. Cochrane 2021[2]", not "Sowa 2016, Trotti et al. Cochrane 2021... [1]". This is a hard requirement when multiple sources are mentioned within a single paragraph.

Trailing citations at the end of a paragraph are still acceptable — but only when the entire paragraph genuinely traces to a single source, or when a final sentence offers a distinct claim supported by one source while prior sentences covered different material. Use trailing citations sparingly as a reinforcement, never as the sole citation for a multi-source paragraph.

**The misattribution failure mode:** the existing trailing citation often has the wrong hyperlink. Before supplementing a multi-source paragraph with new inline citations, verify that any existing trailing citation's URL actually supports the claim it sits next to. If the paragraph ends with "...consistent with the AASM recommendations" and the trailing citation links to a Cochrane review, the citation is misattributed and must be re-targeted to the correct AASM source — or removed entirely if the paragraph should end with Cochrane support instead.

**Before-and-after example:**

*Before (broken):*
"Recent studies emphasize the importance of early assessment. Annes et al. meta-analysis from 2019 found a 35% improvement in outcomes with early intervention. Johnson et al. in their 2023 systematic review confirmed this pattern. Both Nordstrom et al. and the ICMR consensus statement from 2022 recommend a screening window of within 48 hours. [8]"

The single `[8]` at the end might link to any of those sources — likely the last one mentioned, but the reader cannot know. The citation is ambiguous for three out of four named sources.

*After (correct):*
"Recent studies emphasize the importance of early assessment. Annes et al. meta-analysis from 2019[1] found a 35% improvement in outcomes with early intervention. Johnson et al. in their 2023 systematic review[2] confirmed this pattern. Both Nordstrom et al.[3] and the ICMR consensus statement from 2022[4] recommend a screening window of within 48 hours."

Each named source now carries its own citation marker. A reader looking up any claim can immediately identify the source. The trailing citation is removed because the paragraph does not build toward a single final claim — it builds toward multiple coordinated ones.

### Validating citation URLs for correctness

**The URL-behind-the-marker failure.** A citation marker can be formatted correctly, positioned correctly, and still point to the wrong article. The most common culprit: **PubMed search URLs masquerading as article URLs**. A URL like `pubmed.ncbi.nlm.nih.gov/?term=34942138` is a *search query for the term 34942138*, not the article PMID 34942138 itself. The search result may surface a completely different paper (often whatever PubMed's algorithm ranks first). The correct article URL is `pubmed.ncbi.nlm.nih.gov/34942138/`. Visually, both URLs look plausible; only opening the URL reveals the mismatch. PMC IDs have a related failure: a "2017 Cochrane review" linked to `PMC8144933` might actually resolve to the 2021 Cochrane *update* (the same paper listed separately in references as the 2021 version). The year is wrong, but the citation marker looked fine.

**A paired SR + guideline publication is often cited as only one.** When an organization publishes both a systematic review and a companion clinical practice guideline (e.g., Maski et al. 2021 AASM), many AI generators add a citation relationship for only the SR or only the guideline, even though the prose later says "the AASM guideline summary indicates..." or "the systematic review found..." This split prose-to-citation mapping is silent and breaks links for readers trying to verify the guideline-specific claim.

**How to verify in practice.** Open every unique URL in the references / relationships list, or WebFetch / search by PMID/DOI. Confirm that the page title, article title, or metadata on the far end actually matches what the prose claims. For example: is the article titled "Sodium oxybate for narcolepsy: 2021 AASM clinical practice guideline" (guideline) or "Sodium oxybate for narcolepsy: systematic review" (SR)? Is the publication year 2017 or 2021? Does the authors list match what the prose names? This is one-time work per unique URL because of deduplication — checking all 28 sources in a 40-page evidence review takes two hours — and it is the *only* way to catch search-URL and year-mismatch errors.

If you find a mismatch:
- **Replace search URLs with direct article URLs.** `?term=PMID` → `pubmed.ncbi.nlm.nih.gov/PMID/`.
- **Correct mismatched years.** A citation with the wrong year (linked to the 2021 version when the prose says 2017) may need a new relationship pointing to the correct year, or a re-target of the existing URL if the 2017 version is not in the repo and the paragraph can be rewritten to match 2021 without loss of meaning.
- **Add missing companion publications.** When the prose mentions both a SR and a guideline but only one is in relationships, add the missing one. Cite the guideline *only* for guideline-specific claims ("AASM guideline summary"), the SR *only* for SR-specific claims, and cite both for paired claims if ambiguous.

### References section with deduplicated numbering

When inline citations are present, append a new `## References` section (Heading 2) at the very end of the document body. This references list is numbered, with each reference as a clickable URL (or full bibliographic entry where available). The numbering follows a deduplication algorithm:

- **Walk the document in reading order.** The first URL encountered becomes reference `[1]`, the second unique URL becomes `[2]`, and so on.
- **Deduplicate by URL.** If multiple inline citations point to the same source URL, they all link to the same reference number.
- **Number is dense.** The list runs from 1..N where N is the count of unique sources. No gaps.
- **Format: bold forest number from a real numbered list, sub-coral underlined hyperlink.** Use Word's actual numbering machinery — define an `abstractNum`/`num` pair in `numbering.xml` with decimal format and bold-forest run properties for the number, then attach each reference paragraph to that numId via `<w:numPr>`. Don't fake the numbering with literal "1." "2." text, because the spacing between number and URL drifts as the URL length changes. With the real list, the hanging indent is consistent across all 28 entries.
- **Position: at the end.** The References section sits after the last content section, in portrait orientation. Do not place references on a landscape page.

See `references/docx_recipe.md` "References section" for the OOXML pattern and numbering algorithm. For HTML and pptx approaches, consult the respective recipe files.

### Tables on dedicated landscape pages

Multi-column tables with more than ~4 columns of dense text should occupy their own landscape page rather than trying to squeeze into portrait. This frees up horizontal space and makes the data legible.

In OOXML (docx), each `<w:tbl>` is wrapped in section breaks: an empty paragraph with portrait `sectPr` immediately before the table, and an empty paragraph with landscape `sectPr` immediately after. Content following the landscape section re-opens portrait. For pptx, wide tables get their own dedicated slide rather than sitting alongside bullet points. For HTML, wide tables escape the narrow reading column via a full-width container.

**Keep the table's title and subtitle on the same landscape page as the table.** A table introduced by a heading (e.g., an H2 "Themes in the source base" or H3 "Value, role, and organizational placement") looks broken when the heading sits at the bottom of the prior portrait page and the table opens cold on the next landscape page. The portrait section break must be inserted *before* the heading, not between the heading and the table, so the title block travels into the landscape section. The same applies to a subtitle paragraph wedged between the heading and the table — it belongs with them.

When the table sits under a parent + child heading hierarchy (an H2 section heading with optional intro paragraph, followed by an H3 that directly titles the table), the parent should travel with the table too — provided no body content separates the H2 from the H3 + table. Walking backward from the table, keep capturing through stacked headings and any subtitle paragraphs wedged between them, and stop only at the first body paragraph that's clearly normal flow content (or at a previous table or section break). This makes the parent section heading appear on the same landscape page as its first child table, instead of being orphaned on the prior portrait page.

**Merge adjacent landscape sections to avoid blank pages.** When two tables sit back-to-back with no real portrait body content between them — i.e., table 1's landscape break would fall immediately before table 2's title block — emitting a `sectPr=portrait` break between them creates a section that contains nothing but two empty paragraphs, which Word renders as a blank portrait page. Instead, drop the previous landscape break and let the two table clusters share one continuous landscape section. The reader sees table 1 → table 2's title → table 2, with no blank page wedged in.

The benefit is that 8-column source catalogues and evidence-mapping tables have room to breathe without sacrificing portrait reading flow for the rest of the document, and a reader never lands on a "where's the table title?" landscape page. See the landscape-sections guidance in each recipe file.

### Figures and rendered diagrams

When the source artifact contains a mermaid timeline, a flowchart, or any diagram that's currently text-only (e.g. a `SourceCode`-styled paragraph holding raw mermaid), render it to a Cohere-styled PNG and embed the PNG, replacing the text block. Word renders mermaid as raw text by default, and a published deliverable should not show a code listing where a chart belongs.

The image itself uses the Cohere palette: warm-cream background, coral primary for axis lines and node markers, forest for axis labels and section dividers, ink for body labels, and slate for captions or muted text. Avoid black, gray, or saturated chart-junk colors. PIL with DejaVu Sans (or Aptos if available) is sufficient for editorial timelines and simple node diagrams; matplotlib is fine for charts but takes more work to bring to the same typographic feel.

Embed the image as an inline picture, not an anchored floater. Center it on the page, give it 6.5" of width on US Letter portrait (matching the body text column), and let the height scale by aspect ratio. If the diagram is genuinely too wide for portrait — e.g. a 12-event horizontal timeline — keep it at 6.5" and let the labels stay readable, or move the figure into its own landscape section the same way wide tables do.

## How to apply the style by artifact type

For each artifact type, the recipe is the same: set the background, set the font, recolor headings, restyle tables and links, and add the coral rule under the H1. Specific code snippets live in `references/`.

### Word documents (.docx)

Use the docx-js library and configure the styles in the Document constructor. The full reference implementation is in `references/docx_recipe.md` — copy the snippet directly when starting from scratch, or adapt the tokens when restyling an existing build script.

The single most important thing to get right in docx is the default style block. If the body font is set there, every plain TextRun inherits it without needing per-run font properties.

### Slide decks (.pptx)

Use the pptx skill's image-based slide approach (the standard Anthropic pptx pattern), then place text and shape elements over a cream-filled slide background. Apply coral to titles, forest to subtitles, and use cream-filled rectangles with a coral top border for key callouts. The reference recipe is in `references/pptx_recipe.md`.

### HTML / web reports / dashboards

Drop the CSS variable block from `references/html_recipe.md` into a `<style>` tag and reference the variables throughout. The variables map one-to-one onto the design tokens above.

### PDFs (canvas-design / poster output)

Set the canvas background to cream, use coral for the title block, forest for any axis labels or small chart annotations, and ink for the body. Treat coral as a precious resource — use it on the title and one or two emphasis points per page, not on every heading at every level.

## Restyling an existing artifact

When the user already has an artifact and asks for a Cohere-style pass, do not rebuild the content. Identify the points where color and typography are set and make targeted edits:

1. **Find the style scope.** In docx, this is the styles block in the docx-js Document; in HTML, the CSS variables or theme file; in pptx, the slide master and any inline shape fills.
2. **Swap the tokens.** Replace primary heading color with primary coral, secondary heading color with sub-coral, body text with deep ink, page or section backgrounds with warm cream, and hyperlinks with sub-coral. Replace any blue, indigo, or purple defaults wherever they appear.
3. **Set the body font in the default style.** This single change propagates to every otherwise-unstyled text run.
4. **Add the coral underline rule under the H1** if there isn't one already.
5. **Convert table headers from the prior fill color to cream + coral underline + forest text.**
6. **Restyle inline citations.** If the artifact uses bracketed inline citations like `[1]`, recolor them to sub-coral. In running prose, make them superscript with no underline. In table cells, keep them at body size with underline preserved. See the "Citations, references, and wide tables" section above.
7. **Consolidate citation numbering and add a References section.** Walk the document in reading order, deduplicate citations by URL, assign new sequential numbers on first appearance, and append a numbered References section at the end with deduped hyperlinks. If there are no citations in the original, skip this step.
8. **Lift wide tables to landscape pages, with their titles.** Any table with more than ~4 columns of dense text should occupy its own landscape page (or dedicated slide for pptx, or full-width container for HTML). Use section breaks in docx to wrap the table. Place the portrait section break *before* the table's title block — the immediately preceding heading, any subtitle paragraph between heading and table, and any parent heading directly above (when no body content separates parent from child) — so the entire title block travels onto the landscape page with the table. When two tables sit back-to-back with nothing but title blocks between them, merge them into one landscape section by dropping the redundant break, otherwise an empty portrait section sneaks in between and prints as a blank page.

9. **Render any text-form diagrams (mermaid timelines, flowcharts, ASCII figures) as Cohere-styled PNGs and embed them.** Replace the source-code paragraph with a centered inline image, 6.5" wide on portrait, using cream/coral/forest palette. Drop the original code block.
10. **Fact-check inline citations AND table citations, including URLs.** Many AI-generated reports treat citations as sequential markers without verifying that each `[N]` actually points to a source supporting the claim it's attached to. Walk every citation — body inline AND every cell in every table — identify the claim being made, and confirm the URL on the citation hyperlink supports that claim by opening it or fetching its metadata. Pay special attention to PubMed search URLs (`?term=`) and PMC IDs that may point to a different publication year than the prose states. See "Validating citation URLs for correctness" in the Citations section for detection guidance and verification workflow. If a URL is wrong, redirect the hyperlink to the correct source. A claim that lists *multiple* sources ("AMCP format guidance; NICE RWE framework; FDA RWE guidance; EMA RWE vision; ICER value framework.") needs *all* of those citations side-by-side (`[1][2][3][4][5]`), not just one — splitting the marker is mandatory whenever the cell text or sentence enumerates more than one source. This rule also applies to paragraphs that name multiple studies by author or title across multiple sentences: each named source must carry its own inline citation marker immediately after its name, not a single trailing citation at the paragraph end (see "Distributing citations across sentences" in the Citations section for worked examples). Also strip stray entity-citation markers that appear inside author/organization cells (e.g., "Anke-Peggy Holtorf[7] et al." where the [7] points to an unrelated URL — these are AI-tooling artifacts and should be removed). After correcting, re-renumber so the references list reflects the new first-appearance order.

    *Sub-rule: strip AI-tooling residue.* Some AI document-generation pipelines emit invisible private-use-area markers around entity references — e.g. `entity["organization","McKinsey & Company","consulting firm"]` rendered as readable text in the docx. Walk every `<w:t>` element and replace these with the entity's bare name; also strip any orphaned PUA characters (U+E000–U+EFFF). They render as empty boxes or strange symbols in some readers.
11. **Add a cover page** if the artifact is long enough to warrant one (see "Cover page" above) and the original didn't have a styled cover. If the original opened with the document title as an H1, remove that H1 — the cover is the title — and start body content with the first H2.
12. **Verify by rendering.** Convert the artifact to PDF (for docx/pptx) or take a screenshot (for HTML), and visually confirm the palette is consistent, citations are styled correctly, no blank pages have crept in between sections, and nothing has been left in the old color scheme.

The reason these steps work in this order is that each one constrains the next — once the default font is set, the per-run font overrides become discoverable as inconsistencies, and once the heading colors are set, leftover hyperlinks in default blue stand out immediately.

## Avoiding mistakes

- **Do not introduce a serif.** The look is sans throughout — **Aptos** for body and headings, **Aptos Display** for the largest H1 / cover-title sizes. Pairing a serif body with the Aptos display reads as editorial-magazine, not Cohere.
- **Do not over-use coral.** Coral is the accent. If every heading at every level is coral, the hierarchy collapses. Use primary coral for H1 and a few key emphasis points; use sub-coral for H2 and links; use forest for H3 and table-header text.
- **Do not use pure white backgrounds.** Cream is the single most identity-bearing token in the palette. Losing it makes the artifact feel generic.
- **Do not include Cohere's logo, wordmark, or proprietary typeface.** This skill is a visual identity in the spirit of Cohere's aesthetic, not a reproduction of Cohere's trademarks. The user has not requested — and is not entitled to — proprietary brand assets.
- **Do not pair coral with red.** Reserve red for error / warning states only, and use it sparingly. Coral and red are too close in hue and clash.

## References

- `references/docx_recipe.md` — drop-in docx-js style block and table treatment.
- `references/pptx_recipe.md` — slide background, title style, callout box, and table styling for pptx.
- `references/html_recipe.md` — CSS variables and base styles.
- `assets/palette.svg` — the palette swatches as an SVG you can include in a brand-guideline page.
