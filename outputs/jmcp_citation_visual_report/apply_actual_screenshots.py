from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path(r"C:\Users\Justin\Desktop\linkedin-posts-mac\outputs\jmcp_citation_visual_report")
ASSETS = ROOT / "assets"
HTML = ROOT / "jmcp_citation_validation_visual_report.html"


def box_image(src: str, dst: str, boxes: list[tuple[int, int, int, int]], fill=(255, 240, 138, 90)) -> None:
    img = Image.open(ASSETS / src).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    for box in boxes:
        draw.rounded_rectangle(box, radius=8, fill=fill, outline=(216, 74, 50, 255), width=5)
    Image.alpha_composite(img, overlay).convert("RGB").save(ASSETS / dst)


box_image(
    "actual_jmcp_717_scroll_clip.png",
    "actual_jmcp_717_body_ref31_highlight.png",
    [(175, 56, 1115, 183), (728, 143, 774, 176)],
)

box_image(
    "actual_pubmed_40446757_local.png",
    "actual_pubmed_40446757_highlight.png",
    [(310, 320, 710, 348), (140, 350, 612, 374), (138, 395, 842, 496)],
)

Image.open(ASSETS / "actual_pubmed_40446757_highlight.png").crop((120, 300, 875, 640)).save(
    ASSETS / "actual_pubmed_40446757_highlight_crop.png"
)
Image.open(ASSETS / "actual_jmcp_717_body_ref31_highlight.png").crop((130, 35, 1160, 365)).save(
    ASSETS / "actual_jmcp_717_body_ref31_highlight_crop.png"
)

box_image(
    "actual_crossref_ncsme_query.png",
    "actual_crossref_ncsme_query_highlight.png",
    [(0, 0, 1278, 42), (432, 310, 994, 346)],
)

text = HTML.read_text(encoding="utf-8")
text = text.replace(
    'src="assets/source_flagged_ncsme.png"',
    'src="assets/actual_crossref_ncsme_query_highlight.png"',
)
text = text.replace(
    'src="assets/search_flagged_ncsme.png"',
    'src="assets/actual_bing_ncsme_codebook.png"',
)
text = text.replace(
    'src="assets/actual_pmc_ncsme_2015.png"',
    'src="assets/actual_bing_ncsme_codebook.png"',
)
text = text.replace(
    "NCSME-PR codebook citation was not located online",
    "Searches located adjacent NCSME records, not the cited 2021 codebook",
)
text = text.replace(
    "Exact title, NCSME-PR Codebook, and author/title searches did not locate the 2021 codebook. Related 2015 survey publications were found, but not this cited 2021 codebook.",
    "Crossref and web searches located adjacent published articles and 2015 NCSME material, but not the cited 2021 codebook.",
)
text = text.replace(
    'src="assets/source_flagged_majd.png"',
    'src="assets/actual_jmcp_717_body_ref31_highlight_crop.png"',
)
text = text.replace(
    'src="assets/search_flagged_majd.png"',
    'src="assets/actual_pubmed_40446757_highlight_crop.png"',
)
text = text.replace(
    'src="assets/actual_jmcp_717_body_ref31_highlight.png"',
    'src="assets/actual_jmcp_717_body_ref31_highlight_crop.png"',
)
text = text.replace(
    'src="assets/actual_pubmed_40446757_highlight.png"',
    'src="assets/actual_pubmed_40446757_highlight_crop.png"',
)
text = text.replace(
    "University of Houston 2022 work was not located online",
    "Current source evidence points to a matching 2025 Majd article",
)
text = text.replace(
    "Exact dissertation or University of Houston 2022 title was not located. Searches found a related 2025 journal article with similar title, not the cited 2022 work.",
    "The live JMCP article body cites the prior Majd study, and PubMed lists a matching article with the same title family, 2025 publication year, PMID 40446757, and DOI 10.1016/j.jdiacomp.2025.109080.",
)
HTML.write_text(text, encoding="utf-8")

manifest = ROOT / "sources" / "reference-screenshots.csv"
manifest.write_text(
    "\n".join(
        [
            "label,path,caption",
            f"Reference 1 - JMCP issue source set,{ASSETS / 'source_issue_scope.png'},Issue source set and extraction selector context.",
            f"Reference 2 - NCSME Crossref query,{ASSETS / 'actual_crossref_ncsme_query_highlight.png'},Actual Crossref API query screenshot for the cited NCSME codebook search.",
            f"Reference 3 - NCSME Bing exact-title query,{ASSETS / 'actual_bing_ncsme_codebook.png'},Actual Bing screenshot showing no exact search results for the cited 2021 codebook title.",
            f"Reference 4 - JMCP article body citation,{ASSETS / 'actual_jmcp_717_body_ref31_highlight_crop.png'},Actual JMCP article screenshot showing the body citation to the prior Majd study.",
            f"Reference 5 - PubMed likely correction,{ASSETS / 'actual_pubmed_40446757_highlight_crop.png'},Actual PubMed screenshot showing matching 2025 article metadata.",
        ]
    )
    + "\n",
    encoding="utf-8",
)
