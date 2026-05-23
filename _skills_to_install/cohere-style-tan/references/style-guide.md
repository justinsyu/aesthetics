# Cohere Style Tan Guide

## Source

Base new work on the current tan editorial HTML slide deck style. When available, inspect `examples/fda_workforce_budget_slides.html` before designing. If that file is unavailable, use this guide as the canonical style reference.

## Design Tokens

```css
:root {
  --ink: #10120f;
  --muted: #5c6257;
  --paper: #f6f1e8;
  --paper-2: #ebe4d6;
  --card: #fffaf0;
  --line: #1b1f17;
  --lime: #d7ff5f;
  --orange: #ffb86b;
  --blue: #b8d8ff;
  --pink: #ffd3e0;
  --gray: #d6d0c2;
  --red: #ff8a76;
  --shadow: 0 18px 48px rgba(16, 18, 15, 0.08);
  --radius: 26px;
}
```

Use tan paper as the dominant field, black ink for headlines and dark panels, muted olive-gray for explanatory copy, and lime/blue/orange/pink/red only as strong data accents. Avoid letting the page collapse into one color family.

## Background

Use a soft tan paper base with subtle radial color fields. For final slide-deck PDFs, build this as a precomposited 1600 x 900 PNG and place it as a full-slide image layer behind the content so the PDF render matches the browser screenshot:

```html
<article class="slide">
  <img class="slide-bg-img" src="tan_slide_background.png" alt="" aria-hidden="true" />
  <div class="wrap">...</div>
</article>
```

```css
.slide { position: relative; background: var(--paper); }
.slide-bg-img {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
  user-select: none;
}
.slide > *:not(.slide-bg-img) {
  position: relative;
  z-index: 1;
}
```

Use CSS gradients only for quick browser preview or when the rendered PDF has been explicitly checked for parity:

```css
body {
  background: var(--paper);
}

.slide {
  background:
    radial-gradient(circle at top left, rgba(215,255,95,0.32), transparent 34rem),
    radial-gradient(circle at 84% 12%, rgba(184,216,255,0.28), transparent 26rem),
    var(--paper);
}
```

The native HTML PDF exporter sometimes preserves CSS gradients, but PDFKit, Preview, and the in-app PDF viewer can shift them pink or patterned even when browser screenshots look correct. Default to the PNG-backed background for final slide decks, then verify parity by sampling background-only pixels from the browser screenshot and PDF render-check PNG.

## Typography

- Font stack: `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.
- Hero titles: about 92px at 1600px width, line-height `.9`, weight `500`, tight negative tracking.
- Section titles: about 60px, line-height `.96`, weight `500`.
- Metric numbers: 50px or larger, weight `900`, very tight tracking.
- Body copy: muted color, generous line-height, and as large as the layout permits while remaining compact enough to avoid overflow.
- Minimum font size should generally stay at 10-11px depending on text amount; use smaller text only for unavoidable citations, source URLs, footnotes, or metadata.
- Use different header sizes to express hierarchy; avoid flattening slide titles, section headers, card titles, and table headings into one size.
- Use large type with restraint. In cards, panels, and tables, size text to the container instead of forcing hero-scale typography.

## Layout

- Canonical slide size: 1600 x 900.
- Wrapper: `width: min(1360px, calc(100vw - 48px)); margin: 0 auto;`.
- Every slide is a single viewport with no scrolling.
- If important information does not fit on one slide/page, split it across two pages rather than trimming substantive content or reducing text below readable size.
- Use `article.slide` for each page and include slide numbers such as `01 / 10`.
- Use grid layouts for metrics and comparisons: two, three, or four equal columns.
- Maintain enough vertical clearance under large titles; eyebrow pills should never sit on top of title descenders.
- For bottom footer/source bands, keep the spacing above the bottom page or sheet edge visually balanced with the top spacing, then verify it in PDF render-check output.
- Make responsive compact rules `@media screen and (...)`, not generic `@media (...)`, so print/PDF output keeps the desktop slide typography.

## Components

- Eyebrow pills: lime fill, black border, uppercase, heavy weight, rounded full pill.
- Panels/cards: tan or cream fill, black border, radius around 26px, light shadow in browser.
- Dark panels: `#11130f` background with tan text and translucent tan secondary copy.
- Data bars: rounded tracks and fills, with lime for current annual/reference values, blue for prior years, orange/red for warnings or newest stress signals.
- Tables: black outer grid with cream cells and black header row.
- Source slides: two-column source lists with compact but readable type.
- Do not add author/social attribution, custom icons, or visible implementation/style-system labels unless the user explicitly requested them for that artifact.

## Avoid

- Nested cards inside cards.
- Decorative blobs or purely ornamental graphics.
- Hidden overflow that clips important content.
- Tiny tables that require zooming to understand.
- Raster PDF as the default export path when text selection and links matter.
- Raster export for any artifact where the user asks for selectable text; use native/print PDF export instead.
