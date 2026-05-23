#!/usr/bin/env python3
import argparse
import asyncio
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCREENSHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"

DISCOVERY_TERMS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "generative ai",
    "genai",
    "large language model",
    "llm",
    "natural language processing",
    "nlp",
    "predictive",
    "algorithm",
    "automation",
    "automated",
    "software",
    "platform",
    "analytics",
    "data science",
    "real-world evidence",
    "real world evidence",
    "evidence generation",
    "systematic literature review",
    "literature review",
]

AI_TERMS = [
    "artificial intelligence",
    "generative ai",
    "genai",
    "machine learning",
    "large language model",
    "large language models",
    "llm",
    "llms",
    "natural language processing",
    "nlp",
    "deep learning",
    "ai-enabled",
    "ai powered",
    "ai-powered",
]

AI_REGEX = re.compile(
    r"\b("
    r"artificial intelligence|generative ai|genai|machine learning|"
    r"large language models?|llms?|natural language processing|nlp|"
    r"deep learning|ai[- ]enabled|ai[- ]powered|ai"
    r")\b",
    re.I,
)

OFFERING_TERMS = [
    "platform",
    "solution",
    "solutions",
    "service",
    "services",
    "software",
    "analytics",
    "automation",
    "automated",
    "evidence",
    "research",
    "clinical",
    "health economics",
    "heor",
    "market access",
]

SKIP_EXTENSIONS = re.compile(r"\.(pdf|docx?|xlsx?|pptx?|zip|jpg|jpeg|png|gif|svg|webp|mp4|mov|avi|mp3)(\?|$)", re.I)
SKIP_URL_PARTS = re.compile(r"(login|signin|sign-in|register|cart|checkout|privacy|terms|cookie|careers?/apply|jobs?/apply)", re.I)


def slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:80] or "vendor"


def norm_url(url: str) -> str:
    url = urldefrag(url)[0]
    parsed = urlparse(url)
    if not parsed.scheme:
        return ""
    path = parsed.path or "/"
    return parsed._replace(path=path, fragment="").geturl()


def root_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/"


def host_key(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def same_site(url: str, base: str) -> bool:
    h = host_key(url)
    b = host_key(base)
    return h == b or h.endswith("." + b) or b.endswith("." + h)


def score_text(text: str, url: str = "") -> int:
    hay = f"{url} {text}".lower()
    score = 0
    score += 8 * len(AI_REGEX.findall(hay))
    for term in DISCOVERY_TERMS:
        if term in hay:
            score += 2
    for term in OFFERING_TERMS:
        if term in hay:
            score += 1
    return score


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


async def get_page_text(page) -> str:
    return await page.evaluate(
        """() => {
          const tags = ['script','style','noscript','svg','canvas'];
          tags.forEach(t => document.querySelectorAll(t).forEach(n => n.remove()));
          return document.body ? document.body.innerText : document.documentElement.innerText;
        }"""
    )


async def highlight_terms(page) -> int:
    terms = AI_TERMS + ["AI", "predictive analytics", "automation", "automated", "data science"]
    return await page.evaluate(
        """(terms) => {
          const escaped = terms
            .filter(Boolean)
            .map(t => t.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'))
            .sort((a,b) => b.length - a.length);
          const rx = new RegExp('(?<![A-Za-z0-9])(' + escaped.join('|') + ')(?![A-Za-z0-9])', 'gi');
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
              if (!node.nodeValue || !rx.test(node.nodeValue)) return NodeFilter.FILTER_REJECT;
              rx.lastIndex = 0;
              const parent = node.parentElement;
              if (!parent) return NodeFilter.FILTER_REJECT;
              const tag = parent.tagName.toLowerCase();
              if (['script','style','noscript','textarea','input','mark'].includes(tag)) return NodeFilter.FILTER_REJECT;
              return NodeFilter.FILTER_ACCEPT;
            }
          });
          const nodes = [];
          while (walker.nextNode()) nodes.push(walker.currentNode);
          let count = 0;
          for (const node of nodes) {
            const span = document.createElement('span');
            span.innerHTML = node.nodeValue.replace(rx, '<mark class="codex-ai-highlight">$1</mark>');
            count += (span.innerHTML.match(/codex-ai-highlight/g) || []).length;
            node.parentNode.replaceChild(span, node);
          }
          const style = document.createElement('style');
          style.textContent = `
            mark.codex-ai-highlight {
              background: #fff176 !important;
              color: #000 !important;
              box-shadow: 0 0 0 2px #f9a825 !important;
              border-radius: 2px !important;
              padding: 0 2px !important;
            }
          `;
          document.head.appendChild(style);
          return count;
        }""",
        terms,
    )


async def collect_links(page, base: str) -> list[str]:
    hrefs = await page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)"""
    )
    out = []
    for href in hrefs:
        url = norm_url(href)
        if not url or not same_site(url, base):
            continue
        if SKIP_EXTENSIONS.search(url) or SKIP_URL_PARTS.search(url):
            continue
        out.append(url)
    return sorted(set(out))


async def try_fetch_text(request, url: str) -> str:
    try:
        response = await request.get(url, timeout=12000)
        if not response.ok:
            return ""
        return await response.text()
    except Exception:
        return ""


async def sitemap_urls(request, base: str, max_urls: int) -> list[str]:
    seeds = [urljoin(root_url(base), "sitemap.xml")]
    found = []
    seen_sitemaps = set()
    while seeds and len(found) < max_urls:
        sm_url = seeds.pop(0)
        if sm_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sm_url)
        body = await try_fetch_text(request, sm_url)
        if not body or "<" not in body[:100]:
            continue
        try:
            root = ET.fromstring(body.encode("utf-8"))
        except Exception:
            continue
        for loc in root.findall(".//{*}loc"):
            loc_text = (loc.text or "").strip()
            if not loc_text:
                continue
            if loc_text.endswith(".xml") and same_site(loc_text, base):
                seeds.append(loc_text)
            elif same_site(loc_text, base):
                url = norm_url(loc_text)
                if url and not SKIP_EXTENSIONS.search(url) and not SKIP_URL_PARTS.search(url):
                    found.append(url)
            if len(found) >= max_urls:
                break
    return sorted(set(found))


async def crawl_vendor(browser, request, row: dict, args) -> dict:
    vendor = row["display_name"]
    website = row.get("website") or ""
    record = {
        "display_name": vendor,
        "booth": row.get("booth", ""),
        "website": website,
        "website_source": row.get("website_source", ""),
        "profile_url": row.get("profile_url", ""),
        "event_about": row.get("event_about", ""),
        "pages_visited": [],
        "ai_pages": [],
        "screenshots": [],
        "errors": [],
    }
    if not website:
        record["errors"].append("No website resolved.")
        return record

    base = root_url(website)
    context = await browser.new_context(
        viewport={"width": 1440, "height": 1000},
        user_agent="Mozilla/5.0 AppleWebKit/537.36 Chrome/124 Safari/537.36",
        ignore_https_errors=True,
    )
    page = await context.new_page()
    queue = [base]
    try:
        for u in await sitemap_urls(request, base, args.max_sitemap_urls):
            if score_text("", u) >= 2:
                queue.append(u)
    except Exception as exc:
        record["errors"].append(f"sitemap discovery failed: {exc!r}")
    queue = list(dict.fromkeys(queue))
    visited = set()
    candidate_links = []
    try:
        while queue and len(visited) < args.max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=args.timeout_ms)
                await page.wait_for_timeout(1200)
                final_url = norm_url(page.url)
                if not same_site(final_url, base):
                    continue
                title = clean_text(await page.title())
                text = clean_text(await get_page_text(page))
                text_score = score_text(text, final_url)
                record["pages_visited"].append({"url": final_url, "title": title, "score": text_score})
                links = await collect_links(page, base)
                for link in links:
                    if link not in visited and score_text("", link) >= 2:
                        candidate_links.append(link)
                for link in candidate_links:
                    if link not in visited and link not in queue:
                        queue.append(link)

                has_ai = bool(AI_REGEX.search(text))
                if has_ai and text_score >= args.min_ai_score:
                    highlights = await highlight_terms(page)
                    digest = hashlib.sha1(final_url.encode()).hexdigest()[:10]
                    shot_dir = SCREENSHOTS / slug(vendor)
                    shot_dir.mkdir(parents=True, exist_ok=True)
                    shot_path = shot_dir / f"{digest}.png"
                    try:
                        await page.screenshot(path=str(shot_path), full_page=True)
                    except Exception as exc:
                        record["errors"].append(f"{final_url}: full-page screenshot failed, retried viewport: {exc!r}")
                        await page.screenshot(path=str(shot_path), full_page=False)
                    snippets = []
                    lower = text.lower()
                    for term in AI_TERMS:
                        idx = lower.find(term.strip())
                        if idx >= 0:
                            snippets.append(text[max(0, idx - 220) : min(len(text), idx + 420)])
                    page_record = {
                        "url": final_url,
                        "title": title,
                        "score": text_score,
                        "highlight_count": highlights,
                        "screenshot": str(shot_path),
                        "snippets": snippets[:3],
                    }
                    record["ai_pages"].append(page_record)
                    record["screenshots"].append(str(shot_path))
            except Exception as exc:
                record["errors"].append(f"{url}: {exc!r}")
    finally:
        await context.close()
    return record


async def main_async(args) -> None:
    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    selected = rows[args.start : args.end]
    out_records = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--disable-dev-shm-usage", "--disable-quic", "--disable-http2"],
        )
        request = p.request
        req_context = await request.new_context(ignore_https_errors=True)
        sem = asyncio.Semaphore(args.concurrency)

        async def run(row):
            async with sem:
                print(f"crawling {row['display_name']}", flush=True)
                try:
                    return await crawl_vendor(browser, req_context, row, args)
                except Exception as exc:
                    return {
                        "display_name": row.get("display_name", ""),
                        "booth": row.get("booth", ""),
                        "website": row.get("website", ""),
                        "website_source": row.get("website_source", ""),
                        "profile_url": row.get("profile_url", ""),
                        "event_about": row.get("event_about", ""),
                        "pages_visited": [],
                        "ai_pages": [],
                        "screenshots": [],
                        "errors": [f"vendor crawl failed: {exc!r}"],
                    }

        tasks = [asyncio.create_task(run(row)) for row in selected]
        for task in asyncio.as_completed(tasks):
            out_records.append(await task)
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(json.dumps(out_records, indent=2, ensure_ascii=False), encoding="utf-8")
        await req_context.dispose()
        await browser.close()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out_records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(out_records)} vendor crawl records to {args.output}")


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DATA / "ispor26_exhibitors_with_websites.json"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=sys.maxsize)
    parser.add_argument("--max-pages", type=int, default=35)
    parser.add_argument("--max-sitemap-urls", type=int, default=250)
    parser.add_argument("--min-ai-score", type=int, default=8)
    parser.add_argument("--timeout-ms", type=int, default=18000)
    parser.add_argument("--concurrency", type=int, default=2)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    started = time.time()
    asyncio.run(main_async(args))
    print(f"elapsed_sec={time.time() - started:.1f}")


if __name__ == "__main__":
    main()
