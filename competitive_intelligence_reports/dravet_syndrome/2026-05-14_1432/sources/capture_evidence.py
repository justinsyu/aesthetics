from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

RUN = Path("/Users/justinyu/Desktop/linkedin-posts/competitive_intelligence_reports/dravet_syndrome/2026-05-14_1432")

SOURCES = [
    {
        "url": "https://encoded.com/press-releases/encoded-therapeutics-presents-new-clinical-data-from-polaris-phase-1-2-trials-of-etx101-gene-therapy-in-dravet-syndrome-at-the-asgct-2026-presidential-symposium/",
        "date": ("source-01-date.png", "May 13, 2026"),
        "evidence": [
            ("source-01-evidence-01.png", "ongoing POLARIS Phase 1/2 trials of ETX101", "approximately a 76% median monthly countable seizure frequency"),
            ("source-01-evidence-02.png", "Patients who reached 52 weeks of observation", "no treatment- or procedure-related serious adverse events"),
        ],
    },
    {
        "url": "https://www.jax.org/news-and-insights/2026/may/precision-dna-editing-targets-root-cause-of-severe-childhood-epilepsy-in-preclinical-study",
        "date": ("source-02-date.png", "Article | May 13, 2026"),
        "evidence": [
            ("source-02-evidence-01.png", "The preclinical study focused on a specific Dravet-causing SCN1A variant called R613X", "single injection into the brain in very young mice"),
            ("source-02-evidence-02.png", "corrected nearly 60% of the mutated DNA", "significant survival improvement"),
        ],
    },
    {
        "url": "https://clinicaltrials.gov/study/NCT07013331",
        "date": ("source-03-date.png", "Last Update Posted 2026-05-08"),
        "evidence": [
            ("source-03-evidence-01.png", "Recruiting", "A PET-MRI Study of Serotoninergic Brainstem Pathway in Patients With Dravet Syndrome"),
            ("source-03-evidence-02.png", "The DRAPETOTINE study will thus focus on imaging 5HT brainstem pathway with PET and MRI", "This study will involve 20 adult patients"),
        ],
    },
    {
        "url": "https://clinicaltrials.gov/study/NCT07013331?tab=history",
        "date": None,
        "evidence": [
            ("source-03-evidence-03.png", "3\t2026-05-05", "Recruitment Status"),
        ],
    },
    {
        "url": "https://clinicaltrials.gov/study/NCT04462770",
        "date": ("source-04-date.png", "Last Update Posted 2026-05-14"),
        "evidence": [
            ("source-04-evidence-02.png", "This is a multicenter, Phase 3, randomized, double-blind, placebo-controlled study", "Percent Change in Countable Motor Seizures Per 28 Days"),
        ],
    },
    {
        "url": "https://clinicaltrials.gov/study/NCT04462770?tab=history",
        "date": None,
        "evidence": [
            ("source-04-evidence-03.png", "34\t2026-05-12"),
        ],
    },
]


def close_obstructions(page):
    for pattern in ["Accept", "Save and close", "I Accept", "Accept All", "Agree", "Close"]:
        try:
            page.get_by_text(pattern, exact=True).first.click(timeout=1200)
        except PlaywrightTimeoutError:
            pass
        except Exception:
            pass
    page.evaluate(
        """() => {
          const selectors = [
            '[class*="cookie"]', '[id*="cookie"]', '[aria-label*="cookie" i]',
            '[class*="modal"]', '[role="dialog"]', '.cky-consent-container',
            '.cky-modal', '.osano-cm-window', '.newsletter', '[class*="popup"]'
          ];
          for (const selector of selectors) {
            document.querySelectorAll(selector).forEach((el) => {
              const text = (el.innerText || '').toLowerCase();
              if (text.includes('cookie') || text.includes('privacy') || text.includes('newsletter') || el.getAttribute('role') === 'dialog') {
                el.style.display = 'none';
              }
            });
          }
        }"""
    )


def highlight(page, text):
    found = page.evaluate(
        """(needle) => {
          const styleId = 'ci-highlight-style';
          if (!document.getElementById(styleId)) {
            const style = document.createElement('style');
            style.id = styleId;
            style.textContent = '.ci-highlight { background: #d7ff5f !important; color: #10120f !important; box-shadow: 0 0 0 3px #10120f !important; border-radius: 3px; padding: 1px 2px; }';
            document.head.appendChild(style);
          }
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          const normalize = (value) => value.replace(/\\s+/g, ' ').trim();
          let node;
          while ((node = walker.nextNode())) {
            const raw = node.nodeValue || '';
            const idx = raw.indexOf(needle);
            if (idx >= 0) {
              const span = document.createElement('span');
              span.className = 'ci-highlight';
              const before = document.createTextNode(raw.slice(0, idx));
              const hit = document.createTextNode(raw.slice(idx, idx + needle.length));
              const after = document.createTextNode(raw.slice(idx + needle.length));
              span.appendChild(hit);
              node.parentNode.insertBefore(before, node);
              node.parentNode.insertBefore(span, node);
              node.parentNode.insertBefore(after, node);
              node.parentNode.removeChild(node);
              span.scrollIntoView({ block: 'center', inline: 'nearest' });
              return true;
            }
            if (normalize(raw).includes(normalize(needle))) {
              const parent = node.parentElement;
              parent.classList.add('ci-highlight');
              parent.scrollIntoView({ block: 'center', inline: 'nearest' });
              return true;
            }
          }
          const elements = Array.from(document.querySelectorAll('p, li, h1, h2, h3, h4, div, span, td, th, dd, dt'));
          const element = elements.find((el) => normalize(el.innerText || '').includes(normalize(needle)));
          if (element) {
            element.classList.add('ci-highlight');
            element.scrollIntoView({ block: 'center', inline: 'nearest' });
            return true;
          }
          return false;
        }""",
        text,
    )
    if not found:
        raise RuntimeError(f"Could not highlight text: {text}")


def capture(page, out_path):
    page.wait_for_timeout(700)
    page.screenshot(path=str(out_path), full_page=False)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1150}, device_scale_factor=1)
        for source in SOURCES:
            page = context.new_page()
            page.goto(source["url"], wait_until="domcontentloaded", timeout=60000)
            close_obstructions(page)
            page.wait_for_timeout(700)

            if source["date"]:
                filename, date_text = source["date"]
                highlight(page, date_text)
                capture(page, RUN / "screenshots/date-verification" / filename)

            for filename, *phrases in source["evidence"]:
                page.goto(source["url"], wait_until="domcontentloaded", timeout=60000)
                close_obstructions(page)
                page.wait_for_timeout(700)
                for phrase in phrases:
                    highlight(page, phrase)
                capture(page, RUN / "screenshots/evidence" / filename)
            page.close()
        browser.close()


if __name__ == "__main__":
    main()
