from pathlib import Path
from playwright.sync_api import sync_playwright


RUN_DIR = Path("/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/duchenne_muscular_dystrophy/2026-05-13_1728")
DATE_DIR = RUN_DIR / "screenshots" / "date-verification"
EVIDENCE_DIR = RUN_DIR / "screenshots" / "evidence"


SOURCES = [
    {
        "ref": 1,
        "name": "Entrada Therapeutics",
        "url": "https://www.globenewswire.com/news-release/2026/05/07/3289797/0/en/Entrada-Therapeutics-Announces-Positive-Topline-Results-from-Cohort-1-of-Participants-with-Duchenne-Muscular-Dystrophy-Treated-with-ENTR-601-44-in-Phase-1-2-ELEVATE-44-201-Study.html",
        "date": "May 07, 2026 07:00 ET",
        "evidence": [
            [
                "ELEVATE-44-201 is a clinical study of ENTR-601-44 in ambulatory participants ages four to 20",
                "Consequently, Cohort 1 demonstrated an increase of 2.36% in dystrophin over a baseline of 4.00% and an increase of 2.31% in exon skipping over a baseline of 2.66% in treated participants",
                "Statistically significant and potentially differentiated improvement in treated participants versus placebo in Time to Rise velocity",
            ],
            [
                "The results demonstrated a favorable safety and tolerability profile with no reported serious adverse events (SAEs) and no adverse events (AEs) leading to discontinuation from the study.",
                "The Company expects to report results from the Cohort 1 open-label study and Cohort 2 MAD study by year-end 2026, with data from Cohort 3 (up to 18 mg/kg) to follow.",
            ],
        ],
    },
    {
        "ref": 2,
        "name": "Solid Biosciences",
        "url": "https://www.globenewswire.com/news-release/2026/05/12/3293411/0/en/solid-biosciences-reports-first-quarter-2026-financial-results-and-provides-business-updates.html",
        "date": "May 12, 2026 16:08 ET",
        "evidence": [
            [
                "First participant dosed in the Phase 3 IMPACT DUCHENNE clinical trial",
                "dosing of 47 participants in Phase 1/2 INSPIRE DUCHENNE clinical trial",
                "positive opinion on the Company’s Pediatric Investigation Plan from the European Medicines Agency",
            ],
            [
                "IMPACT DUCHENNE is a Phase 3 placebo-controlled, randomized, double-blind clinical trial evaluating the efficacy of a single dose of SGT-003 in ambulatory participants with a genetically confirmed Duchenne diagnosis.",
                "SGT-003 continued to be generally well tolerated in the 47 participants dosed in the INSPIRE DUCHENNE trial as of May 11, 2026.",
            ],
        ],
    },
    {
        "ref": 3,
        "name": "Capricor Therapeutics",
        "url": "https://www.capricor.com/investors/news-events/press-releases/detail/344/capricor-therapeutics-reports-first-quarter-2026-financial",
        "date": "May 12, 2026",
        "evidence": [
            [
                "Deramiocel BLA under active FDA review; PDUFA target action date of August 22, 2026; labeling discussions expected to commence soon",
                "HOPE-3 Phase 3 trial met its primary endpoint (PUL v2.0; upper limb function) and all Type I error-controlled secondary endpoints",
                "GMP manufacturing facility fully operational; second-floor expansion well underway",
            ],
            [
                "The FDA review and PDUFA date are unaffected by Capricor’s lawsuit against NS Pharma.",
                "Approximately 90 patients are currently enrolled across Capricor's collective open-label extension studies",
                "more than 800 infusions",
            ],
        ],
    },
    {
        "ref": 4,
        "name": "Dyne Therapeutics",
        "url": "https://www.globenewswire.com/news-release/2026/05/11/3291782/0/en/dyne-therapeutics-reports-first-quarter-2026-financial-results-and-recent-business-highlights.html",
        "date": "May 11, 2026 07:30 ET",
        "evidence": [
            [
                "Positive pre-BLA meeting completed with FDA for z-rostudirsen in exon 51 DMD; on track for BLA submission in Q2 2026 and potential launch in Q1 2027",
                "Dyne plans to initiate a global confirmatory Phase 3 clinical trial of z-rostudirsen in Q2 2026.",
            ],
            [
                "Unadjusted dystrophin production in these participants reached an average of 9.48% of normal (n=4) as compared to 0.52% at baseline (n=3)",
                "muscle content-adjusted dystrophin production reached an average of 18.33% of normal (n=4) as compared to 1.47% at baseline (n=3).",
                "Dyne is advancing four development candidates (DYNE-253, DYNE-245, DYNE-244 and DYNE-255) for the potential treatment of DMD amenable to skipping of exons 53, 45, 44, and 55, respectively.",
            ],
        ],
    },
    {
        "ref": 5,
        "name": "Atossa Therapeutics",
        "url": "https://investors.atossatherapeutics.com/2026-05-08-Atossa-Therapeutics-Reports-First-Quarter-2026-Financial-Results-and-Provides-a-Corporate-Update",
        "date": "May 8, 2026",
        "evidence": [
            [
                "generating data to support its potential in rare diseases, including Duchenne Muscular Dystrophy (DMD)",
                "we secured both Orphan Drug and Rare Pediatric Disease designations from the FDA for (Z)-endoxifen in DMD",
                "the Company demonstrated that (Z)-endoxifen improved muscle strength, increased lean mass, and reduced biochemical markers of muscle damage in dystrophic mouse models.",
            ],
        ],
    },
]


HIGHLIGHT_SCRIPT = """
({ text, className }) => {
  function installStyle() {
    if (document.getElementById("ci-highlight-style")) return;
    const style = document.createElement("style");
    style.id = "ci-highlight-style";
    style.textContent = `
      mark.ci-date-highlight,
      mark.ci-evidence-highlight {
        background: #fff172 !important;
        color: #11130f !important;
        outline: 3px solid #e01f1f !important;
        border-radius: 3px !important;
        padding: 1px 2px !important;
      }
    `;
    document.head.appendChild(style);
  }
  installStyle();

  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (parent.closest("script, style, noscript, mark")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    }
  );

  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const idx = node.nodeValue.indexOf(text);
    if (idx === -1) continue;
    const range = document.createRange();
    range.setStart(node, idx);
    range.setEnd(node, idx + text.length);
    const mark = document.createElement("mark");
    mark.className = className;
    range.surroundContents(mark);
    const rect = mark.getBoundingClientRect();
    mark.scrollIntoView({ block: "center", inline: "nearest" });
    return { found: true, text, y: rect.y, height: rect.height };
  }
  return { found: false, text };
}
"""


def dismiss_overlays(page):
    page.keyboard.press("Escape")
    labels = [
        "Accept",
        "Accept All",
        "I Accept",
        "Agree",
        "I Agree",
        "Continue",
        "Close",
        "No thanks",
        "That's ok",
        "I decline",
        "Let me choose",
    ]
    for label in labels:
        try:
            locator = page.get_by_role("button", name=label, exact=False)
            if locator.count():
                locator.first.click(timeout=700)
                page.wait_for_timeout(300)
        except Exception:
            pass
    for text in ["That's ok", "I decline", "Let me choose"]:
        try:
            locator = page.get_by_text(text, exact=False)
            if locator.count():
                locator.first.click(timeout=700)
                page.wait_for_timeout(300)
        except Exception:
            pass


def mark_text(page, text, class_name):
    result = page.evaluate(HIGHLIGHT_SCRIPT, {"text": text, "className": class_name})
    if not result.get("found"):
        raise RuntimeError(f"Could not highlight text: {text}")
    page.wait_for_timeout(250)
    return result


def capture_source(page, source):
    print(f"Reference {source['ref']}: {source['name']}")
    page.goto(source["url"], wait_until="domcontentloaded", timeout=70000)
    page.wait_for_timeout(2000)
    dismiss_overlays(page)

    mark_text(page, source["date"], "ci-date-highlight")
    page.wait_for_timeout(500)
    page.screenshot(path=str(DATE_DIR / f"source-{source['ref']:02d}-date.png"), full_page=False)

    for idx, snippets in enumerate(source["evidence"], 1):
        first = True
        for snippet in snippets:
            result = mark_text(page, snippet, "ci-evidence-highlight")
            if first:
                page.wait_for_timeout(300)
                first = False
        page.wait_for_timeout(500)
        page.screenshot(path=str(EVIDENCE_DIR / f"source-{source['ref']:02d}-evidence-{idx:02d}.png"), full_page=False)


def main():
    DATE_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 980},
            device_scale_factor=1,
        )
        page = context.new_page()
        for source in SOURCES:
            capture_source(page, source)
        browser.close()


if __name__ == "__main__":
    main()
