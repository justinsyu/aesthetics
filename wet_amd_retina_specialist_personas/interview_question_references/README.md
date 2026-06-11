# Interview Question References

## Purpose

This folder collects public interview prompts and questions that the wet AMD persona specialists have been asked. The intended use is persona evaluation: provide an AI model with the cleaned persona plus neutral clinical context, generate a response to the same prompt, and compare that generated response with the doctor's real answer at the linked source.

These files do not attempt to reproduce full interview answers. The linked source remains the reference for the actual answer.

## How to Use

1. Select a specialist profile from `../profiles/`.
2. Select one interview prompt from that specialist's interview-reference file.
3. Provide the model only the persona profile and clean context needed to answer the prompt.
4. Generate the simulated response.
5. Compare the simulated response with the source interview answer.
6. Score fit on:
   - topic coverage;
   - evidence priorities;
   - safety and efficacy emphasis;
   - operational/practice concerns;
   - uncertainty and caveat style;
   - whether the model invented claims not present in the persona or source context.

## Interpretation Rules

- Treat entries labeled "question" as public prompts where the interviewer question is visible or clearly represented.
- Treat entries labeled "interview prompt/topic" as weaker evaluation items when the public page provides a video title, abstract, or interviewer framing but not the exact question text.
- Do not infer private views from interview answers. Use the comparison to calibrate persona behavior, not to claim the physician's current preference.
- Keep exact answer text in the source, not in this repository, unless a short excerpt is explicitly needed and copyright limits are respected.

## Files

The individual doctor files in this folder contain the detailed references. [interview_question_index.csv](interview_question_index.csv) is the consolidated machine-readable index.

For persona evaluation, use the filtered benchmark in [opinion_filtered/](opinion_filtered/). It keeps only prompts that require clinical judgment, opinion, prioritization, evidence interpretation, adoption thinking, or other persona-discriminating perspective. The original full set remains here for traceability.

| Specialist | File | References |
|---|---|---:|
| Jeffrey S. Heier, MD | [jeffrey_heier.md](jeffrey_heier.md) | 8 |
| Carl D. Regillo, MD | [carl_regillo.md](carl_regillo.md) | 12 |
| Charles C. Wykoff, MD, PhD | [charles_wykoff.md](charles_wykoff.md) | 22 |
| David M. Brown, MD | [david_brown.md](david_brown.md) | 8 |
| Arshad M. Khanani, MD, MA | [arshad_khanani.md](arshad_khanani.md) | 14 |
| Peter K. Kaiser, MD | [peter_kaiser.md](peter_kaiser.md) | 24 |
| Philip J. Rosenfeld, MD, PhD | [philip_rosenfeld.md](philip_rosenfeld.md) | 24 |
| Nancy M. Holekamp, MD | [nancy_holekamp.md](nancy_holekamp.md) | 24 |
| Dante J. Pieramici, MD | [dante_pieramici.md](dante_pieramici.md) | 16 |
| Allen C. Ho, MD | [allen_ho.md](allen_ho.md) | 12 |

Total consolidated references: 164.

Opinion-filtered benchmark references: 136.
