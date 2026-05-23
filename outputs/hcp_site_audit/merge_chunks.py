#!/usr/bin/env python3
import csv
from pathlib import Path


BASE = Path(__file__).resolve().parent
FIELDS = [
    "input_url",
    "final_url",
    "status",
    "brand_name",
    "generic_name",
    "company",
    "color_scheme_hex",
    "primary_hex",
    "secondary_hex",
    "accent_hex",
    "rwe_prompt_flag",
    "rwe_assessment",
    "rwe_evidence_terms",
    "notes",
]


def main() -> None:
    seen = set()
    rows = []
    warnings = []

    for path in sorted(BASE.glob("chunk_*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != FIELDS:
                warnings.append(
                    f"{path.name}: schema mismatch {reader.fieldnames!r}"
                )
            for row in reader:
                normalized = {field: (row.get(field) or "").strip() for field in FIELDS}
                key = normalized["input_url"].rstrip("/")
                if not key:
                    warnings.append(f"{path.name}: skipped row without input_url")
                    continue
                if key in seen:
                    warnings.append(f"{path.name}: duplicate skipped {normalized['input_url']}")
                    continue
                seen.add(key)
                rows.append(normalized)

    out_path = BASE / "hcp_site_color_drug_rwe_audit.csv"
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    report_path = BASE / "merge_report.txt"
    report_path.write_text(
        "\n".join(
            [
                f"chunks={len(list(BASE.glob('chunk_*.csv')))}",
                f"rows={len(rows)}",
                "warnings:",
                *warnings,
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"wrote {out_path} ({len(rows)} rows)")
    print(f"wrote {report_path} ({len(warnings)} warnings)")


if __name__ == "__main__":
    main()
