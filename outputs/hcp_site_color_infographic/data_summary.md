# Drug/HCP Website Color Patterns - Data Summary

Source: `/Users/justinyu/Desktop/linkedin-posts/outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv`
Total unique URL rows: **681**
Rows with extractable hex palettes: **650** (95.4%)
Rows without extractable palette values: **31** (4.6%)

## Core Finding
Across 681 drug/HCP website URLs, the dominant visual grammar is a clinical blue base, readable neutral scaffolding, and a secondary accent system that usually moves into teal/aqua, purple/pink, or warm orange/gold. The aggregate should be described as website palette prevalence, not as a pure measure of brand identity, because several large manufacturer platforms and web frameworks repeat the same colors across many pages.

## Color Family Distribution
Counts use unique hexes per URL across primary and secondary palette fields. “Site presence” counts each color family at most once per URL.

| Color family | Hex mentions | Share of all hex mentions | Site presence | Share of all URLs |
|---|---:|---:|---:|---:|
| Blue | 918 | 23.2% | 494 | 72.5% |
| Cyan / aqua | 495 | 12.5% | 315 | 46.3% |
| Dark neutral | 411 | 10.4% | 330 | 48.5% |
| Gray / neutral | 374 | 9.5% | 323 | 47.4% |
| White / off-white | 274 | 6.9% | 233 | 34.2% |
| Black / near-black | 216 | 5.5% | 204 | 30.0% |
| Red | 211 | 5.3% | 181 | 26.6% |
| Green / teal | 208 | 5.3% | 162 | 23.8% |
| Light neutral | 205 | 5.2% | 192 | 28.2% |
| Pink / magenta | 203 | 5.1% | 154 | 22.6% |
| Orange / coral | 194 | 4.9% | 155 | 22.8% |
| Purple / violet | 151 | 3.8% | 108 | 15.9% |
| Yellow / gold | 91 | 2.3% | 84 | 12.3% |

## Raw Most Frequent Hexes
These include common CSS/framework colors and neutrals, so use them as “what appears often,” not necessarily “brand-owned colors.”

| Hex | Family | Sites | Primary-field sites | Secondary-field sites |
|---|---|---:|---:|---:|
| `#212529` | Black / near-black | 79 | 53 | 26 |
| `#3860BE` | Blue | 67 | 16 | 51 |
| `#D8D8D8` | Light neutral | 65 | 29 | 36 |
| `#696969` | Gray / neutral | 64 | 41 | 23 |
| `#6C757D` | Gray / neutral | 50 | 38 | 12 |
| `#555555` | Dark neutral | 48 | 23 | 25 |
| `#DC3545` | Red | 47 | 25 | 22 |
| `#333333` | Dark neutral | 43 | 31 | 12 |
| `#0D6EFD` | Blue | 37 | 29 | 8 |
| `#383838` | Dark neutral | 37 | 37 | 0 |
| `#007BFF` | Blue | 34 | 28 | 6 |
| `#0000C9` | Blue | 29 | 21 | 8 |
| `#808080` | Gray / neutral | 27 | 20 | 7 |
| `#0000EE` | Blue | 25 | 11 | 14 |
| `#666666` | Gray / neutral | 24 | 19 | 5 |

## Distinctive Representative Swatches
More useful for an infographic swatch strip because generic grays, white, near-black, and common Bootstrap/link/status colors are filtered out.

| Hex | Family | Sites | Primary-field sites | Secondary-field sites |
|---|---|---:|---:|---:|
| `#3860BE` | Blue | 67 | 16 | 51 |
| `#0000C9` | Blue | 29 | 21 | 8 |
| `#7A00E6` | Purple / violet | 24 | 23 | 1 |
| `#198754` | Green / teal | 20 | 8 | 12 |
| `#0064C1` | Blue | 16 | 5 | 11 |
| `#223D83` | Blue | 15 | 15 | 0 |
| `#FF6900` | Orange / coral | 13 | 2 | 11 |
| `#337AB7` | Blue | 13 | 12 | 1 |
| `#0DCAF0` | Cyan / aqua | 12 | 0 | 12 |
| `#BE2BBB` | Pink / magenta | 12 | 8 | 4 |
| `#0063C3` | Blue | 11 | 6 | 5 |
| `#8A6D3B` | Orange / coral | 11 | 3 | 8 |
| `#003865` | Blue | 10 | 8 | 2 |
| `#0B41CD` | Blue | 10 | 8 | 2 |
| `#3E47E9` | Blue | 9 | 8 | 1 |
| `#A94442` | Red | 9 | 1 | 8 |
| `#0693E3` | Cyan / aqua | 9 | 2 | 7 |
| `#537BAA` | Blue | 8 | 6 | 2 |

## Top Distinctive Swatches by Family
- **Blue:** `#3860BE` (67), `#0000C9` (29), `#0064C1` (16), `#223D83` (15), `#337AB7` (13), `#0063C3` (11), `#003865` (10), `#0B41CD` (10)
- **Cyan / aqua:** `#0DCAF0` (12), `#0693E3` (9), `#019CDC` (7), `#107CAD` (5), `#17A2B8` (4), `#06A59A` (4), `#1AA2DC` (4), `#00857C` (3)
- **Green / teal:** `#198754` (20), `#32AE88` (6), `#117744` (4), `#3C763D` (3), `#509E2F` (3), `#48A23F` (3), `#00D084` (2), `#93D500` (2)
- **Purple / violet:** `#7A00E6` (24), `#5718B0` (8), `#5A21B0` (3), `#A05EAC` (2), `#410099` (2), `#2E008B` (1), `#462B89` (1), `#341D45` (1)
- **Pink / magenta:** `#BE2BBB` (12), `#852166` (7), `#672666` (6), `#CC3366` (4), `#EC008C` (4), `#870051` (3), `#D50180` (3), `#E20177` (2)
- **Orange / coral:** `#FF6900` (13), `#8A6D3B` (11), `#D59F0F` (2), `#FFC845` (2), `#F7941E` (2), `#C75201` (2), `#FF671F` (2), `#F58220` (2)
- **Red:** `#A94442` (9), `#FF5D2D` (5), `#E1242A` (4), `#FF0000` (4), `#DE5052` (3), `#521010` (3), `#EB1700` (3), `#E00000` (2)
- **Yellow / gold:** `#FFD100` (2), `#FFCD00` (2), `#FFCC00` (2), `#FFDD00` (2), `#B2CA02` (2), `#FEE013` (2), `#FEE124` (2), `#FFFF00` (1)

## Palette Archetypes
Site-level archetypes ignore neutral support colors when a stronger hue is present.

| Archetype | Sites | Share | Example palettes |
|---|---:|---:|---|
| Blue + teal/aqua | 295 | 43.3% | QVAR RediHaler (Teva): #007EC3, #992321, #083A81, #404040, #117744; ANNOVERA (TherapeuticsMD): #273478, #1FBCAB, #E50B79, #942C6B, #3B82F6; HCPs (TherapeuticsMD): #2E008B, #2D2D2D, #0085AD, #0D6EFD, #212529 |
| Blue + warm accent | 79 | 11.6% | BENDEKA (Unknown): #696969, #8F99BC, #E44926, #555555, #D8D8D8; IMVEXXY (TherapeuticsMD): #1C2A5B, #212529, #1863DC, #F48475, #F1E7E4; Leqselvi (Sun Pharma): #212529, #16436D, #FFB908, #CF0000, #6AAAE4 |
| Purple/pink-led | 68 | 10.0% | Firazyr (Takeda): #F58026, #676767, #82214A, #E1242A, #F1F1F1; RENFLEXIS (Organon): #171717, #E20177, #D02F76, #53565A, #75787B; JUBLIA (Bausch Health): #444444, #462B89, #999999, #2D7C8F, #626366 |
| Blue + purple/pink | 63 | 9.3% | IBSRELA (Ardelyx): #92278F, #EBF0F3, #333333, #262262, #696969; Official (Teva): #6D3075, #1B6CA7, #696969, #0000EE, #F5F5F5; BOTOX (AbbVie): #80379B, #F4F4F4, #545454, #727272, #D8D8D8 |
| Green/teal/aqua-led | 58 | 8.5% | ONYDA XR (Unknown): #E5E7EB, #014358, #078092, #00A2BD, #1275B3; JATENZO (Tolmar): #58B947, #D6D6D6, #1A303F, #F2F2F2, #FF6900; ZIMHI (ZMI Pharma): #373B3C, #666666, #E10A1E, #EDF1F3, #212121 |
| Blue-led | 57 | 8.4% | VICTOZA (Novo Nordisk): #001965, #005AD2, #939AA7, #D8D8D8, #C1C1C1; ACTIMMUNE (Amgen): #D6D6D6, #0063C3, #3D3E3E, #F4F4F4, #1032CF; FASENRA (Unknown): #E1E1E1, #003865, #F4F4F4, #333F48, #666666 |
| Neutral-led | 21 | 3.1% | Tyenne (Unknown): #000000; Lexette (Unknown): #FFFFFF, #000000, #F5F5F5, #666666, #CCCCCC; https://betaseron.com (Unknown): #808080 |
| Warm-led | 9 | 1.3% | AIRDUO DIGIHALER / AIRDUO RESPICLICK (Teva): #636466, #696969, #4D4D4F, #FFFF00, #555555; PRIALT (TerSera): #FEC524; SHINGRIX (GSK): #4C4D4E, #9E0B0F, #D71920, #EFEFED, #544F40 |

## Company / Status Caveats
- Top companies by row count: Unknown (123); Pfizer (46); Sanofi (36); Genentech (29); Amgen (20); Bristol Myers Squibb (14); AbbVie (14); Takeda (13); Novartis (13); AstraZeneca (11); Azurity (11); Janssen (10).
- Status distribution: 200 (312); rendered (220); ok (100); error (22); 403 (20); blocked (3); http_200 (2); partial (1); 404 (1).
- RWE assessment values in the compiled data: no (390); yes (149); maybe (121); not_assessed (15); unknown (6).
- Potential lower-confidence rows with blocked/error/navigation/404/timeout language: **165**. Keep these in the denominator only with a footnote.
- Repeated corporate domains/platforms, especially PfizerPro, Sanofi campus, Gene/Roche, AbbVie, J&J/Janssen, Novartis, AstraZeneca, Amgen, and GSK, can amplify house colors relative to independent brand sites.

## Narrative Takeaways
1. **Blue is the category anchor.** Blue appears on 494 of 681 URLs (72.5%), far ahead of any single expressive hue family.
2. **The second color is where brands differentiate.** Teal/aqua is the most common companion family, followed by purple/pink and warm accent colors.
3. **Neutral systems matter.** Dark, gray, black, white, and light-neutral colors appear often because HCP websites carry dense prescribing, safety, dosing, and access content.
4. **Warm colors tend to signal action or emphasis.** Red, orange/coral, and yellow/gold are common as accents but comparatively rare as the main palette direction.
5. **Platform repetition is a real caveat.** Treat the data as a snapshot of rendered HCP/drug web design patterns, not a definitive census of brand guidelines.

## Suggested One-Page Infographic Layout
- Hero: “681 drug/HCP URLs analyzed; 95.4% had extractable hex palettes.”
- Main visual: site-presence bar chart by color family, led by Blue at 72.5%.
- Swatches: two rows, “raw frequent colors” and “distinctive brand-like colors.”
- Archetype tiles: Blue + teal/aqua, Blue + warm accent, Blue + purple/pink, Purple/pink-led, Green/teal/aqua-led, Warm-led, Neutral-led.
- Footnote: blocked/error rows and repeated manufacturer platforms affect aggregate prevalence.
