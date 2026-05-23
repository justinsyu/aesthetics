import asyncio
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE = Path("/Users/justinyu/Desktop/linkedin-posts/outputs/hcp_site_audit")
TMP = BASE / "tmp_worker_3"
URLS_TSV = TMP / "chunk_3_urls.tsv"
PROGRESS_JSONL = TMP / "chunk_3_progress.jsonl"
PARTIAL_CSV = TMP / "partial_chunk_3_progress.csv"
FINAL_CSV = BASE / "chunk_3.csv"

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

CHROME_CAVEAT = "Codex Chrome plugin callable API unavailable in worker; used Playwright/headless HTTP fallback."

OVERRIDES = {
    "hcp.myairduo.com": ("AIRDUO DIGIHALER / AIRDUO RESPICLICK", "fluticasone propionate and salmeterol inhalation powder", "Teva"),
    "jatenzohcp.com": ("JATENZO", "testosterone undecanoate", "Tolmar"),
    "organonpro.com": ("RENFLEXIS", "infliximab-abda", "Organon"),
    "www.jubliarx.com": ("JUBLIA", "efinaconazole topical solution 10%", "Bausch Health"),
    "www.remicadehcp.com": ("REMICADE", "infliximab", "Janssen Biotech"),
    "galafoldhcp.com": ("GALAFOLD", "migalastat", "Amicus Therapeutics"),
    "vevye.com": ("VEVYE", "cyclosporine ophthalmic solution 0.1%", "Harrow"),
    "actimmunehcp.com": ("ACTIMMUNE", "interferon gamma-1b", "Amgen"),
    "alymsys.us": ("ALYMSYS", "bevacizumab-maly", "Amneal"),
    "aristadahcp.com": ("ARISTADA", "aripiprazole lauroxil", "Alkermes"),
    "avycaz.com": ("AVYCAZ", "ceftazidime and avibactam", "AbbVie"),
    "biktarvyhcp.com": ("BIKTARVY", "bictegravir, emtricitabine, and tenofovir alafenamide", "Gilead Sciences"),
    "breyanzihcp.com": ("BREYANZI", "lisocabtagene maraleucel", "Bristol Myers Squibb"),
    "camcevihcp.com": ("CAMCEVI", "leuprolide mesylate", "Accord BioPharma"),
    "comirnatyhcp.pfizerpro.com": ("COMIRNATY", "COVID-19 Vaccine, mRNA", "Pfizer and BioNTech"),
    "daliresphcp.com": ("DALIRESP", "roflumilast", "AstraZeneca"),
    "dovatohcp.com": ("DOVATO", "dolutegravir and lamivudine", "ViiV Healthcare"),
    "enjaymohcp.com": ("ENJAYMO", "sutimlimab-jome", "Sanofi"),
    "equetro.com": ("EQUETRO", "carbamazepine", "Validus Pharmaceuticals"),
    "fetroja.com": ("FETROJA", "cefiderocol", "Shionogi"),
    "halaven.com": ("HALAVEN", "eribulin mesylate", "Eisai"),
    "hcp.euflexxa.com": ("EUFLEXXA", "1% sodium hyaluronate", "Ferring Pharmaceuticals"),
    "hemlibra-hcp.com": ("HEMLIBRA", "emicizumab-kxwh", "Genentech"),
    "invegasustennahcp.com": ("INVEGA SUSTENNA", "paliperidone palmitate", "Janssen"),
    "leqviohcp.com": ("LEQVIO", "inclisiran", "Novartis"),
    "ninlarohcp.com": ("NINLARO", "ixazomib", "Takeda Oncology"),
    "ongentyshcp.com": ("ONGENTYS", "opicapone", "Neurocrine Biosciences"),
    "pavblu.com": ("PAVBLU", "aflibercept-ayyh", "Amgen"),
    "skyrizihcp.com": ("SKYRIZI", "risankizumab-rzaa", "AbbVie"),
    "ultomirishcp.com": ("ULTOMIRIS", "ravulizumab-cwvz", "Alexion"),
    "vyzultahcp.com": ("VYZULTA", "latanoprostene bunod ophthalmic solution", "Bausch + Lomb"),
    "pro.campus.sanofi": ("CEREZYME", "imiglucerase", "Sanofi"),
    "inqovi.com": ("INQOVI", "decitabine and cedazuridine", "Taiho Oncology"),
    "kesimptahcp.com": ("KESIMPTA", "ofatumumab", "Novartis"),
    "lioresal.com": ("LIORESAL", "baclofen", "Saol Therapeutics"),
    "lupronprostatecancer.com": ("LUPRON DEPOT", "leuprolide acetate", "AbbVie"),
    "mvasi.com": ("MVASI", "bevacizumab-awwb", "Amgen"),
    "onivyde.com": ("ONIVYDE", "irinotecan liposome injection", "Ipsen"),
    "orenitramhcp.com": ("ORENITRAM", "treprostinil", "United Therapeutics"),
    "poteligeohcp.com": ("POTELIGEO", "mogamulizumab-kpkc", "Kyowa Kirin"),
    "rinvoqhcp.com": ("RINVOQ", "upadacitinib", "AbbVie"),
    "shingrixhcp.com": ("SHINGRIX", "zoster vaccine recombinant, adjuvanted", "GSK"),
    "syfovreecp.com": ("SYFOVRE", "pegcetacoplan", "Apellis Pharmaceuticals"),
    "tecelra-hcp.com": ("TECELRA", "afamitresgene autoleucel", "Adaptimmune"),
    "tremfyahcp.com": ("TREMFYA", "guselkumab", "Janssen"),
    "valchlorhcp.com": ("VALCHLOR", "mechlorethamine gel", "Helsinn Therapeutics"),
    "venoferhcp.com": ("VENOFER", "iron sucrose", "American Regent"),
    "vowsthcp.com": ("VOWST", "fecal microbiota spores, live-brpk", "Nestle Health Science"),
    "xywavhcp.com": ("XYWAV", "calcium, magnesium, potassium, and sodium oxybates", "Jazz Pharmaceuticals"),
    "zonisade.com": ("ZONISADE", "zonisamide oral suspension", "Azurity Pharmaceuticals"),
    "suflave.com": ("SUFLAVE", "polyethylene glycol 3350, sodium sulfate, potassium chloride, magnesium sulfate, and sodium chloride", "Braintree Laboratories"),
    "www.xerese.com": ("XERESE", "acyclovir and hydrocortisone cream", "Bausch Health"),
    "www.imaavyhcp.com": ("IMAAVY", "nipocalimab-aahu", "Johnson & Johnson"),
    "www.avastin.com": ("AVASTIN", "bevacizumab", "Genentech"),
    "www.katerzia.com": ("KATERZIA", "amlodipine oral suspension", "Azurity Pharmaceuticals"),
    "qinlockhcp.com": ("QINLOCK", "ripretinib", "Deciphera Pharmaceuticals"),
    "www.symbicorttouchpoints.com": ("SYMBICORT", "budesonide and formoterol fumarate dihydrate", "AstraZeneca"),
    "www.luzurx.com": ("LUZU", "luliconazole cream 1%", "Bausch Health"),
    "www.hectorol.com": ("HECTOROL", "doxercalciferol", "Sanofi"),
    "www.methylphenidateer72.com": ("Methylphenidate HCl Extended-Release Tablets", "methylphenidate hydrochloride", ""),
    "www.herceptin.com": ("HERCEPTIN", "trastuzumab", "Genentech"),
    "www.dalvance.com": ("DALVANCE", "dalbavancin", "AbbVie"),
    "www.heronconnect.com": ("SUSTOL", "granisetron extended-release injection", "Heron Therapeutics"),
    "octagam-10.pfizerpro.com": ("OCTAGAM 10%", "immune globulin intravenous (human)", "Octapharma"),
    "www.pfizermedical.com": ("ERAXIS", "anidulafungin", "Pfizer"),
    "www.ryanodex.com": ("RYANODEX", "dantrolene sodium", "Eagle Pharmaceuticals"),
    "exxuahcp.com": ("EXXUA", "gepirone extended-release", "Fabre-Kramer"),
    "www.nuzyra.com": ("NUZYRA", "omadacycline", "Paratek Pharmaceuticals"),
    "penthrox.co.uk": ("PENTHROX", "methoxyflurane", "Medical Developments International"),
    "www.privigen.com": ("PRIVIGEN", "immune globulin intravenous (human), 10% liquid", "CSL Behring"),
    "www.caldolor.com": ("CALDOLOR", "ibuprofen injection", "Cumberland Pharmaceuticals"),
    "www.iclusig.com": ("ICLUSIG", "ponatinib", "Takeda Oncology"),
    "www.qelbreehcp.com": ("QELBREE", "viloxazine extended-release capsules", "Supernus Pharmaceuticals"),
    "www.novomedlink.com": ("VICTOZA", "liraglutide", "Novo Nordisk"),
    "www.sareptadmd.com": ("EXONDYS 51", "eteplirsen", "Sarepta Therapeutics"),
    "payercoverage.ziextenzo.com": ("ZIEXTENZO", "pegfilgrastim-bmez", "Sandoz"),
    "tirosintsol.com": ("TIROSINT-SOL", "levothyroxine sodium", "IBSA Pharma"),
    "www.rylazepro.com": ("RYLAZE", "asparaginase erwinia chrysanthemi (recombinant)-rywn", "Jazz Pharmaceuticals"),
    "www.baxdela.com": ("BAXDELA", "delafloxacin", "Melinta Therapeutics"),
    "www.sarclisahcp.com": ("SARCLISA", "isatuximab-irfc", "Sanofi"),
    "hylenex.com": ("HYLENEX", "hyaluronidase human injection", "Halozyme"),
    "cystaran.com": ("CYSTARAN", "cysteamine ophthalmic solution", "Leadiant Biosciences"),
    "www.rhogam.com": ("RhoGAM", "Rho(D) immune globulin (human)", "Kedrion Biopharma"),
    "daurismo.pfizerpro.com": ("DAURISMO", "glasdegib", "Pfizer"),
    "penbraya.pfizerpro.com": ("PENBRAYA", "meningococcal groups A, B, C, W, and Y vaccine", "Pfizer"),
    "www.amjevitapro.com": ("AMJEVITA", "adalimumab-atto", "Amgen"),
    "www.lotemaxointment.com": ("LOTEMAX", "loteprednol etabonate ophthalmic ointment", "Bausch + Lomb"),
    "www.gene.com": ("NUTROPIN AQ", "somatropin", "Genentech"),
    "www.us.adakveo.com": ("ADAKVEO", "crizanlizumab-tmca", "Novartis"),
    "www.perjeta-hcp.com": ("PERJETA", "pertuzumab", "Genentech"),
    "www.ziextenzo.com": ("ZIEXTENZO", "pegfilgrastim-bmez", "Sandoz"),
    "vaxchora.com": ("VAXCHORA", "cholera vaccine, live, oral", "Bavarian Nordic"),
    "zomig.com": ("ZOMIG", "zolmitriptan", ""),
    "www.evekeo.com": ("EVEKEO", "amphetamine sulfate", "Azurity Pharmaceuticals"),
    "www.adthyza.com": ("ADTHYZA", "thyroid tablets", "Azurity Pharmaceuticals"),
    "vivimusta.azuritysolutions.com": ("VIVIMUSTA", "bendamustine hydrochloride", "Eagle Pharmaceuticals"),
    "www.rebyotahcp.com": ("REBYOTA", "fecal microbiota, live-jslm", "Ferring Pharmaceuticals"),
    "kloxxado.com": ("KLOXXADO", "naloxone hydrochloride", "Hikma"),
    "www.hetliozpro.com": ("HETLIOZ", "tasimelteon", "Vanda Pharmaceuticals"),
    "www.trulance.com": ("TRULANCE", "plecanatide", "Salix Pharmaceuticals"),
    "www.xofluza-hcp.com": ("XOFLUZA", "baloxavir marboxil", "Genentech"),
    "www.gammagard.com": ("GAMMAGARD LIQUID", "immune globulin infusion (human)", "Takeda"),
    "www.columvi-hcp.com": ("COLUMVI", "glofitamab-gxbm", "Genentech"),
    "www.rituxan.com": ("RITUXAN", "rituximab", "Genentech and Biogen"),
    "www.daytrana.com": ("DAYTRANA", "methylphenidate transdermal system", "Noven Therapeutics"),
    "www.karbinaler.com": ("KARBINAL ER", "carbinoxamine maleate", "Tris Pharma"),
    "www.endometrin.com": ("ENDOMETRIN", "progesterone vaginal insert", "Ferring Pharmaceuticals"),
    "www.gamunex-c.com": ("GAMUNEX-C", "immune globulin injection (human), 10%", "Grifols"),
}

RWE_PATTERNS = [
    (r"\breal[- ]world evidence\b", "real-world evidence"),
    (r"\breal[- ]world data\b", "real-world data"),
    (r"\breal[- ]world\b", "real-world"),
    (r"\bobservational\b", "observational"),
    (r"\bregistry\b", "registry"),
    (r"\bclaims database\b", "claims database"),
    (r"\badministrative claims\b", "administrative claims"),
    (r"\bclaims data\b", "claims data"),
    (r"\bretrospective\b", "retrospective"),
    (r"\bphase 4\b", "phase 4"),
    (r"\bphase iv\b", "phase IV"),
    (r"\bpost[- ]marketing\b", "post-marketing"),
    (r"\bchart review\b", "chart review"),
    (r"\bcase series\b", "case series"),
]


def load_urls():
    rows = []
    for line in URLS_TSV.read_text().splitlines():
        idx, flag, url = line.split("\t", 2)
        rows.append({"corpus_index": idx, "rwe_prompt_flag": flag, "input_url": url})
    return rows


def normalize_hex(value):
    value = value.strip().lower()
    if len(value) == 4:
        value = "#" + "".join(ch * 2 for ch in value[1:])
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return value.upper()
    return None


def rgb_to_hex(match):
    nums = [int(float(x)) for x in match.groups()[:3]]
    if any(x < 0 or x > 255 for x in nums):
        return None
    return "#{:02X}{:02X}{:02X}".format(*nums)


def luminance(hex_color):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def extract_colors(html, computed_colors):
    colors = []
    for val in re.findall(r"#[0-9a-fA-F]{3,6}\b", html or ""):
        hx = normalize_hex(val)
        if hx:
            colors.append(hx)
    for m in re.finditer(r"rgba?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)", html or ""):
        hx = rgb_to_hex(m)
        if hx:
            colors.append(hx)
    for val in computed_colors or []:
        if isinstance(val, str):
            for m in re.finditer(r"rgba?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)", val):
                hx = rgb_to_hex(m)
                if hx:
                    colors.append(hx)
            hx = normalize_hex(val) if val.startswith("#") else None
            if hx:
                colors.append(hx)
    skip = {"#FFFFFF", "#000000", "#F8F8F8", "#F9F9F9", "#FAFAFA", "#F5F5F5", "#EEEEEE", "#EDEDED", "#CCCCCC", "#333333", "#222222", "#111111"}
    counts = Counter(c for c in colors if c not in skip)
    ranked = [c for c, _ in counts.most_common() if 20 < luminance(c) < 245]
    if not ranked:
        ranked = [c for c, _ in Counter(colors).most_common() if c not in {"#FFFFFF", "#000000"}]
    scheme = ranked[:6]
    return scheme


def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def extract_text_info(html, title, url):
    soup = BeautifulSoup(html or "", "lxml")
    metas = []
    for meta in soup.find_all("meta"):
        name = (meta.get("name") or meta.get("property") or "").lower()
        if any(k in name for k in ["description", "title", "og:title"]):
            metas.append(meta.get("content") or "")
    visible = soup.get_text(" ", strip=True)
    text_blob = clean_text(" ".join([title or "", *metas, visible[:10000]]))
    host = urlparse(url).netloc.lower().removeprefix("www.")
    brand, generic, company = "", "", ""
    for key, val in OVERRIDES.items():
        if host == key or host.endswith("." + key) or key in url:
            brand, generic, company = val
            break
    if not brand:
        m = re.search(r"\b([A-Z][A-Z0-9-]{2,}(?:\s+[A-Z0-9-]{2,})?)\b(?:\s*\(|\s+for|\s+HCP|\s+Official|\s+-)", text_blob)
        if m:
            brand = m.group(1).strip()
    if not generic:
        m = re.search(r"\(([^)]{3,90})\)", text_blob)
        if m and not re.search(r"HCP|healthcare|patient|PDF|USA|US", m.group(1), re.I):
            generic = m.group(1).strip()
    if not company:
        for name in [
            "Pfizer", "Sanofi", "AbbVie", "Genentech", "Novartis", "Gilead", "Janssen",
            "Bristol Myers Squibb", "Takeda", "AstraZeneca", "Amgen", "Eisai", "Jazz",
            "Ferring", "Bausch", "Bausch + Lomb", "Novo Nordisk", "GSK", "Merck",
            "Teva", "Organon", "Ipsen", "UCB", "Alkermes", "Supernus", "Azurity",
            "Sarepta", "Grifols", "CSL Behring", "Octapharma",
        ]:
            if re.search(r"\b" + re.escape(name) + r"\b", text_blob, re.I):
                company = name
                break
    return brand, generic, company, text_blob


def assess_rwe(text):
    found = []
    low = text.lower()
    for pattern, label in RWE_PATTERNS:
        if re.search(pattern, low, re.I):
            found.append(label)
    unique = []
    for f in found:
        if f not in unique:
            unique.append(f)
    if any(f in unique for f in ["real-world evidence", "real-world data", "observational", "registry", "claims database", "administrative claims", "claims data", "phase 4"]):
        assessment = "yes"
    elif unique:
        assessment = "possible"
    else:
        assessment = "not found"
    return assessment, "; ".join(unique[:8])


async def page_extract(browser, item, sem):
    async with sem:
        input_url = item["input_url"]
        page = await browser.new_page(viewport={"width": 1366, "height": 900})
        final_url = input_url
        status = "ok"
        html = ""
        title = ""
        computed = []
        notes = [CHROME_CAVEAT, f"corpus_index={item['corpus_index']}"]
        try:
            resp = await page.goto(input_url, wait_until="domcontentloaded", timeout=25000)
            if resp:
                status = str(resp.status)
            await page.wait_for_timeout(2500)
            # Common HCP/continue gates are clicked only when visible.
            for selector in [
                "text=/continue/i",
                "text=/enter/i",
                "text=/yes/i",
                "button:has-text('Accept')",
                "button:has-text('I Agree')",
            ]:
                try:
                    loc = page.locator(selector).first
                    if await loc.is_visible(timeout=600):
                        await loc.click(timeout=1200)
                        await page.wait_for_timeout(900)
                        break
                except Exception:
                    pass
            final_url = page.url
            title = await page.title()
            html = await page.content()
            computed = await page.evaluate(
                """() => Array.from(document.querySelectorAll('body *')).slice(0, 700).flatMap(el => {
                    const s = getComputedStyle(el);
                    return [s.color, s.backgroundColor, s.borderTopColor];
                }).filter(Boolean)"""
            )
        except Exception as e:
            status = "error"
            notes.append(f"playwright_error={type(e).__name__}: {str(e)[:140]}")
            try:
                r = requests.get(input_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                status = str(r.status_code)
                final_url = r.url
                html = r.text
                title = BeautifulSoup(html, "lxml").title.string if BeautifulSoup(html, "lxml").title else ""
                notes.append("requests_fallback_used")
            except Exception as e2:
                notes.append(f"requests_error={type(e2).__name__}: {str(e2)[:140]}")
        finally:
            await page.close()

        colors = extract_colors(html, computed)
        brand, generic, company, text_blob = extract_text_info(html, title, final_url or input_url)
        rwe_assessment, rwe_terms = assess_rwe(text_blob)
        if not colors:
            notes.append("color extraction limited/no non-neutral CSS colors found")
        if not brand:
            notes.append("brand not confidently extracted")
        return {
            "input_url": input_url,
            "final_url": final_url,
            "status": status,
            "brand_name": brand,
            "generic_name": generic,
            "company": company,
            "color_scheme_hex": "; ".join(colors),
            "primary_hex": colors[0] if len(colors) > 0 else "",
            "secondary_hex": colors[1] if len(colors) > 1 else "",
            "accent_hex": colors[2] if len(colors) > 2 else "",
            "rwe_prompt_flag": item["rwe_prompt_flag"],
            "rwe_assessment": rwe_assessment,
            "rwe_evidence_terms": rwe_terms,
            "notes": " ".join(notes),
        }


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


async def main():
    items = load_urls()
    results_by_url = {}
    if PROGRESS_JSONL.exists():
        for line in PROGRESS_JSONL.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                results_by_url[row["input_url"]] = row

    pending = [i for i in items if i["input_url"] not in results_by_url]
    sem = asyncio.Semaphore(4)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [asyncio.create_task(page_extract(browser, item, sem)) for item in pending]
        completed = 0
        for coro in asyncio.as_completed(tasks):
            row = await coro
            results_by_url[row["input_url"]] = row
            with PROGRESS_JSONL.open("a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            ordered = [results_by_url[i["input_url"]] for i in items if i["input_url"] in results_by_url]
            write_csv(PARTIAL_CSV, ordered)
            completed += 1
            print(f"{len(results_by_url)}/{len(items)} {row['status']} {row['input_url']}", flush=True)
        await browser.close()

    ordered = [results_by_url[i["input_url"]] for i in items]
    write_csv(FINAL_CSV, ordered)
    print(f"WROTE {len(ordered)} rows to {FINAL_CSV}")


if __name__ == "__main__":
    asyncio.run(main())
