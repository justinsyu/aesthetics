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
- Table cells: `16px`, line-height `1.21`
- Source text: `16px`, line-height `1.27`
- Key takeaway body: `24-26px`, line-height `1.16-1.21`
- Minimum readable type: generally `10-11px`
- Letter spacing should be `0` except tiny metadata where existing styling requires it

## Components

- Eyebrow: lime pill with black border, uppercase, 15px, 8px x 12px padding; use topic and date only, with no time-window label
- Panels/cards: 1.5px near-black border, `rgba(255,250,240,.86)` fill, 24px radius, restrained shadow
- Dark panels: `#11130f` background, paper text, no washed-out gray in PDF
- Metrics: large numeric value, muted label, compact citation
- Tags: small uppercase pills using lime, blue, orange, pink, gray, or red
- Lists: no browser bullets; use lime dot pseudo-elements
- Slide number: bottom right, small uppercase metadata
- Citations: superscript-style links with `.cite { font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 900; }`

## Example Report Structures

- Cover slide: date/topic eyebrow, title, optional scope sentence, four compact metric cards when feasible, then a dark `Executive summary` callout containing cited bullets
- References slide: `references-slide` article class, `References 1-N` eyebrow, `References` title, and a single-page source-agnostic grid/table with columns `Ref`, `Source`, `Date / Status / Source Owner`, and `Evidence Used in Report`
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
- Do not add terminal periods to title-style headings, chips, labels, captions, or fragment-style display text. Use periods only for complete sentences or where punctuation is required for grammar, citations, or abbreviations.
- Do not use viewer-facing process headers such as "Factual scope," "Source construction," or "Recorded..." headings.
- State the report date range once on the title slide. Avoid generic time-window labels elsewhere; when date range wording is necessary, use "between [date] and [date]."
- Final citation slides should be titled "References" and use source-agnostic columns such as `Ref`, `Source`, `Date / Status / Source Owner`, and `Evidence Used in Report`.

## Layout QA

Review browser screenshots and rendered PDF screenshots. Reduce padding or rebalance layout when panels contain excessive blank space. Split content across slides when important cited evidence cannot fit without overlap or unreadable type.

Visible header, navigation, brand-bar, and similar page chrome should use the same horizontal wrapper and gutter math as the main body content unless the chrome is intentionally full-bleed.

When review flags a large multi-line title as touching or too tight and asks not to bold it, increase title line-height or inter-line spacing and reduce font-weight rather than only shrinking the title text.

When review selects header, navigation, or brand-bar UI chrome and asks not to bold it, reduce the font-weight for that selected chrome only. Do not change unrelated body copy, titles, card headings, or citation typography to satisfy chrome-specific weight feedback.

When review selects a summary-stat or metric row and asks "don't bold," reduce font-weight only for that selected row's labels and values. Preserve hierarchy with size, spacing, or color rather than bold.

When review selects large metric values inside product or data cards and asks "don't bold," reduce font-weight only for those selected card metric values. Preserve the card hierarchy with value size, spacing, alignment, muted labels, or color rather than bold.

When review selects compact product-card stat labels that should fit on one line, first widen the label text box or rebalance the card/grid width before shrinking type; reduce font size only as much as needed after available width has been used.

When review selects market, city, provider, compact chart axis/list labels such as state abbreviations, or similar list-item labels and asks not to bold them, reduce the selected item label's perceived emphasis, not just its declared font-weight. If regular or medium labels still read as bold because of uppercase styling, high contrast, tight letterforms, or the font family, soften those factors with title case or lowercase where appropriate, lower contrast, smaller size, more open spacing, or a lighter/less assertive face. Preserve selected-state hierarchy with spacing, borders, background tint, or accent markers rather than bold-looking text.

When review selects a top utility strip, banner, status bar, or similar visible page chrome and asks to remove it, delete the chrome entirely instead of restyling it; preserve essential status or method context only outside the visible chrome.

When review selects a visible methodological caveat, methods note, limitation note, provenance note, or similar note box and asks to remove it, delete the entire visible note instead of restyling, shrinking, or relabeling it; preserve necessary caveats or provenance in source logs or other non-visible documentation where appropriate.

For same-row peer components, reserve shared multi-line header height only when at least one peer header actually wraps; if every header in the row is one line, let subtext begin after the normal heading margin instead of leaving an empty second-line gap.

For data or infographic cards with large metric values above bars, timelines, rings, or other visual marks, verify the rendered spacing between the number and the mark. If review flags the value as crowded, add enough vertical gap or rebalance the card so the metric reads as a distinct label rather than touching the visualization.
