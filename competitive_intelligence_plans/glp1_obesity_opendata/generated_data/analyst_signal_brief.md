# Analyst Signal Brief: GLP-1 Obesity OpenData

Run timestamp: 2026-05-28T21:14:03+00:00

## Status

- Validation status: `review_required`.
- This brief is source-derived from deterministic lexical matches and requires analyst review before use as final CI.
- CMS annual spending signals are usable for product-level spend/claim screening where brand-specific rows exist.
- Large P0 sources remain metadata-only unless the run is executed with `--include-large-source-downloads`.

## Largest Latest-Year Public Payer Spending Signals

- `cms/part-d-spending` / Ozempic: 2023 spending $9,194,048,435; claims 6,927,972; YoY spending change 98.6545%; rule `overall_rows_only`.
- `cms/part-d-spending` / Trulicity: 2023 spending $7,363,856,224; claims 5,316,020; YoY spending change 18.2893%; rule `overall_rows_only`.
- `cms/medicaid-spending` / Trulicity: 2023 spending $2,867,003,544; claims 2,784,493; YoY spending change 34.5427%; rule `overall_rows_only`.
- `cms/part-d-spending` / Mounjaro: 2023 spending $2,361,384,157; claims 1,821,486; YoY spending change 1539.4499%; rule `overall_rows_only`.
- `cms/medicaid-spending` / Ozempic: 2023 spending $2,085,485,949; claims 2,064,001; YoY spending change 117.9022%; rule `overall_rows_only`.
- `cms/part-d-spending` / Rybelsus: 2023 spending $1,665,906,943; claims 1,075,026; YoY spending change 70.8807%; rule `overall_rows_only`.
- `cms/part-d-spending` / Victoza: 2023 spending $1,321,848,711; claims 867,680; YoY spending change -15.1465%; rule `overall_rows_only`.
- `cms/medicaid-spending` / Victoza: 2023 spending $596,557,354; claims 584,992; YoY spending change -7.0262%; rule `overall_rows_only`.
- `cms/medicaid-spending` / Wegovy: 2023 spending $541,318,642; claims 409,729; YoY spending change 1220.1853%; rule `overall_rows_only`.
- `cms/medicaid-spending` / Mounjaro: 2023 spending $426,155,516; claims 408,495; YoY spending change 1156.8624%; rule `overall_rows_only`.
- `cms/part-d-spending` / Soliqua: 2023 spending $302,998,642; claims 263,822; YoY spending change 40.314%; rule `overall_rows_only`.
- `cms/part-d-spending` / Bydureon: 2023 spending $284,117,600; claims 212,868; YoY spending change -20.1212%; rule `overall_rows_only`.

## Supply and Lifecycle Watch

- FDA limited-availability candidate: Victoza (2 unique source rows; 6 lexical match records).
- FDA shortage-watch candidate: Saxenda (1 unique source rows; classifications {'current_available': 1}).
- FDA shortage-watch candidate: ingredient:liraglutide (7 unique source rows; classifications {'current_available': 6, 'to_be_discontinued': 1}).

## Caveats

- Source rows are candidate matches, not adjudicated findings.
- Manufacturer names and ingredient-only matches are not enough for definitive brand attribution.
- Public CMS spending is gross public-program spending context and not manufacturer net revenue.
- Spending direction fields describe spending change, not claims change.
- Non-consecutive annual comparisons are labeled as latest-vs-prior-observed rather than strict YoY.
- The next execution step is analyst review of `match_qc_sample.csv`, then a large-source scan for `cms/sdud`, `cms/nadac`, and `cms/drug-rebate-products` if network/runtime constraints permit.
