import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const sourceHtml = resolve(here, "slovenia_top10_drug_prices.html");
const backgroundPng = resolve(here, "slovenia_top10_drug_prices_background.png");
const printHtml = resolve(here, "slovenia_top10_drug_prices_print.html");
const png = resolve(here, "slovenia_top10_drug_prices.png");
const pdf = resolve(here, "slovenia_top10_drug_prices_text_selectable.pdf");
const pdfRenderPrefix = resolve(here, "slovenia_top10_drug_prices_pdf_render");
const chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const width = 1600;
const height = 2609;

execFileSync("magick", [
  "-size",
  "40x40",
  "xc:#f8f5ee",
  "-fill",
  "#efede7",
  "-draw",
  "rectangle 0,0 0,39",
  "-fill",
  "#f0ede7",
  "-draw",
  "rectangle 0,0 39,0",
  "-fill",
  "#e6e3dd",
  "-draw",
  "point 0,0",
  "-write",
  "mpr:gridtile",
  "+delete",
  "-size",
  `${width}x${height}`,
  "tile:mpr:gridtile",
  backgroundPng,
]);

const original = readFileSync(sourceHtml, "utf8");
const printCss = `

    @page {
      size: ${width}px ${height}px;
      margin: 0;
    }

    html,
    body {
      width: ${width}px;
      min-height: ${height}px;
      background: transparent !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    .page {
      position: relative;
      width: ${width}px;
      height: ${height}px;
      min-height: ${height}px;
      overflow: hidden;
      background: transparent !important;
      isolation: isolate;
    }

    .pdf-bg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      z-index: 0;
      pointer-events: none;
      user-select: none;
    }

    .page > :not(.pdf-bg) {
      position: relative;
      z-index: 1;
    }
`;

const printReady = original
  .replace("</style>", `${printCss}\n  </style>`)
  .replace(
    /(<main class="page"[^>]*>)/,
    `$1\n    <img class="pdf-bg" src="./slovenia_top10_drug_prices_background.png" alt="" aria-hidden="true">`,
  );

writeFileSync(printHtml, printReady);

execFileSync(chrome, [
  "--headless=new",
  "--disable-gpu",
  "--hide-scrollbars",
  `--window-size=${width},${height}`,
  `--screenshot=${png}`,
  pathToFileURL(sourceHtml).href,
]);

execFileSync(chrome, [
  "--headless=new",
  "--disable-gpu",
  "--no-pdf-header-footer",
  `--print-to-pdf=${pdf}`,
  pathToFileURL(printHtml).href,
]);

execFileSync("pdftoppm", [
  "-png",
  "-r",
  "96",
  "-singlefile",
  pdf,
  pdfRenderPrefix,
]);

console.log(printHtml);
console.log(backgroundPng);
console.log(png);
console.log(pdf);
console.log(`${pdfRenderPrefix}.png`);
