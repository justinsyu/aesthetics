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
const chromePathForExporter = chromePath.replaceAll("\\", "/");
const runDate = "May 26, 2026";
const runDateSlug = "05.26.26";
const reportSlug = "regenxbio_wet_amd_website_currentness_audit";
const runFolder = path.join(repoRoot, "competitive_intelligence_reports", reportSlug, "2026-05-26_website_currentness");

const dirs = {
  assets: path.join(runFolder, "assets"),
  evidence: path.join(runFolder, "screenshots", "evidence"),
  browserExport: path.join(runFolder, "screenshots", "browser-export"),
  renderReview: path.join(runFolder, "screenshots", "render-review"),
  sources: path.join(runFolder, "sources"),
};

for (const dir of Object.values(dirs)) fs.mkdirSync(dir, { recursive: true });

const outputFiles = {
  reportHtml: path.join(runFolder, "report.html"),
  reportPdf: path.join(runFolder, `${reportSlug}-ci-report-${runDateSlug}.pdf`),
  screenshotPdf: path.join(runFolder, `${reportSlug}-ci-screenshots-${runDateSlug}.pdf`),
  sourceLog: path.join(dirs.sources, "source-log.md"),
  screenshotManifest: path.join(dirs.sources, "reference-screenshots.csv"),
};

const skillRoot = path.join(repoRoot, "_skills_to_install", "cohere-style-ci");
const exporterScript = path.join(skillRoot, "scripts", "export_html_slides_pdf.mjs");
const screenshotAssemblerScript = path.join(skillRoot, "scripts", "assemble_reference_screenshots_pdf.py");
const backgroundCandidates = [
  path.join(skillRoot, "assets", "tan_slide_background.png"),
  path.join(repoRoot, "outputs", "wet_amd_terminology_comparison", "tan_slide_background.png"),
  path.join(repoRoot, "competitive_intelligence_reports", "ocular_hypertension_glaucoma", "2026-05-12_1245", "assets", "tan_slide_background.png"),
];
const backgroundSource = backgroundCandidates.find((candidate) => fs.existsSync(candidate));
if (backgroundSource) fs.copyFileSync(backgroundSource, path.join(dirs.assets, "tan_slide_background.png"));

const sourceUrls = {
  patientWetAmd: "https://www.regenxbio.com/patients-families/wet-amd/",
  programPage: "https://www.regenxbio.com/therapeutic-programs/rgx-314/",
  sec10q: "https://www.sec.gov/Archives/edgar/data/1590877/000119312526222804/rgnx-20260331.htm",
  ctgovAaviate: "https://clinicaltrials.gov/study/NCT04514653",
};

const screenshotSpecs = [
  {
    id: "source-01-patient-page-atmosphere-ascent-enrolling",
    ref: 1,
    label: "REGENXBIO patient wet AMD page: ATMOSPHERE and ASCENT active/enrolling wording",
    source: "Patient wet AMD page",
    url: sourceUrls.patientWetAmd,
    owner: "Live website page / REGENXBIO",
    evidence: "Patient page states REGENXBIO is currently enrolling patients and that ATMOSPHERE/ASCENT are active and enrolling.",
    find: [
      "REGENXBIO is currently enrolling patients with wet AMD in several clinical trials:",
      "These trials are active and enrolling patients.",
    ],
  },
  {
    id: "source-02-sec-atmosphere-ascent-completed",
    ref: 2,
    label: "Q1 2026 Form 10-Q: ATMOSPHERE and ASCENT enrollment completed in October 2025",
    source: "Q1 2026 Form 10-Q",
    url: sourceUrls.sec10q,
    owner: "SEC filing / REGENXBIO",
    evidence: "Enrollment in ATMOSPHERE and ASCENT was completed in October 2025; topline data expected in Q4 2026.",
    find: [
      "Sura-vec for Treatment of Wet AMD",
      "Enrollment in the ATMOSPHERE",
      "was completed in October 2025",
      "Topline data from these trials are expected to be shared in the fourth quarter of 2026",
    ],
  },
  {
    id: "source-03-patient-page-aaviate-enrolling",
    ref: 3,
    label: "REGENXBIO patient wet AMD page: AAVIATE active/enrolling wording",
    source: "Patient wet AMD page",
    url: sourceUrls.patientWetAmd,
    owner: "Live website page / REGENXBIO",
    evidence: "Patient page states AAVIATE is active and enrolling patients and links to NCT04514653.",
    find: [
      "AAVIATE",
      "ABBV-RGX-314 in patients with wet AMD, is active and enrolling patients",
      "NCT04514653",
    ],
  },
  {
    id: "source-04-sec-aaviate-completed",
    ref: 4,
    label: "Q1 2026 Form 10-Q: AAVIATE enrollment completed",
    source: "Q1 2026 Form 10-Q",
    url: sourceUrls.sec10q,
    owner: "SEC filing / REGENXBIO",
    evidence: "Enrollment of the AAVIATE trial has been completed.",
    find: [
      "The AAVIATE",
      "Enrollment of the AAVIATE trial has been completed",
    ],
  },
  {
    id: "source-05-ctgov-aaviate-active-not-recruiting",
    ref: 5,
    label: "ClinicalTrials.gov NCT04514653: AAVIATE active, not recruiting with 146 actual participants",
    source: "ClinicalTrials.gov NCT04514653",
    url: sourceUrls.ctgovAaviate,
    owner: "Current ClinicalTrials.gov study page / ClinicalTrials.gov",
    evidence: "AAVIATE status shown as active, not recruiting, with enrollment listed as 146 actual participants.",
    find: [
      "Active, not recruiting",
      "Enrollment",
      "146",
    ],
  },
  {
    id: "source-06-program-page-context",
    ref: 6,
    label: "REGENXBIO ABBV-RGX-314 page: wet AMD program and trial context",
    source: "Therapeutic-program page",
    url: sourceUrls.programPage,
    owner: "Live website page / REGENXBIO",
    evidence: "Program page identifies sura-vec/ABBV-RGX-314 developed with AbbVie for wet AMD/DR; ATMOSPHERE, ASCENT, and AAVIATE listed.",
    find: [
      "REGENXBIO is developing surabgene lomparvovec",
      "in collaboration with AbbVie",
      "The Phase II AAVIATE",
    ],
  },
];

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function rel(filePath) {
  return path.relative(runFolder, filePath).replaceAll(path.sep, "/");
}

function runCommand(label, command, args, options = {}) {
  console.log(`${label}: ${command} ${args.map((arg) => (/\s/.test(arg) ? JSON.stringify(arg) : arg)).join(" ")}`);
  const result = spawnSync(command, args, {
    cwd: options.cwd || repoRoot,
    encoding: "utf8",
    env: { ...process.env, CHROME_PATH: chromePathForExporter, ...(options.env || {}) },
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.status !== 0) throw new Error(`${label} failed with exit code ${result.status ?? "unknown"}`);
}

async function dismissBanners(page) {
  for (const label of ["Accept All", "Accept Cookies", "Accept", "Reject All", "Reject", "I Accept", "Close"]) {
    const button = page.getByText(label, { exact: true }).first();
    if (await button.count().catch(() => 0)) await button.click({ timeout: 1200, force: true }).catch(() => {});
  }
  await page.evaluate(() => {
    const selectors = [
      "[id*='cookie' i]",
      "[class*='cookie' i]",
      "[id*='onetrust' i]",
      "[class*='onetrust' i]",
      "[aria-label*='cookie' i]",
      "[class*='privacy' i]",
      "[id*='privacy' i]",
      "[role='dialog']",
    ];
    for (const element of document.querySelectorAll(selectors.join(","))) {
      const style = window.getComputedStyle(element);
      if (style.position === "fixed" || style.position === "sticky" || Number(style.zIndex) > 1000) element.remove();
    }
  });
}

async function highlightAndFrame(page, phrases) {
  return page.evaluate((rawPhrases) => {
    document.querySelectorAll("[data-codex-highlight]").forEach((el) => el.remove());
    const phrases = rawPhrases.map((item) => item.replace(/\s+/g, " ").trim()).filter(Boolean);
    const rects = [];
    const normalized = (text) => text.replace(/\s+/g, " ").trim();
    const visibleRects = (range) => Array.from(range.getClientRects()).filter((rect) => rect.width > 2 && rect.height > 2);
    const locate = (phrase) => {
      const lowerPhrase = phrase.toLowerCase();
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const text = node.nodeValue || "";
        const directIndex = text.toLowerCase().indexOf(lowerPhrase);
        if (directIndex >= 0) {
          const range = document.createRange();
          range.setStart(node, directIndex);
          range.setEnd(node, directIndex + phrase.length);
          if (visibleRects(range).length) return range;
        }
        if (normalized(text).toLowerCase().includes(lowerPhrase)) {
          const range = document.createRange();
          range.selectNodeContents(node);
          if (visibleRects(range).length) return range;
        }
      }
      return null;
    };
    const colors = [
      ["rgba(255, 242, 80, .72)", "#c15f00"],
      ["rgba(184, 216, 255, .72)", "#0b63b6"],
      ["rgba(215, 255, 95, .66)", "#4d7100"],
      ["rgba(255, 211, 224, .7)", "#a02f62"],
    ];
    phrases.forEach((phrase, index) => {
      const range = locate(phrase);
      if (!range) return;
      for (const rect of visibleRects(range)) {
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
    });
    if (!rects.length) return { ok: false, pageTitle: document.title };
    const minX = Math.max(0, Math.min(...rects.map((rect) => rect.x)) - 360);
    const minY = Math.max(0, Math.min(...rects.map((rect) => rect.y)) - 320);
    const maxX = Math.max(...rects.map((rect) => rect.x + rect.width)) + 460;
    const maxY = Math.max(...rects.map((rect) => rect.y + rect.height)) + 260;
    const centerX = Math.max(0, (minX + maxX) / 2 - window.innerWidth / 2);
    const centerY = Math.max(0, (minY + maxY) / 2 - window.innerHeight / 2);
    window.scrollTo(centerX, centerY);
    const clipX = Math.max(0, minX - centerX);
    const clipY = Math.max(0, minY - centerY);
    return {
      ok: true,
      pageTitle: document.title,
      clip: {
        x: clipX,
        y: clipY,
        width: Math.min(window.innerWidth - clipX, Math.max(900, maxX - minX)),
        height: Math.min(window.innerHeight - clipY, Math.max(620, maxY - minY)),
      },
    };
  }, phrases);
}

async function captureScreenshots() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: ["--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check", "--disable-http2"],
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
    userAgent: "linkedin-posts-mac CI evidence capture contact=justin@example.com",
    extraHTTPHeaders: {
      "User-Agent": "linkedin-posts-mac CI evidence capture contact=justin@example.com",
      "Accept-Language": "en-US,en;q=0.9",
    },
  });
  const outputs = [];
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(45000);
    for (const spec of screenshotSpecs) {
      console.log(`Capturing ${spec.id}`);
      await page.goto(spec.url, { waitUntil: "commit", timeout: 45000 });
      await page.waitForLoadState("domcontentloaded", { timeout: 20000 }).catch(() => {});
      await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
      await dismissBanners(page);
      const result = await highlightAndFrame(page, spec.find);
      await page.waitForTimeout(300);
      const screenshotPath = path.join(dirs.evidence, `${spec.id}.png`);
      await page.screenshot(result.ok && result.clip ? { path: screenshotPath, clip: result.clip } : { path: screenshotPath, fullPage: false });
      outputs.push({ ...spec, screenshotPath, found: result.ok, pageTitle: result.pageTitle });
    }
  } finally {
    await browser.close();
  }
  return outputs;
}

function evidenceFigure(item, note) {
  return `
    <figure class="evidence-card">
      <div class="evidence-top"><span>Reference ${item.ref}</span><a href="${esc(item.displayUrl || item.url)}">${esc(new URL(item.displayUrl || item.url).hostname)}</a></div>
      <img src="${esc(rel(item.screenshotPath))}" alt="${esc(item.label)}" />
      <figcaption>${esc(note || item.evidence)}</figcaption>
    </figure>`;
}

function buildHtml(captures) {
  const byId = Object.fromEntries(captures.map((item) => [item.id, item]));
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>REGENXBIO Wet AMD Website Currentness Audit</title>
  <style>
    :root {
      --ink: #10120f; --muted: #5c6257; --paper: #f6f1e8; --paper-2: #ebe4d6;
      --line: #1b1f17; --lime: #d7ff5f; --shadow: 0 18px 48px rgba(16,18,15,.08); --radius: 24px;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; background: var(--paper); color: var(--ink); scrollbar-width: none; }
    html::-webkit-scrollbar, body::-webkit-scrollbar { display: none; }
    body, *, *::before, *::after { -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    a { color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px; }
    .slide { width: 100vw; height: 100vh; min-height: 100vh; overflow: hidden; position: relative; display: flex; align-items: flex-start; padding: 36px 0 20px; page-break-after: always; break-after: page; background: var(--paper); }
    .slide:last-child { page-break-after: auto; break-after: auto; }
    .slide-bg-img { position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; pointer-events: none; user-select: none; opacity: .9; }
    .wrap { width: min(1360px, calc(100vw - 56px)); margin: 0 auto; position: relative; z-index: 1; }
    .evidence-slide { padding: 24px 0 14px; }
    .evidence-slide .wrap { width: min(1460px, calc(100vw - 34px)); }
    .eyebrow { display: inline-flex; align-items: center; border: 1.4px solid var(--line); padding: 8px 12px; border-radius: 999px; font-size: 15px; font-weight: 850; text-transform: uppercase; margin-bottom: 22px; background: var(--lime); }
    h1, h2, h3, p { margin: 0; }
    h1 { font-size: 67px; line-height: .95; font-weight: 560; max-width: 1340px; }
    h2 { font-size: 46px; line-height: .98; font-weight: 560; max-width: 1460px; }
    h3 { font-size: 27px; line-height: 1.04; font-weight: 650; }
    .dek { margin-top: 22px; color: var(--muted); font-size: 23px; line-height: 1.18; max-width: 1280px; }
    .section-head { margin-bottom: 14px; }
    .section-head p { margin-top: 24px; color: var(--muted); font-size: 20px; line-height: 1.12; max-width: 1440px; }
    .references-slide .section-head { margin-bottom: 28px; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 20px; }
    .metric, .table, .callout, .evidence-card { border: 1.5px solid var(--line); background: rgba(255,250,240,.9); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
    .callout { background: #11130f; color: var(--paper); border-color: #11130f; padding: 18px 22px; margin-top: 18px; }
    .callout h3 { color: var(--lime); }
    .callout li { color: rgba(246,241,232,.86); }
    .metric { min-height: 124px; padding: 16px; }
    .num { font-size: 44px; line-height: .92; font-weight: 400; }
    .label { margin-top: 8px; font-size: 18px; line-height: 1.1; color: var(--muted); }
    .summary-list { margin: 14px 0 0; padding-left: 22px; display: grid; gap: 7px; }
    .summary-list li { font-size: 22px; line-height: 1.15; }
    .evidence-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; align-items: stretch; }
    .evidence-grid.three { grid-template-columns: repeat(3, 1fr); }
    .evidence-card { display: flex; flex-direction: column; min-height: 0; margin: 0; background: rgba(255,250,240,.92); border-radius: 18px; }
    .evidence-top { display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 7px 10px; border-bottom: 1px solid var(--line); background: var(--paper-2); font-size: 12px; font-weight: 800; text-transform: uppercase; }
    .evidence-top a { text-transform: none; font-weight: 700; color: var(--muted); }
    .evidence-card img { display: block; width: 100%; height: 420px; object-fit: contain; object-position: center; background: white; border-bottom: 1px solid rgba(16,18,15,.22); }
    .evidence-grid.three .evidence-card img { height: 336px; }
    figcaption { margin: 0; padding: 8px 10px 9px; color: var(--muted); font-size: 17px; line-height: 1.08; }
    .evidence-grid.three figcaption { font-size: 14px; line-height: 1.08; }
    .table { display: grid; }
    .row { display: grid; border-bottom: 1px solid var(--line); min-height: 70px; }
    .row:last-child { border-bottom: 0; }
    .row.refs { grid-template-columns: .28fr .92fr 1.1fr 1.85fr; min-height: 56px; }
    .row.refs.head { min-height: 38px; }
    .cell { padding: 12px; border-right: 1px solid var(--line); font-size: 17px; line-height: 1.13; }
    .row.refs .cell { display: flex; align-items: center; padding: 7px 10px; font-size: 14.4px; line-height: 1.08; }
    .row.refs .cell:first-child { justify-content: center; text-align: center; padding-left: 0; padding-right: 0; }
    .cell:last-child { border-right: 0; }
    .head .cell { background: #11130f; color: var(--paper); font-weight: 850; text-transform: uppercase; font-size: 16px; white-space: nowrap; }
    .row.refs.head .cell { align-items: center; justify-content: flex-start; padding-top: 5px; padding-bottom: 5px; font-size: 14px; }
    .row.refs.head .cell:first-child { justify-content: center; }
    .cite { font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 900; text-decoration: none; }
    .slide-num { position: absolute; right: 40px; bottom: 24px; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: rgba(16,18,15,.38); font-weight: 800; z-index: 2; }
    @page { size: 1600px 900px; margin: 0; }
    @media print {
      html, body { width: 1600px; height: 900px; }
      .slide { width: 1600px; height: 900px; min-height: 900px; padding: 36px 0 20px; }
      .slide.evidence-slide { padding: 24px 0 14px; }
      .wrap { width: 1360px; }
      .evidence-slide .wrap { width: 1460px; }
      .metric, .table, .callout, .evidence-card { box-shadow: none; }
    }
    @media screen and (max-width: 900px) { .slide { width: 1600px; height: 900px; } }
  </style>
</head>
<body>
  <article class="slide title-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="eyebrow">WEBSITE AUDIT | MAY 26, 2026</div>
      <h1>REGENXBIO Wet AMD Website Currentness Audit</h1>
      <p class="dek">This deck reviews REGENXBIO public wet AMD website statements for ABBV-RGX-314/sura-vec against the current Form 10-Q and ClinicalTrials.gov record data. Findings are limited to website enrollment-status wording that differs from later official source language.</p>
      <div class="grid-4">
        <div class="metric"><div class="num">2</div><div class="label">Evidence-supported website-currentness observations</div></div>
        <div class="metric"><div class="num">3</div><div class="label">Wet AMD trials named on the patient page: ATMOSPHERE, ASCENT, and AAVIATE</div></div>
        <div class="metric"><div class="num">Oct 2025</div><div class="label">Current 10-Q timing for completed ATMOSPHERE and ASCENT enrollment</div></div>
        <div class="metric"><div class="num">146</div><div class="label">AAVIATE actual enrollment listed in the current registry record</div></div>
      </div>
      <div class="callout">
        <h3>Executive summary</h3>
        <ul class="summary-list">
          <li>The patient wet AMD page states that REGENXBIO is currently enrolling patients with wet AMD in several clinical trials and that ATMOSPHERE and ASCENT are active and enrolling; the current filing states enrollment in those pivotal trials was completed in October 2025.<a class="cite" href="${sourceUrls.patientWetAmd}">1</a><a class="cite" href="${sourceUrls.sec10q}">2</a></li>
          <li>The same patient page states that AAVIATE is active and enrolling patients; the current filing states enrollment of AAVIATE has been completed, and the current registry record lists ACTIVE_NOT_RECRUITING with 146 actual participants.<a class="cite" href="${sourceUrls.patientWetAmd}">3</a><a class="cite" href="${sourceUrls.sec10q}">4</a><a class="cite" href="${sourceUrls.ctgovAaviate}">5</a></li>
          <li>Context: the therapeutic-program page identifies sura-vec/ABBV-RGX-314 as a wet AMD/DR program developed with AbbVie and lists ATMOSPHERE, ASCENT, and AAVIATE; this context was not treated as a finding.<a class="cite" href="${sourceUrls.programPage}">6</a></li>
        </ul>
      </div>
    </div>
    <div class="slide-num">1/4</div>
  </article>

  <article class="slide evidence-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">ATMOSPHERE and ASCENT status</div>
        <h2>Patient-page active/enrolling wording differs from the current filing's completed-enrollment statement</h2>
        <p>The observation is limited to enrollment-status wording. The current filing states that ATMOSPHERE and ASCENT enrollment was completed in October 2025 and that topline data are expected in the fourth quarter of 2026.</p>
      </div>
      <div class="evidence-grid">
        ${evidenceFigure(byId["source-01-patient-page-atmosphere-ascent-enrolling"], "The patient wet AMD page states that REGENXBIO is currently enrolling wet AMD patients and that ATMOSPHERE and ASCENT are active and enrolling.")}
        ${evidenceFigure(byId["source-02-sec-atmosphere-ascent-completed"], "The current 10-Q states that ATMOSPHERE and ASCENT enrollment was completed in October 2025.")}
      </div>
    </div>
    <div class="slide-num">2/4</div>
  </article>

  <article class="slide evidence-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">AAVIATE status</div>
        <h2>Patient-page AAVIATE enrolling wording differs from both filing and registry status language</h2>
        <p>The current filing states enrollment of the AAVIATE trial has been completed. ClinicalTrials.gov lists NCT04514653 as ACTIVE_NOT_RECRUITING with actual enrollment of 146.</p>
      </div>
      <div class="evidence-grid three">
        ${evidenceFigure(byId["source-03-patient-page-aaviate-enrolling"], "The patient page states that AAVIATE is active and enrolling patients and links to NCT04514653.")}
        ${evidenceFigure(byId["source-04-sec-aaviate-completed"], "The current 10-Q states that enrollment of the AAVIATE trial has been completed.")}
        ${evidenceFigure(byId["source-05-ctgov-aaviate-active-not-recruiting"], "The current ClinicalTrials.gov study page shows active, not recruiting status and 146 actual participants.")}
      </div>
    </div>
    <div class="slide-num">3/4</div>
  </article>

  <article class="slide references-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">References 1-6</div>
        <h2>References</h2>
      </div>
      <div class="table">
        <div class="row refs head"><div class="cell">Ref</div><div class="cell">Source</div><div class="cell">Date / Status / Source Owner</div><div class="cell">Evidence Used in Report</div></div>
        ${captures.map((item) => `<div class="row refs"><div class="cell">${item.ref}</div><div class="cell"><a href="${esc(item.displayUrl || item.url)}">${esc(item.source)}</a></div><div class="cell">${esc(item.owner)}</div><div class="cell">${esc(item.evidence)}</div></div>`).join("\n        ")}
      </div>
    </div>
    <div class="slide-num">4/4</div>
  </article>
</body>
</html>`;
}

function writeSourceArtifacts(captures) {
  const sourceLog = `# REGENXBIO Wet AMD Website Currentness Audit Source Log

Scope: Web-only source review of REGENXBIO public wet AMD website statements for ABBV-RGX-314/sura-vec versus the current Form 10-Q and ClinicalTrials.gov record data. Normal source lag was not treated as a website-currentness observation unless the public website itself presented current enrollment-status wording that differed from later official source language.

## Included References

${captures.map((item) => `${item.ref}. ${item.label}
   - URL: ${item.displayUrl || item.url}
   - Screenshot: ${rel(item.screenshotPath)}
   - Highlight status: ${item.found ? "text highlighted in rendered browser screenshot" : "requested highlight text not found; screenshot retained for review"}`).join("\n\n")}
`;
  fs.writeFileSync(outputFiles.sourceLog, sourceLog);
  const rows = ["label,path,caption"];
  for (const item of captures) rows.push([JSON.stringify(`Reference ${item.ref} - evidence`), JSON.stringify(rel(item.screenshotPath)), JSON.stringify(item.label)].join(","));
  fs.writeFileSync(outputFiles.screenshotManifest, rows.join("\n") + "\n");
}

function exportArtifacts() {
  runCommand("Export REGENXBIO report PDF", process.execPath, [
    exporterScript,
    "--input", outputFiles.reportHtml,
    "--output", outputFiles.reportPdf,
    "--screenshots-dir", dirs.browserExport,
    "--render-check-dir", dirs.renderReview,
    "--chrome", chromePathForExporter,
  ]);
  runCommand("Assemble REGENXBIO screenshot PDF", "python", [
    screenshotAssemblerScript,
    "--output", outputFiles.screenshotPdf,
    "--manifest", outputFiles.screenshotManifest,
  ], { cwd: runFolder });
}

async function main() {
  const captures = await captureScreenshots();
  writeSourceArtifacts(captures);
  fs.writeFileSync(outputFiles.reportHtml, buildHtml(captures));
  exportArtifacts();
  console.log(JSON.stringify({
    runFolder,
    report: outputFiles.reportHtml,
    reportPdf: outputFiles.reportPdf,
    screenshotPdf: outputFiles.screenshotPdf,
    slideCount: 4,
    screenshots: captures.map((item) => ({ id: item.id, found: item.found, path: item.screenshotPath })),
  }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
