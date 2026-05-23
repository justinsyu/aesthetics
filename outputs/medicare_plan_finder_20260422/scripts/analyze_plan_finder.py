#!/usr/bin/env python3
"""Reproducible summaries for the April 2026 CMS Plan Finder PUF.

Inputs are the extracted pipe-delimited component files from the CMS
Monthly Prescription Drug Plan Formulary and Pharmacy Network Information
release dated 2026-04-22.
"""

from __future__ import annotations

import json
import math
import os
import re
import urllib.request
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "extracted"
ANALYSIS = ROOT / "analysis"
ANALYSIS.mkdir(exist_ok=True)


FILES = {
    "plan": EXTRACTED / "plan information  20260430.txt",
    "basic": EXTRACTED / "basic drugs formulary file  20260430.txt",
    "beneficiary": EXTRACTED / "beneficiary cost file  20260430.txt",
    "excluded": EXTRACTED / "excluded drugs formulary file  20260430.txt",
    "ibc": EXTRACTED / "Indication Based Coverage Formulary File  20260430.txt",
    "insulin": EXTRACTED / "insulin beneficiary cost file  20260430.txt",
    "geo": EXTRACTED / "geographic locator file 20260430.txt",
}

PHARMACY_ZIPS = sorted(EXTRACTED.glob("pharmacy networks file  20260430 part *.zip"))


def read_pipe(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="|", dtype=str, keep_default_na=False, encoding="latin1")


def to_num(series: pd.Series) -> pd.Series:
    clean = series.astype(str).str.strip().replace({"": None, " ": None})
    return pd.to_numeric(clean, errors="coerce")


def pct(value: float) -> float:
    if pd.isna(value):
        return math.nan
    return round(float(value) * 100, 1)


def contract_type(contract_id: str) -> str:
    if contract_id.startswith("S"):
        return "Stand-alone PDP"
    if contract_id.startswith("R"):
        return "Regional MA-PD"
    if contract_id.startswith("H"):
        return "Local MA-PD"
    return "Other"


def p25(series: pd.Series) -> float:
    return float(series.quantile(0.25))


def p75(series: pd.Series) -> float:
    return float(series.quantile(0.75))


def summarize_numeric(series: pd.Series) -> dict[str, float | int]:
    s = series.dropna()
    return {
        "n": int(s.shape[0]),
        "mean": round(float(s.mean()), 2) if len(s) else math.nan,
        "median": round(float(s.median()), 2) if len(s) else math.nan,
        "p25": round(p25(s), 2) if len(s) else math.nan,
        "p75": round(p75(s), 2) if len(s) else math.nan,
        "min": round(float(s.min()), 2) if len(s) else math.nan,
        "max": round(float(s.max()), 2) if len(s) else math.nan,
    }


def rxnorm_names(rxcuis: list[str]) -> dict[str, str]:
    cache_path = ANALYSIS / "rxnorm_names_cache.json"
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())
    else:
        cache = {}

    for rxcui in rxcuis:
        if rxcui in cache:
            continue
        url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json"
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            props = payload.get("properties", {})
            cache[rxcui] = props.get("name") or props.get("synonym") or ""
        except Exception:
            cache[rxcui] = ""

    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True))
    return {rxcui: cache.get(rxcui, "") for rxcui in rxcuis}


def add_frames(existing: pd.DataFrame | None, new: pd.DataFrame) -> pd.DataFrame:
    if existing is None:
        return new.copy()
    return existing.add(new, fill_value=0)


def profile_pharmacy_network(plans: pd.DataFrame) -> dict[str, object] | None:
    if not PHARMACY_ZIPS:
        return None

    plan_counts: pd.DataFrame | None = None
    fee_counts = {
        "rows": 0,
        "selected_fee_nonmissing_30": 0,
        "selected_fee_lt_brand_30": 0,
        "selected_fee_eq_brand_30": 0,
        "selected_fee_gt_brand_30": 0,
        "selected_fee_lt_generic_30": 0,
        "selected_fee_eq_generic_30": 0,
        "selected_fee_gt_generic_30": 0,
    }
    usecols = [
        "CONTRACT_ID",
        "PLAN_ID",
        "SEGMENT_ID",
        "PHARMACY_NUMBER",
        "PHARMACY_ZIPCODE",
        "PREFERRED_STATUS_RETAIL",
        "PREFERRED_STATUS_MAIL",
        "PHARMACY_RETAIL",
        "PHARMACY_MAIL",
        "IN_AREA_FLAG",
        "BRAND_DISPENSING_FEE_30",
        "GENERIC_DISPENSING_FEE_30",
        "SELECTED_DISPENSING_FEE_30",
    ]

    for zip_path in PHARMACY_ZIPS:
        chunks = pd.read_csv(
            zip_path,
            sep="|",
            dtype=str,
            keep_default_na=False,
            encoding="latin1",
            compression="zip",
            usecols=usecols,
            chunksize=1_000_000,
        )
        for chunk in chunks:
            chunk["plan_key"] = chunk["CONTRACT_ID"] + "-" + chunk["PLAN_ID"] + "-" + chunk["SEGMENT_ID"]
            retail = (chunk["PHARMACY_RETAIL"] == "Y") & (chunk["IN_AREA_FLAG"] == "1")
            preferred_retail = retail & (chunk["PREFERRED_STATUS_RETAIL"] == "Y")
            mail = chunk["PHARMACY_MAIL"] == "Y"
            preferred_mail = mail & (chunk["PREFERRED_STATUS_MAIL"] == "Y")
            agg = pd.DataFrame(
                {
                    "network_rows": chunk.groupby("plan_key").size(),
                    "retail_in_area_rows": retail.groupby(chunk["plan_key"]).sum(),
                    "preferred_retail_in_area_rows": preferred_retail.groupby(chunk["plan_key"]).sum(),
                    "mail_rows": mail.groupby(chunk["plan_key"]).sum(),
                    "preferred_mail_rows": preferred_mail.groupby(chunk["plan_key"]).sum(),
                }
            )
            plan_counts = add_frames(plan_counts, agg)

            brand = to_num(chunk["BRAND_DISPENSING_FEE_30"])
            generic = to_num(chunk["GENERIC_DISPENSING_FEE_30"])
            selected = to_num(chunk["SELECTED_DISPENSING_FEE_30"])
            nonmissing = selected.notna()
            fee_counts["rows"] += int(chunk.shape[0])
            fee_counts["selected_fee_nonmissing_30"] += int(nonmissing.sum())
            fee_counts["selected_fee_lt_brand_30"] += int((nonmissing & brand.notna() & (selected < brand)).sum())
            fee_counts["selected_fee_eq_brand_30"] += int((nonmissing & brand.notna() & (selected == brand)).sum())
            fee_counts["selected_fee_gt_brand_30"] += int((nonmissing & brand.notna() & (selected > brand)).sum())
            fee_counts["selected_fee_lt_generic_30"] += int((nonmissing & generic.notna() & (selected < generic)).sum())
            fee_counts["selected_fee_eq_generic_30"] += int((nonmissing & generic.notna() & (selected == generic)).sum())
            fee_counts["selected_fee_gt_generic_30"] += int((nonmissing & generic.notna() & (selected > generic)).sum())

    assert plan_counts is not None
    plan_counts = plan_counts.reset_index().rename(columns={"index": "plan_key"})
    for col in plan_counts.columns:
        if col != "plan_key":
            plan_counts[col] = plan_counts[col].astype(int)
    plan_counts["preferred_retail_share_in_area"] = (
        plan_counts["preferred_retail_in_area_rows"] / plan_counts["retail_in_area_rows"].replace({0: pd.NA})
    )
    plan_counts = plan_counts.merge(plans[["plan_key", "contract_type"]], on="plan_key", how="left")
    plan_counts.to_csv(ANALYSIS / "pharmacy_network_plan_summary.csv", index=False)

    by_type = []
    for label, frame in [("All plans", plan_counts)] + list(plan_counts.groupby("contract_type")):
        by_type.append(
            {
                "segment": label,
                "plans_with_network_rows": int(frame["plan_key"].nunique()),
                "median_retail_in_area_rows": round(float(frame["retail_in_area_rows"].median()), 0),
                "median_preferred_retail_in_area_rows": round(float(frame["preferred_retail_in_area_rows"].median()), 0),
                "median_preferred_retail_share_in_area_pct": round(float(frame["preferred_retail_share_in_area"].median() * 100), 1),
                "plans_with_mail_order_pct": pct((frame["mail_rows"] > 0).mean()),
                "plans_with_preferred_mail_order_pct": pct((frame["preferred_mail_rows"] > 0).mean()),
            }
        )
    by_type_df = pd.DataFrame(by_type)
    by_type_df.to_csv(ANALYSIS / "pharmacy_network_summary.csv", index=False)

    denominator = fee_counts["selected_fee_nonmissing_30"] or 1
    fee_summary = {
        **fee_counts,
        "selected_fee_nonmissing_pct": pct(fee_counts["selected_fee_nonmissing_30"] / fee_counts["rows"]),
        "selected_fee_lt_brand_pct_among_nonmissing": pct(fee_counts["selected_fee_lt_brand_30"] / denominator),
        "selected_fee_eq_brand_pct_among_nonmissing": pct(fee_counts["selected_fee_eq_brand_30"] / denominator),
        "selected_fee_gt_brand_pct_among_nonmissing": pct(fee_counts["selected_fee_gt_brand_30"] / denominator),
        "selected_fee_lt_generic_pct_among_nonmissing": pct(fee_counts["selected_fee_lt_generic_30"] / denominator),
        "selected_fee_eq_generic_pct_among_nonmissing": pct(fee_counts["selected_fee_eq_generic_30"] / denominator),
        "selected_fee_gt_generic_pct_among_nonmissing": pct(fee_counts["selected_fee_gt_generic_30"] / denominator),
    }
    (ANALYSIS / "pharmacy_selected_fee_summary.json").write_text(json.dumps(fee_summary, indent=2))
    return {
        "network_summary": by_type_df.to_dict(orient="records"),
        "selected_fee_summary": fee_summary,
        "pharmacy_zip_parts": [p.name for p in PHARMACY_ZIPS],
    }


def main() -> None:
    plan = read_pipe(FILES["plan"])
    basic = read_pipe(FILES["basic"])
    beneficiary = read_pipe(FILES["beneficiary"])
    excluded = read_pipe(FILES["excluded"])
    ibc = read_pipe(FILES["ibc"])
    insulin = read_pipe(FILES["insulin"])
    geo = read_pipe(FILES["geo"])

    plan["plan_key"] = plan["CONTRACT_ID"] + "-" + plan["PLAN_ID"] + "-" + plan["SEGMENT_ID"]
    plan["contract_type"] = plan["CONTRACT_ID"].map(contract_type)
    plan["PREMIUM_NUM"] = to_num(plan["PREMIUM"])
    plan["DEDUCTIBLE_NUM"] = to_num(plan["DEDUCTIBLE"])
    unique_plan_cols = [
        "plan_key",
        "CONTRACT_ID",
        "PLAN_ID",
        "SEGMENT_ID",
        "CONTRACT_NAME",
        "PLAN_NAME",
        "FORMULARY_ID",
        "PREMIUM_NUM",
        "DEDUCTIBLE_NUM",
        "SNP",
        "PLAN_SUPPRESSED_YN",
        "contract_type",
    ]
    plans = plan[unique_plan_cols].drop_duplicates("plan_key").copy()

    service_rows = (
        plan.groupby("plan_key", as_index=False)
        .agg(
            service_area_rows=("COUNTY_CODE", "size"),
            states=("STATE", lambda s: ";".join(sorted(set(x for x in s if x.strip())))),
            county_rows=("COUNTY_CODE", lambda s: sum(1 for x in s if x.strip())),
            pdp_regions=("PDP_REGION_CODE", lambda s: ";".join(sorted(set(x for x in s if x.strip())))),
        )
    )
    plans = plans.merge(service_rows, on="plan_key", how="left")

    plan_summary_rows = []
    for label, frame in [("All plans", plans)] + list(plans.groupby("contract_type")):
        plan_summary_rows.append(
            {
                "segment": label,
                "plans": int(frame.shape[0]),
                "suppressed_plans": int((frame["PLAN_SUPPRESSED_YN"] == "Y").sum()),
                "median_premium": round(float(frame["PREMIUM_NUM"].median()), 2),
                "p25_premium": round(float(frame["PREMIUM_NUM"].quantile(0.25)), 2),
                "p75_premium": round(float(frame["PREMIUM_NUM"].quantile(0.75)), 2),
                "zero_premium_pct": pct((frame["PREMIUM_NUM"] == 0).mean()),
                "median_deductible": round(float(frame["DEDUCTIBLE_NUM"].median()), 2),
                "deductible_615_pct": pct((frame["DEDUCTIBLE_NUM"] >= 615).mean()),
            }
        )
    pd.DataFrame(plan_summary_rows).to_csv(ANALYSIS / "plan_summary.csv", index=False)

    pdp_region_summary = (
        plan.loc[plan["contract_type"] == "Stand-alone PDP"]
        .drop_duplicates(["plan_key", "PDP_REGION_CODE"])
        .groupby("PDP_REGION_CODE", as_index=False)
        .agg(
            plans=("plan_key", "nunique"),
            median_premium=("PREMIUM_NUM", "median"),
            min_premium=("PREMIUM_NUM", "min"),
            max_premium=("PREMIUM_NUM", "max"),
            median_deductible=("DEDUCTIBLE_NUM", "median"),
        )
        .sort_values("median_premium", ascending=False)
    )
    pdp_region_summary.to_csv(ANALYSIS / "pdp_region_summary.csv", index=False)

    local_county_availability = (
        plan.loc[(plan["contract_type"] == "Local MA-PD") & (plan["PLAN_SUPPRESSED_YN"] != "Y")]
        .groupby(["STATE", "COUNTY_CODE"], as_index=False)
        .agg(local_ma_pd_plans=("plan_key", "nunique"))
        .merge(geo[["COUNTY_CODE", "COUNTY", "STATENAME"]], on="COUNTY_CODE", how="left")
    )
    local_county_availability.to_csv(ANALYSIS / "local_ma_pd_county_availability.csv", index=False)

    for col in ["TIER_LEVEL_VALUE", "QUANTITY_LIMIT_AMOUNT", "QUANTITY_LIMIT_DAYS"]:
        basic[col + "_NUM"] = to_num(basic[col])

    basic["restriction_count"] = (
        (basic["QUANTITY_LIMIT_YN"] == "Y").astype(int)
        + (basic["PRIOR_AUTHORIZATION_YN"] == "Y").astype(int)
        + (basic["STEP_THERAPY_YN"] == "Y").astype(int)
    )
    basic_formulary = (
        basic.groupby("FORMULARY_ID", as_index=False)
        .agg(
            ndc_count=("NDC", "nunique"),
            rxcui_count=("RXCUI", "nunique"),
            ql_ndc_pct=("QUANTITY_LIMIT_YN", lambda s: pct((s == "Y").mean())),
            pa_ndc_pct=("PRIOR_AUTHORIZATION_YN", lambda s: pct((s == "Y").mean())),
            st_ndc_pct=("STEP_THERAPY_YN", lambda s: pct((s == "Y").mean())),
            any_um_ndc_pct=("restriction_count", lambda s: pct((s > 0).mean())),
            selected_ndc_count=("SELECTED_DRUG_YN", lambda s: int((s == "Y").sum())),
            selected_rxcui_count=("RXCUI", lambda s: int(basic.loc[s.index].loc[basic.loc[s.index, "SELECTED_DRUG_YN"] == "Y", "RXCUI"].nunique())),
            median_tier=("TIER_LEVEL_VALUE_NUM", "median"),
        )
    )
    basic_formulary.to_csv(ANALYSIS / "formulary_summary_by_formulary.csv", index=False)

    plan_formulary = plans.merge(basic_formulary, on="FORMULARY_ID", how="left")
    formulary_plan_summary_rows = []
    for label, frame in [("All plans", plan_formulary)] + list(plan_formulary.groupby("contract_type")):
        formulary_plan_summary_rows.append(
            {
                "segment": label,
                "plans_with_formulary": int(frame["ndc_count"].notna().sum()),
                "median_ndcs": round(float(frame["ndc_count"].median()), 0),
                "median_rxcui": round(float(frame["rxcui_count"].median()), 0),
                "median_ql_ndc_pct": round(float(frame["ql_ndc_pct"].median()), 1),
                "median_pa_ndc_pct": round(float(frame["pa_ndc_pct"].median()), 1),
                "median_st_ndc_pct": round(float(frame["st_ndc_pct"].median()), 1),
                "median_any_um_ndc_pct": round(float(frame["any_um_ndc_pct"].median()), 1),
                "plans_with_selected_drug_entries_pct": pct((frame["selected_ndc_count"].fillna(0) > 0).mean()),
            }
        )
    pd.DataFrame(formulary_plan_summary_rows).to_csv(ANALYSIS / "formulary_plan_summary.csv", index=False)

    selected = basic.loc[basic["SELECTED_DRUG_YN"] == "Y"].copy()
    selected_names = rxnorm_names(sorted(selected["RXCUI"].unique().tolist()))
    selected["rxnorm_name"] = selected["RXCUI"].map(selected_names)
    selected["restriction_label"] = selected.apply(
        lambda r: ",".join(
            label
            for label, flag in [
                ("QL", r["QUANTITY_LIMIT_YN"] == "Y"),
                ("PA", r["PRIOR_AUTHORIZATION_YN"] == "Y"),
                ("ST", r["STEP_THERAPY_YN"] == "Y"),
            ]
            if flag
        )
        or "None",
        axis=1,
    )
    selected_summary = (
        selected.groupby(["RXCUI", "rxnorm_name"], as_index=False)
        .agg(
            formularies=("FORMULARY_ID", "nunique"),
            ndcs=("NDC", "nunique"),
            median_tier=("TIER_LEVEL_VALUE_NUM", "median"),
            ql_pct=("QUANTITY_LIMIT_YN", lambda s: pct((s == "Y").mean())),
            pa_pct=("PRIOR_AUTHORIZATION_YN", lambda s: pct((s == "Y").mean())),
            st_pct=("STEP_THERAPY_YN", lambda s: pct((s == "Y").mean())),
        )
        .sort_values(["formularies", "rxnorm_name"], ascending=[False, True])
    )
    selected_summary.to_csv(ANALYSIS / "selected_drug_rxcui_summary.csv", index=False)

    for col in [
        "COST_AMT_PREF",
        "COST_AMT_NONPREF",
        "COST_AMT_MAIL_PREF",
        "COST_AMT_MAIL_NONPREF",
        "COST_MAX_AMT_PREF",
        "COST_MAX_AMT_NONPREF",
        "COST_MAX_AMT_MAIL_PREF",
        "COST_MAX_AMT_MAIL_NONPREF",
    ]:
        beneficiary[col + "_NUM"] = to_num(beneficiary[col])

    beneficiary["plan_key"] = beneficiary["CONTRACT_ID"] + "-" + beneficiary["PLAN_ID"] + "-" + beneficiary["SEGMENT_ID"]
    beneficiary = beneficiary.merge(plans[["plan_key", "contract_type"]], on="plan_key", how="left")
    ben_30_initial = beneficiary.loc[(beneficiary["COVERAGE_LEVEL"] == "1") & (beneficiary["DAYS_SUPPLY"] == "1")].copy()
    specialty = ben_30_initial.loc[ben_30_initial["TIER_SPECIALTY_YN"] == "Y"].copy()
    specialty_summary = []
    for label, frame in [("All plans", specialty)] + list(specialty.groupby("contract_type")):
        specialty_summary.append(
            {
                "segment": label,
                "plan_tier_rows": int(frame.shape[0]),
                "plans_with_specialty_tier": int(frame["plan_key"].nunique()),
                "deductible_applies_pct": pct((frame["DED_APPLIES_YN"] == "Y").mean()),
                "coinsurance_pref_pct": pct((frame["COST_TYPE_PREF"] == "2").mean()),
                "median_pref_coinsurance_if_coinsurance": round(float(frame.loc[frame["COST_TYPE_PREF"] == "2", "COST_AMT_PREF_NUM"].median() * 100), 1),
                "median_nonpref_coinsurance_if_coinsurance": round(float(frame.loc[frame["COST_TYPE_NONPREF"] == "2", "COST_AMT_NONPREF_NUM"].median() * 100), 1),
            }
        )
    pd.DataFrame(specialty_summary).to_csv(ANALYSIS / "specialty_tier_summary.csv", index=False)

    for col in insulin.columns:
        if col.startswith("copay_") or col.startswith("coin_"):
            insulin[col + "_NUM"] = to_num(insulin[col])
    insulin["plan_key"] = insulin["CONTRACT_ID"] + "-" + insulin["PLAN_ID"] + "-" + insulin["SEGMENT_ID"]
    insulin = insulin.merge(plans[["plan_key", "contract_type"]], on="plan_key", how="left")
    insulin_30 = insulin.loc[insulin["DAYS_SUPPLY"] == "1"].copy()
    insulin_summary_rows = []
    for label, frame in [("All plans", insulin_30)] + list(insulin_30.groupby("contract_type")):
        insulin_summary_rows.append(
            {
                "segment": label,
                "plan_tier_rows": int(frame.shape[0]),
                "plans_with_insulin_rows": int(frame["plan_key"].nunique()),
                "pref_retail_copay_nonmissing_pct": pct(frame["copay_amt_pref_insln_NUM"].notna().mean()),
                "pref_retail_copay_median": round(float(frame["copay_amt_pref_insln_NUM"].median()), 2),
                "pref_retail_copay_le_35_pct": pct((frame["copay_amt_pref_insln_NUM"].dropna() <= 35).mean()),
                "pref_retail_coin_nonmissing_pct": pct(frame["coin_amt_pref_insln_NUM"].notna().mean()),
                "pref_retail_coin_median_pct": round(float(frame["coin_amt_pref_insln_NUM"].median() * 100), 1),
                "nonpref_retail_copay_median": round(float(frame["copay_amt_nonpref_insln_NUM"].median()), 2),
                "nonpref_retail_coin_median_pct": round(float(frame["coin_amt_nonpref_insln_NUM"].median() * 100), 1),
            }
        )
    pd.DataFrame(insulin_summary_rows).to_csv(ANALYSIS / "insulin_summary.csv", index=False)

    excluded["plan_base"] = excluded["CONTRACT_ID"] + "-" + excluded["PLAN_ID"]
    excluded_summary = {
        "excluded_rows": int(excluded.shape[0]),
        "plans_with_excluded_benefit_contract_plan": int(excluded["plan_base"].nunique()),
        "rxcui_count": int(excluded["RXCUI"].nunique()),
        "quantity_limit_pct": pct((excluded["QUANTITY_LIMIT_YN"] == "1").mean()),
        "prior_auth_pct": pct((excluded["PRIOR_AUTH_YN"] == "Y").mean()),
        "step_therapy_pct": pct((excluded["STEP_THERAPY_YN"] == "Y").mean()),
        "capped_benefit_pct": pct((excluded["CAPPED_BENEFIT_YN"] == "Y").mean()),
    }
    (ANALYSIS / "excluded_drugs_summary.json").write_text(json.dumps(excluded_summary, indent=2))

    ibc_names = rxnorm_names(sorted(ibc["RXCUI"].unique().tolist()))
    ibc["rxnorm_name"] = ibc["RXCUI"].map(ibc_names)
    ibc_summary = (
        ibc.assign(plan_base=ibc["CONTRACT_ID"] + "-" + ibc["PLAN_ID"])
        .groupby(["RXCUI", "rxnorm_name", "DISEASE"], as_index=False)
        .agg(plans=("plan_base", "nunique"))
        .sort_values("plans", ascending=False)
    )
    ibc_summary.to_csv(ANALYSIS / "indication_based_coverage_summary.csv", index=False)

    pharmacy_profile = None
    if os.environ.get("RUN_PHARMACY_PROFILE") == "1":
        pharmacy_profile = profile_pharmacy_network(plans)

    key_metrics = {
        "source_release": "Monthly Prescription Drug Plan Formulary and Pharmacy Network Information : 2026-04-22",
        "contract_year_zip": "2026_20260415.zip",
        "puf_month": "2026-04",
        "outer_zip_sha256": "b9d7c523f9b92c67a39e5eccf7e1609a5a1ed11a7fe6f39af4e05fd568a4f223",
        "row_counts": {name: int(read_pipe(path).shape[0]) for name, path in FILES.items()},
        "unique_plans": int(plans.shape[0]),
        "unique_plans_by_type": plans["contract_type"].value_counts().to_dict(),
        "service_area_rows": int(plan.shape[0]),
        "unique_formularies": int(basic["FORMULARY_ID"].nunique()),
        "unique_basic_ndcs": int(basic["NDC"].nunique()),
        "unique_basic_rxcuis": int(basic["RXCUI"].nunique()),
        "plan_summary": pd.read_csv(ANALYSIS / "plan_summary.csv").to_dict(orient="records"),
        "formulary_plan_summary": pd.read_csv(ANALYSIS / "formulary_plan_summary.csv").to_dict(orient="records"),
        "specialty_tier_summary": pd.read_csv(ANALYSIS / "specialty_tier_summary.csv").to_dict(orient="records"),
        "insulin_summary": pd.read_csv(ANALYSIS / "insulin_summary.csv").to_dict(orient="records"),
        "local_ma_pd_county_availability": summarize_numeric(local_county_availability["local_ma_pd_plans"]),
        "pdp_region_median_premium": summarize_numeric(pdp_region_summary["median_premium"]),
        "pdp_region_plan_count": summarize_numeric(pdp_region_summary["plans"]),
        "excluded_drugs_summary": excluded_summary,
        "ibc_rows": int(ibc.shape[0]),
        "ibc_plan_pairs": int((ibc["CONTRACT_ID"] + "-" + ibc["PLAN_ID"]).nunique()),
        "pharmacy_profile": pharmacy_profile,
    }
    (ANALYSIS / "key_metrics.json").write_text(json.dumps(key_metrics, indent=2))

    top_tables = {
        "lowest_local_ma_pd_counties": local_county_availability.sort_values(["local_ma_pd_plans", "STATE", "COUNTY_CODE"]).head(20).to_dict(orient="records"),
        "highest_local_ma_pd_counties": local_county_availability.sort_values(["local_ma_pd_plans", "STATE", "COUNTY_CODE"], ascending=[False, True, True]).head(20).to_dict(orient="records"),
        "highest_pdp_premium_regions": pdp_region_summary.head(10).to_dict(orient="records"),
        "lowest_pdp_premium_regions": pdp_region_summary.sort_values("median_premium").head(10).to_dict(orient="records"),
        "selected_drugs": selected_summary.to_dict(orient="records"),
        "ibc_top": ibc_summary.head(20).to_dict(orient="records"),
    }
    (ANALYSIS / "top_tables.json").write_text(json.dumps(top_tables, indent=2))


if __name__ == "__main__":
    main()
