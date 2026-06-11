import { spawn } from "node:child_process";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve("competitive_intelligence_reports/spyglass_pharma_website_currentness_audit/2026-06-02_website_currentness");
const evidenceDir = join(root, "screenshots", "evidence");
mkdirSync(evidenceDir, { recursive: true });

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const port = 9333 + Math.floor(Math.random() * 400);
const profile = join(root, "sources", ".chrome-profile");
rmSync(profile, { recursive: true, force: true });

const targets = [
  {
    file: "source-01-study-data-phase-12-expected.png",
    url: "https://spyglasspharma.com/study-data/",
    snippet: "12-month interim data expected 2026",
    label: "Study-data page presents 12-month interim data as expected in 2026",
  },
  {
    file: "source-02-ir-march-12-month-results.png",
    url: "https://www.sec.gov/Archives/edgar/data/1778922/000177892226000004/exhibit991-8kpr.htm",
    snippet: "today announced positive 12-month results from the Phase 1/2 trial",
    label: "March 9, 2026 company release filed with SEC announces positive 12-month Phase 1/2 results",
  },
  {
    file: "source-03-technology-results-to-date-3-month.png",
    url: "https://www.spyglasspharma.com/our-technology/",
    snippet: "Phase 1/2 Study at 3 Months",
    label: "Technology page clinical-results module still foregrounds Phase 1/2 3-month data",
  },
  {
    file: "source-04-sec-q1-12-month-results.png",
    url: "https://www.sec.gov/Archives/edgar/data/1778922/000177892226000033/exhibit991-8kprx051426.htm",
    snippet: "Topline 12-month data from the BIM-IOL System Phase 1/2 trial",
    label: "May 14, 2026 company update repeats 12-month Phase 1/2 results",
  },
  {
    file: "source-05-pipeline-phase-3-context.png",
    url: "https://spyglasspharma.com/pipeline/",
    snippet: "Two Phase 3 clinical trials underway",
    label: "Pipeline page Phase 3 status context",
  },
  {
    file: "source-06-ir-may-phase-3-context.png",
    url: "https://www.sec.gov/Archives/edgar/data/1778922/000177892226000033/exhibit991-8kprx051426.htm",
    snippet: "Enrollment remains on track in the registrational Phase 3 trials",
    label: "May 14, 2026 company update supports Phase 3 enrollment context",
  },
  {
    file: "source-07-study-data-phase-3-bcdva-12-months.png",
    url: "https://spyglasspharma.com/study-data/#phase-3-clinical-trials",
    snippet: "Co-primary endpoints:",
    label: "Study-data page Phase 3 co-primary endpoint timing",
  },
  {
    file: "source-08-ctgov-sgp-005-bcdva-month-6.png",
    url: "https://clinicaltrials.gov/study/NCT07218783",
    snippet: "BCDVA 20/40 or better",
    label: "ClinicalTrials.gov SGP-005 BCDVA endpoint timing",
  },
  {
    file: "source-09-ctgov-sgp-006-bcdva-month-6.png",
    url: "https://clinicaltrials.gov/study/NCT07218796",
    snippet: "BCDVA 20/40 or better",
    label: "ClinicalTrials.gov SGP-006 BCDVA endpoint timing",
  },
];

function sleep(ms) {
  return new Promise((resolveSleep) => setTimeout(resolveSleep, ms));
}

async function waitForJson(url, tries = 80) {
  for (let i = 0; i < tries; i += 1) {
    try {
      const res = await fetch(url);
      if (res.ok) return res.json();
    } catch {}
    await sleep(250);
  }
  throw new Error(`Timed out waiting for ${url}`);
}

class Cdp {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.events = [];
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve: done, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else done(msg.result ?? {});
      } else if (msg.method) {
        this.events.push(msg);
      }
    };
  }

  async open() {
    while (this.ws.readyState === WebSocket.CONNECTING) await sleep(20);
  }

  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    const payload = JSON.stringify({ id, method, params });
    return new Promise((resolveSend, rejectSend) => {
      this.pending.set(id, { resolve: resolveSend, reject: rejectSend });
      this.ws.send(payload);
    });
  }

  close() {
    this.ws.close();
  }
}

function injectScript(snippet) {
  return `
(() => {
  const target = ${JSON.stringify(snippet)};
  const normalize = (s) => String(s || "").replace(/\\s+/g, " ").trim();
  document.querySelectorAll('[role="dialog"], .modal, .popup, .cookie, #onetrust-banner-sdk, .ot-sdk-container').forEach((el) => {
    const txt = normalize(el.innerText).toLowerCase();
    if (txt.includes("cookie") || txt.includes("privacy") || txt.includes("subscribe")) el.remove();
  });
  const allText = normalize(document.body.innerText);
  const shortTarget = normalize(target);
  let found = false;
  window.getSelection().removeAllRanges();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const nodeText = normalize(node.textContent);
    const ix = nodeText.toLowerCase().indexOf(shortTarget.toLowerCase());
    if (ix >= 0) {
      const raw = node.textContent;
      const rawLower = raw.toLowerCase();
      const rawIx = rawLower.indexOf(target.toLowerCase());
      const start = rawIx >= 0 ? rawIx : Math.max(0, rawLower.indexOf(shortTarget.split(" ")[0].toLowerCase()));
      const end = rawIx >= 0 ? rawIx + target.length : raw.length;
      const range = document.createRange();
      range.setStart(node, start);
      range.setEnd(node, Math.min(end, raw.length));
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      found = true;
      break;
    }
  }
  if (!found) {
    window.find(shortTarget, false, false, true, false, false, false);
  }
  const sel = window.getSelection();
  const rects = sel.rangeCount ? Array.from(sel.getRangeAt(0).getClientRects()) : [];
  const valid = rects.filter((r) => r.width > 4 && r.height > 4);
  const anchor = valid[0];
  if (anchor) {
    window.scrollTo({ top: Math.max(0, anchor.top + window.scrollY - (window.innerHeight * 0.42)), left: 0, behavior: "instant" });
  } else {
    const idx = allText.toLowerCase().indexOf(shortTarget.toLowerCase());
    if (idx >= 0) window.scrollTo(0, Math.max(0, document.body.scrollHeight * (idx / Math.max(1, allText.length)) - 250));
  }
  setTimeout(() => {
    const sel2 = window.getSelection();
    const rects2 = sel2.rangeCount ? Array.from(sel2.getRangeAt(0).getClientRects()) : [];
    rects2.filter((r) => r.width > 4 && r.height > 4).forEach((r) => {
      const box = document.createElement("div");
      box.setAttribute("data-codex-highlight", "true");
      Object.assign(box.style, {
        position: "absolute",
        left: (r.left + window.scrollX - 3) + "px",
        top: (r.top + window.scrollY - 3) + "px",
        width: (r.width + 6) + "px",
        height: (r.height + 6) + "px",
        border: "3px solid #e13d2f",
        background: "rgba(255, 235, 59, 0.28)",
        zIndex: 2147483647,
        pointerEvents: "none",
        boxSizing: "border-box"
      });
      document.body.appendChild(box);
    });
  }, 120);
})();
`;
}

async function captureOne(browser, target) {
  const pageInfo = await (await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(target.url)}`, { method: "PUT" })).json();
  const cdp = new Cdp(pageInfo.webSocketDebuggerUrl);
  await cdp.open();
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 920,
    deviceScaleFactor: 1.5,
    mobile: false,
  });
  await cdp.send("Page.navigate", { url: target.url });
  await sleep(4500);
  await cdp.send("Runtime.evaluate", {
    expression: `
      (() => {
        const buttons = Array.from(document.querySelectorAll('button, a'));
        const accept = buttons.find((b) => /accept all/i.test(b.innerText || b.textContent || ""));
        const close = buttons.find((b) => /reject all|close|dismiss/i.test(b.innerText || b.textContent || ""));
        if (accept) accept.click();
        else if (close) close.click();
      })();
    `,
  });
  await sleep(1200);
  await cdp.send("Runtime.evaluate", {
    expression: `window.scrollTo(0, document.body.scrollHeight);`,
  });
  await sleep(1200);
  await cdp.send("Runtime.evaluate", {
    expression: `
      (() => {
        document.querySelectorAll('details').forEach((el) => { el.open = true; });
        const candidates = Array.from(document.querySelectorAll('button, a, [role="button"], .accordion, .accordion-header, .elementor-tab-title'));
        candidates
          .filter((el) => /view study design|expand all/i.test(el.innerText || el.textContent || ""))
          .forEach((el) => { try { el.click(); } catch {} });
      })();
    `,
  });
  await sleep(1200);
  await cdp.send("Runtime.evaluate", {
    expression: `window.scrollTo(0, 0);`,
  });
  await sleep(800);
  await cdp.send("Runtime.evaluate", {
    expression: injectScript(target.snippet),
    awaitPromise: false,
  });
  await sleep(1000);
  const shot = await cdp.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  writeFileSync(join(evidenceDir, target.file), Buffer.from(shot.data, "base64"));
  cdp.close();
  await fetch(`http://127.0.0.1:${port}/json/close/${pageInfo.id}`);
}

const chrome = spawn(chromePath, [
  "--headless=new",
  "--disable-gpu",
  "--disable-extensions",
  "--hide-scrollbars",
  "--no-first-run",
  "--no-default-browser-check",
  "--user-agent=CodexCurrentnessAudit/1.0 (website currentness audit; contact via local Codex user)",
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`,
  "about:blank",
], { stdio: "ignore" });

try {
  await waitForJson(`http://127.0.0.1:${port}/json/version`);
  for (const target of targets) {
    console.log(`Capturing ${target.file}: ${target.label}`);
    await captureOne(chrome, target);
  }
} finally {
  chrome.kill();
}
