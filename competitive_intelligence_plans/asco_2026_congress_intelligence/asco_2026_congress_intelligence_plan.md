# ASCO 2026 Congress Intelligence Build Plan

Prepared: 2026-05-27

Primary workspace inputs:

- Local ASCO 2026 abstract dataset: `C:\Users\Justin\Desktop\linkedin-posts-mac\ASCO-2026-Abstracts`
- Target output folder: `C:\Users\Justin\Desktop\linkedin-posts-mac\competitive_intelligence_plans\asco_2026_congress_intelligence`

Primary public sources:

- Prezent Vivo and Nested Knowledge partnership announcement, PR Newswire: [https://www.prnewswire.com/news-releases/prezent-vivo-and-nested-knowledge-partner-to-bring-ai-powered-competitive-intelligence-to-life-sciences-teams-302782111.html](https://www.prnewswire.com/news-releases/prezent-vivo-and-nested-knowledge-partner-to-bring-ai-powered-competitive-intelligence-to-life-sciences-teams-302782111.html)
- Prezent version of the partnership announcement: [https://www.prezent.ai/news/prezent-vivo-nested-knowledge-partnership](https://www.prezent.ai/news/prezent-vivo-nested-knowledge-partnership)
- Prezent partnership explainer: [https://www.prezent.ai/blog/why-prezent-vivo-is-partnering-with-nested-knowledge](https://www.prezent.ai/blog/why-prezent-vivo-is-partnering-with-nested-knowledge)
- Prezent Vivo platform page: [https://www.prezent.ai/](https://www.prezent.ai/)
- Prezent Vivo launch announcement: [https://www.prezent.ai/prezent-vivo-launch-announcement](https://www.prezent.ai/prezent-vivo-launch-announcement)
- Prezent congress planning guide: [https://www.prezent.ai/blog/congress-planning](https://www.prezent.ai/blog/congress-planning)
- Nested Knowledge life sciences evidence synthesis page: [https://about.nested-knowledge.com/evidence-synthesis-for-life-sciences-organizations/](https://about.nested-knowledge.com/evidence-synthesis-for-life-sciences-organizations/)
- Nested Knowledge rapid-review-to-living-evidence post: [https://about.nested-knowledge.com/2026/04/15/from-rapid-review-to-living-evidence-synthesis/](https://about.nested-knowledge.com/2026/04/15/from-rapid-review-to-living-evidence-synthesis/)
- Nested Knowledge traceable insight post: [https://about.nested-knowledge.com/2026/04/10/from-evidence-to-insight-without-losing-the-trail/](https://about.nested-knowledge.com/2026/04/10/from-evidence-to-insight-without-losing-the-trail/)
- Nested Knowledge AutoLit documentation: [https://about.nested-knowledge.com/docs/autolit/](https://about.nested-knowledge.com/docs/autolit/)
- Nested Knowledge Synthesis documentation: [https://about.nested-knowledge.com/docs/synthesis/](https://about.nested-knowledge.com/docs/synthesis/)
- Nested Knowledge Dashboard documentation: [https://about.nested-knowledge.com/docs/dashboard/](https://about.nested-knowledge.com/docs/dashboard/)
- ASCO Annual Meeting abstract search source used by the local manifest: [https://www.asco.org/annual-meeting/search?filters=%7B%22mediaTypes%22:%5B%22Abstracts%22%5D%7D&userInput=&sortBy=Relevancy&contentKey=ANNUAL_MEETING&contentKeyYear=2026](https://www.asco.org/annual-meeting/search?filters=%7B%22mediaTypes%22:%5B%22Abstracts%22%5D%7D&userInput=&sortBy=Relevancy&contentKey=ANNUAL_MEETING&contentKeyYear=2026)

Note: the final ASCO source URL above should use the local manifest value as the operational source of truth. If reusing the URL manually, preserve the `mediaTypes=["Abstracts"]`, `contentKey=ANNUAL_MEETING`, and `contentKeyYear=2026` parameters from `manifest.json`.

## Executive Intent

Build an ASCO 2026 congress intelligence system that converts the local ASCO abstract corpus into source-backed, role-specific competitive intelligence deliverables before, during, and after the meeting. The workflow should match the operating model described in the Prezent Vivo and Nested Knowledge partnership: rigorous evidence synthesis, rapid AI-assisted processing, human validation, and communication outputs that teams can use directly for decisions and execution [PR Newswire](https://www.prnewswire.com/news-releases/prezent-vivo-and-nested-knowledge-partner-to-bring-ai-powered-competitive-intelligence-to-life-sciences-teams-302782111.html).

The ASCO dataset is already large enough to support a production-style pilot:

- `download_manifest.json` and `manifest.json` report 7,295 ASCO 2026 abstract records.
- Local folders contain 7,295 JSON files and 7,295 HTML files.
- `asco_2026_abstracts.jsonl` contains 7,295 records with full abstract body text.
- `abstracts_index.csv` provides a lightweight index with `uid`, `contentId`, `abstractNumber`, `title`, `primaryPerson`, `meetingName`, `meetingYear`, `url`, and `summary`.
- Every sampled record includes full `body` content; 1,709 records include HTML tables; 3,844 records have summary text; 60 abstract numbers start with `LBA`.
- The manifest track distribution shows broad oncology coverage, including large counts in gastrointestinal cancer, health services research, care delivery, NSCLC metastatic disease, colorectal and anal cancer, breast cancer, symptom science, developmental therapeutics, genitourinary cancer, gynecologic cancer, hematologic malignancies, melanoma, CNS tumors, sarcoma, and pediatric oncology.

The build should not try to replace expert interpretation. It should accelerate evidence finding, extraction, synthesis, prioritization, and deck generation while preserving a visible source chain and human review. That framing is consistent with Prezent Vivo's stated AI plus human expertise model for life sciences communications [Prezent Vivo](https://www.prezent.ai/) and Nested Knowledge's emphasis on traceable AI, human oversight, audit trails, and evidence synthesis outputs [Nested Knowledge AutoLit](https://about.nested-knowledge.com/docs/autolit/).

Related website review found three directly relevant themes beyond the PR Newswire release: Prezent's partnership explainer frames the offering as converting evidence-review outputs into usable team deliverables [Prezent partnership explainer](https://www.prezent.ai/blog/why-prezent-vivo-is-partnering-with-nested-knowledge); Prezent's congress planning guide treats competitive intelligence as part of a coordinated pre-, during-, and post-congress communication program [Prezent congress planning](https://www.prezent.ai/blog/congress-planning); and Nested Knowledge's living-evidence and traceable-insight posts emphasize versioned evidence refreshes, audit trails, and claim-to-source traceability [Nested Knowledge living evidence](https://about.nested-knowledge.com/2026/04/15/from-rapid-review-to-living-evidence-synthesis/) [Nested Knowledge traceable insight](https://about.nested-knowledge.com/2026/04/10/from-evidence-to-insight-without-losing-the-trail/).

## Source Claim to Workflow Mapping

| Source claim | Practical ASCO workflow implication | Implementation requirement |
|---|---|---|
| The partnership promises congress intelligence packages before major meetings, with competitor data, emerging science, and KOL positioning [PR Newswire](https://www.prnewswire.com/news-releases/prezent-vivo-and-nested-knowledge-partner-to-bring-ai-powered-competitive-intelligence-to-life-sciences-teams-302782111.html). | Generate pre-congress dossiers from ASCO abstracts by tumor type, sponsor, asset, mechanism, biomarker, line of therapy, endpoint, session type, and investigator. | Build prioritized pre-meeting packages from `asco_2026_abstracts.jsonl`, `abstracts_index.csv`, and the per-record JSON/HTML files. |
| The announcement describes on-site synthesis packages that translate newly presented data into actionable implications for commercial, medical, and market access teams [PR Newswire](https://www.prnewswire.com/news-releases/prezent-vivo-and-nested-knowledge-partner-to-bring-ai-powered-competitive-intelligence-to-life-sciences-teams-302782111.html). | During May 29 to June 2, operate a daily update cycle that flags newly relevant sessions, slide/poster availability if added, competitor press releases, and changes in interpretation. | Add session watchlists, daily run logs, analyst signoff, and "what changed since yesterday" outputs. |
| The partnership includes monthly living evidence updates throughout the year [Prezent announcement](https://www.prezent.ai/news/prezent-vivo-nested-knowledge-partnership), and Nested Knowledge describes living synthesis as a way to keep rapid-review evidence current when landscapes change [Nested Knowledge living evidence](https://about.nested-knowledge.com/2026/04/15/from-rapid-review-to-living-evidence-synthesis/). | Convert ASCO findings into standing topic nests or evidence workspaces that refresh with publications, registry changes, labels, guidelines, HTA actions, and company disclosures. | Create monthly refresh jobs by topic with source deltas, evidence tables, and a living claim register. |
| Nested Knowledge describes AutoLit for search, screening, extraction, critical appraisal, and Synthesis for visualizing and sharing outputs [Nested Knowledge life sciences](https://about.nested-knowledge.com/evidence-synthesis-for-life-sciences-organizations/). | Treat ASCO abstracts as seed records for evidence synthesis rather than final evidence alone. Link each priority abstract to trials, publications, labels, guidelines, and RWE sources. | Store source lineage and extraction status for each finding; export structured evidence to dashboards and decks. |
| Nested Knowledge states that Synthesis can provide qualitative, quantitative, PRISMA, critical appraisal, manuscript, and dashboard outputs [Synthesis docs](https://about.nested-knowledge.com/docs/synthesis/). | For each priority topic, produce a source-backed dashboard plus a concise narrative with methods, included records, excluded records, and analyst interpretation. | Define dashboard cards for landscape maps, endpoint tables, evidence hierarchy, competitor matrix, and implication tracker. |
| Nested Knowledge Dashboard supports customizable cards, tables, PRISMA cards, study cards, tag cards, and Smart Insights [Dashboard docs](https://about.nested-knowledge.com/docs/dashboard/). | Use dashboard cards as the evidence layer behind team-specific decks. | Create reusable dashboard templates for Medical Affairs, HEOR, Market Access, Commercial, and Launch. |
| Prezent Vivo positions itself as an AI and expert communications partner for life sciences outputs including presentations, posters, MSL materials, leadership updates, and launch readiness reviews [Prezent Vivo launch](https://www.prezent.ai/prezent-vivo-launch-announcement), and its partnership explainer describes using Nested Knowledge outputs as inputs for synthesized narratives and expert-reviewed deliverables [Prezent partnership explainer](https://www.prezent.ai/blog/why-prezent-vivo-is-partnering-with-nested-knowledge). | Convert the same validated evidence core into different narrative and deck formats without rebuilding the evidence review each time. | Separate evidence objects from communication objects, with role-specific templates consuming the same approved claim register. |
| Prezent Vivo emphasizes brand-compliant, scientifically precise, compliant communications and enterprise workflows [Prezent Vivo](https://www.prezent.ai/). | Build MLR-ready outputs with citation footnotes, source excerpts, fair-balance checks, claim labels, and reviewer status. | Require source citations, claim classification, confidence ratings, and human validation before any external-facing reuse. |

## Operating Model

The ASCO intelligence build should run as four connected workstreams:

1. Evidence ingestion and normalization
2. Competitive interpretation and prioritization
3. Living evidence management
4. Communication packaging and role-specific delivery

The core design principle is "one evidence core, many communication surfaces." ASCO abstracts, enriched source records, extracted endpoints, and analyst judgments should be stored once, then reused across congress packages, on-site updates, monthly updates, deep dives, and team-specific decks.

## ASCO Dataset Use Cases

### 1. Congress Intelligence Packages

Purpose: prepare teams before the first relevant session begins.

Inputs:

- Full ASCO abstract corpus from `asco_2026_abstracts.jsonl`
- Per-record JSON and HTML files for full abstract body and tables
- `abstracts_index.csv` for fast browsing and linking
- `manifest.json` for ASCO source metadata, track counts, session type counts, and download provenance
- External sources for validation: ClinicalTrials.gov, company press releases, investor decks, labels, guideline pages, PubMed, and HTA sources

Outputs:

- Topline congress brief by therapeutic area
- Priority abstract watchlist
- Competitor asset matrix
- Mechanism and biomarker heatmap
- Endpoint and study design table
- KOL and institution map based on first speaker, author string if available, sponsor, trial group, and session prominence
- "Implication by function" pages for Medical Affairs, HEOR, Market Access, Commercial, and Launch
- Source appendix with ASCO URL, local record ID, source enrichment links, and review status

Build logic:

- Prioritize Plenary, Oral Abstract, Rapid Oral Abstract, Clinical Science Symposium, late-breaking abstract numbers, and strategically important poster records.
- Increase priority when records contain pivotal phase 2/3 language, randomized design, survival endpoints, registrational intent, direct comparator, new safety signal, biomarker-defined population, quality-of-life outcome, economic outcome, or practice-changing language.
- Reduce priority when records are small retrospective case series, purely descriptive, off-strategy, or not tied to active competitor questions.
- Keep all records searchable even if not promoted into the primary package.

### 2. On-Site Synthesis Updates

Purpose: support rapid interpretation while ASCO is underway.

Cadence:

- Morning: "today's sessions and risk areas" note.
- Midday: quick scan of newly available materials, company releases, and priority sessions.
- Evening: "what changed today" synthesis with decision implications.
- Final day: cross-congress takeaways and unresolved watch items.

Outputs:

- Daily change log
- One-page signal cards for new or materially changed findings
- Function-specific daily email/slack-ready summaries
- Deck inserts for leadership or field-team updates
- "Needs expert review" queue for ambiguous claims, immature data, or likely promotional sensitivity

On-site synthesis should not rely only on abstract text. It should track whether slides, posters, presentation recordings, corporate releases, or journal publications appear after the abstract release. The local ASCO records currently show `hasPosters=false`, `hasSlides=false`, and `hasVideos=false` across the downloaded records; the pipeline should re-check these flags and source URLs during the meeting.

### 3. Monthly Living Evidence Updates

Purpose: extend ASCO intelligence beyond the congress window.

Monthly update scope:

- ASCO abstract-to-publication status
- ClinicalTrials.gov status, enrollment, endpoint, site, sponsor, and completion date changes
- New PubMed publications and preprints
- FDA, EMA, and other regulator updates
- NCCN, ASCO, ESMO, and other guideline updates
- HTA and payer signals where relevant
- Company pipeline, earnings, and investor-deck changes
- New congress abstracts from ESMO, EHA, WCLC, SITC, ASH, SABCS, AACR, and tumor-specific meetings

Deliverables:

- Monthly evidence delta memo
- Updated evidence table and claim register
- Dashboard refresh
- Team-specific "what changed and why it matters" pages
- Backlog of deep-dive questions created by stakeholders

Nested Knowledge's living evidence library concept supports this use case because it positions the evidence workspace as editable, refreshable, and shareable throughout the product lifecycle [Nested Knowledge life sciences](https://about.nested-knowledge.com/evidence-synthesis-for-life-sciences-organizations/).

### 4. On-Demand Deep Dives

Purpose: answer reactive questions quickly without losing rigor.

Example triggers:

- Competitor reports unexpected OS, PFS, ORR, duration-of-response, MRD, pCR, EFS, QoL, safety, discontinuation, or subgroup signal.
- A new mechanism, combination, or biomarker appears across multiple abstracts.
- A payer-relevant endpoint appears in a competitor abstract.
- A late-breaking abstract changes a launch assumption.
- Field teams request approved, source-backed answers for recurring customer questions.

Deep-dive workflow:

1. Frame the question, decision owner, due date, and acceptable evidence standard.
2. Pull ASCO records by asset, sponsor, target, tumor, biomarker, endpoint, line, and setting.
3. Enrich with trial registry, publications, labels, company materials, and prior congresses.
4. Extract data into a standard evidence table.
5. Grade confidence and identify caveats.
6. Produce a short answer, a slide-ready summary, and a source appendix.
7. Add validated findings to the living claim register for reuse.

## Team-Specific Versions

### Medical Affairs

Primary questions:

- Which data may change scientific exchange priorities?
- Which investigators, institutions, or cooperative groups are shaping the evidence?
- Which endpoints, subgroups, biomarkers, and safety considerations require MSL preparation?
- Which claims are mature enough for reactive scientific exchange, and which require caution?

Deliverables:

- MSL-ready scientific narrative
- KOL and institution map
- Unmet-need and mechanism summary
- Evidence caveat table
- FAQ with approved source references
- Advisory board pre-read or post-ASCO synthesis

ASCO-specific build notes:

- Capture `primaryPerson.displayName`, abstract title, abstract number, meeting URL, session type, track, and any author/sponsor fields available in the JSON or body.
- Flag hypothesis-generating data separately from registrational or practice-changing evidence.
- Include a "do not overstate" section for cross-trial comparisons, immature follow-up, subgroup uncertainty, and indirect comparisons.

### HEOR

Primary questions:

- Which abstracts include patient-reported outcomes, health-related quality of life, resource use, costs, hospitalization, treatment burden, equity, adherence, real-world effectiveness, or value frameworks?
- Which data may support future SLRs, NMAs, cost-effectiveness models, budget impact models, or indirect treatment comparisons?
- Which endpoints are HTA-relevant but not yet mature?

Deliverables:

- HEOR evidence table
- PRO and QoL endpoint tracker
- Real-world evidence tracker
- HTA-relevance memo
- Evidence-gap matrix by indication and comparator
- Monthly update feed for future SLR/NMA maintenance

ASCO-specific build notes:

- Prioritize abstracts in Quality Care/Health Services Research, Care Delivery/Models of Care, Symptom Science and Palliative Care, and Market Access-relevant tumor tracks.
- Extract endpoint definitions, time horizons, instruments, comparator arms, missing data issues, and analysis populations.
- Mark whether evidence is suitable for model input, background burden, scenario analysis, or only hypothesis generation.

### Market Access

Primary questions:

- Which ASCO findings may change payer perception of clinical value, differentiation, unmet need, safety, administration burden, or sequencing?
- Which competitor data may affect formulary strategy, value dossiers, HTA submissions, or payer objection handling?
- Where do data support or weaken claims on durability, tolerability, convenience, biomarker targeting, QoL, resource use, or total cost of care?

Deliverables:

- Payer implication brief
- Value message evidence grid
- Competitor differentiation table
- HTA and reimbursement watchlist
- Payer objection and evidence response matrix

ASCO-specific build notes:

- Translate clinical findings into payer-relevant dimensions without making unsupported economic claims.
- Label evidence as direct ASCO evidence, inferred implication, or external validation needed.
- Link ASCO findings to current labels, guidelines, and reimbursement assumptions before recommending message changes.

### Commercial

Primary questions:

- Which competitor data may affect positioning, share expectations, messaging, segmentation, field training, or brand planning?
- Which claims can competitors credibly make after ASCO?
- Which emerging mechanisms or regimens may shift the market map?

Deliverables:

- Competitive threat and opportunity brief
- Asset-by-asset battlecard
- Message risk tracker
- Field training slide inserts
- Leadership summary with action recommendations

ASCO-specific build notes:

- Keep commercial implications separate from medical claims.
- Classify findings by potential business impact, evidence strength, time to impact, and likely competitor amplification.
- Monitor company press releases and investor materials as secondary signals that require validation against ASCO abstracts and primary evidence.

### Launch Teams

Primary questions:

- Which ASCO data affect launch readiness assumptions, target product profile, competitive positioning, evidence-generation needs, and objection handling?
- Which gaps should be addressed in publication plans, medical education, access strategy, or field readiness?
- Which competitor events could change launch timing or message hierarchy?

Deliverables:

- Launch readiness evidence update
- Competitive scenario planner
- Evidence-gap backlog
- Cross-functional action tracker
- Launch message validation pack

ASCO-specific build notes:

- Tie each finding to launch workstreams: evidence generation, medical strategy, market access, commercial training, publication planning, regulatory, and analytics.
- Maintain a dated assumption register so changes after ASCO can be traced to specific abstracts, publications, or regulatory events.

## Data Architecture

### Raw Layer

Store immutable source files:

- `manifest.json`: ASCO source URL, endpoint, operation name, pagination, filters, reported totals, and track/session distributions.
- `download_manifest.json`: downloader metadata, expected/downloaded totals, source page, local directory names, and API endpoint.
- `asco_2026_abstracts.jsonl`: canonical raw JSONL feed.
- `abstracts.jsonl`: alternate JSONL export.
- `abstracts_index.csv`: lightweight browsing index.
- `abstracts_json/*.json`: one JSON object per abstract.
- `abstracts_html/*.html`: one HTML source per abstract.

Raw files should be read-only after ingestion. Any corrections, encoding fixes, entity normalization, or extraction results should be stored in curated tables with source pointers back to raw records.

### Curated Evidence Layer

Recommended tables:

- `abstract_fact`: one row per ASCO abstract with `uid`, `contentId`, `presentationId`, `abstractNumber`, `title`, `meetingYear`, `meetingName`, `url`, `localJsonPath`, `localHtmlPath`, `sessionType`, `track`, `publishDate`, `lastUpdated`, `primaryPerson`, and `sourceHash`.
- `abstract_text_section`: extracted Background, Methods, Results, Conclusions, table footer, and unclassified body text.
- `abstract_table`: parsed HTML tables with row/column structure, source abstract, table number, and extraction confidence.
- `topic_tag`: tumor type, disease setting, biomarker, mechanism, modality, line of therapy, study phase, endpoint, population, geography, and evidence type.
- `asset_company`: product names, generic names, sponsor/company, comparator, combination partners, class, and approval status where available.
- `trial_link`: NCT IDs, registry URLs, phase, enrollment, status, primary completion, sponsor, arms, endpoints, and ASCO abstract IDs.
- `evidence_claim`: atomic claims with claim text, source record, evidence type, directionality, magnitude, caveats, confidence, and approval status.
- `priority_signal`: score, rationale, audience relevance, team owner, and recommended action.
- `source_log`: all external URLs searched or cited, access date, source type, and validation status.
- `review_status`: AI extraction status, analyst review status, medical/legal/regulatory status if applicable, and release status.
- `deliverable_registry`: package name, audience, version, source records used, reviewer, delivery date, and next refresh date.

### Evidence Synthesis Layer

For each priority topic or franchise:

- Create a "nest" or equivalent workspace seeded with ASCO abstract records.
- Add PubMed, ClinicalTrials.gov, labels, prior congresses, guidelines, and HTA records as external sources.
- Use a stable PICO or PICOTS frame when the question is comparative.
- Maintain an inclusion/exclusion log for records promoted into a formal evidence table.
- Use structured tags aligned to the curated evidence schema.
- Export dashboard-ready tables and citation metadata.

Nested Knowledge's described AutoLit workflow supports search, screening, tagging, extraction, and critical appraisal [AutoLit docs](https://about.nested-knowledge.com/docs/autolit/). Its Synthesis outputs can then provide interactive qualitative and quantitative views, dashboards, PRISMA visuals, and manuscript-style outputs [Synthesis docs](https://about.nested-knowledge.com/docs/synthesis/).

### Communication Layer

Prezent Vivo or a comparable communication layer should consume only reviewed evidence objects and approved claim text. It should produce:

- Executive PowerPoint decks
- Role-specific slide modules
- Congress update memos
- Field-ready FAQs
- Deep-dive summaries
- Leadership readouts
- Monthly living-evidence update decks
- Source appendices

Prezent Vivo's public materials describe purpose-built life sciences communications, AI-assisted generation, brand-compliant outputs, human expert support, and deliverables across presentations, posters, documents, MSL training, and launch readiness [Prezent Vivo](https://www.prezent.ai/) [Prezent Vivo launch](https://www.prezent.ai/prezent-vivo-launch-announcement). The implementation should mirror those claims by keeping evidence provenance and reviewer controls visible in the delivery workflow.

## Processing Pipeline

### Step 1: Inventory and Checksum

Actions:

- Count JSON, HTML, and JSONL records.
- Compare counts to `manifest.json` and `download_manifest.json`.
- Generate hashes for `asco_2026_abstracts.jsonl`, `abstracts_index.csv`, and each per-record source file.
- Record the ASCO source URL and download timestamp from the manifest.

Acceptance criteria:

- 7,295 records reconcile across manifest, JSONL, JSON files, and HTML files.
- Every abstract in `abstracts_index.csv` maps to a JSON file and ASCO URL.
- Any missing source file is logged before analysis begins.

### Step 2: Normalize Text and Metadata

Actions:

- Parse JSON body fields with a real HTML parser.
- Extract section labels: Background, Methods, Results, Conclusions, and table footers.
- Convert HTML entities and repair mojibake where needed.
- Normalize abstract numbers, including `LBA`, `e`, and numeric formats.
- Normalize meeting URLs to `https://www.asco.org/abstracts-presentations/{contentId}` or the corresponding ASCO path in the record.
- Normalize speaker names and roles.

Acceptance criteria:

- Each abstract has clean plain text and sectioned text.
- Tables are preserved as structured rows and columns, not flattened into unreadable text.
- Source pointers remain attached at field level.

### Step 3: Classify Topics and Entities

Actions:

- Tag tumor type, track, disease setting, line of therapy, phase, modality, mechanism, biomarker, endpoint, geography, population, and evidence type.
- Extract asset names, generic names, trial acronyms, sponsor names, comparator names, and NCT IDs.
- Identify KOLs and institutions from available author/speaker fields and source enrichment.
- Flag HEOR, QoL, RWE, equity, adherence, burden, cost, and access-relevant records.

Acceptance criteria:

- Each priority abstract has human-reviewed tags for the fields used in deliverables.
- Entity extraction is conservative: uncertain asset, sponsor, or trial matches are marked "needs validation."
- Search aliases are retained for products and mechanisms.

### Step 4: Score Competitive Priority

Suggested score dimensions:

- Session prominence: Plenary, Oral Abstract, Rapid Oral, Clinical Science Symposium, Poster, Publication Only.
- Evidence maturity: randomized phase 3, phase 2 signal, early phase, retrospective, modeling, survey, case series.
- Business relevance: direct competitor, adjacent class, launch assumption, strategic indication, major KOL, payer-sensitive endpoint.
- Endpoint significance: OS, PFS, EFS, pCR, ORR, DoR, MRD, safety, QoL, costs, treatment burden, subgroup effect.
- Novelty: new asset, new mechanism, new combination, new biomarker, new line, first readout, long-term follow-up.
- Actionability: requires field training, MSL update, payer narrative change, leadership escalation, deep dive, or monthly watch.

Acceptance criteria:

- Every package-level record has a visible score and analyst rationale.
- Scores can be filtered by team relevance, not only overall priority.
- Low-confidence model scores cannot auto-promote a finding without analyst review.

### Step 5: Enrich With External Sources

Minimum enrichment sources:

- ASCO abstract URL from the local record.
- ClinicalTrials.gov record where trial identifiers can be found.
- Sponsor press release and investor materials if the company publicizes the data.
- PubMed or journal publication if available.
- FDA/EMA label and approval history for approved products.
- Guideline pages when findings may affect standard of care.
- HTA or payer sources when Market Access or HEOR questions are in scope.

Acceptance criteria:

- Company claims are treated as leads until reconciled against ASCO, registries, labels, or publications.
- Each evidence claim has at least one primary or authoritative source.
- External source logs include URL, source type, date accessed, and extraction owner.

### Step 6: Build Evidence Claims

Actions:

- Convert abstract findings into atomic claims.
- Attach data values, populations, comparators, limitations, and source links.
- Label claims as descriptive, comparative, safety, efficacy, PRO/QoL, economic, burden, mechanistic, operational, or strategic implication.
- Separate "source says" from "analyst interpretation."

Acceptance criteria:

- No unsupported claim appears in a deliverable.
- Every inference is labeled as an inference.
- Cross-trial comparisons are marked as indirect unless based on a valid comparative analysis.

### Step 7: Package for Audiences

Actions:

- Generate common evidence module.
- Generate role-specific modules for Medical Affairs, HEOR, Market Access, Commercial, and Launch.
- Produce congress, daily update, monthly update, and deep-dive templates.
- Include source appendix, review status, and confidence labels.

Acceptance criteria:

- Each audience version answers that team's decisions, not just rephrased general content.
- Claims are consistent across audiences.
- Role-specific recommendations are traceable to the same evidence objects.

## QA and Compliance Controls

### Source Integrity

- Preserve raw ASCO files unchanged.
- Use checksums for raw data and generated extracts.
- Store source URL, local path, content ID, abstract number, and access/download date with every extracted finding.
- Maintain a source hierarchy: public abstract and registry evidence over company summaries; labels and guidelines over promotional interpretation; peer-reviewed publications over press releases when available.

### Extraction QA

- Run automated completeness checks for title, abstract number, URL, body text, speaker, meeting year, and section extraction.
- Manually review all high-priority records and all claims promoted to deliverables.
- Double-review records used for Medical Affairs, Market Access, HEOR, or Commercial claims.
- Reconcile HTML tables against parsed tables for high-priority abstracts.
- Track extraction confidence and reviewer initials.

### Medical, Legal, Regulatory, and Promotional Controls

- Separate scientific evidence from commercial implication.
- Label off-label, investigational, not-yet-approved, and non-comparative findings.
- Avoid efficacy or safety superiority claims unless directly supported.
- Include limitations for immature data, small sample sizes, retrospective designs, incomplete follow-up, and subgroup analyses.
- Require review before field-facing, external, or promotional reuse.
- Include fair-balance prompts where safety and benefit claims appear together.
- Do not copy ASCO abstract text into deliverables beyond short, attributed snippets if needed; paraphrase and cite instead.

### AI Governance

- Use AI for extraction assistance, clustering, summarization, draft generation, and signal detection.
- Require human signoff for entity matching, evidence claims, implication statements, and final deliverables.
- Store prompts, model outputs, reviewer edits, and release status for auditability.
- Prefer retrieval-grounded generation against approved evidence tables.
- Block generation from unreviewed raw text for final field-facing content.

Nested Knowledge's documentation emphasizes traceability, validation, human oversight, and audit trails for AI-supported evidence synthesis [AutoLit docs](https://about.nested-knowledge.com/docs/autolit/). Those principles should be copied into the ASCO operating SOP.

## Deliverables

### Package 1: Pre-Congress Intelligence Package

Timing: immediately, using the downloaded ASCO corpus.

Contents:

- Executive overview by tumor area.
- Top 25 to 50 abstracts by strategic importance.
- Competitor and asset matrix.
- Mechanism, biomarker, and endpoint heatmaps.
- Session watchlist for May 29 to June 2.
- Team-specific implication pages.
- Source appendix and review log.

### Package 2: On-Site Daily Synthesis

Timing: May 29 to June 2, 2026.

Contents:

- Daily "what changed" page.
- New evidence and changed interpretation tracker.
- Company communication scan.
- Priority session notes.
- Team-specific action items.
- Carry-forward unresolved questions.

### Package 3: Post-Congress Readout

Timing: within 3 business days after the meeting.

Contents:

- Cross-congress strategic synthesis.
- Final prioritized signal list.
- Competitor positioning changes.
- Evidence strength and caveat matrix.
- Action tracker by function.
- Recommendations for monthly living evidence topics.

### Package 4: Monthly Living Evidence Update

Timing: monthly after ASCO.

Contents:

- Source delta since prior month.
- New publications, trial registry changes, regulatory changes, guideline changes, HTA/access signals, and company updates.
- Updated claim register.
- Evidence gap closure or new gap creation.
- Recommended stakeholder actions.

### Package 5: On-Demand Deep Dive

Timing: 24 to 72 hours depending on complexity and review requirements.

Contents:

- Decision question.
- Evidence table.
- Short answer.
- Confidence and caveats.
- Recommended action.
- Source appendix.
- Reusable slide module.

## Timeline

### Day 0: 2026-05-27

- Freeze raw ASCO dataset and generate checksums.
- Build normalized abstract table and sectioned text extraction.
- Build initial topic/entity tags.
- Produce first priority scoring run.
- Create pre-congress package outline and source appendix structure.

### Day 1: 2026-05-28

- Complete high-priority abstract review.
- Enrich top records with ClinicalTrials.gov, company, publication, label, and guideline sources.
- Draft pre-congress intelligence package.
- Create team-specific versions.
- Run QA on all claims and source links.

### ASCO Days: 2026-05-29 to 2026-06-02

- Run daily source refresh.
- Monitor ASCO URLs for changes to poster, slide, and video flags.
- Monitor company and journal releases linked to priority abstracts.
- Publish morning watchlist and evening synthesis.
- Escalate urgent high-impact findings to the relevant team owners.

### Post-Congress Week: 2026-06-03 to 2026-06-10

- Produce final congress readout.
- Lock reviewed claim register v1.
- Select topics for monthly living evidence monitoring.
- Convert high-value findings into reusable deck modules, FAQs, and evidence tables.
- Archive meeting-specific daily logs.

### Monthly: July 2026 Forward

- Refresh literature, registry, label, guideline, HTA, and company sources.
- Update dashboards and claims.
- Publish monthly delta memo.
- Trigger deep dives when new data materially changes the evidence picture.

## Next Build Steps

1. Create `data_dictionary.md` for the ASCO normalized schema.
2. Create extraction scripts for JSONL inventory, HTML section parsing, table parsing, and source hashing.
3. Create `priority_scoring_config.yml` with adjustable weights by audience.
4. Create `source_enrichment_queue.csv` for top-priority records.
5. Create a claim register template with source, evidence type, confidence, caveat, review status, and audience reuse fields.
6. Create role-specific deliverable templates:
   - `medical_affairs_asco_update.md`
   - `heor_asco_update.md`
   - `market_access_asco_update.md`
   - `commercial_asco_update.md`
   - `launch_asco_update.md`
7. Create a dashboard specification aligned to Nested Knowledge Synthesis and Dashboard concepts:
   - Evidence map
   - Endpoint table
   - Competitor matrix
   - KOL map
   - Claim register
   - Source delta timeline
8. Create a QA checklist:
   - Raw source reconciliation
   - Entity validation
   - Claim support
   - Team-specific risk review
   - MLR/compliance readiness
9. Pilot one tumor area and one cross-tumor theme before scaling across the full 7,295-record corpus.
10. Maintain reusable congress-abstract and living-evidence production guidance in the `cohere-style-ci` skill so future CI runs preserve evidence provenance, separate synthesis from communications, and support congress packages, on-site synthesis, monthly updates, deep dives, and team-specific outputs.

## Pilot Recommendation

Start with two pilots:

- Tumor-specific pilot: NSCLC, because the manifest shows large ASCO coverage across metastatic NSCLC and local-regional/small-cell/other thoracic cancer tracks.
- Cross-functional pilot: HEOR and Market Access evidence signals, because the manifest includes high counts in Quality Care/Health Services Research, Care Delivery/Models of Care, Symptom Science and Palliative Care, and several records likely relevant to patient burden, costs, real-world outcomes, and value evidence.

Pilot success criteria:

- 100 priority abstracts reviewed.
- 25 evidence claims fully source-backed and reviewer-approved.
- 5 role-specific mini-decks or memos generated from the same claim register.
- 1 living evidence dashboard specification completed.
- 1 daily on-site update produced using the same pipeline.
- All outputs include source links, caveats, confidence labels, and review status.

## Open Implementation Decisions

- Whether to use Nested Knowledge directly, an internal evidence database, or both.
- Which therapeutic areas should receive full packages versus watchlist-only coverage.
- Which company/asset taxonomy should be treated as the source of truth.
- Whether field-facing outputs require MLR review before distribution.
- Which external sources are in scope for monthly updates by geography.
- Whether team-specific decks should be generated in PowerPoint, markdown, HTML, or all three.
- Whether ASCO copyrighted content restrictions require additional controls for internal redistribution of abstract text, tables, or figures.

## Practical Definition of Done

The ASCO congress intelligence system is ready for production when:

- The ASCO corpus is normalized, searchable, tagged, and source-linked.
- Priority scoring can generate ranked abstract lists by team.
- Evidence claims are reusable across deliverables.
- Every claim in a package links back to ASCO and any enrichment sources.
- Human review status is visible.
- Daily updates can be generated in less than two hours.
- Monthly refreshes can identify source deltas without redoing the full review.
- Medical Affairs, HEOR, Market Access, Commercial, and Launch each receive outputs tailored to their decisions.
- The workflow demonstrates the partnership model: rapid evidence synthesis plus expert-reviewed, audience-ready life sciences communications [PR Newswire](https://www.prnewswire.com/news-releases/prezent-vivo-and-nested-knowledge-partner-to-bring-ai-powered-competitive-intelligence-to-life-sciences-teams-302782111.html).
