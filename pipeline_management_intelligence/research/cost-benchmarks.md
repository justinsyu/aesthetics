# Pipeline Management Intelligence Cost Benchmarks

Check date: 2026-05-27

Purpose: source strategy and conservative annual-cost analog ranges for dashboard planning estimates. These are drug-acquisition analog ranges, not net payer cost estimates. They exclude rebates, discounts, patient assistance, administration, wastage, adherence, site-of-care effects, and plan-specific utilization.

## Source strategy

Use public, stable sources that can be cited in the dashboard data as analog support:

- Manufacturer price / affordability pages for current list price or WAC anchors. These are useful when a product page explicitly states a monthly, per-dose, or per-vial list price.
- FDA labels via Drugs@FDA/DailyMed for dosing frequency. Pair label dosing with WAC/list price to annualize a drug-only benchmark.
- CMS ASP drug pricing files for Medicare Part B buy-and-bill products when manufacturer WAC pages are unavailable or need triangulation.
- CMS Medicare Part D / Part B drug spending dashboards for observed gross spend context. Use as a reasonableness check, not as the primary analog, because per-beneficiary spend can reflect discontinuation, dosing, rebates, and mixed indications.
- Peer-reviewed or non-profit reports for categories where exact WAC is fragmented across many products, especially MS disease-modifying therapies and hemophilia factor/non-factor prophylaxis.

Do not cite ClinicalTrials.gov as a cost source. ClinicalTrials.gov supports phase, sponsor, status, and timing; annual cost should cite analog-price support separately.

## Recommended ranges

| Therapeutic area | Conservative annual-cost analog range | Recommended source label | Public analog support |
| --- | ---: | --- | --- |
| Oncology | $140,000-$260,000 | Oncology analog WAC: PD-1 / targeted oncology annualized from public list-price anchors | KEYTRUDA public cost page states list price per 3-week or 6-week dose, annualizing to roughly $213K before discounts: https://www.keytruda.com/financial-support/ . BMS OPDIVO cost/support page gives current per-vial or per-dose patient-facing cost context: https://www.opdivo.com/support-and-resources/financial-support . CMS ASP files can triangulate Part B oncology biologic payment limits: https://www.cms.gov/medicare/payment/fee-for-service-providers/part-b-drugs/asp-pricing-files |
| Immunology | $45,000-$100,000 | Immunology biologic analog WAC: IL-23 / IL-17 / atopic-dermatitis biologics | SKYRIZI official cost page states $22,356.36 list price per dose, with maintenance intervals varying by indication: https://www.skyrizi.com/skyrizi-complete/cost-and-savings . DUPIXENT official pricing page states list price near $4,262 monthly, about $51K annually before insurance: https://www.dupixent.com/support-savings/cost-insurance . TREMFYA official cost page provides another IL-23 anchor: https://www.tremfya.com/plaque-psoriasis/cost-support-and-more/cost |
| Cardiometabolic | $4,000-$17,000 | Cardiometabolic analog WAC / direct-price: GLP-1, incretin, and metabolic specialty therapies | NovoCare Wegovy cost page provides public cash/direct-pricing context for semaglutide obesity treatment: https://www.novocare.com/obesity/products/wegovy/savings-offer.html . LillyDirect / Zepbound savings pages provide public direct-price anchors for tirzepatide obesity treatment: https://zepbound.lilly.com/coverage-savings . CMS Part D dashboard can be used as a reasonableness check for broad cardiometabolic drugs such as Ozempic/Jardiance: https://data.cms.gov/tools/medicare-part-d-spending-dashboard |
| Neurology | $25,000-$110,000 | Neurology analog WAC: MS DMTs plus high-cost neurologic biologics | National MS Society has repeatedly documented that many MS disease-modifying therapies have annual list prices above $80K-$100K, making them a strong neurology specialty benchmark: https://www.nationalmssociety.org/advocacy/policy-priorities/affordable-access-to-ms-medications . Eisai/Biogen LEQEMBI public price disclosure states annual drug cost of $26,500 at maintenance dosing: https://www.leqembi.com/en/cost-support . CMS ASP files can triangulate Part B neurologic biologics: https://www.cms.gov/medicare/payment/fee-for-service-providers/part-b-drugs/asp-pricing-files |
| Hematology | $250,000-$850,000 | Hematology analog WAC: hemophilia / sickle-cell / complement high-cost specialty therapy | Hemophilia prophylaxis has long been documented as a high-cost category, often several hundred thousand dollars annually depending on factor use, weight, and bleed profile; Blood Advances cost-effectiveness literature is a defensible public anchor: https://ashpublications.org/bloodadvances/article/5/17/3402/476406/Cost-effectiveness-analysis-of-emicizumab . HEMLIBRA official cost page gives a current public non-factor hemophilia prophylaxis analog: https://www.hemlibra.com/patient/cost.html . CMS Part B ASP files provide public payment-limit support for infused/injected hematology biologics: https://www.cms.gov/medicare/payment/fee-for-service-providers/part-b-drugs/asp-pricing-files |
| Ophthalmology | $12,000-$72,000 | Ophthalmology analog WAC: anti-VEGF retina therapy annualized by injection frequency and laterality | EYLEA HD list price / WAC pages provide a current high-dose aflibercept anchor: https://www.eylea.us/ehr/eylea-hd/financial-assistance . VABYSMO official access and cost resources provide a faricimab anti-VEGF anchor: https://www.vabysmo.com/patient/access-and-support/financial-resources.html . CMS ASP files are especially useful for retina buy-and-bill products and can support per-unit public payment-limit checks: https://www.cms.gov/medicare/payment/fee-for-service-providers/part-b-drugs/asp-pricing-files |

## Implementation recommendation

For current dashboard defaults, keep the six area-level ranges simple and auditable:

- Oncology: $140K-$260K
- Immunology: $45K-$100K
- Cardiometabolic: $4K-$17K
- Neurology: $25K-$110K
- Hematology: $250K-$850K
- Ophthalmology: $12K-$72K

Use the source label in the cost rationale and attach at least two public source URLs per therapeutic area when exporting analyst-facing data. If a specific asset has a clear modality signal, override the area benchmark with a narrower analog:

- Cell/gene therapy: separate one-time or amortized-cost logic; do not force into annual chronic ranges.
- Oral oncology small molecule: use oncology range but cite oral targeted therapy analogs when available.
- Retina anti-VEGF: annualize by injection interval and likely treated eyes; keep $72K as a conservative upper bound for frequent or bilateral therapy.
- Broad cardiometabolic incretin: cap at the public GLP-1/incretin range unless the asset is a rare cardiometabolic biologic.
- Hematology rare disease: use the hematology range only for chronic specialty therapy; create separate logic for curative gene therapy or transplant-like episodes.

## Suggested data fields

```json
{
  "annual_cost_source_label": "Oncology analog WAC: PD-1 / targeted oncology annualized from public list-price anchors",
  "annual_cost_source_urls": [
    "https://www.keytruda.com/financial-support/",
    "https://www.cms.gov/medicare/payment/fee-for-service-providers/part-b-drugs/asp-pricing-files"
  ],
  "annual_cost_source_note": "Planning benchmark only; not a net payer cost estimate."
}
```
