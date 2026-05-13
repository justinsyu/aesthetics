import { chromium } from "/tmp/als-ci-playwright/node_modules/playwright/index.mjs";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/als/2026-05-12_1234";

const jobs = [
  {
    url: "https://www.globenewswire.com/news-release/2026/05/07/3290601/0/en/leonabio-reports-first-quarter-2026-financial-results-and-provides-business-update.html",
    output: `${runDir}/screenshots/date-verification/source-02-leonabio-ath1105-date.png`,
    needles: ["May 07, 2026 16:05 ET"],
    className: "codex-ci-date"
  },
  {
    url: "https://www.globenewswire.com/news-release/2026/05/07/3290601/0/en/leonabio-reports-first-quarter-2026-financial-results-and-provides-business-update.html",
    output: `${runDir}/screenshots/evidence/source-02-leonabio-ath1105-evidence.png`,
    needles: ["On-track to Initiate Phase 2 Proof-of-Concept Study of ATH-1105 in ALS patients in 2H 2026"],
    className: "codex-ci-evidence"
  },
  {
    url: "https://clinicaltrials.gov/study/NCT07571174",
    output: `${runDir}/screenshots/evidence/source-05-ctgov-lilly-ly4256984-evidence.png`,
    needles: ["The main purpose of this study is to assess the long-term safety and tolerability of LY4256984 in participants with Amyotrophic Lateral Sclerosis (ALS)."],
    className: "codex-ci-evidence"
  },
  {
    url: "https://clinicaltrials.gov/study/NCT04297683",
    output: `${runDir}/screenshots/evidence/source-07-ctgov-healey-master-evidence.png`,
    needles: ["The HEALEY ALS Platform Trial is a perpetual multi-center, multi-regimen clinical trial evaluating the safety and efficacy of investigational products for the treatment of ALS."],
    className: "codex-ci-evidence"
  }
];

async function settle(page) {
  await page.waitForLoadState("domcontentloaded", { timeout: 45000 }).catch(() => {});
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  await page.waitForTimeout(1400);
}

async function prepare(page) {
  await page.addStyleTag({
    content: `
      mark.codex-ci-mark {
        background: rgba(255, 223, 0, .42) !important;
        color: inherit !important;
        outline: 5px solid #ffdf00 !important;
        outline-offset: 3px !important;
        box-shadow: 0 0 0 3px rgba(16,18,15,.95), 0 0 0 11px rgba(255,223,0,.28) !important;
      }
      mark.codex-ci-date {
        background: rgba(255, 184, 107, .42) !important;
        outline-color: #ff8a00 !important;
      }
    `
  });
  await page.evaluate(() => {
    for (const button of Array.from(document.querySelectorAll("button, a, [role='button'], input[type='button'], input[type='submit']"))) {
      const text = (button.innerText || button.value || button.getAttribute("aria-label") || "").trim();
      if (/^(accept|agree|close|dismiss|continue|got it|ok|i agree|allow all|reject all|no thanks)$/i.test(text)) {
        try { button.click(); } catch {}
      }
    }
    for (const node of Array.from(document.querySelectorAll("body *"))) {
      const style = getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      const topChrome = (style.position === "fixed" || style.position === "sticky") && rect.top <= 5 && rect.width > 500 && rect.height > 35;
      const obviousOverlay = /cookie|privacy|consent|subscribe|newsletter|modal|popup|interstitial|chat|drift|launcher|banner|gdpr/i.test(`${node.id || ""} ${node.className || ""}`);
      if (topChrome || obviousOverlay) node.remove();
    }
  });
}

async function markNeedle(page, needle, className) {
  return await page.evaluate(({ needle, className }) => {
    const target = needle.toLowerCase().replace(/\s+/g, " ").trim();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const text = node.nodeValue || "";
        if (!text.trim()) return NodeFilter.FILTER_REJECT;
        const normalized = text.toLowerCase().replace(/\s+/g, " ");
        return normalized.includes(target) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    const textNode = walker.nextNode();
    if (!textNode) return { ok: false, reason: `No exact text-node match for ${needle}` };

    const text = textNode.nodeValue || "";
    const lower = text.toLowerCase();
    const compactNeedle = needle.toLowerCase();
    let index = lower.indexOf(compactNeedle);
    let length = needle.length;
    if (index < 0) {
      index = 0;
      length = text.length;
    }
    const before = text.slice(0, index);
    const match = text.slice(index, index + length);
    const after = text.slice(index + length);
    const mark = document.createElement("mark");
    mark.className = `codex-ci-mark ${className}`;
    mark.textContent = match;
    const parent = textNode.parentNode;
    parent.insertBefore(document.createTextNode(before), textNode);
    parent.insertBefore(mark, textNode);
    parent.insertBefore(document.createTextNode(after), textNode);
    parent.removeChild(textNode);
    mark.scrollIntoView({ block: "center", inline: "nearest" });
    const rect = mark.getBoundingClientRect();
    return { ok: true, marked: match, rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height } };
  }, { needle, className });
}

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
});
const context = await browser.newContext({
  viewport: { width: 1440, height: 1000 },
  deviceScaleFactor: 1,
  colorScheme: "light",
  locale: "en-US"
});

for (const job of jobs) {
  const page = await context.newPage();
  await page.goto(job.url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await settle(page);
  await prepare(page);
  let result = { ok: false };
  for (const needle of job.needles) {
    result = await markNeedle(page, needle, job.className);
    if (result.ok) break;
  }
  await page.waitForTimeout(800);
  await page.screenshot({ path: job.output, fullPage: false });
  console.log(`${result.ok ? "retook" : "fallback"} ${job.output}: ${result.ok ? result.marked.slice(0, 120) : result.reason}`);
  await page.close();
}

await browser.close();
