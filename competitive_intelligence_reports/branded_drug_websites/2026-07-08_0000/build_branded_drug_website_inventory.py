import csv
import io
import json
import re
import time
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen


RUN_DIR = Path(__file__).resolve().parent
RAW_DIR = RUN_DIR / "raw"
WORKING_DIR = RUN_DIR / "working"
TODAY = date(2026, 7, 8)

URLS = {
    "ndc_text_zip": "https://www.accessdata.fda.gov/cder/ndctext.zip",
    "orange_book_zip": "https://www.fda.gov/media/76860/download?attachment",
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
)

GENERIC_WORDS = {
    "TABLETS",
    "TABLET",
    "CAPSULES",
    "CAPSULE",
    "INJECTION",
    "SOLUTION",
    "SUSPENSION",
    "CREAM",
    "OINTMENT",
    "GEL",
    "PATCH",
    "KIT",
    "SYRINGE",
    "VIAL",
    "PEN",
    "AUTO-INJECTOR",
    "AUTOINJECTOR",
    "PREFILLED",
    "EXTENDED",
    "RELEASE",
    "DELAYED",
    "ORAL",
    "TOPICAL",
    "OPHTHALMIC",
    "INTRAVENOUS",
    "SUBCUTANEOUS",
    "FOR",
    "USP",
    "HCL",
    "HYDROCHLORIDE",
    "SODIUM",
    "POTASSIUM",
}

EXCLUDE_NAME_PATTERNS = [
    r"\bVACCINE\b",
    r"\bCOVID-19\b",
    r"\bSARS-COV-2\b",
    r"\bINFLUENZA\b",
    r"\bHEPATITIS [AB]\b",
    r"\bMEASLES\b",
    r"\bMUMPS\b",
    r"\bRUBELLA\b",
    r"\bVARICELLA\b",
    r"\bPNEUMOCOCCAL\b",
    r"\bMENINGOCOCCAL\b",
    r"\bPOLIOVIRUS\b",
    r"\bROTAVIRUS\b",
    r"\bTETANUS\b",
    r"\bDIPHTHERIA\b",
    r"\bPERTUSSIS\b",
    r"\bRABIES\b",
    r"\bTYPHOID\b",
    r"\bSMALLPOX\b",
    r"\bANTIGEN\b",
    r"\bCONTROL\b",
    r"\bREAGENT\b",
    r"\bTEST\b",
    r"\bDIAGNOSTIC\b",
]


def fetch(url, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size:
        return out_path
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=90) as response:
        out_path.write_bytes(response.read())
    return out_path


def sniff_delimiter(sample):
    for delimiter in ["\t", "~", ",", "|"]:
        if delimiter in sample:
            return delimiter
    return ","


def read_zip_table(zip_path, member_name):
    with zipfile.ZipFile(zip_path) as zf:
        names = {name.lower(): name for name in zf.namelist()}
        actual = names[member_name.lower()]
        data = zf.read(actual)
    text = data.decode("utf-8-sig", errors="replace")
    delimiter = sniff_delimiter(text[:4096])
    return list(csv.DictReader(io.StringIO(text), delimiter=delimiter))


def normalize_text(value):
    value = (value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def norm_key(value):
    value = normalize_text(value).upper()
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def brand_slug(value):
    value = norm_key(value).lower()
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def looks_generic_brand(name, generic):
    name_key = norm_key(name)
    generic_key = norm_key(generic)
    if not name_key:
        return True
    if name_key == generic_key:
        return True
    if name_key in generic_key or generic_key in name_key:
        if len(name_key) > 5 and len(generic_key) > 5:
            return True
    tokens = [tok for tok in name_key.split() if tok not in GENERIC_WORDS]
    generic_tokens = set(generic_key.split())
    if tokens and all(tok in generic_tokens for tok in tokens):
        return True
    return False


def excluded_by_name(*values):
    haystack = " ".join(norm_key(v) for v in values)
    return any(re.search(pattern, haystack) for pattern in EXCLUDE_NAME_PATTERNS)


def is_active_ndc(row):
    end = normalize_text(row.get("ENDMARKETINGDATE"))
    if not end:
        return True
    try:
        end_date = date(int(end[:4]), int(end[4:6]), int(end[6:8]))
    except Exception:
        return True
    return end_date >= TODAY


def ndc_brand_rows(product_rows):
    rows = []
    for row in product_rows:
        product_type = normalize_text(row.get("PRODUCTTYPENAME"))
        if product_type != "HUMAN PRESCRIPTION DRUG":
            continue
        if not is_active_ndc(row):
            continue
        brand = normalize_text(row.get("PROPRIETARYNAME"))
        generic = normalize_text(row.get("NONPROPRIETARYNAME"))
        labeler = normalize_text(row.get("LABELERNAME"))
        marketing_category = normalize_text(row.get("MARKETINGCATEGORYNAME"))
        if not brand:
            continue
        if excluded_by_name(brand, generic, row.get("PHARM_CLASSES")):
            continue
        application = normalize_text(row.get("APPLICATIONNUMBER"))
        high_confidence_source = marketing_category in {
            "NDA",
            "BLA",
            "NDA AUTHORIZED GENERIC",
        } or application.startswith(("NDA", "BLA"))
        generic_like = looks_generic_brand(brand, generic)
        if not high_confidence_source and generic_like:
            continue
        rows.append(
            {
                "brand_name": brand,
                "brand_key": norm_key(brand),
                "brand_slug": brand_slug(brand),
                "generic_name": generic,
                "labeler": labeler,
                "product_type": product_type,
                "marketing_category": marketing_category,
                "application_number": application,
                "dosage_form": normalize_text(row.get("DOSAGEFORMNAME")),
                "route": normalize_text(row.get("ROUTENAME")),
                "start_marketing_date": normalize_text(row.get("STARTMARKETINGDATE")),
                "end_marketing_date": normalize_text(row.get("ENDMARKETINGDATE")),
                "listing_expiration_date": normalize_text(
                    row.get("LISTING_RECORD_CERTIFIED_THROUGH")
                ),
                "pharm_classes": normalize_text(row.get("PHARM_CLASSES")),
                "source_basis": "FDA NDC Directory active human prescription listing",
                "source_confidence": "high"
                if high_confidence_source and not generic_like
                else "medium",
                "uncertainty_notes": ""
                if high_confidence_source and not generic_like
                else "Brand status inferred from active NDC listing; review if this is a generic-style private-label product.",
            }
        )
    return rows


def aggregate_brands(rows):
    grouped = {}
    for row in rows:
        key = (row["brand_key"], norm_key(row["generic_name"]))
        if key not in grouped:
            grouped[key] = dict(row)
            grouped[key]["labelers_all"] = set()
            grouped[key]["marketing_categories_all"] = set()
            grouped[key]["application_numbers_all"] = set()
            grouped[key]["dosage_forms_all"] = set()
            grouped[key]["routes_all"] = set()
        item = grouped[key]
        for field, target in [
            ("labeler", "labelers_all"),
            ("marketing_category", "marketing_categories_all"),
            ("application_number", "application_numbers_all"),
            ("dosage_form", "dosage_forms_all"),
            ("route", "routes_all"),
        ]:
            if row[field]:
                item[target].add(row[field])
        if row["source_confidence"] == "high":
            item["source_confidence"] = "high"
    output = []
    for item in grouped.values():
        for field in [
            "labelers_all",
            "marketing_categories_all",
            "application_numbers_all",
            "dosage_forms_all",
            "routes_all",
        ]:
            item[field] = "; ".join(sorted(item[field]))
        output.append(item)
    return sorted(output, key=lambda r: (r["brand_key"], r["generic_name"]))


def parse_orange_book(zip_path):
    rows = read_zip_table(zip_path, "Products.txt")
    retained = set()
    for row in rows:
        trade = normalize_text(row.get("Trade_Name") or row.get("Trade Name"))
        ingredient = normalize_text(row.get("Ingredient"))
        drug_type = normalize_text(row.get("Type"))
        appl_type = normalize_text(row.get("Appl_Type"))
        if drug_type != "RX" or appl_type != "N":
            continue
        if excluded_by_name(trade, ingredient):
            continue
        retained.add((norm_key(trade), norm_key(ingredient)))
    return retained


def search_url(query):
    return f"https://www.bing.com/search?q={quote_plus(query)}"


def candidate_urls(brand):
    slug = brand_slug(brand)
    if not slug or len(slug) < 3:
        return []
    bases = [
        f"https://www.{slug}.com/",
        f"https://{slug}.com/",
        f"https://www.{slug}hcp.com/",
        f"https://{slug}hcp.com/",
        f"https://www.{slug}pro.com/",
        f"https://{slug}pro.com/",
        f"https://hcp.{slug}.com/",
        f"https://www.{slug}.com/hcp",
        f"https://www.{slug}.com/healthcare-professionals",
        f"https://www.{slug}.com/patient",
        f"https://www.{slug}.com/patients",
    ]
    return bases


def fetch_page(url):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=12) as response:
            final_url = response.geturl()
            content_type = response.headers.get("content-type", "")
            data = response.read(500_000)
        if "text/html" not in content_type and "text/plain" not in content_type:
            return final_url, "", f"non_html:{content_type}"
        return final_url, data.decode("utf-8", errors="ignore"), ""
    except HTTPError as exc:
        return url, "", f"http_{exc.code}"
    except URLError as exc:
        return url, "", f"url_error:{exc.reason}"
    except Exception as exc:
        return url, "", f"error:{type(exc).__name__}"


def clean_html_text(html):
    html = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", html)
    html = re.sub(r"(?is)<[^>]+>", " ", html)
    html = re.sub(r"&nbsp;|&#160;", " ", html)
    html = re.sub(r"&amp;", "&", html)
    return re.sub(r"\s+", " ", html).strip()


def classify_page(brand, html):
    text = clean_html_text(html)
    upper = text.upper()
    brand_key = norm_key(brand)
    evidence = []
    if brand_key and brand_key in upper:
        evidence.append("brand name visible")
    audience = []
    hcp_patterns = [
        "FOR HEALTHCARE PROFESSIONALS",
        "FOR US HEALTHCARE PROFESSIONALS",
        "FOR U.S. HEALTHCARE PROFESSIONALS",
        "HEALTHCARE PROFESSIONALS",
        "HEALTH CARE PROFESSIONALS",
        "HCP",
        "PRESCRIBING INFORMATION",
    ]
    patient_patterns = [
        "FOR PATIENTS",
        "PATIENTS AND CAREGIVERS",
        "PATIENT SUPPORT",
        "SAVINGS CARD",
        "COPAY",
        "TALK TO YOUR DOCTOR",
    ]
    for pattern in hcp_patterns:
        if pattern in upper:
            audience.append("hcp")
            evidence.append(pattern.lower())
            break
    for pattern in patient_patterns:
        if pattern in upper:
            audience.append("patient")
            evidence.append(pattern.lower())
            break
    if "IMPORTANT SAFETY INFORMATION" in upper:
        evidence.append("important safety information")
    if not audience:
        audience.append("mixed_or_unknown")
    return "+".join(sorted(set(audience))), "; ".join(evidence[:5]), text[:300]


def discover_candidate_sites(rows, max_rows=None):
    discovered = []
    checked = 0
    for row in rows[: max_rows or len(rows)]:
        found_for_brand = []
        for url in candidate_urls(row["brand_name"]):
            final_url, html, error = fetch_page(url)
            checked += 1
            if error:
                continue
            audience, evidence, snippet = classify_page(row["brand_name"], html)
            if "brand name visible" not in evidence and row["brand_slug"] not in urlparse(final_url).netloc.lower():
                continue
            found_for_brand.append(
                {
                    "brand_name": row["brand_name"],
                    "generic_name": row["generic_name"],
                    "labeler": row["labeler"],
                    "source_url_checked": url,
                    "final_url": final_url,
                    "audience_signal": audience,
                    "evidence": evidence,
                    "snippet": snippet,
                    "discovery_method": "candidate domain/url probe",
                }
            )
            time.sleep(0.15)
        if not found_for_brand:
            discovered.append(
                {
                    "brand_name": row["brand_name"],
                    "generic_name": row["generic_name"],
                    "labeler": row["labeler"],
                    "source_url_checked": "",
                    "final_url": "",
                    "audience_signal": "not_found_by_candidate_probe",
                    "evidence": "",
                    "snippet": "",
                    "discovery_method": "candidate domain/url probe",
                }
            )
        else:
            discovered.extend(found_for_brand)
    return discovered, checked


def write_csv(path, rows, fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fieldnames:
        keys = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    WORKING_DIR.mkdir(parents=True, exist_ok=True)

    ndc_zip = fetch(URLS["ndc_text_zip"], RAW_DIR / "ndctext.zip")
    orange_zip = fetch(URLS["orange_book_zip"], RAW_DIR / "orange_book.zip")

    ndc_products = read_zip_table(ndc_zip, "product.txt")
    brand_rows = ndc_brand_rows(ndc_products)
    brands = aggregate_brands(brand_rows)
    orange_book_n_rx = parse_orange_book(orange_zip)

    for row in brands:
        pair = (row["brand_key"], norm_key(row["generic_name"]))
        row["orange_book_innovator_rx_match"] = "yes" if pair in orange_book_n_rx else "no"
        if row["orange_book_innovator_rx_match"] == "yes":
            row["source_confidence"] = "high"

    high = [row for row in brands if row["source_confidence"] == "high"]
    medium = [row for row in brands if row["source_confidence"] != "high"]

    discovered, checked = discover_candidate_sites(high)

    summary = {
        "run_date": str(TODAY),
        "ndc_product_rows": len(ndc_products),
        "active_human_prescription_candidate_ndc_rows": len(brand_rows),
        "unique_candidate_brand_generic_pairs": len(brands),
        "high_confidence_brand_generic_pairs": len(high),
        "medium_confidence_brand_generic_pairs": len(medium),
        "orange_book_innovator_rx_brand_generic_pairs": len(orange_book_n_rx),
        "candidate_site_urls_checked": checked,
        "candidate_site_records": len(discovered),
        "source_urls": URLS,
        "notes": [
            "NDC Directory is used as the marketed-status spine for finished marketed products submitted in SPL listing.",
            "High-confidence rows are NDC NDA/BLA/NDA authorized generic or Orange Book NDA RX matches after vaccine/OTC/diagnostic-style exclusions.",
            "Website discovery in this builder uses deterministic candidate URL probing only; search-engine and manual QA should be layered on top for completeness.",
        ],
    }

    write_csv(WORKING_DIR / "ndc_active_human_rx_brand_rows.csv", brand_rows)
    write_csv(WORKING_DIR / "branded_rx_universe_candidates_all.csv", brands)
    write_csv(WORKING_DIR / "branded_rx_universe_high_confidence.csv", high)
    write_csv(WORKING_DIR / "branded_rx_universe_medium_review.csv", medium)
    write_csv(WORKING_DIR / "candidate_site_probe_results.csv", discovered)
    (RUN_DIR / "run_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    site_counts = Counter(row["audience_signal"] for row in discovered)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("site_signal_counts", dict(site_counts))


if __name__ == "__main__":
    main()
