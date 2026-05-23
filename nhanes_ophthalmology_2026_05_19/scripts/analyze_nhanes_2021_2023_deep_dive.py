#!/usr/bin/env python3
"""NHANES August 2021-August 2023 ophthalmology-related deep-dive analysis.

This script intentionally uses only public 2021-August 2023 NHANES files.
It does not estimate ophthalmic disease prevalence because public eye-exam,
retinal-imaging, visual-field, cataract, glaucoma, AMD, or diabetic-retinopathy
variables are not available in this cycle.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "output"

FILES = {
    "DEMO_L": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.xpt",
    "FNQ_L": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/FNQ_L.xpt",
    "BAQ_L": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BAQ_L.xpt",
    "DIQ_L": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DIQ_L.xpt",
    "DPQ_L": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DPQ_L.xpt",
}

DPQ_COLS = ["DPQ010", "DPQ020", "DPQ030", "DPQ040", "DPQ050", "DPQ060", "DPQ070", "DPQ080", "DPQ090"]


def download_missing() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for stem, url in FILES.items():
        path = RAW / f"{stem}.xpt"
        if path.exists() and path.stat().st_size > 0:
            continue
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        path.write_bytes(response.content)


def read_xpt(stem: str, columns: list[str]) -> pd.DataFrame:
    df = pd.read_sas(RAW / f"{stem}.xpt", format="xport", encoding="latin1")
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df.loc[:, numeric_cols] = df.loc[:, numeric_cols].mask(df.loc[:, numeric_cols].abs() < 1e-70, 0)
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{stem}.xpt missing expected columns: {missing}")
    return df.loc[:, columns]


def load_data() -> pd.DataFrame:
    download_missing()
    df = read_xpt("DEMO_L", ["SEQN", "RIDAGEYR", "RIAGENDR", "RIDRETH3", "WTINT2YR", "WTMEC2YR", "SDMVSTRA", "SDMVPSU"])
    for stem, cols in {
        "FNQ_L": ["SEQN", "FNQ021", "FNQ410", "FNDADI", "FNDAEDI", "FNQ510", "FNQ520", "FNQ530", "FNQ540"],
        "BAQ_L": ["SEQN", "BAQ321B"],
        "DIQ_L": ["SEQN", "DIQ010"],
        "DPQ_L": ["SEQN", *DPQ_COLS],
    }.items():
        df = df.merge(read_xpt(stem, cols), on="SEQN", how="left", validate="one_to_one")
    df["sex"] = df["RIAGENDR"].map({1: "Male", 2: "Female"})
    df["race_ethnicity"] = df["RIDRETH3"].map({
        1: "Mexican American",
        2: "Other Hispanic",
        3: "Non-Hispanic White",
        4: "Non-Hispanic Black",
        6: "Non-Hispanic Asian",
        7: "Other or multiracial",
    })
    df["age_group_adult"] = pd.cut(df["RIDAGEYR"], bins=[17, 39, 64, 79, math.inf], labels=["18-39", "40-64", "65-79", "80+"])
    df["age_group_20_69"] = pd.cut(df["RIDAGEYR"], bins=[19, 39, 54, 69], labels=["20-39", "40-54", "55-69"])
    return df


def wg_difficulty(series: pd.Series, threshold: str) -> pd.Series:
    valid = series.isin([1, 2, 3, 4])
    positives = [2, 3, 4] if threshold == "some_or_more" else [3, 4]
    return series.isin(positives).astype(float).where(valid)


def yes_no(series: pd.Series) -> pd.Series:
    return series.eq(1).astype(float).where(series.isin([1, 2]))


def phq9_score(df: pd.DataFrame) -> pd.Series:
    valid = df[DPQ_COLS].isin([0, 1, 2, 3]).all(axis=1)
    total = df[DPQ_COLS].where(df[DPQ_COLS].isin([0, 1, 2, 3])).sum(axis=1)
    return total.where(valid)


def domain_linearized(df: pd.DataFrame, y: pd.Series, domain: pd.Series, weight: str) -> tuple[float, pd.Series, pd.Series]:
    valid = domain.fillna(False) & y.notna() & df[weight].notna() & df["SDMVSTRA"].notna() & df["SDMVPSU"].notna()
    denom = float(df.loc[valid, weight].sum())
    if denom <= 0:
        raise ValueError("No positive survey-weight denominator")
    est = float((df.loc[valid, weight] * y.loc[valid].astype(float)).sum() / denom)
    z = pd.Series(0.0, index=df.index)
    z.loc[valid] = df.loc[valid, weight] * (y.loc[valid].astype(float) - est) / denom
    return est, z, valid


def se_from_linearized(df: pd.DataFrame, z: pd.Series) -> float:
    psu = pd.DataFrame({"strata": df["SDMVSTRA"], "psu": df["SDMVPSU"], "z": z}).groupby(["strata", "psu"], observed=True)["z"].sum().reset_index()
    var = 0.0
    for _, g in psu.groupby("strata", observed=True):
        m = len(g)
        if m > 1:
            var += float(m / (m - 1) * ((g["z"] - g["z"].mean()) ** 2).sum())
    return math.sqrt(max(var, 0.0))


def estimate(df: pd.DataFrame, y: pd.Series, domain: pd.Series, weight: str) -> dict[str, float]:
    est, z, valid = domain_linearized(df, y, domain, weight)
    se = se_from_linearized(df, z)
    weighted_denominator = int(round(df.loc[valid, weight].sum(), 0))
    weighted_n = float((df.loc[valid, weight] * y.loc[valid].astype(float)).sum())
    return {
        "unweighted_n": int(valid.sum()),
        "weighted_denominator": weighted_denominator,
        "weighted_n": int(round(weighted_n, 0)),
        "estimate": round(100 * est, 2),
        "se": round(100 * se, 2),
        "ci_low": round(max(0, 100 * (est - 1.96 * se)), 2),
        "ci_high": round(min(100, 100 * (est + 1.96 * se)), 2),
    }


def contrast(df: pd.DataFrame, y: pd.Series, domain_a: pd.Series, domain_b: pd.Series, weight: str, label_a: str, label_b: str) -> dict[str, float | str]:
    est_a, z_a, valid_a = domain_linearized(df, y, domain_a, weight)
    est_b, z_b, valid_b = domain_linearized(df, y, domain_b, weight)
    diff = est_a - est_b
    se_diff = se_from_linearized(df, z_a - z_b)
    ratio = est_a / est_b if est_b > 0 else np.nan
    return {
        "group_a": label_a,
        "group_b": label_b,
        "estimate_a": round(100 * est_a, 2),
        "estimate_b": round(100 * est_b, 2),
        "absolute_difference": round(100 * diff, 2),
        "diff_ci_low": round(100 * (diff - 1.96 * se_diff), 2),
        "diff_ci_high": round(100 * (diff + 1.96 * se_diff), 2),
        "prevalence_ratio": round(ratio, 2),
        "n_a": int(valid_a.sum()),
        "n_b": int(valid_b.sum()),
    }


def add_overall(rows: list[dict], df: pd.DataFrame, variable: str, label: str, y: pd.Series, domain: pd.Series, denominator: str, weight: str, outcome_family: str) -> None:
    rows.append({
        "analysis": "overall",
        "variable": variable,
        "label": label,
        "level": "Overall",
        "denominator": denominator,
        "weight": weight,
        "outcome_family": outcome_family,
        **estimate(df, y, domain, weight),
    })


def add_strata(rows: list[dict], df: pd.DataFrame, variable: str, label: str, y: pd.Series, domain: pd.Series, stratifier: str, strat_col: str, denominator: str, weight: str, outcome_family: str) -> None:
    for level in df.loc[domain.fillna(False), strat_col].dropna().unique():
        level_domain = domain & df[strat_col].eq(level)
        stats = estimate(df, y, level_domain, weight)
        if stats["unweighted_n"] < 30:
            continue
        rows.append({
            "analysis": f"by {stratifier}",
            "variable": variable,
            "label": label,
            "level": str(level),
            "denominator": denominator,
            "weight": weight,
            "outcome_family": outcome_family,
            **stats,
        })


def main() -> None:
    df = load_data()
    adults = df["RIDAGEYR"].ge(18)
    youth = df["RIDAGEYR"].between(5, 17)
    age20_69 = df["RIDAGEYR"].between(20, 69)

    seeing_some = wg_difficulty(df["FNQ410"], "some_or_more")
    seeing_severe = wg_difficulty(df["FNQ410"], "severe")
    youth_seeing_severe = wg_difficulty(df["FNQ021"], "severe")
    blurred = yes_no(df["BAQ321B"])
    diabetes = yes_no(df["DIQ010"])
    wg_disability = yes_no(df["FNDADI"])
    wg_enhanced = yes_no(df["FNDAEDI"])
    phq_moderate = phq9_score(df).ge(10).astype(float).where(phq9_score(df).notna())
    daily_depressed_lot = (df["FNQ530"].eq(1) & df["FNQ540"].eq(2)).astype(float).where(df["FNQ530"].isin([1, 2, 3, 4, 5]) & df["FNQ540"].isin([1, 2, 3]))
    daily_anxious_lot = (df["FNQ510"].eq(1) & df["FNQ520"].eq(2)).astype(float).where(df["FNQ510"].isin([1, 2, 3, 4, 5]) & df["FNQ520"].isin([1, 2, 3]))

    rows: list[dict] = []
    add_overall(rows, df, "seeing_some_or_more", "Difficulty seeing even with glasses or contact lenses: some difficulty or worse", seeing_some, adults, "Adults aged 18 years or older", "WTINT2YR", "seeing function")
    add_overall(rows, df, "seeing_severe", "Difficulty seeing even with glasses or contact lenses: a lot of difficulty or cannot do at all", seeing_severe, adults, "Adults aged 18 years or older", "WTINT2YR", "seeing function")
    add_overall(rows, df, "youth_seeing_severe", "Youth difficulty seeing even with glasses or contact lenses: a lot of difficulty or cannot do at all", youth_seeing_severe, youth, "Children and adolescents aged 5-17 years", "WTINT2YR", "seeing function")
    add_overall(rows, df, "blurred_vision_head_movement", "Blurred vision with head movement in the past 12 months", blurred, age20_69, "Participants aged 20-69 years", "WTINT2YR", "symptom")
    add_overall(rows, df, "diagnosed_diabetes", "Doctor ever told participant had diabetes", diabetes, adults, "Adults aged 18 years or older", "WTINT2YR", "risk context")
    add_overall(rows, df, "wg_disability", "Washington Group Short Set disability indicator", wg_disability, adults, "Adults aged 18 years or older", "WTINT2YR", "functioning")
    add_overall(rows, df, "wg_enhanced_disability", "Washington Group Short Set Enhanced disability indicator", wg_enhanced, adults, "Adults aged 18 years or older", "WTINT2YR", "functioning")
    add_overall(rows, df, "phq9_moderate", "PHQ-9 score of 10 or greater", phq_moderate, adults, "Adults aged 18 years or older with DPQ data", "WTMEC2YR", "patient-reported outcome")
    add_overall(rows, df, "daily_depressed_lot", "Daily depressed feelings with intensity reported as a lot", daily_depressed_lot, adults, "Adults aged 18 years or older", "WTINT2YR", "patient-reported outcome")
    add_overall(rows, df, "daily_anxious_lot", "Daily worried, nervous, or anxious feelings with intensity reported as a lot", daily_anxious_lot, adults, "Adults aged 18 years or older", "WTINT2YR", "patient-reported outcome")

    for variable, label, y, domain, denom, weight, family in [
        ("seeing_some_or_more", "Adult seeing difficulty: some difficulty or worse", seeing_some, adults, "Adults aged 18 years or older", "WTINT2YR", "seeing function"),
        ("seeing_severe", "Adult seeing difficulty: a lot of difficulty or cannot do at all", seeing_severe, adults, "Adults aged 18 years or older", "WTINT2YR", "seeing function"),
        ("blurred_vision_head_movement", "Blurred vision with head movement in the past 12 months", blurred, age20_69, "Participants aged 20-69 years", "WTINT2YR", "symptom"),
    ]:
        add_strata(rows, df, variable, label, y, domain, "age", "age_group_20_69" if variable == "blurred_vision_head_movement" else "age_group_adult", denom, weight, family)
        add_strata(rows, df, variable, label, y, domain, "sex", "sex", denom, weight, family)
        add_strata(rows, df, variable, label, y, domain, "race_ethnicity", "race_ethnicity", denom, weight, family)

    severe_domain = adults & seeing_severe.eq(1)
    nonsevere_domain = adults & seeing_severe.eq(0)
    contrasts = [
        {
            "contrast": "PHQ-9 >=10 by severe seeing difficulty",
            "outcome": "PHQ-9 score of 10 or greater",
            **contrast(df, phq_moderate, severe_domain, nonsevere_domain, "WTMEC2YR", "Severe seeing difficulty", "No severe seeing difficulty"),
        },
        {
            "contrast": "Diagnosed diabetes by severe seeing difficulty",
            "outcome": "Doctor ever told participant had diabetes",
            **contrast(df, diabetes, severe_domain, nonsevere_domain, "WTINT2YR", "Severe seeing difficulty", "No severe seeing difficulty"),
        },
        {
            "contrast": "Daily depressed feelings by severe seeing difficulty",
            "outcome": "Daily depressed feelings with intensity reported as a lot",
            **contrast(df, daily_depressed_lot, severe_domain, nonsevere_domain, "WTINT2YR", "Severe seeing difficulty", "No severe seeing difficulty"),
        },
        {
            "contrast": "Daily anxious feelings by severe seeing difficulty",
            "outcome": "Daily worried, nervous, or anxious feelings with intensity reported as a lot",
            **contrast(df, daily_anxious_lot, severe_domain, nonsevere_domain, "WTINT2YR", "Severe seeing difficulty", "No severe seeing difficulty"),
        },
        {
            "contrast": "Severe seeing difficulty age gradient",
            "outcome": "Severe seeing difficulty",
            **contrast(df, seeing_severe, adults & df["age_group_adult"].eq("80+"), adults & df["age_group_adult"].eq("18-39"), "WTINT2YR", "Age 80+", "Age 18-39"),
        },
        {
            "contrast": "Severe seeing difficulty by sex",
            "outcome": "Severe seeing difficulty",
            **contrast(df, seeing_severe, adults & df["sex"].eq("Female"), adults & df["sex"].eq("Male"), "WTINT2YR", "Female", "Male"),
        },
        {
            "contrast": "Blurred vision with head movement by sex",
            "outcome": "Blurred vision with head movement",
            **contrast(df, blurred, age20_69 & df["sex"].eq("Female"), age20_69 & df["sex"].eq("Male"), "WTINT2YR", "Female", "Male"),
        },
        {
            "contrast": "Blurred vision with head movement race-ethnicity contrast",
            "outcome": "Blurred vision with head movement",
            **contrast(df, blurred, age20_69 & df["race_ethnicity"].eq("Other Hispanic"), age20_69 & df["race_ethnicity"].eq("Non-Hispanic White"), "WTINT2YR", "Other Hispanic", "Non-Hispanic White"),
        },
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "current_2021_2023_deep_dive_estimates.csv", index=False)
    pd.DataFrame(contrasts).to_csv(OUT / "current_2021_2023_key_contrasts.csv", index=False)
    metadata = {
        "scope": "NHANES August 2021-August 2023 public files only",
        "files": FILES,
        "methods": [
            "Linked records by SEQN",
            "Used WTINT2YR for interview/questionnaire outcomes",
            "Used WTMEC2YR for PHQ-9 estimates because DPQ is an examination-component questionnaire",
            "Estimated weighted proportions with Taylor-linearized standard errors over SDMVSTRA and SDMVPSU",
            "Defined adult severe seeing difficulty as FNQ410 in {3, 4}; some-or-more as FNQ410 in {2, 3, 4}",
            "Defined blurred vision with head movement as BAQ321B = 1 among participants aged 20-69 years",
            "Defined PHQ-9 score >=10 from DPQ010-DPQ090 values 0-3",
        ],
        "limitation": "The public 2021-August 2023 release does not include ophthalmology examination, visual acuity, retinal imaging, visual-field, cataract, glaucoma, AMD, or diabetic-retinopathy outcomes.",
    }
    (OUT / "current_2021_2023_methods_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"Wrote {OUT / 'current_2021_2023_deep_dive_estimates.csv'}")
    print(f"Wrote {OUT / 'current_2021_2023_key_contrasts.csv'}")


if __name__ == "__main__":
    main()
