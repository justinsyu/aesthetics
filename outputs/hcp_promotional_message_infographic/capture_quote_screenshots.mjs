import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("/Users/justinyu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const outDir = "/Users/justinyu/Desktop/linkedin-posts/outputs/hcp_promotional_message_infographic/source_screenshots";
await fs.mkdir(outDir, { recursive: true });

const sources = [
  {
    id: "dawnzera",
    url: "https://dawnzerahcp.com",
    quote: "FLIP THE SWITCH™ on your expectations of hereditary angioedema (HAE) prophylactic treatment.",
    matchTerms: ["FLIP THE SWITCH", "prophylactic treatment"],
    dismiss: [/^Continue$/i],
  },
  {
    id: "juxtapid",
    url: "https://www.juxtapid.com/hcp",
    quote: "Help your patients reach and maintain their LDL-C goals",
    matchTerms: ["Help your patients", "LDL-C goals"],
    dismiss: [/^Ok$/i, /^×$/i],
  },
  {
    id: "jatenzo",
    url: "https://jatenzohcp.com",
    quote: "FEEL THE IMPACT OF TRT, NOT THE DELIVERY OF IT.",
    matchTerms: ["FEEL THE IMPACT", "DELIVERY OF IT"],
    dismiss: [/I AM A U\.S\. HEALTHCARE PROFESSIONAL/i, /Accept All Cookies/i],
  },
];

function normalize(value) {
  return (value || "").replace(/\s+/g, " ").trim();
}

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const page = await browser.newPage({
  viewport: { width: 1200, height: 720 },
  deviceScaleFactor: 1,
  ignoreHTTPSErrors: true,
});

for (const source of sources) {
  await page.goto(source.url, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForTimeout(2500);
  for (let pass = 0; pass < 3; pass += 1) {
    for (const pattern of source.dismiss) {
      const targets = [
        page.getByRole("button", { name: pattern }).first(),
        page.getByText(pattern).first(),
      ];
      for (const button of targets) {
      if (await button.count().catch(() => 0)) {
        try {
          await button.click({ timeout: 2500 });
          await page.waitForTimeout(900);
        } catch {
          // Some gates render as inert overlays in headless mode; ignore and continue.
        }
      }
      }
    }
  }
  await page.evaluate(() => {
    for (const selector of [
      "#onetrust-banner-sdk",
      ".ot-sdk-container",
      ".cookie",
      "[class*='cookie']",
      "[id*='cookie']",
      "[aria-label*='cookie' i]",
    ]) {
      for (const node of document.querySelectorAll(selector)) {
        node.style.display = "none";
      }
    }
  });

  const found = await page.evaluate(({ quote, matchTerms }) => {
    const wanted = quote.replace(/\s+/g, " ").trim();
    const terms = matchTerms.map((term) => term.toLowerCase());
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let best = null;
    while (walker.nextNode()) {
      const el = walker.currentNode;
      const text = (el.innerText || "").replace(/\s+/g, " ").trim();
      const lower = text.toLowerCase();
      if (!text || (!text.includes(wanted) && !terms.every((term) => lower.includes(term)))) continue;
      const rect = el.getBoundingClientRect();
      if (!best || text.length < best.textLength) {
        best = {
          textLength: text.length,
          tag: el.tagName,
          rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
        };
        window.__quoteEl = el;
      }
    }
    if (!window.__quoteEl) return null;
    window.__quoteEl.scrollIntoView({ block: "center", inline: "center" });
    return best;
  }, { quote: source.quote, matchTerms: source.matchTerms });

  if (!found) {
    try {
      await fs.access(path.join(outDir, `${source.id}.png`));
      console.warn(`Reusing existing screenshot for ${source.id}; quote not found during this recapture.`);
      continue;
    } catch {
      throw new Error(`Quote not found on rendered page for ${source.id}: ${source.quote}`);
    }
  }

  await page.waitForTimeout(800);
  await page.evaluate(() => {
    const el = window.__quoteEl;
    if (!el) return;
    el.style.outline = "5px solid #d7ff5f";
    el.style.outlineOffset = "8px";
    el.style.borderRadius = "8px";
    el.style.backgroundColor = "rgba(215,255,95,0.12)";
  });
  await page.screenshot({
    path: path.join(outDir, `${source.id}.png`),
    fullPage: false,
  });
  console.log(JSON.stringify({ ...source, found }));
}

await browser.close();
