# pptx recipe — Cohere-style-lite

For slide decks, use the standard pptx skill workflow (image-based or python-pptx, depending on the artifact). Apply the Cohere palette through the slide master and a small set of recurring layouts. **Typography is Aptos throughout** (Microsoft's new geometric sans, the default replacement for Calibri in Office), with **Aptos Display** reserved for the cover-slide title and any other display-tier headlines.

## Cover slide

The first slide is a cover slide, not a content slide. The composition mirrors the docx cover page: forest eyebrow, coral title, coral rule, italic ink subtitle, slate dateline — all centered, on a cream background, no logo or imagery.

- **Eyebrow** — Aptos, 16pt, bold, forest `#39594D`, all caps, tracking +60. Positioned at roughly the vertical center of the slide minus 1.5".
- **Title** — Aptos Display, 60–72pt, bold, primary coral `#FF7759`, tracking -2. Centered just above the slide's vertical midline.
- **Coral rule** — single horizontal line, 2pt, primary coral, ~3" wide centered below the title, with ~12pt of breathing room above and below.
- **Subtitle** — Aptos, 22pt, italic, deep ink `#1A1A1A`. One line, the angle of the deck.
- **Dateline** — Aptos, 14pt, slate `#6B6B6B`, all caps optional, tracking +30. Anchored to the lower third of the slide.

Do not put a logo, image, or wordmark on the cover. Do not put a "Confidential" disclaimer or a slide number on the cover. The cohere cover is purely typographic.

## Slide background

Set every slide background to warm cream `#FAF6F1`. In python-pptx:

```python
from pptx.dml.color import RGBColor

for slide in prs.slides:
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0xFA, 0xF6, 0xF1)
```

## Title block

The slide title is the place where coral lives. Set the title text in primary coral `#FF7759`, weight bold, character spacing tight, and place a 1.5pt coral rule beneath it.

- Title font: Aptos Display, 40pt, bold, color `#FF7759`, tracking -1
- Subtitle: Aptos, 20pt, regular, color `#39594D` (forest accent)
- Body bullets: Aptos, 16pt, regular, color `#1A1A1A`

## Callout boxes

Use cream-filled rectangles with a 2pt coral top border to highlight a key data point or quote. Inside, place a single line of forest-accent forest text and a deep-ink body line. This is the most distinctive recurring slide element.

```
┌──────────────────────────────────────────────────────────┐  ← 2pt coral rule on top
│ Forest accent label                                      │
│                                                          │
│ Larger ink-colored body content                          │
│                                                          │
└──────────────────────────────────────────────────────────┘  cream fill, no border on bottom
```

## Tables

- Header row: cream fill, forest-accent bold text, 1pt coral bottom border on the header row
- Body rows: no fill, beige `#E8DFD3` hairline rules between rows
- Avoid alternating row stripes — the look is restrained, not zebra

## Charts

- Bars / lines: primary coral for the focal series; forest for a secondary series; muted slate for context
- Axis labels: 10pt forest accent
- Gridlines: beige `#E8DFD3`, hairline weight only
- No chartjunk: no border around the plot area, no background fill, no shadows

## Wide-table slides

Source catalogues, evidence-mapping tables, and other dense multi-column layouts (8+ columns) should occupy their own dedicated slide rather than squeeze alongside bullet points. A full slide gives the table room to breathe horizontally while maintaining the 16:9 aspect ratio.

- **Table slide layout:** single table as the primary content, with margins of ~0.5" on all sides.
- **Table title and subtitle on the same slide.** The slide's title placeholder carries the table's title (e.g. "Value, role, and organizational placement"), and any one-line subtitle sits directly below in italic ink. The deck should never put a section heading on one slide and the table it introduces on the next — the reader loses the connection.
- **Table styling:** apply the standard Cohere table treatment (cream header, forest bold text, coral underline on the header row, beige hairline dividers between body rows).
- **No bullet points or competing content** on a wide-table slide. The table is the focal point.
- **Slide background:** warm cream, matching every other slide in the deck.

This keeps data legible and ensures the narrative flow of the slide deck is not disrupted by cramped, unreadable tables.

## Citations on slides

When a slide deck references external sources via bracketed citations like `^[1]` or `^[12]`:

### Footnote citations on body slides

Include the citation marker in the body text in sub-coral (`#D85A3F`), rendered as a superscript. List all references in the slide's footer at 9pt muted slate (`#6B6B6B`), right-aligned, in the format: `[1] https://example.com  [2] https://example.com`.

### References slide

Alternatively, collect all citations on a final slide titled "References" (as a standard H2 in the Cohere style, set in **Aptos**). Format the references as a numbered list with:
- Bold forest (`#39594D`) numbering
- Sub-coral (`#D85A3F`) underlined hyperlinks
- 11pt font
- Hanging indent so wrapped URLs align under the URL text, not the number

This mirror the docx References section structure and deduplication: walk the presentation in slide order, deduplicate by URL, assign sequential numbers on first appearance, and collect in the References slide.

## Footnote format for body slides (if using footer references)

Footer text is set in **Aptos** at 9pt, slate color, right-aligned.

```
Slide body text with citation marker^1 references something.

Footer (9pt slate, right-aligned): [1] https://example.com  [2] https://example.com```

Note: Do not underline footer citations — they are reference pointers at small size and an underline at 9pt reads as visual clutter. The URLs in the footer are typically hyperlinked for clickability in digital decks, but the underline is optional.
