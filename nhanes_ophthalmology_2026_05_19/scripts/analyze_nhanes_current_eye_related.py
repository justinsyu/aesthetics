#!/usr/bin/env python3
"""NHANES August 2021-August 2023 current eye-related descriptive analysis."""

from __future__ import annotations

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
    return df.loc[:, columns]


def survey_mean(df: pd.DataFrame, outcome: pd.Series, domain: pd.Series, weight: str) -> dict[str, float]:
    valid = domain & outcome.notna() & df[weight].notna() & df["SDMVSTRA"].notna() & df["SDMVPSU"].notna()
    denom = float((df.loc[valid, weight]).sum())
    estimate = float((df.loc[valid, weight] * outcome.loc[valid]).sum() / denom)
    z = pd.Series(0.0, index=df.index)
    z.loc[valid] = df.loc[valid, weight] * (outcome.loc[valid] - estimate) / denom
    psu = pd.DataFrame({"strata": df["SDMVSTRA"], "psu": df["SDMVPSU"], "z": z}).groupby(["strata", "psu"], observed=True)["z"].sum().reset_index()
    var = 0.0
    for _, g in psu.groupby("strata", observed=True):
        m = len(g)
        if m > 1:
            var += float(m / (m - 1) * ((g["z"] - g["z"].mean()) ** 2).sum())
    se = math.sqrt(max(var, 0.0))
    return {
        "unweighted_n": int(valid.sum()),
        "weighted_denominator": int(round(denom, 0)),
        "estimate": round(100 * estimate, 2),
        "se": round(100 * se, 2),
        "ci_low": round(max(0, 100 * (estimate - 1.96 * se)), 2),
        "ci_high": round(min(100, 100 * (estimate + 1.96 * se)), 2),
    }


def wg_difficulty(series: pd.Series, some_or_more: bool) -> pd.Series:
    valid = series.isin([1, 2, 3, 4])
    positives = [2, 3, 4] if some_or_more else [3, 4]
    return series.isin(positives).astype(float).where(valid)


def yes_no(series: pd.Series) -> pd.Series:
    return series.eq(1).astype(float).where(series.isin([1, 2]))


def phq9_moderate(df: pd.DataFrame) -> pd.Series:
    cols = ["DPQ010", "DPQ020", "DPQ030", "DPQ040", "DPQ050", "DPQ060", "DPQ070", "DPQ080", "DPQ090"]
    valid = df[cols].isin([0, 1, 2, 3]).all(axis=1)
    total = df[cols].where(df[cols].isin([0, 1, 2, 3])).sum(axis=1)
    return (total >= 10).astype(float).where(valid)


def main() -> None:
    download_missing()
    demo = read_xpt("DEMO_L", ["SEQN", "RIDAGEYR", "RIAGENDR", "RIDRETH3", "WTINT2YR", "WTMEC2YR", "SDMVSTRA", "SDMVPSU"])
    for stem, columns in {
        "FNQ_L": ["SEQN", "FNQ021", "FNQ410", "FNDADI", "FNDAEDI"],
        "BAQ_L": ["SEQN", "BAQ321B"],
        "DIQ_L": ["SEQN", "DIQ010"],
        "DPQ_L": ["SEQN", "DPQ010", "DPQ020", "DPQ030", "DPQ040", "DPQ050", "DPQ060", "DPQ070", "DPQ080", "DPQ090"],
    }.items():
        demo = demo.merge(read_xpt(stem, columns), on="SEQN", how="left")

    rows = []

    def add(variable: str, label: str, outcome: pd.Series, domain: pd.Series, denominator: str, weight: str, source_type: str) -> None:
        rows.append({
            "dataset": "NHANES August 2021-August 2023",
            "variable": variable,
            "label": label,
            "denominator": denominator,
            "weight": weight,
            "source_type": source_type,
            **survey_mean(demo, outcome, domain, weight),
        })

    adults = demo["RIDAGEYR"].ge(18)
    youth = demo["RIDAGEYR"].between(5, 17)
    age20_69 = demo["RIDAGEYR"].between(20, 69)
    severe_seeing = wg_difficulty(demo["FNQ410"], some_or_more=False)
    phq = phq9_moderate(demo)

    add("adult_seeing_some_or_more", "Difficulty seeing even with glasses or contact lenses: some difficulty or worse", wg_difficulty(demo["FNQ410"], True), adults, "Adults aged 18 years or older", "WTINT2YR", "patient-reported functioning")
    add("adult_seeing_lot_or_cannot", "Difficulty seeing even with glasses or contact lenses: a lot of difficulty or cannot do at all", severe_seeing, adults, "Adults aged 18 years or older", "WTINT2YR", "patient-reported functioning")
    add("youth_seeing_lot_or_cannot", "Difficulty seeing even with glasses or contact lenses: a lot of difficulty or cannot do at all", wg_difficulty(demo["FNQ021"], False), youth, "Children and adolescents aged 5-17 years", "WTINT2YR", "patient-reported functioning")
    add("adult_wg_ss_disability", "Washington Group Short Set disability indicator", yes_no(demo["FNDADI"]), adults, "Adults aged 18 years or older", "WTINT2YR", "patient-reported functioning")
    add("blurred_vision_with_head_movement", "Blurred vision with head movement in the past 12 months", yes_no(demo["BAQ321B"]), age20_69, "Participants aged 20-69 years", "WTINT2YR", "patient-reported symptom")
    add("diagnosed_diabetes", "Doctor ever told participant had diabetes", yes_no(demo["DIQ010"]), adults, "Adults aged 18 years or older", "WTINT2YR", "ophthalmology risk factor")
    add("phq9_moderate_severe_seeing", "PHQ-9 score of 10 or greater among adults with severe seeing difficulty", phq, adults & severe_seeing.eq(1), "Adults with a lot of difficulty seeing or cannot see", "WTMEC2YR", "patient-reported outcome")
    add("phq9_moderate_no_severe_seeing", "PHQ-9 score of 10 or greater among adults without severe seeing difficulty", phq, adults & severe_seeing.eq(0), "Adults without severe seeing difficulty", "WTMEC2YR", "patient-reported outcome")

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "current_eye_related_estimates.csv", index=False)
    print(f"Wrote {OUT / 'current_eye_related_estimates.csv'}")


if __name__ == "__main__":
    main()
