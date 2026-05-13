#!/usr/bin/env node
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname } from "node:path";
import { spawn, spawnSync } from "node:child_process";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_plans/huntingtons_disease/competitive_intelligence_reports/huntingtons_disease/2026-05-12_1241";
const width = 1600;
const height = 900;
const userAgent = "OpenAI-Codex-CI/1.0 contact=justin208350@berkeley.edu";

const shots = [
  {
    url: "https://clinicaltrials.gov/study/NCT07326709",
    path: `${runDir}/screenshots/date-verification/source-01-date.png`,
    scrollText: "Recruiting",
    marks: ["Recruiting", "Last Update Posted", "2026-05-12"],
  },
  {
    url: "https://clinicaltrials.gov/study/NCT07326709",
    path: `${runDir}/screenshots/evidence/source-01-evidence-01.png`,
    scrollText: "Recruiting",
    marks: [
      "Recruiting",
      "A Study to Investigate the Efficacy, Safety and Tolerability of Votoplam in Participants With Huntington's Disease",
      "Novartis Pharmaceuticals",
      "Last Update Posted",
      "2026-05-12",
    ],
  },
  {
    url: "https://clinicaltrials.gov/study/NCT07326709",
    path: `${runDir}/screenshots/evidence/source-01-evidence-02.png`,
    scrollText: "Enrollment (Estimated)",
    marks: ["Enrollment", "770", "Study Type", "Interventional", "Phase", "Phase 3"],
  },
  {
    url: "https://clinicaltrials.gov/study/NCT07326709",
    path: `${runDir}/screenshots/evidence/source-01-evidence-03.png`,
    scrollText: "Change from Baseline in cUHDRS score",
    marks: ["Change from Baseline in cUHDRS score", "Baseline, Month 36"],
  },
  {
    url: "https://clinicaltrials.gov/study/NCT06826612",
    path: `${runDir}/screenshots/date-verification/source-02-date.png`,
    scrollText: "Recruiting",
    marks: ["Recruiting", "Last Update Posted", "2026-05-05"],
  },
  {
    url: "https://clinicaltrials.gov/study/NCT06826612",
    path: `${runDir}/screenshots/evidence/source-02-evidence-01.png`,
    scrollText: "Recruiting",
    marks: [
      "Recruiting",
      "A Randomized Study of SPK-10001 Gene Therapy in Participants With Huntington's Disease",
      "Hoffmann-La Roche",
      "Last Update Posted",
      "2026-05-05",
    ],
  },
  {
    url: "https://clinicaltrials.gov/study/NCT06826612",
    path: `${runDir}/screenshots/evidence/source-02-evidence-02.png`,
    scrollText: "Enrollment (Estimated)",
    marks: ["Enrollment", "53", "Study Type", "Interventional", "Phase", "Phase 1", "Phase 2"],
  },
  {
    url: "https://clinicaltrials.gov/study/NCT06826612",
    path: `${runDir}/screenshots/evidence/source-02-evidence-03.png`,
    scrollText: "Number of Participants with Treatment-emergent Adverse Events",
    marks: [
      "Number of Participants with Treatment-emergent Adverse Events",
      "Change from Baseline in Unified Huntington's Disease Rating Scale",
      "Baseline, Month 24",
    ],
  },
  {
    url: "https://www.sec.gov/Archives/edgar/data/1070081/000107008126000011/tmb-20260507xex99d1.htm",
    path: `${runDir}/screenshots/date-verification/source-03-date.png`,
    scrollText: "WARREN, N.J., May 7, 2026",
    marks: ["WARREN, N.J., May 7, 2026"],
  },
  {
    url: "https://www.sec.gov/Archives/edgar/data/1070081/000107008126000011/tmb-20260507xex99d1.htm",
    path: `${runDir}/screenshots/evidence/source-03-evidence-01.png`,
    scrollText: "Reported positive topline results in April 2026",
    marks: [
      "Reported positive topline results in April 2026",
      "PIVOT-HD long-term extension study of votoplam",
      "52% slowing of disease progression",
      "First patient dosed in Phase 3 INVEST-HD study",
      "$50 million milestone payment",
    ],
  },
  {
    url: "https://www.sec.gov/Archives/edgar/data/1590560/000110465926055242/qure-20260505xex99d1.htm",
    path: `${runDir}/screenshots/date-verification/source-04-date.png`,
    scrollText: "May 5, 2026",
    marks: ["May 5, 2026"],
  },
  {
    url: "https://www.sec.gov/Archives/edgar/data/1590560/000110465926055242/qure-20260505xex99d1.htm",
    path: `${runDir}/screenshots/evidence/source-04-evidence-01.png`,
    scrollText: "Advancing AMT-130 for the treatment of Huntington",
    marks: [
      "Advancing AMT-130 for the treatment of Huntington",
      "Type B meeting with the FDA",
      "four-year data expected in the third quarter of 2026",
      "Marketing Authorization Application",
      "third quarter of 2026",
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

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function launchChrome(chromePath, userDataDir) {
  return new Promise((resolve, reject) => {
    const child = spawn(chromePath, [
      "--headless=new",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--no-first-run",
      "--no-default-browser-check",
      "--hide-scrollbars",
      "--remote-debugging-port=0",
      `--user-agent=${userAgent}`,
      `--user-data-dir=${userDataDir}`,
      "about:blank",
    ], { stdio: ["ignore", "ignore", "pipe"] });

    let stderr = "";
    let settled = false;
    const timer = setTimeout(() => {
      if (!settled) {
        child.kill("SIGTERM");
        reject(new Error(`Timed out waiting for Chrome DevTools endpoint. ${stderr}`));
      }
    }, 15000);

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match && !settled) {
        settled = true;
        clearTimeout(timer);
        resolve({ child, browserWsUrl: match[1] });
      }
    });

    child.once("error", reject);
    child.once("exit", (code) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(new Error(`Chrome exited before DevTools was ready with code ${code}. ${stderr}`));
      }
    });
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
      this.ws.onopen = () => resolve();
      this.ws.onerror = () => reject(new Error(`Could not connect to ${this.wsUrl}`));
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve: ok, reject: bad } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) bad(new Error(`${msg.error.message}${msg.error.data ? `: ${msg.error.data}` : ""}`));
          else ok(msg.result);
        }
      };
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
    });
  }

  close() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.close();
  }
}

async function createPage(browserWsUrl) {
  const browserUrl = new URL(browserWsUrl);
  const response = await fetch(`http://${browserUrl.host}/json/new?about:blank`, { method: "PUT" });
  if (!response.ok) throw new Error(`Could not create Chrome target: HTTP ${response.status}`);
  const target = await response.json();
  const client = new CdpClient(target.webSocketDebuggerUrl);
  await client.connect();
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Network.enable");
  await client.send("Network.setUserAgentOverride", { userAgent });
  await client.send("Network.setExtraHTTPHeaders", {
    headers: { "User-Agent": userAgent },
  });
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
  if (result.exceptionDetails) {
    throw new Error(`Evaluation failed: ${result.exceptionDetails.text}`);
  }
  return result.result.value;
}

async function waitForReady(client) {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    const ready = await evaluate(client, "document.readyState === 'complete'");
    if (ready) return;
    await wait(150);
  }
  throw new Error("Timed out waiting for page readiness.");
}

const markerScript = (marks, scrollText) => `
(() => {
  const normalize = (value) => String(value || '').replace(/\\s+/g, ' ').trim().toLowerCase();
  document.querySelectorAll('.ci-marker').forEach((el) => el.remove());
  const style = document.createElement('style');
  style.className = 'ci-marker';
  style.textContent = \`
    [class*="survey"], [id*="survey"], [aria-label*="glossary" i], [title*="glossary" i] {
      display: none !important;
    }
    .ci-box {
      position: absolute;
      border: 4px solid #ff6b00;
      background: rgba(255, 235, 59, 0.26);
      box-shadow: 0 0 0 2px rgba(0,0,0,.48);
      z-index: 2147483646;
      pointer-events: none;
      border-radius: 4px;
    }\`;
  document.head.appendChild(style);

  const skipTags = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEXTAREA']);
  const nodes = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      if (node.parentElement && skipTags.has(node.parentElement.tagName)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  while (walker.nextNode()) nodes.push(walker.currentNode);

  function markOne(needle) {
    const wanted = normalize(needle);
    if (!wanted) return null;
    for (const node of nodes) {
      const raw = node.nodeValue;
      const folded = normalize(raw);
      const foldedIndex = folded.indexOf(wanted);
      if (foldedIndex < 0) continue;
      const rawLower = raw.toLowerCase();
      const rawIndex = rawLower.indexOf(String(needle).toLowerCase());
      const start = rawIndex >= 0 ? rawIndex : Math.max(0, Math.min(raw.length - 1, foldedIndex));
      const end = rawIndex >= 0 ? rawIndex + String(needle).length : raw.length;
      const range = document.createRange();
      range.setStart(node, start);
      range.setEnd(node, Math.min(node.length, end));
      const rects = Array.from(range.getClientRects()).filter((r) => r.width > 2 && r.height > 2);
      const rect = rects[0] || range.getBoundingClientRect();
      if (!rect || rect.width < 2 || rect.height < 2) continue;
      for (const r of rects.slice(0, 5)) {
        const box = document.createElement('div');
        box.className = 'ci-marker ci-box';
        box.style.left = (r.left + window.scrollX - 3) + 'px';
        box.style.top = (r.top + window.scrollY - 3) + 'px';
        box.style.width = (r.width + 6) + 'px';
        box.style.height = (r.height + 6) + 'px';
        document.body.appendChild(box);
      }
      return { top: rect.top + window.scrollY, text: raw.trim().slice(0, 120) };
    }
    return null;
  }

  const marks = ${JSON.stringify(marks)};
  const results = marks.map((text) => ({ text, result: markOne(text) }));
  const scrollResult = markOne(${JSON.stringify(scrollText)}) || results.find((r) => r.result)?.result;
  if (scrollResult) {
    window.scrollTo({ top: Math.max(0, scrollResult.top - 170), behavior: 'instant' });
  }
  return results;
})()
`;

async function capture(client, item) {
  await client.send("Page.navigate", { url: item.url });
  await waitForReady(client);
  await evaluate(client, "document.fonts ? document.fonts.ready.then(() => true) : true", true).catch(() => null);
  await wait(item.url.includes("clinicaltrials.gov") ? 2600 : 800);
  const results = await evaluate(client, markerScript(item.marks, item.scrollText));
  await wait(350);
  mkdirSync(dirname(item.path), { recursive: true });
  const screenshot = await client.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  writeFileSync(item.path, Buffer.from(screenshot.data, "base64"));
  const missing = results.filter((row) => !row.result).map((row) => row.text);
  console.log(`${missing.length ? "WARN" : "OK"} ${item.path}${missing.length ? ` missing: ${missing.join(" | ")}` : ""}`);
}

async function main() {
  const chromePath = findChrome();
  const userDataDir = mkdtempSync(`${tmpdir()}/hd-ci-chrome-`);
  const { child, browserWsUrl } = await launchChrome(chromePath, userDataDir);
  const client = await createPage(browserWsUrl);
  try {
    for (const item of shots) {
      await capture(client, item);
    }
  } finally {
    client.close();
    child.kill("SIGTERM");
    await wait(700);
    rmSync(userDataDir, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
