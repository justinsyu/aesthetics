# Structure and format conventions for self-paced online certification courseware: research findings

Research conducted 2026-07-06 for the BCMAEP course website. Scope: evidence and platform conventions to guide the information architecture of a static website delivering a 15-module, text-based, board-style certification course (pharmaceutical medical affairs / HEOR) with knowledge checks and a capstone portfolio. All cited URLs were either fetched directly or returned and summarized in search results; sources that could not be loaded are listed at the end. This report determined the information architecture and lesson-page template implemented in `../build/build_site.mjs`.

## 1. Instructional design structure for self-paced online courses

### 1.1 Lesson and module page structure in quality frameworks

The two most widely used course-design quality frameworks in US higher education both codify the "objectives first, aligned assessment, transparent grading" pattern:

- The [Quality Matters (QM) Higher Education Rubric, Seventh Edition](https://www.qualitymatters.org/qa-resources/rubric-standards/higher-ed-rubric) contains 8 General Standards and 44 Specific Review Standards; certification requires an 85% score with all Essential (3-point) standards met. The eight General Standards are: (1) Course Overview and Introduction, (2) Learning Objectives (Competencies), (3) Assessment and Measurement, (4) Instructional Materials, (5) Learning Activities and Learner Interaction, (6) Course Technology, (7) Learner Support, (8) Accessibility and Usability. QM requires learning objectives to be stated at both the course level and the module level, measurable, and appropriate to the course level, and defines "Alignment" as the condition where objectives (2.1, 2.2), assessments (3.1), materials (4.1), activities (5.1), and technology (6.1) work together ([QM rubric standards overview](https://www.qualitymatters.org/qa-resources/rubric-standards)). Note: the full annotated text of the Specific Review Standards is copyrighted and not publicly reproduced; a university QM page confirms this restriction explicitly ([UAMS Educational Development](https://educationaldevelopment.uams.edu/qualitymatters/qm-rubric)).
- The [SUNY OSCQR rubric, Standard 44](https://oscqr.suny.edu/standard44/) states: "Course grading policies, including consequences of late submissions, are clearly stated in the Course Information/Syllabus materials," and its guidance recommends linking each graded activity back to rubrics and criteria descriptions, on the rationale that explicit grading standards correlate with learner achievement and motivation.

Practical lesson-page implications from these frameworks: a lesson page should open with 2 to 4 measurable module- or lesson-level objectives, present content in labeled chunks, close with a summary, and connect every assessment item to a stated objective and a published grading policy.

### 1.2 Hierarchy conventions and chunk sizes for text-based learning

- The Nielsen Norman Group article on chunking (Kate Moran, March 20, 2016) recommends: short paragraphs separated by white space, line lengths of roughly 50 to 75 characters, clear visual hierarchy grouping related items, headings with strong contrast, highlighted keywords, bulleted or numbered lists, and summary paragraphs for longer sections. The rationale is working-memory capacity, citing George Miller's 1956 finding of approximately 7 plus or minus 2 chunks in short-term memory ([NN/g: How Chunking Helps Content Processing](https://www.nngroup.com/articles/chunking/), fetched directly).
- University teaching-center guidance converges on segments of under about 15 minutes per chunk, with 6 to 15 minutes cited for video and roughly 10 minutes as a broad recommendation ([UMass Amherst CTL](https://www.umass.edu/ctl/how-do-i-chunk-content-increase-learning), [Montgomery College Hub](https://mcblogs.montgomerycollege.edu/thehub/fundamentals-of-teaching/instructor_resources/chunking-instructional-content/), [UChicago Online](https://online.uchicago.edu/2018/11/30/chunk-your-content/); claims per search-result summaries).
- Platform hierarchy conventions: Open edX structures courses as sections, subsections, and units, with the navigation sidebar reflecting that tree ([Open edX Redwood sidebar navigation release notes](https://docs.openedx.org/en/latest/community/release_notes/redwood/sidebar_nav.html)); Canvas structures courses as Modules containing ordered items, and its guidance is to place everything students need in modules in the precise intended order ([University of Pittsburgh teaching center](https://teaching.pitt.edu/resources/how-to-set-up-modules-for-your-course-in-canvas/)). A three-level hierarchy (course, module, lesson/unit) is the common denominator across Canvas, Open edX, and Coursera.

### 1.3 Evidence for retrieval practice and interpolated testing (verified citable sources)

Two verified peer-reviewed sources:

1. Adesope, O. O., Trevisan, D. A., and Sundararajan, N. (2017). Rethinking the use of tests: A meta-analysis of practice testing. Review of Educational Research, 87(3), 659-701. DOI: [10.3102/0034654316689306](https://doi.org/10.3102/0034654316689306). Across 272 independent effects from 188 experiments, practice testing produced a weighted mean effect size of g = 0.51 versus restudying and g = 0.93 versus filler or no activity; multiple-choice practice tests showed g = 0.70 versus g = 0.48 for short-answer formats, and testing with feedback was only slightly more effective than without ([summary at The Learning Scientists](https://www.learningscientists.org/blog/2017/2/9-1), fetched directly; effect sizes verified via the SAGE record and [ERIC EJ1141817](https://eric.ed.gov/?id=EJ1141817)).
2. Szpunar, K. K., Khan, N. Y., and Schacter, D. L. (2013). Interpolated memory tests reduce mind wandering and improve learning of online lectures. Proceedings of the National Academy of Sciences, 110(16), 6313-6317. DOI: [10.1073/pnas.1221764110](https://doi.org/10.1073/pnas.1221764110), PMID 23576743 ([full text at PMC3631699](https://pmc.ncbi.nlm.nih.gov/articles/PMC3631699/), fetched directly). In two experiments (N = 80) using a 21-minute lecture split into four segments, interpolated tests after each segment reduced self-reported mind wandering (19% vs 41% of probes), increased note-taking, improved final-segment test performance (89% vs 65-70%), and reduced test anxiety, relative to non-tested and restudy conditions.

Design implication: knowledge checks belong inside the lesson (interpolated after each content chunk) as well as at the end of each module, not only in a final exam. Supplementary meta-analytic reviews report medium effect sizes (g approximately 0.50 to 0.61) in applied classroom settings ([retrieval practice state-of-the-art review, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292765/); [spaced retrieval practice in STEM courses, g = 0.28 spaced vs massed](https://link.springer.com/article/10.1186/s40594-024-00468-5)).

## 2. LMS and courseware navigation conventions

### 2.1 Persistent sidebar, breadcrumbs, and next/previous controls

- Sidebar: Open edX added a persistent course navigation sidebar in the Redwood release; it shows sections and subsections with completion-state icons so learners "see what sections they have in-progress and how much content they've completed at a glance" ([Open edX Redwood release notes](https://docs.openedx.org/en/latest/community/release_notes/redwood/sidebar_nav.html), [Open edX navigation announcement](https://openedx.org/announcements/update-course-navigation-changes/)). Canvas uses a persistent left course menu plus a Modules index.
- Next/previous: Canvas places Next and Previous buttons at the bottom of every module item page so students can move sequentially without returning to the module list ([SFSU Canvas navigation guide](https://athelp.sfsu.edu/hc/en-us/articles/18435027728019-Canvas-user-interface-and-navigation)). Canvas community threads document two instructive failure modes: item types that drop the next/previous controls force users back to the module index ([Instructure Community thread 633140](https://community.canvaslms.com/t5/Canvas-Question-Forum/Module-navigation-missing-next-previous-buttons-in-discussions/m-p/633140)), and users request the controls at both top and bottom of the page, describing that placement as a UI standard ([Instructure idea thread](https://instructure.jiveon.com/ideas/1936)). The design lesson: every lesson page, without exception, needs consistent previous/next controls.
- Breadcrumbs: NN/g guidance is that breadcrumbs are useful when a site has 3 or more hierarchy levels, support orientation for users who arrive deep in the site from search, and supplement (never replace) global and local navigation ([NN/g: Breadcrumbs: 11 Design Guidelines](https://www.nngroup.com/articles/breadcrumbs/)). A course > module > lesson site meets the 3-level threshold.

### 2.2 Progress indicators and resume behavior

- Coursera (feature announcement, September 27, 2016, fetched directly): progress bars on the dashboard and course home, week-by-week summaries of required content, and a highlighted recommended next step with a single "Start" button that resumes at the last stopping point. In early testing, learners with these features were over 10% more likely to complete courses and approximately 11% more likely to catch up and finish after falling behind ([Coursera blog](https://blog.coursera.org/new-progress-tracking-features-on-coursera/)).
- edX: green check marks appear in the course outline and top navigation as learners complete content, and the "Resume Course" control opens the unit the learner most recently completed ([edX Learner's Guide: checking progress](https://edx.readthedocs.io/projects/open-edx-learner-guide/en/latest/SFD_check_progress.html)).
- Per-item estimated completion time is displayed by major MOOC platforms as a convention, but no verifiable documentation of this specific practice was located in this research session [citation needed]; the recommendation below is therefore grounded in the general evidence that time-management supports improved completion (Coursera blog above).

### 2.3 Syllabus and gradebook/assessment transparency

- OSCQR Standard 44 (quoted in 1.1) requires grading policies, including late-submission consequences, in the syllabus materials, with each graded activity linked to criteria ([OSCQR Standard 44](https://oscqr.suny.edu/standard44/), fetched directly).
- University teaching-center syllabus guidance converges on: which activities count toward the final grade, the weight of each assessment component, evaluation criteria for each assignment, and feedback timelines ([Carnegie Mellon Eberly Center grading policy examples](https://www.cmu.edu/teaching/designteach/design/syllabus/samples-gradingpolicies/index.html), [Georgetown CNDLS syllabus grading policies](https://cndls.georgetown.edu/resources/syllabus-policies/grading/); claims per search-result summaries).

## 3. Web standards for educational content

### 3.1 WCAG 2.2 essentials

WCAG 2.2 became a W3C Recommendation on October 5, 2023 ([W3C: What's New in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/), fetched directly; [WCAG 2.2 specification](https://www.w3.org/TR/WCAG22/)). It adds 9 success criteria and removes 4.1.1 Parsing. Criteria most relevant to a course site, targeting Level AA:

- Contrast (from WCAG 2.x baseline): 4.5:1 for normal text, 3:1 for large text (SC 1.4.3); 3:1 for UI components and graphical objects (SC 1.4.11).
- Heading hierarchy: heading structure requirements carry over from earlier WCAG versions (SC 1.3.1 Info and Relationships, SC 2.4.6 Headings and Labels); one h1 per page with non-skipping levels is the standard implementation.
- New in 2.2 at Level A/AA: 2.4.11 Focus Not Obscured (Minimum, AA; sticky headers must not fully hide the focused element), 2.5.7 Dragging Movements (AA), 2.5.8 Target Size (Minimum, AA; interactive targets at least 24 by 24 CSS pixels), 3.2.6 Consistent Help (A; help mechanisms in the same place on every page), 3.3.7 Redundant Entry (A), 3.3.8 Accessible Authentication (AA). Focus Appearance (2.4.13, AAA) specifies a focus indicator at least as large as a 2 CSS pixel perimeter with 3:1 contrast between focused and unfocused states.
- Keyboard navigation: full keyboard operability (SC 2.1.1) applies to all interactive elements, including quiz widgets and accordion components.

### 3.2 Typography and line length for long-form screen reading

- Line length (measure): NN/g recommends roughly 50 to 75 characters per line ([NN/g chunking article](https://www.nngroup.com/articles/chunking/), fetched directly); Butterick's Practical Typography recommends 45 to 90 characters including spaces ([Practical Typography: line length](https://practicaltypography.com/line-length.html), fetched directly); Baymard and UXPin summarize the research consensus at 50 to 75 characters ([Baymard](https://baymard.com/blog/line-length-readability), [UXPin](https://www.uxpin.com/studio/blog/optimal-line-length-for-readability/)); WCAG SC 1.4.8 Visual Presentation (Level AAA) sets 80 characters as the maximum for Latin scripts.
- Font size and line height: 16px is the browser default and the widely cited minimum for body text; line height of about 1.4 to 1.6 is the standard recommendation for long-form text, and WCAG SC 1.4.12 (Text Spacing) requires that content tolerate user-applied line height of 1.5 times font size without loss ([US Web Design System typography guidance](https://designsystem.digital.gov/components/typography/); claims per search-result summaries).

### 3.3 Mobile responsiveness expectations

- WCAG SC 1.4.10 Reflow (AA) requires content to present without loss of information or two-dimensional scrolling at a width equivalent to 320 CSS pixels (equivalently, a 1280px viewport at 400% zoom); exceptions include data tables and diagrams, which may scroll within their own container ([W3C Understanding SC 1.4.10](https://www.w3.org/WAI/WCAG21/Understanding/reflow.html)).
- Combined with Target Size (24px minimum) and 16px body text, the practical floor is: single-column reading layout on small screens, a collapsible sidebar, tables wrapped in horizontally scrollable containers, and no reliance on hover.
- The Canvas community threads in 2.1 illustrate the cost of inconsistent mobile navigation (next/previous controls missing on Android), reinforcing that sequential controls must survive the responsive collapse.

## 4. Credibility signals vs diploma-mill signals for certification programs

### 4.1 What credible certification programs disclose

- NCCA (National Commission for Certifying Agencies) accreditation, the reference standard for professional certification bodies, requires a published exam content outline (blueprint) derived from a job task analysis, stating the relative emphasis (domain weights) of each content area and total test length, and this outline is made available to the public; a published candidate handbook covering application through maintenance is also required, along with standard-setting studies and a defensible pass score ([Assessment Systems: What is NCCA Accreditation](https://assess.com/ncca-accreditation/); [NCCA Standards document, HMDCB copy](https://hmdcb.org/uploads/files/ncca%20standards.pdf); examples of the genre: [NBCOT exam handbook](https://www.nbcot.org/-/media/PDFs/Cert_Exam_Handbook.pdf), [ANCC certification handbook](https://www.nursingworld.org/globalassets/certification/ancc-certification-handbook.pdf)).
- In the medical affairs domain specifically, the ACMA's BCMAS program presents itself with an explicit accreditor (IACET/ANSI, a continuing-education-provider accreditor) and cites a published knowledge-gain study (reported 80% knowledge increase, p < 0.001) ([ACMA BCMAS Enterprise page](https://acmalifesciences.org/bcmas-enterprise), [BCMAS program info](https://medicalaffairsspecialist.org/certifications/bcmas/program-info)). Note the category distinction: IACET accredits continuing education and training providers, while NCCA accredits certification programs themselves; a credible site names its accreditor precisely and does not conflate the two categories.

### 4.2 Diploma-mill signals to avoid

Search-verified summaries of CHEA and consumer-education sources converge on these red flags ([CHEA: Important Questions About Degree Mills](https://www.chea.org/important-questions-about-degree-mills), page returned via search but direct fetch blocked, see unreachable list; [GetEducated: 10 Ways to Spot a Diploma Mill](https://www.geteducated.com/college-degree-mills/161-college-degree-or-diploma-mill/); [TheBestSchools comparison](https://thebestschools.org/magazine/online-college-vs-diploma-mills/)):

- Accreditation claims from agencies not recognized by the US Department of Education or CHEA, including self-created accreditors and vague "international" or "worldwide" accreditation claims.
- Credentials awarded for flat fees, life experience, or implausibly short completion times.
- Names imitating well-known institutions; vague or oddly structured program descriptions.
- The corresponding positive signals: precise and verifiable accreditation statements (or an honest statement that the program is not accredited), published exam blueprints and pass criteria, published rubrics, named faculty with verifiable credentials, and per-lesson citation of primary sources with DOIs/PMIDs.

## Sites not reached

- https://www.chea.org/important-questions-about-degree-mills returned HTTP 403 Forbidden on direct fetch; CHEA-attributed claims above rely on search-result summaries and secondary consumer-education sources.
- https://qualitymatters.org/sites/default/files/presentations/QMRubric_6thEd_SUChecklist.pdf downloaded but the PDF text could not be parsed; QM Specific Review Standard wording is additionally restricted by copyright (confirmed at the UAMS page), so QM claims above are limited to publicly stated general standards.
- No verifiable source was located for the specific convention of per-item estimated completion times on Coursera/edX lesson items; that single claim is marked [citation needed] above.

---

# Prioritized recommendations for the certification course website

## Information architecture

1. Use a three-level hierarchy: Course > Module (15) > Lesson, with lessons as single pages of roughly 10 to 20 minutes of reading (approximately 2,000 to 4,000 words), consistent with the under-15-minutes chunk guidance and NN/g working-memory rationale. Target 4 to 8 lessons per module.
2. Provide a persistent course sidebar listing all modules and lessons with per-item completion checkmarks and current-location highlighting, collapsing to a toggle on small screens (pattern: Open edX Redwood sidebar; Canvas course menu).
3. Add a breadcrumb trail (Course > Module N > Lesson N.N) on every lesson page; the 3-level hierarchy meets the NN/g threshold at which breadcrumbs add value, and it orients learners arriving from search or bookmarks.
4. Place previous/next lesson controls at both the top and bottom of every lesson page, with no page types exempt; Canvas community complaints show that any gap in sequential controls forces users back to the index.
5. Build a course home page with an overall progress bar, per-module progress, and one primary "Continue" button that resumes at the first incomplete lesson (Coursera reported over 10% higher completion with this pattern). For a static site, persist completion state in localStorage with a JSON export/import option.
6. Publish a syllabus page containing: the full module map with module-level objectives, the assessment structure (knowledge checks, module quizzes, capstone), component weights and passing criteria, estimated total study hours, and feedback/turnaround expectations (OSCQR 44; CMU and Georgetown syllabus conventions).

## Lesson page template (top to bottom)

7. Fixed template order for every lesson: breadcrumb; title; metadata row (module, lesson number, estimated reading time, number of knowledge-check questions); 2 to 4 measurable learning objectives; chunked content; key-points summary box; end-of-lesson knowledge check; previous/next controls. Objectives-first, module-level statement is the QM Standard 2 convention.
8. Chunk the body with a heading every 200 to 400 words, paragraphs of 3 to 5 sentences, bulleted lists for parallel items, and a summary box per major section (NN/g chunking guidance).
9. Interpolate 1 to 2 self-check questions after every 2 to 3 content sections, in addition to the end-of-lesson check; interpolated testing reduced mind wandering from 41% to 19% of probes and raised final-segment performance from 65-70% to 89% (Szpunar et al., 2013, PNAS, DOI 10.1073/pnas.1221764110).
10. Make every knowledge check a retrieval event with immediate explanatory feedback, using predominantly multiple-choice with some short-answer prompts (practice testing g = 0.51 vs restudy; multiple-choice g = 0.70; Adesope et al., 2017, DOI 10.3102/0034654316689306). Include 2 to 3 cumulative items per module quiz drawn from earlier modules to exploit spacing benefits.

## Standards and presentation

11. Set body text at 16 to 18px with line height approximately 1.5 and a content column capped near 65 to 70 characters per line; wrap wide tables in their own horizontally scrollable containers so the page never scrolls horizontally (NN/g 50-75 characters; Butterick 45-90; WCAG 1.4.10 Reflow at 320 CSS px).
12. Target WCAG 2.2 Level AA explicitly: 4.5:1 text contrast, one h1 per page with non-skipping heading levels, visible focus indicators with at least 3:1 contrast that are never fully obscured by sticky headers, interactive targets at least 24 by 24 CSS pixels, full keyboard operability of quiz widgets, and a help/contact link in the same location on every page (SC 3.2.6). State the conformance target on the site.

## Credibility

13. Publish an exam blueprint page modeled on NCCA convention: a domain-weight table mapping the 15 modules to percentage emphasis on the final assessment, item counts, question formats, and the passing standard with its rationale. Publish the capstone portfolio rubric (criteria and performance levels) before enrollment, and link each graded activity to its criteria (OSCQR 44).
14. Write a precise accreditation and status page: state exactly what the credential is and is not (a certificate of completion vs an accredited professional certification), name any recognized accreditor precisely or state plainly that the program is not accredited, and avoid vague "internationally recognized" phrasing; unrecognized or vague accreditation claims are the primary diploma-mill signal identified by CHEA-aligned sources.
15. Cite primary sources throughout the courseware: a references section per lesson with DOIs/PMIDs for peer-reviewed claims (mirroring HEOR professional norms), named authors/reviewers with verifiable credentials, and visible "last reviewed" dates on each lesson. This both differentiates the program from low-credibility offerings and models the evidence practices the curriculum teaches.

## Implementation notes for this site

Applied in `../build/build_site.mjs`, `../assets/css/site.css`, and `../assets/js/site.js`:

- Recommendations 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, and 15 are implemented directly (sidebar with completion marks and progress bar; breadcrumbs; prev/next at top and bottom; resume button with localStorage progress and JSON export/import; syllabus page; knowledge checks as reveal-style retrieval events with the Adesope et al. citation and interactive sample MCQs with rationale feedback; 72ch measure at 17px/1.6 with scrollable table wrappers; WCAG 2.2 AA targets stated in the footer; published blueprint, rubrics, and honest accreditation-status page; per-lesson key readings with verified hyperlinked citations).
- Recommendation 1 is adapted rather than followed literally: the course's 15 modules are kept as single lesson pages (roughly 10 to 30 minutes of core reading each) with a two-column in-page section index, because splitting the source modules into 4 to 8 sub-pages would fragment the authored curriculum documents the site is generated from.
- Recommendation 9 (interpolated mid-lesson questions) is not implemented because the source modules place their knowledge checks at the end; adding mid-lesson questions would require authoring new assessment content rather than rendering existing content.
- The metadata row shows approximate structured-effort hours (from the syllabus) and computed core-reading minutes; the per-item completion-time convention is marked [citation needed] in the research above and is presented as descriptive metadata only.
