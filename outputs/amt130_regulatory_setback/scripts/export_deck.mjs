import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';

const chromePath = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const htmlPath = path.resolve('amt130_regulatory_setback_deck.html');
const pdfPath = path.resolve('amt130_regulatory_setback_deck.pdf');
const previewDir = path.resolve('render-check');

async function exportDeck() {
  await fs.mkdir(previewDir, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: ['--no-sandbox']
  });
  const page = await browser.newPage({
    viewport: { width: 1600, height: 900 },
    deviceScaleFactor: 1
  });
  await page.goto(`file:///${htmlPath.replaceAll('\\', '/')}`, { waitUntil: 'load' });
  await page.pdf({
    path: pdfPath,
    width: '1600px',
    height: '900px',
    printBackground: true,
    margin: { top: '0', right: '0', bottom: '0', left: '0' }
  });

  const slides = await page.locator('.slide').count();
  for (let i = 0; i < slides; i += 1) {
    await page.locator('.slide').nth(i).screenshot({
      path: path.join(previewDir, `slide-${String(i + 1).padStart(2, '0')}.png`)
    });
  }
  await browser.close();
}

exportDeck().catch((err) => {
  console.error(err);
  process.exit(1);
});
