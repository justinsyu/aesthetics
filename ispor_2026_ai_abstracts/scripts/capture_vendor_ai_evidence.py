#!/usr/bin/env python3
"""Crawl vendor websites for AI-offering evidence and capture highlighted screenshots."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import textwrap
import time
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from PIL import Image
from playwright.sync_api import sync_playwright
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


ROOT = Path("/Users/justinyu/Desktop/linkedin-posts/ispor_2026_ai_abstracts")
INPUT_SUMMARY = ROOT / "vendors" / "vendor_summary.json"
OUT = ROOT / "vendor_ai_evidence"
SCREENSHOTS = OUT / "screenshots"
PDF_PATH = OUT / "vendor_ai_evidence_screenshots.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

AI_TERMS = [
    "artificial intelligence",
    "generative ai",
    "genai",
    "machine learning",
    "predictive analytics",
    "natural language processing",
    "large language model",
    "llm",
    "ai-powered",
    "ai enabled",
    "ai-enabled",
    "automation",
    "automated",
    "data science",
]

OFFERING_TERMS = [
    "service",
    "services",
    "solution",
    "solutions",
    "platform",
    "product",
    "software",
    "technology",
    "capabilities",
    "we help",
    "we provide",
    "we offer",
    "offering",
    "support",
    "powered",
    "enables",
    "accelerate",
]

URL_HINTS = [
    "ai",
    "artificial",
    "machine-learning",
    "machine_learning",
    "generative",
    "genai",
    "data-science",
    "predictive",
    "analytics",
    "automation",
    "platform",
    "technology",
    "solutions",
    "services",
    "capabilities",
    "real-world",
    "evidence",
    "heor",
]


DOMAINS = {
    # likely vendors
    "Amazon Web Services": "https://aws.amazon.com",
    "argenx": "https://www.argenx.com",
    "Arysana": "https://arysana.com",
    "AstraZeneca": "https://www.astrazeneca.com",
    "AureusIQ": "https://www.aureusiq.com",
    "BeOne Medicines": "https://www.beonemedicines.com",
    "Booz Allen Hamilton": "https://www.boozallen.com",
    "Boston Scientific": "https://www.bostonscientific.com",
    "Columbia Data Analytics": "https://www.columbiadataanalytics.com",
    "ConnectHEOR": "https://www.connectheor.com",
    "Costello Medical": "https://www.costellomedical.com",
    "Covalence Research": "https://covalenceresearch.com",
    "Cytel": "https://www.cytel.com",
    "DataUnite": "https://www.dataunite.com",
    "EasySLR": "https://www.easyslr.com",
    "EVERSANA": "https://www.eversana.com",
    "Evidence Prime": "https://www.evidenceprime.com",
    "Evidinno Outcomes Research": "https://evidinno.com",
    "Eviviz": "https://eviviz.com",
    "Flatiron Health": "https://flatiron.com",
    "Forian": "https://www.forian.com",
    "Gilead Sciences": "https://www.gilead.com",
    "GSK": "https://www.gsk.com",
    "Heorlytics": "https://heorlytics.com",
    "Johnson & Johnson": "https://www.jnj.com",
    "Keiji.AI": "https://keiji.ai",
    "Klick Health": "https://www.klick.com",
    "KolateAI PharmaTech": "https://www.kolate.ai",
    "Landmark Science": "https://www.landmarkscience.com",
    "McKesson": "https://www.mckesson.com",
    "Menarini Group": "https://www.menarini.com",
    "Merck & Co.": "https://www.merck.com",
    "Microsoft": "https://www.microsoft.com",
    "MILLER ECONOMICS": "https://www.millereconomics.com",
    "NAMina Bio": "https://www.naminabio.com",
    "Nested Knowledge": "https://nested-knowledge.com",
    "Novo Nordisk": "https://www.novonordisk.com",
    "Oncoscope-AI": "https://oncoscope.com",
    "Ontada": "https://www.ontada.com",
    "OPEN Health": "https://www.openhealthgroup.com",
    "Optum": "https://www.optum.com",
    "Oracle Life Sciences": "https://www.oracle.com/life-sciences/",
    "Parexel": "https://www.parexel.com",
    "Pfizer": "https://www.pfizer.com",
    "Pharmacoevidence": "https://www.pharmacoevidence.com",
    "PharmaQuant": "https://www.pharmaquant.org",
    "PHAROS Labs": "https://www.pharos-labs.com",
    "Precision AQ": "https://www.precisionaq.com",
    "Principal Health Economics": "https://www.principalhealtheconomics.com",
    "Regeneron Pharmaceuticals": "https://www.regeneron.com",
    "Sandpiper Analytics": "https://www.sandpiperanalytics.com",
    "Sarepta Therapeutics": "https://www.sarepta.com",
    "SAS Institute": "https://www.sas.com",
    "Skyward Analytics": "https://www.skywardanalytics.com",
    "Star Biopharma Consulting": "https://www.starbiopharmaconsulting.com",
    "Swipha Pharma Nig": "https://swipharma.com",
    "Systematic Review Ltd.": "https://systematicreviewltd.com",
    "Takeda Pharmaceuticals": "https://www.takeda.com",
    "Teva Pharmaceuticals": "https://www.tevapharm.com",
    "The Synthesis Company of California": "https://www.thesynthesis.company",
    "Thermo Fisher Scientific": "https://www.thermofisher.com",
    "Trinity Life Sciences": "https://trinitylifesciences.com",
    "Truveta": "https://www.truveta.com",
    "Value Analytics Labs": "https://www.valueanalyticslabs.com",
    "Veev Consulting": "https://www.veevconsulting.com",
    "Xplain Data": "https://xplaindata.com",
    "ZS Associates": "https://www.zs.com",
    # manual-review organizations
    "Carevive": "https://www.carevive.com",
    "Dandelion Health": "https://www.dandelionhealth.ai",
    "Harvey L. Neiman Health Policy Institute": "https://www.neimanhpi.org",
    "Health Catalyst": "https://www.healthcatalyst.com",
    "HTA-Hive": "https://www.htahive.com",
    "JPS Healthcare": "https://www.jpshealthnet.org",
    "Knight Therapeutics": "https://www.knighttx.com",
    "Northwell": "https://www.northwell.edu",
    "Oncomed BH / Grupo Orizonti": "https://www.oncomedbh.com.br",
    "Pomelo Care": "https://www.pomelocare.com",
    "Sciensus": "https://www.sciensus.com",
    "Syreon Research Institute": "https://syreon.eu",
    "Unimed-BH": "https://www.unimedbh.com.br",
    # no general public organization site to crawl
    "Independent Consultant": None,
    "PAIML Scientific Working Group": None,
}


@dataclass
class Candidate:
    vendor: str
    status: str
    category: str
    url: str
    title: str
    score: int
    support_text: str
    source: str


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80]


def norm_url(url: str, base: str | None = None) -> str | None:
    if not url:
        return None
    absolute = urllib.parse.urljoin(base or "", url)
    parsed = urllib.parse.urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    parsed = parsed._replace(fragment="")
    return urllib.parse.urlunparse(parsed)


def same_site(url: str, root: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
    root_host = urllib.parse.urlparse(root).netloc.lower().replace("www.", "")
    return host == root_host or host.endswith("." + root_host)


def fetch(url: str, timeout: int = 12) -> requests.Response | None:
    try:
        return requests.get(url, headers=HEADERS, timeout=timeout, verify=False, allow_redirects=True)
    except Exception:
        return None


def visible_text_and_title(content: str) -> tuple[str, str, list[str]]:
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    blocks = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "a", "div"]):
        text = re.sub(r"\s+", " ", tag.get_text(" ", strip=True))
        if 35 <= len(text) <= 500:
            blocks.append(text)
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    return text, title, blocks


def evidence_score(url: str, title: str, text: str, blocks: list[str]) -> tuple[int, str]:
    lower_text = text.lower()
    lower_url = url.lower()
    ai_hits = sum(1 for term in AI_TERMS if term in lower_text or term in lower_url)
    offering_hits = sum(1 for term in OFFERING_TERMS if term in lower_text or term in lower_url)
    url_hits = sum(1 for term in URL_HINTS if term in lower_url)
    support_blocks = []
    for block in blocks:
        b = block.lower()
        if any(term in b for term in AI_TERMS) and any(term in b for term in OFFERING_TERMS + ["model", "models", "analytics", "data"]):
            support_blocks.append(block)
        if len(support_blocks) >= 3:
            break
    score = ai_hits * 5 + offering_hits * 2 + url_hits + len(support_blocks) * 8
    # Penalize generic news/blog pages unless strongly offering oriented.
    if any(x in lower_url for x in ["/blog", "/news", "/press", "/article", "/insights"]) and len(support_blocks) < 2:
        score -= 5
    return score, " ".join(support_blocks)[:900]


def sitemap_urls(root: str, limit: int = 250) -> list[str]:
    urls = []
    for sitemap_path in ["/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml"]:
        sitemap = urllib.parse.urljoin(root, sitemap_path)
        response = fetch(sitemap, timeout=10)
        if not response or response.status_code >= 400 or "<" not in response.text[:100]:
            continue
        try:
            tree = ET.fromstring(response.text.encode("utf-8"))
        except Exception:
            continue
        locs = [el.text.strip() for el in tree.iter() if el.tag.endswith("loc") and el.text]
        nested = [loc for loc in locs if loc.endswith(".xml") and len(urls) < limit]
        page_locs = [loc for loc in locs if not loc.endswith(".xml")]
        urls.extend(page_locs)
        for nested_url in nested[:8]:
            nested_response = fetch(nested_url, timeout=10)
            if not nested_response or nested_response.status_code >= 400:
                continue
            try:
                nested_tree = ET.fromstring(nested_response.text.encode("utf-8"))
                urls.extend([el.text.strip() for el in nested_tree.iter() if el.tag.endswith("loc") and el.text])
            except Exception:
                pass
        if urls:
            break
    deduped = []
    seen = set()
    for url in urls:
        cleaned = norm_url(url)
        if cleaned and same_site(cleaned, root) and cleaned not in seen:
            seen.add(cleaned)
            deduped.append(cleaned)
    def priority(u: str) -> int:
        lu = u.lower()
        return sum(10 for hint in URL_HINTS if hint in lu) - len(lu) // 100
    return sorted(deduped, key=priority, reverse=True)[:limit]


def homepage_links(root: str, limit: int = 80) -> list[str]:
    response = fetch(root, timeout=12)
    if not response or response.status_code >= 400:
        return [root]
    soup = BeautifulSoup(response.text, "html.parser")
    links = [root]
    for a in soup.find_all("a", href=True):
        url = norm_url(a["href"], response.url)
        if url and same_site(url, root):
            label = f"{a.get_text(' ', strip=True)} {url}".lower()
            if any(hint.replace("-", " ") in label or hint in label for hint in URL_HINTS):
                links.append(url)
    seen = set()
    out = []
    for url in links:
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out[:limit]


def ddg_site_search(vendor: str, root: str, limit: int = 8) -> list[str]:
    host = urllib.parse.urlparse(root).netloc.replace("www.", "")
    query = f'site:{host} "{vendor}" ("AI" OR "artificial intelligence" OR "machine learning" OR "predictive analytics" OR "generative AI")'
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    response = fetch(url, timeout=12)
    if not response or response.status_code >= 400:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for a in soup.select(".result__a"):
        href = a.get("href")
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        target = qs.get("uddg", [href])[0]
        target = norm_url(target)
        if target and same_site(target, root):
            results.append(target)
    return results[:limit]


def collect_candidates(vendor: str, status: str, category: str, root: str) -> tuple[list[Candidate], str]:
    urls = []
    for source, source_urls in [
        ("sitemap", sitemap_urls(root)),
        ("homepage_links", homepage_links(root)),
        ("site_search", ddg_site_search(vendor, root)),
    ]:
        for url in source_urls:
            if url not in urls:
                urls.append(url)
    # Always include homepage for explicit AI-first companies.
    if root not in urls:
        urls.insert(0, root)
    # Keep crawl bounded but prioritize relevant paths.
    def url_priority(u: str) -> int:
        lu = u.lower()
        return sum(10 for hint in URL_HINTS if hint in lu) + (20 if any(ai in lu for ai in ["ai", "machine", "predict"]) else 0)
    urls = sorted(urls, key=url_priority, reverse=True)[:45]
    candidates = []
    errors = []
    for url in urls:
        response = fetch(url, timeout=14)
        if not response:
            errors.append(f"fetch failed: {url}")
            continue
        ctype = response.headers.get("content-type", "")
        if response.status_code >= 400 or ("text/html" not in ctype and "html" not in response.text[:200].lower()):
            continue
        text, title, blocks = visible_text_and_title(response.text)
        score, support = evidence_score(response.url, title, text, blocks)
        if score >= 18 and support:
            candidates.append(Candidate(vendor, status, category, response.url, title, score, support, "crawl"))
        time.sleep(0.05)
    # Prefer actual offering/service pages, keep up to 4 pages per organization.
    candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
    deduped = []
    seen = set()
    for c in candidates:
        if c.url in seen:
            continue
        seen.add(c.url)
        deduped.append(c)
    return deduped[:4], "; ".join(errors[:3])


def highlight_and_capture(page, item: Candidate, out_path: Path) -> tuple[bool, str]:
    page.goto(item.url, wait_until="domcontentloaded", timeout=35000)
    page.wait_for_timeout(1500)
    # Dismiss common overlays if possible.
    for label in ["Accept", "Accept All", "I Accept", "Agree", "Got it", "Allow all", "Reject All"]:
        try:
            page.get_by_text(label, exact=False).first.click(timeout=800)
            page.wait_for_timeout(400)
            break
        except Exception:
            pass
    phrases = []
    for phrase in re.split(r"(?<=[.!?])\s+", item.support_text):
        phrase = phrase.strip()
        if len(phrase) >= 50:
            phrases.append(phrase[:160])
    phrases.extend(["artificial intelligence", "generative AI", "machine learning", "AI-powered", "predictive analytics", "natural language processing"])
    page.evaluate(
        """
        (phrases) => {
          const style = document.createElement('style');
          style.textContent = `
            mark.codex-ai-evidence {
              background: #fff176 !important;
              color: #111 !important;
              padding: 0 2px !important;
              box-shadow: 0 0 0 2px rgba(255, 193, 7, .7) !important;
            }
            .codex-evidence-block {
              outline: 4px solid #1a73e8 !important;
              outline-offset: 4px !important;
              background: rgba(255, 241, 118, 0.18) !important;
            }
          `;
          document.head.appendChild(style);
          const lowerPhrases = phrases.map(p => String(p).toLowerCase()).filter(Boolean);
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
              const text = node.nodeValue || '';
              if (!text.trim() || node.parentElement?.closest('script,style,noscript,mark')) return NodeFilter.FILTER_REJECT;
              const lower = text.toLowerCase();
              return lowerPhrases.some(p => lower.includes(p) || (p.length > 30 && p.includes(lower.trim().slice(0, 30))))
                ? NodeFilter.FILTER_ACCEPT
                : NodeFilter.FILTER_REJECT;
            }
          });
          const nodes = [];
          while (walker.nextNode() && nodes.length < 20) nodes.push(walker.currentNode);
          for (const node of nodes) {
            const text = node.nodeValue;
            const lower = text.toLowerCase();
            const phrase = lowerPhrases.find(p => lower.includes(p));
            if (!phrase) continue;
            const idx = lower.indexOf(phrase);
            const range = document.createRange();
            range.setStart(node, idx);
            range.setEnd(node, idx + phrase.length);
            const mark = document.createElement('mark');
            mark.className = 'codex-ai-evidence';
            try {
              range.surroundContents(mark);
              const block = mark.closest('p,li,h1,h2,h3,section,article,div');
              if (block) block.classList.add('codex-evidence-block');
            } catch {}
          }
          const first = document.querySelector('mark.codex-ai-evidence, .codex-evidence-block');
          if (first) first.scrollIntoView({block: 'center', inline: 'nearest'});
          return Boolean(first);
        }
        """,
        phrases,
    )
    page.wait_for_timeout(800)
    page.screenshot(path=str(out_path), full_page=False)
    return True, page.url


def build_pdf(evidence_rows: list[dict], no_evidence_rows: list[dict]) -> None:
    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(letter))
    width, height = landscape(letter)
    c.setTitle("Vendor AI Evidence Screenshots")

    def draw_header(title: str, subtitle: str = ""):
        c.setFillColor(colors.HexColor("#10120f"))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(0.45 * inch, height - 0.45 * inch, title[:115])
        if subtitle:
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor("#55584f"))
            c.drawString(0.45 * inch, height - 0.65 * inch, subtitle[:170])

    draw_header("Vendor AI Offering / Services Evidence", "Screenshots from public websites with highlighted supporting text")
    c.setFont("Helvetica", 10)
    c.drawString(0.45 * inch, height - 1.0 * inch, f"Evidence screenshots: {len(evidence_rows)}")
    c.drawString(0.45 * inch, height - 1.22 * inch, f"Organizations with no captured evidence or no site to crawl: {len(no_evidence_rows)}")
    c.drawString(0.45 * inch, height - 1.55 * inch, "The PDF labels each screenshot with organization, classification status, URL, and supporting text excerpt.")
    c.showPage()

    for row in evidence_rows:
        draw_header(f"{row['vendor']} [{row['status']}]", row["url"])
        c.setFont("Helvetica", 7.4)
        c.setFillColor(colors.HexColor("#333333"))
        support = row.get("support_text", "")
        y = height - 0.87 * inch
        for line in textwrap.wrap(f"Highlighted support: {support}", width=170)[:3]:
            c.drawString(0.45 * inch, y, line)
            y -= 0.14 * inch
        img_path = row.get("screenshot_path")
        if img_path and Path(img_path).exists():
            with Image.open(img_path) as im:
                iw, ih = im.size
            max_w = width - 0.9 * inch
            max_h = height - 1.35 * inch
            scale = min(max_w / iw, max_h / ih)
            draw_w = iw * scale
            draw_h = ih * scale
            c.drawImage(img_path, 0.45 * inch, 0.35 * inch, width=draw_w, height=draw_h, preserveAspectRatio=True)
        c.showPage()

    draw_header("Organizations without captured AI offering/service screenshot")
    c.setFont("Helvetica", 8)
    y = height - 0.8 * inch
    for row in no_evidence_rows:
        text = f"{row['vendor']} [{row['status']}]: {row.get('reason', '')} {row.get('site', '')}"
        for line in textwrap.wrap(text, width=155):
            if y < 0.5 * inch:
                c.showPage()
                draw_header("Organizations without captured AI offering/service screenshot")
                c.setFont("Helvetica", 8)
                y = height - 0.8 * inch
            c.drawString(0.45 * inch, y, line)
            y -= 0.16 * inch
        y -= 0.06 * inch
    c.save()


def main() -> None:
    requests.packages.urllib3.disable_warnings()  # local evidence collection, some vendor SSL chains are incomplete.
    OUT.mkdir(exist_ok=True)
    SCREENSHOTS.mkdir(exist_ok=True)
    summary = json.loads(INPUT_SUMMARY.read_text())
    organizations = []
    for entry in summary:
        name = entry["name"]
        organizations.append(
            {
                "vendor": name,
                "status": entry["status"],
                "category": entry["category"],
                "site": DOMAINS.get(name),
            }
        )

    evidence_items: list[Candidate] = []
    no_evidence_rows: list[dict] = []
    crawl_rows: list[dict] = []
    for org in organizations:
        site = org["site"]
        if not site:
            no_evidence_rows.append({**org, "reason": "No general public organization website assigned for crawl"})
            continue
        print(f"crawl {org['vendor']} -> {site}", flush=True)
        candidates, errors = collect_candidates(org["vendor"], org["status"], org["category"], site)
        crawl_rows.append({**org, "candidate_count": len(candidates), "errors": errors})
        if not candidates:
            no_evidence_rows.append({**org, "reason": "No public page with explicit AI-offering/service evidence captured by bounded crawl"})
        evidence_items.extend(candidates)

    evidence_rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 950}, device_scale_factor=1)
        page = context.new_page()
        for i, item in enumerate(evidence_items, start=1):
            safe = slugify(f"{i:03d}-{item.vendor}")
            digest = hashlib.sha1(item.url.encode()).hexdigest()[:8]
            shot_path = SCREENSHOTS / f"{safe}-{digest}.png"
            try:
                print(f"screenshot {i}/{len(evidence_items)} {item.vendor}: {item.url}", flush=True)
                ok, final_url = highlight_and_capture(page, item, shot_path)
                evidence_rows.append(
                    {
                        "vendor": item.vendor,
                        "status": item.status,
                        "category": item.category,
                        "url": final_url,
                        "title": item.title,
                        "score": item.score,
                        "support_text": item.support_text,
                        "screenshot_path": str(shot_path),
                    }
                )
            except Exception as exc:
                no_evidence_rows.append(
                    {
                        "vendor": item.vendor,
                        "status": item.status,
                        "category": item.category,
                        "site": item.url,
                        "reason": f"Screenshot capture failed: {exc}",
                    }
                )
        context.close()
        browser.close()

    with (OUT / "vendor_ai_evidence_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["vendor", "status", "category", "url", "title", "score", "support_text", "screenshot_path"],
        )
        writer.writeheader()
        writer.writerows(evidence_rows)
    (OUT / "vendor_ai_evidence_manifest.json").write_text(json.dumps(evidence_rows, indent=2), encoding="utf-8")

    with (OUT / "vendor_ai_no_evidence.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["vendor", "status", "category", "site", "reason"])
        writer.writeheader()
        writer.writerows(no_evidence_rows)
    (OUT / "vendor_ai_crawl_log.json").write_text(json.dumps(crawl_rows, indent=2), encoding="utf-8")

    build_pdf(evidence_rows, no_evidence_rows)
    print(
        json.dumps(
            {
                "organizations": len(organizations),
                "evidence_screenshots": len(evidence_rows),
                "no_evidence_or_failed": len(no_evidence_rows),
                "pdf": str(PDF_PATH),
                "manifest": str(OUT / "vendor_ai_evidence_manifest.csv"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
