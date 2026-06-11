import calendar
import csv
from collections import Counter, defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "meeting-dates-2025-06-2026-05.csv"
PDF_PATH = ROOT / "meeting-calendar-2025-06-2026-05-no-active-links.pdf"

PAGE_W, PAGE_H = landscape(letter)
MARGIN = 34
INK = colors.HexColor("#10120f")
MUTED = colors.HexColor("#5c6257")
LINE = colors.HexColor("#1b1f17")
PANEL = colors.HexColor("#fffaf0")
PAPER = colors.HexColor("#f6f1e8")
PAPER2 = colors.HexColor("#ebe4d6")
TAN = colors.HexColor("#d8cab5")
SAND = colors.HexColor("#cbbb9f")
CLAY = colors.HexColor("#bba985")
VOLUME_MED = colors.HexColor("#b7a27b")
VOLUME_HIGH = colors.HexColor("#92764d")
BLUE = colors.HexColor("#b8d8ff")
LIME = colors.HexColor("#d7ff5f")
WARN = colors.HexColor("#ffb86b")
GRAY = colors.HexColor("#d6d0c2")
RED = colors.HexColor("#ff8a76")
SOFT = PAPER2
SOFT2 = GRAY
PINK = colors.HexColor("#ffd3e0")
DARK = colors.HexColor("#11130f")
CALENDAR_DOT_COLORS = [
    colors.HexColor("#d1c0a2"),
    colors.HexColor("#c8beb0"),
    colors.HexColor("#d6b9a9"),
    colors.HexColor("#c4c7a5"),
    colors.HexColor("#c8d2ce"),
    colors.HexColor("#c9b38f"),
]

FONT_PATHS = {
    "title": [
        Path.home() / "AppData/Local/Microsoft/Windows/Fonts/SpaceGrotesk-Medium.ttf",
        Path.home() / "AppData/Local/Microsoft/Windows/Fonts/SpaceGrotesk-SemiBold.ttf",
        Path("C:/Windows/Fonts/SpaceGrotesk-Medium.ttf"),
        Path("C:/Windows/Fonts/SpaceGrotesk-SemiBold.ttf"),
    ],
    "body": [
        Path.home() / "AppData/Local/Microsoft/Windows/Fonts/Inter-Variable.ttf",
        Path("C:/Windows/Fonts/Inter-Variable.ttf"),
        Path.home() / "AppData/Local/Temp/inter-font-install/Inter-Variable.ttf",
    ],
}
FONT_PATHS_USED = {}


def _register_font(name, candidates, fallback):
    for path in candidates:
        if path.exists():
            try:
                pdfmetrics.registerFont(TTFont(name, str(path)))
                FONT_PATHS_USED[name] = str(path)
                return name
            except Exception:
                continue
    FONT_PATHS_USED[name] = f"fallback:{fallback}"
    return fallback


TITLE_FONT = _register_font("SpaceGroteskLocal", FONT_PATHS["title"], "Helvetica-Bold")
BODY_FONT = _register_font("InterLocal", FONT_PATHS["body"], "Helvetica")
BODY_FONT_BOLD = BODY_FONT


def read_rows():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def wrap_text(text, font, size, width):
    words = str(text or "").split()
    lines = []
    line = ""
    for word in words:
        candidate = word if not line else f"{line} {word}"
        if stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            if stringWidth(word, font, size) <= width:
                line = word
            else:
                part = ""
                for ch in word:
                    if stringWidth(part + ch, font, size) <= width:
                        part += ch
                    else:
                        if part:
                            lines.append(part)
                        part = ch
                line = part
    if line:
        lines.append(line)
    return lines


def draw_wrapped(c, text, x, y, width, font=BODY_FONT, size=8, leading=10, color=INK, max_lines=None):
    c.setFillColor(color)
    c.setFont(font, size)
    lines = wrap_text(text, font, size, width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines:
            lines[-1] = lines[-1].rstrip(".") + "..."
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


DOT_SCHEMES = [
    [
        (0, 58, 310, PAGE_H - 82, 16, 0.70, TAN, 0.42, 0.0, 0.0),
        (PAGE_W - 292, PAGE_H - 218, 270, 178, 18, 0.62, BLUE, 0.28, 2.0, 1.0),
        (PAGE_W - 255, 34, 218, 94, 17, 0.58, PINK, 0.24, 4.0, 3.0),
    ],
    [
        (28, PAGE_H - 168, PAGE_W - 56, 118, 16, 0.66, PAPER2, 0.46, 1.0, 2.0),
        (PAGE_W - 260, 38, 218, PAGE_H - 100, 19, 0.62, TAN, 0.34, 3.0, 0.0),
    ],
    [
        (32, PAGE_H - 180, PAGE_W - 64, 126, 17, 0.68, TAN, 0.38, 0.0, 0.0),
        (42, 92, 212, PAGE_H - 174, 18, 0.58, PAPER2, 0.42, 2.0, 4.0),
        (PAGE_W - 284, 46, 240, 122, 16, 0.54, SAND, 0.27, 4.0, 2.0),
    ],
    [
        (PAGE_W - 316, 54, 274, PAGE_H - 96, 17, 0.62, TAN, 0.36, 1.0, 1.0),
        (40, PAGE_H - 178, 246, 118, 18, 0.56, CLAY, 0.22, 3.0, 0.0),
    ],
    [
        (28, 58, 246, PAGE_H - 122, 16, 0.60, TAN, 0.34, 2.0, 1.0),
        (PAGE_W - 360, 40, 316, 132, 15, 0.55, PAPER2, 0.44, 0.0, 4.0),
        (318, PAGE_H - 152, 184, 104, 18, 0.50, SAND, 0.22, 4.0, 2.0),
    ],
    [
        (42, PAGE_H - 196, PAGE_W - 84, 140, 18, 0.62, PAPER2, 0.42, 4.0, 1.0),
        (PAGE_W - 276, 76, 232, 236, 16, 0.50, SAND, 0.24, 1.0, 3.0),
    ],
    [
        (36, 52, PAGE_W - 72, PAGE_H - 100, 19, 0.52, TAN, 0.28, 0.0, 0.0),
        (42, 76, 248, 154, 15, 0.58, PAPER2, 0.42, 2.0, 1.0),
        (PAGE_W - 288, PAGE_H - 204, 238, 138, 17, 0.54, CLAY, 0.22, 1.0, 4.0),
    ],
]


def draw_dot_grid(c, x, y, w, h, spacing, radius, color, alpha, phase_x=0, phase_y=0):
    c.saveState()
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0, fill=0)
    c.setFillAlpha(alpha)
    c.setFillColor(color)
    left = int(x - spacing)
    right = int(x + w + spacing)
    bottom = int(y - spacing)
    top = int(y + h + spacing)
    for yy in range(bottom, top, spacing):
        for xx in range(left, right, spacing):
            dot_x = xx + phase_x
            dot_y = yy + phase_y
            if x <= dot_x <= x + w and y <= dot_y <= y + h:
                c.circle(dot_x, dot_y, radius, fill=1, stroke=0)
    c.restoreState()


def draw_background(c, page_num):
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    scheme = DOT_SCHEMES[(page_num - 1) % len(DOT_SCHEMES)]
    for spec in scheme:
        draw_dot_grid(c, *spec)


def draw_pill(c, x, y, text, fill=LIME, font_size=7.2, px=8, py=4, center_text=False):
    text_w = stringWidth(text, BODY_FONT_BOLD, font_size)
    w = text_w + px * 2
    h = font_size + py * 2
    c.setFillColor(fill)
    c.setStrokeColor(LINE)
    c.setLineWidth(1.15)
    c.roundRect(x, y, w, h, h / 2, stroke=1, fill=1)
    c.setFillColor(INK)
    c.setFont(BODY_FONT_BOLD, font_size)
    if center_text:
        ascent = pdfmetrics.getAscent(BODY_FONT_BOLD, font_size)
        descent = pdfmetrics.getDescent(BODY_FONT_BOLD, font_size)
        baseline_y = y + h / 2 - (ascent + descent) / 2
    else:
        baseline_y = y + py - 0.2
    c.drawString(x + px, baseline_y, text)
    return w


def draw_panel(c, x, y, w, h, fill=PANEL, radius=8, line_width=1.55):
    c.setFillColor(fill)
    c.setStrokeColor(LINE)
    c.setLineWidth(line_width)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)


def monthly_volume_color(count, max_count):
    ratio = count / max_count if max_count else 0
    if ratio >= 0.72:
        return VOLUME_HIGH
    if ratio >= 0.45:
        return VOLUME_MED
    return TAN


def draw_footer(c, page_num):
    c.setFont(BODY_FONT, 7)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MARGIN, 18, f"Page {page_num}")


def plotted_rows(rows):
    return [r for r in rows if r["date_iso"] and r["status"] in {"confirmed", "planned", "tentative", "proposed"}]


def draw_cover(c, by_date, by_month, page_num):
    draw_background(c, page_num)
    draw_pill(c, MARGIN, PAGE_H - 52, "PUBLIC SOURCE MEETING DATES", LIME, font_size=7.4)
    c.setFillColor(INK)
    c.setFont(BODY_FONT, 7.8)
    c.drawString(MARGIN, PAGE_H - 64, "June 2025-May 2026")
    c.setFillColor(INK)
    c.setFont(TITLE_FONT, 27)
    c.drawString(MARGIN, PAGE_H - 92, "State Medicaid P&T and Related Pharmacy")
    c.drawString(MARGIN, PAGE_H - 124, "Committee Calendar")

    panel_y = 56
    panel_h = PAGE_H - 214
    panel_gap = 22
    monthly_x = MARGIN
    monthly_w = 428
    cluster_x = monthly_x + monthly_w + panel_gap
    cluster_w = PAGE_W - MARGIN - cluster_x

    draw_panel(c, monthly_x, panel_y, monthly_w, panel_h)
    draw_panel(c, cluster_x, panel_y, cluster_w, panel_h)

    c.setFillColor(INK)
    c.setFont(BODY_FONT_BOLD, 15)
    c.drawString(monthly_x + 16, panel_y + panel_h - 32, "Monthly volume")
    max_month = max(by_month.values())
    y = panel_y + panel_h - 68
    month_label_x = monthly_x + 16
    month_bar_x = monthly_x + 128
    month_bar_w = 244
    month_count_x = month_bar_x + month_bar_w + 24
    for key, count in by_month.items():
        c.setFillColor(INK)
        c.setFont(BODY_FONT, 8)
        c.drawString(month_label_x, y, key)
        c.setFillColor(PAPER2)
        c.roundRect(month_bar_x, y - 2, month_bar_w, 9, 4.5, fill=1, stroke=0)
        c.setFillColor(monthly_volume_color(count, max_month))
        c.roundRect(month_bar_x, y - 2, month_bar_w * count / max_month, 9, 4.5, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont(BODY_FONT_BOLD, 8)
        c.drawRightString(month_count_x, y, str(count))
        y -= 27

    c.setFont(BODY_FONT_BOLD, 15)
    c.setFillColor(INK)
    c.drawString(cluster_x + 16, panel_y + panel_h - 32, "Largest same-day clusters")
    y = panel_y + panel_h - 68
    cluster_pad = 14
    cluster_card_h = 29
    cluster_step = 32
    cluster_body_w = cluster_w - cluster_pad * 2
    for date, items in sorted(by_date.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:10]:
        card_y = y - 18
        draw_panel(c, cluster_x + 12, card_y, cluster_w - 24, cluster_card_h, SOFT2)
        c.setFillColor(INK)
        c.setFont(BODY_FONT_BOLD, 7.8)
        c.drawString(cluster_x + cluster_pad + 12, card_y + cluster_card_h - 11.2, f"{date} | {len(items)}")
        draw_wrapped(
            c,
            ", ".join(i["state"] for i in items),
            cluster_x + cluster_pad + 12,
            card_y + 7.2,
            cluster_body_w - 24,
            size=6.5,
            leading=7,
            color=MUTED,
            max_lines=1,
        )
        y -= cluster_step
    draw_footer(c, page_num)


def draw_month_panel_dots(c, x, y, w, h, page_num, panel_index):
    color = CALENDAR_DOT_COLORS[(page_num - 2) % len(CALENDAR_DOT_COLORS)]
    c.saveState()
    p = c.beginPath()
    p.roundRect(x + 1.5, y + 1.5, w - 3, h / 2 - 3, 8)
    c.clipPath(p, stroke=0, fill=0)
    draw_dot_grid(
        c,
        x + 18,
        y + 16,
        w - 36,
        h / 2 - 26,
        17,
        0.48,
        color,
        0.30,
        2.0 + panel_index * 5.0,
        1.0 + panel_index * 3.0,
    )
    c.restoreState()


def draw_month(c, year, month, rows_by_date, x, y, w, h, page_num, panel_index):
    draw_panel(c, x, y, w, h)
    draw_month_panel_dots(c, x, y, w, h, page_num, panel_index)
    c.setFillColor(INK)
    c.setFont(BODY_FONT_BOLD, 13)
    c.drawString(x + 12, y + h - 22, f"{calendar.month_name[month]} {year}")
    prefix = f"{year}-{month:02d}"
    month_count = sum(len(v) for k, v in rows_by_date.items() if k.startswith(prefix))
    draw_pill(c, x + w - 78, y + h - 30, f"{month_count} events", BLUE, font_size=6.6, px=7, py=3.6, center_text=True)

    grid_x = x + 12
    grid_y = y + h - 205
    cell_w = (w - 24) / 7
    cell_h = 25
    c.setFillColor(MUTED)
    c.setFont(BODY_FONT_BOLD, 6)
    for i, wd in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        c.drawCentredString(grid_x + i * cell_w + cell_w / 2, grid_y + 6 * cell_h + 12, wd)
    first, days = calendar.monthrange(year, month)
    first = (first + 1) % 7
    max_cluster = max([len(v) for v in rows_by_date.values()] or [1])
    for d in range(1, days + 1):
        idx = first + d - 1
        col, row = idx % 7, idx // 7
        cx = grid_x + col * cell_w
        cy = grid_y + (5 - row) * cell_h
        c.setStrokeColor(PAPER2)
        c.setLineWidth(0.55)
        c.setFillColor(PANEL)
        c.roundRect(cx + 1, cy + 1, cell_w - 3, cell_h - 3, 3, fill=1, stroke=1)
        c.setFillColor(MUTED)
        c.setFont(BODY_FONT, 5.5)
        c.drawString(cx + 4, cy + cell_h - 9, str(d))
        key = f"{year}-{month:02d}-{d:02d}"
        items = rows_by_date.get(key, [])
        if items:
            count = len(items)
            planned = any(i["status"] != "confirmed" for i in items)
            radius = 5 + 6 * (count / max_cluster)
            c.setFillColor(PANEL if planned else BLUE)
            c.setStrokeColor(WARN if planned else LINE)
            c.setLineWidth(1.2 if planned else 1.0)
            c.circle(cx + cell_w / 2, cy + cell_h / 2 - 1, radius, fill=1, stroke=1)
            c.setFillColor(INK)
            c.setFont(BODY_FONT_BOLD, 7)
            c.drawCentredString(cx + cell_w / 2, cy + cell_h / 2 - 4, str(count))

    detail_y = grid_y - 14
    for key in sorted(k for k in rows_by_date if k.startswith(prefix)):
        items = rows_by_date[key]
        day = str(int(key[-2:]))
        c.setFillColor(INK)
        c.setFont(BODY_FONT_BOLD, 7)
        c.drawString(x + 14, detail_y, day)
        c.setFillColor(INK)
        c.setFont(BODY_FONT, 7)
        names = ", ".join(i["state"] + ("*" if i["status"] != "confirmed" else "") for i in items)
        draw_wrapped(c, names, x + 35, detail_y, w - 50, size=7, leading=8, color=INK, max_lines=2)
        detail_y -= 17
        if detail_y < y + 10:
            break


def draw_calendar_pages(c, plotted, page_start):
    rows_by_date = defaultdict(list)
    for r in plotted:
        rows_by_date[r["date_iso"]].append(r)
    months = [(2025, m) for m in range(6, 13)] + [(2026, m) for m in range(1, 6)]
    page_num = page_start
    for i in range(0, len(months), 2):
        draw_background(c, page_num)
        c.setFillColor(INK)
        c.setFont(TITLE_FONT, 16)
        c.drawString(MARGIN, PAGE_H - 35, "Monthly Calendar")
        c.setFillColor(MUTED)
        c.setFont(BODY_FONT, 8)
        c.drawString(
            MARGIN,
            PAGE_H - 57,
            "Filled blue circles show confirmed meeting-date counts; hollow white circles with orange borders show planned, tentative, or proposed (non-confirmed) meeting-date counts.",
        )
        c.drawString(
            MARGIN,
            PAGE_H - 69,
            "Asterisks in the monthly lists mark planned, tentative, or proposed (non-confirmed) meeting entries.",
        )
        panel_w = (PAGE_W - MARGIN * 2 - 18) / 2
        for j, (year, month) in enumerate(months[i : i + 2]):
            draw_month(c, year, month, rows_by_date, MARGIN + j * (panel_w + 18), 42, panel_w, PAGE_H - 122, page_num, j)
        draw_footer(c, page_num)
        c.showPage()
        page_num += 1
    return page_num


def main():
    rows = read_rows()
    plotted = plotted_rows(rows)
    by_date = defaultdict(list)
    for r in plotted:
        by_date[r["date_iso"]].append(r)
    by_month = Counter()
    for r in plotted:
        year, month, _ = r["date_iso"].split("-")
        by_month[f"{calendar.month_name[int(month)]} {year}"] += 1
    ordered_months = {}
    for y, m in [(2025, x) for x in range(6, 13)] + [(2026, x) for x in range(1, 6)]:
        ordered_months[f"{calendar.month_name[m]} {y}"] = by_month[f"{calendar.month_name[m]} {y}"]

    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(letter), pageCompression=1)
    draw_cover(c, by_date, ordered_months, 1)
    c.showPage()
    draw_calendar_pages(c, plotted, 2)
    c.save()


if __name__ == "__main__":
    main()
