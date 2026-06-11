import { createRequire } from "node:module";
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
const runFolder = path.join(
  repoRoot,
  "competitive_intelligence_reports",
  "ocular_therapeutix_website_currentness_audit",
  "2026-05-26_website_currentness"
);

const dirs = {
  assets: path.join(runFolder, "assets"),
  evidence: path.join(runFolder, "screenshots", "evidence"),
  render: path.join(runFolder, "screenshots", "render-review"),
  browserExport: path.join(runFolder, "screenshots", "browser-export"),
  sources: path.join(runFolder, "sources"),
};

for (const dir of Object.values(dirs)) fs.mkdirSync(dir, { recursive: true });

const outputFiles = {
  reportHtml: path.join(runFolder, "report.html"),
  reportPdf: path.join(runFolder, "ocular_therapeutix_website_currentness_audit-ci-report-05.26.26.pdf"),
  screenshotAppendixPdf: path.join(runFolder, "ocular_therapeutix_website_currentness_audit-ci-screenshots-05.26.26.pdf"),
};

const backgroundCandidates = [
  path.join(repoRoot, "outputs", "wet_amd_terminology_comparison", "tan_slide_background.png"),
  path.join(repoRoot, "competitive_intelligence_reports", "ocular_hypertension_glaucoma", "2026-05-12_1245", "assets", "tan_slide_background.png"),
];
const backgroundSource = backgroundCandidates.find((candidate) => fs.existsSync(candidate));
if (backgroundSource) {
  fs.copyFileSync(backgroundSource, path.join(dirs.assets, "tan_slide_background.png"));
}

const ctgovActivePhase2Term = "AREA[Phase]PHASE2 AND (AREA[OverallStatus]RECRUITING OR AREA[OverallStatus]ACTIVE_NOT_RECRUITING OR AREA[OverallStatus]NOT_YET_RECRUITING OR AREA[OverallStatus]ENROLLING_BY_INVITATION)";

const sourceUrls = {
  otxTic: "https://www.ocutx.com/pipeline/otx-tic/",
  clinicalTrials: "https://www.ocutx.com/pipeline/clinical-trials/",
  ctgovOtxTic: "https://clinicaltrials.gov/study/NCT05335122",
  ctgovOcularActivePhase2: `https://clinicaltrials.gov/search?term=${encodeURIComponent(ctgovActivePhase2Term)}&spons=Ocular%20Therapeutix`,
  sec10q: "https://www.sec.gov/Archives/edgar/data/1393434/000110465926055256/ocul-20260331x10q.htm",
};

const screenshotSpecs = [
  {
    id: "source-01-otx-tic-website-phase2",
    url: sourceUrls.otxTic,
    label: "Ocular website source: OTX-TIC page states current Phase 2 status",
    find: ["OTX-TIC is currently in Phase 2 clinical trials."],
  },
  {
    id: "source-02-ctgov-otx-tic-completed",
    url: sourceUrls.ctgovOtxTic,
    label: "ClinicalTrials.gov: OTX-TIC Phase 2 record is completed",
    find: ["Completed"],
  },
  {
    id: "source-03-sec-otx-tic-completed",
    url: sourceUrls.sec10q,
    label: "SEC 10-Q: OTX-TIC completed Phase 2 and next steps are being evaluated",
    find: ["has completed a Phase 2 clinical trial", "We are evaluating next steps for the OTX-TIC program"],
  },
  {
    id: "source-04-website-solr-555",
    url: sourceUrls.clinicalTrials,
    label: "Ocular website source: SOL-R trial design shows 555 randomized subjects",
    find: ["555 total subjects randomized", "Primary Endpoint (Week 56)"],
    clinicalAccordionHeading: "SOL",
  },
  {
    id: "source-05-sec-solr-631",
    url: sourceUrls.sec10q,
    label: "SEC 10-Q: SOL-R completed randomization with 631 subjects",
    find: ["completed randomization of the SOL-R trial with a total of 631 subjects randomized", "Topline data for the SOL-R trial are expected to be available in the first quarter of 2027"],
  },
  {
    id: "source-06-website-helios-week52-week56",
    url: sourceUrls.clinicalTrials,
    label: "Ocular website source: HELIOS-3 endpoint text contains Week 56 and Week 52",
    find: ["Primary Endpoint (Week 56)", "at Week 52 from baseline"],
    occurrenceHint: "Q6M and Q12M",
    clinicalAccordionHeading: "HELIOS",
  },
  {
    id: "source-07-sec-helios-week56",
    url: sourceUrls.sec10q,
    label: "SEC 10-Q: HELIOS-3 protocol amendment extends endpoint from Week 52 to Week 56",
    find: ["extend the primary endpoint assessment from Week 52 to Week 56", "assessed at Week 56"],
  },
  {
    id: "source-08-ctgov-active-phase2-zero",
    url: sourceUrls.ctgovOcularActivePhase2,
    label: "ClinicalTrials.gov search: active-status Ocular Phase 2 sponsor query returns no records",
    find: ["Search Details: No results for:", "Sponsor/Collaborator: Ocular Therapeutix", "No records found."],
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

async function highlightAndFrame(page, phrases, occurrenceHint) {
  return page.evaluate(({ phrases: rawPhrases, occurrenceHint: rawHint }) => {
    const phrases = rawPhrases.map((item) => item.replace(/\s+/g, " ").trim()).filter(Boolean);
    const hint = rawHint ? rawHint.toLowerCase() : "";
    const selection = window.getSelection();
    const added = [];
    const rects = [];

    const resetSelection = () => {
      if (selection) selection.removeAllRanges();
    };

    const addOverlay = (range, color, outline) => {
      const clientRects = Array.from(range.getClientRects()).filter((rect) => rect.width > 2 && rect.height > 2);
      for (const rect of clientRects) {
        const overlay = document.createElement("div");
        overlay.setAttribute("data-codex-highlight", "true");
        overlay.style.position = "absolute";
        overlay.style.left = `${window.scrollX + rect.left - 3}px`;
        overlay.style.top = `${window.scrollY + rect.top - 3}px`;
        overlay.style.width = `${rect.width + 6}px`;
        overlay.style.height = `${rect.height + 6}px`;
        overlay.style.background = color;
        overlay.style.border = `3px solid ${outline}`;
        overlay.style.borderRadius = "6px";
        overlay.style.pointerEvents = "none";
        overlay.style.mixBlendMode = "multiply";
        overlay.style.zIndex = "2147483647";
        document.body.appendChild(overlay);
        added.push(overlay);
        rects.push({
          x: window.scrollX + rect.left,
          y: window.scrollY + rect.top,
          width: rect.width,
          height: rect.height,
        });
      }
    };

    const normalized = (text) => text.replace(/\s+/g, " ").trim();

    const isInHintScope = (node) => {
      if (!hint) return true;
      const element = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
      if (!element) return false;
      let scope = element;
      while (scope && scope !== document.body) {
        const scopeText = (scope.innerText || "").toLowerCase();
        const scopeRect = scope.getBoundingClientRect();
        if (scopeText.includes(hint) && scopeRect.height <= Math.max(900, window.innerHeight * 0.9)) return true;
        scope = scope.parentElement;
      }
      return false;
    };

    const hasVisibleRects = (range) => Array.from(range.getClientRects()).some((rect) => rect.width > 2 && rect.height > 2);

    const locateByTextNodes = (phrase, scopedOnly = false) => {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const value = normalized(node.nodeValue || "");
        const index = value.toLowerCase().indexOf(phrase.toLowerCase());
        if (index >= 0) {
          if (scopedOnly && !isInHintScope(node)) continue;
          const original = node.nodeValue || "";
          const directIndex = original.toLowerCase().indexOf(phrase.toLowerCase());
          if (directIndex >= 0) {
            const range = document.createRange();
            range.setStart(node, directIndex);
            range.setEnd(node, directIndex + phrase.length);
            if (hasVisibleRects(range)) return range;
            continue;
          }
          const range = document.createRange();
          range.selectNodeContents(node);
          if (hasVisibleRects(range)) return range;
        }
      }
      return null;
    };

    const findPhrase = (phrase) => {
      const scopedRange = locateByTextNodes(phrase, true);
      if (scopedRange) return scopedRange;
      resetSelection();
      const found = window.find(phrase, false, false, true, false, true, false);
      if (found && selection && selection.rangeCount) {
        const selectedRange = selection.getRangeAt(0).cloneRange();
        if (hasVisibleRects(selectedRange)) return selectedRange;
      }
      return locateByTextNodes(phrase);
    };

    const colors = [
      ["rgba(255, 242, 80, .72)", "#c15f00"],
      ["rgba(184, 216, 255, .72)", "#0b63b6"],
      ["rgba(215, 255, 95, .66)", "#4d7100"],
    ];

    for (let i = 0; i < phrases.length; i += 1) {
      const range = findPhrase(phrases[i]);
      if (range) addOverlay(range, colors[i % colors.length][0], colors[i % colors.length][1]);
    }
    resetSelection();

    if (!rects.length) return { ok: false, rects: [], pageTitle: document.title };

    let target = rects[0];
    if (hint) {
      const allText = document.body.innerText.toLowerCase();
      const hintIndex = allText.indexOf(hint);
      if (hintIndex >= 0) {
        const candidate = rects.find((rect) => rect.y > target.y - 200) || target;
        target = candidate;
      }
    }

    const minX = Math.max(0, Math.min(...rects.map((rect) => rect.x)) - 520);
    const minY = Math.max(0, Math.min(...rects.map((rect) => rect.y)) - 220);
    const maxX = Math.max(...rects.map((rect) => rect.x + rect.width)) + 360;
    const maxY = Math.max(...rects.map((rect) => rect.y + rect.height)) + 260;
    const centerX = Math.max(0, (minX + maxX) / 2 - window.innerWidth / 2);
    const centerY = Math.max(0, (minY + maxY) / 2 - window.innerHeight / 2);
    window.scrollTo(centerX, centerY);
    const clipX = Math.max(0, minX - centerX);
    const clipY = Math.max(0, minY - centerY);
    const clipWidth = Math.min(window.innerWidth - clipX, Math.max(900, maxX - minX));
    const clipHeight = Math.min(window.innerHeight - clipY, Math.max(520, maxY - minY));

    return {
      ok: true,
      rects,
      pageTitle: document.title,
      clip: {
        x: clipX,
        y: clipY,
        width: clipWidth,
        height: clipHeight,
      },
    };
  }, { phrases, occurrenceHint });
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
  });
}

async function preparePageForSpec(page, spec) {
  await dismissBanners(page);
  if (!spec.clinicalAccordionHeading) return;
  await page.evaluate((heading) => {
    const normalize = (value) => (value || "").replace(/\s+/g, " ").trim().toLowerCase();
    const needle = normalize(heading);
    const candidates = Array.from(document.querySelectorAll("details, .e-n-accordion-item"));
    const target = candidates.find((element) => normalize(element.innerText).includes(needle));
    if (!target) return;
    const summary = target.querySelector("summary");
    if (summary) summary.click();
    if (target.tagName.toLowerCase() === "details" && !target.open) {
      target.open = true;
      target.setAttribute("open", "");
    }
    target.scrollIntoView({ block: "center", inline: "nearest" });
  }, spec.clinicalAccordionHeading);
  await page.waitForTimeout(650);
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
    userAgent: "CodexSourceScreenshot/1.0 contact=research@example.com",
    extraHTTPHeaders: {
      "User-Agent": "CodexSourceScreenshot/1.0 contact=research@example.com",
    },
  });
  const outputs = [];
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(45000);
    for (const spec of screenshotSpecs) {
      console.log(`Capturing ${spec.id}`);
      await page.goto(spec.url, { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForLoadState("networkidle", { timeout: 25000 }).catch(() => {});
      await page.evaluate(() => {
        document.documentElement.style.scrollBehavior = "auto";
        document.querySelectorAll("[data-codex-highlight]").forEach((el) => el.remove());
      });
      await preparePageForSpec(page, spec);
      const result = await highlightAndFrame(page, spec.find, spec.occurrenceHint);
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
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Ocular Therapeutix Website Currentness Audit</title>
  <style>
    :root {
      --ink: #10120f;
      --muted: #5c6257;
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
      --radius: 24px;
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
      padding: 36px 0 20px;
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
      font-size: 15px;
      font-weight: 850;
      text-transform: uppercase;
      margin-bottom: 22px;
      background: var(--lime);
    }
    h1, h2, h3, p { margin: 0; }
    h1 { font-size: 75px; line-height: .95; font-weight: 560; max-width: 1320px; }
    h2 { font-size: 48px; line-height: .98; font-weight: 560; max-width: 1300px; }
    h3 { font-size: 27px; line-height: 1.04; font-weight: 650; }
    .dek { margin-top: 22px; color: var(--muted); font-size: 26px; line-height: 1.2; max-width: 1260px; }
    .section-head { margin-bottom: 16px; }
    .section-head p { margin-top: 16px; color: var(--muted); font-size: 22px; line-height: 1.18; max-width: 1280px; }
    .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
    .panel, .metric, .card, .table, .callout, .evidence-card {
      border: 1.5px solid var(--line);
      background: rgba(255,250,240,.9);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .panel { padding: 22px; }
    .callout { background: #11130f; color: var(--paper); border-color: #11130f; padding: 24px 26px; }
    .callout h3 { color: var(--lime); }
    .callout p, .callout li { color: rgba(246,241,232,.86); }
    .metric { padding: 20px; min-height: 155px; }
    .num { font-size: 50px; line-height: .92; font-weight: 400; }
    .label { margin-top: 12px; font-size: 22px; line-height: 1.12; color: var(--muted); }
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
    .summary-list { margin: 14px 0 0; padding-left: 22px; display: grid; gap: 9px; }
    .summary-list li { font-size: 22px; line-height: 1.15; }
    .title-slide h1 { font-size: 64px; max-width: 1360px; }
    .title-slide .dek { font-size: 23px; line-height: 1.14; max-width: 100%; }
    .title-slide .grid-4 { margin-top: 20px !important; }
    .title-slide .metric { min-height: 124px; padding: 16px; }
    .title-slide .num { font-size: 44px; }
    .title-slide .label { margin-top: 8px; font-size: 18px; line-height: 1.1; }
    .title-slide .callout { margin-top: 18px !important; padding: 18px 22px; }
    .title-slide .summary-list { gap: 7px; }
    .title-slide .summary-list li { font-size: 23px; line-height: 1.16; }
    .observation-card { padding: 22px; min-height: 232px; }
    .observation-card p { margin-top: 10px; color: var(--muted); font-size: 21px; line-height: 1.17; }
    .evidence-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; align-items: stretch; }
    .evidence-grid.three { grid-template-columns: repeat(3, 1fr); }
    .evidence-grid.four { grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .evidence-card { display: flex; flex-direction: column; min-height: 0; margin: 0; background: rgba(255,250,240,.92); }
    .evidence-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      padding: 9px 12px;
      border-bottom: 1px solid var(--line);
      background: var(--paper-2);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .evidence-top a { text-transform: none; font-weight: 700; color: var(--muted); }
    .evidence-card img {
      display: block;
      width: 100%;
      height: 315px;
      object-fit: contain;
      object-position: center;
      background: white;
      border-bottom: 1px solid rgba(16,18,15,.22);
    }
    .evidence-grid.three .evidence-card img { height: 292px; }
    .evidence-grid.four .evidence-card img { height: 238px; }
    .evidence-grid.four figcaption { font-size: 13px; line-height: 1.12; }
    .evidence-slide {
      padding: 24px 0 14px;
    }
    .evidence-slide .wrap {
      width: min(1460px, calc(100vw - 34px));
    }
    .evidence-slide .eyebrow {
      margin-bottom: 16px;
      padding: 7px 11px;
    }
    .evidence-slide .section-head {
      margin-bottom: 10px;
    }
    .evidence-slide h2 {
      font-size: 44px;
      line-height: .96;
      max-width: 1450px;
    }
    .evidence-slide .section-head p {
      margin-top: 22px;
      font-size: 20px;
      line-height: 1.12;
      max-width: 1440px;
    }
    .evidence-slide .evidence-grid {
      gap: 10px;
    }
    .evidence-slide .evidence-grid.four {
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }
    .evidence-slide .evidence-card {
      border-radius: 18px;
    }
    .evidence-slide .evidence-top {
      padding: 7px 10px;
    }
    .evidence-slide .evidence-card img {
      height: 420px;
    }
    .evidence-slide .evidence-grid.four .evidence-card img {
      height: 205px;
    }
    .evidence-slide figcaption {
      padding: 8px 10px 9px;
      font-size: 17px;
      line-height: 1.08;
    }
    .evidence-slide .evidence-grid.four figcaption {
      font-size: 14px;
      line-height: 1.08;
    }
    figcaption {
      margin: 0;
      padding: 10px 12px 12px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.16;
    }
    .note-card { padding: 20px; min-height: 172px; }
    .note-card p { margin-top: 8px; color: var(--muted); font-size: 20px; line-height: 1.16; }
    .table { display: grid; }
    .row { display: grid; border-bottom: 1px solid var(--line); min-height: 70px; }
    .row:last-child { border-bottom: 0; }
    .row.refs { grid-template-columns: .28fr .9fr 1.15fr 1.9fr; min-height: 53px; }
    .row.refs.head { min-height: 40px; }
    .cell { padding: 12px 12px; border-right: 1px solid var(--line); font-size: 17px; line-height: 1.13; }
    .row.refs .cell { padding: 8px 10px; font-size: 14.5px; line-height: 1.08; }
    .row.refs:not(.head) .cell {
      display: flex;
      align-items: center;
    }
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
      font-size: 16px;
      white-space: nowrap;
    }
    .row.refs.head .cell {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      padding-top: 4px;
      padding-bottom: 4px;
      font-size: 14px;
    }
    .row.refs.head .cell:first-child { justify-content: center; }
    .references-slide .section-head {
      margin-bottom: 30px;
    }
    .cite { font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 900; text-decoration: none; }
    .slide-num { position: absolute; right: 40px; bottom: 24px; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: rgba(16,18,15,.38); font-weight: 800; z-index: 2; }
    @page { size: 1600px 900px; margin: 0; }
    @media print {
      html, body { width: 1600px; height: 900px; }
      .slide { width: 1600px; height: 900px; min-height: 900px; padding: 36px 0 20px; }
      .slide.evidence-slide { padding: 24px 0 14px; }
      .wrap { width: 1360px; }
      .panel, .metric, .card, .table, .callout, .evidence-card { box-shadow: none; }
    }
    @media screen and (max-width: 900px) {
      .slide { width: 1600px; height: 900px; }
    }
  </style>
</head>
<body>
  <article class="slide title-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="eyebrow">WEBSITE AUDIT | MAY 26, 2026</div>
      <h1>Ocular Therapeutix Website<br>Currentness Audit</h1>
      <p class="dek">This deck compares public website statements with the most recently available official registry or filing data, including website pages that present different status, count, or endpoint wording than those sources. Other timing differences were noted only when the public website presented a current claim with wording or values that differed from those sources.</p>
      <div class="grid-4" style="margin-top:28px;">
        <div class="metric"><div class="num">3</div><div class="label">Evidence-supported website-currentness observations.</div></div>
        <div class="metric"><div class="num">0</div><div class="label">Active-status Ocular Phase 2 sponsor records returned by CT.gov query.</div></div>
        <div class="metric"><div class="num">2</div><div class="label">Clinical-trials page observations: SOL-R count and HELIOS-3 endpoint text.</div></div>
        <div class="metric"><div class="num">4</div><div class="label">Prior observations not included as website-currentness observations in this review.</div></div>
      </div>
      <div class="callout" style="margin-top:24px;">
        <h3>Executive summary</h3>
        <ul class="summary-list">
          <li>The OTX-TIC page states OTX-TIC is currently in Phase 2; CT.gov lists the treatment record as completed, the active-status sponsor query returns zero Ocular Phase 2 records, and the current 10-Q states next steps are being evaluated.<a class="cite" href="${sourceUrls.otxTic}">1</a><a class="cite" href="${sourceUrls.ctgovOtxTic}">2</a><a class="cite" href="${sourceUrls.ctgovOcularActivePhase2}">8</a><a class="cite" href="${sourceUrls.sec10q}">3</a></li>
          <li>The Ocular clinical-trials page lists SOL-R as a 555-subject randomized trial, while the current filing reports completed randomization with 631 subjects.<a class="cite" href="${sourceUrls.clinicalTrials}">4</a><a class="cite" href="${sourceUrls.sec10q}">5</a></li>
          <li>The HELIOS-3 website description contains Week 56 in the endpoint heading and Week 52 in the endpoint sentence; the current filing states that the endpoint assessment was extended from Week 52 to Week 56.<a class="cite" href="${sourceUrls.clinicalTrials}">6</a><a class="cite" href="${sourceUrls.sec10q}">7</a></li>
        </ul>
      </div>
    </div>
    <div class="slide-num">1/5</div>
  </article>

  <article class="slide evidence-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">OTX-TIC status</div>
        <h2>Website Phase 2 wording compared with active-status Phase 2 treatment-trial checks</h2>
        <p>The CT.gov sponsor query identified no active-status Phase 2 Ocular records. Glaukos travoprost implant records list separate sponsors/products and were not included as Ocular OTX-TIC records for this status comparison.</p>
      </div>
      <div class="evidence-grid four">
        ${evidenceFigure(byId["source-01-otx-tic-website-phase2"], 1, "Ocular's OTX-TIC page states that OTX-TIC is currently in Phase 2 clinical trials.")}
        ${evidenceFigure(byId["source-02-ctgov-otx-tic-completed"], 2, "The OTX-TIC Phase 2 treatment record is listed as completed on ClinicalTrials.gov.")}
        ${evidenceFigure(byId["source-08-ctgov-active-phase2-zero"], 8, "A ClinicalTrials.gov active-status Phase 2 sponsor search for Ocular Therapeutix returns no records.")}
        ${evidenceFigure(byId["source-03-sec-otx-tic-completed"], 3, "The current 10-Q states that OTX-TIC has completed Phase 2 and that next steps are being evaluated.")}
      </div>
    </div>
    <div class="slide-num">2/5</div>
  </article>

  <article class="slide evidence-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">SOL-R randomized count</div>
        <h2>The SOL-R website count is 555 and the current filing reports 631 randomized subjects</h2>
        <p>The website page reports 555 randomized subjects; the May 2026 Form 10-Q reports completed randomization with 631 subjects.</p>
      </div>
      <div class="evidence-grid">
        ${evidenceFigure(byId["source-04-website-solr-555"], 4, "The Ocular clinical-trials page states that SOL-R has 555 total subjects randomized.")}
        ${evidenceFigure(byId["source-05-sec-solr-631"], 5, "The 10-Q reports that SOL-R completed randomization with 631 subjects and gives a Q1 2027 topline-data expectation.")}
      </div>
    </div>
    <div class="slide-num">3/5</div>
  </article>

  <article class="slide evidence-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">HELIOS-3 endpoint</div>
        <h2>The HELIOS-3 website text contains Week 56 and Week 52 endpoint language</h2>
        <p>This observation is not based on CT.gov showing Week 52; the website text contains both Week 56 and Week 52 endpoint references, while the current filing describes the February 2026 amendment to Week 56.</p>
      </div>
      <div class="evidence-grid">
        ${evidenceFigure(byId["source-06-website-helios-week52-week56"], 6, "The website's HELIOS-3 endpoint heading states Week 56, while the endpoint sentence states Week 52.")}
        ${evidenceFigure(byId["source-07-sec-helios-week56"], 7, "The 10-Q states that the HELIOS-3 protocol amendment extended endpoint assessment from Week 52 to Week 56.")}
      </div>
    </div>
    <div class="slide-num">4/5</div>
  </article>

  <article class="slide references-slide">
    ${backgroundSource ? '<img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />' : ""}
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">References 1-8</div>
        <h2>References</h2>
      </div>
      <div class="table">
        <div class="row refs head">
          <div class="cell">Ref</div>
          <div class="cell">Source</div>
          <div class="cell">Date / Status / Source Owner</div>
          <div class="cell">Evidence Used in Report</div>
        </div>
        <div class="row refs"><div class="cell">1</div><div class="cell"><a href="${sourceUrls.otxTic}">Ocular OTX-TIC page</a></div><div class="cell">Live website page / Ocular Therapeutix</div><div class="cell">Website statement that OTX-TIC is currently in Phase 2 clinical trials.</div></div>
        <div class="row refs"><div class="cell">2</div><div class="cell"><a href="${sourceUrls.ctgovOtxTic}">ClinicalTrials.gov NCT05335122</a></div><div class="cell">Registry record / Ocular Therapeutix sponsor</div><div class="cell">Completed Phase 2 OTX-TIC treatment record for OAG/OHT.</div></div>
        <div class="row refs"><div class="cell">3</div><div class="cell"><a href="${sourceUrls.sec10q}">Q1 2026 Form 10-Q</a></div><div class="cell">Filed May 2026 / Ocular Therapeutix</div><div class="cell">OTX-TIC completed Phase 2 and next steps are being evaluated.</div></div>
        <div class="row refs"><div class="cell">4</div><div class="cell"><a href="${sourceUrls.clinicalTrials}">Ocular clinical-trials page</a></div><div class="cell">Live website page / Ocular Therapeutix</div><div class="cell">SOL-R 555-subject randomized count shown on the website.</div></div>
        <div class="row refs"><div class="cell">5</div><div class="cell"><a href="${sourceUrls.sec10q}">Q1 2026 Form 10-Q</a></div><div class="cell">Filed May 2026 / Ocular Therapeutix</div><div class="cell">SOL-R completed randomization with 631 subjects and Q1 2027 topline timing.</div></div>
        <div class="row refs"><div class="cell">6</div><div class="cell"><a href="${sourceUrls.clinicalTrials}">Ocular clinical-trials page</a></div><div class="cell">Live website page / Ocular Therapeutix</div><div class="cell">HELIOS-3 Week 56 heading and Week 52 endpoint sentence.</div></div>
        <div class="row refs"><div class="cell">7</div><div class="cell"><a href="${sourceUrls.sec10q}">Q1 2026 Form 10-Q</a></div><div class="cell">Filed May 2026 / Ocular Therapeutix</div><div class="cell">HELIOS-3 protocol amendment extending primary endpoint assessment from Week 52 to Week 56.</div></div>
        <div class="row refs"><div class="cell">8</div><div class="cell"><a href="${sourceUrls.ctgovOcularActivePhase2}">ClinicalTrials.gov search results</a></div><div class="cell">Live registry webpage / Ocular sponsor search</div><div class="cell">Active-status Phase 2 sponsor search for Ocular Therapeutix returns no records.</div></div>
      </div>
    </div>
    <div class="slide-num">5/5</div>
  </article>
</body>
</html>`;
}

function writeSourceArtifacts(captures) {
  const log = `# Ocular Therapeutix Website Currentness Review Source Log

Scope: Web-only source review of Ocular Therapeutix public website statements versus the most recently available official online registry or filing data. Other timing differences were noted only when the website presented a current claim with wording or values that differed from those sources.

## Included References

${captures.map((item, index) => `${index + 1}. ${item.label}
   - URL: ${item.url}
   - Screenshot: ${rel(item.screenshotPath)}
   - Highlight status: ${item.found ? "text highlighted in rendered browser screenshot" : "specified text not located in rendered browser view; screenshot retained for documentation"}
`).join("\n")}
`.trimEnd() + "\n";
  fs.writeFileSync(path.join(dirs.sources, "source-log.md"), log);

  const manifest = ["label,path,caption", ...captures.map((item, index) => {
    const label = `Reference ${index + 1} - evidence`;
    return `${JSON.stringify(label)},${JSON.stringify(rel(item.screenshotPath))},${JSON.stringify(item.label)}`;
  })].join("\n");
  fs.writeFileSync(path.join(dirs.sources, "reference-screenshots.csv"), manifest);
}

function buildScreenshotAppendixHtml(captures) {
  const rows = captures.map((item, index) => `
  <section class="page">
    <div class="topline">
      <div>Reference ${index + 1}</div>
      <a href="${esc(item.url)}">${esc(new URL(item.url).hostname)}</a>
    </div>
    <h1>${esc(item.label)}</h1>
    <img src="${esc(pathToFileURL(item.screenshotPath).href)}" alt="${esc(item.label)}" />
    <p>${esc(item.url)}</p>
  </section>`).join("\n");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Ocular Therapeutix Website Currentness Audit Screenshot Appendix</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: #10120f;
      background: #f6f1e8;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .page {
      width: 1600px;
      height: 900px;
      padding: 28px 42px 24px;
      page-break-after: always;
      break-after: page;
      background: #f6f1e8;
    }
    .page:last-child { page-break-after: auto; break-after: auto; }
    .topline {
      display: flex;
      justify-content: space-between;
      gap: 24px;
      font-size: 18px;
      font-weight: 800;
      text-transform: uppercase;
      border-bottom: 2px solid #10120f;
      padding-bottom: 10px;
    }
    .topline a {
      text-transform: none;
      color: #5c6257;
      font-weight: 700;
    }
    h1 {
      margin: 16px 0 14px;
      font-size: 32px;
      line-height: 1.06;
      font-weight: 620;
    }
    img {
      display: block;
      width: 1516px;
      height: 622px;
      object-fit: contain;
      background: #fff;
      border: 2px solid #10120f;
    }
    p {
      margin: 9px 0 0;
      color: #5c6257;
      font-size: 12px;
      line-height: 1.12;
      overflow-wrap: anywhere;
    }
    @page { size: 1600px 900px; margin: 0; }
  </style>
</head>
<body>
${rows}
</body>
</html>`;
}

async function withBrowser(callback) {
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: ["--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check"],
  });
  try {
    return await callback(browser);
  } finally {
    await browser.close();
  }
}

async function exportPdfArtifacts(captures) {
  return withBrowser(async (browser) => {
    const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(outputFiles.reportHtml).href, { waitUntil: "networkidle" });
    await page.emulateMedia({ media: "print" });
    await page.pdf({
      path: outputFiles.reportPdf,
      width: "1600px",
      height: "900px",
      printBackground: true,
      preferCSSPageSize: true,
    });

    await page.setContent(buildScreenshotAppendixHtml(captures), { waitUntil: "load" });
    await page.pdf({
      path: outputFiles.screenshotAppendixPdf,
      width: "1600px",
      height: "900px",
      printBackground: true,
      preferCSSPageSize: true,
    });

    return {
      reportPdf: outputFiles.reportPdf,
      screenshotAppendixPdf: outputFiles.screenshotAppendixPdf,
    };
  });
}

async function verifyDeckLayout() {
  return withBrowser(async (browser) => {
    const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(outputFiles.reportHtml).href, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(dirs.render, "deck-render-review.png"), fullPage: true });
    const result = await page.evaluate(() => {
      const slides = Array.from(document.querySelectorAll(".slide"));
      const overflowItems = [];
      slides.forEach((slide, slideIndex) => {
        const slideRect = slide.getBoundingClientRect();
        const descendants = Array.from(slide.querySelectorAll("*"));
        descendants.forEach((element) => {
          if (element.classList.contains("slide-bg-img")) return;
          const style = window.getComputedStyle(element);
          if (style.display === "none" || style.visibility === "hidden") return;
          const rects = Array.from(element.getClientRects()).filter((rect) => rect.width > 0 && rect.height > 0);
          rects.forEach((rect) => {
            const outside =
              rect.left < slideRect.left - 1 ||
              rect.top < slideRect.top - 1 ||
              rect.right > slideRect.right + 1 ||
              rect.bottom > slideRect.bottom + 1;
            if (!outside) return;
            overflowItems.push({
              slide: slideIndex + 1,
              tag: element.tagName.toLowerCase(),
              className: element.className || "",
              rect: {
                left: Math.round(rect.left - slideRect.left),
                top: Math.round(rect.top - slideRect.top),
                right: Math.round(rect.right - slideRect.left),
                bottom: Math.round(rect.bottom - slideRect.top),
              },
            });
          });
        });
      });
      return { slideCount: slides.length, overflowItems };
    });
    if (result.slideCount !== 5) {
      throw new Error(`Expected 5 slides, found ${result.slideCount}`);
    }
    if (result.overflowItems.length) {
      throw new Error(`Deck overflow detected: ${JSON.stringify(result.overflowItems.slice(0, 10), null, 2)}`);
    }
    return {
      slideCount: result.slideCount,
      renderReviewScreenshot: path.join(dirs.render, "deck-render-review.png"),
    };
  });
}

async function main() {
  const captures = await captureScreenshots();
  writeSourceArtifacts(captures);
  const html = buildHtml(captures);
  fs.writeFileSync(outputFiles.reportHtml, html);
  const exports = await exportPdfArtifacts(captures);
  const layout = await verifyDeckLayout();
  console.log(JSON.stringify({
    runFolder,
    report: outputFiles.reportHtml,
    exports,
    layout,
    screenshots: captures.map((item) => ({ id: item.id, found: item.found, path: item.screenshotPath })),
  }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
