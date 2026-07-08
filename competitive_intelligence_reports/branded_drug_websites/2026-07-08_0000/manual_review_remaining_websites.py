import base64
import csv
import html
import json
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

import build_branded_drug_website_inventory as base
from build_inventory_from_fda_and_existing_seeds import (
    clean_url,
    first_nonempty,
    patient_candidates_from_hcp,
    read_csv,
    write_csv,
)


RUN_DIR = Path(__file__).resolve().parent
WORKING_DIR = RUN_DIR / "working"
USER_AGENT = base.USER_AGENT

THIRD_PARTY_DOMAINS = {
    "bing.com",
    "microsoft.com",
    "duckduckgo.com",
    "google.com",
    "yahoo.com",
    "drugs.com",
    "webmd.com",
    "rxlist.com",
    "goodrx.com",
    "healthline.com",
    "medicalnewstoday.com",
    "mayoclinic.org",
    "medlineplus.gov",
    "wikipedia.org",
    "fda.gov",
    "accessdata.fda.gov",
    "dailymed.nlm.nih.gov",
    "nih.gov",
    "ncbi.nlm.nih.gov",
    "clinicaltrials.gov",
    "ema.europa.eu",
    "pharmacytimes.com",
    "empr.com",
    "pdr.net",
    "medscape.com",
    "singlecare.com",
    "rxwiki.com",
    "centerwatch.com",
}

HCP_TERMS = [
    "FOR HEALTHCARE PROFESSIONALS",
    "FOR U.S. HEALTHCARE PROFESSIONALS",
    "FOR US HEALTHCARE PROFESSIONALS",
    "FOR HEALTH CARE PROFESSIONALS",
    "HEALTHCARE PROFESSIONALS",
    "HEALTH CARE PROFESSIONALS",
    "HEALTHCARE PROVIDERS",
    "HEALTH CARE PROVIDERS",
    "PRESCRIBING INFORMATION",
    "HCP",
]

PATIENT_TERMS = [
    "FOR PATIENTS",
    "PATIENTS AND CAREGIVERS",
    "PATIENTS & CAREGIVERS",
    "PATIENT SUPPORT",
    "PATIENT RESOURCES",
    "SAVINGS CARD",
    "COPAY",
    "CO-PAY",
    "TALK TO YOUR DOCTOR",
    "ASK YOUR DOCTOR",
    "PATIENT BROCHURE",
]

PARKED_OR_FOR_SALE_TERMS = [
    "DOMAIN FOR SALE",
    "BUY THIS DOMAIN",
    "THIS DOMAIN IS FOR SALE",
    "PARKED FREE",
    "SEDO",
    "AFTERNIC",
    "HUGE DOMAINS",
    "GODADDY",
]


def safe_slug_words(brand):
    words = re.findall(r"[A-Za-z0-9]+", brand.lower())
    stop = {
        "er",
        "xr",
        "odt",
        "iv",
        "hcl",
        "usp",
        "injection",
        "tablets",
        "tablet",
        "capsules",
        "capsule",
        "solution",
        "suspension",
    }
    return [w for w in words if w not in stop]


def brand_variants(brand):
    words = safe_slug_words(brand)
    if not words:
        return []
    variants = []
    compact = "".join(words)
    hyphen = "-".join(words)
    variants.extend([compact, hyphen])
    if len(words) > 1:
        variants.append(words[0])
    seen = set()
    output = []
    for value in variants:
        if len(value) >= 4 and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def direct_candidates(brand, audience):
    urls = []
    for variant in brand_variants(brand):
        if audience == "hcp":
            urls.extend(
                [
                    f"https://www.{variant}hcp.com/",
                    f"https://{variant}hcp.com/",
                    f"https://www.{variant}-hcp.com/",
                    f"https://hcp.{variant}.com/",
                    f"https://www.{variant}pro.com/",
                    f"https://{variant}pro.com/",
                    f"https://www.{variant}.com/hcp",
                    f"https://www.{variant}.com/healthcare-professionals",
                    f"https://www.{variant}.com/healthcare-professionals/",
                ]
            )
        else:
            urls.extend(
                [
                    f"https://www.{variant}.com/",
                    f"https://{variant}.com/",
                    f"https://www.{variant}.com/patient",
                    f"https://www.{variant}.com/patients",
                    f"https://www.{variant}.com/patient-support",
                    f"https://www.{variant}.com/savings",
                ]
            )
    return dedupe_urls(urls)


def dedupe_urls(urls):
    output = []
    seen = set()
    for url in urls:
        url = clean_url(url)
        key = url.rstrip("/").lower()
        if key and key not in seen:
            seen.add(key)
            output.append(url)
    return output


def decode_bing_url(url):
    parsed = urlparse(html.unescape(url))
    if "bing.com" not in parsed.netloc:
        return html.unescape(url)
    query = parse_qs(parsed.query)
    encoded = query.get("u", [""])[0]
    if encoded.startswith("a1"):
        encoded = encoded[2:]
    if encoded:
        padded = encoded + "=" * (-len(encoded) % 4)
        try:
            return base64.urlsafe_b64decode(padded.encode()).decode("utf-8", errors="ignore")
        except Exception:
            return html.unescape(url)
    return html.unescape(url)


def fetch_url(url, max_bytes=450_000, timeout=9):
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout) as response:
            final_url = response.geturl()
            ctype = response.headers.get("content-type", "")
            data = response.read(max_bytes)
        text = ""
        if "text/html" in ctype or "text/plain" in ctype or not ctype:
            text = data.decode("utf-8", errors="ignore")
        return {"ok": True, "url": url, "final_url": final_url, "content_type": ctype, "text": text, "error": ""}
    except Exception as exc:
        return {"ok": False, "url": url, "final_url": "", "content_type": "", "text": "", "error": type(exc).__name__}


def domain_is_third_party(url):
    host = urlparse(url).netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    return any(host == domain or host.endswith("." + domain) for domain in THIRD_PARTY_DOMAINS)


def visible_upper(raw):
    return base.clean_html_text(raw).upper()


def brand_present(brand, url, text):
    slug = base.brand_slug(brand)
    host_path = (urlparse(url).netloc + urlparse(url).path).lower()
    if slug and slug in re.sub(r"[^a-z0-9]+", "", host_path):
        return True
    brand_key = base.norm_key(brand)
    return bool(brand_key and brand_key in text)


def brand_visible_in_text(brand, text):
    brand_key = base.norm_key(brand)
    return bool(brand_key and brand_key in text)


def classify_candidate(brand, url, raw_text, intended_audience, result_title="", result_snippet=""):
    page_text = visible_upper(raw_text)
    search_text = " ".join([result_title.upper(), result_snippet.upper()])
    evidence_text = " ".join([page_text, search_text])
    if any(term in evidence_text for term in PARKED_OR_FOR_SALE_TERMS):
        return None
    hcp_hits = [term for term in HCP_TERMS if term in evidence_text]
    patient_hits = [term for term in PATIENT_TERMS if term in evidence_text]
    brand_text_ok = brand_visible_in_text(brand, evidence_text)
    brand_url_ok = brand_present(brand, url, "")
    if not (brand_text_ok or brand_url_ok):
        return None
    if base.excluded_by_name(brand, url, evidence_text[:1000]):
        return None
    if intended_audience == "hcp":
        url_l = url.lower()
        url_audience_signal = (
            "hcp" in url_l or "pro." in url_l or "pro/" in url_l or "professional" in url_l
        )
        if hcp_hits and (brand_text_ok or brand_url_ok):
            return {
                "audience": "hcp",
                "evidence": "; ".join(hcp_hits[:4]),
                "confidence": "high" if hcp_hits else "medium",
            }
        if url_audience_signal and brand_text_ok and page_text:
            return {
                "audience": "hcp",
                "evidence": "hcp/pro/professional URL signal plus visible brand text",
                "confidence": "medium",
            }
    else:
        hcp_only_url = any(part in url.lower() for part in ["hcp", "professional", "pro."])
        if patient_hits and not hcp_only_url:
            return {
                "audience": "patient",
                "evidence": "; ".join(patient_hits[:4]),
                "confidence": "high",
            }
        if patient_hits:
            return {
                "audience": "patient",
                "evidence": "; ".join(patient_hits[:4]) + "; hcp-like URL caveat",
                "confidence": "medium",
            }
    return None


def search_bing(query, max_results=8):
    url = "https://www.bing.com/search?q=" + quote_plus(query)
    result = fetch_url(url, max_bytes=900_000, timeout=12)
    if not result["ok"] or not result["text"]:
        return []
    rows = []
    for match in re.finditer(
        r"<h2[^>]*>\s*<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>",
        result["text"],
        flags=re.I | re.S,
    ):
        raw_url = decode_bing_url(match.group(1))
        title = re.sub(r"<.*?>", " ", html.unescape(match.group(2)))
        title = re.sub(r"\s+", " ", title).strip()
        if not raw_url.startswith("http") or domain_is_third_party(raw_url):
            continue
        rows.append({"url": raw_url, "title": title, "snippet": "", "source": "bing"})
        if len(rows) >= max_results:
            break
    return rows


def title_has_brand(brand, title):
    brand_key = base.norm_key(brand)
    title_key = base.norm_key(title)
    return bool(brand_key and brand_key in title_key)


def evaluate_url(brand, url, audience, method, title="", snippet="", query=""):
    fetched = fetch_url(url)
    final_url = fetched["final_url"] or url
    raw = fetched["text"] if fetched["ok"] else ""
    status = "fetched" if fetched["ok"] else fetched["error"]
    if method == "direct_candidate_url_probe" and not fetched["ok"]:
        return None
    if not raw:
        raw = " ".join([title, snippet, final_url])
    classification = classify_candidate(brand, final_url, raw, audience, title, snippet)
    if not classification and method == "bing_search_result" and audience == "patient":
        url_l = final_url.lower()
        title_l = title.lower()
        official_like = (
            "official" in title_l
            or "patient" in title_l
            or "savings" in title_l
            or "support" in title_l
            or "patient" in query.lower()
            or "official" in query.lower()
        )
        hcp_like = any(part in url_l for part in ["hcp", "professional", "pro."])
        if title_has_brand(brand, title) and official_like and not hcp_like:
            classification = {
                "audience": "patient",
                "evidence": "official/patient-oriented branded search result",
                "confidence": "medium",
            }
    if not classification and method == "bing_search_result" and audience == "hcp":
        title_l = title.lower()
        url_l = final_url.lower()
        hcp_like = (
            "hcp" in title_l
            or "healthcare professional" in title_l
            or "health care professional" in title_l
            or "prescribing" in title_l
            or "hcp" in url_l
            or "professional" in url_l
            or "pro." in url_l
        )
        if title_has_brand(brand, title) and hcp_like:
            classification = {
                "audience": "hcp",
                "evidence": "hcp/professional-oriented branded search result",
                "confidence": "medium",
            }
    if not classification:
        return None
    return {
        "brand_name": brand,
        "audience": audience,
        "url": final_url,
        "source_url_checked": url,
        "discovery_method": method,
        "evidence": classification["evidence"],
        "confidence": classification["confidence"],
        "fetch_status": status,
        "result_title": title,
    }


def is_generic_like_inventory_row(row):
    return base.looks_generic_brand(row.get("brand_name", ""), row.get("generic_name", ""))


def review_brand(row):
    brand = row["brand_name"]
    result = {
        "brand_name": brand,
        "generic_name": row["generic_name"],
        "manufacturer_or_labeler": row["manufacturer_or_labeler"],
        "review_reason": row["reason"],
        "new_hcp_url": "",
        "new_hcp_evidence": "",
        "new_hcp_confidence": "",
        "new_hcp_method": "",
        "new_hcp_fetch_status": "",
        "new_patient_url": "",
        "new_patient_evidence": "",
        "new_patient_confidence": "",
        "new_patient_method": "",
        "new_patient_fetch_status": "",
        "review_status": "",
        "notes": "",
    }
    if is_generic_like_inventory_row(row):
        result["review_status"] = "generic_like_or_nonbranded_scope_review"
        result["notes"] = "FDA/NDC row appears generic-like because proprietary and generic/proper names overlap; not promoted as a branded website hit in manual review."
        return result
    need_hcp = row["reason"] == "no_branded_site_found_in_seed_or_deterministic_probe"
    need_patient = True

    for audience in ["hcp", "patient"]:
        if audience == "hcp" and not need_hcp:
            continue
        candidates = direct_candidates(brand, audience)
        found = None
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_map = {
                executor.submit(evaluate_url, brand, url, audience, "direct_candidate_url_probe"): url
                for url in candidates[:18]
            }
            for future in as_completed(future_map):
                found = future.result()
                if found:
                    break
        if not found:
            queries = (
                [
                    f"{brand} hcp official",
                    f"{brand} healthcare professionals",
                    f'"{brand}" prescribing information hcp',
                    f'"{brand}" "For Healthcare Professionals"',
                ]
                if audience == "hcp"
                else [
                    f"{brand} patient official",
                    f"{brand} official website",
                    f"{brand} patient support",
                    f'"{brand}" savings',
                    f'"{brand}" "For Patients"',
                ]
            )
            for query in queries:
                search_rows = search_bing(query)
                for item in search_rows:
                    if domain_is_third_party(item["url"]):
                        continue
                    found = evaluate_url(
                        brand,
                        item["url"],
                        audience,
                        "bing_search_result",
                        item.get("title", ""),
                        item.get("snippet", ""),
                        query,
                    )
                    if found:
                        break
                if found:
                    break
                time.sleep(0.05)
        if found:
            if audience == "hcp":
                result["new_hcp_url"] = found["url"]
                result["new_hcp_evidence"] = found["evidence"]
                result["new_hcp_confidence"] = found["confidence"]
                result["new_hcp_method"] = found["discovery_method"]
                result["new_hcp_fetch_status"] = found["fetch_status"]
            else:
                result["new_patient_url"] = found["url"]
                result["new_patient_evidence"] = found["evidence"]
                result["new_patient_confidence"] = found["confidence"]
                result["new_patient_method"] = found["discovery_method"]
                result["new_patient_fetch_status"] = found["fetch_status"]

    if result["new_hcp_url"] or result["new_patient_url"]:
        result["review_status"] = "new_url_found"
    else:
        result["review_status"] = "no_url_found_by_manual_review_pass"
        result["notes"] = "No matching official branded HCP or patient URL found by direct URL probes plus Bing query review."
    return result


def merge_outputs(review_rows):
    master = read_csv(RUN_DIR / "master_branded_drug_website_inventory.csv")
    hcp = read_csv(RUN_DIR / "hcp_branded_drug_websites.csv")
    patient = read_csv(RUN_DIR / "patient_branded_drug_websites.csv")
    by_brand = {base.norm_key(row["brand_name"]): row for row in review_rows}

    hcp_urls = {row["hcp_url"].rstrip("/").lower() for row in hcp}
    patient_urls = {row["patient_url"].rstrip("/").lower() for row in patient}

    for row in master:
        key = base.norm_key(row["brand_name"])
        review = by_brand.get(key)
        if not review:
            continue
        if not row["hcp_website_url"] and review.get("new_hcp_url"):
            row["hcp_website_url"] = review["new_hcp_url"]
            row["hcp_website_count_for_brand"] = "1"
            row["audience_evidence"] = first_nonempty(row["audience_evidence"], review["new_hcp_evidence"])
            url_key = review["new_hcp_url"].rstrip("/").lower()
            if url_key not in hcp_urls:
                hcp.append(
                    {
                        "brand_name": row["brand_name"],
                        "original_seed_brand_name": "",
                        "brand_metadata_method": "manual_review_bing_or_direct_probe",
                        "generic_name": row["generic_name"],
                        "company": row["manufacturer_or_labeler"],
                        "hcp_url": review["new_hcp_url"],
                        "hcp_url_original": review["new_hcp_url"],
                        "hcp_access_status": "manual_review_found",
                        "hcp_retrieved_at": "2026-07-08",
                        "rwe_assessment": "not assessed",
                        "rwe_signals": "",
                        "promotional_message_verbatim": "",
                        "message_theme": "",
                        "fda_exact_brand_match_status": "matched_to_master_inventory",
                        "fda_source_confidence": row["fda_source_confidence"],
                        "fda_application_numbers": row["application_numbers"],
                        "scope_status": "in_scope_fda_matched_rx_brand",
                        "scope_exclusion_or_review_reason": "",
                    }
                )
                hcp_urls.add(url_key)
        if not row["patient_website_url"] and review.get("new_patient_url"):
            row["patient_website_url"] = review["new_patient_url"]
            row["patient_website_count_for_brand"] = "1"
            row["audience_evidence"] = first_nonempty(row["audience_evidence"], review["new_patient_evidence"])
            url_key = review["new_patient_url"].rstrip("/").lower()
            if url_key not in patient_urls:
                patient.append(
                    {
                        "brand_name": row["brand_name"],
                        "generic_name": row["generic_name"],
                        "company": row["manufacturer_or_labeler"],
                        "patient_url": review["new_patient_url"],
                        "patient_audience_evidence": review["new_patient_evidence"],
                        "patient_discovery_method": review["new_patient_method"],
                    }
                )
                patient_urls.add(url_key)
        has_hcp = bool(row["hcp_website_url"])
        has_patient = bool(row["patient_website_url"])
        if has_hcp and has_patient:
            row["website_classification"] = "both_hcp_and_patient_found"
            row["confidence"] = "high"
            row["uncertainty_notes"] = ""
        elif has_hcp:
            row["website_classification"] = "hcp_found_patient_not_found"
            row["confidence"] = "partial_manual_review"
            row["uncertainty_notes"] = "HCP URL found; patient URL not found by manual review pass."
        elif has_patient:
            row["website_classification"] = "patient_found_hcp_not_found"
            row["confidence"] = "partial_manual_review"
            row["uncertainty_notes"] = "Patient URL found; HCP URL not found by manual review pass."
        else:
            row["website_classification"] = "no_branded_site_found_after_manual_review_pass"
            row["confidence"] = "manual_review_no_url_found"
            row["uncertainty_notes"] = "No official branded HCP or patient URL found by direct URL probes plus Bing query review."
        row["last_checked_or_seed_date"] = "2026-07-08"

    unresolved = [
        row
        for row in master
        if row["website_classification"]
        in {
            "hcp_found_patient_not_found",
            "patient_found_hcp_not_found",
            "no_branded_site_found_after_manual_review_pass",
        }
    ]
    generic_scope_review = [
        row
        for row in master
        if row["website_classification"] == "no_branded_site_found_after_manual_review_pass"
        and is_generic_like_inventory_row(row)
    ]
    write_csv(RUN_DIR / "master_branded_drug_website_inventory_manual_reviewed.csv", master)
    write_csv(RUN_DIR / "hcp_branded_drug_websites_manual_reviewed.csv", hcp)
    write_csv(RUN_DIR / "patient_branded_drug_websites_manual_reviewed.csv", patient)
    write_csv(RUN_DIR / "unresolved_after_manual_review.csv", unresolved)
    write_csv(RUN_DIR / "generic_like_scope_review_after_manual_review.csv", generic_scope_review)
    return master, hcp, patient, unresolved


def main():
    queue = read_csv(RUN_DIR / "manual_review_queue.csv")
    out_path = RUN_DIR / "manual_review_search_results.csv"
    done = {}
    if out_path.exists():
        done = {base.norm_key(row["brand_name"]): row for row in read_csv(out_path)}

    review_rows = list(done.values())
    remaining = [row for row in queue if base.norm_key(row["brand_name"]) not in done]

    if remaining:
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_map = {executor.submit(review_brand, row): row for row in remaining}
            completed = 0
            for future in as_completed(future_map):
                row = future.result()
                review_rows.append(row)
                completed += 1
                if completed % 50 == 0:
                    write_csv(out_path, review_rows)
                    print(f"completed {len(review_rows)} / {len(queue)}")
        write_csv(out_path, review_rows)

    master, hcp, patient, unresolved = merge_outputs(review_rows)
    summary = {
        "run_date": "2026-07-08",
        "manual_review_input_rows": len(queue),
        "manual_review_result_rows": len(review_rows),
        "new_hcp_urls_found": sum(1 for row in review_rows if row.get("new_hcp_url")),
        "new_patient_urls_found": sum(1 for row in review_rows if row.get("new_patient_url")),
        "review_status_counts": dict(Counter(row["review_status"] for row in review_rows)),
        "manual_reviewed_master_classification_counts": dict(
            Counter(row["website_classification"] for row in master)
        ),
        "manual_reviewed_hcp_unique_urls": len({row["hcp_url"].rstrip("/").lower() for row in hcp}),
        "manual_reviewed_patient_unique_urls": len(
            {row["patient_url"].rstrip("/").lower() for row in patient}
        ),
        "unresolved_after_manual_review_rows": len(unresolved),
        "method_note": "Manual review pass used direct brand URL probes plus Bing result review and HTML/text audience classification. Results still require spot-checking for brands with redirects, JavaScript-only pages, access gates, and manufacturer-portfolio pages that do not expose brand names in static HTML.",
    }
    (RUN_DIR / "manual_review_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
