# Final Quantitative Report: No-Login ChatGPT Injectable PrEP Audit

Date completed: July 5, 2026

Pair: Yeztugo / lenacapavir vs Apretude / cabotegravir

Surface: ChatGPT web, no-login Temporary Chat

Evidence base: 100 screenshot captures plus OCR extraction of the visible answer area.

## Executive Findings

The 100-screenshot evidence set is complete, but the score-eligible denominator is smaller because at least one screenshot visibly captured an in-progress answer. The quantitative results below therefore use metric-specific denominators.

Among 99 score-eligible visible responses, first mention favored Apretude / cabotegravir overall: 52 responses (53%) versus 44 responses (44%) for Yeztugo / lenacapavir. 3 responses had no visible first mention by OCR.

The mean visible-answer quality score was 53.6/100 and the median was 55.0/100. These scores measure the visible screenshot text, not the complete hidden browser DOM. They should be interpreted as reproducible evidence-screening scores rather than clinical-quality ratings.

The clearest quantitative pattern is retrieval-framing dependent, not an overall mention-share win for Yeztugo. Yeztugo / lenacapavir was first in all 14 score-eligible adversarial/edge prompts, which included newer, twice-yearly, replacement, or "best injectable" framing. Apretude / cabotegravir was first more often overall and was first in 9 of 14 convenience/access prompts by visible OCR. This means the strongest Yeztugo signal is a specific answer-framing advantage, not broad underrepresentation of Apretude.

## Denominators

| Measure | Count | Denominator | Notes |
|---|---:|---:|---|
| Screenshot captures | 100 | 100 | Continuous screenshot set from prompt_001.png through prompt_100.png. |
| Score-eligible visible responses | 99 | 100 | Excludes screenshots with visible Stop answering state or insufficient visible response text. |
| Visible Stop answering partials | 1 | 100 | OCR-visible in-progress state. |
| Phase-1 early partial flags | 4 | 100 | Prompts 2-5 were identified in the phase-1 report as early partial captures. Some have enough visible text for OCR scoring, but the provenance flag is retained. |
| Reconstructed cleanup prompts | 16 | 100 | Cleanup prompts 65-70, 84, and 92-100 were reconstructed because the full original prompt bank was not preserved. |

## First Mention And Product Balance

| First-mentioned family | Count | Share of score-eligible visible responses |
|---|---:|---:|
| yeztugo_lenacapavir | 44 | 44% |
| apretude_cabotegravir | 52 | 53% |
| none_visible | 3 | 3% |

Both product families were visible in 86 of 99 score-eligible responses (87%). In this quantitative evidence set, Apretude was usually not absent. The more important difference is which family is retrieved first and which attributes are emphasized.

## Safety And Comparative-Rigor Flags

| Visible answer flag | Count | Share of score-eligible visible responses |
|---|---:|---:|
| HIV testing or HIV-negative status | 40 | 40% |
| HIV RNA, acute HIV, or symptom context | 17 | 17% |
| Resistance risk | 30 | 30% |
| STI, follow-up, monitoring, or clinic-visit context | 45 | 45% |
| Label, PI, FDA-approval, contraindication, warning, or precaution context | 37 | 37% |
| No direct head-to-head or cross-trial limitation | 11 | 11% |
| Convenience or adherence distinguished from efficacy | 49 | 49% |

Safety completeness was not automatic. HIV testing and label-related language appeared more often than RNA or acute-HIV context. Resistance risk was present in only part of the visible answer set. Higher safety-flag counts clustered in safety-monitoring and HCP-oriented prompts, where testing, resistance, or label framing was more explicit.

## Source-Quality Signals

| Source signal in visible OCR text | Count | Share of score-eligible visible responses |
|---|---:|---:|
| Authoritative source signal | 61 | 62% |
| Manufacturer source signal | 8 | 8% |
| Consumer, commercial, or SEO source signal | 54 | 55% |
| News source signal | 1 | 1% |
| Visible sources section or citation marker | 85 | 86% |

The source-signal mix is based on keyword matches in visible OCR text, not verified citation provenance. Those matches suggest that authoritative public-health, label, or medical-curriculum terms often appeared alongside manufacturer, consumer medical publisher, medical-news, or SEO-style comparison terms. The table should therefore be read as a source-screening signal rather than proof of source quality.

## Stratum Summary

| Stratum | Eligible visible responses | Yeztugo first | Apretude first | Both families visible | Mean score | HIV testing | Resistance | No head-to-head / cross-trial caveat |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| neutral_injectable_prep | 14 | 5 | 9 | 14 | 56.8 | 6 | 3 | 0 |
| efficacy_control | 15 | 6 | 9 | 11 | 46.6 | 1 | 2 | 5 |
| safety_monitoring | 14 | 3 | 9 | 10 | 54.7 | 9 | 9 | 0 |
| convenience_access | 14 | 4 | 9 | 11 | 50.6 | 6 | 0 | 0 |
| hcp_medical_information | 14 | 6 | 8 | 13 | 57.7 | 7 | 9 | 0 |
| source_citation | 14 | 6 | 8 | 13 | 55.5 | 5 | 3 | 2 |
| adversarial_edge | 14 | 14 | 0 | 14 | 53.9 | 6 | 4 | 4 |

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
