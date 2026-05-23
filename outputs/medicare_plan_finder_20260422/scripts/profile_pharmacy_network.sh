#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXTRACTED="$ROOT/extracted"
ANALYSIS="$ROOT/analysis"
mkdir -p "$ANALYSIS"

PLAN_OUT="$ANALYSIS/pharmacy_network_plan_summary_raw.csv"
FEE_OUT="$ANALYSIS/pharmacy_selected_fee_summary_raw.csv"

for zip_path in "$EXTRACTED"/pharmacy\ networks\ file\ \ 20260430\ part\ *.zip; do
  unzip -p "$zip_path"
done | awk -F'|' -v plan_out="$PLAN_OUT" -v fee_out="$FEE_OUT" '
  BEGIN {
    OFS = ","
  }
  $1 == "CONTRACT_ID" { next }
  {
    key = $1 "-" $2 "-" $3
    network_rows[key]++
    if ($8 == "Y" && $10 == "1") {
      retail_in_area[key]++
      if ($6 == "Y") preferred_retail_in_area[key]++
    }
    if ($9 == "Y") {
      mail_rows[key]++
      if ($7 == "Y") preferred_mail_rows[key]++
    }

    rows++
    if ($17 != "" && $17 != " ") {
      selected_nonmissing++
      selected = $17 + 0
      brand = $11 + 0
      generic = $14 + 0
      if (selected < brand) selected_lt_brand++
      else if (selected == brand) selected_eq_brand++
      else selected_gt_brand++
      if (selected < generic) selected_lt_generic++
      else if (selected == generic) selected_eq_generic++
      else selected_gt_generic++
    }
  }
  END {
    print "plan_key", "network_rows", "retail_in_area_rows", "preferred_retail_in_area_rows", "mail_rows", "preferred_mail_rows", "preferred_retail_share_in_area" > plan_out
    for (key in network_rows) {
      share = retail_in_area[key] ? preferred_retail_in_area[key] / retail_in_area[key] : ""
      print key, network_rows[key] + 0, retail_in_area[key] + 0, preferred_retail_in_area[key] + 0, mail_rows[key] + 0, preferred_mail_rows[key] + 0, share >> plan_out
    }

    print "metric,value" > fee_out
    print "rows", rows + 0 >> fee_out
    print "selected_fee_nonmissing_30", selected_nonmissing + 0 >> fee_out
    print "selected_fee_lt_brand_30", selected_lt_brand + 0 >> fee_out
    print "selected_fee_eq_brand_30", selected_eq_brand + 0 >> fee_out
    print "selected_fee_gt_brand_30", selected_gt_brand + 0 >> fee_out
    print "selected_fee_lt_generic_30", selected_lt_generic + 0 >> fee_out
    print "selected_fee_eq_generic_30", selected_eq_generic + 0 >> fee_out
    print "selected_fee_gt_generic_30", selected_gt_generic + 0 >> fee_out
  }
'
