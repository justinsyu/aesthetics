#!/usr/bin/env python3
import csv
import html
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


BASE = Path("/Users/justinyu/Desktop/linkedin-posts")
INPUT = BASE / "outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv"
OUT_DIR = BASE / "outputs/hcp_promotional_message_audit"
OUT_CSV = OUT_DIR / "hcp_site_promotional_messages.csv"
SUMMARY_JSON = OUT_DIR / "promotional_message_summary.json"

FIELDS = [
    "source_index",
    "url",
    "final_url",
    "brand_name",
    "generic_name",
    "company",
    "promotional_message_verbatim",
    "message_word_count",
    "message_source",
    "message_theme",
    "claim_type",
    "call_to_action",
    "why_selected",
    "access_status",
    "http_status",
    "blocked_or_error",
    "notes",
    "retrieved_at",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

BAD_PATTERNS = [
    r"\bcookie\b",
    r"\bprivacy\b",
    r"\bterms of use\b",
    r"\bimportant safety information\b",
    r"\bindication\b",
    r"\bcontraindicat",
    r"\badverse reactions?\b",
    r"\bprescribing information\b",
    r"\bmedication guide\b",
    r"\bplease see\b",
    r"\bsee full\b",
    r"\bclick here\b",
    r"\bread more\b",
    r"\blearn more\b",
    r"\blearn about\b",
    r"\bsee information\b",
    r"\bdownload\b",
    r"\bmenu\b",
    r"\bskip to\b",
    r"\bsite map\b",
    r"\bcontact us\b",
    r"\bsign up\b",
    r"\blog in\b",
    r"\bfor medical information\b",
    r"\bthis site is intended\b",
    r"\bare you a healthcare professional\b",
    r"\bsavings (?:program|card)\b",
    r"\bvalid only\b",
    r"\bshould only be\b",
    r"\bclosely monitored\b",
    r"\bofficial (?:hcp )?site\b",
    r"\bindications and important\b",
    r"\bavailable savings\b",
    r"\boffer is only valid\b",
    r"\bcommercial insurance\b",
    r"\bcoverage support\b",
    r"\binsurance coverage\b",
    r"\bpediatric use\b",
    r"\bsafety and efficacy\b",
    r"\binfo for healthcare professionals\b",
    r"\bfor patients as young\b",
    r"\bdiscontinue\b",
    r"\bhbv reactivation\b",
    r"\bantiviral therapy\b",
    r"\belevated urine protein\b",
    r"\bsham-controlled\b",
    r"\bserious, sometimes fatal\b",
    r"\bfatal problems?\b",
    r"\bactive infection should not\b",
    r"\bshould not be treated\b",
    r"\bbenefit of treatment is considered to outweigh the risk\b",
    r"\bliver toxicity\b",
    r"\bdeveloped liver toxicity\b",
    r"\btoxicity may occur\b",
]

PROMO_TERMS = {
    "efficacy": [
        "effective",
        "efficacy",
        "improve",
        "reduce",
        "reduced",
        "relief",
        "control",
        "response",
        "remission",
        "prevent",
        "protect",
        "clearance",
        "durable",
        "sustained",
    ],
    "differentiation": [
        "first",
        "only",
        "unique",
        "different",
        "designed",
        "targeted",
        "selective",
        "advanced",
        "complete",
        "comprehensive",
    ],
    "convenience": [
        "once",
        "daily",
        "weekly",
        "monthly",
        "single",
        "ready-to-use",
        "prefilled",
        "oral",
        "at home",
        "no titration",
        "dosing",
    ],
    "patient fit": [
        "patients",
        "adults",
        "children",
        "treatment option",
        "for your patients",
        "appropriate",
        "eligible",
    ],
}

CTA_PATTERNS = [
    "learn more",
    "see the data",
    "explore",
    "get started",
    "request",
    "download",
    "watch",
    "view",
    "sign up",
]


@dataclass
class Candidate:
    text: str
    source: str
    order: int
    score: float


def clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"\s+", " ", value).strip()
    return value.strip(" |-/–—:")


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", value))


def sentences(value: str) -> Iterable[str]:
    value = clean_text(value)
    if not value:
        return []
    pieces = re.split(r"(?<=[.!?])\s+|[\n\r]+", value)
    out = []
    for piece in pieces:
        piece = clean_text(piece)
        if not piece:
            continue
        if word_count(piece) <= 25:
            out.append(piece)
            continue
        clauses = re.split(r"\s+[–—-]\s+|;\s+|:\s+", piece)
        for clause in clauses:
            clause = clean_text(clause)
            if 4 <= word_count(clause) <= 25:
                out.append(clause)
    return out


def is_bad(text: str) -> bool:
    lower = text.lower()
    if word_count(text) < 4 or word_count(text) > 25:
        return True
    if len(text) < 18 or len(text) > 190:
        return True
    if re.fullmatch(r"[A-Z0-9 .,/+-]{1,40}", text) and word_count(text) < 6:
        return True
    return any(re.search(pattern, lower) for pattern in BAD_PATTERNS)


def theme_and_claim(text: str) -> tuple[str, str]:
    lower = text.lower()
    themes = []
    for theme, terms in PROMO_TERMS.items():
        if any(term in lower for term in terms):
            themes.append(theme)
    if not themes:
        themes.append("positioning")

    if any(term in lower for term in PROMO_TERMS["efficacy"]):
        claim = "efficacy/outcome"
    elif any(term in lower for term in PROMO_TERMS["differentiation"]):
        claim = "differentiation"
    elif any(term in lower for term in PROMO_TERMS["convenience"]):
        claim = "convenience/dosing"
    elif any(term in lower for term in PROMO_TERMS["patient fit"]):
        claim = "patient fit"
    else:
        claim = "brand positioning"
    return "; ".join(themes[:3]), claim


def score_text(text: str, source: str, brand: str) -> float:
    lower = text.lower()
    score = 0.0
    if source.startswith("h1"):
        score += 8
    elif source.startswith("h2"):
        score += 6
    elif source.startswith("meta"):
        score += 5
    elif source.startswith("hero"):
        score += 5
    elif source.startswith("button") or source.startswith("a"):
        score -= 2

    brand_key = re.sub(r"[^a-z0-9]+", " ", (brand or "").lower()).strip()
    if brand_key and brand_key.split()[0] in lower:
        score += 3

    for theme, terms in PROMO_TERMS.items():
        score += sum(2 for term in terms if term in lower)

    if any(term in lower for term in ["first", "only", "proven", "demonstrated"]):
        score += 4
    if any(term in lower for term in ["discover", "give your patients", "help your patients", "offer your patients"]):
        score += 3
    if "patients" in lower or "your patients" in lower:
        score += 2
    if re.search(r"\d+%|\b\d+ (?:months|weeks|days|years)\b", lower):
        score += 2
    if any(term in lower for term in ["learn about", "see information", "overview for hcps", "official website"]):
        score -= 8
    if any(term in lower for term in ["savings", "co-pay", "financial information", "coverage support", "insurance coverage"]):
        score -= 7
    if any(
        term in lower
        for term in [
            "should only",
            "closely monitored",
            "regular follow-up",
            "contraindicat",
            "adverse",
            "safety and efficacy",
            "discontinue",
            "hbv reactivation",
            "antiviral therapy",
            "elevated urine protein",
            "sham-controlled",
            "serious, sometimes fatal",
            "should not be treated",
            "liver toxicity",
            "toxicity may occur",
        ]
    ):
        score -= 10
    if text.endswith("?"):
        score -= 1
    wc = word_count(text)
    if 7 <= wc <= 16:
        score += 2
    elif wc > 21:
        score -= 1
    return score


def source_candidates(soup: BeautifulSoup, brand: str) -> list[Candidate]:
    candidates = []
    order = 0

    def add(text: str, source: str) -> None:
        nonlocal order
        for sent in sentences(text):
            if is_bad(sent):
                continue
            candidates.append(
                Candidate(sent, source, order, score_text(sent, source, brand))
            )
            order += 1

    for name in ["description", "og:description", "twitter:description"]:
        tag = soup.find("meta", attrs={"name": name}) or soup.find(
            "meta", attrs={"property": name}
        )
        if tag and tag.get("content"):
            add(tag["content"], f"meta:{name}")

    title = soup.find("title")
    if title:
        add(title.get_text(" "), "title")

    for selector, source in [
        ("main h1", "h1"),
        ("main h2", "h2"),
        ("h1", "h1"),
        ("h2", "h2"),
        ("h3", "h3"),
        ("main p", "body:p"),
        ("p", "body:p"),
        ("li", "body:li"),
        ("button", "button"),
        ("a", "a"),
    ]:
        for tag in soup.select(selector)[:80]:
            text = tag.get_text(" ")
            add(text, source)

    # Preserve best score per exact text.
    by_text = {}
    for cand in candidates:
        key = cand.text.lower()
        if key not in by_text or cand.score > by_text[key].score:
            by_text[key] = cand
    return sorted(by_text.values(), key=lambda c: (-c.score, c.order))


def extract_cta(soup: BeautifulSoup) -> str:
    labels = []
    for tag in soup.select("a,button"):
        text = clean_text(tag.get_text(" "))
        lower = text.lower()
        if 1 <= word_count(text) <= 6 and any(term in lower for term in CTA_PATTERNS):
            labels.append(text)
    seen = []
    for label in labels:
        if label.lower() not in [x.lower() for x in seen]:
            seen.append(label)
    return "; ".join(seen[:3])


def fetch(url: str) -> tuple[str, int | str, str, str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if not resp.encoding or resp.encoding.lower() in {"iso-8859-1", "latin-1"}:
            resp.encoding = resp.apparent_encoding or "utf-8"
        ctype = resp.headers.get("content-type", "")
        text = resp.text if "html" in ctype or resp.text.lstrip().startswith("<") else ""
        return resp.url, resp.status_code, text, ""
    except Exception as exc:
        return url, "error", "", f"{type(exc).__name__}: {str(exc)[:220]}"


def process(row: dict) -> dict:
    url = row["url"]
    brand = row.get("brand_name", "")
    final_url, status, body, err = fetch(url)
    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    blocked = "no"
    notes = []
    quote = ""
    message_source = ""
    why = ""
    theme = ""
    claim_type = ""
    cta = ""

    if err:
        blocked = "yes"
        notes.append(err)
    elif not body:
        blocked = "yes"
        notes.append("No HTML body captured")
    else:
        soup = BeautifulSoup(body, "lxml")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        page_text = clean_text(soup.get_text(" "))
        lower = page_text.lower()
        if any(
            marker in lower[:3000]
            for marker in [
                "access denied",
                "captcha",
                "are you a healthcare professional",
                "please enable javascript",
                "blocked",
            ]
        ):
            notes.append("Page may be gated, blocked, or JavaScript dependent")
        candidates = source_candidates(soup, brand)
        cta = extract_cta(soup)
        if candidates:
            best = candidates[0]
            quote = best.text
            message_source = best.source
            theme, claim_type = theme_and_claim(quote)
            why = "Highest-scoring short promotional candidate from captured page text"
        else:
            blocked = "yes"
            notes.append("No short promotional candidate found in captured page text")

    return {
        "source_index": row.get("source_index", ""),
        "url": url,
        "final_url": final_url or row.get("final_url", ""),
        "brand_name": brand,
        "generic_name": row.get("generic_name", ""),
        "company": row.get("company", ""),
        "promotional_message_verbatim": quote,
        "message_word_count": word_count(quote) if quote else "",
        "message_source": message_source,
        "message_theme": theme,
        "claim_type": claim_type,
        "call_to_action": cta,
        "why_selected": why,
        "access_status": "quote_extracted" if quote else "no_quote_extracted",
        "http_status": status,
        "blocked_or_error": blocked,
        "notes": "; ".join(notes),
        "retrieved_at": retrieved_at,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    rows.sort(key=lambda r: int(r["source_index"]))

    results = []
    start = time.time()
    with ThreadPoolExecutor(max_workers=24) as executor:
        futures = {executor.submit(process, row): row for row in rows}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            if i % 50 == 0:
                print(f"{i}/{len(rows)} processed")

    results.sort(key=lambda r: int(r["source_index"]))
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    themes = {}
    claims = {}
    statuses = {}
    for row in results:
        statuses[row["access_status"]] = statuses.get(row["access_status"], 0) + 1
        claims[row["claim_type"] or "none"] = claims.get(row["claim_type"] or "none", 0) + 1
        for theme in (row["message_theme"] or "none").split("; "):
            themes[theme] = themes.get(theme, 0) + 1

    SUMMARY_JSON.write_text(
        json.dumps(
            {
                "input": str(INPUT),
                "output": str(OUT_CSV),
                "rows": len(results),
                "quotes_extracted": sum(1 for r in results if r["promotional_message_verbatim"]),
                "statuses": statuses,
                "claim_type_counts": claims,
                "theme_counts": themes,
                "elapsed_seconds": round(time.time() - start, 1),
                "quote_policy": "One short verbatim quote per source page, capped at 25 words.",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUT_CSV} ({len(results)} rows)")
    print(f"wrote {SUMMARY_JSON}")


if __name__ == "__main__":
    main()
