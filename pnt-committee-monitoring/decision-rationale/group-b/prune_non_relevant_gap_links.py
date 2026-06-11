from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

import fill_capped_group_b_gaps as gap_fill


OUT = Path(__file__).resolve().parent
MANIFEST_CSV = OUT / "manifest.csv"
MANIFEST_JSON = OUT / "manifest.json"

PRUNE_URL_PARTS = [
    "Doula-Project_Recommendations.pdf",
    "bulletins-banner-pages-and-reference-modules",
    "/business-transactions/billing-and-remittance/code-sets",
    "/contact-information/portal-links-for-providers",
    "/clinical-services/long-term-care",
    "in.gov/recovery/indiana-initiatives",
    "law.cornell.edu/rules/frap",
    "law.cornell.edu/rules/frcp",
    "law.cornell.edu/rules/frcrmp",
    "law.cornell.edu/rules/frbp",
    "law.cornell.edu/wex/category/criminal_law_and_procedure",
    "iowamedicaidpdl.com/content/iowamedicaidpdl/en",
    "info-letters-provider-info/latest-news",
    "info-letters-provider-info/listserv",
    "fax-confidentiality-certificate",
    "billing/340b.html",
    "billing/faq.html",
    "billing/Payer-Sheet.html",
    "mainecarepdl.org/content/mainecarepdl/en/contact.html",
    "mainecarepdl.org/content/mainecarepdl/en/payer-sheets.html",
    "mainecarepdl.org/content/mainecarepdl/en/smac.html",
    "mainecarepdl.org/content/dam/ffs-medicare/me/pdl/cash-waiver-form.pdf",
    "mainecarepdl.org/content/dam/ffs-medicare/me/reversal-form.pdf",
]

PRUNE_EXACT_URLS = {
    "https://www.mainecarepdl.org/",
    "https://www.mainecarepdl.org/content/mainecarepdl/en",
}


def read_rows() -> list[gap_fill.ManifestRow]:
    with MANIFEST_CSV.open(newline="", encoding="utf-8") as f:
        return [gap_fill.ManifestRow(**row) for row in csv.DictReader(f)]


def should_prune(row: gap_fill.ManifestRow) -> bool:
    if row.status != "saved_after_capped_gap_fill":
        return False
    if not row.source_role.startswith("linked from capped seed:"):
        return False
    if row.url in PRUNE_EXACT_URLS:
        return True
    return any(part.lower() in row.url.lower() for part in PRUNE_URL_PARTS)


def delete_local_file(relative_path: str) -> None:
    if not relative_path:
        return
    target = (OUT / relative_path).resolve()
    if OUT.resolve() not in target.parents:
        raise RuntimeError(f"Refusing to delete outside group-b: {target}")
    if target.exists() and target.is_file():
        target.unlink()


def main() -> None:
    rows = read_rows()
    keep: list[gap_fill.ManifestRow] = []
    pruned: list[gap_fill.ManifestRow] = []
    for row in rows:
        if should_prune(row):
            delete_local_file(row.file_path)
            delete_local_file(row.text_path)
            pruned.append(row)
        else:
            keep.append(row)

    MANIFEST_JSON.write_text(json.dumps([asdict(row) for row in keep], indent=2), encoding="utf-8")
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(gap_fill.ManifestRow.__annotations__.keys()))
        writer.writeheader()
        for row in keep:
            writer.writerow(asdict(row))
    gap_fill.write_summary(keep)
    print(f"pruned={len(pruned)} remaining_rows={len(keep)}")


if __name__ == "__main__":
    main()
