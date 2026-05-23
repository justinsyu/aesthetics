import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


BASE = Path("/Users/justinyu/Desktop/linkedin-posts/outputs/heor_vendor_ai_capabilities_2026")
RAW = BASE / "screenshots" / "raw"
BOXED = BASE / "screenshots" / "boxed"
DATA = BASE / "data"
PDF = BASE / "pdf"
REVIEW = BASE / "review"

CANDIDATES = REVIEW / "vendor_candidate_research.json"
CAPTURE_MANIFEST = DATA / "evidence_capture_manifest.json"
FINAL_JSON = DATA / "heor_vendor_ai_capabilities.json"
FINAL_PDF = PDF / "heor_vendor_ai_capability_screenshots.pdf"


URL_FIXES = {
    "Trinity Life Sciences": {
        "url": "https://trinitylifesciences.com/services/analytics/trinity-ai/",
        "phrase": "Trinity AI provides a comprehensive portfolio of data science applications",
        "summary": (
            "Trinity AI combines AI/ML, GenAI, analytics, and life-sciences expertise for "
            "decision intelligence, patient finding, market research, insights synthesis, and workflow efficiency."
        ),
    }
}


EXTRA_VENDOR_RECORDS = [
    {
        "vendor": "MadeAi",
        "classification": "minor",
        "source_basis": ["ispor_exhibitor_2026", "general_knowledge"],
        "sheet_counts": {"consulting_rows": 0, "all_attendee_rows": 0},
        "exhibitor_evidence": [
            {
                "source": "ispor_exhibitor_2026",
                "url": "https://n1b.goexposoftware.com/events/ispor26/goExpo/exhibitor/listExhibitorProfiles.php",
                "exhibitor_name": "MadeAi",
                "booth": "641",
            }
        ],
        "rationale": "ISPOR 2026 exhibitor and AI-native evidence synthesis platform for HEOR/RWE workflows.",
        "notes": "Added during AI capability evidence pass.",
    },
    {
        "vendor": "Atropos Health",
        "classification": "major",
        "source_basis": ["general_knowledge"],
        "sheet_counts": {"consulting_rows": 0, "all_attendee_rows": 0},
        "exhibitor_evidence": [],
        "rationale": "Recognized RWE vendor with Green Button and ChatRWD evidence-generation products.",
        "notes": "Added during AI capability evidence pass because it is a major AI/RWE vendor even though not found in the attendee/exhibitor backbone.",
    },
]


ALIASES = {
    "Cencora": "Cencora/FormularyDecisions",
    "Flatiron": "Flatiron Health",
    "Oracle Health and Life Sciences": "Oracle Health and Life Sciences",
}


BOXES = {
    1: [(80, 250, 800, 530), (1020, 440, 1260, 530)],
    2: [(365, 35, 1120, 135)],
    3: [(40, 150, 690, 330), (885, 300, 1065, 430)],
    4: [(55, 70, 870, 435)],
    5: [(170, 230, 1340, 470), (170, 500, 930, 610)],
    6: [(430, 300, 955, 420)],
    7: [(60, 260, 1360, 515)],
    8: [(300, 55, 1365, 505)],
    9: [(0, 160, 650, 285)],
    10: [(25, 170, 640, 390)],
    11: [(0, 65, 1030, 300)],
    12: [(95, 300, 1320, 535)],
    13: [(0, 115, 460, 360), (430, 300, 1240, 500)],
    14: [(300, 185, 920, 340)],
    15: [(170, 55, 1280, 170), (120, 600, 1350, 710)],
    16: [(85, 190, 760, 515)],
    17: [(0, 340, 765, 655)],
    18: [(475, 140, 1060, 465)],
    19: [(300, 150, 1220, 500)],
    20: [(60, 140, 980, 330)],
    21: [(0, 85, 1350, 500)],
    22: [(300, 170, 1120, 600)],
    23: [(300, 145, 1030, 325)],
    24: [(60, 260, 1260, 405), (60, 610, 1410, 735)],
}


def ensure_dirs():
    for path in [BOXED, DATA, PDF, REVIEW]:
        path.mkdir(parents=True, exist_ok=True)


def load_inputs():
    candidates = json.loads(CANDIDATES.read_text())
    manifest = json.loads(CAPTURE_MANIFEST.read_text())
    return candidates, manifest


def normalize_vendor(name):
    return ALIASES.get(name, name)


def draw_boxes(manifest):
    outputs = []
    for item in manifest:
        raw = Path(item["raw_screenshot"])
        if not raw.exists():
            continue
        image = Image.open(raw).convert("RGB")
        draw = ImageDraw.Draw(image)
        for box in BOXES.get(item["index"], [(60, 120, image.width - 60, min(image.height - 80, 420))]):
            draw.rectangle(box, outline=(255, 0, 0), width=8)
        out = BOXED / raw.name
        image.save(out, quality=95)
        item["boxed_screenshot"] = str(out)
        outputs.append(out)
    return outputs


def build_vendor_json(candidates, manifest):
    records = list(candidates["vendor_candidates"])
    existing = {r["vendor"].lower(): r for r in records}
    for extra in EXTRA_VENDOR_RECORDS:
        if extra["vendor"].lower() not in existing:
            records.append(extra)
            existing[extra["vendor"].lower()] = extra

    capabilities = defaultdict(list)
    for item in manifest:
        vendor = normalize_vendor(item["vendor"])
        fixed = URL_FIXES.get(item["vendor"], {})
        cap = {
            "capability_summary": fixed.get("summary", item["summary"]),
            "evidence_url": fixed.get("url", item["url"]),
            "evidence_page_title": item.get("title", ""),
            "evidence_text": fixed.get("phrase", item["phrase"]),
            "raw_screenshot": item["raw_screenshot"],
            "boxed_screenshot": item.get("boxed_screenshot"),
        }
        capabilities[vendor].append(cap)

    final_records = []
    for rec in records:
        vendor = rec["vendor"]
        caps = capabilities.get(vendor, [])
        final_records.append(
            {
                **rec,
                "direct_website_ai_capability_found": bool(caps),
                "ai_search_status": "found_on_vendor_site" if caps else "no_direct_ai_capability_found_in_reviewed_sources",
                "ai_capabilities": caps,
            }
        )

    out = {
        "metadata": {
            **candidates.get("metadata", {}),
            "task_folder": str(BASE),
            "vendor_count": len(final_records),
            "vendors_with_direct_ai_capabilities": sum(1 for r in final_records if r["direct_website_ai_capability_found"]),
            "evidence_screenshot_count": sum(len(r["ai_capabilities"]) for r in final_records),
            "notes": [
                "Vendor backbone was built from the attendee workbook Affiliation/Affiliation short name columns, official ISPOR 2026 exhibitor directory, AMCP 2026 materials, and HEOR market knowledge.",
                "AI capabilities were recorded only where a direct vendor website page was identified and captured in Chrome.",
                "Vendors without direct AI evidence remain in the JSON with an empty ai_capabilities list.",
            ],
        },
        "primary_sources": candidates.get("primary_sources", []),
        "vendors": final_records,
    }
    FINAL_JSON.write_text(json.dumps(out, indent=2))
    return out


def build_pdf(manifest):
    c = canvas.Canvas(str(FINAL_PDF), pagesize=landscape(letter))
    page_w, page_h = landscape(letter)
    margin = 28
    for item in manifest:
        img_path = Path(item.get("boxed_screenshot", item["raw_screenshot"]))
        if not img_path.exists():
            continue
        title = f"{item['index']:02d}. {item['vendor']} - AI capability evidence"
        source = URL_FIXES.get(item["vendor"], {}).get("url", item["url"])
        phrase = URL_FIXES.get(item["vendor"], {}).get("phrase", item["phrase"])

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(margin, page_h - margin - 4, title)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(margin, page_h - margin - 18, f"Evidence text: {phrase[:150]}")
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(margin, page_h - margin - 30, f"Source: {source[:160]}")

        img = Image.open(img_path)
        max_w = page_w - 2 * margin
        max_h = page_h - 92
        scale = min(max_w / img.width, max_h / img.height)
        draw_w = img.width * scale
        draw_h = img.height * scale
        x = (page_w - draw_w) / 2
        y = margin
        c.drawImage(ImageReader(img), x, y, draw_w, draw_h)
        c.showPage()
    c.save()


def build_contact_sheet():
    imgs = sorted([p for p in BOXED.glob("*.png") if p.name[:2].isdigit()])
    thumb_w, thumb_h = 360, 183
    cols = 4
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 380, rows * 230), "white")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(imgs):
        im = Image.open(path).convert("RGB")
        im.thumbnail((thumb_w, thumb_h))
        x = (i % cols) * 380
        y = (i // cols) * 230
        sheet.paste(im, (x, y + 30))
        draw.text((x, y), path.name[:46], fill=(0, 0, 0))
    out = REVIEW / "boxed_contact_sheet.jpg"
    sheet.save(out, quality=92)
    return out


def main():
    ensure_dirs()
    candidates, manifest = load_inputs()
    for item in manifest:
        if item["vendor"] in URL_FIXES:
            item.update(URL_FIXES[item["vendor"]])
    draw_boxes(manifest)
    result = build_vendor_json(candidates, manifest)
    build_pdf(manifest)
    contact = build_contact_sheet()
    print(json.dumps({
        "final_json": str(FINAL_JSON),
        "final_pdf": str(FINAL_PDF),
        "boxed_contact_sheet": str(contact),
        "vendor_count": result["metadata"]["vendor_count"],
        "vendors_with_ai": result["metadata"]["vendors_with_direct_ai_capabilities"],
    }, indent=2))


if __name__ == "__main__":
    main()
