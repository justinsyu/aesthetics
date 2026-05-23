#!/usr/bin/env python3
"""Download public EU drug-pricing source files and write manifests."""

from __future__ import annotations

import csv
import hashlib
import http.client
import json
import mimetypes
import os
import re
import ssl
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD_DIR = ROOT / "downloads"
MANIFEST_DIR = ROOT / "manifest"
LOG_DIR = ROOT / "logs"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
)


@dataclass(frozen=True)
class Source:
    country: str
    label: str
    url: str
    kind: str
    note: str = ""
    navigation_url: str = ""


SOURCES = [
    Source("Austria", "Austria source 1", "https://www.sozialversicherung.at/cdscontent/load?contentid=10008.802603&version=1776774123", "direct"),
    Source("Austria", "Austria source 2", "https://www.sozialversicherung.at/cdscontent/load?contentid=10008.802601&version=1776774148", "direct"),
    Source("Belgium", "SAM v2 full download", "https://www.vas.ehealth.fgov.be/websamcivics/samcivics/download/samv2-download?type=FULL&xsd=5&version=11964", "direct"),
    Source("Bulgaria", "NCPR register", "https://portal.ncpr.bg/registers/pages/register/list-medicament.xhtml", "interactive", "Interactive register; no direct public bulk file in supplied link list."),
    Source("Croatia", "HALMED published medicine prices", "https://www.halmed.hr/fdsak3jnFsk1Kfa/ostale_stranice/Zbirni-popis-objavljenih-cijena-lijekova-7356-svi.xlsx", "direct"),
    Source("Cyprus", "MOH drug price list", "https://www.moh.gov.cy/moh/phs/phs.nsf/All/ED7050D4BFEA2CF8C2258B6D00316E8C/$file/%CE%A4%CE%B9%CE%BC%CE%BF%CE%BA%CE%B1%CF%84%CE%AC%CE%BB%CE%BF%CE%B3%CE%BF%CF%82_%CE%942024_02.08.2024_(25.07.2024)_WEB_EL.xlsx", "direct"),
    Source("Czech", "SUKL SCAU zip", "https://sukl.gov.cz/wp-content/uploads/2026/04/SCAU260501v21.zip", "direct"),
    Source("Denmark", "Medicinpriser", "https://www.medicinpriser.dk/Default.aspx?lng=2", "interactive", "Interactive price-search page; no direct public bulk file in supplied link list."),
    Source("Estonia", "Ravimiregister", "https://www.ravimiregister.ee/en/default.aspx?pv=HumRavimid.Otsing", "interactive", "Interactive register; no direct public bulk file in supplied link list."),
    Source("Finland", "Kanta medicine database latest", "https://www.kanta.fi/kantafi-rest/kantafi-laaketietokanta/download/latest", "direct"),
    Source("France", "BDPM CIS/CIP text", "https://base-donnees-publique.medicaments.gouv.fr/download/file/CIS_CIP_bdpm.txt", "direct"),
    Source("Germany", "BfArM Festbeträge PDF", "https://www.bfarm.de/SharedDocs/Downloads/DE/Arzneimittel/Zulassung/amInformationen/Festbetraege/2026/festbetraege-20260501.pdf?__blob=publicationFile", "direct_pdf", "Downloaded only if no same-dataset spreadsheet alternative is found."),
    Source("Greece", "MOH revised price bulletin", "https://www.moh.gov.gr/articles/times-farmakwn/deltia-timwn/13924-deltio-anathewrhmenwn-timwn-farmakwn-anthrwpinhs-xrhshs-dekembrioy-2025?fdl=30389", "direct"),
    Source("Hungary", "NEAK PUPHA", "https://www.neak.gov.hu/pfile/file?inline=true&path=%2Fletoltheto%2FATFO_dok%2Fgyogyszer%2FPUPHA%2FPUPHA_20260501_v4_javitott.zip1", "direct"),
    Source("Ireland", "SSPCRS drug list", "https://www.sspcrs.ie/druglist/pub", "interactive", "Interactive/export page; no direct public bulk file in supplied link list."),
    Source("Italy", "AIFA equivalent medicines", "https://www.aifa.gov.it/documents/20142/3688205/Lista_farmaci_equivalenti_15.05.2026.xls", "direct"),
    Source("Latvia", "NVD media download", "https://www.vmnvd.gov.lv/lv/media/42932/download?attachment=", "direct"),
    Source("Lithuania", "E-TAR legal act", "https://www.e-tar.lt/portal/lt/legalAct/a38a8e74c96211f08918e1adc7c5b1ec", "interactive", "Legal/interactive page; no direct public bulk pricing file in supplied link list."),
    Source("Luxembourg", "CNS positive list CSV", "https://cns.public.lu/dam-assets/legislations/texte-coordonne/liste-positive/2605/2605-liste-pos.csv", "direct"),
    Source("Malta", "Medicines Authority local search export", "https://medicinesauthority.gov.mt/Exports/Local/AdvancedSearchResultsLocal.xls", "direct", "Supplied as non-pricing; downloaded because it is a direct public spreadsheet link."),
    Source("Netherlands", "Medicijnkosten", "https://www.medicijnkosten.nl/zoeken", "interactive", "Interactive price-search page; no direct public bulk file in supplied link list."),
    Source("Poland", "Gov.pl attachment", "https://www.gov.pl/attachment/e8aafc4d-a517-48e9-8147-deabe255cfbc", "direct"),
    Source("Portugal", "Infarmed search", "https://extranet.infarmed.pt/CITS-pesquisamedicamento-fo/pesquisaMedicamento.jsf", "interactive", "Interactive medicine-search page; no direct public bulk file in supplied link list."),
    Source("Romania", "National public catalogue", "https://ms.ro/media/documents/05.11.2025_Catalogul_public_national_al_preturilor_maximale_ale_medicamentelor.xlsx", "direct"),
    Source("Slovakia", "Categorized medicines list", "https://www.health.gov.sk/Zdroje?/Sources/kategorizacia/zkl/202605/cast_A_zoznam_liekov_N_k_01_05_2026.xlsx", "direct"),
    Source("Slovenia", "JAZMP prices", "https://www.jazmp.si/fileadmin/datoteke/seznami/SFE/Cene/cene_20260501.xlsx", "direct"),
    Source("Spain", "Nomenclator Excel", "https://www.sanidad.gob.es/profesionales/nomenclator.do?metodo=nomenclatorExcel", "direct"),
    Source("Sweden", "TLV medprice", "https://www.tlv.se/file/medprice", "direct"),
]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def host_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def filename_from_content_disposition(header: Optional[str]) -> Optional[str]:
    if not header:
        return None
    star = re.search(r"filename\*=([^']*)''([^;]+)", header, flags=re.I)
    if star:
        return Path(unquote(star.group(2))).name
    plain = re.search(r'filename="?([^";]+)"?', header, flags=re.I)
    if plain:
        return Path(unquote(plain.group(1))).name
    return None


def filename_from_url(url: str) -> Optional[str]:
    name = Path(unquote(urlparse(url).path)).name
    return name or None


def sniff_extension(data: bytes, content_type: str) -> str:
    lower = content_type.lower().split(";")[0].strip()
    if data.startswith(b"PK\x03\x04"):
        return ".zip"
    if data.startswith(b"\xd0\xcf\x11\xe0"):
        return ".xls"
    if data.startswith(b"%PDF"):
        return ".pdf"
    if lower in {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel.sheet.macroenabled.12",
    }:
        return ".xlsx"
    if lower in {"application/vnd.ms-excel", "application/msexcel"}:
        return ".xls"
    if lower in {"text/csv", "application/csv"}:
        return ".csv"
    if lower.startswith("text/plain"):
        return ".txt"
    guessed = mimetypes.guess_extension(lower)
    return guessed or ""


def known_suffix(name: Optional[str]) -> str:
    if not name:
        return ""
    suffix = Path(name).suffix.lower()
    if suffix in {".xlsx", ".xls", ".csv", ".txt", ".zip", ".pdf", ".xml"}:
        return suffix
    if suffix == ".zip1":
        return ".zip"
    return ""


def preferred_file_extension(name: Optional[str], data: bytes, content_type: str) -> str:
    suffix = known_suffix(name)
    if suffix:
        return suffix
    sniffed = sniff_extension(data, content_type)
    if sniffed:
        return sniffed
    if name:
        suffix = Path(name).suffix
        if suffix:
            return suffix
    return ".bin"


def is_html_body(data: bytes) -> bool:
    stripped = data[:512].lstrip().lower()
    return stripped.startswith(b"<!doctype html") or stripped.startswith(b"<html")


def safe_filename(source: Source, response_name: Optional[str], data: bytes, content_type: str) -> str:
    ext = preferred_file_extension(response_name or filename_from_url(source.url), data, content_type)
    base = f"{slugify(source.country)}__{slugify(source.label)}"
    return f"{base}{ext}"


def download(source: Source) -> dict[str, object]:
    req = Request(source.url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    started = datetime.now(timezone.utc).isoformat()
    last_error: Optional[Exception] = None
    for attempt in range(1, 4):
        try:
            try:
                response_obj = urlopen(req, timeout=90)
            except URLError as exc:
                if isinstance(exc.reason, ssl.SSLCertVerificationError):
                    context = ssl._create_unverified_context()
                    response_obj = urlopen(req, timeout=90, context=context)
                else:
                    raise
            with response_obj as response:
                final_url = response.geturl()
                status_code = getattr(response, "status", 200)
                headers = response.headers
                content_type = headers.get("Content-Type", "")
                content_disposition = headers.get("Content-Disposition", "")
                try:
                    data = response.read()
                except http.client.IncompleteRead as exc:
                    raise RuntimeError(f"Incomplete response body on attempt {attempt}: {exc}") from exc
            break
        except Exception as exc:
            last_error = exc
            if attempt == 3:
                raise
    else:
        raise RuntimeError(f"Download failed: {last_error!r}")

    if status_code >= 400:
        raise RuntimeError(f"HTTP {status_code}")
    if not data:
        raise RuntimeError("Empty response body")

    if is_html_body(data):
        snippet = data[:300].decode("utf-8", errors="replace").replace("\n", " ")
        raise RuntimeError(f"Received HTML page instead of a bulk file: {snippet}")

    response_name = filename_from_content_disposition(content_disposition)
    filename = safe_filename(source, response_name, data, content_type)
    output_path = DOWNLOAD_DIR / filename
    output_path.write_bytes(data)

    sha256 = hashlib.sha256(data).hexdigest()
    return {
        "status": "downloaded",
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": status_code,
        "content_type": content_type,
        "content_disposition": content_disposition,
        "final_url": final_url,
        "download_path": str(output_path.relative_to(ROOT)),
        "filename": filename,
        "bytes": len(data),
        "sha256": sha256,
        "error": "",
    }


def row_for_source(source: Source) -> dict[str, object]:
    parsed = urlparse(source.url)
    return {
        "country": source.country,
        "label": source.label,
        "kind": source.kind,
        "source_url": source.url,
        "direct_file_url": source.url if source.kind.startswith("direct") else "",
        "navigation_url": source.navigation_url or source.url,
        "host_url": host_url(source.url),
        "host": parsed.netloc,
        "note": source.note,
        "status": "",
        "started_at_utc": "",
        "completed_at_utc": "",
        "http_status": "",
        "content_type": "",
        "content_disposition": "",
        "final_url": "",
        "download_path": "",
        "filename": "",
        "bytes": "",
        "sha256": "",
        "error": "",
    }


def write_manifests(rows: list[dict[str, object]]) -> tuple[Path, Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = MANIFEST_DIR / f"eu_drug_pricing_manifest_{timestamp}.csv"
    json_path = MANIFEST_DIR / f"eu_drug_pricing_manifest_{timestamp}.json"
    if not rows:
        raise RuntimeError("No manifest rows to write")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return csv_path, json_path


def main() -> int:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for source in SOURCES:
        print(f"{source.country}: {source.label}", file=sys.stderr, flush=True)
        row = row_for_source(source)
        if source.kind == "interactive":
            row["status"] = "metadata_only"
            row["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            rows.append(row)
            continue
        if source.kind == "direct_pdf" and os.environ.get("DOWNLOAD_GERMANY_PDF") != "1":
            row["status"] = "deferred_pdf"
            row["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            row["error"] = "Germany PDF deferred pending spreadsheet-alternative check."
            rows.append(row)
            continue

        try:
            result = download(source)
            row.update(result)
        except Exception as exc:
            row["status"] = "failed"
            row["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            row["error"] = repr(exc)
            if isinstance(exc, HTTPError):
                row["http_status"] = exc.code
        rows.append(row)

    csv_path, json_path = write_manifests(rows)
    latest_csv = MANIFEST_DIR / "latest_manifest.csv"
    latest_json = MANIFEST_DIR / "latest_manifest.json"
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")

    downloaded = sum(1 for row in rows if row["status"] == "downloaded")
    failed = sum(1 for row in rows if row["status"] == "failed")
    metadata_only = sum(1 for row in rows if row["status"] == "metadata_only")
    print(f"CSV manifest: {csv_path}")
    print(f"JSON manifest: {json_path}")
    print(f"Downloaded: {downloaded}; failed: {failed}; metadata-only: {metadata_only}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
