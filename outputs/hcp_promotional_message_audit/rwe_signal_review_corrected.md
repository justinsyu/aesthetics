# Site-Level RWE Signals With Promotional Context

Generated: 2026-05-16 19:04

## Review Finding

The extracted `promotional_message_verbatim` field should **not** be treated as the RWE claim. It was generated separately as the strongest short promotional pitch on each page. For RWE-positive rows, it usually captures a hero line, meta description, CTA-adjacent line, or product-positioning statement rather than the real-world evidence section.

- RWE-positive pages in the audit: **149**
- RWE-positive pages whose extracted promotional message itself contains RWE terminology: **1**
- Correct interpretation: use `rwe_signals` as the RWE audit signal; use the promotional-message CSV only for general messaging analysis.

## RWE Signal Terms Found

- postmarketing: 51
- registry: 45
- real-world: 43
- observational: 27
- real-world evidence: 26
- retrospective: 19
- claims: 15
- phase 4: 6
- claims data: 6
- post-marketing: 5
- real-world data: 5
- database: 4
- long-term extension: 3
- rwe: 2
- ehr: 2
- administrative claims: 1
- real world: 1
- patient registry: 1
- real-world experience: 1
- phase iv: 1

## Promotional Messages That Actually Mention RWE

| Brand | Company | Promotional message containing RWE wording | RWE signals | URL |
|---|---|---|---|---|
| THE | Janssen | THOUGHT LEADER SERIES: REAL-WORLD EVIDENCE IN THE TREATMENT OF mCSPC | real-world evidence | [https://erleadahcp.com](https://erleadahcp.com) |

## Site-Level RWE-Positive Pages for Review

This table intentionally omits the general promotional-message field because it is not the RWE claim text.

| # | Brand | Generic | Company | RWE signal terms | URL |
|---:|---|---|---|---|---|
| 1 | Quillichewer |  | Tris Pharma, Inc | registry | [https://www.quillichewerhcp.com](https://www.quillichewerhcp.com) |
| 2 | ONYDA XR | clonidine |  | registry; retrospective; post-marketing | [https://www.onydahcp.com](https://www.onydahcp.com) |
| 3 | DYANAVEL XR | amphetamine | Tris Pharma | registry | [https://www.dyanavelxrhcp.com](https://www.dyanavelxrhcp.com) |
| 4 | Quillivantxr |  | Tris Pharma, Inc | registry | [https://www.quillivantxrhcp.com](https://www.quillivantxrhcp.com) |
| 5 | NATESTO | testosterone nasal gel | Acerus Pharmaceuticals | postmarketing | [https://www.natestohcp.com](https://www.natestohcp.com) |
| 6 | HCP. Juxtapid® (lomitapide) HoFH | lomitapide | Chiesi | registry | [https://www.juxtapid.com/hcp](https://www.juxtapid.com/hcp) |
| 7 | JUBLIA | efinaconazole topical solution 10% | Bausch Health | phase 4 | [https://www.jubliarx.com/hcp](https://www.jubliarx.com/hcp) |
| 8 | SPINRAZA® (nusinersen) | nusinersen | Biogen | real-world, real-world evidence, observational | [https://www.spinraza-hcp.com](https://www.spinraza-hcp.com) |
| 9 | ABRAXANE® Injectable Suspension |  | Bristol Myers Squibb | postmarketing | [https://abraxanepro.com](https://abraxanepro.com) |
| 10 | Official | Respiratory Syncytial Virus Vaccine | Pfizer | observational; postmarketing; real-world; real-world evidence; registry | [https://abrysvoadult.pfizerpro.com](https://abrysvoadult.pfizerpro.com) |
| 11 | Unknown | repository corticotropin injection |  | real-world; retrospective; phase 4 | [https://actharhcp.com](https://actharhcp.com) |
| 12 | ACTIVASE | alteplase | Genentech | registry | [https://activase.com](https://activase.com) |
| 13 | ADBRY | tralokinumab-Idrm | LEO Pharma Inc | real-world; real-world evidence; registry | [https://adbryhcp.com](https://adbryhcp.com) |
| 14 | ADVATE | Recombinant | Takeda | real-world | [https://advatepro.com](https://advatepro.com) |
| 15 | ANORO ELLIPTA | umeclidinium/vilanterol | GSK | administrative claims | [https://anorohcp.com](https://anorohcp.com) |
| 16 | Apligraf® Living Cellular Skin |  | Novartis | real-world, real-world evidence, observational | [https://apligraf.com](https://apligraf.com) |
| 17 | APRETUDE | cabotegravir 200 mg/mL |  | real-world evidence; real-world | [https://apretudehcp.com](https://apretudehcp.com) |
| 18 | BENLYSTA | belimumab | GSK | phase 4; real-world; real-world evidence; registry | [https://benlystahcp.com](https://benlystahcp.com) |
| 19 | BIKTARVY | bictegravir, emtricitabine, and tenofovir alafenamide | Gilead Sciences | registry | [https://biktarvyhcp.com](https://biktarvyhcp.com) |
| 20 | Cabenuva | cabotegravir; rilpivirine | ViiV Healthcare or licensor. PMUS-CBRWCNT260004 April 2026 Pr | observational; real world; real-world; registry | [https://cabenuvahcp.com](https://cabenuvahcp.com) |
| 21 | CAMZYOS | mavacamten | Bristol Myers Squibb | long-term extension | [https://camzyoshcp.com](https://camzyoshcp.com) |
| 22 | CINVANTI® (aprepitant) injectable emulsion | aprepitant | Merck | real-world | [https://cinvanti.com](https://cinvanti.com) |
| 23 | COMIRNATY | COVID-19 Vaccine, mRNA | Pfizer and BioNTech | real-world evidence; real-world | [https://comirnatyhcp.pfizerpro.com](https://comirnatyhcp.pfizerpro.com) |
| 24 | ENSPRYNG | satralizumab-mwge |  | registry; claims | [https://enspryng-hcp.com](https://enspryng-hcp.com) |
| 25 | ENTYVIO® (vedolizumab) | vedolizumab | Takeda | real-world, claims, postmarketing | [https://entyviohcp.com](https://entyviohcp.com) |
| 26 | LGS | cannabidiol | Jazz | registry | [https://epidiolexhcp.com](https://epidiolexhcp.com) |
| 27 | EQUETRO | carbamazepine | Validus Pharmaceuticals | registry; retrospective | [https://equetro.com/professionals](https://equetro.com/professionals) |
| 28 | THE |  | Janssen | real-world evidence | [https://erleadahcp.com](https://erleadahcp.com) |
| 29 | FETROJA | cefiderocol | Shionogi | real-world evidence; real-world | [https://fetroja.com](https://fetroja.com) |
| 30 | FIRDAPSE | amifampridine | Catalyst Pharmaceuticals | registry | [https://firdapsehcp.com](https://firdapsehcp.com) |
| 31 | AVONEX | interferon beta-1a | Biogen | postmarketing | [https://hcp.avonex.com](https://hcp.avonex.com) |
| 32 | CERDELGA | eliglustat | Sanofi | observational; retrospective | [https://hcp.cerdelga.com](https://hcp.cerdelga.com) |
| 33 | Elfabrio® (pegunigalsidase alfa | pegunigalsidase alfa-iwxj | Chiesi | registry | [https://hcp.elfabrio.com](https://hcp.elfabrio.com) |
| 34 | Emflaza |  | PTC Therapeutics, Inc | observational; real-world; real-world data | [https://hcp.emflaza.com](https://hcp.emflaza.com) |
| 35 | HYALGAN | sodium hyaluronate | Fidia Pharma | observational | [https://hcp.hyalgan.com](https://hcp.hyalgan.com) |
| 36 | IBRANCE® (palbociclib) HCPs | palbociclib | Pfizer | real-world, real-world evidence, RWE, postmarketing | [https://ibrance.pfizerpro.com](https://ibrance.pfizerpro.com) |
| 37 | Unknown | durvalumab |  | real-world data; real-world | [https://imfinzihcp.com](https://imfinzihcp.com) |
| 38 | Kimyrsa | oritavancin | Melinta Therapeutics, LLC | real-world, retrospective, observational, registry | [https://kimyrsa.com](https://kimyrsa.com) |
| 39 | LYNPARZA | olaparib | AstraZeneca / Merck | claims data | [https://lynparzahcp.com](https://lynparzahcp.com) |
| 40 | Official |  | Bausch | phase 4 | [https://miebo-ecp.com](https://miebo-ecp.com) |
| 41 | NINLARO | ixazomib | Takeda Oncology | real-world evidence; real-world | [https://ninlarohcp.com](https://ninlarohcp.com) |
| 42 | NPLATE | romiplostim | Amgen | real-world evidence; observational; claims; retrospective; long-term extension | [https://nplatehcp.com](https://nplatehcp.com) |
| 43 | NUPLAZID® (pimavanserin) | pimavanserin | Acadia | real-world, real-world evidence | [https://nuplazidhcp.com](https://nuplazidhcp.com) |
| 44 | ONGENTYS | opicapone | Neurocrine Biosciences | real-world data; real-world | [https://ongentyshcp.com](https://ongentyshcp.com) |
| 45 | ESR1 | elacestrant | Endo | real-world, real-world evidence, retrospective, observational | [https://orserduhcp.com](https://orserduhcp.com) |
| 46 | PAXLOVID | within PAXLOVID | Pfizer | real-world evidence; observational | [https://paxlovid.pfizerpro.com](https://paxlovid.pfizerpro.com) |
| 47 | RADICAVA ORS® (edaravone) | edaravone | Endo | observational | [https://radicavahcp.com](https://radicavahcp.com) |
| 48 | TEPEZZA® (teprotumumab | teprotumumab-trbw | Amgen | real-world | [https://tepezzahcp.com](https://tepezzahcp.com) |
| 49 | ULTOMIRIS | ravulizumab-cwvz | Alexion | registry | [https://ultomirishcp.com](https://ultomirishcp.com) |
| 50 | UPTRAVI | selexipag |  | real-world evidence | [https://uptravihcp.com](https://uptravihcp.com) |
| 51 | Velphoro | sucroferric oxyhydroxide | , 2025 Fresenius Medical Care | real-world, retrospective, database | [https://velphorohcp.com](https://velphorohcp.com) |
| 52 | MDD | Indication Discover VRAYLAR |  | claims data; real-world | [https://vraylarhcp.com](https://vraylarhcp.com) |
| 53 | CPX-351 | daunorubicin and cytarabine | Jazz | real-world evidence; real-world | [https://vyxeospro.com](https://vyxeospro.com) |
| 54 | VYZULTA | latanoprostene bunod ophthalmic solution | Bausch + Lomb | real-world evidence; real-world | [https://vyzultahcp.com](https://vyzultahcp.com) |
| 55 | XERAVA | eravacycline | Innoviva Specialty Therapeutics â¢ | real-world | [https://xerava.com](https://xerava.com) |
| 56 | Survival |  |  | real-world; real-world evidence | [https://yescartahcp.com](https://yescartahcp.com) |
| 57 | Inflectra | infliximab | Pfizer | real-world, real-world evidence, retrospective, postmarketing | [https://inflectra.pfizerpro.com](https://inflectra.pfizerpro.com) |
| 58 | Injectafer |  |  | claims data; post-marketing | [https://injectaferhcp.com](https://injectaferhcp.com) |
| 59 | ISTURISA | osilodrostat | Recordati Rare Diseases | claims | [https://isturisa.com](https://isturisa.com) |
| 60 | Joenja® (leniolisib) | leniolisib | Pharming Healthcare, Inc | registry | [https://joenja-hcp.com](https://joenja-hcp.com) |
| 61 | Kadcyla |  | Genentech | observational; post-marketing; retrospective | [https://kadcyla-hcp.com](https://kadcyla-hcp.com) |
| 62 | HR+/HER2 | ribociclib | Novartis | postmarketing | [https://kisqali-hcp.com](https://kisqali-hcp.com) |
| 63 | Hyperkalemia | sodium zirconium cyclosilicate | AstraZeneca | real-world, real-world evidence, RWE, EHR | [https://lokelma-hcp.com](https://lokelma-hcp.com) |
| 64 | LYBALVI | olanzapine and samidorphan | Alkermes | postmarketing; registry | [https://lybalvihcp.com](https://lybalvihcp.com) |
| 65 | MAVYRET (glecaprevir/pibrentasvir) | glecaprevir/pibrentasvir | AbbVie | postmarketing | [https://mavyret.com/hcp](https://mavyret.com/hcp) |
| 66 | MYRBETRIQ | mirabegron | Astellas | claims; postmarketing; phase 4 | [https://myrbetriqhcp.com](https://myrbetriqhcp.com) |
| 67 | ONUREG | azacitidine | Bristol Myers Squibb | retrospective | [https://onuregpro.com](https://onuregpro.com) |
| 68 | OPSUMIT | macitentan | Johnson & Johnson | claims data; postmarketing | [https://opsumithcp.com](https://opsumithcp.com) |
| 69 | Opzelura |  | Incyte | postmarketing; registry | [https://opzelurahcp.com](https://opzelurahcp.com) |
| 70 | Perseris | e.g., stroke, transient ischemic attack | Indivior UK Limited | registry | [https://perserishcp.com](https://perserishcp.com) |
| 71 | PROVENGE | sipuleucel-T | Dendreon Pharmaceuticals LLC | real-world; registry | [https://provenge.com/hcp](https://provenge.com/hcp) |
| 72 | High LDL | evolocumab | Amgen | claims | [https://repathahcp.com](https://repathahcp.com) |
| 73 | Secuado | psychosis |  | registry | [https://secuado.com](https://secuado.com) |
| 74 | SHINGRIX | zoster vaccine recombinant, adjuvanted | GSK | observational | [https://shingrixhcp.com](https://shingrixhcp.com) |
| 75 | SOHONOS | palovarotene | Ipsen | registry | [https://sohonos.com](https://sohonos.com) |
| 76 | Spritam | levetiracetam |  | claims | [https://spritamhcp.com](https://spritamhcp.com) |
| 77 | Strensiq |  | Alexion | ehr; postmarketing; registry | [https://strensiq-hcp.com](https://strensiq-hcp.com) |
| 78 | INDICATION TECFIDERA | dimethyl fumarate | Biogen | registry; observational; postmarketing | [https://tecfiderahcp.com](https://tecfiderahcp.com) |
| 79 | TURALIO | pexidartinib | Daiichi Sankyo | patient registry; registry | [https://turaliohcp.com](https://turaliohcp.com) |
| 80 | TYMLOS® (abaloparatide) Injection | abaloparatide | Radius | observational, postmarketing | [https://tymlos.com/hcp](https://tymlos.com/hcp) |
| 81 | VECTIBIX | panitumumab | Amgen | claims data; postmarketing; real-world; retrospective | [https://vectibixhcp.com](https://vectibixhcp.com) |
| 82 | Vemlidy |  | Gilead | postmarketing; registry | [https://vemlidyhcp.com](https://vemlidyhcp.com) |
| 83 | VOYDEYA | danicopan |  | registry | [https://voydeyahcp.com](https://voydeyahcp.com) |
| 84 | VUMERITY | diroximel fumarate | Biogen | postmarketing; real-world; registry | [https://vumerityhcp.com](https://vumerityhcp.com) |
| 85 | VYLOY® (zolbetuximab | zolbetuximab-clzb | Astellas | real-world | [https://vyloyhcp.com](https://vyloyhcp.com) |
| 86 | Official |  | Pfizer | real-world; real-world evidence | [https://vyndamax.pfizerpro.com](https://vyndamax.pfizerpro.com) |
| 87 | XYWAV | calcium, magnesium, potassium, and sodium oxybates | Jazz Pharmaceuticals | phase 4 | [https://xywavhcp.com](https://xywavhcp.com) |
| 88 | YORVIPATH | palopegteriparatide | April 2026 Ascendis | observational; postmarketing | [https://yorvipathhcp.com](https://yorvipathhcp.com) |
| 89 | ZEPOSIA | ozanimod | Bristol Myers Squibb | registry | [https://zeposiahcp.com](https://zeposiahcp.com) |
| 90 | ES | lurbinectedin | Jazz Pharmaceuticals | claims | [https://zepzelcapro.com](https://zepzelcapro.com) |
| 91 | Unknown | diclofenac potassium |  | registry | [https://zipsor.com/hcp](https://zipsor.com/hcp) |
| 92 | ZONISADE | zonisamide oral suspension | Azurity Pharmaceuticals | registry | [https://zonisade.com](https://zonisade.com) |
| 93 | ZYMFENTRA | infliximab-dyyb | Celltrion USA | postmarketing | [https://zymfentra.com/hcp](https://zymfentra.com/hcp) |
| 94 | All Stages of APC | degarelix for injection | Ferring | postmarketing | [https://firmagon.com/hcp](https://firmagon.com/hcp) |
| 95 | SUNOSI |  | Axsome Therapeutics, Inc | registry | [https://www.sunosihcp.com](https://www.sunosihcp.com) |
| 96 | HCP | dornase alfa | Genentech | registry | [https://pulmozyme.com/hcp.html](https://pulmozyme.com/hcp.html) |
| 97 | Cholesterol Medication | rosuvastatin | Pfizer | postmarketing, database | [https://www.crestor.com/hcp](https://www.crestor.com/hcp) |
| 98 | ALPROLIX | coagulation factor IX recombinant Fc fusion protein | Sanofi | real-world data; real-world experience | [https://pro.campus.sanofi/us/products/alprolix](https://pro.campus.sanofi/us/products/alprolix) |
| 99 | LANT | insulin glargine | Sanofi | postmarketing, database | [https://www.lantus.com/hcp](https://www.lantus.com/hcp) |
| 100 | MOZOBIL | plerixafor | Sanofi | postmarketing | [https://pro.campus.sanofi/us/products/mozobil](https://pro.campus.sanofi/us/products/mozobil) |
| 101 | MULTAQ | dronedarone | Sanofi | claims data; post-marketing; postmarketing | [https://www.multaqhcp.com](https://www.multaqhcp.com) |
| 102 | LUCENTIS | ranibizumab | Genentech/Roche | claims | [https://www.lucentis.com/hcp.html](https://www.lucentis.com/hcp.html) |
| 103 | POLIVY® (polatuzumab vedotin | polatuzumab vedotin-piiq | Genentech | retrospective, postmarketing, database | [https://www.polivy.com/hcp.html](https://www.polivy.com/hcp.html) |
| 104 | Prolensa | bromfenac ophthalmic solution | Bausch + Lomb | postmarketing | [https://www.prolensarx.com](https://www.prolensarx.com) |
| 105 | Cutaquig | Immune Globulin Subcutaneous (Human | Pfizer | claims | [https://cutaquig.pfizerpro.com](https://cutaquig.pfizerpro.com) |
| 106 | Solu | hydrocortisone Na succinate for inj, USP | Pfizer | postmarketing | [https://solucortef.pfizerpro.com](https://solucortef.pfizerpro.com) |
| 107 | FRAGMIN | dalteparin sodium | Pfizer | observational; retrospective; postmarketing | [https://www.pfizermedical.com/fragmin](https://www.pfizermedical.com/fragmin) |
| 108 | Short | remimazolam | Horizon | real-world, observational | [https://www.byfavo.com](https://www.byfavo.com) |
| 109 | INDICATION | asenapine |  | registry | [https://www.secuado.com/professional](https://www.secuado.com/professional) |
| 110 | Belbuca | buprenorphine buccal film | Collegium | observational, postmarketing | [https://www.belbuca.com/hcp](https://www.belbuca.com/hcp) |
| 111 | KENGREAL | cangrelor | Chiesi | real-world; real-world data | [https://kengreal.com](https://kengreal.com) |
| 112 | CUROSURF® (poractant alfa) | poractant alfa | AbbVie | retrospective, observational | [https://curosurf.com](https://curosurf.com) |
| 113 | VIBATIV® (telavancin) | telavancin | Cumberland Pharmaceuticals Inc | real-world | [https://www.vibativ.com/](https://www.vibativ.com/) |
| 114 | HYRIMOZ | adalimumab-adaz |  | real-world evidence; real-world; post-marketing | [https://www.hyrimoz.com/pro](https://www.hyrimoz.com/pro) |
| 115 | QELBREE | viloxazine extended-release capsules | Supernus Pharmaceuticals | registry | [https://www.qelbreehcp.com](https://www.qelbreehcp.com) |
| 116 | TROKENDIXR |  | Supernus | registry; postmarketing | [https://www.trokendixrhcp.com](https://www.trokendixrhcp.com) |
| 117 | CONEXXENCE® (denosumab | denosumab-bnht | Fresenius Kabi | postmarketing | [https://biosimilars.fresenius-kabi.com/portfolio/products/conexxence](https://biosimilars.fresenius-kabi.com/portfolio/products/conexxence) |
| 118 | SOLIQUA |  | Sanofi | postmarketing | [https://www.soliqua100-33.com/hcp](https://www.soliqua100-33.com/hcp) |
| 119 | Thymoglobulin® Anti | Rabbit | Sanofi | postmarketing | [https://www.thymoglobulin.com](https://www.thymoglobulin.com) |
| 120 | EXONDYS 51 | eteplirsen | Sarepta Therapeutics | observational | [https://www.sareptadmd.com/exondys51](https://www.sareptadmd.com/exondys51) |
| 121 | Eucrisa | crisaborole | Pfizer | phase iv | [https://eucrisa.pfizerpro.com](https://eucrisa.pfizerpro.com) |
| 122 | ROXYBOND | oxycodone hydrochloride | Protega Pharmaceuticals | observational | [https://www.roxybond.com](https://www.roxybond.com) |
| 123 | Tolsura | itraconazole | Mayne Pharma Commercial LLC | postmarketing | [https://tolsura.com](https://tolsura.com) |
| 124 | FIBRYGAUSA |  | Octapharma USA | real-world evidence | [https://fibrygausa.com](https://fibrygausa.com) |
| 125 | BALFAXAR | first licensed in Germany as Octaplex in 2003 | CSL Behring | postmarketing | [https://balfaxar.com](https://balfaxar.com) |
| 126 | Prostate Cancer Diagnostic Imaging | piflufolastat F 18 | Lantheus | real-world | [https://pylarify.com](https://pylarify.com) |
| 127 | Cibinqo |  | Pfizer | postmarketing; registry | [https://cibinqo.pfizerpro.com](https://cibinqo.pfizerpro.com) |
| 128 | Litfulo | ritlecitinib | Pfizer | postmarketing | [https://litfulo.pfizerpro.com](https://litfulo.pfizerpro.com) |
| 129 | PENBRAYA | meningococcal groups A, B, C, W, and Y vaccine | Pfizer | registry | [https://penbraya.pfizerpro.com](https://penbraya.pfizerpro.com) |
| 130 | RUXIENCE |  | Pfizer | postmarketing | [https://ruxience.pfizerpro.com](https://ruxience.pfizerpro.com) |
| 131 | ARANESP | darbepoetin alfa | Amgen Inc | postmarketing | [https://www.aranesp.com/professional/oncology](https://www.aranesp.com/professional/oncology) |
| 132 | Amgenesas |  | Amgen | real-world, claims, postmarketing | [https://www.epogen.com/professional](https://www.epogen.com/professional) |
| 133 | ALECENSA | alectinib | Genentech/Roche | retrospective; postmarketing | [https://www.alecensa.com/hcp/metastatic.html](https://www.alecensa.com/hcp/metastatic.html) |
| 134 | CELLCEPT | mycophenolate mofetil | Genentech | registry | [https://www.gene.com/medical-professionals/medicines/cellcept](https://www.gene.com/medical-professionals/medicines/cellcept) |
| 135 | ALECENSA | alectinib | Genentech/Roche | retrospective; postmarketing | [https://www.alecensa.com/hcp/metastatic/dosing-and-administration.html](https://www.alecensa.com/hcp/metastatic/dosing-and-administration.html) |
| 136 | POLIVY | polatuzumab vedotin-piiq | Genentech/Roche | retrospective; postmarketing | [https://www.polivy-hcp.com](https://www.polivy-hcp.com) |
| 137 | Roxybond | e.g., non-opioid analgesics or opioid combination products |  | observational | [https://www.roxybond.com/efficacy-safety-and-dosing](https://www.roxybond.com/efficacy-safety-and-dosing) |
| 138 | VIVOTIF | Typhoid Vaccine Live Oral Ty21a | Bavarian Nordic Inc | claims; postmarketing | [https://vivotif.com](https://vivotif.com) |
| 139 | Myhibbin | mycophenolate mofetil oral suspension | Genentech | registry, postmarketing | [https://www.myhibbin.com](https://www.myhibbin.com) |
| 140 | DUAKLIR PRESSAIR | aclidinium bromide/formoterol fumarate | Covis Pharma | observational | [https://hcp.duaklir.us](https://hcp.duaklir.us) |
| 141 | SAPHNELO® (anifrolumab | anifrolumab-fnia | AstraZeneca | real-world, observational, registry | [https://www.saphnelohcp.com](https://www.saphnelohcp.com) |
| 142 | HYSINGLA ER | hydrocodone bitartrate | Purdue Pharma | observational; postmarketing | [https://www.hysinglaer.com](https://www.hysinglaer.com) |
| 143 | XELJANZ | tofacitinib | Pfizer | claims; postmarketing; long-term extension | [https://xeljanz.pfizerpro.com](https://xeljanz.pfizerpro.com) |
| 144 | ZURZUVAE | zuranolone | Supernus | registry | [https://www.zurzuvae.com/hcp](https://www.zurzuvae.com/hcp) |
| 145 | APIDRA | insulin glulisine | Sanofi | claims | [https://pro.campus.sanofi/us/products/apidra](https://pro.campus.sanofi/us/products/apidra) |
| 146 | Cablivi | caplacizumab-yhdp | Sanofi | postmarketing; real-world; real-world evidence | [https://pro.campus.sanofi/us/products/cablivi](https://pro.campus.sanofi/us/products/cablivi) |
| 147 | Lucentis | ranibizumab | Genentech | claims | [https://www.lucentis.com](https://www.lucentis.com) |
| 148 | EMVERM | mebendazole | Amneal Pharmaceuticals LLC | postmarketing | [https://www.emvermhcp.com](https://www.emvermhcp.com) |
| 149 | ADSTILADRIN | nadofaragene firadenovec-vncg | Sarepta Therapeutics | real-world evidence; retrospective | [https://www.adstiladrinhcp.com](https://www.adstiladrinhcp.com) |

## Limitation

The current compiled CSV stores RWE signal terms, not full verbatim RWE evidence claims. To produce a true RWE-claims inventory, each RWE-positive URL should be revisited and the exact visible real-world evidence sentence, table heading, or section text should be captured with source context.
