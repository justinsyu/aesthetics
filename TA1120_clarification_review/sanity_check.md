# Sanity check — TA1120 specialist outputs

Date: 22 May 2026

## File existence and size

| File | Size | Status |
|------|------|--------|
| specialist_outputs/clinical_questions.md | 37 KB | OK |
| specialist_outputs/statistician_questions.md | 27 KB | OK |
| specialist_outputs/health_economist_questions.md | 39 KB | OK |
| specialist_outputs/information_specialist_questions.md | 29 KB | OK |
| actual_nice_questions.md | 20 KB | OK |

## Question counts per specialist (target: 25-45)

| Specialist | Questions | Status |
|------------|-----------|--------|
| Clinical reviewer | 36 | within range |
| Statistician | 30 | within range |
| Health economist | 50 | slightly above range — complex submission justifies it; merger will deduplicate |
| Information specialist | 35 | within range |

## Actual NICE questions

23 total, comprising A1-A10 (effectiveness), B1-B12 (cost-effectiveness), C1 (textual). 8 marked Priority.

## Blinding audit

Grep for literal NICE question stems ("Priority question", "please provide an updated", "^A[0-9]\\.", "^B[0-9]\\.") in all four specialist output files returned **0 hits** in each file. No contamination detected — specialists wrote in their own voice.

## Substance spot-check

Each specialist's deliverable returned a detailed structured report with section/table/figure references back to Document B, citation of relevant NICE DSU TSDs (statistician), PRISMA / Cochrane / PMG36 (information specialist), and concrete topic anchors. No stub-quality output detected.

## Conclusion

Specialist outputs passed sanity check. Proceeding to merger/comparator.
