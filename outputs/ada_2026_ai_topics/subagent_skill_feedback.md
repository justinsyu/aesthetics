Suggested small wording change recommended.

Location: after the existing conference abstract guidance around `_skills_to_install\cohere-style-ci\SKILL.md:190-192`.

Add:

> For local conference abstract or poster corpus summaries, treat the local dataset as the source of truth when requested. Do not require web screenshots or last-7-days freshness checks unless the user asks for source revalidation; instead provide source notes or methodology plus a machine-readable retained-record CSV with source IDs, local locators, included/excluded status, topic labels, and evidence text or fields used for each summarized finding.

Rationale: the skill already has local-archive exceptions in Final QA, but the core workflow still heavily implies web screenshots and freshness validation. This small addition makes the local conference corpus case explicit and preserves record-level traceability.