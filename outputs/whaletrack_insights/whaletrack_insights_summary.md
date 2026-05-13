# Whale Track Data Insights

Input CSV: `/Users/justinyu/Desktop/linkedin-posts/whaletrack_all_records.csv`

## Headline Findings

- The export contains **65,751 public All records sightings**.
- **65,674 records (99.9%) include GPS coordinates**. The rendered detail pages confirm that missing coordinates are real `N/A` values for sampled records.
- The core map view contains **65,284 coordinate records** around Scotland and nearby waters. There are **322 valid coordinate records outside that core geography** plus **68 records at 0,0**, which should be treated as data-quality exceptions or non-local reports.
- Reporting volume peaks in **2025 with 14,497 sightings**. The 2026 data is partial through May 9, 2026.
- From 2018-2025, **76% of records fall in June-September**, confirming a strong seasonal fieldwork/reporting pattern.
- The top 12 observers contribute **39% of all records**, so observer/program workflow effects matter when comparing trends.
- Survey mix: Casual Sighting 59%, Excursion Sighting 39%, Land Based Survey Sighting 2%.
- Data source mix: app 51%, not recorded 41%, website 8%.

## Leading Species by Sightings

- Harbour porpoise: 22,345 sightings (34.0%)
- Short-beaked common dolphin: 18,138 sightings (27.6%)
- Minke whale: 12,656 sightings (19.2%)
- Bottlenose dolphin: 5,637 sightings (8.6%)
- Basking shark: 1,401 sightings (2.1%)

## Leading Species by Reported Individuals

- Short-beaked common dolphin: 306,368 reported individuals
- Harbour porpoise: 60,747 reported individuals
- Bottlenose dolphin: 41,142 reported individuals
- Minke whale: 17,430 reported individuals
- Unidentified dolphin: 6,746 reported individuals

## Generated Infographics

- Overview and species mix: `/Users/justinyu/Desktop/linkedin-posts/outputs/whaletrack_insights/01_overview_species.png`
- Species records vs individuals: `/Users/justinyu/Desktop/linkedin-posts/outputs/whaletrack_insights/02_species_abundance.png`
- Annual and seasonal patterns: `/Users/justinyu/Desktop/linkedin-posts/outputs/whaletrack_insights/03_temporal_patterns.png`
- Sources and observers: `/Users/justinyu/Desktop/linkedin-posts/outputs/whaletrack_insights/04_sources_observers.png`
- GPS density map: `/Users/justinyu/Desktop/linkedin-posts/outputs/whaletrack_insights/05_gps_density_map.html`
- Interactive GPS map: `/Users/justinyu/Desktop/linkedin-posts/outputs/whaletrack_insights/whaletrack_gps_interactive_map.html`
