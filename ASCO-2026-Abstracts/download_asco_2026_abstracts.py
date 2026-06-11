#!/usr/bin/env python3
"""Download 2026 ASCO Annual Meeting abstract search results.

The ASCO search page embeds a public GraphQL2 endpoint and token in its
server-rendered Angular state. This script reads that state, then pages through
the MultiSearch API and writes the results as JSONL plus a compact CSV index.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SEARCH_URL = (
    "https://www.asco.org/annual-meeting/search?"
    "filters=%7B%22mediaTypes%22:%5B%22Abstracts%22%5D%7D&"
    "userInput=&sortBy=Relevancy&contentKey=ANNUAL_MEETING&contentKeyYear=2026"
)

QUERY = """
query MultiSearch($input: MultiSearchInput!) {
  search(input: $input) {
    status
    result {
      total
      hits {
        uid
        isExternal
        contentType
        styleType
        contentId
        contentSourceId
        presentationId
        journalName
        meetingName
        titles
        doi
        summary
        status
        abstractNumber
        posterBoardNumber
        body
        title
        highlights {
          body
          title
        }
        primaryPerson {
          displayName
          role
        }
        date {
          start
          end
          timeZone
        }
        meeting {
          contentId
          name
          year
        }
        publishDate {
          start
          end
          timeZone
        }
        lastUpdated {
          start
          end
          timeZone
        }
        contentUrl {
          path
          target
          title
          fqdn
          fragment
          queryParams
        }
        thumbnailUrl {
          path
          target
          title
          fqdn
          fragment
          queryParams
        }
        taxonomy {
          subjectsThes
          genesThes
          drugsThes
          orgThes
          entitiesThes
          countriesThes
        }
        relatedMaterials {
          title
          contentId
          contentType
          contentSourceId
          sessionType
          contentUrl {
            path
            target
            title
            fqdn
            fragment
            queryParams
          }
        }
        deadlineDate {
          start
          end
          timeZone
        }
        hasAbstract
        hasPosters
        hasSlides
        hasVideos
        cursor {
          uid
          score
          startDate
          dateTimePublished
          sessionTypeWeight
          primaryTrack
          abstractNumber
        }
      }
      filters {
        type
        buckets {
          key
          displayName
          doc_count
        }
      }
    }
    errors {
      code
      message
    }
    __typename
  }
}
""".strip()


def request_json(url: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers or {}, method="GET" if data is None else "POST")
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def request_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")


def load_config(search_url: str) -> dict[str, Any]:
    page = request_text(search_url)
    match = re.search(r'<script id="ng-state" type="application/json">(.*?)</script>', page, re.S)
    if not match:
        raise RuntimeError("Could not find Angular ng-state JSON on the ASCO search page.")
    state = json.loads(html.unescape(match.group(1)))
    return state["CONFIG_KEY"]


def fetch_page(endpoint: str, token: str, offset: int, size: int, retries: int) -> dict[str, Any]:
    payload = {
        "operationName": "MultiSearch",
        "variables": {
            "input": {
                "userInput": "*",
                "filters": {"mediaTypes": ["Abstracts"]},
                "sortBy": "Relevancy",
                "contentKey": "ANNUAL_MEETING",
                "contentKeyYear": 2026,
                "from": offset,
                "size": size,
            }
        },
        "query": QUERY,
    }
    headers = {
        "authorization": token,
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
    }
    for attempt in range(retries + 1):
        try:
            response = request_json(endpoint, payload, headers)
            if "errors" in response:
                raise RuntimeError(json.dumps(response["errors"], ensure_ascii=False))
            search = response["data"]["search"]
            if search["status"] != "SUCCESS":
                raise RuntimeError(json.dumps(search.get("errors"), ensure_ascii=False))
            return search["result"]
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            if attempt >= retries:
                raise
            sleep_for = 2**attempt
            print(f"retry offset={offset} after {sleep_for}s: {exc}", file=sys.stderr)
            time.sleep(sleep_for)
    raise RuntimeError("unreachable")


def full_url(content_url: dict[str, Any] | None) -> str:
    if not content_url:
        return ""
    fqdn = content_url.get("fqdn") or "www.asco.org"
    path = content_url.get("path") or ""
    return f"https://{fqdn}{path}" if path else ""


def write_outputs(out_dir: Path, records: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "abstracts.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    fields = [
        "uid",
        "contentId",
        "abstractNumber",
        "title",
        "primaryPerson",
        "meetingName",
        "meetingYear",
        "url",
        "summary",
    ]
    with (out_dir / "abstracts_index.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "uid": record.get("uid", ""),
                    "contentId": record.get("contentId", ""),
                    "abstractNumber": record.get("abstractNumber", ""),
                    "title": record.get("title", ""),
                    "primaryPerson": (record.get("primaryPerson") or {}).get("displayName", ""),
                    "meetingName": record.get("meetingName", ""),
                    "meetingYear": (record.get("meeting") or {}).get("year", ""),
                    "url": full_url(record.get("contentUrl")),
                    "summary": record.get("summary", ""),
                }
            )

    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="ASCO-2026-Abstracts")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0, help="Optional record limit for testing.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    config = load_config(SEARCH_URL)
    endpoint = config["api2"]["uri"]
    token = config["api2"]["authorization"]

    records: list[dict[str, Any]] = []
    filters: list[dict[str, Any]] = []
    total = None
    offset = 0

    while True:
        result = fetch_page(endpoint, token, offset, args.page_size, args.retries)
        total = int(result["total"])
        if not filters:
            filters = result.get("filters") or []
        hits = result.get("hits") or []
        if not hits:
            break
        records.extend(hits)
        print(f"downloaded {len(records)}/{total}", file=sys.stderr)
        if args.limit and len(records) >= args.limit:
            records = records[: args.limit]
            break
        offset += len(hits)
        if offset >= total:
            break
        time.sleep(args.sleep)

    manifest = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sourceUrl": SEARCH_URL,
        "endpoint": endpoint,
        "operationName": "MultiSearch",
        "pagination": {"from": 0, "size": args.page_size, "actualRecords": len(records), "reportedTotal": total},
        "variables": {
            "userInput": "*",
            "filters": {"mediaTypes": ["Abstracts"]},
            "sortBy": "Relevancy",
            "contentKey": "ANNUAL_MEETING",
            "contentKeyYear": 2026,
        },
        "filters": filters,
        "outputs": ["abstracts.jsonl", "abstracts_index.csv"],
    }
    write_outputs(out_dir, records, manifest)
    print(f"wrote {len(records)} records to {out_dir}", file=sys.stderr)
    return 0 if total is None or len(records) == total or args.limit else 1


if __name__ == "__main__":
    raise SystemExit(main())
