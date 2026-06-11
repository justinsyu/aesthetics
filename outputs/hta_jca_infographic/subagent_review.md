# Subagent review: HTA JCA infographic

Reviewed artifacts:

- `hta_jca_infographic.html`
- `hta_jca_infographic.pdf`
- `normalized_data.json`
- `source_notes.md`

## Findings

The requested metric story is represented consistently across the normalized data, source notes, HTML, and exported PDF:

- Ongoing JCAs: 15
- Discontinued JCAs: 1
- Completed JCAs: 0
- Oncology-related ongoing JCAs: 13 of 15
- Substance mix: 9 chemicals, 4 ATMPs, 2 biologicals
- Orphan split: 8 yes / 7 no
- Accelerated assessments: 0
- Variations to existing MA: 0
- Reverts to standard timetable: 0
- EMA validation window: 27 Mar 2025 to 26 Mar 2026
- Lead assessor concentration: Germany IQWiG leads 4 ongoing assessments; Ireland NCPE, Austria FSI, and Sweden TLV each show 2 in the visual
- Validation timeline: 12 active records validated in 2025 and 3 in 2026, with monthly counts shown for Mar 2025 through Mar 2026

The PDF is present, one page, and text-selectable. Text extraction confirmed the KPI values, timeline values, validation window, and lead-assessor statement are available in the PDF text layer.

## Limitations

- The lead-assessor chart in the infographic shows the top six displayed agencies only; `normalized_data.json` retains all nine lead assessors.
- PDF text extraction line-wraps and uppercases some labels, so exact phrase searches can miss labels such as `chemical substances`, `ATMPs`, `biologicals`, and `orphan yes/no split` even though the values and visual labels are present.
- The oncology-related count appears to be based on indication text classification rather than an explicit workbook field; this is appropriate for the stated story but should remain described as a derived metric.
- I did not modify the HTML, PDF, JSON, or source notes.
