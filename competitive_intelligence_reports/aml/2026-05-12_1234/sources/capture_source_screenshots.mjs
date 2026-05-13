#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const RUN = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/aml/2026-05-12_1234";
const DATE_DIR = `${RUN}/screenshots/date-verification`;
const EVIDENCE_DIR = `${RUN}/screenshots/evidence`;

const sources = [
  {
    id: "01",
    slug: "syndax-revuforj-eha",
    url: "https://www.globenewswire.com/news-release/2026/05/12/3293092/0/en/syndax-highlights-12-revuforj-revumenib-abstracts-accepted-for-eha-2026-advancing-leadership-in-menin-inhibition.html",
    date: "May 12, 2026 10:31 ET",
    evidence: [
      "today highlighted the release of 12 Revuforj",
      "Key revumenib data accepted for presentation at EHA 2026:",
    ],
  },
  {
    id: "02",
    slug: "kura-ziftomenib-eha",
    url: "https://www.globenewswire.com/news-release/2026/05/12/3293020/35186/en/kura-oncology-and-kyowa-kirin-to-present-updated-frontline-ziftomenib-7-3-combination-data-at-eha-2026-congress.html",
    date: "May 12, 2026 09:40 ET",
    evidence: [
      "The oral presentation will highlight updated results in 99 patients",
      "Composite complete response (CRc) rates of 96%",
      "Measurable residual disease (MRD)-negativity rates among CRc responders",
    ],
  },
  {
    id: "03",
    slug: "blossomhill-bh30236-eha",
    url: "https://www.globenewswire.com/news-release/2026/05/12/3292992/0/en/blossomhill-therapeutics-to-present-initial-clinical-dose-escalation-data-from-the-phase-1-1b-trial-of-bh-30236-in-patients-with-r-r-aml-or-hr-mds-at-eha2026.html",
    date: "May 12, 2026 09:30 ET",
    evidence: [
      "initial dose escalation data from its Phase 1/1b trial of BH-30236",
      "As of the January 23, 2026 cutoff date for the EHA abstract submission",
      "Early signs of clinical activity were observed",
    ],
  },
  {
    id: "04",
    slug: "moleculin-annamycin-cardiac",
    url: "https://www.globenewswire.com/news-release/2026/05/12/3293002/0/en/independent-cleveland-clinic-review-finds-no-clinically-significant-cardiotoxicity-with-moleculin-s-annamycin-in-r-r-aml-patients-dosed-beyond-conventional-anthracycline-limits.html",
    date: "May 12, 2026 09:30 ET",
    evidence: [
      "Pooled analysis of 90 subjects across 5 trials",
      "Among 78 patients with source-data verified pre- and post-treatment ejection fraction assessments",
    ],
  },
  {
    id: "05",
    slug: "evaxion-evx04-eha",
    url: "https://www.globenewswire.com/news-release/2026/05/12/3293006/0/en/evaxion-to-present-new-data-for-evx-04-an-off-the-shelf-therapeutic-vaccine-for-acute-myeloid-leukemia-at-the-eha-2026-congress.html",
    date: "May 12, 2026 09:30 ET",
    evidence: [
      "will announce the functional characterization of EVX-04",
      "Evaxion plans to submit a clinical trial application in the second half of 2026",
      "All 16 ERV fragments included in EVX-04 elicit a specific immune response",
    ],
  },
  {
    id: "06",
    slug: "cero-cer1236-dose-cohort",
    url: "https://www.globenewswire.com/news-release/2026/05/11/3291858/0/en/cero-therapeutics-completes-second-ascending-dose-cohort-of-phase-1-cer-1236-trial.html",
    date: "May 11, 2026 08:15 ET",
    evidence: [
      "completed dosing and the 28-day dose-limiting toxicity",
      "patients received CER-1236 at a total dose of 4 × 10⁶ cells/kg",
      "now escalating to the planned 1 × 10⁷ cells/kg split-dose cohort",
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

async function waitForReady(client, expectedUrl = "") {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    const ready = await evaluate(client, `
      (() => {
        const hrefOk = ${JSON.stringify(expectedUrl)} ? location.href.toLowerCase().includes(${JSON.stringify(expectedUrl.toLowerCase().slice(0, 80))}) : true;
        return hrefOk && document.readyState === 'complete' && document.body && document.body.innerText.length > 1000;
      })()
    `);
    if (ready) return;
    await delay(200);
  }
  throw new Error("Timed out waiting for page load");
}

async function preparePage(client, url) {
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: 1600,
    height: 1100,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await client.send("Page.navigate", { url });
  await delay(750);
  await waitForReady(client, new URL(url).pathname);
  await evaluate(client, "document.fonts ? document.fonts.ready.then(() => true) : true", true);
  await evaluate(client, `
    (() => {
      document.documentElement.style.scrollBehavior = 'auto';
      const style = document.createElement('style');
      style.textContent = [
        'html,body{scrollbar-width:none!important}',
        'html::-webkit-scrollbar,body::-webkit-scrollbar{display:none!important}',
        '.cc-window,.cookie,.cookies,.cookie-banner,.modal,.newsletter,.popup,[class*="cookie"],[id*="cookie"],[class*="modal"],[id*="modal"],[class*="newsletter"],[id*="newsletter"],[class*="chat"],[id*="chat"]{display:none!important}',
        '.marked-evidence{outline:5px solid #ff2f00!important;background:rgba(255,255,0,.45)!important;box-shadow:0 0 0 8px rgba(255,47,0,.12)!important;border-radius:4px!important}'
      ].join('\\n');
      document.head.appendChild(style);
      document.querySelectorAll('button,[role="button"]').forEach((el) => {
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
      const candidates = Array.from(document.querySelectorAll('time,h1,h2,h3,p,li,td,th,span'));
      let best = null;
      for (const el of candidates) {
        const text = normalize(el.innerText || el.textContent);
        if (!text || !text.includes(phrase)) continue;
        if (!best || text.length < normalize(best.innerText || best.textContent).length) best = el;
      }
      if (!best) {
        for (const el of candidates) {
          const text = normalize(el.innerText || el.textContent);
          if (!text || !phrase.toLowerCase().split(' ').every((part) => !part || text.toLowerCase().includes(part))) continue;
          best = el;
          break;
        }
      }
      if (!best) return { found: false, phrase };
      best.classList.add('marked-evidence');
      best.scrollIntoView({ block: 'center', inline: 'nearest' });
      const r = best.getBoundingClientRect();
      return { found: true, phrase, text: normalize(best.innerText || best.textContent).slice(0, 500), rect: [r.left, r.top, r.width, r.height] };
    })()
  `);
  if (!found.found) {
    const debug = await evaluate(client, `
      (() => ({
        href: location.href,
        title: document.title,
        hasPhraseInBody: document.body.innerText.includes(${JSON.stringify(phrase)}),
        times: Array.from(document.querySelectorAll('time')).map((t) => t.textContent),
        sample: document.body.innerText.slice(0, 900)
      }))()
    `);
    throw new Error(`Phrase not found: ${phrase}\\n${JSON.stringify(debug, null, 2)}`);
  }
  await delay(500);
  const result = await client.send("Page.captureScreenshot", { format: "png", fromSurface: true });
  writeFileSync(output, Buffer.from(result.data, "base64"));
  return found;
}

async function main() {
  mkdirSync(DATE_DIR, { recursive: true });
  mkdirSync(EVIDENCE_DIR, { recursive: true });
  const userDataDir = join(tmpdir(), `aml-ci-chrome-${process.pid}`);
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
  process.exit(0);
}

main().catch((err) => {
  console.error(err.stack || err.message);
  process.exit(1);
});
