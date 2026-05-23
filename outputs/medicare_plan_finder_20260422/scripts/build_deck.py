#!/usr/bin/env python3
"""Build the Cohere-style tan slide deck and methods note."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
DECK = ROOT / "deck"
ASSETS = DECK / "assets"
DECK.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)


def load_json(name: str):
    return json.loads((ANALYSIS / name).read_text())


METRICS = load_json("key_metrics.json")
TOP = load_json("top_tables.json")


def first(segment: str, rows: list[dict]) -> dict:
    return next(row for row in rows if row["segment"] == segment)


ALL_PLAN = first("All plans", METRICS["plan_summary"])
LOCAL_PLAN = first("Local MA-PD", METRICS["plan_summary"])
PDP_PLAN = first("Stand-alone PDP", METRICS["plan_summary"])
REG_PLAN = first("Regional MA-PD", METRICS["plan_summary"])
ALL_FORM = first("All plans", METRICS["formulary_plan_summary"])
ALL_SPEC = first("All plans", METRICS["specialty_tier_summary"])
PDP_SPEC = first("Stand-alone PDP", METRICS["specialty_tier_summary"])
ALL_INSULIN = first("All plans", METRICS["insulin_summary"])
PDP_INSULIN = first("Stand-alone PDP", METRICS["insulin_summary"])


def make_background() -> None:
    path = ASSETS / "tan_slide_background.png"
    w, h = 1600, 900
    base = Image.new("RGB", (w, h), "#f6f1e8")

    def radial(cx, cy, radius, color, alpha):
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for r in range(radius, 0, -8):
            a = int(alpha * (r / radius) ** 1.8)
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, a))
        return layer.filter(ImageFilter.GaussianBlur(26))

    img = base.convert("RGBA")
    img.alpha_composite(radial(95, 90, 620, (215, 255, 95), 90))
    img.alpha_composite(radial(1340, 90, 470, (184, 216, 255), 76))
    img.alpha_composite(radial(1280, 790, 420, (255, 184, 107), 42))
    img.convert("RGB").save(path, optimize=True)


def pct(value) -> str:
    return f"{float(value):.1f}%"


def money(value) -> str:
    return f"${float(value):,.2f}".replace(".00", "")


def bar(label: str, value: float, max_value: float, color: str = "lime", note: str = "") -> str:
    width = max(3, min(100, value / max_value * 100))
    return f"""
      <div class="bar-row">
        <div class="bar-label">{label}</div>
        <div>
          <div class="track"><span class="bar {color}" style="width:{width:.1f}%"></span></div>
          {f'<div class="bar-note">{note}</div>' if note else ''}
        </div>
        <div class="bar-value">{value:g}</div>
      </div>
    """


def hbar(label: str, value: float, color: str = "lime", suffix: str = "%") -> str:
    width = max(3, min(100, value))
    return f"""
      <div class="hbar">
        <div class="hbar-top"><span>{label}</span><strong>{value:g}{suffix}</strong></div>
        <div class="track slim"><span class="bar {color}" style="width:{width:.1f}%"></span></div>
      </div>
    """


def cite(n: int) -> str:
    return f'<a class="cite" href="#source-{n}">{n}</a>'


def bg() -> str:
    return '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />'


def slide_num(n: int, total: int = 12) -> str:
    return ""


def selected_drug_rows() -> str:
    rows = [
        ("Etanercept products", "Tier 5", "QL 81%; PA 98.5%", "Enbrel RXCUIs"),
        ("Apixaban tablets", "Tier 3", "QL 90.6%-92.4%; PA 0%", "Eliquis 2.5 mg and 5 mg"),
        ("SGLT2 inhibitors", "Tier 3", "QL 94.8%-98.2%; PA 0%", "Dapagliflozin and empagliflozin"),
        ("Ibrutinib products", "Tier 5", "QL 92.4%-94.8%; PA 99.1%", "Imbruvica capsule/tablet"),
    ]
    return "\n".join(
        f"""
        <div class="table-row four">
          <div><strong>{drug}</strong><span>{desc}</span></div>
          <div>{tier}</div>
          <div>{um}</div>
          <div>329 formularies</div>
        </div>
        """
        for drug, tier, um, desc in rows
    )


def region_rows(rows: list[dict]) -> str:
    return "\n".join(
        f"""
        <div class="table-row three">
          <div>{r['PDP_REGION_CODE']}</div>
          <div>{int(r['plans'])}</div>
          <div>{money(r['median_premium'])}</div>
        </div>
        """
        for r in rows
    )


def county_rows(rows: list[dict]) -> str:
    return "\n".join(
        f"""
        <div class="table-row three">
          <div>{r['COUNTY']}, {r['STATE']}</div>
          <div>{int(r['local_ma_pd_plans'])}</div>
          <div>{r['STATENAME']}</div>
        </div>
        """
        for r in rows
    )


def write_html() -> None:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Medicare Plan Finder Part D Data Signals, April 2026</title>
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
      --radius: 26px;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; scrollbar-width: none; }}
    html::-webkit-scrollbar, body::-webkit-scrollbar {{ display: none; }}
    body {{
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.34;
    }}
    body, *, *::before, *::after {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    a {{ color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .slide {{
      width: 100vw;
      min-height: 100vh;
      height: 100vh;
      padding: 68px 0 34px;
      position: relative;
      overflow: hidden;
      page-break-after: always;
      break-after: page;
      background: var(--paper);
    }}
    .slide:last-child {{ page-break-after: auto; break-after: auto; }}
    .slide-bg-img {{ position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; pointer-events: none; user-select: none; }}
    .slide > *:not(.slide-bg-img) {{ position: relative; z-index: 1; }}
    .wrap {{ width: min(1360px, calc(100vw - 48px)); margin: 0 auto; }}
    h1, h2, h3, p {{ margin: 0; }}
    h1 {{ font-size: 88px; line-height: .92; letter-spacing: -0.045em; font-weight: 500; max-width: 1300px; }}
    h2 {{ font-size: 58px; line-height: .96; letter-spacing: -0.04em; font-weight: 500; }}
    h3 {{ font-size: 29px; line-height: 1.02; letter-spacing: -0.035em; font-weight: 550; }}
    .eyebrow {{
      display: inline-flex; align-items: center; border: 1.4px solid var(--line); padding: 8px 12px;
      border-radius: 999px; font-size: 15px; font-weight: 850; letter-spacing: .06em; text-transform: uppercase;
      margin-bottom: 18px; background: var(--lime);
    }}
    .section-head {{ margin-bottom: 26px; }}
    .section-head p {{ margin-top: 13px; color: var(--muted); font-size: 22px; max-width: 1280px; }}
    .hero-grid {{ display: grid; grid-template-columns: 1fr; gap: 28px; }}
    .hero-note {{
      width: 1120px; border: 1.5px solid var(--line); border-radius: var(--radius); background: rgba(255,250,240,.84);
      padding: 26px 30px; box-shadow: var(--shadow);
    }}
    .hero-note p {{ color: var(--muted); font-size: 27px; line-height: 1.28; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
    .metric, .panel, .card {{
      border: 1.5px solid var(--line); border-radius: var(--radius); background: rgba(255,250,240,.84); box-shadow: var(--shadow);
    }}
    .metric {{ min-height: 142px; padding: 18px 20px; }}
    .num {{ font-size: 48px; line-height: .95; letter-spacing: -0.055em; font-weight: 600; }}
    .label {{ margin-top: 10px; color: var(--muted); font-size: 15px; line-height: 1.25; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .panel {{ overflow: hidden; }}
    .panel.dark {{ background: #11130f; color: var(--paper); }}
    .panel.dark p, .panel.dark .muted, .panel.dark .label {{ color: rgba(246,241,232,.72); }}
    .panel-pad {{ padding: 26px; }}
    .card {{ padding: 22px; min-height: 174px; }}
    .card p {{ color: var(--muted); margin-top: 10px; font-size: 17px; }}
    .big-text {{ color: var(--muted); font-size: 29px; line-height: 1.3; }}
    .bars {{ display: grid; gap: 16px; }}
    .bar-row {{ display: grid; grid-template-columns: 210px 1fr 118px; gap: 15px; align-items: center; }}
    .bar-label {{ font-weight: 850; font-size: 17px; letter-spacing: -0.02em; }}
    .track {{ position: relative; height: 32px; border: 1px solid rgba(16,18,15,.25); border-radius: 999px; background: rgba(16,18,15,.07); overflow: hidden; }}
    .track.slim {{ height: 18px; }}
    .panel.dark .track {{ border-color: rgba(246,241,232,.28); background: rgba(246,241,232,.08); }}
    .bar {{ position: absolute; inset: 0 auto 0 0; border-radius: 999px; min-width: 6px; }}
    .lime {{ background: var(--lime); }} .orange {{ background: var(--orange); }} .blue {{ background: var(--blue); }}
    .pink {{ background: var(--pink); }} .gray {{ background: var(--gray); }} .red {{ background: var(--red); }}
    .bar-value {{ color: var(--muted); font-weight: 850; font-size: 17px; }}
    .panel.dark .bar-value, .panel.dark .bar-label {{ color: var(--paper); }}
    .bar-note {{ margin-top: 5px; color: var(--muted); font-size: 13px; }}
    .hbar {{ display: grid; gap: 8px; margin-bottom: 14px; }}
    .hbar-top {{ display: flex; justify-content: space-between; gap: 16px; color: var(--muted); font-size: 16px; }}
    .hbar-top strong {{ color: var(--ink); }}
    .table {{ border: 1.5px solid var(--line); border-radius: 24px; overflow: hidden; background: var(--line); display: grid; gap: 1px; }}
    .table-row {{ display: grid; gap: 1px; background: var(--line); }}
    .table-row.three {{ grid-template-columns: 1.2fr .55fr .75fr; }}
    .table-row.four {{ grid-template-columns: 1.35fr .48fr 1fr .72fr; }}
    .table-row > div {{ background: var(--card); padding: 13px 15px; min-height: 58px; font-size: 16px; }}
    .table-row.head > div {{ background: #11130f; color: var(--paper); font-size: 12px; letter-spacing: .055em; text-transform: uppercase; font-weight: 850; min-height: auto; }}
    .table-row span {{ display: block; color: var(--muted); margin-top: 4px; font-size: 13px; line-height: 1.2; }}
    .cite {{ font-size: .62em; vertical-align: super; margin-left: 2px; font-weight: 800; text-decoration: none; }}
    .note {{ margin-top: 13px; color: var(--muted); font-size: 14px; }}
    .source-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px 26px; }}
    .source-list p {{ color: var(--muted); font-size: 18px; margin-bottom: 13px; break-inside: avoid; }}
    .method-list {{ display: grid; gap: 12px; }}
    .method-item {{ display: grid; grid-template-columns: 170px 1fr; gap: 18px; border-top: 1px solid rgba(16,18,15,.22); padding-top: 12px; }}
    .method-item strong {{ font-size: 16px; }}
    .method-item p {{ color: var(--muted); font-size: 16px; line-height: 1.34; }}
    .slide-geography h2 {{ font-size: 54px; }}
    .slide-geography .section-head {{ margin-bottom: 18px; }}
    .slide-geography .section-head p {{ font-size: 20px; }}
    .slide-geography .table-row > div {{ min-height: 50px; padding: 10px 13px; font-size: 15px; }}
    .slide-geography .note {{ margin-top: 8px; font-size: 12px; }}
    .slide-num {{ position: absolute; left: auto; right: 40px; bottom: 28px; width: max-content; font-size: 11px; letter-spacing: .16em; text-transform: uppercase; color: rgba(16,18,15,.38); font-weight: 800; }}
    @page {{ size: 1600px 900px; margin: 0; }}
    @media print {{
      .slide {{ width: 1600px; height: 900px; min-height: 900px; padding: 68px 0 34px; box-shadow: none; }}
      .wrap {{ width: 1360px; }}
      .metric, .panel, .card, .hero-note {{ box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <article class="slide">
    {bg()}
    <div class="wrap hero-grid">
      <div>
        <div class="eyebrow">CMS Plan Finder PUF · April 2026 release</div>
        <h1>Medicare Part D plan data reveal formulary, cost-sharing, and access-management signals</h1>
      </div>
      <div class="hero-note">
        <p>Analysis of the latest available CMS monthly Plan Finder public use file as of May 19, 2026: release dated April 22, 2026, for contract year 2026. Estimates are unweighted and should be interpreted as plan, formulary, or plan-pharmacy record summaries rather than enrollment-weighted exposure measures.{cite(1)}</p>
      </div>
      <div class="metrics">
        <div class="metric"><div class="num">{METRICS['unique_plans']:,}</div><div class="label">unique plan-segments after deduplicating service-area rows</div></div>
        <div class="metric"><div class="num">{METRICS['unique_formularies']}</div><div class="label">active formularies in the basic formulary file</div></div>
        <div class="metric"><div class="num">{METRICS['row_counts']['basic'] / 1_000_000:.2f}M</div><div class="label">basic formulary rows with tier and utilization-management fields</div></div>
        <div class="metric"><div class="num">2.1 GB</div><div class="label">compressed CMS ZIP, SHA-256 recorded for replication</div></div>
      </div>
    </div>
    {slide_num(1)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Methods</div>
        <h2>Plan-level inference required deduplication before cross-file joins</h2>
        <p>CMS publishes plan information at the service-area row level. Analyses used the plan-segment key defined in the record layout and retained service-area expansion only for county or region availability measures.{cite(2)}</p>
      </div>
      <div class="grid-2">
        <div class="panel"><div class="panel-pad method-list">
          <div class="method-item"><strong>Source</strong><p>Downloaded CMS Monthly Prescription Drug Plan Formulary and Pharmacy Network Information titled 2026-04-22; direct file <code>2026_20260415.zip</code>.</p></div>
          <div class="method-item"><strong>Unit</strong><p>Plans were uniquely identified by <code>CONTRACT_ID</code>, <code>PLAN_ID</code>, and <code>SEGMENT_ID</code>; plan-county rows were not counted as separate plans.</p></div>
          <div class="method-item"><strong>Joins</strong><p>Plan information was joined to formulary summaries by <code>FORMULARY_ID</code>; cost-sharing analyses used plan-tier-days-supply-channel rows.</p></div>
          <div class="method-item"><strong>Interpretation</strong><p>No estimates are weighted by enrollment, utilization, claims volume, net price, rebates, or spending.</p></div>
        </div></div>
        <div class="panel dark"><div class="panel-pad">
          <h3>Record linkage used in the analysis</h3>
          <p class="big-text" style="margin-top:18px">Plan information defines the plan universe; the basic formulary file defines formulary entries and restrictions; beneficiary cost and insulin files define tier-level cost sharing; pharmacy-network files define plan-pharmacy attributes and dispensing fees.{cite(2)}</p>
          <p class="note" style="color:rgba(246,241,232,.72)">CMS notes that pharmacy network and drug pricing data are updated on Medicare Plan Finder every two weeks, so a monthly PUF may not exactly match the current Medicare.gov display.{cite(3)}</p>
        </div></div>
      </div>
    </div>
    {slide_num(2)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Plan universe</div>
        <h2>MA-PD plan-segments dominate the file; stand-alone PDPs have higher median premiums</h2>
        <p>The file contained {METRICS['service_area_rows']:,} plan information rows but {METRICS['unique_plans']:,} unique plan-segments after deduplication.</p>
      </div>
      <div class="grid-2">
        <div class="panel"><div class="panel-pad bars">
          {bar("Local MA-PD", LOCAL_PLAN["plans"], LOCAL_PLAN["plans"], "lime", f"median premium {money(LOCAL_PLAN['median_premium'])}; zero-premium {pct(LOCAL_PLAN['zero_premium_pct'])}")}
          {bar("Stand-alone PDP", PDP_PLAN["plans"], LOCAL_PLAN["plans"], "blue", f"median premium {money(PDP_PLAN['median_premium'])}; zero-premium {pct(PDP_PLAN['zero_premium_pct'])}")}
          {bar("Regional MA-PD", REG_PLAN["plans"], LOCAL_PLAN["plans"], "orange", f"median premium {money(REG_PLAN['median_premium'])}; zero-premium {pct(REG_PLAN['zero_premium_pct'])}")}
        </div></div>
        <div class="grid-2" style="grid-template-columns:1fr 1fr">
          <div class="metric"><div class="num">{pct(ALL_PLAN['zero_premium_pct'])}</div><div class="label">of all unique plan-segments had $0 listed premium</div></div>
          <div class="metric"><div class="num">{money(PDP_PLAN['median_premium'])}</div><div class="label">median stand-alone PDP monthly premium</div></div>
          <div class="metric"><div class="num">{money(ALL_PLAN['median_deductible'])}</div><div class="label">median annual deductible across unique plan-segments</div></div>
          <div class="metric"><div class="num">{pct(PDP_PLAN['deductible_615_pct'])}</div><div class="label">of stand-alone PDPs had deductible at or above $615</div></div>
        </div>
      </div>
    </div>
    {slide_num(3)}
  </article>

  <article class="slide slide-geography">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Geography</div>
        <h2>Local MA-PD plan availability varied widely across counties</h2>
        <p>County availability counts were based on unsuppressed local MA-PD plan-segments in the plan information file. These are offer counts, not enrollment-weighted access measures.</p>
      </div>
      <div class="grid-2">
        <div class="panel dark"><div class="panel-pad">
          <div class="metrics" style="grid-template-columns:repeat(2,1fr)">
            <div><div class="num">{METRICS['local_ma_pd_county_availability']['median']:.0f}</div><div class="label">median local MA-PD plans per county</div></div>
            <div><div class="num">{METRICS['local_ma_pd_county_availability']['min']:.0f}-{METRICS['local_ma_pd_county_availability']['max']:.0f}</div><div class="label">observed county range</div></div>
          </div>
          <div style="margin-top:28px">
            {hbar("25th percentile", METRICS['local_ma_pd_county_availability']['p25'] / METRICS['local_ma_pd_county_availability']['max'] * 100, "blue", "")}
            {hbar("median", METRICS['local_ma_pd_county_availability']['median'] / METRICS['local_ma_pd_county_availability']['max'] * 100, "lime", "")}
            {hbar("75th percentile", METRICS['local_ma_pd_county_availability']['p75'] / METRICS['local_ma_pd_county_availability']['max'] * 100, "orange", "")}
          </div>
        </div></div>
        <div class="panel"><div class="panel-pad">
          <h3>Highest and lowest county examples</h3>
          <div class="table" style="margin-top:16px">
            <div class="table-row head three"><div>County</div><div>Plans</div><div>State name</div></div>
            {county_rows(TOP['highest_local_ma_pd_counties'][:3])}
            {county_rows(TOP['lowest_local_ma_pd_counties'][:3])}
          </div>
          <p class="note">County examples are descriptive and are not adjusted for population, Medicare Advantage penetration, plan enrollment, or county-level morbidity.</p>
        </div></div>
      </div>
    </div>
    {slide_num(4)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Formulary management</div>
        <h2>More than half of formulary entries had at least one utilization-management flag</h2>
        <p>Across plan-linked formularies, the median formulary contained {ALL_FORM['median_ndcs']:,.0f} NDC/RxCUI entries. The following percentages are median within-formulary shares across plan-segments.</p>
      </div>
      <div class="grid-2">
        <div class="panel"><div class="panel-pad">
          {hbar("Any utilization-management flag", ALL_FORM["median_any_um_ndc_pct"], "lime")}
          {hbar("Quantity limit", ALL_FORM["median_ql_ndc_pct"], "blue")}
          {hbar("Prior authorization", ALL_FORM["median_pa_ndc_pct"], "orange")}
          {hbar("Step therapy", ALL_FORM["median_st_ndc_pct"], "pink")}
          <p class="note">Utilization-management flags were calculated at the formulary-entry level. A flag does not imply a beneficiary-level restriction rate.</p>
        </div></div>
        <div class="panel dark"><div class="panel-pad">
          <h3>Analytic implication</h3>
          <p class="big-text" style="margin-top:18px">The Plan Finder PUF can support repeated monitoring of formulary design, but observed restriction rates should be interpreted as design attributes and not as measures of treatment access, abandonment, or health outcomes.</p>
          <p class="note" style="color:rgba(246,241,232,.72)">The basic formulary file includes NDC/RxCUI, tier, quantity limit, prior authorization, step therapy, and selected-drug indicators.{cite(2)}</p>
        </div></div>
      </div>
    </div>
    {slide_num(5)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Selected drugs</div>
        <h2>The 2026 selected-drug flag enables monitoring of formulary placement and restrictions</h2>
        <p>All active formularies included entries flagged as selected drugs. Examples below are descriptive RxCUI-level summaries for selected products with high formulary coverage.</p>
      </div>
      <div class="panel"><div class="panel-pad">
        <div class="table">
          <div class="table-row head four"><div>Selected-drug product group</div><div>Median tier</div><div>Observed UM pattern</div><div>Coverage in file</div></div>
          {selected_drug_rows()}
        </div>
        <p class="note">Selected-drug analyses used RxNorm names only for labeling. The PUF does not contain manufacturer discounts, rebates, net prices, utilization, or beneficiary spending.</p>
      </div></div>
    </div>
    {slide_num(6)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Specialty tiers</div>
        <h2>Specialty-tier cost sharing was commonly subject to the deductible and often expressed as coinsurance</h2>
        <p>The beneficiary cost file was restricted to initial coverage, 30-day supply rows with <code>TIER_SPECIALTY_YN = Y</code>.</p>
      </div>
      <div class="grid-3">
        <div class="metric"><div class="num">{ALL_SPEC['plans_with_specialty_tier']:,}</div><div class="label">plan-segments with at least one specialty-tier row</div></div>
        <div class="metric"><div class="num">{pct(ALL_SPEC['deductible_applies_pct'])}</div><div class="label">specialty-tier rows where deductible applies</div></div>
        <div class="metric"><div class="num">{pct(PDP_SPEC['coinsurance_pref_pct'])}</div><div class="label">stand-alone PDP specialty rows using preferred-retail coinsurance</div></div>
      </div>
      <div class="grid-2" style="margin-top:18px">
        <div class="panel"><div class="panel-pad">
          {hbar("All plan-segments: preferred-retail coinsurance", ALL_SPEC["coinsurance_pref_pct"], "lime")}
          {hbar("Stand-alone PDPs: preferred-retail coinsurance", PDP_SPEC["coinsurance_pref_pct"], "blue")}
          {hbar("All plan-segments: deductible applies", ALL_SPEC["deductible_applies_pct"], "orange")}
        </div></div>
        <div class="panel dark"><div class="panel-pad">
          <h3>Observed coinsurance level</h3>
          <p class="big-text" style="margin-top:18px">Among rows using coinsurance, the median preferred-retail specialty-tier coinsurance was {ALL_SPEC['median_pref_coinsurance_if_coinsurance']:.0f}% overall and {PDP_SPEC['median_pref_coinsurance_if_coinsurance']:.0f}% in stand-alone PDPs.</p>
        </div></div>
      </div>
    </div>
    {slide_num(7)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Insulin</div>
        <h2>Insulin cost-sharing fields show the policy cap structure but require the statutory lesser-of interpretation</h2>
        <p>For 2026, CMS states that the applicable beneficiary amount for Part D-covered insulin is the lesser of the copay cap, a maximum-fair-price-based amount when applicable, or a negotiated-price-based amount.{cite(3)}</p>
      </div>
      <div class="grid-2">
        <div class="grid-2" style="grid-template-columns:1fr 1fr">
          <div class="metric"><div class="num">{ALL_INSULIN['plans_with_insulin_rows']:,}</div><div class="label">plan-segments with insulin cost-sharing rows</div></div>
          <div class="metric"><div class="num">{money(ALL_INSULIN['pref_retail_copay_median'])}</div><div class="label">median populated preferred-retail 30-day insulin copay</div></div>
          <div class="metric"><div class="num">{pct(ALL_INSULIN['pref_retail_copay_le_35_pct'])}</div><div class="label">populated preferred-retail copay rows at or below $35</div></div>
          <div class="metric"><div class="num">{ALL_INSULIN['pref_retail_coin_median_pct']:.0f}%</div><div class="label">median populated preferred-retail insulin coinsurance</div></div>
        </div>
        <div class="panel"><div class="panel-pad">
          {hbar("All plans: preferred-retail copay populated", ALL_INSULIN["pref_retail_copay_nonmissing_pct"], "lime")}
          {hbar("PDPs: preferred-retail copay populated", PDP_INSULIN["pref_retail_copay_nonmissing_pct"], "blue")}
          {hbar("All plans: preferred-retail coinsurance populated", ALL_INSULIN["pref_retail_coin_nonmissing_pct"], "orange")}
          <p class="note">Blank fields should not be interpreted as zero cost sharing. Analyses should stratify by channel and days supply.</p>
        </div></div>
      </div>
    </div>
    {slide_num(8)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Supplemental coverage</div>
        <h2>Excluded-drug and indication-based coverage files identify narrower benefit-design signals</h2>
        <p>These files are smaller than the basic formulary file but are useful for tracking supplemental and indication-specific coverage policies.</p>
      </div>
      <div class="grid-2">
        <div class="panel"><div class="panel-pad">
          <h3>Excluded drugs</h3>
          <div class="metrics" style="grid-template-columns:repeat(2,1fr); margin-top:18px">
            <div><div class="num">{METRICS['excluded_drugs_summary']['plans_with_excluded_benefit_contract_plan']:,}</div><div class="label">contract-plan pairs with excluded-drug entries</div></div>
            <div><div class="num">{METRICS['excluded_drugs_summary']['rxcui_count']}</div><div class="label">distinct RxCUI values in the excluded-drug file</div></div>
          </div>
          {hbar("Quantity-limit rows", METRICS['excluded_drugs_summary']['quantity_limit_pct'], "blue")}
          {hbar("Capped-benefit rows", METRICS['excluded_drugs_summary']['capped_benefit_pct'], "orange")}
        </div></div>
        <div class="panel dark"><div class="panel-pad">
          <h3>Indication-based coverage</h3>
          <p class="big-text" style="margin-top:18px">The indication-based coverage file contained {METRICS['ibc_rows']} rows across {METRICS['ibc_plan_pairs']} contract-plan pairs. The most frequent examples included ixekizumab, dupilumab, pitolisant, rimegepant, and anakinra indication entries.</p>
          <p class="note" style="color:rgba(246,241,232,.72)">Interpretation should remain product- and indication-specific because the file is sparse relative to the full formulary universe.</p>
        </div></div>
      </div>
    </div>
    {slide_num(9)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Regional PDP premiums</div>
        <h2>Stand-alone PDP premium distributions varied by region</h2>
        <p>PDP region summaries were based on unique stand-alone PDP plan-segments, not county-expanded rows. Region names are available in the geographic locator file.</p>
      </div>
      <div class="grid-2">
        <div class="panel"><div class="panel-pad">
          <h3>Highest median premium regions</h3>
          <div class="table" style="margin-top:16px">
            <div class="table-row head three"><div>PDP region</div><div>Plans</div><div>Median premium</div></div>
            {region_rows(TOP['highest_pdp_premium_regions'][:6])}
          </div>
        </div></div>
        <div class="panel dark"><div class="panel-pad">
          <h3>Distribution across 39 PDP regions</h3>
          <div class="metrics" style="grid-template-columns:repeat(2,1fr); margin-top:18px">
            <div><div class="num">{money(METRICS['pdp_region_median_premium']['median'])}</div><div class="label">median of regional median premiums</div></div>
            <div><div class="num">{money(METRICS['pdp_region_median_premium']['min'])}-{money(METRICS['pdp_region_median_premium']['max'])}</div><div class="label">range of regional median premiums</div></div>
          </div>
          <p class="note" style="color:rgba(246,241,232,.72)">Regional comparisons are descriptive. They are not adjusted for benefit design, low-income premium subsidy benchmarks, enrollment, or formulary differences.</p>
        </div></div>
      </div>
    </div>
    {slide_num(10)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Interpretation</div>
        <h2>Signals worth monitoring for HEOR and market access research</h2>
        <p>The PUF is best suited to transparent, repeated measurement of benefit design. It should be paired with enrollment, claims, outcomes, and net-cost data for causal or budget-impact interpretation.</p>
      </div>
      <div class="grid-3">
        <div class="card"><h3>Formulary design</h3><p>Track tier placement and utilization-management changes, particularly for selected drugs, high-cost specialty products, and products with indication-based coverage.</p></div>
        <div class="card"><h3>Patient affordability</h3><p>Use beneficiary cost files to describe plan-level cost-sharing structures, while separating copay and coinsurance and avoiding claims about realized out-of-pocket spending.</p></div>
        <div class="card"><h3>Market access comparators</h3><p>Compare plan types and regions descriptively, with clear denominators and without conflating plan availability with beneficiary enrollment or use.</p></div>
      </div>
      <div class="panel dark" style="margin-top:18px"><div class="panel-pad">
        <p class="big-text">A conservative interpretation is that April 2026 Plan Finder data show broad formulary standardization, frequent formulary-entry utilization management, and clearly observable IRA-related data fields, but not beneficiary-level access, net prices, manufacturer discounts, or clinical outcomes.</p>
      </div></div>
    </div>
    {slide_num(11)}
  </article>

  <article class="slide">
    {bg()}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Sources and replication</div>
        <h2>Primary sources and reproducible files</h2>
        <p>Full methods, commands, file hashes, and generated summary tables are documented in the companion methods note in the same output directory.</p>
      </div>
      <div class="panel"><div class="panel-pad source-list">
        <div>
          <p id="source-1"><strong>1. CMS/data.gov dataset.</strong> Monthly Prescription Drug Plan Formulary and Pharmacy Network Information. Latest available distribution used: 2026-04-22. <a href="https://catalog.data.gov/dataset/monthly-prescription-drug-plan-formulary-and-pharmacy-network-information">catalog.data.gov</a></p>
          <p id="source-2"><strong>2. CMS record layout.</strong> Prescription Drug Plan Formulary and Pharmacy Network Public Use File Record Layout, 2026. <a href="https://data.cms.gov/sites/default/files/2025-10/0564eb37-402d-4110-bd98-2d5399dc30e7/PUFRecordLayout-2026.pdf">PDF</a></p>
        </div>
        <div>
          <p id="source-3"><strong>3. CMS methodology.</strong> Prescription Drug Plan Formulary and Pharmacy Network Public Use File Methodology, 2026. <a href="https://data.cms.gov/sites/default/files/2025-10/8f1d8b42-bfd1-4f9c-b86d-b92af0c6f3d5/Methodology-PUF-2026.pdf">PDF</a></p>
          <p><strong>Local reproducibility.</strong> Analysis script: <code>scripts/analyze_plan_finder.py</code>; deck builder: <code>scripts/build_deck.py</code>; source ZIP SHA-256: <code>{METRICS['outer_zip_sha256']}</code>.</p>
        </div>
      </div></div>
    </div>
    {slide_num(12)}
  </article>
</body>
</html>
"""
    (DECK / "medicare_plan_finder_20260422_cohere_tan.html").write_text(html)


def write_methods() -> None:
    methods = f"""# Methods: CMS Medicare Plan Finder Part D PUF, April 2026

## Data source

The analysis used the CMS Monthly Prescription Drug Plan Formulary and Pharmacy Network Information public use file distribution titled `2026-04-22`, which was the latest distribution listed by CMS/data.gov on May 19, 2026. The next estimated monthly release listed by CMS/data.gov was May 20, 2026, so the April 22 file was treated as the most recent available file at the time of analysis.

- Dataset page: https://catalog.data.gov/dataset/monthly-prescription-drug-plan-formulary-and-pharmacy-network-information
- Direct ZIP: https://data.cms.gov/sites/default/files/2026-04/675bb472-ce7a-48a1-b5ca-8ce7c9fc8c58/2026_20260415.zip
- Record layout: https://data.cms.gov/sites/default/files/2025-10/0564eb37-402d-4110-bd98-2d5399dc30e7/PUFRecordLayout-2026.pdf
- Methodology: https://data.cms.gov/sites/default/files/2025-10/8f1d8b42-bfd1-4f9c-b86d-b92af0c6f3d5/Methodology-PUF-2026.pdf
- Downloaded ZIP SHA-256: `{METRICS['outer_zip_sha256']}`

## Files processed

The CMS ZIP contains nested component ZIP files. The analysis extracted and processed the plan information, geographic locator, basic formulary, beneficiary cost, insulin beneficiary cost, excluded drugs, and indication-based coverage files. The pharmacy-network component was retained as compressed parts because the six parts are large; a streaming profiler script is included for replication.

Observed row counts from the extracted files were:

- Plan information: {METRICS['row_counts']['plan']:,}
- Basic drugs formulary: {METRICS['row_counts']['basic']:,}
- Beneficiary cost: {METRICS['row_counts']['beneficiary']:,}
- Insulin beneficiary cost: {METRICS['row_counts']['insulin']:,}
- Excluded drugs formulary: {METRICS['row_counts']['excluded']:,}
- Indication-based coverage formulary: {METRICS['row_counts']['ibc']:,}
- Geographic locator: {METRICS['row_counts']['geo']:,}

## Analytic units

Plan information rows are service-area-expanded. Plan-level analyses therefore deduplicated records using `CONTRACT_ID`, `PLAN_ID`, and `SEGMENT_ID`, consistent with the CMS record layout. Contract IDs beginning with `H` were classified as local MA-PD, `R` as regional MA-PD, and `S` as stand-alone PDP. Suppressed plans identified by `PLAN_SUPPRESSED_YN = Y` were retained for denominator transparency; CMS states that suppressed plans appear in plan information but not other component files.

Formulary-level analyses used `FORMULARY_ID`. Plan-linked formulary analyses merged deduplicated plan records to formulary summaries using `FORMULARY_ID`. Cost-sharing analyses used the beneficiary cost and insulin beneficiary cost files at the plan-tier-days-supply-channel level.

## Measures

Plan universe measures included counts by contract type, median premiums, zero-premium shares, median deductibles, and shares with deductibles at or above $615.

Formulary measures included the number of distinct NDC/RxCUI entries per formulary and the within-formulary percentage of entries flagged for quantity limits, prior authorization, step therapy, and any of those utilization-management fields.

Selected-drug analyses used `SELECTED_DRUG_YN` in the basic formulary file. RxCUI labels were obtained from the National Library of Medicine RxNorm API and cached locally in `analysis/rxnorm_names_cache.json`; these labels were used only for slide readability.

Specialty-tier measures used beneficiary cost rows with `COVERAGE_LEVEL = 1`, `DAYS_SUPPLY = 1`, and `TIER_SPECIALTY_YN = Y`. Insulin measures used `DAYS_SUPPLY = 1` rows from the insulin beneficiary cost file and summarized populated copay and coinsurance fields. Blank insulin fields were treated as missing, not zero.

County availability measures counted unsuppressed local MA-PD plan-segments by `STATE` and `COUNTY_CODE`. Stand-alone PDP region summaries used deduplicated stand-alone PDP plan-segments by `PDP_REGION_CODE`.

## Limitations

All estimates are unweighted by enrollment, claims, utilization, prescriptions, population, morbidity, rebates, manufacturer discounts, or net prices. The PUF describes submitted plan design and Plan Finder inputs, not realized patient experience or outcomes. CMS notes that Medicare Plan Finder pharmacy network and drug pricing data are updated every two weeks, so a monthly PUF may not exactly match the current Medicare.gov display. The files do not reflect manufacturer discounts applied under the Medicare Part D Manufacturer Discount Program.

## Replication commands

From `/Users/justinyu/Desktop/linkedin-posts`:

```bash
mkdir -p outputs/medicare_plan_finder_20260422/raw outputs/medicare_plan_finder_20260422/extracted
curl -L --fail --continue-at - --output outputs/medicare_plan_finder_20260422/raw/2026_20260415.zip \\
  'https://data.cms.gov/sites/default/files/2026-04/675bb472-ce7a-48a1-b5ca-8ce7c9fc8c58/2026_20260415.zip'
shasum -a 256 outputs/medicare_plan_finder_20260422/raw/2026_20260415.zip
unzip -o outputs/medicare_plan_finder_20260422/raw/2026_20260415.zip -d outputs/medicare_plan_finder_20260422/extracted
for f in outputs/medicare_plan_finder_20260422/extracted/*.zip; do
  case "$(basename "$f")" in
    pharmacy\\ networks*) ;;
    *) unzip -o "$f" -d outputs/medicare_plan_finder_20260422/extracted ;;
  esac
done
python3 outputs/medicare_plan_finder_20260422/scripts/analyze_plan_finder.py
python3 outputs/medicare_plan_finder_20260422/scripts/build_deck.py
node /Users/justinyu/.codex/skills/cohere-style-tan/scripts/export_html_slides_pdf.mjs \\
  --input /Users/justinyu/Desktop/linkedin-posts/outputs/medicare_plan_finder_20260422/deck/medicare_plan_finder_20260422_cohere_tan.html \\
  --output /Users/justinyu/Desktop/linkedin-posts/outputs/medicare_plan_finder_20260422/deck/medicare_plan_finder_20260422_cohere_tan.pdf \\
  --screenshots-dir /Users/justinyu/Desktop/linkedin-posts/outputs/medicare_plan_finder_20260422/deck/export/screenshots \\
  --render-check-dir /Users/justinyu/Desktop/linkedin-posts/outputs/medicare_plan_finder_20260422/deck/export/render-check
```

The streaming pharmacy-network profiler can be run separately:

```bash
bash outputs/medicare_plan_finder_20260422/scripts/profile_pharmacy_network.sh
```
"""
    (ROOT / "methods.md").write_text(methods)


def main() -> None:
    make_background()
    write_html()
    write_methods()


if __name__ == "__main__":
    main()
