
import csv, json, re, ssl, html as html_lib, time
from pathlib import Path
from urllib.parse import urlparse, urljoin
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass

TMP = Path('/Users/justinyu/Desktop/linkedin-posts/outputs/hcp_site_audit/tmp_worker_0')
OUT = Path('/Users/justinyu/Desktop/linkedin-posts/outputs/hcp_site_audit/chunk_0.csv')
SELECTED = json.loads((TMP/'chunk_0_urls.json').read_text(encoding='utf-8'))
HEADER = ['input_url','final_url','status','brand_name','generic_name','company','color_scheme_hex','primary_hex','secondary_hex','accent_hex','rwe_prompt_flag','rwe_assessment','rwe_evidence_terms','notes']

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'

COMPANY_BY_HOST = {
    'pfizerpro.com':'Pfizer','pfizermedical.com':'Pfizer','organonpro.com':'Organon','tevapharm.com':'Teva','novomedlink.com':'Novo Nordisk','novologpro.com':'Novo Nordisk','ozempicpro.com':'Novo Nordisk','novonordisk':'Novo Nordisk','lilly.com':'Eli Lilly','gene.com':'Genentech','genentech':'Genentech','merckconnect.com':'Merck','merckvaccines.com':'Merck','sanofi':'Sanofi','bmscustomerconnect.com':'Bristol Myers Squibb','bms.com':'Bristol Myers Squibb','janssen':'Johnson & Johnson','jnj':'Johnson & Johnson','abbvie':'AbbVie','amgen':'Amgen','astrazeneca':'AstraZeneca','gilead':'Gilead Sciences','takeda':'Takeda','roche':'Roche','novartis':'Novartis','bayer':'Bayer','alexion':'Alexion','ucb':'UCB','biogen':'Biogen','galderma':'Galderma','bausch':'Bausch + Lomb','myalcon.com':'Alcon','mallinckrodt':'Mallinckrodt','therapeuticsmd':'TherapeuticsMD','fresenius-kabi.com':'Fresenius Kabi','octapharma':'Octapharma','grifols':'Grifols','cslbehring':'CSL Behring','campus.sanofi':'Sanofi'
}
COMPANY_NAMES = ['Pfizer','Teva','Takeda','TherapeuticsMD','Organon','Novo Nordisk','Bausch + Lomb','Bausch','Braeburn','Biogen','Galderma','Janssen','Johnson & Johnson','AbbVie','Bristol Myers Squibb','BMS','GSK','GlaxoSmithKline','Sanofi','Genentech','Roche','Novartis','Amgen','AstraZeneca','Merck','Gilead','Eli Lilly','Lilly','UCB','Bayer','CSL Behring','Grifols','Octapharma','Ferring','Ipsen','Daiichi Sankyo','Regeneron','Alnylam','Chiesi','Mallinckrodt','Alexion','Alcon','Fresenius Kabi','Amicus','Ardelyx','Jazz Pharmaceuticals','Sarepta','Otsuka','Sunovion','Ionis','Apellis','Horizon','Acadia','Astellas','Radius','Azurity','Purdue','Lantheus','Heron','Octapharma','Shionogi','Acrotech','Eagle Pharmaceuticals','Endo','Collegium','Alkermes']
RWE_PATTERNS = [
    ('real-world', r'\breal[ -]?world\b'), ('real-world evidence', r'\breal[ -]?world evidence\b'),
    ('RWE', r'\bRWE\b'), ('retrospective', r'\bretrospective\b'), ('observational', r'\bobservational\b'),
    ('claims', r'\bclaims\b'), ('registry', r'\bregistr(y|ies)\b'), ('phase 4', r'\bphase\s*4\b'),
    ('postmarketing', r'\bpost[ -]?marketing\b'), ('chart review', r'\bchart review\b'),
    ('database', r'\bdatabase\b'), ('EHR', r'\bEHR\b|electronic health records?')
]

COMMON_WORDS = set('hcp healthcare professional professionals patient patients prescribing information official site home resources support dosing efficacy safety treatment data clinical about for with and the from usa us'.split())

def session():
    s = requests.Session()
    s.headers.update({'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
    adapter = HTTPAdapter(max_retries=1, pool_connections=24, pool_maxsize=24)
    s.mount('http://', adapter); s.mount('https://', adapter)
    return s

S = session()

def fetch(url, timeout=14):
    try:
        r = S.get(url, timeout=timeout, allow_redirects=True, verify=False)
        return r.status_code, r.url, r.text or '', r.headers.get('content-type',''), ''
    except Exception as e:
        return 'error', url, '', '', type(e).__name__ + ': ' + str(e)[:160]

def visible_text_and_meta(doc):
    soup = BeautifulSoup(doc, 'lxml') if doc else BeautifulSoup('', 'lxml')
    title = (soup.title.string if soup.title and soup.title.string else '')
    metas = []
    for sel in [('name','description'),('property','og:description'),('name','twitter:description')]:
        tag = soup.find('meta', attrs={sel[0]: sel[1]})
        if tag and tag.get('content'): metas.append(tag.get('content'))
    for bad in soup(['script','style','noscript','svg']): bad.decompose()
    text = soup.get_text(' ', strip=True)
    return soup, clean(title), clean(' '.join(metas)), clean(text, 25000)

def clean(s, max_len=5000):
    return re.sub(r'\s+', ' ', html_lib.unescape(s or '')).strip()[:max_len]

def brand_from_url(url):
    u = urlparse(url)
    host = u.netloc.lower().replace('www.','')
    parts = [p for p in host.split('.') if p not in ('com','net','org','us','co','global')]
    token = parts[0] if parts else host
    path_parts = [p for p in u.path.split('/') if p]
    if 'products' in path_parts:
        token = path_parts[-1]
    elif host in ('medicalinformation.astrazeneca-us.com','www.gene.com','gene.com') and path_parts:
        token = path_parts[-1]
    token = re.sub(r'\.(html|asp)$','',token)
    token = re.sub(r'(hcp|pro|rx|ecp|usa|us)$','',token)
    token = token.replace('-hcp','').replace('hcp-','').replace('_','-')
    token = token.replace('xrhcp',' xr').replace('xrhcp',' xr')
    token = re.sub(r'[-]+',' ', token)
    token = re.sub(r'\b(main benchworks|payercoverage|medicalinformation)\b','', token).strip()
    return token.upper() if len(token) <= 6 else token.title()

def improve_brand(seed, title, text):
    sample = clean((title + ' ' + text[:2000]), 3000)
    # Brand often leads title before HCP/For/Official separators.
    first = re.split(r'\||-|–|—|:', title)[0].strip()
    first = re.sub(r'\b(HCP|Healthcare Professionals?|Official.*)$','', first, flags=re.I).strip()
    if first and 2 <= len(first) <= 45 and not re.search(r'prescribing information|home|resources', first, re.I):
        words = [w for w in re.split(r'\s+', first) if w.lower() not in COMMON_WORDS]
        if words:
            return ' '.join(words[:4]).strip(' ®™')
    return seed.strip(' ®™')

def infer_generic(brand, text):
    t = text[:12000]
    b = re.escape((brand or '').split()[0]) if brand else r'[A-Z][A-Za-z0-9-]+'
    patterns = [
        rf'{b}[^\n\(]{{0,80}}\(([^\)]{{3,90}})\)',
        r'generic name\s*[:\-]\s*([A-Za-z0-9 ,/\-]+)',
        r'active ingredient(?:s)?\s*[:\-]\s*([A-Za-z0-9 ,/\-]+)',
        r'contains\s+([a-z][a-z0-9\-]+(?:\s+[a-z][a-z0-9\-]+){0,3})\s+(?:as|,|for|in)'
    ]
    for pat in patterns:
        m = re.search(pat, t, re.I)
        if m:
            val = clean(m.group(1), 120).strip(' .;:®™')
            if val and not re.search(r'HCP|healthcare|professional|patient|official|prescribing|click|learn|view', val, re.I):
                return val
    return ''

def infer_company(url, text):
    host = urlparse(url).netloc.lower()
    for key, val in COMPANY_BY_HOST.items():
        if key in host or key in url.lower(): return val
    low = text.lower()
    for name in COMPANY_NAMES:
        if name.lower() in low: return 'Bristol Myers Squibb' if name=='BMS' else ('Eli Lilly' if name=='Lilly' else name)
    m = re.search(r'(?:©|copyright)\s*(?:\d{4}\s*)?([^\.\n\|]{3,60})', text, re.I)
    if m:
        val = clean(m.group(1), 80).strip(' .|')
        if not re.search(r'all rights|cookie|privacy', val, re.I): return val
    return ''

def normalize_hex(h):
    h = h.strip().lower()
    if len(h)==4: h = '#' + ''.join(c*2 for c in h[1:])
    if re.fullmatch(r'#[0-9a-f]{6}', h): return h.upper()
    return ''

def rgb_to_hex(m):
    nums = [int(float(x)) for x in re.findall(r'\d+(?:\.\d+)?', m)[:3]]
    if len(nums)==3 and all(0<=n<=255 for n in nums): return '#%02X%02X%02X' % tuple(nums)
    return ''

def color_score(hexv):
    r,g,b = int(hexv[1:3],16), int(hexv[3:5],16), int(hexv[5:7],16)
    mx,mn=max(r,g,b),min(r,g,b); sat=mx-mn; lum=0.2126*r+0.7152*g+0.0722*b
    neutral = sat < 18 or lum < 20 or lum > 242
    return (0 if neutral else 1, sat, -abs(lum-128))

def extract_colors(url, soup, html):
    blobs = [html[:300000]]
    for tag in soup.find_all('link', href=True):
        href = tag.get('href','')
        rel = ' '.join(tag.get('rel') or [])
        if 'stylesheet' in rel.lower() or href.endswith('.css'):
            cssurl = urljoin(url, href)
            if len(blobs) >= 7: break
            try:
                cr = S.get(cssurl, timeout=5, verify=False, headers={'User-Agent': UA})
                if cr.ok and len(cr.text) < 800000: blobs.append(cr.text)
            except Exception:
                pass
    alltext = '\n'.join(blobs)
    colors=[]
    for h in re.findall(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b', alltext):
        nh=normalize_hex(h)
        if nh: colors.append(nh)
    for rgb in re.findall(r'rgba?\([^\)]{5,40}\)', alltext, flags=re.I):
        hx=rgb_to_hex(rgb)
        if hx: colors.append(hx)
    counts=Counter(c for c in colors if c not in ('#FFFFFF','#000000','#FFF','#000'))
    ranked=sorted(counts, key=lambda c:(counts[c], color_score(c)), reverse=True)
    selected=[]
    for c in ranked:
        if c not in selected: selected.append(c)
        if len(selected)>=8: break
    if len(selected)<5:
        for c in ['#FFFFFF','#000000','#F5F5F5','#666666','#CCCCCC','#004B8D','#00A3E0','#E6E6E6']:
            if c not in selected: selected.append(c)
            if len(selected)>=5: break
    selected=selected[:8]
    primary=selected[0]
    secondary=selected[1] if len(selected)>1 else selected[0]
    accent=''
    for c in selected:
        if color_score(c)[0] == 1 and c not in (primary, secondary): accent=c; break
    accent = accent or (selected[2] if len(selected)>2 else secondary)
    return selected, primary, secondary, accent

def rwe_assess(text, prompt_flag):
    found=[]
    for label, pat in RWE_PATTERNS:
        if re.search(pat, text, re.I) and label not in found: found.append(label)
    if found:
        return 'yes', ', '.join(found[:6])
    if prompt_flag:
        return 'maybe', ''
    if text:
        return 'no', ''
    return 'unknown', ''

def process(item):
    input_url=item['url']
    status, final_url, html, ctype, err = fetch(input_url)
    soup, title, meta, body = visible_text_and_meta(html)
    text = clean(' '.join([title, meta, body]), 30000)
    brand = improve_brand(brand_from_url(final_url or input_url), title, text)
    generic = infer_generic(brand, text)
    company = infer_company(final_url or input_url, text)
    colors, primary, secondary, accent = extract_colors(final_url or input_url, soup, html) if html else (['#FFFFFF','#000000','#F5F5F5','#666666','#CCCCCC'], '#FFFFFF', '#000000', '#666666')
    prompt_flag = item.get('rwe_prompt_flag') in (True, 'true', 'True')
    assessment, terms = rwe_assess(text, prompt_flag)
    notes = ['Chrome plugin attempted but failed with extension navigation/context errors; HTTP fallback used']
    if err: notes.append('HTTP fetch '+err)
    if not generic: notes.append('generic not confidently found on fetched page')
    if not company: notes.append('company not confidently found on fetched page')
    if status in ('error', 403, 404, 500, 502, 503): notes.append('status may reflect blocking or unavailable page')
    return {
        'input_url': input_url,
        'final_url': final_url or input_url,
        'status': str(status),
        'brand_name': brand,
        'generic_name': generic,
        'company': company,
        'color_scheme_hex': ','.join(colors),
        'primary_hex': primary,
        'secondary_hex': secondary,
        'accent_hex': accent,
        'rwe_prompt_flag': str(bool(prompt_flag)).lower(),
        'rwe_assessment': assessment,
        'rwe_evidence_terms': terms,
        'notes': '; '.join(notes)[:500]
    }

def main():
    rows=[]
    with ThreadPoolExecutor(max_workers=14) as ex:
        futs={ex.submit(process,item): item for item in SELECTED}
        for i,f in enumerate(as_completed(futs),1):
            rows.append(f.result())
            if i % 20 == 0:
                with (TMP/'fallback_progress.json').open('w', encoding='utf-8') as fp:
                    json.dump({'done':i,'total':len(SELECTED)}, fp)
    order={r['url']:i for i,r in enumerate(SELECTED)}
    rows.sort(key=lambda r: order[r['input_url']])
    with OUT.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader(); w.writerows(rows)
    with (TMP/'fallback_summary.json').open('w', encoding='utf-8') as f:
        json.dump({'rows':len(rows),'output':str(OUT)}, f, indent=2)
    print(json.dumps({'rows':len(rows),'output':str(OUT)}, indent=2))

if __name__ == '__main__':
    main()
