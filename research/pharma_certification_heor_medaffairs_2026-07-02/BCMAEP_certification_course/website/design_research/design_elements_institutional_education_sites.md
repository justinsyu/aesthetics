# Design research: online education and certification websites

Research conducted 2026-07-06 for the BCMAEP course website. Method: page structure captured via web fetch; typography and color values extracted from downloaded production CSS files where noted. All URLs below were actually loaded unless listed in "Sites not reached." This report determined the visual design system implemented in `../assets/css/site.css`.

## Sites not reached

- harvardonline.harvard.edu: HTTP 429 on repeated attempts (fetch and browser-UA curl). Harvard's course catalog was examined instead via pll.harvard.edu, which lists the same Harvard Online courses.
- publichealth.jhu.edu (Johns Hopkins Bloomberg School of Public Health): HTTP 403 on all paths, both fetch methods. Program names and positioning were confirmed only through search results.
- pce.uw.edu/certificates/health-economics-and-outcomes-research: HTTP 404 (program renamed); the equivalent page on sop.washington.edu loaded and is covered below.
- online.stanford.edu returned 403 to standard fetch but loaded via curl with a browser user agent; findings below are from the downloaded HTML and CSS.

## 1. Harvard Professional and Lifelong Learning (https://pll.harvard.edu/ and https://pll.harvard.edu/course/data-science-and-ai-principles)

- Typography (from production CSS): Merriweather (serif) for display headings; Merriweather Sans for body and UI; Manrope and Inter appear in newer components. Serif/sans pairing signals academic identity.
- Color (from CSS): Harvard crimson #a51c30 as the single brand accent; otherwise a grayscale system driven by CSS variables (gray-200 through gray-600); white background.
- Course page anatomy: title + one-paragraph description + photo above the fold; a metadata grid ("fact bar") with 6 items: duration (5 weeks), price ($1,200), modality (Online), time commitment (4-5 hours/week), pace (self-paced), subject/difficulty. Then "What you'll learn" (3 bullets), narrative course description, instructor block (headshot, name, professorship title), "You may also like" carousel, email-list signup.
- Trust signals: counts stated plainly ("515 COURSES", "6,000,000+ LEARNERS", "246 COUNTRIES"); 12 Harvard schools listed as content sources; attributing school logo (Faculty of Arts and Sciences) on each course; VPAL attribution in footer.
- Navigation: minimal header (logo, search, subject dropdown); catalog filters by subject and modality; lean footer (accessibility, privacy, terms, image attribution).

## 2. MIT Open Learning (https://openlearning.mit.edu/)

- Headline "Reinventing Education"; audience-segmented navigation (For Learners and Organizations, For MIT Faculty).
- Programs presented as flat cards (MITx MicroMasters, MITx Courses, OpenCourseWare, xPRO) with short descriptions and "Learn more" links; no pricing on cards.
- Trust signals: institutional identity itself plus dated news stories featuring learners; no badges or statistics on the homepage.
- Footer: contact, social links, accessibility/privacy/conduct policies.

## 3. MITx Online (https://mitxonline.mit.edu/)

- Typography (from production CSS): Inter for body, Poppins for headings.
- Color (from CSS): MIT red #a31f34 (68 uses, the dominant brand color), deep navy #03152d (38 uses) for dark sections, grays #212529/#6c757d, pale blue-gray panels #f0f5f7.
- Layout: hero states value plainly ("learn for free... earn a certificate for a low fee"); horizontally scrolling course cards showing thumbnail, start date, title; single "Explore Courses" CTA.
- Trust signals: "ranked #1 university in the world", "Certificate signed by MIT faculty"; honor code linked in footer.

## 4. Stanford Online (https://online.stanford.edu/ and https://online.stanford.edu/programs/artificial-intelligence-professional-program)

- Typography (from production CSS): Source Sans Pro as the primary family (36 declarations) with Inter Variable in newer components; no serif.
- Color (from CSS custom properties, an unusually explicit token system): cardinal red #8c1515 (used as --color-background for brand sections), dark red #820000, near-black #2e2d29, cool grey #4d4f53, fog #f4f4f4 and light sandstone #f9f6ef as section backgrounds, lagunita teal #007c92 and blue #006cb8 for links/secondary.
- Homepage anatomy: hero "Empowering Learners to Shape Tomorrow, Today." with subheading; sections "Explore Our Programs", "Featured Courses", "Featured Programs", and the credibility banner "Stanford Content. Stanford Faculty. Stanford Credentials."
- Program page anatomy (AI Professional Program): Overview, What you can expect, What you need to get started, Courses (with per-course pricing: $1,595-$1,950 per course, "10 weeks"), Flexible Enrollment Options (Individual vs Groups/Teams), What You'll Earn, Academic Director (Christopher Manning), Teaching Team (8 named professors with headshots), Need Help?/Connect.
- Navigation: deep topical menus (Graduate Certificates, Artificial Intelligence, Free Content, Academic Calendar, Application and Enrollment, Enrollment FAQs); title pattern "Program | Stanford Online".

## 5. University of Washington, CHOICE Institute certificate (https://sop.washington.edu/choice/graduate-education-training-programs/certificate-in-health-economics-health-technology-assessment-and-market-access/)

The closest structural template to the target deliverable: a university-run HEOR certificate page.

- Typography (from uw_wp_theme CSS): Encode Sans family (UW brand font, including Encode Sans Compressed for headings) with Open Sans; WordPress presets also register Roboto Slab and Uni Sans.
- Color (from theme CSS): UW purple #4b2e83 (14 uses) and metallic golds #85754d / #b7a57a; neutral #f0f1f1 panels.
- Page anatomy (53 sections): hero title + tagline "Transform Healthcare Decision Making"; fact panel (Online / 9 months / flexible pace; $8,505 total; 9 CEUs; asynchronous); "Recommended By Students" (3 named alumni with headshots and titles); "Who Should Enroll"; "What You'll Learn" (4 competencies); 3-course accordion with dates, syllabus links, per-course cost ($2,835); "Learn from the Experts" faculty section (6 named faculty with linked profiles, including Sean D. Sullivan, Lou Garrison); capstone section; Program Costs; scholarship section with eligibility and equity statement; Program Requirements and How to Apply (English proficiency, international students, technology requirements); application timeline with explicit deadline ("Apply by Sep 16"); 13-item FAQ; "Ready to Move Forward?" closing CTA; program manager contact by name.
- Navigation: breadcrumbs under the title; school-level top nav; full UW-branded footer with copyright, accessibility, privacy.

## 6. ACMA / BCMAS (https://medicalaffairsspecialist.org/), the direct benchmark competitor

- Typography (from Next.js CSS): Inter throughout (single sans family via --font-inter variable).
- Color (from CSS): deep petrol teal #014459 as primary (18 uses), darker shades #062b37 / #051d23, mid teal #1b6f83, pale teal backgrounds #ecf3f5 / #e8eef3, neutral grays.
- Page anatomy: hero "Board Certified Medical Affairs Specialist Program" with certification badge image and value bullets; accreditation logo band above the fold (IACET/ANSI, ACPE, ACCME); fact strip (100% online, self-paced, 6 months access, ~40 hours, CE credits); statistics block (92% more prepared, 87% of KOLs prefer BCMAS-certified MSLs); corporate logo wall (Novartis, AbbVie, Pfizer, Roche, Takeda and others, "Trusted by 1000+ companies since 2015"); media mention logos (Forbes, USA Today, Fox News); testimonials with names and credentials and 5-star ratings; pricing ($2,399 or $839/month installments); team-enrollment section; FAQ; policy-heavy footer (Academic Integrity, Anti-Discrimination, Conflict of Interest) plus physical address.
- Trust signals of note: ACMA Verify credential-verification platform; "#1 program" superlative claims sit alongside the accreditation logos (the accreditation band and verification registry read as credible; the superlatives and media logos read as marketing).

## 7. MAPS, Medical Affairs Professional Society (https://medicalaffairs.org/)

- Typography (from Enfold theme CSS): Open Sans (400/600) for body and headings; occasional Times New Roman fallbacks in legacy styles.
- Color (from dynamic theme CSS): amber gold family #edaf44 / #febf55 / #dc9e33 / #cb8d22 as accent against white and gray #808184.
- Anatomy: hero states the organizational identity ("premier non-profit global Medical Affairs organization FOR... BY..."); three learning pathways as cards (eAcademy online courses, MasterClass, Knowledge Center); membership statistics ("18,000+ members from 280+ companies"); event promotion.
- Trust signals: non-profit status stated; governance transparency (bylaws, policies linked); physical address and phone in footer.
- Navigation: wide top menu (Membership, Professional Development, MasterClass, Partnerships, Meetings and Events, Opportunities, About) with login/join/cart utilities.

## 8. ISPOR (https://www.ispor.org/education-training and https://www.ispor.org/education-training/short-courses)

- Typography (from site.css and Google Fonts link): Oswald (condensed sans, weights 200-700) for headings, Open Sans (400/600/700) for body, Poppins in newer components.
- Color (from CSS): lime green #95c93d and sky blue #27aae1 / #1193ca as accents, warm gray-brown #716658 for text, beige neutrals #e6e4e1 / #ebe9e6; overall a light, association-style palette rather than a dark academic one.
- Education page anatomy: banner headline "HEOR Education at ISPOR" plus mission paragraph; four offering cards (Short Courses, Education Center, HEOR Learning Lab, Webinars) each with a CTA; testimonials; "ISPOR Reach" statistic (attendees from 70+ countries).
- Short courses page: breadcrumbs (Home > Education > Short Courses); sidebar navigation of sibling education offerings; two-tier pricing tables (member vs non-member: $890/$710 for 8-hour, $445/$355 for 4-hour, with student/government rates); explicit alignment to the HEOR Competency Framework and annual curriculum updates.
- Footer: extensive policy list (AI Policy, Antitrust Compliance, Code of Ethics, Diversity Policy, Privacy) that itself functions as a governance trust signal.

## 9. Coursera certificate page (https://www.coursera.org/professional-certificates/google-data-analytics)

Included as the marketing-heavy contrast case.

- Anatomy: hero with partner logo and career-outcome headline; dense fact bar (9-course series, 4.8 stars from 180,764 reviews, Beginner, 6 months at 10 hrs/week, flexible, 3,675,192 enrolled); "What you'll learn" (4 bullets); 17+ skill tags; 9-course accordion with per-course hours; instructor block with aggregate learner counts; employer logo wall; outcome claim ("75% report a positive career outcome within six months"); salary/job-market statistics; testimonials; ACE college-credit block; 16-item FAQ; "Enroll for free" CTAs plus subscription upsell banners ("10,000+ programs for $239").
- Distinctive MOOC-platform patterns: star ratings, enrollment counters, promotional pricing, career-outcome persuasion. These are the elements the institutional sites conspicuously avoid.

## 10. edX (https://www.edx.org/)

- Typography (from production CSS): Inter as the single family.
- Color (from CSS): edX red #d23228 / dark red #921108, very dark teal #00262b / #002121, cyan #03c7e8, plus warm marketing tints (#fef9c3 pale yellow, peach gradient tones #f1a483 / #ee8c62) absent from the university sites.
- Homepage anatomy: "Explore top courses", testimonials ("Hear what other learners have to say"), B2B section ("Empower every member of your team"), "Popular topics", community framing, free-account registration CTA. Platform-marketing register, closer to Coursera than to the .edu sites.

## 11. ABIM, American Board of Internal Medicine (https://www.abim.org/)

The strongest board-certification reference pattern.

- Typography (from styles.min.css and Google Fonts): Montserrat (variable weight) for headings, Open Sans for body.
- Color (from CSS): mid blue #00669e and dark blue #004a72 as primaries, light blue #4bafec, pale blue panel #e3f0ff, accent orange #f79b1c, teal #16b9b1, gold #ffcf4f; near-black text #010101 / #363636.
- Anatomy: mission-statement headline ("Certifying Physicians Who Demonstrate the Knowledge, Skills and Attitudes Essential for Excellent Patient Care") with a photo of a named certified physician ("ABIM Certified since 2013"); "Check a Certification" verification search in the header itself, with a dedicated /verify-physician/ tool; three lifecycle cards (Get Certified in Internal Medicine, Get Certified in a Subspecialty, Maintain Your Certification) each with exam blueprints and assessment dates.
- Trust signals: ~300,000 board-certified physicians; "79% reported a positive impact on practice"; ">90k certificates maintained with the LKA"; "75%+ of Board members actively practice"; GuideStar Platinum badge; registered motto "Of the Profession, For the Public".
- Navigation organized by credential lifecycle (Becoming Certified / Maintaining Your Certification / About ABIM Certification); footer segmented by audience (patients, program directors, credentialers, media).

## 12. NBME (https://www.nbme.org/)

- Typography (from Typekit kit rhc2ovf): Gotham (Adobe Fonts), a geometric sans associated with institutional identity.
- Color (from et-core CSS): primary blue #0077c8, deep navy #0a2a4d and #1b4973, cyan #00b5e2, green #00ab85, pale cyan panel #e5f8fc, neutral #f5f5f5.
- Anatomy: mission-style hero ("Advancing Assessment, Supporting Optimal Care") linking to "Who We Are"; audience-segmented content ("For Examinees" / "For Educators") as image cards; no pricing or promotional elements on the homepage.
- Trust signals: TRUSTe and VeraSafe privacy seals; Philadelphia street address; research/grants sections signaling scientific mission.

---

# Synthesis: ranked design elements of credible institutional education sites

Ranked by consistency of use across the university and board sites (Harvard PLL, Stanford, MIT/MITx, UW, ABIM, NBME, ISPOR), as distinct from MOOC-platform marketing patterns (Coursera, edX). Implementation guidance targets a fictional-but-serious pharmaceutical certification board.

**1. One dark, desaturated institutional color with near-total restraint elsewhere.**
Observed in 8 of 8 institutional sites: crimson #a51c30 (Harvard), cardinal #8c1515 (Stanford), MIT red #a31f34, UW purple #4b2e83, ABIM blues #004a72/#00669e, NBME navy #0a2a4d, ACMA petrol teal #014459. The medical/assessment bodies cluster in blue-teal. Implementation: pick a single deep navy-teal primary in the #0f3050 to #014459 range (differentiated from ACMA's exact #014459), use it for the header band, H1/H2, primary buttons, and footer; hold all other color to neutrals. Add one restrained metallic accent for the credential itself (gold in the #85754d to #edaf44 range, per UW and MAPS) used only on the badge, seal, and small rules.

**2. A standardized fact bar on every program page.**
Harvard PLL (duration, price, modality, hours/week, pace, subject), UW (format, months, total cost, CEUs), BCMAS (100% online, 40 hours, 6 months access, CE credits), ISPOR (member/non-member price tables). Implementation: directly under the hero, a 4-6 cell grid with label-over-value typography: Duration, Time commitment, Format, Exam windows, CE credits, Fee. Labels in 11-12px uppercase letterspaced sans, values in 18-20px semibold.

**3. Named faculty and governance people with headshots, titles, and affiliations.**
Stanford (academic director plus 8 named professors), UW (6 faculty with linked profiles), Harvard PLL (professorship title under instructor). Implementation: an "Examination Board" or "Faculty" section of 4-8 people: photo, full name with degrees, institutional title. Photos uniform in crop and background. This is the single strongest differentiator from low-credibility certificate mills.

**4. Credential verification as a first-class feature.**
ABIM places "Check a Certification" in the global header; ACMA operates ACMA Verify. Implementation: a header link "Verify a Credential" leading to a name-search page, plus a statement of the public registry's purpose. Nothing signals board-style legitimacy more directly.

**5. Serif/sans academic typography, or a two-weight sans system.**
Two credible patterns observed: (a) serif display + sans body: Merriweather + Merriweather Sans (Harvard PLL); (b) distinctive sans headings + humanist sans body: Montserrat + Open Sans (ABIM), Oswald + Open Sans (ISPOR), Encode Sans + Open Sans (UW), Source Sans Pro alone (Stanford), Inter alone (ACMA, MITx, edX). Implementation for a board register: Source Serif 4 or Merriweather at 600-700 for H1/H2 (34-44px), Source Sans 3 or Inter at 400/600 for body (16-18px, line-height 1.6) and UI. Avoid decorative or geometric-trendy display faces.

**6. Accreditation and third-party recognition band, high on the page.**
BCMAS shows IACET/ANSI, ACPE, ACCME logos above the fold; ABIM shows GuideStar Platinum; NBME shows TRUSTe/VeraSafe. Implementation: a grayscale logo strip beneath the hero labeled factually ("Accreditations and recognitions"), each logo linked to the accreditor's listing. Keep logos monochrome to avoid a sponsor-wall look.

**7. Plain quantitative statistics instead of persuasion.**
Harvard PLL ("515 courses, 246 countries"), ABIM ("nearly 300,000 board-certified physicians", "79% reported positive impact"), MAPS ("18,000+ members from 280+ companies"), ISPOR ("70+ countries"). Implementation: a 3-4 stat row with large numerals (primary color) and short neutral captions; cite the measurement year. Avoid Coursera-style salary claims and enrollment counters.

**8. Structured curriculum as numbered modules with hours and objectives.**
UW's 3-course accordion with syllabus links and per-course costs; Coursera's 9-course accordion with per-course hours; Stanford's course list with units. Implementation: an accordion of numbered modules, each with 2-4 learning objectives, contact hours, and assessment format; link a downloadable exam blueprint (ABIM's blueprint pattern) rather than hiding content behind enrollment.

**9. Explicit eligibility, requirements, and application timeline.**
UW (requirements, English proficiency, technology requirements, dated deadlines, "Apply by Sep 16"); ABIM (certification pathways with assessment dates). Implementation: a dedicated "Eligibility and Application" section with a dated timeline component and stated prerequisites (degree, years of experience). Dated deadlines signal cohort discipline; "enroll any time, start instantly" signals a content product.

**10. Breadcrumbs and lifecycle-organized navigation.**
ISPOR (Home > Education > Short Courses), UW (breadcrumbs under title), ABIM (Becoming Certified / Maintaining Your Certification), NBME (Examinees / Institutions). Implementation: shallow top nav of 5-6 items organized by candidate lifecycle (Certification, Recertification, Verify a Credential, Exam Resources, About the Board), breadcrumbs on all interior pages, no mega-menu clutter.

**11. Governance-heavy footer with a physical address.**
Universal across the credible set: street address (ACMA: Oradell NJ; MAPS: Golden CO; NBME: Philadelphia; ABIM: Philadelphia), plus policy links whose titles themselves signal governance (ISPOR: Antitrust Compliance, Code of Ethics, AI Policy; ACMA: Academic Integrity, Conflict of Interest, Anti-Discrimination). Implementation: 4-column footer: contact with street address; policies (privacy, code of ethics, conflict of interest, non-discrimination, exam security); quick links; and a one-line mission statement (ABIM's "Of the Profession, For the Public" pattern).

**12. Neutral off-white section alternation, no gradients.**
Stanford alternates white with fog #f4f4f4 and light sandstone #f9f6ef; ABIM uses pale blue #e3f0ff panels; NBME pale cyan #e5f8fc; MITx #f0f5f7. edX's peach/yellow gradient tints mark the marketing register. Implementation: alternate #ffffff with one warm neutral (#f5f4f0) and one pale tint of the primary (#eef4f7); reserve the dark primary for one full-bleed band (stats or CTA) per page.

**13. Testimonials only with full names, credentials, and roles.**
UW (three named alumni with titles and headshots), BCMAS (named reviewers with post-nominals). Implementation: 2-3 quotes maximum, each with name, degrees, job title, and company category (not logo walls); no star ratings.

**14. Restrained CTA system.**
Institutional sites use one or two verbs ("Apply", "Enroll", "Learn More") in the primary color, once above the fold and once at page end (UW's closing "Ready to Move Forward?"). Implementation: solid primary-color button, 4px radius or square, sentence case; never persistent sticky banners, countdown timers, or discount framing.

**15. Named human contact for the program.**
UW lists its program manager by name with email; ISPOR provides a questions contact block; NBME/ABIM provide audience-specific contact routes. Implementation: end the program page with a named credentialing coordinator and institutional email, not a chatbot or generic form.

**Anti-patterns to avoid (observed on Coursera, edX, and partly BCMAS):** enrollment counters and star ratings, "#1" superlatives, media-mention logo walls, subscription upsell banners, salary claims, promotional pricing, and more than one typeface trend per page. The BCMAS site is instructive as the direct competitor: its accreditation band, fact strip, and verification registry are worth matching; its superlative claims and media logos are where a more institutional register can visibly differentiate.

## Sources loaded

[pll.harvard.edu](https://pll.harvard.edu/), [pll.harvard.edu course page](https://pll.harvard.edu/course/data-science-and-ai-principles), [openlearning.mit.edu](https://openlearning.mit.edu/), [mitxonline.mit.edu](https://mitxonline.mit.edu/), [online.stanford.edu](https://online.stanford.edu/), [Stanford AI Professional Program](https://online.stanford.edu/programs/artificial-intelligence-professional-program), [UW CHOICE certificate](https://sop.washington.edu/choice/graduate-education-training-programs/certificate-in-health-economics-health-technology-assessment-and-market-access/), [medicalaffairsspecialist.org](https://medicalaffairsspecialist.org/), [medicalaffairs.org](https://medicalaffairs.org/), [ispor.org/education-training](https://www.ispor.org/education-training), [ISPOR short courses](https://www.ispor.org/education-training/short-courses), [Coursera Google Data Analytics](https://www.coursera.org/professional-certificates/google-data-analytics), [edx.org](https://www.edx.org/), [abim.org](https://www.abim.org/), [nbme.org](https://www.nbme.org/).

## Implementation notes for this site

Applied in `../assets/css/site.css` and the page templates in `../build/build_site.mjs`:

- Primary #0d3b54 (deep navy-teal, distinct from ACMA #014459); gold #7a6540 / #d9b96a reserved for the seal, kickers, and small rules (elements 1, 12).
- Serif display (Georgia stack) over humanist sans body at 17px/1.6 with a 72ch measure; no external font requests so the site is fully self-contained (element 5, adapted).
- Dark full-bleed fact band with label-over-value statistics on the home page (elements 2, 7).
- Numbered module structure with hours, objectives, and a published exam blueprint page (element 8); explicit eligibility section (element 9).
- Breadcrumbs on all interior pages; shallow 5-item top nav; governance-oriented footer with program status, accessibility, and source policies (elements 10, 11).
- Restrained CTA system: at most two buttons above the fold, sentence case, 4px radius (element 14).
- Elements 3 (named faculty), 4 (verification registry), 13 (testimonials), and 15 (named contact) are deliberately omitted: the program is a version 1.0 design with no faculty, certificants, alumni, or staff, and fabricating people or a registry would violate the program's integrity standard. These are documented as roadmap items instead.
