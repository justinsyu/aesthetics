#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def main() -> None:
    roster = load_json(DATA / "ispor26_exhibitors_with_websites.json")
    roster_by_name = {row["display_name"]: row for row in roster}
    chunk_paths = sorted(DATA.glob("crawl_chunk_*.json"))
    crawl_records = []
    for path in chunk_paths:
        crawl_records.extend(load_json(path))

    crawl_by_name = {row["display_name"]: row for row in crawl_records}
    all_rows = []
    ai_rows = []
    seen_ai_pages = set()
    for roster_row in roster:
        name = roster_row["display_name"]
        crawl = crawl_by_name.get(name, {})
        ai_pages = crawl.get("ai_pages", [])
        all_rows.append(
            {
                "display_name": name,
                "booth": roster_row.get("booth", ""),
                "website": roster_row.get("website", ""),
                "website_source": roster_row.get("website_source", ""),
                "profile_url": roster_row.get("profile_url", ""),
                "pages_visited": len(crawl.get("pages_visited", [])),
                "ai_pages": len(ai_pages),
                "screenshots": len(crawl.get("screenshots", [])),
                "errors": " | ".join(crawl.get("errors", [])),
            }
        )
        for page in ai_pages:
            key = (name, page.get("url", ""))
            if key in seen_ai_pages:
                continue
            seen_ai_pages.add(key)
            ai_rows.append(
                {
                    "display_name": name,
                    "booth": roster_row.get("booth", ""),
                    "website": roster_row.get("website", ""),
                    "page_title": page.get("title", ""),
                    "page_url": page.get("url", ""),
                    "score": page.get("score", ""),
                    "highlight_count": page.get("highlight_count", ""),
                    "screenshot": page.get("screenshot", ""),
                    "snippet": " / ".join(page.get("snippets", [])[:2]),
                }
            )

    summary_csv = DATA / "vendor_crawl_summary.csv"
    ai_csv = DATA / "ai_offering_pages.csv"
    highlighted_csv = DATA / "highlighted_ai_offering_pages.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
    with ai_csv.open("w", newline="", encoding="utf-8") as f:
        fields = ["display_name", "booth", "website", "page_title", "page_url", "score", "highlight_count", "screenshot", "snippet"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ai_rows)
    highlighted_rows = [row for row in ai_rows if int(row["highlight_count"] or 0) > 0]
    with highlighted_csv.open("w", newline="", encoding="utf-8") as f:
        fields = ["display_name", "booth", "website", "page_title", "page_url", "score", "highlight_count", "screenshot", "snippet"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(highlighted_rows)

    md = []
    md.append("# ISPOR 2026 Exhibitor AI Offering Screenshot Index\n")
    md.append(f"- Exhibitors in GoExpo roster: {len(roster)}")
    md.append(f"- Crawl chunk files assembled: {len(chunk_paths)}")
    md.append(f"- Vendors with completed crawl records: {len(crawl_records)}")
    md.append(f"- Vendors with AI-related pages captured: {sum(1 for r in all_rows if r['ai_pages'])}")
    md.append(f"- AI-related pages/screenshots detected after dedupe: {len(ai_rows)}")
    md.append(f"- Screenshots with visible highlighted AI/ML text: {len(highlighted_rows)}")
    md.append("\n## Method Notes\n")
    md.append("- Roster source: ISPOR 2026 GoExpo exhibitor list and profile pages.")
    md.append("- Website domains were validated by parallel subagents and stored in `website_overrides.json`; uncertain entries remain marked through the crawler summary/errors.")
    md.append("- The crawler visits same-site pages discovered from the homepage, same-domain links, and sitemap URLs whose URL/text matches AI, machine learning, automation, platform, analytics, RWE, HEOR, or evidence-discovery terms.")
    md.append("- Screenshots are full-page captures with DOM-injected yellow highlights around matched AI/ML terms.")
    md.append("- Public websites can block automation, require JavaScript flows, hide pages behind forms, or omit sitemaps; those limitations are retained in the `errors` column.")
    md.append("\n## Captured AI Offering Pages With Visible Highlights\n")
    current = None
    for row in sorted(highlighted_rows, key=lambda r: (r["display_name"].lower(), r["page_title"].lower())):
        if row["display_name"] != current:
            current = row["display_name"]
            md.append(f"\n### {current}\n")
        rel_shot = Path(row["screenshot"]).relative_to(ROOT.parent) if row["screenshot"] else ""
        md.append(f"- [{row['page_title'] or row['page_url']}]({row['page_url']})")
        md.append(f"  - Screenshot: `{rel_shot}`")
        md.append(f"  - Highlight count: {row['highlight_count']}; score: {row['score']}")
    if not highlighted_rows:
        md.append("\nNo AI offering pages were captured.\n")

    md_path = ROOT / "README.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {summary_csv}")
    print(f"Wrote {ai_csv}")
    print(f"Wrote {highlighted_csv}")
    print(f"Wrote {md_path}")
    print(f"vendors={len(roster)} crawl_records={len(crawl_records)} ai_pages={len(ai_rows)} highlighted_pages={len(highlighted_rows)}")


if __name__ == "__main__":
    main()
