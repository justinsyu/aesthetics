# Eliquis 2.5 mg x 60 euro price infographic source note

Input file: `/Users/justinyu/Desktop/linkedin-posts/eu_drug_pricing/analysis/eliquis_2_5mg_60_price_extract.csv`

The infographic uses rows where `included_in_chart == yes` and `currency == EUR`.

Included countries and listed source prices:

| Country | Source-listed pack price | Price basis in CSV |
| --- | ---: | --- |
| Latvia | €115.92 | pharmacy price incl. 12% VAT |
| Cyprus | €82.87 | maximum retail price incl. VAT |
| Luxembourg | €82.59 | CNS positive-list public price field |
| Austria | €77.55 | eEKO listed pack price, interpreted from cents field |
| Finland | €69.71 | tax-included retail sale price, cents field |
| Greece | €64.16 | retail price incl. VAT column |
| France | €59.97 | public price incl. dispensing fee field in BDPM presentation file |
| Slovakia | €55.56 | final price column |
| Slovenia | €52.06 | wholesale price column |

Metrics shown on the infographic:

| Metric | Value |
| --- | ---: |
| Euro source rows in chart | 9 |
| Median listed pack price | €69.71 |
| Highest to lowest listed price | 2.23x |
| Absolute high-low spread | €63.86 |

Limitation: these rows compare the source-listed pack price field available in each country. The price bases differ by source and country, including retail/pharmacy prices with VAT or tax, tax-included retail sale price, public price including a dispensing-fee field, wholesale price, and national list or reimbursement-system price fields. They should not be interpreted as an apples-to-apples ex-factory, net, reimbursed-price, reimbursement-adjusted, or like-for-like cross-country price comparison. Romania and Sweden were excluded from the chart because the relevant CSV rows were not euro denominated and no currency conversion was applied.
