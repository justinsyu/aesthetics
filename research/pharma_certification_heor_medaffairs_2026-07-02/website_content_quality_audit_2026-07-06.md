# BCMAEP Website Content Quality Audit

Prepared: 2026-07-06  
Scope: `BCMAEP_certification_course/website/`  
Constraint: read-only review of existing website files. This report is the only new file created.

## Executive Assessment

The website is unusually complete for a version 1.0 certification-course concept. It has a coherent information architecture, consistent navigation, a full 15-module curriculum, clear applied activities, capstone rubrics, a source register, an AI-use policy, and repeated disclosures that the credential is not accredited or psychometrically validated. The content is relevant to medical affairs, HEOR, market access, evidence generation, and AI governance, and the strongest material is in the HEOR, HTA, RWE, integrated evidence planning, and AI-governance modules.

The main quality risk is credibility calibration. The site is explicit in several places that the program has not undergone job-task-analysis validation, item-bank piloting, formal standard setting, or accreditation review, but the branding and some outcome language still read as if the credential already exists and already validates job readiness. That tension should be resolved before public use.

The second risk is source precision. The site makes broad claims that every sourced teaching claim is backed by verified authoritative sources and that the source register is the consolidated citation pool. The local review found strong citation density and no missing internal links, but also found currentness gaps, absent sources in the source register, one encoding defect, and several visually collapsed key-reading citations.

## Review Method

- Inspected the generated static site in `BCMAEP_certification_course/website/` and the underlying source material in `BCMAEP_certification_course/`.
- Used two read-only subagents: one for narrative quality and coherence, and one for factual/source-support review.
- Ran a local link and anchor check across 25 HTML pages. Result: 2,132 local/external link or source references inspected, 0 missing local files or anchors.
- Reviewed local source files including `references/source_register.md`, `governance/accreditation_and_quality_alignment.md`, `assessment/exam_blueprint_and_sample_items.md`, `market_alignment/job_description_links.md`, and representative modules.
- Performed targeted live verification for the FDA AI-guidance landscape because the relevant guidance is time-sensitive. FDA's AI drug-development hub is current as of 2026-05-01 and lists January 2026 guiding principles in addition to the January 2025 draft guidance.

## Major Strengths

1. **The site is structurally complete.** It includes a homepage, handbook, curriculum, assessment blueprint, capstone, case library, AI policy, accreditation page, market-alignment analysis, source register, and 15 module pages. This is closer to a full course prototype than a marketing site.

2. **The accreditation caveat is visible and repeated.** The homepage, accreditation page, and footer all state that the program is not yet accredited and has not completed validation, piloting, standard setting, or accreditation review. This is an important integrity feature.

3. **The curriculum scope is relevant.** The module sequence covers the major role families named by the site: medical affairs, MSL/field medical, medical information, publications, HEOR, RWE, HTA, market access, integrated evidence planning, and AI governance.

4. **The applied-work emphasis is credible.** The portfolio model and repeated deliverables make the course more practical than a pure reading curriculum. The best examples are the integrated evidence generation plan, HTA/payer outline, KOL engagement plan, medical information response, and AI-use audit log.

5. **The HEOR and AI material is differentiated.** Modules 7 to 10 and 14 are more developed than a generic medical-affairs overview. The site correctly treats AI governance as a workflow-control problem rather than as prompt-writing instruction.

6. **Internal navigation is technically sound.** The local check found no missing local targets or fragment anchors across the generated HTML site.

## Critical Findings

### 1. Credential status is over-presented as current

Severity: High  
Evidence: `website/index.html`, `website/handbook.html`, `website/accreditation.html`

The site repeatedly uses current-state credential language such as "Board Certified Medical Affairs and Evidence Professional," "Credential awarded," "BCMAEP holder," and "credential recognizes demonstrated competency." This conflicts with the site's own disclosure that the program is a version 1.0 design without job-task-analysis validation, item-bank piloting, formal standard setting, or accreditation review.

Recommendation: Replace top-level claims with calibrated language such as "proposed credential," "certification design," "candidate credential design," or "curriculum and assessment prototype" until there is a sponsoring body and validation record. The program name can remain, but pages should make clear that it is a proposed credential rather than an awarded one.

### 2. Readiness and certification-outcome claims exceed the evidence base

Severity: High  
Evidence: `website/index.html`, `website/capstone.html`, `website/modules/module-10.html`

The site says or implies that successful candidates are ready for first industry roles and that the program can certify ability to do the work. That is stronger than the available evidence supports. A blueprint, sample items, and rubrics can describe intended assessment, but they do not establish that the assessment validly predicts role performance.

Recommendation: Recast these statements as intent, not validated outcome. For example: "designed to assess applied readiness," "intended to support first-role preparation," or "aims to evaluate work-product capability." Avoid "holder can" claims until the exam, portfolio scoring, and job-task analysis have been externally validated.

### 3. "Accreditation-ready" is too strong without external validation

Severity: High to Medium  
Evidence: `website/index.html`, `website/accreditation.html`, `BCMAEP_certification_course/governance/accreditation_and_quality_alignment.md`

The site is careful to state that the program is not accredited, but "accreditation-ready" may still imply that the design is ready for submission or external review. The same page acknowledges that several prerequisite steps have not occurred.

Recommendation: Use "structured for alignment with ISO/IEC 17024, NCCA, and IACET expectations" or "designed to support future accreditation work." Reserve "accreditation-ready" for a later stage after a formal job-task analysis, item-bank development, pilot testing, standard setting, governance documentation, and impartiality controls exist.

### 4. Domain language is internally confusing

Severity: Medium  
Evidence: `website/index.html`, `website/curriculum.html`, `website/handbook.html`, `website/assessment.html`

The homepage and curriculum emphasize five instructional domains. The handbook defines seven competency domains, with F and G cross-cutting. The assessment page says F and G are embedded rather than separate exam blocks. This is logically defensible, but the reader has to reconcile the terminology.

Recommendation: Standardize all pages to a single formulation: "five instructional module groups plus two cross-cutting competency domains." Show domains F and G in the overview, not only in the handbook and assessment.

### 5. The FDA AI guidance section is current only through early 2025

Severity: Medium  
Evidence: `website/ai-policy.html`, `website/modules/module-14.html`, `references/source_register.md`

The site frames FDA AI guidance around the January 2025 draft guidance. That source remains relevant, but FDA's AI drug-development hub, current as of 2026-05-01, also lists "Guiding Principles of Good AI Practice in Drug Development" from January 2026 and revised AI-related resources.

Recommendation: Update the AI policy, Module 14, and source register to include the 2026 FDA/EMA guiding principles and the FDA AI drug-development hub. Keep the January 2025 guidance clearly labeled as "draft," "Level 1," and "not for implementation."

Reference checked:
- FDA AI drug-development hub: https://www.fda.gov/about-fda/center-drug-evaluation-and-research-cder/artificial-intelligence-drug-development
- FDA January 2025 draft guidance page: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/considerations-use-artificial-intelligence-support-regulatory-decision-making-drug-and-biological

### 6. The source-register claim is broader than the actual register

Severity: Medium  
Evidence: `website/references.html`, `BCMAEP_certification_course/references/source_register.md`, `website/market-alignment.html`, module knowledge-check sections

The register says it consolidates verified sources and functions as the canonical citation pool. However, site pages cite sources that are not in the register, including Adesope 2017 for retrieval practice and the market-alignment page's MSL position statement and ExploreHealthCareers source.

Recommendation: Either add all recurring site citations to the source register or narrow the language to say that the register is a selected core source pool. For a certification site, the better path is to make the register complete.

### 7. Market-alignment evidence is relevant but over-interpreted

Severity: Medium  
Evidence: `website/market-alignment.html`, `website/index.html`, `market_alignment/job_description_links.md`

The market-alignment analysis is useful, but it rests on a sample of approximately 75 postings collected on 2026-07-02, with only about one third fetched in full and the rest captured from search-result summaries. The page discloses this, but the headline framing and homepage summary can still read as a stronger market validation than the method supports. There is also a count inconsistency: the website says "more than 33 companies," while the link index refers to "more than 35 companies" and later "33 named" companies.

Recommendation: Move the sampling caveat above the interpretation, call the evidence base a "screened sample," and describe counts as prevalence tiers rather than frequency estimates. Resolve the company-count discrepancy and clarify whether searched companies without retained postings are included.

### 8. Some standalone-site references point to local source paths

Severity: Low to Medium  
Evidence: `website/accreditation.html`, `website/market-alignment.html`, `website/handbook.html`

Several pages refer to files or folders such as `market_alignment/`, `job_description_links.md`, `raw/`, and `modules/`. Those references are useful inside the repository but not in a standalone static website unless those artifacts are linked or bundled.

Recommendation: Replace local-path references with live links, generated appendix pages, downloadable files, or a short note that the source archive is not included in the static site.

### 9. Several key-reading lists have formatting glitches

Severity: Low  
Evidence: `website/modules/module-10.html`, `website/modules/module-11.html`, `website/modules/module-12.html`, `website/modules/module-13.html`, `website/modules/module-15.html`

Some generated key-reading lists collapse multiple citations into one list item with a hyphen separator. This reduces polish and can make citation boundaries unclear.

Recommendation: Fix the generator or source Markdown so each key reading becomes its own list item. Rebuild the site after repairing the source.

### 10. The source register has a character-encoding defect

Severity: Low  
Evidence: `website/references.html`, `BCMAEP_certification_course/references/source_register.md`

At least one author name in the source register renders with mojibake rather than the intended accented character. This is a small issue, but it weakens the credibility of a page that is explicitly about source integrity.

Recommendation: Repair the source encoding before regenerating the website, and run a scan for common mojibake patterns before publication.

## Coherence and Relevance Assessment

The core narrative is coherent: clinicians and other scientific professionals need a structured route into medical affairs and evidence roles, and the program integrates medical affairs operations, HEOR, market access, evidence planning, and AI governance. The most coherent sections are the homepage overview, curriculum map, AI policy, and modules 7 to 10.

The main coherence problem is not the curriculum logic but the status logic. The site alternates between an honest prototype/status disclosure and polished credential language that sounds market-ready. A skeptical reader could interpret this as overclaiming even though the caveats are present.

The relevance is strong for early-career or transitioning professionals interested in medical affairs, MSL, medical information, HEOR, RWE, and market access. The content is less directly relevant to senior medical-affairs leadership, people management, project finance, vendor contracting, and tool-specific field operations. The market-alignment page already identifies some of these gaps.

## Accuracy Assessment

The site is broadly accurate in its treatment of certification versus certificate distinctions, non-accreditation status, the importance of independent assessment, HEOR/HTA concepts, AI verification risk, publication-ethics accountability, and the need for source traceability.

The biggest accuracy/currentness issue is the AI guidance landscape, which should be updated for 2026 FDA/EMA materials. The biggest evidence-traceability issue is the mismatch between the "canonical source register" claim and the actual set of citations used across the site.

The review did not find missing internal links or broken local anchors. External scripted checks were not treated as definitive because some official and DOI sites block automated requests. No confirmed broken external links were identified in this review.

## Prioritized Recommendations

1. Recalibrate all credential-status and outcome language before public publication.
2. Replace "accreditation-ready" with "structured for alignment" or similar language until validation and governance prerequisites are complete.
3. Standardize the domain model as "five instructional module groups plus two cross-cutting competency domains."
4. Update the AI guidance content for 2026 FDA/EMA materials and explicitly mark the 2025 FDA guidance as draft and not for implementation.
5. Make the source register complete, or narrow the claim that it is the canonical citation pool.
6. Tighten the market-alignment methodology language and resolve the company-count inconsistency.
7. Convert repository-local source references into reader-facing links or appendices.
8. Repair key-reading list formatting and source-register encoding.
9. Add a short "validation roadmap" page or box that separates completed design work from future validation work.
10. Before any public release, run a fresh currentness check on accreditation standards, FDA/EMA AI materials, job-posting market alignment, and major guidance links.

## Bottom Line

This is a strong course-site prototype with unusually good scope, structure, and evidence orientation. Its main weakness is not topical relevance or depth. The weakness is that its polished credential framing outruns its documented validation status. If the language is recalibrated and the source/currentness gaps are repaired, the site would read as a credible, rigorous certification-design prototype rather than as an unvalidated credential presented in finished form.
