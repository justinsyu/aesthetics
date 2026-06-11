# Group D Buried P&T/DUR/PDL Insights

Scope: Group D only, using local sources under `pnt-committee-monitoring/decision-rationale/group-d`. Output prioritizes confirmed, source-backed details with pharma relevance.

## Top Findings

1. **Rebate participation can change clinical step burden.** Oklahoma explicitly ties preferred CGRP migraine access to supplemental rebate participation: Ajovy and Emgality require two preventive-therapy failures while rebated, but would revert to three if rebate participation lapses. Trace: Oklahoma, CGRP inhibitors, `text/oklahoma/oklahoma__02142024-dur-packet-pdf__059a7ea6fc.txt`, page 211.

2. **High-cost formulation launches are being dissected at unit-cost level.** Oklahoma's February 2026 packet compares Tanlor 1,000 mg at $2,820 per 30 days with generic methocarbamol tablets under $10 per 30 days, and metaxalone 640 mg at $7,500 per 30 days with metaxalone 800 mg at $60. Trace: Oklahoma, muscle relaxants, `text/oklahoma/oklahoma__02112026-dur-packet-pdf__43dcf97f10.txt`, pages 127-128.

3. **North Dakota is building disease-specific GLP-1 and liver-disease gates that go beyond label checks.** Zepbound for OSA excludes type 2 diabetes and requires PSG-defined moderate/severe OSA, specialist involvement, six months of weight management, and six months of CPAP failure. Rezdiffra for MASH must step through semaglutide, and through semaglutide plus pioglitazone when type 2 diabetes is present. Trace: North Dakota handouts, `text/north-dakota/north-dakota__nd-dur-board-meeting-handouts-2025-pdf__cc07fe9a6a.txt`, pages 23-24.

4. **Preferred does not always mean broad access.** North Carolina added Wegovy as preferred only for cardiovascular risk reduction and explicitly said it still required PA with no auto-approved PAs. Ohio's Wegovy non-obesity pathway similarly excludes type 1 and type 2 diabetes and requires cardiovascular standard-of-care documentation plus renewal weight-loss/PDC thresholds. Traces: NC July 2024 minutes, page 8; Ohio April 2026 draft minutes, pages 21-22.

5. **Manufacturer evidence windows are narrow and procedural.** Oklahoma requires in-person public comment with a 24-hour post-agenda deadline and one speaker per manufacturer. Oregon requests clinical written testimony two weeks before the meeting and says FDA-label recitation is not helpful. Pennsylvania requires testimony registration 14 days before meetings and allows only one manufacturer representative per product. Rhode Island refuses late, hard-copy, or off-topic clinical submissions. Traces are in each state's process documents listed in the JSON.

6. **Final action often sits outside the committee vote.** North Carolina submits panel-approved recommendations to the DHHS Secretary for final approval. New York DURB recommends preferred/non-preferred status to the Commissioner of Health after public comment, clinical review, and cost review. Ohio's Medicaid Director must act within 30 days after recommendations are posted and explain rejected recommendations within a defined timeframe.

7. **Some hidden access barriers are dosage-form or workflow based.** North Dakota's non-solid dosage forms can reject at point of sale for members 10 and older even when no clinical PA applies. New York CDRP drugs can require prescriber-only PA initiation and clinical-call-center documentation, with faxed support requested.

## Traceability Index

| State | Insight | Drug/Class | Type | Source |
|---|---|---|---|---|
| Oklahoma | Public comment is in-person only, capped, one speaker per manufacturer | DUR Board public comment | manufacturer_submission_rule | `text/oklahoma/oklahoma__02112026-dur-agenda-pdf__cea0a811bd.txt`, p.2 |
| Oklahoma | CGRP step burden changes if supplemental rebates lapse | Ajovy, Emgality, CGRP inhibitors | cost_analysis_signal | `text/oklahoma/oklahoma__02142024-dur-packet-pdf__059a7ea6fc.txt`, p.211 |
| Oklahoma | HAE PBPA tiers put new products behind lower-tier failures | Andembry, Dawnzera, Ekterly | step_edit | `text/oklahoma/oklahoma__02112026-dur-packet-pdf__43dcf97f10.txt`, p.119 |
| Oklahoma | Line-extension muscle relaxants face cost scrutiny | Tanlor, metaxalone 640 mg, Zanaflex 8 mg | cost_analysis_signal | `text/oklahoma/oklahoma__02112026-dur-packet-pdf__43dcf97f10.txt`, p.127 |
| North Dakota | Rezdiffra steps through semaglutide, plus pioglitazone with T2D | MASH agents | step_edit | `text/north-dakota/north-dakota__nd-dur-board-meeting-handouts-2025-pdf__cc07fe9a6a.txt`, p.24 |
| North Dakota | Zepbound OSA excludes diabetes and requires CPAP/weight-management failure | Zepbound | access_barrier | `text/north-dakota/north-dakota__nd-dur-board-meeting-handouts-2025-pdf__cc07fe9a6a.txt`, p.23 |
| North Dakota | PBC agents require biopsy, ursodiol failure, alcohol testing, lab renewal | Iqirvo, Livdelzi, Ocaliva | renewal_threshold | `text/north-dakota/north-dakota__nd-dur-board-meeting-handouts-2025-pdf__cc07fe9a6a.txt`, p.39 |
| North Dakota | Non-solid dosage forms reject for members 10+ without dosage-form justification | Non-solid dosage forms | hidden_access_barrier | `text/north-dakota/north-dakota__nd-dur-board-meeting-handouts-2025-pdf__cc07fe9a6a.txt`, p.223 |
| North Carolina | Panel recommendations go to DHHS Secretary after 30-day comment cycle | PDL Review Panel | final_decision_mechanics | `text/north-carolina/north-carolina__download__02fd4d9f1b.txt`, p.1 |
| North Carolina | Wegovy preferred only for MACE, still manual PA | Wegovy | off_label_exclusion | `text/north-carolina/north-carolina__download__0753767b59.txt`, p.8 |
| North Carolina | GLP-1 obesity coverage reinstated off-cycle but split preferred/non-preferred | Wegovy, Zepbound, Saxenda | timing_implementation | `text/north-carolina/north-carolina__download__92bf8029c6.txt`, p.2 |
| Oregon | Outside parties can request voting ad hoc experts 21 days before review | P&T ad hoc experts | final_decision_mechanics | `text/oregon/oregon__p-t-operating-procedures-pdf__8ba0ee8ab4.txt`, p.2 |
| Oregon | Comparative new evidence is favored over label recitation | P&T testimony | manufacturer_submission_rule | `text/oregon/oregon__p-t-operating-procedures-pdf__8ba0ee8ab4.txt`, p.4 |
| Oregon | Interim PA/non-preferred controls can apply before P&T review | New drugs, line extensions, combinations, biosimilars | hidden_access_barrier | `text/oregon/oregon__p-t-operating-procedures-pdf__8ba0ee8ab4.txt`, p.5 |
| South Carolina | Industry must use Single PDL mailbox and avoid direct member contact | Single PDL submissions | manufacturer_submission_rule | `text/south-carolina/south-carolina__ptcommittee-asp__12798742f3.txt`, HTML |
| South Carolina | Wakefulness agents get one-step non-preferred criteria; Uzedy has child PA carveout | Nuvigil, Provigil, Sunosi, Wakix, Uzedy | step_edit | `text/south-carolina/south-carolina__ptminutes-20250806-pdf__5cdbc41d98.txt`, p.3 |
| Rhode Island | Clinical submissions must distinguish products and meet deadline | P&T clinical submissions | manufacturer_submission_rule | `text/rhode-island/rhode-island__pharmacy-therapeutics-committee__ec41d83173.txt`, HTML |
| Rhode Island | Advance manufacturer clinical packets barred; materials capped to one page | P&T public testimony | manufacturer_submission_rule | `text/rhode-island/rhode-island__pandt-bylaws-pdf__31be89323a.txt`, p.4 |
| Ohio | Manufacturer presentations are clinical-only, Friday-confirmed, and written materials due two business days before vote | P&T presentations | manufacturer_submission_rule | `text/ohio/ohio__20230401-pt-bylaws-approved-pdf__9ae4bbc117.txt`, p.4 |
| Ohio | Medicaid Director has 30-day action clock and rejection-explanation duty | P&T final decision process | final_decision_mechanics | `text/ohio/ohio__5164-7510-10-17-2019-pdf__1e0c43ca7e.txt`, p.2 |
| Ohio | Wegovy non-obesity criteria exclude diabetes and require 5% renewal weight loss plus 80% PDC | Wegovy, GLP-1s | renewal_threshold | `text/ohio/ohio__20260408-pt-meeting-minutes-draft-pdf__4264e5b5e5.txt`, p.21 |
| Pennsylvania | Public testimony requires 14-day registration, one manufacturer per product, no Q&A | P&T testimony | manufacturer_submission_rule | `text/pennsylvania/pennsylvania__ptby-laws4-apprvd-by-pt-9-14-21-final-pdf__21618d5e47.txt`, p.4 |
| Pennsylvania | Journavx PA is limited to 14 days and resets only for separate acute pain episodes | Journavx | renewal_threshold | `text/pennsylvania/pennsylvania__2026-01-05-analgesics-acute-pain-agents-pdf__f1d5788d9d.txt`, p.5 |
| New York | DURB recommendations flow through public comment, clinical review, cost review, then Commissioner selection | Preferred Drug Program | final_decision_mechanics | `text/new-york/new-york__pdp-about-asp__28af7bb49a.txt`, HTML |
| New York | CDRP can require prescriber-only PA initiation and clinical-call-center evidence | CDRP drugs | hidden_access_barrier | `text/new-york/new-york__cdrp-about-asp__c544a03674.txt`, HTML |

Full structured records with URL, local path, document ID, page number, confidence, and validation note are in `group-d-insights.json`.
