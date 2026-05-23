#!/usr/bin/env node
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { tmpdir } from "node:os";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/hepatocellular_carcinoma/2026-05-14_0000";

const sources = [
  {
    ref: 1,
    slug: "create-mt303",
    name: "CREATE Medicines PRNewswire release",
    url: "https://www.prnewswire.com/news-releases/create-medicines-announces-122-million-series-b-financing-to-advance-in-vivo-car-pipeline-in-autoimmune-disease-and-oncology-302771778.html",
    datePhrase: "May 14, 2026",
    evidence: [
      "Early clinical data from the company's MT-303 program in frontline hepatocellular carcinoma",
      "CREATE Medicines is a clinical-stage biotechnology company pioneering in vivo immune programming",
    ],
  },
  {
    ref: 2,
    slug: "rznomics-rmat",
    name: "Rznomics PRNewswire release",
    url: "https://www.prnewswire.com/news-releases/rznomics-announces-us-fda-regenerative-medicine-advanced-therapy-designation-granted-to-rz-001-for-hepatocellular-carcinoma-302766762.html",
    datePhrase: "May 08, 2026",
    evidence: [
      "the U.S. Food and Drug Administration (FDA) has granted Regenerative Medicine Advanced Therapy (RMAT) Designation to RZ-001",
      "RZ-001 previously received Orphan Drug Designation (ODD) in 2024 and Fast Track Designation (FTD) in 2025 for the treatment of HCC",
    ],
  },
  {
    ref: 3,
    slug: "canfite-namodenoson",
    name: "Can-Fite BioPharma SEC Exhibit 99.1",
    url: "https://www.sec.gov/Archives/edgar/data/1536196/000121390026055438/ea029030801ex99-1.htm",
    datePhrase: "May 13, 2026",
    evidence: [
      "Can-Fite’s liver drug, Namodenoson, is being evaluated in a Phase III trial for hepatocellular carcinoma (HCC)",
      "Fast Track Designation as a second line treatment for HCC by the U.S. Food and Drug Administration",
    ],
  },
  {
    ref: 4,
    slug: "coherus-casdozokitug",
    name: "Coherus Oncology SEC Exhibit 99.1",
    url: "https://www.sec.gov/Archives/edgar/data/1512762/000110465926058666/chrs-20260511xex99d1.htm",
    datePhrase: "May 11, 2026",
    evidence: [
      "Patient accrual complete for 1L HCC Phase 2 randomized clinical trial for anti-IL27 casdozokitug",
      "timing for data readouts tracking to projections",
    ],
  },
  {
    ref: 5,
    slug: "tvardi-tti-101",
    name: "Tvardi Therapeutics SEC Exhibit 99.1",
    url: "https://www.sec.gov/Archives/edgar/data/1346830/000110465926057524/tm2613977d1_ex99-1.htm",
    datePhrase: "May 8, 2026",
    evidence: [
      "Topline data from Phase 2 trial of TTI-101 in hepatocellular carcinoma (HCC) on track for 2H 2026",
      "Phase 1b/2 trial remains on track to report topline results in 2H 2026",
    ],
  },
  {
    ref: 6,
    slug: "ctgov-bayer-post-io",
    name: "ClinicalTrials.gov NCT06117891",
    url: "https://clinicaltrials.gov/study/NCT06117891",
    datePhrase: "Last Update Posted 2026-05-12",
    evidence: [
      "An Observational Study in Patients With Unresectable Hepatocellular Carcinoma (uHCC) Following Treatment With Atezolizumab Plus Bevacizumab",
      "Active, not recruiting",
      "Primary Completion (Actual)",
      "Enrollment (Estimated)",
    ],
  },
  {
    ref: 7,
    slug: "ctgov-az-rilvegostomig",
    name: "ClinicalTrials.gov NCT06921785",
    url: "https://clinicaltrials.gov/study/NCT06921785",
    datePhrase: "Last Update Posted 2026-05-11",
    evidence: [
      "A Phase III, Randomised, Open-label, Sponsor-blinded, Multicentre Study of Rilvegostomig in Combination With Bevacizumab With or Without Tremelimumab as First-line Treatment in Patients With Advanced Hepatocellular Carcinoma",
      "Enrollment (Estimated)",
    ],
  },
  {
    ref: 8,
    slug: "ctgov-beone-bgb-b2033",
    name: "ClinicalTrials.gov NCT06427941",
    url: "https://clinicaltrials.gov/study/NCT06427941",
    datePhrase: "Last Update Posted 2026-05-14",
    evidence: [
      "A Phase 1 Study of BGB-B2033, Alone or in Combination With Tislelizumab With or Without Bevacizumab",
      "Metastatic Hepatocellular Carcinoma",
      "Part C (Asia Monotherapy Dose Expansion in HCC)",
      "Part D (US Monotherapy Dose Expansion in HCC)",
      "Enrollment (Estimated)",
    ],
  },
];

function ensureDir(path) {
  mkdirSync(path, { recursive: true });
}

function wait(ms) {
  return new Promise((resolveWait) => setTimeout(resolveWait, ms));
}

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
  }
  throw new Error("Could not find Chrome or Chromium. Set CHROME_PATH to the browser executable.");
}

function launchChrome(chromePath, userDataDir) {
  return new Promise((resolveLaunch, rejectLaunch) => {
    const child = spawn(chromePath, [
      "--headless=new",
      "--disable-gpu",
      "--remote-debugging-port=0",
      `--user-data-dir=${userDataDir}`,
      "about:blank",
    ], { stdio: ["ignore", "ignore", "pipe"] });

    let settled = false;
    let stderr = "";
    const timer = setTimeout(() => {
      if (!settled) {
        child.kill("SIGTERM");
        rejectLaunch(new Error(`Timed out waiting for Chrome DevTools endpoint. ${stderr}`));
      }
    }, 15000);

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match && !settled) {
        settled = true;
        clearTimeout(timer);
        resolveLaunch({ child, browserWsUrl: match[1] });
      }
    });

    child.once("error", (err) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        rejectLaunch(err);
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
    return new Promise((resolveConnect, rejectConnect) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolveConnect();
      this.ws.onerror = () => rejectConnect(new Error(`Could not connect to ${this.wsUrl}`));
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(`${msg.error.message}${msg.error.data ? `: ${msg.error.data}` : ""}`));
          else resolve(msg.result);
        }
      };
    });
  }

  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolveSend, rejectSend) => {
      this.pending.set(id, { resolve: resolveSend, reject: rejectSend });
    });
  }

  close() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.close();
  }
}

async function createPage(browserWsUrl, targetUrl) {
  const browserUrl = new URL(browserWsUrl);
  const httpOrigin = `http://${browserUrl.host}`;
  const response = await fetch(`${httpOrigin}/json/new?${encodeURIComponent("about:blank")}`, { method: "PUT" });
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
  if (result.exceptionDetails) {
    const text = result.exceptionDetails.exception?.description || result.exceptionDetails.text;
    throw new Error(`Evaluation failed: ${text}`);
  }
  return result.result.value;
}

async function waitForReady(client) {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    const ready = await evaluate(client, "document.readyState === 'complete' && !!document.body");
    if (ready) return;
    await wait(150);
  }
  throw new Error("Timed out waiting for document readiness.");
}

async function preparePage(client, url) {
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Network.enable");
  if (new URL(url).hostname.endsWith("sec.gov")) {
    await client.send("Network.setUserAgentOverride", {
      userAgent: "HCC competitive intelligence report contact justinyu@example.com",
    });
  }
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 1000,
    deviceScaleFactor: 1,
    mobile: false,
  });
  const currentUrl = await evaluate(client, "location.href");
  if (currentUrl === "about:blank") {
    await client.send("Page.navigate", { url });
  }
  await waitForReady(client);
  await wait(5500);
  await evaluate(client, `
    (() => {
      if (!document.body) return false;
      document.documentElement.style.scrollBehavior = 'auto';
      const style = document.createElement('style');
      style.textContent = [
        '.ci-highlight{background:#fff16a!important;color:#000!important;box-shadow:0 0 0 3px #f35b04!important;border-radius:2px!important;padding:1px 2px!important;}',
        '.ci-outline{outline:5px solid #f35b04!important;outline-offset:4px!important;background:rgba(255,241,106,.25)!important;}',
        '[role="dialog"],[aria-modal="true"],.ot-sdk-container,.onetrust-pc-dark-filter,.modal,.newsletter,.cookie,.truste_box_overlay,.truste_overlay{display:none!important;visibility:hidden!important;}',
        'body{overflow:visible!important;}'
      ].join('\\n');
      document.head.appendChild(style);
      for (const el of Array.from(document.querySelectorAll('button'))) {
        const text = (el.innerText || el.textContent || '').toLowerCase();
        if (/(accept|agree|close|continue|dismiss|got it)/.test(text) && /(cookie|privacy|consent|close|dismiss|continue|accept|agree|got it)/.test(text)) {
          try { el.click(); } catch {}
        }
      }
      for (const el of Array.from(document.querySelectorAll('iframe'))) {
        const src = String(el.src || '').toLowerCase();
        if (/privacy|consent|cookie|newsletter|adservice|doubleclick/.test(src)) el.remove();
      }
      return true;
    })()
  `);
}

async function markPhrase(client, phrase) {
  return evaluate(client, `
    (() => {
      if (!document.body) return { found: false, phrase: ${JSON.stringify(phrase)}, reason: 'no document body' };
      const phrase = ${JSON.stringify(phrase)};
      const normalize = (value) => String(value || '')
        .replace(/\\u00a0/g, ' ')
        .replace(/[\\u2010-\\u2015]/g, '-')
        .replace(/&amp;/g, '&')
        .replace(/\\s+/g, ' ')
        .trim();
      const wanted = normalize(phrase).toLowerCase();
      for (const el of document.querySelectorAll('.ci-outline')) el.classList.remove('ci-outline');
      for (const mark of Array.from(document.querySelectorAll('mark.ci-highlight'))) {
        mark.replaceWith(document.createTextNode(mark.textContent || ''));
      }
      document.body.normalize();
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
          const text = normalize(node.nodeValue);
          if (!text || !text.toLowerCase().includes(wanted)) return NodeFilter.FILTER_SKIP;
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_SKIP;
          const style = getComputedStyle(parent);
          if (style.display === 'none' || style.visibility === 'hidden') return NodeFilter.FILTER_SKIP;
          return NodeFilter.FILTER_ACCEPT;
        }
      });
      const textNode = walker.nextNode();
      if (textNode) {
        const original = textNode.nodeValue || '';
        const normalizedOriginal = normalize(original).toLowerCase();
        const normalizedPhrase = normalize(phrase).toLowerCase();
        const directIndex = original.toLowerCase().indexOf(phrase.toLowerCase());
        const fallbackIndex = normalizedOriginal.indexOf(normalizedPhrase);
        const index = directIndex >= 0 ? directIndex : fallbackIndex;
        if (index >= 0) {
          const spanLength = directIndex >= 0 ? phrase.length : Math.min(phrase.length, original.length - index);
          const range = document.createRange();
          range.setStart(textNode, index);
          range.setEnd(textNode, Math.min(original.length, index + spanLength));
          const mark = document.createElement('mark');
          mark.className = 'ci-highlight';
          try {
            range.surroundContents(mark);
            mark.scrollIntoView({ block: 'center', inline: 'nearest' });
            const rect = mark.getBoundingClientRect();
            return { found: true, mode: 'mark', text: normalize(mark.textContent), rect: [rect.left, rect.top, rect.width, rect.height] };
          } catch {}
        }
      }
      const candidates = Array.from(document.body.querySelectorAll('h1,h2,h3,h4,p,li,td,th,div,span,a')).filter((el) => {
        const text = normalize(el.innerText || el.textContent);
        if (!text.toLowerCase().includes(wanted)) return false;
        const rect = el.getBoundingClientRect();
        const style = getComputedStyle(el);
        return rect.width > 20 && rect.height > 8 && style.display !== 'none' && style.visibility !== 'hidden';
      }).sort((a, b) => normalize(a.innerText || a.textContent).length - normalize(b.innerText || b.textContent).length);
      const target = candidates[0];
      if (!target) return { found: false, phrase };
      target.classList.add('ci-outline');
      target.scrollIntoView({ block: 'center', inline: 'nearest' });
      const rect = target.getBoundingClientRect();
      return { found: true, mode: 'outline', text: normalize(target.innerText || target.textContent).slice(0, 400), rect: [rect.left, rect.top, rect.width, rect.height] };
    })()
  `);
}

async function screenshot(client, outputPath) {
  await wait(500);
  const image = await client.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  ensureDir(dirname(outputPath));
  writeFileSync(outputPath, Buffer.from(image.data, "base64"));
}

async function stopProcess(child) {
  if (!child || child.killed || child.exitCode !== null) return;
  child.kill("SIGTERM");
  await Promise.race([
    new Promise((resolveStop) => child.once("exit", resolveStop)),
    wait(3000),
  ]);
  if (child.exitCode === null && !child.killed) child.kill("SIGKILL");
}

async function captureSource(source, chrome) {
  const client = await createPage(chrome.browserWsUrl, source.url);
  const outputs = [];
  try {
    await preparePage(client, source.url);
    let result = await markPhrase(client, source.datePhrase);
    if (!result.found) {
      const debugText = await evaluate(client, `JSON.stringify({ title: document.title, url: location.href, text: ((document.body && document.body.innerText) || (document.documentElement && document.documentElement.innerText) || '').slice(0, 1200) })`);
      throw new Error(`Date phrase not found for reference ${source.ref}: ${source.datePhrase}\n${debugText}`);
    }
    const datePath = resolve(runDir, "screenshots/date-verification", `source-${String(source.ref).padStart(2, "0")}-date.png`);
    await screenshot(client, datePath);
    outputs.push({ label: `Reference ${source.ref} - date verification`, path: datePath, caption: `${source.name}: ${source.datePhrase}` });

    for (let index = 0; index < source.evidence.length; index += 1) {
      result = await markPhrase(client, source.evidence[index]);
      if (!result.found) {
        const debugText = await evaluate(client, `JSON.stringify({ title: document.title, url: location.href, text: ((document.body && document.body.innerText) || (document.documentElement && document.documentElement.innerText) || '').slice(0, 1200) })`);
        throw new Error(`Evidence phrase not found for reference ${source.ref}.${index + 1}: ${source.evidence[index]}\n${debugText}`);
      }
      const evidencePath = resolve(runDir, "screenshots/evidence", `source-${String(source.ref).padStart(2, "0")}-evidence-${String(index + 1).padStart(2, "0")}.png`);
      await screenshot(client, evidencePath);
      outputs.push({ label: `Reference ${source.ref} - evidence ${index + 1}`, path: evidencePath, caption: source.evidence[index] });
    }
  } finally {
    client.close();
  }
  return outputs;
}

async function main() {
  const chromePath = findChrome();
  const tempProfile = mkdtempSync(resolve(tmpdir(), "hcc-ci-source-chrome-"));
  const chrome = await launchChrome(chromePath, tempProfile);
  const allItems = [];
  try {
    for (const source of sources) {
      console.log(`Capturing reference ${source.ref}: ${source.name}`);
      const items = await captureSource(source, chrome);
      allItems.push(...items);
    }
  } finally {
    await stopProcess(chrome.child);
    rmSync(tempProfile, { recursive: true, force: true });
  }

  const csv = ["label,path,caption", ...allItems.map((item) => [
    item.label,
    item.path,
    item.caption,
  ].map((value) => `"${String(value).replace(/"/g, '""')}"`).join(","))].join("\n") + "\n";
  writeFileSync(resolve(runDir, "sources/reference-screenshots.csv"), csv);
  writeFileSync(resolve(runDir, "sources/source-capture-metadata.json"), JSON.stringify({ sources, screenshots: allItems }, null, 2));
  console.log(`Saved ${allItems.length} screenshots and manifest rows.`);
}

main().catch((err) => {
  console.error(err.stack || err.message);
  process.exit(1);
});
