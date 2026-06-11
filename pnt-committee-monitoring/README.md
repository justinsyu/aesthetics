# P&T Committee Monitoring

Research date: May 27, 2026

Scope: public information for all 50 states on Medicaid pharmacy and therapeutics, preferred drug list, drug utilization review, or equivalent decision bodies. The research focused on how decisions are made, when meetings or decisions happen, who is involved, what materials are public, and what gaps remain.

Files:

- `state-monitoring-matrix.md`: normalized all-state matrix with key sources, process notes, cadence, participants, public materials, and gaps.
- `meeting-dates-2025-06-2026-05.csv`: deterministic meeting-date rows for the June 1, 2025 through May 31, 2026 research window.
- `meeting-dates-2025-06-2026-05.json`: JSON version of the meeting-date evidence rows.
- `meeting-calendar-2025-06-2026-05.html`: standalone calendar visualization with circle size indicating same-day committee meeting concentration.
- `meeting-calendar-notes.md`: counting rules, status definitions, and no-exact-date state summary.
- `meeting-calendar-2025-06-2026-05-no-active-links.pdf`: calendar-only PDF export generated separately from the corrected data, with no reference appendix and no active PDF hyperlinks.
- `validation-summary.md`: validation method, applied corrections, and PDF hyperlink verification summary.
- `export_no_link_pdf.py`: local script used to generate the no-active-link PDF from the corrected CSV.

Method:

- Five parallel subagents researched ten states each.
- Official state Medicaid, health agency, boards/commissions, or state Medicaid pharmacy contractor portals were prioritized.
- Statutes, regulations, or credible state-linked contractor materials were used where official committee pages were incomplete.
- Notes distinguish committee recommendations, agency final decisions, meeting materials, and final PDL/formulary implementation where public sources allow.
- Meeting-date calendar rows include row-level source URLs and status flags. Cancelled, packet-only, and no-exact-date findings are retained in the dataset but excluded from the plotted meeting-count bubbles.
- The no-active-link PDF is generated without modifying or stripping links from the source HTML, CSV, or JSON artifacts.

High-level takeaways:

- Most states publish at least one of the following: PDL, meeting agenda, minutes, committee page, or DUR/P&T board page.
- The most transparent states publish agendas, minutes, rosters, recommendation packets, public comment instructions, and final decision or PDL change documents.
- Several states use DUR boards, drug formulary committees, prior authorization advisory committees, or PDL advisory committees instead of a body explicitly named "P&T Committee."
- Cost and rebate analysis is commonly less public than clinical review, public testimony, meeting agendas, and final PDL changes.
- Current rosters and meeting calendars are unevenly available; some states publish schedules clearly while others only expose PDLs, state plan language, or contractor documents.
