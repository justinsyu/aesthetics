# HTML recipe — Cohere-style-lite

Drop the CSS-variables block into a `<style>` tag at the top of the document, then reference variables throughout. The variables map directly onto the canonical design tokens. Typography is **Aptos** throughout (Microsoft's new geometric sans, the default replacement for Calibri in Office), with **Aptos Display** reserved for the largest H1 / cover-title sizes — so `--cohere-font` resolves to Aptos and `--cohere-font-display` resolves to Aptos Display.

## Base CSS

```css
:root {
  --cohere-coral:     #FF7759;
  --cohere-sub-coral: #D85A3F;
  --cohere-forest:    #39594D;
  --cohere-ink:       #1A1A1A;
  --cohere-slate:     #6B6B6B;
  --cohere-cream:     #FAF6F1;
  --cohere-beige:     #E8DFD3;

  --cohere-font: "Aptos", "Aptos Display", "Calibri", sans-serif;
  --cohere-font-display: "Aptos Display", "Aptos", "Calibri", sans-serif;
}

html, body {
  margin: 0;
  background: var(--cohere-cream);
  color: var(--cohere-ink);
  font-family: var(--cohere-font);
  font-size: 16px;
  line-height: 1.45;
}

main, article, .container {
  max-width: 880px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}

h1 {
  font-family: var(--cohere-font-display);
  font-size: 2.75rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--cohere-coral);
  border-bottom: 1.5px solid var(--cohere-coral);
  padding-bottom: 0.4rem;
  margin: 2.5rem 0 1.5rem;
}

h2 {
  font-family: var(--cohere-font);  /* Aptos */
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--cohere-sub-coral);
  margin: 2.25rem 0 1rem;
}

h3 {
  font-family: var(--cohere-font);  /* Aptos */
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--cohere-forest);
  margin: 1.75rem 0 0.75rem;
}

p, li {
  font-family: var(--cohere-font);  /* Aptos throughout */
  color: var(--cohere-ink);
}

a {
  color: var(--cohere-sub-coral);
  text-decoration: underline;
  text-decoration-color: var(--cohere-sub-coral);
}

a:hover { text-decoration-thickness: 2px; }

/* Inline citations — superscript in prose, body-size with underline in tables */
.citation, sup.citation {
  color: var(--cohere-sub-coral);
  text-decoration: none;
  font-weight: 500;
}

sup.citation {
  vertical-align: super;
  font-size: 0.75em;
}

td .citation, th .citation {
  text-decoration: underline;
  text-decoration-color: var(--cohere-sub-coral);
}

.muted, figcaption, .caption {
  color: var(--cohere-slate);
  font-size: 0.875rem;
}
```

## Tables

```css
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  font-size: 0.95rem;
}

thead th {
  font-family: var(--cohere-font);  /* Aptos */
  background: var(--cohere-cream);
  color: var(--cohere-forest);
  font-weight: 700;
  text-align: left;
  padding: 0.6rem 0.8rem;
  border-bottom: 2px solid var(--cohere-coral);
}

tbody td {
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid var(--cohere-beige);
  vertical-align: top;
}

tbody tr:last-child td { border-bottom: none; }

/* Wide tables: break out of the narrow reading column to full width.
   The .wide-table container should also wrap the table's heading and
   subtitle so the title travels with the table when the page is paged
   to PDF in landscape. */
.wide-table {
  width: 100vw;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  padding: 0 1.5rem;
}

.wide-table > h2,
.wide-table > h3 {
  /* keep the title visually attached to the table below it */
  max-width: 880px;
  margin: 2rem auto 0.5rem;
}

.wide-table table {
  margin: 0.5rem auto 2rem;
}

@media print {
  /* For print/PDF flows, prevent a page break between the table's
     heading and its body. */
  .wide-table { page-break-inside: avoid; break-inside: avoid; }
  .wide-table > h2,
  .wide-table > h3 { page-break-after: avoid; break-after: avoid; }
}
```

## References section

When the document includes citations, append a References section at the end of the body. Format each reference with a bold forest number, two spaces, and a sub-coral underlined hyperlink.

```html
<section class="references">
  <h2>References</h2>
  <ol class="references-list">
    <li><strong>1</strong>  <a href="https://example.com/source-one">https://example.com/source-one</a></li>
    <li><strong>2</strong>  <a href="https://example.com/source-two">https://example.com/source-two</a></li>
  </ol>
</section>
```

```css
.references-list {
  list-style: none;
  padding-left: 0;
}

.references-list li {
  margin: 0.5rem 0;
  padding-left: 2.5rem;
  text-indent: -2rem;       /* hanging indent */
}

.references-list strong {
  color: var(--cohere-forest);
  font-weight: 700;
  margin-right: 0.5rem;
}

.references-list a {
  color: var(--cohere-sub-coral);
  text-decoration: underline;
  text-decoration-color: var(--cohere-sub-coral);
}
```

## Callout boxes

```css
.callout {
  background: white;
  border-top: 2px solid var(--cohere-coral);
  padding: 1rem 1.25rem;
  margin: 1.5rem 0;
}

.callout-label {
  color: var(--cohere-forest);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
}
```

## Buttons

```css
.btn {
  display: inline-block;
  background: var(--cohere-coral);
  color: white;
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  border-radius: 4px;
  text-decoration: none;
  transition: background 120ms ease;
}

.btn:hover { background: var(--cohere-sub-coral); }

.btn-secondary {
  background: transparent;
  color: var(--cohere-sub-coral);
  border: 1.5px solid var(--cohere-sub-coral);
}
```

## Cover hero (long-form articles, white papers, landing pages)

For an editorial cover at the top of a long article — same composition as the docx and pptx covers.

```html
<header class="cohere-cover">
  <p class="eyebrow">Evidence Brief</p>
  <h1 class="cover-title">HEOR Teams in Biopharma</h1>
  <hr class="coral-rule" />
  <p class="cover-subtitle"><em>External evidence demands are rising while standalone HEOR groups are being embedded, split, or de-layered</em></p>
  <p class="dateline">May 2026</p>
</header>
```

```css
.cohere-cover {
  text-align: center;
  padding: 8rem 1rem 6rem;
  border: 0;
}

.cohere-cover .eyebrow {
  font-family: var(--cohere-font);  /* Aptos */
  color: var(--cohere-forest);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.875rem;
  margin: 0 0 1rem;
}

.cohere-cover .cover-title {
  /* override the default h1 — the cover title isn't a content H1 */
  font-family: var(--cohere-font-display);
  color: var(--cohere-coral);
  font-size: 3.75rem;
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 1.05;
  border: 0;
  padding: 0;
  margin: 0 0 1rem;
}

.cohere-cover .coral-rule {
  width: 6rem;
  height: 2px;
  background: var(--cohere-coral);
  border: 0;
  margin: 1.25rem auto;
}

.cohere-cover .cover-subtitle {
  color: var(--cohere-ink);
  font-size: 1.25rem;
  font-style: italic;
  max-width: 640px;
  margin: 0.5rem auto 3rem;
  line-height: 1.4;
}

.cohere-cover .dateline {
  font-family: var(--cohere-font);  /* Aptos */
  color: var(--cohere-slate);
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.875rem;
  margin: 0;
}
```

The cover is its own block before the article body. Don't repeat the title as an `<h1>` inside the article — the cover's `.cover-title` is the document title, and the article should start with the first content `<h2>`.

## Charts

For Chart.js or recharts, set tick / label fonts to **Aptos** so axis labels match the rest of the artifact, and configure the palette to use:
- Primary series: `var(--cohere-coral)` / `#FF7759`
- Secondary series: `var(--cohere-forest)` / `#39594D`
- Tertiary / context: `var(--cohere-slate)` / `#6B6B6B`
- Gridlines: `var(--cohere-beige)` / `#E8DFD3`
- Plot background: transparent (the cream page background shows through)
