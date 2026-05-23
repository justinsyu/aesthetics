import { chromium } from "/tmp/als-ci-playwright/node_modules/playwright/index.mjs";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/als/2026-05-13_1033";
const dateDir = `${runDir}/screenshots/date-verification`;
const evidenceDir = `${runDir}/screenshots/evidence`;

const sources = [
  {
    id: "source-01-coya",
    url: "https://ir.coyatherapeutics.com/news/news-details/2026/Coya-Therapeutics-Reports-First-Quarter-2026-Financial-Results-and-Provides-a-Corporate-Update/default.aspx",
    dateNeedle: "May 12, 2026",
    evidenceNeedle: "The ALSTARS trial is now in full recruitment mode, and we maintain our guidance for a 1Q 2027 topline readout.",
    evidenceNeedles: [
      "The ALSTARS trial is now in full recruitment mode, and we maintain our guidance for a 1Q 2027 topline readout.",
      "FDA granted Fast Track Designation to COYA 302 for the treatment of ALS on May 11, 2026.",
    ],
    waitMs: 12000,
  },
  {
    id: "source-02-amylyx",
    url: "https://www.amylyx.com/news/amylyx-pharmaceuticals-reports-first-quarter-2026-financial-results",
    dateNeedle: "May 07, 2026",
    evidenceNeedle: "Amylyx completed enrollment of Cohort 2 (n=12) of the Phase 1 LUMINA clinical trial of AMX0114",
    evidenceNeedles: [
      "Amylyx completed enrollment of Cohort 2 (n=12) of the Phase 1 LUMINA clinical trial of AMX0114",
      "LUMINA is evaluating the safety, tolerability, pharmacokinetics, and pharmacodynamics of AMX0114",
    ],
    waitMs: 3500,
  },
  {
    id: "source-03-leonabio",
    url: "https://www.globenewswire.com/news-release/2026/05/07/3290601/0/en/leonabio-reports-first-quarter-2026-financial-results-and-provides-business-update.html",
    dateNeedle: "May 07, 2026 16:05 ET",
    evidenceNeedle: "LeonaBio is on track to dose ALS patients in a Phase 2 proof-of-concept clinical trial in the second half of 2026.",
    evidenceNeedles: [
      "ATH-1105 showed a favorable safety profile and was well tolerated in both single and multiple ascending dose studies",
      "LeonaBio is on track to dose ALS patients in a Phase 2 proof-of-concept clinical trial in the second half of 2026.",
    ],
    waitMs: 3500,
  },
  {
    id: "source-04-insmed",
    url: "https://investor.insmed.com/2026-05-07-Insmed-Reports-First-Quarter-2026-Financial-Results-and-Provides-Business-Update",
    dateNeedle: "May 7, 2026",
    evidenceNeedle: "Insmed continues to enroll patients in the Phase 1 ARMOR study of INS1202",
    evidenceNeedles: [
      "Insmed continues to enroll patients in the Phase 1 ARMOR study of INS1202",
      "an intrathecally delivered gene therapy for patients with amyotrophic lateral sclerosis (ALS).",
    ],
    waitMs: 3500,
  },
  {
    id: "source-05-promis",
    url: "https://www.promisneurosciences.com/investors/news-events/press-releases/detail/267/promis-neurosciences-announces-first-quarter-2026-financial/",
    dateNeedle: "May 12, 2026",
    evidenceNeedle: "PMN267 is the lead preclinical candidate antibody directed against toxic misfolded TDP-43",
    evidenceNeedles: [
      "Amyotrophic Lateral Sclerosis Disease Program (PMN267)",
      "PMN267 is the lead preclinical candidate antibody directed against toxic misfolded TDP-43",
    ],
    waitMs: 3500,
  },
  {
    id: "source-06-als-association",
    url: "https://www.als.org/stories-news/als-association-awards-3-million-bring-expert-als-care-communities-dont-have-it",
    dateNeedle: "ARLINGTON, VA (May 7, 2026)",
    evidenceNeedle: "The ALS Association today announced the newest recipients of the Hoffman ALS Clinic Development and Capacity Awards",
    evidenceNeedles: [
      "New Hoffman clinic grants target rural, underserved, and geographically isolated Americans living with ALS",
      "Right now, only around half of registered people living with ALS receive multidisciplinary care",
    ],
    waitMs: 12000,
  },
  {
    id: "source-07-ctgov-tricals",
    url: "https://clinicaltrials.gov/study/NCT06008249?tab=history",
    dateNeedle: "Last Update Posted 2026-05-13",
    evidenceNeedle: "The planned interim analysis showed no survival benefit of taking the drug when compared with placebo.",
    evidenceNeedles: [
      "The planned interim analysis showed no survival benefit of taking the drug when compared with placebo.",
      "3 2026-05-12 Recruitment Status Study Status Oversight Study Design Contacts/Locations",
    ],
    waitMs: 7000,
  },
];

function normalizeText(value) {
  return (value || "").replace(/\s+/g, " ").trim();
}

async function cleanPage(page) {
  await page.evaluate(() => {
    const style = document.createElement("style");
    style.id = "ci-clean-style";
    style.textContent = `
      #QSIFeedbackButton-btn,
      #QSIFeedbackButton-close-btn,
      [id*="onetrust"],
      [class*="onetrust"],
      #sliding-popup,
      .eu-cookie-compliance-banner,
      .eu-cookie-compliance-content,
      .eu-cookie-compliance-message,
      .eu-cookie-compliance-buttons,
      [class*="newsletter" i],
      [id*="newsletter" i] {
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
  }).catch(() => {});

  const labels = [
    "Accept all",
    "Accept All",
    "Accept",
    "I agree",
    "I Agree",
    "Agree",
    "Continue",
    "Close",
    "No thanks",
  ];
  for (const label of labels) {
    const button = page.getByRole("button", { name: label }).first();
    if (await button.isVisible().catch(() => false)) {
      await button.click({ timeout: 1500 }).catch(() => {});
    }
  }
}

async function waitForVisibleText(page, needle, timeout = 30000) {
  const expected = normalizeText(needle);
  await page.waitForFunction((value) => {
    return document.body && document.body.innerText.replace(/\s+/g, " ").includes(value);
  }, expected, { timeout });
}

async function markNeedles(page, needles, scrollNeedle) {
  const result = await page.evaluate(({ needles, scrollNeedle }) => {
    const normalize = (value) => (value || "").replace(/\s+/g, " ").trim();
    const visible = (el) => {
      const style = window.getComputedStyle(el);
      return style.visibility !== "hidden" && style.display !== "none";
    };
    document.querySelectorAll(".ci-mark").forEach((el) => el.classList.remove("ci-mark"));
    const markTextNode = (needle) => {
      const target = normalize(needle);
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        if (!node.nodeValue || !normalize(node.nodeValue).includes(target)) continue;
        const parent = node.parentElement;
        if (!parent || !visible(parent)) continue;
        const span = document.createElement("span");
        span.className = "ci-mark";
        span.textContent = node.nodeValue;
        parent.replaceChild(span, node);
        return span;
      }
      return null;
    };
    const all = [document.body, ...Array.from(document.querySelectorAll("body *"))].filter(visible);
    const marked = [];
    for (const needle of needles) {
      const target = normalize(needle);
      const textNodeMark = markTextNode(needle);
      if (textNodeMark) {
        marked.push({ needle, found: true, text: normalize(textNodeMark.innerText).slice(0, 240) });
        continue;
      }
      const matches = all
        .filter((el) => normalize(el.innerText).includes(target))
        .sort((a, b) => normalize(a.innerText).length - normalize(b.innerText).length);
      if (!matches.length) {
        marked.push({ needle, found: false });
        continue;
      }
      matches[0].classList.add("ci-mark");
      marked.push({ needle, found: true, text: normalize(matches[0].innerText).slice(0, 240) });
    }
    const scrollTarget = normalize(scrollNeedle || needles[0]);
    const scrollEl = all
      .filter((el) => normalize(el.innerText).includes(scrollTarget))
      .sort((a, b) => normalize(a.innerText).length - normalize(b.innerText).length)[0];
    if (scrollEl) scrollEl.scrollIntoView({ block: "center", inline: "nearest" });
    return marked;
  }, { needles, scrollNeedle });
  await page.waitForTimeout(800);
  const missing = result.filter((item) => !item.found);
  if (missing.length) {
    throw new Error(`Could not mark: ${missing.map((item) => item.needle).join(" | ")}`);
  }
  return result;
}

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

for (const source of sources) {
  const page = await context.newPage();
  await page.goto(source.url, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(source.waitMs);
  await waitForVisibleText(page, source.dateNeedle, 45000);
  await cleanPage(page);

  await markNeedles(page, [source.dateNeedle], source.dateNeedle);
  await page.screenshot({ path: `${dateDir}/${source.id}-date.png`, fullPage: false });

  await markNeedles(page, source.evidenceNeedles, source.evidenceNeedle);
  await page.screenshot({ path: `${evidenceDir}/${source.id}-evidence-01.png`, fullPage: false });

  console.log(`${source.id}\t${normalizeText(await page.locator("body").innerText()).slice(0, 180)}`);
  await page.close();
}

await browser.close();
