import csv
import hashlib
import html
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
TEXT = OUT / "text"
TARGET_STATES = [
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
]
SLUGS = {s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") for s in TARGET_STATES}
MATRIX = ROOT / "pnt-committee-monitoring" / "state-monitoring-matrix.md"
MEETINGS = ROOT / "pnt-committee-monitoring" / "meeting-dates-2025-06-2026-05.csv"
MANIFEST_CSV = OUT / "manifest.csv"
MANIFEST_JSON = OUT / "manifest.json"
SUMMARY = OUT / "summary.md"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"
TIMEOUT = 22
MAX_DEPTH = 1
MAX_DOCS_PER_STATE = 45
MAX_LINKS_FROM_PAGE = 35

RELEVANT_TERMS = [
    "agenda", "minutes", "meeting", "materials", "packet", "committee", "board",
    "dur", "drug utilization", "pharmacy", "therapeutics", "formulary", "pdl",
    "preferred drug", "prior authorization", "pa criteria", "criteria", "protocol",
    "recommendation", "decision", "approved", "public comment", "testimony",
    "hearing", "rebate", "cost", "fiscal", "edit", "clinical", "provider notice",
    "pharmacy facts", "drug list", "single pdl",
]
LOW_VALUE = [
    "facebook", "twitter", "linkedin", "youtube", "instagram", "privacy",
    "accessibility", "contact", "careers", "login", "subscribe", "rss", "sitemap",
]
SKIP_EXT = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".css", ".js", ".mp4", ".mp3", ".zip"}
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt", ".rtf"}

THERAPEUTIC_PATTERNS = {
    "ADHD / CNS stimulants": r"\b(adhd|attention deficit|stimulants?|amphetamine|methylphenidate|vyvanse|concerta|atomoxetine|guanfacine)\b",
    "Asthma / COPD / respiratory": r"\b(asthma|copd|respiratory|inhaler|bronchodilator|ics|lama|laba|dupixent|xolair|tezspire)\b",
    "Autoimmune / immunology": r"\b(rheumatoid|psoriasis|psoriatic|atopic dermatitis|crohn|ulcerative colitis|ibd|biologic|jak inhibitor|tnf|humira|stelara|entyvio|skyrizi|rinvoq|cosentyx|taltz)\b",
    "Cardiometabolic / anticoagulation": r"\b(cardiovascular|anticoagulant|doac|hypertension|heart failure|hyperlipidemia|cholesterol|pcsk9|eliquis|xarelto|entresto|repatha|praluent)\b",
    "Diabetes / obesity / GLP-1": r"\b(diabetes|glp-?1|sglt2|insulin|obesity|weight loss|semaglutide|tirzepatide|ozempic|wegovy|mounjaro|zepbound|trulicity|jardiance|farxiga)\b",
    "Hepatitis / HIV / infectious disease": r"\b(hepatitis|hcv|hiv|antiretroviral|prep|antiviral|epclusa|mavyret|biktarvy|descovy|truvada)\b",
    "Migraine / headache": r"\b(migraine|cgrp|gepant|triptan|aimovig|ajovy|emgality|nurtec|ubrelvy|qulipta)\b",
    "Oncology / hematology": r"\b(oncology|cancer|neoplasm|leukemia|lymphoma|myeloma|car-?t|chemotherapy|hemophilia|sickle cell)\b",
    "Opioid / substance use / pain": r"\b(opioid|opiate|substance use|sud|buprenorphine|naloxone|pain|analgesic|gabapentin|pregabalin)\b",
    "Psychiatry / behavioral health": r"\b(antipsychotic|antidepressant|depression|bipolar|schizophrenia|psychiatric|ssri|snri|latuda|vraylar|rexulti|abilify)\b",
    "Rare disease / specialty": r"\b(rare disease|orphan|spinal muscular atrophy|cystic fibrosis|enzyme replacement|gene therapy|spinraza|zgensma|trikafta)\b",
    "Ophthalmology": r"\b(ophthalmology|retina|macular|amd|diabetic macular edema|glaucoma|eylea|lucentis|vabysmo)\b",
}
RATIONALE_PATTERNS = {
    "clinical efficacy/safety": r"\b(efficacy|effective|effectiveness|safety|adverse|clinical|evidence|study|trial|outcomes?)\b",
    "comparative therapeutic value": r"\b(therapeutically equivalent|therapeutic alternative|superior|inferior|comparative|class review|drug class)\b",
    "prior authorization / step therapy": r"\b(prior authorization|pa criteria|clinical criteria|step therapy|step edit|fail(ed|ure)?|trial of|criteria)\b",
    "utilization / overuse controls": r"\b(utilization|quantity limit|dose limit|duration limit|duplicate therapy|prospective dur|retrospective dur)\b",
    "cost / fiscal / rebate limits": r"\b(cost|fiscal|budget|rebate|supplemental rebate|net cost|financial|expenditure|savings)\b",
    "public comment / manufacturer input": r"\b(public comment|testimony|manufacturer|stakeholder|hearing|speaker|registration|submit comments)\b",
    "final authority / implementation": r"\b(final decision|approved by|commissioner|director|department|implementation|effective date|claims processing|provider notice)\b",
}


def clean(value):
    value = html.unescape(value or "")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s+", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.title = ""
        self._title = []
        self._in_title = False
        self._href = None
        self._anchor = []
        self._skip = 0
        self._text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style", "noscript"}:
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "a" and attrs.get("href"):
            self._href = attrs["href"]
            self._anchor = []
        if tag in {"p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4"} and not self._skip:
            self._text.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1
        if tag == "title":
            self._in_title = False
            self.title = clean(" ".join(self._title))
        if tag == "a" and self._href:
            self.links.append((self._href, clean(" ".join(self._anchor))))
            self._href = None
            self._anchor = []

    def handle_data(self, data):
        if self._in_title:
            self._title.append(data)
        if self._href:
            self._anchor.append(data)
        if not self._skip:
            self._text.append(data)

    @property
    def text(self):
        return clean(" ".join(self._text))


def slugify(url):
    parsed = urllib.parse.urlparse(url)
    base = urllib.parse.unquote(parsed.path.rstrip("/").split("/")[-1] or parsed.netloc)
    if parsed.query:
        base += "-" + hashlib.sha1(parsed.query.encode("utf-8", "ignore")).hexdigest()[:8]
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-._").lower()
    return (base or "document")[:90]


def norm(url):
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse(parsed._replace(fragment=""))


def ext_for(url, ctype):
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext in DOC_EXT:
        return ext
    if ext in {".asp", ".aspx", ".jsp", ".htm", ".html"}:
        return ".html"
    ctype = (ctype or "").lower()
    if "pdf" in ctype:
        return ".pdf"
    if "word" in ctype or "officedocument.wordprocessingml" in ctype:
        return ".docx"
    if "excel" in ctype or "spreadsheet" in ctype:
        return ".xlsx"
    if "csv" in ctype:
        return ".csv"
    if "text/plain" in ctype:
        return ".txt"
    return ".html"


def link_score(url, text):
    lower = f"{url} {text}".lower()
    parsed = urllib.parse.urlparse(url)
    ext = Path(parsed.path).suffix.lower()
    if parsed.scheme not in {"http", "https"} or ext in SKIP_EXT:
        return 0
    if any(term in lower for term in LOW_VALUE):
        return 0
    score = 0
    for term in RELEVANT_TERMS:
        if term in lower:
            score += 2
    if ext in DOC_EXT:
        score += 4
    if any(term in lower for term in ["agenda", "minutes", "materials", "recommendation", "decision", "criteria", "protocol", "pdl"]):
        score += 5
    return score


def read_seeds():
    seeds = defaultdict(list)
    matrix = MATRIX.read_text(encoding="utf-8")
    for state in TARGET_STATES:
        match = re.search(rf"^## {re.escape(state)}\n(?P<body>.*?)(?=^## |\Z)", matrix, re.M | re.S)
        if match:
            for label, url in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", match.group("body")):
                seeds[state].append({"url": url, "label": label, "seed_type": "state-monitoring-matrix"})
    with MEETINGS.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            state = row.get("state", "")
            if state in TARGET_STATES and row.get("source_url"):
                seeds[state].append({
                    "url": row["source_url"],
                    "label": f"{row.get('date_iso', '')} {row.get('committee', '')}".strip(),
                    "seed_type": "meeting-dates-csv",
                })
    return seeds


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as response:
        return response.geturl(), getattr(response, "status", 200), response.headers.get("Content-Type", ""), response.read()


def extract_pdf(path):
    pieces = []
    with fitz.open(path) as doc:
        for idx, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                pieces.append(f"\n\n--- Page {idx} ---\n{text}")
    return clean("\n".join(pieces))


def extract_docx(path):
    pieces = []
    with ZipFile(path) as zf:
        for name in ["word/document.xml", "word/footnotes.xml", "word/endnotes.xml"]:
            if name in zf.namelist():
                xml = zf.read(name).decode("utf-8", "ignore")
                xml = re.sub(r"<w:tab\s*/>", "\t", xml)
                xml = re.sub(r"</w:p>", "\n", xml)
                pieces.append(re.sub(r"<[^>]+>", " ", xml))
    return clean("\n".join(pieces))


def write_manifest(rows):
    fields = ["state", "url", "label", "seed_type", "depth", "discovered_from", "status", "http_status", "content_type", "raw_path", "text_path", "title", "error"]
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    MANIFEST_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def collect():
    for folder in [RAW, TEXT]:
        for state in TARGET_STATES:
            (folder / SLUGS[state]).mkdir(parents=True, exist_ok=True)
    rows = []
    seeds = read_seeds()
    seen = defaultdict(set)
    for state in TARGET_STATES:
        queue = []
        for item in seeds[state]:
            url = norm(item["url"])
            if url not in seen[state]:
                queue.append({**item, "url": url, "depth": 0, "discovered_from": ""})
                seen[state].add(url)
        idx = 0
        while queue and sum(1 for r in rows if r["state"] == state and r["status"] == "saved") < MAX_DOCS_PER_STATE:
            item = queue.pop(0)
            idx += 1
            row = {
                "state": state, "url": item["url"], "label": item.get("label", ""),
                "seed_type": item.get("seed_type", "linked-from-seed"), "depth": item.get("depth", 0),
                "discovered_from": item.get("discovered_from", ""), "status": "", "http_status": "",
                "content_type": "", "raw_path": "", "text_path": "", "title": "", "error": "",
            }
            try:
                final_url, code, ctype, data = fetch(item["url"])
                row["url"], row["http_status"], row["content_type"] = final_url, str(code), ctype
                ext = ext_for(final_url, ctype)
                name = f"{SLUGS[state]}__{idx:03d}__{slugify(final_url)}"
                if not name.endswith(ext):
                    name += ext
                raw_path = RAW / SLUGS[state] / name
                raw_path.write_bytes(data)
                row["raw_path"] = str(raw_path.relative_to(OUT)).replace("\\", "/")
                title, text, links = "", "", []
                if ext == ".pdf":
                    text = extract_pdf(raw_path)
                elif ext == ".docx":
                    text = extract_docx(raw_path)
                elif ext in {".html", ".htm", ".txt", ".csv"}:
                    parser = Parser()
                    parser.feed(data.decode("utf-8", "ignore"))
                    title, text, links = parser.title, parser.text, parser.links
                    if not text and ext in {".txt", ".csv"}:
                        text = clean(data.decode("utf-8", "ignore"))
                else:
                    row["error"] = f"saved but no text extractor for {ext}"
                row["title"] = title
                if text:
                    text_path = TEXT / SLUGS[state] / re.sub(r"\.[^.]+$", ".txt", name)
                    text_path.write_text(f"Source URL: {final_url}\nState: {state}\nLabel: {row['label']}\nContent-Type: {ctype}\nTitle: {title}\n\n{text}\n", encoding="utf-8")
                    row["text_path"] = str(text_path.relative_to(OUT)).replace("\\", "/")
                row["status"] = "saved"
                if item.get("depth", 0) < MAX_DEPTH and links:
                    candidates = []
                    for href, link_text in links:
                        next_url = norm(urllib.parse.urljoin(final_url, href))
                        score = link_score(next_url, link_text)
                        if score > 0 and next_url not in seen[state]:
                            candidates.append((score, next_url, link_text))
                    candidates.sort(key=lambda x: (-x[0], x[1]))
                    for _, next_url, link_text in candidates[:MAX_LINKS_FROM_PAGE]:
                        queue.append({"url": next_url, "label": link_text[:140], "seed_type": "linked-from-seed", "depth": item.get("depth", 0) + 1, "discovered_from": final_url})
                        seen[state].add(next_url)
                time.sleep(0.12)
            except Exception as exc:
                row["status"] = "blocked"
                if isinstance(exc, urllib.error.HTTPError):
                    row["http_status"] = str(exc.code)
                row["error"] = f"{type(exc).__name__}: {exc}"
            rows.append(row)
            if len(rows) % 20 == 0:
                write_manifest(rows)
        write_manifest(rows)
    write_manifest(rows)
    write_summary(rows)
    return rows


def snippets(text, pattern, max_items=3):
    out = []
    for match in re.finditer(pattern, text, flags=re.I):
        snippet = clean(text[max(0, match.start() - 160): min(len(text), match.end() + 240)]).replace("\n", " ")
        if snippet and snippet not in out:
            out.append(snippet)
        if len(out) >= max_items:
            break
    return out


def load_texts(rows):
    by_state = defaultdict(list)
    for row in rows:
        if row.get("text_path"):
            path = OUT / row["text_path"]
            if path.exists():
                by_state[row["state"]].append((row, path.read_text(encoding="utf-8", errors="ignore")))
    return by_state


def state_docs_section(rows):
    by_state = defaultdict(list)
    for row in rows:
        by_state[row["state"]].append(row)
    lines = []
    for state in TARGET_STATES:
        saved = [r for r in by_state[state] if r["status"] == "saved"]
        texted = [r for r in saved if r["text_path"]]
        blocked = [r for r in by_state[state] if r["status"] != "saved"]
        lines += [f"### {state}", "", f"- Documents/pages saved: {len(saved)}; text extracted: {len(texted)}; blocked/not saved: {len(blocked)}."]
        important = [r for r in saved if any(t in f"{r['label']} {r['url']} {r['title']}".lower() for t in ["agenda", "minutes", "materials", "pdl", "preferred", "criteria", "protocol", "meeting", "pharmacy facts", "public notice", "recommendation"])]
        for row in important[:12]:
            label = clean(row["label"] or row["title"] or Path(row["raw_path"]).name)
            lines.append(f"  - `{row['raw_path']}` - {label}; source: {row['url']}")
        if len(important) > 12:
            lines.append(f"  - Additional relevant saved items: {len(important) - 12}; see `manifest.csv`.")
        if blocked:
            lines.append("  - Blocked/not saved:")
            for row in blocked[:8]:
                lines.append(f"    - {row['url']} - {row['error'] or row['http_status']}")
        lines.append("")
    return "\n".join(lines)


def write_summary(rows):
    saved = [r for r in rows if r["status"] == "saved"]
    texted = [r for r in saved if r["text_path"]]
    blocked = [r for r in rows if r["status"] != "saved"]
    texts = load_texts(rows)
    joined = {state: "\n\n".join(text for _, text in items) for state, items in texts.items()}
    rationale_counts, rationale_states = Counter(), defaultdict(list)
    for label, pattern in RATIONALE_PATTERNS.items():
        for state, text in joined.items():
            count = len(re.findall(pattern, text, flags=re.I))
            if count:
                rationale_counts[label] += count
                rationale_states[label].append(state)
    ta_counts, ta_states, ta_snips = Counter(), defaultdict(list), defaultdict(list)
    for label, pattern in THERAPEUTIC_PATTERNS.items():
        for state, text in joined.items():
            count = len(re.findall(pattern, text, flags=re.I))
            if count:
                ta_counts[label] += count
                ta_states[label].append(state)
                for snip in snippets(text, pattern, 2):
                    ta_snips[label].append((state, snip))

    lines = [
        "# Group C P&T/DUR/PDL Decision-Rationale Source Collection",
        "",
        f"Scope: {', '.join(TARGET_STATES)}.",
        "",
        "This collection uses `state-monitoring-matrix.md` and `meeting-dates-2025-06-2026-05.csv` as seed sources. It saves seed URLs plus one-hop linked agenda, minutes, material, PDL, criteria, protocol, notice, public-comment, and pharmacy documents/pages when their link text or URL is decision-rationale relevant.",
        "",
        "Important limitation: this is a public-source collection. Product-level decisions, rebate positions, net-cost calculations, votes, or approval-to-review timing are reported only when present in saved public text. No product-level finding below is inferred from absence or non-public deliberations.",
        "",
        "## Collection Outputs",
        "",
        "- Manifest CSV: `manifest.csv`",
        "- Manifest JSON: `manifest.json`",
        "- Raw saved sources: `raw/<state>/`",
        "- Extracted text: `text/<state>/`",
        f"- Saved sources: {len(saved)}",
        f"- Sources with extracted text: {len(texted)}",
        f"- Blocked/not saved: {len(blocked)}",
        f"- States with extracted text: {', '.join(sorted(texts))}",
        "",
        "## Documents Collected by State",
        "",
        state_docs_section(rows),
        "## Key Decision-Rationale Patterns",
        "",
        "### Patterns Applicable Across Drugs",
        "",
    ]
    if rationale_counts:
        for label, count in rationale_counts.most_common():
            lines.append(f"- **{label}** appears in extracted text across {len(rationale_states[label])} state(s): {', '.join(rationale_states[label])}. Term hits: {count}.")
    else:
        lines.append("- No rationale-related terms were extracted. Review blocked sources and raw files.")
    lines += [
        "",
        "High-value cross-drug implications for pharma companies:",
        "",
        "- Monitor both the advisory body and the implementation channel. Committee discussion, recommendation, agency acceptance, PDL posting, provider notice, and claims-system effective date can be separate events.",
        "- Treat agenda posting as the earliest practical signal for engagement. Public-comment/testimony windows are often tied to agenda posting, public hearing notices, or short pre-meeting registration deadlines.",
        "- Prepare evidence in the language committees use publicly: comparative clinical value, safety, utilization management criteria, unmet need, medically necessary exception paths, and member/provider disruption.",
        "- Cost and rebate considerations appear in statutes, PDL frameworks, or fiscal-edit language more often than in drug-by-drug public rationale. Do not expect public minutes to disclose net-cost tradeoffs.",
        "- Track class reviews rather than only brand mentions. Competitors can be affected through class-wide preferred/non-preferred moves, PA criteria, quantity limits, and step edits.",
        "",
        "### Therapeutic Area / Disease-Specific Signals Found",
        "",
    ]
    if ta_counts:
        for label, count in ta_counts.most_common():
            lines.append(f"- **{label}**: found in {len(ta_states[label])} state(s): {', '.join(ta_states[label])}. Term hits: {count}.")
            for state, snip in ta_snips[label][:3]:
                lines.append(f"  - {state}: \"{snip[:420]}\"")
    else:
        lines.append("- No targeted therapeutic-area terms were detected in extracted text. This does not mean these areas were not reviewed.")
    lines += [
        "",
        "## Public Rationale Transparency",
        "",
        "- Stronger transparency signals include posted meeting materials, minutes, PDL recommendations, protocol/criteria documents, public-comment instructions, member lists, and final implementation notices.",
        "- Weaker transparency signals include schedule-only pages, PDL-only pages, public notices without attachments, or minutes that record procedural actions without drug-by-drug rationale.",
        "- Public rationale usually emphasizes clinical appropriateness, safety, comparative value, PA/step criteria, utilization controls, and implementation mechanics. Drug-specific net price/rebate rationale is generally unavailable in the public record.",
        "",
        "## Final-Decision Separation",
        "",
        "- Many public bodies are advisory or recommendatory. Pharma monitoring should track committee recommendation, agency acceptance/final decision, PDL posting, provider notice, and claims-system effective date as separate milestones.",
        "- A recommendation can create an early signal before coverage actually changes; conversely, an agency or contractor update may reveal implementation even when minutes are sparse.",
        "",
        "## Manufacturer / Public-Comment Windows",
        "",
        "- Public-comment, testimony, hearing, speaker-registration, and written-comment processes are the most actionable engagement windows found in these source types.",
        "- Engagement preparation should start before the public packet is posted where classes are predictable from annual review cycles, PDL update cadence, or recurring DUR topics.",
        "",
        "## Cost / Rebate / Rationale Limitations",
        "",
        "- Cost-effectiveness, fiscal edits, supplemental rebates, or net-cost concepts appear as governance criteria in some sources, but detailed calculations are not usually public.",
        "- Absence of a public cost rationale should be labeled as unavailable, not interpreted as lack of cost influence.",
        "",
        "## High-Value Pharma Monitoring Implications",
        "",
        "- Build a state-by-state watchlist with four artifact types: agenda/packet, minutes/recommendations, final PDL/PA/criteria updates, and provider/pharmacy bulletins.",
        "- Separate evidence needs by decision layer: clinical dossier for committee discussion, affordability/rebate strategy for confidential negotiation, operational pull-through for implementation notices.",
        "- Watch public-comment deadlines and speaker registration. Missing a short window can remove the only public opportunity to shape the record before recommendation.",
        "- Flag when a state has a DUR board rather than a body called P&T; for market access purposes, the relevant decision signal may still be DUR, DPAC, formulary committee, or PDL committee activity.",
        "- Maintain an explicit data-gap field by state and class. Public files often do not identify exact votes, final rationale, or net-cost assumptions.",
        "",
        "## Blocked or Unextracted Sources",
        "",
    ]
    if blocked:
        for row in blocked:
            lines.append(f"- {row['state']}: {row['url']} - {row['error'] or row['http_status']}")
    else:
        lines.append("- None blocked during this run.")
    unextracted = [r for r in saved if not r["text_path"]]
    if unextracted:
        lines += ["", "Saved but no text extracted:"]
        for row in unextracted:
            lines.append(f"- {row['state']}: `{row['raw_path']}` - {row['error'] or row['content_type']}")
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    rows = collect()
    print(f"Manifest rows: {len(rows)}")
    print(f"Saved: {sum(1 for r in rows if r['status'] == 'saved')}")
    print(f"Text extracted: {sum(1 for r in rows if r['text_path'])}")
    print(f"Blocked: {sum(1 for r in rows if r['status'] != 'saved')}")
