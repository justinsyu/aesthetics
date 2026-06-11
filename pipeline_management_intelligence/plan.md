# Pipeline Management Intelligence Product Plan

## Product Intent

Build an updateable payer pipeline management product that turns public pipeline signals into a working formulary-readiness view. The product should answer what is coming, when it may launch, what clinical and cost profile it may carry, and what payer action is warranted before launch.

This is not a slide deck. It uses the cohere-style-tan font and color tokens, but the output is a dense operational dashboard with code-native text, filters, tables, and refreshable data.

## Primary Users

- Market access strategy teams
- Managed care account teams
- Formulary and pipeline planning teams
- HEOR and evidence strategy teams

## Data Sources

The first version uses no-key public data and maintains a seed fallback.

| Source | Use | Refresh Role |
| --- | --- | --- |
| ClinicalTrials.gov API v2 | Active and recruiting studies, sponsor, phase, condition, intervention, dates, trial URLs | Primary pipeline universe |
| openFDA Drugs@FDA API | Recent regulatory metadata and approvals where queryable | Context and validation |
| openFDA Label API | Label safety and indication text for approved comparators/assets | Context and validation |
| Manual seed assets | Ensures product remains usable if public APIs fail | Fallback and demo baseline |

Paid sources such as Evaluate Pharma, Citeline, BioMedTracker, MMIT, SSR, Red Book, or claims feeds can be added later behind the same schema.

## Canonical Schema

Each asset is normalized to:

```json
{
  "asset_id": "string",
  "asset_name": "string",
  "manufacturer": "string",
  "therapeutic_area": "string",
  "indication": "string",
  "mechanism": "string",
  "phase": "string",
  "development_status": "string",
  "expected_launch_window": "0-12 months | 12-24 months | 24-36 months | 36+ months | Launched",
  "expected_launch_date": "YYYY-MM-DD or null",
  "clinical_differentiation": "Low | Modest | Meaningful | High",
  "clinical_summary": "string",
  "safety_summary": "string",
  "estimated_annual_cost_low": 0,
  "estimated_annual_cost_high": 0,
  "budget_impact_level": "Low | Medium | High",
  "disruption_risk": "Low | Medium | High",
  "recommended_action": "Monitor | Prepare | Actively Plan",
  "management_tools": ["PA", "ST", "QL", "SP"],
  "evidence_gaps": ["string"],
  "sources": [{"title": "string", "type": "string", "url": "string", "date": "YYYY-MM-DD"}],
  "last_updated": "ISO-8601"
}
```

## Scoring Model

The current model is intentionally transparent and heuristic. It is designed to be replaced or calibrated as proprietary pricing, epidemiology, and payer policy data become available.

Inputs:

- Development phase and regulatory proximity
- Estimated launch window
- Sponsor type and trial status
- Clinical differentiation proxy from phase, endpoint maturity, and intervention novelty
- Therapeutic area cost archetype
- Population and budget impact proxy from indication category

Outputs:

- `clinical_differentiation`: Low, Modest, Meaningful, High
- `budget_impact_level`: Low, Medium, High
- `disruption_risk`: Low, Medium, High
- `recommended_action`: Monitor, Prepare, Actively Plan

Rules of thumb:

- Phase 3, NDA/BLA-submitted, and approved assets receive higher readiness weight.
- High-cost specialty, oncology, rare disease, hematology, and gene/cell therapy assets receive higher budget-impact weight.
- Assets with near-term launch windows and high budget impact become high disruption risk.
- Assets with incomplete comparative evidence retain evidence-gap flags even when risk is high.

## Refresh Cadence

Default cadence: monthly.

Recommended cadence by use case:

- Monthly: standing class-level monitoring
- Weekly: launch-year assets, FDA advisory committee periods, PDUFA windows
- Daily: active conference, FDA action week, or post-readout monitoring

The script supports:

```bash
node scripts/refresh-data.mjs --once
node scripts/refresh-data.mjs --interval 24h
node scripts/refresh-data.mjs --limit 120 --once
node scripts/refresh-data.mjs --areas Oncology,Immunology,Hematology --limit 90 --once
node scripts/refresh-data.mjs --condition oncology --limit 60 --once
```

`--interval` keeps the process alive and refreshes repeatedly. Use Task Scheduler, cron, GitHub Actions, or a hosted job runner for production scheduling.

## Product Outputs

- Dashboard UI: filters, launch timeline, disruption heatmap, asset table, selected asset detail, evidence gaps, source log
- JSON dataset: `data/pipeline-assets.json`
- CSV export: `data/pipeline-assets.csv`
- Source log: included in JSON and visible in the UI
- Update metadata: source status, run time, condition scope, refresh cadence, API fallback state

## Execution Plan

1. Create the product folder and plan.
2. Build a refresh script that pulls ClinicalTrials.gov records, normalizes them, scores them, and writes JSON/CSV.
3. Add seed fallback assets for offline/API-failure operation.
4. Build the static dashboard with cohere-style-tan fonts and colors.
5. Run the refresh script to generate the initial data.
6. Start a local server and verify the product in browser.
7. Update CI skill guidance with the reusable lesson: competitive intelligence outputs may need an updateable product/data app rather than a static report.

## Production Extensions

- Add paid pipeline databases as source adapters.
- Add plan-specific lives and prevalence estimates.
- Add WAC/net price benchmarks and analog launch curves.
- Add explicit PDUFA and FDA advisory committee ingestion.
- Add manual analyst override fields with audit history.
- Add snapshot comparison to show what changed since the prior refresh.
- Add automated alerting when risk scores or launch windows change.

## Traceability Requirements

Every generated asset must carry field-level rationale for:

- `expected_launch_window`: source date field, phase-specific month offset, estimated launch date, and refresh date used for bucket assignment
- `estimated_annual_cost_low` and `estimated_annual_cost_high`: therapeutic-area analog range, multiplier, and reason the value is a planning estimate rather than a sourced price
- `clinical_differentiation`: phase, endpoint count, intervention count, score, and method limits
- `budget_impact_level`: cost range, therapeutic area, broad-population signal, and method limits
- `disruption_risk`: launch window, budget impact, clinical differentiation, phase, score, and method limits
- `recommended_action`: direct mapping from risk level to monitor, prepare, or actively plan
- `clinical_trial_links`: one or more direct ClinicalTrials.gov study URLs that support the active/ongoing trial signal for the row
- `marketed_status`: openFDA Drugs@FDA application number, original approval date, product marketing status, and source URL when the product is already FDA-approved / marketed

The UI should keep the table scannable and expose rationales in the selected-asset detail pane. Source links should remain row-level and field rationales should clearly distinguish internet-sourced fields from generated planning estimates.

## Validation

- Exclude non-pharma academic and medical-center sponsors before ranking. Validate that no retained asset has a lead sponsor matching academic, hospital, health-system, clinic, institute, university, or cancer-center patterns unless a pharma manufacturer/collaborator is explicitly identified as the commercial owner.
- Require portfolio breadth in each refreshed dataset. Validate that `assets[*].therapeutic_area` contains more than one distinct value, or fail the run with a message that the condition/source query is too narrow for cross-area pipeline intelligence.
- Require field-level rationale and traceability for every asset. Validate that expected launch window, annual cost range, disruption risk, and recommended action each have a non-empty rationale tied to source evidence or a named heuristic rule, plus at least one source URL for analyst review.
- Require every retained row to include at least one direct ClinicalTrials.gov study URL. When multiple retained studies map to the same drug, manufacturer, therapeutic area, and indication, merge them into one row and retain all NCT links.
- Use openFDA Drugs@FDA to override launch timing for already FDA-approved / marketed products. FDA-marketed products should show `Marketed` rather than a future launch window, with approval date, application number, marketing status, and FDA source URL in the rationale.
