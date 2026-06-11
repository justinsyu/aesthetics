import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const playwrightRoot = process.env.PLAYWRIGHT_CORE_ROOT || path.join(process.env.TEMP || process.env.TMP || ".", "codex-playwright-core");
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(playwrightRoot, "node_modules", "playwright-core"));

const chromePath = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const reportSlug = "4dmt_website_currentness_audit";
const runDate = "May 26, 2026";
const runDateSlug = "05.26.26";
const runFolder = path.join(repoRoot, "competitive_intelligence_reports", reportSlug, "2026-05-26_website_currentness");
const skillRoot = path.join(repoRoot, "_skills_to_install", "cohere-style-ci");

const dirs = {
  assets: path.join(runFolder, "assets"),
  evidence: path.join(runFolder, "screenshots", "evidence"),
  browserExport: path.join(runFolder, "screenshots", "browser-export"),
  renderReview: path.join(runFolder, "screenshots", "render-review"),
  sources: path.join(runFolder, "sources"),
};
for (const dir of Object.values(dirs)) fs.mkdirSync(dir, { recursive: true });

const outputs = {
  html: path.join(runFolder, "report.html"),
  reportPdf: path.join(runFolder, `${reportSlug}-ci-report-${runDateSlug}.pdf`),
  screenshotsPdf: path.join(runFolder, `${reportSlug}-ci-screenshots-${runDateSlug}.pdf`),
  sourceLog: path.join(dirs.sources, "source-log.md"),
  manifest: path.join(dirs.sources, "reference-screenshots.csv"),
};

const backgroundCandidates = [
  path.join(skillRoot, "assets", "tan_slide_background.png"),
  path.join(repoRoot, "outputs", "wet_amd_terminology_comparison", "tan_slide_background.png"),
  path.join(repoRoot, "competitive_intelligence_reports", "ocular_therapeutix_website_currentness_audit", "2026-05-26_website_currentness", "assets", "tan_slide_background.png"),
];
const backgroundSource = backgroundCandidates.find((candidate) => fs.existsSync(candidate));
if (backgroundSource) fs.copyFileSync(backgroundSource, path.join(dirs.assets, "tan_slide_background.png"));

const sourceUrls = {
  fourFrontHome: "https://4frontclinicalstudies.com/",
  fourFrontStudyCenters: "https://4frontclinicalstudies.com/study-centers/",
  fourFrontAbout: "https://4frontclinicalstudies.com/about/",
  fourFrontFaqs: "https://4frontclinicalstudies.com/faqs/",
  ctgov4Front1: "https://clinicaltrials.gov/study/NCT06864988",
  ctgov4Front1Api: "https://clinicaltrials.gov/api/v2/studies/NCT06864988?format=json",
  ctgov4Front2: "https://clinicaltrials.gov/study/NCT07064759",
  ctgov4Front2Api: "https://clinicaltrials.gov/api/v2/studies/NCT07064759?format=json",
  sec10q: "https://www.sec.gov/Archives/edgar/data/1650648/000119312526211939/fdmt-20260331.htm",
};

const references = [
  { ref: 1, source: "4FRONT patient-study site", url: sourceUrls.fourFrontHome, owner: "Live website page / 4DMT study site", evidence: "4FRONT-1 currently-enrolling label and study-center call to action." },
  { ref: 2, source: "ClinicalTrials.gov NCT06864988", url: sourceUrls.ctgov4Front1, owner: "Registry record / 4DMT sponsor", evidence: "4FRONT-1 Phase 3 record status listed as active, not recruiting." },
  { ref: 3, source: "Q1 2026 Form 10-Q", url: sourceUrls.sec10q, owner: "Filed May 2026 / 4DMT", evidence: "4FRONT-1 enrollment completion and expected randomized population above 500 participants." },
  { ref: 4, source: "4FRONT study-center page", url: sourceUrls.fourFrontStudyCenters, owner: "Live website page / 4DMT study site", evidence: "Study-center page lists 4FRONT-1 with recruiting status." },
  { ref: 5, source: "4FRONT About page", url: sourceUrls.fourFrontAbout, owner: "Live website page / 4DMT study site", evidence: "4FRONT-1 joining and eligibility language remains visible." },
  { ref: 6, source: "4FRONT FAQ page", url: sourceUrls.fourFrontFaqs, owner: "Live website page / 4DMT study site", evidence: "FAQ describes 4FRONT-1 eligibility in response to a joining-related question." },
  { ref: 7, source: "ClinicalTrials.gov NCT07064759", url: sourceUrls.ctgov4Front2, owner: "Registry record / 4DMT sponsor", evidence: "4FRONT-2 Phase 3 record status listed as recruiting." },
];

const screenshotSpecs = [
  { id: "source-01-4front-home-currently-enrolling", ref: 1, label: "4FRONT patient site: 4FRONT-1 is labeled currently enrolling", url: sourceUrls.fourFrontHome, find: ["Currently enrolling"], occurrenceHint: "u.s. and canada only" },
  { id: "source-02-ctgov-4front1-active-not-recruiting", ref: 2, label: "ClinicalTrials.gov API: 4FRONT-1 record lists active, not recruiting", url: sourceUrls.ctgov4Front1Api, find: ['"nctId":"NCT06864988"', '"overallStatus":"ACTIVE_NOT_RECRUITING"'] },
  { id: "source-03-sec-4front1-enrollment-complete", ref: 3, label: "4DMT 10-Q: 4FRONT-1 enrollment completed", url: sourceUrls.sec10q, find: ["we announced enrollment completion", "overenrolled and expected to exceed 500 patients randomized"] },
  { id: "source-04-4front-study-centers-recruiting", ref: 4, label: "4FRONT patient site: study-center page lists 4FRONT-1 recruiting", url: sourceUrls.fourFrontStudyCenters, find: ["Recruiting", "4FRONT-1"], occurrenceHint: "4front-1" },
  { id: "source-05-4front-about-who-can-join", ref: 5, label: "4FRONT patient site: 4FRONT-1 eligibility language remains visible", url: sourceUrls.fourFrontAbout, find: ["You may be able to join if you:"], occurrenceHint: "4front-1 you may be able to join" },
  { id: "source-06-4front-faq-can-i-join", ref: 6, label: "4FRONT patient site: FAQ describes 4FRONT-1 joining criteria", url: sourceUrls.fourFrontFaqs, clickText: "Can I join the studies if I’ve already had treatment for wet AMD?", find: ["4FRONT-1 is for people who have never received wet AMD treatments"], occurrenceHint: "4front-1" },
  { id: "source-07-ctgov-4front2-recruiting", ref: 7, label: "ClinicalTrials.gov API: 4FRONT-2 record lists recruiting status", url: sourceUrls.ctgov4Front2Api, find: ['"acronym":"4FRONT-2"', '"overallStatus":"RECRUITING"'] },
];

function rel(filePath) {
  return path.relative(runFolder, filePath).replaceAll(path.sep, "/");
}

function esc(value) {
  return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}

async function dismissBanners(page) {
  for (const label of ["Accept All", "Accept Cookies", "Accept", "Reject All", "Reject", "I Accept", "Allow all cookies", "Use necessary cookies only", "Close"]) {
    const button = page.getByRole("button", { name: label, exact: true }).first();
    if (await button.count().catch(() => 0)) await button.click({ timeout: 1200, force: true }).catch(() => {});
  }
  await page.evaluate(() => {
    const selectors = ["[id*='cookie' i]", "[class*='cookie' i]", "[id*='onetrust' i]", "[class*='onetrust' i]", "[aria-label*='cookie' i]", "[role='dialog']"];
    for (const element of document.querySelectorAll(selectors.join(","))) {
      const style = window.getComputedStyle(element);
      const text = (element.textContent || "").toLowerCase();
      const isOverlay = style.position === "fixed" || style.position === "sticky" || Number(style.zIndex) > 1000;
      if (isOverlay && (text.includes("cookie") || text.includes("privacy"))) element.remove();
    }
  }).catch(() => {});
}

async function highlightAndFrame(page, phrases, occurrenceHint = "") {
  return page.evaluate(({ phrases: rawPhrases, occurrenceHint: rawHint }) => {
    const phrases = rawPhrases.map((value) => value.replace(/\s+/g, " ").trim()).filter(Boolean);
    const hint = rawHint.toLowerCase();
    const rects = [];
    const normalized = (text) => (text || "").replace(/\s+/g, " ").trim();
    const hasVisibleRects = (range) => Array.from(range.getClientRects()).some((rect) => rect.width > 2 && rect.height > 2);
    const inHintScope = (node) => {
      if (!hint) return true;
      let scope = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
      while (scope && scope !== document.body) {
        const box = scope.getBoundingClientRect();
        if ((scope.innerText || "").toLowerCase().includes(hint) && box.height <= Math.max(1100, window.innerHeight * 1.1)) return true;
        scope = scope.parentElement;
      }
      return false;
    };
    const locate = (phrase, scopedOnly = false) => {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const index = normalized(node.nodeValue).toLowerCase().indexOf(phrase.toLowerCase());
        if (index < 0 || (scopedOnly && !inHintScope(node))) continue;
        const directIndex = (node.nodeValue || "").toLowerCase().indexOf(phrase.toLowerCase());
        const range = document.createRange();
        if (directIndex >= 0) {
          range.setStart(node, directIndex);
          range.setEnd(node, directIndex + phrase.length);
        } else {
          range.selectNodeContents(node);
        }
        if (hasVisibleRects(range)) return range;
      }
      return null;
    };
    const mark = (range, index) => {
      const colors = [["rgba(255, 242, 80, .72)", "#c15f00"], ["rgba(184, 216, 255, .72)", "#0b63b6"], ["rgba(215, 255, 95, .66)", "#4d7100"]];
      for (const rect of Array.from(range.getClientRects()).filter((item) => item.width > 2 && item.height > 2)) {
        const overlay = document.createElement("div");
        overlay.setAttribute("data-codex-highlight", "true");
        overlay.style.position = "absolute";
        overlay.style.left = `${window.scrollX + rect.left - 3}px`;
        overlay.style.top = `${window.scrollY + rect.top - 3}px`;
        overlay.style.width = `${rect.width + 6}px`;
        overlay.style.height = `${rect.height + 6}px`;
        overlay.style.background = colors[index % colors.length][0];
        overlay.style.border = `3px solid ${colors[index % colors.length][1]}`;
        overlay.style.borderRadius = "6px";
        overlay.style.pointerEvents = "none";
        overlay.style.mixBlendMode = "multiply";
        overlay.style.zIndex = "2147483647";
        document.body.appendChild(overlay);
        rects.push({ x: window.scrollX + rect.left, y: window.scrollY + rect.top, width: rect.width, height: rect.height });
      }
    };
    phrases.forEach((phrase, index) => {
      const range = locate(phrase, true) || locate(phrase, false);
      if (range) mark(range, index);
    });
    if (!rects.length) return { ok: false, pageTitle: document.title };
    const minX = Math.max(0, Math.min(...rects.map((rect) => rect.x)) - 520);
    const minY = Math.max(0, Math.min(...rects.map((rect) => rect.y)) - 220);
    const maxX = Math.max(...rects.map((rect) => rect.x + rect.width)) + 460;
    const maxY = Math.max(...rects.map((rect) => rect.y + rect.height)) + 280;
    const centerX = Math.max(0, (minX + maxX) / 2 - window.innerWidth / 2);
    const centerY = Math.max(0, (minY + maxY) / 2 - window.innerHeight / 2);
    window.scrollTo(centerX, centerY);
    return {
      ok: true,
      pageTitle: document.title,
      clip: {
        x: Math.max(0, minX - centerX),
        y: Math.max(0, minY - centerY),
        width: Math.min(window.innerWidth, Math.max(900, maxX - minX)),
        height: Math.min(window.innerHeight, Math.max(520, maxY - minY)),
      },
    };
  }, { phrases, occurrenceHint });
}

async function captureScreenshots() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: ["--disable-gpu", "--disable-http2", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check"],
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
    userAgent: "CodexSourceScreenshot/1.0 contact=research@example.com",
    extraHTTPHeaders: { "User-Agent": "CodexSourceScreenshot/1.0 contact=research@example.com" },
    ignoreHTTPSErrors: true,
  });
  const captures = [];
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(45000);
    for (const spec of screenshotSpecs) {
      console.log(`Capturing ${spec.id}`);
      await page.goto(spec.url, { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForLoadState("networkidle", { timeout: 25000 }).catch(() => {});
      await dismissBanners(page);
      if (spec.clickText) {
        await page.getByText(spec.clickText, { exact: true }).first().click({ timeout: 3000 }).catch(() => {});
        await page.waitForTimeout(350);
      }
      await page.evaluate(() => {
        document.documentElement.style.scrollBehavior = "auto";
        document.querySelectorAll("[data-codex-highlight]").forEach((item) => item.remove());
      }).catch(() => {});
      const result = await highlightAndFrame(page, spec.find, spec.occurrenceHint);
      await page.waitForTimeout(350);
      const screenshotPath = path.join(dirs.evidence, `${spec.id}.png`);
      await page.screenshot(result.ok && result.clip ? { path: screenshotPath, clip: result.clip } : { path: screenshotPath, fullPage: false });
      captures.push({ ...spec, screenshotPath, found: result.ok, pageTitle: result.pageTitle });
    }
  } finally {
    await browser.close();
  }
  return captures;
}

function evidenceFigure(item, ref, note) {
  return `<figure class="evidence-card"><div class="evidence-top"><span>Reference ${ref}</span><a href="${esc(item.url)}">${esc(new URL(item.url).hostname)}</a></div><img src="${esc(rel(item.screenshotPath))}" alt="${esc(item.label)}" /><figcaption>${esc(note || item.label)}</figcaption></figure>`;
}

function buildHtml(captures) {
  const byId = Object.fromEntries(captures.map((item) => [item.id, item]));
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>4DMT Website Currentness Audit</title>
<style>
:root{--ink:#10120f;--muted:#5c6257;--paper:#f6f1e8;--paper-2:#ebe4d6;--line:#1b1f17;--lime:#d7ff5f;--shadow:0 18px 48px rgba(16,18,15,.08)}
*{box-sizing:border-box}html,body{margin:0;background:var(--paper);color:var(--ink);scrollbar-width:none}html::-webkit-scrollbar,body::-webkit-scrollbar{display:none}body,*{-webkit-print-color-adjust:exact;print-color-adjust:exact;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit;text-decoration-thickness:1px;text-underline-offset:3px}
.slide{width:100vw;height:100vh;min-height:100vh;overflow:hidden;position:relative;display:flex;align-items:flex-start;padding:34px 0 18px;page-break-after:always;break-after:page;background:var(--paper)}.slide:last-child{page-break-after:auto;break-after:auto}.slide-bg-img{position:absolute;inset:0;z-index:0;width:100%;height:100%;object-fit:cover;opacity:.9}.wrap{width:min(1360px,calc(100vw - 56px));margin:0 auto;position:relative;z-index:1}.eyebrow{display:inline-flex;align-items:center;border:1.4px solid var(--line);padding:8px 12px;border-radius:999px;font-size:14px;font-weight:850;text-transform:uppercase;margin-bottom:18px;background:var(--lime)}
h1,h2,h3,p{margin:0}h1{font-size:66px;line-height:.96;font-weight:560;max-width:1320px}h2{font-size:44px;line-height:.98;font-weight:560;max-width:1400px}h3{font-size:25px;line-height:1.04;font-weight:650}.dek{margin-top:18px;color:var(--muted);font-size:23px;line-height:1.18;max-width:1260px}.section-head{margin-bottom:14px}.section-head p{margin-top:12px;color:var(--muted);font-size:20px;line-height:1.14;max-width:1360px}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.metric,.callout,.evidence-card,.table{border:1.5px solid var(--line);background:rgba(255,250,240,.9);border-radius:22px;box-shadow:var(--shadow);overflow:hidden}.metric{padding:17px;min-height:124px}.num{font-size:46px;line-height:.92;font-weight:400}.label{margin-top:10px;font-size:19px;line-height:1.12;color:var(--muted)}.callout{margin-top:20px;background:#11130f;color:var(--paper);border-color:#11130f;padding:22px 24px}.callout h3{color:var(--lime)}.summary-list{margin:13px 0 0;padding-left:22px;display:grid;gap:9px}.summary-list li{font-size:20px;line-height:1.14;color:rgba(246,241,232,.88)}
.evidence-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.evidence-grid.three{grid-template-columns:repeat(3,1fr)}.evidence-card{margin:0;border-radius:18px}.evidence-top{display:flex;justify-content:space-between;gap:10px;padding:7px 10px;border-bottom:1px solid var(--line);font-size:12px;font-weight:850;text-transform:uppercase}.evidence-top a{text-transform:none;color:var(--muted);font-weight:750;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.evidence-card img{display:block;width:100%;height:350px;object-fit:contain;object-position:center;background:#fff;border-bottom:1px solid var(--line)}.evidence-grid.three .evidence-card img{height:340px}figcaption{margin:0;padding:8px 10px 10px;color:var(--muted);font-size:15px;line-height:1.08}
.row{display:grid;border-bottom:1px solid var(--line);min-height:59px}.row:last-child{border-bottom:0}.row.refs{grid-template-columns:.28fr .9fr 1.15fr 1.9fr}.cell{padding:9px 10px;border-right:1px solid var(--line);font-size:14.5px;line-height:1.08}.cell:last-child{border-right:0}.row.refs .cell:first-child{display:flex;align-items:center;justify-content:center;text-align:center;padding-left:0;padding-right:0}.head .cell{display:flex;align-items:center;background:#11130f;color:var(--paper);font-weight:850;text-transform:uppercase;font-size:14px;white-space:nowrap}.cite{font-size:.58em;vertical-align:super;margin-left:2px;font-weight:900;text-decoration:none}.slide-num{position:absolute;right:40px;bottom:24px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:rgba(16,18,15,.38);font-weight:800;z-index:2}
@page{size:1600px 900px;margin:0}@media print{html,body{width:1600px;height:900px}.slide{width:1600px;height:900px;min-height:900px;padding:34px 0 18px}.wrap{width:1360px}.metric,.callout,.evidence-card,.table{box-shadow:none}}
</style>
</head>
<body>
<article class="slide">
${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
<div class="wrap">
<div class="eyebrow">4DMT web audit | ${runDate}</div>
<h1>4DMT Website Currentness Audit</h1>
<p class="dek">This deck focuses on 4DMT public website statements that differ from the most recently available company or registry sources. The review treats 4FRONT-2 recruitment as a scope boundary, not as a 4FRONT-1 currentness observation.</p>
<div class="grid-4" style="margin-top:24px;">
<div class="metric"><div class="num">1</div><div class="label">High-confidence website-currentness observation.</div></div>
<div class="metric"><div class="num">3</div><div class="label">4FRONT-1 recruitment-oriented website sections reviewed.</div></div>
<div class="metric"><div class="num">500+</div><div class="label">4FRONT-1 randomized participants expected in 4DMT's 10-Q.</div></div>
<div class="metric"><div class="num">1</div><div class="label">Related 4FRONT-2 recruiting statement retained as context.</div></div>
</div>
<div class="callout"><h3>Executive summary</h3><ul class="summary-list">
<li>The 4FRONT patient-study home page labels 4FRONT-1 as currently enrolling and directs viewers to find a study center; ClinicalTrials.gov lists NCT06864988 as active, not recruiting, and 4DMT's current 10-Q states that 4FRONT-1 enrollment was completed.<a class="cite" href="${sourceUrls.fourFrontHome}">1</a><a class="cite" href="${sourceUrls.ctgov4Front1}">2</a><a class="cite" href="${sourceUrls.sec10q}">3</a></li>
<li>The About and FAQ pages retain 4FRONT-1-specific joining and eligibility language. These statements were classified as related recruitment-context evidence rather than separate observations because they share the same underlying 4FRONT-1 enrollment-status comparison.<a class="cite" href="${sourceUrls.fourFrontAbout}">5</a><a class="cite" href="${sourceUrls.fourFrontFaqs}">6</a></li>
<li>4FRONT-2 recruitment language was not classified as a currentness observation because the 4FRONT-2 registry record lists recruiting status.<a class="cite" href="${sourceUrls.ctgov4Front2}">7</a></li>
</ul></div></div><div class="slide-num">1/5</div></article>

<article class="slide">
${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
<div class="wrap"><div class="section-head"><div class="eyebrow">4FRONT-1 recruitment status</div><h2>4FRONT-1 enrollment wording on the patient-study site differs from registry and company status sources</h2><p>The patient-study site presents 4FRONT-1 as currently enrolling. Current registry and company sources describe 4FRONT-1 as active-not-recruiting, with enrollment completed.</p></div>
<div class="evidence-grid three">
${evidenceFigure(byId["source-01-4front-home-currently-enrolling"], 1, "The 4FRONT patient-study home page labels 4FRONT-1 as currently enrolling and links viewers to a study-center finder.")}
${evidenceFigure(byId["source-02-ctgov-4front1-active-not-recruiting"], 2, "ClinicalTrials.gov lists the 4FRONT-1 Phase 3 record as active, not recruiting.")}
${evidenceFigure(byId["source-03-sec-4front1-enrollment-complete"], 3, "4DMT's current 10-Q states that 4FRONT-1 enrollment was completed and expected to exceed 500 randomized participants.")}
</div></div><div class="slide-num">2/5</div></article>

<article class="slide">
${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
<div class="wrap"><div class="section-head"><div class="eyebrow">4FRONT-1 recruitment context</div><h2>Additional 4FRONT-1 pages retain joining and eligibility language after enrollment completion</h2><p>These pages are related evidence for the same 4FRONT-1 currentness observation. They were not counted as independent observations because they depend on the same enrollment-completion comparison.</p></div>
<div class="evidence-grid three">
${evidenceFigure(byId["source-05-4front-about-who-can-join"], 5, "The About page presents 4FRONT-1 joining criteria for people who may be able to join the study.")}
${evidenceFigure(byId["source-06-4front-faq-can-i-join"], 6, "The FAQ page describes 4FRONT-1 eligibility in response to a joining-related question.")}
${evidenceFigure(byId["source-04-4front-study-centers-recruiting"], 4, "The 4FRONT study-center page lists 4FRONT-1 with recruiting status.")}
</div></div><div class="slide-num">3/5</div></article>

<article class="slide">
${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
<div class="wrap"><div class="section-head"><div class="eyebrow">Scope boundary</div><h2>4FRONT-2 recruiting language was not classified as a currentness observation</h2><p>The patient-study site also labels 4FRONT-2 as currently enrolling. This was retained as a scope boundary because the 4FRONT-2 registry record lists recruiting status.</p></div>
<div class="evidence-grid">
${evidenceFigure(byId["source-01-4front-home-currently-enrolling"], 1, "The patient-study site includes currently enrolling labels for the 4FRONT study family.")}
${evidenceFigure(byId["source-07-ctgov-4front2-recruiting"], 7, "ClinicalTrials.gov lists the 4FRONT-2 Phase 3 record as recruiting.")}
</div></div><div class="slide-num">4/5</div></article>

<article class="slide">
${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
<div class="wrap"><div class="section-head"><div class="eyebrow">References 1-7</div><h2>References</h2></div>
<div class="table"><div class="row refs head"><div class="cell">Ref</div><div class="cell">Source</div><div class="cell">Date / Status / Source Owner</div><div class="cell">Evidence Used in Report</div></div>
${references.map((item) => `<div class="row refs"><div class="cell">${item.ref}</div><div class="cell"><a href="${esc(item.url)}">${esc(item.source)}</a></div><div class="cell">${esc(item.owner)}</div><div class="cell">${esc(item.evidence)}</div></div>`).join("\n")}
</div></div><div class="slide-num">5/5</div></article>
</body></html>`;
}

function writeSourceArtifacts(captures) {
  const log = `# 4DMT Website Currentness Review Source Log

Run date: ${runDate}

Scope: Web-only source review of 4DMT public website and study-site statements versus the most recently available official online registry or company sources. Other timing differences were noted only when a public website presented a current claim with wording or values that differed from those sources.

## Included References

${references.map((reference) => {
  const rows = captures.filter((capture) => capture.ref === reference.ref);
  return `${reference.ref}. ${reference.source}
   - URL: ${reference.url}
   - Source owner: ${reference.owner}
   - Evidence used: ${reference.evidence}
${rows.map((capture, index) => `   - Screenshot ${index + 1}: ${rel(capture.screenshotPath)}
     - Highlight status: ${capture.found ? "supporting text highlighted in rendered browser screenshot" : "specified text not located in rendered browser view; screenshot retained for documentation"}`).join("\n")}`;
}).join("\n\n")}
`.trimEnd() + "\n";
  fs.writeFileSync(outputs.sourceLog, log);

  const manifest = ["label,path,caption", ...captures.map((capture, index) => {
    return [JSON.stringify(`Reference ${capture.ref} - evidence ${index + 1}`), JSON.stringify(capture.screenshotPath), JSON.stringify(`${capture.label} | ${capture.url}`)].join(",");
  })].join("\n") + "\n";
  fs.writeFileSync(outputs.manifest, manifest);
}

function runCommand(label, command, args) {
  const result = spawnSync(command, args, { cwd: repoRoot, stdio: "inherit", env: { ...process.env, CHROME_PATH: chromePath.replaceAll("\\", "/") } });
  if (result.status !== 0) throw new Error(`${label} failed with status ${result.status}`);
}

async function main() {
  const captures = await captureScreenshots();
  writeSourceArtifacts(captures);
  fs.writeFileSync(outputs.html, buildHtml(captures));
  runCommand("Export report PDF", process.execPath, [
    path.join(skillRoot, "scripts", "export_html_slides_pdf.mjs"),
    "--input", outputs.html,
    "--output", outputs.reportPdf,
    "--screenshots-dir", dirs.browserExport,
    "--render-check-dir", dirs.renderReview,
  ]);
  runCommand("Assemble screenshot PDF", "python", [
    path.join(skillRoot, "scripts", "assemble_reference_screenshots_pdf.py"),
    "--output", outputs.screenshotsPdf,
    "--manifest", outputs.manifest,
  ]);
  console.log(JSON.stringify({ runFolder, outputs, screenshots: captures.map((item) => ({ id: item.id, found: item.found, path: item.screenshotPath })) }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
