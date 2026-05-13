#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const runDir = "/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/mash/2026-05-12_1242";
const dateDir = join(runDir, "screenshots/date-verification");
const evidenceDir = join(runDir, "screenshots/evidence");

const sources = [
  {
    ref: 1,
    slug: "madrigal-q1-2026",
    url: "https://ir.madrigalpharma.com/news-releases/news-release-details/madrigal-pharmaceuticals-reports-first-quarter-2026-financial",
    waitFor: "First-quarter 2026 Rezdiffra",
    dateText: "MAY 6, 2026",
    evidence: [
      "First-quarter 2026 Rezdiffra® (resmetirom) net sales of $311.3 million, representing year-over-year growth of 127%",
      "As of March 31, 2026, more than 42,250 patients on Rezdiffra",
      "Advances pipeline with global licensing agreement for a clinical-stage siRNA asset targeting a mutation in the PNPLA3 gene, a genetically validated driver of MASH",
      "MGL-2086 (oral GLP-1) Phase 1 trial on track to initiate in 2Q26; ervogastat/resmetirom drug-drug interaction study on track to initiate in 4Q26",
      "Reports cash, cash equivalents, restricted cash and marketable securities of $817.9 million as of March 31, 2026"
    ]
  },
  {
    ref: 2,
    slug: "nct07581951-hsk31679",
    url: "https://clinicaltrials.gov/study/NCT07581951",
    waitFor: "HSK31679",
    dateText: "Last Update Posted 2026-05-12",
    evidence: [
      "A Phase 3 Study Evaluating the Safety and Efficacy of HSK31679 in Patients With MASH",
      "Sponsor Haisco Pharmaceutical Group Co., Ltd.",
      "Enrollment (Estimated) 400",
      "Phase 3"
    ],
    evidence2: [
      "Drug: HSK31679",
      "Enrollment (Estimated) 400",
      "Study Type Interventional",
      "Phase 3"
    ]
  },
  {
    ref: 3,
    slug: "nct06419374-pegozafermin",
    url: "https://clinicaltrials.gov/study/NCT06419374",
    waitFor: "Pegozafermin",
    dateText: "Last Update Posted 2026-05-06",
    evidence: [
      "A Study to Evaluate the Efficacy and Safety of Pegozafermin in Participants With Compensated Cirrhosis Due to MASH",
      "Sponsor 89bio, Inc.",
      "Enrollment (Estimated) 762",
      "Phase 3"
    ],
    evidence2: [
      "Biological: Pegozafermin",
      "Enrollment (Estimated) 762",
      "Study Type Interventional",
      "Phase 3"
    ]
  },
  {
    ref: 4,
    slug: "nct05519475-aln-hsd",
    url: "https://clinicaltrials.gov/study/NCT05519475",
    waitFor: "ALN-HSD",
    dateText: "Last Update Posted 2026-05-07",
    evidence: [
      "A Precision Medicine Approach Using Gene Silencing to Treat a Chronic Liver Disease Called Metabolic Dysfunction-Associated Steatohepatitis (MASH)",
      "Sponsor Regeneron Pharmaceuticals",
      "Drug: ALN-HSD",
      "Phase 2"
    ],
    evidence2: [
      "Drug: ALN-HSD",
      "Enrollment (Estimated) 120",
      "Study Type Interventional",
      "Phase 2"
    ]
  },
  {
    ref: 5,
    slug: "nct06108219-miricorilant",
    url: "https://clinicaltrials.gov/study/NCT06108219",
    waitFor: "Miricorilant",
    dateText: "Last Update Posted 2026-05-08",
    evidence: [
      "A Phase 2b, Randomized, Double-Blind, Placebo-Controlled Study Evaluating the Efficacy and Safety of Miricorilant in Adult Patients With Nonalcoholic Steatohepatitis/Metabolic Dysfunction-Associated Steatohepatitis (MONARCH)",
      "Sponsor Corcept Therapeutics",
      "Enrollment (Actual) 175",
      "Phase 2"
    ],
    evidence2: [
      "Drug: Miricorilant (Cohort A)",
      "Enrollment (Actual) 175",
      "Study Type Interventional",
      "Phase 2"
    ]
  },
  {
    ref: 6,
    slug: "nct03884075-semaglutide",
    url: "https://clinicaltrials.gov/study/NCT03884075",
    waitFor: "Semaglutide",
    dateText: "Last Update Posted 2026-05-12",
    evidence: [
      "Non-Alcoholic Fatty Liver Disease, the HEpatic Response to Oral Glucose, and the Effect of Semaglutide (NAFLD HEROES)",
      "Sponsor National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK)",
      "Drug: Semaglutide",
      "Phase 2"
    ],
    evidence2: [
      "Drug: Semaglutide",
      "Enrollment (Estimated) 84",
      "Study Type Interventional",
      "Phase 2"
    ]
  },
  {
    ref: 7,
    slug: "nct05370053-elf",
    url: "https://clinicaltrials.gov/study/NCT05370053",
    waitFor: "Enhanced Liver Fibrosis",
    dateText: "Last Update Posted 2026-05-11",
    evidence: [
      "The Availability of the Enhanced Liver Fibrosis (ELF) Test Affects the Rate of Diagnosis of Nonalcoholic Steatohepatitis (NASH) With Fibrosis in Patients Referred to Hepatology",
      "Sponsor University of Kansas Medical Center",
      "Diagnostic Test: ELF Test",
      "Completed"
    ],
    evidence2: [
      "Diagnostic Test: ELF Test",
      "Enrollment (Actual) 450",
      "Study Type Interventional"
    ]
  },
  {
    ref: 8,
    slug: "nct06884293-ibi362",
    url: "https://clinicaltrials.gov/study/NCT06884293",
    waitFor: "IBI362",
    dateText: "Last Update Posted 2026-05-12",
    evidence: [
      "A Study Comparing IBI362 vs Semaglutide in Chinese Overweight or Obese Adults With Metabolic Dysfunction-associated Fatty Liver Disease",
      "Sponsor Innovent Biologics (Suzhou) Co. Ltd.",
      "Enrollment (Actual) 479",
      "Phase 3"
    ],
    evidence2: [
      "Drug: IBI362",
      "Drug: semaglutide",
      "Enrollment (Actual) 479",
      "Phase 3"
    ]
  }
];

function chromeCandidates() {
  return [
    process.env.CHROME_PATH,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser"
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
      "about:blank"
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

    child.once("error", (err) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(err);
      }
    });

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
          const { resolve: done, reject: fail } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) fail(new Error(`${msg.error.message}${msg.error.data ? `: ${msg.error.data}` : ""}`));
          else done(msg.result);
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
    returnByValue: true
  });
  if (result.exceptionDetails) throw new Error(`Evaluation failed: ${result.exceptionDetails.text}`);
  return result.result.value;
}

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForText(client, text) {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    const ready = await evaluate(client, `document.readyState === "complete" && document.body && document.body.innerText.includes(${JSON.stringify(text)})`);
    if (ready) return;
    await delay(250);
  }
  const body = await evaluate(client, "document.body ? document.body.innerText.slice(0, 1000) : ''");
  throw new Error(`Timed out waiting for text "${text}". Body starts: ${body}`);
}

async function preparePage(client) {
  await evaluate(client, `
    (() => {
      document.documentElement.style.scrollBehavior = "auto";
      const style = document.createElement("style");
      style.textContent = [
        "html,body{scrollbar-width:none!important}",
        "html::-webkit-scrollbar,body::-webkit-scrollbar,*::-webkit-scrollbar{display:none!important}",
        ".usa-banner,.site-alert,.cookie,.cookies,.ot-sdk-container,[id*=cookie],[class*=cookie],[class*=Cookie]{display:none!important}",
        "#onetrust-consent-sdk,#onetrust-banner-sdk,.onetrust-pc-dark-filter,.ot-sdk-row,.ot-sdk-container{display:none!important}",
        "#usercentrics-root,[id*=usercentrics],[class*=usercentrics],[data-testid*=uc-]{display:none!important}",
        "body,main,.main-content,.node-release,*{filter:none!important;backdrop-filter:none!important}",
        "[class*=glossary-panel],[id*=glossary],[class*=Glossary]{display:none!important}"
      ].join("");
      document.head.appendChild(style);
      for (const button of Array.from(document.querySelectorAll("button"))) {
        const t = (button.innerText || button.textContent || "").trim().toLowerCase();
        if (["accept", "accept all", "agree", "i agree", "close", "hide glossary"].some((x) => t === x || t.includes(x))) {
          try { button.click(); } catch {}
        }
      }
      return true;
    })()
  `);
}

async function markText(client, snippets) {
  return evaluate(client, `
    (() => {
      const snippets = ${JSON.stringify(snippets)};
      document.querySelectorAll("[data-ci-box]").forEach((el) => el.remove());
      const normalize = (s) => String(s || "").replace(/\\u00a0/g, " ").replace(/\\s+/g, " ").trim();
      const visible = (el) => {
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none";
      };
      const results = [];
      for (const snippet of snippets) {
        const needle = normalize(snippet);
        const candidates = Array.from(document.body.querySelectorAll("body *"))
          .filter((el) => visible(el) && normalize(el.innerText).includes(needle))
          .map((el) => ({ el, rect: el.getBoundingClientRect(), text: normalize(el.innerText) }))
          .sort((a, b) => (a.rect.width * a.rect.height) - (b.rect.width * b.rect.height));
        const chosen = candidates[0];
        if (!chosen) {
          results.push({ snippet, found: false });
          continue;
        }
        const rect = chosen.el.getBoundingClientRect();
        const box = document.createElement("div");
        box.setAttribute("data-ci-box", "true");
        box.style.position = "absolute";
        box.style.left = Math.max(0, rect.left + window.scrollX - 6) + "px";
        box.style.top = Math.max(0, rect.top + window.scrollY - 6) + "px";
        box.style.width = Math.max(12, rect.width + 12) + "px";
        box.style.height = Math.max(12, rect.height + 12) + "px";
        box.style.border = "5px solid #ff3b30";
        box.style.background = "rgba(255, 238, 88, 0.30)";
        box.style.boxShadow = "0 0 0 9999px rgba(255,255,255,0)";
        box.style.pointerEvents = "none";
        box.style.zIndex = "2147483647";
        document.body.appendChild(box);
        chosen.el.setAttribute("data-ci-target", "true");
        results.push({
          snippet,
          found: true,
          text: chosen.text.slice(0, 260),
          y: Math.round(rect.top + window.scrollY)
        });
      }
      const first = document.querySelector("[data-ci-target]");
      if (first) first.scrollIntoView({ block: "center", inline: "nearest" });
      return results;
    })()
  `);
}

async function clearMarks(client) {
  await evaluate(client, `(() => { document.querySelectorAll("[data-ci-box]").forEach((el) => el.remove()); document.querySelectorAll("[data-ci-target]").forEach((el) => el.removeAttribute("data-ci-target")); return true; })()`);
}

async function capture(client, path) {
  await delay(300);
  const shot = await client.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false
  });
  writeFileSync(path, Buffer.from(shot.data, "base64"));
}

async function stopProcess(child) {
  if (!child || child.killed || child.exitCode !== null) return;
  child.kill("SIGTERM");
  await Promise.race([new Promise((resolve) => child.once("exit", resolve)), delay(3000)]);
  if (child.exitCode === null && !child.killed) child.kill("SIGKILL");
}

mkdirSync(dateDir, { recursive: true });
mkdirSync(evidenceDir, { recursive: true });

const chromePath = findChrome();
const userDataDir = mkdtempSync(join(tmpdir(), "mash-ci-chrome-"));
const { child, browserWsUrl } = await launchChrome(chromePath, userDataDir);
const manifest = [];

try {
  for (const source of sources) {
    console.log(`Capturing source ${source.ref}: ${source.slug}`);
    const client = await createPage(browserWsUrl, source.url);
    try {
      await client.send("Page.enable");
      await client.send("Runtime.enable");
      await client.send("Network.enable");
      await client.send("Network.setUserAgentOverride", {
        userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        platform: "macOS"
      });
      await client.send("Emulation.setDeviceMetricsOverride", {
        width: 1600,
        height: 900,
        deviceScaleFactor: 1,
        mobile: false
      });
      await client.send("Page.navigate", { url: source.url });
      await waitForText(client, source.waitFor);
      await preparePage(client);
      await clearMarks(client);
      const dateMarks = await markText(client, [source.dateText]);
      const datePath = join(dateDir, `source-${String(source.ref).padStart(2, "0")}-date.png`);
      await capture(client, datePath);
      await clearMarks(client);
      const evidenceMarks = await markText(client, source.evidence);
      const evidencePath = join(evidenceDir, `source-${String(source.ref).padStart(2, "0")}-evidence-01.png`);
      await capture(client, evidencePath);
      let evidence2Path = null;
      let evidence2Marks = null;
      if (source.evidence2) {
        await clearMarks(client);
        evidence2Marks = await markText(client, source.evidence2);
        evidence2Path = join(evidenceDir, `source-${String(source.ref).padStart(2, "0")}-evidence-02.png`);
        await capture(client, evidence2Path);
      }
      manifest.push({ ...source, datePath, evidencePath, evidence2Path, dateMarks, evidenceMarks, evidence2Marks });
    } finally {
      client.close();
    }
  }
} finally {
  await stopProcess(child);
  rmSync(userDataDir, { recursive: true, force: true });
}

writeFileSync(join(runDir, "sources/capture-manifest.json"), JSON.stringify(manifest, null, 2));
console.log(`Wrote ${manifest.length} source screenshot entries.`);
