# Meeting-Date Calendar Notes

Research window: June 1, 2025 through May 31, 2026. Current date: May 27, 2026.

Generated artifacts:

- `meeting-dates-2025-06-2026-05.csv`: normalized meeting-date evidence rows.
- `meeting-dates-2025-06-2026-05.json`: same rows as JSON for reuse.
- `meeting-calendar-2025-06-2026-05.html`: standalone calendar visualization.
- `meeting-calendar-notes.md`: counting rules, status definitions, and validation summary.

Validation summary:

- Five parallel state-group subagents validated the data against public source URLs.
- Validated corrections were applied after the full subagent pass.
- Corrected dataset rows: 200.
- Plotted committee-date rows: 196.
- States with at least one exact plotted date: 50 of 50.
- States without an exact plotted date in this source pass: None.

Counting rules:

- Plotted statuses: confirmed and planned.
- Excluded from bubble counts but retained in the table: cancelled and packet_only.
- The calendar counts committee-date rows, not unique states. Virginia and Tennessee include both P&T/PAC and DUR rows where validators identified separate public decision-body meetings.
- Planned rows are visibly labeled separately in the calendar and source table.
