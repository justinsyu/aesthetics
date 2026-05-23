# docx-js / OOXML recipe — Cohere-style-report

Drop-in style configuration for the Aptos-maroon-coral editorial report look. The single most important block is the `styles.default.document.run` — it sets the body font (**Aptos**) and color across every otherwise-unstyled TextRun, which means no per-run overrides are needed for plain body copy. Display-tier text (the cover title and section H1s) uses **Aptos Display**.

## Tokens

```javascript
const REPORT = {
  maroon:   '8B2820', // titles, section headings, table header background
  coral:    'D85A3F', // eyebrow, rules, links, citations, header/footer hairlines
  ink:      '1A1A1A', // body
  slate:    '6B6B6B', // captions, muted lines
  beige:    'E8DFD3', // table dividers (hairline borders on body cells)
  white:    'FFFFFF', // background; table-header text
  // Aptos throughout. Aptos Display reserved for the cover title and section H1s
  // (the display tier). Calibri is the portable fallback when Aptos is not installed.
  fontBody:         'Aptos',           // body, H2, H3, eyebrow, labels, table header, header, footer, captions
  fontHeader:       'Aptos Display',   // cover title, H1 (sections) - display tier
  fontHeaderFooter: 'Aptos',           // page header + footer (matches body)
};
```

## Document styles block (docx-js)

```javascript
styles: {
  default: {
    document:  { run: { font: REPORT.fontBody, size: 24, color: REPORT.ink } },   // 12pt body, Aptos
    hyperlink: { run: { color: REPORT.coral, underline: { type: 'single', color: REPORT.coral } } },
  },
  paragraphStyles: [
    { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run:       { size: 84, bold: true, font: REPORT.fontHeader, color: REPORT.maroon, characterSpacing: -12 },   // Aptos Display
      paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 240 } } },
    { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run:       { size: 44, bold: true, font: REPORT.fontHeader, color: REPORT.maroon },                          // Aptos Display
      paragraph: { spacing: { before: 480, after: 200 }, outlineLevel: 0,
                   border: { bottom: { style: BorderStyle.SINGLE, size: 14, color: REPORT.coral, space: 6 } } } },
    { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run:       { size: 32, font: REPORT.fontBody, color: REPORT.maroon },                                        // Aptos
      paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 1 } },
    { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run:       { size: 28, font: REPORT.fontBody, color: REPORT.maroon },                                        // Aptos
      paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } },
    { id: 'Hyperlink', name: 'Hyperlink', basedOn: 'Normal', next: 'Normal',
      run: { color: REPORT.coral, underline: { type: 'single', color: REPORT.coral } } },
  ],
},
```

## Page background

Plain white. Do not set a `background` color — the absence of fill is the style.

```javascript
const doc = new Document({
  // no background; white page
  styles: { /* as above */ },
  sections: [/* ... */],
});
```

## Cover page

Five centered blocks. The eyebrow's `before` spacing is what pushes the composition toward the vertical center of the page.

### docx-js (paragraph builders)

```javascript
import { Paragraph, TextRun, AlignmentType, BorderStyle } from 'docx';

function coverPage({ eyebrowCategory, title, subtitle, description, scope, period, reportDate }) {
  const display = REPORT.fontHeader;   // Aptos Display - title only
  const body    = REPORT.fontBody;     // Aptos - everything else

  const eyebrow = (text, color = REPORT.coral, size = 22) => new TextRun({
    text: text.toUpperCase(),
    font: body, bold: true, color,                                  // Aptos
    size, characterSpacing: 60,
  });

  return [
    // 1. Coral eyebrow: "RESEARCH  ·  INSIGHTS"
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 3600, after: 120 },
      children: [eyebrow('Research  ·  Insights')],
    }),
    // 2. Italic-ish category sub-line
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 40 },
      children: [new TextRun({ text: eyebrowCategory, italics: true, font: body, color: REPORT.slate, size: 22 })],   // Aptos italic
    }),
    // 3. Coral horizontal rule
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 40, after: 240 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: REPORT.coral, space: 6 } },
      children: [new TextRun({ text: '' })],
    }),
    // 4. Title (maroon, Aptos Display, 42pt, tight tracking)
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 120, after: 200 },
      children: [new TextRun({
        text: title, font: display, bold: true, color: REPORT.maroon,    // Aptos Display
        size: 84, characterSpacing: -12,
      })],
    }),
    // 5. Sans subtitle
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 200 },
      children: [new TextRun({ text: subtitle, font: body, color: REPORT.ink, size: 26 })],   // Aptos
    }),
    // 6. Italic Aptos description
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 600 },
      children: [new TextRun({ text: description, italics: true, font: body, color: REPORT.ink, size: 24 })],  // Aptos italic
    }),
    // 7. Metadata: SCOPE / COVERAGE PERIOD / REPORT DATE
    ...['Scope', scope, 'Coverage period', period, 'Report date', reportDate].map((text, i) => {
      const isLabel = i % 2 === 0;
      return new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: isLabel ? 200 : 0, after: isLabel ? 20 : 0 },
        children: [isLabel
          ? eyebrow(text, REPORT.coral, 18)
          : new TextRun({ text, font: body, color: REPORT.ink, size: 22 })],   // Aptos
      });
    }),
  ];
}

// Wrap cover and body in two separate sections
sections: [
  {
    properties: {
      titlePage: true,                                  // suppress header/footer on cover
      page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
    },
    children: coverPage({ /* args */ }),
  },
  {
    properties: { page: { /* normal portrait body */ } },
    headers: { default: bodyHeader },
    footers: { default: bodyFooter },
    children: bodyContent,
  },
],
```

### Raw OOXML cover-page block (for surgical edits)

Prepend to the start of `<w:body>`. The eyebrow's `before="3600"` is the value that produced visual balance on US Letter portrait in the reference docx. Adjust to match the page-height / content-height computation in SKILL.md Rule 1.

```xml
<!-- 1. RESEARCH . INSIGHTS eyebrow (coral, Aptos, all caps, wide tracking) -->
<w:p>
  <w:pPr><w:spacing w:before="3600" w:after="120"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:b/><w:color w:val="D85A3F"/><w:spacing w:val="60"/><w:sz w:val="22"/>
    </w:rPr>
    <w:t xml:space="preserve">Research  ·  Insights</w:t>
  </w:r>
</w:p>

<!-- 2. Italic Aptos sub-line: category -->
<w:p>
  <w:pPr><w:spacing w:before="0" w:after="40"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:i/><w:color w:val="6B6B6B"/><w:sz w:val="22"/>
    </w:rPr>
    <w:t xml:space="preserve">AI Strategy  ·  Pharmaceuticals</w:t>
  </w:r>
</w:p>

<!-- 3. Coral horizontal rule -->
<w:p>
  <w:pPr>
    <w:pBdr><w:bottom w:val="single" w:color="D85A3F" w:sz="12" w:space="6"/></w:pBdr>
    <w:spacing w:before="40" w:after="240"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:t xml:space="preserve"></w:t></w:r>
</w:p>

<!-- 4. Title (maroon, Aptos Display, ~42pt, tight tracking) -->
<w:p>
  <w:pPr><w:spacing w:before="120" w:after="200"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/>
      <w:b/><w:color w:val="8B2820"/><w:spacing w:val="-12"/><w:sz w:val="84"/>
    </w:rPr>
    <w:t xml:space="preserve">AI in pharma</w:t>
  </w:r>
</w:p>

<!-- 5. Sans subtitle -->
<w:p>
  <w:pPr><w:spacing w:before="0" w:after="200"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:color w:val="1A1A1A"/><w:sz w:val="26"/>
    </w:rPr>
    <w:t xml:space="preserve">Where the world's leading drugmakers are deploying AI in 2025-2026</w:t>
  </w:r>
</w:p>

<!-- 6. Italic Aptos description -->
<w:p>
  <w:pPr><w:spacing w:before="0" w:after="600"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:i/><w:color w:val="1A1A1A"/><w:sz w:val="24"/>
    </w:rPr>
    <w:t xml:space="preserve">A landscape review of AI-driven drug discovery, R&amp;D infrastructure, manufacturing, and diagnostics initiatives across leading pharmaceutical companies.</w:t>
  </w:r>
</w:p>

<!-- 7. Metadata triplet: SCOPE / COVERAGE PERIOD / REPORT DATE -->
<w:p>
  <w:pPr><w:spacing w:before="200" w:after="20"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:b/><w:color w:val="D85A3F"/><w:spacing w:val="60"/><w:sz w:val="18"/>
    </w:rPr>
    <w:t xml:space="preserve">Scope</w:t>
  </w:r>
</w:p>
<w:p>
  <w:pPr><w:spacing w:before="0" w:after="0"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="22"/></w:rPr>
    <w:t xml:space="preserve">Top global pharmaceutical companies; AI-driven discovery, R&amp;D, manufacturing, and diagnostics</w:t>
  </w:r>
</w:p>
<!-- Repeat for COVERAGE PERIOD and REPORT DATE -->

<!-- 8. Section break: cover is its own section with titlePg suppressing header/footer -->
<w:p>
  <w:pPr>
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840" w:orient="portrait"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"
               w:header="708" w:footer="708" w:gutter="0"/>
      <w:titlePg/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:pPr>
</w:p>
```

### Cover-page vertical balance

The eyebrow's `before` spacing is the load-bearing knob for vertical balance. On US Letter portrait with 1" margins, the printable area is roughly:

```
page_height_twips     = 15840
top_margin_twips      = 1440
bottom_margin_twips   = 1440
printable_height      = 15840 - 1440 - 1440 = 12960 twips ~= 9 inches
```

Sum the heights of the seven content blocks (eyebrow line, sub-line, rule, title, subtitle, description, metadata triplet — each one is its own `<w:p>`). A rough heuristic: each text line is ~`sz/2` points tall plus the `before+after` spacing on its paragraph. The title block (84-half-points = 42pt × ~1.2 line-height) is the dominant element at ~750 twips, plus its spacing.

Empirically, `before="3600"` on the eyebrow produced visual balance for the reference content (one-line title, two-line description, three metadata rows). For a longer title (two lines) or longer description, reduce `before` to `3000-3200`. For a shorter cover, increase to `4000`.

After laying out the seven content blocks, add a final empty paragraph with `before="600"` to balance the trailing whitespace, or use the last metadata row's `after` spacing if it sits naturally near the bottom.

## Page header (every body page, suppressed on cover)

Aptos maroon document title **left-aligned** + coral "Research · Insights" **right-aligned** via a right tab stop at the right page margin. Coral hairline below.

**Hard rules:**

- The header's left-hand text is **only** the document's main title — the same string shown on the cover page. No subtitle, no ": Executive summary", no eyebrow, no sub-heading appended. If the cover title is `AI in pharma`, the header reads exactly `AI in pharma`.
- The title is **left-aligned**; "Research · Insights" is **right-aligned** via the tab stop.
- Both runs are set in **Aptos** (`<w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>`), the new Office default that replaced Calibri. Body text is **Aptos** as well — Aptos is the single typeface throughout.
- The right tab stop sits at the right page margin: `w:pos="9360"` on portrait sections (8.5" page − 2×1" margins = 6.5" = 9360 twips). On landscape sections, use `w:pos="12960"` (11" page − 2×1" margins = 9" = 12960 twips). Each section's header file must use the tab position appropriate for that section's page width.

```xml
<!-- word/header1.xml — portrait body section -->
<?xml version="1.0" encoding="UTF-8"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p>
    <w:pPr>
      <w:pBdr><w:bottom w:val="single" w:sz="6" w:space="6" w:color="D85A3F"/></w:pBdr>
      <w:tabs><w:tab w:val="right" w:pos="9360"/></w:tabs>
      <w:spacing w:after="0" w:before="0"/>
    </w:pPr>
    <!-- Left: document title only — exact match to the cover title.
         No subtitle, no ": Executive summary", no eyebrow appended. -->
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
        <w:b/><w:color w:val="8B2820"/><w:sz w:val="18"/>
      </w:rPr>
      <w:t xml:space="preserve">AI in pharma</w:t>
    </w:r>
    <!-- Tab to the right margin -->
    <w:r><w:tab/></w:r>
    <!-- Right: coral "Research . Insights" mark, right-aligned by the tab stop -->
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
        <w:color w:val="D85A3F"/><w:sz w:val="18"/>
      </w:rPr>
      <w:t xml:space="preserve">Research  ·  Insights</w:t>
    </w:r>
  </w:p>
</w:hdr>
```

For a landscape section (wide-table page), use a separate header file with `w:pos="12960"` on the tab stop:

```xml
<!-- word/header2.xml — landscape section -->
<w:p>
  <w:pPr>
    <w:pBdr><w:bottom w:val="single" w:sz="6" w:space="6" w:color="D85A3F"/></w:pBdr>
    <w:tabs><w:tab w:val="right" w:pos="12960"/></w:tabs>
    <w:spacing w:after="0" w:before="0"/>
  </w:pPr>
  <w:r>
    <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:b/><w:color w:val="8B2820"/><w:sz w:val="18"/></w:rPr>
    <w:t xml:space="preserve">AI in pharma</w:t>
  </w:r>
  <w:r><w:tab/></w:r>
  <w:r>
    <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="D85A3F"/><w:sz w:val="18"/></w:rPr>
    <w:t xml:space="preserve">Research  ·  Insights</w:t>
  </w:r>
</w:p>
```

## Page footer (every body page, suppressed on cover)

Aptos document title **left-aligned** + "Page X of Y" **right-aligned** via `PAGE` / `NUMPAGES` fields. Coral hairline above. Same right tab-stop pattern as the header.

**Hard rules** (mirror the header):

- The footer's left-hand text is **only** the document's main title — the same string shown on the cover page. No subtitle, no ": Executive summary", no eyebrow, no sub-heading. If the cover title is `AI in pharma`, the footer reads exactly `AI in pharma` on the left.
- The title is **left-aligned**; "Page X of Y" is **right-aligned** via the tab stop.
- All footer runs are set in **Aptos** (`<w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>`), not Aptos.
- Tab stop: `w:pos="9360"` for portrait sections, `w:pos="12960"` for landscape sections.

```xml
<!-- word/footer1.xml — portrait body section -->
<?xml version="1.0" encoding="UTF-8"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p>
    <w:pPr>
      <w:pBdr><w:top w:val="single" w:sz="6" w:space="6" w:color="D85A3F"/></w:pBdr>
      <w:tabs><w:tab w:val="right" w:pos="9360"/></w:tabs>
      <w:spacing w:after="0" w:before="0"/>
    </w:pPr>
    <!-- Left: document title only — exact match to the cover title. -->
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:t xml:space="preserve">AI in pharma</w:t>
    </w:r>
    <!-- Tab to the right margin -->
    <w:r><w:tab/></w:r>
    <!-- Right: "Page X of Y" via PAGE / NUMPAGES fields, right-aligned by the tab stop -->
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:t xml:space="preserve">Page </w:t>
    </w:r>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:fldChar w:fldCharType="begin"/>
    </w:r>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:instrText xml:space="preserve">PAGE</w:instrText>
    </w:r>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:fldChar w:fldCharType="end"/>
    </w:r>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:t xml:space="preserve"> of </w:t>
    </w:r>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:fldChar w:fldCharType="begin"/>
    </w:r>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:instrText xml:space="preserve">NUMPAGES</w:instrText>
    </w:r>
    <w:r>
      <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="1A1A1A"/><w:sz w:val="18"/></w:rPr>
      <w:fldChar w:fldCharType="end"/>
    </w:r>
  </w:p>
</w:ftr>
```

For landscape sections, use a separate footer file with `w:pos="12960"` on the tab stop and the same Aptos / title-only / left-and-right-aligned pattern.

Wire header / footer to the body section in `document.xml`:

```xml
<w:sectPr>
  <w:headerReference w:type="default" r:id="rIdHeader1"/>
  <w:footerReference w:type="default" r:id="rIdFooter1"/>
  <!-- ... pgSz, pgMar ... -->
</w:sectPr>
```

And to `word/_rels/document.xml.rels`:

```xml
<Relationship Id="rIdHeader1"
  Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
  Target="header1.xml"/>
<Relationship Id="rIdFooter1"
  Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
  Target="footer1.xml"/>
```

## Section heading (H1) with full-width coral underline

Set on the `Heading1` style; every H1 inherits it.

```xml
<w:style w:styleId="Heading1" w:type="paragraph">
  <w:name w:val="heading 1"/>
  <w:pPr>
    <w:keepNext/><w:keepLines/>
    <w:pBdr><w:bottom w:val="single" w:sz="14" w:space="6" w:color="D85A3F"/></w:pBdr>
    <w:spacing w:after="200" w:before="480"/>
    <w:outlineLvl w:val="0"/>
  </w:pPr>
  <w:rPr>
    <w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/>
    <w:b/><w:color w:val="8B2820"/><w:sz w:val="44"/>
  </w:rPr>
</w:style>
```

## Table treatment

Header row: deep-maroon background fill (`#8B2820`), bold white **Aptos** text.
Body cells: no fill; hairline beige borders (`#E8DFD3`, `sz=4`); generous cell margins (`top/bottom=100`, `left/right=140` DXA).

### docx-js

```javascript
const border  = { style: BorderStyle.SINGLE, size: 4, color: REPORT.beige };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 100, bottom: 100, left: 140, right: 140 };

function headerCell(width, text) {
  return new TableCell({
    borders,
    width:   { size: width, type: WidthType.DXA },
    shading: { fill: REPORT.maroon, type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({
      children: [new TextRun({
        text, bold: true, size: 20, color: REPORT.white, font: REPORT.fontSans,
      })],
    })],
  });
}

function bodyCell(width, paragraphs) {
  return new TableCell({
    borders,
    width:   { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: paragraphs,
  });
}
```

### Raw OOXML (table-header cell)

```xml
<w:tc>
  <w:tcPr>
    <w:tcW w:type="dxa" w:w="2000"/>
    <w:shd w:val="clear" w:color="auto" w:fill="8B2820"/>
    <w:tcMar>
      <w:top w:w="100" w:type="dxa"/>
      <w:left w:w="140" w:type="dxa"/>
      <w:bottom w:w="100" w:type="dxa"/>
      <w:right w:w="140" w:type="dxa"/>
    </w:tcMar>
  </w:tcPr>
  <w:p>
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
        <w:b/><w:color w:val="FFFFFF"/><w:sz w:val="20"/>
      </w:rPr>
      <w:t xml:space="preserve">Company</w:t>
    </w:r>
  </w:p>
</w:tc>
```

### Table-level border defaults (apply to `<w:tblPr>`)

```xml
<w:tblBorders>
  <w:top    w:val="single" w:sz="4" w:space="0" w:color="E8DFD3"/>
  <w:left   w:val="single" w:sz="4" w:space="0" w:color="E8DFD3"/>
  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E8DFD3"/>
  <w:right  w:val="single" w:sz="4" w:space="0" w:color="E8DFD3"/>
  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E8DFD3"/>
  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E8DFD3"/>
</w:tblBorders>
```

## Inline citations

Coral with matching coral underline. The hyperlink stays clickable.

### Body prose (optional superscript, coral, underlined)

```xml
<w:hyperlink r:id="rIdCite1">
  <w:r>
    <w:rPr>
      <w:color w:val="D85A3F"/>
      <w:u w:val="single"/>
      <w:uColor w:val="D85A3F"/>
      <w:vertAlign w:val="superscript"/>
      <w:sz w:val="16"/>
    </w:rPr>
    <w:t>[1]</w:t>
  </w:r>
</w:hyperlink>
```

### Table cells (body size, coral, underlined, no superscript)

```xml
<w:hyperlink r:id="rIdCite1">
  <w:r>
    <w:rPr>
      <w:color w:val="D85A3F"/>
      <w:u w:val="single"/>
      <w:uColor w:val="D85A3F"/>
    </w:rPr>
    <w:t>[1]</w:t>
  </w:r>
</w:hyperlink>
```

## Landscape sections for wide tables

Tables with 5+ columns or otherwise too wide for portrait get lifted onto a landscape page. Wrap with portrait then landscape then portrait section breaks. Carry the table's title block (heading + optional subtitle, plus parent heading when no body content separates them) onto the landscape page so the heading doesn't strand at the bottom of the prior portrait page.

Any wide table that's lifted to landscape MUST also (a) have its caption styled via `TableCaption` (see "Table and figure caption style (`TableCaption`)" below) — never `Heading 1` — and (b) have cell text sized per the column-count guideline in "Table cell font sizing" below.

```xml
<!-- Close portrait section BEFORE the table's heading -->
<w:p>
  <w:pPr>
    <w:sectPr>
      <w:headerReference w:type="default" r:id="rIdHeader1"/>
      <w:footerReference w:type="default" r:id="rIdFooter1"/>
      <w:pgSz w:w="12240" w:h="15840" w:orient="portrait"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"
               w:header="708" w:footer="708" w:gutter="0"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:pPr>
</w:p>

<!-- Heading travels to the landscape page -->
<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
  <w:r><w:t>Wide-table title</w:t></w:r>
</w:p>

<!-- Numbered caption -->
<w:p><w:pPr><w:pStyle w:val="Caption"/></w:pPr>
  <w:r><w:rPr><w:i/></w:rPr><w:t>Table 3. AI initiatives by company.</w:t></w:r>
</w:p>

<!-- The wide table itself -->
<w:tbl>
  <!-- ... -->
</w:tbl>

<!-- Close landscape and re-open portrait -->
<w:p>
  <w:pPr>
    <w:sectPr>
      <w:headerReference w:type="default" r:id="rIdHeader1"/>
      <w:footerReference w:type="default" r:id="rIdFooter1"/>
      <w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"
               w:header="708" w:footer="708" w:gutter="0"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:pPr>
</w:p>
```

The document's final `<w:sectPr>` must remain portrait so reading flow ends correctly. Merge adjacent landscape sections (when two tables sit back-to-back) by popping the in-between portrait break — the same algorithm used in cohere-style-lite.

## Numbered table captions

Use the `TableCaption` paragraph style (Aptos bold maroon 11pt — see "Table and figure caption style (`TableCaption`)" below) for every table caption and every figure caption. Never use `Heading 1` for captions — that styles them at 22pt with a full-width coral underline rule, which dwarfs the artifact below and confuses the visual hierarchy. The caption is a sub-label for the artifact, not a section divider.

Prepend `Table N.` to every caption. If a table has no caption, synthesize one from the table's first header cell.

```python
import re

TABLE_PREFIX_RE = re.compile(r"^Table\s+\d+\.?\s*", re.I)

def number_tables(body, doc):
    counter = 1
    for elem in body.iter():
        if elem.tag.endswith('}tbl'):
            caption = preceding_caption_paragraph(elem)
            if caption is None:
                title = synthesize_title_from_table(elem)
                caption = make_caption_paragraph(f"Table {counter}. {title}",
                                                  style="TableCaption")
                insert_before(elem, caption)
            else:
                # If the existing caption was wrongly styled Heading1 / Heading 1,
                # reassign to TableCaption so it sits below Heading 1 in hierarchy.
                set_paragraph_style(caption, "TableCaption")
                txt = caption.text or ""
                stripped = TABLE_PREFIX_RE.sub("", txt)
                caption.text = f"Table {counter}. {stripped}".strip()
            counter += 1
```

The legacy italic-slate `Caption` style (below) is retained only for non-table inline figure annotations that need a quieter, secondary register — table and figure captions both use `TableCaption`.

```xml
<w:style w:styleId="Caption" w:type="paragraph">
  <w:name w:val="Caption"/>
  <w:basedOn w:val="Normal"/>
  <w:pPr><w:spacing w:after="120" w:before="0"/></w:pPr>
  <w:rPr><w:i/><w:color w:val="6B6B6B"/><w:sz w:val="20"/></w:rPr>
</w:style>
```

## Table and figure caption style (`TableCaption`)

Captions for tables and figures must be SMALLER than `Heading 1` and proportionate to the document body — never heading-tier. The style requirements:

- **Aptos** (NOT Aptos Display — Aptos Display is reserved for the cover title and section H1s).
- **Bold**, **maroon `#8B2820`**, **11pt** (`<w:sz w:val="22"/>` — 22 half-points).
- Spacing `before="240"`, `after="160"`.
- `<w:keepNext/>` and `<w:keepLines/>` so the caption never strands away from the table or figure that follows it across a page break.
- **No coral underline rule.** The coral underline is reserved for `Heading 1`. Caption identity is carried by Aptos bold + maroon + 11pt alone.
- **Single-line fit** at the document content width. If the caption text is too long to fit on one line, edit the caption — do not let it wrap, and do not bump the size up.

Drop this style block into `styles.xml`:

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

Apply to a table caption paragraph:

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="TableCaption"/>
  </w:pPr>
  <w:r>
    <w:t>Table 3. AI initiatives by company.</w:t>
  </w:r>
</w:p>
<w:tbl>
  <!-- ... -->
</w:tbl>
```

Apply identically to a figure caption (figure captions sit in the same visual tier — same Aptos bold maroon 11pt; only the prefix changes from `Table N.` to `Figure N.`):

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="TableCaption"/>
  </w:pPr>
  <w:r>
    <w:t>Figure 2. Pfizer pipeline timeline, 2020–2025.</w:t>
  </w:r>
</w:p>
<!-- inline picture follows -->
```

When restyling an existing report, walk every paragraph immediately preceding a `<w:tbl>` (or wrapping a figure / inline image) — if its `<w:pStyle>` resolves to `Heading1`, `Heading 1`, or any heading-tier style, reassign to `TableCaption`:

```python
def reassign_caption_styles(body):
    for elem in body.iter():
        if elem.tag.endswith('}tbl'):
            cap = preceding_caption_paragraph(elem)
            if cap is not None and current_style(cap) in {"Heading1", "Heading 1"}:
                set_paragraph_style(cap, "TableCaption")
        elif is_figure_paragraph(elem):
            cap = preceding_caption_paragraph(elem)
            if cap is not None and current_style(cap) in {"Heading1", "Heading 1"}:
                set_paragraph_style(cap, "TableCaption")
```

## Table cell font sizing

Every word in every table cell must fit naturally — no mid-word hyphenation, no wrap that breaks a token before it is complete. Size cell text small enough that any single word fits in its column.

### Column-count sizing rules

| Table column count | Body cell font size                        | Header row font size                            |
|--------------------|--------------------------------------------|-------------------------------------------------|
| 4 columns or fewer | 11pt — `<w:sz w:val="22"/>` (same as body) | 11pt bold                                       |
| 5–7 columns        | 10pt — `<w:sz w:val="20"/>`                | 11pt bold                                       |
| 8 columns or more  | 8–9pt — `<w:sz w:val="16"/>` or `<w:sz w:val="18"/>` | one tier larger than body, never above 11pt |

Worked example: an 8-column landscape table at 6.5"+1"+6.5" landscape content width (~13.5") leaves ~1.4" per column. The body sizes to 8pt (`<w:sz w:val="16"/>`); the header row sizes to 9pt bold (`<w:sz w:val="18"/>`). At 8pt, common scientific terms like "immunology", "anti-cancer", and "AlphaFold-based" fit on a single line in a 1.4" column; at 12pt they do not.

### Header row constraint

The header row stays one tier larger than body cells but **never exceeds 11pt** — even on a 4-column table, the header doesn't bump to 12pt or 14pt. The maroon header fill carries the visual emphasis; size escalation is not needed.

### Hyperlink / citation runs inside cells

Hyperlink runs (`[N]` citations) inside cells must inherit the same size as the surrounding body cell. Cell-level `<w:sz>` does NOT cascade to hyperlink runs — every citation run inside a cell must explicitly carry its own `<w:sz>` matching the cell body size:

```xml
<!-- citation in an 8pt body cell -->
<w:hyperlink r:id="rIdCite5">
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:color w:val="D85A3F"/>
      <w:u w:val="single"/>
      <w:uColor w:val="D85A3F"/>
      <w:sz w:val="16"/>
      <w:szCs w:val="16"/>
    </w:rPr>
    <w:t>[5]</w:t>
  </w:r>
</w:hyperlink>
```

### Disable doc-wide automatic hyphenation

Do NOT include `<w:autoHyphenation/>` in `word/settings.xml`. If it is present, remove it. Hyphens are a wrapping band-aid that look unprofessional in tables — the correct fix is sizing the cell text per the column-count guideline above.

```bash
# Check whether settings.xml has it set
grep -n "autoHyphenation" word/settings.xml

# Remove the element if present (sed in-place; macOS variant uses `-i ''`)
sed -i 's|<w:autoHyphenation/>||g' word/settings.xml
```

For a programmatic removal:

```python
from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def disable_auto_hyphenation(settings_xml_path):
    tree = etree.parse(settings_xml_path)
    root = tree.getroot()
    for el in root.findall(f"{W}autoHyphenation"):
        root.remove(el)
    tree.write(settings_xml_path, xml_declaration=True, encoding="UTF-8", standalone=True)
```

### OOXML pattern: cell-level `<w:sz>`

Every run inside the cell carries its own `<w:sz>` (cells don't inherit from a per-cell paragraph style):

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

Header cell, one tier larger (9pt bold, white-on-maroon, for an 8+ column table):

```xml
<w:tc>
  <w:tcPr>
    <w:tcW w:w="1440" w:type="dxa"/>
    <w:shd w:val="clear" w:color="auto" w:fill="8B2820"/>
  </w:tcPr>
  <w:p>
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
        <w:b/>
        <w:color w:val="FFFFFF"/>
        <w:sz w:val="18"/>      <!-- 9pt header for 8+ column table -->
        <w:szCs w:val="18"/>
      </w:rPr>
      <w:t>Company</w:t>
    </w:r>
  </w:p>
</w:tc>
```

### Helper: pick body / header sizes from column count

```python
def cell_sizes_for_columns(n_cols):
    """Returns (body_half_pts, header_half_pts) for a table with n_cols columns.

    Half-points: 22 = 11pt, 20 = 10pt, 18 = 9pt, 16 = 8pt.
    """
    if n_cols <= 4:
        return 22, 22       # 11pt body, 11pt header bold
    if n_cols <= 7:
        return 20, 22       # 10pt body, 11pt header bold
    # 8+ columns: tighten body to 8pt, header to 9pt
    return 16, 18           # 8pt body, 9pt header bold
```

## LaTeX residue cleanup

Pandoc-via-LaTeX manuscripts leave readable scraps in body text. Walk every `<w:t>` and strip:

```python
import re

LATEX_PATTERNS = [
    re.compile(r"\\begin\{easylist\}\\el\s*"),
    re.compile(r"\\@end\{easylist\}"),
    re.compile(r"\\end\{[^}]+\}"),
    re.compile(r"\\begin\{[^}]+\}"),
    re.compile(r"\\el\b\s*"),
]
STRAY_AT = re.compile(r"^@\s+")  # only at paragraph start

def clean_paragraph_text(paragraph_elem):
    runs = paragraph_elem.findall(w("r"))
    for run in runs:
        for t in run.findall(w("t")):
            if t.text is None: continue
            txt = t.text
            for pat in LATEX_PATTERNS:
                txt = pat.sub("", txt)
            t.text = txt
    # Strip stray '@' at the very start of the first non-empty run
    first = first_text_in_paragraph(paragraph_elem)
    if first is not None and first.text:
        first.text = STRAY_AT.sub("", first.text)
```

Then convert affected paragraphs into proper bullet lists:

```xml
<!-- numbering.xml: define a bullet list once -->
<w:abstractNum w:abstractNumId="200">
  <w:multiLevelType w:val="hybridMultilevel"/>
  <w:lvl w:ilvl="0">
    <w:start w:val="1"/>
    <w:numFmt w:val="bullet"/>
    <w:lvlText w:val="."/>
    <w:lvlJc w:val="left"/>
    <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:color w:val="1A1A1A"/>
    </w:rPr>
  </w:lvl>
</w:abstractNum>
<w:num w:numId="200"><w:abstractNumId w:val="200"/></w:num>
```

Then on each list-item paragraph:

```xml
<w:pPr>
  <w:numPr>
    <w:ilvl w:val="0"/>
    <w:numId w:val="200"/>
  </w:numPr>
</w:pPr>
```

Do not insert literal `.` glyphs at the start of paragraph text — that fakes the list and breaks Word's outline / indent machinery.

## Diagram-to-PNG render pattern (PIL)

When the source has a text-form timeline, flowchart, or mermaid block, render to a Cohere-styled PNG using the report palette.

```python
from PIL import Image, ImageDraw, ImageFont

MAROON = (139, 40, 32)
CORAL  = (216, 90, 63)
INK    = (26, 26, 26)
SLATE  = (107, 107, 107)
WHITE  = (255, 255, 255)

def render_timeline(events, out_path, width=2000, height=900):
    """events = [(date_str, label_str), ...]"""
    img = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(img)
    try:
        # Aptos for body, Aptos Display for the title
        title_font = ImageFont.truetype("Aptos-Display.ttf", 56)
        body_font  = ImageFont.truetype("Aptos.ttf", 28)
        date_font  = ImageFont.truetype("Aptos.ttf", 22)
    except OSError:
        # DejaVu Sans is the closest portable fallback when Aptos is not installed
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 56)
        body_font  = ImageFont.truetype("DejaVuSans.ttf", 28)
        date_font  = ImageFont.truetype("DejaVuSans.ttf", 22)

    # Title
    draw.text((80, 60), "AI in pharma - Timeline", font=title_font, fill=MAROON)

    # Coral baseline rule
    y = height // 2
    draw.line([(120, y), (width - 120, y)], fill=CORAL, width=4)

    # Evenly distributed event slots
    n = len(events)
    if n == 0: return img.save(out_path)
    x_step = (width - 240) // max(n - 1, 1)
    for i, (date, label) in enumerate(events):
        x = 120 + i * x_step
        # Coral dot
        r = 10
        draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=CORAL)
        # Date (slate, above)
        draw.text((x - 40, y - 70), date, font=date_font, fill=SLATE)
        # Label (ink, below)
        draw.text((x - 90, y + 30), label, font=body_font, fill=INK)

    img.save(out_path)
```

Embed at 6.5" wide on portrait pages (`cx="5943600"` EMU). The inline-picture XML pattern is identical to the one used in cohere-style-lite — see that recipe's "Embedding figures" section, just substitute the report palette.

## References section

When inline citations are present, end the document with a `Heading 1` titled `References` followed by a **real Word numbered list** of unique source URLs. Three load-bearing pieces (all required — see SKILL.md Rule 9):

- `<w:abstractNum>` + `<w:num>` pair in `numbering.xml`, `numId="500"` by convention.
- The number itself rendered **bold maroon `#8B2820`** via `<w:rPr>` inside the level block.
- A `ReferenceItem` paragraph style with `<w:contextualSpacing/>` and `spacing` after 120 so adjacent paragraphs collapse the inter-paragraph gap into a tidy list.
- Each reference paragraph contains **only** the `<w:hyperlink>` URL — no leading literal `[N]` text, because Word's numbering machinery owns the number.

### Deduplication algorithm

```python
def renumber_and_dedupe_citations(body, rels):
    url_to_number = {}
    next_n = 1

    # First pass: walk all hyperlinks in body in document order
    for hyperlink in body.iter(w("hyperlink")):
        visible = hyperlink_text(hyperlink)
        if not CITATION_MARKER_RE.match(visible):
            continue
        rid = hyperlink.get(R("id"))
        url = rels[rid].target
        if url not in url_to_number:
            url_to_number[url] = next_n
            next_n += 1
        new_n = url_to_number[url]
        set_hyperlink_text(hyperlink, f"[{new_n}]")

    # Second pass: rebuild the references list (dense 1..M, numId 500)
    refs_paragraphs = [
        make_reference_paragraph(n, url, num_id=500)
        for url, n in sorted(url_to_number.items(), key=lambda kv: kv[1])
    ]
    replace_references_section(body, refs_paragraphs)

CITATION_MARKER_RE = re.compile(r"^\[\d+\]$")
```

### OOXML for the References section

```xml
<!-- Heading 1: References -->
<w:p>
  <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/>
      <w:b/><w:color w:val="8B2820"/><w:sz w:val="44"/>
    </w:rPr>
    <w:t>References</w:t>
  </w:r>
</w:p>

<!-- One numbered paragraph per unique URL.
     IMPORTANT: paragraph contains ONLY the <w:hyperlink>.
     No <w:r><w:t>[1]</w:t></w:r> literal-number runs — Word's
     numId=500 numbering machinery renders the number for us. -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ReferenceItem"/>
    <w:numPr>
      <w:ilvl w:val="0"/>
      <w:numId w:val="500"/>
    </w:numPr>
  </w:pPr>
  <w:hyperlink r:id="rIdRef1">
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
        <w:color w:val="D85A3F"/>
        <w:u w:val="single" w:color="D85A3F"/>
        <w:sz w:val="22"/>
      </w:rPr>
      <w:t>https://pfizer.com/press/q3-2025</w:t>
    </w:r>
  </w:hyperlink>
</w:p>
```

### Numbering definition (`numbering.xml`)

The `<w:abstractNum>` block defines the level — including the **bold-maroon `<w:rPr>`** that styles the rendered number `1.`, `2.`, `3.` itself. The paired `<w:num>` block binds it to a `numId` we reference from each reference paragraph.

```xml
<!-- abstractNum: define the level. The <w:rPr> on the level controls the
     COLOR/WEIGHT of the rendered number itself ("1.", "2.", ...). -->
<w:abstractNum w:abstractNumId="500">
  <w:multiLevelType w:val="hybridMultilevel"/>
  <w:lvl w:ilvl="0">
    <w:start w:val="1"/>
    <w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%1."/>
    <w:lvlJc w:val="left"/>
    <w:pPr>
      <!-- Hanging indent: number sits in a fixed gutter so multi-line
           URL wrap doesn't disturb the alignment. -->
      <w:ind w:left="640" w:hanging="360"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:b/>                          <!-- bold number -->
      <w:color w:val="8B2820"/>       <!-- maroon number -->
    </w:rPr>
  </w:lvl>
</w:abstractNum>

<!-- num: bind the abstractNum to the numId we reference from each reference paragraph -->
<w:num w:numId="500">
  <w:abstractNumId w:val="500"/>
</w:num>
```

**Schema-ordering reminder.** `numbering.xml` requires that **all `<w:abstractNum>` blocks precede all `<w:num>` blocks**. If the file already contains the LaTeX-bullet `<w:abstractNum w:abstractNumId="200">` and `<w:num w:numId="200">` from Rule 4, insert the new `<w:abstractNum w:abstractNumId="500">` after the existing abstractNums, then insert the new `<w:num w:numId="500">` after the existing nums. Inserting `<w:num>` before any `<w:abstractNum>` will fail Word's schema validation and the doc will refuse to open.

### `ReferenceItem` paragraph style

The `ReferenceItem` paragraph style enforces uniform body-text appearance and collapses inter-paragraph spacing between adjacent reference items via `<w:contextualSpacing/>` — so a 1-line URL and a 3-line wrapped URL sit at the same visual rhythm.

```xml
<w:style w:type="paragraph" w:styleId="ReferenceItem">
  <w:name w:val="Reference Item"/>
  <w:basedOn w:val="Normal"/>
  <w:next w:val="ReferenceItem"/>
  <w:pPr>
    <!-- spacing after 120; <w:contextualSpacing/> drops it to 0
         between two adjacent ReferenceItem paragraphs -->
    <w:spacing w:after="120" w:before="0" w:line="280" w:lineRule="auto"/>
    <w:contextualSpacing/>
  </w:pPr>
  <w:rPr>
    <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
    <w:color w:val="1A1A1A"/>
    <w:sz w:val="20"/>                 <!-- Aptos 10pt -->
  </w:rPr>
</w:style>
```

The combination of (a) Word's numbering machinery owning the number text and indentation, (b) `ReferenceItem` style enforcing consistent before/after spacing, and (c) `<w:contextualSpacing/>` collapsing the spacing between adjacent items — gives a tidy, evenly-spaced reference list regardless of whether individual URLs wrap to one, two, or three lines.

## Table-row source citations and adjacent-duplicate cleanup

Two cleanup passes that run once per document, after Rule 8's deduplication and before the final repack. Both relate to citations inside `<w:tbl>` cells; see SKILL.md Rule 10 for the full rationale.

### (a) Every row in a source/citation column must carry an inline citation marker

When restyling an existing report, walk every table whose header row contains a cell with text matching `^(Sources?|Citations?|References?)$` (case-insensitive — typically the rightmost column). For each body row in that table, check whether the source cell contains at least one `<w:hyperlink>` whose visible text matches `^\[\d+\]$`. If it does NOT — the cell is plain text like "Reuters", "Bayer press", "Merck press", naming a publication but with no link — WebSearch for the actual article using the row's company name + use case + date as the query, append a numbered citation hyperlink to the cell, add the URL as a new `<Relationship>` entry in `word/_rels/document.xml.rels`, and add it as a new unique reference entry at the end of the References section.

```python
import re

CITE_RE = re.compile(r"^\[\d+\]$")
SOURCE_HEADER_RE = re.compile(r"^(sources?|citations?|references?)$", re.I)

def backfill_table_source_citations(doc, rels, references_url_map, web_search):
    for tbl in doc.iter(w("tbl")):
        header_cells = [cell_text(c) for c in first_row_cells(tbl)]
        src_idx = next(
            (i for i, h in enumerate(header_cells) if SOURCE_HEADER_RE.match(h.strip())),
            None,
        )
        if src_idx is None:
            continue
        for row in body_rows(tbl):
            src_cell = cell_at(row, src_idx)
            if any(CITE_RE.match(hyperlink_text(hl)) for hl in src_cell.iter(w("hyperlink"))):
                continue  # already has a [N] marker — skip
            company = cell_text(cell_at(row, 0))
            use_case = cell_text(cell_at(row, 1))
            date = cell_text(cell_at(row, 2))
            url = web_search(f"{company} {use_case} {date} {cell_text(src_cell)}")
            if not url:
                # Fall back to the company's press-release homepage — never fabricate.
                url = company_press_url(company)
            n = ensure_reference(references_url_map, url, rels)
            append_citation_hyperlink(src_cell, n, url, rels)
```

### (b) Adjacent duplicate citations within the same cell are forbidden

This rule applies to **every cell in every column**, not just the Sources column. Scan each cell's run sequence; whenever two consecutive `<w:hyperlink>` elements resolve to the same `[N]` (after Rule 8's dedup pass), drop the later one. Keep ONLY the first occurrence; delete every subsequent identical hyperlink-and-text pair (including any whitespace text run sitting between them, if it's purely separator whitespace).

**Pseudo-XML — before** (cell shows `[5][5]` because two anchor-fragment hyperlinks both collapsed to citation number 5):

```xml
<w:tc>
  <w:p>
    <w:r><w:t xml:space="preserve">Pfizer-BioNTech mRNA platform </w:t></w:r>
    <w:hyperlink r:id="rIdCite5a">
      <w:r>
        <w:rPr><w:color w:val="D85A3F"/><w:u w:val="single"/></w:rPr>
        <w:t>[5]</w:t>
      </w:r>
    </w:hyperlink>
    <w:hyperlink r:id="rIdCite5b">
      <w:r>
        <w:rPr><w:color w:val="D85A3F"/><w:u w:val="single"/></w:rPr>
        <w:t>[5]</w:t>
      </w:r>
    </w:hyperlink>
  </w:p>
</w:tc>
```

**Pseudo-XML — after** (drop the second `[5]` hyperlink — keep the first only):

```xml
<w:tc>
  <w:p>
    <w:r><w:t xml:space="preserve">Pfizer-BioNTech mRNA platform </w:t></w:r>
    <w:hyperlink r:id="rIdCite5a">
      <w:r>
        <w:rPr><w:color w:val="D85A3F"/><w:u w:val="single"/></w:rPr>
        <w:t>[5]</w:t>
      </w:r>
    </w:hyperlink>
  </w:p>
</w:tc>
```

The same logic applies to longer runs (`[10][10][10]` collapses to a single `[10]`). Implementation:

```python
def collapse_adjacent_duplicate_citations(cell):
    for p in cell.iter(w("p")):
        children = list(p)
        prev_marker = None
        to_remove = []
        for child in children:
            if child.tag == w("hyperlink"):
                marker = hyperlink_text(child)
                if CITE_RE.match(marker) and marker == prev_marker:
                    to_remove.append(child)
                    continue
                prev_marker = marker
            elif child.tag == w("r") and is_pure_whitespace(child):
                # whitespace separator between two same-marker hyperlinks: also drop
                continue
            else:
                prev_marker = None
        for child in to_remove:
            p.remove(child)
```

## Body-prose named-claim citation backfill (Rule 13)

A cleanup pass that runs once per document, after Rule 8's deduplication and Rule 10's table-cell passes, and before the final renumbering pass. Where Rule 10 covers table cells, this rule covers **body paragraphs** — the Executive Summary, Findings, Discussion, Conclusions, and every other body section. See SKILL.md Rule 13 for the full rationale.

The behaviour: walk every paragraph in every body section (excluding the cover page, page headers/footers, and the References list itself). For each paragraph, identify every **named factual claim** — any phrase that (a) names a specific organization or person, (b) names a specific deal, study, or program, (c) states a specific number, percentage, dollar amount, date, or quantitative outcome, or (d) quotes or paraphrases a stated position from a source. For each such claim, check whether an inline `[N]` hyperlink follows it (immediately after the claim text, or at the end of the containing sentence). If no citation follows, identify the source from context (often the same study or press release already cited elsewhere in the document, so its URL is already in the References list) and insert a new `<w:hyperlink>` marker. Reuse existing reference numbers wherever possible; only mint a new reference number when the underlying source genuinely isn't in the existing References list — in that case, WebSearch for the source URL and add a new entry.

**Per-source marker placement.** Within a single sentence that names multiple sources, EACH source must get its own marker placed **immediately after its name**. The pattern `Sowa 2016[1], Trotti 2021[2], and AASM 2021[3]` is correct; `Sowa 2016, Trotti 2021, and AASM 2021[1]` is wrong — readers can't tell which marker supports which name. This is the same per-source marker placement rule from Rule 10 / Table-row source citations — cross-reference it.

**The Executive Summary is the most common offender.** Its job is to enumerate many sources in compressed form, which makes the missed-citation pattern especially visible. Treat the Executive Summary the same way as a table's Sources column — every named partnership, deal, or outcome carries its own `[N]`.

### Worked before/after — Executive Summary paragraph

Before (every named partnership shares a single trailing citation, or carries no citation at all):

```
Key trends include drug discovery platforms (Novartis–Isomorphic,
Takeda–Nabla/Iambic, AstraZeneca–Algen/CSPC), AI-powered R&D
collaborations (Merck–Mayo, Sanofi–QuantHealth, GSK–Helix,
AstraZeneca–Immunai), and advanced computing infrastructure
(Lilly's NVIDIA AI factory, Merck's Google Cloud partnership,
Roche's NVIDIA-powered AI hub).
```

After (every named partnership carries its own `[N]` marker, placed immediately after the partnership name; existing reference numbers are reused from elsewhere in the document):

```
Key trends include drug discovery platforms (Novartis–Isomorphic[6],
Takeda–Nabla/Iambic[5][15], AstraZeneca–Algen/CSPC[8][17]),
AI-powered R&D collaborations (Merck–Mayo[19], Sanofi–QuantHealth[12],
GSK–Helix[11], AstraZeneca–Immunai[4]), and advanced computing
infrastructure (Lilly's NVIDIA AI factory[1], Merck's Google Cloud
partnership[9], Roche's NVIDIA-powered AI hub[7]).
```

Each named partnership now carries its own marker. The reader can trace any single claim back to a specific source.

### Renumbering after backfill — cross-reference

Any citations newly added to body prose under this rule must trigger the renumbering pass already specified in Rule 8 ("De-duplicate and re-order citations") and Rule 9 ("References section uses a real Word numbered list"). Specifically: after adding new citations, walk the entire document again in reading order; re-derive the canonical `[1]`...`[N]` ordering based on each unique source's FIRST appearance; rewrite every marker and rebuild the References list (`numId="500"`, bold-maroon numbers, `ReferenceItem` paragraph style) accordingly. Do not restate the algorithm here — see the **Deduplication algorithm** subsection above for the canonical pseudocode.

### Implementation sketch

```python
import re

CITE_RE = re.compile(r"^\[\d+\]$")

# Body-prose paragraphs to scan: every paragraph in <w:body> that is NOT
#   - in the cover section (suppressed via <w:titlePg/>),
#   - in a header / footer XML part,
#   - or inside the References section (after the "References" Heading 1).
def body_prose_paragraphs(doc):
    in_refs = False
    for p in doc.iter_body_paragraphs():
        if is_heading1(p) and paragraph_text(p).strip().lower() in {"references", "sources", "bibliography"}:
            in_refs = True
            continue
        if in_refs:
            continue
        if is_cover_paragraph(p):
            continue
        yield p

def backfill_body_prose_citations(doc, rels, references_url_map, web_search):
    """For every named factual claim in every body paragraph, ensure an
    inline [N] hyperlink follows the claim. Reuse existing reference
    numbers from references_url_map wherever possible."""
    for p in body_prose_paragraphs(doc):
        claims = extract_named_claims(p)        # see "What counts as a claim" below
        for claim in claims:
            if has_following_citation(p, claim, CITE_RE):
                continue
            url = resolve_source_for_claim(claim, doc, web_search)
            if url is None:
                # leave a TODO comment in the doc; do NOT fabricate a citation
                leave_todo(p, claim)
                continue
            n = ensure_reference(references_url_map, url, rels)
            insert_citation_hyperlink_after(p, claim, n, url, rels)
    # Trigger renumbering pass (Rules 8 + 9) — re-derive [1]..[N] in
    # reading order and rebuild the References list.
    renumber_and_dedupe_citations(doc, rels)
```

**What counts as a named factual claim** — keep the matcher conservative; false positives are easier to recover from than false negatives left in the manuscript:

- Organization or person name: token starts with a capital letter, optionally followed by additional capitalised tokens (`Novartis`, `Mayo Clinic`, `the FDA`, `Pfizer`, `Roche`).
- Named deal / study / program: hyphenated or possessive form linking an organization to a named project (`Novartis–Isomorphic`, `Lilly's NVIDIA AI factory`, `the SUMMIT-1 trial`, `Anthem's value framework`).
- Quantitative outcome: a number with units (`$1.7B`, `55%`, `180h to 80h`, `Q3 2025`).
- Stated position from a source: verb-phrase patterns like `X mentions Y`, `X recommends Y`, `X reports Y`, `according to X`.

**Insertion site.** Place the `<w:hyperlink>` immediately after the run that contains the claim text. If the claim spans multiple runs, place the citation after the run that contains the last token of the claim. The hyperlink uses the same coral color + underline as every other inline citation (see "Inline citations / Body prose" earlier in this recipe).

**Where to source URLs.** First, check `references_url_map` — if the URL is already in the existing References list (very common: the same press release or trial was cited elsewhere in the document), reuse that number. Only fall through to `WebSearch` if the source genuinely isn't already in the document. Never fabricate a URL.


## Page margins (US Letter)

Portrait body pages: 1" margins all around (`top/right/bottom/left=1440` twips). Landscape table pages: same.

```javascript
sections: [{
  properties: {
    page: {
      size:   { width: 12240, height: 15840, orientation: PageOrientation.PORTRAIT },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
    },
  },
  children: [/* ... */],
}]
```

## Validation

After generating the file, validate it. Use the docx skill's `scripts/office/validate.py`. If it fails, unpack, repair the XML, and repack.

```bash
python scripts/office/validate.py output.docx
```
