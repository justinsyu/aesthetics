import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import build_branded_drug_website_inventory as base
from build_inventory_from_fda_and_existing_seeds import read_csv, write_csv
from manual_review_remaining_websites import HCP_TERMS, PATIENT_TERMS, PARKED_OR_FOR_SALE_TERMS


RUN_DIR = Path(__file__).resolve().parent
USER_AGENT = base.USER_AGENT

BAD_HOST_OR_PATH_PARTS = [
    "hugedomains.com",
    "namepros.com",
    "fruits.co",
    "cambiahealth.com",
    "dailymed.nlm.nih.gov",
    "medicine.com",
    "clevelandclinic.org",
    "myasthenia-gravis.com",
    "acdd.com",
    "acdsee.com",
    "acdc.com",
    "creatineinfo.org",
    "takeda.com/en-us/about/products",
    "lilly.com/medicines/current",
    "astrazeneca-us.com/",
    "boehringer-ingelheim.com/",
    "organon.com:443/our-focus/products-list",
    "merckconnect.com",
    "satsumarx.com/our-product",
    "maynepharma.com/us-products",
    "amphastar.com/cortrosyn",
    "satsumarx.com",
    "cambiahealth.com",
]

GENERIC_SUPPLY_TERMS = [
    "BLOOD",
    "COLLECTION",
    "SYSTEM",
    "DEXTROSE",
    "SODIUM CHLORIDE",
    "POTASSIUM",
    "LACTATED RINGERS",
    "STERILE WATER",
    "OXYGEN",
    "AIR COMPRESSED",
    "NERVE GRAFT",
    "BETADINE",
    "XYZAL",
]

OUT_OF_SCOPE_BRANDS = {
    "BETADINE",
    "XYZAL",
    "AVANCE NERVE GRAFT",
    "LASTACAFT",
    "CARDIOLITE",
    "LOCAMETZ",
    "NEPHROSCAN",
    "LIPIODOL",
}


def fetch(url):
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=12) as response:
            final_url = response.geturl()
            ctype = response.headers.get("content-type", "")
            data = response.read(700_000)
        text = data.decode("utf-8", errors="ignore") if "html" in ctype or "text" in ctype else ""
        return {"ok": True, "final_url": final_url, "content_type": ctype, "text": text, "error": ""}
    except Exception as exc:
        return {"ok": False, "final_url": "", "content_type": "", "text": "", "error": type(exc).__name__}


def clean_text(html):
    return base.clean_html_text(html)


def host_path(url):
    parsed = urlparse(url)
    return f"{parsed.netloc}{parsed.path}".lower()


def bad_url(url):
    value = url.lower()
    return any(part in value for part in BAD_HOST_OR_PATH_PARTS)


def brand_in_text_or_url(brand, text, url):
    brand_key = base.norm_key(brand)
    if brand_key and brand_key in base.norm_key(text):
        return True
    slug = base.brand_slug(brand)
    return bool(slug and slug in base.brand_slug(host_path(url)))


def is_generic_or_supply(row):
    brand_key = base.norm_key(row["brand_name"])
    if any(brand_key == base.norm_key(brand) for brand in OUT_OF_SCOPE_BRANDS):
        return True
    if base.looks_generic_brand(row["brand_name"], row["generic_name"]):
        return True
    haystack = base.norm_key(" ".join([row["brand_name"], row["generic_name"]]))
    return any(term in haystack for term in GENERIC_SUPPLY_TERMS)


def is_hcp_url(url):
    value = url.lower()
    return any(part in value for part in ["hcp", "/pro", "pro.", "professional", "healthcare"])


def is_patient_url(url):
    value = url.lower()
    return not is_hcp_url(url)


def page_title(html):
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html or "")
    if not m:
        return ""
    return re.sub(r"\s+", " ", base.clean_html_text(m.group(1))).strip()


def unusable_page_title(title):
    upper_title = title.upper()
    return any(term in upper_title for term in ["404", "NOT FOUND", "MAINTENANCE", "ERROR"])


def parked_or_for_sale_page(title, upper_text):
    parked_hit = any(term in upper_text for term in PARKED_OR_FOR_SALE_TERMS)
    if not parked_hit:
        return False
    title_upper = title.upper()
    rx_page_signal = any(
        term in upper_text
        for term in ["PRESCRIBING INFORMATION", "IMPORTANT SAFETY INFORMATION", "MEDICATION GUIDE"]
    )
    audience_title_signal = any(term in title_upper for term in ["HCP WEBSITE", "FOR PATIENTS", "PATIENT WEBSITE"])
    return not (rx_page_signal or audience_title_signal)


def exact_brand_domain(brand, url):
    host = urlparse(url).netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    host_main = host.split(":")[0].split(".")[0]
    slug = base.brand_slug(brand)
    return bool(slug and slug == base.brand_slug(host_main))


def hcp_only_page(title, upper_text):
    title_upper = title.upper()
    explicit_patient_title = any(
        term in title_upper
        for term in ["OFFICIAL PATIENT", "PATIENT WEBSITE", "PATIENT SITE", "FOR PATIENTS", "CONSUMER SITE"]
    )
    if explicit_patient_title:
        return False
    hcp_title = any(
        term in title_upper
        for term in ["HCP", "HCPS", "HEALTHCARE PROFESSIONAL", "HEALTH CARE PROFESSIONAL"]
    )
    if hcp_title:
        return True
    hcp_body = any(term in upper_text[:8000] for term in ["FOR HEALTHCARE PROFESSIONALS", "FOR US HEALTHCARE PROFESSIONALS", "FOR U.S. HEALTHCARE PROFESSIONALS"])
    patient_body = any(term in upper_text[:12000] for term in PATIENT_TERMS)
    return (hcp_title or hcp_body) and not patient_body


def drug_product_signal(upper_text):
    signals = [
        "FDA-APPROVED",
        "PRESCRIPTION",
        "INDICATION",
        "IMPORTANT SAFETY INFORMATION",
        "PRESCRIBING INFORMATION",
        "MEDICATION",
        "TABLET",
        "INJECTION",
        "CAPSULE",
        "DOSING",
    ]
    return any(signal in upper_text[:80000] for signal in signals)


def weak_product_information_only_page(title, upper_text):
    title_upper = title.upper()
    return (
        "INFORMATION" in title_upper
        and "VIEW PRODUCT INFORMATION" in upper_text[:20000]
        and not any(term in upper_text[:30000] for term in PATIENT_TERMS)
        and "IMPORTANT SAFETY INFORMATION" not in upper_text[:30000]
        and "PRESCRIBING INFORMATION" not in upper_text[:30000]
    )


def verify_candidate(row):
    result = dict(row)
    result.update(
        {
            "accepted": "no",
            "accepted_audience": "",
            "accepted_url": "",
            "verification_status": "",
            "verification_evidence": "",
            "page_title": "",
            "reject_reason": "",
        }
    )
    if is_generic_or_supply(row):
        result["reject_reason"] = "generic-like or supply/device/system row"
        return result
    if bad_url(row["candidate_url"]):
        result["reject_reason"] = "known non-branded-site or noisy host/path"
        return result

    fetched = fetch(row["candidate_url"])
    result["verification_status"] = "fetched" if fetched["ok"] else fetched["error"]
    final_url = fetched["final_url"] or row["candidate_url"]
    text = clean_text(fetched["text"])
    upper = text.upper()
    result["page_title"] = page_title(fetched["text"])
    title = result["page_title"]

    if not fetched["ok"]:
        result["reject_reason"] = "non-blocked candidate did not refetch successfully"
        return result
    if unusable_page_title(title):
        result["reject_reason"] = "error or maintenance page"
        return result
    if parked_or_for_sale_page(title, upper):
        result["reject_reason"] = "parked or domain-sale page"
        return result
    if not brand_in_text_or_url(row["brand_name"], text, final_url):
        result["reject_reason"] = "brand not visible in page text or URL"
        return result

    hcp_hits = [term for term in HCP_TERMS if term in upper]
    patient_hits = [term for term in PATIENT_TERMS if term in upper]
    has_pi_isi = "IMPORTANT SAFETY INFORMATION" in upper or "PRESCRIBING INFORMATION" in upper

    audience = row["candidate_audience"]
    if audience == "hcp":
        if is_hcp_url(final_url) and (hcp_hits or has_pi_isi):
            result["accepted"] = "yes"
            result["accepted_audience"] = "hcp"
            result["accepted_url"] = final_url
            result["verification_evidence"] = "; ".join(hcp_hits[:4] or ["HCP URL plus PI/ISI"])
            return result
        result["reject_reason"] = "candidate marked HCP but page lacks HCP-specific evidence"
        return result

    if hcp_only_page(title, upper):
        result["accepted"] = "yes"
        result["accepted_audience"] = "hcp"
        result["accepted_url"] = final_url
        result["verification_evidence"] = "; ".join(hcp_hits[:4] or ["HCP-only page detected from direct-domain review"])
        return result

    standalone_brand = exact_brand_domain(row["brand_name"], final_url)
    title_patient = any(term in title.upper() for term in ["PATIENT", "FOR PATIENTS", "OFFICIAL PATIENT"])
    # Patient-facing or mixed product pages. A standalone brand domain can be accepted
    # when it has patient/ISI/PI evidence or appears to be the canonical brand site.
    if is_patient_url(final_url) and (
        patient_hits
        or title_patient
        or (has_pi_isi and standalone_brand)
        or (standalone_brand and drug_product_signal(upper) and not weak_product_information_only_page(title, upper))
    ):
        result["accepted"] = "yes"
        result["accepted_audience"] = "patient"
        result["accepted_url"] = final_url
        evidence = patient_hits[:4]
        if has_pi_isi:
            evidence.append("PI/ISI present")
        if not evidence:
            evidence.append("standalone branded domain")
        result["verification_evidence"] = "; ".join(evidence)
        return result

    result["reject_reason"] = "patient/mixed candidate lacks patient or product-site evidence"
    return result


def apply_accepts(verification_rows):
    master = read_csv(RUN_DIR / "master_branded_drug_website_inventory_manual_reviewed.csv")
    hcp = read_csv(RUN_DIR / "hcp_branded_drug_websites_manual_reviewed.csv")
    patient = read_csv(RUN_DIR / "patient_branded_drug_websites_manual_reviewed.csv")

    master_by_brand = {base.norm_key(r["brand_name"]): r for r in master}

    removed_hcp_urls = {
        r["hcp_url"].rstrip("/").lower()
        for r in hcp
        if r.get("brand_metadata_method") == "nonblocked_followup_verified"
    }
    removed_patient_urls = {
        r["patient_url"].rstrip("/").lower()
        for r in patient
        if r.get("patient_discovery_method") == "nonblocked_followup_verified"
    }
    hcp = [r for r in hcp if r.get("brand_metadata_method") != "nonblocked_followup_verified"]
    patient = [r for r in patient if r.get("patient_discovery_method") != "nonblocked_followup_verified"]

    for row in master:
        if row["hcp_website_url"].rstrip("/").lower() in removed_hcp_urls:
            row["hcp_website_url"] = ""
            row["hcp_website_count_for_brand"] = "0"
        if row["patient_website_url"].rstrip("/").lower() in removed_patient_urls:
            row["patient_website_url"] = ""
            row["patient_website_count_for_brand"] = "0"
        has_hcp = bool(row["hcp_website_url"])
        has_patient = bool(row["patient_website_url"])
        if has_hcp and has_patient:
            row["website_classification"] = "both_hcp_and_patient_found"
            row["confidence"] = "high"
            row["uncertainty_notes"] = ""
        elif has_hcp:
            row["website_classification"] = "hcp_found_patient_not_found"
            row["confidence"] = "partial_manual_review"
            row["uncertainty_notes"] = "HCP URL found; patient URL not found by reviewed nonblocked follow-up."
        elif has_patient:
            row["website_classification"] = "patient_found_hcp_not_found"
            row["confidence"] = "partial_manual_review"
            row["uncertainty_notes"] = "Patient URL found; HCP URL not found by reviewed nonblocked follow-up."
        elif row["website_classification"] != "no_branded_site_found_after_manual_review_pass":
            row["website_classification"] = "no_branded_site_found_after_manual_review_pass"
            row["confidence"] = "manual_review_no_url_found"
            row["uncertainty_notes"] = "No official branded HCP or patient URL found by direct URL probes plus Bing query review."

    hcp_urls = {r["hcp_url"].rstrip("/").lower() for r in hcp}
    patient_urls = {r["patient_url"].rstrip("/").lower() for r in patient}
    applied = []

    # choose one URL per brand/audience, preferring hcp-specific paths for hcp and root/shorter URL for patient
    best = {}
    for row in verification_rows:
        if row["accepted"] != "yes":
            continue
        key = (base.norm_key(row["brand_name"]), row["accepted_audience"])
        current = best.get(key)
        if not current:
            best[key] = row
            continue
        if row["accepted_audience"] == "hcp":
            row_is_hcp_url = is_hcp_url(row["accepted_url"])
            current_is_hcp_url = is_hcp_url(current["accepted_url"])
            if row_is_hcp_url and not current_is_hcp_url:
                best[key] = row
            elif row_is_hcp_url == current_is_hcp_url and len(row["accepted_url"]) < len(current["accepted_url"]):
                best[key] = row
        else:
            if len(row["accepted_url"]) < len(current["accepted_url"]):
                best[key] = row

    for row in best.values():
        master_row = master_by_brand.get(base.norm_key(row["brand_name"]))
        if not master_row:
            continue
        if row["accepted_audience"] == "hcp":
            if not master_row["hcp_website_url"]:
                master_row["hcp_website_url"] = row["accepted_url"]
                master_row["hcp_website_count_for_brand"] = "1"
                if row["accepted_url"].rstrip("/").lower() not in hcp_urls:
                    hcp.append(
                        {
                            "brand_name": master_row["brand_name"],
                            "original_seed_brand_name": "",
                            "brand_metadata_method": "nonblocked_followup_verified",
                            "generic_name": master_row["generic_name"],
                            "company": master_row["manufacturer_or_labeler"],
                            "hcp_url": row["accepted_url"],
                            "hcp_url_original": row["candidate_url"],
                            "hcp_access_status": "nonblocked_followup_verified",
                            "hcp_retrieved_at": "2026-07-08",
                            "rwe_assessment": "not assessed",
                            "rwe_signals": "",
                            "promotional_message_verbatim": "",
                            "message_theme": "",
                            "fda_exact_brand_match_status": "matched_to_master_inventory",
                            "fda_source_confidence": master_row["fda_source_confidence"],
                            "fda_application_numbers": master_row["application_numbers"],
                            "scope_status": "in_scope_fda_matched_rx_brand",
                            "scope_exclusion_or_review_reason": "",
                        }
                    )
                    hcp_urls.add(row["accepted_url"].rstrip("/").lower())
                applied.append(row)
        elif row["accepted_audience"] == "patient":
            if not master_row["patient_website_url"]:
                master_row["patient_website_url"] = row["accepted_url"]
                master_row["patient_website_count_for_brand"] = "1"
                if row["accepted_url"].rstrip("/").lower() not in patient_urls:
                    patient.append(
                        {
                            "brand_name": master_row["brand_name"],
                            "generic_name": master_row["generic_name"],
                            "company": master_row["manufacturer_or_labeler"],
                            "patient_url": row["accepted_url"],
                            "patient_audience_evidence": row["verification_evidence"],
                            "patient_discovery_method": "nonblocked_followup_verified",
                        }
                    )
                    patient_urls.add(row["accepted_url"].rstrip("/").lower())
                applied.append(row)

        has_hcp = bool(master_row["hcp_website_url"])
        has_patient = bool(master_row["patient_website_url"])
        if has_hcp and has_patient:
            master_row["website_classification"] = "both_hcp_and_patient_found"
            master_row["confidence"] = "high"
            master_row["uncertainty_notes"] = ""
        elif has_hcp:
            master_row["website_classification"] = "hcp_found_patient_not_found"
            master_row["confidence"] = "partial_manual_review"
            master_row["uncertainty_notes"] = "HCP URL found; patient URL not found by reviewed nonblocked follow-up."
        elif has_patient:
            master_row["website_classification"] = "patient_found_hcp_not_found"
            master_row["confidence"] = "partial_manual_review"
            master_row["uncertainty_notes"] = "Patient URL found; HCP URL not found by reviewed nonblocked follow-up."

    unresolved = [
        r
        for r in master
        if r["website_classification"]
        in {
            "hcp_found_patient_not_found",
            "patient_found_hcp_not_found",
            "no_branded_site_found_after_manual_review_pass",
        }
    ]
    write_csv(RUN_DIR / "master_branded_drug_website_inventory_manual_reviewed.csv", master)
    write_csv(RUN_DIR / "hcp_branded_drug_websites_manual_reviewed.csv", hcp)
    write_csv(RUN_DIR / "patient_branded_drug_websites_manual_reviewed.csv", patient)
    write_csv(RUN_DIR / "unresolved_after_manual_review.csv", unresolved)
    return applied, master, hcp, patient, unresolved


def main():
    candidates = read_csv(RUN_DIR / "no_site_followup_probable_missed_direct_domains.csv")
    verification_rows = [verify_candidate(row) for row in candidates]
    write_csv(RUN_DIR / "nonblocked_candidate_verification.csv", verification_rows)

    applied, master, hcp, patient, unresolved = apply_accepts(verification_rows)
    summary = {
        "run_date": "2026-07-08",
        "nonblocked_candidate_rows_reviewed": len(candidates),
        "accepted_candidate_rows": sum(1 for r in verification_rows if r["accepted"] == "yes"),
        "accepted_hcp_rows": sum(1 for r in verification_rows if r["accepted_audience"] == "hcp"),
        "accepted_patient_rows": sum(1 for r in verification_rows if r["accepted_audience"] == "patient"),
        "applied_unique_brand_audience_rows": len(applied),
        "reject_reason_counts": dict(Counter(r["reject_reason"] for r in verification_rows if r["accepted"] != "yes")),
        "master_classification_counts_after_merge": dict(Counter(r["website_classification"] for r in master)),
        "hcp_unique_urls_after_merge": len({r["hcp_url"].rstrip("/").lower() for r in hcp}),
        "patient_unique_urls_after_merge": len({r["patient_url"].rstrip("/").lower() for r in patient}),
        "unresolved_rows_after_merge": len(unresolved),
    }
    (RUN_DIR / "nonblocked_candidate_merge_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
