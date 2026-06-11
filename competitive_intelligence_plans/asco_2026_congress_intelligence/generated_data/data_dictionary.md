# ASCO 2026 curated data dictionary

Generated outputs are source-linked extracts derived from the local `ASCO-2026-Abstracts` corpus. Raw source files are not modified.

## `abstract_fact.csv`

One row per ASCO abstract. Key fields include `uid`, `contentId`, `presentationId`, `abstractNumber`, `title`, `meetingYear`, `meetingName`, source `url`, local raw file paths and hashes, `sessionType`, `track`, publication/update timestamps, first speaker, content availability flags, body length, body hash, table count, and available ASCO taxonomy fields.

## `abstract_text_section.csv`

Long-format section extraction. One row per extracted section per abstract. Sections include `background`, `methods`, `results`, `conclusions`, `unclassified`, and `table_footer_N` rows where ASCO HTML table footers were present.

## `abstract_table.csv` and `abstract_table.jsonl`

Parsed HTML table extraction. CSV contains one table per row with caption, footer, dimensions, confidence, and `cellsJson`. JSONL preserves the same table rows as nested arrays.

## `topic_session_classification.csv`

One row per abstract with rule-based classification from available ASCO fields and abstract text: session, track, tumor/topic area, study phase, design, line of therapy, evidence type, endpoints, modalities, NCT IDs, trial acronym candidates, priority score/tier, audience scores, and source URL.

## `role_specific/*.csv`

Role-filtered priority lists for Medical Affairs, HEOR, Market Access, Commercial, and Launch. Records are included when the role relevance score is at least 30 and are sorted by role relevance and overall priority.

## `source_inventory.csv`

SHA-256 source inventory for top-level ASCO files and per-abstract JSON/HTML files used by the pipeline.

## `priority_scoring_config.json`

Transparent scoring weights and keyword dictionaries used by the current processing run. Scores are triage aids, not analyst-approved conclusions.
