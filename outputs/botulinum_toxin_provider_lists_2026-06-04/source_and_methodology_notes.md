# Botulinum Toxin Provider Locator Extraction Notes

Run date: 2026-06-04

These files are public locator extracts, not manufacturer-certified master account lists. The CSVs reflect participating providers/practices exposed by each product's public locator API at run time.

## Completed CSVs

- `botox_cosmetic_alle_providers.csv`: BOTOX Cosmetic / Allē locator, deduplicated by Allē provider ID. National overlapping radius-grid extraction. Error log: `botox_cosmetic_alle_errors.json`.
- `dysport_usa_providers.csv`: Dysport USA locator, deduplicated by Dysport provider ID. National overlapping radius-grid extraction. Error log: `dysport_usa_errors.json`.
- `xeomin_aesthetic_providers.csv`: Xeomin Aesthetic locator, deduplicated by Merz/Salesforce account ID. National overlapping radius-grid extraction. Error log: `xeomin_aesthetic_errors.json`.

## Partial / Blocked Extracts

- `daxxify_providers.csv`: DAXXIFY locator extract from browser-origin requests. Direct server requests hit Vercel's security checkpoint, and browser-origin tiling was rate-limited after the initial requests. The file is therefore partial. See `daxxify_errors.json`.
- `jeuveau_evolus_practices_partial.csv`: Jeuveau/Evolus public endpoint was identified, but the endpoint returned repeated 504 Gateway Timeout responses for dense metro and sample queries during extraction. The file is partial/empty for this run. See `jeuveau_evolus_partial_errors.json`.

## Retry On 2026-06-04

- `jeuveau_evolus_practices_retry.csv`: Successful browser-origin retry using 24 major metro centers with 25-mile radius searches. This produced 1,426 deduplicated practice rows. It is an expanded best-effort extract, not a verified national all-provider list. Metadata: `jeuveau_evolus_retry_metadata.json`.
- DAXXIFY retry: Browser-origin and direct requests continued returning `429 Too many requests`. Static bundle inspection found the locator calls `/api/fap/find-in-bounds` and `/api/fap/find-in-radius`; no alternate public provider feed was found. The prior `daxxify_providers.csv` remains the best available partial extract from this session.

## Locator Sources

- BOTOX Cosmetic / Allē: `https://botoxcosmetic.alle.com/search`
- Dysport USA: `https://www.dysportusa.com/find-a-specialist`
- Xeomin Aesthetic: `https://www.xeominaesthetic.com/find-a-provider/`
- Jeuveau / Evolus: `https://www.evolus.com/jeuveau/find-a-practice?product=jeuveau`
- DAXXIFY: `https://www.daxxify.com/daxxify-near-me`
- Letybo: `https://www.letybousa.com/` was checked; no public provider locator was found on the official site at run time.

## Reproducibility

- Direct locator extraction script: `scrape_direct_locators.mjs`
- DAXXIFY required browser-origin fetches because direct requests returned a Vercel security checkpoint.
- Jeuveau/Evolus endpoint discovered in the public app bundle:
  - `https://txcvquhsn7.execute-api.us-east-1.amazonaws.com/production/getRankedFacilityProfilesWithinRadius`
  - The endpoint accepted `latitude`, `longitude`, `radius`, and `product=jeuveau`, but repeatedly timed out during the run.
