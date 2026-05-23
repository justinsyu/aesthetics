import fs from "node:fs";
import path from "node:path";
import { chromium } from "/tmp/als-ci-playwright/node_modules/playwright/index.mjs";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/als/2026-05-13_1033";
const outDir = path.join(runDir, "sources", "clinicaltrials-history-text");
fs.mkdirSync(outDir, { recursive: true });

const ncts = [
  "NCT06008249",
  "NCT07571174",
  "NCT07543367",
  "NCT07295990",
  "NCT01925196",
  "NCT04297683",
  "NCT06735014",
  "NCT06782724",
  "NCT03362658",
  "NCT07572838",
  "NCT05568615",
  "NCT05819931",
];

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const context = await browser.newContext({ viewport: { width: 1440, height: 1400 }, deviceScaleFactor: 1 });

for (const nct of ncts) {
  const page = await context.newPage();
  const responses = [];
  page.on("response", (response) => {
    const url = response.url();
    if (url.includes("clinicaltrials.gov/api") || url.includes("/data-api/")) {
      responses.push(`${response.status()} ${url}`);
    }
  });
  const url = `https://clinicaltrials.gov/study/${nct}?tab=history`;
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(7000);
  const text = await page.locator("body").innerText({ timeout: 30000 }).catch((error) => `TEXT_ERROR: ${error.message}`);
  const content = [
    `URL: ${url}`,
    "",
    "NETWORK_RESPONSES:",
    ...responses,
    "",
    "PAGE_TEXT:",
    text,
  ].join("\n");
  fs.writeFileSync(path.join(outDir, `${nct}.txt`), content);
  console.log(`${nct}\t${text.split("\n").slice(0, 8).join(" | ")}`);
  await page.close();
}

await browser.close();
