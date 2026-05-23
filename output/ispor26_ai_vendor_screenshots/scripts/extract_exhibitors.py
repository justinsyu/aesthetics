#!/usr/bin/env python3
import csv
import html
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


BASE = "https://n1b.goexposoftware.com/events/ispor26/goExpo/"
LIST_URL = urljoin(BASE, "exhibitor/listExhibitorProfiles.php")
OUT_DIR = Path(__file__).resolve().parents[1] / "data"


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 ISPOR exhibitor research"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def textify(node) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip() if node else ""


def extract_website(soup: BeautifulSoup) -> str:
    labels = soup.select(".exhibitorExtra")
    for idx, label in enumerate(labels):
        label_text = textify(label).lower().rstrip(":")
        if "website" in label_text and idx + 1 < len(labels):
            link = labels[idx + 1].find("a", href=True)
            if link:
                return link["href"].strip()

    for a in soup.find_all("a", href=True):
        href = html.unescape(a["href"]).strip()
        visible = textify(a)
        if href.startswith(("http://", "https://")):
            if "goexposoftware.com" not in href and "core-apps.com" not in href and "ispor.org" not in href:
                return href
        if visible.startswith(("http://", "https://", "www.")):
            return visible if visible.startswith("http") else f"https://{visible}"
    return ""


def decode_cfemail(value: str) -> str:
    try:
        key = int(value[:2], 16)
        chars = [chr(int(value[i : i + 2], 16) ^ key) for i in range(2, len(value), 2)]
        return "".join(chars)
    except Exception:
        return ""


def extract_emails(soup: BeautifulSoup) -> list[str]:
    emails = set()
    for span in soup.select("span.__cf_email__[data-cfemail]"):
        decoded = decode_cfemail(span.get("data-cfemail", ""))
        if decoded and "@" in decoded:
            emails.add(decoded.lower())
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("mailto:"):
            emails.add(href.split(":", 1)[1].split("?", 1)[0].lower())
    return sorted(emails)


def extract_profile(profile_url: str) -> dict:
    body = fetch(profile_url)
    soup = BeautifulSoup(body, "html.parser")
    title = textify(soup.select_one(".col-lg-4 img"))
    if not title:
        img = soup.select_one(".col-lg-4 img[alt]")
        title = img.get("alt", "").strip() if img else ""

    booth = ""
    booth_label = soup.find(string=re.compile(r"Booth:"))
    if booth_label:
        booth_parent = booth_label.parent.parent if booth_label.parent else None
        booth = textify(booth_parent).replace("Booth:", "").strip()

    about = ""
    long = soup.select_one(".longString")
    short = soup.select_one(".shortString")
    if long:
        about = textify(long)
    elif short:
        about = textify(short)

    categories = [textify(li) for li in soup.select("ul.ffListHelper li") if textify(li)]
    emails = extract_emails(soup)
    email_domains = sorted({email.rsplit("@", 1)[1] for email in emails if "@" in email})
    return {
        "profile_url": profile_url,
        "display_name": title,
        "booth": booth,
        "event_about": about,
        "categories": categories,
        "profile_emails": emails,
        "profile_email_domains": email_domains,
        "profile_website": extract_website(soup),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    list_html = fetch(LIST_URL)
    (OUT_DIR / "event_exhibitor_list.html").write_text(list_html, encoding="utf-8")
    soup = BeautifulSoup(list_html, "html.parser")
    rows = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "viewExhibitorProfile.php?__id=" not in href:
            continue
        profile_url = urljoin(BASE, href)
        if profile_url in seen:
            continue
        seen.add(profile_url)
        rows.append({"display_name": textify(a), "profile_url": profile_url})

    enriched = []
    for idx, row in enumerate(rows, start=1):
        print(f"[{idx}/{len(rows)}] {row['display_name']}", flush=True)
        try:
            profile = extract_profile(row["profile_url"])
            row.update({k: v for k, v in profile.items() if v or k not in row})
        except Exception as exc:
            row["profile_error"] = repr(exc)
        enriched.append(row)
        time.sleep(0.08)

    json_path = OUT_DIR / "ispor26_exhibitors.json"
    csv_path = OUT_DIR / "ispor26_exhibitors.csv"
    json_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["display_name", "booth", "categories", "event_about", "profile_url", "profile_website", "profile_error"],
        )
        writer.writeheader()
        for item in enriched:
            writer.writerow({k: item.get(k, "") for k in writer.fieldnames})
    print(f"Wrote {len(enriched)} exhibitors to {json_path} and {csv_path}")


if __name__ == "__main__":
    main()
