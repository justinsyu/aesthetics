import csv
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import build_branded_drug_website_inventory as base
from build_inventory_from_fda_and_existing_seeds import read_csv, write_csv
from manual_review_remaining_websites import direct_candidates


RUN_DIR = Path(__file__).resolve().parent
USER_AGENT = base.USER_AGENT


def probe(url):
    req = Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with urlopen(req, timeout=8) as response:
            final_url = response.geturl()
            ctype = response.headers.get("content-type", "")
            text = ""
            if "text/html" in ctype or "text/plain" in ctype:
                text = response.read(80_000).decode("utf-8", errors="ignore")
            return {"url": url, "final_url": final_url, "status": str(response.status), "content_type": ctype, "text": text, "error": ""}
    except HTTPError as exc:
        return {"url": url, "final_url": exc.geturl() or url, "status": str(exc.code), "content_type": exc.headers.get("content-type", "") if exc.headers else "", "text": "", "error": "HTTPError"}
    except URLError as exc:
        return {"url": url, "final_url": "", "status": "", "content_type": "", "text": "", "error": type(exc.reason).__name__}
    except Exception as exc:
        return {"url": url, "final_url": "", "status": "", "content_type": "", "text": "", "error": type(exc).__name__}


def host_has_brand(brand, url):
    return base.brand_slug(brand) in base.brand_slug(url)


def audit_row(row):
    if base.looks_generic_brand(row["brand_name"], row["generic_name"]):
        return []
    tasks = []
    for audience in ["hcp", "patient"]:
        for url in direct_candidates(row["brand_name"], audience):
            if host_has_brand(row["brand_name"], url):
                tasks.append((audience, url))
    found = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(probe, url): (audience, url) for audience, url in tasks}
        for future in as_completed(futures):
            audience, _ = futures[future]
            result = future.result()
            status = result["status"]
            text_up = result["text"].upper()
            if status in {"200", "301", "302", "403"}:
                # Keep blocked direct brand domains and pages with visible brand/audience text as possible misses.
                evidence = []
                if base.norm_key(row["brand_name"]) in base.norm_key(result["text"]):
                    evidence.append("visible brand text")
                if "HEALTHCARE PROFESSIONAL" in text_up or "HCP" in text_up or "PRESCRIBING INFORMATION" in text_up:
                    evidence.append("HCP text")
                if "PATIENT" in text_up or "SAVINGS" in text_up or "COPAY" in text_up or "CO-PAY" in text_up:
                    evidence.append("patient text")
                if status == "403":
                    evidence.append("direct branded domain blocks simple HTTP")
                if status == "200" and not evidence:
                    continue
                found.append(
                    {
                        "brand_name": row["brand_name"],
                        "generic_name": row["generic_name"],
                        "manufacturer_or_labeler": row["manufacturer_or_labeler"],
                        "candidate_audience": audience,
                        "candidate_url": result["final_url"] or result["url"],
                        "status": status,
                        "content_type": result["content_type"],
                        "evidence": "; ".join(evidence),
                        "review_action": "verify in browser before merging; candidate identified from direct brand-domain probe",
                    }
                )
    return found


def main():
    master = read_csv(RUN_DIR / "master_branded_drug_website_inventory_manual_reviewed.csv")
    rows = [
        r
        for r in master
        if r["website_classification"] == "no_branded_site_found_after_manual_review_pass"
    ]
    all_found = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(audit_row, row): row for row in rows}
        completed = 0
        for future in as_completed(futures):
            all_found.extend(future.result())
            completed += 1
            if completed % 50 == 0:
                print(f"direct audited {completed} / {len(rows)}")
    write_csv(RUN_DIR / "no_site_followup_direct_blocked_domain_candidates.csv", all_found)
    summary = {
        "run_date": "2026-07-08",
        "no_site_rows_audited": len(rows),
        "candidate_rows": len(all_found),
        "brands_with_candidates": len({base.norm_key(r["brand_name"]) for r in all_found}),
        "status_counts": dict(Counter(r["status"] for r in all_found)),
        "audience_counts": dict(Counter(r["candidate_audience"] for r in all_found)),
        "method_note": "Direct brand-domain probe over no-site rows. Includes 403/blocked branded domains as possible misses, but candidates require browser verification before merging.",
    }
    (RUN_DIR / "no_site_followup_direct_blocked_domain_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
