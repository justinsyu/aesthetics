# Group A Buried P&T/DUR/PDL Insights

Scope: Alabama, Alaska, Arizona, Arkansas, California, Connecticut, Florida, and Georgia materials under `pnt-committee-monitoring/decision-rationale/group-a`. Colorado had no successful source text in the local collection, and Delaware agenda material was lower-value than the validated findings below.

## Top Findings

1. **Cost logic is often structurally separate from public clinical review.** Arkansas is the clearest example: a public Drug Review Committee handles clinical evidence, while a closed Drug Cost Committee reviews proprietary rebate/net-cost data and finalizes preferred-status recommendations. Arizona similarly tells manufacturers which reviewed categories need rebate offers before a P&T meeting.

2. **Manufacturer engagement windows can be earlier and narrower than public comment.** Alaska required manufacturer clinical submissions for its January 16, 2026 meeting by January 2, while general written materials were requested by January 14. Georgia generally waits until a drug has been on the market at least six months, posts drugs/classes about 30 days before the Manufacturers' Forum, and allows a 10-business-day appeal meeting window after quarterly DURB meetings.

3. **Implementation artifacts carry the access signal.** Florida's December 12, 2025 P&T change summary, effective April 1, 2026, shows several new products landing Non-PDL while Brinsupri became PDL with clinical PA. Georgia's January 1, 2025 implementation list placed Rezdiffra, Agamree, Voquezna, Xdemvy, and Xphozah as NP/PA.

4. **Step edits and renewal thresholds are highly drug/class-specific.** Arkansas requires six consecutive months of controller-medication compliance for Xolair asthma and ties adult C-II stimulant access to functional impairment in school, work, or job-seeking. Connecticut's TNF, topical antipsoriatic, and CAPS criteria show how preferred status, sample-use rules, and cost-effectiveness logic can vary inside specialty classes.

5. **Some barriers are not labeled as PA.** Florida's GLP-1 barriers appear as age, volume, days-supply, and starter-fill edits in the limitations file. California's DUR alerts include refill-interval and additive-toxicity triggers before a prescriber ever sees a classic PA denial. Alabama's adult prescription cap can create benefit-limit friction outside PDL status.

## Selected Traceability

| State | Insight | Drug/Class | Type | Source |
|---|---|---|---|---|
| Alaska | Manufacturer submissions due much earlier than public comments for Jan. 2026 P&T | All agenda classes | Manufacturer submission rule | `text/alaska/alaska__ak-medicaid-pt-january-2026-notice-pdf__714c4d2351.txt`, p. 1 |
| Alaska | Manufacturer form routes PDL comments to Prime and discourages direct member contact | All PDL products | Process mechanics | `text/alaska/alaska__ak-submission-request-form-for-pharmaceutical-manufacturers-pdf__0507d82efb.txt`, p. 1 |
| Arizona | Rebate offers requested for HAE, new drugs, and LHRH, but not for several other reviewed classes | HAE, LHRH, SGLT2, oncology, PAH, UC | Cost-analysis signal | `text/arizona/arizona__az-jan-2026p-t-meeting-manufacturer-letter-pdf__ce4cd20b46.txt`, pp. 1-2 |
| Arizona | Spravato listed preferred with no grandfathering in Jan. 2026 recommendations | Spravato / esketamine | PDL placement | `text/arizona/arizona__az-january2026ptrecommendationslides-pdf__86cf05e600.txt`, p. 4 |
| Arkansas | Closed Drug Cost Committee reviews proprietary rebates/net cost | All PDL classes | Cost-analysis signal | `text/arkansas/arkansas__0502ab6b-5657-6ef6-b9a9-a2e6df168b85__f00e61afef.txt`, pp. 1-2 |
| Arkansas | Adult stimulant criteria require functional impairment documentation | C-II stimulants, Qelbree | Renewal/access threshold | `text/arkansas/arkansas__1650aea6-d1e5-4668-26d0-38e974096389__28d1f85f8a.txt`, p. 2 |
| Connecticut | Statutory PA safety valves: 14-day supply, 24-hour deemed approval, mental-health continuity, antiretroviral PDL exclusion | Non-preferred drugs, mental-health drugs, antiretrovirals | Override/final decision mechanics | `text/connecticut/connecticut__state-laws-requirements-for-pa-pdf__118afe7c41.txt`, p. 1 |
| Connecticut | TNF criteria prefer selected adalimumab/infliximab products but allow exceptions | TNF inhibitors | Drug-class criteria | `text/connecticut/connecticut__tnf-pdf__5dfea1083b.txt`, p. 3 |
| Connecticut | CAPS rationale explicitly leaves preference to cost-effective agents when clinical preference is not generalizable | Kineret, Ilaris, Arcalyst | Cost-analysis signal | `text/connecticut/connecticut__caps-pdf__cf75c68146.txt`, p. 2 |
| Florida | Dec. 2025 P&T changes effective Apr. 1, 2026 show Non-PDL defaults and Brinsupri PDL with clinical PA | New products, Brinsupri | Implementation timing | `text/florida/florida__summary-of-changes-december-2025-p-t-pdf__82a52dcb0e.txt`, p. 1 |
| Florida | GLP-1 barriers are age, volume, days-supply, and starter-fill limits | Mounjaro, Ozempic, Rybelsus, Trulicity, Victoza | Quantity limit | `text/florida/florida__summary-of-drug-limitations-04-30-2026-v175-pdf__1554dfcd8d.txt`, pp. 63, 71, 86, 103, 107 |
| Georgia | Rezdiffra and four other new drugs placed NP/PA effective Jan. 1, 2025 | Rezdiffra, Agamree, Voquezna, Xdemvy, Xphozah | PDL placement | `text/georgia/georgia__jan-2025-durbhandout__7b2da93ca9.txt`, p. 10 |
| Georgia | Manufacturer process includes six-month post-market review norm, 30-day pre-forum posting, and 10-business-day appeal window | New drugs and rebate classes | Manufacturer submission rule | `text/georgia/georgia__jan-2025-durbhandout__7b2da93ca9.txt`, p. 11 |
| California | DUR alerts include opioid-specific early-refill sensitivity and four-prescription CNS additive-toxicity trigger | Opioids, benzodiazepines, antipsychotics, selected psychotropics | DUR edit | `text/california/california__dur-json__1106aa5794.txt`, page n/a |
| Alabama | Adult prescription limits cap many adults at five drugs monthly but exempt antipsychotic, HIV, and seizure drugs | Adult prescriptions | Hidden access barrier | `text/alabama/alabama__4-3-8-rx-limits-aspx__67a3ef58b7.txt`, page n/a |

Full structured traceability for all 20 findings is in `group-a-insights.json`.
