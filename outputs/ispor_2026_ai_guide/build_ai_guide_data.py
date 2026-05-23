#!/usr/bin/env python3
import csv
import html
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[1]
PROGRAM_HTML = WORKSPACE / "outputs" / "ispor_2026_ai_sessions" / "program_page.html"
PROGRAM_URL = "https://www.ispor.org/conferences-education/conferences/upcoming-conferences/ispor-2026/program/program/"

AI_PATTERN = re.compile(
    r"(?<![A-Za-z])AI(?![A-Za-z/])|"
    r"artificial intelligence|GenAI|generative AI|generative artificial intelligence|"
    r"machine learning|large language model|\bLLMs?\b|"
    r"natural language processing|\bNLP\b|agentic|prompt engineering|"
    r"digital twins?|reinforcement learning",
    re.I,
)

DATE_2026 = {
    "Sun May 17": "2026-05-17",
    "Mon May 18": "2026-05-18",
    "Tue May 19": "2026-05-19",
    "Wed May 20": "2026-05-20",
}


def clean(value: object) -> str:
    text = html.unescape(str(value or ""))
    text = BeautifulSoup(text, "html.parser").get_text(" ")
    return re.sub(r"\s+", " ", text).strip()


def filters(item: dict, name: str) -> list[str]:
    return [clean(entry.get("Title")) for entry in item.get("Filters", {}).get(name, [])]


def speakers(item: dict) -> list[dict]:
    out = []
    for group in item.get("SpeakerGroups") or []:
        role = clean(group.get("SpeakerType"))
        for speaker in group.get("Speakers") or []:
            out.append(
                {
                    "role": role,
                    "name": clean(speaker.get("Title")),
                    "affiliation": clean(speaker.get("AffiliationAndLocation")),
                }
            )
    return out


def topic_text(item: dict) -> str:
    return " | ".join(
        [
            clean(item.get("Title")),
            clean(item.get("Content")),
            " ".join(filters(item, "tracks")),
            " ".join(filters(item, "Category")),
        ]
    )


def matching_terms(text: str) -> list[str]:
    terms = []
    for match in AI_PATTERN.finditer(text):
        term = match.group(0)
        normalized = {
            "ai": "AI",
            "artificial intelligence": "artificial intelligence",
            "genai": "GenAI",
            "generative ai": "generative AI",
            "generative artificial intelligence": "generative artificial intelligence",
            "machine learning": "machine learning",
            "llm": "LLM",
            "llms": "LLMs",
            "large language model": "large language model",
            "natural language processing": "natural language processing",
            "nlp": "NLP",
            "agentic": "agentic",
            "prompt engineering": "prompt engineering",
            "digital twin": "digital twin",
            "digital twins": "digital twins",
            "reinforcement learning": "reinforcement learning",
        }.get(term.lower(), term)
        if normalized not in terms:
            terms.append(normalized)
    return terms


def parse_time(display_time: str) -> tuple[str, str]:
    parts = [part.strip() for part in (display_time or "").split("-")]
    if len(parts) != 2:
        return "", ""
    return parts[0], parts[1]


def to_24h(time_value: str) -> str:
    try:
        return datetime.strptime(time_value, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        return ""


def derive_theme(title: str, description: str, session_type: str) -> str:
    text = f"{title} {description} {session_type}".lower()
    if any(term in text for term in ["systematic literature", "slr", "literature review", "evidence synthesis", "jca"]):
        return "Evidence synthesis"
    if any(term in text for term in ["model", "cea", "cost-effectiveness", "digital twin", "reinforcement learning", "health economic"]):
        return "Modeling and analytics"
    if any(term in text for term in ["hta", "regulatory", "submission", "guidance", "decision-making", "credibility"]):
        return "HTA, regulatory, and submissions"
    if any(term in text for term in ["rwe", "real-world", "ehr", "claims", "unstructured", "social media", "patient voice", "narrative"]):
        return "RWE and unstructured data"
    if any(term in text for term in ["career", "education", "skills", "up-skilling", "communication"]):
        return "Skills and workforce"
    if any(term in text for term in ["market access", "value", "payer", "pricing"]):
        return "Access and value strategy"
    return "AI methods in HEOR"


def summarize(title: str, description: str) -> str:
    text = description or title
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = " ".join(sentences[:2]).strip()
    if len(summary) > 360:
        summary = summary[:357].rsplit(" ", 1)[0] + "..."
    return summary


def extract_poster_items(content: str) -> list[dict]:
    text = clean(content)
    matches = list(re.finditer(r"\b(PT\d+|IC\d+):\s*", text))
    posters = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = text[match.end() : end].strip(" ;")
        posters.append({"code": match.group(1), "title": title})
    return posters


def related_presentations(item: dict) -> list[dict]:
    related = []
    for child in item.get("Children") or []:
        text = topic_text(child)
        terms = matching_terms(text)
        if terms:
            related.append(
                {
                    "code": clean(child.get("AcceptanceCode")),
                    "title": clean(child.get("Title")),
                    "url": child.get("Url") or "",
                    "display_time": clean(child.get("DisplayTime")),
                    "terms": terms,
                    "summary": summarize(clean(child.get("Title")), clean(child.get("Content"))),
                    "authors": clean(child.get("AuthorBlock")),
                    "speakers": speakers(child),
                }
            )

    for poster in extract_poster_items(item.get("Content", "")):
        terms = matching_terms(f"{poster['code']} {poster['title']}")
        if terms and not any(entry["code"] == poster["code"] and entry["title"] == poster["title"] for entry in related):
            related.append(
                {
                    "code": poster["code"],
                    "title": poster["title"],
                    "url": item.get("Url") or "",
                    "display_time": "",
                    "terms": terms,
                    "summary": poster["title"],
                    "authors": "",
                    "speakers": [],
                }
            )
    return related


def build() -> tuple[list[dict], dict]:
    soup = BeautifulSoup(PROGRAM_HTML.read_text(encoding="utf-8"), "html.parser")
    raw = soup.find("data", id="cti-program-data")["value"]
    program = json.loads(raw)
    sessions = []

    for item in program:
        tracks = filters(item, "tracks")
        item_text = topic_text(item)
        item_terms = matching_terms(item_text)
        related = related_presentations(item)
        is_ai = "AI" in tracks or bool(item_terms) or bool(related)
        if not is_ai:
            continue

        start, end = parse_time(clean(item.get("DisplayTime")))
        session_type = ", ".join(filters(item, "areaofstudy"))
        title = clean(item.get("Title"))
        description = clean(item.get("Content"))
        terms = item_terms[:]
        if "AI" in tracks and "AI track" not in terms:
            terms.insert(0, "AI track")

        sessions.append(
            {
                "id": item.get("Id"),
                "session_id": item.get("SessionId"),
                "title": title,
                "date_label": clean(item.get("LongDisplayDate")),
                "date_short": clean(item.get("DisplayDate")),
                "date": DATE_2026.get(clean(item.get("DisplayDate")), ""),
                "time": clean(item.get("DisplayTime")),
                "start_time": start,
                "end_time": end,
                "start_24h": to_24h(start),
                "end_24h": to_24h(end),
                "session_type": session_type,
                "topics": filters(item, "Category"),
                "tracks": tracks,
                "level": ", ".join(filters(item, "levels")),
                "location": "",
                "url": item.get("Url") or "",
                "speakers": speakers(item),
                "summary": summarize(title, description),
                "theme": derive_theme(title, description, session_type),
                "ai_terms": terms,
                "related_presentations": related,
                "ai_relevance": (
                    "Official AI track"
                    if "AI" in tracks
                    else (
                        "AI terms in title or description"
                        if item_terms
                        else "Contains AI-related podium or poster presentation"
                    )
                ),
            }
        )

    sessions.sort(key=lambda row: (row["date"], row["start_24h"], row["title"]))
    metadata = {
        "source_url": PROGRAM_URL,
        "source_file": str(PROGRAM_HTML),
        "source_note": "Parsed official ISPOR program data payload id='cti-program-data'. Public payload did not include room/location fields.",
        "session_count": len(sessions),
        "related_presentation_count": sum(len(session["related_presentations"]) for session in sessions),
        "counts_by_day": dict(Counter(session["date_short"] for session in sessions)),
        "counts_by_theme": dict(Counter(session["theme"] for session in sessions)),
        "ai_track_count": sum(1 for session in sessions if "AI" in session["tracks"]),
    }
    return sessions, metadata


def main() -> None:
    sessions, metadata = build()
    (ROOT / "ai_sessions_curated.json").write_text(
        json.dumps({"metadata": metadata, "sessions": sessions}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    fieldnames = [
        "date",
        "date_short",
        "time",
        "start_time",
        "end_time",
        "session_type",
        "theme",
        "title",
        "tracks",
        "topics",
        "ai_relevance",
        "ai_terms",
        "related_presentations",
        "speakers",
        "url",
        "location",
    ]
    with (ROOT / "ai_sessions_curated.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for session in sessions:
            writer.writerow(
                {
                    "date": session["date"],
                    "date_short": session["date_short"],
                    "time": session["time"],
                    "start_time": session["start_time"],
                    "end_time": session["end_time"],
                    "session_type": session["session_type"],
                    "theme": session["theme"],
                    "title": session["title"],
                    "tracks": "; ".join(session["tracks"]),
                    "topics": "; ".join(session["topics"]),
                    "ai_relevance": session["ai_relevance"],
                    "ai_terms": "; ".join(session["ai_terms"]),
                    "related_presentations": "; ".join(
                        f"{entry['code']} {entry['title']}".strip() for entry in session["related_presentations"]
                    ),
                    "speakers": "; ".join(
                        f"{speaker['role']}: {speaker['name']} ({speaker['affiliation']})"
                        for speaker in session["speakers"]
                    ),
                    "url": session["url"],
                    "location": session["location"],
                }
            )

    source_log = [
        "# Source Log",
        "",
        f"- Official ISPOR 2026 program page: {PROGRAM_URL}",
        f"- Local capture: `{PROGRAM_HTML}`",
        "- Extraction source: embedded `cti-program-data` payload in the official page HTML.",
        "- Scope: agenda entries that are on the official AI track, contain AI/GenAI/LLM/NLP/machine-learning language in the title or description, or contain AI-related podium/poster presentations.",
        "- Exclusion rule: speaker biographies alone were not used to classify sessions as AI-related.",
        "- Location note: the public program payload reviewed for this guide did not expose room/location fields.",
    ]
    (ROOT / "sources-source-log.md").write_text("\n".join(source_log) + "\n", encoding="utf-8")

    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
