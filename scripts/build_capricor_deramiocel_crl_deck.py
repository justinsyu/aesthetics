#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import subprocess
import urllib.request
from pathlib import Path

import fitz
from PIL import Image, ImageDraw


ROOT = Path("competitive_intelligence_reports/duchenne_muscular_dystrophy/capricor_deramiocel_crl_2026").resolve()
SOURCES = ROOT / "sources"
RAW = ROOT / "screenshots" / "raw"
EVIDENCE = ROOT / "screenshots" / "evidence"
VIEWS = ROOT / "sources" / "pdf-evidence-views"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
INTER_REGULAR = Path(r"C:\Users\Justin\AppData\Local\Microsoft\Windows\Fonts\Inter-Variable.ttf")
INTER_ITALIC = Path(r"C:\Users\Justin\AppData\Local\Microsoft\Windows\Fonts\Inter-Italic-Variable.ttf")

for directory in [SOURCES, RAW, EVIDENCE, VIEWS]:
    directory.mkdir(parents=True, exist_ok=True)


SOURCES_DATA = [
    {
        "id": "S1",
        "label": "FDA CRL, clinical efficacy deficiency",
        "url": "https://download.open.fda.gov/crl/CRL_BLA125842_20250709.pdf",
        "file": "source-01-fda-crl-clinical.png",
        "kind": "pdf",
        "pdf_page": 1,
        "box": (55, 365, 1180, 1345),
        "crop": (345, 255, 1280, 1045),
        "caption": "FDA CRL page 1: HOPE-2 failed prespecified endpoints; cardiomyopathy case relied on post hoc analyses.",
    },
    {
        "id": "S2",
        "label": "FDA CRL, multiplicity and randomized-control recommendation",
        "url": "https://download.open.fda.gov/crl/CRL_BLA125842_20250709.pdf",
        "file": "source-02-fda-crl-statistics.png",
        "kind": "pdf",
        "pdf_page": 2,
        "box": (55, 75, 1180, 1030),
        "crop": (380, 85, 1215, 700),
        "caption": "FDA CRL page 2: 50 exploratory endpoints, no multiplicity strategy, and OLE confounding.",
    },
    {
        "id": "S3",
        "label": "Capricor July 2025 CRL announcement",
        "url": "https://www.capricor.com/investors/news-events/press-releases/detail/319/capricor-therapeutics-provides-regulatory-update-on",
        "file": "source-03-capricor-crl.png",
        "raw": "source-03-capricor-crl-raw.png",
        "box": (210, 625, 1360, 1185),
        "caption": "Capricor announcement: CRL, substantial-evidence issue, additional clinical data, and HOPE-2/OLE/natural-history support.",
    },
    {
        "id": "S4",
        "label": "Capricor September 2025 Type A meeting update",
        "url": "https://www.capricor.com/investors/news-events/press-releases/detail/326/capricor-therapeutics-provides-regulatory-update-on",
        "file": "source-04-capricor-typea.png",
        "raw": "source-04-capricor-typea-raw.png",
        "box": (210, 625, 1395, 1190),
        "caption": "Capricor Type A update: FDA aligned that HOPE-3 could serve as the additional study and define endpoints.",
    },
    {
        "id": "S5",
        "label": "FDA Multiple Endpoints guidance",
        "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/multiple-endpoints-clinical-trials",
        "file": "source-05-fda-multiple-endpoints.png",
        "raw": "source-05-fda-multiple-endpoints-raw.png",
        "box": (430, 560, 1185, 995),
        "caption": "FDA guidance: multiple endpoints increase false-conclusion risk without multiplicity adjustment.",
    },
    {
        "id": "S6",
        "label": "FDA NurOwn ALS update",
        "url": "https://www.fda.gov/vaccines-blood-biologics/cellular-gene-therapy-products/update-amyotrophic-lateral-sclerosis-als-product-development",
        "file": "source-06-fda-nurown.png",
        "raw": "source-06-fda-nurown-raw.png",
        "box": (435, 290, 1165, 925),
        "caption": "FDA NurOwn update: none of the randomized primary or secondary endpoints were met.",
    },
    {
        "id": "S7",
        "label": "BioMarin Kyndrisa DMD CRL",
        "url": "https://www.biomarin.com/news/press-releases/fda-issues-complete-response-letter-for-kyndrisatm-for-duchenne-muscular-dystrophy-amenable-to-exon-51-skipping/",
        "file": "source-07-biomarin-drisapersen.png",
        "raw": "source-07-biomarin-drisapersen-raw.png",
        "box": (195, 395, 1435, 690),
        "caption": "BioMarin DMD precedent: FDA issued a CRL and concluded substantial evidence had not been met.",
    },
]

SOURCE_BY_ID = {source["id"]: source for source in SOURCES_DATA}


def download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 10_000:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        path.write_bytes(response.read())


def draw_box(image_path: Path, output_path: Path, box: tuple[int, int, int, int]) -> None:
    im = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(im, "RGBA")
    x1, y1, x2, y2 = box
    draw.rectangle([x1, y1, x2, y2], outline=(220, 55, 45, 255), width=8)
    draw.rectangle([x1, y1, x2, y2], fill=(255, 230, 0, 38))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(output_path)


def crop_image(image_path: Path, output_path: Path, crop: tuple[int, int, int, int]) -> None:
    im = Image.open(image_path).convert("RGB")
    im.crop(crop).save(output_path)


def render_pdf_page(pdf: Path, page_number: int, output_path: Path, box: tuple[int, int, int, int]) -> None:
    doc = fitz.open(pdf)
    page = doc[page_number - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    base = output_path.with_name(output_path.stem + "-page.png")
    pix.save(base)
    draw_box(base, output_path, box)


def build_pdf_evidence_views() -> None:
    pdf = SOURCES / "CRL_BLA125842_20250709.pdf"
    download("https://download.open.fda.gov/crl/CRL_BLA125842_20250709.pdf", pdf)
    for source in SOURCES_DATA:
        if source.get("kind") != "pdf":
            continue
        image = VIEWS / (Path(source["file"]).stem + "-annotated-page.png")
        render_pdf_page(pdf, source["pdf_page"], image, source["box"])
        html_path = VIEWS / (Path(source["file"]).stem + ".html")
        html_path.write_text(
            f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(source['label'])}</title>
<style>
@font-face {{ font-family: 'Inter'; src: url('{INTER_REGULAR.resolve().as_uri()}') format('truetype'); font-weight: 100 900; font-style: normal; }}
body {{ margin: 0; background: #e7e5dd; font-family: 'Inter'; }}
.page {{ width: 1600px; min-height: 1200px; display: grid; place-items: center; padding: 28px; box-sizing: border-box; }}
.sheet {{ background: white; box-shadow: 0 8px 24px rgba(0,0,0,.18); padding: 12px; }}
img {{ display: block; max-height: 1130px; max-width: 1510px; }}
.label {{ position: fixed; left: 28px; bottom: 18px; background: rgba(255,255,255,.94); border: 2px solid #c83a32; padding: 8px 12px; font-size: 18px; color: #241b16; }}
</style></head><body><div class="page"><div class="sheet"><img src="{image.name}" alt="{html.escape(source['label'])}"></div></div><div class="label">{html.escape(source['caption'])}</div></body></html>""",
            encoding="utf-8",
        )
        raw_out = RAW / source["file"].replace(".png", "-raw.png")
        subprocess.run(
            [
                str(CHROME),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1600,1200",
                f"--screenshot={raw_out}",
                pathToFileURL(html_path),
            ],
            check=True,
        )
        raw_out.replace(RAW / source["file"])


def pathToFileURL(path: Path) -> str:
    return path.resolve().as_uri()


def annotate_web_sources() -> None:
    for source in SOURCES_DATA:
        if source.get("kind") == "pdf":
            # PDF evidence views are already captured with the bounding box visible.
            continue
        draw_box(RAW / source["raw"], EVIDENCE / source["file"], source["box"])


def copy_pdf_evidence() -> None:
    for source in SOURCES_DATA:
        if source.get("kind") == "pdf":
            raw = RAW / source["file"]
            if "crop" in source:
                crop_image(raw, EVIDENCE / source["file"], source["crop"])
            else:
                (EVIDENCE / source["file"]).write_bytes(raw.read_bytes())


def write_source_files() -> None:
    manifest = ROOT / "sources" / "reference-screenshots.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["label", "path", "caption"])
        writer.writeheader()
        for source in SOURCES_DATA:
            writer.writerow(
                {
                    "label": f"{source['id']} - {source['label']}",
                    "path": str((EVIDENCE / source["file"]).resolve()),
                    "caption": f"{source['caption']} Source: {source['url']}",
                }
            )

    log_lines = ["# Source Log", ""]
    for source in SOURCES_DATA:
        log_lines.extend(
            [
                f"## {source['id']} - {source['label']}",
                f"- URL: {source['url']}",
                f"- Screenshot: {EVIDENCE / source['file']}",
                f"- Evidence note: {source['caption']}",
                "",
            ]
        )
    (ROOT / "sources" / "source-log.md").write_text("\n".join(log_lines), encoding="utf-8")

    (ROOT / "sources" / "run-manifest.json").write_text(
        json.dumps(
            {
                "topic": "Capricor deramiocel CRL in DMD cardiomyopathy",
                "scope": "Historical regulatory precedent analysis; not limited to last 7 days.",
                "screenshot_method": "Webpages captured in Chrome; FDA CRL PDF pages rendered from the source PDF into browser-view evidence pages and captured in Chrome.",
                "sources": SOURCES_DATA,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def cite(*ids: str) -> str:
    links = " ".join(
        f'<a class="cite" href="{html.escape(SOURCE_BY_ID[source_id]["url"])}">[{source_id}]</a>'
        for source_id in ids
    )
    return f'<span class="cites">{links}</span>'


def slide(title: str, eyebrow: str, body: str, image: str | None = None, foot: str = "", proof_class: str = "") -> str:
    image_html = f'<div class="proof {proof_class}"><img src="screenshots/evidence/{image}" alt=""></div>' if image else ""
    return f"""<section class="slide">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{title}</h1>
  <div class="grid">
    <div class="copy">{body}</div>
    {image_html}
  </div>
  <div class="foot">{foot}</div>
</section>"""


def bullet(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def write_deck() -> None:
    inter_regular_url = INTER_REGULAR.resolve().as_uri()
    inter_italic_url = INTER_ITALIC.resolve().as_uri()
    slides = [
        f"""<section class="slide cover">
  <div class="eyebrow">Competitive intelligence regulatory review</div>
  <h1>Deramiocel CRL: evidence basis and relevant precedents</h1>
  <p class="dek">FDA's July 9, 2025 complete response letter identified deficiencies related to substantial evidence for a DMD cardiomyopathy claim: failed prespecified HOPE-2 endpoints, exploratory cardiac analyses, no multiplicity strategy, and a nonrandomized OLE. {cite("S1", "S2")}</p>
  <div class="cards">
    <div><b>Product</b><span>Deramiocel / CAP-1002</span></div>
    <div><b>Application</b><span>BLA 125842</span></div>
    <div><b>CRL date</b><span>July 9, 2025</span></div>
  </div>
</section>""",
        slide(
            "FDA identified deficiencies in the evidence supporting the proposed indication",
            "CRL finding",
            bullet(
                [
                    f"HOPE-2 and HOPE-2-OLE were submitted as the primary and supportive evidence base. {cite('S1')}",
                    f"FDA stated HOPE-2 failed the prespecified primary endpoint and prespecified secondary endpoints. {cite('S1')}",
                    f"The cardiomyopathy evidence relied on post hoc analyses rather than a trial designed to assess DMD cardiomyopathy. {cite('S1')}",
                ]
            ),
            "source-01-fda-crl-clinical.png",
            f"{cite('S1')} FDA CRL, BLA 125842, July 9, 2025.",
            "proof-wide",
        ),
        slide(
            "FDA's statistical concerns were specific",
            "CRL finding",
            bullet(
                [
                    f"FDA identified 50 secondary/exploratory endpoints, including 26 cardiac MRI endpoints. {cite('S2')}",
                    f"No prespecified hypothesis testing or multiplicity adjustment strategy controlled Type I error. {cite('S2')}",
                    f"FDA identified exploratory analyses and the nonrandomized OLE as insufficient to establish effectiveness. {cite('S2')}",
                ]
            ),
            "source-02-fda-crl-statistics.png",
            f"{cite('S2')} FDA CRL, BLA 125842, July 9, 2025.",
            "proof-wide",
        ),
        slide(
            "Capricor's public framing described the stated evidence deficiency",
            "Company disclosure",
            bullet(
                [
                    f"Capricor said FDA cited lack of substantial evidence and need for additional clinical data. {cite('S3')}",
                    f"The company disclosed the package relied on HOPE-2, HOPE-2-OLE, and natural-history comparisons. {cite('S3')}",
                    f"CMC items were referenced, but public detail is redacted; the clinical evidence issue is the most clearly identifiable regulatory risk from public sources. {cite('S1', 'S3')}",
                ]
            ),
            "source-03-capricor-crl.png",
            f"{cite('S3')} Capricor press release, July 11, 2025.",
        ),
        slide(
            "The post-CRL update described the evidence path",
            "Type A meeting",
            bullet(
                [
                    f"After the Type A meeting, Capricor said FDA aligned that HOPE-3 could serve as the additional study. {cite('S4')}",
                    f"The updated path preserved PUL v2.0 as primary and put LVEF forward as a key secondary endpoint. {cite('S4')}",
                    f"That sequencing supports the conclusion that prospective controlled evidence was a key deficiency identified during review. {cite('S2', 'S4')}",
                ]
            ),
            "source-04-capricor-typea.png",
            f"{cite('S4')} Capricor press release, September 25, 2025.",
        ),
        slide(
            "FDA guidance described multiplicity risks relevant to the CRL",
            "Regulatory learning",
            bullet(
                [
                    f"FDA's endpoints guidance states that false conclusions become a concern as endpoint counts rise without multiplicity adjustment. {cite('S5')}",
                    f"The deramiocel CRL used the same logic: exploratory endpoints and nominal signals were not considered sufficient to establish effectiveness. {cite('S2')}",
                    f"Implication: pre-specify the cardiac estimand, hierarchy, and multiplicity plan before filing for a cardiac label. {cite('S2', 'S5')}",
                ]
            ),
            "source-05-fda-multiple-endpoints.png",
            f"{cite('S5')} FDA Multiple Endpoints guidance page, content current April 16, 2024.",
        ),
        slide(
            "NurOwn indicates that unmet need does not substitute for successful randomized endpoints",
            "Analog precedent",
            bullet(
                [
                    f"FDA publicly said NurOwn data did not support proposed clinical benefit after a randomized Phase 3 trial. {cite('S6')}",
                    f"None of the randomized primary or secondary endpoints were met, despite high public interest in ALS. {cite('S6')}",
                    f"Implication: patient urgency and biologic plausibility do not make exploratory or post hoc findings sufficient to establish substantial evidence. {cite('S6')}",
                ]
            ),
            "source-06-fda-nurown.png",
            f"{cite('S6')} FDA ALS/NurOwn update, March 2, 2021.",
        ),
        slide(
            "DMD-specific precedent had described the substantial-evidence standard",
            "Analog precedent",
            bullet(
                [
                    f"BioMarin's drisapersen CRL in DMD stated the application was not ready for approval in its present form. {cite('S7')}",
                    f"The company disclosed FDA concluded substantial evidence of effectiveness had not been met. {cite('S7')}",
                    f"Implication: DMD regulatory flexibility did not remove the need for adequate evidence tied to the proposed claim. {cite('S7')}",
                ]
            ),
            "source-07-biomarin-drisapersen.png",
            f"{cite('S7')} BioMarin press release, January 14, 2016.",
        ),
        f"""<section class="slide conclusion">
  <div class="eyebrow">Synthesis</div>
  <h1>Was the CRL risk reasonably foreseeable?</h1>
  <div class="takeaway">
    <b>Available evidence suggests the CRL risk was reasonably foreseeable at the submission-strategy level.</b>
    <p>The precise FDA timing may have been uncertain, but the central objection was identifiable from the submitted evidence structure and prior FDA guidance: a cardiomyopathy indication needed prospectively defined, controlled evidence for cardiac benefit, not retrospective cardiac analyses derived from a neuromuscular trial that missed prespecified endpoints. {cite("S1", "S2", "S5")}</p>
  </div>
  <div class="two">
    <div>{bullet([f"Pre-submission risk factor: reliance on post hoc cardiac endpoints without a controlled Type I error plan. {cite('S2', 'S5')}", f"Pre-submission risk factor: use of nonrandomized OLE/natural-history comparisons as supportive evidence for a label-defining claim. {cite('S1', 'S2')}", f"Less knowable from public sources: redacted CMC specifics. {cite('S1', 'S3')}"])}</div>
    <div>{bullet([f"Practical implication: align the proposed label with the trial objective, estimand, endpoint hierarchy, and control group. {cite('S2', 'S5')}", f"For cell therapies, CMC/potency readiness remains important, but the public record identifies the clinical-evidence deficiency as central. {cite('S1', 'S3')}", f"The post-CRL HOPE-3 path supports the need for prospective controlled data. {cite('S4')}"])}</div>
  </div>
  <div class="foot">Sources: S1-S7.</div>
</section>""",
        f"""<section class="slide references">
  <div class="eyebrow">References</div>
  <h1>Source List</h1>
  <ol>
    {''.join(f'<li><a href="{html.escape(source["url"])}">{html.escape(source["label"])}</a></li>' for source in SOURCES_DATA)}
  </ol>
</section>""",
    ]

    font_css = f"""
@font-face {{ font-family: 'Inter'; src: url('{inter_regular_url}') format('truetype'); font-weight: 100 900; font-style: normal; }}
@font-face {{ font-family: 'Inter'; src: url('{inter_italic_url}') format('truetype'); font-weight: 100 900; font-style: italic; }}
"""
    css = font_css + """
@page { size: 1600px 900px; margin: 0; }
* { box-sizing: border-box; }
html, body, button, input, textarea, select, svg, .slide, .slide * { font-family: 'Inter'; }
body { margin: 0; background: #e7e2d6; color: #231b16; font-family: 'Inter'; }
.slide { position: relative; width: 1600px; height: 900px; padding: 58px 70px 46px; page-break-after: always; overflow: hidden; background: #f4efe4; border-top: 14px solid #131313; }
.slide::after { content: ""; position: absolute; inset: 14px 0 auto 0; height: 4px; background: linear-gradient(90deg,#d62f2f,#f2c94c,#147a7e); }
.eyebrow { text-transform: uppercase; letter-spacing: .08em; font-size: 18px; font-weight: 800; color: #b5302b; margin-bottom: 20px; }
h1 { margin: 0 0 28px; font-size: 48px; line-height: 1.05; max-width: 1280px; font-weight: 800; }
.cover h1 { font-size: 68px; max-width: 1320px; }
.dek { font-size: 29px; line-height: 1.32; max-width: 1260px; margin: 0 0 44px; }
.grid { display: grid; grid-template-columns: 560px 1fr; gap: 42px; align-items: start; }
.copy { font-size: 25px; line-height: 1.28; }
ul { margin: 0; padding-left: 27px; }
li { margin-bottom: 20px; }
.proof { height: 575px; border: 2px solid #2a211c; background: #fff; box-shadow: 8px 8px 0 #d8cdb9; overflow: hidden; display: flex; align-items: flex-start; justify-content: center; }
.proof img { width: 100%; height: 100%; object-fit: cover; object-position: top center; display: block; }
.proof-wide img { object-fit: contain; object-position: center center; background: #fff; }
.foot { position: absolute; left: 70px; right: 70px; bottom: 24px; font-size: 17px; color: #5d5248; border-top: 1px solid #cfc2ac; padding-top: 10px; }
.cards { display: flex; gap: 18px; margin-top: 30px; }
.cards div { border: 2px solid #231b16; background: #fffdf5; padding: 22px 26px; min-width: 260px; box-shadow: 6px 6px 0 #d8cdb9; }
.cards b { display: block; font-size: 18px; text-transform: uppercase; color: #b5302b; margin-bottom: 10px; font-weight: 500; }
.cards span { font-size: 28px; font-weight: 400; }
.scope { position: absolute; left: 70px; right: 70px; bottom: 42px; font-size: 21px; color: #5d5248; }
.takeaway { background: #fffdf5; border: 3px solid #231b16; padding: 30px; max-width: 1320px; font-size: 31px; line-height: 1.25; box-shadow: 9px 9px 0 #d8cdb9; }
.takeaway b { display: block; color: #b5302b; margin-bottom: 12px; }
.takeaway p { margin: 0; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 34px; margin-top: 38px; font-size: 24px; line-height: 1.25; }
.conclusion .takeaway { font-size: 28px; padding: 24px 28px; }
.conclusion .two { font-size: 21px; line-height: 1.22; margin-top: 26px; }
.conclusion li { margin-bottom: 12px; }
.references ol { font-size: 24px; line-height: 1.35; max-width: 1350px; }
.references li { margin-bottom: 16px; }
a { color: #0b5b8c; }
.cite { font-weight: 650; text-decoration: underline; color: #0b5b8c; }
.cites { white-space: nowrap; }
"""
    html_doc = f"<!doctype html><html><head><meta charset='utf-8'><title>Capricor Deramiocel CRL Deck</title><style>{css}</style></head><body>{''.join(slides)}</body></html>"
    (ROOT / "report.html").write_text(html_doc, encoding="utf-8")


def main() -> None:
    build_pdf_evidence_views()
    annotate_web_sources()
    copy_pdf_evidence()
    write_source_files()
    write_deck()
    print(ROOT)


if __name__ == "__main__":
    main()
