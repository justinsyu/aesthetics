import csv
import json
import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import build_branded_drug_website_inventory as base


RUN_DIR = Path(__file__).resolve().parent
ROOT = RUN_DIR.parents[2]
WORKING_DIR = RUN_DIR / "working"
RAW_DIR = RUN_DIR / "raw"
USER_AGENT = base.USER_AGENT

HCP_SITE_SEED = ROOT / "outputs" / "hcp_site_audit" / "hcp_site_color_scheme_drug_info.csv"
HCP_MESSAGE_SEED = (
    ROOT / "outputs" / "hcp_promotional_message_audit" / "hcp_site_promotional_messages.csv"
)
PATIENT_RETAINED = (
    ROOT
    / "competitive_intelligence_reports"
    / "patient_pro_not_in_label"
    / "2026-07-05_patient_site_pro_label_audit"
    / "sources"
    / "patient-retained-rows.json"
)


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def first_nonempty(*values):
    for value in values:
        value = (value or "").strip()
        if value:
            return value
    return ""


def clean_url(url):
    url = (url or "").strip()
    if not url:
        return ""
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    return url


def site_origin(url):
    parsed = urlparse(url)
    if not parsed.netloc:
        return ""
    return f"{parsed.scheme or 'https'}://{parsed.netloc}/"


def patient_candidates_from_hcp(row):
    brand = first_nonempty(row.get("brand_name"), row.get("brand"))
    slug = base.brand_slug(brand)
    urls = []
    source_url = clean_url(first_nonempty(row.get("final_url"), row.get("url"), row.get("hcp_url")))
    if source_url:
        parsed = urlparse(source_url)
        host = parsed.netloc.lower()
        host_no_www = host[4:] if host.startswith("www.") else host
        if host.startswith("hcp."):
            urls.append(f"{parsed.scheme}://www.{host[4:]}/")
            urls.append(f"{parsed.scheme}://{host[4:]}/")
        if "hcp" in host_no_www and slug:
            rewritten = host_no_www.replace(f"{slug}hcp", slug).replace(f"{slug}-hcp", slug)
            rewritten = rewritten.replace(f"hcp{slug}", slug).replace(f"hcp-{slug}", slug)
            if rewritten != host_no_www:
                urls.append(f"{parsed.scheme}://www.{rewritten}/")
                urls.append(f"{parsed.scheme}://{rewritten}/")
        if "/hcp" in parsed.path.lower() or "healthcare" in parsed.path.lower():
            urls.append(site_origin(source_url))
    if slug:
        urls.extend(
            [
                f"https://www.{slug}.com/",
                f"https://{slug}.com/",
                f"https://www.{slug}.com/patient",
                f"https://www.{slug}.com/patients",
                f"https://www.{slug}.com/patient-support",
            ]
        )
    deduped = []
    seen = set()
    for url in urls:
        url = clean_url(url)
        key = url.rstrip("/").lower()
        if key and key not in seen:
            seen.add(key)
            deduped.append(url)
    return deduped[:7]


def url_message_slug(row):
    url = clean_url(first_nonempty(row.get("final_url"), row.get("url"), row.get("hcp_url")))
    parsed = urlparse(url)
    text = " ".join(
        [
            parsed.netloc,
            parsed.path,
            row.get("promotional_message_verbatim", ""),
        ]
    ).lower()
    text = text.replace("healthcare-professionals", "hcp")
    text = re.sub(r"\b(www|hcp|pro|rx|us|usa|com|html|en|ecp|globalassets|pdf)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", "", text)
    text = text.replace("healthcareprofessional", "")
    text = text.replace("healthcareprofessionals", "")
    text = text.replace("forhealthcareprofessionals", "")
    return text


def build_slug_lookup(fda_rows):
    lookup = []
    for row in fda_rows:
        slug = row.get("brand_slug") or base.brand_slug(row.get("brand_name", ""))
        if len(slug) >= 4:
            lookup.append((slug, row))
    return sorted(lookup, key=lambda item: len(item[0]), reverse=True)


def infer_fda_match(row, fda_by_brand, fda_slug_lookup):
    original_brand = row.get("brand_name", "")
    original_key = base.norm_key(original_brand)
    haystack = url_message_slug(row)
    url_slug_match = None
    for slug, fda_row in fda_slug_lookup:
        if slug in haystack:
            url_slug_match = (slug, fda_row)
            break
    if url_slug_match:
        _, fda_row = url_slug_match
        if not original_key or base.norm_key(fda_row["brand_name"]) != original_key:
            return fda_row["brand_name"], [fda_row], "inferred_from_url_or_message_fda_slug"

    if original_key in fda_by_brand:
        return original_brand, fda_by_brand[original_key], "original_brand_exact_fda_match"

    # Fall back to uppercase brand-like words in the promotional message.
    message = row.get("promotional_message_verbatim", "")
    for token in re.findall(r"\b[A-Z][A-Z0-9-]{3,}\b", message):
        key = base.norm_key(token)
        if key in fda_by_brand:
            return fda_by_brand[key][0]["brand_name"], fda_by_brand[key], "inferred_from_promotional_message_token"

    return original_brand, [], "not_matched_by_exact_brand_key"


def fetch_short(url):
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=7) as response:
            final_url = response.geturl()
            content_type = response.headers.get("content-type", "")
            data = response.read(350_000)
        if "text/html" not in content_type and "text/plain" not in content_type:
            return {"url": url, "final_url": final_url, "ok": False, "error": content_type}
        return {
            "url": url,
            "final_url": final_url,
            "ok": True,
            "html": data.decode("utf-8", errors="ignore"),
            "error": "",
        }
    except Exception as exc:
        return {"url": url, "final_url": "", "ok": False, "error": type(exc).__name__}


def visible_text(html):
    return base.clean_html_text(html).upper()


def patient_signal(brand, html):
    text = visible_text(html)
    brand_key = base.norm_key(brand)
    brand_visible = bool(brand_key and brand_key in text)
    signals = [
        "FOR PATIENTS",
        "PATIENTS AND CAREGIVERS",
        "PATIENTS & CAREGIVERS",
        "PATIENT SUPPORT",
        "SAVINGS CARD",
        "COPAY",
        "TALK TO YOUR DOCTOR",
        "ASK YOUR DOCTOR",
        "PATIENT BROCHURE",
        "PATIENT RESOURCES",
    ]
    hits = [signal for signal in signals if signal in text]
    hcp_only = (
        "FOR HEALTHCARE PROFESSIONALS" in text[:5000]
        or "FOR U.S. HEALTHCARE PROFESSIONALS" in text[:5000]
        or "FOR US HEALTHCARE PROFESSIONALS" in text[:5000]
    )
    return brand_visible, hits, hcp_only


def probe_patient_sites(hcp_rows):
    tasks = []
    seen = set()
    for row in hcp_rows:
        brand = first_nonempty(row.get("brand_name"), row.get("inferred_brand_name"))
        for url in patient_candidates_from_hcp(row):
            key = (base.norm_key(brand), url.rstrip("/").lower())
            if key not in seen:
                seen.add(key)
                tasks.append((brand, row, url))
    retained = []
    checked = 0
    with ThreadPoolExecutor(max_workers=24) as executor:
        future_map = {executor.submit(fetch_short, url): (brand, row, url) for brand, row, url in tasks}
        for future in as_completed(future_map):
            brand, row, url = future_map[future]
            checked += 1
            result = future.result()
            if not result.get("ok"):
                continue
            brand_visible, hits, hcp_only = patient_signal(brand, result["html"])
            host_has_brand = base.brand_slug(brand) in urlparse(result["final_url"]).netloc.lower()
            if hits and (brand_visible or host_has_brand) and not hcp_only:
                retained.append(
                    {
                        "brand_name": brand,
                        "generic_name": row.get("generic_name", ""),
                        "company": row.get("company", ""),
                        "patient_url": result["final_url"],
                        "patient_audience_evidence": "; ".join(hits[:4]),
                        "patient_discovery_method": "derived from known HCP URL and probed rendered/static HTML",
                    }
                )
    best = {}
    for row in retained:
        key = base.norm_key(row["brand_name"])
        current = best.get(key)
        score = len(row["patient_audience_evidence"])
        if not current or score > len(current["patient_audience_evidence"]):
            best[key] = row
    return list(best.values()), checked, len(tasks)


def load_patient_retained_seed():
    if not PATIENT_RETAINED.exists():
        return []
    data = json.loads(PATIENT_RETAINED.read_text(encoding="utf-8"))
    rows = []
    for item in data:
        rows.append(
            {
                "brand_name": first_nonempty(item.get("brand"), item.get("brand_name")),
                "generic_name": "",
                "company": first_nonempty(item.get("manufacturer"), item.get("company")),
                "patient_url": first_nonempty(item.get("url"), item.get("source_url")),
                "patient_audience_evidence": first_nonempty(
                    item.get("source_type"), item.get("context"), "patient retained-row seed"
                ),
                "patient_discovery_method": "prior patient PRO-not-in-label retained-row seed",
            }
        )
    return rows


def build_universe():
    ndc_zip = RAW_DIR / "ndctext.zip"
    orange_zip = RAW_DIR / "orange_book.zip"
    if not ndc_zip.exists():
        ndc_zip = base.fetch(base.URLS["ndc_text_zip"], ndc_zip)
    if not orange_zip.exists():
        orange_zip = base.fetch(base.URLS["orange_book_zip"], orange_zip)
    ndc_products = base.read_zip_table(ndc_zip, "product.txt")
    brand_rows = base.ndc_brand_rows(ndc_products)
    brands = base.aggregate_brands(brand_rows)
    orange = base.parse_orange_book(orange_zip)
    for row in brands:
        pair = (row["brand_key"], base.norm_key(row["generic_name"]))
        row["orange_book_innovator_rx_match"] = "yes" if pair in orange else "no"
        if row["orange_book_innovator_rx_match"] == "yes":
            row["source_confidence"] = "high"
    high = [row for row in brands if row["source_confidence"] == "high"]
    medium = [row for row in brands if row["source_confidence"] != "high"]
    return ndc_products, brand_rows, brands, high, medium, orange


def main():
    WORKING_DIR.mkdir(parents=True, exist_ok=True)
    ndc_products, brand_rows, all_brands, high_brands, medium, orange = build_universe()
    hcp_rows = read_csv(HCP_SITE_SEED)
    hcp_messages = {row["source_index"]: row for row in read_csv(HCP_MESSAGE_SEED)}

    hcp_by_brand = defaultdict(list)
    hcp_inventory = []
    hcp_review = []
    fda_by_brand = defaultdict(list)
    for row in all_brands:
        fda_by_brand[row["brand_key"]].append(row)
    fda_slug_lookup = build_slug_lookup(high_brands)

    for row in hcp_rows:
        msg = hcp_messages.get(row.get("source_index"), {})
        seed_for_inference = dict(row)
        seed_for_inference["promotional_message_verbatim"] = msg.get("promotional_message_verbatim", "")
        inferred_brand, fda_matches, inference_method = infer_fda_match(
            seed_for_inference, fda_by_brand, fda_slug_lookup
        )
        brand_key = base.norm_key(inferred_brand)
        scope_exclusion = ""
        if base.excluded_by_name(
            inferred_brand,
            row.get("generic_name", ""),
            row.get("company", ""),
            msg.get("promotional_message_verbatim", ""),
            row.get("url", ""),
            row.get("final_url", ""),
        ):
            scope_exclusion = "excluded_by_vaccine_diagnostic_or_non_drug_pattern"
        fda_matches = fda_by_brand.get(brand_key, [])
        fda_status = "matched_to_fda_candidate" if fda_matches else inference_method
        hcp_record = {
            "brand_name": inferred_brand,
            "original_seed_brand_name": row.get("brand_name", ""),
            "brand_metadata_method": inference_method,
            "generic_name": first_nonempty(row.get("generic_name"), *(m.get("generic_name", "") for m in fda_matches[:1])),
            "company": first_nonempty(row.get("company"), *(m.get("labeler", "") for m in fda_matches[:1])),
            "hcp_url": first_nonempty(row.get("final_url"), row.get("url")),
            "hcp_url_original": row.get("url", ""),
            "hcp_access_status": row.get("status", ""),
            "hcp_retrieved_at": row.get("retrieved_at", ""),
            "rwe_assessment": row.get("rwe_assessment", ""),
            "rwe_signals": row.get("rwe_signals", ""),
            "promotional_message_verbatim": msg.get("promotional_message_verbatim", ""),
            "message_theme": msg.get("message_theme", ""),
            "fda_exact_brand_match_status": fda_status,
            "fda_source_confidence": "; ".join(sorted({m.get("source_confidence", "") for m in fda_matches if m.get("source_confidence")})),
            "fda_application_numbers": "; ".join(sorted({m.get("application_numbers_all", "") for m in fda_matches if m.get("application_numbers_all")})),
            "scope_status": "in_scope_fda_matched_rx_brand" if fda_matches and not scope_exclusion else "review_or_out_of_scope",
            "scope_exclusion_or_review_reason": scope_exclusion
            if scope_exclusion
            else ("" if fda_matches else "not matched to high-confidence FDA/NDC brand universe"),
        }
        if hcp_record["scope_status"] == "in_scope_fda_matched_rx_brand":
            hcp_inventory.append(hcp_record)
            hcp_by_brand[brand_key].append(hcp_record)
        else:
            hcp_review.append(hcp_record)

    patient_probe_rows, checked, task_count = probe_patient_sites(hcp_inventory)
    patient_seed_rows = load_patient_retained_seed()
    patient_by_brand = defaultdict(list)
    patient_review = []
    for row in patient_probe_rows + patient_seed_rows:
        if row.get("patient_url"):
            key = base.norm_key(row["brand_name"])
            if key in fda_by_brand and not base.excluded_by_name(
                row.get("brand_name", ""),
                row.get("generic_name", ""),
                row.get("company", ""),
                row.get("patient_url", ""),
            ):
                patient_by_brand[key].append(row)
            else:
                row["scope_status"] = "review_or_out_of_scope"
                row["scope_exclusion_or_review_reason"] = "not matched to high-confidence FDA/NDC brand universe"
                patient_review.append(row)

    master = []
    for row in high_brands:
        brand_key = row["brand_key"]
        hcp = hcp_by_brand.get(brand_key, [])
        patient = patient_by_brand.get(brand_key, [])
        if hcp and patient:
            classification = "both_hcp_and_patient_found"
        elif hcp:
            classification = "hcp_found_patient_not_found_by_seed_or_probe"
        elif patient:
            classification = "patient_found_hcp_not_found_by_seed"
        else:
            classification = "no_branded_site_found_in_seed_or_deterministic_probe"
        master.append(
            {
                "brand_name": row["brand_name"],
                "generic_name": row["generic_name"],
                "manufacturer_or_labeler": row["labelers_all"],
                "product_type": "prescription drug",
                "marketing_categories": row["marketing_categories_all"],
                "application_numbers": row["application_numbers_all"],
                "dosage_forms": row["dosage_forms_all"],
                "routes": row["routes_all"],
                "fda_source_basis": row["source_basis"],
                "fda_source_confidence": row["source_confidence"],
                "orange_book_innovator_rx_match": row["orange_book_innovator_rx_match"],
                "hcp_website_url": hcp[0]["hcp_url"] if hcp else "",
                "hcp_website_count_for_brand": len(hcp),
                "patient_website_url": patient[0]["patient_url"] if patient else "",
                "patient_website_count_for_brand": len(patient),
                "website_classification": classification,
                "audience_evidence": first_nonempty(
                    patient[0].get("patient_audience_evidence", "") if patient else "",
                    hcp[0].get("promotional_message_verbatim", "") if hcp else "",
                ),
                "last_checked_or_seed_date": first_nonempty(
                    hcp[0].get("hcp_retrieved_at", "") if hcp else "",
                    "2026-07-08",
                ),
                "confidence": "high" if hcp or patient else "needs_manual_review",
                "uncertainty_notes": ""
                if hcp or patient
                else "No site found in existing broad HCP seed, patient retained-row seed, or deterministic patient-domain probe; requires search-engine/manual verification.",
            }
        )

    review_queue = [
        {
            "brand_name": row["brand_name"],
            "generic_name": row["generic_name"],
            "manufacturer_or_labeler": row["manufacturer_or_labeler"],
            "search_hcp_query": f'"{row["brand_name"]}" "For Healthcare Professionals"',
            "search_patient_query": f'"{row["brand_name"]}" "For Patients"',
            "reason": row["website_classification"],
        }
        for row in master
        if row["confidence"] == "needs_manual_review"
        or row["website_classification"].endswith("not_found_by_seed_or_probe")
    ]

    hcp_dedup = {}
    for row in hcp_inventory:
        key = row["hcp_url"].rstrip("/").lower()
        hcp_dedup[key] = row
    patient_dedup = {}
    for rows in patient_by_brand.values():
        for row in rows:
            key = row["patient_url"].rstrip("/").lower()
            patient_dedup[key] = row

    write_csv(WORKING_DIR / "ndc_active_human_rx_brand_rows.csv", brand_rows)
    write_csv(WORKING_DIR / "branded_rx_universe_candidates_all.csv", all_brands)
    write_csv(WORKING_DIR / "branded_rx_universe_high_confidence.csv", high_brands)
    write_csv(WORKING_DIR / "branded_rx_universe_medium_review.csv", medium)
    write_csv(RUN_DIR / "master_branded_drug_website_inventory.csv", master)
    write_csv(RUN_DIR / "hcp_branded_drug_websites.csv", sorted(hcp_dedup.values(), key=lambda r: r["brand_name"]))
    write_csv(RUN_DIR / "hcp_seed_unmatched_or_out_of_scope_review.csv", sorted(hcp_review, key=lambda r: (r["brand_name"], r["hcp_url"])))
    write_csv(RUN_DIR / "patient_branded_drug_websites.csv", sorted(patient_dedup.values(), key=lambda r: r["brand_name"]))
    write_csv(RUN_DIR / "patient_seed_unmatched_or_out_of_scope_review.csv", sorted(patient_review, key=lambda r: (r["brand_name"], r["patient_url"])))
    write_csv(RUN_DIR / "manual_review_queue.csv", review_queue)

    summary = {
        "run_date": "2026-07-08",
        "ndc_product_rows": len(ndc_products),
        "active_human_prescription_candidate_ndc_rows": len(brand_rows),
        "unique_candidate_brand_generic_pairs": len(all_brands),
        "high_confidence_brand_generic_pairs_in_master": len(high_brands),
        "medium_confidence_review_pairs": len(medium),
        "orange_book_innovator_rx_pairs": len(orange),
        "hcp_seed_rows": len(hcp_rows),
        "hcp_seed_in_scope_rows": len(hcp_inventory),
        "hcp_seed_review_or_out_of_scope_rows": len(hcp_review),
        "hcp_unique_urls": len(hcp_dedup),
        "patient_seed_rows": len(patient_seed_rows),
        "patient_probe_candidate_urls": task_count,
        "patient_probe_candidate_urls_checked": checked,
        "patient_probe_brands_found": len(patient_probe_rows),
        "patient_unique_urls": len(patient_dedup),
        "patient_review_or_out_of_scope_rows": len(patient_review),
        "master_classification_counts": dict(Counter(row["website_classification"] for row in master)),
        "review_queue_rows": len(review_queue),
        "key_limitations": [
            "The HCP website list is seeded from an existing 681-row HCP site audit collected in May 2026 and exact brand-key matched to the FDA universe where possible.",
            "Patient-site discovery is not a complete search-engine crawl; it combines prior patient retained rows with deterministic probes derived from HCP domains.",
            "Rows without a found URL are retained in the manual review queue rather than silently excluded.",
            "FDA NDC listing is a marketed-listing source, but FDA notes labeler-submitted NDC listing data are not independently verified by the agency.",
        ],
    }
    (RUN_DIR / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
