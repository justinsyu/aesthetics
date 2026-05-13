#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const outDir = resolve("outputs/pharma_cms_2025");
const sourceDir = join(outDir, "sources");
const screenshotDir = join(outDir, "screenshots");
mkdirSync(screenshotDir, { recursive: true });

function chromeCandidates() {
  return [
    process.env.CHROME_PATH,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
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
  throw new Error("Chrome/Chromium not found.");
}

function launchChrome(chromePath) {
  return new Promise((resolveLaunch, rejectLaunch) => {
    const userDataDir = join(tmpdir(), `codex-cdp-${Date.now()}`);
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
    const timer = setTimeout(() => rejectLaunch(new Error(`Timed out launching Chrome. ${stderr}`)), 15000);
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) {
        clearTimeout(timer);
        resolveLaunch({ child, browserWsUrl: match[1] });
      }
    });
    child.once("error", rejectLaunch);
  });
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.nextId = 1;
    this.pending = new Map();
  }
  connect() {
    return new Promise((resolveConnect, rejectConnect) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolveConnect();
      this.ws.onerror = () => rejectConnect(new Error(`Could not connect to ${this.wsUrl}`));
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message));
          else resolve(msg.result);
        }
      };
    });
  }
  send(method, params = {}) {
    const id = this.nextId++;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
  close() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.close();
  }
}

async function createPage(browserWsUrl, targetUrl) {
  const browserUrl = new URL(browserWsUrl);
  const response = await fetch(`http://${browserUrl.host}/json/new?${encodeURIComponent(targetUrl)}`, { method: "PUT" });
  if (!response.ok) throw new Error(`Could not create target: ${response.status}`);
  const target = await response.json();
  const client = new CdpClient(target.webSocketDebuggerUrl);
  await client.connect();
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  return client;
}

async function evaluate(client, expression, awaitPromise = false) {
  const result = await client.send("Runtime.evaluate", { expression, awaitPromise, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
  return result.result.value;
}

async function waitForReady(client) {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    if (await evaluate(client, "document.readyState === 'complete'")) return;
    await new Promise((r) => setTimeout(r, 150));
  }
  throw new Error("Timed out waiting for page readiness.");
}

async function captureUrl(browserWsUrl, url, outfile, options = {}) {
  const width = options.width || 1400;
  const height = options.height || 900;
  const client = await createPage(browserWsUrl, "about:blank");
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await client.send("Page.navigate", { url });
  await waitForReady(client);
  await evaluate(client, "document.fonts ? document.fonts.ready.then(() => true) : true", true);
  await new Promise((r) => setTimeout(r, options.wait || 600));

  let clip = null;
  if (options.highlightClip) {
    clip = await evaluate(client, `
      (() => {
        const els = Array.from(document.querySelectorAll('[data-codex-highlight]')).filter(el => {
          const r = el.getBoundingClientRect();
          return r.width > 0 && r.height > 0;
        });
        if (!els.length) return null;
        const rects = els.map(el => el.getBoundingClientRect());
        const left = 0;
        const right = Math.min(document.documentElement.scrollWidth, ${width});
        const top = Math.max(0, Math.min(...rects.map(r => r.top)) - 170 + window.scrollY);
        const bottom = Math.max(...rects.map(r => r.bottom)) + 170 + window.scrollY;
        return { x: left, y: top, width: right - left, height: Math.min(1100, Math.max(520, bottom - top)), scale: 1 };
      })()
    `);
  }

  const params = { format: "png", captureBeyondViewport: true, fromSurface: true };
  if (clip) params.clip = clip;
  const shot = await client.send("Page.captureScreenshot", params);
  writeFileSync(outfile, Buffer.from(shot.data, "base64"));
  client.close();
}

async function cmsEvidenceHtml() {
  const sourceUrl = "https://www.cms.gov/newsroom/fact-sheets/fiscal-year-2025-improper-payments-fact-sheet";
  let html = await (await fetch(sourceUrl)).text();
  const style = `<style>
    .codex-source-banner{position:fixed;top:0;left:0;right:0;z-index:999999;background:#10120f;color:#fffaf0;font:700 16px/1.2 Arial,sans-serif;padding:9px 14px}
    .codex-highlight{background:#d7ff5f!important;outline:4px solid #ff8a00!important;outline-offset:2px!important;color:#000!important;font-weight:900!important}
    body{padding-top:42px!important}
  </style>`;
  html = html.replace("</head>", `${style}</head>`);
  html = html.replace("<body", `<body`);
  html = html.replace(/(<body[^>]*>)/, `$1<div class="codex-source-banner">Highlighted CMS source facts used in the infographic</div>`);
  [
    "$28.83 billion",
    "$23.67&nbsp;billion",
    "$4.23&nbsp;billion",
    "$37.39 billion",
    "$1.37 billion",
    "$657.46 million",
  ].forEach((value) => {
    html = html.replace(value, `<span class="codex-highlight" data-codex-highlight="cms">${value}</span>`);
  });
  const file = join(sourceDir, "cms_highlighted_evidence.html");
  writeFileSync(file, html);
  return pathToFileURL(file).href;
}

function fxEvidenceHtml() {
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    body{margin:0;background:#f6f1e8;color:#10120f;font-family:Arial,sans-serif;padding:34px}
    h1{font-size:42px;margin:0 0 18px}.url{font-size:16px;color:#5c6257;margin-bottom:22px}
    table{border-collapse:collapse;width:100%;background:#fffaf0}td,th{border:3px solid #10120f;padding:14px;font-size:24px;text-align:left}
    th{background:#10120f;color:#fffaf0}.hl{background:#d7ff5f;font-weight:900;box-shadow:inset 0 0 0 4px #ff8a00}
  </style></head><body>
    <h1>Highlighted IRS 2025 exchange rates used</h1>
    <div class="url">Source: https://www.irs.gov/individuals/international-taxpayers/yearly-average-currency-exchange-rates</div>
    <table><thead><tr><th>Currency</th><th>2025 yearly average rate, foreign currency per USD</th></tr></thead><tbody>
      <tr><td>Euro</td><td class="hl">0.886</td></tr><tr><td>Danish krone</td><td class="hl">6.617</td></tr>
      <tr><td>Pound sterling</td><td class="hl">0.759</td></tr><tr><td>Japanese yen</td><td class="hl">149.632</td></tr>
      <tr><td>Indian rupee</td><td class="hl">87.133</td></tr>
    </tbody></table>
  </body></html>`;
  const file = join(sourceDir, "irs_fx_highlighted_evidence.html");
  writeFileSync(file, html);
  return pathToFileURL(file).href;
}

const fallbackEvidenceTickers = new Set(["SNY", "NVO", "GSK", "VRTX"]);

function formatReported(value, currency) {
  const abs = Math.abs(value);
  if (abs >= 1e12) return `${currency} ${(value / 1e12).toLocaleString("en-US", { maximumFractionDigits: 2 })} trillion`;
  if (abs >= 1e9) return `${currency} ${(value / 1e9).toLocaleString("en-US", { maximumFractionDigits: 3 })} billion`;
  return `${currency} ${(value / 1e6).toLocaleString("en-US", { maximumFractionDigits: 1 })} million`;
}

function xbrlEvidenceHtml(row) {
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    body{margin:0;background:#f6f1e8;color:#10120f;font-family:Arial,sans-serif;padding:34px}
    h1{font-size:42px;margin:0 0 14px}.url{font-size:17px;color:#5c6257;margin-bottom:22px}
    table{border-collapse:collapse;width:100%;background:#fffaf0}td,th{border:3px solid #10120f;padding:16px;font-size:26px;text-align:left}
    th{background:#10120f;color:#fffaf0}.hl{background:#d7ff5f;font-weight:900;box-shadow:inset 0 0 0 4px #ff8a00}
    .note{font-size:20px;line-height:1.35;max-width:1100px;color:#5c6257;margin-top:18px}
  </style></head><body>
    <h1>${row.company} SEC XBRL facts used</h1>
    <div class="url">SEC filing document: ${row.source_url}<br>SEC companyfacts endpoint: ${row.companyfacts_url}</div>
    <table><thead><tr><th>Fact</th><th>XBRL tag</th><th>Reported value</th><th>Period</th></tr></thead><tbody>
      <tr><td>Revenue</td><td>${row.rev_tag}</td><td class="hl">${formatReported(row.revenue_reported, row.currency)}</td><td>${row.period_start} to ${row.period_end}</td></tr>
      <tr><td>Net income</td><td>${row.ni_tag}</td><td class="hl">${formatReported(row.net_income_reported, row.currency)}</td><td>${row.period_start} to ${row.period_end}</td></tr>
    </tbody></table>
    <p class="note">This card preserves the exact SEC XBRL facts and source links because this filing's SEC-rendered inline document does not produce a readable cropped table in headless screenshot capture.</p>
  </body></html>`;
  const file = join(sourceDir, `${String(row.rank).padStart(2, "0")}_${row.ticker}_xbrl_evidence.html`);
  writeFileSync(file, html);
  return pathToFileURL(file).href;
}

async function main() {
  const data = JSON.parse(readFileSync(join(outDir, "data.json"), "utf8"));
  const chrome = await launchChrome(findChrome());
  try {
    await captureUrl(chrome.browserWsUrl, pathToFileURL(join(outDir, "source_audit_table.html")).href, join(screenshotDir, "00_source_audit_table.png"), { width: 1600, height: 1200 });
    await captureUrl(chrome.browserWsUrl, await cmsEvidenceHtml(), join(screenshotDir, "cms_2025_improper_payments_highlighted.png"), { width: 1400, height: 900, highlightClip: true, wait: 1200 });
    await captureUrl(chrome.browserWsUrl, fxEvidenceHtml(), join(screenshotDir, "irs_2025_fx_rates_highlighted.png"), { width: 1400, height: 760 });
    for (const row of data.rows) {
      const useFallback = fallbackEvidenceTickers.has(row.ticker);
      const url = useFallback ? xbrlEvidenceHtml(row) : pathToFileURL(row.highlighted_filing).href;
      const name = `${String(row.rank).padStart(2, "0")}_${row.ticker}_sec_filing_highlighted.png`;
      await captureUrl(chrome.browserWsUrl, url, join(screenshotDir, name), { width: 1400, height: 900, highlightClip: !useFallback, wait: 800 });
      console.log(`Captured ${name}`);
    }
  } finally {
    chrome.child.kill("SIGTERM");
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
