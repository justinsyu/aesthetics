# Group C P&T/DUR/PDL Decision-Rationale Source Collection

Scope: Massachusetts, Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey.

Status: updated with a targeted capped-crawl gap fill. This pass attempted only rows that had been marked `uncollected_seed_gap` because the broad crawl stopped before the seed URL was downloaded. It did not retry pre-existing 403, timeout, DNS, invalid URL, or other blocked/error rows, and it did not perform broad crawling.

## Files

- `manifest.csv` / `manifest.json`: collected, blocked, recovered, and uncollected seed URLs.
- `raw/<state>/`: saved source copies already collected.
- `text/<state>/`: extracted text already collected.
- `gap-fill-report.json`: targeted capped-gap attempt counts from the current pass.

## Collection Totals

- Saved source files/pages: 191
- Sources with extracted text: 186
- Blocked seed/source URLs: 13
- Remaining capped-crawl seed gaps: 0
- Saved files without extracted text: 5

## Targeted Capped-Crawl Gap Fill

- Attempted capped seed gaps: 22
- Final newly saved counts by state, including seed pages and bounded same-page document links:
  - Minnesota: 2 seed page(s), 0 same-page linked document/page(s).
  - Mississippi: 1 seed page(s), 0 same-page linked document/page(s).
  - Montana: 5 seed page(s), 12 same-page linked document/page(s).
  - Nebraska: 4 seed page(s), 36 same-page linked document/page(s).
  - Nevada: 3 seed page(s), 8 same-page linked document/page(s).
  - New Hampshire: 4 seed page(s), 12 same-page linked document/page(s).
  - New Jersey: 2 seed page(s), 3 same-page linked document/page(s).
- Repaired URL-encoding/host issues from the targeted pass: 15 save(s).
- Final non-addressable targeted-pass gaps:
  - New Jersey: 1 seed page(s), 2 same-page link(s).

## New Patterns Added By This Fill

- The capped-gap fill materially improved coverage for Montana, Nebraska, Nevada, New Hampshire, and New Jersey, replacing their prior seed-gap status with extracted text coverage.
- Nebraska contributed the largest new decision-rationale corpus in this pass, led by DUR minutes/agendas and PDL sources. The extracted text is especially criteria-heavy: prior authorization/step-therapy, utilization limits, comparative therapeutic value, and implementation language are all prominent.
- Montana added DUR/Formulary meeting material and PDL content. The newly available text reinforces a common pattern: public documents expose clinical criteria, preferred/non-preferred positioning, and PA logic more consistently than explicit net-cost or rebate rationale.
- Nevada added Silver State Scripts/P&T and DUR archive material. The strongest new signals are public-comment/manufacturer-input language, utilization review framing, and PA/criteria language around opioid, diabetes/obesity, respiratory, migraine, and autoimmune terms.
- New Hampshire added Prime Therapeutics portal, agenda/minute, and PDL material. The new text increases visibility into cardiometabolic, respiratory, opioid/pain, ADHD/CNS, diabetes/GLP-1, autoimmune, and migraine classes.
- New Jersey added DURB membership/source pages and action-summary material where available, but the current text is mostly governance and utilization-review oriented rather than product-decision rich.
- Product mentions newly strengthened by the filled states include GLP-1/obesity agents (`Wegovy`, `Zepbound`), migraine agents (`Emgality`, `Ajovy`, `Aimovig`, `Nurtec`, `Qulipta`), immunology/specialty agents (`Rinvoq`, `Dupixent`, `Humira`, `Cosentyx`, `Stelara`, `Skyrizi`), cardiometabolic agents (`Xarelto`, `Entresto`, `Repatha`, `Praluent`), and hepatitis C agents (`Epclusa`, `Mavyret`). These are source-text hits, not confirmed decisions unless the linked text explicitly states an action.

## State Coverage

| State | Saved | Text extracted | Blocked | Uncollected seed gaps | Notes |
|---|---:|---:|---:|---:|---|
| Massachusetts | 0 | 0 | 7 | 0 | Mass.gov returned HTTP 403 during collection |
| Michigan | 40 | 37 | 1 | 0 | Collected text available |
| Minnesota | 5 | 5 | 0 | 0 | Collected text available |
| Mississippi | 46 | 46 | 0 | 0 | Collected text available |
| Missouri | 11 | 11 | 2 | 0 | Collected text available |
| Montana | 17 | 17 | 0 | 0 | Collected text available |
| Nebraska | 40 | 38 | 0 | 0 | Collected text available |
| Nevada | 11 | 11 | 0 | 0 | Collected text available |
| New Hampshire | 16 | 16 | 0 | 0 | Collected text available |
| New Jersey | 5 | 5 | 3 | 0 | Collected text available |

## Collected Documents by State

### Massachusetts

- No local documents collected before the crawl was stopped.
- Blocked/uncollected seed URLs:
  - https://www.mass.gov/doc/dur-december-10-2025-meeting-agenda-0/download - HTTPError: HTTP Error 403: Forbidden
  - https://www.mass.gov/doc/dur-march-11-2026-meeting-agenda-0/download - HTTPError: HTTP Error 403: Forbidden
  - https://www.mass.gov/info-details/about-the-masshealth-drug-utilization-review-dur-program - HTTPError: HTTP Error 403: Forbidden
  - https://www.mass.gov/lists/drug-utilization-review-dur-board-meeting-agendas - HTTPError: HTTP Error 403: Forbidden
  - https://www.mass.gov/lists/drug-utilization-review-dur-board-meeting-minutes - HTTPError: HTTP Error 403: Forbidden
  - Additional blocked/uncollected URLs: 2; see `manifest.csv`.

### Michigan

- `raw/michigan/michigan__002__mi.primetherapeutics.com.html`; text: `not extracted`; MI Prime Medicaid portal
- `raw/michigan/michigan__009__mi.primetherapeutics.com.html`; text: `not extracted`; Pharmacy Benefits Program/Prime Therapeutics Management, LLC
- `raw/michigan/michigan__020__mi.primetherapeutics.com.html`; text: `not extracted`; .
- `raw/michigan/michigan__004__mirx_ptc_materials_20250603.pdf`; text: `text/michigan/michigan__004__mirx_ptc_materials_20250603.txt`; 2025-06-03 MDHHS Pharmacy and Therapeutics Committee
- `raw/michigan/michigan__005__mirx_ptc_materials_20260303.pdf`; text: `text/michigan/michigan__005__mirx_ptc_materials_20260303.txt`; 2025-09-02 MDHHS Pharmacy and Therapeutics Committee
- Additional saved items: 35; see `manifest.csv`.
- Blocked/uncollected seed URLs:
  - https://michigan.fhsc.com/Committees/PandT.asp - URLError: <urlopen error [Errno 11001] getaddrinfo failed>

### Minnesota

- `raw/minnesota/minnesota__005__d5bd5333eafe8b0ccd6023ba818d1aa6-db08499c.html`; text: `text/minnesota/minnesota__005__d5bd5333eafe8b0ccd6023ba818d1aa6-db08499c.txt`; 2025-06-18 Drug Formulary Committee
- `raw/minnesota/minnesota__002__d5bd5333eafe8b0ccd6023ba818d1aa6-f76db395.html`; text: `text/minnesota/minnesota__002__d5bd5333eafe8b0ccd6023ba818d1aa6-f76db395.txt`; 2025-06-18 Drug Formulary Committee
- `raw/minnesota/minnesota__001__d5bd5333eafe8b0ccd6023ba818d1aa6-3f589e74.html`; text: `text/minnesota/minnesota__001__d5bd5333eafe8b0ccd6023ba818d1aa6-3f589e74.txt`; MN DHS Drug Formulary Committee
- `raw/minnesota/minnesota__004__d5bd5333eafe8b0ccd6023ba818d1aa6-f83089ee.html`; text: `text/minnesota/minnesota__004__d5bd5333eafe8b0ccd6023ba818d1aa6-f83089ee.txt`; MN DHS Drug Formulary Committee
- `raw/minnesota/minnesota__003__2025-12-17-dfc-minutes_tcm1053-717154.pdf`; text: `text/minnesota/minnesota__003__2025-12-17-dfc-minutes_tcm1053-717154.txt`; 2025-12-17 Drug Formulary Committee

### Mississippi

- `raw/mississippi/mississippi__029__drug-utilization-review-dur-board.html`; text: `text/mississippi/mississippi__029__drug-utilization-review-dur-board.txt`; Drug Utilization Review Board
- `raw/mississippi/mississippi__003__pharmacy-and-therapeutics-committee-archive.html`; text: `text/mississippi/mississippi__003__pharmacy-and-therapeutics-committee-archive.txt`; P&T archive
- `raw/mississippi/mississippi__001__pharmacy-and-therapeutics-committee.html`; text: `text/mississippi/mississippi__001__pharmacy-and-therapeutics-committee.txt`; P&T Committee
- `raw/mississippi/mississippi__030__pharmacy-and-therapeutics-committee.html`; text: `text/mississippi/mississippi__030__pharmacy-and-therapeutics-committee.txt`; Select a page
- `raw/mississippi/mississippi__031__pharmacy-and-therapeutics-committee.html`; text: `text/mississippi/mississippi__031__pharmacy-and-therapeutics-committee.txt`; Pharmacy and Therapeutics Committee - Mississippi Division of Medicaid Pharmacy and Therapeutics Committee - Mississippi Division of Medicaid
- Additional saved items: 41; see `manifest.csv`.

### Missouri

- `raw/missouri/missouri__009__alzheimers-agents-acetylcholinesterase-inhibitors-n-methyl-d-aspartate-receptor.html`; text: `text/missouri/missouri__009__alzheimers-agents-acetylcholinesterase-inhibitors-n-methyl-d-aspartate-receptor.txt`; Alzheimer’s Agents, Acetylcholinesterase Inhibitors, N-Methyl-D-Aspartate Receptor Antagonists & Combinations PDL Edit January 2026
- `raw/missouri/missouri__010__anti-migraine-alternative-agents-pdl-edit-january-2026.html`; text: `text/missouri/missouri__010__anti-migraine-alternative-agents-pdl-edit-january-2026.txt`; Anti-Migraine, Alternative Agents PDL Edit January 2026
- `raw/missouri/missouri__025__mydss.mo.gov-media-file-corticosteroids-and-rhinitis-nasal-april-2026-proposal.html`; text: `text/missouri/missouri__025__mydss.mo.gov-media-file-corticosteroids-and-rhinitis-nasal-april-2026-proposal.txt`; Corticosteroids and Rhinitis nasal April 2026 Proposal
- `raw/missouri/missouri__026__mydss.mo.gov-media-file-corticosteroids-ophthalmic-april-2026-proposal.html`; text: `text/missouri/missouri__026__mydss.mo.gov-media-file-corticosteroids-ophthalmic-april-2026-proposal.txt`; Corticosteroids Ophthalmic April 2026 Proposal
- `raw/missouri/missouri__028__mydss.mo.gov-media-file-corticosteroids-oral-inhaled-april-2026-proposal.html`; text: `text/missouri/missouri__028__mydss.mo.gov-media-file-corticosteroids-oral-inhaled-april-2026-proposal.txt`; Corticosteroids Oral Inhaled April 2026 Proposal
- Additional saved items: 6; see `manifest.csv`.
- Blocked/uncollected seed URLs:
  - https://mydss.mo.gov/media/pdf/anticholinergics-long-acting-beta-adrenergics-laba-inhaled-corticosteroid-ics-2 - TimeoutError: The read operation timed out
  - https://mydss.mo.gov/mhd/pharmacy-committees - TimeoutError: The read operation timed out

### Montana

- `raw/montana/montana__001__medicaiddur.html`; text: `text/montana/montana__001__medicaiddur.txt`; Medicaid DUR Board
- `raw/montana/montana__002__19dur.html`; text: `text/montana/montana__002__19dur.txt`; DUR/Formulary meeting materials
- `raw/montana/montana__015__may2026preferreddruglist.pdf`; text: `text/montana/montana__015__may2026preferreddruglist.txt`; PDL PDF
- `raw/montana/montana__003__august2023durmeetingminutesamended10252023.pdf`; text: `text/montana/montana__003__august2023durmeetingminutesamended10252023.txt`; August 9, 2023 Amended
- `raw/montana/montana__004__mtapr2023durmeetingagenda04.26.23.pdf`; text: `text/montana/montana__004__mtapr2023durmeetingagenda04.26.23.txt`; April 26, 2023
- Additional saved items: 12; see `manifest.csv`.

### Nebraska

- `raw/nebraska/nebraska__002__dur-board-meeting-minutes-10.28.25.pdf`; text: `text/nebraska/nebraska__002__dur-board-meeting-minutes-10.28.25.txt`; Minutes​
- `raw/nebraska/nebraska__003__dur-board-meeting-minutes-september-9-2025.pdf`; text: `text/nebraska/nebraska__003__dur-board-meeting-minutes-september-9-2025.txt`; Minutes​
- `raw/nebraska/nebraska__004__draft-dur-board-meeting-minutes-1.13.26.pdf`; text: `text/nebraska/nebraska__004__draft-dur-board-meeting-minutes-1.13.26.txt`; Draft Minutes​
- `raw/nebraska/nebraska__005__ne-medicaid-dur-board-meeting-agenda-11.15.22.pdf`; text: `text/nebraska/nebraska__005__ne-medicaid-dur-board-meeting-agenda-11.15.22.txt`; November 15, 2022
- `raw/nebraska/nebraska__006__nebraska-medicaid-dur-board-meeting-agenda---february-13-2024.pdf`; text: `text/nebraska/nebraska__006__nebraska-medicaid-dur-board-meeting-agenda---february-13-2024.txt`; February 13, 2024
- Additional saved items: 35; see `manifest.csv`.

### Nevada

- `raw/nevada/nevada__001__www.nevadamedicaid.nv.gov.html`; text: `text/nevada/nevada__001__www.nevadamedicaid.nv.gov.txt`; Silver State Scripts Board / P&T page
- `raw/nevada/nevada__002__dur-archives-2025.html`; text: `text/nevada/nevada__002__dur-archives-2025.txt`; 2025-07-31 Drug Utilization Review Board
- `raw/nevada/nevada__011__dur_2026_meeting_schedule.pdf`; text: `text/nevada/nevada__011__dur_2026_meeting_schedule.txt`; 2026-01-15 Drug Utilization Review Board
- `raw/nevada/nevada__003__dur_01_16_25_agenda.pdf`; text: `text/nevada/nevada__003__dur_01_16_25_agenda.txt`; DUR Agenda 01-16-25
- `raw/nevada/nevada__004__dur_01_16_25_minutes.pdf`; text: `text/nevada/nevada__004__dur_01_16_25_minutes.txt`; DUR Minutes 01-16-25
- Additional saved items: 6; see `manifest.csv`.

### New Hampshire

- `raw/new-hampshire/new-hampshire__001__nh.primetherapeutics.com.html`; text: `text/new-hampshire/new-hampshire__001__nh.primetherapeutics.com.txt`; NH Medicaid Pharmacy portal
- `raw/new-hampshire/new-hampshire__022__5091d9a9-8abb-fa9a-8d1b-598d15f04c9e.pdf`; text: `text/new-hampshire/new-hampshire__022__5091d9a9-8abb-fa9a-8d1b-598d15f04c9e.txt`; NHRx_PDL (10).pdf
- `raw/new-hampshire/new-hampshire__023__cd3e6793-b2a7-ccf0-1c36-70c18f52ee31.pdf`; text: `text/new-hampshire/new-hampshire__023__cd3e6793-b2a7-ccf0-1c36-70c18f52ee31.txt`; NHRx_PDL (11).pdf
- `raw/new-hampshire/new-hampshire__014__91c61a5a-350c-a884-33f0-5c390327898c.pdf`; text: `text/new-hampshire/new-hampshire__014__91c61a5a-350c-a884-33f0-5c390327898c.txt`; NH PDL example
- `raw/new-hampshire/new-hampshire__024__91c61a5a-350c-a884-33f0-5c390327898c.pdf`; text: `text/new-hampshire/new-hampshire__024__91c61a5a-350c-a884-33f0-5c390327898c.txt`; NH_PDL 7.14.2025.pdf
- Additional saved items: 11; see `manifest.csv`.

### New Jersey

- `raw/new-jersey/new-jersey__001__members.html`; text: `text/new-jersey/new-jersey__001__members.txt`; DURB members
- `raw/new-jersey/new-jersey__003__protocols.html`; text: `text/new-jersey/new-jersey__003__protocols.txt`; DURB Approved Protocols
- `raw/new-jersey/new-jersey__004__durb.html`; text: `text/new-jersey/new-jersey__004__durb.txt`; NJ DURB
- `raw/new-jersey/new-jersey__005__index.html`; text: `text/new-jersey/new-jersey__005__index.txt`; Meeting Schedule & Minutes
- `raw/new-jersey/new-jersey__006__protocols.html`; text: `text/new-jersey/new-jersey__006__protocols.txt`; DURB Approved Protocols
- Blocked/uncollected seed URLs:
  - https://nj.gov/humanservices/dmahs/boards/durb/meeting/ - HTTPError: HTTP Error 404: Not found
  - https://www.nj.gov/humanservices/dmahs/boards/durb/Summary_of_DURB_Action.pdf - HTTPError: HTTP Error 404: Not found
  - https://www.nj.gov/humanservices/dmahs/boards/durb/meeting/ - HTTPError: HTTP Error 404: Not found

## Extracted Decision-Rationale Patterns

These are term-supported patterns from extracted text only; they are directional and should be re-run after the remaining seed gaps are collected.

- **Prior authorization / step-therapy logic**: 16242 term hits across 8 state(s): Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire.
- **Clinical efficacy/safety framing**: 5754 term hits across 7 state(s): Michigan, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire.
- **Utilization controls**: 1561 term hits across 7 state(s): Michigan, Mississippi, Montana, Nebraska, Nevada, New Hampshire, New Jersey.
- **Comparative therapeutic value**: 1068 term hits across 5 state(s): Michigan, Mississippi, Missouri, Montana, Nebraska.
- **Cost / fiscal / rebate signals**: 849 term hits across 7 state(s): Michigan, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire.
- **Final authority / implementation**: 661 term hits across 9 state(s): Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey.
- **Public comment / manufacturer input**: 609 term hits across 8 state(s): Michigan, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey.

Interpretation for pharma monitoring:

- Public artifacts most often expose clinical, utilization-management, and implementation language; detailed net-cost/rebate rationale is usually a gap.
- Meeting packets, recommendations, provider notices, PDL/PA criteria, and minutes need to be tracked together because recommendation and implementation can be separated.
- Public-comment or testimony instructions are strategically important because they are often the only public engagement window captured in these materials.

## Therapy / Disease / Class Mentions Found

- **Opioid / substance use / pain**: 1209 term hits in Michigan, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire.
  - Michigan: "lution2  Nalocet®  oxycodone caps 2  oxycodone tabs (20mg, 30mg)2  oxycodone oral conc soln2  oxymorphone2  pentazocine/naloxone  Percocet®  Prolate®  --- Page 28 --- Michigan Preferred Drug List (PDL)/Single PDL  Effective 06/01/2025  Preferred Agents do not require prior authorization, except as noted in the chart at"
- **Diabetes / obesity / GLP-1**: 1206 term hits in Michigan, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire.
  - Michigan: "II.  Therapeutic Class Reviews: Antibiotics/Anti-Infectives and Asthma/COPD/Allergy Agents  IX.  Off-Cycle Review: Anti-Obesity Criteria  X.  Meeting Dates  XI.  Adjourn  Public Comments:  1. Elena Fernandez, HEOR Field Associate Director, East, on behalf of Vertex Pharmaceuticals, on Alyftrek.  2. Christine Dube, Dire"
- **ADHD / CNS stimulants**: 980 term hits in Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, New Hampshire.
  - Michigan: "tabs 2  buprenorphine/naloxone SL film (generic Suboxone films)2  Opioid Withdrawal Symptom Management  clonidine tabs  guanfacine/guanfacine ER  lofexidine  Lucemyra®  --- Page 30 --- Michigan Preferred Drug List (PDL)/Single PDL  Effective 06/01/2025  Preferred Agents do not require prior authorization, except as not"
- **Autoimmune / immunology**: 736 term hits in Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire.
  - Michigan: "ge 5 --- Michigan Pharmacy and Therapeutics Committee  Tuesday, June 3, 2025  Agenda  5  8. Biosimilars to ustekinumab (Stelara) - an interleukin (IL)-12 and IL-23 antagonist indicated for the treatment of  adults and pediatric patients 6 years and older with plaque psoriasis (PsO) and psoriatic arthritis (PsA), as wel"
- **Cardiometabolic / anticoagulation**: 728 term hits in Michigan, Mississippi, Missouri, Montana, Nebraska, New Hampshire.
  - Michigan: "eatment of the cardiomyopathy of wild- type or variant transthyretin-mediated amyloidosis (ATTR-CM) in adults to reduce cardiovascular death and  cardiovascular related hospitalization. [Not a PDL class - Add to MPPL with PA] Note: Under review for carveout.  Proposed Criteria:  •  Patient is 18 years of age or older; "
- **Asthma / COPD / respiratory**: 711 term hits in Michigan, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire.
  - Michigan: "MDHHS Updates  VI.  Public Comment  VII.  New Drugs  VIII.  Therapeutic Class Reviews: Antibiotics/Anti-Infectives and Asthma/COPD/Allergy Agents  IX.  Off-Cycle Review: Anti-Obesity Criteria  X.  Meeting Dates  XI.  Adjourn  Public Comments:  1. Elena Fernandez, HEOR Field Associate Director, East, on behalf of Vertex"
- **Oncology / hematology**: 590 term hits in Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, New Hampshire, New Jersey.
  - Michigan: "to prevent or reduce the frequency of bleeding episodes in adult and pediatric patients 12 years of  age and older with hemophilia A (congenital factor VIII deficiency) with FVIII inhibitors or hemophilia B  (congenital factor IX deficiency) with FIX inhibitors. [Not a PDL class - Add to MPPL with PA] Note: Falls in an"
- **Hepatitis / HIV / infectious disease**: 546 term hits in Michigan, Mississippi, Missouri, Montana, Nebraska, New Hampshire, New Jersey.
  - Michigan: "oducts  9. Cephalosporins – 3rd Generation [PDL pg 5]  a. No change to the current classification of drug products  10. Hepatitis C – [PDL pg 6]  a. No change to the current classification of drug products  11. Hepatitis C – Direct Acting Antivirals [PDL pg 6]  a. No change to the current classification of drug product"
- **Migraine / headache**: 405 term hits in Michigan, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire.
  - Michigan: "lmitriptan ODT2 /zolmitriptan nasal  Zomig® nasal spray / Zomig® tablet  Antimigraine Agents, Acute Treatment -  Other  Nurtec ODT®2♦  Elyxyb®2  Reyvow2  Ubrelvy®2  Zavzpret®2  Antimigraine Agents, Preventive Treatment♦ Aimovig®2  Ajovy®2  Emgality®2  Nurtec ODT®2  Qulipta®2  Skeletal Muscle Relaxants  baclofen tablets"
- **Psychiatry / behavioral health**: 257 term hits in Michigan, Mississippi, Missouri, Montana, Nebraska, New Hampshire.
  - Michigan: "Valtoco®  vigabatrin  Vigadrone®  Vimpat®  Xcopri®  Zarontin®  Zonisade®  zonisamide  Ztalmy®  Atypical Antipsychotics  Abilify®, Abilify MyCite®  Abilify Asimtufii®, Abilify Maintena®  aripiprazole, aripiprazole ODT  Aristada®, Aristada Initio®  Caplyta®  clozapine, clozapine ODT  Clozaril®  Cobenfy®  Erzofri®  Fanapt"

## Product Mentions Found

- Rinvoq: 102 hit(s) in Michigan, Mississippi, Montana, Nebraska, Nevada, New Hampshire.
- Dupixent: 92 hit(s) in Michigan, Mississippi, Montana, Nebraska, Nevada, New Hampshire.
- Emgality: 83 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Humira: 69 hit(s) in Michigan, Minnesota, Mississippi, Montana, Nebraska, New Hampshire.
- Xarelto: 65 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Ajovy: 58 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Cosentyx: 52 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Repatha: 50 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Entresto: 49 hit(s) in Michigan, Mississippi, Missouri, Montana, Nebraska, New Hampshire.
- Aimovig: 47 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Bydureon: 47 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Stelara: 46 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Epclusa: 45 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Praluent: 44 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Skyrizi: 44 hit(s) in Michigan, Mississippi, Montana, Nebraska, New Hampshire.
- Additional configured product hits: 25; see extracted text files for details.

## Explicit Limitations

- Collection is incomplete for this group because the broad crawl was intentionally stopped.
- This update filled only seed gaps caused by the crawl cap; it did not retry pre-existing blocked/error rows.
- Massachusetts source pages/documents were attempted but returned HTTP 403 in the local collector.
- No `uncollected_seed_gap` rows remain in the current Group C manifest; remaining gaps are blocked/error rows such as HTTP 403, DNS failure, timeout, or HTTP 404.
- Text extraction was not available for every saved file; see `manifest.csv` for saved-but-unextracted rows.
- Product-level conclusions, exact votes, final coverage decisions, approval-to-review speed, rebate logic, and net-cost rationale are unavailable unless explicitly present in extracted text.
- Counts are search-term counts, not validated clinical categorizations.

## High-Value Next Pass

- For remaining blocked/error rows, use source-owner pages, alternate official mirrors, or manual browser retrieval where permitted rather than automated broad crawling.
- Prioritize meeting packets/material PDFs, minutes, PDL recommendation documents, PA/protocol criteria, provider notices, and public-comment instructions.
- Normalize extracted rows into: state, date, body, drug/class, action/recommendation, rationale text, final authority, effective date, comment/manufacturer window, source URL, and gap flags.
