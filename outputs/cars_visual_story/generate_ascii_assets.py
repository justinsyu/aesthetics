from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageEnhance


ASSET_DIR = Path(__file__).resolve().parent / "assets"
RAMP = ".,:;+xX5S#@"


def hex_color(rgb):
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def ascii_svg(source, output, cols, contrast=1.12, saturation=1.16):
    image = Image.open(source).convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Color(image).enhance(saturation)

    width, height = image.size
    rows = max(1, round(cols * height / (width * 1.58)))
    small = image.resize((cols, rows), Image.Resampling.LANCZOS)

    cell_w = width / cols
    cell_h = height / rows
    font_size = cell_h * 1.08

    pieces = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#0b0d0d"/>',
        f'<g font-family="JetBrains Mono, Menlo, Monaco, Consolas, monospace" font-size="{font_size:.2f}" font-weight="800" text-anchor="middle">',
    ]

    pixels = small.load()
    for row in range(rows):
        y = (row + 0.82) * cell_h
        for col in range(cols):
            rgb = pixels[col, row]
            r, g, b = rgb
            luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
            char = RAMP[min(len(RAMP) - 1, int(luma / 256 * len(RAMP)))]
            x = (col + 0.5) * cell_w
            color = hex_color(rgb)
            pieces.append(
                f'<rect x="{col * cell_w:.2f}" y="{row * cell_h:.2f}" width="{cell_w:.2f}" height="{cell_h:.2f}" fill="{color}" opacity="0.18"/>'
            )
            pieces.append(
                f'<text x="{x:.2f}" y="{y:.2f}" fill="{color}">{escape(char)}</text>'
            )

    pieces.extend(["</g>", "</svg>"])
    output.write_text("\n".join(pieces), encoding="utf-8")


def main():
    jobs = [
        ("character-head.png", "character-head-ascii.svg", 172),
        ("sally.png", "sally-ascii.svg", 86),
        ("luigi-guido.png", "luigi-guido-ascii.svg", 86),
        ("mater.png", "mater-ascii.svg", 86),
        ("doc.png", "doc-ascii.svg", 86),
    ]
    for source_name, output_name, cols in jobs:
        ascii_svg(ASSET_DIR / source_name, ASSET_DIR / output_name, cols)


if __name__ == "__main__":
    main()
