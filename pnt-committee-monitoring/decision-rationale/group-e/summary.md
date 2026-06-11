# Group E decision-rationale source summary

Scope: South Dakota, Tennessee, Texas, Utah, Vermont, Virginia, Washington, West Virginia, Wisconsin, and Wyoming.

Status: Targeted capped-gap fill completed. This update used only rows in `manifest.csv` marked as `uncollected_seed_gap` because broad crawling had been stopped/capped, plus clearly relevant same-page West Virginia meeting documents linked from the collected P&T meeting page. Known 403, 404, timeout, invalid URL, and connection-reset rows were not retried unless a capped seed URL newly returned that status during this targeted pass. Full row-level source status is in `manifest.csv` and `manifest.json`.

## Targeted fill result

| State | Newly collected from capped gaps | Newly failed from capped gaps | Same-page documents added | Notes |
|---|---:|---:|---:|---|
| Tennessee | 5 | 0 | 0 | DUR/PAC schedules and the November 6, 2025 PAC minutes were collected from OptumRx/TennCare document URLs. |
| West Virginia | 1 | 3 | 13 | Current BMS P&T meetings page was collected, plus agenda, meeting-notes, and changes-only PDFs from that page. Three legacy DHHR URLs now return 404. |
| Wisconsin | 4 | 0 | 0 | Pharmacy resources, PAC page, PAC guidelines, and PDL PDF were collected. |
| Wyoming | 7 | 0 | 0 | Annual report, P&T regulation, public-comment policy, May 2026 agenda, and August/November/February minutes were collected. |
| Total | 17 | 3 | 13 | No `uncollected_seed_gap` rows remain in Group E. |

## Current collection status

| State | Collected text records | Failed records | Uncollected seed gaps | Most useful collected source types |
|---|---:|---:|---:|---|
| South Dakota | 36 | 0 | 0 | P&T meeting pages, board/member pages, March 2025 packet, March 2026 materials, draft minutes, public-meeting guidance |
| Tennessee | 8 | 1 | 0 | TennCare PAC minutes/schedules, DUR schedules, TennCare policy, Optum contract amendment, performance audit |
| Texas | 70 | 3 | 0 | TMHP DUR meeting notices, Texas statutes; key recommendation/decision PDFs returned 404 |
| Utah | 37 | 9 | 0 | P&T/DUR pages, P&T bylaws, DUR bylaws, PDL PDF, PA/coverage pages |
| Vermont | 59 | 3 | 0 | Pharmacy Best Practices and Cost Control report, legislative pages; official DURB page/PDFs returned 403 |
| Virginia | 120 | 1 | 0 | Town Hall meeting files, DUR minutes/agendas, DMAS bulletins, P&T/DUR governing materials |
| Washington | 113 | 0 | 0 | HCA meetings/materials, participants, related rules, August/October 2025 P&T/DUR topic agendas |
| West Virginia | 14 | 3 | 0 | BMS P&T meeting page, 2025/2026 agendas, meeting notes, changes-only PDFs, PDL/PA change artifacts |
| Wisconsin | 4 | 0 | 0 | PAC guidelines, PDL PDF, pharmacy resource page, PAC meeting page |
| Wyoming | 7 | 0 | 0 | P&T minutes, May 2026 agenda, public-comment policy, P&T regulation, Medicaid annual report |

## Remaining non-addressable gaps

These are not capped-crawl gaps. They are blocked, failed, or obsolete URLs that should not be retried without a new source-discovery request.

- Tennessee: `https://www.tn.gov/tenncare/members-applicants/pharmacy.html` failed with remote connection reset.
- Texas: three direct Vendor Drug/PDL recommendation or decision PDFs returned HTTP 404.
- Utah: six oEmbed links returned HTTP 400, and three state page URLs with unencoded folder spaces were invalid.
- Vermont: official DURB page, policies/procedures PDF, and December 2024 pharmacy newsletter returned HTTP 403.
- Virginia: one board-of-medical-assistance URL returned HTTP 404.
- West Virginia: the legacy DHHR PDL, legacy P&T committee page, and legacy Chapter 518 pharmacy manual URLs returned HTTP 404. The current BMS P&T meeting page was collected successfully.

## General decision-rationale patterns

1. Rationale is often visible in criteria mechanics rather than in a narrative "why" field. The highest-yield artifacts are meeting notes, changes-only PDFs, PAC/P&T minutes, and PA criteria pages because they expose preferred/non-preferred status, trial requirements, renewal criteria, documentation expectations, and motions.

2. Most public decisions separate clinical recommendation from cost or operational implementation. Wyoming repeatedly pairs "limit to indication" with referral to the Department of Health for cost analysis. Wisconsin explicitly bases recommendations on safety, effectiveness, clinical outcomes, and relative cost. West Virginia meeting notes show committee motions, while the changes-only/PDL files show the resulting access controls.

3. New drugs often start constrained until a class review or deeper criteria cycle. Wisconsin says new drugs are usually added to existing PDL classes as non-preferred until the next scheduled class review. Tennessee and Wyoming minutes show new products being approved with PA criteria, quantity limits, or "limit to indication" language rather than open access.

4. Manufacturer engagement is structured and time-limited. Tennessee public testimony was five minutes. Wisconsin speakers must register, may speak in one four-minute slot in up to two drug classes, and may only address drugs in the reviewed class. Wyoming requires written materials at least seven days before the meeting, limits oral comments to three minutes, accepts only published studies for committee review, and asks presenters to state requested action, supporting evidence, contrary evidence, and differentiation versus alternatives.

5. Committees ask questions that reveal likely coverage objections. Tennessee asked about acute versus prophylactic use for Symbravo, labeled adjunctive-use boundaries and NNT for Caplyta, Zepbound's OSA versus diabetes indication, GLP-1 diet monitoring, and evidence for off-label/additional GLP-1 use. Wyoming minutes repeatedly note no comparative evidence, accelerated approval status, lack of outcomes data, and need for cost analysis.

6. "Documentation" versus "attestation" is a major access lever. Tennessee minutes distinguish chart notes/lab values from provider attestation and show TennCare rejecting some PAC wording changes when the agency wanted different documentation flexibility or guideline alignment. Wisconsin's general non-preferred criteria require evidence of poor response, adverse reaction, drug interaction, or a medical condition preventing use of preferred drugs.

7. Public minutes can reveal agency override or post-committee governance. Tennessee's PAC minutes include a "review of decisions from previous meeting" where TennCare rejected some PAC-approved modifications. Wisconsin recommendations go to the Secretary for adoption, modification, or rejection. Wyoming's P&T committee provides recommendations and feedback to Medicaid Pharmacy Services under regulation.

## Therapy, class, and product patterns added by the capped-gap fill

### Tennessee

- The November 6, 2025 PAC minutes are a high-yield product-level source. Public testimony covered Vykat XR, Symbravo, Caplyta, Zepbound, Camzyos, and Eliquis.
- GLP-1/weight management rationale is unusually explicit. TennCare described interim coverage effective August 1, 2025, utilization growth over three months, budgetary concern, and a policy goal of maintaining access for members most likely to benefit. Criteria include labeled-age minimums, obesity/BMI and comorbidity thresholds, lifestyle or comprehensive weight-management participation, no duplicate GLP-1 use for weight loss, renewal weight-loss thresholds, and quantity limits for Saxenda, Wegovy, and Zepbound.
- Committee discussion sharpened the GLP-1 access rule. The final approved modification returned the adult BMI cutoff to greater than 30 kg/m2 and clarified that the medication will not be used with other GLP-1 agonists for weight loss.
- Oncology and rare/specialty drugs are handled through PA criteria tied to diagnosis, biomarker or mutation status, prior therapy, specialist involvement, response, and toxicity. Example: Avmapki/Fakzynja criteria for recurrent low-grade serous ovarian cancer include KRAS mutation, prior guideline-recommended systemic therapy, oncologist involvement, response, and toxicity checks.
- TennCare's post-meeting decision review is especially valuable for pharma: PAC-approved changes can be rejected by the agency based on PA workflow, provider burden, off-label/rare-disease justification needs, or guideline components.

### West Virginia

- The current BMS P&T page confirms virtual meetings, agendas, meeting notes, and changes-only artifacts for 2025 and 2026. Public comments are limited to agenda classes; one agenda specifies a three-minute limit per product.
- Meeting notes show a common bulk-approval workflow: non-extracted categories may be accepted as presented, while extracted classes receive motions and votes. Many motions are unanimous, but at least one non-narcotic analgesic motion carried by roll-call vote after amendment.
- Classes appearing in collected notes and changes include GLP-1 diabetes agents, MACE-reduction GLP-1 agents, MASH, antipsychotics, atopic dermatitis immunomodulators, antihemophilia factors, DPP-4 inhibitors, hypoglycemia agents, stimulants/non-amphetamine agents, acute antimigraine agents, lipotropics/non-statins, antiretrovirals, antivirals, beta blockers, antiemetics, and skeletal muscle relaxants.
- West Virginia PDL/changes artifacts expose granular PA rules. Common patterns include required trials of each or multiple preferred agents, same-mechanism or same-subclass trial requirements, appeal-only categories, allergy/exception carveouts, diagnosis/age restrictions, and notes that convenience or enhanced compliance alone may be insufficient justification for non-preferred access.

### Wisconsin

- Wisconsin makes the rationale framework explicit: recommendations are based primarily on relative safety, effectiveness, clinical outcomes, and relative cost to Wisconsin Medicaid versus therapeutically interchangeable alternatives in the same class.
- Non-preferred coverage generally requires at least one of: unsatisfactory therapeutic response or clinically significant adverse reaction to a preferred drug, clinically significant interaction with a preferred option, or a medical condition preventing use of a preferred option. This is directly useful for anticipating evidence packages and exception narratives.
- Wisconsin has alternate criteria for selected CNS/behavioral and PAH classes: Alzheimer's agents, anticonvulsants, other antidepressants, SSRIs, antiparkinson agents, antipsychotics, and pulmonary arterial hypertension.
- Manufacturer engagement is formal and constrained. Committee members should not meet privately with manufacturers on upcoming topics, but manufacturers may provide information during public comment. Written testimony is reviewed by department staff and submitted to committee members before meetings.
- The PDL PDF confirms a practical access distinction: some preferred agents still require clinical prior authorization, and SeniorCare coverage can depend on rebate-agreement status.

### Wyoming

- Wyoming's public-comment policy is one of the clearest manufacturer playbooks in this group. Materials must be submitted seven days in advance; unpublished posters and package-insert summaries are not accepted; presenters must address requested action, supporting evidence, contrary evidence, and differentiation.
- Wyoming minutes show a repeatable decision formula for new drugs: approve or limit to indication, then refer to the Department of Health for cost analysis when budget impact or therapeutic alternatives matter.
- GLP-1/MASH criteria are detailed. Wegovy for MASH requires biopsy or noninvasive test confirmation, F2/F3 fibrosis, diet/exercise attestation, no concurrent GLP-1 or GLP-1/GIP therapy, and renewal checks that disease has not progressed to F4 fibrosis.
- Migraine criteria evolved toward CGRP/gepant sequencing. Minutes state Botox should generally follow CGRP antagonist or gepant trial, with a 12-week trial requirement and combination therapy allowed when headaches remain above a threshold.
- Wyoming rare-disease and specialty reviews frequently cite limited comparative evidence, accelerated approval, small populations, or future head-to-head evidence. Products/classes discussed include Vykat XR/Prader-Willi syndrome, Vanrafia/IgA nephropathy, Saphnelo/systemic sclerosis-associated interstitial lung disease, vitiligo/JAK inhibitors, hemophilia agents, hereditary angioedema products, Sephience/PKU, chronic spontaneous urticaria, and multiple rare-disease or specialty agents in February and November 2026 minutes.
- Program-level context matters: minutes mention the PBA system implementation, Most Favored Nation/GENEROUS model monitoring, and other state operations that can affect timing and implementation even after committee action.

## Updated pharma monitoring implications

- Prioritize meeting minutes and changes-only files over agendas when looking for rationale. Agendas flag timing and class scope; minutes and changes-only files reveal motions, extracted classes, criteria edits, and final operational language.
- Build evidence dossiers around the state-specific questions committees actually ask: labeled indication, requested action, comparative evidence, contrary evidence, differentiation, NNT or clinical magnitude, patient monitoring, prior therapy history, documentation burden, and renewal outcomes.
- For GLP-1, obesity, MASH, and diabetes-adjacent indications, expect budget/utilization scrutiny and criteria that combine labeled use, BMI/comorbidity cutoffs, lifestyle attestation, duplicate-therapy restrictions, and renewal response thresholds.
- For rare disease, oncology, specialty biologics, and accelerated-approval products, expect access to be tied to diagnosis precision, biomarker/genetic status, specialist involvement, prior therapy, toxicity monitoring, disease response, comparative evidence gaps, and possible future review after new evidence.
- For CNS and behavioral-health classes, watch both access protection and utilization controls. Wisconsin provides alternate continuity criteria for several CNS classes, while Tennessee and West Virginia show active review of antipsychotics, antidepressants/SNRIs, stimulants, and ADHD/narcolepsy-related classes.
- Manufacturer teams should calendar public-comment registration and material deadlines as separate milestones from meeting dates. Wyoming's seven-day material deadline and Wisconsin/Tennessee testimony rules are concrete examples.
- Treat committee votes as important but not final. TennCare can reject PAC modifications; Wisconsin sends recommendations to the Secretary; Wyoming sends recommendations and cost-analysis referrals to Medicaid Pharmacy Services/Department of Health.

## Explicit limitations

- This was not a broad crawl. It filled only capped-crawl seed gaps and bounded, obvious same-page West Virginia meeting documents.
- No `uncollected_seed_gap` rows remain in Group E, but 20 blocked/failed rows remain for non-capped reasons.
- Product and therapy mentions are reported only when present in extracted text. They are not claims of final coverage status unless the collected source explicitly states the outcome.
- West Virginia current meeting documents were collected, but three legacy DHHR URLs are obsolete/404.
- Texas direct PDL recommendation/decision PDFs remain unavailable due HTTP 404, and Vermont official DURB materials remain unavailable due HTTP 403.
