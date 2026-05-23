# 340B affluent-area hospital infographic source log

## Scope

The infographic shows selected active HRSA OPAIS hospital parent entities whose listed street-address ZIP Code Tabulation Area has ACS 2024 five-year median household income above the U.S. ACS 2024 five-year median.

## Data Sources

- HRSA OPAIS public reports page: https://340bopais.hrsa.gov/reports
  - Downloaded file: `340B_CoveredEntityJson_Daily_20260521_141430.zip`
  - Extracted file: `OPA_CE_DAILY_PUBLIC.JSON`
  - Download date: 2026-05-21
- Census Reporter API over U.S. Census ACS table B19013:
  - Release: `acs2024_5yr`, years 2020-2024
  - Table: B19013, median household income in the past 12 months in 2024 inflation-adjusted dollars
  - U.S. benchmark endpoint: https://api.censusreporter.org/1.0/data/show/acs2024_5yr?table_ids=B19013&geo_ids=01000US
  - ZCTA endpoints use the form `https://api.censusreporter.org/1.0/data/show/acs2024_5yr?table_ids=B19013&geo_ids=86000US{zip}`
- HRSA eligibility overview: https://www.hrsa.gov/opa/eligibility-and-registration

## Transform

1. Download HRSA Covered Entity Daily Export JSON from the OPAIS public reports page.
2. Keep rows with `participating == TRUE`.
3. Keep hospital entity types: `DSH`, `CAH`, `PED`, `RRC`, `SCH`, and `CAN`.
4. Keep parent hospital rows where `subName` is empty.
5. Join each parent row to ACS 2024 five-year ZCTA median household income by the five-digit ZIP code in `streetAddress.zip`.
6. Compare ZCTA median household income with U.S. ACS 2024 five-year median household income of $80,734.
7. Select the top 10 rows by ZCTA median household income for the displayed infographic.

## Caveats

- ZCTA median household income is a geography-level attribute, not a hospital patient-mix measure.
- The join uses the street-address ZIP code listed in HRSA OPAIS; hospital systems may serve patients across many ZIP codes.
- 340B eligibility is not inferred from ZCTA income.
- The displayed list is selected from the downloaded HRSA daily export snapshot and should be refreshed before reuse in a later reporting period.
