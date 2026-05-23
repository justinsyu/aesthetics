#!/usr/bin/env python3
"""Assemble labeled screenshot images into a single PDF."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 36
HEADER_HEIGHT = 54
FOOTER_HEIGHT = 24


@dataclass(frozen=True)
class Item:
    label: str
    path: Path
    caption: str = ""


def parse_item(value: str) -> Item:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--item values must use LABEL=/path/to/image")
    label, raw_path = value.split("=", 1)
    label = label.strip()
    raw_path = raw_path.strip()
    if not label or not raw_path:
        raise argparse.ArgumentTypeError("--item values must include both label and path")
    return Item(label=label, path=Path(raw_path).expanduser())


def read_manifest(path: Path) -> list[Item]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"label", "path"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Manifest is missing required column(s): {names}")

        items = []
        for row_number, row in enumerate(reader, start=2):
            label = (row.get("label") or "").strip()
            raw_path = (row.get("path") or "").strip()
            caption = (row.get("caption") or "").strip()
            if not label or not raw_path:
                raise ValueError(f"Manifest row {row_number} must include label and path")
            items.append(Item(label=label, path=Path(raw_path).expanduser(), caption=caption))
        return items


def validate_items(items: list[Item]) -> None:
    if not items:
        raise ValueError("No screenshots were provided")
    for item in items:
        if not item.path.exists():
            raise FileNotFoundError(f"Screenshot not found: {item.path}")
        if item.path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            raise ValueError(f"Unsupported image type for {item.path}; use PNG or JPEG")


def draw_wrapped_text(pdf: canvas.Canvas, text: str, x: float, y: float, width: float, size: int) -> float:
    pdf.setFont("Helvetica", size)
    words = text.split()
    line = ""
    line_height = size + 3
    for word in words:
        candidate = f"{line} {word}".strip()
        if pdf.stringWidth(candidate, "Helvetica", size) <= width:
            line = candidate
            continue
        if line:
            pdf.drawString(x, y, line)
            y -= line_height
        line = word
    if line:
        pdf.drawString(x, y, line)
        y -= line_height
    return y


def add_page(pdf: canvas.Canvas, item: Item, page_number: int, total_pages: int) -> None:
    image = Image.open(item.path)
    image = ImageOps.exif_transpose(image).convert("RGB")
    image_reader = ImageReader(image)

    pdf.setFillColor(colors.HexColor("#F7F0DE"))
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)

    pdf.setFillColor(colors.HexColor("#111111"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 6, item.label)

    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN - 4, item.path.name)

    image_top = PAGE_HEIGHT - MARGIN - HEADER_HEIGHT
    image_bottom = MARGIN + FOOTER_HEIGHT + (26 if item.caption else 0)
    max_width = PAGE_WIDTH - (MARGIN * 2)
    max_height = image_top - image_bottom
    scale = min(max_width / image.width, max_height / image.height)
    draw_width = image.width * scale
    draw_height = image.height * scale
    x = (PAGE_WIDTH - draw_width) / 2
    y = image_bottom + (max_height - draw_height) / 2

    pdf.setStrokeColor(colors.HexColor("#222222"))
    pdf.setLineWidth(0.75)
    pdf.rect(x - 1, y - 1, draw_width + 2, draw_height + 2, stroke=1, fill=0)
    pdf.drawImage(image_reader, x, y, draw_width, draw_height, preserveAspectRatio=True, mask="auto")

    if item.caption:
        pdf.setFillColor(colors.HexColor("#222222"))
        draw_wrapped_text(pdf, item.caption, MARGIN, MARGIN + FOOTER_HEIGHT + 12, max_width, 9)

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(PAGE_WIDTH - MARGIN, MARGIN, f"{page_number} / {total_pages}")
    pdf.showPage()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble labeled PNG/JPEG screenshots into a PDF.")
    parser.add_argument("--output", required=True, help="Output PDF path.")
    parser.add_argument("--item", action="append", type=parse_item, default=[], help="Repeat as LABEL=/path/to/image.")
    parser.add_argument("--manifest", help="CSV with columns label,path,caption.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    items = list(args.item)
    if args.manifest:
        items.extend(read_manifest(Path(args.manifest).expanduser()))

    validate_items(items)

    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=letter)
    for index, item in enumerate(items, start=1):
        add_page(pdf, item, index, len(items))
    pdf.save()
    print(f"Wrote {output} with {len(items)} screenshot(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
