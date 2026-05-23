import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


BASE = Path("/Users/justinyu/Desktop/linkedin-posts/outputs/heor_vendor_ai_capabilities_2026")
RAW = BASE / "screenshots" / "highlighted_raw_ai_only"
OUT = BASE / "screenshots" / "highlighted_ai_only_tight"
DATA = BASE / "data"
PDF = BASE / "pdf"
REVIEW = BASE / "review"
SOURCE_JSON = DATA / "heor_vendor_ai_capabilities.json"
FINAL_JSON = DATA / "heor_vendor_ai_capabilities_tight_highlighted_ai_only.json"
FINAL_PDF = PDF / "heor_vendor_ai_capability_screenshots_tight_highlighted_ai_only.pdf"


ITEMS = [
    {
        "vendor": "IQVIA",
        "file": "02-iqvia-deploy-ready-to-use-or-configurable-ai-agents-designed-around-real-world-life-sc.png",
        "evidence_text": "Introducing IQVIA.ai: Your Agentic",
        "summary": "IQVIA.ai agentic AI offering.",
        "url": "https://www.iqvia.com/solutions/innovative-models/artificial-intelligence-and-machine-learning/iqvia-ai-platform",
        "line_boxes": [(163, 300, 790, 369), (163, 375, 550, 448)],
    },
    {
        "vendor": "Datavant",
        "file": "03-datavant-ai-powered-real-world-data-platform.png",
        "evidence_text": "AI-Powered Real-World Data Platform",
        "summary": "AI-powered real-world data platform.",
        "url": "https://www.datavant.com/press-release/labcorp-introduces-ai-powered-real-world-data-platform-with-aws-and-datavant-to-accelerate-alzheimers-research",
        "line_boxes": [(500, 199, 1298, 251)],
    },
    {
        "vendor": "OPEN Health",
        "file": "04-open-health-leverage-ai-technologies-for-evidence-synthesis.png",
        "evidence_text": "leverage AI technologies for evidence synthesis",
        "summary": "AI technologies for evidence synthesis.",
        "url": "https://www.openhealthgroup.com/news/07-12-2023/open-health-and-nested-knowledge-announce-strategic-research-collaboration-to-leverage-ai-technologies-for-evidence-synthesis/",
        "line_boxes": [(815, 461, 1000, 510), (326, 510, 881, 558), (328, 558, 514, 609)],
    },
    {
        "vendor": "Trinity Life Sciences",
        "file": "06-trinity-life-sciences-trinity-ai-provides-a-comprehensive-portfolio-of-data-science-applications.png",
        "evidence_text": "Increasing the Speed and Precision of Insights Through AI",
        "summary": "Trinity AI offering for insight speed and precision.",
        "url": "https://trinitylifesciences.com/services/analytics/trinity-ai/",
        "line_boxes": [(492, 194, 1038, 244), (647, 246, 867, 292)],
    },
    {
        "vendor": "Komodo Health",
        "file": "07-komodo-health-accelerate-research-studies-and-evidence-generation-using-advanced-technology-th.png",
        "evidence_text": "using advanced technology that harnesses AI",
        "summary": "Technology that harnesses AI.",
        "url": "https://www.komodohealth.com/maplab-for-heor-rwe/",
        "line_boxes": [(520, 516, 780, 543), (100, 548, 220, 575)],
    },
    {
        "vendor": "Oracle Health and Life Sciences",
        "file": "10-oracle-health-and-life-sciences-unify-and-analyze-real-world-and-research-data-at-scale-with-generative-ai.png",
        "evidence_text": "generative AI",
        "summary": "Generative AI for data intelligence.",
        "url": "https://www.oracle.com/life-sciences/data-intelligence/",
        "line_boxes": [(498, 239, 605, 266)],
    },
    {
        "vendor": "Nested Knowledge",
        "file": "11-nested-knowledge-ai-enabled-platform-for-systematic-literature-review-and-evidence-synthesis.png",
        "evidence_text": "AI-Enabled Literature Search and Evidence Synthesis",
        "summary": "AI-enabled literature search and evidence synthesis.",
        "url": "https://about.nested-knowledge.com/2026/04/21/nested-knowledge-and-elsevier-announce-partnership-to-advance-ai-enabled-literature-search-and-evidence-synthesis/",
        "line_boxes": [(352, 104, 1180, 147), (183, 150, 380, 203)],
    },
    {
        "vendor": "Keiji.AI",
        "file": "14-keiji-ai-keiji-ai-builds-specialized-ai-agents-that-accelerate-clinical-trials.png",
        "evidence_text": "Building AI for Clinical Research",
        "summary": "AI for clinical research.",
        "url": "https://keiji.ai/about",
        "line_boxes": [(630, 292, 878, 333), (635, 329, 873, 371)],
    },
    {
        "vendor": "nference",
        "file": "15-nference-an-ai-first-approach-to-transform-real-world-data-rwd-to-real-world-evidence-rwe.png",
        "evidence_text": "AI-first approach",
        "summary": "AI-first approach.",
        "url": "https://nference.com/nsights",
        "line_boxes": [(820, 628, 1165, 659), (330, 424, 980, 461)],
    },
    {
        "vendor": "MadeAi",
        "file": "17-madeai-empowering-heor-medical-affairs-market-access-and-rwe-professionals-in-life-scie.png",
        "evidence_text": "Trusted AI Platform for Life Sciences",
        "summary": "Trusted AI platform for life sciences.",
        "url": "https://madeai.com/",
        "line_boxes": [(467, 338, 728, 387), (105, 396, 720, 448)],
    },
    {
        "vendor": "Atropos Health",
        "file": "18-atropos-health-the-first-generative-ai-application-to-deliver-full-observational-studies-on-hea.png",
        "evidence_text": "The first generative AI application",
        "summary": "Generative AI application.",
        "url": "https://www.atroposhealth.com/chatrwd/",
        "line_boxes": [(145, 424, 705, 466)],
    },
]


DROPPED = [
    "Flatiron Health",
    "Panalgo",
    "Cytel",
    "TriNetX",
    "HealthVerity",
    "OM1",
    "Cencora/FormularyDecisions",
    "Elicit",
    "DistillerSR",
    "EasySLR",
    "Verantos",
]


def tight_highlight(image, boxes):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x1, y1, x2, y2 in boxes:
        pad_x = 3
        pad_y = 2
        draw.rounded_rectangle(
            (x1 - pad_x, y1 - pad_y, x2 + pad_x, y2 + pad_y),
            radius=2,
            fill=(255, 235, 59, 118),
        )
    return Image.alpha_composite(image, overlay).convert("RGB")


def build_images():
    OUT.mkdir(parents=True, exist_ok=True)
    rendered = []
    for item in ITEMS:
        src = RAW / item["file"]
        image = Image.open(src).convert("RGBA")
        dest = OUT / item["file"]
        tight_highlight(image, item["line_boxes"]).save(dest, quality=95)
        rendered.append({**item, "highlighted_screenshot": dest})
    return rendered


def build_json(items):
    source = json.loads(SOURCE_JSON.read_text())
    by_vendor = {v["vendor"]: v for v in source["vendors"]}
    vendors = []
    for item in items:
        original = by_vendor.get(item["vendor"], {"vendor": item["vendor"], "classification": "unknown", "source_basis": []})
        vendors.append(
            {
                **{k: v for k, v in original.items() if k != "ai_capabilities"},
                "direct_website_ai_capability_found": True,
                "ai_search_status": "found_on_vendor_site_tight_highlighted_ai_only",
                "ai_capabilities": [
                    {
                        "capability_summary": item["summary"],
                        "evidence_url": item["url"],
                        "evidence_text": item["evidence_text"],
                        "highlighted_screenshot": str(item["highlighted_screenshot"]),
                    }
                ],
            }
        )
    payload = {
        "metadata": {
            "created_date": "2026-05-14",
            "task_folder": str(BASE),
            "source_inventory": str(SOURCE_JSON),
            "vendors_with_tight_highlighted_ai_evidence": len(vendors),
            "screenshot_count": len(items),
            "dropped_from_prior_ai_list": DROPPED,
            "selection_rule": "Kept only screenshots where visible tightly highlighted text confirms an AI offering or AI-enabled capability.",
        },
        "vendors": vendors,
    }
    FINAL_JSON.write_text(json.dumps(payload, indent=2))
    return payload


def build_pdf(items):
    PDF.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(FINAL_PDF), pagesize=landscape(letter))
    page_w, page_h = landscape(letter)
    margin = 28
    for index, item in enumerate(items, start=1):
        img = Image.open(item["highlighted_screenshot"])
        c.setFont("Helvetica-Bold", 15)
        c.setFillColor(colors.black)
        c.drawString(margin, page_h - margin - 4, f"{index:02d}. {item['vendor']} - tight text highlight AI evidence")
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(margin, page_h - margin - 18, f"Highlighted text: {item['evidence_text'][:150]}")
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(margin, page_h - margin - 30, f"Source: {item['url'][:160]}")
        max_w = page_w - 2 * margin
        max_h = page_h - 92
        scale = min(max_w / img.width, max_h / img.height)
        draw_w = img.width * scale
        draw_h = img.height * scale
        c.drawImage(ImageReader(img), (page_w - draw_w) / 2, margin, draw_w, draw_h)
        c.showPage()
    c.save()


def contact_sheet(items):
    cols = 3
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 500, rows * 300), "white")
    draw = ImageDraw.Draw(sheet)
    for i, item in enumerate(items):
        im = Image.open(item["highlighted_screenshot"]).convert("RGB")
        im.thumbnail((480, 245))
        x = (i % cols) * 500
        y = (i // cols) * 300
        sheet.paste(im, (x, y + 35))
        draw.text((x, y), f"{item['vendor']}: {item['evidence_text'][:38]}", fill=(0, 0, 0))
    dest = REVIEW / "ai_only_tight_highlight_contact_sheet.jpg"
    sheet.save(dest, quality=92)
    return dest


def main():
    items = build_images()
    data = build_json(items)
    build_pdf(items)
    sheet = contact_sheet(items)
    print(
        json.dumps(
            {
                "json": str(FINAL_JSON),
                "pdf": str(FINAL_PDF),
                "contact_sheet": str(sheet),
                "vendors": data["metadata"]["vendors_with_tight_highlighted_ai_evidence"],
                "screenshots": data["metadata"]["screenshot_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
