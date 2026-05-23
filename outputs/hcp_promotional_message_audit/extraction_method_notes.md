# Promotional Message Extraction Method Notes

Scope: derive one short verbatim promotional product pitch per URL in `outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv`, preserving the existing 681-row manifest order and product metadata. This note is method guidance only; it does not edit the final promotional-message CSV.

## Existing Inputs Reviewed

- Source manifest: `outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv`
- Manifest row count: 681
- Manifest fields: `source_index`, `url`, `final_url`, `brand_name`, `generic_name`, `company`, palette fields, RWE fields, `status`, `notes`, `retrieved_at`
- Status distribution in the compiled audit: 312 `200`, 220 `rendered`, 100 `ok`, 22 `error`, 20 `403`, 3 `blocked`, 2 `http_200`, 1 `partial`, 1 `404`
- Product metadata gaps in the compiled audit: 51 missing brand values, 129 missing generic values, 123 missing company values
- Saved rendered text coverage: `outputs/hcp_site_audit/browser_extract.jsonl` contains 25 URL records, 22 with substantive body text and screenshots
- Prior scripts: `outputs/hcp_site_audit/build_csv_from_browser_jsonl.py`, `merge_chunks.py`, `tmp_worker_0/fallback_extract.py`, and `tmp_worker_3/extract_worker_3.py`

Implication: use the compiled CSV as the URL/product manifest, but do not rely on it as the promotional-copy source. The message extraction pass should reopen or refetch each site because most rows do not have stored rendered page text.

## Recommended Output CSV Schema

Use one row per manifest row, preserving `source_index` and source order.

- `source_index`
- `url`
- `final_url`
- `brand_name`
- `generic_name`
- `company`
- `message_quote`
- `message_word_count`
- `message_theme`
- `claim_type`
- `rhetorical_frame`
- `cta_text`
- `cta_type`
- `quote_placement`
- `page_section`
- `page_title`
- `source_text_window`
- `extraction_method`
- `status`
- `confidence`
- `caveats`
- `retrieved_at`

Optional but useful if screenshots are captured:

- `screenshot_path`
- `evidence_selector_or_locator`
- `evidence_url_fragment`

## Quote Rules

- Store one verbatim promotional product message per URL.
- Keep `message_quote` at or below 25 words from that source.
- Prefer one contiguous phrase, headline, subhead, card headline, or CTA-adjacent claim; do not assemble a quote from separate page regions.
- Preserve original wording, capitalization, numerals, and clinically meaningful symbols where practical.
- Normalize only whitespace and line breaks.
- Do not quote boxed warnings, Important Safety Information, adverse-event statements, prescribing-information disclaimers, cookie banners, legal footers, or navigation-only text.
- If the strongest visible pitch is longer than 25 words, select the strongest self-contained contiguous clause or sentence fragment under 25 words and record `caveats=excerpted_from_longer_message`.
- Avoid adding ellipses inside `message_quote`; if a quote is an excerpt, explain that in `caveats`.
- If no promotional pitch is visible, leave `message_quote` blank and use an explicit non-success `status`.

## Candidate Priority

Score candidate copy in this order:

1. Above-the-fold hero headline or subhead that directly positions the product
2. Efficacy or clinical-data headline with product benefit or outcome
3. Differentiation claim such as first/only, established, proven, biosimilar, rapid, durable, convenient, targeted, or broad indication
4. Dosing, administration, device, adherence, or patient-fit claim
5. Access, coverage, savings, support, or patient-services pitch
6. CTA text only when it contains meaningful product positioning, not generic text such as "Learn more"

Tie-breakers:

- Prefer copy naming or clearly referring to the product over generic disease education.
- Prefer messages close to the homepage or landing page top over deep secondary content.
- Prefer quantified or differentiating statements over generic "support" language.
- Prefer HCP-facing product pitches over patient-facing content reached by redirect.
- For blocked/error rows, retain row with `status=blocked` or `status=error` rather than inferring from outside knowledge.

## Candidate Filters

Discard candidates dominated by:

- Safety, risk, contraindication, adverse reactions, warnings, and medication-guide copy
- Prescribing information labels, legal disclaimers, copyright, privacy, terms, and cookie language
- Navigation labels, menu items, footer links, breadcrumb text, and form labels
- Generic disease burden text that does not pitch the product
- Repeated site furniture such as "For Healthcare Professionals" unless it is part of a stronger product line
- Unverifiable PDF or external source text unless the site visibly promotes that PDF as product content and the extraction method captures it explicitly

## Theme Taxonomy

Use one primary `message_theme` per URL:

- `efficacy`
- `safety_tolerability`
- `dosing_administration`
- `convenience_adherence`
- `mechanism_targeting`
- `differentiation_first_only`
- `durability_long_term`
- `speed_onset`
- `patient_fit_population`
- `access_coverage`
- `support_services`
- `real_world_evidence`
- `biosimilar_value`
- `brand_identity`
- `disease_education`
- `unclear`

## Claim Type Taxonomy

Use one primary `claim_type` per URL:

- `clinical_outcome`
- `comparative_or_differentiating`
- `administration_or_dosing`
- `safety_or_tolerability`
- `mechanism_or_science`
- `indication_or_population`
- `access_or_affordability`
- `support_or_resources`
- `evidence_or_study`
- `emotional_or_empowerment`
- `availability_or_approval`
- `cta_only`
- `none_found`

## Rhetorical Frame

Use a concise label that can support infographic synthesis:

- `clinical_confidence`
- `practical_workflow`
- `patient_control`
- `unmet_need`
- `proof_point`
- `simplification`
- `speed`
- `precision`
- `legacy_trust`
- `access_enablement`
- `cost_value`
- `innovation`
- `category_leadership`
- `unclear`

## CTA Fields

Capture the strongest nearby call to action if visible.

- `cta_text`: verbatim CTA text, normalized whitespace
- `cta_type`: `learn_more`, `request_sample`, `sign_up`, `download_pi`, `view_data`, `start_form`, `patient_support`, `coverage`, `savings`, `contact_rep`, `none`

Do not let a CTA replace the promotional quote unless the CTA itself is the strongest pitch.

## Quote Placement

Use one of:

- `hero`
- `above_fold_card`
- `homepage_body`
- `efficacy_section`
- `clinical_data_section`
- `dosing_section`
- `safety_section`
- `access_coverage_section`
- `support_resources_section`
- `rwe_section`
- `modal_interstitial`
- `pdf_or_pi`
- `metadata_only`
- `not_visible`
- `blocked`

`page_section` can hold a more specific visible heading when available.

## Status Values

- `extracted_verified`: quote was visible in rendered or fetched page text and passed filters
- `extracted_needs_review`: plausible quote found, but page was partially rendered, metadata-only, or context was limited
- `no_promotional_copy_found`: page accessible but no suitable product pitch after filters
- `blocked`: blocked, gated, or bot-protected
- `error`: navigation, HTTP, SSL, timeout, or script failure
- `non_product_redirect`: redirected to corporate, patient, non-US, or unrelated page
- `metadata_only`: only title/meta description available

Confidence values: `high`, `medium`, `low`.

## Extraction Procedure

1. Load `hcp_site_color_scheme_drug_info.csv` and preserve row order.
2. For each URL, open the rendered page when possible with Chrome/Playwright using the same desktop-class user agent used in the prior audit.
3. Close or accept cookie banners, HCP interstitials, and popups where feasible.
4. Capture visible text with DOM structure. Include title, meta description, headings, buttons/links, and text blocks with approximate placement.
5. Split text into candidates by visible element and nearby context rather than by raw page-wide lines only.
6. Remove boilerplate and safety/legal/navigation candidates using the filters above.
7. Score candidates using placement, product specificity, claim strength, and verbatim quote length.
8. Select one candidate under 25 words; if no high-quality candidate exists, use explicit status/caveat.
9. Classify theme, claim type, rhetorical frame, CTA, and placement.
10. Write a complete CSV row even for blocked/error/no-copy cases.
11. Validate row count, uniqueness, quote word counts, and non-empty statuses.

## Suggested Candidate Scoring

Recommended additive scoring:

- `+40` hero or above-fold placement
- `+30` direct product brand mention or clear product-specific headline
- `+25` quantified clinical outcome, efficacy, duration, dosing, or access proof point
- `+20` differentiating phrase such as first, only, proven, established, rapid, durable, convenient, targeted, once-daily, no titration, or biosimilar
- `+15` near a visible CTA
- `+10` shorter than 16 words and self-contained
- `-35` safety/legal/ISI language
- `-25` generic disease education without product reference
- `-20` navigation/footer/form-only text
- `-15` longer than 25 words before excerpting

## Validation Checks

- Final row count equals 681.
- `source_index` values match the source manifest.
- No quote exceeds 25 words.
- Every row has one of the approved `status` values.
- Every extracted row has non-empty `message_theme`, `claim_type`, `quote_placement`, and `confidence`.
- Blocked/error rows retain the original URL and product metadata from the manifest.
- Randomly review at least 5% of `extracted_verified` rows against rendered screenshots or saved text windows.

## Caveats to Preserve

- Some sites block automated access or require HCP/cookie interstitial handling; do not infer copy from brand knowledge.
- Product metadata from the color/RWE audit has known gaps; do not silently "fix" brand/generic/company unless the extraction page visibly supports the correction.
- Some HCP pages promote multiple indications or combination regimens. Quote the pitch tied most directly to the landing URL and record `caveats=multi_indication_site` or `caveats=combination_context` where needed.
- Some sites redirect between HCP, patient, corporate, payer, or medical-information pages. Record redirects and use `non_product_redirect` if the reached page is not a promotional product page.
- Promotional text is dynamic and may change by visit, geography, cookie state, or viewport. Record `retrieved_at` and `extraction_method`.

## Draft Implementation Improvements

The existing color/RWE scripts can be extended, but the promotional extractor should be a separate script so the final audit CSV remains stable.

Recommended script path:

`outputs/hcp_promotional_message_audit/extract_promotional_messages.py`

Recommended data flow:

- Input: `outputs/hcp_site_audit/hcp_site_color_scheme_drug_info.csv`
- Optional cache: `outputs/hcp_promotional_message_audit/rendered_text_cache.jsonl`
- Output: `outputs/hcp_promotional_message_audit/hcp_site_promotional_messages.csv`
- QA report: `outputs/hcp_promotional_message_audit/promotional_message_qa.md`

Implementation notes:

- Reuse company/brand/generic values from the manifest as seed metadata.
- Prefer rendered Playwright text extraction over raw HTTP because many pages are script-rendered.
- Cache per-URL extracted DOM text and status so interrupted runs can resume without re-hitting all 681 sites.
- Keep extraction deterministic: candidate generation, scoring, and taxonomy rules should be code-defined before any manual review.
- Use concurrency cautiously, with retries and per-domain throttling, because many HCP sites use bot defenses.
- Include `source_text_window` as a short surrounding context field for auditability, but do not use long source excerpts in infographic-visible outputs.

## Pilot Examples From Saved Browser Text

These examples demonstrate the intended quote style and stay under 25 words per source:

- QVAR RediHaler: `QVAR REDIHALER FOR THE MAINTENANCE TREATMENT OF ASTHMA`
- FIRAZYR: `can be a key part of a treatment plan`
- BENDEKA: `Offer your patients a short, fixed course of therapy`

These should be revalidated during the full extraction pass rather than copied blindly into the final CSV.
