# Cohere Style CI Style Reference

Use this reference when creating competitive intelligence HTML slide reports. The visual and structural style is derived from the current AML CI example report HTML in `examples/aml_reference_report/report.html`.

Before building or revising a report, open that example report and match its current deck grammar unless the user provides a different design reference. In particular, the cover slide should use metric cards directly under the title followed by a dark `Executive summary` section with bullets, and the final slide should use the example report's one-page `References 1-N` structure.

## Canvas

- Fixed slide size: 1600 x 900
- Browser `.slide`: `width: 100vw; height: 100vh; min-height: 100vh; overflow: hidden`
- Print `.slide`: `width: 1600px; height: 900px; min-height: 900px`
- Standard slide padding: `36px 0 20px`
- Inner wrapper: `width: min(1360px, calc(100vw - 56px)); margin: 0 auto`
- Use `assets/tan_slide_background.png` as a full-slide background image layer

## Colors

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
  --radius: 24px;
}
```

## Typography

- Font stack: `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- H1: `86px`, line-height `.92`, font-weight `560`
- H2: `56px`, line-height `.98`, font-weight `560`
- H3: `30px`, line-height `1.04`, font-weight `650`
- Deck subtitle/dek: `28px`, line-height `1.24`
- Section supporting text: `25px`, line-height `1.24`
- Card body: `19px` minimum baseline, line-height `1.27`; increase to `21-24px` where fixed-page card or component space allows
- Mechanism-pattern explanatory text below section or card headings: use `22-24px` body sizing where space allows, with `12-16px` top spacing from the heading so the explanation does not read as cramped
- Table cells: `16px`, line-height `1.21`
- Table section/header cells must keep header text on one line, vertically centered, and fully inside the cell. Adjust column widths, cell padding, or concise header wording before allowing wrapped, clipped, or overflowing table headers.
- For the References slide table specifically, increase body copy above `16px` (for example 17-19px) when fixed slide space permits, enlarge header text proportionally, then adjust row heights and wrapping rather than reducing legibility.
- Source text: `16px`, line-height `1.27`
- Key takeaway body: `24-26px`, line-height `1.16-1.21`
- Minimum readable type: generally `10-11px`
- Letter spacing should be `0` except tiny metadata where existing styling requires it

## Components

- Eyebrow: lime pill with black border, uppercase, 15px, 8px x 12px padding; use topic and date only, with no time-window label
- Panels/cards: 1.5px near-black border, `rgba(255,250,240,.86)` fill, 24px radius, restrained shadow
- Dark panels: `#11130f` background, paper text, no washed-out gray in PDF; when review feedback asks for neon green on a selected heading inside a dark callout, or globally requests dark/black callout component headers in neon green, apply the lime accent only to the selected or affected dark-callout heading or phrase, keep supporting body text and citations in high-contrast white or light text, and verify the exported PDF preserves the accent color and readability
- Dark panel lists: style visible bullet markers in lime while keeping bullet text, citations, and supporting copy in high-contrast white or light text
- Metrics: large numeric value, muted label, compact citation
- Tags: small uppercase pills using lime, blue, orange, pink, gray, or red
- Lists: no browser bullets; use lime dot pseudo-elements
- Slide number: bottom right, small uppercase metadata
- Citations: superscript-style links with `.cite { font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 900; }`

## Example Report Structures

- Cover slide: date/topic eyebrow, title, optional scope sentence, four compact metric cards when feasible, then a dark `Executive summary` callout containing cited bullets
- References slide: `references-slide` article class, `References 1-N` eyebrow, `References` title, and a single-page source-agnostic grid/table with columns `Ref`, `Source`, `Date / Status / Source Owner`, and `Evidence Used in Report`; for HEOR/value-evidence reference or evidence tables where the field is sponsorship or funding, use `Sponsor` or `Sponsor/Funder` instead of `Source Owner`
- On the References slide table, keep the first `Ref` column centered horizontally in both header and body cells.
- Knowledge-graph or relationship-map slides should keep node and edge labels readable, group nodes by explicit source-supported entity type, and avoid dense hairball layouts. Use legends for node type, edge type, and confidence/inference status, and keep graph-specific caveats or provenance references visually proximate without crowding the map.
- If the exact number of metric cards differs because the report is small or dense, keep the example hierarchy: metrics before executive-summary bullets, not side-by-side with them

## HTML Skeleton

```html
<article class="slide">
  <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
  <div class="wrap">
    <div class="eyebrow">Topic | Date</div>
    <h1>Factual headline without terminal period</h1>
    <p class="dek">Evidence-backed summary with inline citation<a class="cite" href="https://example.com">1</a></p>
  </div>
  <div class="slide-num">01 / 06</div>
</article>
```

## Editorial Language

- Use scientific, objective source attribution such as "states that," "reported," "listed," "describes," or "documented"; do not use "says."
- Use formal competitive-intelligence phrasing. Avoid casual freshness framing such as "new" or "newly" when "first-posted," "reported," "published," "during the reporting period," or an exact source date is more precise.
- In HEOR and value-evidence tables, avoid vague labels such as "manufacturer signal" when manufacturer involvement can be confirmed. Use `Sponsor` or `Sponsor/Funder` when the field is asking for sponsorship or funding, confirm actual sponsor/funder/manufacturer involvement, and state the specific source-supported role, such as employee authorship, funding, sponsorship, consulting support, data-license involvement, or writing support.
- Do not add terminal periods to title-style headings, chips, labels, captions, or fragment-style display text. Use periods only for complete sentences or where punctuation is required for grammar, citations, or abbreviations.
- Do not use viewer-facing process headers such as "Factual scope," "Source construction," or "Recorded..." headings.
- State the report date range once on the title slide. Avoid generic time-window labels elsewhere; when date range wording is necessary, use "between [date] and [date]."
- Final citation slides should be titled "References" and use source-agnostic columns such as `Ref`, `Source`, `Date / Status / Source Owner`, and `Evidence Used in Report`; for HEOR/value-evidence reference or evidence tables where the field is sponsorship or funding, use `Sponsor` or `Sponsor/Funder` instead of `Source Owner`.

## Layout QA

Review browser screenshots and rendered PDF screenshots. Reduce padding or rebalance layout when panels contain excessive blank space. Split content across slides when important cited evidence cannot fit without overlap or unreadable type.

When review flags a large multi-line title as touching or too tight and asks not to bold it, increase title line-height or inter-line spacing and reduce font-weight rather than only shrinking the title text.

When review selects header, navigation, or brand-bar UI chrome and asks not to bold it, reduce the font-weight for that selected chrome only. Do not change unrelated body copy, titles, card headings, or citation typography to satisfy chrome-specific weight feedback.

When retaining header, navigation, brand-bar, or page chrome, align its left and right gutters to the same visible main body section or inner wrapper edges with no extra inset, and keep chrome text at a consistent font size unless a specific hierarchy is intentional.

When review selects a summary-stat or metric row and asks "don't bold," reduce font-weight only for that selected row's labels and values. Preserve hierarchy with size, spacing, or color rather than bold.

When review selects large metric values inside product or data cards and asks "don't bold," reduce font-weight only for those selected card metric values. Preserve the card hierarchy with value size, spacing, alignment, muted labels, or color rather than bold.

When review selects compact product-card stat labels that should fit on one line, first widen the label text box or rebalance the card/grid width before shrinking type; reduce font size only as much as needed after available width has been used.

When review selects market, city, provider, compact chart axis/list labels such as state abbreviations, or similar list-item labels and asks not to bold them, reduce the selected item label's perceived emphasis, not just its declared font-weight. If regular or medium labels still read as bold because of uppercase styling, high contrast, tight letterforms, or the font family, soften those factors with title case or lowercase where appropriate, lower contrast, smaller size, more open spacing, or a lighter/less assertive face. Preserve selected-state hierarchy with spacing, borders, background tint, or accent markers rather than bold-looking text.

When review selects a top utility strip, banner, status bar, or similar visible page chrome and asks to remove it, delete the chrome entirely instead of restyling it; preserve essential status or method context only outside the visible chrome.

When review selects a visible methodological caveat, methods note, limitation note, provenance note, or similar note box and asks to remove it, delete the entire visible note instead of restyling, shrinking, or relabeling it; preserve necessary caveats or provenance in source logs or other non-visible documentation where appropriate.

For same-row peer components, reserve shared multi-line header height only when at least one peer header actually wraps; if every header in the row is one line, let subtext begin after the normal heading margin instead of leaving an empty second-line gap.
For same-row peer-card headings, keep headings to a consistent rendered line count within the row; when one heading is flagged or wraps to two lines, make other same-row peer headings render as two lines through balanced wrapping or concise manual line breaks.

Within peer cards or repeated component grids, balance comparable internal blocks as a set: keep subtext below like headings to the same rendered line count where feasible, align follow-on content starts, and use equal-height repeated boxes so one card does not appear heavier or looser than its peers.
When review asks to remove a selected metric card, peer card, panel, or row component, delete it and reflow or rebalance the remaining row/grid; do not leave an empty slot or preserve the old column count.

When render review flags a panel or section heading sitting too close to the table, card, or component immediately beneath it, add vertical spacing below the heading rather than shrinking the heading or the content below; when a heading is followed by a dense table, preserve clear vertical space below the heading before the table begins.

After adjusting slide or infographic title line-height, preserve clear vertical spacing below the full title block so the next object does not sit too close to the title's lowest descenders, punctuation, or citation markers.

When a slide uses section-head subtext directly under the title, keep that subtext on one line whenever the available width allows; adjust title/subtext width, spacing, or title-specific type size before accepting a two-line wrap.

When review feedback asks for larger table text in a spacious table, increase the affected table body text and rebalance column widths, padding, or row spacing before shrinking content, while preserving slide fit; if repeated feedback says table or References body values are still too small and rendered whitespace remains, enlarge the body values further, then re-render and verify the table still fits on the page.

For data or infographic cards with large metric values above bars, timelines, rings, or other visual marks, verify the rendered spacing between the number and the mark. If review flags the value as crowded, add enough vertical gap or rebalance the card so the metric reads as a distinct label rather than touching the visualization.
