---
name: cohere-style-tan
description: Build or revise tan editorial HTML slide decks and single-page infographic graphics in the Cohere-style visual system. Use when Codex needs to create or update HTML slides/graphics, match the current tan/black/lime/blue/orange FDA-style deck, avoid clipped rounded containers or slide overflow, or export PDFs whose colors, backgrounds, gradients, hyperlinks, and text behavior match the intended browser rendering.
---

# Cohere Style Tan

## Overview

Use this skill for polished 16:9 HTML slide decks and single-page editorial infographics that use the tan editorial style from the current FDA workforce/budget slides.

For slide decks or infographics that need selectable text and links, the default PDF workflow uses Chrome DevTools `Page.printToPDF` with CSS page sizing and printed backgrounds enabled. For tall one-page infographics or cases where the user requires exact PNG color parity, use the raster workflow: DevTools `Page.captureScreenshot` of the target `.sheet`/page element, then lossless PNG-backed PDF assembly. Do not use Chrome's CLI `--screenshot` as the final source for tall graphics; it can clip the bottom of rounded containers when the viewport height equals the document height.

## Workflow

1. Inspect the current HTML slide deck first when one is available. For the original reference deck, use `examples/fda_workforce_budget_slides.html` if it exists.
2. Load `references/style-guide.md` before creating or revising slides.
3. Keep each slide as a fixed 16:9 composition, using `.slide` sections and a canonical 1600 x 900 export viewport. For slide decks that use the tan radial background, generate a 1600 x 900 PNG background and place it as a full-slide `<img>` layer behind the selectable text before PDF export; do not rely on CSS radial gradients for final print PDFs. For one-page infographics, use a fixed `.sheet` wrapper with explicit width/height and `overflow: hidden`.
4. Check every slide in a real browser at desktop size and at the user's current review viewport when possible. Fix overlapping, clipped, or hidden content before exporting.
5. Always review rendered images of every slide before final delivery, using a fresh-context subagent/reviewer when available, plus a contact sheet and spot checks of dense slides. Decrease excessive blank space, empty panel interiors, and overlarge padding unless the whitespace is intentionally serving hierarchy and has been visually confirmed.
6. Export the PDF with `scripts/export_html_slides_pdf.mjs`. Use default `print` mode for selectable slide PDFs; use `--mode raster --selector .sheet` for exact-color one-page infographic PDFs.
7. Render-check the PDF back to images and compare every slide when practical, and always compare the first page, any dark/chart-heavy pages, source pages, and any page recently edited.
8. For raster infographic PDFs, inspect the bottom 10-15% of the rendered PDF and source PNG to confirm rounded panel borders are complete and the bottom padding is intentional, not clipped.
9. Confirm the PDF contains extractable text and URI link annotations when the slide deck has links. Raster PDFs intentionally will not have extractable text.
10. Re-check prior user constraints before final export, especially requests to omit author/social attribution, avoid custom icons, use neutral scientific language, or avoid terminal punctuation in titles.

## HTML Requirements

- Use semantic slide containers: `<article class="slide">` for every page.
- Do not leave implementation labels such as `cohere-style-tan` or `Cohere-style tan HTML rebuild` visible in the final artifact unless the user explicitly asks for them.
- Use a 1600 x 900 print target: `@page { size: 1600px 900px; margin: 0; }`.
- Set `.slide { height: 100vh; min-height: 100vh; overflow: hidden; }` for browser review and `height: 900px; min-height: 900px;` in print CSS.
- For single-page graphics, use a wrapper such as `.sheet { width: 1200px; height: <final-px>; overflow: hidden; }` and `@page { size: 1200px <final-px>; margin: 0; }`. Do not trim the wrapper height until a rendered screenshot confirms all bottom borders, shadows, labels, and descenders are visible.
- Set `body, *, *::before, *::after { -webkit-print-color-adjust: exact; print-color-adjust: exact; }` in print CSS.
- Put deck backgrounds on `.slide`, not only `body`, when the PDF must match the HTML. Body-level gradients can paginate or color-shift differently in Chrome print.
- For the standard tan deck background, generate or export a 1600 x 900 PNG background and place it as a real full-slide `<img>` layer behind selectable text before native/print PDF export. This preserves selectable text while avoiding print-rendering shifts from CSS radial or linear gradients. Treat CSS gradients as browser-only previews unless a rendered PDF check proves parity.
- Use a background layer pattern like `.slide-bg-img { position:absolute; inset:0; z-index:0; width:100%; height:100%; object-fit:cover; pointer-events:none; user-select:none; }` and `.slide > *:not(.slide-bg-img) { position:relative; z-index:1; }`.
- Scope responsive shrink rules to `@media screen and (...)` so mobile/browser review typography does not leak into PDF print rendering.
- Do not remove backgrounds or data fills in print CSS. Suppress CSS `box-shadow` in print when PDFKit renders shadows as gray blocks.
- Hide scrollbars in browser captures with `scrollbar-width: none` and `::-webkit-scrollbar { display: none; }`.
- Design each slide so the content fits without vertical scrolling. Do not rely on clipped overflow to hide unfinished content.
- If important information does not fit on one slide/page, split it across two pages rather than trimming substantive content or reducing text below readable size.
- Avoid excessive blank space inside panels, source sections, quote layouts, and metric blocks. If a slide reads as sparse in the rendered image, tighten padding, rebalance columns, reduce empty panel height, or add substantive source/context content.
- Reference and source cards must have visually balanced top and bottom padding around their text; do not let the first line feel pinned to the top or the last line sit too close to the bottom edge.
- Use objective, scientific, neutral language appropriate for a medical journal when summarizing biomedical, regulatory, or clinical evidence. Avoid promotional, conversational, advocacy-oriented, or rhetorically loaded phrasing unless it is a clearly attributed direct quote.
- Do not use periods at the ends of slide titles, section titles, card titles, table headings, or other title-style display text. Body text and direct quotes may retain source punctuation.
- Multi-line titles and headlines must have enough line-height and inter-line spacing that characters, ascenders, descenders, strokes, and punctuation never touch or visually collide between lines. Verify rendered browser/PDF output and increase line-height or spacing rather than accepting touching title lines.
- Keep citations visible and compact; use superscript-style citation markers rather than long URLs in body slides.

## PDF Export

Use the bundled exporter from this skill directory:

```bash
node /Users/justinyu/.codex/skills/cohere-style-tan/scripts/export_html_slides_pdf.mjs \
  --input /absolute/path/to/slides.html \
  --output /absolute/path/to/slides.pdf \
  --screenshots-dir /absolute/path/to/export/screenshots \
  --render-check-dir /absolute/path/to/export/render-check
```

For a single-page infographic where exact PDF colors must match the PNG:

```bash
node /Users/justinyu/.codex/skills/cohere-style-tan/scripts/export_html_slides_pdf.mjs \
  --input /absolute/path/to/graphic.html \
  --output /absolute/path/to/graphic.pdf \
  --mode raster \
  --selector .sheet \
  --width 1200 \
  --height 2402 \
  --screenshots-dir /absolute/path/to/export/screenshots \
  --render-check-dir /absolute/path/to/export/render-check
```

Exporter behavior:

- Launches Chrome headless at 1600 x 900.
- Loads the HTML with screen media, waits for document and font readiness, and scrolls to each selected page element for screenshot QA.
- Supports `--selector`; default is `.slide`, and `.sheet` is the preferred target for single-page infographic exports.
- Captures oversized `.sheet`/page elements with DevTools `Page.captureScreenshot` plus `captureBeyondViewport` and an element clip, avoiding Chrome CLI screenshot clipping at the bottom edge.
- Switches to print media and exports the HTML with Chrome `Page.printToPDF`.
- Uses `printBackground: true`, `preferCSSPageSize: true`, zero margins, and a 16:9 paper size.
- In `--mode raster`, assembles the captured PNGs into a lossless image-backed PDF so PDF colors match the screenshot source.
- Optionally renders the generated PDF back to PNG files for visual QA when `pdftoppm` is installed.
- Reports extracted text length and URI annotation count so selectability and links can be checked.
- Fails on detected slide overflow unless `--allow-overflow` is passed.

If a user asks for selectable text, use native/print PDF export. Only pass `--mode raster` when a user explicitly chooses a non-selectable image PDF for maximum visual parity, or when a tall infographic PDF must match the PNG exactly and selectability is not required.

## QA Checklist

- The HTML page shows no visible scrollbars in the slide viewport.
- Eyebrows, titles, citations, and slide numbers do not overlap.
- Titles and card headings do not end with periods.
- Language is objective, neutral, and appropriate for the subject matter; biomedical/regulatory decks should read like a medical journal or regulatory briefing, not marketing copy.
- Main body text is as large as the layout permits while preserving hierarchy and fit; minimum text generally stays at 10-11px depending on text density, with smaller sizes reserved only for unavoidable citations or metadata.
- Large metric cards and bar charts fit inside their panels at 1600 x 900.
- Panels and source slides do not contain excessive unused interior space; padding is visually balanced after rendered-image review.
- For cards or charts with stacked or repeated bars, verify rendered PDF/PNG outputs before finalizing; if bottom whitespace remains excessive, increase bar/row spacing or rebalance the component rather than leaving dead space.
- Reference/source card render-checks verify the first line and last line have symmetric breathing room above and below the text block.
- Dark panels export as near-black, not washed-out gray.
- Lime, blue, orange, pink, gray, and red fills match the browser screenshots.
- Tall infographic bottom borders and rounded corners are visible in both source PNG and PDF render-checks; no panel is cut off to reduce padding.
- Footer/source bands have balanced breathing room above the bottom page or sheet edge, comparable to the top spacing, and this is verified in render-check output.
- The PDF has one page per selected page element (`.slide` for decks, `.sheet` for single-page graphics).
- Text can be selected or extracted with `pdftotext`.
- Hyperlinks are clickable or visible as URI annotations when checked with `pypdf`.
- Render-check PNGs from the PDF match the original screenshot captures.
- For PNG-backed backgrounds, sample several background-only pixels from the browser screenshot and rendered PDF; the RGB values should match exactly or differ only by negligible antialiasing at object edges.

## Resources

- `references/style-guide.md`: design tokens, component rules, and layout guidance for this visual system.
- `scripts/export_html_slides_pdf.mjs`: deterministic Chrome HTML-to-PDF exporter for slide decks, with optional raster fallback.
