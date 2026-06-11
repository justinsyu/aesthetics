import urllib.request
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
SUPP = ROOT / "supplements"
SUPP_TEXT = ROOT / "extracted_text" / "supplements"
SUPP.mkdir(exist_ok=True)
SUPP_TEXT.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

SUPPLEMENTS = [
    (
        "khanani_2022_jama_brolucizumab_supplement.pdf",
        "https://pmc.ncbi.nlm.nih.gov/articles/instance/8613703/bin/jamaophthalmol-e214585-s001.pdf",
    ),
    (
        "gallivan_2023_view_supplementary_material_1.pdf",
        "https://pmc.ncbi.nlm.nih.gov/articles/instance/10748734/bin/NIHMS1952437-supplement-Supplementary_Material_1.pdf",
    ),
    (
        "gallivan_2023_view_supplementary_material_2.pdf",
        "https://pmc.ncbi.nlm.nih.gov/articles/instance/10748734/bin/NIHMS1952437-supplement-Supplementary_Material_2.pdf",
    ),
]


def download(url, target):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as res:
        data = res.read()
        ctype = res.headers.get("content-type", "")
    target.write_bytes(data)
    return ctype, len(data)


def extract(path):
    reader = PdfReader(str(path))
    out = []
    for idx, page in enumerate(reader.pages, start=1):
        out.append(f"\n\n--- Page {idx} ---\n")
        out.append(page.extract_text() or "")
    target = SUPP_TEXT / (path.stem + ".txt")
    target.write_text("".join(out), encoding="utf-8", errors="ignore")
    return target


def main():
    for name, url in SUPPLEMENTS:
        target = SUPP / name
        ctype, size = download(url, target)
        text_target = extract(target)
        print(f"{name}\t{size}\t{ctype}\t{text_target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
