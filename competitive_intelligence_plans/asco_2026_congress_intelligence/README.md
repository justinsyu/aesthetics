# ASCO 2026 Congress Intelligence

## Product dashboard

Run from this folder:

```powershell
python -m http.server 8766
```

Then open:

```text
http://localhost:8766/index.html
```

The dashboard loads `generated_data/dashboard_data.json`. If that file is unavailable, it uses a small embedded fallback. Use the `Load JSON` control in the dashboard to test a newly generated JSON bundle without replacing the bundled file.

Expected dashboard JSON collections:

```json
{
  "dataset": {},
  "metrics": [],
  "sessionTypes": [],
  "tracks": [],
  "prioritySignals": [],
  "audienceWorkspaces": [],
  "workflow": [],
  "sources": []
}
```

## Data processing

This folder contains two complementary data-processing scripts. Both read the local `ASCO-2026-Abstracts` corpus and write curated outputs under `generated_data`; neither writes to the raw ASCO folder.

Build the dashboard bundle and compact role queues:

```powershell
python competitive_intelligence_plans\asco_2026_congress_intelligence\scripts\build_asco_intelligence_data.py
```

Build the deeper extraction outputs for section review, table parsing, role-specific CSV work queues, source inventory, and validation:

Run from the repository root:

```powershell
python competitive_intelligence_plans\asco_2026_congress_intelligence\scripts\process_asco_2026.py
```

Optional arguments:

```powershell
python competitive_intelligence_plans\asco_2026_congress_intelligence\scripts\process_asco_2026.py `
  --raw-dir C:\Users\Justin\Desktop\linkedin-posts-mac\ASCO-2026-Abstracts `
  --output-dir C:\Users\Justin\Desktop\linkedin-posts-mac\competitive_intelligence_plans\asco_2026_congress_intelligence\generated_data
```

Generated outputs:

- `dashboard_data.json`: compact dashboard data bundle for `index.html`.
- `priority_signals.json`: top scored signal records used by the dashboard.
- `role_outputs/*.json` and `role_outputs/*.csv`: compact dashboard-oriented role queues.
- `abstract_fact.csv`: one normalized source-linked row per abstract.
- `abstract_text_section.csv`: Background, Methods, Results, Conclusions, unclassified text, and table footers.
- `abstract_table.csv` / `abstract_table.jsonl`: detected HTML tables with row/column counts and parsed cells.
- `topic_session_classification.csv`: topic, session, phase, design, endpoint, modality, priority, and audience scores.
- `role_specific/*.csv`: filtered priority lists for Medical Affairs, HEOR, Market Access, Commercial, and Launch.
- `source_inventory.csv`: SHA-256 source inventory for top-level and per-abstract files.
- `validation_summary.md` / `validation_summary.json`: reconciliation and extraction counts.
- `priority_scoring_config.json`: transparent scoring thresholds and keyword maps.

Raw ASCO files are read only.
