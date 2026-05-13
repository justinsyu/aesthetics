#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { dirname } from "node:path";
import { tmpdir } from "node:os";

const width = 1440;
const height = 1000;
const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_plans/iga_nephropathy/competitive_intelligence_reports/iga_nephropathy/2026-05-12_1245";

const sources = [
  {
    ref: 1,
    slug: "vera-q1-update",
    url: "https://ir.veratx.com/news-releases/news-release-details/vera-therapeutics-provides-business-update-and-reports-first-3",
    date: {
      output: "screenshots/date-verification/source-01-vera-q1-update-date.png",
      phrases: ["May 7, 2026"],
      scrollTo: "Vera Therapeutics Provides Business Update and Reports First Quarter 2026 Financial Results",
    },
    evidence: [
      {
        output: "screenshots/evidence/source-01-vera-q1-update-evidence-01.png",
        phrases: [
          "U.S. Food and Drug Administration (FDA) granted priority review to Biologics License Application (BLA)",
          "Prescription Drug User Fee Act (PDUFA) date of July 7, 2026",
          "On track for U.S. commercial launch of atacicept in mid-2026",
        ],
        scrollTo: "U.S. Food and Drug Administration (FDA) granted priority review",
      },
      {
        output: "screenshots/evidence/source-01-vera-q1-update-evidence-02.png",
        phrases: [
          "Pivotal two-year eGFR data from the ORIGIN 3 trial expected Q1 2027",
          "ORIGIN Phase 3 trial met the primary endpoint",
          "trial continues in a placebo-controlled blinded manner",
        ],
        scrollTo: "Pivotal two-year eGFR data from the ORIGIN 3 trial expected Q1 2027",
      },
    ],
  },
  {
    ref: 2,
    slug: "ctgov-ykst02",
    url: "https://clinicaltrials.gov/study/NCT07498673",
    date: {
      output: "screenshots/date-verification/source-02-ctgov-ykst02-date.png",
      phrases: ["2026-05-12"],
      scrollTo: "Last Update Posted",
    },
    evidence: [
      {
        output: "screenshots/evidence/source-02-ctgov-ykst02-evidence-01.png",
        phrases: [
          "Recruiting",
          "A Study of YKST02 in Participants With Primary IgA Nephropathy",
          "NCT07498673",
          "Union Hospital, Tongji Medical College, Huazhong University of Science and Technology",
        ],
        scrollTo: "A Study of YKST02 in Participants With Primary IgA Nephropathy",
      },
    ],
  },
  {
    ref: 3,
    slug: "ctgov-felzartamab",
    url: "https://clinicaltrials.gov/study/NCT06935357",
    date: {
      output: "screenshots/date-verification/source-03-ctgov-felzartamab-date.png",
      phrases: ["2026-05-06"],
      scrollTo: "Last Update Posted",
    },
    evidence: [
      {
        output: "screenshots/evidence/source-03-ctgov-felzartamab-evidence-01.png",
        phrases: [
          "Recruiting",
          "A Study to Learn About the Effects of Felzartamab Infusions on Adults With Immunoglobulin A Nephropathy (IgAN)",
          "NCT06935357",
          "Biogen",
        ],
        scrollTo: "A Study to Learn About the Effects of Felzartamab Infusions",
      },
    ],
  },
  {
    ref: 4,
    slug: "ctgov-mezagitamab",
    url: "https://clinicaltrials.gov/study/NCT06963827",
    date: {
      output: "screenshots/date-verification/source-04-ctgov-mezagitamab-date.png",
      phrases: ["2026-05-06"],
      scrollTo: "Last Update Posted",
    },
    evidence: [
      {
        output: "screenshots/evidence/source-04-ctgov-mezagitamab-evidence-01.png",
        phrases: [
          "Recruiting",
          "A Study of Mezagitamab in Adults With Kidney Condition Called IgA Nephropathy",
          "NCT06963827",
          "Takeda",
        ],
        scrollTo: "A Study of Mezagitamab in Adults With Kidney Condition Called IgA Nephropathy",
      },
    ],
  },
];

function chromeCandidates() {
  return [
    process.env.CHROME_PATH,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome",
    "chromium",
    "chromium-browser",
  ].filter(Boolean);
}

function findChrome() {
  for (const candidate of chromeCandidates()) {
    if (candidate.includes("/") && existsSync(candidate)) return candidate;
    if (!candidate.includes("/")) {
      const found = spawnSync("which", [candidate], { encoding: "utf8" });
      if (found.status === 0 && found.stdout.trim()) return found.stdout.trim();
    }
  }
  throw new Error("Could not find Chrome or Chromium. Set CHROME_PATH to the browser executable.");
}

function launchChrome(chromePath, userDataDir) {
  return new Promise((resolve, reject) => {
    const child = spawn(chromePath, [
      "--headless=new",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--hide-scrollbars",
      "--no-first-run",
      "--no-default-browser-check",
      "--remote-debugging-port=0",
      `--user-data-dir=${userDataDir}`,
      "about:blank",
    ], { stdio: ["ignore", "ignore", "pipe"] });

    let stderr = "";
    const timer = setTimeout(() => reject(new Error(`Timed out waiting for Chrome DevTools endpoint. ${stderr}`)), 15000);
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) {
        clearTimeout(timer);
        resolve({ child, browserWsUrl: match[1] });
      }
    });
    child.once("error", reject);
    child.once("exit", (code) => reject(new Error(`Chrome exited before DevTools was ready: ${code}. ${stderr}`)));
  });
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.nextId = 1;
    this.pending = new Map();
  }
  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = resolve;
      this.ws.onerror = () => reject(new Error(`Could not connect to ${this.wsUrl}`));
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve: done, reject: fail } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) fail(new Error(msg.error.message));
          else done(msg.result);
        }
      };
    });
  }
  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
  close() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.close();
  }
}

async function createPage(browserWsUrl, targetUrl) {
  const browserUrl = new URL(browserWsUrl);
  const httpOrigin = `http://${browserUrl.host}`;
  const response = await fetch(`${httpOrigin}/json/new?${encodeURIComponent(targetUrl)}`, { method: "PUT" });
  if (!response.ok) throw new Error(`Could not create Chrome target: HTTP ${response.status}`);
  const target = await response.json();
  const client = new CdpClient(target.webSocketDebuggerUrl);
  await client.connect();
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: false,
  });
  return client;
}

async function evaluate(client, expression, awaitPromise = false) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise,
    returnByValue: true,
  });
  if (result.exceptionDetails) throw new Error(`Evaluation failed: ${result.exceptionDetails.text}`);
  return result.result.value;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForReady(client) {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    const ready = await evaluate(client, "document.readyState === 'complete'");
    const hasBody = await evaluate(client, "Boolean(document.body && document.body.innerText && document.body.innerText.length > 100)");
    if (ready && hasBody) return;
    await sleep(250);
  }
  throw new Error("Timed out waiting for document readiness.");
}

async function markAndCapture(client, item, output) {
  const outPath = `${runDir}/${output}`;
  mkdirSync(dirname(outPath), { recursive: true });
  const result = await evaluate(client, `(() => {
    const phrases = ${JSON.stringify(item.phrases)};
    const scrollTo = ${JSON.stringify(item.scrollTo)};
    const norm = (s) => (s || "").replace(/\\u00a0/g, " ").replace(/\\s+/g, " ").trim();
    document.querySelectorAll(".codex-ci-mark, .codex-ci-anchor").forEach((el) => {
      el.classList.remove("codex-ci-mark", "codex-ci-anchor");
    });
    let style = document.getElementById("codex-ci-style");
    if (!style) {
      style = document.createElement("style");
      style.id = "codex-ci-style";
      document.head.appendChild(style);
    }
    style.textContent = ".codex-ci-mark{outline:5px solid #ff3b30!important;outline-offset:4px!important;background:rgba(255,230,0,.42)!important;box-shadow:0 0 0 8px rgba(255,230,0,.22)!important}.codex-ci-anchor{outline:7px solid #007aff!important;outline-offset:5px!important}";

    const visible = (el) => {
      const r = el.getBoundingClientRect();
      const cs = window.getComputedStyle(el);
      return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none";
    };
    const all = Array.from(document.querySelectorAll("body *")).filter(visible);
    const marked = [];
    const smallestMatch = (phrase) => {
      const p = norm(phrase);
      let matches = all.filter((el) => norm(el.innerText).includes(p));
      matches = matches.filter((el) => !Array.from(el.children).some((child) => norm(child.innerText).includes(p)));
      return matches.sort((a, b) => {
        const ar = a.getBoundingClientRect();
        const br = b.getBoundingClientRect();
        return (ar.width * ar.height) - (br.width * br.height);
      })[0];
    };
    for (const phrase of phrases) {
      const p = norm(phrase);
      let el = smallestMatch(phrase);
      if (!el) {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while ((node = walker.nextNode())) {
          if (norm(node.textContent).includes(p)) {
            el = node.parentElement;
            break;
          }
        }
      }
      if (el) {
        el.classList.add("codex-ci-mark");
        marked.push({ phrase, text: norm(el.innerText).slice(0, 220) });
      } else {
        marked.push({ phrase, missing: true });
      }
    }
    const scrollPhrase = norm(scrollTo || phrases[0]);
    const anchor = smallestMatch(scrollTo || phrases[0]) || document.querySelector(".codex-ci-mark");
    if (anchor) {
      anchor.classList.add("codex-ci-anchor");
      anchor.scrollIntoView({ block: "center", inline: "nearest" });
    }
    return { marked, scrollY: window.scrollY, title: document.title, url: location.href };
  })()`, true);
  await sleep(650);
  const screenshot = await client.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false, fromSurface: true });
  writeFileSync(outPath, Buffer.from(screenshot.data, "base64"));
  return { output, ...result };
}

async function main() {
  const chromePath = findChrome();
  const userDataDir = mkdtempSync(`${tmpdir()}/ci-sources-`);
  const { child, browserWsUrl } = await launchChrome(chromePath, userDataDir);
  const log = [];
  try {
    const onlyRefs = process.env.ONLY_REFS
      ? new Set(process.env.ONLY_REFS.split(",").map((value) => Number(value.trim())).filter(Boolean))
      : null;
    for (const source of sources.filter((entry) => !onlyRefs || onlyRefs.has(entry.ref))) {
      const client = await createPage(browserWsUrl, source.url);
      try {
        await waitForReady(client);
        await sleep(1000);
        log.push({ ref: source.ref, slug: source.slug, kind: "date", ...(await markAndCapture(client, source.date, source.date.output)) });
        for (const evidence of source.evidence) {
          log.push({ ref: source.ref, slug: source.slug, kind: "evidence", ...(await markAndCapture(client, evidence, evidence.output)) });
        }
      } finally {
        client.close();
      }
    }
  } finally {
    child.kill("SIGTERM");
    await sleep(500);
    rmSync(userDataDir, { recursive: true, force: true });
  }
  writeFileSync(`${runDir}/sources/capture-log.json`, JSON.stringify(log, null, 2));
  console.log(JSON.stringify(log, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
