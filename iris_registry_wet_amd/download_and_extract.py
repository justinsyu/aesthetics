import json
import re
import tarfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
DOWNLOADS = ROOT / "downloads"
SOURCES = ROOT / "sources"
TEXT = ROOT / "extracted_text"

for directory in (DOWNLOADS, SOURCES, TEXT):
    directory.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


ITEMS = [
    {
        "slug": "rao_2018_real_world_vision_single_antivegf",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, lines 366-368",
        "title": "Real-World Vision in Age-Related Macular Degeneration Patients Treated with Single Anti-VEGF Drug Type for 1 Year in the IRIS Registry",
        "year": 2018,
        "pmid": "29146306",
        "doi": "10.1016/j.ophtha.2017.10.010",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/29146306/",
            "https://doi.org/10.1016/j.ophtha.2017.10.010",
        ],
        "qualification": "nAMD patients treated with bevacizumab, ranibizumab, or aflibercept monotherapy in IRIS Registry.",
    },
    {
        "slug": "ho_2020_baseline_va_wet_amd",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 327",
        "title": "Baseline Visual Acuity at Wet AMD Diagnosis Predicts Long-Term Vision Outcomes: An Analysis of the IRIS Registry",
        "year": 2020,
        "pmid": "33231696",
        "doi": "10.3928/23258160-20201104-05",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/33231696/",
            "https://doi.org/10.3928/23258160-20201104-05",
            "https://experts.umn.edu/en/publications/baseline-visual-acuity-at-wet-amd-diagnosis-predicts-long-term-vi/",
        ],
        "qualification": "IRIS Registry wet AMD/nAMD diagnosis cohort evaluating baseline VA and long-term outcomes.",
    },
    {
        "slug": "khanani_2022_brolucizumab_safety",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 293",
        "title": "Safety Outcomes of Brolucizumab in Neovascular Age-Related Macular Degeneration: Results From the IRIS Registry and Komodo Healthcare Map",
        "year": 2022,
        "pmid": "34817566",
        "pmcid": "PMC8613703",
        "doi": "10.1001/jamaophthalmol.2021.4585",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/34817566/",
            "https://jamanetwork.com/journals/jamaophthalmology/fullarticle/2786559",
        ],
        "qualification": "nAMD brolucizumab safety analysis using IRIS Registry, with Komodo comparator database.",
    },
    {
        "slug": "maccumber_2023_cjo_antivegf_wet_amd",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 291",
        "title": "Antivascular endothelial growth factor agents for wet age-related macular degeneration: an IRIS registry analysis",
        "year": 2023,
        "pmid": "34863677",
        "doi": "10.1016/j.jcjo.2021.10.008",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/34863677/",
            "https://www.sciencedirect.com/science/article/pii/S0008418221003951",
        ],
        "qualification": "Wet AMD patients receiving anti-VEGF injections in IRIS Registry; treatment patterns and outcomes.",
    },
    {
        "slug": "gallivan_2023_view_emulation",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 257; Verana publication page",
        "title": "Emulating VIEW 1 and VIEW 2 Clinical Trial Outcome Data Using the American Academy of Ophthalmology IRIS Registry",
        "year": 2023,
        "pmid": "36626210",
        "pmcid": "PMC10748734",
        "doi": "10.3928/23258160-20221214-01",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/36626210/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10748734/",
            "https://veranahealth.com/verana-health-study-using-curated-real-world-data-to-replicate-phase-iii-ophthalmology-clinical-trial-published-in-osli-retina/",
        ],
        "qualification": "IRIS Registry nAMD cohort used to emulate VIEW wet AMD trial eligibility, treatment regimens, and endpoints.",
    },
    {
        "slug": "khurana_2023_ltfu_namd",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 237",
        "title": "Loss to Follow-up in Patients with Neovascular Age-Related Macular Degeneration Treated with Anti-VEGF Therapy in the United States in the IRIS Registry",
        "year": 2023,
        "pmid": "36858288",
        "doi": "10.1016/j.ophtha.2023.02.021",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/36858288/",
            "https://doi.org/10.1016/j.ophtha.2023.02.021",
        ],
        "qualification": "Treatment-naive nAMD patients treated with anti-VEGF in IRIS Registry; LTFU and nonpersistence outcomes.",
    },
    {
        "slug": "maccumber_2023_brolucizumab_interval_extension",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 167",
        "title": "Factors Linked to Injection Interval Extension in Eyes with Wet Age-Related Macular Degeneration Switched to Brolucizumab",
        "year": 2023,
        "pmid": "36990322",
        "doi": "10.1016/j.ophtha.2023.03.017",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/36990322/",
            "https://doi.org/10.1016/j.ophtha.2023.03.017",
            "https://scholars.houstonmethodist.org/en/publications/factors-linked-to-injection-interval-extension-in-eyes-with-wet-a",
        ],
        "qualification": "IRIS Registry wet AMD eyes switched to brolucizumab; interval-extension outcome.",
    },
    {
        "slug": "maccumber_2023_one_year_brolucizumab",
        "include": True,
        "format": "manuscript/poster antecedent noted",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 145",
        "title": "One-Year Brolucizumab Outcomes in Neovascular Age-Related Macular Degeneration from a Large United States Cohort in the IRIS Registry",
        "year": 2023,
        "pmid": "37086857",
        "doi": "10.1016/j.ophtha.2023.04.012",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/37086857/",
            "https://www.sciencedirect.com/science/article/abs/pii/S0161642023002774",
        ],
        "qualification": "IRIS Registry nAMD brolucizumab-treated cohort; one-year effectiveness and treatment-pattern outcomes.",
    },
    {
        "slug": "rahimy_2023_ga_progression_with_namd_fellow_eye",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 151",
        "title": "Progression of Geographic Atrophy: Retrospective Analysis of Patients from the IRIS Registry",
        "year": 2023,
        "pmid": "37274013",
        "pmcid": "PMC10232896",
        "doi": "10.1016/j.xops.2023.100318",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/37274013/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10232896/",
        ],
        "qualification": "GA cohort explicitly stratified by fellow-eye nAMD and evaluated new-onset nAMD/vision outcomes.",
    },
    {
        "slug": "hunt_2022_environmental_factors_amd",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 243",
        "title": "Association of Environmental Factors with Age-Related Macular Degeneration using the Intelligent Research in Sight Registry",
        "year": 2022,
        "pmid": "",
        "pmcid": "PMC9754968",
        "doi": "10.1016/j.xops.2022.100195",
        "landing_urls": [
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC9754968/",
            "https://doi.org/10.1016/j.xops.2022.100195",
        ],
        "qualification": "IRIS Registry analysis modeling exudative and active exudative AMD versus nonexudative/no AMD.",
    },
    {
        "slug": "wykoff_2024_six_year_antivegf_namd",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 133",
        "title": "Impact of Anti-VEGF Treatment and Patient Characteristics on Vision Outcomes in Neovascular Age-related Macular Degeneration: Up to 6-Year Analysis of the AAO IRIS Registry",
        "year": 2024,
        "pmid": "38187126",
        "pmcid": "PMC10767511",
        "doi": "10.1016/j.xops.2023.100421",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/38187126/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10767511/",
        ],
        "qualification": "Large IRIS Registry nAMD anti-VEGF cohort; treatment patterns and VA outcomes up to 6 years.",
    },
    {
        "slug": "gong_2024_fellow_eye_conversion",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 71",
        "title": "Fellow Eyes Conversion Rates in Patients With Unilateral Exudative Age-Related Macular Degeneration: An Academy IRIS Registry Analysis",
        "year": 2024,
        "pmid": "38319061",
        "doi": "10.3928/23258160-20240125-01",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/38319061/",
            "https://visualize.jove.com/38319061-fellow-eyes-conversion-rates-in-patients-with-unilateral-exudative-age-related-macular-degeneration-an-academy-irissupsup-registry-analysis",
        ],
        "qualification": "Unilateral exudative AMD cohort in IRIS Registry; fellow-eye conversion outcome.",
    },
    {
        "slug": "zarbin_2024_brolucizumab_safety",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 81",
        "title": "Real-World Safety Outcomes with Brolucizumab in Neovascular Age-Related Macular Degeneration: Findings from the IRIS Registry",
        "year": 2024,
        "pmid": "38520643",
        "pmcid": "PMC11039576",
        "doi": "10.1007/s40123-024-00920-3",
        "pdf_urls": ["https://link.springer.com/content/pdf/10.1007/s40123-024-00920-3.pdf"],
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/38520643/",
            "https://link.springer.com/article/10.1007/s40123-024-00920-3",
        ],
        "qualification": "IRIS Registry nAMD brolucizumab safety cohort followed up to two years.",
    },
    {
        "slug": "fevrier_2024_catt_emulation",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "AAO IRIS Registry Data Analysis page, line 87",
        "title": "Comparison of Methods of Clinical Trial Emulation Utilizing Data From the Comparison of AMD Treatment Trial (CATT) and the IRIS Registry",
        "year": 2024,
        "pmid": "38881608",
        "pmcid": "PMC11179401",
        "doi": "10.1016/j.xops.2024.100524",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/38881608/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11179401/",
        ],
        "qualification": "IRIS Registry treatment-naive nAMD eyes used to emulate CATT PRN arms and compare VA outcomes.",
    },
    {
        "slug": "ali_2025_faricimab_early_outcomes",
        "include": True,
        "format": "manuscript / evolved from ARVO FARETINA poster",
        "aao_evidence": "Current PubMed/publisher search; Verana nAMD publications page references FARETINA-AMD",
        "title": "Early Outcomes After Initiation of Faricimab for Neovascular Age-Related Macular Degeneration",
        "year": 2025,
        "pmid": "40371970",
        "doi": "10.3928/23258160-20250304-02",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/40371970/",
            "https://iovs.arvojournals.org/article.aspx?articleid=2787245",
            "https://veranahealth.com/products/namd/",
        ],
        "qualification": "FARETINA/IRIS Registry faricimab nAMD outcomes; identified as a current publication successor to ARVO abstract.",
    },
    {
        "slug": "acharya_2025_disparities_antivegf_initiation",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "Current PubMed/publisher search; not visible on saved AAO list",
        "title": "Disparities in Presentation and Anti-VEGF Therapy Initiation for Neovascular Age-Related Macular Degeneration: An Analysis of the Academy IRIS Registry",
        "year": 2025,
        "pmid": "40738331",
        "doi": "10.1016/j.ophtha.2025.07.024",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/40738331/",
            "https://www.sciencedirect.com/science/article/abs/pii/S0161642025004580",
        ],
        "qualification": "Newly diagnosed nAMD patients in Academy IRIS Registry; presentation VA and anti-VEGF initiation disparities.",
    },
    {
        "slug": "barikian_2026_antivegf_exposure_outcomes",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "Current PubMed/publisher search; not visible on saved AAO list",
        "title": "Characteristics and Outcomes of Patients with Neovascular Age-Related Macular Degeneration by Anti-VEGF Exposure in United States Clinical Practice",
        "year": 2026,
        "pmid": "40614931",
        "doi": "10.1016/j.oret.2025.06.016",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/40614931/",
            "https://www.sciencedirect.com/science/article/pii/S2468653025003100",
        ],
        "qualification": "IRIS Registry newly diagnosed nAMD eyes; anti-VEGF exposure and one-year visual outcomes.",
    },
    {
        "slug": "tabano_2026_one_year_faricimab",
        "include": True,
        "format": "manuscript / conference-update lineage",
        "aao_evidence": "Current PubMed/publisher search; Roche/Genentech presentation links saved separately",
        "title": "One-year Real-world Outcomes With Faricimab in Neovascular Age-related Macular Degeneration",
        "year": 2026,
        "pmid": "41891889",
        "doi": "10.3928/23258160-20260302-02",
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/41891889/",
            "https://doi.org/10.3928/23258160-20260302-02",
        ],
        "qualification": "Current one-year nAMD faricimab outcomes analysis drawing on real-world IRIS-derived data.",
    },
    {
        "slug": "zhang_2026_endophthalmitis_biologics",
        "include": True,
        "format": "manuscript",
        "aao_evidence": "Current PubMed/publisher search; not visible on saved AAO list",
        "title": "Visual Outcomes Following Infectious Endophthalmitis from Intravitreal Injections of Biologic Drugs: An Intelligent Research in Sight Registry Retrospective Analysis",
        "year": 2026,
        "pmid": "42033607",
        "doi": "10.1007/s40123-026-01371-8",
        "pdf_urls": ["https://link.springer.com/content/pdf/10.1007/s40123-026-01371-8.pdf"],
        "landing_urls": [
            "https://pubmed.ncbi.nlm.nih.gov/42033607/",
            "https://doi.org/10.1007/s40123-026-01371-8",
        ],
        "qualification": "IRIS Registry biologic-injection endophthalmitis study; includes neovascular/wet AMD subgroup among retinal indications.",
    },
    {
        "slug": "ashourizadeh_2026_cataract_conversion_preprint",
        "include": True,
        "format": "preprint / AAO 2025 presentation topic",
        "aao_evidence": "Current preprint search; AAO 2025 presentation coverage found via Vumedi",
        "title": "Cataract Surgery and the Risk of Conversion from Dry to Neovascular Age-related Macular Degeneration in the IRIS Registry",
        "year": 2026,
        "doi": "10.21203/rs.3.rs-5505014/v2",
        "landing_urls": [
            "https://www.researchsquare.com/article/rs-5505014/v2",
            "https://sciety.org/articles/activity/10.21203/rs.3.rs-5505014/v1",
        ],
        "qualification": "IRIS Registry dry AMD cohort with conversion to neovascular AMD as the primary outcome.",
    },
    {
        "slug": "leng_2024_arvo_namd_ga_antivegf_presentation",
        "include": True,
        "format": "presentation PDF",
        "aao_evidence": "Public Verana/ARVO presentation PDF",
        "title": "IRIS Registry Analysis of Anti-VEGF Treatment in Patients With Coexisting Neovascular Age-Related Macular Degeneration and Geographic Atrophy",
        "year": 2024,
        "pdf_urls": ["https://veranahealth.com/wp-content/uploads/2024/05/Leng_ARVO-2024_nAMD-IRIS-Registry_Presentation_disclosure.pdf"],
        "landing_urls": ["https://veranahealth.com/wp-content/uploads/2024/05/Leng_ARVO-2024_nAMD-IRIS-Registry_Presentation_disclosure.pdf"],
        "qualification": "ARVO 2024 presentation using IRIS Registry nAMD + GA anti-VEGF treatment data.",
    },
    {
        "slug": "asrs_2022_conversion_rates_poster",
        "include": True,
        "format": "poster PDF",
        "aao_evidence": "Public ASRS Wet AMD meeting PDF",
        "title": "Conversion Rates from Nonexudative to Exudative Age-Related Macular Degeneration: An AAO IRIS Registry Analysis",
        "year": 2022,
        "pdf_urls": ["https://www.asrs.org/content/documents/wet-amd-1.pdf"],
        "landing_urls": ["https://www.asrs.org/content/documents/wet-amd-1.pdf"],
        "qualification": "Conference/poster material evaluating conversion to exudative/wet AMD with AAO IRIS Registry data.",
    },
    {
        "slug": "leng_2021_asrs_long_term_antivegf_namd_presentation",
        "include": True,
        "format": "presentation PDF",
        "aao_evidence": "Public Genentech/ASRS 2021 presentation PDF",
        "title": "Long-term Experience With Intravitreal Anti-VEGF in Patients With nAMD: Analysis of Intelligent Research in Sight Registry",
        "year": 2021,
        "pdf_urls": ["https://medically.gene.com/content/dam/pdmahub/restricted/ophthalmology/asrs-2021/ASRS-2021-presentation-leng-long-term-experience-W-ith-intravitreal-anti-VEGF-in-patients-with-nAMD-analysis-of-intelligent-research-in-sight.pdf"],
        "landing_urls": ["https://medically.gene.com/content/dam/pdmahub/restricted/ophthalmology/asrs-2021/ASRS-2021-presentation-leng-long-term-experience-W-ith-intravitreal-anti-VEGF-in-patients-with-nAMD-analysis-of-intelligent-research-in-sight.pdf"],
        "qualification": "ASRS presentation antecedent to long-term anti-VEGF nAMD IRIS outcomes work.",
    },
    {
        "slug": "maccumber_2020_retina_society_brolucizumab_profiles",
        "include": True,
        "format": "poster PDF",
        "aao_evidence": "Public Retina Society meeting archive PDF",
        "title": "Profiles of Patients Who Initiated Brolucizumab for Neovascular (Wet) Age-related Macular Degeneration in the IRIS Registry",
        "year": 2020,
        "pdf_urls": ["https://www.retinasociety.org/content/meetingarchive/2020/maccumber-mathew-profiles-of-patients.pdf"],
        "landing_urls": ["https://www.retinasociety.org/content/meetingarchive/2020/maccumber-mathew-profiles-of-patients.pdf"],
        "qualification": "Retina Society poster using IRIS Registry wet AMD brolucizumab initiation cohort.",
    },
]


def urlopen(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(request, timeout=60)


def safe_name(text):
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return text[:180]


def download_url(url, target):
    try:
        with urlopen(url) as response:
            data = response.read()
            ctype = response.headers.get("Content-Type", "")
        target.write_bytes(data)
        return {"path": str(target.relative_to(ROOT)), "bytes": len(data), "content_type": ctype, "ok": True}
    except Exception as exc:
        return {"path": str(target.relative_to(ROOT)), "ok": False, "error": str(exc)}


def pmc_pdf_url(pmcid):
    api = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={urllib.parse.quote(pmcid)}"
    try:
        xml_text = urlopen(api).read().decode("utf-8")
        (SOURCES / f"oa_{pmcid}.xml").write_text(xml_text, encoding="utf-8")
        root = ET.fromstring(xml_text)
        for link in root.findall(".//link"):
            if link.attrib.get("format") == "pdf":
                href = link.attrib.get("href")
                return href.replace("ftp://ftp.ncbi.nlm.nih.gov", "https://ftp.ncbi.nlm.nih.gov")
    except Exception:
        return None
    return None


def fetch_pubmed_xml(pmids):
    pmids = [p for p in pmids if p]
    if not pmids:
        return {}
    ids = ",".join(pmids)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
    xml_text = urlopen(url).read().decode("utf-8")
    (SOURCES / "pubmed_efetch_manifest_items.xml").write_text(xml_text, encoding="utf-8")
    root = ET.fromstring(xml_text)
    records = {}
    for article in root.findall(".//PubmedArticle"):
        pmid_el = article.find(".//PMID")
        if pmid_el is None:
            continue
        pmid = pmid_el.text
        abstract_parts = []
        for abstract in article.findall(".//Abstract/AbstractText"):
            label = abstract.attrib.get("Label")
            text = "".join(abstract.itertext()).strip()
            if text:
                abstract_parts.append(f"{label}: {text}" if label else text)
        records[pmid] = {
            "abstract": "\n".join(abstract_parts),
            "xml": ET.tostring(article, encoding="unicode"),
        }
    for item in ITEMS:
        pmid = item.get("pmid")
        if pmid and pmid in records:
            (SOURCES / f"{item['slug']}_pubmed.xml").write_text(records[pmid]["xml"], encoding="utf-8")
            (SOURCES / f"{item['slug']}_abstract.txt").write_text(records[pmid]["abstract"], encoding="utf-8")
    return records


def extract_pdf_text(pdf_path):
    try:
        reader = PdfReader(str(pdf_path))
        parts = []
        for i, page in enumerate(reader.pages):
            try:
                parts.append(f"\n\n--- Page {i+1} ---\n" + (page.extract_text() or ""))
            except Exception as exc:
                parts.append(f"\n\n--- Page {i+1} extraction error: {exc} ---\n")
        out = TEXT / (pdf_path.stem + ".txt")
        out.write_text("".join(parts), encoding="utf-8", errors="ignore")
        return str(out.relative_to(ROOT))
    except Exception as exc:
        return f"ERROR: {exc}"


def main():
    pmids = [item.get("pmid") for item in ITEMS if item.get("pmid")]
    pubmed_records = fetch_pubmed_xml(pmids)
    results = []
    for item in ITEMS:
        item = dict(item)
        saved = []
        if item.get("pmcid"):
            pdf = pmc_pdf_url(item["pmcid"])
            if pdf:
                item.setdefault("pdf_urls", []).append(pdf)
        for url in item.get("pdf_urls", []):
            ext = ".pdf" if ".pdf" in urllib.parse.urlparse(url).path.lower() else ".bin"
            target = DOWNLOADS / f"{item['slug']}{ext}"
            result = download_url(url, target)
            result["source_url"] = url
            saved.append(result)
        if item.get("pmid") and item["pmid"] in pubmed_records:
            item["pubmed_abstract"] = pubmed_records[item["pmid"]]["abstract"]
        item["saved_files"] = saved
        results.append(item)

    for pdf in DOWNLOADS.glob("*.pdf"):
        text_path = extract_pdf_text(pdf)
        for item in results:
            for saved in item.get("saved_files", []):
                if saved.get("ok") and saved.get("path") == str(pdf.relative_to(ROOT)):
                    saved["extracted_text"] = text_path

    (ROOT / "publication_manifest.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    included_lines = []
    for item in results:
        if not item.get("include"):
            continue
        included_lines.append(
            f"- {item['year']} | {item['format']} | {item['title']} | DOI: {item.get('doi','')} | PMID: {item.get('pmid','')} | {item['qualification']}"
        )
    (ROOT / "publication_manifest.md").write_text(
        "# IRIS Registry Wet AMD / nAMD Publication Manifest\n\n"
        "Source root: AAO IRIS Registry Data Analysis page plus current PubMed/publisher/conference searches.\n\n"
        + "\n".join(included_lines)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"items": len(results), "pdfs": len(list(DOWNLOADS.glob('*.pdf')))}, indent=2))


if __name__ == "__main__":
    main()
