import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/head_and_neck_squamous_cell_carcinoma/2026-05-12_1235";
const dateDir = path.join(runDir, "screenshots/date-verification");
const evidenceDir = path.join(runDir, "screenshots/evidence");

const sources = [
  {
    ref: "01",
    name: "Inhibrx Biosciences",
    url: "https://inhibrxbiosciences.investorroom.com/2026-05-11-Inhibrx-Reports-Interim-Phase-2-Data-for-INBRX-106-in-First-Line-HNSCC-Initial-Results-Demonstrate-Potential-Costimulatory-Benefit-Over-PD-1-Monotherapy",
    date: "May 11, 2026",
    evidence: [
      {
        slug: "orr",
        phrases: [
          "44.0% confirmed Objective Response Rate",
          "44.0% versus 21.4%",
          "53 patients"
        ]
      },
      {
        slug: "next-steps",
        phrases: [
          "progression-free survival data",
          "fourth quarter of 2026",
          "begin the Phase 3 portion"
        ]
      }
    ]
  },
  {
    ref: "02",
    name: "Bicara Therapeutics via GlobeNewswire",
    url: "https://www.globenewswire.com/news-release/2026/05/11/3291783/0/en/bicara-therapeutics-reports-first-quarter-2026-financial-results-and-provides-business-update.html",
    date: "May 11, 2026",
    evidence: [
      {
        slug: "fortifi",
        phrases: [
          "substantially enrolled by the end of the year",
          "interim analysis in mid-2027",
          "loading dose of 1500mg weekly"
        ]
      },
      {
        slug: "asco-cash",
        phrases: [
          "Long-term follow-up data",
          "ASCO 2026",
          "$539.8 million"
        ]
      }
    ]
  },
  {
    ref: "03",
    name: "Corbus Pharmaceuticals",
    url: "https://ir.corbuspharma.com/news-events/press-releases/detail/467/corbus-pharmaceuticals-reports-q1-2026-financial-results-and-provides-a-corporate-update",
    date: "May 12, 2026",
    evidence: [
      {
        slug: "crb701-path",
        phrases: [
          "broad alignment with the FDA",
          "second-line HNSCC this summer",
          "Report monotherapy data"
        ]
      },
      {
        slug: "cash",
        phrases: [
          "$138.2 million",
          "fund operations into 2028"
        ]
      }
    ]
  },
  {
    ref: "04",
    name: "Pyxis Oncology via GlobeNewswire",
    url: "https://www.globenewswire.com/news-release/2026/05/07/3290537/0/en/Pyxis-Oncology-Appoints-Nelson-Azoulay-as-Chief-Business-Officer.html",
    date: "May 07, 2026",
    evidence: [
      {
        slug: "micvo",
        phrases: [
          "advance MICVO",
          "Phase 1 clinical study in patients with recurrent and metastatic head and neck squamous cell carcinoma",
          "Fast Track Designation"
        ]
      }
    ]
  },
  {
    ref: "05",
    name: "PDS Biotechnology",
    url: "https://pdsbiotech.com/index.php/investors/news-center/press-releases/press-releases1/134-2026-news/1037-pds-biotech-announces-conference-call-and-webcast-for-2026-f2026-05-06-050506",
    date: "May 06, 2026",
    evidence: [
      {
        slug: "q1-call-program",
        phrases: [
          "conference call and webcast",
          "Wednesday, May 13, 2026",
          "pivotal clinical trial to advance its lead program in advanced HPV16-positive head and neck squamous cell cancers"
        ]
      }
    ]
  }
];

async function ensureDirs() {
  await fs.mkdir(dateDir, { recursive: true });
  await fs.mkdir(evidenceDir, { recursive: true });
}

async function dismissOverlays(page) {
  const candidates = [
    "Accept All", "Accept all", "Accept", "I Accept", "I agree", "Agree", "Got it",
    "Close", "No thanks", "Reject All", "Continue"
  ];
  for (const label of candidates) {
    try {
      const locator = page.getByText(label, { exact: false }).first();
      if (await locator.isVisible({ timeout: 500 })) {
        await locator.click({ timeout: 1000 });
        await page.waitForTimeout(250);
      }
    } catch {}
  }
}

async function preparePage(page) {
  await page.addStyleTag({
    content: `
      .ci-mark {
        background: rgba(215, 255, 95, 0.78) !important;
        outline: 4px solid #11130f !important;
        box-decoration-break: clone;
        -webkit-box-decoration-break: clone;
        color: inherit !important;
      }
      .ci-box {
        outline: 5px solid #11130f !important;
        box-shadow: 0 0 0 8px rgba(215, 255, 95, 0.45) !important;
        background: rgba(215, 255, 95, 0.22) !important;
      }
      .ci-screenshot-note {
        position: fixed;
        left: 18px;
        top: 18px;
        z-index: 2147483647;
        background: #11130f;
        color: #f6f1e8;
        border: 3px solid #d7ff5f;
        border-radius: 8px;
        padding: 8px 12px;
        font: 700 15px/1.15 Arial, sans-serif;
        max-width: 540px;
      }
    `
  });
}

async function markPhrases(page, phrases, label) {
  const result = await page.evaluate(({ phrases, label }) => {
    document.querySelectorAll(".ci-mark").forEach((node) => {
      const parent = node.parentNode;
      if (!parent) return;
      parent.replaceChild(document.createTextNode(node.textContent || ""), node);
      parent.normalize();
    });
    document.querySelectorAll(".ci-box").forEach((node) => node.classList.remove("ci-box"));
    document.querySelectorAll(".ci-screenshot-note").forEach((node) => node.remove());

    const normalize = (text) => (text || "").replace(/\s+/g, " ").trim();
    const isVisible = (el) => {
      if (!el || !(el instanceof Element)) return false;
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== "hidden" && style.display !== "none" && rect.width > 0 && rect.height > 0;
    };

    const marked = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!normalize(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        const parent = node.parentElement;
        if (!isVisible(parent)) return NodeFilter.FILTER_REJECT;
        if (["SCRIPT", "STYLE", "NOSCRIPT"].includes(parent.tagName)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });

    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);

    for (const phrase of phrases) {
      const target = normalize(phrase);
      let found = false;

      for (const node of textNodes) {
        if (!node.parentNode) continue;
        const normalizedNode = normalize(node.nodeValue);
        if (!normalizedNode.includes(target)) continue;

        const raw = node.nodeValue || "";
        const idx = raw.replace(/\u00a0/g, " ").toLowerCase().indexOf(phrase.toLowerCase());
        if (idx >= 0) {
          const before = document.createTextNode(raw.slice(0, idx));
          const span = document.createElement("span");
          span.className = "ci-mark";
          span.textContent = raw.slice(idx, idx + phrase.length);
          const after = document.createTextNode(raw.slice(idx + phrase.length));
          node.parentNode.insertBefore(before, node);
          node.parentNode.insertBefore(span, node);
          node.parentNode.insertBefore(after, node);
          node.parentNode.removeChild(node);
          marked.push({ phrase, mode: "span" });
          found = true;
          break;
        }
      }

      if (!found) {
        const candidates = [...document.querySelectorAll("p, li, h1, h2, h3, h4, div, span, td")].filter((el) =>
          isVisible(el) && normalize(el.innerText).includes(target)
        );
        candidates.sort((a, b) => normalize(a.innerText).length - normalize(b.innerText).length);
        if (candidates[0]) {
          candidates[0].classList.add("ci-box");
          marked.push({ phrase, mode: "box" });
          found = true;
        }
      }

      if (!found) marked.push({ phrase, mode: "missing" });
    }

    const note = document.createElement("div");
    note.className = "ci-screenshot-note";
    note.textContent = label;
    document.body.appendChild(note);

    const first = document.querySelector(".ci-mark, .ci-box");
    if (first) first.scrollIntoView({ block: "center", inline: "nearest" });
    return marked;
  }, { phrases, label });

  await page.waitForTimeout(650);
  return result;
}

async function captureItem(page, source) {
  await page.goto(source.url, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(1800);
  await dismissOverlays(page);
  await preparePage(page);

  const dateResult = await markPhrases(page, [source.date], `Reference ${Number(source.ref)} - date verification`);
  await page.screenshot({
    path: path.join(dateDir, `source-${source.ref}-date.png`),
    fullPage: false
  });

  const evidenceResults = [];
  for (let i = 0; i < source.evidence.length; i += 1) {
    const item = source.evidence[i];
    const result = await markPhrases(page, item.phrases, `Reference ${Number(source.ref)} - evidence ${i + 1}`);
    await page.screenshot({
      path: path.join(evidenceDir, `source-${source.ref}-evidence-${String(i + 1).padStart(2, "0")}-${item.slug}.png`),
      fullPage: false
    });
    evidenceResults.push({ item, result });
  }

  return { ref: source.ref, name: source.name, dateResult, evidenceResults };
}

await ensureDirs();
const browser = await chromium.launch({ headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
const context = await browser.newContext({
  viewport: { width: 1440, height: 1040 },
  deviceScaleFactor: 1,
  userAgent: "codex-ci/1.0 contact justinyu@example.com"
});
const page = await context.newPage();
const log = [];
for (const source of sources) {
  try {
    log.push(await captureItem(page, source));
  } catch (error) {
    log.push({ ref: source.ref, name: source.name, error: String(error?.stack || error) });
  }
}
await browser.close();
console.log(JSON.stringify(log, null, 2));
