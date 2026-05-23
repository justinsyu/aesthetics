import fs from "node:fs";
import path from "node:path";
import { chromium } from "/tmp/als-ci-playwright/node_modules/playwright/index.mjs";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/als/2026-05-13_1033";
const outDir = path.join(runDir, "sources", "primary-page-text");
fs.mkdirSync(outDir, { recursive: true });

const sources = [
  ["source-01-coya", "https://ir.coyatherapeutics.com/news/news-details/2026/Coya-Therapeutics-Reports-First-Quarter-2026-Financial-Results-and-Provides-a-Corporate-Update/default.aspx"],
  ["source-02-amylyx", "https://www.amylyx.com/news/amylyx-pharmaceuticals-reports-first-quarter-2026-financial-results"],
  ["source-03-leonabio", "https://www.globenewswire.com/news-release/2026/05/07/3290601/0/en/leonabio-reports-first-quarter-2026-financial-results-and-provides-business-update.html"],
  ["source-04-insmed", "https://investor.insmed.com/2026-05-07-Insmed-Reports-First-Quarter-2026-Financial-Results-and-Provides-Business-Update"],
  ["source-05-promis", "https://www.promisneurosciences.com/investors/news-events/press-releases/detail/267/promis-neurosciences-announces-first-quarter-2026-financial/"],
  ["source-06-als-association", "https://www.als.org/stories-news/als-association-awards-3-million-bring-expert-als-care-communities-dont-have-it"],
  ["source-07-ctgov-tricals", "https://clinicaltrials.gov/study/NCT06008249?tab=history&a=2&b=3#version-content-panel"],
];

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const context = await browser.newContext({ viewport: { width: 1440, height: 1400 }, deviceScaleFactor: 1 });

for (const [slug, url] of sources) {
  const page = await context.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(url.includes("clinicaltrials.gov") ? 7000 : 3000);
  await page.evaluate(() => {
    for (const selector of [
      "[id*='cookie']",
      "[class*='cookie']",
      "[class*='modal']",
      "[id*='modal']",
      "[class*='newsletter']",
      "[id*='newsletter']",
      "#QSIFeedbackButton-btn",
      "#QSIFeedbackButton-close-btn",
    ]) {
      document.querySelectorAll(selector).forEach((el) => {
        const rect = el.getBoundingClientRect();
        if (rect.width > 100 || rect.height > 40 || selector.includes("QSI")) el.style.display = "none";
      });
    }
  }).catch(() => {});
  const text = await page.locator("body").innerText({ timeout: 30000 }).catch((error) => `TEXT_ERROR: ${error.message}`);
  fs.writeFileSync(path.join(outDir, `${slug}.txt`), `URL: ${url}\n\n${text}`);
  console.log(`${slug}\t${url}\t${text.slice(0, 240).replace(/\s+/g, " ")}`);
  await page.close();
}

await browser.close();
