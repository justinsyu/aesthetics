# Group D Decision-Rationale Collection Manifest

Scope: New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Rhode Island, and South Carolina.

Broad crawling was stopped at the user's request. This manifest summarizes the documents already saved under `raw/` and extracted under `text/`. The row-level manifest is preserved in `manifest.csv` and `manifest.json`.

## Collection Counts

| State | Records in manifest | Successful HTTP 200 | Blocked/error records | Seed URLs not attempted |
|---|---:|---:|---:|---:|
| New Mexico | 23 | 22 | 1 | 0 |
| New York | 18 | 13 | 5 | 0 |
| North Carolina | 90 | 90 | 0 | 0 |
| North Dakota | 90 | 90 | 0 | 0 |
| Ohio | 22 | 11 | 11 | 0 |
| Oklahoma | 90 | 88 | 2 | 0 |
| Oregon | 80 | 79 | 1 | 0 |
| Pennsylvania | 97 | 91 | 6 | 0 |
| Rhode Island | 90 | 90 | 0 | 0 |
| South Carolina | 90 | 90 | 0 | 0 |
| **Total** | **690** | **664** | **26** | **0** |

## Key Collected Source Types

- New Mexico: HCA PDL page, combined P&T/DUR public notice, pharmacy/utilization pages, PA form, related provider pages.
- New York: NYRx preferred drug program and related class coverage pages; direct NYSDOH DUR pages/PDFs were attempted but blocked by 403.
- North Carolina: PDL archive, PDL guidelines, current PDL, DUR agenda, meeting/notice pages, drug and clinical coverage pages.
- North Dakota: PDL page, DUR board pages, PDL versions, agendas, meeting handouts, minutes, notices.
- Ohio: statute, P&T bylaws, P&T agendas/minutes, UPDL library page, drug coverage / PA related pages; several old pharmacy URLs were 404 or invalid.
- Oklahoma: DUR board, agendas, packets, archive pages, policies/procedures, board members, public comment/speaker materials.
- Oregon: OHA P&T page, OHP PDL page, DURM pages, meeting pages, recommendations/newsletters, operating materials.
- Pennsylvania: statewide PDL page, pharmacy services pages, PA PDL meeting page, bylaws, September 2025 agenda, clinical guideline PDFs.
- Rhode Island: EOHHS P&T page, open-meeting entry, provider updates, minutes PDFs, historical minutes.
- South Carolina: SCDHHS P&T taxonomy page, contractor P&T page, single PDL notice, pharmacy manual/pages, historical P&T minutes.

## Blocked Or Uncollected URLs

All seed URLs from `state-monitoring-matrix.md` and `meeting-dates-2025-06-2026-05.csv` were attempted or already represented. The following material gaps remain because a saved attempt returned an error or an unusable URL:

- New Mexico: one HCA confidentiality/privacy PDF returned 403.
- New York: NYSDOH DUR main page, 2025/2026 meeting pages, membership PDF, and bylaws PDF returned 403/CloudFront blocks. NYRx contractor pages were still collected.
- Ohio: several legacy `pharmacy.medicaid.ohio.gov` and `medicaid.ohio.gov/stakeholders-and-partners/phm/...` URLs returned 404; several SPBM document-library URLs contained unescaped spaces and were recorded as invalid URLs.
- Oklahoma: two linked URLs returned 404, including one malformed quoted URL from extracted page text.
- Oregon: one OSU student-experience page returned 403 and is not decision-rationale relevant.
- Pennsylvania: several broad `pa.gov` links failed with timeout, SSL EOF, or local socket exhaustion during the earlier crawl; the relevant PDL, P&T, agenda, and clinical-guideline sources were collected elsewhere in the corpus.

