# Second-Pass Cohere Style CI Feedback Recommendation

## Scope reviewed

- Research folder: `research/pharma_certification_heor_medaffairs_2026-07-02/`
- Prior feedback report: `subagent_reports/cohere_style_ci_feedback.md`
- Skill: `_skills_to_install/cohere-style-ci/SKILL.md`
- Reference: `_skills_to_install/cohere-style-ci/references/style-guide.md`

I did not modify the skill or reference files.

## Conclusion

One additional narrow reusable lesson is warranted for `_skills_to_install/cohere-style-ci/SKILL.md`.

The prior update already covers the core certification/course-market risk: source-stated competitor claims must be archived separately from analyst-derived curriculum implications. The completed second-pass research adds a distinct recurring issue: public training materials, case studies, syllabi, slide decks, brochures, examples, and toolkits are often useful as evidence or assigned-reading references, but public availability does not establish permission to republish, copy, or package them as course assets.

This is not just a legal footnote. It directly affects competitive-intelligence wording. A CI artifact should not describe public third-party PDFs, syllabi, slides, or case prompts as reusable courseware unless reuse permission is visible and confirmed. It should distinguish "evidence/reference source" from "reusable course asset."

## Proposed edit

Add this bullet near the existing certification/training/course-market CI rule in `_skills_to_install/cohere-style-ci/SKILL.md`:

> For curriculum, certification, training, or case-study CI work that identifies public third-party syllabi, slide decks, PDFs, brochures, case packets, examples, or toolkits, distinguish public accessibility from reuse permission. Treat archived third-party materials as evidence, assigned-reading links, or design references unless visible license or terms explicitly allow reuse. In source logs or methods notes, record any visible copyright, license, permission, gated-access, participant-only, or "not for sale/distribution" restrictions, and do not describe materials as reusable course assets or copy substantial text, slide images, assignments, or case prompts into paid or distributed courseware without confirmed permission.

## Rationale

- `README.md` now states that public availability does not imply permission to republish content inside a paid course, and that archived third-party materials should be treated as reference copies and assigned-reading links unless reuse permissions are confirmed.
- `case_study_sources.md` repeatedly flags reuse and interpretation caveats: MAPS slides should not be repackaged as original material, APGO material carries copyright language, UF syllabi are not open-license assignment banks, the Jones & Bartlett sample is marked "not for sale or distribution," and several public PDFs are brochures, summaries, or competition descriptions rather than reusable case packets.
- This lesson is separate from the already-added source-claim versus synthesis rule. It is about how to characterize public materials as evidence, references, design inputs, or reusable assets.

## Reference-file decision

No edit is recommended for `references/style-guide.md`.

The style guide already covers audience framing, source-observed facts versus analyst implications, and avoiding unsupported source-to-analysis substitutions. The new lesson belongs in the skill's evidence/source-handling rules because it governs source archiving, permissions caveats, and CI claim boundaries rather than visual style or slide grammar.

## Non-recommendations

I do not recommend a new rule for blocked, failed, or URL-only sources. The current skill already covers blocked captures, failed source pages, anti-bot pages, and downstream coverage-count updates. The second-pass inventory had failed or URL-only items, but that does not expose a new skill gap.
