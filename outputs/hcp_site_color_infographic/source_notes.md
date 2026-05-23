# HCP/drug website color infographic source notes

Dataset: `/Users/justinyu/Desktop/linkedin-posts/outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv`

Rows analyzed: 681 unique URL rows

Rows with extractable hex palettes: 650

Dataset timestamp used in CSV: 2026-05-14T21:28:15+00:00

Fields used: `url`, `brand_name`, `company`, `primary_colors_hex`, `secondary_colors_hex`, `status`, `notes`

Color binning: hex values were grouped by hue and lightness into blue, cyan/aqua, dark neutral, gray/neutral, white/off-white, black/near-black, light neutral, red, green/teal, orange/coral, pink/magenta, purple/violet, and yellow/gold. Site-presence percentages count each family at most once per URL row.

Blocked/error handling: all rows remained in the denominator for URL-level prevalence. Rows without captured colors contributed to row count and caveats but not to swatch or first-color calculations.

Output files:

- `hcp_drug_website_color_infographic.html`
- `hcp_drug_website_color_infographic.png`
- `hcp_drug_website_color_infographic.pdf`
