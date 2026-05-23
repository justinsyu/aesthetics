# docx-js recipe — Cohere-style-lite

Drop-in style configuration for docx-js. The single most important block is the `styles.default.document.run` — it sets the body font and color across every otherwise-unstyled TextRun, which means no per-run overrides are needed for plain body copy.

## Tokens

```javascript
const COHERE = {
  coral:    'FF7759', // primary
  ink:      '1A1A1A', // body
  cream:    'FAF6F1', // page / table fills
  subCoral: 'D85A3F', // H2 / links
  forest:   '39594D', // H3 / table header text
  beige:    'E8DFD3', // dividers
  slate:    '6B6B6B', // captions
  fontHeader: 'Aptos Display', // display tier (cover title, H1)
  fontBody:   'Aptos',         // body, H2, H3, captions
};
```

## Document styles block

Pass this as the `styles` field to `new Document({...})`. The hyperlink override at the top makes every link sub-coral instead of the docx default blue.

```javascript
styles: {
  default: {
    document: { run: { font: COHERE.fontBody, size: 20, color: COHERE.ink } }, // 10pt body
    hyperlink: { run: { color: COHERE.subCoral, underline: { type: 'single', color: COHERE.subCoral } } },
  },
  paragraphStyles: [
    { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run:       { size: 44, bold: true, font: COHERE.fontHeader, color: COHERE.coral, characterSpacing: -10 },
      paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0,
                   border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: COHERE.coral, space: 6 } } } },
    { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run:       { size: 28, bold: true, font: COHERE.fontHeader, color: COHERE.subCoral, characterSpacing: -6 },
      paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 1 } },
    { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run:       { size: 22, bold: true, font: COHERE.fontHeader, color: COHERE.forest, characterSpacing: -4 },
      paragraph: { spacing: { before: 220, after: 110 }, outlineLevel: 2 } },
    { id: 'Hyperlink', name: 'Hyperlink', basedOn: 'Normal', next: 'Normal',
      run: { color: COHERE.subCoral, underline: { type: 'single', color: COHERE.subCoral } } },
  ],
},
```

## Page background (warm cream)

```javascript
const doc = new Document({
  // ...
  background: { color: COHERE.cream },
  // ...
});
```

## Cover page

For any long-form artifact (white paper, evidence review, brief, report, deck), open with a Cohere-style cover page rather than diving straight into an H1. The cover composition has five centered lines: forest eyebrow → coral title → coral rule → italic ink subtitle → slate dateline. After the dateline, insert a section break with `titlePg: true` so the cover doesn't show the body footer, then start the body content.

### docx-js (paragraph builders)

```javascript
import { Paragraph, TextRun, AlignmentType, BorderStyle, PageBreak } from 'docx';

function coverPage({ eyebrow, title, subtitle, dateline }) {
  const font = COHERE.fontHeader;
  return [
    // 1. Eyebrow — forest, all caps, wide tracking
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 4000, after: 240 },
      children: [new TextRun({
        text: eyebrow.toUpperCase(),
        font, bold: true,
        color: COHERE.forest,
        size: 22,                  // 11pt
        characterSpacing: 60,      // wide tracking
      })],
    }),
    // 2. Title — coral, large, tight tracking
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 240 },
      children: [new TextRun({
        text: title,
        font, bold: true,
        color: COHERE.coral,
        size: 64,                  // 32pt display
        characterSpacing: -16,
      })],
    }),
    // 3. Coral rule — empty paragraph with bottom border
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 120, after: 360 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: COHERE.coral, space: 6 } },
      children: [new TextRun({ text: '' })],
    }),
    // 4. Subtitle — italic, deep ink
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 120 },
      children: [new TextRun({
        text: subtitle,
        font, italics: true,
        color: COHERE.ink,
        size: 28,                  // 14pt
      })],
    }),
    // 5. Dateline — muted slate, wide tracking, lower third of page
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 720, after: 0 },
      children: [new TextRun({
        text: dateline,
        font,
        color: COHERE.slate,
        size: 24,                  // 12pt
        characterSpacing: 30,
      })],
    }),
  ];
}
```

Wrap the cover and the body in two separate `sections`, with the cover section using `titlePage: true` so headers/footers in the body section don't show on the cover:

```javascript
sections: [
  {
    properties: {
      titlePage: true,                                 // suppress header/footer on cover
      page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
    },
    children: coverPage({
      eyebrow: 'Evidence Brief',
      title: 'HEOR Teams in Biopharma',
      subtitle: 'External evidence demands are rising while standalone HEOR groups are being embedded, split, or de-layered',
      dateline: 'May 2026',
    }),
  },
  {
    properties: { /* normal body section, with header/footer if desired */ },
    children: bodyContent,                             // starts with the first H2, NOT a repeat H1
  },
],
```

### Raw OOXML (for surgical edits to an existing docx)

When you're modifying a pre-built docx rather than generating one from docx-js, prepend these paragraphs to the start of `<w:body>`. Note the `<w:sectPr>` at the end of the block, with `<w:titlePg/>` — this is what creates the section break and tells Word the cover should not show the body footer.

```xml
<w:p>
  <w:pPr><w:spacing w:after="240" w:before="4000"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:b/><w:color w:val="39594D"/>
      <w:spacing w:val="60"/>
      <w:sz w:val="22"/>
    </w:rPr>
    <w:t xml:space="preserve">EVIDENCE BRIEF</w:t>
  </w:r>
</w:p>
<w:p>
  <w:pPr><w:spacing w:after="240" w:before="0"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/>
      <w:b/><w:color w:val="FF7759"/>
      <w:spacing w:val="-16"/>
      <w:sz w:val="64"/>
    </w:rPr>
    <w:t xml:space="preserve">Document Title Here</w:t>
  </w:r>
</w:p>
<w:p>
  <w:pPr>
    <w:pBdr><w:bottom w:val="single" w:color="FF7759" w:sz="18" w:space="6"/></w:pBdr>
    <w:spacing w:after="360" w:before="120"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:t xml:space="preserve"></w:t></w:r>
</w:p>
<w:p>
  <w:pPr><w:spacing w:after="120" w:before="0"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:i/><w:color w:val="1A1A1A"/>
      <w:sz w:val="28"/>
    </w:rPr>
    <w:t xml:space="preserve">One-line subtitle giving the angle of the piece</w:t>
  </w:r>
</w:p>
<w:p>
  <w:pPr><w:spacing w:after="0" w:before="720"/><w:jc w:val="center"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:color w:val="6B6B6B"/>
      <w:spacing w:val="30"/>
      <w:sz w:val="24"/>
    </w:rPr>
    <w:t xml:space="preserve">May 2026</w:t>
  </w:r>
</w:p>
<!-- Section break: cover page is its own section, with titlePg so it doesn't carry the body footer -->
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

After inserting the cover page block, find the original H1 (the one carrying the document title) in the body content and remove it. The cover page is now the title — repeating it as an H1 on page 2 is the most common mistake.

### Cover-page guardrails

- Don't add a logo, mark, or imagery to the cover. The composition is purely typographic; that's the look.
- Don't pair the eyebrow color with the dateline color — eyebrow is forest, dateline is slate. Mixing them collapses the hierarchy.
- The coral rule is short and floats below the title block. Don't extend it edge-to-edge across the page; that reads as an HTML `<hr>`, not as an editorial mark.
- The subtitle is one line, not a paragraph. If you find yourself writing two sentences, you're writing the executive summary instead.
- The dateline is the LAST line. Don't add author names, an organization, or a version number unless the user explicitly asks — the cohere look is editorial restraint.

## Table treatment

Table-header rows: cream fill, forest-accent text, coral underline rule.

```javascript
const border       = { style: BorderStyle.SINGLE, size: 4,  color: COHERE.beige };
const borderHeavy  = { style: BorderStyle.SINGLE, size: 12, color: COHERE.coral };
const borders      = { top: border, bottom: border, left: border, right: border };
const cellMargins  = { top: 100, bottom: 100, left: 140, right: 140 };

function headerCell(width, text) {
  return new TableCell({
    borders: { ...borders, bottom: borderHeavy },
    width:   { size: width, type: WidthType.DXA },
    shading: { fill: COHERE.cream, type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({
      children: [new TextRun({ text, bold: true, size: 18, color: COHERE.forest, font: COHERE.fontHeader })],
    })],
  });
}
```

Body cells: no fill, hairline beige borders, generous padding.

```javascript
function bodyCell(width, paragraphs) {
  return new TableCell({
    borders,
    width:   { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: paragraphs,
  });
}
```

## Inline citations

Bracketed inline citations like `[1]` and `[12]` should be styled in sub-coral (`#D85A3F`) with context-dependent superscript treatment. The hyperlink behind the citation must be preserved.

### Body prose (superscript, no underline)

In running text, render the citation as superscript at reduced font size with no underline:

```xml
<w:r>
  <w:rPr>
    <w:color w:val="D85A3F"/>
    <w:vertAlign w:val="superscript"/>
    <w:sz w:val="14"/>              <!-- 7pt: half of body 10pt -->
    <w:noUnderline/>
  </w:rPr>
  <w:annotationRef/>
  <!-- or for plain text citations without a link, just: -->
  <!-- <w:t>[1]</w:t> -->
</w:r>
```

If the citation is a hyperlink, wrap it as a standard `<w:hyperlink>` with the citation text `[1]` as the visible content, apply sub-coral color, and omit the underline from the run properties.

### Table cells (body size, underlined, no superscript)

In table cells, keep the citation at body text size to avoid further shrinking dense cells. Preserve the underline to maintain the affordance that the citation is a link:

```xml
<w:r>
  <w:rPr>
    <w:color w:val="D85A3F"/>
    <w:u w:val="single"/>           <!-- underline -->
    <w:uColor w:val="D85A3F"/>      <!-- underline matches text color -->
    <!-- no vertAlign="superscript" -->
    <!-- no sz reduction -->
  </w:rPr>
  <w:t>[1]</w:t>
</w:r>
```

Wrap this run inside a `<w:hyperlink>` element pointing to the reference target if the citation is clickable.

## References section

When the document uses inline citations, append a `## References` section (Heading 2) at the end of the body content. The reference list is numbered, with each unique source appearing once and each hyperlink deduped by its target URL.

### Algorithm

Walk the document in reading order. For each unique URL encountered:
1. If the URL has not been seen before, assign it the next sequential number (1, 2, 3, ...).
2. If the URL has been seen before, reuse its existing number.
3. Rewrite each inline citation's `[N]` text to match the deduplicated number.

This results in a dense numbered list from 1..M where M is the count of unique sources.

### OOXML format

```xml
<!-- Heading 2: References -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading2"/>
    <w:outlineLevel w:val="1"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:b/><w:color w:val="D85A3F"/>
      <w:sz w:val="28"/>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:spacing w:val="-6"/>
    </w:rPr>
    <w:t>References</w:t>
  </w:r>
</w:p>

<!-- Each reference paragraph attaches to a numId; the numbering definition
     in numbering.xml controls the displayed number, the hanging indent, and
     the bold-forest styling of the number itself. -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ReferenceItem"/>
    <w:numPr>
      <w:ilvl w:val="0"/>
      <w:numId w:val="100"/>
    </w:numPr>
  </w:pPr>
  <w:hyperlink r:id="rIdRef001">
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
        <w:color w:val="D85A3F"/>
        <w:u w:val="single" w:color="D85A3F"/>
        <w:sz w:val="20"/>
      </w:rPr>
      <w:t>https://example.com/source-one</w:t>
    </w:r>
  </w:hyperlink>
</w:p>
```

Define the numbering and the `ReferenceItem` paragraph style up front:

```xml
<!-- Inside word/numbering.xml, before </w:numbering> -->
<w:abstractNum w:abstractNumId="100">
  <w:nsid w:val="00010000"/>
  <w:multiLevelType w:val="hybridMultilevel"/>
  <w:lvl w:ilvl="0">
    <w:start w:val="1"/>
    <w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%1."/>
    <w:lvlJc w:val="left"/>
    <w:pPr><w:ind w:left="640" w:hanging="360"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>
      <w:b/>
      <w:color w:val="39594D"/>
    </w:rPr>
  </w:lvl>
</w:abstractNum>
<w:num w:numId="100">
  <w:abstractNumId w:val="100"/>
</w:num>

<!-- Inside word/styles.xml, before </w:styles> -->
<w:style w:type="paragraph" w:styleId="ReferenceItem">
  <w:name w:val="Reference Item"/>
  <w:basedOn w:val="Normal"/>
  <w:next w:val="ReferenceItem"/>
  <w:qFormat/>
  <w:pPr>
    <w:spacing w:after="120" w:before="0" w:line="280" w:lineRule="auto"/>
    <w:contextualSpacing/>
  </w:pPr>
  <w:rPr>
    <w:rFonts w:ascii="Aptos" w:cs="Aptos" w:eastAsia="Aptos" w:hAnsi="Aptos"/>
    <w:color w:val="1A1A1A"/>
    <w:sz w:val="20"/>
  </w:rPr>
</w:style>
```

The combination of (a) Word's numbering machinery handling the number text and indentation, (b) `ReferenceItem` style enforcing consistent before/after spacing, and (c) `<w:contextualSpacing/>` collapsing the spacing between adjacent items in the same list — gives a tidy, evenly-spaced reference list regardless of whether individual URLs wrap to one, two, or three lines. Don't fake the numbering with literal "1." text and a tab — the spacing won't match across long and short URLs.

## Landscape sections per table

Wide tables (8+ columns or very dense multi-column layouts) should occupy their own landscape page, *together with their title and subtitle*. The portrait section break is inserted before the heading that introduces the table, not between the heading and the table; otherwise the heading is stranded at the bottom of the prior portrait page while the table opens cold on a landscape page.

The landscape section that contains a table therefore looks like this in document order:

```
... prior portrait body content ...
<empty paragraph with sectPr=portrait>     ← closes the prior portrait section
<heading paragraph: H2 / H3 / H1>          ← table title, now on the landscape page
<optional subtitle paragraph>              ← e.g. "The citation in the last column…"
<table>
<empty paragraph with sectPr=landscape>    ← closes the landscape section
... next portrait body content ...
```

To find the title block when modifying an existing docx, walk backward from each `<w:tbl>`, skipping bookmarks and empty paragraphs. Greedily capture paragraphs into a list (in walk-back order), then prune trailing body paragraphs from the far end before committing — that way subtitles wedged between headings get included while normal flow content does not.

Concretely:

- Capture every paragraph above the table — heading or body — until you hit a previous table, a section break, two consecutive body paragraphs, or roughly 6 paragraphs.
- Then, from the far end (the oldest captured = farthest from the table), pop any trailing body paragraph. The remaining list is the title block.

This rule captures all of these patterns:

- `[Heading]` → just the table's heading.
- `[body subtitle, Heading]` → heading plus its subtitle.
- `[Heading (parent), body subtitle, Heading (child)]` → e.g. an H2 + intro paragraph + H3 hierarchy where the H2 directly introduces the H3 + table.
- `[Heading (parent), Heading (child)]` → stacked headings without a subtitle.

It deliberately excludes a body paragraph that sits before any heading in walk-back order, because that paragraph belongs to the previous flow content, not to the table's title block. Once the title block is identified, insert the portrait `sectPr` paragraph at the position *before* the captured title block, not directly before the table.

#### Merging adjacent landscape sections

When two tables sit back-to-back with no real portrait body content between them, naively wrapping each in a separate landscape section produces a blank portrait page between them — the empty section contains only an empty paragraph with `sectPr=portrait`, which Word renders as a blank page. To fix this, build the wrapped document iteratively: for each table, before appending the new portrait `sectPr` break, check whether the most recent element in the output stream is a landscape `sectPr` paragraph. If it is, *pop it* and reuse the existing landscape section instead of opening a new one. The two table clusters then share one continuous landscape section.

```python
def is_landscape_break(elem):
    if elem.tag != w('p'): return False
    pPr = elem.find(w('pPr'));   sectPr = pPr.find(w('sectPr')) if pPr is not None else None
    pgSz = sectPr.find(w('pgSz')) if sectPr is not None else None
    return pgSz is not None and pgSz.get(w('orient')) == 'landscape'

# In the wrap loop, when we encounter a table:
title_block = output[title_start:]
output = output[:title_start]
if output and is_landscape_break(output[-1]):
    output.pop()                       # extend the prior landscape section
else:
    output.append(portrait_break)      # open a new landscape section
output.extend(title_block)
output.append(table)
output.append(landscape_break)
```

### Before the table (portrait section close + title block + table)

```xml
<!-- Closing paragraph for the portrait section, inserted BEFORE the heading -->
<w:p>
  <w:pPr>
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840" w:orient="portrait"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"
               w:header="708" w:footer="708" w:gutter="0"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:pPr>
</w:p>

<!-- Heading (table title) — now in the landscape section -->
<w:p>
  <w:pPr><w:pStyle w:val="Heading3"/></w:pPr>
  <w:r><w:t xml:space="preserve">Value, role, and organizational placement</w:t></w:r>
</w:p>

<!-- Optional subtitle paragraph that sits between heading and table -->
<w:p>
  <w:pPr><w:pStyle w:val="FirstParagraph"/></w:pPr>
  <w:r><w:t xml:space="preserve">The citation in the last column opens the original source.</w:t></w:r>
</w:p>

<!-- Now the wide table -->
<w:tbl>
  <!-- table content: 8+ columns, wide cells -->
</w:tbl>
```

### After the table (landscape section close + portrait re-open)

```xml
<!-- After the </w:tbl>, close the landscape section and re-open portrait -->
<w:p>
  <w:pPr>
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840" w:orient="landscape"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"
               w:header="708" w:footer="708" w:gutter="0"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:pPr>
</w:p>

<!-- Body content continues in portrait; re-opens automatically -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading2"/>
  </w:pPr>
  <w:r><w:t>Next section heading (portrait again)</w:t></w:r>
</w:p>
```

### Important: document-level section handling

The document's final `<w:sectPr>` (whether a child of `<w:body>` or nested in the last paragraph) must remain portrait to preserve the reading flow after any landscape tables. Do not leave the document ending on a landscape section.

## Embedding figures (rendered diagrams)

When the source artifact contains a text-form diagram — e.g. a `SourceCode`-styled paragraph with raw mermaid syntax for a timeline or flowchart — render it to a Cohere-styled PNG outside the docx (PIL or matplotlib), then drop the PNG into the docx as an inline picture and remove the source-code paragraph.

Three steps:

1. **Render the PNG.** Use the Cohere palette: cream `#FAF6F1` background, coral `#FF7759` for primary marks, forest `#39594D` for axis labels, ink `#1A1A1A` for body labels, slate `#6B6B6B` for muted text. For a horizontal timeline, position events at evenly distributed slots (not by year) so multi-event years don't overlap, and label years once per group. Save to `word/media/figure.png` inside the unzipped docx working directory.

2. **Add the rels + content type for the image.** Append to `word/_rels/document.xml.rels`:

```xml
<Relationship Id="rIdTimeline"
  Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
  Target="media/figure.png"/>
```

And ensure `[Content_Types].xml` declares the PNG default extension:

```xml
<Default Extension="png" ContentType="image/png"/>
```

3. **Replace the source-code paragraph with an inline picture.** The picture XML uses `wp:inline`, with EMU units (914400 EMU per inch). For a 6.5" wide image at the source aspect ratio, set `cx="5943600"` and compute `cy` proportionally.

```xml
<w:p>
  <w:pPr><w:jc w:val="center"/><w:spacing w:before="240" w:after="240"/></w:pPr>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0"
                 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
        <wp:extent cx="5943600" cy="2548700"/>
        <wp:effectExtent l="0" t="0" r="0" b="0"/>
        <wp:docPr id="1" name="HEOR Timeline"/>
        <wp:cNvGraphicFramePr>
          <a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>
        </wp:cNvGraphicFramePr>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="1" name="figure.png"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="rIdTimeline"
                        xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>
                <a:stretch><a:fillRect/></a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm><a:off x="0" y="0"/><a:ext cx="5943600" cy="2548700"/></a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
```

The picture sits inline in the body's portrait flow. If the diagram is too wide to read at 6.5", it can also be promoted into a dedicated landscape section using the same technique used for wide tables.

## Page margins (US Letter, landscape data tables)

For text-only documents, use 1" margins. For documents with wide multi-column tables, use landscape orientation and slightly tighter top/bottom margins.

```javascript
sections: [{
  properties: {
    page: {
      size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE }, // pass portrait dims; docx-js swaps internally
      margin: { top: 1080, right: 1440, bottom: 1080, left: 1440 }, // 0.75" / 1" / 0.75" / 1"
    },
  },
  children: [/* content */],
}]
```

## Validation

After generating the file, validate it. Use the docx skill's `scripts/office/validate.py`. If it fails, unpack, repair the XML, and repack.

```bash
python scripts/office/validate.py output.docx
```
