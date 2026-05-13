from pathlib import Path
from playwright.sync_api import sync_playwright


RUN = Path("/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/duchenne_muscular_dystrophy/2026-05-12_1235")
DATE_DIR = RUN / "screenshots" / "date-verification"
EVIDENCE_DIR = RUN / "screenshots" / "evidence"

SOURCES = [
    {
        "id": "01",
        "name": "Entrada Therapeutics",
        "url": "https://www.globenewswire.com/news-release/2026/05/07/3289797/0/en/Entrada-Therapeutics-Announces-Positive-Topline-Results-from-Cohort-1-of-Participants-with-Duchenne-Muscular-Dystrophy-Treated-with-ENTR-601-44-in-Phase-1-2-ELEVATE-44-201-Study.html",
        "date": "May 07, 2026",
        "evidence": [
            "Cohort 1 demonstrated an increase of 2.36% in dystrophin",
            "Statistically significant and potentially differentiated improvement in treated participants versus placebo in Time to Rise velocity",
        ],
    },
    {
        "id": "02",
        "name": "Solid Biosciences",
        "url": "https://www.globenewswire.com/news-release/2026/05/07/3289921/0/en/Solid-Biosciences-Doses-First-Participant-in-Phase-3-IMPACT-DUCHENNE-Clinical-Trial-Evaluating-SGT-003-in-Duchenne-Muscular-Dystrophy.html",
        "date": "May 07, 2026",
        "evidence": [
            "first participant has been dosed in IMPACT DUCHENNE",
            "46 participants have been dosed with SGT-003",
        ],
    },
    {
        "id": "03",
        "name": "Sarepta Therapeutics",
        "url": "https://www.sec.gov/Archives/edgar/data/873303/000119312526208966/srpt-ex99_1.htm",
        "date": "May 6, 2026",
        "evidence": [
            "Net product revenues for the first quarter 2026 totaled $330.5 million",
            "Completed submission of sNDA for AMONDYS 45 and VYONDYS 53",
        ],
    },
    {
        "id": "04",
        "name": "Capricor Therapeutics",
        "url": "https://www.capricor.com/investors/news-events/press-releases/detail/343/capricor-therapeutics-takes-legal-action-to-protect-patient",
        "date": "May 07, 2026",
        "evidence": [
            "filed a lawsuit against Nippon Shinyaku",
            "Priority Review, with a target PDUFA action date of August 22, 2026",
        ],
    },
    {
        "id": "05",
        "name": "Dyne Therapeutics",
        "url": "https://www.sec.gov/Archives/edgar/data/1818794/000119312526215720/dyn-ex99_1.htm",
        "date": "May 11, 2026",
        "evidence": [
            "Positive pre-BLA meeting completed with FDA for z-rostudirsen",
            "on track for BLA submission in Q2 2026 and potential launch in Q1 2027",
        ],
    },
    {
        "id": "06",
        "name": "Atossa Therapeutics",
        "url": "https://investors.atossatherapeutics.com/2026-05-08-Atossa-Therapeutics-Reports-First-Quarter-2026-Financial-Results-and-Provides-a-Corporate-Update",
        "date": "May 8, 2026",
        "evidence": [
            "improved muscle strength, increased lean mass",
            "Orphan Drug Designation to (Z)-endoxifen for the treatment of DMD",
        ],
    },
    {
        "id": "07",
        "name": "Tenaya Therapeutics",
        "url": "https://investors.tenayatherapeutics.com/news-releases/news-release-details/tenaya-therapeutics-reports-first-quarter-2026-financial-results",
        "date": "May 06, 2026",
        "evidence": [
            "TN-301 treatment at doses as low as 3 mg/kg improved grip strength",
            "TN-301 was granted both Rare Pediatric Disease Designation and Orphan Drug Designation",
        ],
    },
]


HIGHLIGHT_JS = r"""
(phrases) => {
  const style = document.createElement('style');
  style.textContent = `
    mark.ci-highlight {
      background: #d7ff5f !important;
      color: #10120f !important;
      outline: 4px solid #ff3b30 !important;
      outline-offset: 3px !important;
      border-radius: 2px !important;
      box-shadow: 0 0 0 3px rgba(255,255,255,.85) !important;
      padding: 0 2px !important;
    }
    .ci-box-highlight {
      outline: 5px solid #ff3b30 !important;
      outline-offset: 5px !important;
      background: rgba(215,255,95,.32) !important;
      box-shadow: 0 0 0 4px rgba(255,255,255,.9) !important;
    }
    .ci-hide, [id*="cookie" i], [class*="cookie" i], [id*="onetrust" i], [class*="onetrust" i],
    [class*="newsletter" i], [id*="newsletter" i], [class*="modal" i], [role="dialog"] {
      display: none !important;
      visibility: hidden !important;
    }
  `;
  document.head.appendChild(style);

  const skipped = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'MARK', 'SVG']);
  const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const normalize = (s) => s.replace(/\s+/g, ' ').trim();
  const results = [];

  function markTextNode(textNode, phrase) {
    const text = textNode.nodeValue;
    const index = text.indexOf(phrase);
    if (index === -1) return null;
    const before = document.createTextNode(text.slice(0, index));
    const mark = document.createElement('mark');
    mark.className = 'ci-highlight';
    mark.textContent = text.slice(index, index + phrase.length);
    const after = document.createTextNode(text.slice(index + phrase.length));
    textNode.parentNode.insertBefore(before, textNode);
    textNode.parentNode.insertBefore(mark, textNode);
    textNode.parentNode.insertBefore(after, textNode);
    textNode.parentNode.removeChild(textNode);
    return mark;
  }

  function markExactPhrase(phrase) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue || !normalize(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        if (node.parentElement && skipped.has(node.parentElement.tagName)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    for (const node of textNodes) {
      const mark = markTextNode(node, phrase);
      if (mark) return mark;
    }
    return null;
  }

  function markContainingElement(phrase) {
    const elements = Array.from(document.body.querySelectorAll('p, li, h1, h2, h3, h4, td, div, span, font, time'));
    const matches = elements
      .filter((el) => normalize(el.innerText || '').includes(phrase))
      .sort((a, b) => normalize(a.innerText || '').length - normalize(b.innerText || '').length);
    if (!matches.length) return null;
    matches[0].classList.add('ci-box-highlight');
    return matches[0];
  }

  for (const phrase of phrases) {
    let node = markExactPhrase(phrase);
    if (!node) node = markContainingElement(phrase);
    results.push({ phrase, found: Boolean(node) });
  }

  const first = document.querySelector('mark.ci-highlight, .ci-box-highlight');
  if (first) first.scrollIntoView({ block: 'center', inline: 'center', behavior: 'instant' });
  document.documentElement.style.scrollBehavior = 'auto';
  return results;
}
"""


def dismiss_obstructions(page):
    selectors = [
        "button:has-text('Accept')",
        "button:has-text('Accept All')",
        "button:has-text('I Accept')",
        "button:has-text('Agree')",
        "button:has-text('Got it')",
        "button:has-text('Close')",
        "[aria-label='Close']",
        ".onetrust-close-btn-handler",
        "#onetrust-accept-btn-handler",
    ]
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            if locator.count() and locator.is_visible(timeout=700):
                locator.click(timeout=1000)
        except Exception:
            pass


def capture_one(page, source, kind, phrases, output_path):
    page.goto(source["url"], wait_until="domcontentloaded", timeout=65000)
    page.wait_for_timeout(1800)
    dismiss_obstructions(page)
    page.evaluate(
        "() => { document.querySelectorAll('iframe, .ad, .ads, [class*=advert i], [id*=advert i]').forEach(el => el.classList.add('ci-hide')); }"
    )
    result = page.evaluate(HIGHLIGHT_JS, phrases)
    missing = [row["phrase"] for row in result if not row["found"]]
    if missing:
        raise RuntimeError(f"{source['id']} {kind} missing highlights: {missing}")
    page.wait_for_timeout(500)
    page.screenshot(path=str(output_path), full_page=False)


def main():
    DATE_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome,
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 1050},
            device_scale_factor=1.5,
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        for source in SOURCES:
            capture_one(
                page,
                source,
                "date",
                [source["date"]],
                DATE_DIR / f"source-{source['id']}-date.png",
            )
            capture_one(
                page,
                source,
                "evidence",
                source["evidence"],
                EVIDENCE_DIR / f"source-{source['id']}-evidence-01.png",
            )
            print(f"captured source {source['id']} - {source['name']}")
        browser.close()


if __name__ == "__main__":
    main()
