#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/mps_ii_hunter_syndrome/2026-05-12_1240";
const dateDir = join(runDir, "screenshots/date-verification");
const evidenceDir = join(runDir, "screenshots/evidence");
const ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36 linkedin-posts-ci-report/1.0 justinyu@example.com";

const sources = [
  {
    ref: "01",
    dateUrl: "https://www.federalregister.gov/api/v1/documents/2026-09242?fields[]=publication_date&fields[]=title&fields[]=abstract",
    evidenceUrl: "https://www.federalregister.gov/api/v1/documents/2026-09242?fields[]=publication_date&fields[]=title&fields[]=abstract",
    dateMarks: ["2026-05-11"],
    evidenceMarks: [
      "FDA is announcing the issuance of a priority review voucher",
      "AVLAYAH (tividenofusp alfa-eknm), approved March 24, 2026",
      "Denali Therapeutics Inc.",
      "meets the criteria for a priority review voucher"
    ],
  },
  {
    ref: "02",
    dateUrl: "https://www.sec.gov/Archives/edgar/data/1714899/000171489926000062/ex991pressreleaseq12026.htm",
    evidenceUrl: "https://www.sec.gov/Archives/edgar/data/1714899/000171489926000062/ex991pressreleaseq12026.htm",
    dateMarks: ["May\u00a07, 2026", "May 7, 2026"],
    evidenceMarks: [
      "AVLAYAH launched in U.S.",
      "first patients treated in commercial setting in April",
      "The ongoing global Phase 2/3 COMPASS study is designed to generate confirmatory evidence"
    ],
  },
  {
    ref: "03",
    dateUrl: "https://www.sec.gov/Archives/edgar/data/1714899/000171489926000064/0001714899-26-000064-index.html",
    evidenceUrl: "https://www.sec.gov/Archives/edgar/data/1714899/000171489926000064/dnli-20260331.htm",
    dateMarks: ["Filing Date", "2026-05-07"],
    evidenceMarks: [
      "approved for the treatment of neurologic manifestations in patients with Hunter syndrome",
      "We began commercial distribution of AVLAYAH in April 2026",
      "91% (95% CI: 89%, 92%) reduction in CSF HS levels",
      "ongoing global Phase 2/3 COMPASS study is designed to generate confirmatory evidence"
    ],
  },
  {
    ref: "04",
    dateUrl: "https://clinicaltrials.gov/api/v2/studies/NCT06075537",
    evidenceUrl: "https://clinicaltrials.gov/api/v2/studies/NCT06075537",
    dateMarks: ["2026-05-12"],
    evidenceMarks: [
      "NCT06075537",
      "ENROLLING_BY_INVITATION",
      "PHASE2",
      "PHASE3",
      "Denali Therapeutics Inc.",
      "An Extension Study of the Long-Term Safety, Tolerability, and Efficacy of Tividenofusp Alfa"
    ],
  },
  {
    ref: "05",
    dateUrl: "https://www.gcbiopharma.com/kor/news_view.do?idx=3187",
    evidenceUrl: "https://www.gcbiopharma.com/kor/news_view.do?idx=3187",
    dateMarks: ["2026-05-06"],
    evidenceMarks: [
      "헌터라제 ICV",
      "페루 의약품관리국(DIGEMID)로부터 품목허가를 획득",
      "일본과 러시아에 이어 세 번째로 획득한 해외 품목허가",
      "월 1회 투약"
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
  throw new Error("Could not find Chrome or Chromium.");
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
        resolve({ child, browserWsUrl: match[1] });
      }
    });
    child.once("error", reject);
    child.once("exit", (code) => {
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
          const { resolve: res, reject: rej } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) rej(new Error(`${msg.error.message}${msg.error.data ? `: ${msg.error.data}` : ""}`));
          else res(msg.result);
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
  const httpOrigin = `http://${browserUrl.host}`;
  const response = await fetch(`${httpOrigin}/json/new?about%3Ablank`, { method: "PUT" });
  if (!response.ok) throw new Error(`Could not create Chrome target: HTTP ${response.status}`);
  const target = await response.json();
  const client = new CdpClient(target.webSocketDebuggerUrl);
  await client.connect();
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Network.enable");
  await client.send("Network.setUserAgentOverride", { userAgent: ua });
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 1040,
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

async function waitForReady(client) {
  const deadline = Date.now() + 18000;
  while (Date.now() < deadline) {
    if (await evaluate(client, "document.readyState === 'complete'")) return;
    await wait(200);
  }
  throw new Error("Timed out waiting for document readiness.");
}

async function navigate(client, url) {
  await client.send("Page.navigate", { url });
  await waitForReady(client);
  await wait(1200);
  await evaluate(client, `
    (() => {
      document.documentElement.style.scrollBehavior = 'auto';
      const style = document.createElement('style');
      style.textContent = [
        'html,body{scrollbar-width:none!important;background:#fff!important}',
        'html::-webkit-scrollbar,body::-webkit-scrollbar{display:none!important}',
        'pre{white-space:pre-wrap!important;word-break:break-word!important;font:16px/1.35 ui-monospace,SFMono-Regular,Menlo,monospace!important;max-width:1320px!important;}',
        '.ci-mark{background:#d7ff5f!important;color:#000!important;outline:4px solid #111!important;box-shadow:0 0 0 4px #d7ff5f!important;border-radius:2px!important;}'
      ].join('\\n');
      document.head.appendChild(style);
      return true;
    })()
  `);
}

async function markText(client, phrases) {
  const json = JSON.stringify(phrases);
  return evaluate(client, `
    (() => {
      const phrases = ${json};
      let count = 0;
      function wrapInTextNode(node, phrase) {
        const text = node.nodeValue;
        const idx = text.indexOf(phrase);
        if (idx < 0) return false;
        const before = document.createTextNode(text.slice(0, idx));
        const mark = document.createElement('span');
        mark.className = 'ci-mark';
        mark.setAttribute('data-ci-mark', String(count + 1));
        mark.textContent = text.slice(idx, idx + phrase.length);
        const after = document.createTextNode(text.slice(idx + phrase.length));
        const parent = node.parentNode;
        parent.insertBefore(before, node);
        parent.insertBefore(mark, node);
        parent.insertBefore(after, node);
        parent.removeChild(node);
        count += 1;
        return true;
      }
      for (const phrase of phrases) {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
          acceptNode(node) {
            if (!node.nodeValue || !node.nodeValue.includes(phrase)) return NodeFilter.FILTER_REJECT;
            if (node.parentElement && node.parentElement.closest('script,style,noscript')) return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
          }
        });
        const node = walker.nextNode();
        if (node) wrapInTextNode(node, phrase);
      }
      const first = document.querySelector('.ci-mark');
      if (first) first.scrollIntoView({ block: 'center', inline: 'nearest' });
      return { marked: count, text: document.body.innerText.slice(0, 1200) };
    })()
  `);
}

async function screenshot(client, path) {
  mkdirSync(dirname(path), { recursive: true });
  const result = await client.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: false,
    fromSurface: true,
  });
  writeFileSync(path, Buffer.from(result.data, "base64"));
}

async function stopProcess(child) {
  if (!child || child.killed || child.exitCode !== null) return;
  child.kill("SIGTERM");
  await Promise.race([
    new Promise((resolve) => child.once("exit", resolve)),
    wait(3000),
  ]);
  if (child.exitCode === null && !child.killed) child.kill("SIGKILL");
}

const chromePath = findChrome();
const userDataDir = mkdtempSync(join(tmpdir(), "mps-ci-chrome-"));
const { child, browserWsUrl } = await launchChrome(chromePath, userDataDir);

try {
  for (const source of sources) {
    const dateClient = await createPage(browserWsUrl);
    await navigate(dateClient, source.dateUrl);
    const dateResult = await markText(dateClient, source.dateMarks);
    if (!dateResult.marked) throw new Error(`No date mark created for source ${source.ref}`);
    await screenshot(dateClient, join(dateDir, `source-${source.ref}-date.png`));
    dateClient.close();

    const evidenceClient = await createPage(browserWsUrl);
    await navigate(evidenceClient, source.evidenceUrl);
    const evidenceResult = await markText(evidenceClient, source.evidenceMarks);
    if (!evidenceResult.marked) throw new Error(`No evidence mark created for source ${source.ref}: ${evidenceResult.text}`);
    await screenshot(evidenceClient, join(evidenceDir, `source-${source.ref}-evidence-01.png`));
    evidenceClient.close();
    console.log(`captured source ${source.ref}: ${dateResult.marked} date marks, ${evidenceResult.marked} evidence marks`);
  }
} finally {
  await stopProcess(child);
  rmSync(userDataDir, { recursive: true, force: true });
}
