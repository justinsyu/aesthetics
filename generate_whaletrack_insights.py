#!/usr/bin/env python3
import json
import textwrap
import zipfile
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import font_manager
import numpy as np
import pandas as pd
import plotly.express as px
import requests


INPUT_CSV = Path("whaletrack_all_records.csv")
OUTPUT_DIR = Path("outputs/whaletrack_insights")
PDF_DIR = OUTPUT_DIR / "pdf"
NE_ZIP = OUTPUT_DIR / "ne_10m_admin_0_countries.zip"
NE_URL = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip"

SPECIES_GROUPS = {
    "Harbour porpoise": "Porpoise",
    "Short-beaked common dolphin": "Dolphin",
    "Bottlenose dolphin": "Dolphin",
    "Risso's dolphin": "Dolphin",
    "White-beaked dolphin": "Dolphin",
    "Atlantic white-sided dolphin": "Dolphin",
    "Striped dolphin": "Dolphin",
    "Unidentified dolphin": "Dolphin",
    "Minke whale": "Whale",
    "Humpback whale": "Whale",
    "Killer whale": "Whale",
    "Fin whale": "Whale",
    "Unidentified whale": "Whale",
    "Northern bottlenose whale": "Whale",
    "Long-finned pilot whale": "Whale",
    "Sei whale": "Whale",
    "Sperm whale": "Whale",
    "Blue Whale": "Whale",
    "Cuvier's beaked whale": "Whale",
    "Sowerby's beaked whale": "Whale",
    "Basking shark": "Basking shark",
    "Sunfish": "Other megafauna",
}

COLORS = {
    "ink": "#10120f",
    "muted": "#5c6257",
    "paper": "#f6f1e8",
    "paper_2": "#ebe4d6",
    "card": "#fffaf0",
    "line": "#1b1f17",
    "lime": "#d7ff5f",
    "orange": "#ffb86b",
    "blue": "#b8d8ff",
    "pink": "#ffd3e0",
    "gray": "#d6d0c2",
    "red": "#ff8a76",
    "dark": "#11130f",
    "water": "#cfe1e6",
}
ACCENTS = [COLORS["lime"], COLORS["blue"], COLORS["orange"], COLORS["pink"], COLORS["red"], COLORS["gray"]]
TAN_CMAP = LinearSegmentedColormap.from_list(
    "cohere_tan",
    [COLORS["paper_2"], COLORS["blue"], COLORS["lime"], COLORS["orange"], COLORS["red"]],
)


def setup():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    sans_font = "Inter" if "Inter" in available_fonts else "DejaVu Sans"
    plt.rcParams.update(
        {
            "figure.facecolor": COLORS["paper"],
            "axes.facecolor": COLORS["card"],
            "savefig.facecolor": COLORS["paper"],
            "font.family": sans_font,
            "axes.titleweight": "normal",
            "axes.titlesize": 17,
            "axes.labelcolor": COLORS["muted"],
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["muted"],
            "text.color": COLORS["ink"],
            "axes.edgecolor": COLORS["line"],
            "grid.color": "#c9c2b4",
            "axes.linewidth": 1.2,
        }
    )


def style_panel(ax, grid_axis=None):
    ax.set_facecolor(COLORS["card"])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.95)
        spine.set_color("#4a453b")
    if grid_axis:
        ax.grid(axis=grid_axis, color="#d8d0c2", linewidth=0.8, alpha=0.75)
    ax.tick_params(labelsize=10)


def wrapped_labels(labels, width=18):
    return [textwrap.fill(str(label), width=width, break_long_words=False) for label in labels]


def wrap_y_tick_labels(ax, width=18, fontsize=9.5):
    labels = [tick.get_text() for tick in ax.get_yticklabels()]
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(wrapped_labels(labels, width=width), fontsize=fontsize)


def add_pill(ax, text, x=0.0, y=1.02):
    ax.text(
        x,
        y,
        text.upper(),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.5,
        fontweight=850,
        color=COLORS["ink"],
        bbox={
            "boxstyle": "round,pad=0.36,rounding_size=0.9",
            "facecolor": COLORS["lime"],
            "edgecolor": COLORS["line"],
            "linewidth": 1.1,
        },
    )


def add_title_block(ax, title, subtitle=None, size=30):
    ax.axis("off")
    add_pill(ax, "Whale Track insights", x=0, y=0.78)
    ax.text(0, 0.46, title, fontsize=size, fontweight=500, color=COLORS["ink"], va="center")
    if subtitle:
        subtitle_text = "\n".join(textwrap.wrap(subtitle, width=132, break_long_words=False))
        ax.text(0, 0.12, subtitle_text, fontsize=12, color=COLORS["muted"], va="center", linespacing=1.25)


def load_data():
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    for column in [
        "listing_total",
        "latitude",
        "longitude",
        "data_count_total",
        "data_count_adults",
        "data_count_calves",
        "data_count_juveniles",
        "data_distance",
    ]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["data_timestamp"], errors="coerce", utc=True)
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["month_name"] = df["timestamp"].dt.month_name().str.slice(0, 3)
    df["species_group"] = df["listing_species"].map(SPECIES_GROUPS).fillna("Other or unknown")
    df["has_coordinates"] = df[["latitude", "longitude"]].notna().all(axis=1)
    df["is_zero_zero"] = (df["latitude"].fillna(999) == 0) & (df["longitude"].fillna(999) == 0)
    df["in_core_geography"] = (
        df["latitude"].between(54.0, 61.5)
        & df["longitude"].between(-9.8, -0.5)
        & ~df["is_zero_zero"]
    )
    df["analysis_year"] = df["year"].where(df["year"].between(2017, 2026))
    return df


def annotate_bar_values(ax, values, pad=0.01):
    max_value = max(values) if len(values) else 0
    for patch, value in zip(ax.patches, values):
        ax.text(
            patch.get_width() + max_value * pad,
            patch.get_y() + patch.get_height() / 2,
            f"{value:,.0f}",
            va="center",
            ha="left",
            fontsize=10,
            fontweight=800,
            color=COLORS["ink"],
        )


def savefig(fig, name):
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=160)
    fig.savefig(PDF_DIR / path.with_suffix(".pdf").name)
    plt.close(fig)
    return path


def infographic_overview(df):
    species_counts = df["listing_species"].value_counts()
    top_species = species_counts.head(8).sort_values()
    survey_counts = df["survey_name"].value_counts()

    fig = plt.figure(figsize=(16, 9), constrained_layout=False)
    fig.subplots_adjust(left=0.105, right=0.945, top=0.95, bottom=0.08)
    gs = fig.add_gridspec(3, 4, height_ratios=[0.50, 0.92, 1.72], hspace=0.26, wspace=0.28)
    title = fig.add_subplot(gs[0, :])
    add_title_block(
        title,
        "What Is in the Whale Track Export",
        "A sighting means one submitted record. GPS means the record includes latitude and longitude; it does not prove the animal was at an exact point.",
        size=28,
    )

    metrics = [
        ("Submitted sightings", len(df), COLORS["lime"]),
        ("Unique species names", df["listing_species"].nunique(), COLORS["blue"]),
        ("Named observers", df["username"].nunique(), COLORS["orange"]),
        ("Records with GPS", df["has_coordinates"].sum(), COLORS["pink"]),
    ]
    for idx, (label, value, color) in enumerate(metrics):
        ax = fig.add_subplot(gs[1, idx])
        ax.axis("off")
        ax.add_patch(
            plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color=COLORS["card"], ec=COLORS["line"], lw=1.35)
        )
        ax.add_patch(plt.Rectangle((0, 0.83), 1, 0.17, transform=ax.transAxes, color=color, ec=COLORS["line"], lw=1.1))
        ax.text(0.08, 0.54, f"{value:,.0f}", fontsize=29, fontweight=900, color=COLORS["ink"])
        ax.text(0.08, 0.24, label, fontsize=12, color=COLORS["muted"])

    ax1 = fig.add_subplot(gs[2, :2])
    style_panel(ax1, "x")
    ax1.barh(top_species.index, top_species.values, color=COLORS["lime"], edgecolor=COLORS["line"], linewidth=0.9)
    ax1.set_title("Species Named Most Often")
    ax1.set_xlabel("Number of submitted sightings")
    wrap_y_tick_labels(ax1, width=20, fontsize=9.4)
    annotate_bar_values(ax1, top_species.values)
    ax1.set_xlim(0, top_species.max() * 1.18)
    ax1.margins(y=0.08)

    ax2 = fig.add_subplot(gs[2, 2:])
    style_panel(ax2)
    pie_colors = [COLORS["blue"], COLORS["orange"], COLORS["pink"]]
    wedges, _, _ = ax2.pie(
        survey_counts.values,
        labels=None,
        autopct=lambda pct: f"{pct:.0f}%",
        startangle=90,
        colors=pie_colors[: len(survey_counts)],
        wedgeprops={"linewidth": 1.2, "edgecolor": COLORS["line"]},
        textprops={"fontsize": 11, "fontweight": 800, "color": COLORS["ink"]},
    )
    ax2.set_title("How the Sighting Was Reported")
    ax2.legend(
        wedges,
        survey_counts.index,
        loc="center left",
        bbox_to_anchor=(0.86, 0.5),
        ncol=1,
        frameon=False,
        fontsize=9.5,
    )
    ax2.set_aspect("equal")

    return savefig(fig, "01_overview_species.png")


def infographic_species_abundance(df):
    by_species = (
        df.groupby("listing_species")
        .agg(sightings=("record_id", "size"), individuals=("listing_total", "sum"), median_group=("listing_total", "median"))
        .sort_values("sightings", ascending=False)
        .head(12)
        .iloc[::-1]
    )

    fig = plt.figure(figsize=(16, 9), constrained_layout=False)
    fig.subplots_adjust(left=0.125, right=0.965, top=0.95, bottom=0.08)
    gs = fig.add_gridspec(2, 2, height_ratios=[0.34, 1], hspace=0.18, wspace=0.44)
    title = fig.add_subplot(gs[0, :])
    add_title_block(
        title,
        "Sighting Records and Animal Counts Answer Different Questions",
        "A sighting counts one submitted record. Reported animals add the animals listed in each record, so one large group can change the ranking.",
        size=22,
    )
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.remove()
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    style_panel(ax2, "x")
    ax2.barh(by_species.index, by_species["sightings"], color=COLORS["blue"], edgecolor=COLORS["line"], linewidth=0.8)
    ax2.set_title("Most Submitted Sighting Records")
    ax2.set_xlabel("Number of submitted sightings")
    wrap_y_tick_labels(ax2, width=19, fontsize=9.2)
    annotate_bar_values(ax2, by_species["sightings"].values)
    ax2.set_xlim(0, by_species["sightings"].max() * 1.22)

    by_individuals = by_species.sort_values("individuals").tail(12)
    style_panel(ax3, "x")
    ax3.barh(by_individuals.index, by_individuals["individuals"], color=COLORS["orange"], edgecolor=COLORS["line"], linewidth=0.8)
    ax3.set_title("Most Animals Reported")
    ax3.set_xlabel("Reported animals across all records")
    wrap_y_tick_labels(ax3, width=19, fontsize=9.2)
    annotate_bar_values(ax3, by_individuals["individuals"].values)
    ax3.set_xlim(0, by_individuals["individuals"].max() * 1.24)
    return savefig(fig, "02_species_abundance.png")


def infographic_temporal(df):
    annual = df[df["analysis_year"].notna()].groupby("analysis_year").size()
    monthly = (
        df[df["analysis_year"].between(2018, 2025)]
        .pivot_table(index="month", columns="analysis_year", values="record_id", aggfunc="count", fill_value=0)
        .reindex(range(1, 13))
    )
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = plt.figure(figsize=(16, 9), constrained_layout=False)
    fig.subplots_adjust(left=0.065, right=0.925, top=0.95, bottom=0.08)
    gs = fig.add_gridspec(3, 1, height_ratios=[0.30, 0.82, 1.22], hspace=0.34)
    title = fig.add_subplot(gs[0, 0])
    add_title_block(
        title,
        "Reports Peak in Summer and Were Highest in 2025",
        "These counts reflect both animal sightings and when people submitted reports. The 2026 year is incomplete through May 9, 2026.",
        size=24,
    )

    ax1 = fig.add_subplot(gs[1, 0])
    style_panel(ax1, "y")
    colors = [COLORS["blue"]] * len(annual)
    if len(colors):
        colors[int(np.argmax(annual.values))] = COLORS["lime"]
        colors[-1] = COLORS["orange"]
    ax1.bar(annual.index.astype(int), annual.values, color=colors, edgecolor=COLORS["line"], linewidth=0.9)
    ax1.plot(annual.index.astype(int), annual.values, color=COLORS["ink"], linewidth=1.4, marker="o", markersize=4)
    ax1.set_title("Submitted Sightings by Year")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Submitted sightings")
    for year, value in annual.items():
        if value == annual.max() or year in [2017, 2026]:
            ax1.text(year, value + annual.max() * 0.025, f"{value:,.0f}", ha="center", fontsize=10)

    ax2 = fig.add_subplot(gs[2, 0])
    style_panel(ax2)
    image = ax2.imshow(monthly.values, aspect="auto", cmap=TAN_CMAP)
    ax2.set_title("Submitted Sightings by Month, 2018-2025")
    ax2.set_yticks(np.arange(12), month_labels)
    ax2.set_xticks(np.arange(len(monthly.columns)), [int(c) for c in monthly.columns])
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Month")
    cbar = fig.colorbar(image, ax=ax2, shrink=0.85, pad=0.012)
    cbar.set_label("Submitted sightings")
    return savefig(fig, "03_temporal_patterns.png")


def infographic_sources_observers(df):
    source = df["data_datasource"].fillna("not recorded").value_counts()
    platform = df["data_platform"].fillna("not recorded").value_counts().head(9).iloc[::-1]
    top_users = df["username"].fillna("not recorded").value_counts().head(12)
    top_share = top_users.sum() / len(df)

    fig = plt.figure(figsize=(16, 9), constrained_layout=False)
    fig.subplots_adjust(left=0.13, right=0.955, top=0.95, bottom=0.08)
    gs = fig.add_gridspec(3, 2, height_ratios=[0.32, 0.9, 1.10], hspace=0.36, wspace=0.34)
    title = fig.add_subplot(gs[0, :])
    add_title_block(
        title,
        "How Reports Enter the Dataset",
        "Observer names, app use and platform codes describe the reporting process. Platform codes are raw export labels; they are not direct measures of animal abundance.",
        size=24,
    )
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])
    ax3 = fig.add_subplot(gs[2, :])

    style_panel(ax1)
    wedges, _, _ = ax1.pie(
        source.values,
        labels=None,
        autopct=lambda pct: f"{pct:.0f}%",
        startangle=90,
        colors=[COLORS["lime"], COLORS["gray"], COLORS["orange"], COLORS["blue"]],
        wedgeprops={"linewidth": 1.2, "edgecolor": COLORS["line"]},
        textprops={"fontsize": 10.5, "fontweight": 800},
    )
    ax1.set_title("Was a Data Source Recorded?")
    ax1.legend(wedges, source.index, loc="center left", bbox_to_anchor=(0.98, 0.5), frameon=False, fontsize=10)

    style_panel(ax2, "x")
    ax2.barh(platform.index, platform.values, color=COLORS["pink"], edgecolor=COLORS["line"], linewidth=0.8)
    ax2.set_title("Raw Platform Codes in the Export")
    ax2.set_xlabel("Number of submitted sightings")
    wrap_y_tick_labels(ax2, width=18, fontsize=9.4)
    annotate_bar_values(ax2, platform.values)
    ax2.set_xlim(0, platform.max() * 1.2)

    top_users_plot = top_users.iloc[::-1]
    style_panel(ax3, "x")
    ax3.barh(top_users_plot.index, top_users_plot.values, color=COLORS["red"], edgecolor=COLORS["line"], linewidth=0.8)
    ax3.set_title(f"These 12 Observers Submitted {top_share:.0%} of Records")
    ax3.set_xlabel("Number of submitted sightings")
    wrap_y_tick_labels(ax3, width=22, fontsize=9.4)
    annotate_bar_values(ax3, top_users_plot.values)
    ax3.set_xlim(0, top_users_plot.max() * 1.18)
    return savefig(fig, "04_sources_observers.png")


def download_natural_earth():
    if NE_ZIP.exists() and zipfile.is_zipfile(NE_ZIP):
        return NE_ZIP
    response = requests.get(NE_URL, timeout=45)
    response.raise_for_status()
    NE_ZIP.write_bytes(response.content)
    return NE_ZIP


def plot_base_map(ax):
    try:
        import geopandas as gpd

        zip_path = download_natural_earth()
        world = gpd.read_file(f"zip://{zip_path}")
        area = world[world["ADMIN"].isin(["United Kingdom", "Ireland"])]
        area.plot(ax=ax, facecolor=COLORS["card"], edgecolor=COLORS["line"], linewidth=0.8, zorder=1)
    except Exception:
        ax.set_facecolor(COLORS["water"])


def infographic_gps_map(df):
    valid = df[df["has_coordinates"] & ~df["is_zero_zero"]].copy()
    core = valid[valid["in_core_geography"]]
    outliers = valid[~valid["in_core_geography"]]

    map_asset = OUTPUT_DIR / "05_gps_density_map_map.png"
    fig = plt.figure(figsize=(8.2, 5.6), constrained_layout=False)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.985, bottom=0.185)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor(COLORS["water"])
    plot_base_map(ax)

    hb = ax.hexbin(
        core["longitude"],
        core["latitude"],
        gridsize=75,
        mincnt=1,
        bins="log",
        cmap=TAN_CMAP,
        alpha=0.88,
        linewidths=0,
        zorder=2,
    )
    sample = core.sample(min(1600, len(core)), random_state=7)
    ax.scatter(sample["longitude"], sample["latitude"], s=2.4, c=COLORS["card"], alpha=0.16, zorder=3)
    ax.scatter(outliers["longitude"].clip(-10, 0), outliers["latitude"].clip(54, 61.3), s=0)
    ax.set_xlim(-9.4, -0.8)
    ax.set_ylim(54.5, 60.8)
    ax.set_aspect("auto")
    ax.set_xlabel("Longitude", fontsize=10)
    ax.set_ylabel("Latitude", fontsize=10)
    ax.grid(color=COLORS["card"], linewidth=0.8, alpha=0.65)
    for spine in ax.spines.values():
        spine.set_linewidth(1.1)
        spine.set_color(COLORS["line"])
    cbar = fig.colorbar(hb, ax=ax, orientation="horizontal", shrink=0.46, pad=0.075, aspect=28)
    cbar.set_label("Submitted sightings per hexagon, log scale", fontsize=10)
    cbar.outline.set_edgecolor(COLORS["line"])
    cbar.outline.set_linewidth(0.9)
    fig.savefig(map_asset, dpi=180, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)

    stat_rows = [
        ("Records inside this map", len(core), COLORS["lime"]),
        ("Valid coordinates outside this map", len(outliers), COLORS["blue"]),
        ("Valid GPS records in the export", len(valid), COLORS["orange"]),
    ]
    stat_html = "\n".join(
        f"""
        <section class="stat-card">
          <div class="swatch" style="background:{color}"></div>
          <p>{escape(label)}</p>
          <strong>{value:,.0f}</strong>
        </section>
        """
        for label, value, color in stat_rows
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Where GPS Sightings Cluster Around Scotland</title>
  <style>
    :root {{
      --ink: {COLORS["ink"]};
      --muted: {COLORS["muted"]};
      --paper: {COLORS["paper"]};
      --paper-2: {COLORS["paper_2"]};
      --card: {COLORS["card"]};
      --line: {COLORS["line"]};
      --lime: {COLORS["lime"]};
    }}
    @page {{ size: 900px 1200px; margin: 0; }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    body, *, *::before, *::after {{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    .sheet {{
      position: relative;
      width: 900px;
      height: 1200px;
      overflow: hidden;
      padding: 42px 46px 40px;
      background: var(--paper);
    }}
    .kicker {{
      display: inline-flex;
      align-items: center;
      border: 1.5px solid var(--line);
      border-radius: 999px;
      background: var(--lime);
      padding: 6px 10px;
      font-size: 12px;
      line-height: 1;
      font-weight: 850;
      letter-spacing: .04em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 16px 0 8px;
      max-width: 760px;
      font-size: 42px;
      line-height: .98;
      font-weight: 520;
      letter-spacing: 0;
    }}
    .dek {{
      margin: 0;
      max-width: 790px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.35;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-top: 24px;
    }}
    .stat-card, .note {{
      border: 1.25px solid var(--line);
      background: var(--card);
    }}
    .stat-card {{
      min-height: 122px;
      padding: 18px 18px 16px;
    }}
    .swatch {{
      width: 22px;
      height: 22px;
      border: 1.25px solid var(--line);
      margin-bottom: 13px;
    }}
    .stat-card p {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.15;
      font-weight: 850;
      letter-spacing: .035em;
      text-transform: uppercase;
    }}
    .stat-card strong {{
      font-size: 32px;
      line-height: 1;
      font-weight: 900;
    }}
    .map-card {{
      margin-top: 22px;
      border: 1.4px solid var(--line);
      background: var(--card);
      padding: 14px;
    }}
    .map-card img {{
      display: block;
      width: 100%;
      height: auto;
      border: 1px solid var(--line);
      background: var(--card);
    }}
    .notes {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-top: 20px;
    }}
    .note {{
      min-height: 158px;
      padding: 17px 18px;
    }}
    .note h2 {{
      margin: 0 0 9px;
      font-size: 15px;
      line-height: 1;
      font-weight: 850;
      letter-spacing: .02em;
      text-transform: uppercase;
    }}
    .note p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }}
    .footer {{
      position: absolute;
      left: 46px;
      right: 46px;
      bottom: 38px;
      border-top: 1px solid var(--line);
      padding-top: 11px;
      color: var(--muted);
      font-size: 11.5px;
      line-height: 1.25;
    }}
  </style>
</head>
<body>
  <article class="sheet" aria-label="Portrait GPS sightings density infographic">
    <header>
      <div class="kicker">Whale Track insights</div>
      <h1>Where GPS Sightings Cluster Around Scotland</h1>
      <p class="dek">Each mapped point is a submitted sighting record with latitude and longitude. This shows where reports cluster; it is not a continuous animal track.</p>
    </header>
    <main>
      <div class="stats">{stat_html}
      </div>
      <figure class="map-card">
        <img src="{escape(map_asset.name)}" alt="Density map of submitted Whale Track GPS records around Scotland">
      </figure>
      <div class="notes">
        <section class="note">
          <h2>How to read the color</h2>
          <p>Colored hexagons group nearby GPS records. Warmer colors mean more submitted sighting records in that area.</p>
        </section>
        <section class="note">
          <h2>Important limit</h2>
          <p>Coordinates describe report locations. The chart should not be read as exact animal paths or as a full measure of local abundance.</p>
        </section>
      </div>
    </main>
    <footer class="footer">Source: Whale Track All records export. Map includes valid latitude and longitude records and excludes records at 0,0.</footer>
  </article>
</body>
</html>
"""
    html_path = OUTPUT_DIR / "05_gps_density_map.html"
    html_path.write_text(html, encoding="utf-8")
    return html_path


def interactive_map(df):
    valid = df[df["has_coordinates"] & ~df["is_zero_zero"]].copy()
    valid["reported_total"] = valid["listing_total"].fillna(0)
    valid["display_time"] = valid["listing_date"].fillna("") + " " + valid["listing_time"].fillna("")
    fig = px.scatter_mapbox(
        valid,
        lat="latitude",
        lon="longitude",
        color="species_group",
        size="reported_total",
        size_max=14,
        zoom=6.0,
        center={"lat": 57.55, "lon": -5.75},
        opacity=0.52,
        hover_name="listing_species",
        hover_data={
            "record_id": True,
            "display_time": True,
            "listing_total": True,
            "survey_name": True,
            "username": True,
            "latitude": ":.4f",
            "longitude": ":.4f",
            "species_group": False,
            "reported_total": False,
        },
        mapbox_style="carto-positron",
        title=None,
        labels={
            "species_group": "Species category",
            "record_id": "Record ID",
            "display_time": "Reported date/time",
            "listing_total": "Reported animals",
            "survey_name": "Report type",
            "username": "Observer",
            "latitude": "Latitude",
            "longitude": "Longitude",
        },
        color_discrete_sequence=[
            COLORS["blue"],
            COLORS["lime"],
            COLORS["orange"],
            COLORS["pink"],
            COLORS["red"],
            COLORS["gray"],
        ],
    )
    fig.update_layout(
        margin={"l": 18, "r": 18, "t": 10, "b": 14},
        legend_title_text="Species category",
        paper_bgcolor=COLORS["paper"],
        plot_bgcolor=COLORS["paper"],
        font={"family": "Inter, Arial, sans-serif", "color": COLORS["ink"], "size": 13},
        legend={
            "bgcolor": COLORS["card"],
            "bordercolor": COLORS["line"],
            "borderwidth": 1,
            "x": 0.012,
            "y": 0.985,
            "font": {"size": 12},
        },
    )
    path = OUTPUT_DIR / "whaletrack_gps_interactive_map.html"
    html = fig.to_html(include_plotlyjs="cdn", full_html=True, config={"displayModeBar": False, "responsive": True})
    html = html.replace("<title></title>", "<title>Whale Track GPS Sightings Interactive Map</title>")
    if "<title>" not in html:
        html = html.replace("<head>", "<head><title>Whale Track GPS Sightings Interactive Map</title>", 1)
    header = f"""
    <header class="map-header">
      <div>
        <div class="map-kicker">Whale Track insights</div>
        <h1>Where GPS Sightings Cluster Around Scotland</h1>
        <p>Each point is a submitted sighting record with latitude and longitude, not a continuous animal track. Hover points for species, observer and coordinate detail.</p>
      </div>
      <div class="map-badge">GPS coordinate view</div>
    </header>
    """
    css = f"""
    <style>
      :root {{
        --ink: {COLORS["ink"]};
        --paper: {COLORS["paper"]};
        --card: {COLORS["card"]};
        --line: {COLORS["line"]};
        --lime: {COLORS["lime"]};
      }}
      html, body {{
        margin: 0;
        min-height: 100%;
        width: 100%;
        background: var(--paper);
        color: var(--ink);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      body {{
        overflow: hidden;
      }}
      .map-header {{
        box-sizing: border-box;
        height: 132px;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 22px;
        padding: 18px 22px 14px;
        border-bottom: 1.4px solid var(--line);
      }}
      .map-kicker, .map-badge {{
        display: inline-flex;
        border: 1.4px solid var(--line);
        border-radius: 999px;
        background: var(--lime);
        padding: 7px 11px;
        font-size: 12px;
        line-height: 1;
        font-weight: 850;
        letter-spacing: .06em;
        text-transform: uppercase;
        white-space: nowrap;
      }}
      .map-header h1 {{
        margin: 12px 0 6px;
        max-width: 930px;
        font-size: clamp(24px, 3vw, 38px);
        line-height: .98;
        font-weight: 520;
        letter-spacing: 0;
      }}
      .map-header p {{
        margin: 0;
        max-width: 860px;
        color: {COLORS["muted"]};
        font-size: 13px;
        line-height: 1.35;
      }}
      .plotly-graph-div {{
        height: calc(100vh - 132px) !important;
        min-height: 520px;
      }}
      @media (max-width: 700px) {{
        body {{
          overflow: auto;
        }}
        .map-header {{
          height: auto;
          min-height: 164px;
          display: block;
          padding: 14px 14px 12px;
        }}
        .map-badge {{
          margin-top: 10px;
        }}
        .map-header h1 {{
          font-size: 25px;
          line-height: 1.02;
        }}
        .map-header p {{
          font-size: 12.5px;
        }}
        .plotly-graph-div {{
          height: calc(100vh - 178px) !important;
          min-height: 560px;
        }}
      }}
      @page {{
        size: 1600px 900px;
        margin: 0;
      }}
      @media print {{
        body, *, *::before, *::after {{
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }}
        html, body {{
          width: 1600px;
          height: 900px;
          overflow: hidden;
        }}
        .map-header {{
          height: 132px;
        }}
        .plotly-graph-div {{
          height: 768px !important;
          min-height: 768px;
        }}
      }}
    </style>
    """
    html = html.replace("</head>", css + "\n</head>")
    html = html.replace("<body>", "<body>" + header, 1)
    path.write_text(html, encoding="utf-8")
    return path


def build_summary(df, artifacts):
    total = len(df)
    coordinates = int(df["has_coordinates"].sum())
    core_geo = int((df["has_coordinates"] & df["in_core_geography"]).sum())
    coord_outliers = int((df["has_coordinates"] & ~df["in_core_geography"] & ~df["is_zero_zero"]).sum())
    zero_zero = int(df["is_zero_zero"].sum())
    top_species = df["listing_species"].value_counts().head(5)
    top_individuals = df.groupby("listing_species")["listing_total"].sum().sort_values(ascending=False).head(5)
    annual = df[df["analysis_year"].notna()].groupby("analysis_year").size()
    peak_year = int(annual.idxmax())
    peak_year_count = int(annual.max())
    summer_share = (
        df[df["analysis_year"].between(2018, 2025)]["month"].isin([6, 7, 8, 9]).mean()
    )
    top_user_counts = df["username"].value_counts().head(12)
    source = df["data_datasource"].fillna("not recorded").value_counts(normalize=True)
    survey = df["survey_name"].value_counts(normalize=True)

    lines = [
        "# Whale Track Data Insights",
        "",
        f"Input CSV: `{INPUT_CSV.resolve()}`",
        "",
        "## Headline Findings",
        "",
        f"- The export contains **{total:,} public All records sightings**.",
        f"- **{coordinates:,} records ({coordinates / total:.1%}) include GPS coordinates**. The rendered detail pages confirm that missing coordinates are real `N/A` values for sampled records.",
        f"- The core map view contains **{core_geo:,} coordinate records** around Scotland and nearby waters. There are **{coord_outliers:,} valid coordinate records outside that core geography** plus **{zero_zero:,} records at 0,0**, which should be treated as data-quality exceptions or non-local reports.",
        f"- Reporting volume peaks in **{peak_year} with {peak_year_count:,} sightings**. The 2026 data is partial through May 9, 2026.",
        f"- From 2018-2025, **{summer_share:.0%} of records fall in June-September**, confirming a strong seasonal fieldwork/reporting pattern.",
        f"- The top 12 observers contribute **{top_user_counts.sum() / total:.0%} of all records**, so observer/program workflow effects matter when comparing trends.",
        f"- Survey mix: " + ", ".join(f"{name} {share:.0%}" for name, share in survey.items()) + ".",
        f"- Data source mix: " + ", ".join(f"{name} {share:.0%}" for name, share in source.items()) + ".",
        "",
        "## Leading Species by Sightings",
        "",
    ]
    for species, count in top_species.items():
        lines.append(f"- {species}: {count:,} sightings ({count / total:.1%})")
    lines.extend(["", "## Leading Species by Reported Individuals", ""])
    for species, count in top_individuals.items():
        lines.append(f"- {species}: {count:,.0f} reported individuals")
    lines.extend(["", "## Generated Infographics", ""])
    for label, path in artifacts.items():
        lines.append(f"- {label}: `{path.resolve()}`")
    lines.append("")
    (OUTPUT_DIR / "whaletrack_insights_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    setup()
    df = load_data()
    artifacts = {
        "Overview and species mix": infographic_overview(df),
        "Species records vs individuals": infographic_species_abundance(df),
        "Annual and seasonal patterns": infographic_temporal(df),
        "Sources and observers": infographic_sources_observers(df),
        "GPS density map": infographic_gps_map(df),
        "Interactive GPS map": interactive_map(df),
    }
    build_summary(df, artifacts)
    print(json.dumps({key: str(value) for key, value in artifacts.items()}, indent=2))
    print(f"Summary: {OUTPUT_DIR / 'whaletrack_insights_summary.md'}")


if __name__ == "__main__":
    main()
