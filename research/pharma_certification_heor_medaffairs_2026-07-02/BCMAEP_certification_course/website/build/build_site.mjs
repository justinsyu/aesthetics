// Build script for the BCMAEP certification course website.
// Converts the course Markdown into a static site under website/.
// Usage: node build/build_site.mjs   (run from the website/ directory or anywhere; paths are absolute-resolved)

import { marked } from 'marked';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const COURSE_ROOT = path.resolve(HERE, '..', '..'); // BCMAEP_certification_course/
const SITE_ROOT = path.resolve(HERE, '..');         // website/

// breaks:true keeps intentional single-newline structure (label lines such as
// "Permitted: ..." / "Required controls: ...") as line breaks; the source
// Markdown writes paragraphs as single lines, so no spurious breaks result.
marked.setOptions({ gfm: true, breaks: true });

// ---------------------------------------------------------------------------
// Registry
// ---------------------------------------------------------------------------

const DOMAINS = [
  { key: 'A', title: 'Industry orientation and translation', modules: [1, 2, 3], weight: '15%' },
  { key: 'B', title: 'Scientific and clinical foundations', modules: [4, 5, 6], weight: '20%' },
  { key: 'C', title: 'Evidence generation, HEOR, HTA, and market access', modules: [7, 8, 9, 10], weight: '30%' },
  { key: 'D', title: 'Scientific communication and field medical', modules: [11, 12, 13], weight: '20%' },
  { key: 'E', title: 'AI, data, and professional practice', modules: [14, 15], weight: '15%' },
];

const MODULES = [
  { n: 1,  src: 'module_01_industry_and_lifecycle.md',                 short: 'Industry and the development lifecycle' },
  { n: 2,  src: 'module_02_medical_affairs_operating_model.md',        short: 'The medical affairs operating model' },
  { n: 3,  src: 'module_03_compliance_ethics_nonpromotional.md',       short: 'Compliance and the nonpromotional boundary' },
  { n: 4,  src: 'module_04_trial_design_biostatistics_appraisal.md',   short: 'Trial design, biostatistics, and appraisal' },
  { n: 5,  src: 'module_05_regulatory_affairs_approval_pathways.md',   short: 'Regulatory affairs and approval pathways' },
  { n: 6,  src: 'module_06_pharmacovigilance_safety_risk.md',          short: 'Pharmacovigilance and risk management' },
  { n: 7,  src: 'module_07_rwd_rwe.md',                                short: 'Real-world data and evidence' },
  { n: 8,  src: 'module_08_heor_methods_economic_evaluation.md',       short: 'HEOR methods and economic evaluation' },
  { n: 9,  src: 'module_09_hta_market_access.md',                      short: 'HTA and global market access' },
  { n: 10, src: 'module_10_integrated_evidence_generation_planning.md',short: 'Integrated evidence generation planning' },
  { n: 11, src: 'module_11_msl_field_medical.md',                      short: 'MSL excellence and field medical' },
  { n: 12, src: 'module_12_scientific_communications_publications.md', short: 'Scientific communications and publications' },
  { n: 13, src: 'module_13_advisory_boards_isr_medical_education.md',  short: 'Advisory boards, ISR, and education' },
  { n: 14, src: 'module_14_ai_data_fluency.md',                        short: 'AI and data fluency' },
  { n: 15, src: 'module_15_professional_practice_career_transition.md',short: 'Professional practice and transition' },
];

const DOCS = [
  { id: 'handbook',        src: '00_program_handbook.md',                          out: 'handbook.html',        title: 'Program handbook' },
  { id: 'assessment',      src: 'assessment/exam_blueprint_and_sample_items.md',   out: 'assessment.html',      title: 'Examination blueprint and sample items' },
  { id: 'capstone',        src: 'assessment/capstone_portfolio_and_rubrics.md',    out: 'capstone.html',        title: 'Capstone portfolio and rubrics' },
  { id: 'cases',           src: 'assessment/case_library.md',                      out: 'cases.html',           title: 'Case library' },
  { id: 'ai-policy',       src: 'governance/ai_use_policy_and_playbook.md',        out: 'ai-policy.html',       title: 'AI-use policy and playbook' },
  { id: 'accreditation',   src: 'governance/accreditation_and_quality_alignment.md', out: 'accreditation.html', title: 'Accreditation and quality alignment' },
  { id: 'references',      src: 'references/source_register.md',                   out: 'references.html',      title: 'Source register' },
  { id: 'market',          src: 'market_alignment/medical_affairs_responsibilities_summary.md', out: 'market-alignment.html', title: 'Market alignment analysis' },
];

// Internal cross-reference map: markdown source path -> site page.
const XREF = {
  '00_program_handbook.md': { href: 'handbook.html', label: 'Program handbook' },
  '01_syllabus_and_learning_map.md': { href: 'curriculum.html', label: 'Curriculum and syllabus' },
  'assessment/exam_blueprint_and_sample_items.md': { href: 'assessment.html', label: 'Examination blueprint' },
  'assessment/capstone_portfolio_and_rubrics.md': { href: 'capstone.html', label: 'Capstone portfolio and rubrics' },
  'assessment/case_library.md': { href: 'cases.html', label: 'Case library' },
  'governance/ai_use_policy_and_playbook.md': { href: 'ai-policy.html', label: 'AI-use policy' },
  'governance/accreditation_and_quality_alignment.md': { href: 'accreditation.html', label: 'Accreditation and quality alignment' },
  'references/source_register.md': { href: 'references.html', label: 'Source register' },
  'market_alignment/medical_affairs_responsibilities_summary.md': { href: 'market-alignment.html', label: 'Market alignment analysis' },
};
for (const m of MODULES) {
  XREF['modules/' + m.src] = { href: `modules/module-${String(m.n).padStart(2, '0')}.html`, label: `Module ${m.n}` };
}

const SITE_NAME = 'BCMAEP';
const SITE_LONG = 'Board Certified Medical Affairs and Evidence Professional';
const VERSION_LINE = 'Version 1.0 curriculum design, prepared July 2026.';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function readCourseFile(rel) {
  return fs.readFileSync(path.join(COURSE_ROOT, rel), 'utf8');
}

function slugify(text) {
  return text.toLowerCase()
    .replace(/<[^>]+>/g, '')
    .replace(/&[a-z]+;/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .slice(0, 64);
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function moduleHref(n, rootPrefix) {
  return `${rootPrefix}modules/module-${String(n).padStart(2, '0')}.html`;
}

function moduleId(n) {
  return `m${String(n).padStart(2, '0')}`;
}

// Rewrite internal .md references (both link form and backtick form) to site pages.
function rewriteInternalRefs(md, rootPrefix) {
  // Link form: [text](path.md) possibly with ../ prefixes
  md = md.replace(/\]\((?:\.\.\/)*([A-Za-z0-9_\/]+\.md)\)/g, (whole, p) => {
    const target = XREF[p];
    return target ? `](${rootPrefix}${target.href})` : whole;
  });
  // Backtick form: `path.md` -> link with document label
  md = md.replace(/`(?:\.\.\/)*([A-Za-z0-9_\/]+\.md)`/g, (whole, p) => {
    const target = XREF[p];
    return target ? `[${target.label}](${rootPrefix}${target.href})` : whole;
  });
  return md;
}

// Post-process marked output: external links open in a new tab, tables scroll,
// h2/h3 get stable ids.
function postProcess(html, usedIds) {
  html = html.replace(/<a href="(https?:\/\/[^"]+)"/g, '<a href="$1" target="_blank" rel="noopener"');
  html = html.replace(/<table>/g, '<div class="table-wrap"><table>').replace(/<\/table>/g, '</table></div>');
  html = html.replace(/<h([23])>([\s\S]*?)<\/h\1>/g, (whole, level, inner) => {
    let id = slugify(inner);
    if (!id) return whole;
    let unique = id, i = 2;
    while (usedIds.has(unique)) unique = `${id}-${i++}`;
    usedIds.add(unique);
    return `<h${level} id="${unique}">${inner}</h${level}>`;
  });
  return html;
}

function mdToHtml(md, rootPrefix, usedIds) {
  return postProcess(marked.parse(rewriteInternalRefs(md, rootPrefix)), usedIds);
}

function readingMinutes(md) {
  const words = md.replace(/[#>*`|\[\]()-]/g, ' ').split(/\s+/).filter(Boolean).length;
  return Math.max(5, Math.round(words / 220 / 5) * 5);
}

// Split a markdown document into { preamble, sections: [{heading, body}] } at ## level.
function splitSections(md) {
  const lines = md.split('\n');
  const sections = [];
  let preamble = [];
  let current = null;
  for (const line of lines) {
    const m = line.match(/^## (.*)/);
    if (m) {
      if (current) sections.push(current);
      current = { heading: m[1].trim(), body: [] };
    } else if (current) {
      current.body.push(line);
    } else {
      preamble.push(line);
    }
  }
  if (current) sections.push(current);
  return { preamble: preamble.join('\n'), sections: sections.map(s => ({ heading: s.heading, body: s.body.join('\n').trim() })) };
}

// ---------------------------------------------------------------------------
// Page shell
// ---------------------------------------------------------------------------

function sidebar(rootPrefix, activeHref) {
  const link = (href, label, cls = '') => {
    const active = href === activeHref ? ' aria-current="page"' : '';
    return `<a class="snav-link ${cls}"${active} href="${rootPrefix}${href}">${label}</a>`;
  };
  const moduleLinks = DOMAINS.map(d => {
    const items = d.modules.map(n => {
      const m = MODULES.find(x => x.n === n);
      const href = `modules/module-${String(n).padStart(2, '0')}.html`;
      const active = href === activeHref ? ' aria-current="page"' : '';
      return `<li><a class="snav-link snav-module" data-module="${moduleId(n)}"${active} href="${rootPrefix}${href}">` +
        `<span class="snav-check" aria-hidden="true"></span><span class="snav-num">${n}</span><span>${m.short}</span></a></li>`;
    }).join('\n');
    return `<li class="snav-domain"><span class="snav-domain-label">Domain ${d.key} &middot; ${d.title}</span><ul>${items}</ul></li>`;
  }).join('\n');

  return `
<nav class="sidebar" id="sidebar" aria-label="Course navigation">
  <div class="snav-group">
    <span class="snav-head">Program</span>
    <ul>
      <li>${link('index.html', 'Overview')}</li>
      <li>${link('handbook.html', 'Program handbook')}</li>
      <li>${link('curriculum.html', 'Curriculum and syllabus')}</li>
    </ul>
  </div>
  <div class="snav-group">
    <span class="snav-head">Modules</span>
    <div class="snav-progress" aria-hidden="true"><div class="snav-progress-bar" id="snav-progress-bar"></div></div>
    <p class="snav-progress-text" id="snav-progress-text" role="status"></p>
    <ul class="snav-domains">
${moduleLinks}
    </ul>
  </div>
  <div class="snav-group">
    <span class="snav-head">Assessment</span>
    <ul>
      <li>${link('assessment.html', 'Examination blueprint')}</li>
      <li>${link('capstone.html', 'Capstone portfolio')}</li>
      <li>${link('cases.html', 'Case library')}</li>
    </ul>
  </div>
  <div class="snav-group">
    <span class="snav-head">Governance</span>
    <ul>
      <li>${link('ai-policy.html', 'AI-use policy')}</li>
      <li>${link('accreditation.html', 'Accreditation and quality')}</li>
    </ul>
  </div>
  <div class="snav-group">
    <span class="snav-head">Reference</span>
    <ul>
      <li>${link('references.html', 'Source register')}</li>
      <li>${link('market-alignment.html', 'Market alignment')}</li>
    </ul>
  </div>
</nav>`;
}

function seal(size = 40) {
  // Inline SVG monogram seal.
  return `<svg class="seal" width="${size}" height="${size}" viewBox="0 0 64 64" role="img" aria-label="BCMAEP seal">
  <circle cx="32" cy="32" r="30" fill="none" stroke="currentColor" stroke-width="2.5"/>
  <circle cx="32" cy="32" r="24" fill="none" stroke="currentColor" stroke-width="1"/>
  <text x="32" y="37" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="15" font-weight="bold" fill="currentColor" letter-spacing="0.5">MA</text>
  <text x="32" y="14.5" text-anchor="middle" font-family="Georgia, serif" font-size="6.5" fill="currentColor" letter-spacing="2">BCMAEP</text>
  <text x="32" y="55" text-anchor="middle" font-family="Georgia, serif" font-size="6.5" fill="currentColor" letter-spacing="1">EST 2026</text>
</svg>`;
}

function shell({ title, description, rootPrefix, activeHref, contentHtml, bodyClass = '', withSidebar = true }) {
  const nav = withSidebar ? sidebar(rootPrefix, activeHref) : '';
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)} | ${SITE_NAME}</title>
<meta name="description" content="${escapeHtml(description)}">
<link rel="stylesheet" href="${rootPrefix}assets/css/site.css">
<link rel="icon" href="data:image/svg+xml,${encodeURIComponent(seal(32).replace('class="seal" ', ''))}">
</head>
<body class="${bodyClass}">
<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <div class="header-inner">
    <button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="sidebar"${withSidebar ? '' : ' hidden'}>
      <span class="nav-toggle-bars" aria-hidden="true"></span> Menu
    </button>
    <a class="brand" href="${rootPrefix}index.html">
      ${seal(38)}
      <span class="brand-text">
        <span class="brand-name">${SITE_NAME}</span>
        <span class="brand-sub">${SITE_LONG}</span>
      </span>
    </a>
    <nav class="top-nav" aria-label="Primary">
      <a href="${rootPrefix}index.html">Overview</a>
      <a href="${rootPrefix}curriculum.html">Curriculum</a>
      <a href="${rootPrefix}assessment.html">Assessment</a>
      <a href="${rootPrefix}accreditation.html">Accreditation</a>
      <a href="${rootPrefix}references.html">Sources</a>
    </nav>
  </div>
</header>
<div class="layout${withSidebar ? '' : ' layout-full'}">
${nav}
<main id="main" class="main">
${contentHtml}
</main>
</div>
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">${seal(34)}<div><strong>${SITE_NAME}</strong><br>${SITE_LONG}</div></div>
    <div class="footer-cols">
      <div>
        <span class="footer-head">Program</span>
        <a href="${rootPrefix}handbook.html">Program handbook</a>
        <a href="${rootPrefix}curriculum.html">Curriculum and syllabus</a>
        <a href="${rootPrefix}assessment.html">Examination blueprint</a>
        <a href="${rootPrefix}capstone.html">Capstone portfolio</a>
      </div>
      <div>
        <span class="footer-head">Governance</span>
        <a href="${rootPrefix}accreditation.html">Accreditation and quality</a>
        <a href="${rootPrefix}ai-policy.html">AI-use policy</a>
        <a href="${rootPrefix}references.html">Source register</a>
        <a href="${rootPrefix}market-alignment.html">Market alignment</a>
      </div>
      <div>
        <span class="footer-head">Help</span>
        <a href="${rootPrefix}index.html#how-to-use">How to use this site</a>
        <a href="${rootPrefix}index.html#program-status">Program status</a>
        <a href="${rootPrefix}curriculum.html#your-progress">Your progress</a>
      </div>
    </div>
    <div class="footer-legal">
      <p><strong>Program status.</strong> ${VERSION_LINE} This program is a complete curriculum and certification design; it has not undergone job-task-analysis validation, item-bank piloting, formal standard setting, or accreditation review. It is designed for alignment with ISO/IEC 17024, the NCCA Standards, and the ANSI/IACET Standard, and is not accredited by any body at this version (see <a href="${rootPrefix}accreditation.html">accreditation and quality alignment</a>).</p>
      <p><strong>Accessibility.</strong> This site targets WCAG 2.2 Level AA conformance: minimum 4.5:1 text contrast, keyboard-operable interactive components, visible focus indicators, and single-column reflow at narrow widths.</p>
      <p><strong>Sources.</strong> Teaching claims carry hyperlinked citations to verified authoritative sources; the consolidated pool is the <a href="${rootPrefix}references.html">source register</a>. Cited third-party materials are assigned readings; public availability does not grant republication rights.</p>
    </div>
  </div>
</footer>
<script src="${rootPrefix}assets/js/site.js"></script>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Module lesson pages
// ---------------------------------------------------------------------------

function classifySection(heading) {
  if (/^Learning objectives/i.test(heading)) return 'objectives';
  if (/^Why this matters/i.test(heading)) return 'why';
  if (/^\d+\.\d+\s/.test(heading)) return 'numbered';
  if (/^Worked example/i.test(heading)) return 'worked';
  if (/^Applied activity/i.test(heading)) return 'activity';
  if (/^AI-use focus/i.test(heading)) return 'ai';
  if (/^Knowledge check/i.test(heading)) return 'kc';
  if (/^Key readings/i.test(heading)) return 'readings';
  if (/^Connection to the capstone/i.test(heading)) return 'capstone';
  return 'other';
}

function parseKnowledgeCheck(body) {
  // Items: "1. Question ... (Answer: ...)" where the answer runs to the item's last ")".
  const items = [];
  const chunks = body.split(/\n(?=\d+\.\s)/).map(c => c.trim()).filter(c => /^\d+\.\s/.test(c));
  for (const chunk of chunks) {
    const text = chunk.replace(/^\d+\.\s*/, '');
    const at = text.indexOf('(Answer');
    if (at === -1) { items.push({ q: text, a: null }); continue; }
    let q = text.slice(0, at).trim();
    let a = text.slice(at).replace(/^\(Answer[:\s]*/i, '').trim();
    if (a.endsWith(')')) a = a.slice(0, -1).trim();
    items.push({ q, a });
  }
  return items;
}

function renderKnowledgeCheck(items, rootPrefix, usedIds) {
  const cards = items.map((it, i) => {
    const q = mdToHtml(it.q, rootPrefix, usedIds).replace(/^<p>|<\/p>\s*$/g, '');
    const a = it.a ? mdToHtml(it.a[0].toUpperCase() + it.a.slice(1), rootPrefix, usedIds) : '<p>See module text.</p>';
    return `<details class="kc-item">
  <summary><span class="kc-num">${i + 1}</span><span class="kc-q">${q}</span><span class="kc-toggle" aria-hidden="true">Show answer</span></summary>
  <div class="kc-answer"><span class="kc-answer-label">Model answer</span>${a}</div>
</details>`;
  }).join('\n');
  return `<p class="kc-intro">Answer each question from memory before revealing the model answer. Retrieval practice of this kind improves retention relative to re-reading (<a href="https://doi.org/10.3102/0034654316689306" target="_blank" rel="noopener">Adesope et al., 2017</a>).</p>
<div class="kc-list">${cards}</div>`;
}

function prevNextNav(mod, rootPrefix, position) {
  const prev = MODULES.find(m => m.n === mod.n - 1);
  const next = MODULES.find(m => m.n === mod.n + 1);
  const prevLink = prev
    ? `<a class="pn-link pn-prev" href="${moduleHref(prev.n, rootPrefix)}"><span class="pn-dir">Previous</span><span class="pn-title">Module ${prev.n}: ${prev.short}</span></a>`
    : `<a class="pn-link pn-prev" href="${rootPrefix}curriculum.html"><span class="pn-dir">Previous</span><span class="pn-title">Curriculum and syllabus</span></a>`;
  const nextLink = next
    ? `<a class="pn-link pn-next" href="${moduleHref(next.n, rootPrefix)}"><span class="pn-dir">Next</span><span class="pn-title">Module ${next.n}: ${next.short}</span></a>`
    : `<a class="pn-link pn-next" href="${rootPrefix}capstone.html"><span class="pn-dir">Next</span><span class="pn-title">Capstone portfolio</span></a>`;
  return `<nav class="prevnext prevnext-${position}" aria-label="Lesson navigation">${prevLink}${nextLink}</nav>`;
}

function buildModulePage(mod) {
  const rootPrefix = '../';
  const usedIds = new Set();
  const raw = readCourseFile('modules/' + mod.src);
  const titleMatch = raw.match(/^# Module \d+:\s*(.*)/m);
  const fullTitle = titleMatch ? titleMatch[1].trim() : mod.short;
  const { preamble, sections } = splitSections(raw);
  const domainLine = preamble.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'))[0] || '';
  const hoursMatch = domainLine.match(/Approximately\s+(\d+)\s+hours/i);
  const hours = hoursMatch ? hoursMatch[1] : null;
  const minutes = readingMinutes(raw);
  const domain = DOMAINS.find(d => d.modules.includes(mod.n));

  const numbered = sections.filter(s => classifySection(s.heading) === 'numbered');
  const kcSection = sections.find(s => classifySection(s.heading) === 'kc');
  const kcItems = kcSection ? parseKnowledgeCheck(kcSection.body) : [];

  // In-lesson table of contents
  const tocEntries = [];
  const sectionHtmlParts = [];

  for (const s of sections) {
    const kind = classifySection(s.heading);
    const id = (() => {
      let base = slugify(s.heading) || kind;
      let unique = base, i = 2;
      while (usedIds.has(unique)) unique = `${base}-${i++}`;
      usedIds.add(unique);
      return unique;
    })();
    const headingHtml = mdToHtml('## ' + s.heading, rootPrefix, new Set()).replace(/<h2[^>]*>/, '').replace('</h2>', '').trim();

    if (kind === 'objectives') {
      sectionHtmlParts.push(`<section class="objectives" id="${id}" aria-labelledby="${id}-h">
<h2 id="${id}-h">Learning objectives</h2>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    } else if (kind === 'why') {
      sectionHtmlParts.push(`<section class="callout callout-why" id="${id}">
<h2>${headingHtml}</h2>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    } else if (kind === 'numbered') {
      tocEntries.push({ id, label: s.heading });
      sectionHtmlParts.push(`<section class="lesson-section" id="${id}">
<h2>${headingHtml}</h2>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    } else if (kind === 'worked' || kind === 'activity' || kind === 'ai') {
      const label = kind === 'worked' ? 'Worked example' : kind === 'activity' ? 'Applied activity' : 'AI-use focus';
      const cls = kind === 'worked' ? 'card-worked' : kind === 'activity' ? 'card-activity' : 'card-ai';
      tocEntries.push({ id, label });
      // Avoid a kicker that duplicates the heading: keep the kicker as the card
      // label and reduce the heading to its distinctive remainder, if any.
      let headline = '';
      if (kind === 'worked') {
        const rest = s.heading.replace(/^Worked example:\s*/i, '');
        headline = rest && rest !== s.heading ? rest[0].toUpperCase() + rest.slice(1) : '';
      } else if (kind === 'activity') {
        const par = s.heading.match(/\(([^)]+)\)/);
        headline = par ? par[1][0].toUpperCase() + par[1].slice(1) : '';
      }
      sectionHtmlParts.push(`<section class="feature-card ${cls}" id="${id}" aria-label="${label}">
<span class="card-kicker">${label}</span>
${headline ? `<h2>${escapeHtml(headline)}</h2>` : `<h2 class="visually-hidden">${label}</h2>`}
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    } else if (kind === 'kc') {
      tocEntries.push({ id, label: 'Knowledge check' });
      sectionHtmlParts.push(`<section class="knowledge-check" id="${id}">
<h2>Knowledge check</h2>
${renderKnowledgeCheck(kcItems, rootPrefix, usedIds)}
</section>`);
    } else if (kind === 'readings') {
      tocEntries.push({ id, label: 'Key readings' });
      sectionHtmlParts.push(`<section class="key-readings" id="${id}">
<h2>Key readings</h2>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    } else if (kind === 'capstone') {
      sectionHtmlParts.push(`<section class="callout callout-capstone" id="${id}">
<h2>Connection to the capstone</h2>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    } else {
      sectionHtmlParts.push(`<section class="lesson-section" id="${id}">
<h2>${headingHtml}</h2>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    }
  }

  const toc = tocEntries.length
    ? `<nav class="lesson-toc" aria-label="In this module"><span class="lesson-toc-head">In this module</span><ol>` +
      tocEntries.map(t => `<li><a href="#${t.id}">${escapeHtml(t.label)}</a></li>`).join('') + `</ol></nav>`
    : '';

  const meta = [
    `Module ${mod.n} of 15`,
    `Domain ${domain.key}`,
    hours ? `approximately ${hours} hours of structured effort` : null,
    `about ${minutes} minutes of core reading`,
    `${kcItems.length} knowledge-check questions`,
  ].filter(Boolean).map(x => `<span>${x}</span>`).join('<span class="meta-sep" aria-hidden="true">&middot;</span>');

  const content = `
<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>
  <li><a href="../index.html">${SITE_NAME}</a></li>
  <li><a href="../curriculum.html">Curriculum</a></li>
  <li aria-current="page">Module ${mod.n}</li>
</ol></nav>
${prevNextNav(mod, rootPrefix, 'top')}
<article class="lesson" data-module="${moduleId(mod.n)}">
<header class="lesson-header">
  <p class="lesson-meta">${meta}</p>
  <h1>${escapeHtml(fullTitle)}</h1>
  <p class="lesson-domain">${escapeHtml(domainLine)}</p>
</header>
${toc}
${sectionHtmlParts.join('\n')}
<div class="lesson-complete">
  <button class="btn btn-complete" data-complete="${moduleId(mod.n)}" type="button">Mark module ${mod.n} as complete</button>
  <span class="lesson-complete-status" role="status"></span>
</div>
</article>
${prevNextNav(mod, rootPrefix, 'bottom')}`;

  return shell({
    title: `Module ${mod.n}: ${fullTitle}`,
    description: `BCMAEP Module ${mod.n}: ${fullTitle}. Domain ${domain.key} lesson with objectives, worked example, applied activity, and knowledge check.`,
    rootPrefix,
    activeHref: `modules/module-${String(mod.n).padStart(2, '0')}.html`,
    contentHtml: content,
    bodyClass: 'page-lesson',
  });
}

// ---------------------------------------------------------------------------
// Generic document pages
// ---------------------------------------------------------------------------

function buildDocPage(doc) {
  const rootPrefix = '';
  const usedIds = new Set();
  let raw = readCourseFile(doc.src);
  // Drop the top-level H1; the template provides the page heading.
  const h1Match = raw.match(/^# (.*)/m);
  const h1 = h1Match ? h1Match[1].trim() : doc.title;
  raw = raw.replace(/^# .*\n/, '');

  let body;
  if (doc.id === 'assessment') {
    body = buildAssessmentBody(raw, rootPrefix, usedIds);
  } else {
    body = mdToHtml(raw, rootPrefix, usedIds);
  }

  // On-this-page TOC from h2 ids.
  const tocItems = [...body.matchAll(/<h2 id="([^"]+)">([\s\S]*?)<\/h2>/g)]
    .map(m => `<li><a href="#${m[1]}">${m[2].replace(/<[^>]+>/g, '')}</a></li>`).join('');
  const toc = tocItems ? `<nav class="lesson-toc" aria-label="On this page"><span class="lesson-toc-head">On this page</span><ol>${tocItems}</ol></nav>` : '';

  const content = `
<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>
  <li><a href="index.html">${SITE_NAME}</a></li>
  <li aria-current="page">${escapeHtml(doc.title)}</li>
</ol></nav>
<article class="document">
<header class="lesson-header"><h1>${escapeHtml(h1)}</h1></header>
${toc}
${body}
</article>`;

  return shell({
    title: doc.title,
    description: `BCMAEP ${doc.title}.`,
    rootPrefix,
    activeHref: doc.out,
    contentHtml: content,
    bodyClass: 'page-document',
  });
}

// Assessment page: convert "### Sample item N (...)" sections into interactive items.
function buildAssessmentBody(raw, rootPrefix, usedIds) {
  const itemBlocks = [];
  // Capture each sample item section.
  const md = raw.replace(/### Sample item (\d+) \(([^)]+)\)\n([\s\S]*?)(?=\n### Sample item |\n## |$)/g, (whole, num, tag, body) => {
    itemBlocks.push({ num: Number(num), tag, body: body.trim() });
    return `\n<!--SAMPLE_ITEM_${num}-->\n`;
  });
  let html = mdToHtml(md, rootPrefix, usedIds);
  for (const item of itemBlocks) {
    html = html.replace(`<!--SAMPLE_ITEM_${item.num}-->`, renderSampleItem(item, rootPrefix, usedIds));
  }
  return html;
}

function renderSampleItem(item, rootPrefix, usedIds) {
  const lines = item.body.split('\n');
  const stemLines = [], options = [];
  let correct = null, rationaleMd = '';
  for (const line of lines) {
    const opt = line.match(/^([A-D])\.\s+(.*)/);
    const cor = line.match(/^Correct:\s*([A-D])\.\s*Rationale:\s*([\s\S]*)/);
    if (opt) options.push({ key: opt[1], text: opt[2].trim() });
    else if (cor) { correct = cor[1]; rationaleMd = cor[2].trim(); }
    else if (!correct) stemLines.push(line);
    else rationaleMd += '\n' + line;
  }
  const stem = mdToHtml(stemLines.join('\n').trim(), rootPrefix, usedIds);
  const rationale = mdToHtml(rationaleMd.trim(), rootPrefix, usedIds);
  const optHtml = options.map(o =>
    `<button type="button" class="quiz-option" data-key="${o.key}"><span class="quiz-key">${o.key}</span><span>${mdToHtml(o.text, rootPrefix, usedIds).replace(/^<p>|<\/p>\s*$/g, '')}</span></button>`
  ).join('\n');
  return `<div class="quiz-item" data-correct="${correct}" id="sample-item-${item.num}">
<p class="quiz-tag">Sample item ${item.num} &middot; ${escapeHtml(item.tag)}</p>
<div class="quiz-stem">${stem}</div>
<div class="quiz-options" role="group" aria-label="Answer options for sample item ${item.num}">
${optHtml}
</div>
<div class="quiz-feedback" hidden>
<p class="quiz-verdict" role="status"></p>
<div class="quiz-rationale"><span class="kc-answer-label">Rationale</span>${rationale}</div>
</div>
</div>`;
}

// ---------------------------------------------------------------------------
// Curriculum page (from the syllabus)
// ---------------------------------------------------------------------------

function buildCurriculumPage() {
  const rootPrefix = '';
  const usedIds = new Set();
  const raw = readCourseFile('01_syllabus_and_learning_map.md');
  const { sections } = splitSections(raw.replace(/^# .*\n/, ''));

  const parts = [];

  // Progress panel
  parts.push(`<section class="progress-panel" id="your-progress">
<h2 id="your-progress-h">Your progress</h2>
<p class="progress-summary" id="progress-summary" role="status">Progress is stored in this browser only.</p>
<div class="progress-track" aria-hidden="true"><div class="progress-fill" id="progress-fill"></div></div>
<div class="progress-actions">
  <a class="btn btn-primary" id="continue-btn" href="modules/module-01.html">Start module 1</a>
  <button class="btn btn-ghost" id="progress-export" type="button">Export progress</button>
  <button class="btn btn-ghost" id="progress-import" type="button">Import progress</button>
  <button class="btn btn-ghost" id="progress-reset" type="button">Reset</button>
</div>
<p class="progress-note">Completion state is saved in your browser (localStorage); no account is required and nothing is transmitted. Export produces a small JSON file you can import in another browser.</p>
</section>`);

  for (const s of sections) {
    const modMatch = s.heading.match(/^Module (\d+):\s*(.*)/);
    const capMatch = /^Capstone/.test(s.heading);
    if (modMatch) {
      const n = Number(modMatch[1]);
      const mod = MODULES.find(m => m.n === n);
      const domain = DOMAINS.find(d => d.modules.includes(n));
      const id = `module-${String(n).padStart(2, '0')}`;
      usedIds.add(id);
      parts.push(`<section class="syllabus-module" id="${id}" data-module="${moduleId(n)}">
<header class="syllabus-module-head">
  <div>
    <p class="syllabus-kicker">Module ${n} <span class="meta-sep" aria-hidden="true">&middot;</span> Domain ${domain.key} <span class="syllabus-check" data-check="${moduleId(n)}"></span></p>
    <h2>${escapeHtml(modMatch[2])}</h2>
  </div>
  <a class="btn btn-primary btn-open" href="${moduleHref(n, rootPrefix)}">Open module ${n}</a>
</header>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    } else if (capMatch) {
      parts.push(`<section class="syllabus-module syllabus-capstone" id="capstone">
<header class="syllabus-module-head">
  <div>
    <p class="syllabus-kicker">Capstone</p>
    <h2>${escapeHtml(s.heading.replace(/^Capstone:\s*/, ''))}</h2>
  </div>
  <a class="btn btn-primary btn-open" href="capstone.html">Open capstone specification</a>
</header>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    } else {
      const id = slugify(s.heading);
      usedIds.add(id);
      parts.push(`<section class="lesson-section" id="${id}">
<h2>${escapeHtml(s.heading)}</h2>
${mdToHtml(s.body, rootPrefix, usedIds)}
</section>`);
    }
  }

  const content = `
<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>
  <li><a href="index.html">${SITE_NAME}</a></li>
  <li aria-current="page">Curriculum and syllabus</li>
</ol></nav>
<article class="document">
<header class="lesson-header">
  <h1>Curriculum and syllabus</h1>
  <p class="lesson-domain">Fifteen modules in five instructional domains (A through E), plus two cross-cutting domains and a capstone portfolio. Approximately 90 to 110 hours of structured effort over a 6-to-12-month window. For each module: competencies, learning objectives, topic outline, applied deliverable, AI-use focus, and assessment linkage.</p>
</header>
${parts.join('\n')}
</article>`;

  return shell({
    title: 'Curriculum and syllabus',
    description: 'The BCMAEP learning map: 15 modules in five instructional domains plus a capstone, with objectives, hours, deliverables, and assessment linkage for each.',
    rootPrefix,
    activeHref: 'curriculum.html',
    contentHtml: content,
    bodyClass: 'page-document page-curriculum',
  });
}

// ---------------------------------------------------------------------------
// Landing page
// ---------------------------------------------------------------------------

function buildIndexPage() {
  const rootPrefix = '';
  const totalHours = MODULES.length ? '90 to 110' : '';

  const domainCards = DOMAINS.map(d => {
    const mods = d.modules.map(n => {
      const m = MODULES.find(x => x.n === n);
      return `<li><a href="${moduleHref(n, rootPrefix)}">Module ${n}: ${m.short}</a></li>`;
    }).join('');
    return `<div class="domain-card">
<p class="domain-key">Domain ${d.key} <span class="domain-weight">${d.weight} of the examination</span></p>
<h3>${d.title}</h3>
<ul class="domain-modules">${mods}</ul>
</div>`;
  }).join('\n');

  const content = `
<section class="hero">
  <div class="hero-inner">
    <p class="hero-kicker">A board-style certification curriculum, version 1.0</p>
    <h1>Board Certified Medical Affairs and Evidence Professional</h1>
    <p class="hero-lede">BCMAEP prepares clinicians and other professionals moving into pharmaceutical, biotechnology, and medical-technology industry roles: medical affairs, medical science liaison, medical information, HEOR, market access, and evidence generation. A structured 15-module curriculum leads to a criterion-referenced board examination and a rubric-scored work-product portfolio. The credential recognizes demonstrated competency, not course attendance.</p>
    <div class="hero-actions">
      <a class="btn btn-primary btn-lg" id="hero-continue" href="curriculum.html">View the curriculum</a>
      <a class="btn btn-outline btn-lg" href="handbook.html">Read the program handbook</a>
    </div>
    <p class="hero-status">Version 1.0 design; accreditation-ready against ISO/IEC 17024, NCCA, and ANSI/IACET, and <a href="accreditation.html">not yet accredited</a>.</p>
  </div>
</section>

<section class="factbar" aria-label="Credential facts">
  <div class="fact"><span class="fact-num">15</span><span class="fact-label">modules in five instructional domains, plus a capstone</span></div>
  <div class="fact"><span class="fact-num">${totalHours}</span><span class="fact-label">hours of structured effort over 6 to 12 months</span></div>
  <div class="fact"><span class="fact-num">150</span><span class="fact-label">scored items on the proctored board examination</span></div>
  <div class="fact"><span class="fact-num">8</span><span class="fact-label">rubric-scored work products in the capstone portfolio</span></div>
  <div class="fact"><span class="fact-num">3</span><span class="fact-label">year recertification cycle with 30 hours of continuing development</span></div>
</section>

<section class="home-section" id="about">
  <h2>About the credential</h2>
  <div class="prose">
    <p>BCMAEP is a board-style certification: a structured 15-module curriculum leads to a criterion-referenced board examination and a rubric-scored work-product portfolio. The credential recognizes demonstrated competency, not course attendance. The curriculum is organized into seven competency domains derived from the responsibilities documented across medical affairs and evidence roles (see the <a href="market-alignment.html">market alignment analysis</a>).</p>
    <p>It covers the full role landscape a career changer enters, from field medical and medical information to HEOR, market access, and evidence generation, and adds depth in three areas: integrated evidence generation planning across the product lifecycle; HEOR, health technology assessment, and market access method fluency; and governed use of artificial intelligence with explicit human accountability. Learners produce eight realistic work products scored with published rubrics, so the credential reflects the ability to produce usable work, not only to answer questions. The design and competency framework are set out in the <a href="handbook.html">program handbook</a>.</p>
  </div>
</section>

<section class="home-section" id="domains">
  <h2>Five instructional domains</h2>
  <p class="home-section-lede">Domains A through E map to the 15 modules; medical governance and compliance (Domain F) and strategy and decision making (Domain G) are embedded across modules and assessed in the portfolio. Domain C carries the largest examination weight (30%).</p>
  <div class="domain-grid">
${domainCards}
  </div>
</section>

<section class="home-section" id="assessment-model">
  <h2>How the credential is earned</h2>
  <div class="path-grid">
    <div class="path-step">
      <span class="path-num">1</span>
      <h3>Complete the curriculum</h3>
      <p>Work the 15 modules in sequence. Each module states measurable objectives, teaches with cited primary sources, and closes with a worked example, an applied activity that produces a draft work product, and a knowledge check. See the <a href="curriculum.html">curriculum and syllabus</a>.</p>
    </div>
    <div class="path-step">
      <span class="path-num">2</span>
      <h3>Pass the board examination</h3>
      <p>A proctored examination of 150 scored items (plus 15 unscored pilot items) over 3 hours, weighted by a published domain blueprint, with a criterion-referenced passing standard set by a modified-Angoff study. See the <a href="assessment.html">examination blueprint and sample items</a>.</p>
    </div>
    <div class="path-step">
      <span class="path-num">3</span>
      <h3>Pass the capstone portfolio</h3>
      <p>Eight work products resembling first-year industry outputs, from a product situation brief to an integrated evidence generation plan, assessed against published analytic rubrics. See the <a href="capstone.html">capstone portfolio specification</a>.</p>
    </div>
  </div>
</section>

<section class="home-section" id="eligibility">
  <h2>Eligibility</h2>
  <div class="prose">
    <p>Two routes, consistent with common credentialing practice for certifications of persons:</p>
    <ul>
      <li><strong>Credentialed route:</strong> a doctoral or professional clinical or scientific degree (for example MD, DO, MBBS, PharmD, PhD, DNP, NP, PA, BDS, DDS, DVM).</li>
      <li><strong>Experience route:</strong> a bachelor's degree plus two years of relevant professional experience in healthcare, life sciences, or a related field.</li>
    </ul>
    <p>The examination and the portfolio, not the entry route, determine the credential.</p>
  </div>
</section>

<section class="home-section" id="how-to-use">
  <h2>How to use this site</h2>
  <div class="prose">
    <p>Read the <a href="handbook.html">program handbook</a> to understand the credential, then work the modules in order from the <a href="curriculum.html">curriculum page</a>. Each module page ends with a knowledge check and a button to mark the module complete; completion state is stored only in your browser, and the curriculum page can export it as a file. The <a href="cases.html">case library</a>, <a href="ai-policy.html">AI-use policy</a>, and <a href="references.html">source register</a> support the applied activities throughout.</p>
  </div>
</section>

<section class="home-section home-status" id="program-status">
  <h2>Program status and integrity</h2>
  <div class="prose">
    <p>This is a version 1.0 curriculum and certification design, prepared July 2026. It has not undergone job-task-analysis validation, item-bank piloting, formal standard setting, or accreditation review. It is designed for alignment with ISO/IEC 17024, the NCCA Standards for the Accreditation of Certification Programs, and the ANSI/IACET Standard, and it is not accredited by any body at this version. The <a href="accreditation.html">accreditation and quality alignment</a> page states precisely what is and is not claimed, and the roadmap to accreditation.</p>
    <p>Every sourced teaching claim carries a hyperlinked citation to a verified authoritative source, consolidated in the <a href="references.html">source register</a>. A <a href="market-alignment.html">market alignment analysis</a> of about 75 real job postings across 39 companies and organizations documents how the curriculum maps to the responsibilities of the roles it prepares for.</p>
  </div>
</section>`;

  return shell({
    title: `${SITE_LONG} (${SITE_NAME})`,
    description: 'A board-style certification curriculum preparing clinicians and other professionals for pharmaceutical industry roles in medical affairs, HEOR, market access, and evidence generation.',
    rootPrefix,
    activeHref: 'index.html',
    contentHtml: content,
    bodyClass: 'page-home',
    withSidebar: true,
  });
}

// ---------------------------------------------------------------------------
// Build
// ---------------------------------------------------------------------------

function writeSiteFile(rel, html) {
  const p = path.join(SITE_ROOT, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, html, 'utf8');
  console.log('wrote', rel, `(${(html.length / 1024).toFixed(0)} KB)`);
}

fs.mkdirSync(path.join(SITE_ROOT, 'modules'), { recursive: true });

writeSiteFile('index.html', buildIndexPage());
writeSiteFile('curriculum.html', buildCurriculumPage());
for (const doc of DOCS) writeSiteFile(doc.out, buildDocPage(doc));
for (const mod of MODULES) writeSiteFile(`modules/module-${String(mod.n).padStart(2, '0')}.html`, buildModulePage(mod));

console.log('done');
