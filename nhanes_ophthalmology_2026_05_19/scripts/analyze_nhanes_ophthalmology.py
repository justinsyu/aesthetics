#!/usr/bin/env python3
"""NHANES 2005-2008 ophthalmology weighted descriptive analysis.

Inputs are public CDC NHANES XPT files. The script downloads any missing raw
files, derives ophthalmology-relevant indicators, and writes weighted estimates.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "output"

NHANES_FILES = [
    ("2005-2006", "DEMO_D", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/DEMO_D.xpt"),
    ("2005-2006", "VIQ_D", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/VIQ_D.xpt"),
    ("2005-2006", "VIX_D", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/VIX_D.xpt"),
    ("2005-2006", "OPXFDT_D", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/OPXFDT_D.xpt"),
    ("2005-2006", "OPXRET_D", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/OPXRET_D.xpt"),
    ("2007-2008", "DEMO_E", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/DEMO_E.xpt"),
    ("2007-2008", "VIQ_E", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/VIQ_E.xpt"),
    ("2007-2008", "VIX_E", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/VIX_E.xpt"),
    ("2007-2008", "OPXFDT_E", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/OPXFDT_E.xpt"),
    ("2007-2008", "OPXRET_E", "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/OPXRET_E.xpt"),
]

DEMO_COLS = ["SEQN", "SDDSRVYR", "RIDAGEYR", "RIAGENDR", "RIDRETH1", "WTMEC2YR", "SDMVPSU", "SDMVSTRA"]
VIQ_COLS = ["SEQN", "VIQ031", "VIQ041", "VIQ051A", "VIQ051C", "VIQ061", "VIQ071", "VIQ090", "VIQ310"]
VIX_COLS = ["SEQN", "VIDRVA", "VIDLVA", "VIDROVA", "VIDLOVA"]
FDT_COLS = ["SEQN", "OPASCST1", "OPDODFDT", "OPDOSFDT"]
RET_COLS = ["SEQN", "OPASCST2", "OPDUARMA", "OPDURL4", "OPDUD125", "OPDUASD", "OPDUGA", "OPDUEXU"]


def download_missing() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for _, stem, url in NHANES_FILES:
        destination = RAW_DIR / f"{stem}.xpt"
        if destination.exists() and destination.stat().st_size > 0:
            continue
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        destination.write_bytes(response.content)


def read_xpt(stem: str, columns: Iterable[str] | None = None) -> pd.DataFrame:
    path = RAW_DIR / f"{stem}.xpt"
    if not path.exists():
        raise FileNotFoundError(f"Missing expected raw file: {path}")
    df = pd.read_sas(path, format="xport", encoding="latin1")
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df.loc[:, numeric_cols] = df.loc[:, numeric_cols].mask(df.loc[:, numeric_cols].abs() < 1e-70, 0)
    if columns is not None:
        missing = sorted(set(columns) - set(df.columns))
        if missing:
            raise ValueError(f"{stem}.xpt is missing expected columns: {missing}")
        df = df.loc[:, list(columns)]
    return df


def load_combined() -> pd.DataFrame:
    pieces = []
    for cycle, suffix in [("2005-2006", "D"), ("2007-2008", "E")]:
        demo = read_xpt(f"DEMO_{suffix}", DEMO_COLS)
        demo["cycle"] = cycle
        viq = read_xpt(f"VIQ_{suffix}", VIQ_COLS)
        vix = read_xpt(f"VIX_{suffix}", VIX_COLS)
        fdt = read_xpt(f"OPXFDT_{suffix}", FDT_COLS)
        ret = read_xpt(f"OPXRET_{suffix}", RET_COLS)

        merged = demo.merge(viq, on="SEQN", how="left", validate="one_to_one")
        merged = merged.merge(vix, on="SEQN", how="left", validate="one_to_one")
        merged = merged.merge(fdt, on="SEQN", how="left", validate="one_to_one")
        merged = merged.merge(ret, on="SEQN", how="left", validate="one_to_one")
        pieces.append(merged)

    combined = pd.concat(pieces, ignore_index=True)
    combined["WTMEC4YR"] = combined["WTMEC2YR"] / 2.0
    combined["sex"] = combined["RIAGENDR"].map({1: "Male", 2: "Female"})
    combined["age_group"] = pd.cut(
        combined["RIDAGEYR"],
        bins=[39, 49, 59, 69, 79, math.inf],
        labels=["40-49", "50-59", "60-69", "70-79", "80+"],
    )
    return combined


def yes_no(series: pd.Series) -> pd.Series:
    return pd.Series(np.where(series.eq(1), 1.0, np.where(series.eq(2), 0.0, np.nan)), index=series.index)


def any_positive(df: pd.DataFrame, columns: list[str], positive_values: set[int], valid_values: set[int]) -> pd.Series:
    values = df[columns]
    has_positive = values.isin(positive_values).any(axis=1)
    has_valid = values.isin(valid_values).any(axis=1)
    return pd.Series(np.where(has_positive, 1.0, np.where(has_valid, 0.0, np.nan)), index=df.index)


def derive_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    presenting = out[["VIDRVA", "VIDLVA"]].replace({666: 666.0})
    out["presenting_better_eye_va"] = presenting.min(axis=1, skipna=True)
    out["presenting_va_impairment_better_eye"] = np.where(
        out["presenting_better_eye_va"].notna(),
        (out["presenting_better_eye_va"] > 40).astype(float),
        np.nan,
    )

    corrected_right = out["VIDROVA"].fillna(out["VIDRVA"]).replace({666: 666.0})
    corrected_left = out["VIDLOVA"].fillna(out["VIDLVA"]).replace({666: 666.0})
    out["corrected_better_eye_va"] = pd.concat([corrected_right, corrected_left], axis=1).min(axis=1, skipna=True)
    out["corrected_va_impairment_better_eye"] = np.where(
        out["corrected_better_eye_va"].notna(),
        (out["corrected_better_eye_va"] > 40).astype(float),
        np.nan,
    )

    out["self_rated_fair_poor_very_poor"] = np.where(
        out["VIQ031"].isin([3, 4, 5]),
        1.0,
        np.where(out["VIQ031"].isin([1, 2]), 0.0, np.nan),
    )
    out["worry_eyesight_some_most_all"] = np.where(
        out["VIQ041"].isin([2, 3, 4]),
        1.0,
        np.where(out["VIQ041"].isin([0, 1]), 0.0, np.nan),
    )
    out["difficulty_reading_newsprint"] = np.where(
        out["VIQ051A"].isin([2, 3, 4, 5]),
        1.0,
        np.where(out["VIQ051A"].eq(1), 0.0, np.nan),
    )
    out["difficulty_steps_dim_light"] = np.where(
        out["VIQ051C"].isin([2, 3, 4, 5]),
        1.0,
        np.where(out["VIQ051C"].eq(1), 0.0, np.nan),
    )
    out["vision_limits_activities"] = np.where(
        out["VIQ061"].isin([1, 2, 3, 4]),
        1.0,
        np.where(out["VIQ061"].eq(0), 0.0, np.nan),
    )
    out["self_report_cataract_surgery"] = yes_no(out["VIQ071"])
    out["self_report_glaucoma"] = yes_no(out["VIQ090"])
    out["self_report_macular_degeneration"] = yes_no(out["VIQ310"])

    out["retinal_exam_complete"] = np.where(
        out["OPASCST2"].eq(1),
        1.0,
        np.where(out["OPASCST2"].isin([2, 3]), 0.0, np.nan),
    )
    out["fdt_exam_complete"] = np.where(
        out["OPASCST1"].eq(1),
        1.0,
        np.where(out["OPASCST1"].isin([2, 3]), 0.0, np.nan),
    )
    out["fdt_visual_field_loss_either_eye"] = any_positive(
        out, ["OPDODFDT", "OPDOSFDT"], positive_values={2}, valid_values={1, 2}
    )
    out["any_retinopathy_worse_eye"] = np.where(
        out["OPDUARMA"].eq(1),
        1.0,
        np.where(out["OPDUARMA"].eq(0), 0.0, np.nan),
    )
    out["large_drusen_worse_eye"] = np.where(
        out["OPDUD125"].eq(1),
        1.0,
        np.where(out["OPDUD125"].eq(0), 0.0, np.nan),
    )
    out["soft_drusen_worse_eye"] = np.where(
        out["OPDUASD"].eq(1),
        1.0,
        np.where(out["OPDUASD"].eq(0), 0.0, np.nan),
    )
    out["late_arm_signs_worse_eye"] = any_positive(out, ["OPDUGA", "OPDUEXU"], positive_values={1}, valid_values={0, 1})

    return out


def survey_mean(df: pd.DataFrame, outcome: str, domain: pd.Series) -> dict[str, float]:
    valid = domain & df[outcome].notna() & df["WTMEC4YR"].notna() & df["SDMVSTRA"].notna() & df["SDMVPSU"].notna()
    if valid.sum() == 0:
        raise ValueError(f"No valid records for {outcome}")

    y = df[outcome].astype(float)
    w = df["WTMEC4YR"].astype(float)
    denom = float((w * valid.astype(float)).sum())
    estimate = float((w * y.fillna(0) * valid.astype(float)).sum() / denom)

    z = w * valid.astype(float) * (y.fillna(0) - estimate) / denom
    z = z.where(valid, 0.0)
    design = pd.DataFrame({"strata": df["SDMVSTRA"], "psu": df["SDMVPSU"], "z": z})
    psu_totals = design.groupby(["strata", "psu"], observed=True)["z"].sum().reset_index()

    variance = 0.0
    for _, strata_frame in psu_totals.groupby("strata", observed=True):
        m = len(strata_frame)
        if m <= 1:
            continue
        centered = strata_frame["z"] - strata_frame["z"].mean()
        variance += float(m / (m - 1) * (centered**2).sum())

    se = math.sqrt(max(variance, 0.0))
    return {
        "unweighted_n": int(valid.sum()),
        "weighted_denominator": denom,
        "estimate": estimate,
        "se": se,
        "ci_low": estimate - 1.96 * se,
        "ci_high": estimate + 1.96 * se,
    }


def add_binary(rows: list[dict], df: pd.DataFrame, variable: str, label: str, min_age: int = 40) -> None:
    domain = df["RIDAGEYR"].ge(min_age)
    stats = survey_mean(df, variable, domain)
    rows.append(
        {
            "section": "Overall",
            "variable": variable,
            "label": label,
            "estimate_type": "percent",
            **stats,
        }
    )


def add_category(rows: list[dict], df: pd.DataFrame, source: str, code: int, label: str, min_age: int = 40) -> None:
    variable = f"{source}_{code}"
    df[variable] = np.where(df[source].eq(code), 1.0, np.where(df[source].isin([1, 2, 3, 4]), 0.0, np.nan))
    stats = survey_mean(df, variable, df["RIDAGEYR"].ge(min_age))
    rows.append(
        {
            "section": "Retinopathy severity",
            "variable": variable,
            "label": label,
            "estimate_type": "percent",
            **stats,
        }
    )


def build_estimates(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []

    add_binary(rows, df, "retinal_exam_complete", "Retinal imaging exam complete among age 40+")
    add_binary(rows, df, "fdt_exam_complete", "FDT visual-field exam complete among age 40+")
    add_binary(rows, df, "presenting_va_impairment_better_eye", "Presenting visual acuity worse than 20/40 in better-seeing eye")
    add_binary(rows, df, "corrected_va_impairment_better_eye", "Objective-refraction visual acuity worse than 20/40 in better-seeing eye")
    add_binary(rows, df, "fdt_visual_field_loss_either_eye", "FDT 2-2-1 visual-field loss in either eye")
    add_binary(rows, df, "any_retinopathy_worse_eye", "Any retinopathy in worse eye")
    add_category(rows, df, "OPDURL4", 1, "No retinopathy")
    add_category(rows, df, "OPDURL4", 2, "Mild non-proliferative retinopathy")
    add_category(rows, df, "OPDURL4", 3, "Moderate/severe non-proliferative retinopathy")
    add_category(rows, df, "OPDURL4", 4, "Proliferative retinopathy")
    add_binary(rows, df, "large_drusen_worse_eye", "Large drusen >=125 microns in worse eye")
    add_binary(rows, df, "soft_drusen_worse_eye", "Any soft drusen in worse eye")
    add_binary(rows, df, "late_arm_signs_worse_eye", "Geographic atrophy or exudative ARM signs in worse eye")
    add_binary(rows, df, "self_rated_fair_poor_very_poor", "Self-rated eyesight fair/poor/very poor")
    add_binary(rows, df, "worry_eyesight_some_most_all", "Worries about eyesight some/most/all of the time")
    add_binary(rows, df, "difficulty_reading_newsprint", "Difficulty reading ordinary newsprint")
    add_binary(rows, df, "difficulty_steps_dim_light", "Difficulty seeing steps/curbs in dim light")
    add_binary(rows, df, "vision_limits_activities", "Vision limits duration of activities at least a little")
    add_binary(rows, df, "self_report_cataract_surgery", "Ever had cataract surgery")
    add_binary(rows, df, "self_report_glaucoma", "Ever told by eye doctor had glaucoma")
    add_binary(rows, df, "self_report_macular_degeneration", "Ever told had age-related macular degeneration")

    estimates = pd.DataFrame(rows)
    percent_mask = estimates["estimate_type"].eq("percent")
    for col in ["estimate", "se", "ci_low", "ci_high"]:
        estimates.loc[percent_mask, col] = estimates.loc[percent_mask, col] * 100
    estimates["ci_low"] = estimates["ci_low"].clip(lower=0, upper=100)
    estimates["ci_high"] = estimates["ci_high"].clip(lower=0, upper=100)
    estimates["weighted_denominator"] = estimates["weighted_denominator"].round(0).astype("int64")
    for col in ["estimate", "se", "ci_low", "ci_high"]:
        estimates[col] = estimates[col].round(2)
    return estimates


def write_summary(estimates: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    estimates.to_csv(OUT_DIR / "weighted_ophthalmology_estimates.csv", index=False)

    selected = estimates.loc[
        estimates["variable"].isin(
            [
                "presenting_va_impairment_better_eye",
                "corrected_va_impairment_better_eye",
                "fdt_visual_field_loss_either_eye",
                "any_retinopathy_worse_eye",
                "large_drusen_worse_eye",
                "late_arm_signs_worse_eye",
                "self_report_glaucoma",
                "self_report_macular_degeneration",
            ]
        ),
        ["label", "unweighted_n", "estimate", "se", "ci_low", "ci_high"],
    ]
    with (OUT_DIR / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write("# NHANES 2005-2008 Ophthalmology Weighted Descriptives\n\n")
        handle.write(
            "Public CDC XPT inputs: DEMO, VIQ, VIX, OPXFDT, and OPXRET for 2005-2006 and 2007-2008. "
            "Analyses use four-year MEC weights (`WTMEC2YR / 2`) and Taylor-linearized strata/PSU standard errors. "
            "Primary domain is participants age 40 years and older with non-missing outcome data.\n\n"
        )
        handle.write(selected.to_markdown(index=False))
        handle.write("\n")


def main() -> None:
    download_missing()
    combined = load_combined()
    analytic = derive_indicators(combined)
    estimates = build_estimates(analytic)
    write_summary(estimates)
    print(f"Wrote {OUT_DIR / 'weighted_ophthalmology_estimates.csv'}")
    print(f"Wrote {OUT_DIR / 'summary.md'}")


if __name__ == "__main__":
    main()
