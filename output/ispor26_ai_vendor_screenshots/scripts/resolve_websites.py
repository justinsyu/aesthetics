#!/usr/bin/env python3
import json
import re
import time
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
IN_PATH = DATA / "ispor26_exhibitors.json"
OUT_PATH = DATA / "ispor26_exhibitors_with_websites.json"
OVERRIDES_PATH = DATA / "website_overrides.json"

EXCLUDE_DOMAINS = {
    "goexposoftware.com",
    "ispor.org",
    "linkedin.com",
    "facebook.com",
    "x.com",
    "twitter.com",
    "instagram.com",
    "youtube.com",
    "crunchbase.com",
    "pitchbook.com",
    "bloomberg.com",
    "zoominfo.com",
    "dnb.com",
    "rocketreach.co",
    "glassdoor.com",
    "indeed.com",
    "wikipedia.org",
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "yahoo.com",
    "icloud.com",
    "aol.com",
}


def fetch(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 Chrome/124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def host(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower().replace("www.", "")


def clean_company(name: str) -> str:
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"\b(inc|inc\.|llc|ltd|limited|gmbh|pvt\.?|lp|l\.p\.|plc|corp\.?|corporation|company)\b", "", name, flags=re.I)
    return re.sub(r"\s+", " ", name).strip()


def score_candidate(company: str, url: str, title: str, snippet: str) -> int:
    h = host(url)
    if not h or any(h == d or h.endswith("." + d) for d in EXCLUDE_DOMAINS):
        return -100
    text = f"{h} {title} {snippet}".lower()
    tokens = [t.lower() for t in re.findall(r"[a-zA-Z0-9]+", clean_company(company)) if len(t) > 1]
    score = 0
    for token in tokens:
        if token in text:
            score += 3
        if token in h:
            score += 4
    if any(word in text for word in ["official", "home", "solutions", "health", "research", "consulting"]):
        score += 1
    if urlparse(url).path not in ("", "/"):
        score -= 1
    return score


def duckduckgo(company: str) -> list[dict]:
    query = quote_plus(f'{company} official website HEOR health economics outcomes research')
    url = f"https://duckduckgo.com/html/?q={query}"
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for result in soup.select(".result"):
        a = result.select_one(".result__a")
        if not a or not a.get("href"):
            continue
        result_url = a["href"]
        if "uddg=" in result_url:
            from urllib.parse import parse_qs, unquote, urlparse

            result_url = unquote(parse_qs(urlparse(result_url).query).get("uddg", [""])[0])
        candidates.append(
            {
                "url": result_url,
                "title": re.sub(r"\s+", " ", a.get_text(" ", strip=True)),
                "snippet": re.sub(r"\s+", " ", (result.select_one(".result__snippet") or result).get_text(" ", strip=True)),
            }
        )
    return candidates


def bing(company: str) -> list[dict]:
    query = quote_plus(f'{company} official website HEOR health economics outcomes research')
    html = fetch(f"https://www.bing.com/search?q={query}")
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for li in soup.select("li.b_algo"):
        a = li.find("a", href=True)
        if not a:
            continue
        candidates.append(
            {
                "url": a["href"],
                "title": re.sub(r"\s+", " ", a.get_text(" ", strip=True)),
                "snippet": re.sub(r"\s+", " ", (li.select_one(".b_caption") or li).get_text(" ", strip=True)),
            }
        )
    return candidates


def resolve_one(row: dict, overrides: dict) -> dict:
    if row.get("display_name") in overrides:
        row["website"] = overrides[row["display_name"]]
        row["website_source"] = "curated_override"
        return row

    if row.get("profile_website"):
        row["website"] = row["profile_website"]
        row["website_source"] = "goexpo_profile"
        return row

    email_domains = [
        domain
        for domain in row.get("profile_email_domains", [])
        if domain and not any(domain == d or domain.endswith("." + d) for d in EXCLUDE_DOMAINS)
    ]
    if email_domains:
        domain = sorted(email_domains, key=len)[0]
        row["website"] = f"https://{domain}/"
        row["website_source"] = "goexpo_profile_email_domain"
        return row

    candidates = []
    errors = []
    for provider in (duckduckgo, bing):
        try:
            candidates.extend(provider(row["display_name"]))
            if candidates:
                break
        except Exception as exc:
            errors.append(f"{provider.__name__}: {exc!r}")
        time.sleep(0.3)

    ranked = []
    seen = set()
    for c in candidates:
        c_host = host(c["url"])
        if c_host in seen:
            continue
        seen.add(c_host)
        c["score"] = score_candidate(row["display_name"], c["url"], c["title"], c["snippet"])
        ranked.append(c)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    row["website_candidates"] = ranked[:5]
    row["website_resolution_errors"] = errors
    if ranked and ranked[0]["score"] >= 5:
        row["website"] = f"{urlparse(ranked[0]['url']).scheme}://{urlparse(ranked[0]['url']).netloc}/"
        row["website_source"] = "search"
    else:
        row["website"] = ""
        row["website_source"] = "unresolved"
    return row


def main() -> None:
    rows = json.loads(IN_PATH.read_text(encoding="utf-8"))
    overrides = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8")) if OVERRIDES_PATH.exists() else {}
    out = []
    for idx, row in enumerate(rows, start=1):
        print(f"[{idx}/{len(rows)}] resolving {row['display_name']}", flush=True)
        resolved = resolve_one(dict(row), overrides)
        out.append(resolved)
        if resolved.get("website_source") not in {"curated_override", "goexpo_profile", "goexpo_profile_email_domain"}:
            time.sleep(0.5)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    resolved = sum(bool(r.get("website")) for r in out)
    print(f"Wrote {OUT_PATH}; resolved {resolved}/{len(out)} websites")


if __name__ == "__main__":
    main()
