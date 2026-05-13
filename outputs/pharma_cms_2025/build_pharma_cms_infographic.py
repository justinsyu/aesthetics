#!/usr/bin/env python3
import csv
import html
import json
import math
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image

OUT = Path(__file__).resolve().parent
SOURCES = OUT / "sources"
SCREENSHOTS = OUT / "screenshots"
EXPORT = OUT / "export"
SOURCES.mkdir(parents=True, exist_ok=True)
SCREENSHOTS.mkdir(parents=True, exist_ok=True)
EXPORT.mkdir(parents=True, exist_ok=True)

UA = "codex research justin@example.com"

# Public biopharma/pharma companies with SEC annual-report XBRL available.
# Ranking is then determined only by 2025 reported revenue, translated to USD.
CANDIDATES = {
    "JNJ": "0000200406",
    "LLY": "0000059478",
    "MRK": "0000310158",
    "PFE": "0000078003",
    "ABBV": "0001551152",
    "AZN": "0000901832",
    "NVS": "0001114448",
    "SNY": "0001121404",
    "BMY": "0000014272",
    "NVO": "0000353278",
    "GSK": "0001131399",
    "AMGN": "0000318154",
    "TAK": "0001395064",
    "GILD": "0000882095",
    "TEVA": "0000818686",
    "REGN": "0000872589",
    "VTRS": "0001792044",
    "VRTX": "0000875320",
    "BHC": "0000885590",
    "BIIB": "0000875045",
    "INCY": "0000879169",
    "JAZZ": "0001232524",
    "PRGO": "0001585364",
    "ARGX": "0001697862",
    "ALNY": "0001178670",
    "RDY": "0001135951",
    "BNTX": "0001776985",
    "NBIX": "0000914475",
    "MRNA": "0001682852",
}

DISPLAY_NAMES = {
    "JNJ": "Johnson & Johnson",
    "LLY": "Eli Lilly",
    "MRK": "Merck & Co.",
    "PFE": "Pfizer",
    "ABBV": "AbbVie",
    "AZN": "AstraZeneca",
    "NVS": "Novartis",
    "SNY": "Sanofi",
    "BMY": "Bristol Myers Squibb",
    "NVO": "Novo Nordisk",
    "GSK": "GSK",
    "AMGN": "Amgen",
    "TAK": "Takeda",
    "GILD": "Gilead",
    "TEVA": "Teva",
    "REGN": "Regeneron",
    "VTRS": "Viatris",
    "VRTX": "Vertex",
    "BHC": "Bausch Health",
    "BIIB": "Biogen",
    "INCY": "Incyte",
    "JAZZ": "Jazz",
    "PRGO": "Perrigo",
    "ARGX": "argenx",
    "ALNY": "Alnylam",
    "RDY": "Dr. Reddy's",
    "BNTX": "BioNTech",
    "NBIX": "Neurocrine",
    "MRNA": "Moderna",
}

LOGO_FILES = {
    "JNJ": "logos/JNJ.svg",
    "LLY": "logos/LLY.svg",
    "MRK": "logos/MRK.svg",
    "PFE": "logos/PFE.svg",
    "ABBV": "logos/ABBV.svg",
    "AZN": "logos/AZN.svg",
    "NVS": "logos/NVS.svg",
    "SNY": "logos/SNY.svg",
    "BMY": "logos/BMY.svg",
    "NVO": "logos/NVO.png",
    "GSK": "logos/GSK.svg",
    "AMGN": "logos/AMGN.svg",
    "TAK": "logos/TAK.svg",
    "GILD": "logos/GILD.svg",
    "TEVA": "logos/TEVA.svg",
    "REGN": "logos/REGN.svg",
    "VTRS": "logos/VTRS.svg",
    "VRTX": "logos/VRTX.svg",
    "BHC": "logos/BHC.svg",
    "BIIB": "logos/BIIB.svg",
}

REV_TAGS = [
    ("us-gaap", "Revenues"),
    ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    ("us-gaap", "SalesRevenueNet"),
    ("us-gaap", "SalesRevenueGoodsNet"),
    ("ifrs-full", "Revenue"),
    ("ifrs-full", "RevenueFromContractsWithCustomers"),
    ("ifrs-full", "RevenueFromSaleOfGoods"),
]
NI_TAGS = [
    ("us-gaap", "NetIncomeLoss"),
    ("us-gaap", "ProfitLoss"),
    ("ifrs-full", "ProfitLossAttributableToOwnersOfParent"),
    ("ifrs-full", "ProfitLossAttributableToOrdinaryEquityHoldersOfParentEntity"),
    ("ifrs-full", "ProfitLoss"),
]

# IRS yearly average currency exchange rates for 2025:
# foreign currency units per U.S. dollar. To get USD, divide by the rate.
FX_RATES = {
    "USD": 1.0,
    "EUR": 0.886,
    "DKK": 6.617,
    "GBP": 0.759,
    "JPY": 149.632,
    "INR": 87.133,
}

CMS_PROGRAMS = [
    ("Medicare FFS", 28.83),
    ("Medicare Advantage Part C", 23.67),
    ("Medicare Part D", 4.23),
    ("Medicaid", 37.39),
    ("CHIP", 1.37),
    ("APTC", 0.65746),
]

SHEET_WIDTH = 1200
SHEET_HEIGHT = 2245


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def generate_sheet_background():
    path = OUT / "pharma_cms_2025_background.png"
    width, height = SHEET_WIDTH, SHEET_HEIGHT
    base = hex_to_rgb("#f6f1e8")
    img = Image.new("RGB", (width, height), base)
    pixels = img.load()
    fields = [
        (0.08 * width, 0.03 * height, 350, hex_to_rgb("#d7ff5f"), 0.42),
        (0.88 * width, 0.08 * height, 300, hex_to_rgb("#b8d8ff"), 0.38),
        (0.78 * width, 0.95 * height, 330, hex_to_rgb("#ffb86b"), 0.34),
    ]
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            for cx, cy, radius, color, alpha in fields:
                distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if distance >= radius:
                    continue
                mix = alpha * (1 - distance / radius)
                r = round(r * (1 - mix) + color[0] * mix)
                g = round(g * (1 - mix) + color[1] * mix)
                b = round(b * (1 - mix) + color[2] * mix)
            pixels[x, y] = (r, g, b)
    img.save(path)
    return path.name


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read().decode("utf-8", "ignore")


def select_fact(facts, tags):
    best = None
    for tax, tag in tags:
        if tax not in facts or tag not in facts[tax]:
            continue
        for unit, values in facts[tax][tag]["units"].items():
            for fact in values:
                if fact.get("fy") != 2025 or fact.get("fp") != "FY":
                    continue
                if fact.get("form") not in ("10-K", "20-F", "40-F"):
                    continue
                start = fact.get("start", "")
                end = fact.get("end", "")
                score = 0
                if fact.get("frame") == "CY2025":
                    score += 50
                if start.startswith("2025") and end.startswith("2025"):
                    score += 30
                if end.startswith("2025") or end.startswith("2026"):
                    score += 10
                if fact.get("form") in ("10-K", "20-F"):
                    score += 5
                if best is None or score > best[0]:
                    best = (score, tax, tag, unit, fact)
    if best is None:
        return None
    _, tax, tag, unit, fact = best
    return {
        "taxonomy": tax,
        "tag": tag,
        "unit": unit,
        "value": fact["val"],
        "accn": fact["accn"],
        "form": fact["form"],
        "filed": fact.get("filed", ""),
        "start": fact.get("start", ""),
        "end": fact.get("end", ""),
        "frame": fact.get("frame", ""),
    }


def accession_primary_doc(cik, accn):
    sub = fetch_json(f"https://data.sec.gov/submissions/CIK{cik}.json")
    recent = sub["filings"]["recent"]
    if accn in recent["accessionNumber"]:
        idx = recent["accessionNumber"].index(accn)
        return recent["primaryDocument"][idx]
    for file_info in sub["filings"].get("files", []):
        older = fetch_json(f"https://data.sec.gov/submissions/{file_info['name']}")
        old_recent = older["filings"]["recent"]
        if accn in old_recent["accessionNumber"]:
            idx = old_recent["accessionNumber"].index(accn)
            return old_recent["primaryDocument"][idx]
    raise RuntimeError(f"Primary document not found for {cik} {accn}")


def sec_doc_url(cik, accn, doc):
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/{doc}"


def format_billions(value):
    return f"${value / 1_000_000_000:,.1f}B"


def format_source_value(value, unit):
    if abs(value) >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:,.2f}T {unit}"
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.1f}B {unit}"
    return f"{value / 1_000_000:,.1f}M {unit}"


def normalize_num(text):
    stripped = re.sub(r"[^0-9().-]", "", text or "")
    if not stripped:
        return None
    negative = stripped.startswith("(") and stripped.endswith(")")
    stripped = stripped.strip("()")
    try:
        value = float(stripped)
    except ValueError:
        return None
    return -value if negative else value


def fact_matches_visible_text(tag, target_value):
    text_value = normalize_num(tag.get_text(" ", strip=True))
    if text_value is None:
        return False
    try:
        scale = int(tag.get("scale", "0"))
    except ValueError:
        scale = 0
    candidate = text_value * (10 ** scale)
    tolerance = max(1.0, abs(target_value) * 0.0005)
    return abs(candidate - target_value) <= tolerance


def build_highlighted_filing(row):
    def highlighted_soup_for_url(url):
        html_text = fetch_text(url)
        soup = BeautifulSoup(html_text, "lxml")
        if soup.head is None:
            soup.insert(0, soup.new_tag("head"))
        base = soup.new_tag("base", href=url.rsplit("/", 1)[0] + "/")
        soup.head.insert(0, base)
        style = soup.new_tag("style")
        style.string = """
        ix\\:nonfraction[data-codex-highlight="revenue"],
        ix\\:nonfraction[data-codex-highlight="income"],
        [data-codex-highlight="revenue"],
        [data-codex-highlight="income"] {
          background: #d7ff5f !important;
          outline: 5px solid #ff8a00 !important;
          outline-offset: 2px !important;
          color: #000 !important;
          box-shadow: 0 0 0 10px rgba(255,184,107,.32) !important;
          position: relative !important;
          z-index: 99999 !important;
        }
        body::before {
          content: "Highlighted SEC filing facts: revenue and net income used in the calculation";
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 100000;
          background: #10120f;
          color: #fffaf0;
          font: 700 16px/1.2 Arial, sans-serif;
          padding: 8px 14px;
        }
        """
        soup.head.append(style)
        ids = []
        targets = [
            ("revenue", row["rev_tag"], row["revenue_reported"]),
            ("income", row["ni_tag"], row["net_income_reported"]),
        ]
        for kind, tag_name, target in targets:
            for element in soup.find_all(attrs={"name": re.compile(rf"(^|:){re.escape(tag_name)}$")}):
                if fact_matches_visible_text(element, target):
                    element["data-codex-highlight"] = kind
                    if element.get("id"):
                        ids.append(element["id"])
        return soup, ids

    soup, ids = highlighted_soup_for_url(row["source_url"])
    if len(ids) < 2:
        filing_dir = row["source_url"].rsplit("/", 1)[0]
        try:
            listing = fetch_json(f"{filing_dir}/index.json")
            htm_names = [
                item["name"] for item in listing["directory"]["item"]
                if item["name"].lower().endswith((".htm", ".html"))
                and item["name"] not in row["source_url"].rsplit("/", 1)[1]
            ]
            htm_names.sort(key=lambda name: (0 if "_d" in name.lower() else 1, name))
            for name in htm_names:
                candidate_url = f"{filing_dir}/{name}"
                candidate_soup, candidate_ids = highlighted_soup_for_url(candidate_url)
                if len(candidate_ids) >= 2:
                    soup, ids = candidate_soup, candidate_ids
                    row["source_url"] = candidate_url
                    break
        except Exception:
            pass
    out_file = SOURCES / f"{row['rank']:02d}_{row['ticker']}_highlighted_filing.html"
    out_file.write_text(str(soup), encoding="utf-8")
    row["highlighted_filing"] = str(out_file)
    row["highlight_ids"] = ids


def build_rows():
    rows = []
    for ticker, cik in CANDIDATES.items():
        facts = fetch_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
        rev = select_fact(facts["facts"], REV_TAGS)
        ni = select_fact(facts["facts"], NI_TAGS)
        if not rev or not ni:
            continue
        unit = rev["unit"]
        if ni["unit"] != unit or unit not in FX_RATES:
            continue
        primary_doc = accession_primary_doc(cik, rev["accn"])
        source_url = sec_doc_url(cik, rev["accn"], primary_doc)
        rate = FX_RATES[unit]
        row = {
            "ticker": ticker,
            "company": DISPLAY_NAMES.get(ticker, facts.get("entityName", ticker)),
            "cik": cik,
            "form": rev["form"],
            "filed": rev["filed"],
            "period_start": rev["start"],
            "period_end": rev["end"],
            "revenue_reported": rev["value"],
            "net_income_reported": ni["value"],
            "currency": unit,
            "fx_per_usd": rate,
            "revenue_usd": rev["value"] / rate,
            "net_income_usd": ni["value"] / rate,
            "rev_tag": rev["tag"],
            "ni_tag": ni["tag"],
            "rev_accn": rev["accn"],
            "ni_accn": ni["accn"],
            "source_url": source_url,
            "companyfacts_url": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
        }
        rows.append(row)
        time.sleep(0.12)
    rows.sort(key=lambda r: r["revenue_usd"], reverse=True)
    top20 = rows[:20]
    for idx, row in enumerate(top20, 1):
        row["rank"] = idx
        build_highlighted_filing(row)
        time.sleep(0.12)
    return top20


def write_outputs(rows):
    background_file = generate_sheet_background()
    cms_total = sum(value for _, value in CMS_PROGRAMS)
    net_income_total = sum(r["net_income_usd"] for r in rows) / 1_000_000_000
    revenue_total = sum(r["revenue_usd"] for r in rows) / 1_000_000_000
    ratio = net_income_total / cms_total
    data = {
        "generated": time.strftime("%Y-%m-%d"),
        "method": "Ranked SEC-reporting pharma/biopharma companies by 2025 annual revenue fact in EDGAR XBRL, translated to USD using IRS 2025 yearly average exchange rates.",
        "rows": rows,
        "cms_programs": CMS_PROGRAMS,
        "cms_total_b": cms_total,
        "top20_net_income_b": net_income_total,
        "top20_revenue_b": revenue_total,
        "ratio": ratio,
        "fx_rates": FX_RATES,
    }
    (OUT / "data.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    with (OUT / "pharma_top20_sec_2025.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "rank", "company", "ticker", "currency", "revenue_reported",
                "net_income_reported", "fx_per_usd", "revenue_usd", "net_income_usd",
                "form", "filed", "period_start", "period_end", "rev_tag", "ni_tag",
                "source_url", "companyfacts_url"
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in writer.fieldnames})

    max_ni = max(abs(r["net_income_usd"]) for r in rows)
    bar_rows = []
    for row in rows:
        width = max(2, round(abs(row["net_income_usd"]) / max_ni * 100))
        sign = "negative" if row["net_income_usd"] < 0 else "positive"
        bar_rows.append(f"""
          <tr>
            <td class="rank">{row['rank']}</td>
            <td><strong>{html.escape(row['company'])}</strong><span>{html.escape(row['ticker'])} · revenue {format_billions(row['revenue_usd'])}</span></td>
            <td class="money">{format_billions(row['net_income_usd'])}</td>
            <td><div class="bar-track"><div class="bar-fill {sign}" style="width:{width}%"></div></div></td>
          </tr>
        """)

    cms_rows = []
    cms_max = max(v for _, v in CMS_PROGRAMS)
    for label, value in CMS_PROGRAMS:
        cms_rows.append(f"""
          <div class="cms-row">
            <div><strong>{html.escape(label)}</strong><span>${value:,.2f}B</span></div>
            <div class="cms-track"><div style="width:{value / cms_max * 100:.1f}%"></div></div>
          </div>
        """)

    logo_cells = []
    for row in rows:
        logo_file = LOGO_FILES.get(row["ticker"])
        if not logo_file:
            continue
        logo_cells.append(f"""
          <div class="logo-cell">
            <img src="{html.escape(logo_file)}" alt="{html.escape(row['company'])} logo">
          </div>
        """)

    notes = (
        "SEC data are EDGAR XBRL facts from 2025 annual reports; top 20 are the largest "
        "SEC-reporting pharma/biopharma companies found in the candidate set, ranked by revenue alone. "
        "Non-USD filings are translated with IRS 2025 yearly average exchange rates. CMS says improper "
        "payments are not a fraud measure; this compares the government estimate commonly used as a "
        "waste/error proxy with pharma net income."
    )

    html_out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>2025 Pharma Net Income vs CMS Improper Payments</title>
  <style>
    :root {{
      --ink:#10120f; --muted:#5c6257; --paper:#f6f1e8; --paper2:#ebe4d6;
      --card:#fffaf0; --line:#1b1f17; --lime:#d7ff5f; --orange:#ffb86b;
      --blue:#b8d8ff; --pink:#ffd3e0; --gray:#d6d0c2; --red:#ff8a76;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--paper2); color:var(--ink); font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .sheet {{ width:1200px; height:2245px; margin:0 auto; overflow:hidden; position:relative; padding:54px; background:var(--paper); }}
    .sheet-bg {{ position:absolute; inset:0; z-index:0; width:100%; height:100%; object-fit:cover; pointer-events:none; user-select:none; }}
    .sheet > *:not(.sheet-bg):not(.sources) {{ position:relative; z-index:1; }}
    .eyebrow {{ display:inline-flex; align-items:center; gap:10px; padding:10px 18px; border:2px solid var(--line); border-radius:999px; background:var(--lime); font-weight:900; font-size:18px; letter-spacing:.02em; text-transform:uppercase; }}
    h1 {{ margin:30px 0 24px; font-size:64px; line-height:1.02; letter-spacing:-.02em; font-weight:650; max-width:1092px; }}
    .sub {{ max-width:1092px; color:var(--muted); font-size:24px; line-height:1.22; margin:0 0 32px; }}
    .hero-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; margin:28px 0 26px; }}
    .metric {{ border:3px solid var(--line); border-radius:24px; padding:28px; min-height:245px; background:var(--card); box-shadow:0 18px 48px rgba(16,18,15,.08); }}
    .metric.dark {{ background:var(--ink); color:var(--paper); }}
    .metric .label {{ font-size:20px; color:var(--muted); line-height:1.25; font-weight:750; text-transform:uppercase; letter-spacing:.03em; }}
    .metric.dark .label {{ color:rgba(246,241,232,.68); }}
    .metric .value {{ margin-top:18px; font-size:86px; line-height:.88; letter-spacing:-.025em; font-weight:500; }}
    .metric .caption {{ margin-top:18px; color:var(--muted); font-size:20px; line-height:1.3; }}
    .metric.dark .caption {{ color:rgba(246,241,232,.78); }}
    .ratio-strip {{ border:3px solid var(--line); border-radius:24px; overflow:hidden; background:var(--card); display:grid; grid-template-columns:{ratio / (ratio + 1) * 100:.2f}% 1fr; height:76px; margin-bottom:28px; }}
    .ratio-strip div {{ display:flex; align-items:center; padding:0 24px; font-weight:900; font-size:22px; }}
    .ratio-strip .left {{ background:var(--lime); border-right:3px solid var(--line); }}
    .ratio-strip .right {{ background:var(--pink); justify-content:flex-end; }}
    .content {{ display:grid; grid-template-columns: 1.2fr .8fr; gap:24px; }}
    .panel {{ border:3px solid var(--line); border-radius:24px; background:rgba(255,250,240,.86); overflow:hidden; }}
    .panel h2 {{ margin:0; padding:20px 22px; background:var(--ink); color:var(--paper); font-size:30px; line-height:1; letter-spacing:-.02em; }}
    table {{ width:100%; border-collapse:collapse; }}
    td {{ border-top:2px solid var(--line); padding:10px 12px; vertical-align:middle; font-size:18px; }}
    td.rank {{ width:42px; text-align:center; font-weight:900; background:var(--blue); }}
    td span {{ display:block; margin-top:3px; color:var(--muted); font-size:13px; line-height:1.15; }}
    td.money {{ width:112px; text-align:right; font-weight:900; }}
    .bar-track {{ width:148px; height:18px; border:2px solid var(--line); border-radius:999px; background:var(--paper2); overflow:hidden; }}
    .bar-fill {{ height:100%; background:var(--lime); }}
    .bar-fill.negative {{ background:var(--red); }}
    .cms-body {{ padding:20px; }}
    .cms-row {{ margin-bottom:20px; }}
    .cms-row div:first-child {{ display:flex; justify-content:space-between; gap:16px; font-size:20px; }}
    .cms-row span {{ font-weight:900; }}
    .cms-track {{ margin-top:8px; height:22px; border:2px solid var(--line); border-radius:999px; background:var(--paper2); overflow:hidden; }}
    .cms-track div {{ height:100%; background:var(--orange); }}
    .callout {{ margin-top:22px; border:3px solid var(--line); border-radius:22px; background:var(--blue); padding:28px 22px; }}
    .callout strong {{ display:block; font-size:48px; line-height:.95; letter-spacing:-.02em; margin-bottom:12px; }}
    .callout p {{ margin:0; font-size:24px; line-height:1.22; }}
    .logo-wall {{ margin-top:28px; display:grid; grid-template-columns:repeat(4, 1fr); gap:24px 12px; width:100%; }}
    .logo-cell {{ height:76px; border:2px solid rgba(16,18,15,.28); border-radius:12px; background:rgba(255,250,240,.72); display:flex; align-items:center; justify-content:center; padding:10px; }}
    .logo-cell img {{ width:90px; height:44px; object-fit:contain; display:block; }}
    .sources {{ position:absolute; left:54px; right:54px; bottom:32px; border-top:3px solid var(--line); padding-top:14px; color:var(--muted); font-size:14px; line-height:1.35; }}
    @page {{ size:1200px 2245px; margin:0; }}
    @media print {{ body {{ background:var(--paper); }} .sheet {{ margin:0; }} * {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }} }}
  </style>
</head>
<body>
  <main class="sheet">
    <img class="sheet-bg" src="{html.escape(background_file)}" alt="" aria-hidden="true">
    <div class="eyebrow">SEC annual reports · CMS FY2025</div>
    <h1>CMS improper payments approached a major share of top pharma profits</h1>
    <p class="sub">For the 20 largest SEC-reporting pharma/biopharma companies ranked by 2025 revenue, aggregate net income was {ratio:.1f}x the CMS FY2025 improper-payment estimate.</p>
    <section class="hero-grid">
      <div class="metric dark">
        <div class="label">Top 20 pharma net income</div>
        <div class="value">${net_income_total:,.1f}B</div>
        <div class="caption">Sum of 2025 net income from SEC annual report XBRL facts</div>
      </div>
      <div class="metric">
        <div class="label">CMS estimated improper payments</div>
        <div class="value">${cms_total:,.1f}B</div>
        <div class="caption">Medicare FFS, Part C, Part D, Medicaid, CHIP,<br>and APTC</div>
      </div>
    </section>
    <div class="ratio-strip"><div class="left">Pharma net income ${net_income_total:,.1f}B</div><div class="right">CMS ${cms_total:,.1f}B</div></div>
    <section class="content">
      <div class="panel">
        <h2>Net income by company</h2>
        <table>{''.join(bar_rows)}</table>
      </div>
      <div>
        <div class="panel">
          <h2>CMS estimate by program</h2>
          <div class="cms-body">{''.join(cms_rows)}</div>
        </div>
        <div class="callout">
          <strong>${revenue_total:,.0f}B</strong>
          <p>Total 2025 revenue represented by the top 20 list. Revenue ranks the companies; net income powers the comparison.</p>
        </div>
        <div class="logo-wall" aria-label="Company logos">{''.join(logo_cells)}</div>
      </div>
    </section>
    <div class="sources">
      Sources: SEC EDGAR XBRL annual-report facts for each company; IRS 2025 yearly average currency exchange rates; CMS Fiscal Year 2025 Improper Payments Fact Sheet. {html.escape(notes)}
    </div>
  </main>
</body>
</html>"""
    (OUT / "pharma_cms_2025_infographic.html").write_text(html_out, encoding="utf-8")

    audit_rows = []
    for r in rows:
        audit_rows.append(f"""
        <tr>
          <td>{r['rank']}</td><td>{html.escape(r['company'])}</td><td>{html.escape(r['ticker'])}</td>
          <td class="hl">{format_source_value(r['revenue_reported'], r['currency'])}</td>
          <td class="hl">{format_source_value(r['net_income_reported'], r['currency'])}</td>
          <td>{format_billions(r['net_income_usd'])}</td><td>{html.escape(r['rev_tag'])}<br>{html.escape(r['ni_tag'])}</td>
          <td><a href="{html.escape(r['source_url'])}">SEC filing</a></td>
        </tr>
        """)
    audit_html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Source Audit</title>
    <style>body{{font-family:Arial,sans-serif;background:#f6f1e8;color:#10120f;margin:28px}}h1{{font-size:44px;margin:0 0 18px}}table{{border-collapse:collapse;width:100%;background:#fffaf0}}td,th{{border:2px solid #10120f;padding:8px;font-size:14px;text-align:left}}th{{background:#10120f;color:#fffaf0}}.hl{{background:#d7ff5f;font-weight:900}}.note{{max-width:1000px;color:#5c6257;font-size:16px;line-height:1.35}}</style></head>
    <body><h1>Source audit: 2025 SEC facts used</h1><p class="note">{html.escape(notes)}</p><table><thead><tr><th>Rank</th><th>Company</th><th>Ticker</th><th>Revenue fact</th><th>Net income fact</th><th>Net income USD</th><th>XBRL tags</th><th>Source</th></tr></thead><tbody>{''.join(audit_rows)}</tbody></table></body></html>"""
    (OUT / "source_audit_table.html").write_text(audit_html, encoding="utf-8")


def main():
    rows = build_rows()
    write_outputs(rows)
    print(f"Wrote {len(rows)} rows")
    print(f"Net income total: ${sum(r['net_income_usd'] for r in rows) / 1_000_000_000:,.3f}B")
    print(f"CMS total: ${sum(v for _, v in CMS_PROGRAMS):,.3f}B")


if __name__ == "__main__":
    main()
