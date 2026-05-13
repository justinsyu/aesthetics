# AI Pharma Deals Tracker Source Validity Audit

Date checked: 2026-05-07

## Scope

Validated the 77 non-summary CSV rows in `ai_pharma_deals_tracker_07may2026.csv` against the linked source URLs and targeted web search corroboration. This audit focused on whether the source links are legitimate and whether they support the listed parties, date, and value where applicable.

## Summary

- 77 deal rows checked.
- Most source links are legitimate and substantively support the listed deal parties and deal subject.
- Local direct-link fetch audit: 74 links returned reachable pages with expected party-name matches; 3 returned HTTP 403 but were corroborated by web search or alternate indexed sources.
- Several rows have monetary/date/classification caveats. The infographic is directionally supported by the CSV, but the `$87.7B` aggregate should be treated as a tracker-derived estimate, not a fully primary-source reconciled total.

## Material Caveats

| CSV row | Deal | Caveat |
|---:|---|---|
| 32 | CSPC Pharmaceuticals / AstraZeneca | CSV lists `$18.5B`. AstraZeneca's linked release supports `$1.2B` upfront and up to `$3.5B` development/regulatory milestones, plus further commercial/sales milestones, but does not itself state `$18.5B`. Reuters/C&EN corroborate an up-to-$18.5B figure attributed to CSPC disclosures. |
| 52 | TuneLab / Eli Lilly | Link is legitimate, but it supports Lilly launching TuneLab, not a transaction with “TuneLab” as a counterparty. The `$1B` refers to estimated cost of proprietary data used to train models, not deal value. |
| 59 | Gero / Chugai | Linked Chugai source supports the parties/date but states up to approximately `$250M`, not `$1,000M`. |
| 75 | Genesis / Incyte | Linked release supports `$30M` upfront and up to `$295M` milestones per target. CSV’s `$885M` total is not directly stated; depending on target-count interpretation, total could differ. |
| 76 | Noetik / GSK | Linked source supports the deal and `$50M` in upfront capital/near-term milestones, but the date is January 8, 2026, not January 8, 2025. |
| 27 | Unnatural Products / Novartis | Source says up to `$100M` upfront/pre-IND payments plus up to `$1.7B` in milestones. CSV’s split/total is not exact. |
| 4, 14 | Profluent/Lilly; Infinimmune/Merck | Sources support the milestone amounts shown, but those amounts are not clean “total deal value” because upfront and/or funding components are undisclosed. |

## Link Issues

- Row 17 Simulations Plus: CSV URL appears malformed with an encoded suffix, but canonical Business Wire/Simulations Plus mirrors support the item.
- Row 35 OpenAI/Torch: CNBC link returned HTTP 403 in direct fetch; search snippets/syndication corroborate the reported transaction.
- Row 71 Repertoire/Genentech: original link was not accessible in one verification pass; alternate Flagship Pioneering/StreetInsider versions corroborate the announcement.
- Rows 50, 61, 63 returned HTTP 403 in local direct fetch, but web search corroborated the linked subject matter.

## Sources Spot-Checked

- AstraZeneca/CSPC: https://www.astrazeneca.com/media-centre/press-releases/2026/astrazeneca-agrees-obesity-and-t2d-deal-with-cspc.html
- Reuters mirror for AstraZeneca/CSPC: https://www.investing.com/news/stock-market-news/astrazeneca-strikes-deal-for-up-to-185-billion-to-license-weightloss-drugs-from-chinas-cspc-4476023
- Lilly TuneLab: https://investor.lilly.com/news-releases/news-release-details/lilly-launches-tunelab-platform-give-biotechnology-companies
- Chugai/Gero: https://www.chugai-pharm.co.jp/news/detail/20250707160000_1487.html
- XtalPi/DoveTree: https://www.nasdaq.com/press-release/xtalpi-and-dovetree-announce-landmark-6-billion-ai-drug-discovery-collaboration-2025
- Monte Rosa/Novartis: https://www.globenewswire.com/news-release/2025/09/15/3149823/0/en/monte-rosa-therapeutics-announces-collaboration-with-novartis-for-degraders-to-treat-immune-mediated-diseases.html
- Noetik/GSK: https://finance.yahoo.com/news/gsk-licenses-noetik-ai-foundation-140000300.html
