#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

POSITIVE_PATTERNS = [
    r"\bAI[- ]powered\b",
    r"\bAI[- ]enabled\b",
    r"\bAI[- ]driven\b",
    r"\bAI[- ]assisted\b",
    r"\bgenerative AI (platform|solution|service|services|software|tool|tools|product|products|capabilit|offering)",
    r"\bartificial intelligence (platform|solution|service|services|software|tool|tools|product|products|capabilit|offering)",
    r"\b(machine learning|natural language processing|NLP|LLM|large language model).{0,80}\b(platform|solution|service|software|tool|product|offering|analytics)",
    r"\b(platform|solution|service|software|tool|product|offering|analytics).{0,80}\b(machine learning|natural language processing|NLP|LLM|large language model)",
    r"\bAI.{0,80}\b(platform|solution|service|software|tool|product|offering|feature|demo|capabilit|workflow|automation)",
    r"\b(platform|solution|service|software|tool|product|offering|feature|demo|capabilit|workflow|automation).{0,80}\bAI\b",
    r"\bpredictive (analytics|model|models|modeling|modelling|platform|solution|software|tool)",
]

OFFERING_URL_PARTS = re.compile(
    r"(/product|/products|/solution|/solutions|/service|/services|/platform|/software|/technology|/technologies|/demo|/case-stud|/capabilit|/artificial-intelligence|/machine-learning|/generative-ai|ai-powered)",
    re.I,
)

THOUGHT_URL_PARTS = re.compile(
    r"(/blog|/blogs|/article|/articles|/insight|/insights|/news|/press|/webinar|/podcast|/event|/events|/resource|/resources|/career|/careers|/job|/jobs)",
    re.I,
)

EXCLUDE_TITLE_PATTERNS = [
    r"\bcareer(s)?\b",
    r"\bjob(s)?\b",
    r"\bjoin us\b",
    r"\bevent(s)?\b",
    r"\bconference\b",
    r"\bpodcast\b",
    r"\bwebinar\b",
    r"\bblog\b",
    r"\binsight(s)?\b",
    r"\barticle\b",
    r"\bnews\b",
    r"\bpress release\b",
]

ALLOW_THOUGHT_CONTENT_IF = [
    r"\blaunch(es|ed|ing)?\b.{0,120}\b(AI|artificial intelligence|generative AI|machine learning).{0,120}\b(product|platform|solution|service|feature|tool|software)",
    r"\b(introduces|introduced|unveils|unveiled|announces|announced)\b.{0,120}\b(AI|artificial intelligence|generative AI|machine learning).{0,120}\b(product|platform|solution|service|feature|tool|software)",
    r"\b(AI|artificial intelligence|generative AI|machine learning).{0,80}\bdemo\b",
    r"\bcase stud(y|ies)\b",
    r"\bcustomer story\b.{0,120}\b(AI|artificial intelligence|generative AI|machine learning)",
]


def has_any(patterns, text):
    return any(re.search(pattern, text, re.I | re.S) for pattern in patterns)


def classify(row):
    title = row.get("page_title", "")
    url = row.get("page_url", "")
    snippet = row.get("snippet", "")
    text = f"{title}\n{url}\n{snippet}"
    positive_hits = [p for p in POSITIVE_PATTERNS if re.search(p, text, re.I | re.S)]
    if not positive_hits:
        return {
            "explicit_ai_offering": False,
            "confidence": "low",
            "reason": "AI is present, but no explicit product/offering/service language was detected in the title, URL, or captured evidence text.",
            "positive_hits": [],
        }

    title_has_ai = re.search(r"\b(AI|artificial intelligence|generative AI|machine learning|NLP|LLM|large language model)\b", title, re.I)
    title_has_offering = re.search(r"\b(product|platform|solution|service|software|tool|offering|feature|capabilit|workflow|automation|demo|case study|case studies)\b", title, re.I)
    url_has_offering = bool(OFFERING_URL_PARTS.search(url))
    url_is_bad_container = bool(re.search(r"(/author/|/tag/|/category/|/people/|/team/)", url, re.I))
    snippet_strong = has_any(
        [
            r"\bAI[- ]powered\b.{0,100}\b(product|platform|solution|service|software|tool|feature|workflow|automation)",
            r"\bAI[- ]enabled\b.{0,100}\b(product|platform|solution|service|software|tool|feature|workflow|automation)",
            r"\bAI[- ]driven\b.{0,100}\b(product|platform|solution|service|software|tool|feature|workflow|automation)",
            r"\bgenerative AI\b.{0,100}\b(product|platform|solution|service|software|tool|feature|workflow|automation)",
            r"\b(product|platform|solution|service|software|tool|feature|workflow|automation)\b.{0,100}\b(AI[- ]powered|AI[- ]enabled|AI[- ]driven|generative AI)",
        ],
        snippet,
    )

    title_excluded = has_any(EXCLUDE_TITLE_PATTERNS, title) or bool(THOUGHT_URL_PARTS.search(url))
    allowed_thought = has_any(ALLOW_THOUGHT_CONTENT_IF, text) or (
        bool(OFFERING_URL_PARTS.search(url)) and not bool(THOUGHT_URL_PARTS.search(url))
    )
    explicit = False
    if url_is_bad_container:
        explicit = False
    elif title_has_ai and title_has_offering:
        explicit = True
    elif url_has_offering and snippet_strong:
        explicit = True
    elif not title_excluded and snippet_strong:
        explicit = True
    elif allowed_thought and (title_has_ai or snippet_strong):
        explicit = True
    if explicit:
        confidence = "high" if bool(OFFERING_URL_PARTS.search(url)) or has_any([r"\bAI[- ]powered\b", r"\bAI[- ]enabled\b", r"\bAI[- ]driven\b"], text) else "medium"
        reason = "Explicit AI language appears with product/offering/service terms in the page title, URL, or captured evidence text."
    else:
        confidence = "low"
        reason = "Appears to be thought leadership/news/event content rather than a vendor product, offering, or service page."
    return {
        "explicit_ai_offering": explicit,
        "confidence": confidence,
        "reason": reason,
        "positive_hits": positive_hits[:3],
    }


def main():
    source = DATA / "highlighted_ai_offering_pages.csv"
    rows = list(csv.DictReader(source.open(encoding="utf-8")))
    out = []
    for idx, row in enumerate(rows, start=1):
        result = classify(row)
        out.append({"review_id": idx, **row, **result})
    path = DATA / "explicit_ai_offering_candidates.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    selected = [r for r in out if r["explicit_ai_offering"]]
    csv_path = DATA / "explicit_ai_offering_candidates.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fields = [
            "review_id",
            "display_name",
            "website",
            "page_title",
            "page_url",
            "screenshot",
            "highlight_count",
            "confidence",
            "reason",
            "snippet",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: r.get(k, "") for k in fields} for r in selected])
    print(f"reviewed={len(out)} selected={len(selected)}")
    print(path)
    print(csv_path)


if __name__ == "__main__":
    main()
