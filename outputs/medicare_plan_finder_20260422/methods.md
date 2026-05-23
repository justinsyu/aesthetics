# Methods: CMS Medicare Plan Finder Part D PUF, April 2026

## Data source

The analysis used the CMS Monthly Prescription Drug Plan Formulary and Pharmacy Network Information public use file distribution titled `2026-04-22`, which was the latest distribution listed by CMS/data.gov on May 19, 2026. The next estimated monthly release listed by CMS/data.gov was May 20, 2026, so the April 22 file was treated as the most recent available file at the time of analysis.

- Dataset page: https://catalog.data.gov/dataset/monthly-prescription-drug-plan-formulary-and-pharmacy-network-information
- Direct ZIP: https://data.cms.gov/sites/default/files/2026-04/675bb472-ce7a-48a1-b5ca-8ce7c9fc8c58/2026_20260415.zip
- Record layout: https://data.cms.gov/sites/default/files/2025-10/0564eb37-402d-4110-bd98-2d5399dc30e7/PUFRecordLayout-2026.pdf
- Methodology: https://data.cms.gov/sites/default/files/2025-10/8f1d8b42-bfd1-4f9c-b86d-b92af0c6f3d5/Methodology-PUF-2026.pdf
- Downloaded ZIP SHA-256: `b9d7c523f9b92c67a39e5eccf7e1609a5a1ed11a7fe6f39af4e05fd568a4f223`

## Files processed

The CMS ZIP contains nested component ZIP files. The analysis extracted and processed the plan information, geographic locator, basic formulary, beneficiary cost, insulin beneficiary cost, excluded drugs, and indication-based coverage files. The pharmacy-network component was retained as compressed parts because the six parts are large; a streaming profiler script is included for replication.

Observed row counts from the extracted files were:

- Plan information: 112,635
- Basic drugs formulary: 1,122,175
- Beneficiary cost: 173,090
- Insulin beneficiary cost: 43,136
- Excluded drugs formulary: 13,717
- Indication-based coverage formulary: 367
- Geographic locator: 3,279

## Analytic units

Plan information rows are service-area-expanded. Plan-level analyses therefore deduplicated records using `CONTRACT_ID`, `PLAN_ID`, and `SEGMENT_ID`, consistent with the CMS record layout. Contract IDs beginning with `H` were classified as local MA-PD, `R` as regional MA-PD, and `S` as stand-alone PDP. Suppressed plans identified by `PLAN_SUPPRESSED_YN = Y` were retained for denominator transparency; CMS states that suppressed plans appear in plan information but not other component files.

Formulary-level analyses used `FORMULARY_ID`. Plan-linked formulary analyses merged deduplicated plan records to formulary summaries using `FORMULARY_ID`. Cost-sharing analyses used the beneficiary cost and insulin beneficiary cost files at the plan-tier-days-supply-channel level.

## Measures

Plan universe measures included counts by contract type, median premiums, zero-premium shares, median deductibles, and shares with deductibles at or above $615.

Formulary measures included the number of distinct NDC/RxCUI entries per formulary and the within-formulary percentage of entries flagged for quantity limits, prior authorization, step therapy, and any of those utilization-management fields.

Selected-drug analyses used `SELECTED_DRUG_YN` in the basic formulary file. RxCUI labels were obtained from the National Library of Medicine RxNorm API and cached locally in `analysis/rxnorm_names_cache.json`; these labels were used only for slide readability.

Specialty-tier measures used beneficiary cost rows with `COVERAGE_LEVEL = 1`, `DAYS_SUPPLY = 1`, and `TIER_SPECIALTY_YN = Y`. Insulin measures used `DAYS_SUPPLY = 1` rows from the insulin beneficiary cost file and summarized populated copay and coinsurance fields. Blank insulin fields were treated as missing, not zero.

County availability measures counted unsuppressed local MA-PD plan-segments by `STATE` and `COUNTY_CODE`. Stand-alone PDP region summaries used deduplicated stand-alone PDP plan-segments by `PDP_REGION_CODE`.

## Limitations

All estimates are unweighted by enrollment, claims, utilization, prescriptions, population, morbidity, rebates, manufacturer discounts, or net prices. The PUF describes submitted plan design and Plan Finder inputs, not realized patient experience or outcomes. CMS notes that Medicare Plan Finder pharmacy network and drug pricing data are updated every two weeks, so a monthly PUF may not exactly match the current Medicare.gov display. The files do not reflect manufacturer discounts applied under the Medicare Part D Manufacturer Discount Program.

## Replication commands

From `/Users/justinyu/Desktop/linkedin-posts`:

```bash
mkdir -p outputs/medicare_plan_finder_20260422/raw outputs/medicare_plan_finder_20260422/extracted
curl -L --fail --continue-at - --output outputs/medicare_plan_finder_20260422/raw/2026_20260415.zip \
  'https://data.cms.gov/sites/default/files/2026-04/675bb472-ce7a-48a1-b5ca-8ce7c9fc8c58/2026_20260415.zip'
shasum -a 256 outputs/medicare_plan_finder_20260422/raw/2026_20260415.zip
unzip -o outputs/medicare_plan_finder_20260422/raw/2026_20260415.zip -d outputs/medicare_plan_finder_20260422/extracted
for f in outputs/medicare_plan_finder_20260422/extracted/*.zip; do
  case "$(basename "$f")" in
    pharmacy\ networks*) ;;
    *) unzip -o "$f" -d outputs/medicare_plan_finder_20260422/extracted ;;
  esac
done
python3 outputs/medicare_plan_finder_20260422/scripts/analyze_plan_finder.py
python3 outputs/medicare_plan_finder_20260422/scripts/build_deck.py
node /Users/justinyu/.codex/skills/cohere-style-tan/scripts/export_html_slides_pdf.mjs \
  --input /Users/justinyu/Desktop/linkedin-posts/outputs/medicare_plan_finder_20260422/deck/medicare_plan_finder_20260422_cohere_tan.html \
  --output /Users/justinyu/Desktop/linkedin-posts/outputs/medicare_plan_finder_20260422/deck/medicare_plan_finder_20260422_cohere_tan.pdf \
  --screenshots-dir /Users/justinyu/Desktop/linkedin-posts/outputs/medicare_plan_finder_20260422/deck/export/screenshots \
  --render-check-dir /Users/justinyu/Desktop/linkedin-posts/outputs/medicare_plan_finder_20260422/deck/export/render-check
```

The streaming pharmacy-network profiler can be run separately:

```bash
bash outputs/medicare_plan_finder_20260422/scripts/profile_pharmacy_network.sh
```
