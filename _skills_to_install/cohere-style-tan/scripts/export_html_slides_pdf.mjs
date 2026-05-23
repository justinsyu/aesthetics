#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const DEFAULT_WIDTH = 1600;
const DEFAULT_HEIGHT = 900;

function parseArgs(argv) {
  const args = {
    width: DEFAULT_WIDTH,
    height: DEFAULT_HEIGHT,
    mode: "print",
    allowOverflow: false,
    selector: ".slide",
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--allow-overflow") {
      args.allowOverflow = true;
      continue;
    }
    if (!arg.startsWith("--")) throw new Error(`Unexpected argument: ${arg}`);
    const key = arg.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${arg}`);
    args[key] = value;
    i += 1;
  }
  if (!args.input || !args.output) {
    throw new Error("Usage: export_html_slides_pdf.mjs --input slides.html --output slides.pdf [--mode print|raster] [--selector .slide|.sheet] [--screenshots-dir dir] [--render-check-dir dir]");
  }
  if (!["print", "raster"].includes(args.mode)) throw new Error("--mode must be either print or raster.");
  args.width = Number(args.width);
  args.height = Number(args.height);
  if (!Number.isFinite(args.width) || !Number.isFinite(args.height)) throw new Error("Width and height must be numbers.");
  return args;
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

function findChrome(explicitPath) {
  const candidates = explicitPath ? [explicitPath, ...chromeCandidates()] : chromeCandidates();
  for (const candidate of candidates) {
    if (candidate.includes("/") && existsSync(candidate)) return candidate;
    if (!candidate.includes("/")) {
      const found = spawnSync("which", [candidate], { encoding: "utf8" });
      if (found.status === 0 && found.stdout.trim()) return found.stdout.trim();
    }
  }
  throw new Error("Could not find Chrome or Chromium. Set CHROME_PATH to the browser executable.");
}

function launchChrome(chromePath, userDataDir) {
  return new Promise((resolveLaunch, rejectLaunch) => {
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

    child.once("exit", (code) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        rejectLaunch(new Error(`Chrome exited before DevTools was ready with code ${code}. ${stderr}`));
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
    returnByValue: true,
  });
  if (result.exceptionDetails) throw new Error(`Evaluation failed: ${result.exceptionDetails.text}`);
  return result.result.value;
}

async function wait(ms) {
  return new Promise((resolveWait) => setTimeout(resolveWait, ms));
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

async function removeDirWithRetry(path) {
  for (let attempt = 0; attempt < 5; attempt += 1) {
    try {
      rmSync(path, { recursive: true, force: true });
      return;
    } catch (err) {
      if (attempt === 4) throw err;
      await wait(200 * (attempt + 1));
    }
  }
}

async function waitForReady(client) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    const ready = await evaluate(client, "document.readyState === 'complete'");
    if (ready) return;
    await wait(150);
  }
  throw new Error("Timed out waiting for document readiness.");
}

async function captureSlides(client, args, screenshotsDir, targetUrl) {
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: args.width,
    height: args.height,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await client.send("Emulation.setEmulatedMedia", { media: "screen" });
  await client.send("Page.navigate", { url: targetUrl });
  await waitForReady(client);
  await evaluate(client, "document.fonts ? document.fonts.ready.then(() => true) : true", true);
  await evaluate(client, `
    (() => {
      document.documentElement.style.scrollBehavior = 'auto';
      const style = document.createElement('style');
      style.textContent = 'html,body{scrollbar-width:none!important}html::-webkit-scrollbar,body::-webkit-scrollbar{display:none!important}*{scrollbar-width:none!important}*::-webkit-scrollbar{display:none!important}';
      document.head.appendChild(style);
      return true;
    })()
  `);

  const selectorLiteral = JSON.stringify(args.selector);
  const slideCount = await evaluate(client, `document.querySelectorAll(${selectorLiteral}).length`);
  if (!slideCount) throw new Error(`No elements matching ${args.selector} were found.`);

  mkdirSync(screenshotsDir, { recursive: true });
  const screenshots = [];
  const overflow = [];

  for (let index = 0; index < slideCount; index += 1) {
    const info = await evaluate(client, `
      (() => {
        const slide = document.querySelectorAll(${selectorLiteral})[${index}];
        window.scrollTo(0, slide.offsetTop);
        const sr = slide.getBoundingClientRect();
        const offenders = Array.from(slide.querySelectorAll('*')).filter((el) => {
          const r = el.getBoundingClientRect();
          if (r.width < 1 && r.height < 1) return false;
          return r.left < sr.left - 1 || r.top < sr.top - 1 || r.right > sr.right + 1 || r.bottom > sr.bottom + 1;
        }).slice(0, 8).map((el) => {
          const r = el.getBoundingClientRect();
          return {
            tag: el.tagName.toLowerCase(),
            className: String(el.className || ''),
            text: (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 80),
            rect: [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]
          };
        });
        return {
          label: slide.getAttribute('aria-label') || slide.id || 'slide ${index + 1}',
          scrollOverflowY: slide.scrollHeight - slide.clientHeight,
          scrollOverflowX: slide.scrollWidth - slide.clientWidth,
          offenders
        };
      })()
    `);
    await wait(120);
    const hasScrollOverflow = args.selector === ".slide" && (info.scrollOverflowY > 2 || info.scrollOverflowX > 2);
    if (hasScrollOverflow || info.offenders.length) {
      overflow.push({ slide: index + 1, ...info });
    }
    const metrics = await evaluate(client, `
      (() => {
        const page = document.querySelectorAll(${selectorLiteral})[${index}];
        const r = page.getBoundingClientRect();
        return {
          x: Math.max(0, Math.floor(r.left + window.scrollX)),
          y: Math.max(0, Math.floor(r.top + window.scrollY)),
          width: Math.ceil(r.width),
          height: Math.ceil(r.height)
        };
      })()
    `);
    const useElementClip = metrics.height > args.height || metrics.width > args.width || args.selector !== ".slide";
    const image = await client.send("Page.captureScreenshot", {
      format: "png",
      fromSurface: true,
      captureBeyondViewport: useElementClip,
      ...(useElementClip ? {
        clip: {
          x: metrics.x,
          y: metrics.y,
          width: metrics.width,
          height: metrics.height,
          scale: 1,
        },
      } : {}),
    });
    const imagePath = resolve(screenshotsDir, `slide_${String(index + 1).padStart(2, "0")}.png`);
    writeFileSync(imagePath, Buffer.from(image.data, "base64"));
    screenshots.push({ path: imagePath, width: metrics.width, height: metrics.height });
  }

  if (overflow.length && !args.allowOverflow) {
    throw new Error(`Detected possible slide overflow:\n${JSON.stringify(overflow, null, 2)}\nUse --allow-overflow only after visually confirming the overflow is intentional.`);
  }

  return { slideCount, screenshots, overflow };
}

function assemblePdf(screenshots, outputPath, width, height) {
  mkdirSync(dirname(outputPath), { recursive: true });
  const py = `
import sys, zlib
from pathlib import Path
from PIL import Image

output = Path(sys.argv[1])
image_paths = [Path(p) for p in sys.argv[2:]]

def pdf_obj(n, data):
    if isinstance(data, str):
        data = data.encode('ascii')
    return f"{n} 0 obj\\n".encode('ascii') + data + b"\\nendobj\\n"

def make_pdf(objects):
    parts = [b"%PDF-1.4\\n%\\xe2\\xe3\\xcf\\xd3\\n"]
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(sum(len(p) for p in parts))
        parts.append(pdf_obj(i, obj))
    xref = sum(len(p) for p in parts)
    parts.append(f"xref\\n0 {len(objects)+1}\\n".encode('ascii'))
    parts.append(b"0000000000 65535 f \\n")
    for off in offsets[1:]:
        parts.append(f"{off:010d} 00000 n \\n".encode('ascii'))
    parts.append(f"trailer\\n<< /Size {len(objects)+1} /Root 1 0 R >>\\nstartxref\\n{xref}\\n%%EOF\\n".encode('ascii'))
    output.write_bytes(b"".join(parts))

pages = []
images = []
contents = []
kids = []
count = len(image_paths)

for idx, path in enumerate(image_paths):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    page_w = w * 0.75
    page_h = h * 0.75
    raw = zlib.compress(im.tobytes(), 9)
    page_obj = 3 + idx
    image_obj = 3 + count + idx
    content_obj = 3 + (2 * count) + idx
    kids.append(f"{page_obj} 0 R")
    pages.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w:.6f} {page_h:.6f}] /Resources << /XObject << /Im0 {image_obj} 0 R >> >> /Contents {content_obj} 0 R >>")
    images.append(
        f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(raw)} >>\\nstream\\n".encode('ascii')
        + raw
        + b"\\nendstream"
    )
    content = f"q\\n{page_w:.6f} 0 0 {page_h:.6f} 0 0 cm\\n/Im0 Do\\nQ\\n".encode('ascii')
    contents.append(f"<< /Length {len(content)} >>\\nstream\\n".encode('ascii') + content + b"endstream")

objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {count} >>",
    *pages,
    *images,
    *contents,
]
make_pdf(objects)
`;
  const imagePaths = screenshots.map((item) => item.path);
  const result = spawnSync("python3", ["-", outputPath, ...imagePaths], {
    input: py,
    encoding: "utf8",
  });
  if (result.status !== 0) {
    throw new Error(`Lossless raster PDF assembly failed. Ensure Pillow is installed.\n${result.stderr || result.stdout}`);
  }
}

async function printHtmlPdf(client, outputPath, width, height) {
  mkdirSync(dirname(outputPath), { recursive: true });
  await client.send("Emulation.setEmulatedMedia", { media: "print" });
  await evaluate(client, "window.scrollTo(0, 0); true");
  await wait(150);
  const pdf = await client.send("Page.printToPDF", {
    printBackground: true,
    preferCSSPageSize: true,
    landscape: true,
    paperWidth: width / 96,
    paperHeight: height / 96,
    marginTop: 0,
    marginRight: 0,
    marginBottom: 0,
    marginLeft: 0,
    scale: 1,
    transferMode: "ReturnAsBase64",
  });
  writeFileSync(outputPath, Buffer.from(pdf.data, "base64"));
}

function renderCheck(outputPath, renderCheckDir) {
  if (!renderCheckDir) return { skipped: true, reason: "No render-check directory requested." };
  const which = spawnSync("which", ["pdftoppm"], { encoding: "utf8" });
  if (which.status !== 0) return { skipped: true, reason: "pdftoppm not found." };
  mkdirSync(renderCheckDir, { recursive: true });
  const prefix = resolve(renderCheckDir, basename(outputPath, ".pdf"));
  const result = spawnSync("pdftoppm", ["-png", "-r", "96", outputPath, prefix], { encoding: "utf8" });
  if (result.status !== 0) return { skipped: true, reason: result.stderr || result.stdout || "pdftoppm failed." };
  return { skipped: false, prefix };
}

function inspectPdf(outputPath) {
  const text = spawnSync("pdftotext", [outputPath, "-"], { encoding: "utf8" });
  const textLength = text.status === 0 ? text.stdout.replace(/\s+/g, "").length : null;
  const py = `
import json, sys
from pypdf import PdfReader
reader = PdfReader(sys.argv[1])
links = 0
for page in reader.pages:
    for annot in page.get('/Annots') or []:
        obj = annot.get_object()
        action = obj.get('/A')
        if action and action.get('/URI'):
            links += 1
print(json.dumps({'pages': len(reader.pages), 'uriLinks': links}))
`;
  const links = spawnSync("python3", ["-", outputPath], { input: py, encoding: "utf8" });
  let annotationInfo = null;
  if (links.status === 0 && links.stdout.trim()) annotationInfo = JSON.parse(links.stdout);
  return { textLength, ...annotationInfo };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const inputPath = resolve(args.input);
  const outputPath = resolve(args.output);
  if (!existsSync(inputPath)) throw new Error(`Input not found: ${inputPath}`);

  const screenshotsDir = resolve(args.screenshotsDir || `${outputPath.replace(/\\.pdf$/i, "")}-screenshots`);
  const tempProfile = mkdtempSync(resolve(tmpdir(), "cohere-style-chrome-"));
  const chromePath = findChrome(args.chrome);
  const targetUrl = pathToFileURL(inputPath).href;

  let chrome;
  let client;
  try {
    chrome = await launchChrome(chromePath, tempProfile);
    client = await createPage(chrome.browserWsUrl, targetUrl);
    const capture = await captureSlides(client, args, screenshotsDir, targetUrl);
    if (args.mode === "raster") {
      assemblePdf(capture.screenshots, outputPath, args.width, args.height);
    } else {
      await printHtmlPdf(client, outputPath, args.width, args.height);
    }
    const check = renderCheck(outputPath, args.renderCheckDir ? resolve(args.renderCheckDir) : null);
    const pdfInspection = inspectPdf(outputPath);
    console.log(JSON.stringify({
      input: inputPath,
      output: outputPath,
      mode: args.mode,
      slideCount: capture.slideCount,
      screenshotsDir,
      renderCheck: check,
      pdfInspection,
      overflowWarnings: capture.overflow,
    }, null, 2));
  } finally {
    if (client) client.close();
    if (chrome?.child) await stopProcess(chrome.child);
    await removeDirWithRetry(tempProfile);
  }
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
