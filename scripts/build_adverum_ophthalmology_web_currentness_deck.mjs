import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

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
const reportSlug = "adverum_ophthalmology_web_currentness_audit";
const runFolder = path.join(
  repoRoot,
  "competitive_intelligence_reports",
  reportSlug,
  "2026-05-26_website_currentness"
);

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
  path.join(repoRoot, "competitive_intelligence_reports", "ocular_therapeutix_web_discrepancy_audit", "2026-05-26_website_currentness", "assets", "tan_slide_background.png"),
];
const backgroundSource = backgroundCandidates.find((candidate) => fs.existsSync(candidate));
if (backgroundSource) {
  fs.copyFileSync(backgroundSource, path.join(dirs.assets, "tan_slide_background.png"));
}

const sourceUrls = {
  adverumArtemis: "https://adverum.com/ixo-vec-artemis-wamd-trial/",
  adverumPipeline: "https://adverum.com/pipeline/",
  ctgovArtemis: "https://clinicaltrials.gov/api/v2/studies/NCT06856577?format=json",
  ctgovArtemisRecord: "https://clinicaltrials.gov/study/NCT06856577",
  ctgovOptic: "https://clinicaltrials.gov/api/v2/studies/NCT03748784?format=json",
  ctgovOpticRecord: "https://clinicaltrials.gov/study/NCT03748784",
  ctgovAquarius: "https://clinicaltrials.gov/api/v2/studies/NCT07482176?format=json",
  ctgovAquariusRecord: "https://clinicaltrials.gov/study/NCT07482176",
};

const references = [
  {
    ref: 1,
    source: "Adverum ARTEMIS patient page",
    url: sourceUrls.adverumArtemis,
    owner: "Adverum public website",
    evidence: "The page states that the trial is open for enrollment and cites ClinicalTrials.gov identifier NCT06856577 as updated April 27, 2025 and accessed April 28, 2025.",
  },
  {
    ref: 2,
    source: "ClinicalTrials.gov ARTEMIS API record",
    url: sourceUrls.ctgovArtemisRecord,
    apiUrl: sourceUrls.ctgovArtemis,
    owner: "ClinicalTrials.gov registry",
    evidence: "The current ARTEMIS record lists overall status ACTIVE_NOT_RECRUITING, May 2026 status verification, May 22, 2026 last update posting, and 311 actual enrollment.",
  },
  {
    ref: 3,
    source: "Adverum pipeline page",
    url: sourceUrls.adverumPipeline,
    owner: "Adverum public website",
    evidence: "The page describes the OPTIC clinical program in present tense and states that the most recent follow-up covered participants between 1 and 2 years post treatment.",
  },
  {
    ref: 4,
    source: "ClinicalTrials.gov OPTIC API record",
    url: sourceUrls.ctgovOpticRecord,
    apiUrl: sourceUrls.ctgovOptic,
    owner: "ClinicalTrials.gov registry",
    evidence: "The current OPTIC record lists overall status COMPLETED, actual completion date June 22, 2022, and last update posting August 8, 2023.",
  },
  {
    ref: 5,
    source: "ClinicalTrials.gov AQUARIUS API record",
    url: sourceUrls.ctgovAquariusRecord,
    apiUrl: sourceUrls.ctgovAquarius,
    owner: "ClinicalTrials.gov registry",
    evidence: "The current AQUARIUS Phase 3 context record lists overall status RECRUITING, May 2026 status verification, and actual start date March 16, 2026.",
  },
];

const screenshotSpecs = [
  {
    id: "source-01a-adverum-artemis-open-enrollment",
    ref: 1,
    label: "Adverum ARTEMIS page: open-enrollment statement",
    url: sourceUrls.adverumArtemis,
    find: ["This trial is open for enrollment."],
  },
  {
    id: "source-01b-adverum-artemis-reference-date",
    ref: 1,
    label: "Adverum ARTEMIS page: dated ClinicalTrials.gov reference line",
    url: sourceUrls.adverumArtemis,
    find: ["ClinicalTrials.gov identifier: NCT06856577.", "Updated April 27, 2025.", "Accessed April 28, 2025."],
  },
  {
    id: "source-02a-ctgov-artemis-status-update",
    ref: 2,
    label: "ClinicalTrials.gov ARTEMIS API: status verification and last update",
    url: sourceUrls.ctgovArtemis,
    find: ['"statusVerifiedDate":"2026-05"', '"overallStatus":"ACTIVE_NOT_RECRUITING"', '"lastUpdatePostDateStruct":{"date":"2026-05-22"'],
  },
  {
    id: "source-02b-ctgov-artemis-enrollment",
    ref: 2,
    label: "ClinicalTrials.gov ARTEMIS API: actual enrollment count",
    url: sourceUrls.ctgovArtemis,
    find: ['"enrollmentInfo":{"count":311,"type":"ACTUAL"'],
  },
  {
    id: "source-03a-adverum-pipeline-optic-program",
    ref: 3,
    label: "Adverum pipeline page: present-tense OPTIC clinical program text",
    url: sourceUrls.adverumPipeline,
    find: ["OPTIC clinical program for wet AMD is investigating the safety and efficacy of Ixo-vec for the first two years post-treatment", "for up to five years"],
  },
  {
    id: "source-03b-adverum-pipeline-optic-follow-up",
    ref: 3,
    label: "Adverum pipeline page: most recent follow-up text",
    url: sourceUrls.adverumPipeline,
    find: ["At most recent follow-up", "between 1- and 2-years post treatment"],
  },
  {
    id: "source-04-ctgov-optic-completed",
    ref: 4,
    label: "ClinicalTrials.gov OPTIC API: completed status and dates",
    url: sourceUrls.ctgovOptic,
    find: ['"overallStatus":"COMPLETED"', '"completionDateStruct":{"date":"2022-06-22","type":"ACTUAL"', '"lastUpdatePostDateStruct":{"date":"2023-08-08"'],
  },
  {
    id: "source-05-ctgov-aquarius-context",
    ref: 5,
    label: "ClinicalTrials.gov AQUARIUS API: active Phase 3 context",
    url: sourceUrls.ctgovAquarius,
    find: ['"statusVerifiedDate":"2026-05"', '"overallStatus":"RECRUITING"', '"startDateStruct":{"date":"2026-03-16","type":"ACTUAL"'],
  },
];

function rel(filePath) {
  return path.relative(runFolder, filePath).replaceAll(path.sep, "/");
}

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function urlForRef(reference) {
  return reference.url;
}

function runCommand(label, command, args, options = {}) {
  console.log(`${label}: ${command} ${args.map((arg) => (/\s/.test(arg) ? JSON.stringify(arg) : arg)).join(" ")}`);
  const result = spawnSync(command, args, {
    cwd: repoRoot,
    encoding: "utf8",
    env: { ...process.env, CHROME_PATH: chromePathForExporter, ...(options.env || {}) },
    ...options,
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.status !== 0) {
    throw new Error(`${label} failed with exit code ${result.status ?? "unknown"}`);
  }
  return result;
}

async function dismissBanners(page) {
  const labels = [
    "Accept All",
    "Accept Cookies",
    "Accept",
    "Reject All",
    "Reject",
    "I Accept",
    "Close",
  ];
  for (const label of labels) {
    const button = page.getByText(label, { exact: true }).first();
    if (await button.count().catch(() => 0)) {
      await button.click({ timeout: 1200, force: true }).catch(() => {});
    }
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
      "[aria-label*='privacy' i]",
      "[role='dialog']",
    ];
    for (const element of document.querySelectorAll(selectors.join(","))) {
      const style = window.getComputedStyle(element);
      const isOverlay = style.position === "fixed" || style.position === "sticky" || Number(style.zIndex) > 1000;
      if (isOverlay) element.remove();
    }
  }).catch(() => {});
}

async function waitForRenderedSource(page, url) {
  if (!url.includes("adverum.com")) return;
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    const title = await page.title().catch(() => "");
    const bodyText = await page.locator("body").innerText({ timeout: 1500 }).catch(() => "");
    if (!title.includes("Just a moment") && !bodyText.includes("Enable JavaScript and cookies")) return;
    await page.waitForTimeout(1500);
  }
}

async function highlightAndFrame(page, phrases) {
  return page.evaluate((rawPhrases) => {
    const phrases = rawPhrases.map((item) => item.replace(/\s+/g, " ").trim()).filter(Boolean);
    const rects = [];
    const marks = [];

    const wrapPhrase = (phrase, color, outline) => {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const original = node.nodeValue || "";
        const directIndex = original.toLowerCase().indexOf(phrase.toLowerCase());
        if (directIndex >= 0) {
          const before = document.createTextNode(original.slice(0, directIndex));
          const mark = document.createElement("mark");
          mark.setAttribute("data-codex-highlight", "true");
          mark.textContent = original.slice(directIndex, directIndex + phrase.length);
          mark.style.background = color;
          mark.style.border = `3px solid ${outline}`;
          mark.style.borderRadius = "6px";
          mark.style.padding = "0 2px";
          mark.style.color = "inherit";
          mark.style.boxDecorationBreak = "clone";
          mark.style.webkitBoxDecorationBreak = "clone";
          const after = document.createTextNode(original.slice(directIndex + phrase.length));
          node.parentNode.insertBefore(before, node);
          node.parentNode.insertBefore(mark, node);
          node.parentNode.insertBefore(after, node);
          node.parentNode.removeChild(node);
          marks.push(mark);
          return true;
        }
      }
      return false;
    };

    const colors = [
      ["rgba(255, 242, 80, .72)", "#c15f00"],
      ["rgba(184, 216, 255, .72)", "#0b63b6"],
      ["rgba(215, 255, 95, .66)", "#4d7100"],
    ];

    for (let i = 0; i < phrases.length; i += 1) {
      wrapPhrase(phrases[i], colors[i % colors.length][0], colors[i % colors.length][1]);
    }

    for (const mark of marks) {
      const clientRects = Array.from(mark.getClientRects()).filter((rect) => rect.width > 2 && rect.height > 2);
      for (const rect of clientRects) {
        rects.push({
          x: window.scrollX + rect.left,
          y: window.scrollY + rect.top,
          width: rect.width,
          height: rect.height,
        });
      }
    }

    if (!rects.length) return { ok: false, rects: [], pageTitle: document.title };

    const minX = Math.max(0, Math.min(...rects.map((rect) => rect.x)) - 520);
    const minY = Math.max(0, Math.min(...rects.map((rect) => rect.y)) - 190);
    const maxX = Math.max(...rects.map((rect) => rect.x + rect.width)) + 360;
    const maxY = Math.max(...rects.map((rect) => rect.y + rect.height)) + 210;
    const centerY = Math.max(0, (minY + maxY) / 2 - window.innerHeight / 2);
    window.scrollTo(0, centerY);

    const clipX = Math.max(0, minX);
    const clipY = Math.max(0, minY - centerY);
    const clipWidth = Math.min(window.innerWidth - clipX, Math.max(1040, maxX - minX));
    const clipHeight = Math.min(window.innerHeight - clipY, Math.max(420, maxY - minY));

    return {
      ok: true,
      rects,
      pageTitle: document.title,
      clip: { x: clipX, y: clipY, width: clipWidth, height: clipHeight },
    };
  }, phrases);
}

async function captureScreenshots() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: ["--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check"],
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    extraHTTPHeaders: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    },
  });
  const outputs = [];
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(45000);
    for (const spec of screenshotSpecs) {
      console.log(`Capturing ${spec.id}`);
      await page.goto(spec.url, { waitUntil: "domcontentloaded", timeout: 60000 });
      await waitForRenderedSource(page, spec.url);
      await page.waitForLoadState("networkidle", { timeout: 25000 }).catch(() => {});
      await dismissBanners(page);
      await page.evaluate(() => {
        document.documentElement.style.scrollBehavior = "auto";
        document.querySelectorAll("[data-codex-highlight]").forEach((el) => el.remove());
      }).catch(() => {});
      const result = await highlightAndFrame(page, spec.find);
      await page.waitForTimeout(350);
      const screenshotPath = path.join(dirs.evidence, `${spec.id}.png`);
      const options = result.ok && result.clip
        ? { path: screenshotPath, clip: result.clip }
        : { path: screenshotPath, fullPage: false };
      await page.screenshot(options);
      outputs.push({ ...spec, screenshotPath, found: result.ok, pageTitle: result.pageTitle });
    }
  } finally {
    await browser.close();
  }
  return outputs;
}

function evidenceFigure(item, ref, note) {
  return `<figure class="evidence-card">
      <div class="evidence-top"><span>Reference ${ref}</span><a href="${esc(item.url)}">${esc(new URL(item.url).hostname)}</a></div>
      <img src="${esc(rel(item.screenshotPath))}" alt="${esc(item.label)}" />
      <figcaption>${esc(note || item.label)}</figcaption>
    </figure>`;
}

function buildHtml(captures) {
  const byId = Object.fromEntries(captures.map((item) => [item.id, item]));
  const ref = Object.fromEntries(references.map((item) => [item.ref, item]));
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Adverum Ophthalmology Website Currentness Audit</title>
  <style>
    :root {
      --ink: #10120f;
      --muted: #5b6258;
      --paper: #f6f1e8;
      --paper-2: #ebe4d6;
      --card: #fffaf0;
      --line: #1b1f17;
      --lime: #d7ff5f;
      --orange: #ffb86b;
      --blue: #b8d8ff;
      --pink: #ffd3e0;
      --gray: #d6d0c2;
      --red: #ff8a76;
      --shadow: 0 18px 48px rgba(16,18,15,.08);
      --radius: 22px;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; background: var(--paper); color: var(--ink); scrollbar-width: none; }
    html::-webkit-scrollbar, body::-webkit-scrollbar { display: none; }
    body, *, *::before, *::after {
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    a { color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px; }
    .slide {
      width: 100vw;
      height: 100vh;
      min-height: 100vh;
      overflow: hidden;
      position: relative;
      display: flex;
      align-items: flex-start;
      padding: 34px 0 18px;
      page-break-after: always;
      break-after: page;
      background: var(--paper);
    }
    .slide:last-child { page-break-after: auto; break-after: auto; }
    .slide-bg-img {
      position: absolute;
      inset: 0;
      z-index: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      pointer-events: none;
      user-select: none;
      opacity: .9;
    }
    .wrap { width: min(1360px, calc(100vw - 56px)); margin: 0 auto; position: relative; z-index: 1; }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      border: 1.4px solid var(--line);
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 14px;
      font-weight: 850;
      text-transform: uppercase;
      margin-bottom: 18px;
      background: var(--lime);
    }
    h1, h2, h3, p { margin: 0; }
    h1 { font-size: 62px; line-height: .96; font-weight: 560; max-width: 1320px; letter-spacing: 0; }
    h2 { font-size: 44px; line-height: .98; font-weight: 560; max-width: 1300px; letter-spacing: 0; }
    h3 { font-size: 25px; line-height: 1.04; font-weight: 650; letter-spacing: 0; }
    .dek { margin-top: 18px; color: var(--muted); font-size: 23px; line-height: 1.18; max-width: 1260px; }
    .section-head { margin-bottom: 12px; }
    .section-head p { margin-top: 10px; color: var(--muted); font-size: 18px; line-height: 1.14; max-width: 1280px; }
    .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .panel, .metric, .table, .callout, .evidence-card, .note-card {
      border: 1.5px solid var(--line);
      background: rgba(255,250,240,.9);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .panel { padding: 20px; }
    .callout { background: #11130f; color: var(--paper); border-color: #11130f; padding: 22px 24px; }
    .callout h3 { color: var(--lime); }
    .callout p, .callout li { color: rgba(246,241,232,.88); }
    .metric { padding: 17px; min-height: 122px; }
    .num { font-size: 46px; line-height: .92; font-weight: 400; }
    .label { margin-top: 10px; font-size: 19px; line-height: 1.12; color: var(--muted); }
    .tag {
      display: inline-block;
      padding: 5px 9px;
      border: 1.2px solid var(--line);
      border-radius: 999px;
      font-size: 12px;
      font-weight: 850;
      text-transform: uppercase;
      background: var(--paper-2);
      white-space: nowrap;
      margin-bottom: 10px;
    }
    .lime { background: var(--lime); }
    .orange { background: var(--orange); }
    .blue { background: var(--blue); }
    .pink { background: var(--pink); }
    .red { background: var(--red); }
    .gray { background: var(--gray); }
    .summary-list { margin: 13px 0 0; padding-left: 22px; display: grid; gap: 9px; }
    .summary-list li { font-size: 20px; line-height: 1.14; }
    .finding-grid { display: grid; grid-template-columns: .9fr 1.1fr; gap: 14px; align-items: start; }
    .comparison { display: grid; gap: 12px; }
    .comparison .panel { min-height: 150px; }
    .comparison p { color: var(--muted); font-size: 18px; line-height: 1.13; margin-top: 8px; }
    .evidence-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .evidence-grid.three { grid-template-columns: repeat(3, 1fr); }
    .evidence-card { margin: 0; border-radius: 18px; background: rgba(255,250,240,.92); }
    .evidence-top {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      padding: 7px 10px;
      border-bottom: 1px solid var(--line);
      font-size: 12px;
      font-weight: 850;
      text-transform: uppercase;
    }
    .evidence-top a { text-transform: none; color: var(--muted); font-weight: 750; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .evidence-card img {
      display: block;
      width: 100%;
      height: 174px;
      object-fit: cover;
      object-position: top left;
      background: #fff;
      border-bottom: 1px solid var(--line);
    }
    .evidence-grid.three .evidence-card img { height: 174px; }
    figcaption {
      margin: 0;
      padding: 8px 10px 10px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.08;
    }
    .note-card { padding: 16px; min-height: 260px; }
    .note-card p { margin-top: 8px; color: var(--muted); font-size: 18px; line-height: 1.13; }
    .context-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 12px; }
    .context-card { padding: 20px; min-height: 240px; }
    .context-card h3 { font-size: 28px; }
    .context-card p { margin-top: 12px; color: var(--muted); font-size: 22px; line-height: 1.15; }
    .table { display: grid; }
    .row { display: grid; border-bottom: 1px solid var(--line); min-height: 62px; }
    .row:last-child { border-bottom: 0; }
    .row.refs { grid-template-columns: .28fr .8fr 1fr 1.88fr; min-height: 58px; }
    .cell { padding: 10px 11px; border-right: 1px solid var(--line); font-size: 15px; line-height: 1.1; }
    .row.refs .cell:first-child {
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding-left: 0;
      padding-right: 0;
    }
    .cell:last-child { border-right: 0; }
    .head .cell {
      background: #11130f;
      color: var(--paper);
      font-weight: 850;
      text-transform: uppercase;
      font-size: 13px;
      white-space: nowrap;
    }
    .cite { font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 900; text-decoration: none; }
    .slide-num { position: absolute; right: 40px; bottom: 24px; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: rgba(16,18,15,.38); font-weight: 800; z-index: 2; }
    @page { size: 1600px 900px; margin: 0; }
    @media print {
      html, body { width: 1600px; height: 900px; }
      .slide { width: 1600px; height: 900px; min-height: 900px; padding: 34px 0 18px; }
      .wrap { width: 1360px; }
      .panel, .metric, .table, .callout, .evidence-card, .note-card { box-shadow: none; }
    }
    @media screen and (max-width: 900px) {
      .slide { width: 1600px; height: 900px; }
    }
  </style>
</head>
<body>
  <article class="slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="eyebrow">Adverum ophthalmology web audit | ${runDate}</div>
      <h1>Adverum Ophthalmology Website Currentness Audit</h1>
      <p class="dek">This audit compares live Adverum ophthalmology website statements with current ClinicalTrials.gov registry records for Ixo-vec wet AMD trials. Observations are limited to source-currentness comparisons supported by public website text and registry data.</p>
      <div class="grid-4" style="margin-top:24px;">
        <div class="metric"><div class="num">2</div><div class="label">High-confidence website-currentness observations.</div></div>
        <div class="metric"><div class="num">5</div><div class="label">Primary source references retained in the report.</div></div>
        <div class="metric"><div class="num">311</div><div class="label">ARTEMIS actual enrollment in the current registry record.</div></div>
        <div class="metric"><div class="num">2026-05</div><div class="label">Current ARTEMIS status verification month.</div></div>
      </div>
      <div class="callout" style="margin-top:20px;">
        <h3>Executive summary</h3>
        <ul class="summary-list">
          <li>The Adverum ARTEMIS patient page states that the trial is open for enrollment and cites an April 2025 ClinicalTrials.gov reference line; the current ARTEMIS registry record lists ACTIVE_NOT_RECRUITING, May 2026 status verification, May 22, 2026 last update posting, and 311 actual enrollment.<a class="cite" href="${urlForRef(ref[1])}">1</a><a class="cite" href="${urlForRef(ref[2])}">2</a></li>
          <li>The Adverum pipeline page uses present-tense OPTIC program wording and a most-recent-follow-up statement covering 1 to 2 years post treatment; the current OPTIC registry record lists the study as COMPLETED, with actual completion on June 22, 2022 and last update posting on August 8, 2023.<a class="cite" href="${urlForRef(ref[3])}">3</a><a class="cite" href="${urlForRef(ref[4])}">4</a></li>
          <li>Current Phase 3 registry context includes ARTEMIS and AQUARIUS; AQUARIUS is listed as RECRUITING with May 2026 status verification and actual start on March 16, 2026. This context is not treated as a standalone website-currentness observation.<a class="cite" href="${urlForRef(ref[2])}">2</a><a class="cite" href="${urlForRef(ref[5])}">5</a></li>
        </ul>
      </div>
    </div>
    <div class="slide-num">1/5</div>
  </article>

  <article class="slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Observation 1 | ARTEMIS enrollment status</div>
        <h2>Adverum ARTEMIS enrollment language differs from the current registry status</h2>
        <p>The website statement is framed as a current patient-facing trial availability claim. The current ClinicalTrials.gov API record lists ARTEMIS as active, not recruiting, with a later update date and actual enrollment count.</p>
      </div>
      <div class="finding-grid">
        <div class="comparison">
          <div class="panel">
            <span class="tag orange">Adverum website</span>
            <h3>Open-enrollment claim and older reference line</h3>
            <p>The patient page states that the trial is open for enrollment and cites NCT06856577 as updated April 27, 2025 and accessed April 28, 2025.<a class="cite" href="${urlForRef(ref[1])}">1</a></p>
          </div>
          <div class="panel">
            <span class="tag blue">Current registry record</span>
            <h3>Active, not recruiting</h3>
            <p>The current ARTEMIS API record lists statusVerifiedDate 2026-05, overallStatus ACTIVE_NOT_RECRUITING, lastUpdatePostDate 2026-05-22, and enrollment 311 actual.<a class="cite" href="${urlForRef(ref[2])}">2</a></p>
          </div>
        </div>
        <div class="evidence-grid">
          ${evidenceFigure(byId["source-01a-adverum-artemis-open-enrollment"], 1, "Adverum patient page statement that ARTEMIS is open for enrollment.")}
          ${evidenceFigure(byId["source-01b-adverum-artemis-reference-date"], 1, "Adverum reference line citing NCT06856577 as updated April 27, 2025 and accessed April 28, 2025.")}
          ${evidenceFigure(byId["source-02a-ctgov-artemis-status-update"], 2, "ClinicalTrials.gov API fields for ARTEMIS status verification, overall status, and last update posting.")}
          ${evidenceFigure(byId["source-02b-ctgov-artemis-enrollment"], 2, "ClinicalTrials.gov API field for ARTEMIS actual enrollment count.")}
        </div>
      </div>
    </div>
    <div class="slide-num">2/5</div>
  </article>

  <article class="slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Observation 2 | OPTIC program wording</div>
        <h2>Adverum OPTIC program wording differs from the completed registry record</h2>
        <p>The pipeline page presents OPTIC program language in the present tense and describes most recent follow-up at 1 to 2 years. The current OPTIC registry record lists the trial as completed, with actual completion in 2022.</p>
      </div>
      <div class="finding-grid">
        <div class="comparison">
          <div class="panel">
            <span class="tag orange">Adverum website</span>
            <h3>Present-tense program description</h3>
            <p>The pipeline page states that the OPTIC clinical program is investigating Ixo-vec safety and efficacy during the first two years post treatment and long-term outcomes up to five years.<a class="cite" href="${urlForRef(ref[3])}">3</a></p>
          </div>
          <div class="panel">
            <span class="tag blue">Current registry record</span>
            <h3>Completed status</h3>
            <p>The OPTIC ClinicalTrials.gov API record lists overallStatus COMPLETED, completionDateStruct 2022-06-22 actual, and lastUpdatePostDate 2023-08-08.<a class="cite" href="${urlForRef(ref[4])}">4</a></p>
          </div>
        </div>
        <div class="evidence-grid">
          ${evidenceFigure(byId["source-03a-adverum-pipeline-optic-program"], 3, "Adverum pipeline page present-tense OPTIC clinical program wording.")}
          ${evidenceFigure(byId["source-03b-adverum-pipeline-optic-follow-up"], 3, "Adverum pipeline page most-recent-follow-up statement for participants 1 to 2 years post treatment.")}
          ${evidenceFigure(byId["source-04-ctgov-optic-completed"], 4, "ClinicalTrials.gov API fields for OPTIC completed status, actual completion date, and last update posting.")}
          <div class="note-card">
            <span class="tag gray">Scope note</span>
            <h3>Neutral currentness framing</h3>
            <p>This observation is limited to the relationship between current website wording and the cited registry record. It does not assess clinical interpretation, program strategy, or regulatory implications.</p>
          </div>
        </div>
      </div>
    </div>
    <div class="slide-num">3/5</div>
  </article>

  <article class="slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Registry context | Phase 3 Ixo-vec wet AMD records</div>
        <h2>Current Phase 3 registry context includes ARTEMIS and AQUARIUS</h2>
        <p>AQUARIUS is retained as source-scope context because it is an active Phase 3 Ixo-vec registry record. It is not used as a standalone website-currentness observation in this deck.</p>
      </div>
      <div class="context-grid">
        <div class="panel context-card">
          <span class="tag blue">ARTEMIS | NCT06856577</span>
          <h3>Active, not recruiting</h3>
          <p>Status verified May 2026; last update posted May 22, 2026; actual enrollment 311. This current registry status is the comparator for the Adverum ARTEMIS patient-page observation.<a class="cite" href="${urlForRef(ref[2])}">2</a></p>
        </div>
        <div class="panel context-card">
          <span class="tag lime">AQUARIUS | NCT07482176</span>
          <h3>Recruiting</h3>
          <p>Status verified May 2026; actual study start March 16, 2026. This supports current Phase 3 source context without changing the ARTEMIS-specific enrollment-status comparison.<a class="cite" href="${urlForRef(ref[5])}">5</a></p>
        </div>
      </div>
      <div class="evidence-grid" style="margin-top:14px;">
        ${evidenceFigure(byId["source-02a-ctgov-artemis-status-update"], 2, "ARTEMIS current registry status and last update fields.")}
        ${evidenceFigure(byId["source-05-ctgov-aquarius-context"], 5, "AQUARIUS current registry status, verification month, and actual start date fields.")}
      </div>
    </div>
    <div class="slide-num">4/5</div>
  </article>

  <article class="slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">References 1-5</div>
        <h2>References</h2>
        <p>References are limited to live Adverum pages and current ClinicalTrials.gov registry records used in the report.</p>
      </div>
      <div class="table">
        <div class="row refs head">
          <div class="cell">Ref</div>
          <div class="cell">Source</div>
          <div class="cell">Date / Status / Source Owner</div>
          <div class="cell">Evidence Used in Report</div>
        </div>
        ${references.map((item) => `<div class="row refs"><div class="cell">${item.ref}</div><div class="cell"><a href="${esc(item.url)}">${esc(item.source)}</a></div><div class="cell">${esc(item.owner)}</div><div class="cell">${esc(item.evidence)}</div></div>`).join("\n        ")}
      </div>
    </div>
    <div class="slide-num">5/5</div>
  </article>
</body>
</html>`;
}

function writeSourceArtifacts(captures) {
  const byRef = new Map();
  for (const capture of captures) {
    if (!byRef.has(capture.ref)) byRef.set(capture.ref, []);
    byRef.get(capture.ref).push(capture);
  }

  const log = `# Adverum Ophthalmology Website Currentness Audit Source Log

Run date: ${runDate}

Scope: Public Adverum ophthalmology website statements compared with current ClinicalTrials.gov registry records for Ixo-vec wet AMD trials. The report uses neutral source-currentness framing and does not assess clinical, regulatory, or strategic implications.

## Included References

${references.map((reference) => {
  const capturesForRef = byRef.get(reference.ref) || [];
  const screenshotLines = capturesForRef.map((capture, index) => `   - Screenshot ${index + 1}: ${rel(capture.screenshotPath)}
     - Highlight status: ${capture.found ? "supporting text highlighted in rendered browser screenshot" : "requested highlight text not identified; screenshot retained for review"}`).join("\n");
  return `${reference.ref}. ${reference.source}
   - URL: ${reference.url}
   ${reference.apiUrl ? `- API URL: ${reference.apiUrl}\n   ` : ""}- Source owner: ${reference.owner}
   - Evidence used: ${reference.evidence}
${screenshotLines}`;
}).join("\n\n")}

## Source-Scope Notes

- ARTEMIS and OPTIC observations are treated as high-confidence website-currentness comparisons because live Adverum website language is compared against current ClinicalTrials.gov records for the same named trials.
- AQUARIUS is included only as current Phase 3 registry context. It is not treated as a standalone website-currentness observation.
`.trimEnd() + "\n";
  fs.writeFileSync(outputFiles.sourceLog, log);

  const rows = ["label,path,caption"];
  const ordinalByRef = new Map();
  for (const capture of captures) {
    const next = (ordinalByRef.get(capture.ref) || 0) + 1;
    ordinalByRef.set(capture.ref, next);
    const label = `Reference ${capture.ref} - evidence ${next}`;
    rows.push([
      JSON.stringify(label),
      JSON.stringify(capture.screenshotPath),
      JSON.stringify(`${capture.label} | ${capture.url}`),
    ].join(","));
  }
  fs.writeFileSync(outputFiles.screenshotManifest, rows.join("\n") + "\n");
}

function exportReportPdf() {
  runCommand("Export report PDF", process.execPath, [
    exporterScript,
    "--input", outputFiles.reportHtml,
    "--output", outputFiles.reportPdf,
    "--screenshots-dir", dirs.browserExport,
    "--render-check-dir", dirs.renderReview,
    "--chrome", chromePathForExporter,
  ]);
}

function assembleScreenshotPdf() {
  runCommand("Assemble reference screenshots PDF", "python", [
    screenshotAssemblerScript,
    "--output", outputFiles.screenshotPdf,
    "--manifest", outputFiles.screenshotManifest,
  ]);
}

async function main() {
  const captures = await captureScreenshots();
  writeSourceArtifacts(captures);
  fs.writeFileSync(outputFiles.reportHtml, buildHtml(captures));
  exportReportPdf();
  assembleScreenshotPdf();
  console.log(JSON.stringify({
    runFolder,
    reportHtml: outputFiles.reportHtml,
    reportPdf: outputFiles.reportPdf,
    screenshotPdf: outputFiles.screenshotPdf,
    sourceLog: outputFiles.sourceLog,
    screenshotManifest: outputFiles.screenshotManifest,
    screenshots: captures.map((item) => ({ id: item.id, ref: item.ref, found: item.found, path: item.screenshotPath })),
  }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
