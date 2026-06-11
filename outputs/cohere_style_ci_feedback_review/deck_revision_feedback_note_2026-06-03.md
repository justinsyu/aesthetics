# Cohere-style CI deck revision feedback review

Applicable: no new skill-file change recommended.

This pass reviewed the current deck-revision feedback against the local `cohere-style-ci` skill and style guide without editing either file, because both skill files are already modified in git. The reusable feedback appears already covered by the current local skill/style guidance.

Already covered guidance:

- Keep viewer-facing CI decks neutral, scientific, and reader-facing; avoid local paths, generated artifact names, source-log mechanics, hashes, and analyst-run process language on visible slides.
- Preserve auditability in companion artifacts such as source logs, retained records, manifests, QA notes, screenshots, and exclusion rationales.
- Use direct References slide titling, source-agnostic reference columns, and centered `Ref` / `REF` identifiers.
- Scope typography feedback carefully: main slide titles can stay lighter or medium weight, while card/panel headings, chips, tags, and compact table headers may use heavier weight when needed.
- Treat one-word heading/table-label lines, clipping, overflow, stale render screenshots, excessive blank space, and misaligned fixed-page components as QA defects before handoff.
- For AI-topic conference or local-corpus scans, classify from visible title first, introduction/objective fields second, and full abstract text only as fallback; preserve fallback order and false-positive rationale in non-viewer artifacts.

Reusable guidance for this revision:

- Do not edit the dirty skill files for this pass; keep this note as the local applicability record.
- Future CI deck revisions should apply the covered guidance directly during layout, copy, and PDF QA, then update the skill only in a separate owned skill-maintenance task if the dirty local changes are accepted or reconciled.

Files inspected:

- `AGENTS.md`
- `_skills_to_install/cohere-style-ci/SKILL.md`
- `_skills_to_install/cohere-style-ci/references/style-guide.md`
- `outputs/cohere_style_ci_feedback_review/subagent_cohere_style_ci_feedback.md`
- `outputs/cohere_style_ci_feedback_review/subagent_prior_outputs_inventory.md`
- `ecfs_2026_ai_topics/subagent_cohere_style_ci_feedback.md`

Files changed:

- `outputs/cohere_style_ci_feedback_review/deck_revision_feedback_note_2026-06-03.md`
