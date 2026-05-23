#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path
from textwrap import shorten

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = ROOT
PDF_PATH = OUT_DIR / "ISPOR_2026_explicit_AI_offering_screenshots.pdf"
EVIDENCE_DIR = ROOT / "tmp" / "pdf_evidence_images"
Image.MAX_IMAGE_PIXELS = None


def load_rows():
    all_rows = json.loads((DATA / "explicit_ai_offering_candidates.json").read_text(encoding="utf-8"))
    by_id = {int(row["review_id"]): row for row in all_rows}
    accepted = set()
    review_paths = sorted((DATA / "classification_reviews").glob("accepted_part_*.json"))
    if review_paths:
        for path in review_paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            accepted.update(int(x) for x in data.get("accepted_review_ids", []))
    else:
        accepted.update(int(row["review_id"]) for row in all_rows if row.get("explicit_ai_offering"))
    rows = [by_id[rid] for rid in sorted(accepted) if rid in by_id]
    rows = [row for row in rows if row.get("screenshot") and Path(row["screenshot"]).exists()]
    return rows


def evidence_image(src_path, review_id):
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EVIDENCE_DIR / f"review_{review_id}.jpg"
    if out_path.exists():
        return str(out_path)

    with Image.open(src_path) as original:
        img = original.convert("RGB")
        width, height = img.size
        pixels = img.load()
        xs = []
        ys = []
        sample_x = max(1, width // 1200)
        sample_y = max(1, height // 1600)
        for y in range(0, height, sample_y):
            for x in range(0, width, sample_x):
                r, g, b = pixels[x, y]
                if r > 210 and g > 160 and b < 150:
                    xs.append(x)
                    ys.append(y)

        if xs and ys:
            y_sorted = sorted(ys)
            x_sorted = sorted(xs)
            y_center = y_sorted[len(y_sorted) // 2]
            x_center = x_sorted[len(x_sorted) // 2]
            y_span = max(ys) - min(ys)
            x_span = max(xs) - min(xs)
            crop_height = min(height, max(720, min(1300, y_span + 520)))
            crop_width = min(width, max(1050, min(1700, x_span + 760)))
            x1 = max(0, x_center - crop_width // 2)
            x2 = min(width, x1 + crop_width)
            x1 = max(0, x2 - crop_width)
            y1 = max(0, y_center - crop_height // 2)
            y2 = min(height, y1 + crop_height)
            y1 = max(0, y2 - crop_height)
            img = img.crop((x1, y1, x2, y2))
        else:
            img.thumbnail((2200, 1800), Image.Resampling.LANCZOS)

        if img.width > 2200 or img.height > 2200:
            img.thumbnail((2200, 2200), Image.Resampling.LANCZOS)
        img.save(out_path, "JPEG", quality=86, optimize=True)
    return str(out_path)


def image_flowable(path, max_width, max_height):
    with Image.open(path) as img:
        width, height = img.size
    scale = min(max_width / width, max_height / height)
    return RLImage(path, width=width * scale, height=height * scale)


def write_csv(rows):
    path = DATA / "explicit_ai_offerings_final.csv"
    fields = ["review_id", "display_name", "website", "page_title", "page_url", "screenshot", "highlight_count", "snippet"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: row.get(k, "") for k in fields} for row in rows])
    return path


def build_pdf(rows):
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=landscape(letter),
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch,
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontSize=7.5,
            leading=9,
            textColor=colors.HexColor("#333333"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Url",
            parent=styles["BodyText"],
            fontSize=7,
            leading=8,
            textColor=colors.HexColor("#23527c"),
            wordWrap="CJK",
        )
    )
    story = []
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["display_name"]].append(row)

    story.append(Paragraph("ISPOR 2026 Exhibitors - Explicit AI Offering Screenshots", styles["Title"]))
    story.append(Spacer(1, 0.08 * inch))
    story.append(
        Paragraph(
            f"{len(rows)} screenshots across {len(grouped)} companies. Included pages explicitly show an AI product, offering, platform, solution, tool, feature, service, case study, or demo. Generic AI thought leadership, author pages, careers pages, and related-content/sidebar-only matches were excluded.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.18 * inch))
    toc_data = [["Company", "Screenshots"]]
    for company in sorted(grouped):
        toc_data.append([company, str(len(grouped[company]))])
    toc = Table(toc_data, colWidths=[6.5 * inch, 1.2 * inch])
    toc.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d0d0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(toc)
    story.append(PageBreak())

    max_image_width = 9.9 * inch
    max_image_height = 5.3 * inch
    for company in sorted(grouped):
        company_rows = sorted(grouped[company], key=lambda r: (r.get("page_title", ""), r.get("page_url", "")))
        for idx, row in enumerate(company_rows, start=1):
            story.append(Paragraph(company, styles["Heading2"]))
            story.append(Paragraph(shorten(row.get("page_title", "") or row.get("page_url", ""), width=150, placeholder="..."), styles["Heading4"]))
            story.append(Paragraph(row.get("page_url", ""), styles["Url"]))
            story.append(Paragraph(f"Screenshot {idx} of {len(company_rows)} for this company | Review ID {row.get('review_id')} | Highlight count {row.get('highlight_count')}", styles["Small"]))
            story.append(Spacer(1, 0.08 * inch))
            evidence_path = evidence_image(row["screenshot"], row.get("review_id"))
            story.append(image_flowable(evidence_path, max_image_width, max_image_height))
            if row.get("snippet"):
                story.append(Spacer(1, 0.06 * inch))
                story.append(Paragraph(shorten(row["snippet"].replace("\n", " "), width=330, placeholder="..."), styles["Small"]))
            story.append(PageBreak())
    doc.build(story)


def main():
    rows = load_rows()
    csv_path = write_csv(rows)
    build_pdf(rows)
    print(f"rows={len(rows)}")
    print(csv_path)
    print(PDF_PATH)


if __name__ == "__main__":
    main()
