# Phase 2/3 Ophthalmology Disease-State Overlap
Source date: May 11, 2026.

## Scope and Method
- Companies were transcribed from the supplied image on a best-effort basis; the image is low-resolution, so this file keeps the company list explicit.
- Scope is ophthalmology/vision disease states. Broad pharma pipelines outside eye disease were excluded.
- Inclusion rule: active ClinicalTrials.gov interventional studies with status `RECRUITING`, `NOT_YET_RECRUITING`, `ACTIVE_NOT_RECRUITING`, or `ENROLLING_BY_INVITATION`, and phase containing Phase 2, Phase 2/3, Phase 1/2, or Phase 3.
- Disease-state labels below are normalized from trial condition text. Each supporting trial links to ClinicalTrials.gov.
- Source: [ClinicalTrials.gov API v2](https://clinicaltrials.gov/api/v2/studies).

## Top 10 Disease States by Company Overlap
| Rank | Disease state | Companies | Count |
|---:|---|---|---:|
| 1 | Neovascular age-related macular degeneration (wet AMD/nAMD) | 4D Molecular Therapeutics, AbbVie / Allergan, Adverum Biotechnologies, AsclepiX Therapeutics, Bayer, Chengdu Kanghong Biotechnology, EyePoint Pharmaceuticals, Genentech, Kodiak Sciences, Kyowa Kirin, Ocular Therapeutix, Outlook Therapeutics, Perceive Biotherapeutics, REGENXBIO, Regeneron Pharmaceuticals, Roche, Sanofi | 17 |
| 2 | Geographic atrophy | AbbVie / Allergan, Annexon Biosciences, Apellis Pharmaceuticals, Aviceda Therapeutics, Belite Bio, Boehringer Ingelheim, Genentech, Gyroscope Therapeutics, Janssen Pharmaceuticals, Kriya Therapeutics, Novartis, Ocugen, Perceive Biotherapeutics, Regeneron Pharmaceuticals, Sanofi | 15 |
| 3 | Diabetic macular edema | 4D Molecular Therapeutics, AbbVie / Allergan, Boehringer Ingelheim, Curacle, EyePoint Pharmaceuticals, Genentech, Kyowa Kirin, Outlook Therapeutics, REGENXBIO, Regeneron Pharmaceuticals, Roche | 11 |
| 4 | Diabetic retinopathy | 4D Molecular Therapeutics, AbbVie / Allergan, Boehringer Ingelheim, Genentech, Kodiak Sciences, Ocular Therapeutix, Perfuse Therapeutics, REGENXBIO, Roche, Valo Health | 10 |
| 5 | Glaucoma / ocular hypertension | AbbVie / Allergan, Bausch + Lomb, Glaukos, Perfuse Therapeutics, Santen Pharmaceutical, Thea Laboratories | 6 |
| 6 | Retinitis pigmentosa | GenSight Biologics, Kiora Pharmaceuticals, Novartis, Ocugen, Thea Laboratories, jCyte | 6 |
| 7 | Dry eye disease | AbbVie / Allergan, Bausch + Lomb, Oculis, Vanda Pharmaceuticals, VivaVision Biotech | 5 |
| 8 | Age-related macular degeneration, non-neovascular/unspecified | Novartis, Roche, Smilebiotek Zhuhai, Stealth BioTherapeutics | 4 |
| 9 | Stargardt disease | Belite Bio, Ocugen, Ray Therapeutics, Sanofi | 4 |
| 10 | Thyroid eye disease | Amgen, Kriya Therapeutics, Roche | 3 |

## Company-Level Findings
| Company | Normalized disease states with active Phase 2/3 treatment trials | Supporting trials |
|---|---|---|
| 4D Molecular Therapeutics | Diabetic macular edema; Diabetic retinopathy; Neovascular age-related macular degeneration (wet AMD/nAMD); X-linked retinitis pigmentosa | Diabetic macular edema: [NCT05930561](https://clinicaltrials.gov/study/NCT05930561) (P2; 4D-150 IVT, Aflibercept IVT)<br>Diabetic retinopathy: [NCT05930561](https://clinicaltrials.gov/study/NCT05930561) (P2; 4D-150 IVT, Aflibercept IVT)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06864988](https://clinicaltrials.gov/study/NCT06864988) (P3; 4D-150 IVT (3E10 vg/eye), EYLEA® (aflibercept) Injection 2 mg (0.05mL)); [NCT05197270](https://clinicaltrials.gov/study/NCT05197270) (P1/P2; 4D-150 IVT, Aflibercept IVT); [NCT07064759](https://clinicaltrials.gov/study/NCT07064759) (P3; 4D-150 IVT (3E10 vg/eye), EYLEA® (aflibercept) Injection 2 mg (0.05mL))<br>X-linked retinitis pigmentosa: [NCT04517149](https://clinicaltrials.gov/study/NCT04517149) (P1/P2; 4D-125 IVT Injection, Observational) |
| AbbVie / Allergan | Diabetic macular edema; Diabetic retinopathy; Dry eye disease; Geographic atrophy; Glaucoma / ocular hypertension; Neovascular age-related macular degeneration (wet AMD/nAMD) | Diabetic macular edema: [NCT04567550](https://clinicaltrials.gov/study/NCT04567550) (P2; ABBV-RGX-314 Dose 1, ABBV-RGX-314 Dose 2, ABBV-RGX-314 Dose 3, Topical Steroid, ABBV-RGX-3)<br>Diabetic retinopathy: [NCT04567550](https://clinicaltrials.gov/study/NCT04567550) (P2; ABBV-RGX-314 Dose 1, ABBV-RGX-314 Dose 2, ABBV-RGX-314 Dose 3, Topical Steroid, ABBV-RGX-3)<br>Dry eye disease: [NCT07284381](https://clinicaltrials.gov/study/NCT07284381) (P3; ABBV-444, REFRESH OPTIVE UD)<br>Geographic atrophy: [NCT07160179](https://clinicaltrials.gov/study/NCT07160179) (P1/P2; ABBV-6628, SYFOVRE)<br>Glaucoma / ocular hypertension: [NCT03891446](https://clinicaltrials.gov/study/NCT03891446) (P3; Bimatoprost SR, Standard of Care); [NCT04499248](https://clinicaltrials.gov/study/NCT04499248) (P1/P2; AGN-193408 SR, Lumigan, Sham Administration, Lumigan Vehicle, AGN-193408 SR); [NCT06822738](https://clinicaltrials.gov/study/NCT06822738) (P3; XEN63 Glaucoma Treatment System)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT04704921](https://clinicaltrials.gov/study/NCT04704921) (P2/P3; ABBV-RGX-314, ABBV-RGX-314, Ranibizumab (LUCENTIS®)); [NCT05407636](https://clinicaltrials.gov/study/NCT05407636) (P3; ABBV-RGX-314 Dose 1, ABBV-RGX-314 Dose 2, Aflibercept (EYLEA®)); [NCT04514653](https://clinicaltrials.gov/study/NCT04514653) (P2; Ranibizumab, ABBV-RGX-314 Dose 1, ABBV-RGX-314 Dose 2, ABBV-RGX-314 Dose 3, Local Steroid); [NCT07007065](https://clinicaltrials.gov/study/NCT07007065) (P3; Surabgene Lomparvovec (ABBV-RGX-314), Ranibizumab Control); [NCT03999801](https://clinicaltrials.gov/study/NCT03999801) (P2; RGX-314) |
| Adverum Biotechnologies | Neovascular age-related macular degeneration (wet AMD/nAMD) | Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06856577](https://clinicaltrials.gov/study/NCT06856577) (P3; Ixo-vec, Aflibercept); [NCT07482176](https://clinicaltrials.gov/study/NCT07482176) (P3; Ixo-vec, Aflibercept); [NCT05536973](https://clinicaltrials.gov/study/NCT05536973) (P2; ADVM-022, ADVM-022) |
| Aerie Pharmaceuticals | None found under scope | - |
| AffaMed Therapeutics | None found under scope | - |
| Aldeyra Therapeutics | None found under scope | - |
| Alimera Sciences | Radiation retinopathy | Radiation retinopathy: [NCT05844982](https://clinicaltrials.gov/study/NCT05844982) (P3; Faricimab, fluocinolone acetonide) |
| Alkahest | None found under scope | - |
| Allegro Ophthalmics | None found under scope | - |
| Amgen | Thyroid eye disease | Thyroid eye disease: [NCT06248619](https://clinicaltrials.gov/study/NCT06248619) (P3; Teprotumumab, Placebo); [NCT06401044](https://clinicaltrials.gov/study/NCT06401044) (P1/P2; AMG 732, Placebo); [NCT07438405](https://clinicaltrials.gov/study/NCT07438405) (P2; AMG 732) |
| Annexon Biosciences | Geographic atrophy | Geographic atrophy: [NCT06510816](https://clinicaltrials.gov/study/NCT06510816) (P3; Vonaprument, Sham Administration) |
| Apellis Pharmaceuticals | Geographic atrophy | Geographic atrophy: [NCT07215390](https://clinicaltrials.gov/study/NCT07215390) (P2; APL-3007, pegcetacoplan (APL-2), APL-3007, pegcetacoplan (APL-2), Placebo, Syfovre) |
| AsclepiX Therapeutics | Neovascular age-related macular degeneration (wet AMD/nAMD) | Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT05859776](https://clinicaltrials.gov/study/NCT05859776) (P1/P2; AXT107 Low Dose, AXT107 Mid Dose, AXT107 High Dose) |
| Astellas Pharma | Macular degenerative disease | Macular degenerative disease: [NCT03167203](https://clinicaltrials.gov/study/NCT03167203) (P1/P2; Human Embryonic Stem Cell-Derived Retinal Pigment Epithelial Cells) |
| Aviceda Therapeutics | Geographic atrophy | Geographic atrophy: [NCT05839041](https://clinicaltrials.gov/study/NCT05839041) (P2; AVD-104, Avacincaptad) |
| Bausch + Lomb | Dry eye disease; Glaucoma / ocular hypertension; Postoperative ocular pain | Dry eye disease: [NCT07128628](https://clinicaltrials.gov/study/NCT07128628) (P2; Lifitegrast/Perfluorohexyloctane Fixed Dose Combination, Lifitegrast, Perfluorohexyloctane)<br>Glaucoma / ocular hypertension: [NCT07168902](https://clinicaltrials.gov/study/NCT07168902) (P2; BL1107 Low dose, BL1107 High dose, Timolol maleate 0.5%)<br>Postoperative ocular pain: [NCT07412496](https://clinicaltrials.gov/study/NCT07412496) (P2; Topical Ocular BL1332 low dose, Topical Ocular BL1332 high dose, BL1332 Vehicle ophthalmic) |
| Bayer | Neovascular age-related macular degeneration (wet AMD/nAMD) | Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT07129239](https://clinicaltrials.gov/study/NCT07129239) (P3; Maintenance) |
| Beacon Therapeutics | X-linked retinitis pigmentosa | X-linked retinitis pigmentosa: [NCT03316560](https://clinicaltrials.gov/study/NCT03316560) (P1/P2; rAAV2tYF-GRK1-RPGR); [NCT04850118](https://clinicaltrials.gov/study/NCT04850118) (P2/P3; rAAV2tYF-GRK1-hRPGRco, Control); [NCT06275620](https://clinicaltrials.gov/study/NCT06275620) (P2; AGTC-501 (high dose and standard corticosteroid regimen), AGTC-501 (low dose and standard ); [NCT06333249](https://clinicaltrials.gov/study/NCT06333249) (P2; rAAV2tYF-GRK1-RPGR); [NCT07174726](https://clinicaltrials.gov/study/NCT07174726) (P2; Adeno-associated virus vector expressing a human RPGR gene) |
| Belite Bio | Geographic atrophy; Stargardt disease | Geographic atrophy: [NCT05949593](https://clinicaltrials.gov/study/NCT05949593) (P3; Tinlarebant, Placebo)<br>Stargardt disease: [NCT06388083](https://clinicaltrials.gov/study/NCT06388083) (P2/P3; Tinlarebant, Placebo) |
| Boehringer Ingelheim | Diabetic macular edema; Diabetic retinopathy; Geographic atrophy | Diabetic macular edema: [NCT07553429](https://clinicaltrials.gov/study/NCT07553429) (P1/P2; Low dose BI 3812465, Medium dose BI 3812465, High dose BI 3812465); [NCT06962839](https://clinicaltrials.gov/study/NCT06962839) (P2; BI 1815368, Placebo)<br>Diabetic retinopathy: [NCT06321302](https://clinicaltrials.gov/study/NCT06321302) (P2; BI 764524, Sham comparator to BI 764524, Aflibercept (Eylea®) - US only)<br>Geographic atrophy: [NCT06769048](https://clinicaltrials.gov/study/NCT06769048) (P2; Placebo-matching BI 1584862, BI 1584862); [NCT06722157](https://clinicaltrials.gov/study/NCT06722157) (P2; BI 771716, Pegcetacoplan, Sham comparator to BI 771716) |
| Chengdu Kanghong Biotechnology | Neovascular age-related macular degeneration (wet AMD/nAMD) | Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT05672121](https://clinicaltrials.gov/study/NCT05672121) (P1/P2; KH631); [NCT06458595](https://clinicaltrials.gov/study/NCT06458595) (P1/P2; KH658) |
| Clearside Biomedical | None found under scope | - |
| Curacle | Diabetic macular edema | Diabetic macular edema: [NCT07459829](https://clinicaltrials.gov/study/NCT07459829) (P2; CU06-1004, Placebo Control) |
| Eluminex Biosciences | None found under scope | - |
| EyeBio | None found under scope | - |
| EyePoint Pharmaceuticals | Diabetic macular edema; Neovascular age-related macular degeneration (wet AMD/nAMD) | Diabetic macular edema: [NCT07449923](https://clinicaltrials.gov/study/NCT07449923) (P3; EYP-1901, Aflibercept (2.0 mg)); [NCT07449936](https://clinicaltrials.gov/study/NCT07449936) (P3; EYP-1901, Aflibercept (2.0 mg))<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06668064](https://clinicaltrials.gov/study/NCT06668064) (P3; EYP-1901, Aflibercept (2.0 mg)); [NCT06683742](https://clinicaltrials.gov/study/NCT06683742) (P3; EYP-1901, Aflibercept (2.0 mg)) |
| Genentech | Diabetic macular edema; Diabetic retinopathy; Geographic atrophy; Neovascular age-related macular degeneration (wet AMD/nAMD); Radiation retinopathy | Diabetic macular edema: [NCT06850922](https://clinicaltrials.gov/study/NCT06850922) (P1/P2; RO7446603, Aflibercept, Faricimab)<br>Diabetic retinopathy: [NCT06790784](https://clinicaltrials.gov/study/NCT06790784) (P3; Vitrectomy, Endolaser, Faricimab, Panretinal Photocoagulation (PRP))<br>Geographic atrophy: [NCT05626114](https://clinicaltrials.gov/study/NCT05626114) (P2; OpRegen)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06847542](https://clinicaltrials.gov/study/NCT06847542) (P3; Susvimo PDS Implant, Ranibizumab)<br>Radiation retinopathy: [NCT05844982](https://clinicaltrials.gov/study/NCT05844982) (P3; Faricimab, fluocinolone acetonide) |
| GenSight Biologics | Leber hereditary optic neuropathy; Retinitis pigmentosa | Leber hereditary optic neuropathy: [NCT07303296](https://clinicaltrials.gov/study/NCT07303296) (P2; GS010 High dose, GS010 Low dose)<br>Retinitis pigmentosa: [NCT03326336](https://clinicaltrials.gov/study/NCT03326336) (P1/P2; Gene therapy: GS030-DP AND Medical device: GS030-MD) |
| Glaukos | Demodex blepharitis; Glaucoma / ocular hypertension; Keratoconus; Persistent corneal epithelial defect | Demodex blepharitis: [NCT07400965](https://clinicaltrials.gov/study/NCT07400965) (P2; GLK-321 low dose BID, GLK-321 mid dose BID, GLK-321 high dose BID, GLK-321 high dose QD, P)<br>Glaucoma / ocular hypertension: [NCT07075718](https://clinicaltrials.gov/study/NCT07075718) (P2/P3; Gen 2 Travoprost Intracameral Implant, Timolol eye drops 0.5%, Sham Procedure, Placebo eye); [NCT07495852](https://clinicaltrials.gov/study/NCT07495852) (P3; Gen 2 Travoprost Intracameral Implant, Timolol eye drops 0.5%, Sham Procedure, placebo eye); [NCT06066645](https://clinicaltrials.gov/study/NCT06066645) (P3; Travoprost Intraocular Implant, Sham procedure 1, iStent infinite, Sham procedure 2); [NCT06061718](https://clinicaltrials.gov/study/NCT06061718) (P3; iDose TR)<br>Keratoconus: [NCT07400952](https://clinicaltrials.gov/study/NCT07400952) (P2; GLK-221 Ophthalmic Solution, Placebo Ophthalmic Solution); [NCT05314738](https://clinicaltrials.gov/study/NCT05314738) (P1/P2; NXL Energy 1, NXL Energy 2, NXL Energy 3, Sham Treatment)<br>Persistent corneal epithelial defect: [NCT05966493](https://clinicaltrials.gov/study/NCT05966493) (P2; lufepirsen high dose, Vehicle, lufepirsen low dose) |
| Graybug Vision | None found under scope | - |
| Gyroscope Therapeutics | Geographic atrophy | Geographic atrophy: [NCT05481827](https://clinicaltrials.gov/study/NCT05481827) (P2; GT005) |
| iVeena | Progressive myopia / myopia | Progressive myopia / myopia: [NCT05761795](https://clinicaltrials.gov/study/NCT05761795) (P1/P2; IVMED 85, Placebo) |
| Iveric Bio | None found under scope | - |
| Janssen Pharmaceuticals | Geographic atrophy; X-linked retinitis pigmentosa | Geographic atrophy: [NCT06635148](https://clinicaltrials.gov/study/NCT06635148) (P2; JNJ-81201887, Sham Procedure)<br>X-linked retinitis pigmentosa: [NCT05926583](https://clinicaltrials.gov/study/NCT05926583) (P3; AAV5-hRKp.RPGR, AAV5-hRKp.RPGR); [NCT04794101](https://clinicaltrials.gov/study/NCT04794101) (P3; Genetic: AAV5-hRKp.RPGR Intermediate Dose, Genetic: AAV5-hRKp.RPGR Low Dose); [NCT06646289](https://clinicaltrials.gov/study/NCT06646289) (P2; AAV5-hRKp.RPGR, No intervention (Follow-Up assessment)) |
| jCyte | Retinitis pigmentosa | Retinitis pigmentosa: [NCT06912633](https://clinicaltrials.gov/study/NCT06912633) (P2; human retinal progenitor cells, Mock injection) |
| Kala Pharmaceuticals | None found under scope | - |
| Kalaris Therapeutics | None found under scope | - |
| Kiora Pharmaceuticals | Macular edema, other/unspecified; Retinitis pigmentosa | Macular edema, other/unspecified: [NCT06825702](https://clinicaltrials.gov/study/NCT06825702) (P2; KIO-104)<br>Retinitis pigmentosa: [NCT06628947](https://clinicaltrials.gov/study/NCT06628947) (P2; Placebo (Sterile Saline or Balanced Salt Solution), 100 μg KIO-301, 50 μg KIO-301) |
| Kodiak Sciences | Diabetic retinopathy; Inflammatory macular edema; Neovascular age-related macular degeneration (wet AMD/nAMD) | Diabetic retinopathy: [NCT06270836](https://clinicaltrials.gov/study/NCT06270836) (P3; Tarcocimab, Sham injection)<br>Inflammatory macular edema: [NCT06990399](https://clinicaltrials.gov/study/NCT06990399) (P3; KSI-101, Sham Comparator); [NCT06996080](https://clinicaltrials.gov/study/NCT06996080) (P3; KSI-101, Sham Comparator)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06556368](https://clinicaltrials.gov/study/NCT06556368) (P3; Tarcocimab tedromer, Tabirafusp tedromer, Aflibercept) |
| Kriya Therapeutics | Geographic atrophy; Thyroid eye disease | Geographic atrophy: [NCT06765980](https://clinicaltrials.gov/study/NCT06765980) (P1/P2; VV-14295)<br>Thyroid eye disease: [NCT07404111](https://clinicaltrials.gov/study/NCT07404111) (P1/P2; VV-14305, Sham (No Treatment)) |
| Kubota Vision | None found under scope | - |
| Kyowa Kirin | Diabetic macular edema; Neovascular age-related macular degeneration (wet AMD/nAMD) | Diabetic macular edema: [NCT06116916](https://clinicaltrials.gov/study/NCT06116916) (P2; KHK4951, Aflibercept Injection)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06116890](https://clinicaltrials.gov/study/NCT06116890) (P2; KHK4951, Aflibercept Injection) |
| Lineage Cell Therapeutics | None found under scope | - |
| LumiThera | None found under scope | - |
| Nanoscope Therapeutics | None found under scope | - |
| Neurotech Pharmaceuticals | Macular telangiectasia type 2 | Macular telangiectasia type 2: [NCT06397131](https://clinicaltrials.gov/study/NCT06397131) (P3; NT-501 CNTF Implant) |
| NGM Biopharmaceuticals | None found under scope | - |
| Novartis | Age-related macular degeneration, non-neovascular/unspecified; Biallelic RPE65 mutation-associated retinal dystrophy; Geographic atrophy; Retinitis pigmentosa | Age-related macular degeneration, non-neovascular/unspecified: [NCT05230537](https://clinicaltrials.gov/study/NCT05230537) (P2; Iptacopan (LNP023), Placebo)<br>Biallelic RPE65 mutation-associated retinal dystrophy: [NCT04516369](https://clinicaltrials.gov/study/NCT04516369) (P3; voretigene neparvovec)<br>Geographic atrophy: [NCT05481827](https://clinicaltrials.gov/study/NCT05481827) (P2; GT005); [NCT07441642](https://clinicaltrials.gov/study/NCT07441642) (P2; FWY003, Placebo)<br>Retinitis pigmentosa: [NCT03374657](https://clinicaltrials.gov/study/NCT03374657) (P1/P2; CPK850) |
| Ocugen | Geographic atrophy; Leber congenital amaurosis; Retinitis pigmentosa; Stargardt disease | Geographic atrophy: [NCT06018558](https://clinicaltrials.gov/study/NCT06018558) (P1/P2; OCU410)<br>Leber congenital amaurosis: [NCT05203939](https://clinicaltrials.gov/study/NCT05203939) (P1/P2; OCU400 Low Dose, OCU400 Med Dose, OCU400 High Dose, OCU400 Second Eye Dosing)<br>Retinitis pigmentosa: [NCT06388200](https://clinicaltrials.gov/study/NCT06388200) (P3; Sub-Retinal Administration of OCU400-301); [NCT05203939](https://clinicaltrials.gov/study/NCT05203939) (P1/P2; OCU400 Low Dose, OCU400 Med Dose, OCU400 High Dose, OCU400 Second Eye Dosing)<br>Stargardt disease: [NCT05956626](https://clinicaltrials.gov/study/NCT05956626) (P2/P3; OCU410ST) |
| Ocular Therapeutix | Diabetic retinopathy; Neovascular age-related macular degeneration (wet AMD/nAMD) | Diabetic retinopathy: [NCT07235085](https://clinicaltrials.gov/study/NCT07235085) (P3; Single intravitreal injection of axitinib hydrogel implant followed by a mock (sham) injec)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06223958](https://clinicaltrials.gov/study/NCT06223958) (P3; OTX-TKI (axitinib implant), Aflibercept); [NCT07516132](https://clinicaltrials.gov/study/NCT07516132) (P3; OTX-TKI); [NCT06495918](https://clinicaltrials.gov/study/NCT06495918) (P3; OTX-TKI, Aflibercept, Aflibercept) |
| Oculis | Dry eye disease; Uveitic/postoperative cystoid macular edema | Dry eye disease: [NCT07548632](https://clinicaltrials.gov/study/NCT07548632) (P2/P3; Artificial Tear Run-in, licaminlimab, Vehicle of licaminlimab)<br>Uveitic/postoperative cystoid macular edema: [NCT05608837](https://clinicaltrials.gov/study/NCT05608837) (P2; OCS-01) |
| Ocuphire Pharma | Night vision loss / nyctalopia | Night vision loss / nyctalopia: [NCT07140783](https://clinicaltrials.gov/study/NCT07140783) (P3; 0.75% Phentolamine Ophthalmic Solution, Placebo) |
| OcuTerra Therapeutics | None found under scope | - |
| Olix Pharmaceuticals | None found under scope | - |
| Opthea | None found under scope | - |
| Outlook Therapeutics | Diabetic macular edema; Neovascular age-related macular degeneration (wet AMD/nAMD); Retinal vein occlusion | Diabetic macular edema: [NCT05112861](https://clinicaltrials.gov/study/NCT05112861) (P3; bevacizumab)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT05112861](https://clinicaltrials.gov/study/NCT05112861) (P3; bevacizumab)<br>Retinal vein occlusion: [NCT05112861](https://clinicaltrials.gov/study/NCT05112861) (P3; bevacizumab) |
| Oxurion | None found under scope | - |
| Palatin Technologies | None found under scope | - |
| Perceive Biotherapeutics | Geographic atrophy; Neovascular age-related macular degeneration (wet AMD/nAMD) | Geographic atrophy: [NCT06087458](https://clinicaltrials.gov/study/NCT06087458) (P1/P2; VOY-101)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06087458](https://clinicaltrials.gov/study/NCT06087458) (P1/P2; VOY-101) |
| Perfuse Therapeutics | Diabetic retinopathy; Glaucoma / ocular hypertension | Diabetic retinopathy: [NCT06003751](https://clinicaltrials.gov/study/NCT06003751) (P2; PER-001 Intravitreal Implant - Low Dose, PER-001 Intravitreal Implant - High Dose, PER-001)<br>Glaucoma / ocular hypertension: [NCT05822245](https://clinicaltrials.gov/study/NCT05822245) (P1/P2; PER-001 Intravitreal Implant - Low Dose, PER-001 Intravitreal Implant - High Dose, PER-001) |
| Pfizer | None found under scope | - |
| Ray Therapeutics | Stargardt disease | Stargardt disease: [NCT07439887](https://clinicaltrials.gov/study/NCT07439887) (P1/P2; RTx-021) |
| Regeneron Pharmaceuticals | Diabetic macular edema; Geographic atrophy; Neovascular age-related macular degeneration (wet AMD/nAMD); Noninfectious uveitis | Diabetic macular edema: [NCT06491914](https://clinicaltrials.gov/study/NCT06491914) (P3; Aflibercept 8 mg)<br>Geographic atrophy: [NCT06541704](https://clinicaltrials.gov/study/NCT06541704) (P3; Pozelimab, Cemdisiran, Placebo)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06491914](https://clinicaltrials.gov/study/NCT06491914) (P3; Aflibercept 8 mg)<br>Noninfectious uveitis: [NCT07218770](https://clinicaltrials.gov/study/NCT07218770) (P1/P2; REGN7041) |
| REGENXBIO | Diabetic macular edema; Diabetic retinopathy; Neovascular age-related macular degeneration (wet AMD/nAMD) | Diabetic macular edema: [NCT06942520](https://clinicaltrials.gov/study/NCT06942520) (P2; RGX-314 Dose 1, RGX-314 Dose 2, Aflibercept (2.0 mg)); [NCT04567550](https://clinicaltrials.gov/study/NCT04567550) (P2; ABBV-RGX-314 Dose 1, ABBV-RGX-314 Dose 2, ABBV-RGX-314 Dose 3, Topical Steroid, ABBV-RGX-3)<br>Diabetic retinopathy: [NCT04567550](https://clinicaltrials.gov/study/NCT04567550) (P2; ABBV-RGX-314 Dose 1, ABBV-RGX-314 Dose 2, ABBV-RGX-314 Dose 3, Topical Steroid, ABBV-RGX-3)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT04704921](https://clinicaltrials.gov/study/NCT04704921) (P2/P3; ABBV-RGX-314, ABBV-RGX-314, Ranibizumab (LUCENTIS®)); [NCT05407636](https://clinicaltrials.gov/study/NCT05407636) (P3; ABBV-RGX-314 Dose 1, ABBV-RGX-314 Dose 2, Aflibercept (EYLEA®)); [NCT04514653](https://clinicaltrials.gov/study/NCT04514653) (P2; Ranibizumab, ABBV-RGX-314 Dose 1, ABBV-RGX-314 Dose 2, ABBV-RGX-314 Dose 3, Local Steroid) |
| RevOpsis Therapeutics | None found under scope | - |
| Roche | Age-related macular degeneration, non-neovascular/unspecified; Diabetic macular edema; Diabetic retinopathy; Myopic choroidal neovascularization; Neovascular age-related macular degeneration (wet AMD/nAMD); Thyroid eye disease | Age-related macular degeneration, non-neovascular/unspecified: [NCT02286089](https://clinicaltrials.gov/study/NCT02286089) (P1/P2; OpRegen)<br>Diabetic macular edema: [NCT04108156](https://clinicaltrials.gov/study/NCT04108156) (P3; PDS Implant Pre-Filled with 100 mg/mL Ranibizumab, Intravitreal Ranibizumab 0.5 mg Injecti)<br>Diabetic retinopathy: [NCT04661358](https://clinicaltrials.gov/study/NCT04661358) (P3; Fenofibrate, Placebo)<br>Myopic choroidal neovascularization: [NCT06176352](https://clinicaltrials.gov/study/NCT06176352) (P3; Faricimab, Ranibizumab, Sham Procedure)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT04567303](https://clinicaltrials.gov/study/NCT04567303) (P1/P2; Zifibancimig, Ranibizumab, Port Delivery Platform); [NCT03683251](https://clinicaltrials.gov/study/NCT03683251) (P3; PDS Implant with Ranibizumab 100 mg/mL); [NCT06847542](https://clinicaltrials.gov/study/NCT06847542) (P3; Susvimo PDS Implant, Ranibizumab); [NCT05562947](https://clinicaltrials.gov/study/NCT05562947) (P3; PDS With Ranibizumab (100 mg/mL), Ranibizumab (10 mg/mL)); [NCT04657289](https://clinicaltrials.gov/study/NCT04657289) (P3; Ranibizumab, Port Delivery System with Ranibizumab)<br>Thyroid eye disease: [NCT06106828](https://clinicaltrials.gov/study/NCT06106828) (P3; Satralizumab, Placebo); [NCT05987423](https://clinicaltrials.gov/study/NCT05987423) (P3; Satralizumab, Placebo) |
| Sandoz | None found under scope | - |
| Sanofi | Geographic atrophy; Neovascular age-related macular degeneration (wet AMD/nAMD); Stargardt disease | Geographic atrophy: [NCT07215234](https://clinicaltrials.gov/study/NCT07215234) (P1/P2; SAR446597, Sham Comparator)<br>Neovascular age-related macular degeneration (wet AMD/nAMD): [NCT06660667](https://clinicaltrials.gov/study/NCT06660667) (P1/P2; SAR402663, Diluent)<br>Stargardt disease: [NCT01736592](https://clinicaltrials.gov/study/NCT01736592) (P2; Long term follow up in all patients who received SAR422459 in previous study TDU13583) |
| Santen Pharmaceutical | Acquired blepharophimosis; Glaucoma / ocular hypertension | Acquired blepharophimosis: [NCT06514612](https://clinicaltrials.gov/study/NCT06514612) (P3; STN1013800 (0.1% Oxymetazoline Hydrochloride) eye drops in single dose containers, Placebo)<br>Glaucoma / ocular hypertension: [NCT06666855](https://clinicaltrials.gov/study/NCT06666855) (P3; DE-117B Eye Drops, Latanoprost) |
| Smilebiotek Zhuhai | Age-related macular degeneration, non-neovascular/unspecified | Age-related macular degeneration, non-neovascular/unspecified: [NCT07189169](https://clinicaltrials.gov/study/NCT07189169) (P3; QA108 granules, QA108 granules placebo) |
| Stealth BioTherapeutics | Age-related macular degeneration, non-neovascular/unspecified | Age-related macular degeneration, non-neovascular/unspecified: [NCT06373731](https://clinicaltrials.gov/study/NCT06373731) (P3; Elamipretide, Placebo) |
| Surrozen | None found under scope | - |
| Tenpoint Therapeutics | None found under scope | - |
| Thea Laboratories | Glaucoma / ocular hypertension; Leber congenital amaurosis; Ocular inflammation associated with ocular prostheses; Progressive myopia / myopia; Retinitis pigmentosa; Vernal keratoconjunctivitis | Glaucoma / ocular hypertension: [NCT05389267](https://clinicaltrials.gov/study/NCT05389267) (P1/P2; Kinezodianone R hydrochloride, Placebo)<br>Leber congenital amaurosis: [NCT06891443](https://clinicaltrials.gov/study/NCT06891443) (P3; sepofarsen, Placebo IVT)<br>Ocular inflammation associated with ocular prostheses: [NCT05668455](https://clinicaltrials.gov/study/NCT05668455) (P3; Hydrocortisone, Dexamethasone, Povidone)<br>Progressive myopia / myopia: [NCT07522242](https://clinicaltrials.gov/study/NCT07522242) (P2; T10430 lower dose, T10430 middle dose, T10430 higher dose, Vehicle)<br>Retinitis pigmentosa: [NCT06627179](https://clinicaltrials.gov/study/NCT06627179) (P2; Intravitreal Injection of Ultevursen, No intervention, will not receive any active study i)<br>Vernal keratoconjunctivitis: [NCT07169695](https://clinicaltrials.gov/study/NCT07169695) (P2; Slit Lamp Examination, Far Best Corrected Visual Acuity (BCVA), T1695, Ciclosporin, Cornea) |
| Unity Biotechnology | None found under scope | - |
| Valo Health | Diabetic retinopathy | Diabetic retinopathy: [NCT05393284](https://clinicaltrials.gov/study/NCT05393284) (P2; OPL-0401 Dose 1, Placebo) |
| Vanda Pharmaceuticals | Dry eye disease | Dry eye disease: [NCT07179055](https://clinicaltrials.gov/study/NCT07179055) (P2; VSJ-110, Placebo) |
| Vanotech | None found under scope | - |
| Verseon | None found under scope | - |
| Visgenx | None found under scope | - |
| Vitranu | None found under scope | - |
| VivaVision Biotech | Dry eye disease; Noninfectious uveitis | Dry eye disease: [NCT06360133](https://clinicaltrials.gov/study/NCT06360133) (P3; VVN001 Ophthalmic Solution, 5%, VVN001 Ophthalmic Solution, Vehicle)<br>Noninfectious uveitis: [NCT07136805](https://clinicaltrials.gov/study/NCT07136805) (P3; VVN461 Ophthalmic Solution 1.0%, 1.0% prednisolone acetate) |

## Raw Company List and Counts
| Company | Active Phase 2/3 ophthalmology trials found | Disease-state count |
|---|---:|---:|
| 4D Molecular Therapeutics | 5 | 4 |
| AbbVie / Allergan | 12 | 6 |
| Adverum Biotechnologies | 3 | 1 |
| Aerie Pharmaceuticals | 0 | 0 |
| AffaMed Therapeutics | 0 | 0 |
| Aldeyra Therapeutics | 0 | 0 |
| Alimera Sciences | 1 | 1 |
| Alkahest | 0 | 0 |
| Allegro Ophthalmics | 0 | 0 |
| Amgen | 3 | 1 |
| Annexon Biosciences | 1 | 1 |
| Apellis Pharmaceuticals | 1 | 1 |
| AsclepiX Therapeutics | 1 | 1 |
| Astellas Pharma | 1 | 1 |
| Aviceda Therapeutics | 1 | 1 |
| Bausch + Lomb | 3 | 3 |
| Bayer | 1 | 1 |
| Beacon Therapeutics | 7 | 1 |
| Belite Bio | 2 | 2 |
| Boehringer Ingelheim | 5 | 3 |
| Chengdu Kanghong Biotechnology | 2 | 1 |
| Clearside Biomedical | 0 | 0 |
| Curacle | 1 | 1 |
| Eluminex Biosciences | 0 | 0 |
| EyeBio | 0 | 0 |
| EyePoint Pharmaceuticals | 4 | 2 |
| Genentech | 5 | 5 |
| GenSight Biologics | 2 | 2 |
| Glaukos | 8 | 4 |
| Graybug Vision | 0 | 0 |
| Gyroscope Therapeutics | 1 | 1 |
| iVeena | 1 | 1 |
| Iveric Bio | 0 | 0 |
| Janssen Pharmaceuticals | 4 | 2 |
| jCyte | 1 | 1 |
| Kala Pharmaceuticals | 0 | 0 |
| Kalaris Therapeutics | 0 | 0 |
| Kiora Pharmaceuticals | 2 | 2 |
| Kodiak Sciences | 4 | 3 |
| Kriya Therapeutics | 2 | 2 |
| Kubota Vision | 0 | 0 |
| Kyowa Kirin | 2 | 2 |
| Lineage Cell Therapeutics | 0 | 0 |
| LumiThera | 0 | 0 |
| Nanoscope Therapeutics | 0 | 0 |
| Neurotech Pharmaceuticals | 1 | 1 |
| NGM Biopharmaceuticals | 0 | 0 |
| Novartis | 5 | 4 |
| Ocugen | 4 | 4 |
| Ocular Therapeutix | 4 | 2 |
| Oculis | 2 | 2 |
| Ocuphire Pharma | 1 | 1 |
| OcuTerra Therapeutics | 0 | 0 |
| Olix Pharmaceuticals | 0 | 0 |
| Opthea | 0 | 0 |
| Outlook Therapeutics | 1 | 3 |
| Oxurion | 0 | 0 |
| Palatin Technologies | 0 | 0 |
| Perceive Biotherapeutics | 1 | 2 |
| Perfuse Therapeutics | 2 | 2 |
| Pfizer | 0 | 0 |
| Ray Therapeutics | 1 | 1 |
| Regeneron Pharmaceuticals | 4 | 4 |
| REGENXBIO | 5 | 3 |
| RevOpsis Therapeutics | 0 | 0 |
| Roche | 11 | 6 |
| Sandoz | 0 | 0 |
| Sanofi | 4 | 3 |
| Santen Pharmaceutical | 2 | 2 |
| Smilebiotek Zhuhai | 1 | 1 |
| Stealth BioTherapeutics | 1 | 1 |
| Surrozen | 0 | 0 |
| Tenpoint Therapeutics | 0 | 0 |
| Thea Laboratories | 6 | 6 |
| Unity Biotechnology | 0 | 0 |
| Valo Health | 1 | 1 |
| Vanda Pharmaceuticals | 1 | 1 |
| Vanotech | 0 | 0 |
| Verseon | 0 | 0 |
| Visgenx | 0 | 0 |
| Vitranu | 0 | 0 |
| VivaVision Biotech | 2 | 2 |
