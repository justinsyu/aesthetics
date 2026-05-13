import { chromium } from "/tmp/als-ci-playwright/node_modules/playwright/index.mjs";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/als/2026-05-12_1234";

const sources = [
  {
    id: "01",
    slug: "amylyx-lumina",
    url: "https://www.amylyx.com/news/amylyx-pharmaceuticals-reports-first-quarter-2026-financial-results",
    dateNeedle: "May 07, 2026",
    evidenceNeedles: [
      "Amylyx completed enrollment of Cohort 2",
      "Phase 1 LUMINA clinical trial of AMX0114",
      "amyotrophic lateral sclerosis"
    ]
  },
  {
    id: "02",
    slug: "leonabio-ath1105",
    url: "https://www.globenewswire.com/news-release/2026/05/07/3290601/0/en/leonabio-reports-first-quarter-2026-financial-results-and-provides-business-update.html",
    dateNeedle: "May 07, 2026",
    evidenceNeedles: [
      "On-track to Initiate Phase 2 Proof-of-Concept Study of ATH-1105",
      "amyotrophic lateral sclerosis",
      "2H 2026"
    ]
  },
  {
    id: "03",
    slug: "insmed-ins1202",
    url: "https://investor.insmed.com/2026-05-07-Insmed-Reports-First-Quarter-2026-Financial-Results-and-Provides-Business-Update",
    dateNeedle: "May 7, 2026",
    evidenceNeedles: [
      "Insmed continues to enroll patients in the Phase 1 ARMOR study",
      "INS1202",
      "amyotrophic lateral sclerosis"
    ]
  },
  {
    id: "04",
    slug: "promis-pmn267",
    url: "https://www.promisneurosciences.com/investors/news-events/press-releases/detail/267/promis-neurosciences-announces-first-quarter-2026-financial/",
    dateNeedle: "May 12, 2026",
    evidenceNeedles: [
      "Amyotrophic Lateral Sclerosis Disease Program",
      "PMN267 is the lead preclinical candidate antibody",
      "toxic misfolded TDP-43"
    ]
  },
  {
    id: "05",
    slug: "ctgov-lilly-ly4256984",
    url: "https://clinicaltrials.gov/study/NCT07571174",
    dateNeedle: "2026-05-06",
    evidenceNeedles: [
      "A Substudy of LY4256984 in Participants With Sporadic Amyotrophic Lateral Sclerosis",
      "Not yet recruiting",
      "Phase 1"
    ]
  },
  {
    id: "06",
    slug: "ctgov-son-als",
    url: "https://clinicaltrials.gov/study/NCT07571486",
    dateNeedle: "2026-05-06",
    evidenceNeedles: [
      "Therapeutic Approach of Repeated Transient Blood-brain Barrier Opening",
      "Amyotrophic Lateral Sclerosis",
      "Phase 1"
    ]
  },
  {
    id: "07",
    slug: "ctgov-healey-master",
    url: "https://clinicaltrials.gov/study/NCT04297683",
    dateNeedle: "2026-05-08",
    evidenceNeedles: [
      "HEALEY ALS Platform Trial - Master Protocol",
      "Recruiting",
      "Phase 2"
    ]
  },
  {
    id: "08",
    slug: "ctgov-edaravone-extension",
    url: "https://clinicaltrials.gov/study/NCT05568615",
    dateNeedle: "2026-05-08",
    evidenceNeedles: [
      "Extension Study Following the Studies MT-1186-A03 or A04",
      "Safety of Oral Edaravone",
      "Amyotrophic Lateral Sclerosis"
    ]
  }
];

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function settle(page) {
  await page.waitForLoadState("domcontentloaded", { timeout: 45000 }).catch(() => {});
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(1500);
}

async function clearOverlays(page) {
  await page.evaluate(() => {
    const deny = /cookie|privacy|consent|subscribe|newsletter|modal|popup|interstitial|onetrust|truste|didomi|chat|drift|launcher|banner|gdpr/i;
    for (const button of Array.from(document.querySelectorAll("button, a, [role='button'], input[type='button'], input[type='submit']"))) {
      const text = (button.innerText || button.value || button.getAttribute("aria-label") || "").trim();
      if (/^(accept|agree|close|dismiss|continue|got it|ok|i agree|allow all|reject all|no thanks)$/i.test(text)) {
        try { button.click(); } catch {}
      }
    }
    for (const node of Array.from(document.querySelectorAll("body *"))) {
      const idClass = `${node.id || ""} ${node.className || ""} ${node.getAttribute("aria-label") || ""}`;
      const style = getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      const largeFixed = (style.position === "fixed" || style.position === "sticky") && rect.width > 220 && rect.height > 60;
      if (largeFixed && deny.test(idClass)) {
        node.remove();
      }
    }
  });
}

async function installHighlighter(page) {
  await page.addStyleTag({
    content: `
      .codex-ci-box {
        outline: 6px solid #ffdf00 !important;
        outline-offset: 3px !important;
        background: rgba(255, 223, 0, 0.28) !important;
        box-shadow: 0 0 0 3px rgba(16,18,15,.94), 0 0 0 11px rgba(255,223,0,.28) !important;
      }
      .codex-ci-date {
        outline-color: #ff8a00 !important;
        background: rgba(255, 184, 107, 0.34) !important;
      }
    `
  });
}

async function highlightBest(page, needles, className) {
  const result = await page.evaluate(({ needles, className }) => {
    const clean = (value) => (value || "").replace(/\s+/g, " ").trim();
    const wanted = needles.map(clean).filter(Boolean);
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.visibility !== "hidden" && style.display !== "none" && rect.width > 0 && rect.height > 0;
    };
    const candidates = Array.from(document.querySelectorAll("body *"))
      .filter(visible)
      .map((element) => ({ element, text: clean(element.innerText || element.textContent || "") }))
      .filter(({ text }) => wanted.every((needle) => text.toLowerCase().includes(needle.toLowerCase())));
    if (!candidates.length) {
      return { ok: false, reason: `No element found for ${wanted.join(" | ")}` };
    }
    candidates.sort((a, b) => {
      const ar = a.element.getBoundingClientRect();
      const br = b.element.getBoundingClientRect();
      return (a.text.length - b.text.length) || ((ar.width * ar.height) - (br.width * br.height));
    });
    const target = candidates[0].element;
    target.classList.add("codex-ci-box", className);
    target.scrollIntoView({ block: "center", inline: "nearest" });
    const rect = target.getBoundingClientRect();
    return { ok: true, text: candidates[0].text.slice(0, 500), rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height } };
  }, { needles, className });
  await page.waitForTimeout(600);
  return result;
}

async function highlightedScreenshot(page, src, type, needles, className, outputPath) {
  await clearOverlays(page);
  const result = await highlightBest(page, needles, className);
  if (!result.ok) {
    const fallback = needles[0] || "";
    if (fallback) {
      await page.keyboard.press(process.platform === "darwin" ? "Meta+F" : "Control+F").catch(() => {});
      await page.keyboard.type(fallback).catch(() => {});
      await page.keyboard.press("Escape").catch(() => {});
      await page.waitForTimeout(700);
    }
  }
  await page.screenshot({ path: outputPath, fullPage: false });
  console.log(`${src.id} ${type}: ${result.ok ? "highlighted" : result.reason} -> ${outputPath}`);
  return result;
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

for (const src of sources) {
  const page = await context.newPage();
  page.setDefaultTimeout(30000);
  await page.goto(src.url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await settle(page);
  await clearOverlays(page);
  await installHighlighter(page);
  await highlightedScreenshot(
    page,
    src,
    "date",
    [src.dateNeedle],
    "codex-ci-date",
    `${runDir}/screenshots/date-verification/source-${src.id}-${src.slug}-date.png`
  );
  await highlightedScreenshot(
    page,
    src,
    "evidence",
    src.evidenceNeedles,
    "codex-ci-evidence",
    `${runDir}/screenshots/evidence/source-${src.id}-${src.slug}-evidence.png`
  );
  await page.close();
}

await browser.close();
