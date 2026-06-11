#!/usr/bin/env python
"""Extract page-level text from a searchable conference PDF."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def extract_with_pymupdf(path: Path) -> list[dict[str, Any]]:
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise SystemExit("PyMuPDF is required for this helper. Install with: python -m pip install pymupdf") from exc

    pages: list[dict[str, Any]] = []
    with fitz.open(path) as doc:
        for index, page in enumerate(doc):
            text = page.get_text("text").strip()
            pages.append(
                {
                    "page_number": index + 1,
                    "text": text,
                    "char_count": len(text),
                    "extraction_method": "pymupdf_text",
                }
            )
    return pages


def write_text_dump(pages: list[dict[str, Any]], path: Path) -> None:
    chunks: list[str] = []
    for page in pages:
        chunks.append(f"===== Page {page['page_number']} =====")
        chunks.append(page["text"])
        chunks.append("")
    path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--text-out", type=Path)
    args = parser.parse_args()

    if not args.pdf_path.exists():
        raise SystemExit(f"PDF not found: {args.pdf_path}")

    pages = extract_with_pymupdf(args.pdf_path)
    payload = {
        "source_pdf": str(args.pdf_path),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "page_count": len(pages),
        "pages_with_text": sum(1 for page in pages if page["text"]),
        "pages": pages,
    }
    output = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.json_out:
        args.json_out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    if args.text_out:
        write_text_dump(pages, args.text_out)
    if payload["pages_with_text"] == 0:
        print("No text was extracted. This PDF may require OCR.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
