import base64
import csv
import html
import json
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen

import build_branded_drug_website_inventory as base
from build_inventory_from_fda_and_existing_seeds import read_csv, write_csv
from manual_review_remaining_websites import THIRD_PARTY_DOMAINS


RUN_DIR = Path(__file__).resolve().parent
USER_AGENT = base.USER_AGENT

KNOWN_OFFICIAL_HOST_PARTS = [
    "lilly.com",
    "novomedlink.com",
    "boehringer-ingelheim.com",
    "pfizerpro.com",
    "pfizer.com",
    "bmscustomerconnect.com",
    "bms.com",
    "merckconnect.com",
    "merck.com",
    "janssen",
    "abbvie",
    "gsk",
    "sanofi",
    "novartis",
    "gene.com",
    "genentech",
    "astrazeneca",
    "amgen",
    "takeda",
    "otsuka",
    "roche",
    "viiv",
    "vertex",
    "teva",
    "endo",
    "bausch",
    "organon",
    "bayer",
]


def decode_bing_url(url):
    parsed = urlparse(html.unescape(url))
    if "bing.com" not in parsed.netloc:
        return html.unescape(url)
    query = parse_qs(parsed.query)
    encoded = query.get("u", [""])[0]
    if encoded.startswith("a1"):
        encoded = encoded[2:]
    if not encoded:
        return html.unescape(url)
    padded = encoded + "=" * (-len(encoded) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode()).decode("utf-8", errors="ignore")
    except Exception:
        return html.unescape(url)


def domain_is_third_party(url):
    host = urlparse(url).netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    return any(host == domain or host.endswith("." + domain) for domain in THIRD_PARTY_DOMAINS)


def search_bing(query, max_results=10):
    url = "https://www.bing.com/search?q=" + quote_plus(query)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=14) as response:
            text = response.read(900_000).decode("utf-8", errors="ignore")
    except Exception as exc:
        return [], type(exc).__name__
    rows = []
    for match in re.finditer(
        r"<h2[^>]*>\s*<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>",
        text,
        flags=re.I | re.S,
    ):
        result_url = decode_bing_url(match.group(1))
        title = re.sub(r"<.*?>", " ", html.unescape(match.group(2)))
        title = re.sub(r"\s+", " ", title).strip()
        if not result_url.startswith("http") or domain_is_third_party(result_url):
            continue
        rows.append({"url": result_url, "title": title})
        if len(rows) >= max_results:
            break
    return rows, ""


def brand_tokens(brand):
    return [tok.lower() for tok in re.findall(r"[A-Za-z0-9]+", brand) if len(tok) >= 3]


def host_path_text(url):
    parsed = urlparse(url)
    return re.sub(r"[^a-z0-9]+", "", (parsed.netloc + parsed.path).lower())


def title_has_brand(brand, title):
    brand_key = base.norm_key(brand)
    title_key = base.norm_key(title)
    if brand_key and brand_key in title_key:
        return True
    tokens = brand_tokens(brand)
    return bool(tokens and tokens[0] in title.lower())


def url_has_brand(brand, url):
    text = host_path_text(url)
    slug = base.brand_slug(brand)
    if slug and len(slug) >= 4 and slug in text:
        return True
    tokens = brand_tokens(brand)
    return bool(tokens and tokens[0] in text)


def is_known_official_host(url):
    host = urlparse(url).netloc.lower()
    return any(part in host for part in KNOWN_OFFICIAL_HOST_PARTS)


def classify_candidate(row, result, query):
    brand = row["brand_name"]
    title = result["title"]
    url = result["url"]
    blob = " ".join([title, url, query]).lower()
    title_brand = title_has_brand(brand, title)
    url_brand = url_has_brand(brand, url)
    official_host = is_known_official_host(url)
    if not (title_brand or url_brand):
        return None
    audience = "official_or_unknown"
    if any(term in blob for term in ["hcp", "healthcare professional", "health care professional", "prescribing", "professional"]):
        audience = "hcp"
    elif any(term in blob for term in ["patient", "savings", "support", "copay", "co-pay", "official website"]):
        audience = "patient"
    elif "official" in blob:
        audience = "patient_or_mixed"

    score = 0
    if title_brand:
        score += 2
    if url_brand:
        score += 2
    if official_host:
        score += 1
    if "official" in blob:
        score += 1
    if audience in {"hcp", "patient"}:
        score += 1

    confidence = "low"
    if score >= 5:
        confidence = "high"
    elif score >= 3:
        confidence = "medium"

    if confidence == "low":
        return None
    return {
        "brand_name": row["brand_name"],
        "generic_name": row["generic_name"],
        "manufacturer_or_labeler": row["manufacturer_or_labeler"],
        "candidate_audience": audience,
        "candidate_url": url,
        "result_title": title,
        "query": query,
        "confidence": confidence,
        "evidence_basis": "; ".join(
            [
                "title has brand" if title_brand else "",
                "url has brand" if url_brand else "",
                "known manufacturer/brand-owner host" if official_host else "",
                f"audience signal: {audience}",
            ]
        ).strip("; "),
    }


def audit_row(row):
    if base.looks_generic_brand(row["brand_name"], row["generic_name"]):
        return [], {
            "brand_name": row["brand_name"],
            "generic_name": row["generic_name"],
            "manufacturer_or_labeler": row["manufacturer_or_labeler"],
            "review_bucket": "generic_like_or_nonbranded_scope_review",
            "notes": "Proprietary and generic/proper names overlap; not searched as a likely branded product website miss.",
        }
    queries = [
        f'{row["brand_name"]} official website',
        f'{row["brand_name"]} patient official',
        f'{row["brand_name"]} hcp official',
        f'{row["brand_name"]} healthcare professionals',
    ]
    candidates = []
    errors = []
    seen = set()
    for query in queries:
        results, error = search_bing(query)
        if error:
            errors.append(f"{query}: {error}")
        for result in results:
            candidate = classify_candidate(row, result, query)
            if not candidate:
                continue
            key = (candidate["candidate_audience"], candidate["candidate_url"].rstrip("/").lower())
            if key not in seen:
                seen.add(key)
                candidates.append(candidate)
        time.sleep(0.03)
    if candidates:
        return candidates, {
            "brand_name": row["brand_name"],
            "generic_name": row["generic_name"],
            "manufacturer_or_labeler": row["manufacturer_or_labeler"],
            "review_bucket": "possible_missed_site",
            "notes": f"{len(candidates)} candidate(s) found.",
        }
    return [], {
        "brand_name": row["brand_name"],
        "generic_name": row["generic_name"],
        "manufacturer_or_labeler": row["manufacturer_or_labeler"],
        "review_bucket": "no_candidate_found",
        "notes": "; ".join(errors[:2]),
    }


def main():
    master = read_csv(RUN_DIR / "master_branded_drug_website_inventory_manual_reviewed.csv")
    rows = [
        row
        for row in master
        if row["website_classification"] == "no_branded_site_found_after_manual_review_pass"
    ]
    candidates = []
    audit_rows = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {executor.submit(audit_row, row): row for row in rows}
        completed = 0
        for future in as_completed(future_map):
            found, audit = future.result()
            candidates.extend(found)
            audit_rows.append(audit)
            completed += 1
            if completed % 50 == 0:
                print(f"audited {completed} / {len(rows)}")

    # One strongest candidate per brand/audience, keeping all candidates in the raw file.
    score_map = {"high": 3, "medium": 2, "low": 1}
    best = {}
    for row in candidates:
        key = (base.norm_key(row["brand_name"]), row["candidate_audience"])
        current = best.get(key)
        if not current or score_map[row["confidence"]] > score_map[current["confidence"]]:
            best[key] = row

    write_csv(RUN_DIR / "no_site_followup_candidate_misses.csv", candidates)
    write_csv(RUN_DIR / "no_site_followup_best_candidate_misses.csv", sorted(best.values(), key=lambda r: (r["brand_name"], r["candidate_audience"])))
    write_csv(RUN_DIR / "no_site_followup_audit_status.csv", audit_rows)

    summary = {
        "run_date": "2026-07-08",
        "no_site_rows_audited": len(rows),
        "candidate_rows": len(candidates),
        "best_candidate_rows": len(best),
        "brands_with_candidates": len({base.norm_key(r["brand_name"]) for r in candidates}),
        "audit_bucket_counts": dict(Counter(r["review_bucket"] for r in audit_rows)),
        "candidate_confidence_counts": dict(Counter(r["confidence"] for r in candidates)),
        "candidate_audience_counts": dict(Counter(r["candidate_audience"] for r in candidates)),
        "method_note": "Search-result follow-up over no-site rows only. Candidates are possible missed official branded pages based on Bing result titles/URLs and should be verified before merging into the master inventory.",
    }
    (RUN_DIR / "no_site_followup_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
