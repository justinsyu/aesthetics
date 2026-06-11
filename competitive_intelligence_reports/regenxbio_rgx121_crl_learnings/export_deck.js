const fs = require("fs");
const path = require("path");

let chromium;
try {
  ({ chromium } = require("playwright"));
} catch {
  const npxCache = path.join(process.env.LOCALAPPDATA || "", "npm-cache", "_npx");
  const candidates = fs.existsSync(npxCache)
    ? fs.readdirSync(npxCache).map((name) => path.join(npxCache, name, "node_modules", "playwright"))
    : [];
  const playwrightPath = candidates.find((candidate) => fs.existsSync(path.join(candidate, "index.js")));
  if (!playwrightPath) throw new Error("Could not locate Playwright module");
  ({ chromium } = require(playwrightPath));
}

const root = __dirname;
const report = path.join(root, "report.html");
const exportsDir = path.join(root, "exports");
fs.mkdirSync(exportsDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
  await page.goto(`file://${report.replace(/\\/g, "/")}`, { waitUntil: "networkidle" });
  const pdfPath = path.join(exportsDir, "regenxbio-rgx121-crl-learnings.pdf");
  await page.pdf({
    path: pdfPath,
    width: "1600px",
    height: "900px",
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: "0px", right: "0px", bottom: "0px", left: "0px" },
  });
  const slides = await page.locator(".slide").count();
  const overflow = await page.evaluate(() =>
    Array.from(document.querySelectorAll(".slide"))
      .map((slide, i) => ({
        slide: i + 1,
        overflowX: slide.scrollWidth > slide.clientWidth + 1,
        overflowY: slide.scrollHeight > slide.clientHeight + 1,
        scrollWidth: slide.scrollWidth,
        clientWidth: slide.clientWidth,
        scrollHeight: slide.scrollHeight,
        clientHeight: slide.clientHeight,
      }))
      .filter((item) => item.overflowX || item.overflowY)
  );
  fs.writeFileSync(path.join(exportsDir, "render-check.json"), JSON.stringify({ slides, overflow }, null, 2), "utf8");
  await browser.close();
  if (overflow.length) {
    console.error(JSON.stringify(overflow, null, 2));
    process.exitCode = 1;
  } else {
    console.log(`Exported ${slides} slides without detected overflow: ${pdfPath}`);
  }
})();
