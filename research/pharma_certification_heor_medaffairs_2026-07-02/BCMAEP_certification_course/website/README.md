# BCMAEP course website

A self-contained static website delivering the complete BCMAEP certification course: the program pages, all 15 modules as navigable lesson pages, the assessment documents, governance, and references. Generated from the course Markdown in the parent directory; the Markdown remains the canonical source.

## How to view

Open `index.html` in a browser, or serve the folder with any static file server. No build step, account, or network connection is required to read the site; all CSS and JavaScript are local, and progress is stored only in the browser (localStorage) with JSON export/import on the curriculum page.

## Contents

- `index.html`: program overview (credential, domains, assessment model, eligibility, program status)
- `curriculum.html`: syllabus and learning map with per-module progress and a resume button
- `modules/module-01.html` through `module-15.html`: lesson pages with objectives, in-page section index, worked example, applied activity, AI-use focus, interactive knowledge check, key readings, and previous/next navigation
- `assessment.html`: examination blueprint with the 12 sample items as interactive practice questions
- `capstone.html`, `cases.html`: capstone portfolio specification and case library
- `ai-policy.html`, `accreditation.html`: governance pages
- `references.html`, `market-alignment.html`, `handbook.html`: source register, market alignment analysis, program handbook
- `assets/`: stylesheet and site JavaScript
- `design_research/`: the two research reports that determined the design (institutional education-site design elements; online course format best practices), each with implementation notes
- `build/build_site.mjs`: the generator. To rebuild after editing the course Markdown: `cd build && npm install && node build_site.mjs`

## Design basis

The visual system follows the design elements most consistently used by credible institutional education and board-certification sites (Harvard PLL, Stanford Online, MIT/MITx, UW CHOICE, ABIM, NBME, ISPOR), as documented in `design_research/design_elements_institutional_education_sites.md`: a single deep navy-teal institutional color with a restrained gold reserved for the credential seal, serif display over sans body, a label-over-value fact band, breadcrumbs, a governance-oriented footer, and none of the MOOC-marketing anti-patterns (star ratings, enrollment counters, superlatives).

The information architecture follows the evidence and platform conventions documented in `design_research/online_course_format_best_practices.md`: objectives-first lesson template (Quality Matters Standard 2 convention), persistent course sidebar with completion marks (Open edX Redwood pattern), previous/next controls at top and bottom of every lesson (Canvas convention), a resume-where-you-left-off button (Coursera reported over 10% higher completion with this pattern), knowledge checks as retrieval-practice events with immediate feedback ([Adesope et al., 2017](https://doi.org/10.3102/0034654316689306)), a 72-character reading measure, and WCAG 2.2 Level AA targets.

## Integrity notes

- The site preserves the program's status statements: version 1.0 design, not accredited, designed for ISO/IEC 17024, NCCA, and ANSI/IACET alignment.
- No faculty, testimonials, certificant counts, or verification registry are shown, because none exist; fabricating them would violate the program's integrity standard even though the design research identifies them as strong trust signals. They are roadmap items for a sponsoring body.
- All interactive assessment content (knowledge checks, sample items) is rendered verbatim from the authored course documents; the site adds no new assessment content.
