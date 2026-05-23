# NHANES Ophthalmology Descriptive Analysis

This folder contains a bounded, reproducible analysis of public CDC NHANES ophthalmology-relevant files.

## Inputs

Raw XPT files are stored in `data/raw` and are downloaded from CDC if missing:

- `DEMO_L`, `FNQ_L`, `BAQ_L`, `DIQ_L`, and `DPQ_L` for August 2021-August 2023 current eye-related measures
- `DEMO_D`, `VIQ_D`, `VIX_D`, `OPXFDT_D`, `OPXRET_D` for 2005-2006
- `DEMO_E`, `VIQ_E`, `VIX_E`, `OPXFDT_E`, `OPXRET_E` for 2007-2008

## Run

```bash
python3 scripts/analyze_nhanes_ophthalmology.py
python3 scripts/analyze_nhanes_current_eye_related.py
```

The script uses `pandas`, `numpy`, and `requests`. It writes:

- `output/weighted_ophthalmology_estimates.csv`
- `output/current_eye_related_estimates.csv`
- `output/summary.md`

## Analysis Notes

The ophthalmology-module analysis combines NHANES 2005-2006 and 2007-2008 with four-year MEC weights (`WTMEC2YR / 2`). The current-cycle analysis uses August 2021-August 2023 interview or MEC weights according to component source. Standard errors are Taylor-linearized using `SDMVSTRA` and `SDMVPSU`. The latest public cycle contains vision-function and blurred-vision symptom measures, but it does not contain public ophthalmology examination modules, visual acuity, retinal imaging, FDT visual fields, cataract, glaucoma, AMD, or diabetic-retinopathy variables.
