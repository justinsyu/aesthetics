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
const runDate = "June 2, 2026";
const runDateSlug = "2026-06-02";
const reportSlug = "biohaven_troriluzole_sca_crl_lessons";
const runFolder = path.join(repoRoot, "competitive_intelligence_reports", reportSlug, `${runDateSlug}_regulatory_lessons`);

const dirs = {
  evidence: path.join(runFolder, "screenshots", "evidence"),
  renderReview: path.join(runFolder, "screenshots", "render-review"),
  sources: path.join(runFolder, "sources"),
};
for (const dir of Object.values(dirs)) fs.mkdirSync(dir, { recursive: true });

const outputFiles = {
  reportHtml: path.join(runFolder, "report.html"),
  reportPdf: path.join(runFolder, `${reportSlug}-slide-deck-${runDateSlug}.pdf`),
  screenshotAppendixHtml: path.join(runFolder, "screenshot-appendix.html"),
  screenshotAppendixPdf: path.join(runFolder, `${reportSlug}-source-screenshots-${runDateSlug}.pdf`),
  sourceLog: path.join(dirs.sources, "source-log.md"),
  screenshotManifest: path.join(dirs.sources, "reference-screenshots.csv"),
  buildManifest: path.join(runFolder, "build-manifest.json"),
  renderReview: path.join(dirs.renderReview, "deck-render-review.png"),
};

const urls = {
  biohavenCrl: "https://ir.biohaven.com/news-releases/news-release-details/fda-issues-complete-response-letter-biohavens-vyglxia",
  fdaCrl: "https://download.open.fda.gov/crl/CRL_NDA210862_20251104.pdf",
  biohavenFailedTrial: "https://www.prnewswire.com/news-releases/biohaven-provides-update-on-phase-3-clinical-trial-evaluating-troriluzole-for-spinocerebellar-ataxia-sca-301552633.html",
  externalControlGuidance: "https://www.fda.gov/media/164960/download",
  skyclarys: "https://www.fda.gov/drugs/news-events-human-drugs/fda-approves-first-treatment-friedreichs-ataxia",
  skyclarysSnapshot: "https://www.fda.gov/drugs/drug-trials-snapshots/drug-trials-snapshots-skyclarys",
  radicavaReview: "https://www.accessdata.fda.gov/drugsatfda_docs/nda/2017/209176orig1s000medr.pdf",
  nurOwnUpdate: "https://www.fda.gov/vaccines-blood-biologics/cellular-gene-therapy-products/update-amyotrophic-lateral-sclerosis-als-product-development",
  qalsody: "https://www.fda.gov/drugs/news-events-human-drugs/fda-approves-treatment-amyotrophic-lateral-sclerosis-associated-mutation-sod1-gene",
};

const screenshotSpecs = [
  {
    id: "source-01-biohaven-crl-release",
    ref: 1,
    type: "html",
    label: "Biohaven CRL announcement",
    url: urls.biohavenCrl,
    owner: "Biohaven press release, November 4, 2025",
    evidence: "Biohaven announced FDA issued a CRL for VYGLXIA/troriluzole for SCA.",
    find: ["received a Complete Response Letter", "troriluzole's new drug application"],
  },
  {
    id: "source-02-fda-crl-effectiveness",
    ref: 2,
    type: "pdf",
    label: "FDA CRL: no substantial evidence and Study 206-RWE not adequate",
    url: urls.fdaCrl,
    page: 2,
    zoom: 100,
    owner: "FDA CRL for NDA 210862, November 4, 2025",
    evidence: "FDA concluded substantial evidence was not established and Study 206-RWE could not be considered adequate and well-controlled.",
    boxes: [
      { x: 438, y: 118, width: 875, height: 258, label: "Effectiveness deficiency" },
    ],
  },
  {
    id: "source-03-fda-crl-missing-data",
    ref: 3,
    type: "pdf",
    label: "FDA CRL: missing data and sensitivity analysis",
    url: urls.fdaCrl,
    page: 3,
    zoom: 100,
    owner: "FDA CRL for NDA 210862, November 4, 2025",
    evidence: "FDA cited 52% missing Year 3 f-SARA data in treated subjects, 79% in controls, and a nonsignificant Jump-to-Reference analysis.",
    boxes: [
      { x: 438, y: 96, width: 875, height: 284, label: "Missing-data concern" },
    ],
  },
  {
    id: "source-04-fda-crl-prespec-posthoc",
    ref: 4,
    type: "pdf",
    label: "FDA CRL: prespecification and post hoc subgroup limits",
    url: urls.fdaCrl,
    page: 4,
    zoom: 100,
    owner: "FDA CRL for NDA 210862, November 4, 2025",
    evidence: "FDA rejected Biohaven's prespecification argument because the RWE SAP was drafted with prior knowledge of related analyses and overlapping source data.",
    boxes: [
      { x: 438, y: 80, width: 875, height: 410, label: "Prespecification critique" },
    ],
  },
  {
    id: "source-05-biohaven-2022-failed-trial",
    ref: 5,
    type: "html",
    label: "Biohaven-issued 2022 Phase 3 update",
    url: urls.biohavenFailedTrial,
    owner: "Biohaven-issued PRNewswire release, May 23, 2022",
    evidence: "The original randomized Study 206 had minimal f-SARA separation in the overall study population and p=0.76.",
    find: ["overall study population (N=213)", "p=0.76"],
  },
  {
    id: "source-06-fda-external-control-guidance",
    ref: 6,
    type: "pdf",
    label: "FDA external-control guidance: finalize protocol and control arm before trial",
    url: urls.externalControlGuidance,
    page: 7,
    zoom: 100,
    owner: "FDA draft guidance, February 2023",
    evidence: "FDA guidance advised sponsors to finalize the protocol, external control arm, and analytic approach before initiating an externally controlled trial.",
    boxes: [
      { x: 442, y: 312, width: 865, height: 194, label: "Design-phase warning" },
    ],
  },
  {
    id: "source-07-skyclarys-rct-anchor",
    ref: 7,
    type: "html",
    label: "FDA Skyclarys approval page",
    url: urls.skyclarys,
    owner: "FDA approval page, February 28, 2023",
    evidence: "The closest ataxia precedent anchored approval in a randomized, placebo-controlled, double-blind 48-week study; the natural-history comparison was post hoc.",
    find: ["48-week randomized, placebo-controlled, and double-blind study", "post hoc analysis"],
  },
  {
    id: "source-08-skyclarys-exploratory-caution",
    ref: 8,
    type: "html",
    label: "FDA Skyclarys snapshot: natural-history analysis caution",
    url: urls.skyclarysSnapshot,
    owner: "FDA Drug Trials Snapshot",
    evidence: "FDA described the three-year natural-history comparison as post hoc and cautioned that externally collected data should be interpreted carefully.",
    clickText: "MORE INFO",
    find: ["There was a post hoc, propensity-matched analysis", "These exploratory analyses should be interpreted cautiously"],
  },
  {
    id: "source-09-radicava-review",
    ref: 9,
    type: "pdf",
    label: "FDA Radicava review: positive Study 19 plus post hoc Study 16 support",
    url: urls.radicavaReview,
    page: 11,
    zoom: 100,
    owner: "FDA Radicava clinical review, 2017",
    evidence: "FDA's approval rationale used a positive adequate and well-controlled Study 19 as the anchor, with Study 16 as confirmatory evidence.",
    boxes: [
      { x: 438, y: 88, width: 875, height: 420, label: "Prospective RCT anchor" },
    ],
  },
  {
    id: "source-10-nurown-als-update",
    ref: 10,
    type: "html",
    label: "FDA NurOwn ALS product-development update",
    url: urls.nurOwnUpdate,
    owner: "FDA public update, March 2, 2021",
    evidence: "FDA publicly stated that a randomized Phase 3 ALS trial did not meet primary or secondary endpoints and that a small responder difference was not statistically significant.",
    find: ["none of the primary or secondary endpoints were met", "not at all statistically significant"],
  },
];

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function rel(filePath) {
  return path.relative(runFolder, filePath).replaceAll(path.sep, "/");
}

function externalLink(url, text) {
  return `<a href="${esc(url)}">${esc(text)}</a>`;
}

async function dismissBanners(page) {
  for (const label of ["Accept All", "Accept Cookies", "Accept", "Reject All", "Reject", "I Accept", "Close"]) {
    const button = page.getByText(label, { exact: true }).first();
    if (await button.count().catch(() => 0)) await button.click({ timeout: 900, force: true }).catch(() => {});
  }
  await page.evaluate(() => {
    const selectors = [
      "[id*='cookie' i]",
      "[class*='cookie' i]",
      "[id*='onetrust' i]",
      "[class*='onetrust' i]",
      "[aria-label*='cookie' i]",
      "[role='dialog']",
      ".modal-backdrop",
      ".overlay",
    ];
    for (const element of document.querySelectorAll(selectors.join(","))) {
      const style = window.getComputedStyle(element);
      if (style.position === "fixed" || style.position === "sticky" || Number(style.zIndex) > 900) element.remove();
    }
  }).catch(() => {});
}

async function highlightHtml(page, phrases) {
  return page.evaluate((rawPhrases) => {
    document.querySelectorAll("[data-codex-highlight]").forEach((element) => element.remove());
    const phrases = rawPhrases.map((item) => item.replace(/\s+/g, " ").trim()).filter(Boolean);
    const rects = [];
    const normalize = (text) => text.replace(/\s+/g, " ").trim();
    const visibleRects = (range) => Array.from(range.getClientRects()).filter((rect) => rect.width > 2 && rect.height > 2);
    const locate = (phrase) => {
      const lowerPhrase = phrase.toLowerCase();
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const rawText = node.nodeValue || "";
        const directIndex = rawText.toLowerCase().indexOf(lowerPhrase);
        if (directIndex >= 0) {
          const range = document.createRange();
          range.setStart(node, directIndex);
          range.setEnd(node, directIndex + phrase.length);
          if (visibleRects(range).length) return range;
        }
        if (normalize(rawText).toLowerCase().includes(lowerPhrase)) {
          const range = document.createRange();
          range.selectNodeContents(node);
          if (visibleRects(range).length) return range;
        }
      }
      const blocks = Array.from(document.querySelectorAll("p,li,h1,h2,h3,h4,td,th,div"));
      const match = blocks.find((element) => normalize(element.innerText || "").toLowerCase().includes(lowerPhrase));
      if (match) {
        const range = document.createRange();
        range.selectNodeContents(match);
        if (visibleRects(range).length) return range;
      }
      return null;
    };
    const colors = [
      ["rgba(255, 229, 80, .65)", "#db6300"],
      ["rgba(117, 222, 255, .48)", "#057ea8"],
      ["rgba(204, 255, 84, .56)", "#536f00"],
    ];
    phrases.forEach((phrase, index) => {
      const range = locate(phrase);
      if (!range) return;
      for (const rect of visibleRects(range)) {
        const overlay = document.createElement("div");
        overlay.setAttribute("data-codex-highlight", "true");
        overlay.style.position = "absolute";
        overlay.style.left = `${window.scrollX + rect.left - 4}px`;
        overlay.style.top = `${window.scrollY + rect.top - 4}px`;
        overlay.style.width = `${rect.width + 8}px`;
        overlay.style.height = `${rect.height + 8}px`;
        overlay.style.background = colors[index % colors.length][0];
        overlay.style.border = `4px solid ${colors[index % colors.length][1]}`;
        overlay.style.borderRadius = "6px";
        overlay.style.pointerEvents = "none";
        overlay.style.mixBlendMode = "multiply";
        overlay.style.zIndex = "2147483647";
        document.body.appendChild(overlay);
        rects.push({ x: window.scrollX + rect.left, y: window.scrollY + rect.top, width: rect.width, height: rect.height });
      }
    });
    if (!rects.length) return { ok: false, pageTitle: document.title };
    const minX = Math.max(0, Math.min(...rects.map((rect) => rect.x)) - 260);
    const minY = Math.max(0, Math.min(...rects.map((rect) => rect.y)) - 180);
    const maxX = Math.max(...rects.map((rect) => rect.x + rect.width)) + 340;
    const maxY = Math.max(...rects.map((rect) => rect.y + rect.height)) + 230;
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
        height: Math.min(window.innerHeight - clipY, Math.max(480, maxY - minY)),
      },
    };
  }, phrases);
}

async function addPdfBoxes(page, boxes) {
  await page.evaluate((rawBoxes) => {
    document.querySelectorAll("[data-codex-pdf-box]").forEach((element) => element.remove());
    const colors = ["#db6300", "#057ea8", "#536f00"];
    rawBoxes.forEach((box, index) => {
      const overlay = document.createElement("div");
      overlay.setAttribute("data-codex-pdf-box", "true");
      overlay.style.position = "fixed";
      overlay.style.left = `${box.x}px`;
      overlay.style.top = `${box.y}px`;
      overlay.style.width = `${box.width}px`;
      overlay.style.height = `${box.height}px`;
      overlay.style.border = `6px solid ${colors[index % colors.length]}`;
      overlay.style.background = "rgba(255, 229, 80, .11)";
      overlay.style.borderRadius = "7px";
      overlay.style.pointerEvents = "none";
      overlay.style.zIndex = "2147483647";
      if (box.label) {
        const tag = document.createElement("div");
        tag.textContent = box.label;
        tag.style.position = "absolute";
        tag.style.left = "-6px";
        tag.style.top = "-34px";
        tag.style.padding = "5px 8px";
        tag.style.background = colors[index % colors.length];
        tag.style.color = "white";
        tag.style.font = "700 13px Arial, sans-serif";
        tag.style.borderRadius = "7px 7px 0 0";
        overlay.appendChild(tag);
      }
      document.body.appendChild(overlay);
    });
  }, boxes);
}

async function captureScreenshots() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: ["--disable-gpu", "--no-first-run", "--no-default-browser-check", "--disable-http2", "--hide-scrollbars"],
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36",
    extraHTTPHeaders: { "Accept-Language": "en-US,en;q=0.9" },
  });
  const page = await context.newPage();
  page.setDefaultTimeout(45000);
  const outputs = [];
  try {
    for (const spec of screenshotSpecs) {
      console.log(`Capturing ${spec.id}`);
      const screenshotPath = path.join(dirs.evidence, `${spec.id}.png`);
      let result = { ok: true, pageTitle: "" };
      if (spec.type === "pdf") {
        const pdfUrl = `${spec.url}#page=${spec.page}&zoom=${spec.zoom || 100}`;
        await page.goto(pdfUrl, { waitUntil: "domcontentloaded", timeout: 65000 });
        await page.waitForTimeout(4500);
        await addPdfBoxes(page, spec.boxes);
        await page.waitForTimeout(400);
        await page.screenshot({ path: screenshotPath, clip: { x: 300, y: 56, width: 1080, height: 820 } });
        result.pageTitle = await page.title().catch(() => "");
      } else {
        await page.goto(spec.url, { waitUntil: "commit", timeout: 65000 });
        await page.waitForLoadState("domcontentloaded", { timeout: 25000 }).catch(() => {});
        await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
        await dismissBanners(page);
        if (spec.clickText) {
          const trigger = page.getByText(spec.clickText, { exact: true }).first();
          if (await trigger.count().catch(() => 0)) {
            await trigger.click({ timeout: 2500 }).catch(() => {});
            await page.waitForTimeout(500);
          }
        }
        result = await highlightHtml(page, spec.find);
        await page.waitForTimeout(350);
        await page.screenshot(result.ok && result.clip ? { path: screenshotPath, clip: result.clip } : { path: screenshotPath, fullPage: false });
      }
      outputs.push({ ...spec, screenshotPath, found: Boolean(result.ok), pageTitle: result.pageTitle || "" });
    }
  } finally {
    await browser.close();
  }
  return outputs;
}

function evidenceFigure(item, note) {
  return `
    <figure class="evidence-card">
      <div class="evidence-top"><span>Reference ${item.ref}</span>${externalLink(item.url, new URL(item.url).hostname)}</div>
      <img src="${esc(rel(item.screenshotPath))}" alt="${esc(item.label)}" />
      <figcaption>${esc(note || item.evidence)}</figcaption>
    </figure>`;
}

function compactEvidence(item, note) {
  return `
    <figure class="mini-evidence">
      <div class="mini-ref">Ref ${item.ref}</div>
      <img src="${esc(rel(item.screenshotPath))}" alt="${esc(item.label)}" />
      <figcaption>${esc(note || item.evidence)}</figcaption>
    </figure>`;
}

function sourceRows(captures) {
  return captures.map((item) => `
    <div class="source-row">
      <div class="source-ref">${item.ref}</div>
      <div><strong>${esc(item.label)}</strong><br><span>${esc(item.owner)}</span></div>
      <div>${externalLink(item.url, item.url)}</div>
      <div>${esc(item.evidence)}</div>
    </div>`).join("");
}

function buildHtml(captures) {
  const byId = Object.fromEntries(captures.map((item) => [item.id, item]));
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Biohaven Troriluzole SCA CRL Lessons</title>
  <style>
    :root {
      --ink: #151816;
      --muted: #59615c;
      --paper: #f8f3ea;
      --paper-2: #eee5d7;
      --line: #222720;
      --lime: #d7ff5f;
      --cyan: #75deff;
      --orange: #ff9b54;
      --deep: #11140f;
      --shadow: 0 16px 36px rgba(16, 18, 15, .08);
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; background: var(--paper); color: var(--ink); scrollbar-width: none; }
    html::-webkit-scrollbar, body::-webkit-scrollbar { display: none; }
    body, *, *::before, *::after { -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    a { color: inherit; text-decoration-thickness: 1px; text-underline-offset: 3px; }
    .slide { width: 100vw; height: 100vh; min-height: 100vh; overflow: hidden; position: relative; display: flex; align-items: flex-start; padding: 34px 0 20px; page-break-after: always; break-after: page; background: radial-gradient(circle at 86% 12%, rgba(117,222,255,.2), transparent 28%), var(--paper); }
    .slide.dark { background: var(--deep); color: var(--paper); }
    .slide:last-child { page-break-after: auto; break-after: auto; }
    .wrap { width: min(1450px, calc(100vw - 64px)); margin: 0 auto; position: relative; z-index: 1; }
    .eyebrow { display: inline-flex; border: 1.5px solid currentColor; padding: 7px 12px; border-radius: 999px; font-size: 14px; font-weight: 850; text-transform: uppercase; margin-bottom: 18px; background: var(--lime); color: var(--ink); }
    .dark .eyebrow { border-color: var(--lime); }
    h1, h2, h3, p { margin: 0; }
    h1 { font-size: 71px; line-height: .94; font-weight: 560; letter-spacing: 0; max-width: 1320px; }
    h2 { font-size: 43px; line-height: 1; font-weight: 590; letter-spacing: 0; max-width: 1400px; }
    h3 { font-size: 23px; line-height: 1.05; font-weight: 740; letter-spacing: 0; }
    .dek { margin-top: 20px; color: var(--muted); font-size: 23px; line-height: 1.2; max-width: 1330px; }
    .dark .dek, .dark .note, .dark li, .dark .muted { color: rgba(248,243,234,.78); }
    .section-head { margin-bottom: 14px; }
    .section-head p { margin-top: 12px; color: var(--muted); font-size: 19px; line-height: 1.16; max-width: 1380px; }
    .dark .section-head p { color: rgba(248,243,234,.76); }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 22px; }
    .grid-2 { display: grid; grid-template-columns: 1.02fr .98fr; gap: 18px; align-items: stretch; }
    .grid-2.wide-left { grid-template-columns: 1.18fr .82fr; }
    .metric, .callout, .evidence-card, .mini-evidence, .lesson-card, .source-table { border: 1.5px solid var(--line); background: rgba(255,250,242,.94); border-radius: 8px; box-shadow: var(--shadow); overflow: hidden; }
    .dark .metric, .dark .lesson-card { background: rgba(255,255,255,.08); border-color: rgba(248,243,234,.32); color: var(--paper); }
    .metric { min-height: 132px; padding: 17px; }
    .num { font-size: 42px; line-height: .92; font-weight: 560; }
    .label { margin-top: 9px; font-size: 17px; line-height: 1.12; color: var(--muted); }
    .dark .label { color: rgba(248,243,234,.72); }
    .callout { background: var(--deep); color: var(--paper); border-color: var(--deep); padding: 18px 22px; margin-top: 18px; }
    .callout h3 { color: var(--lime); }
    ul { margin: 12px 0 0; padding-left: 22px; display: grid; gap: 8px; }
    li { font-size: 20px; line-height: 1.15; }
    .evidence-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; align-items: stretch; }
    .evidence-card, .mini-evidence { display: flex; flex-direction: column; min-height: 0; margin: 0; }
    .evidence-top { display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 7px 10px; border-bottom: 1px solid var(--line); background: var(--paper-2); font-size: 12px; font-weight: 850; text-transform: uppercase; }
    .evidence-top a { text-transform: none; font-weight: 700; color: var(--muted); }
    .evidence-card img { width: 100%; height: 462px; object-fit: contain; object-position: center; background: white; border-bottom: 1px solid rgba(16,18,15,.22); }
    .evidence-card.tall img { height: 590px; }
    figcaption { margin: 0; padding: 9px 11px 11px; color: var(--muted); font-size: 15.5px; line-height: 1.12; }
    .mini-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
    .mini-evidence img { width: 100%; height: 228px; object-fit: contain; background: white; border-bottom: 1px solid rgba(16,18,15,.22); }
    .mini-ref { padding: 6px 9px; font-size: 12px; font-weight: 850; text-transform: uppercase; border-bottom: 1px solid var(--line); background: var(--paper-2); }
    .mini-evidence figcaption { font-size: 13.5px; line-height: 1.08; padding: 8px 9px; }
    .lesson-stack { display: grid; gap: 12px; }
    .lesson-card { padding: 15px 17px; }
    .lesson-card h3 { margin-bottom: 8px; }
    .lesson-card p { color: var(--muted); font-size: 18px; line-height: 1.16; }
    .dark .lesson-card p { color: rgba(248,243,234,.74); }
    .pill { display: inline-flex; padding: 5px 8px; border-radius: 999px; background: var(--cyan); color: var(--ink); font-size: 13px; font-weight: 850; text-transform: uppercase; margin-bottom: 8px; }
    .table-grid { display: grid; grid-template-columns: .36fr 1fr 1fr; gap: 12px; margin-top: 20px; }
    .table-card { border: 1.5px solid var(--line); background: rgba(255,250,242,.94); border-radius: 8px; padding: 15px; min-height: 250px; }
    .table-card h3 { margin-bottom: 10px; }
    .table-card p { color: var(--muted); font-size: 18px; line-height: 1.18; }
    .table-card .big { font-size: 34px; font-weight: 650; color: var(--ink); line-height: 1; }
    .source-table { display: grid; margin-top: 14px; box-shadow: none; }
    .source-row { display: grid; grid-template-columns: 44px 260px 440px 1fr; border-bottom: 1px solid var(--line); min-height: 54px; }
    .source-row:last-child { border-bottom: 0; }
    .source-row > div { padding: 8px 10px; border-right: 1px solid var(--line); font-size: 13.2px; line-height: 1.08; overflow-wrap: anywhere; }
    .source-row > div:last-child { border-right: 0; }
    .source-row span { color: var(--muted); }
    .source-ref { display: flex; align-items: center; justify-content: center; font-weight: 900; background: var(--lime); }
    .cite { font-size: .58em; vertical-align: super; margin-left: 2px; font-weight: 900; text-decoration: none; }
    .slide-num { position: absolute; right: 38px; bottom: 22px; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: rgba(16,18,15,.42); font-weight: 850; z-index: 2; }
    .dark .slide-num { color: rgba(248,243,234,.36); }
    .split { display: grid; grid-template-columns: .8fr 1.2fr; gap: 18px; }
    .leadbox { border-left: 8px solid var(--orange); padding-left: 18px; margin-top: 20px; }
    .leadbox p { font-size: 28px; line-height: 1.08; max-width: 760px; }
    @page { size: 1600px 900px; margin: 0; }
    @media print {
      html, body { width: 1600px; height: 900px; }
      .slide { width: 1600px; height: 900px; min-height: 900px; padding: 34px 0 20px; }
      .wrap { width: 1450px; }
      .metric, .callout, .evidence-card, .mini-evidence, .lesson-card, .source-table { box-shadow: none; }
    }
    @media screen and (max-width: 900px) { .slide { width: 1600px; height: 900px; } }
  </style>
</head>
<body>
  <article class="slide dark">
    <div class="wrap">
      <div class="eyebrow">Regulatory lessons deck | ${esc(runDate)}</div>
      <h1>Biohaven's troriluzole CRL was broadly foreseeable</h1>
      <p class="dek">FDA's November 4, 2025 CRL for VYGLXIA/troriluzole in spinocerebellar ataxia was not inevitable from the public record, but the risk pattern was visible: a failed randomized primary endpoint, a post hoc/external-control rescue strategy, and public FDA guidance warning that such designs need prospective discipline.</p>
      <div class="grid-3">
        <div class="metric"><div class="num">Nov. 4, 2025</div><div class="label">Most recent public FDA CRL for NDA 210862.</div></div>
        <div class="metric"><div class="num">206-RWE</div><div class="label">FDA said the RWE study could not serve as adequate and well-controlled evidence.</div></div>
        <div class="metric"><div class="num">Avoidable risk</div><div class="label">The exact FDA action was uncertain, but the evidence gap was knowable before filing.</div></div>
      </div>
      <div class="leadbox"><p>The practical lesson: post hoc RWE can sometimes support a file, but it is a poor substitute for a new prospective controlled trial after the original pivotal endpoint misses.</p></div>
    </div>
    <div class="slide-num">1/10</div>
  </article>

  <article class="slide">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">What FDA decided</div>
        <h2>The CRL's core finding was evidentiary, not a narrow labeling or manufacturing fix</h2>
        <p>Biohaven announced the CRL publicly, and FDA's letter stated that substantial evidence of effectiveness had not been established. FDA's path forward was data from an adequate and well-controlled study on a clinically meaningful endpoint.</p>
      </div>
      <div class="evidence-grid">
        ${evidenceFigure(byId["source-01-biohaven-crl-release"], "Biohaven announced receipt of the CRL for VYGLXIA/troriluzole's SCA NDA.")}
        ${evidenceFigure(byId["source-02-fda-crl-effectiveness"], "FDA wrote that substantial evidence had not been established and that Study 206-RWE could not be considered adequate and well-controlled.")}
      </div>
    </div>
    <div class="slide-num">2/10</div>
  </article>

  <article class="slide">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Why Study 206-RWE broke down</div>
        <h2>FDA's concerns tracked the standard external-control failure modes</h2>
        <p>The CRL cited missing data, informative censoring, a nonsignificant prespecified sensitivity analysis, timing bias, measurement mismatch, incomplete comparability, and lack of true prespecification.</p>
      </div>
      <div class="evidence-grid">
        ${evidenceFigure(byId["source-03-fda-crl-missing-data"], "FDA highlighted 52% missing Year 3 treated-subject data, 79% missing external-control data, and a Jump-to-Reference analysis that became nonsignificant.")}
        ${evidenceFigure(byId["source-04-fda-crl-prespec-posthoc"], "FDA said the 2024 protocol/SAP were drafted with prior knowledge of overlapping Study 206 and natural-history analyses, undercutting prespecification.")}
      </div>
    </div>
    <div class="slide-num">3/10</div>
  </article>

  <article class="slide dark">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">First warning sign</div>
        <h2>Biohaven's own randomized trial had already missed in the overall SCA population</h2>
        <p>Once the controlled 48-week study missed, the approval case became a rescue strategy. That did not make approval impossible, but it materially raised the evidentiary bar for any post hoc subgroup or external-control package.</p>
      </div>
      <div class="grid-2">
        <div>
          ${evidenceFigure(byId["source-05-biohaven-2022-failed-trial"], "The 2022 Biohaven-issued update reported minimal f-SARA change at 48 weeks in the overall Study 206 population, with p=0.76.")}
        </div>
        <div class="lesson-stack">
          <div class="lesson-card"><span class="pill">Learning</span><h3>Use failed trial signals to design the next prospective test</h3><p>Radicava's precedent shows a cleaner path: use a post hoc signal to define a narrower, prospective, controlled trial rather than asking FDA to treat the post hoc reconstruction as the pivotal proof.</p></div>
          <div class="lesson-card"><span class="pill">Learning</span><h3>Subgroup rescue carries multiplicity and credibility risk</h3><p>The CRL later stated that Study 206 failed its prespecified endpoint and that SCA3 subgroup analyses were not prespecified or clinically/statistically persuasive after accounting for comparisons and covariates.</p></div>
          <div class="lesson-card"><span class="pill">Decision point</span><h3>The fork should have been visible after 2022</h3><p>Biohaven needed either a new adequate and well-controlled SCA trial or a prospectively locked external-control design before the relevant treatment and natural-history outcomes were known.</p></div>
        </div>
      </div>
    </div>
    <div class="slide-num">4/10</div>
  </article>

  <article class="slide">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Public FDA guidance</div>
        <h2>The 2023 external-control guidance foreshadowed the exact weak spots FDA later cited</h2>
        <p>FDA had already warned that external-control designs should lock the protocol, external control arm, and analytic approach before the trial, with attention to confounding, comparable measurements, follow-up timing, endpoint definition, and missing data.</p>
      </div>
      <div class="grid-2 wide-left">
        ${evidenceFigure(byId["source-06-fda-external-control-guidance"], "FDA's draft guidance advised sponsors to finalize the protocol, external-control arm, and analytic approach before initiating an externally controlled trial.")}
        <div class="lesson-stack">
          <div class="lesson-card"><span class="pill">Mapped to the CRL</span><h3>Prespecification</h3><p>FDA rejected Biohaven's prespecification argument because the 2024 SAP came after prior MAIC analyses and knowledge of overlapping data.</p></div>
          <div class="lesson-card"><span class="pill">Mapped to the CRL</span><h3>Comparability</h3><p>FDA cited unmeasured confounding from supportive treatments, comorbidities, geography, baseline progression, and site/expectation bias.</p></div>
          <div class="lesson-card"><span class="pill">Mapped to the CRL</span><h3>Data quality</h3><p>FDA cited missing f-SARA data, timing differences between 336-day and 365-day windows, and outcome-measure mismatch between f-SARA and SARA-derived f-SARA.</p></div>
        </div>
      </div>
    </div>
    <div class="slide-num">5/10</div>
  </article>

  <article class="slide">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Ataxia comparator</div>
        <h2>Skyclarys showed FDA could be flexible in ataxia, but the anchor was still randomized evidence</h2>
        <p>Omaveloxolone's FA approval was the closest disease-area precedent. FDA described the randomized, placebo-controlled 48-week study as the efficacy basis, while the natural-history comparison was post hoc and exploratory.</p>
      </div>
      <div class="evidence-grid">
        ${evidenceFigure(byId["source-07-skyclarys-rct-anchor"], "FDA's approval page stated that Skyclarys was evaluated in a 48-week randomized, placebo-controlled, double-blind study; the long-term natural-history comparison was post hoc.")}
        ${evidenceFigure(byId["source-08-skyclarys-exploratory-caution"], "FDA's snapshot cautioned that the post hoc natural-history comparison should be interpreted carefully because the data were collected outside a controlled study.")}
      </div>
    </div>
    <div class="slide-num">6/10</div>
  </article>

  <article class="slide dark">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Neuro comparator</div>
        <h2>Radicava suggests the better way to use post hoc evidence</h2>
        <p>Edaravone's approval was not a template for relying on an after-the-fact external comparator as the pivotal proof. FDA's review anchored approval in positive Study 19 and treated the earlier post hoc Study 16 analysis as confirmatory support.</p>
      </div>
      <div class="grid-2">
        ${evidenceFigure(byId["source-09-radicava-review"], "FDA concluded approval was supported by positive Study 19, an adequate and well-controlled randomized study, plus confirmatory evidence from Study 16.")}
        <div class="lesson-stack">
          <div class="lesson-card"><span class="pill">Lesson</span><h3>Convert retrospective learning into prospective proof</h3><p>The more defensible approach is to use subgroup or endpoint learnings from a failed trial to specify a new controlled trial population and analysis.</p></div>
          <div class="lesson-card"><span class="pill">Implication</span><h3>Biohaven's package ran the argument in reverse</h3><p>Study 206 missed first, then Study 206-RWE and genotype narratives attempted to rescue the file after substantial knowledge of trial and natural-history outcomes.</p></div>
          <div class="lesson-card"><span class="pill">Risk</span><h3>Rare disease does not remove the AWC requirement</h3><p>FDA can exercise flexibility, but the CRL shows it still expects a credible route to distinguishing drug effect from natural history, expectation bias, and missingness.</p></div>
        </div>
      </div>
    </div>
    <div class="slide-num">7/10</div>
  </article>

  <article class="slide">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Flexibility boundary</div>
        <h2>NurOwn showed that unmet need and patient urgency do not rescue a failed controlled trial</h2>
        <p>FDA's public ALS update is a useful negative comparator: even in a severe neurodegenerative disease, FDA emphasized that primary and secondary endpoints were not met and that a small responder difference was not statistically significant.</p>
      </div>
      <div class="grid-2">
        ${evidenceFigure(byId["source-10-nurown-als-update"], "FDA stated that NurOwn's randomized Phase 3 trial did not meet primary or secondary endpoints and that the responder difference was not statistically significant.")}
        <div class="lesson-stack">
          <div class="lesson-card"><span class="pill">Not enough</span><h3>Need cannot substitute for study validity</h3><p>The CRL repeatedly returned to whether the data could reliably isolate treatment effect. Biohaven's external-control biases made that uncertain.</p></div>
          <div class="lesson-card"><span class="pill">Different precedent</span><h3>Qalsody is not a close analog</h3><p>Tofersen's accelerated approval rested on a mechanistically coherent biomarker-surrogate argument from a controlled study. Troriluzole did not have a comparable accepted surrogate endpoint.</p></div>
          <div class="lesson-card"><span class="pill">Different precedent</span><h3>Relyvrio was fragile, but still randomized</h3><p>AMX0035 was approved on a positive randomized controlled trial and was later withdrawn after a larger trial failed. It was not an external-natural-history primary case.</p></div>
        </div>
      </div>
    </div>
    <div class="slide-num">8/10</div>
  </article>

  <article class="slide dark">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">What should have changed</div>
        <h2>The avoidable part was the evidentiary strategy, not every FDA judgment call</h2>
        <p>The public record did not guarantee a CRL, but it made the risk visible. The prevention plan needed to attack the exact threats FDA later named.</p>
      </div>
      <div class="table-grid">
        <div class="table-card"><div class="big">1</div><h3>Run a new controlled trial</h3><p>Prospectively enrich or stratify based on the strongest biological/clinical signal, lock f-SARA endpoint handling, and use the prior trial as design learning.</p></div>
        <div class="table-card"><div class="big">2</div><h3>If using external controls, lock them early</h3><p>Select natural-history data, eligibility, follow-up windows, endpoint collection, missing-data handling, and sensitivity analyses before treatment and control outcomes are known.</p></div>
        <div class="table-card"><div class="big">3</div><h3>Make the effect robust to bias</h3><p>Harmonize measurement, minimize missingness, blind raters where possible, control site effects, and require sensitivity analyses to survive plausible unmeasured confounding.</p></div>
      </div>
      <div class="callout">
        <h3>Conclusion</h3>
        <ul>
          <li>Foreseeable: FDA's CRL objections aligned with public guidance and comparator precedents.</li>
          <li>Not fully predetermined: Biohaven had FDA interactions and a rare-disease context, but the public evidence package still carried obvious confirmatory-evidence risk.</li>
          <li>Operational lesson: after a failed randomized endpoint, retrospective RWE should generally guide the next trial, not become the primary substitute for one.</li>
        </ul>
      </div>
    </div>
    <div class="slide-num">9/10</div>
  </article>

  <article class="slide">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Source log</div>
        <h2>Primary source screenshots retained with browser-rendered bounding boxes</h2>
        <p>Every screenshot in this deck was captured from a webpage or PDF opened in Chrome. Orange/cyan bounding boxes mark the specific passages used for the analysis.</p>
      </div>
      <div class="source-table">
        ${sourceRows(captures)}
      </div>
    </div>
    <div class="slide-num">10/10</div>
  </article>

  <script>
    const slides = [...document.querySelectorAll(".slide")];
    let current = 0;
    function show(index) {
      current = Math.max(0, Math.min(slides.length - 1, index));
      slides[current].scrollIntoView({ behavior: "smooth", block: "start" });
    }
    document.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight" || event.key === "PageDown") show(current + 1);
      if (event.key === "ArrowLeft" || event.key === "PageUp") show(current - 1);
      if (event.key === "Home") show(0);
      if (event.key === "End") show(slides.length - 1);
    });
  </script>
</body>
</html>`;
}

function buildAppendixHtml(captures) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Biohaven Troriluzole SCA CRL Source Screenshots</title>
  <style>
    * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: Inter, Arial, sans-serif; }
    body { margin: 0; background: #f8f3ea; color: #151816; }
    .page { width: 1600px; height: 900px; padding: 34px 44px 30px; page-break-after: always; break-after: page; overflow: hidden; }
    .page:last-child { page-break-after: auto; break-after: auto; }
    h1 { margin: 0 0 10px; font-size: 42px; line-height: 1; }
    p { margin: 0 0 16px; color: #59615c; font-size: 18px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    figure { margin: 0; border: 1.5px solid #222720; background: #fffaf2; border-radius: 8px; overflow: hidden; }
    img { display: block; width: 100%; height: 650px; object-fit: contain; background: white; border-bottom: 1px solid #222720; }
    figcaption { padding: 10px 12px; font-size: 15px; line-height: 1.12; color: #59615c; }
    .ref { padding: 7px 12px; background: #d7ff5f; border-bottom: 1px solid #222720; font-weight: 850; text-transform: uppercase; font-size: 13px; }
    @page { size: 1600px 900px; margin: 0; }
  </style>
</head>
<body>
  ${captures.map((item) => `
    <section class="page">
      <h1>Reference ${item.ref}: ${esc(item.label)}</h1>
      <p>${esc(item.owner)} | ${esc(item.url)}</p>
      <figure>
        <div class="ref">Browser-rendered source screenshot with bounding box</div>
        <img src="${esc(rel(item.screenshotPath))}" alt="${esc(item.label)}" />
        <figcaption>${esc(item.evidence)}</figcaption>
      </figure>
    </section>`).join("")}
</body>
</html>`;
}

function writeSourceFiles(captures) {
  const log = `# Biohaven Troriluzole SCA CRL Lessons Source Log

Run date: ${runDate}

Screenshots were captured from source webpages or PDF files opened in Chrome. Highlight boxes were drawn in the browser session before screenshot capture.

${captures.map((item) => `## Reference ${item.ref}: ${item.label}

- URL: ${item.url}
- Owner/date: ${item.owner}
- Evidence use: ${item.evidence}
- Screenshot: ${rel(item.screenshotPath)}
- Highlight status: ${item.found ? "relevant content boxed/highlighted in rendered browser screenshot" : "requested text not found; screenshot retained for review"}`).join("\n\n")}
`;
  fs.writeFileSync(outputFiles.sourceLog, log);

  const rows = ["reference,screenshot,label,url,evidence"];
  for (const item of captures) {
    rows.push([
      JSON.stringify(`Reference ${item.ref}`),
      JSON.stringify(rel(item.screenshotPath)),
      JSON.stringify(item.label),
      JSON.stringify(item.url),
      JSON.stringify(item.evidence),
    ].join(","));
  }
  fs.writeFileSync(outputFiles.screenshotManifest, rows.join("\n") + "\n");
}

async function exportAndCheck() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: ["--disable-gpu", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars"],
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
  try {
    await page.goto(pathToFileURL(outputFiles.reportHtml).href, { waitUntil: "networkidle" });
    await page.pdf({
      path: outputFiles.reportPdf,
      width: "1600px",
      height: "900px",
      printBackground: true,
      preferCSSPageSize: true,
      margin: { top: "0px", right: "0px", bottom: "0px", left: "0px" },
    });
    await page.screenshot({ path: outputFiles.renderReview, fullPage: true });
    const check = await page.evaluate(() => {
      const overflowItems = [];
      document.querySelectorAll(".slide").forEach((slide, slideIndex) => {
        const slideRect = slide.getBoundingClientRect();
        for (const element of slide.querySelectorAll("h1,h2,h3,p,li,figcaption,.metric,.evidence-card,.mini-evidence,.lesson-card,.source-table,.table-card")) {
          const rect = element.getBoundingClientRect();
          if (rect.width === 0 || rect.height === 0) continue;
          if (rect.right > slideRect.right + 1 || rect.bottom > slideRect.bottom + 1 || rect.left < slideRect.left - 1 || rect.top < slideRect.top - 1) {
            overflowItems.push({
              slide: slideIndex + 1,
              tag: element.tagName,
              className: element.className,
              text: (element.textContent || "").slice(0, 80),
              rect: { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom },
              slideRect: { left: slideRect.left, top: slideRect.top, right: slideRect.right, bottom: slideRect.bottom },
            });
          }
        }
      });
      return { slideCount: document.querySelectorAll(".slide").length, overflowItems };
    });
    if (check.slideCount !== 10) throw new Error(`Expected 10 slides, found ${check.slideCount}`);
    if (check.overflowItems.length) throw new Error(`Slide overflow detected: ${JSON.stringify(check.overflowItems, null, 2)}`);

    await page.goto(pathToFileURL(outputFiles.screenshotAppendixHtml).href, { waitUntil: "networkidle" });
    await page.pdf({
      path: outputFiles.screenshotAppendixPdf,
      width: "1600px",
      height: "900px",
      printBackground: true,
      preferCSSPageSize: true,
      margin: { top: "0px", right: "0px", bottom: "0px", left: "0px" },
    });
  } finally {
    await browser.close();
  }
}

async function main() {
  const captures = await captureScreenshots();
  fs.writeFileSync(outputFiles.reportHtml, buildHtml(captures));
  fs.writeFileSync(outputFiles.screenshotAppendixHtml, buildAppendixHtml(captures));
  writeSourceFiles(captures);
  await exportAndCheck();
  fs.writeFileSync(outputFiles.buildManifest, JSON.stringify({
    runDate,
    reportHtml: outputFiles.reportHtml,
    reportPdf: outputFiles.reportPdf,
    screenshotAppendixPdf: outputFiles.screenshotAppendixPdf,
    sourceLog: outputFiles.sourceLog,
    screenshotManifest: outputFiles.screenshotManifest,
    renderReview: outputFiles.renderReview,
    screenshots: captures.map((item) => ({
      ref: item.ref,
      id: item.id,
      found: item.found,
      path: item.screenshotPath,
      url: item.url,
    })),
  }, null, 2));
  console.log(JSON.stringify({
    reportHtml: outputFiles.reportHtml,
    reportPdf: outputFiles.reportPdf,
    screenshotAppendixPdf: outputFiles.screenshotAppendixPdf,
    sourceLog: outputFiles.sourceLog,
    screenshotManifest: outputFiles.screenshotManifest,
    buildManifest: outputFiles.buildManifest,
    renderReview: outputFiles.renderReview,
  }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
