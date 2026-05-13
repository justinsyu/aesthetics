# Disease-Specific Agent Instructions

## Feedback Learnings Workflow

For every task performed in this disease-specific folder, the AI agent must always deploy a subagent to review the most recent feedback provided by the user and determine whether any durable lesson should be captured in LEARNINGS.md.

The subagent's scope must be narrow: inspect only the latest relevant user feedback, compare it against the existing LEARNINGS.md, and recommend or make only targeted updates that preserve existing context.

When updating LEARNINGS.md, never rewrite the entire file. Apply a focused append or minimal localized edit only, so accumulated context is not lost and prior learnings are not accidentally altered or made inaccurate.

If the latest user feedback does not contain a durable, reusable learning for this disease-specific folder, leave LEARNINGS.md unchanged and note that no update was needed.
