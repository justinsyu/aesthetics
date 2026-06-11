# Cohere-style CI prior outputs inventory

Scope: local prior Cohere CI deck outputs and feedback-note patterns only. No existing files were modified.

## Exact files inspected

- `AGENTS.md`
- `_skills_to_install/cohere-style-ci/SKILL.md`
- `_skills_to_install/cohere-style-ci/references/style-guide.md`
- `outputs/ada_2026_ai_topics_ci/subagent_cohere_style_ci_feedback.md`
- `outputs/ada_2026_ai_topics_ci/subagent_strict_qa_notes.md`
- `outputs/ada_2026_ai_topics_ci/subagent_audit_notes.md`
- `outputs/ada_2026_ai_topics_ci/ada_2026_ai_topics_ci_report.html`
- `outputs/endo_2026_ai_topics_ci/subagent_cohere_style_ci_feedback.md`
- `outputs/endo_2026_ai_topics_ci/subagent_strict_qa_notes.md`
- `outputs/endo_2026_ai_topics_ci/subagent_audit_notes.md`
- `outputs/endo_2026_ai_topics_ci/endo_2026_ai_topics_ci_report.html`
- `eha_2026_ai_topics/subagent_cohere_style_ci_feedback.md`
- `eha_2026_ai_topics/subagent_ai_record_audit.md`
- `eha_2026_ai_topics/subagent_weak_term_audit.md`
- `eha_2026_ai_topics/report.html`
- `ecfs_2026_ai_topics/subagent_cohere_style_ci_feedback.md`
- `ecfs_2026_ai_topics/subagent_ai_record_audit.md`
- `ecfs_2026_ai_topics/report.html`
- `outputs/medical_affairs_ai_startups/medical_affairs_ai_startups_inventory.md`
- `outputs/medical_affairs_ai_startups/sources/source-log.md`
- `outputs/medical_affairs_ai_startups/medical_affairs_ai_startups_cohere_ci.html`

Folder inventories were enumerated for:

- `outputs/ada_2026_ai_topics_ci`
- `outputs/endo_2026_ai_topics_ci`
- `eha_2026_ai_topics`
- `ecfs_2026_ai_topics`
- `outputs/medical_affairs_ai_startups`

## Prior local feedback pattern

- Local conference-corpus AI-topic scans should classify topic from visible presentation title first, introduction/objective fields second, and full abstract text only as fallback.
- Weak or ambiguous AI matches need strict false-positive controls. Prior notes call out non-AI acronym matches, generic prediction/modeling, ordinary automated workflows, coding-only AI use, language-editing-only disclosures, and disease/subtype abbreviations.
- Viewer-facing CI reports should use neutral scientific terms such as records, presentations, abstracts, reported, described, included, retained, classified, and excluded.
- Viewer-facing slides should not expose local file paths, local archive mechanics, generated inventory filenames, JSON/MD archive material, hashes, run manifests, source-log wording, or analyst-run process language. Provenance belongs in source logs, retained-record exports, QA notes, manifests, and exclusion files.
- Typography feedback repeats a scoped hierarchy rule: main slide `h1`/`h2` titles should stay regular or medium weight; bold/heavier emphasis is acceptable for section, card, and panel headings, chips, tags, and compact table headers when needed.
- Body paragraphs, bullets, table body cells, citations, source notes, and other reading text should remain regular or medium weight.
- References tables should use direct titles such as `References`, source-agnostic columns, and centered reference identifiers.
- Fixed-page QA should treat one-word heading/card/table-label lines, compressed table headers, clipping, overflow, stale screenshots, and excessive blank space as defects to fix before handoff.
- Local run folders commonly keep report HTML/PDF, retained inventory exports, source logs, run manifests, exclusion files, QA notes, and screenshots together.
- Broad vendor scans should separate AI-native startups from AI-enabled incumbents, scaleups, acquired benchmarks, adjacent vendors, and evidence-thin early vendors, while preserving public-source support for products, workflows, customers/partners, stage, and confidence labels.

## Candidate reusable CI deck style guidance

- For local conference-archive AI decks, make the visible report about source records and evidence classifications, not the mechanics of local collection or generated files.
- Use title-first classification for therapeutic/scientific topic assignment, and document fallback order in non-viewer artifacts.
- Keep inclusion tiers explicit: direct AI/ML, AI-adjacent predictive/modeling, and excluded false positives should be visibly distinct when they affect counts.
- Keep report language objective and biomedical: prefer source-attribution verbs such as reported, described, documented, listed, and included.
- Preserve auditability in companion artifacts: retained-record tables, source logs, run manifests, exclusion rationales, QA notes, and screenshot/export status.
- Apply typography hierarchy narrowly: lighter main slide titles, bold only for local labels/headings/chips where it improves scanability.
- Check rendered browser/PDF pages for fit, heading widows, readable table labels, centered reference IDs, current screenshot sets, and one page per slide.
