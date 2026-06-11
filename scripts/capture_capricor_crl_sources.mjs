#!/usr/bin/env node
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const chromePath = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const outDir = resolve("competitive_intelligence_reports/duchenne_muscular_dystrophy/capricor_deramiocel_crl_2026/screenshots/raw");
mkdirSync(outDir, { recursive: true });

const targets = [
  {
    file: "source-03-capricor-crl-raw.png",
    url: "https://www.capricor.com/investors/news-events/press-releases/detail/319/capricor-therapeutics-provides-regulatory-update-on",
  },
  {
    file: "source-04-capricor-typea-raw.png",
    url: "https://www.capricor.com/investors/news-events/press-releases/detail/326/capricor-therapeutics-provides-regulatory-update-on",
  },
  {
    file: "source-05-fda-multiple-endpoints-raw.png",
    url: "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/multiple-endpoints-clinical-trials",
  },
  {
    file: "source-06-fda-nurown-raw.png",
    url: "https://www.fda.gov/vaccines-blood-biologics/cellular-gene-therapy-products/update-amyotrophic-lateral-sclerosis-als-product-development",
  },
  {
    file: "source-07-biomarin-drisapersen-raw.png",
    url: "https://www.biomarin.com/news/press-releases/fda-issues-complete-response-letter-for-kyndrisatm-for-duchenne-muscular-dystrophy-amenable-to-exon-51-skipping/",
  },
];

function wait(ms) {
  return new Promise((resolveWait) => setTimeout(resolveWait, ms));
}

function launchChrome(userDataDir) {
  return new Promise((resolveLaunch, rejectLaunch) => {
    if (!existsSync(chromePath)) {
      rejectLaunch(new Error(`Chrome not found: ${chromePath}`));
      return;
    }
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
    const timer = setTimeout(() => rejectLaunch(new Error(`Timed out waiting for Chrome. ${stderr}`)), 15000);
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
        if (!msg.id || !this.pending.has(msg.id)) return;
        const { resolve: resolvePending, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message));
        else resolvePending(msg.result);
      };
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolveSend, rejectSend) => {
      this.pending.set(id, { resolve: resolveSend, reject: rejectSend });
    });
  }

  close() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.close();
  }
}

async function createPage(browserWsUrl, url) {
  const endpoint = new URL(browserWsUrl);
  const response = await fetch(`http://${endpoint.host}/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
  if (!response.ok) throw new Error(`Could not create target: ${response.status}`);
  const target = await response.json();
  const client = new CdpClient(target.webSocketDebuggerUrl);
  await client.connect();
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: 1600,
    height: 1200,
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
  for (let i = 0; i < 80; i += 1) {
    if (await evaluate(client, "document.readyState === 'complete'")) return;
    await wait(150);
  }
}

async function cleanPage(client) {
  await evaluate(client, `
    (() => {
      const buttonText = /^(i decline|decline|reject|that's ok|accept|accept all|allow all|agree|save)$/i;
      for (const el of [...document.querySelectorAll('button, a')]) {
        if (buttonText.test((el.textContent || '').trim().toLowerCase())) {
          try { el.click(); } catch {}
        }
      }
      const killerText = /services we would like|enable or disable all services|analytics|marketing|strictly necessary|cookie|consent|privacy/i;
      const isOverlay = (el) => {
        const style = getComputedStyle(el);
        const text = (el.textContent || '').toLowerCase();
        const z = Number.parseInt(style.zIndex || '0', 10);
        return (style.position === 'fixed' || style.position === 'sticky' || z > 1000) && killerText.test(text);
      };
      for (const el of [...document.body.querySelectorAll('*')]) {
        if (isOverlay(el)) el.remove();
      }
      for (const el of [...document.body.children]) {
        const style = getComputedStyle(el);
        const text = (el.textContent || '').toLowerCase();
        const rect = el.getBoundingClientRect();
        const coversViewport = rect.width > innerWidth * 0.75 && rect.height > innerHeight * 0.75;
        if ((style.position === 'fixed' || Number.parseInt(style.zIndex || '0', 10) > 1000) && (killerText.test(text) || coversViewport)) el.remove();
      }
      for (const el of [...document.querySelectorAll('[class*="overlay"], [class*="modal"], [class*="backdrop"], [id*="overlay"], [id*="modal"], [id*="backdrop"]')]) {
        const rect = el.getBoundingClientRect();
        if (rect.width > innerWidth * 0.5 || rect.height > innerHeight * 0.5) el.remove();
      }
      document.documentElement.style.filter = 'none';
      document.body.style.filter = 'none';
      document.body.style.opacity = '1';
      document.documentElement.className = document.documentElement.className
        .split(/\s+/).filter((name) => !/modal|overlay|cookie|consent|privacy/i.test(name)).join(' ');
      document.body.className = document.body.className
        .split(/\s+/).filter((name) => !/modal|overlay|cookie|consent|privacy/i.test(name)).join(' ');
      for (const el of [...document.body.querySelectorAll('*')]) {
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        const fixedBackdrop = style.position === 'fixed' &&
          rect.left <= 5 && rect.top <= 5 &&
          rect.width >= innerWidth * 0.8 && rect.height >= innerHeight * 0.8 &&
          (Number.parseFloat(style.opacity || '1') < 0.95 || /rgba\\(0, 0, 0|rgb\\(0, 0, 0/i.test(style.backgroundColor));
        if (fixedBackdrop) el.remove();
      }
      document.body.style.overflow = 'auto';
      return true;
    })()
  `);
}

async function capture(client, file) {
  try {
    await cleanPage(client);
  } catch {
    // Some pages throw during DOM cleanup; keep capture best-effort rather than losing evidence.
  }
  await wait(500);
  const image = await client.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  const outputPath = resolve(outDir, file);
  mkdirSync(dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, Buffer.from(image.data, "base64"));
  return outputPath;
}

async function main() {
  const tempProfile = mkdtempSync(resolve(tmpdir(), "capricor-source-capture-"));
  let chrome;
  const clients = [];
  try {
    chrome = await launchChrome(tempProfile);
    for (const target of targets) {
      const client = await createPage(chrome.browserWsUrl, target.url);
      clients.push(client);
      await waitForReady(client);
      await wait(2000);
      const output = await capture(client, target.file);
      console.log(`${target.file} -> ${output}`);
    }
  } finally {
    for (const client of clients) client.close();
    if (chrome?.child) chrome.child.kill("SIGTERM");
    await wait(500);
    rmSync(tempProfile, { recursive: true, force: true });
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
