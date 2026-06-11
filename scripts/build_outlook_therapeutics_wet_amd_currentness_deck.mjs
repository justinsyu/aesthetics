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
const reportSlug = "outlook_therapeutics_wet_amd_currentness_audit";
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
  path.join(repoRoot, "competitive_intelligence_reports", "ocular_therapeutix_web_discrepancy_audit", "2026-05-26_website_currentness", "assets", "tan_slide_background.png"),
  path.join(repoRoot, "competitive_intelligence_reports", "ocular_hypertension_glaucoma", "2026-05-12_1245", "assets", "tan_slide_background.png"),
];
const backgroundSource = backgroundCandidates.find((candidate) => fs.existsSync(candidate));
if (backgroundSource) fs.copyFileSync(backgroundSource, path.join(dirs.assets, "tan_slide_background.png"));

const sourceUrls = {
  home: "https://outlooktherapeutics.com/",
  clinicalProgress: "https://outlooktherapeutics.com/lytenava-clinical-progress/",
  q2fy2026: "https://www.sec.gov/Archives/edgar/data/1649989/000110465926062865/tm2614868d1_ex99-1.htm",
  crl2025: "https://www.sec.gov/Archives/edgar/data/1649989/000110465926000066/tm2534608d1_ex99-1.htm",
  resubmission2025: "https://www.sec.gov/Archives/edgar/data/1649989/000110465925078622/tm2523462d1_ex99-1.htm",
};

const screenshotSpecs = [
  {
    id: "source-01-home-bla-resubmitted",
    ref: 1,
    label: "Outlook homepage: U.S. BLA resubmission wording",
    url: sourceUrls.home,
    owner: "Live website page / Outlook Therapeutics",
    evidence: "Homepage U.S. BLA-resubmission sentence for ONS-5010/LYTENAVA.",
    find: ["In the United States, ONS-5010/LYTENAVA", "a BLA has been resubmitted to the FDA"],
  },
  {
    id: "source-02-crl-current-status",
    ref: 2,
    label: "Outlook regulatory update exhibit: FDA issued a CRL for the resubmitted BLA",
    url: sourceUrls.crl2025,
    owner: "December 31, 2025 / Outlook Therapeutics exhibit",
    evidence: "FDA CRL for the resubmitted ONS-5010/LYTENAVA BLA.",
    find: ["December 31, 2025", "FDA has issued a complete response letter (CRL)"],
  },
  {
    id: "source-03-q2fy2026-regulatory-status",
    ref: 3,
    label: "Outlook Q2 FY2026 exhibit: formal dispute resolution status",
    url: sourceUrls.q2fy2026,
    owner: "May 15, 2026 / Outlook Therapeutics exhibit",
    evidence: "Formal dispute resolution meeting and May 2026 FDA-decision expectation.",
    find: ["May 15, 2026", "conducted its formal dispute resolution meeting", "expects a formal decision from the FDA in May 2026"],
  },
  {
    id: "source-04-home-launch-timing",
    ref: 4,
    label: "Outlook homepage: EU/UK launch described as expected in Q2 2025",
    url: sourceUrls.home,
    owner: "Live website page / Outlook Therapeutics",
    evidence: "Homepage EU/UK launch timing states expected second quarter of calendar 2025.",
    find: ["working to initiate its commercial launch", "expected in the second quarter of calendar 2025"],
  },
  {
    id: "source-05-commercial-launch",
    ref: 5,
    label: "Outlook Q2 FY2026 exhibit: commercial launch commenced in Germany and the UK",
    url: sourceUrls.q2fy2026,
    owner: "May 15, 2026 / Outlook Therapeutics exhibit",
    evidence: "Commercial launch commenced in Germany and the UK for wet AMD.",
    find: ["commenced commercial launch of LYTENAVA", "in Germany and the UK as a treatment for wet AMD"],
  },
  {
    id: "source-06-q2fy2026-commercial-rollout",
    ref: 6,
    label: "Outlook Q2 FY2026 exhibit: European rollout and additional launch plans",
    url: sourceUrls.q2fy2026,
    owner: "May 15, 2026 / Outlook Therapeutics exhibit",
    evidence: "European rollout, Netherlands/Ireland 2026 expansion plan, and initial-country demand.",
    find: ["continued to advance the commercial rollout", "intends to expand into the Netherlands and Ireland later in 2026"],
  },
  {
    id: "source-07-clinical-progress-norse-eight",
    ref: 7,
    label: "Outlook clinical-progress page: NORSE EIGHT and 2024 resubmission wording",
    url: sourceUrls.clinicalProgress,
    owner: "Live website page / Outlook Therapeutics",
    evidence: "NORSE EIGHT and BLA resubmission timing described in future-tense 2024 planning language.",
    find: ["NORSE EIGHT will be a randomized", "expects NORSE EIGHT topline results and resubmission"],
  },
  {
    id: "source-08-resubmission-norse-eight",
    ref: 8,
    label: "Outlook BLA resubmission exhibit: NORSE EIGHT and CMC support",
    url: sourceUrls.resubmission2025,
    owner: "February 28, 2025 / Outlook Therapeutics exhibit",
    evidence: "BLA resubmission based on NORSE EIGHT efficacy/safety and additional CMC information.",
    find: ["The ONS-5010 BLA resubmission was based on the efficacy and safety demonstrated in NORSE EIGHT", "additional chemistry, manufacturing and controls"],
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
    const minX = Math.max(0, Math.min(...rects.map((rect) => rect.x)) - 300);
    const minY = Math.max(0, Math.min(...rects.map((rect) => rect.y)) - 220);
    const maxX = Math.max(...rects.map((rect) => rect.x + rect.width)) + 420;
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
        height: Math.min(window.innerHeight - clipY, Math.max(520, maxY - minY)),
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
      <div class="evidence-top"><span>Reference ${item.ref}</span><a href="${esc(item.url)}">${esc(new URL(item.url).hostname)}</a></div>
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
  <title>Outlook Therapeutics Wet AMD Website Currentness Audit</title>
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
    .section-head p { margin-top: 14px; color: var(--muted); font-size: 20px; line-height: 1.12; max-width: 1440px; }
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
    .evidence-grid.four { grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .evidence-card { display: flex; flex-direction: column; min-height: 0; margin: 0; background: rgba(255,250,240,.92); border-radius: 18px; }
    .evidence-top { display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 7px 10px; border-bottom: 1px solid var(--line); background: var(--paper-2); font-size: 12px; font-weight: 800; text-transform: uppercase; }
    .evidence-top a { text-transform: none; font-weight: 700; color: var(--muted); }
    .evidence-card img { display: block; width: 100%; height: 420px; object-fit: contain; object-position: center; background: white; border-bottom: 1px solid rgba(16,18,15,.22); }
    .evidence-grid.four .evidence-card img { height: 205px; }
    figcaption { margin: 0; padding: 8px 10px 9px; color: var(--muted); font-size: 17px; line-height: 1.08; }
    .evidence-grid.four figcaption { font-size: 14px; line-height: 1.08; }
    .table { display: grid; }
    .row { display: grid; border-bottom: 1px solid var(--line); min-height: 70px; }
    .row:last-child { border-bottom: 0; }
    .row.refs { grid-template-columns: .28fr .92fr 1.1fr 1.85fr; min-height: 53px; }
    .cell { padding: 12px; border-right: 1px solid var(--line); font-size: 17px; line-height: 1.13; }
    .row.refs .cell { padding: 8px 10px; font-size: 14.4px; line-height: 1.08; }
    .row.refs .cell:first-child { display: flex; align-items: center; justify-content: center; text-align: center; padding-left: 0; padding-right: 0; }
    .cell:last-child { border-right: 0; }
    .head .cell { background: #11130f; color: var(--paper); font-weight: 850; text-transform: uppercase; font-size: 16px; white-space: nowrap; }
    .row.refs.head .cell { display: flex; align-items: center; justify-content: flex-start; font-size: 14px; }
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
      <div class="eyebrow">Outlook Therapeutics wet AMD web audit | ${runDate}</div>
      <h1>Outlook Therapeutics Wet AMD Website Currentness Audit</h1>
      <p class="dek">This deck reviews Outlook Therapeutics public website statements for ONS-5010/LYTENAVA in wet AMD against later official company regulatory-update and exhibit sources. Observations are limited to website statements that differ from, or remain less current than, later official source language.</p>
      <div class="grid-4">
        <div class="metric"><div class="num">3</div><div class="label">Website-currentness observations in reviewed wet AMD pages.</div></div>
        <div class="metric"><div class="num">8</div><div class="label">Primary source screenshots retained in the appendix.</div></div>
        <div class="metric"><div class="num">2</div><div class="label">Company website pages assessed: homepage and clinical-progress page.</div></div>
        <div class="metric"><div class="num">May 2026</div><div class="label">Most recent cited company update on U.S. regulatory status.</div></div>
      </div>
      <div class="callout">
        <h3>Executive summary</h3>
        <ul class="summary-list">
          <li>The homepage states that the U.S. BLA has been resubmitted; later company sources state that FDA issued a CRL and that Outlook was awaiting a formal FDA decision after an April 2026 formal dispute resolution meeting.<a class="cite" href="${sourceUrls.home}">1</a><a class="cite" href="${sourceUrls.crl2025}">2</a><a class="cite" href="${sourceUrls.q2fy2026}">3</a></li>
          <li>The homepage describes initiating EU/UK commercial launch in the second quarter of calendar 2025; later company source language states Outlook commenced commercial launch in Germany and the UK and continued European rollout in FY2026.<a class="cite" href="${sourceUrls.home}">4</a><a class="cite" href="${sourceUrls.q2fy2026}">5</a><a class="cite" href="${sourceUrls.q2fy2026}">6</a></li>
          <li>The LYTENAVA clinical-progress page describes NORSE EIGHT and BLA resubmission in future-tense 2024 planning language; later company source language identifies a 2025 BLA resubmission based on NORSE EIGHT and CMC information.<a class="cite" href="${sourceUrls.clinicalProgress}">7</a><a class="cite" href="${sourceUrls.resubmission2025}">8</a></li>
        </ul>
      </div>
    </div>
    <div class="slide-num">1/5</div>
  </article>

  <article class="slide evidence-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">U.S. regulatory status</div>
        <h2>Homepage BLA-resubmission wording is less current than later CRL and FDA-review updates</h2>
        <p>The currentness observation is limited to the homepage status sentence. Later official company sources state that FDA issued a CRL for the resubmitted BLA and that Outlook completed a formal dispute resolution meeting while awaiting a formal FDA decision.</p>
      </div>
      <div class="evidence-grid four">
        ${evidenceFigure(byId["source-01-home-bla-resubmitted"], "The homepage states that ONS-5010/LYTENAVA is investigational in the United States and that a BLA has been resubmitted to FDA.")}
        ${evidenceFigure(byId["source-02-crl-current-status"], "The December 31, 2025 company regulatory update states that FDA issued a CRL for the resubmitted BLA.")}
        ${evidenceFigure(byId["source-03-q2fy2026-regulatory-status"], "The May 15, 2026 company update states that Outlook completed a formal dispute resolution meeting and expected an FDA decision in May 2026.")}
        ${evidenceFigure(byId["source-08-resubmission-norse-eight"], "The February 2025 resubmission source is retained to distinguish the original resubmission event from the later FDA status.")}
      </div>
    </div>
    <div class="slide-num">2/5</div>
  </article>

  <article class="slide evidence-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">European commercial status</div>
        <h2>Homepage launch-timing wording remains framed as a future Q2 2025 event</h2>
        <p>Later company source language states that Outlook commenced commercial launch in Germany and the UK, and that the company continued European rollout activities in the second fiscal quarter of 2026.</p>
      </div>
      <div class="evidence-grid">
        ${evidenceFigure(byId["source-04-home-launch-timing"], "The homepage states Outlook is working to initiate EU/UK commercial launch, expected in Q2 2025.")}
        ${evidenceFigure(byId["source-05-commercial-launch"], "The Q2 FY2026 company exhibit states that Outlook commenced commercial launch in Germany and the UK.")}
      </div>
    </div>
    <div class="slide-num">3/5</div>
  </article>

  <article class="slide evidence-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Clinical-progress copy</div>
        <h2>The clinical-progress page retains future-tense NORSE EIGHT and 2024 resubmission language</h2>
        <p>The observation is based on the page's retained planning language. The cited later source states that the 2025 BLA resubmission was based on NORSE EIGHT efficacy and safety results and additional CMC information requested by FDA.</p>
      </div>
      <div class="evidence-grid">
        ${evidenceFigure(byId["source-07-clinical-progress-norse-eight"], "The clinical-progress page describes NORSE EIGHT and BLA resubmission timing using future-tense 2024 planning language.")}
        ${evidenceFigure(byId["source-08-resubmission-norse-eight"], "The later company resubmission exhibit describes NORSE EIGHT and CMC information as support for the 2025 BLA resubmission.")}
      </div>
    </div>
    <div class="slide-num">4/5</div>
  </article>

  <article class="slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">References 1-8</div>
        <h2>References</h2>
      </div>
      <div class="table">
        <div class="row refs head"><div class="cell">Ref</div><div class="cell">Source</div><div class="cell">Date / Status / Source Owner</div><div class="cell">Evidence Used in Report</div></div>
        ${captures.map((item) => `<div class="row refs"><div class="cell">${item.ref}</div><div class="cell"><a href="${esc(item.url)}">${esc(item.ref === 7 ? "LYTENAVA clinical-progress page" : item.ref === 8 ? "BLA resubmission exhibit" : item.ref === 2 ? "FDA CRL regulatory update" : item.ref === 3 || item.ref === 5 || item.ref === 6 ? "Q2 FY2026 company update" : "Outlook homepage")}</a></div><div class="cell">${esc(item.owner)}</div><div class="cell">${esc(item.evidence)}</div></div>`).join("\n        ")}
      </div>
    </div>
    <div class="slide-num">5/5</div>
  </article>
</body>
</html>`;
}

function writeSourceArtifacts(captures) {
  const sourceLog = `# Outlook Therapeutics Wet AMD Website Currentness Audit Source Log

Scope: Web-only source review of Outlook Therapeutics public wet AMD website statements for ONS-5010/LYTENAVA versus later official company regulatory-update and exhibit sources. Normal source lag was not treated as a website-currentness observation unless the public website itself presented a dated or current-status statement that differed from later official source language.

## Included References

${captures.map((item) => `${item.ref}. ${item.label}
   - URL: ${item.url}
   - Screenshot: ${rel(item.screenshotPath)}
   - Highlight status: ${item.found ? "text highlighted in rendered browser screenshot" : "requested highlight text not found; screenshot retained for review"}`).join("\n\n")}
`;
  fs.writeFileSync(outputFiles.sourceLog, sourceLog);
  const rows = ["label,path,caption"];
  for (const item of captures) rows.push([JSON.stringify(`Reference ${item.ref} - evidence`), JSON.stringify(rel(item.screenshotPath)), JSON.stringify(item.label)].join(","));
  fs.writeFileSync(outputFiles.screenshotManifest, rows.join("\n") + "\n");
}

function exportArtifacts() {
  runCommand("Export Outlook report PDF", process.execPath, [
    exporterScript,
    "--input", outputFiles.reportHtml,
    "--output", outputFiles.reportPdf,
    "--screenshots-dir", dirs.browserExport,
    "--render-check-dir", dirs.renderReview,
    "--chrome", chromePathForExporter,
  ]);
  runCommand("Assemble Outlook screenshot PDF", "python", [
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
    slideCount: 5,
    screenshots: captures.map((item) => ({ id: item.id, found: item.found, path: item.screenshotPath })),
  }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
