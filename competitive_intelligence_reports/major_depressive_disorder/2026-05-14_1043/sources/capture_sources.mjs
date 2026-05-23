import { chromium } from "/Users/justinyu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
import path from "node:path";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/major_depressive_disorder/2026-05-14_1043";

const sources = [
  {
    id: "01",
    slug: "definium-ascend",
    url: "https://ir.definiumtx.com/news-events/press-releases/detail/227/definium-therapeutics-announces-first-patient-dosed-in-ascend-the-second-phase-3-pivotal-study-of-dt120-odt-in-major-depressive-disorder",
    dateText: "May 12, 2026",
    evidence: [
      "today announced that the first patient has been dosed in Ascend, its second Phase 3 study evaluating DT120 ODT",
      "The Ascend study will evaluate the efficacy and safety of DT120 ODT versus placebo and is expected to enroll 175 participants"
    ]
  },
  {
    id: "02",
    slug: "compass-q1",
    url: "https://finance.yahoo.com/news/compass-pathways-announces-first-quarter-103000764.html",
    dateText: "May 13, 2026",
    evidence: [
      "FDA granted Compass NDA rolling submission and review request, based on strength of positive Phase 3 data.",
      "CNPV awarded for COMP360, Compass’ proprietary formulation of synthetic psilocybin for TRD"
    ]
  },
  {
    id: "03",
    slug: "alto-q1",
    url: "https://investors.altoneuroscience.com/news/news-details/2026/Alto-Neuroscience-Reports-First-Quarter-2026-Financial-Results-and-Recent-Business-Highlights/default.aspx",
    dateText: "May 13, 2026",
    evidence: [
      "In April 2026, Alto initiated a randomized, double-blind, placebo-controlled Phase 2b trial of ALTO-207",
      "approximately 178 adults with TRD who have experienced between two and five prior treatment failures"
    ]
  },
  {
    id: "04",
    slug: "jnj-apa-ascp",
    url: "https://www.jnj.com/media-center/press-releases/johnson-johnson-reinforces-its-leadership-in-advancing-neuropsychiatry-with-new-portfolio-and-pipeline-data-at-apa-and-ascp",
    dateText: "May 11, 2026",
    evidence: [
      "18 abstracts featuring new and encore data from the Company’s robust neuropsychiatry portfolio and pipeline",
      "Seltorexant: Oral presentation will showcase key data from Phase 3 studies evaluating efficacy as adjunctive therapy in adults with MDD and insomnia symptoms"
    ]
  },
  {
    id: "05",
    slug: "neurolief-prolivrx",
    url: "https://www.prnewswire.com/news-releases/neurolief-to-showcase-prolivrx-at-apa-2026-highlighting-fda-approved-physician-directed-at-home-brain-stimulation-for-major-depressive-disorder-302769004.html",
    dateText: "May 12, 2026",
    evidence: [
      "FDA-approved prescription brain stimulation therapy for adults with Major Depressive Disorder (MDD)",
      "active treatment produced significantly greater improvement in depressive symptoms than sham at eight weeks"
    ]
  },
  {
    id: "06",
    slug: "aytu-q3",
    url: "https://finance.yahoo.com/news/aytu-biopharma-reports-fiscal-2026-200500565.html",
    dateText: "May 13, 2026",
    evidence: [
      "EXXUA -- with only a partial quarter of full sales force support -- contributed $2.4 million in net revenue",
      "more than 1,300 prescriptions written in the quarter by more than 450 unique prescribers"
    ]
  },
  {
    id: "07",
    slug: "brainsway-q1",
    url: "https://www.brainsway.com/news_events/brainsway-reports-first-quarter-2026-financial-results-and-operational-highlights/",
    dateText: "May 13, 2026",
    evidence: [
      "Secured the first insurer coverage for accelerated SWIFT",
      "plans to submit an FDA filing in the second quarter of 2026 for the use of Deep TMS in treating PTSD symptoms in patients with MDD"
    ]
  }
];

function out(...parts) {
  return path.join(runDir, ...parts);
}

async function dismissOverlays(page) {
  const buttonTexts = [
    "Accept", "Accept All", "I Accept", "Agree", "Agree and continue",
    "Continue", "Reject All", "No thanks", "Close"
  ];
  for (const text of buttonTexts) {
    try {
      await page.getByRole("button", { name: new RegExp(`^${text}$`, "i") }).click({ timeout: 900 });
    } catch {}
  }
  await page.evaluate(() => {
    const selectors = [
      "[aria-label*='cookie' i]",
      "[id*='cookie' i]",
      "[class*='cookie' i]",
      "[class*='newsletter' i]",
      "[class*='modal' i]",
      "[class*='popup' i]",
      "[class*='chat' i]",
      ".grecaptcha-badge"
    ];
    for (const selector of selectors) {
      for (const el of document.querySelectorAll(selector)) {
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (style.position === "fixed" || rect.height > 80 || rect.width > 300) {
          el.style.setProperty("display", "none", "important");
        }
      }
    }
  });
}

async function clearMarks(page) {
  await page.evaluate(() => {
    document.querySelectorAll("mark[data-ci-mark='true']").forEach((mark) => {
      mark.replaceWith(document.createTextNode(mark.textContent || ""));
    });
    document.body.normalize();
  });
}

async function markText(page, snippets) {
  return await page.evaluate((rawSnippets) => {
    const snippets = rawSnippets.map((s) => s.replace(/\s+/g, " ").trim());
    const found = [];

    function normalizedIndex(text, snippet) {
      return text.replace(/\s+/g, " ").indexOf(snippet);
    }

    function markNode(node, needle) {
      const raw = node.nodeValue || "";
      const rawNorm = raw.replace(/\s+/g, " ");
      const idxNorm = normalizedIndex(raw, needle);
      if (idxNorm < 0) return null;

      let rawStart = 0;
      let normCount = 0;
      let inSpace = false;
      for (; rawStart < raw.length; rawStart += 1) {
        const ch = raw[rawStart];
        const isSpace = /\s/.test(ch);
        if (isSpace) {
          if (!inSpace) normCount += 1;
          inSpace = true;
        } else {
          normCount += 1;
          inSpace = false;
        }
        if (normCount > idxNorm) break;
      }

      let rawEnd = rawStart;
      let matched = "";
      for (; rawEnd < raw.length && matched.replace(/\s+/g, " ").length < needle.length; rawEnd += 1) {
        matched += raw[rawEnd];
      }

      const range = document.createRange();
      range.setStart(node, rawStart);
      range.setEnd(node, rawEnd);
      const mark = document.createElement("mark");
      mark.dataset.ciMark = "true";
      mark.style.background = "#fff36b";
      mark.style.color = "#10120f";
      mark.style.outline = "3px solid #f04e37";
      mark.style.padding = "1px 2px";
      mark.style.borderRadius = "3px";
      range.surroundContents(mark);
      return mark;
    }

    for (const snippet of snippets) {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
          if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
          const parent = node.parentElement;
          if (!parent || ["SCRIPT", "STYLE", "NOSCRIPT"].includes(parent.tagName)) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        }
      });
      let node;
      let mark = null;
      while ((node = walker.nextNode())) {
        mark = markNode(node, snippet);
        if (mark) break;
      }
      if (mark) {
        found.push(snippet);
      }
    }

    const firstMark = document.querySelector("mark[data-ci-mark='true']");
    if (firstMark) firstMark.scrollIntoView({ block: "center", inline: "nearest" });
    return found;
  }, snippets);
}

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Users/justinyu/.cache/puppeteer/chrome-headless-shell/mac_arm-146.0.7680.153/chrome-headless-shell-mac-arm64/chrome-headless-shell"
});
const context = await browser.newContext({
  viewport: { width: 1440, height: 1050 },
  deviceScaleFactor: 1,
  userAgent: "CodexCIReport/1.0 contact=justinyu@example.com"
});
const page = await context.newPage();

for (const source of sources) {
  console.log(`Capturing source ${source.id}: ${source.url}`);
  await page.goto(source.url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(2500);
  await dismissOverlays(page);

  await clearMarks(page);
  const dateFound = await markText(page, [source.dateText]);
  if (!dateFound.length) throw new Error(`Date text not found for source ${source.id}: ${source.dateText}`);
  await page.waitForTimeout(350);
  await page.screenshot({
    path: out("screenshots", "date-verification", `source-${source.id}-${source.slug}-date.png`),
    fullPage: false
  });

  await clearMarks(page);
  const evidenceFound = await markText(page, source.evidence);
  if (!evidenceFound.length) throw new Error(`Evidence text not found for source ${source.id}`);
  await page.waitForTimeout(350);
  await page.screenshot({
    path: out("screenshots", "evidence", `source-${source.id}-${source.slug}-evidence-01.png`),
    fullPage: false
  });
  console.log(`  date marks: ${dateFound.length}; evidence marks: ${evidenceFound.length}`);
}

await browser.close();
