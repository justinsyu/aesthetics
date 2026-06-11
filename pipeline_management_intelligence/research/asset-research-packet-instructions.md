# Asset Research Packet Instructions

For the assigned pipeline asset, create one JSON packet at `pipeline_management_intelligence/research/packets/<asset_id>.json`.

Use direct source-backed evidence wherever possible. Start with the provided ClinicalTrials.gov URL, then search for manufacturer pipeline pages, press releases, labels or analog labels, payer policies, and price/cost sources or close analogs. Do not use marketed/approved status to re-include an asset; if the assigned record is actually marketed/approved, flag that as an exclusion concern in `quality_flags`.

Required JSON shape:

```json
{
  "asset_id": "",
  "asset_name": "",
  "manufacturer": "",
  "checked_at": "YYYY-MM-DD",
  "research_status": "source_backed",
  "mechanism": "",
  "phase": "",
  "development_status": "",
  "expected_launch_window": "",
  "expected_launch_date": "",
  "clinical_differentiation": "Low|Modest|Meaningful|High",
  "clinical_summary": "",
  "safety_summary": "",
  "estimated_annual_cost_low": 0,
  "estimated_annual_cost_high": 0,
  "budget_impact_level": "Low|Medium|High",
  "disruption_risk": "Low|Medium|High",
  "recommended_action": "Monitor|Prepare|Actively Plan",
  "management_tools": [],
  "evidence_gaps": [],
  "sources": [
    {
      "source_id": "ctgov:NCT00000000",
      "title": "",
      "type": "Clinical trial|Company source|Regulatory source|Cost source|Payer policy analog|Analog label|News",
      "url": "",
      "date": "YYYY-MM-DD",
      "supports": []
    }
  ],
  "rationale": {
    "expected_launch_window": {
      "value": "",
      "basis_type": "source_direct|source_derived",
      "method": "",
      "explanation": "",
      "source_refs": []
    },
    "annual_cost_range": {
      "value": "low-high",
      "basis_type": "source_direct|source_derived",
      "method": "",
      "explanation": "",
      "source_refs": []
    },
    "clinical_differentiation": {
      "value": "",
      "basis_type": "source_direct|source_derived",
      "method": "",
      "explanation": "",
      "source_refs": []
    },
    "budget_impact": {
      "value": "",
      "basis_type": "source_derived",
      "method": "",
      "explanation": "",
      "source_refs": []
    },
    "disruption_risk": {
      "value": "",
      "basis_type": "source_derived",
      "method": "",
      "explanation": "",
      "source_refs": []
    },
    "recommended_action": {
      "value": "",
      "basis_type": "source_derived",
      "method": "",
      "explanation": "",
      "source_refs": []
    }
  },
  "quality_flags": []
}
```

Rules:
- Include every direct ClinicalTrials.gov source URL supporting the asset, including multiple NCT records if the asset is aggregated.
- Every estimate must explain whether it is directly sourced or derived from an analog/source-backed method.
- Annual cost may use an analog when no direct price exists, but the analog and adjustment must be cited.
- Keep explanations concise and dashboard-ready.
- Do not edit `data/research-overrides.json`; integration happens centrally after packets are reviewed.
