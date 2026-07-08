import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import build_branded_drug_website_inventory as base
from build_inventory_from_fda_and_existing_seeds import read_csv, write_csv


RUN_DIR = Path(__file__).resolve().parent

VARIANT_TERMS = {
    "ACTPEN",
    "PFS",
    "PREFILLED",
    "SYRINGE",
    "TITRATION",
    "PACK",
    "REBIDOSE",
    "CO",
    "COPACK",
    "CO-PACK",
    "IV",
    "HD",
    "SV",
    "WR",
    "LAR",
    "DEPOT",
    "FASPRO",
    "HYBREZA",
    "DIGIHALER",
    "RESPICLICK",
    "AUTO",
    "AUTOINJECTOR",
    "PEN",
}


def norm_company(value):
    parts = [p.strip().lower() for p in (value or "").split(";") if p.strip()]
    cleaned = []
    for p in parts:
        p = re.sub(r"\b(inc|llc|l\.l\.c|corporation|corp|company|co|ltd|lp|usa|us)\b", "", p)
        p = re.sub(r"[^a-z0-9]+", " ", p).strip()
        if p:
            cleaned.append(p)
    return cleaned


def company_overlap(a, b):
    aa = norm_company(a)
    bb = norm_company(b)
    if not aa or not bb:
        return False
    for x in aa:
        for y in bb:
            if x in y or y in x:
                return True
    return False


def generic_key(value):
    value = base.norm_key(value)
    value = re.sub(r"\b(HUMAN|RECOMBINANT|ANHYDROUS|MONOHYDRATE)\b", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def base_tokens(brand):
    toks = re.findall(r"[A-Z0-9]+", base.norm_key(brand))
    output = []
    for tok in toks:
        if tok in VARIANT_TERMS:
            continue
        output.append(tok)
    return output


def base_brand_key(brand):
    toks = base_tokens(brand)
    if not toks:
        return ""
    return toks[0]


def is_variant_of(no_site, found):
    if no_site["brand_name"] == found["brand_name"]:
        return False
    no_base = base_brand_key(no_site["brand_name"])
    found_base = base_brand_key(found["brand_name"])
    if no_base and found_base and no_base == found_base:
        return True
    # Same generic/company with at least one shared brand token is a weaker but useful variant signal.
    if generic_key(no_site["generic_name"]) == generic_key(found["generic_name"]) and company_overlap(
        no_site["manufacturer_or_labeler"], found["manufacturer_or_labeler"]
    ):
        no_tokens = set(base_tokens(no_site["brand_name"]))
        found_tokens = set(base_tokens(found["brand_name"]))
        if no_tokens & found_tokens:
            return True
    return False


def main():
    master = read_csv(RUN_DIR / "master_branded_drug_website_inventory_manual_reviewed.csv")
    no_site = [
        r
        for r in master
        if r["website_classification"] == "no_branded_site_found_after_manual_review_pass"
    ]
    found = [r for r in master if r["hcp_website_url"] or r["patient_website_url"]]

    candidates = []
    for row in no_site:
        if base.looks_generic_brand(row["brand_name"], row["generic_name"]):
            continue
        matches = []
        for f in found:
            if is_variant_of(row, f):
                matches.append(f)
        # Prefer rows with both URLs, then HCP-only, then patient-only.
        matches = sorted(
            matches,
            key=lambda r: (
                bool(r["hcp_website_url"]) + bool(r["patient_website_url"]),
                len(r["brand_name"]),
            ),
            reverse=True,
        )
        if matches:
            f = matches[0]
            candidates.append(
                {
                    "unresolved_brand_name": row["brand_name"],
                    "unresolved_generic_name": row["generic_name"],
                    "unresolved_manufacturer_or_labeler": row["manufacturer_or_labeler"],
                    "matched_brand_name": f["brand_name"],
                    "matched_generic_name": f["generic_name"],
                    "matched_manufacturer_or_labeler": f["manufacturer_or_labeler"],
                    "suggested_hcp_url": f["hcp_website_url"],
                    "suggested_patient_url": f["patient_website_url"],
                    "basis": "base-brand or same-generic/manufacturer sibling already has branded URL",
                    "review_action": "verify whether unresolved row should inherit canonical brand URL or remain a formulation-specific no-site row",
                }
            )

    write_csv(RUN_DIR / "no_site_followup_sibling_inheritance_candidates.csv", candidates)
    summary = {
        "run_date": "2026-07-08",
        "no_site_rows_reviewed": len(no_site),
        "sibling_inheritance_candidate_rows": len(candidates),
        "candidate_rows_with_hcp_url": sum(1 for r in candidates if r["suggested_hcp_url"]),
        "candidate_rows_with_patient_url": sum(1 for r in candidates if r["suggested_patient_url"]),
        "method_note": "Candidates are unresolved variant rows whose base brand, formulation sibling, or same-generic/manufacturer sibling already has an HCP and/or patient URL in the reviewed master. These are suggested fixes requiring row-level verification before merge.",
    }
    (RUN_DIR / "no_site_followup_sibling_inheritance_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
