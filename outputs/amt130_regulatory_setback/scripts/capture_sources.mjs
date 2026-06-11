import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';
import sharp from 'sharp';

const outDir = path.resolve('screenshots');
const chromePath = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const localPdf = (file, hash = '') => `file:///${path.resolve('sources', file).replaceAll('\\', '/')}${hash}`;

const sources = [
  {
    id: 's01_uniqure_prior_alignment',
    kind: 'web',
    title: 'uniQure June 2025: planned BLA path',
    url: 'https://www.globenewswire.com/news-release/2025/06/02/3091732/0/en/uniqure-provides-regulatory-update-on-amt-130-for-huntington-s-disease.html',
    snippets: [
      'Alignment with FDA continues to support Accelerated Approval pathway',
      'BLA submission planned for first quarter of 2026',
      'The FDA agreed that the primary efficacy analysis for the BLA will evaluate the 3-year change in cUHDRS'
    ]
  },
  {
    id: 's02_uniqure_dec_reversal',
    kind: 'pdf',
    title: 'uniQure December 2025: pre-BLA minutes reversal',
    url: localPdf('uniqure_dec2025_amt130.pdf', '#page=1'),
    manualBox: { x: 510, y: 252, width: 700, height: 112 }
  },
  {
    id: 's03_uniqure_type_a_minutes',
    kind: 'web',
    title: 'uniQure March 2026: Type A minutes and sham-control recommendation',
    url: 'https://www.globenewswire.com/news-release/2026/03/02/3247236/0/en/uniqure-provides-regulatory-update-on-amt-130-for-huntington-s-disease.html',
    snippets: [
      'FDA stated it cannot agree that data from the Phase I/II studies, compared to an external control, are sufficient',
      'The FDA strongly recommended the Company conduct a prospective, randomized, double-blind, sham surgery-controlled study'
    ],
    manualBox: { x: 226, y: 572, width: 810, height: 350 }
  },
  {
    id: 's04_fda_external_controls',
    kind: 'web',
    title: 'FDA external-control guidance',
    url: 'https://www.fda.gov/regulatory-information/search-fda-guidance-documents/considerations-design-and-conduct-externally-controlled-trials-drug-and-biological-products',
    snippets: [
      'externally controlled clinical trials to provide evidence of the safety and effectiveness',
      'outcomes in participants receiving the test treatment according to a protocol are compared to outcomes in a group of people external to the trial'
    ]
  },
  {
    id: 's05_pierre_fabre_tabelecleucel',
    kind: 'pdf',
    title: 'Pierre Fabre January 2026: tabelecleucel CRL',
    url: localPdf('pierre_fabre_tabelecleucel_crl_20260112.pdf', '#page=1'),
    manualBox: { x: 545, y: 498, width: 690, height: 190 }
  },
  {
    id: 's06_replimune_rp1',
    kind: 'web',
    title: 'Replimune April 2026: RP1 CRL and single-arm risk',
    url: 'https://www.globenewswire.com/news-release/2026/04/10/3272063/0/en/Replimune-Receives-Complete-Response-Letter-from-the-FDA-for-RP1-Biologics-License-Application-for-the-Treatment-of-Advanced-Melanoma.html',
    snippets: [
      'if the data was sufficiently compelling, a single arm trial could be acceptable',
      'we do not object to your proposal to submit a BLA based primarily on data from the cohort'
    ]
  },
  {
    id: 's07_regeneron_odronextamab',
    kind: 'web',
    title: 'Regeneron March 2024: confirmatory trial status CRLs',
    url: 'https://www.globenewswire.com/news-release/2024/03/25/2851488/0/en/Regeneron-Provides-Update-on-Biologics-License-Application-for-Odronextamab.html',
    snippets: [
      'The only approvability issue is related to the enrollment status of the confirmatory trials',
      'the confirmatory portions of these trials should be underway'
    ]
  },
  {
    id: 's08_pubmed_cere120',
    kind: 'web',
    title: 'ClinicalTrials.gov: CERE-120 sham-controlled gene therapy trial',
    url: 'https://clinicaltrials.gov/study/NCT00400634?tab=results',
    snippets: [
      'Double-Blind, Multicenter, Sham Surgery Controlled Study of CERE-120',
      'Sham Surgery Control Group',
      'Primary Outcome Measures'
    ]
  }
];

function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c]));
}

async function addBoxes(imagePath, boxes) {
  const overlays = boxes.map((b, i) => {
    const color = i === 0 ? '#e53935' : '#ff8f00';
    const svg = `<svg width="${Math.ceil(b.width + 16)}" height="${Math.ceil(b.height + 16)}" xmlns="http://www.w3.org/2000/svg">
      <rect x="5" y="5" width="${Math.max(1, Math.ceil(b.width + 6))}" height="${Math.max(1, Math.ceil(b.height + 6))}" rx="6" ry="6" fill="none" stroke="${color}" stroke-width="5"/>
    </svg>`;
    return { input: Buffer.from(svg), left: Math.max(0, Math.floor(b.x - 8)), top: Math.max(0, Math.floor(b.y - 8)) };
  });
  const boxed = imagePath.replace('.png', '_boxed.png');
  await sharp(imagePath).composite(overlays).png().toFile(boxed);
  return boxed;
}

async function findAndBox(page, snippets) {
  const result = await page.evaluate((needles) => {
    const normalize = (s) => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
    const candidates = Array.from(document.querySelectorAll('h1,h2,h3,p,li,td,th,blockquote,div'))
      .map((el) => ({ el, text: normalize(el.innerText || el.textContent || '') }))
      .filter((x) => x.text.length > 10 && x.text.length < 1600);

    const matches = [];
    for (const needle of needles) {
      const n = normalize(needle);
      const hit = candidates
        .filter((x) => x.text.includes(n) || n.includes(x.text.slice(0, Math.min(80, x.text.length))))
        .sort((a, b) => a.text.length - b.text.length)[0];
      if (hit) {
        const rect = hit.el.getBoundingClientRect();
        matches.push({ x: rect.x, y: rect.y, width: rect.width, height: rect.height, text: hit.el.innerText || hit.el.textContent || '' });
      }
    }
    if (!matches.length) return { matches: [] };
    const top = Math.min(...matches.map((m) => m.y));
    window.scrollBy(0, top - 260);
    return { matches: matches.map((m) => ({ ...m, y: m.y - top + 260 })) };
  }, snippets);

  await page.waitForTimeout(800);

  const boxes = await page.evaluate((needles) => {
    const normalize = (s) => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
    const candidates = Array.from(document.querySelectorAll('h1,h2,h3,p,li,td,th,blockquote,div'))
      .map((el) => ({ el, text: normalize(el.innerText || el.textContent || '') }))
      .filter((x) => x.text.length > 10 && x.text.length < 1600);
    const out = [];
    for (const needle of needles) {
      const n = normalize(needle);
      const hit = candidates
        .filter((x) => x.text.includes(n) || n.includes(x.text.slice(0, Math.min(80, x.text.length))))
        .sort((a, b) => a.text.length - b.text.length)[0];
      if (hit) {
        const r = hit.el.getBoundingClientRect();
        if (r.width > 20 && r.height > 10 && r.y < window.innerHeight && r.y + r.height > 0) {
          out.push({ x: r.x, y: r.y, width: Math.min(r.width, window.innerWidth - r.x - 20), height: r.height });
        }
      }
    }
    return out;
  }, snippets);

  return boxes.length ? boxes : result.matches;
}

async function capture() {
  await fs.mkdir(outDir, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: ['--disable-blink-features=AutomationControlled', '--no-sandbox']
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36 AMT130CI/1.0 justin.local@example.com'
  });
  const manifest = [];

  for (const source of sources) {
    const page = await context.newPage();
    await page.goto(source.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(source.kind === 'pdf' ? 4500 : 1200);
    await page.getByText('Reject All', { exact: true }).click({ timeout: 2500 }).catch(() => {});
    await page.getByText('Accept All', { exact: true }).click({ timeout: 2500 }).catch(() => {});
    await page.waitForTimeout(500);

    let boxes = [];
    if (source.manualBox) {
      boxes = [source.manualBox];
    } else {
      boxes = await findAndBox(page, source.snippets);
      if (!boxes.length) {
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForTimeout(500);
        boxes = [{ x: 80, y: 150, width: 1050, height: 260 }];
      }
    }

    const rawPath = path.join(outDir, `${source.id}.png`);
    await page.screenshot({ path: rawPath, fullPage: false });
    const boxedPath = await addBoxes(rawPath, boxes);
    manifest.push({
      ...source,
      screenshot: path.relative('.', boxedPath).replaceAll('\\', '/'),
      rawScreenshot: path.relative('.', rawPath).replaceAll('\\', '/'),
      boxes
    });
    await page.close();
  }

  await browser.close();
  await fs.writeFile('source_manifest.json', JSON.stringify(manifest, null, 2));
}

capture().catch((err) => {
  console.error(err);
  process.exit(1);
});
