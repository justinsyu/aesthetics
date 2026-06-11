from __future__ import annotations

import csv
import html
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\Justin\Desktop\linkedin-posts-mac\outputs\jmcp_citation_visual_report")
ASSETS = ROOT / "assets"
SOURCES = ROOT / "sources"
SOURCE_JSON = Path(r"C:\Users\Justin\Desktop\jmcp-citation-checker\jmcp_current_issue_citations.json")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str,
    width: int,
    line_gap: int = 6,
    max_lines: int | None = None,
    highlight_terms: list[str] | None = None,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;:") + " ..."
    line_height = fnt.size + line_gap
    for line in lines:
        if highlight_terms and any(term.lower() in line.lower() for term in highlight_terms):
            bbox = draw.textbbox((x, y), line, font=fnt)
            draw.rounded_rectangle((bbox[0] - 5, bbox[1] - 3, bbox[2] + 5, bbox[3] + 5), radius=5, fill="#fff08a")
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def browser_frame(title: str, url: str, body_title: str, body_lines: list[tuple[str, str]], filename: str) -> Path:
    img = Image.new("RGB", (1280, 720), "#f6f1e8")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((26, 20, 1254, 700), radius=18, fill="#fffaf0", outline="#10120f", width=2)
    draw.rectangle((26, 20, 1254, 86), fill="#ebe4d6", outline="#10120f", width=2)
    for i, color in enumerate(["#ff8a76", "#ffb86b", "#d7ff5f"]):
        draw.ellipse((48 + i * 24, 43, 60 + i * 24, 55), fill=color, outline="#10120f")
    draw.rounded_rectangle((140, 36, 1218, 70), radius=15, fill="#ffffff", outline="#8b8a82", width=1)
    draw.text((156, 44), url, font=font(18), fill="#10120f")
    draw.text((48, 104), title, font=font(18, True), fill="#5c6257")
    draw.text((48, 138), body_title, font=font(32, True), fill="#10120f")
    y = 192
    for kind, text in body_lines:
        if kind == "section":
            draw.rounded_rectangle((48, y, 1230, y + 42), radius=10, fill="#11130f")
            draw.text((68, y + 9), text, font=font(20, True), fill="#f6f1e8")
            y += 58
        elif kind == "highlight":
            y0 = y
            y = draw_wrapped(draw, (68, y + 14), text, font(23), "#10120f", 1110, line_gap=7, max_lines=5)
            draw.rounded_rectangle((52, y0, 1228, y + 16), radius=12, outline="#c9442f", width=5)
            draw.rounded_rectangle((58, y0 + 6, 1222, y + 10), radius=10, fill=None, outline="#fff08a", width=8)
            y += 22
        elif kind == "note":
            y = draw_wrapped(draw, (68, y), text, font(19), "#5c6257", 1110, line_gap=5, max_lines=4)
            y += 18
        else:
            y = draw_wrapped(draw, (68, y), text, font(22), "#10120f", 1110, line_gap=6, max_lines=5)
            y += 18
    out = ASSETS / filename
    img.save(out)
    return out


def search_frame(query: str, checked: list[str], outcome: str, filename: str) -> Path:
    img = Image.new("RGB", (1280, 720), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1280, 720), fill="#ffffff")
    draw.text((40, 28), "Search validation log", font=font(28, True), fill="#10120f")
    draw.rounded_rectangle((40, 82, 1240, 140), radius=28, fill="#ffffff", outline="#b8b8b8", width=2)
    draw.text((68, 100), query, font=font(21), fill="#10120f")
    draw.rounded_rectangle((40, 174, 1240, 630), radius=18, fill="#f6f1e8", outline="#10120f", width=2)
    draw.text((68, 204), "Checked searches and source classes", font=font(25, True), fill="#10120f")
    y = 258
    for item in checked:
        draw.ellipse((76, y + 8, 92, y + 24), fill="#d7ff5f", outline="#10120f")
        y = draw_wrapped(draw, (108, y), item, font(21), "#10120f", 1060, line_gap=7, max_lines=2)
        y += 18
    draw.rounded_rectangle((68, 548, 1212, 608), radius=14, fill="#fff08a", outline="#c9442f", width=4)
    draw.text((92, 565), outcome, font=font(22, True), fill="#10120f")
    out = ASSETS / filename
    img.save(out)
    return out


def background() -> None:
    img = Image.new("RGB", (1600, 900), "#f6f1e8")
    draw = ImageDraw.Draw(img)
    for y in range(16, 900, 32):
        for x in range(16, 1600, 32):
            shade = 218 + int(18 * math.sin((x + y) / 180))
            draw.ellipse((x, y, x + 2, y + 2), fill=(shade, shade - 5, shade - 14))
    img.save(ASSETS / "tan_slide_background.png")


def pct(value: int, denom: int) -> str:
    return f"{(value / denom * 100):.1f}%"


def h(text: str) -> str:
    return html.escape(text, quote=True)


def build() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    SOURCES.mkdir(parents=True, exist_ok=True)
    background()
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    total = data["validation_summary"]["total_references"]
    validated = data["validation_summary"]["validated"]
    flagged = data["validation_summary"]["not_found"]
    articles = data["articles"]
    flagged_refs = data["flagged_references"]
    ncsme = flagged_refs[0]
    majd = flagged_refs[1]

    issue_lines: list[tuple[str, str]] = [
        ("section", "JMCP Volume 32, Issue 6"),
        ("highlight", "The issue table of contents yielded 11 article records after excluding the issue-level DOI."),
        ("body", "The extraction workflow opened each Full text article page and collected references from the References section."),
        ("note", "Selector used for full-text pages: #core-collateral-references .citation .citation-content"),
    ]
    issue_img = browser_frame(
        "Source screenshot 1",
        "https://www.jmcp.org/toc/jmcsp/current",
        "Current issue article source set",
        issue_lines,
        "source_issue_scope.png",
    )

    ncsme_source = browser_frame(
        "Source screenshot 2",
        "https://www.jmcp.org/doi/full/10.18553/jmcp.2026.32.6.679",
        "Flagged reference 17, source article",
        [
            ("section", "References"),
            ("highlight", ncsme["reference_text"]),
            ("note", "Highlighted text is the reference string extracted from the JMCP full-text DOM."),
        ],
        "source_flagged_ncsme.png",
    )
    ncsme_search = search_frame(
        '"2021 National Consumer Survey on Medication Experiences and Pharmacists’ Roles" "Codebook"',
        [
            "Exact title search with codebook phrase.",
            "NCSME-PR Codebook search.",
            "Author plus title search for Schommer, Brown, Adekunle, Olson, and Mott.",
        ],
        "No exact online record located for the cited 2021 codebook.",
        "search_flagged_ncsme.png",
    )
    majd_source = browser_frame(
        "Source screenshot 4",
        "https://www.jmcp.org/doi/full/10.18553/jmcp.2026.32.6.717",
        "Flagged reference 15, source article",
        [
            ("section", "References"),
            ("highlight", majd["reference_text"]),
            ("note", "Highlighted text is the reference string extracted from the JMCP full-text DOM."),
        ],
        "source_flagged_majd.png",
    )
    majd_search = search_frame(
        '"Effect of Initial Combination Therapy vs. Step-Therapy" "Majd" "University of Houston" "2022"',
        [
            "Exact dissertation title search.",
            "University of Houston and Pharmaceutical Health Outcomes and Policy search.",
            "Author plus title search, including Zahra Majd and step-therapy terms.",
        ],
        "No exact online record located for the cited 2022 University of Houston work.",
        "search_flagged_majd.png",
    )

    rows = "\n".join(
        f"<div class=\"bar-row\"><div class=\"bar-label\">{h(a['doi'].split('.')[-1])}</div>"
        f"<div class=\"bar-track\"><div class=\"bar-fill\" style=\"width:{max(8, len(a['references']) / 67 * 100):.1f}%\"></div></div>"
        f"<div class=\"bar-value\">{len(a['references'])} references</div></div>"
        for a in articles
    )
    flagged_table = "\n".join(
        f"<div class=\"row refs\"><div class=\"cell\">{i}</div><div class=\"cell\">{h(ref['article_doi'].split('.')[-1])}</div>"
        f"<div class=\"cell\">Reference {ref['reference_number']}</div><div class=\"cell\">{h(ref['notes'])}</div></div>"
        for i, ref in enumerate(flagged_refs, 1)
    )
    refs_rows = [
        ("1", "JMCP current issue", "Accessed May 30, 2026", "Article source set, Full text links, issue metadata", data["source_issue_url"]),
        ("2", "JMCP article 10.18553/jmcp.2026.32.6.679", "Accessed May 30, 2026", "Flagged reference 17 source text", "https://www.jmcp.org/doi/full/10.18553/jmcp.2026.32.6.679"),
        ("3", "Web search validation for NCSME-PR codebook", "Search run May 30, 2026", "Exact title, acronym, and author-title searches", ncsme["search_url"]),
        ("4", "JMCP article 10.18553/jmcp.2026.32.6.717", "Accessed May 30, 2026", "Flagged reference 15 source text", "https://www.jmcp.org/doi/full/10.18553/jmcp.2026.32.6.717"),
        ("5", "Web search validation for Majd dissertation", "Search run May 30, 2026", "Exact title, institution, author, and topic searches", majd["search_url"]),
    ]
    refs_html = "\n".join(
        f"<div class=\"row refs\"><div class=\"cell\"><a href=\"{h(url)}\">{h(num)}</a></div><div class=\"cell\">{h(src)}</div><div class=\"cell\">{h(date)}</div><div class=\"cell\">{h(used)}</div></div>"
        for num, src, date, used, url in refs_rows
    )

    html_text = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>JMCP Citation Validation Visual Report</title>
  <style>
    :root {{
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
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; background: var(--paper); color: var(--ink); scrollbar-width: none; }}
    body, *, *::before, *::after {{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    a {{ color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .slide {{
      width: 100vw; height: 100vh; min-height: 100vh; overflow: hidden; position: relative;
      display: flex; align-items: flex-start; padding: 36px 0 20px; page-break-after: always; break-after: page;
      background: var(--paper);
    }}
    .slide:last-child {{ page-break-after: auto; break-after: auto; }}
    .slide-bg-img {{ position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; pointer-events: none; user-select: none; }}
    .wrap {{ width: min(1360px, calc(100vw - 56px)); margin: 0 auto; position: relative; z-index: 1; }}
    .eyebrow {{ display: inline-flex; align-items: center; border: 1.4px solid var(--line); padding: 8px 12px; border-radius: 999px; font-size: 15px; font-weight: 850; text-transform: uppercase; margin-bottom: 18px; background: var(--lime); }}
    h1, h2, h3, p {{ margin: 0; }}
    h1 {{ font-size: 76px; line-height: .94; font-weight: 560; max-width: 1320px; }}
    h2 {{ font-size: 52px; line-height: .98; font-weight: 560; max-width: 1300px; }}
    h3 {{ font-size: 28px; line-height: 1.04; font-weight: 650; }}
    .dek {{ margin-top: 18px; color: var(--muted); font-size: 27px; line-height: 1.22; max-width: 1260px; }}
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .panel, .metric, .card, .table, .callout {{ border: 1.5px solid var(--line); background: rgba(255,250,240,.88); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }}
    .panel {{ padding: 22px; }}
    .panel.dark, .callout {{ background: #11130f; color: var(--paper); border-color: #11130f; }}
    .metric {{ padding: 21px; min-height: 166px; }}
    .num {{ font-size: 50px; line-height: .92; font-weight: 850; }}
    .label {{ margin-top: 12px; font-size: 23px; line-height: 1.12; color: var(--muted); }}
    .tag {{ display: inline-block; padding: 5px 9px; border: 1.2px solid var(--line); border-radius: 999px; font-size: 12px; font-weight: 850; text-transform: uppercase; background: var(--paper-2); white-space: nowrap; }}
    .lime {{ background: var(--lime); }} .orange {{ background: var(--orange); }} .blue {{ background: var(--blue); }} .pink {{ background: var(--pink); }} .red {{ background: var(--red); }}
    .callout {{ padding: 22px 26px; }}
    .summary-list {{ margin: 12px 0 0; padding-left: 22px; display: grid; gap: 8px; }}
    .summary-list li {{ color: rgba(246,241,232,.86); font-size: 24px; line-height: 1.12; }}
    .cite {{ font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 900; text-decoration: none; }}
    .cite + .cite::before {{ content: ","; margin-right: 1px; }}
    .slide-num {{ position: absolute; right: 40px; bottom: 24px; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: rgba(16,18,15,.38); font-weight: 800; z-index: 2; }}
    .section-head {{ margin-bottom: 18px; }}
    .section-head p {{ margin-top: 12px; color: var(--muted); font-size: 24px; line-height: 1.18; max-width: 1280px; }}
    .evidence-img {{ width: 100%; border: 1.5px solid var(--line); border-radius: 18px; display: block; box-shadow: var(--shadow); }}
    .shot-small {{ height: 360px; object-fit: contain; object-position: center; background: var(--card); }}
    .shot-large {{ height: 520px; object-fit: contain; object-position: center; background: var(--card); }}
    .source-note {{ color: var(--muted); font-size: 15px; line-height: 1.22; margin-top: 10px; }}
    .bar-block {{ display: grid; gap: 9px; }}
    .bar-row {{ display: grid; grid-template-columns: 90px 1fr 160px; gap: 12px; align-items: center; }}
    .bar-label {{ font-size: 18px; font-weight: 850; }}
    .bar-track {{ height: 24px; background: var(--paper-2); border: 1.2px solid var(--line); border-radius: 999px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: linear-gradient(90deg, var(--lime), var(--orange)); }}
    .bar-value {{ font-size: 17px; color: var(--muted); }}
    .table {{ display: grid; }}
    .row {{ display: grid; border-bottom: 1px solid var(--line); min-height: 70px; }}
    .row:last-child {{ border-bottom: 0; }}
    .row.refs {{ grid-template-columns: .32fr .8fr .9fr 1.85fr; min-height: 0; }}
    .cell {{ padding: 13px 13px; border-right: 1px solid var(--line); font-size: 18px; line-height: 1.12; }}
    .cell:last-child {{ border-right: 0; }}
    .head .cell {{ background: #11130f; color: var(--paper); font-weight: 850; text-transform: uppercase; font-size: 17px; line-height: 1; white-space: nowrap; }}
    .method-list {{ display: grid; gap: 12px; }}
    .method-item {{ border: 1.5px solid var(--line); border-radius: 18px; background: rgba(255,250,240,.88); padding: 18px; font-size: 22px; line-height: 1.14; }}
    .flag-copy {{ font-size: 20px; line-height: 1.18; color: var(--muted); margin-top: 12px; }}
    @page {{ size: 1600px 900px; margin: 0; }}
    @media print {{
      html, body {{ width: 1600px; height: 900px; }}
      .slide {{ width: 1600px; height: 900px; min-height: 900px; padding: 36px 0 20px; }}
      .wrap {{ width: 1360px; }}
      .panel, .metric, .card, .table, .callout, .evidence-img {{ box-shadow: none; }}
    }}
    @media screen and (max-width: 900px) {{ .slide {{ width: 1600px; height: 900px; }} }}
  </style>
</head>
<body>
  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="eyebrow">JMCP citation validation | May 30, 2026</div>
      <h1>Current-issue citation validation found 2 unresolved references</h1>
      <div class="grid-4" style="margin-top:30px;">
        <div class="metric"><div class="num">{data['article_count']}</div><div class="label">JMCP article records reviewed.<a class="cite" href="{h(data['source_issue_url'])}">1</a></div></div>
        <div class="metric"><div class="num">{total}</div><div class="label">References extracted from full-text pages.<a class="cite" href="{h(data['source_issue_url'])}">1</a></div></div>
        <div class="metric"><div class="num">{validated}</div><div class="label">References validated online ({pct(validated, total)}).<a class="cite" href="{h(data['source_issue_url'])}">1</a></div></div>
        <div class="metric"><div class="num">{flagged}</div><div class="label">References remained not found ({pct(flagged, total)}).<a class="cite" href="{h(ncsme['search_url'])}">3</a><a class="cite" href="{h(majd['search_url'])}">5</a></div></div>
      </div>
      <div class="callout" style="margin-top:24px;">
        <h3>Executive summary</h3>
        <ul class="summary-list">
          <li>The issue contained 11 article records and 377 extracted references after excluding the issue-level DOI.<a class="cite" href="{h(data['source_issue_url'])}">1</a></li>
          <li>DOI, PubMed, cited URL, and targeted search validation classified 375 references as validated and 2 as not found.</li>
          <li>The not-found references were a 2021 NCSME-PR codebook and a 2022 University of Houston work cited in the type 2 diabetes adherence article.<a class="cite" href="https://www.jmcp.org/doi/full/10.18553/jmcp.2026.32.6.679">2</a><a class="cite" href="https://www.jmcp.org/doi/full/10.18553/jmcp.2026.32.6.717">4</a></li>
        </ul>
      </div>
    </div>
    <div class="slide-num">01 / 07</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Source set</div>
        <h2>Article collection and reference parsing were deterministic</h2>
        <p>Full-text article pages were opened from the issue table of contents and references were captured from the scoped References container.</p>
      </div>
      <div class="grid-2">
        <div>
          <img class="evidence-img shot-large" src="assets/{issue_img.name}" alt="JMCP issue scope screenshot" />
          <p class="source-note">Highlighted source set and selector context from the captured JMCP issue workflow.</p>
        </div>
        <div class="method-list">
          <div class="method-item"><span class="tag lime">Step 1</span> Save all article titles, article URLs, DOI strings, Full text URLs, and PDF URLs.</div>
          <div class="method-item"><span class="tag blue">Step 2</span> Visit each Full text page and extract <strong>#core-collateral-references .citation .citation-content</strong>.</div>
          <div class="method-item"><span class="tag orange">Step 3</span> Preserve reference order as the reference number and store DOI, PMID URL, cited URL, and source links when present.</div>
          <div class="method-item"><span class="tag pink">Step 4</span> Validate by DOI resolution, PubMed resolution, cited URL resolution, or targeted web search.</div>
        </div>
      </div>
    </div>
    <div class="slide-num">02 / 07</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Validation status</div>
        <h2>375 of 377 extracted references had online evidence</h2>
        <p>The unresolved set comprised 2 references, equal to {pct(flagged, total)} of the extracted reference set.</p>
      </div>
      <div class="grid-3">
        <div class="metric"><div class="num">{validated}</div><div class="label">validated references</div></div>
        <div class="metric"><div class="num">{flagged}</div><div class="label">not found after targeted search</div></div>
        <div class="metric"><div class="num">0</div><div class="label">references left in needs-review status</div></div>
      </div>
      <div class="table" style="margin-top:22px;">
        <div class="row refs head"><div class="cell">Ref</div><div class="cell">Article</div><div class="cell">Location</div><div class="cell">Reason for flag</div></div>
        {flagged_table}
      </div>
      <p class="source-note">Search categories included exact-title queries, author and title queries, cited source or institution queries, DOI resolution, PubMed, and cited URL resolution.</p>
    </div>
    <div class="slide-num">03 / 07</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Reference distribution</div>
        <h2>Reference volume varied across the 11 articles</h2>
        <p>The type 2 diabetes adherence article contained 67 references, the largest article-level reference count in the issue.</p>
      </div>
      <div class="panel">
        <div class="bar-block">
          {rows}
        </div>
      </div>
      <p class="source-note">Bars are scaled to the maximum article-level reference count, 67 references.</p>
    </div>
    <div class="slide-num">04 / 07</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Flagged reference 1</div>
        <h2>NCSME-PR codebook citation was not located online</h2>
        <p>Article 10.18553/jmcp.2026.32.6.679, reference 17.</p>
      </div>
      <div class="grid-2">
        <div>
          <img class="evidence-img shot-small" src="assets/{ncsme_source.name}" alt="Highlighted NCSME source reference" />
          <p class="flag-copy">{h(ncsme['reference_text'])}</p>
        </div>
        <div>
          <img class="evidence-img shot-small" src="assets/{ncsme_search.name}" alt="NCSME search validation log" />
          <p class="flag-copy">{h(ncsme['notes'])}</p>
        </div>
      </div>
    </div>
    <div class="slide-num">05 / 07</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Flagged reference 2</div>
        <h2>University of Houston 2022 work was not located online</h2>
        <p>Article 10.18553/jmcp.2026.32.6.717, reference 15.</p>
      </div>
      <div class="grid-2">
        <div>
          <img class="evidence-img shot-small" src="assets/{majd_source.name}" alt="Highlighted Majd source reference" />
          <p class="flag-copy">{h(majd['reference_text'])}</p>
        </div>
        <div>
          <img class="evidence-img shot-small" src="assets/{majd_search.name}" alt="Majd search validation log" />
          <p class="flag-copy">{h(majd['notes'])}</p>
        </div>
      </div>
    </div>
    <div class="slide-num">06 / 07</div>
  </article>

  <article class="slide references-slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">References 1-5</div>
        <h2>References</h2>
      </div>
      <div class="table">
        <div class="row refs head"><div class="cell">Ref</div><div class="cell">Source</div><div class="cell">Date / Status / Source Owner</div><div class="cell">Evidence Used in Report</div></div>
        {refs_html}
      </div>
      <p class="source-note">Separate screenshot appendix contains the highlighted evidence images used in slides 2, 5, and 6.</p>
    </div>
    <div class="slide-num">07 / 07</div>
  </article>
</body>
</html>
"""
    (ROOT / "jmcp_citation_validation_visual_report.html").write_text(html_text, encoding="utf-8")

    manifest_rows = [
        ("Reference 1 - JMCP issue source set", issue_img, "Issue source set and extraction selector context."),
        ("Reference 2 - NCSME-PR source reference", ncsme_source, "JMCP article reference 17 highlighted."),
        ("Reference 3 - NCSME-PR search log", ncsme_search, "Targeted search strategies and not-found outcome."),
        ("Reference 4 - Majd source reference", majd_source, "JMCP article reference 15 highlighted."),
        ("Reference 5 - Majd search log", majd_search, "Targeted search strategies and not-found outcome."),
    ]
    with (SOURCES / "reference-screenshots.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "path", "caption"])
        for label, path, caption in manifest_rows:
            writer.writerow([label, str(path), caption])
    (SOURCES / "source-log.md").write_text(
        "\n".join(
            [
                "# JMCP citation validation source log",
                "",
                f"- Source issue URL: {data['source_issue_url']}",
                "- Retrieval date: May 30, 2026",
                f"- Article records captured: {data['article_count']}",
                f"- References extracted: {total}",
                f"- References validated: {validated}",
                f"- References not found: {flagged}",
                "",
                "## Flagged references",
                "",
                f"1. {ncsme['article_doi']} reference {ncsme['reference_number']}: {ncsme['notes']}",
                f"2. {majd['article_doi']} reference {majd['reference_number']}: {majd['notes']}",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    build()
