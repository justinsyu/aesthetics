import { chromium } from "/tmp/als-ci-playwright/node_modules/playwright/index.mjs";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/als/2026-05-13_1033";

const browser = await chromium.launch({
  headless: false,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--disable-blink-features=AutomationControlled"],
});
const context = await browser.newContext({
  viewport: { width: 1440, height: 1050 },
  deviceScaleFactor: 1,
  userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
});

async function addStyle(page) {
  await page.evaluate(() => {
    const style = document.createElement("style");
    style.textContent = `
      #QSIFeedbackButton-btn,
      #QSIFeedbackButton-close-btn,
      #sliding-popup,
      iframe,
      [class*="fun-social-proof"],
      [id*="onetrust"],
      [class*="onetrust"],
      .eu-cookie-compliance-banner,
      .eu-cookie-compliance-content,
      .eu-cookie-compliance-message,
      .eu-cookie-compliance-buttons {
        display: none !important;
        visibility: hidden !important;
      }
      .ci-mark {
        background: rgba(215, 255, 95, 0.86) !important;
        outline: 4px solid #11130f !important;
        outline-offset: 4px !important;
        box-shadow: 0 0 0 8px rgba(215, 255, 95, 0.28) !important;
        color: inherit !important;
      }
    `;
    document.head.appendChild(style);
  });
}

async function captureAlsAssociation() {
  const page = await context.newPage();
  await page.goto("https://www.als.org/stories-news/als-association-awards-3-million-bring-expert-als-care-communities-dont-have-it", {
    waitUntil: "domcontentloaded",
    timeout: 90000,
  });
  await page.waitForFunction(() => document.body.innerText.includes("ARLINGTON, VA (May 7, 2026)"), null, { timeout: 60000 });
  await addStyle(page);
  await page.getByRole("button", { name: /accept/i }).first().click({ timeout: 2000 }).catch(() => {});
  await page.evaluate(() => {
    document.querySelectorAll("iframe").forEach((el) => { el.style.display = "none"; });
    document.documentElement.style.visibility = "visible";
    document.body.style.visibility = "visible";
    document.querySelectorAll(".ci-mark").forEach((el) => el.classList.remove("ci-mark"));
    const date = Array.from(document.querySelectorAll("strong, .article__date"))
      .find((el) => el.innerText.includes("May 7, 2026"));
    if (!date) throw new Error("ALS date element not found");
    date.classList.add("ci-mark");
    date.scrollIntoView({ block: "center", inline: "nearest" });
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${runDir}/screenshots/date-verification/source-06-als-association-date.png`, fullPage: false });

  await page.evaluate(() => {
    document.querySelectorAll("iframe").forEach((el) => { el.style.display = "none"; });
    document.querySelectorAll(".ci-mark").forEach((el) => el.classList.remove("ci-mark"));
    const needle = "Right now, only around half of registered people living with ALS receive multidisciplinary care";
    const block = Array.from(document.querySelectorAll("p"))
      .filter((el) => el.innerText.replace(/\s+/g, " ").includes(needle))
      .sort((a, b) => a.innerText.length - b.innerText.length)[0];
    if (!block) throw new Error(`ALS evidence element not found: ${needle}`);
    block.classList.add("ci-mark");
    block.scrollIntoView({ block: "center", inline: "nearest" });
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${runDir}/screenshots/evidence/source-06-als-association-evidence-01.png`, fullPage: false });
  await page.close();
}

async function captureCtgovTricals() {
  const page = await context.newPage();
  await page.goto("https://clinicaltrials.gov/study/NCT06008249?tab=history", {
    waitUntil: "domcontentloaded",
    timeout: 90000,
  });
  await page.waitForFunction(() => document.body.innerText.includes("Last Update Posted 2026-05-13"), null, { timeout: 60000 });
  await addStyle(page);
  await page.evaluate(() => {
    document.querySelectorAll(".ci-mark").forEach((el) => el.classList.remove("ci-mark"));
    const els = Array.from(document.querySelectorAll("body *"));
    const date = els
      .filter((el) => el.innerText?.replace(/\s+/g, " ").includes("Last Update Posted 2026-05-13"))
      .sort((a, b) => a.innerText.length - b.innerText.length)[0];
    if (!date) throw new Error("CT.gov date element not found");
    date.classList.add("ci-mark");
    date.scrollIntoView({ block: "center", inline: "nearest" });
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${runDir}/screenshots/date-verification/source-07-ctgov-tricals-date.png`, fullPage: false });

  await page.evaluate(() => {
    document.querySelectorAll(".ci-mark").forEach((el) => el.classList.remove("ci-mark"));
    const norm = (value) => (value || "").replace(/\s+/g, " ");
    const els = Array.from(document.querySelectorAll("body *"));
    const needle = "The planned interim analysis showed no survival benefit of taking the drug when compared with placebo.";
    const match = els
      .filter((el) => norm(el.innerText).includes(needle))
      .sort((a, b) => norm(a.innerText).length - norm(b.innerText).length)[0];
    if (!match) throw new Error(`CT.gov evidence element not found: ${needle}`);
    match.classList.add("ci-mark");
    document.querySelector(".ci-mark").scrollIntoView({ block: "center", inline: "nearest" });
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${runDir}/screenshots/evidence/source-07-ctgov-tricals-evidence-01.png`, fullPage: false });

  await page.evaluate(() => {
    document.querySelectorAll(".ci-mark").forEach((el) => el.classList.remove("ci-mark"));
    const norm = (value) => (value || "").replace(/\s+/g, " ");
    const needle = "3 2026-05-12 Recruitment Status Study Status Oversight Study Design Contacts/Locations";
    const match = Array.from(document.querySelectorAll("tr, td, tbody, table, body *"))
      .filter((el) => norm(el.innerText).includes(needle))
      .sort((a, b) => norm(a.innerText).length - norm(b.innerText).length)[0];
    if (!match) throw new Error(`CT.gov history row not found: ${needle}`);
    match.classList.add("ci-mark");
    match.scrollIntoView({ block: "center", inline: "nearest" });
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${runDir}/screenshots/evidence/source-07-ctgov-tricals-evidence-02.png`, fullPage: false });
  await page.close();
}

await captureAlsAssociation();
await captureCtgovTricals();
await browser.close();
