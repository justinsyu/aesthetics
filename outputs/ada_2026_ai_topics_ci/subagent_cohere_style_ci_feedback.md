# Cohere-Style CI Skill Feedback

Applicable: yes.

Reviewed the rebuilt ADA 2026 AI topics CI output against the ENDO 2026 reference. The generalizable correction is that local conference-corpus AI topic scans should classify the scientific or therapeutic topic from the visible presentation title first, then introduction/objective fields, then full abstract text only as fallback. This prevents incidental secondary disease, endpoint, or population terms from overriding the record's visible topic.

The current skill already covered predictive-only records as a separate AI-adjacent tier and acronym false-positive handling. I made a narrow edit to `_skills_to_install/cohere-style-ci/SKILL.md` to add only the missing title-first topic-classification hierarchy to the existing AI-focused local conference-corpus guidance.
