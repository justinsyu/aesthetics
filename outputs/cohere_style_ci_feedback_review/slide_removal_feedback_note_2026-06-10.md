# Cohere-style CI feedback review: whole-slide removal

Reviewed:

- `_skills_to_install/cohere-style-ci/SKILL.md`
- `_skills_to_install/cohere-style-ci/references/style-guide.md`

Finding: no additional skill or style-guide edit was needed.

Rationale: the current `SKILL.md` already covers the reusable feedback pattern. Required Workflow step 12 instructs that when review feedback selects a whole slide/page and asks to delete it, the entire slide element should be removed rather than emptied, visible slide/page numbering should be renumbered, the deck should be re-exported, and the exported PDF page total should be confirmed against the current slide count so no blank page or stale slide number remains. The PDF Export section also instructs cleanup of stale page-render images after deleting slides or changing slide count and confirms that the exported PDF page count must equal the current HTML slide count.

The style guide does not duplicate this operational workflow, but the behavior is already explicitly documented in the primary skill workflow and export QA instructions.
