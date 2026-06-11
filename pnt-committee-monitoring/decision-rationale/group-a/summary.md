# Group A Decision-Rationale Source Collection

Scope: Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware, Florida, and Georgia.

Status: finalized from the documents already collected locally. Broad crawling was stopped at user request. This summary uses the current local raw/text files plus blocked/uncollected URL records; it does not add new web retrievals.

## Manifests and Files

- Current row-level manifest: `manifest-current.csv` and `manifest-current.json`
- Completed-run manifest: `manifest.csv` and `manifest.json`
- Downloaded source copies: `raw/<state>/`
- Extracted text: `text/<state>/`
- Collector used for the completed/partial collection: `collect_group_a.py`

`manifest-current.*` is the preferred manifest for this final state because it includes locally collected files from the interrupted retry as well as blocked/uncollected URL records from the completed run.

## Collection by State

| State | Current manifest rows | Local files | Successful local source files | Gaps / blocked records | Main material collected |
|---|---:|---:|---:|---:|---|
| Alabama | 34 | 34 | 21 | 13 | P&T/PDL pages, meeting-date PDF, prior authorization metrics, pharmacy/DME pages, Synagis and AAC-related pages. Some P&T seed URLs had SSL/time-out failures before the retry added partial local copies. |
| Alaska | 70 | 70 | 70 | 0 | P&T notices, agendas, minutes, PDL files, PDL legends, manufacturer submission form, SFY schedules, and pharmacy pages. |
| Arizona | 93 | 93 | 90 | 3 | AHCCCS pharmacy page, P&T agendas, statewide drug lists, contractor notices, testimony/presentation materials, PA/policy documents, and public-notice pages. |
| Arkansas | 90 | 90 | 90 | 0 | Prime/Arkansas provider documents, DUR Board agendas/minutes, PDL overview, PA/medical-necessity forms, quantity-limit edits, drug class and program notices. |
| California | 61 | 61 | 5 | 56 | DHCS partners page, MCDAC FAQ, drug review policy, Medi-Cal Rx CDL page, and Medi-Cal Rx DUR JSON. Many linked DUR PDFs were recorded as 404 because embedded URLs were malformed or unavailable during collection. |
| Colorado | 2 | 2 | 0 | 2 | Seed P&T and pharmacy-resource URLs only; both returned HTTP 403 in this collection state. |
| Connecticut | 97 | 97 | 90 | 7 | P&T bylaws, statute, agenda/minutes/recommendations PDF, schedule, PDL changes, PA/step therapy forms, class criteria, diabetic supply lists, and pharmacy publications. |
| Delaware | 5 | 5 | 5 | 0 | Pharmacy Corner page, P&T bylaws, and June 2025 / October 2025 / April 2026 agenda downloads. |
| Florida | 37 | 37 | 37 | 0 | AHCA P&T page, pharmacy meeting notices, agendas, PDL page, PDL update PDFs, drug criteria, DUR board pages, and behavioral-health medication resources. |
| Georgia | 85 | 85 | 84 | 1 | DCH PDL pages, DURB meeting pages, recommendation PDFs, PDL PDFs, provider/manual pages, and related pharmacy policy pages. One FFS FAQ PDF returned HTTP 403. |

## Blocked or Uncollected Gaps

- Alabama: initial seed URLs failed on SSL certificate validation and some retry attempts timed out. Partial Alabama local files were still collected later, but the collection should not be treated as complete for Alabama P&T packets/minutes.
- Arizona: two contractor-notice PDF URLs contained unescaped spaces and were recorded as invalid in the completed run.
- California: the seed pages and JSON were collected, but many embedded DUR agenda/minute/educational-article URLs returned 404 in the completed run, mostly with trailing backslash artifacts from JSON escaping. Treat California product/class evidence as incomplete.
- Colorado: the two seed pages returned HTTP 403. No Colorado source text was available beyond error records.
- Connecticut: several linked PA/publication URLs contained unescaped spaces and were recorded as invalid.
- Georgia: the Georgia Medicaid FFS FAQ PDF returned HTTP 403, though many other DCH/DURB/PDL files were collected.

See `manifest-current.csv` for each URL, status, local raw path, extracted text path, and error reason.

## Decision-Rationale Patterns

1. Clinical criteria are the most visible public rationale. Across the collected states, public documents repeatedly surface safety, efficacy/effectiveness, clinical appropriateness, drug-class criteria, medical necessity, prior authorization, step therapy, quantity limits, and preferred/non-preferred status.

2. Economic rationale is usually less transparent than clinical rationale. Cost effectiveness, rebate, or net-cost language appears in several state materials, but product-level rebate logic is generally absent from public artifacts. Arkansas is the clearest example of explicit separation: clinical evidence is public-facing, while cost/rebate review is handled through a separate cost process that uses proprietary data.

3. The most actionable pharma signal is often post-meeting implementation, not meeting minutes. PDL change PDFs, contractor notices, PA criteria, quantity-limit edits, and recommendation PDFs often reveal more practical access impact than agenda titles alone.

4. Committee recommendations are often advisory. Final authority commonly sits with the Medicaid agency or director-level decision-maker rather than the committee itself. This is especially important for Arizona, California, Florida, Georgia, and Connecticut.

5. Manufacturer/public-comment windows vary materially. Alaska exposes a manufacturer submission form and meeting-topic schedule; Arizona and Florida publish testimony/presentation or meeting-notice materials; Delaware provides testimony/logistics resources; Georgia allows public comment from recipients, advocates, and Medicaid providers, while the matrix notes industry comment is not allowed during meetings. These windows are state-specific and should be monitored separately from meeting dates.

6. Published PDLs and PA criteria make class strategy more observable than individual deliberation. For many products, pharma can infer access posture from preferred/non-preferred status, criteria, edits, or implementation memos, but cannot reliably infer the full rationale or vote unless minutes/recommendations state it.

## Therapy, Product, and Class Mentions Found

These are mentions found in collected source text, not confirmed product-level P&T decisions unless the underlying document explicitly says so.

- Diabetes, obesity, and metabolic: GLP-1/GLP-1 RA terms, semaglutide, tirzepatide, Ozempic, Wegovy, Mounjaro, Zepbound, Trulicity, DPP-4, SGLT2, Jardiance, Farxiga, insulin, diabetes, obesity, and weight-loss language appeared across multiple states.
- Respiratory: asthma, COPD, inhalers, bronchodilator/respiratory terms, and related PDL/criteria language appeared in several states.
- Behavioral health and neurology: ADHD, stimulants, antipsychotics, antidepressants, behavioral health, depression, bipolar disorder, schizophrenia, seizure/epilepsy, migraine, and CGRP terms appeared in collected documents.
- Opioid use disorder, substance use, and pain: opioid, naloxone, buprenorphine, Suboxone, Sublocade, methadone, pain, and xylazine appeared in several collected states.
- Infectious disease and vaccines: hepatitis C, hepatitis B, HIV, antiretroviral/PrEP, COVID-19, influenza, RSV, pneumococcal, mpox, measles, vaccine/immunization, and tuberculosis terms appeared.
- Cardiovascular and renal: statins, amlodipine, simvastatin, lovastatin, gemfibrozil, aspirin, cardiovascular, heart failure, anticoagulant, and renal terms appeared.
- Immunology, dermatology, and biologics: biologic/biosimilar, Humira/adalimumab, Dupixent, Skyrizi, psoriasis, rheumatoid, atopic dermatitis, Crohn disease, and ulcerative colitis terms appeared.
- Specialty, oncology, and rare disease: oncology/cancer, hemophilia, sickle cell, cystic fibrosis, gene therapy, rare disease, and orphan terms appeared.

State breadth was strongest for Alaska, Arizona, Arkansas, Connecticut, Florida, and Georgia because those states had richer local text collections. Alabama, California, and Colorado are limited by the collection gaps above.

## High-Value Pharma Monitoring Implications

- Build a state-by-state watchlist that goes beyond meeting dates: agendas, topic schedules, manufacturer submission deadlines, public testimony deadlines, recommendation PDFs, final PDL PDFs, PA criteria, drug limitation pages, and contractor notices.
- Treat clinical evidence and access mechanics as two linked workstreams. Public rationale usually emphasizes safety, efficacy, effectiveness, and criteria, while real access impact often appears later through PDL placement, PA requirements, step therapy, quantity limits, and effective dates.
- For high-budget or fast-moving classes such as GLP-1s/obesity, SGLT2/DPP-4, immunology biologics/biosimilars, behavioral health, OUD therapies, respiratory inhalers, HIV/HCV, vaccines, and rare/specialty therapies, monitor both class-review agendas and implementation memos.
- Plan engagement ahead of topic schedules, not just meeting dates. Alaska and similar states with posted topic/submission materials provide clearer pre-meeting windows; other states require monitoring agenda publication and PDL-change timing.
- Separate committee outcome from final agency action in internal tracking. A recommendation, agenda listing, or discussion item should not be treated as a final coverage change until the state publishes an effective PDL, criteria, bulletin, memo, or final decision artifact.
- Record rationale gaps as a competitive-intelligence finding. When cost/rebate logic, vote detail, or product-specific reasoning is absent, the gap itself is useful: it tells teams where to rely on indirect evidence, stakeholder intelligence, or follow-up public-records work.

## Explicit Limitations

- This is not a complete 50-state analysis; it covers only the requested 10-state Group A.
- Broad crawling was stopped before retry fixes could complete. Current results are therefore a current-state source collection, not a guarantee that every relevant linked document was downloaded.
- Product/class mentions are text hits in local source copies. They should not be interpreted as confirmed decisions, rationales, or coverage changes without checking the specific cited document in `manifest-current.csv`.
- FDA approval-to-review timing, vote counts, rebate amounts, net-cost calculations, and full product-level rationale were generally not available in the normalized source text.
- Colorado has no downloaded decision-rationale source content in this current collection because seed pages returned HTTP 403.
