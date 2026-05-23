#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image


BASE = Path(__file__).resolve().parent
JSONL = BASE / "browser_extract.jsonl"
MASTER = BASE / "tmp_worker_2" / "all_urls.tsv"
OUT = BASE / "hcp_site_color_drug_rwe_audit.csv"

FIELDS = [
    "input_url",
    "final_url",
    "status",
    "brand_name",
    "generic_name",
    "company",
    "color_scheme_hex",
    "primary_hex",
    "secondary_hex",
    "accent_hex",
    "rwe_prompt_flag",
    "rwe_assessment",
    "rwe_evidence_terms",
    "notes",
]

COMPANIES = [
    "AbbVie",
    "Amgen",
    "Astellas",
    "AstraZeneca",
    "Bayer",
    "Biogen",
    "Boehringer Ingelheim",
    "Bristol Myers Squibb",
    "CSL Behring",
    "Eisai",
    "Eli Lilly",
    "Gilead",
    "GlaxoSmithKline",
    "GSK",
    "Janssen",
    "Johnson & Johnson",
    "Merck",
    "Novartis",
    "Novo Nordisk",
    "Organon",
    "Pfizer",
    "Regeneron",
    "Roche",
    "Sanofi",
    "Sarepta",
    "Takeda",
    "Teva",
    "UCB",
    "Vertex",
]

GENERIC_PATTERNS = [
    re.compile(r"\(([^()]{3,120})\)"),
    re.compile(r"generic name[:\s]+([A-Za-z0-9 ,;/-]{3,120})", re.I),
    re.compile(r"active ingredient[:\s]+([A-Za-z0-9 ,;/-]{3,120})", re.I),
]

RWE_TERMS = [
    "real-world",
    "real world",
    "retrospective",
    "observational",
    "claims",
    "registry",
    "phase 4",
    "phase iv",
    "postmarketing",
    "post-market",
    "chart review",
    "database study",
    "electronic health record",
]


def normalize_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def screenshot_colors(path: str):
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        return []
    img = Image.open(p).convert("RGB")
    img.thumbnail((240, 240))
    counts = Counter()
    for r, g, b in img.getdata():
        if r > 245 and g > 245 and b > 245:
            continue
        if r < 18 and g < 18 and b < 18:
            continue
        # Quantize to stable, replicable swatches.
        q = (round(r / 24) * 24, round(g / 24) * 24, round(b / 24) * 24)
        q = tuple(max(0, min(255, v)) for v in q)
        counts[q] += 1
    colors = []
    for rgb, _ in counts.most_common(24):
        hx = normalize_hex(rgb)
        if all(color_distance(hx, old) > 42 for old in colors):
            colors.append(hx)
        if len(colors) >= 8:
            break
    return colors


def color_distance(a, b):
    ar, ag, ab = int(a[1:3], 16), int(a[3:5], 16), int(a[5:7], 16)
    br, bg, bb = int(b[1:3], 16), int(b[3:5], 16), int(b[5:7], 16)
    return ((ar - br) ** 2 + (ag - bg) ** 2 + (ab - bb) ** 2) ** 0.5


def brand_from_url(url):
    host = urlparse(url).netloc.lower()
    host = host.removeprefix("www.").removeprefix("hcp.")
    first = host.split(".")[0]
    for suffix in ["hcp", "pro", "rx", "ecp", "-hcp", "pro"]:
        first = first.replace(suffix, "")
    return re.sub(r"[^a-z0-9]+", " ", first).strip().upper()


def clean_brand(title, url):
    title = re.sub(r"\s+", " ", title or "").strip()
    if title:
        left = re.split(r"\s+[|:-]\s+| for HCPs?| HCP ", title, maxsplit=1, flags=re.I)[0]
        left = re.sub(r"®|™", "", left).strip()
        if 2 <= len(left) <= 45 and not re.search(r"access denied|just a moment|error", left, re.I):
            return left
    return brand_from_url(url)


def clean_generic(text):
    text = re.sub(r"\s+", " ", text or "")
    for pattern in GENERIC_PATTERNS:
        for match in pattern.finditer(text[:12000]):
            value = match.group(1).strip(" .;")
            if re.search(r"\b(mcg|mg|hcp|pdf|patient|logo|safety|information)\b", value, re.I):
                continue
            if 3 <= len(value) <= 90:
                return value
    return ""


def company_from_text(text, final_url):
    haystack = f"{text} {final_url}"
    for company in COMPANIES:
        if re.search(r"\b" + re.escape(company) + r"\b", haystack, re.I):
            return company
    host = urlparse(final_url).netloc.lower()
    domain_map = {
        "pfizer": "Pfizer",
        "novomedlink": "Novo Nordisk",
        "sanofi": "Sanofi",
        "lilly": "Eli Lilly",
        "gene.com": "Genentech/Roche",
        "merck": "Merck",
        "tevapharm": "Teva",
        "gilead": "Gilead",
        "janssen": "Johnson & Johnson",
        "bms": "Bristol Myers Squibb",
        "abbvie": "AbbVie",
        "amgen": "Amgen",
        "astrazeneca": "AstraZeneca",
    }
    for key, value in domain_map.items():
        if key in host:
            return value
    return ""


def rwe_assessment(text):
    lower = (text or "").lower()
    found = [term for term in RWE_TERMS if term in lower]
    if any(term in lower for term in ["real-world", "real world", "registry", "claims", "observational"]):
        return "yes", ", ".join(found[:6])
    if found:
        return "maybe", ", ".join(found[:6])
    return "no", ""


def prompt_flag(index, url):
    if index >= 141:
        return "true"
    if index in {61, 65}:
        return "true"
    return "false"


def load_master():
    rows = []
    with MASTER.open(encoding="utf-8") as handle:
        for line in handle:
            index, url = line.rstrip("\n").split("\t", 1)
            rows.append((int(index), url))
    return rows


def load_extracts():
    data = {}
    if not JSONL.exists():
        return data
    with JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            data[item["input_url"].rstrip("/")] = item
    return data


def main():
    extracts = load_extracts()
    out_rows = []
    for index, input_url in load_master():
        item = extracts.get(input_url.rstrip("/"), {})
        title = item.get("title") or ""
        final_url = item.get("final_url") or input_url
        text = " ".join([title, item.get("body_text") or "", item.get("snapshot") or ""])
        colors = screenshot_colors(item.get("screenshot") or "")
        brand = clean_brand(title, input_url)
        generic = clean_generic(text)
        company = company_from_text(text, final_url)
        rwe, terms = rwe_assessment(text)
        notes = item.get("notes") or ""
        if not generic:
            notes = (notes + "; " if notes else "") + "generic not confidently found in captured page text"
        if not company:
            notes = (notes + "; " if notes else "") + "company not confidently found in captured page text"
        if not colors:
            colors = ["#FFFFFF", "#000000"]
            notes = (notes + "; " if notes else "") + "colors unavailable from screenshot"
        out_rows.append(
            {
                "input_url": input_url,
                "final_url": final_url,
                "status": item.get("status") or "not_extracted",
                "brand_name": brand,
                "generic_name": generic,
                "company": company,
                "color_scheme_hex": ", ".join(colors),
                "primary_hex": colors[0] if colors else "",
                "secondary_hex": colors[1] if len(colors) > 1 else "",
                "accent_hex": colors[2] if len(colors) > 2 else "",
                "rwe_prompt_flag": prompt_flag(index, input_url),
                "rwe_assessment": rwe if item else "unknown",
                "rwe_evidence_terms": terms,
                "notes": notes,
            }
        )

    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"wrote {OUT} ({len(out_rows)} rows, {len(extracts)} browser extracts)")


if __name__ == "__main__":
    main()
