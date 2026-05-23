#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const RUN = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/syngap1/2026-05-14_1431";
const DATE_DIR = `${RUN}/screenshots/date-verification`;
const EVIDENCE_DIR = `${RUN}/screenshots/evidence`;

const sources = [
  {
    id: "01",
    slug: "camp4-cmp002-sec-exhibit-991",
    url: "https://www.sec.gov/Archives/edgar/data/1736730/000173673026000033/a20260514exhibit991.htm",
    date: "CAMBRIDGE, Mass., May 14, 2026",
    evidence: [
      "today announced the presentation of new preclinical data for CMP-002",
      "produced a statistically significant improvement in both seizure threshold and severity",
      "the study employed a seizure induction model using pentylenetetrazol",
      "CAMP4 expects to advance CMP-002 into a Phase 1/2 clinical trial",
      "CMP-002 is CAMP4's lead investigational ASO therapeutic candidate",
      "There are currently no approved disease-modifying therapies",
    ],
  },
  {
    id: "02",
    slug: "camp4-sec-8k",
    url: "https://www.sec.gov/Archives/edgar/data/1736730/000173673026000033/camp-20260514.htm",
    date: "May 14, 2026",
    evidence: [
      "issued a press releases titled",
      "the Company also updated its corporate slide presentation",
      "Press release issued by CAMP4 Therapeutics Corporation on May 14, 2026",
      "Slide presentation, dated May 2026",
    ],
  },
  {
    id: "03",
    slug: "tides-agenda",
    url: "https://informaconnect.com/tides/agenda/4/",
    date: "Thursday, 14 May 2026",
    evidence: [
      "Targeting Noncoding Regulatory RNAs with Antisense Oligonucleotides to Increase Gene Expression",
      "CMP-002 is advancing towards the clinic",
      "Dan Tardiff, PhD",
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
    const timer = setTimeout(() => {
      child.kill("SIGTERM");
      reject(new Error(`Timed out waiting for Chrome DevTools endpoint. ${stderr}`));
    }, 15000);

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) {
        clearTimeout(timer);
        resolve({ child, wsUrl: match[1] });
      }
    });
    child.on("error", reject);
    child.on("exit", (code) => {
      if (!stderr.includes("DevTools listening")) {
        clearTimeout(timer);
        reject(new Error(`Chrome exited before DevTools was ready with code ${code}. ${stderr}`));
      }
    });
  });
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.id = 1;
    this.pending = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = resolve;
      this.ws.onerror = () => reject(new Error(`Could not connect to ${this.wsUrl}`));
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (!msg.id || !this.pending.has(msg.id)) return;
        const { resolve: ok, reject: bad } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) bad(new Error(`${msg.error.message}${msg.error.data ? `: ${msg.error.data}` : ""}`));
        else ok(msg.result);
      };
    });
  }

  send(method, params = {}) {
    const id = this.id++;
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
  return client;
}

async function evaluate(client, expression, awaitPromise = false) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise,
    returnByValue: true,
  });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "Evaluation failed");
  return result.result.value;
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForReady(client) {
  const deadline = Date.now() + 25000;
  while (Date.now() < deadline) {
    const ready = await evaluate(client, `
      (() => document.readyState === 'complete' && document.body && document.body.innerText.length > 500)()
    `);
    if (ready) return;
    await delay(300);
  }
  throw new Error("Timed out waiting for page load");
}

async function preparePage(client, url) {
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Network.enable");
  await client.send("Network.setUserAgentOverride", {
    userAgent: "linkedin-posts-ci/1.0 contact justin@example.com",
  });
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: 1600,
    height: 1100,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await client.send("Page.navigate", { url });
  await delay(1200);
  await waitForReady(client);
  await evaluate(client, "document.fonts ? document.fonts.ready.then(() => true) : true", true);
  await evaluate(client, `
    (() => {
      document.documentElement.style.scrollBehavior = 'auto';
      const style = document.createElement('style');
      style.textContent = [
        'html,body{scrollbar-width:none!important}',
        'html::-webkit-scrollbar,body::-webkit-scrollbar{display:none!important}',
        '.cc-window,.cookie,.cookies,.cookie-banner,.modal,.newsletter,.popup,[class*="cookie"],[class*="Cookie"],[id*="cookie"],[id*="Cookie"],[class*="consent"],[class*="Consent"],[id*="consent"],[id*="Consent"],[class*="privacy"],[class*="Privacy"],[id*="privacy"],[id*="Privacy"],[class*="modal"],[class*="Modal"],[id*="modal"],[id*="Modal"],[class*="newsletter"],[id*="newsletter"],[class*="chat"],[id*="chat"],[aria-label*="cookie" i],[aria-label*="privacy" i],.onetrust-pc-dark-filter{display:none!important}',
        '.marked-evidence{outline:5px solid #ff2f00!important;background:rgba(255,255,0,.48)!important;box-shadow:0 0 0 8px rgba(255,47,0,.12)!important;border-radius:4px!important}'
      ].join('\\n');
      document.head.appendChild(style);
      document.querySelectorAll('button,[role="button"],a').forEach((el) => {
        const label = [el.textContent, el.getAttribute('aria-label'), el.getAttribute('title')].filter(Boolean).join(' ');
        if (/accept|agree|close|dismiss|continue/i.test(label) && el.getBoundingClientRect().width > 0) {
          try { el.click(); } catch {}
        }
      });
      return true;
    })()
  `);
}

async function markAndScreenshot(client, phrase, output) {
  const found = await evaluate(client, `
    (() => {
      const normalize = (s) => (s || '').replace(/\\u00a0/g, ' ').replace(/\\s+/g, ' ').trim();
      const phrase = normalize(${JSON.stringify(phrase)});
      document.querySelectorAll('.marked-evidence').forEach((el) => el.classList.remove('marked-evidence'));
      const candidates = Array.from(document.querySelectorAll('time,h1,h2,h3,h4,p,li,td,th,span,div,font,strong,a'));
      let best = null;
      for (const el of candidates) {
        const text = normalize(el.innerText || el.textContent);
        if (!text || !text.includes(phrase)) continue;
        if (!best || text.length < normalize(best.innerText || best.textContent).length) best = el;
      }
      if (!best) {
        const parts = phrase.toLowerCase().split(' ').filter(Boolean);
        for (const el of candidates) {
          const text = normalize(el.innerText || el.textContent).toLowerCase();
          if (!text || !parts.every((part) => text.includes(part))) continue;
          best = el;
          break;
        }
      }
      if (!best) return { found: false, phrase, sample: normalize(document.body.innerText).slice(0, 1200) };
      best.classList.add('marked-evidence');
      best.scrollIntoView({ block: 'center', inline: 'nearest' });
      const r = best.getBoundingClientRect();
      return { found: true, phrase, text: normalize(best.innerText || best.textContent).slice(0, 650), rect: [r.left, r.top, r.width, r.height] };
    })()
  `);
  if (!found.found) {
    throw new Error(`Phrase not found: ${phrase}\\n${JSON.stringify(found, null, 2)}`);
  }
  await delay(500);
  const result = await client.send("Page.captureScreenshot", { format: "png", fromSurface: true });
  writeFileSync(output, Buffer.from(result.data, "base64"));
  return found;
}

async function main() {
  mkdirSync(DATE_DIR, { recursive: true });
  mkdirSync(EVIDENCE_DIR, { recursive: true });
  const userDataDir = join(tmpdir(), `syngap1-ci-chrome-${process.pid}`);
  mkdirSync(userDataDir, { recursive: true });
  const chromePath = findChrome();
  const { child, wsUrl } = await launchChrome(chromePath, userDataDir);
  const log = [];
  try {
    for (const source of sources) {
      const client = await createPage(wsUrl, source.url);
      try {
        await preparePage(client, source.url);
        const datePath = `${DATE_DIR}/source-${source.id}-${source.slug}-date.png`;
        const dateResult = await markAndScreenshot(client, source.date, datePath);
        log.push({ source: source.id, kind: "date", phrase: source.date, path: datePath, markedText: dateResult.text });

        for (let i = 0; i < source.evidence.length; i += 1) {
          const evidencePath = `${EVIDENCE_DIR}/source-${source.id}-${source.slug}-evidence-${String(i + 1).padStart(2, "0")}.png`;
          const evidenceResult = await markAndScreenshot(client, source.evidence[i], evidencePath);
          log.push({ source: source.id, kind: `evidence-${i + 1}`, phrase: source.evidence[i], path: evidencePath, markedText: evidenceResult.text });
        }
      } finally {
        client.close();
      }
    }
  } finally {
    child.kill("SIGTERM");
    await delay(500);
    rmSync(userDataDir, { recursive: true, force: true });
  }
  writeFileSync(`${RUN}/sources/capture-log.json`, JSON.stringify(log, null, 2));
  console.log(`Captured ${log.length} marked screenshots`);
}

main().catch((err) => {
  console.error(err.stack || err.message);
  process.exit(1);
});
