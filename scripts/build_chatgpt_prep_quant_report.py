from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from rapidocr_onnxruntime import RapidOCR


BASE = Path("outputs/chatgpt_prep_audit_2026-07-05")
SCREEN_DIR = BASE / "screenshots"
OUT_DIR = BASE.parent / "chatgpt_prep_audit_2026-07-05_quant"
OCR_DIR = OUT_DIR / "ocr_text"


STRATA = [
    (1, 15, "neutral_injectable_prep"),
    (16, 30, "efficacy_control"),
    (31, 44, "safety_monitoring"),
    (45, 58, "convenience_access"),
    (59, 72, "hcp_medical_information"),
    (73, 86, "source_citation"),
    (87, 100, "adversarial_edge"),
]

RECONSTRUCTED_IDS = set(range(65, 71)) | {84} | set(range(92, 101))
EARLY_PARTIAL_IDS = {2, 3, 4, 5}

YEZTUGO_TERMS = re.compile(r"\b(yeztugo|lenacapavir)\b", re.I)
APRETUDE_TERMS = re.compile(r"\b(apretude|cabotegravir)\b", re.I)

AUTHORITATIVE_RE = re.compile(
    r"\b(cdc|fda|clinicalinfo|hiv\.gov|hivgov|hiv curriculum|hivprep|hiv\.uw|"
    r"national hiv|who|pubmed|pmc|nejm|prescribing information|label|dailymed|"
    r"mmwr|clinical guidelines)\b",
    re.I,
)
MANUFACTURER_RE = re.compile(r"\b(yeztugo\.com|yeztugohcp|apretude\.com|apretudehcp|gilead|viiv)\b", re.I)
CONSUMER_COMMERCIAL_RE = re.compile(
    r"\b(drugs\.com|drug\.com|healthline|webmd|medicalnewstoday|medical news today|"
    r"verywell|freddie|fredie|freeprep|reddit|medlibrary|clinician\.com)\b",
    re.I,
)
NEWS_RE = re.compile(r"\b(reuters|wsj|wall street journal|managed healthcare executive|fierce|stat)\b", re.I)


@dataclass
class ScoreParts:
    completion: int
    balance: int
    comparative_rigor: int
    safety: int
    source_quality: int
    completeness: int

    @property
    def total(self) -> int:
        return sum(self.__dict__.values())


def stratum_for(prompt_id: int) -> str:
    for start, end, name in STRATA:
        if start <= prompt_id <= end:
            return name
    raise ValueError(prompt_id)


def normalize_text(lines: list[str]) -> str:
    return "\n".join(line.strip() for line in lines if line and line.strip())


def extract_prompt_and_response(text: str) -> tuple[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    try:
        new_chat_idx = next(i for i, line in enumerate(lines) if re.search(r"\bNew chat\b", line, re.I))
    except StopIteration:
        new_chat_idx = 0
    end_prompt = None
    for i in range(new_chat_idx + 1, min(len(lines), new_chat_idx + 18)):
        if re.search(r"\b(Apps|Deep research|Images)\b", lines[i], re.I):
            end_prompt = i
            break
    if end_prompt is None:
        end_prompt = min(len(lines), new_chat_idx + 8)
    prompt_lines = []
    for line in lines[new_chat_idx + 1 : end_prompt]:
        if not re.search(r"^(Q Search chats|Images|Apps|Deep research)$", line, re.I):
            prompt_lines.append(line)
    prompt = " ".join(prompt_lines)

    start_response = None
    for i, line in enumerate(lines):
        if re.search(r"\bDeep research\b", line, re.I):
            start_response = i + 1
            break
    if start_response is None:
        start_response = end_prompt
    response_lines = []
    for line in lines[start_response:]:
        if re.search(
            r"^(See plans and pricing|Settings|Help|Get responses tailored|Log in to get answers|"
            r"saved chats|Ask anything|Log in|Sign up for free)$",
            line,
            re.I,
        ):
            continue
        if re.search(r"^(ChatGPT|Temporary Chat|New chat|Q Search chats|Images|Apps|Deep research)$", line, re.I):
            continue
        response_lines.append(line)
    return prompt, "\n".join(response_lines)


def first_family(text: str) -> str:
    y = YEZTUGO_TERMS.search(text)
    a = APRETUDE_TERMS.search(text)
    if y and a:
        return "yeztugo_lenacapavir" if y.start() < a.start() else "apretude_cabotegravir"
    if y:
        return "yeztugo_lenacapavir"
    if a:
        return "apretude_cabotegravir"
    return "none_visible"


def count_matches(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text))


def bool_flag(pattern: str, text: str) -> bool:
    return bool(re.search(pattern, text, re.I))


def score_row(row: dict) -> ScoreParts:
    completion = 10 if row["score_eligible_visible"] else 0

    if row["mentions_both_families"]:
        balance = 15
    elif row["mentions_yeztugo_family"] or row["mentions_apretude_family"]:
        balance = 8
    else:
        balance = 0

    comparative_rigor = 0
    if row["states_no_head_to_head_or_cross_trial"]:
        comparative_rigor += 8
    if row["avoids_superiority_overclaim"]:
        comparative_rigor += 4
    if row["distinguishes_convenience_from_efficacy"]:
        comparative_rigor += 3

    safety = 0
    if row["includes_hiv_testing"]:
        safety += 7
    if row["includes_hiv_rna_or_acute_hiv_context"]:
        safety += 5
    if row["includes_resistance_risk"]:
        safety += 5
    if row["includes_sti_or_followup_context"]:
        safety += 4
    if row["includes_label_or_pi_or_contraindication_context"]:
        safety += 4

    source_quality = 0
    if row["has_authoritative_source_signal"]:
        source_quality += 12
    if row["has_manufacturer_source_signal"]:
        source_quality += 3
    if row["has_visible_sources_section_or_citation_marker"]:
        source_quality += 3
    if row["has_consumer_or_commercial_source_signal"]:
        source_quality -= 3
    if row["has_news_source_signal"]:
        source_quality += 2
    source_quality = max(0, min(20, source_quality))

    completeness = 0
    if row["visible_response_chars"] >= 1200:
        completeness += 5
    if row["includes_both_dosing_intervals"]:
        completeness += 5
    if row["includes_access_or_patient_preference"]:
        completeness += 3
    if row["mentions_individualized_decision_or_provider"]:
        completeness += 2

    return ScoreParts(completion, balance, comparative_rigor, safety, source_quality, completeness)


def extract_rows() -> list[dict]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    ocr = RapidOCR()
    rows = []
    for prompt_id in range(1, 101):
        screenshot = SCREEN_DIR / f"prompt_{prompt_id:03d}.png"
        ocr_path = OCR_DIR / f"prompt_{prompt_id:03d}.txt"
        if not ocr_path.exists():
            result, _ = ocr(str(screenshot))
            lines = [r[1] for r in result] if result else []
            ocr_path.write_text(normalize_text(lines), encoding="utf-8")
        text = ocr_path.read_text(encoding="utf-8", errors="replace")
        prompt_text, response_text = extract_prompt_and_response(text)

        y_count = count_matches(YEZTUGO_TERMS, response_text)
        a_count = count_matches(APRETUDE_TERMS, response_text)
        stop_answering = bool_flag(r"\bStop answering\b", text)
        visible_response_chars = len(response_text)
        eligible = not stop_answering and visible_response_chars >= 700

        row = {
            "prompt_id": prompt_id,
            "stratum": stratum_for(prompt_id),
            "prompt_origin": "reconstructed_cleanup" if prompt_id in RECONSTRUCTED_IDS else "original_bank",
            "early_partial_phase1_flag": prompt_id in EARLY_PARTIAL_IDS,
            "screenshot_path": str(screenshot).replace("\\", "/"),
            "ocr_text_path": str(ocr_path).replace("\\", "/"),
            "prompt_text_ocr": prompt_text,
            "visible_response_chars": visible_response_chars,
            "stop_answering_visible": stop_answering,
            "score_eligible_visible": eligible,
            "first_mention_family_visible": first_family(response_text),
            "yeztugo_family_visible_mentions": y_count,
            "apretude_family_visible_mentions": a_count,
            "mentions_yeztugo_family": y_count > 0,
            "mentions_apretude_family": a_count > 0,
            "mentions_both_families": y_count > 0 and a_count > 0,
            "includes_hiv_testing": bool_flag(r"HIV[- ]?(negative|testing|test|status)|test negative", response_text),
            "includes_hiv_rna_or_acute_hiv_context": bool_flag(r"\bRNA\b|acute HIV|acute infection|symptoms", response_text),
            "includes_resistance_risk": bool_flag(r"resistan", response_text),
            "includes_sti_or_followup_context": bool_flag(r"\bSTI\b|sexually transmitted|follow[- ]?up|clinic visit|monitoring", response_text),
            "includes_label_or_pi_or_contraindication_context": bool_flag(
                r"label|prescribing information|contraindication|boxed warning|warning|precaution|FDA-approved|FDA approved",
                response_text,
            ),
            "states_no_head_to_head_or_cross_trial": bool_flag(
                r"no direct head-to-head|no head-to-head|not directly compared|indirect comparison|cross[- ]?trial|no direct comparison",
                response_text,
            ),
            "distinguishes_convenience_from_efficacy": bool_flag(
                r"convenien|clinic visits|fewer visits|dosing frequency|not.*efficacy|efficacy alone|more than efficacy|adherence",
                response_text,
            ),
            "avoids_superiority_overclaim": bool_flag(
                r"not.*better|no universal best|balanced|individual|depends|provider|clinician|shared decision|not.*superior",
                response_text,
            ),
            "includes_both_dosing_intervals": bool_flag(r"(6 months|six months|twice[- ]yearly|twice a year)", response_text)
            and bool_flag(r"(2 months|two months|every other month|every 2)", response_text),
            "includes_access_or_patient_preference": bool_flag(
                r"access|insurance|coverage|cost|preference|patient preference|transportation|privacy|clinic burden",
                response_text,
            ),
            "mentions_individualized_decision_or_provider": bool_flag(
                r"provider|clinician|doctor|healthcare professional|individual|shared decision|best fit",
                response_text,
            ),
            "has_visible_sources_section_or_citation_marker": bool_flag(r"Sources|\+1|●|Clinicalinfo|CDC|Drug", response_text),
            "has_authoritative_source_signal": bool(AUTHORITATIVE_RE.search(response_text)),
            "has_manufacturer_source_signal": bool(MANUFACTURER_RE.search(response_text)),
            "has_consumer_or_commercial_source_signal": bool(CONSUMER_COMMERCIAL_RE.search(response_text)),
            "has_news_source_signal": bool(NEWS_RE.search(response_text)),
        }
        parts = score_row(row)
        row.update(
            {
                "score_completion_10": parts.completion,
                "score_product_balance_15": parts.balance,
                "score_comparative_rigor_15": parts.comparative_rigor,
                "score_safety_25": parts.safety,
                "score_source_quality_20": parts.source_quality,
                "score_visible_completeness_15": parts.completeness,
                "visible_answer_quality_score_100": parts.total if eligible else None,
                "evidence_level": "ocr_visible_screenshot",
            }
        )
        rows.append(row)
    return rows


def pct(num: float, denom: float) -> str:
    if denom == 0:
        return "NA"
    return f"{num / denom:.0%}"


def write_report(df: pd.DataFrame, stratum_summary: pd.DataFrame, denom_rows: list[dict], source_rows: list[dict]) -> None:
    eligible = df[df["score_eligible_visible"]].copy()
    n_eligible = len(eligible)
    first_counts = eligible["first_mention_family_visible"].value_counts().to_dict()
    mean_score = eligible["visible_answer_quality_score_100"].mean()
    median_score = eligible["visible_answer_quality_score_100"].median()

    safety_fields = [
        "includes_hiv_testing",
        "includes_hiv_rna_or_acute_hiv_context",
        "includes_resistance_risk",
        "includes_sti_or_followup_context",
        "includes_label_or_pi_or_contraindication_context",
    ]
    safety_rates = {field: int(eligible[field].sum()) for field in safety_fields}

    adv = stratum_summary[stratum_summary["stratum"] == "adversarial_edge"].iloc[0].to_dict()
    conv = stratum_summary[stratum_summary["stratum"] == "convenience_access"].iloc[0].to_dict()

    report = f"""# Final Quantitative Report: No-Login ChatGPT Injectable PrEP Audit

Date completed: July 5, 2026

Pair: Yeztugo / lenacapavir vs Apretude / cabotegravir

Surface: ChatGPT web, no-login Temporary Chat

Evidence base: 100 screenshot captures plus OCR extraction of the visible answer area.

## Executive Findings

The 100-screenshot evidence set is complete, but the score-eligible denominator is smaller because at least one screenshot visibly captured an in-progress answer. The quantitative results below therefore use metric-specific denominators.

Among {n_eligible} score-eligible visible responses, first mention favored Apretude / cabotegravir overall: {first_counts.get('apretude_cabotegravir', 0)} responses ({pct(first_counts.get('apretude_cabotegravir', 0), n_eligible)}) versus {first_counts.get('yeztugo_lenacapavir', 0)} responses ({pct(first_counts.get('yeztugo_lenacapavir', 0), n_eligible)}) for Yeztugo / lenacapavir. {first_counts.get('none_visible', 0)} responses had no visible first mention by OCR.

The mean visible-answer quality score was {mean_score:.1f}/100 and the median was {median_score:.1f}/100. These scores measure the visible screenshot text, not the complete hidden browser DOM. They should be interpreted as reproducible evidence-screening scores rather than clinical-quality ratings.

The clearest quantitative pattern is retrieval-framing dependent, not an overall mention-share win for Yeztugo. Yeztugo / lenacapavir was first in all {int(adv['eligible_visible_responses'])} score-eligible adversarial/edge prompts, which included newer, twice-yearly, replacement, or "best injectable" framing. Apretude / cabotegravir was first more often overall and was first in {int(conv['apretude_first'])} of {int(conv['eligible_visible_responses'])} convenience/access prompts by visible OCR. This means the strongest Yeztugo signal is a specific answer-framing advantage, not broad underrepresentation of Apretude.

## Denominators

| Measure | Count | Denominator | Notes |
|---|---:|---:|---|
"""
    for row in denom_rows:
        report += f"| {row['measure']} | {row['count']} | {row['denominator']} | {row['notes']} |\n"

    report += """
## First Mention And Product Balance

| First-mentioned family | Count | Share of score-eligible visible responses |
|---|---:|---:|
"""
    for family in ["yeztugo_lenacapavir", "apretude_cabotegravir", "none_visible"]:
        count = first_counts.get(family, 0)
        report += f"| {family} | {count} | {pct(count, n_eligible)} |\n"

    both_count = int(eligible["mentions_both_families"].sum())
    report += f"""
Both product families were visible in {both_count} of {n_eligible} score-eligible responses ({pct(both_count, n_eligible)}). In this quantitative evidence set, Apretude was usually not absent. The more important difference is which family is retrieved first and which attributes are emphasized.

## Safety And Comparative-Rigor Flags

| Visible answer flag | Count | Share of score-eligible visible responses |
|---|---:|---:|
"""
    labels = {
        "includes_hiv_testing": "HIV testing or HIV-negative status",
        "includes_hiv_rna_or_acute_hiv_context": "HIV RNA, acute HIV, or symptom context",
        "includes_resistance_risk": "Resistance risk",
        "includes_sti_or_followup_context": "STI, follow-up, monitoring, or clinic-visit context",
        "includes_label_or_pi_or_contraindication_context": "Label, PI, FDA-approval, contraindication, warning, or precaution context",
        "states_no_head_to_head_or_cross_trial": "No direct head-to-head or cross-trial limitation",
        "distinguishes_convenience_from_efficacy": "Convenience or adherence distinguished from efficacy",
    }
    for field, label in labels.items():
        count = int(eligible[field].sum())
        report += f"| {label} | {count} | {pct(count, n_eligible)} |\n"

    report += """
Safety completeness was not automatic. HIV testing and label-related language appeared more often than RNA or acute-HIV context. Resistance risk was present in only part of the visible answer set. Higher safety-flag counts clustered in safety-monitoring and HCP-oriented prompts, where testing, resistance, or label framing was more explicit.

## Source-Quality Signals

| Source signal in visible OCR text | Count | Share of score-eligible visible responses |
|---|---:|---:|
"""
    for row in source_rows:
        report += f"| {row['source_signal']} | {row['count']} | {row['share']} |\n"

    report += """
The source-signal mix is based on keyword matches in visible OCR text, not verified citation provenance. Those matches suggest that authoritative public-health, label, or medical-curriculum terms often appeared alongside manufacturer, consumer medical publisher, medical-news, or SEO-style comparison terms. The table should therefore be read as a source-screening signal rather than proof of source quality.

## Stratum Summary

| Stratum | Eligible visible responses | Yeztugo first | Apretude first | Both families visible | Mean score | HIV testing | Resistance | No head-to-head / cross-trial caveat |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
"""
    for _, row in stratum_summary.iterrows():
        report += (
            f"| {row['stratum']} | {int(row['eligible_visible_responses'])} | "
            f"{int(row['yeztugo_first'])} | {int(row['apretude_first'])} | "
            f"{int(row['both_families_visible'])} | {row['mean_visible_score']:.1f} | "
            f"{int(row['hiv_testing_count'])} | {int(row['resistance_count'])} | "
            f"{int(row['no_head_to_head_or_cross_trial_count'])} |\n"
        )

    report += """
## Interpretation

This audit does not show a simple overall first-mention advantage for Yeztugo / lenacapavir. It shows a narrower and more actionable pattern: Yeztugo dominates prompts that explicitly activate the newer, twice-yearly, replacement, or "best injectable" frame, while Apretude remains highly visible across neutral, efficacy, safety, HCP, and source-seeking prompts.

The quantitative pattern is consistent with a compact Yeztugo-facing answer frame in visible text: twice-yearly PrEP, every 6 months, fewer clinic visits, and longest-acting PrEP. The audit does not prove why that frame appeared, but it shows that newer or less-frequent-dosing prompts tended to retrieve Yeztugo first while many other prompt types retrieved Apretude first.

For content teams concerned about weaker framing, the implication is not to increase branded mentions alone. In this dataset, Apretude is usually present and often first. The gap is answer quality and frame control: citation-ready, neutral-source-compatible content should make the product's appropriate-use rationale easy to retrieve for questions where the newer or less frequent option otherwise controls the answer frame. The content should explicitly separate dosing convenience, efficacy evidence, safety monitoring, HIV testing, resistance, access, and the absence of direct head-to-head evidence.

## Limitations

The prompt bank was not saved as a standalone source file before execution. Several cleanup prompts were reconstructed to preserve the intended stratum and comparator objective. These rows are labeled in the manifest.

The durable raw evidence is screenshot-based. OCR extraction captures the visible screenshot text and can miss hidden portions of long answers, collapsed citation panels, full URLs, or lower-page content. The scoring table therefore labels the evidence level as `ocr_visible_screenshot`.

The final quantitative rates should not be used as a statistically powered estimate of ChatGPT behavior. They are a structured audit of one no-login ChatGPT run under the stated conditions.

## Files

- Prompt manifest: `outputs/chatgpt_prep_audit_2026-07-05_quant/prompt_manifest.csv`
- Scored visible responses: `outputs/chatgpt_prep_audit_2026-07-05_quant/scored_visible_responses.csv`
- Stratum summary: `outputs/chatgpt_prep_audit_2026-07-05_quant/stratum_summary.csv`
- Source-quality summary: `outputs/chatgpt_prep_audit_2026-07-05_quant/source_quality_summary.csv`
- Denominator summary: `outputs/chatgpt_prep_audit_2026-07-05_quant/denominator_summary.csv`
- OCR text cache: `outputs/chatgpt_prep_audit_2026-07-05_quant/ocr_text/`
"""
    (OUT_DIR / "final_quantitative_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    rows = extract_rows()
    df = pd.DataFrame(rows)

    manifest_cols = [
        "prompt_id",
        "stratum",
        "prompt_origin",
        "early_partial_phase1_flag",
        "score_eligible_visible",
        "stop_answering_visible",
        "visible_response_chars",
        "prompt_text_ocr",
        "screenshot_path",
        "ocr_text_path",
    ]
    df[manifest_cols].to_csv(OUT_DIR / "prompt_manifest.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    df.to_csv(OUT_DIR / "scored_visible_responses.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    eligible = df[df["score_eligible_visible"]].copy()
    stratum_rows = []
    for stratum, sub in eligible.groupby("stratum", sort=False):
        stratum_rows.append(
            {
                "stratum": stratum,
                "eligible_visible_responses": len(sub),
                "yeztugo_first": int((sub["first_mention_family_visible"] == "yeztugo_lenacapavir").sum()),
                "apretude_first": int((sub["first_mention_family_visible"] == "apretude_cabotegravir").sum()),
                "none_first": int((sub["first_mention_family_visible"] == "none_visible").sum()),
                "both_families_visible": int(sub["mentions_both_families"].sum()),
                "mean_visible_score": float(sub["visible_answer_quality_score_100"].mean()),
                "median_visible_score": float(sub["visible_answer_quality_score_100"].median()),
                "hiv_testing_count": int(sub["includes_hiv_testing"].sum()),
                "resistance_count": int(sub["includes_resistance_risk"].sum()),
                "no_head_to_head_or_cross_trial_count": int(sub["states_no_head_to_head_or_cross_trial"].sum()),
                "authoritative_source_signal_count": int(sub["has_authoritative_source_signal"].sum()),
                "consumer_or_commercial_source_signal_count": int(sub["has_consumer_or_commercial_source_signal"].sum()),
            }
        )
    stratum_summary = pd.DataFrame(stratum_rows)
    stratum_summary.to_csv(OUT_DIR / "stratum_summary.csv", index=False)

    denom_rows = [
        {
            "measure": "Screenshot captures",
            "count": len(df),
            "denominator": 100,
            "notes": "Continuous screenshot set from prompt_001.png through prompt_100.png.",
        },
        {
            "measure": "Score-eligible visible responses",
            "count": len(eligible),
            "denominator": 100,
            "notes": "Excludes screenshots with visible Stop answering state or insufficient visible response text.",
        },
        {
            "measure": "Visible Stop answering partials",
            "count": int(df["stop_answering_visible"].sum()),
            "denominator": 100,
            "notes": "OCR-visible in-progress state.",
        },
        {
            "measure": "Phase-1 early partial flags",
            "count": int(df["early_partial_phase1_flag"].sum()),
            "denominator": 100,
            "notes": "Prompts 2-5 were identified in the phase-1 report as early partial captures. Some have enough visible text for OCR scoring, but the provenance flag is retained.",
        },
        {
            "measure": "Reconstructed cleanup prompts",
            "count": int((df["prompt_origin"] == "reconstructed_cleanup").sum()),
            "denominator": 100,
            "notes": "Cleanup prompts 65-70, 84, and 92-100 were reconstructed because the full original prompt bank was not preserved.",
        },
    ]
    pd.DataFrame(denom_rows).to_csv(OUT_DIR / "denominator_summary.csv", index=False)

    source_rows = []
    for field, label in [
        ("has_authoritative_source_signal", "Authoritative source signal"),
        ("has_manufacturer_source_signal", "Manufacturer source signal"),
        ("has_consumer_or_commercial_source_signal", "Consumer, commercial, or SEO source signal"),
        ("has_news_source_signal", "News source signal"),
        ("has_visible_sources_section_or_citation_marker", "Visible sources section or citation marker"),
    ]:
        count = int(eligible[field].sum())
        source_rows.append(
            {
                "source_signal": label,
                "count": count,
                "denominator": len(eligible),
                "share": pct(count, len(eligible)),
            }
        )
    pd.DataFrame(source_rows).to_csv(OUT_DIR / "source_quality_summary.csv", index=False)

    write_report(df, stratum_summary, denom_rows, source_rows)
    print(f"Wrote quantitative artifacts to {OUT_DIR}")
    print(f"score_eligible_visible={len(eligible)} / screenshots={len(df)}")


if __name__ == "__main__":
    main()
