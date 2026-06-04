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
- Card body: `19px`, line-height `1.27`
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
- Do not use viewer-facing process headers such as "Factual scope," "Source construction," or "Recorded..." headings.
- State the report date range once on the title slide. Avoid generic time-window labels elsewhere; when date range wording is necessary, use "between [date] and [date]."
- Final citation slides should be titled "References" and use source-agnostic columns such as `Ref`, `Source`, `Date / Status / Source Owner`, and `Evidence Used in Report`.

## Layout QA

Review browser screenshots and rendered PDF screenshots. Reduce padding or rebalance layout when panels contain excessive blank space. Split content across slides when important cited evidence cannot fit without overlap or unreadable type.

When review selects header, navigation, or brand-bar UI chrome and asks not to bold it, reduce the font-weight for that selected chrome only. Do not change unrelated body copy, titles, card headings, or citation typography to satisfy chrome-specific weight feedback.
