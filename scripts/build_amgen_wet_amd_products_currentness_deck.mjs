import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const runDate = "May 26, 2026";
const runDateSlug = "05.26.26";
const reportSlug = "amgen_wet_amd_products_website_currentness_audit";
const runFolder = path.join(
  repoRoot,
  "competitive_intelligence_reports",
  reportSlug,
  "2026-05-26_website_currentness",
);

const dirs = {
  assets: path.join(runFolder, "assets"),
  evidence: path.join(runFolder, "screenshots", "evidence"),
  browserExport: path.join(runFolder, "screenshots", "browser-export"),
  renderReview: path.join(runFolder, "screenshots", "render-review"),
  sources: path.join(runFolder, "sources"),
};

for (const dir of Object.values(dirs)) fs.mkdirSync(dir, { recursive: true });

const outputFiles = {
  reportHtml: path.join(runFolder, "report.html"),
  reportPdf: path.join(runFolder, `${reportSlug}-ci-report-${runDateSlug}.pdf`),
  screenshotPdf: path.join(runFolder, `${reportSlug}-ci-screenshots-${runDateSlug}.pdf`),
  sourceLog: path.join(dirs.sources, "source-log.md"),
  screenshotManifest: path.join(dirs.sources, "reference-screenshots.csv"),
};

const skillRoot = path.join(repoRoot, "_skills_to_install", "cohere-style-ci");
const exporterScript = path.join(skillRoot, "scripts", "export_html_slides_pdf.mjs");
const screenshotAssemblerScript = path.join(skillRoot, "scripts", "assemble_reference_screenshots_pdf.py");
const chromePath = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";

const backgroundCandidates = [
  path.join(skillRoot, "assets", "tan_slide_background.png"),
  path.join(repoRoot, "outputs", "wet_amd_terminology_comparison", "tan_slide_background.png"),
  path.join(repoRoot, "competitive_intelligence_reports", "ocular_therapeutix_web_discrepancy_audit", "2026-05-26_website_currentness", "assets", "tan_slide_background.png"),
];
const backgroundSource = backgroundCandidates.find((candidate) => fs.existsSync(candidate));
if (backgroundSource) fs.copyFileSync(backgroundSource, path.join(dirs.assets, "tan_slide_background.png"));

const dailymedUrl = "https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c61062f3-80ec-4a20-8c28-46e468592a06&version=9";
const references = [
  {
    ref: 1,
    title: "PAVBLU website: wet AMD indication is listed",
    source: "PAVBLU safety page",
    url: "https://www.pavblu.com/safety-efficacy",
    owner: "Live website page / Amgen",
    evidence: "Wet AMD indication statement on the PAVBLU website.",
    screenshot: "screenshots/evidence/source-01-pavblu-website-indication.png",
  },
  {
    ref: 2,
    title: "DailyMed current label: PAVBLU wet AMD indication and May 2026 update",
    source: "DailyMed PAVBLU label",
    url: dailymedUrl,
    owner: "Updated May 10, 2026 / NLM DailyMed",
    evidence: "Current label update date and wet AMD indication.",
    screenshot: "screenshots/evidence/source-02-dailymed-current-indication.png",
  },
  {
    ref: 3,
    title: "PAVBLU website: wet AMD dosing language is listed",
    source: "PAVBLU dosing page",
    url: "https://www.pavblu.com/dosing",
    owner: "Live website page / Amgen",
    evidence: "Next scheduled aflibercept-dose positioning statement.",
    screenshot: "screenshots/evidence/source-03-pavblu-website-dosing.png",
  },
  {
    ref: 4,
    title: "DailyMed current label: wet AMD dosing regimen",
    source: "DailyMed PAVBLU label",
    url: dailymedUrl,
    owner: "Revised 4/2026 / NLM DailyMed",
    evidence: "Wet AMD dosing schedule in the current label.",
    screenshot: "screenshots/evidence/source-04-dailymed-current-dosing.png",
  },
  {
    ref: 5,
    title: "PAVBLU safety page: reference list cites 2024 prescribing information",
    source: "PAVBLU safety page",
    url: "https://www.pavblu.com/safety-efficacy",
    owner: "Live website reference list / Amgen",
    evidence: "Visible 2024 prescribing-information reference and 2025 access-date language.",
    screenshot: "screenshots/evidence/source-05-pavblu-safety-references-2024.png",
  },
  {
    ref: 6,
    title: "DailyMed current label: revised April 2026",
    source: "DailyMed PAVBLU label",
    url: dailymedUrl,
    owner: "Revised 4/2026 / NLM DailyMed",
    evidence: "Current label revision date and biosimilar statement.",
    screenshot: "screenshots/evidence/source-06-dailymed-revised-2026.png",
  },
];

function runCommand(label, command, args, options = {}) {
  console.log(`${label}: ${command} ${args.join(" ")}`);
  const result = spawnSync(command, args, {
    cwd: options.cwd || repoRoot,
    encoding: "utf8",
    env: { ...process.env, CHROME_PATH: chromePath, ...(options.env || {}) },
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.status !== 0) throw new Error(`${label} failed with exit code ${result.status ?? "unknown"}`);
  return result;
}

function writeSourceArtifacts() {
  const sourceLog = `# Amgen Wet AMD Products Website Currentness Audit Source Log

Scope: Web-only currentness review of Amgen public PAVBLU pages related to wet AMD against the current online PAVBLU label. Normal source lag was not treated as a currentness finding unless the website itself presented dated or internally inconsistent current information.

## Included References

${references.map((reference) => `${reference.ref}. ${reference.title}
   - URL: ${reference.url}
   - Screenshot: ${reference.screenshot}
   - Highlight status: text highlighted in rendered browser screenshot`).join("\n\n")}
`;
  fs.writeFileSync(outputFiles.sourceLog, sourceLog);

  const rows = ["label,path,caption"];
  for (const reference of references) {
    rows.push([
      JSON.stringify(`Reference ${reference.ref} - evidence`),
      JSON.stringify(reference.screenshot),
      JSON.stringify(reference.title),
    ].join(","));
  }
  fs.writeFileSync(outputFiles.screenshotManifest, rows.join("\n") + "\n");
}

function normalizeReportHtml() {
  if (!fs.existsSync(outputFiles.reportHtml)) {
    throw new Error(`Expected existing report HTML at ${outputFiles.reportHtml}`);
  }
  const html = fs.readFileSync(outputFiles.reportHtml, "utf8");
  const slideCount = (html.match(/<article class="slide/g) || []).length;
  if (slideCount !== 4) throw new Error(`Expected 4 slides, found ${slideCount}`);
  for (const marker of ["1/4", "2/4", "3/4", "4/4", "References 1-6"]) {
    if (!html.includes(marker)) throw new Error(`Expected marker missing from report HTML: ${marker}`);
  }
  const disallowed = [
    /Reference\s+[7-9]/i,
    /References\s+1-[7-9]/i,
    /<a[^>]*>\s*[7-9]\s*<\/a>/i,
    /[1-5]\/5/,
  ];
  for (const pattern of disallowed) {
    if (pattern.test(html)) throw new Error(`Removed or stale report content still present: ${pattern}`);
  }
}

function removeStaleArtifacts() {
  for (const folder of [dirs.evidence, dirs.browserExport]) {
    if (!fs.existsSync(folder)) continue;
    for (const entry of fs.readdirSync(folder)) {
      const evidenceMatch = entry.match(/^source-(\d{2})-/);
      const slideMatch = entry.match(/^slide_(\d{2})\.png$/);
      const isPrunedEvidence = evidenceMatch && Number(evidenceMatch[1]) > 6;
      const isPrunedSlide = slideMatch && Number(slideMatch[1]) > 4;
      if (isPrunedEvidence || isPrunedSlide || entry === "contact_sheet.png") {
        fs.rmSync(path.join(folder, entry), { force: true });
      }
    }
  }
}

function exportReportPdf() {
  runCommand("Export report PDF", process.execPath, [
    exporterScript,
    "--input", outputFiles.reportHtml,
    "--output", outputFiles.reportPdf,
    "--screenshots-dir", dirs.browserExport,
    "--render-check-dir", dirs.renderReview,
    "--chrome", chromePath,
  ]);
}

function assembleScreenshotPdf() {
  runCommand("Assemble reference screenshots PDF", "python", [
    screenshotAssemblerScript,
    "--output", outputFiles.screenshotPdf,
    "--manifest", outputFiles.screenshotManifest,
  ], { cwd: runFolder });
}

function writeContactSheet() {
  const py = `
from pathlib import Path
from PIL import Image, ImageDraw
folder = Path(r"${dirs.browserExport.replaceAll("\\", "\\\\")}")
slides = [folder / f"slide_{i:02d}.png" for i in range(1, 5)]
if not all(path.exists() for path in slides):
    raise SystemExit("missing slide screenshot for contact sheet")
thumb_w, thumb_h = 520, 293
margin = 24
label_h = 28
out = Image.new("RGB", (margin * 3 + thumb_w * 2, margin * 3 + (thumb_h + label_h) * 2), "#f6f1e8")
draw = ImageDraw.Draw(out)
for idx, path in enumerate(slides):
    img = Image.open(path).convert("RGB")
    img.thumbnail((thumb_w, thumb_h))
    x = margin + (idx % 2) * (thumb_w + margin)
    y = margin + (idx // 2) * (thumb_h + label_h + margin)
    draw.text((x, y), f"Slide {idx + 1}/4", fill="#10120f")
    out.paste(img, (x, y + label_h))
out.save(folder / "contact_sheet.png")
`;
  runCommand("Write browser-export contact sheet", "python", ["-c", py]);
}

function assertCurrentState() {
  const html = fs.readFileSync(outputFiles.reportHtml, "utf8");
  const sourceLog = fs.readFileSync(outputFiles.sourceLog, "utf8");
  const manifest = fs.readFileSync(outputFiles.screenshotManifest, "utf8");
  const combined = `${html}\n${sourceLog}\n${manifest}`;
  const disallowed = [
    /Reference\s+[7-9]/i,
    /References\s+1-[7-9]/i,
    /source-0[7-9]/i,
    /<a[^>]*>\s*[7-9]\s*<\/a>/i,
    /[1-5]\/5/,
  ];
  for (const pattern of disallowed) {
    if (pattern.test(combined)) throw new Error(`Removed or stale content still present: ${pattern}`);
  }
  for (const marker of ["1/4", "2/4", "3/4", "4/4", "References 1-6"]) {
    if (!html.includes(marker)) throw new Error(`Expected marker missing from report HTML: ${marker}`);
  }
  const slideCount = (html.match(/<article class="slide/g) || []).length;
  if (slideCount !== 4) throw new Error(`Expected 4 slides, found ${slideCount}`);
}

function main() {
  const skipPdf = process.argv.includes("--skip-pdf");
  writeSourceArtifacts();
  normalizeReportHtml();
  removeStaleArtifacts();
  if (!skipPdf) {
    exportReportPdf();
    assembleScreenshotPdf();
    writeContactSheet();
  }
  assertCurrentState();
  console.log(JSON.stringify({
    runDate,
    runFolder,
    reportHtml: outputFiles.reportHtml,
    reportPdf: skipPdf ? "not exported" : outputFiles.reportPdf,
    screenshotPdf: skipPdf ? "not exported" : outputFiles.screenshotPdf,
    sourceLog: outputFiles.sourceLog,
    screenshotManifest: outputFiles.screenshotManifest,
    slideCount: 4,
    references: references.map((reference) => reference.ref),
  }, null, 2));
}

main();
