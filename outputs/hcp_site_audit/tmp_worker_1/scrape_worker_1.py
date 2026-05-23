#!/usr/bin/env python3
import asyncio
import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


BASE = Path("/Users/justinyu/Desktop/linkedin-posts/outputs/hcp_site_audit")
TMP = BASE / "tmp_worker_1"
OUT = BASE / "chunk_1.csv"
SESSION = Path(
    "/Users/justinyu/.codex/sessions/2026/05/14/"
    "rollout-2026-05-14T10-46-12-019e2798-99a5-7483-9753-40e7aeac1a1c.jsonl"
)

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

RWE_TERMS = [
    "real-world evidence",
    "real world evidence",
    "real-world data",
    "real world data",
    "real-world",
    "real world",
    "observational",
    "registry",
    "claims database",
    "claims data",
    "retrospective",
    "prospective cohort",
    "phase 4",
    "phase iv",
    "postmarketing",
    "post-marketing",
    "chart review",
    "electronic health record",
    "ehr",
]

COMPANY_PATTERNS = [
    "Pfizer",
    "Teva",
    "Organon",
    "Novo Nordisk",
    "Eli Lilly",
    "Lilly",
    "Bristol Myers Squibb",
    "BMS",
    "Sanofi",
    "Novartis",
    "Genentech",
    "Roche",
    "Johnson & Johnson",
    "Janssen",
    "Amgen",
    "AstraZeneca",
    "Gilead",
    "AbbVie",
    "Takeda",
    "Merck",
    "Bayer",
    "Biogen",
    "UCB",
    "Alkermes",
    "Galderma",
    "Bausch",
    "Bausch + Lomb",
    "Horizon",
    "Mallinckrodt",
    "Apellis",
    "CSL Behring",
    "Fresenius Kabi",
    "Ipsen",
    "Jazz Pharmaceuticals",
    "Otsuka",
    "Regeneron",
    "Sarepta",
    "Alexion",
    "Astellas",
    "Acadia",
    "Ardelyx",
    "Amicus",
    "Ascendis",
    "BioCryst",
    "Catalyst",
    "Daiichi Sankyo",
    "Eisai",
    "Eton",
    "Harmony Biosciences",
    "Heron",
    "Hikma",
    "Incyte",
    "Ipsen",
    "Kyowa Kirin",
    "Lantheus",
    "Legend Biotech",
    "Lundbeck",
    "Mitsubishi Tanabe",
    "Neurocrine",
    "Octapharma",
    "Omeros",
    "Radius",
    "Rigel",
    "Sobi",
    "Sumitomo",
    "Sun Pharma",
    "Travere",
    "United Therapeutics",
    "Vertex",
]

DOMAIN_COMPANY_HINTS = {
    "pfizerpro.com": "Pfizer",
    "pfizermedical.com": "Pfizer",
    "novomedlink.com": "Novo Nordisk",
    "pro.campus.sanofi": "Sanofi",
    "lilly.com": "Eli Lilly",
    "tevapharm.com": "Teva",
    "organonpro.com": "Organon",
    "gene.com": "Genentech",
    "bmscustomerconnect.com": "Bristol Myers Squibb",
    "myalcon.com": "Alcon",
    "fresenius-kabi.com": "Fresenius Kabi",
}


def clean_url(raw: str) -> str:
    return raw.strip().rstrip(".,")


def inherited_prompt() -> str:
    for line in SESSION.read_text(encoding="utf-8").splitlines():
        data = json.loads(line)
        payload = data.get("payload", {})
        if payload.get("type") == "message" and payload.get("role") == "user":
            text = "\n".join(
                item.get("text", "")
                for item in payload.get("content", [])
                if item.get("type") == "input_text"
            )
            if "For all websites in the list below" in text:
                return text
    raise RuntimeError("Inherited prompt not found in session log")


def parse_urls_and_flags(prompt: str):
    urls = []
    flags = {}
    current_rwe = False
    for line in prompt.splitlines():
        low = line.lower()
        if "assess these links for rwe" in low or "assess these links for real-world evidence" in low:
            current_rwe = True
            continue
        for match in re.finditer(r"https?://[^\s)]+", line):
            url = clean_url(match.group(0))
            if url not in flags:
                urls.append(url)
                trailing = low[match.end() :]
                flags[url] = current_rwe or bool(
                    re.search(r"\b(rwe|maybe|phase\s*4|phase\s*iv|yes)\b", trailing)
                )
    return urls, flags


def norm_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def title_case_brand(value: str) -> str:
    value = re.sub(r"[-_]+", " ", value)
    value = re.sub(r"\b(hcp|pro|rx|ecp|usa|us|for|healthcare|professional|professionals)\b", "", value, flags=re.I)
    value = re.sub(r"\s+", " ", value).strip(" -|:")
    if not value:
        return ""
    words = []
    for word in value.split():
        if word.isupper() and len(word) <= 6:
            words.append(word)
        else:
            words.append(word[:1].upper() + word[1:].lower())
    return " ".join(words)


def brand_from_url(url: str) -> str:
    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.strip("/")
    host = host[4:] if host.startswith("www.") else host
    first = host.split(".")[0]
    if first in {"hcp", "pro", "medicalinformation", "payercoverage", "global"}:
        parts = [p for p in path.split("/") if p]
        if parts:
            return title_case_brand(parts[-1])
        if len(host.split(".")) > 1:
            first = host.split(".")[1]
    for suffix in ["hcp", "pro", "rx", "ecp", "usa"]:
        if first.endswith(suffix) and len(first) > len(suffix) + 2:
            first = first[: -len(suffix)]
            break
    return title_case_brand(first)


def extract_brand(title: str, text: str, url: str) -> str:
    url_brand = brand_from_url(url)
    candidates = []
    for source in [title, text[:3000]]:
        for pattern in [
            r"\b([A-Z][A-Z0-9\-]{2,20})\s*\(([^)]{3,80})\)",
            r"\b([A-Z][A-Za-z0-9\-]{2,20})\s+for Healthcare Professionals",
            r"\b([A-Z][A-Za-z0-9\-]{2,20})\s+HCP",
        ]:
            for m in re.finditer(pattern, source):
                candidates.append(m.group(1).strip("- |:"))
    if candidates:
        return title_case_brand(candidates[0])
    title_part = re.split(r"[|®™-]", title or "")[0].strip()
    title_part = re.sub(r"\b(HCP|Healthcare Professionals?|Official Site|For Professionals?)\b", "", title_part, flags=re.I)
    bad_title = re.search(
        r"^(home|information|patient site|pharma|hcp|resources|access denied|403|404|site map)$",
        title_part,
        re.I,
    )
    if 2 <= len(title_part) <= 36 and not bad_title:
        return title_case_brand(title_part)
    return url_brand


def extract_generic(title: str, text: str) -> str:
    source = f"{title} {text[:6000]}"
    patterns = [
        r"\b[A-Z][A-Z0-9\-]{2,24}\s*\(([^)]{3,120})\)",
        r"\bgeneric(?: name)?:?\s*([a-z][a-z0-9\-/ ]{3,80})",
        r"\b(active ingredient|contains)\s+([a-z][a-z0-9\-/ ]{3,80})",
    ]
    for pattern in patterns:
        m = re.search(pattern, source, re.I)
        if m:
            generic = m.group(2) if len(m.groups()) > 1 else m.group(1)
            generic = re.sub(r"\b(tablets?|capsules?|injection|for.*|oral.*|cream|gel|solution|suspension).*$", "", generic, flags=re.I)
            generic = norm_text(generic).strip(" .;:,")
            if re.search(r"\b(placebo|patients?|subjects?|study|week|baseline|randomized|primary endpoint|copyright|all rights|n\s*=|mg\b|%)\b", generic, re.I):
                continue
            if len(generic) > 70 or len(generic) < 4:
                continue
            if not re.search(r"[a-z]", generic):
                continue
            return generic
    return ""


def extract_company(text: str, url: str) -> str:
    host = urlparse(url).netloc.lower()
    full = f"{host} {text[:12000]}"
    for hint, company in DOMAIN_COMPANY_HINTS.items():
        if hint in host:
            return company
    for company in COMPANY_PATTERNS:
        if re.search(rf"\b{re.escape(company)}\b", full, re.I):
            return company
    m = re.search(r"(?:©|\(c\)|copyright)\s*(?:20\d\d)?\s*([A-Z][A-Za-z0-9&+.,' -]{2,60})", full)
    if m:
        company = norm_text(m.group(1))
        company = re.split(r"\b(All rights|US-|PP-|PR-|Last updated|Privacy)\b", company, flags=re.I)[0]
        return company.strip(" .")
    return ""


def classify_rwe(text: str) -> tuple[str, str]:
    low = text.lower()
    found = []
    for term in RWE_TERMS:
        if term in low:
            found.append(term)
    found = sorted(set(found))
    if any(t in found for t in ["real-world evidence", "real world evidence", "real-world data", "real world data", "claims database", "claims data", "registry", "phase 4", "phase iv", "observational"]):
        return "explicit_rwe_language_found", "; ".join(found)
    if found:
        return "possible_rwe_related_language_found", "; ".join(found)
    return "no_explicit_rwe_language_found", ""


def rgb_to_hex(value: str) -> str:
    if not value or value == "transparent":
        return ""
    nums = re.findall(r"[\d.]+", value)
    if len(nums) < 3:
        return ""
    r, g, b = [max(0, min(255, int(float(n)))) for n in nums[:3]]
    if len(nums) >= 4 and float(nums[3]) == 0:
        return ""
    return f"#{r:02X}{g:02X}{b:02X}"


def color_score(hex_color: str, weight: float) -> float:
    r = int(hex_color[1:3], 16) / 255
    g = int(hex_color[3:5], 16) / 255
    b = int(hex_color[5:7], 16) / 255
    mx, mn = max(r, g, b), min(r, g, b)
    sat = 0 if mx == 0 else (mx - mn) / mx
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    neutral_penalty = 0.2 if sat < 0.08 else 1.0
    edge_penalty = 0.35 if lum < 0.06 or lum > 0.94 else 1.0
    return weight * (0.35 + sat) * neutral_penalty * edge_penalty


def distinct_palette(counter: Counter, limit: int = 6):
    ranked = sorted(counter.items(), key=lambda kv: color_score(kv[0], kv[1]), reverse=True)
    picked = []
    for color, _ in ranked:
        if color in {"#FFFFFF", "#000000"}:
            continue
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if lum > 246:
            continue
        def dist(c):
            return math.sqrt(
                (r - int(c[1:3], 16)) ** 2
                + (g - int(c[3:5], 16)) ** 2
                + (b - int(c[5:7], 16)) ** 2
            )
        if all(dist(c) > 42 for c in picked):
            picked.append(color)
        if len(picked) >= limit:
            break
    if not picked:
        picked = [c for c, _ in ranked[:limit]]
    return picked


async def rendered_extract(page, url: str):
    await page.goto(url, wait_until="domcontentloaded", timeout=18000)
    try:
        await page.wait_for_load_state("networkidle", timeout=4500)
    except Exception:
        pass
    for label in ["Accept", "I Accept", "Continue", "Enter", "I am a Healthcare Professional", "Healthcare Professional"]:
        try:
            locator = page.get_by_text(label, exact=False).first
            if await locator.count():
                await locator.click(timeout=1200)
                await page.wait_for_timeout(800)
                break
        except Exception:
            pass
    data = await page.evaluate(
        """() => {
          const meta = {};
          document.querySelectorAll('meta[name],meta[property]').forEach(m => {
            const key = (m.getAttribute('name') || m.getAttribute('property') || '').toLowerCase();
            const val = m.getAttribute('content') || '';
            if (key && val) meta[key] = val;
          });
          const colors = {};
          const add = (value, weight) => {
            if (!value || value === 'transparent') return;
            const key = value.trim();
            colors[key] = (colors[key] || 0) + weight;
          };
          const all = Array.from(document.querySelectorAll('body *')).slice(0, 4500);
          for (const el of all) {
            const cs = getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            const area = Math.max(1, Math.min(400000, Math.abs(rect.width * rect.height)));
            add(cs.backgroundColor, area / 200);
            add(cs.color, Math.max(1, (el.innerText || '').length) / 20);
            add(cs.borderTopColor, 1);
            add(cs.fill, 1);
          }
          return {
            title: document.title || '',
            finalUrl: location.href,
            meta,
            text: document.body ? document.body.innerText : '',
            colors
          };
        }"""
    )
    return data


def http_extract(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=18, allow_redirects=True)
    soup = BeautifulSoup(resp.text, "html.parser")
    meta = {}
    for tag in soup.select("meta[name],meta[property]"):
        key = (tag.get("name") or tag.get("property") or "").lower()
        if key:
            meta[key] = tag.get("content") or ""
    text = soup.get_text(" ", strip=True)
    colors = Counter()
    for color in re.findall(r"#[0-9a-fA-F]{3,8}\b", resp.text):
        if len(color) == 4:
            color = "#" + "".join(ch * 2 for ch in color[1:])
        if len(color) == 7:
            colors[color.upper()] += 12
    return {
        "title": soup.title.get_text(" ", strip=True) if soup.title else "",
        "finalUrl": resp.url,
        "meta": meta,
        "text": text,
        "colors": dict(colors),
        "status_code": resp.status_code,
    }


async def process_one(context, url: str, prompt_flag: bool):
    notes = ["Chrome plugin unavailable in this worker session; used Playwright/HTTP fallback."]
    status = "ok"
    data = {}
    try:
        page = await context.new_page()
        try:
            data = await rendered_extract(page, url)
            status = "rendered"
        finally:
            await page.close()
    except Exception as exc:
        notes.append(f"render_failed: {type(exc).__name__}: {str(exc)[:120]}")
        try:
            data = http_extract(url)
            status = f"http_{data.get('status_code', 'ok')}"
        except Exception as http_exc:
            status = "error"
            notes.append(f"http_failed: {type(http_exc).__name__}: {str(http_exc)[:160]}")
            data = {"title": "", "finalUrl": "", "meta": {}, "text": "", "colors": {}}

    title = norm_text(data.get("title", ""))
    meta = data.get("meta") or {}
    meta_text = " ".join(str(v) for v in meta.values())
    text = norm_text(" ".join([title, meta_text, data.get("text", "")]))
    color_counter = Counter()
    for raw, weight in (data.get("colors") or {}).items():
        hx = raw if isinstance(raw, str) and raw.startswith("#") else rgb_to_hex(raw)
        if hx and len(hx) == 7:
            color_counter[hx.upper()] += float(weight or 1)
    palette = distinct_palette(color_counter)
    brand = extract_brand(title, text, url)
    generic = extract_generic(title, text)
    company = extract_company(text, data.get("finalUrl") or url)
    rwe_assessment, rwe_terms = classify_rwe(text)
    if status == "error":
        rwe_assessment = "not_assessed_fetch_failed"

    return {
        "input_url": url,
        "final_url": data.get("finalUrl") or "",
        "status": status,
        "brand_name": brand,
        "generic_name": generic,
        "company": company,
        "color_scheme_hex": "; ".join(palette),
        "primary_hex": palette[0] if len(palette) > 0 else "",
        "secondary_hex": palette[1] if len(palette) > 1 else "",
        "accent_hex": palette[2] if len(palette) > 2 else "",
        "rwe_prompt_flag": "yes" if prompt_flag else "no",
        "rwe_assessment": rwe_assessment,
        "rwe_evidence_terms": rwe_terms,
        "notes": " ".join(notes),
    }


async def main():
    prompt = inherited_prompt()
    urls, flags = parse_urls_and_flags(prompt)
    chunk = [(i, u) for i, u in enumerate(urls) if i % 6 == 1]
    (TMP / "worker_1_urls.json").write_text(
        json.dumps({"total_deduped": len(urls), "chunk_count": len(chunk), "chunk": chunk}, indent=2),
        encoding="utf-8",
    )
    rows = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 1100},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
            ),
            ignore_https_errors=True,
        )
        sem = asyncio.Semaphore(4)

        async def run(index_url):
            idx, u = index_url
            async with sem:
                row = await process_one(context, u, flags.get(u, False))
                row["notes"] = f"source_index={idx}. {row['notes']}"
                print(f"{len(rows)+1:03d}/{len(chunk)} {idx} {u} {row['status']}", flush=True)
                rows.append(row)

        await asyncio.gather(*(run(item) for item in chunk))
        await context.close()
        await browser.close()

    order = {u: n for n, (_, u) in enumerate(chunk)}
    rows.sort(key=lambda r: order[r["input_url"]])
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} rows={len(rows)}", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
