# Group D P&T/DUR Decision-Rationale Summary

This summary uses only documents already collected under `decision-rationale/group-d/`. Broad crawling was stopped before any further discovery. Do not treat product/class mentions below as final coverage decisions unless explicitly stated in the source text; many are agenda, PDL, packet, or minutes mentions.

## Corpus

- States covered: New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Rhode Island, South Carolina.
- Saved records: 690 collected/attempted rows in `manifest.csv` / `manifest.json`.
- Successful downloads: 664.
- Blocked/error records: 26.
- Seed coverage: all matrix and meeting-date seed URLs for this 10-state group are represented; no seed URL remains unattempted.
- Extraction limit: text extraction used saved HTML/PDF content. No OCR was run, so scanned tables, image-only PDFs, and embedded attachments may be incomplete.

## Documents Collected By State

- New Mexico: HCA PDL page and public notice for the combined P&T/DUR committee. Relevant value is process/timing; product-level decision rationale is largely unavailable because the statewide PDL appears to be in development.
- New York: NYRx preferred drug program and class coverage pages were collected. NYSDOH DUR pages, membership, bylaws, and meeting pages were attempted but blocked by 403, limiting direct rationale visibility.
- North Carolina: PDL archive, PDL guidelines, DUR agenda, current PDL and many linked provider/coverage documents. This is a strong corpus for PDL/PA implementation monitoring.
- North Dakota: DUR board, PDL versions, agendas, handouts, minutes, and schedule pages. This is a strong corpus for tracing class review cycles and draft/final PA criteria.
- Ohio: statute, P&T bylaws, agendas/minutes, UPDL page, and some drug coverage/PA material. Several legacy pharmacy URLs failed, but core P&T governance and meeting materials were captured.
- Oklahoma: DUR board pages, agenda/packet archive, policies/procedures, board membership, public-comment information, and detailed packets. This is one of the richest corpora for rationale, net-cost, rebate, and criteria detail.
- Oregon: OHA P&T, OHP PDL, DURM meeting/recommendation/newsletter pages and related materials. Good for evidence-review process and recommendation tracking; less direct for rebate rationale.
- Pennsylvania: statewide PDL, P&T bylaws, meeting information, September 2025 P&T agenda, and clinical guideline PDFs. Useful for class-level review and secretary/final-approval separation.
- Rhode Island: EOHHS P&T page, open-meeting entry, provider updates, current and historical minutes. Strong for committee recommendation language and public meeting records.
- South Carolina: SCDHHS/contractor P&T pages, single PDL implementation notice, pharmacy materials, and historical/current minutes. Strong for minutes, manufacturer submission policy, and PDL status tracking.

## General Decision-Rationale Patterns

- Clinical rationale is usually the public-facing layer. Across the group, sources repeatedly expose safety, efficacy, effectiveness, diagnosis, age, lab, contraindication, prior therapy, and medical-necessity criteria. This is the layer pharma can most reliably address with dossiers, real-world evidence, guideline updates, and burden-of-disease framing.
- PDL/PA implementation is the actionable output. Public materials often translate committee work into preferred/non-preferred status, prior authorization criteria, step therapy, quantity limits, continuation criteria, grandfathering, or effective-date updates.
- Cost and rebate logic is unevenly visible. Oklahoma packets contain explicit cost, net-cost, and supplemental rebate language; North Dakota and New Mexico reference cost-effectiveness; New York references cost and supplemental rebates through NYRx material; South Carolina minutes include rebate-oriented language in some historical discussions. Most states do not disclose enough rebate detail to reconstruct economic rationale.
- Advisory recommendation and final action are often separate. New York routes recommendations to the Commissioner; Ohio advises the Medicaid Director; Pennsylvania requires DHS Secretary approval; New Mexico describes recommendations to the Medicaid CMO; North Dakota uses DUR Board review with department adoption; Oregon advises OHA; North Carolina posts approved recommendations and PDL changes. Pharma should not stop monitoring at the meeting vote.
- Manufacturer/public-comment windows matter. Oklahoma has speaker/public-comment processes; North Carolina has speaker and meeting links; Rhode Island accepts clinical submissions before meetings; South Carolina routes industry submissions to a designated PDL process and discourages direct member contact; Ohio agendas include manufacturer/interested-party presentations; Oregon and Pennsylvania include public testimony/comment structures.
- The highest-value monitoring sequence is: agenda posted, packet/materials posted, public comment or manufacturer submission deadline, committee recommendation/minutes, final PDL/PA/criteria publication, and effective-date implementation.

## Therapy, Class, And Product Mentions Found

- Diabetes and metabolic disease: insulin and GLP-1 classes recur in North Carolina, North Dakota, Ohio, Oklahoma, Rhode Island, and New York materials. Examples include insulin products in PDLs and Ohio agenda references to GLP-1 receptor agonists for non-obesity indications.
- Pain, opioid use disorder, and overdose: opioid analgesics, medication-assisted treatment, naloxone/opioid-overdose agents, and OUD-related materials appear in Oklahoma, Pennsylvania, Rhode Island, North Dakota, Oregon, Ohio, and New York sources.
- Behavioral health / CNS: antipsychotics, antidepressants, stimulants/ADHD therapies, Alzheimer’s agents, migraine therapies, sedative/hypnotics, and related CNS classes appear across New York, North Carolina, North Dakota, Ohio, Oklahoma, Pennsylvania, Rhode Island, and South Carolina.
- Oncology and high-cost specialty: Oklahoma packet/agenda text includes GI cancer drug review mentions such as Tevimbra, Vyloy, and Ziihera; Pennsylvania agenda text includes oncology/breast cancer classes; North Dakota handouts mention oncology products/classes in utilization and review contexts.
- Immunology/dermatology: topical/systemic immunomodulators, psoriasis, atopic dermatitis, biologics/biosimilars, and products such as Humira, Cosentyx, Dupixent, Rinvoq, Skyrizi, and Stelara appear in PDL or minutes contexts, especially North Carolina, North Dakota, Rhode Island, and South Carolina.
- Infectious disease: antibiotics/anti-infectives, hepatitis C, HIV/prep/antiretroviral, and antifungal categories appear in New York, North Carolina, North Dakota, Pennsylvania, Rhode Island, and South Carolina materials.
- Respiratory: asthma/COPD, cystic fibrosis, inhaled antibiotics, and products such as Alyftrek or Xolair appear in Ohio, North Dakota, Oklahoma, Rhode Island, and South Carolina materials.
- Cardiovascular/hematology: anticoagulants, angiotensin modulators, pulmonary arterial hypertension, hemophilia, thrombocytopenia, lipid/cholesterol, and heart failure classes appear in Ohio, Oklahoma, Pennsylvania, North Dakota, Rhode Island, and North Carolina materials.

## State-Specific Pharma Implications

- New Mexico: Monitor PDL vendor implementation and committee build-out. Current public materials are more useful for process entry points than for drug-specific rationale.
- New York: NYRx class coverage is usable, but direct DUR meeting materials were blocked in this collection. Pharma should separately monitor NYSDOH access and NYRx updates before meetings.
- North Carolina: Track PDL archive, approved recommendations, speaker windows, and final PDL versions. The corpus supports class-level PDL/PA surveillance better than final rationale reconstruction.
- North Dakota: Strong opportunity to monitor first-review/second-review cycles, draft PA criteria, handouts, and final adoption. This state is useful for anticipating criteria evolution before final implementation.
- Ohio: Statute/bylaws clarify safety, efficacy, and effectiveness framing; agendas expose upcoming PDL proposal classes and manufacturer presentation windows. Final UPDL/criteria tracking remains necessary.
- Oklahoma: Highest-value state in this group for rationale extraction. Packets often connect utilization, clinical criteria, cost/net-cost, rebate, recommendations, and public comment.
- Oregon: Monitor DURM recommendations, OHA P&T pages, newsletters, and meeting materials for evidence-review framing. Economic rationale remains less transparent.
- Pennsylvania: September agenda and clinical guideline PDFs connect committee recommendations to later PA guideline changes. Watch for secretary approval and effective-date translation.
- Rhode Island: Historical and current minutes provide concise recommendation/action language. Clinical submission deadlines are actionable for manufacturer evidence planning.
- South Carolina: Minutes and submission policy are useful. Industry should use the designated submission channel and avoid direct committee-member lobbying on PDL status.

## Explicit Limitations

- The crawl was stopped, so this is not an exhaustive state archive.
- The corpus includes some broad linked pages that are not decision-rationale relevant; row-level inclusion in the manifest does not imply analytical relevance.
- Product names/classes found in PDLs, agendas, minutes, or packets are mentions, not necessarily final coverage decisions.
- FDA-approval-to-review timing was not calculated because the collected normalized files do not contain approval dates or a complete extracted decision timeline.
- Rebate and net-cost logic is generally not reconstructable except where packets or minutes explicitly discuss it.
- Source blocks remain material for New York direct DUR documents and several stale Ohio URLs.

