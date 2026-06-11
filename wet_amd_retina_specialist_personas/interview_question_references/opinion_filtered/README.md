# Opinion-Filtered Interview Benchmark

## Purpose

This folder filters the full interview-question reference set to prompts that are most useful for persona evaluation. Included prompts require a doctor's judgment, opinion, clinical perspective, prioritization, risk/benefit tradeoff, evidence interpretation, patient-selection reasoning, practice-style judgment, future outlook, or adoption threshold.

The full, unfiltered source set remains in `../`.

## Inclusion Rule

Include a prompt when there is no single right answer and the response would reveal how the doctor thinks. Examples:

- How should this therapy fit into practice?
- Which patients are good candidates?
- What evidence would change adoption?
- How should risks be weighed against durability?
- What is the biggest unmet need?
- What is your interpretation of these results?
- What future developments matter most?

## Exclusion Rule

Exclude or separately label prompts that mainly ask for factual recall or generic explanation. Examples:

- Define wet AMD.
- Explain what PDS is.
- Summarize a trial result without asking for interpretation.
- Describe meeting logistics.
- Provide disease prevalence or pathophysiology.

## Files

- `opinion_interview_question_index.csv` - consolidated opinion-filtered benchmark set.
- One Markdown file per specialist - human-readable filtered references.
- `classification_audit.csv` - all 164 original rows with include/exclude decisions and reasons.
- `answers/` - answer-status fields and paraphrased answer summaries where public answers are available.
- `persona_testing_qa_examples_5page.pdf` - five-page presentation PDF with prominent Q&A pairs for persona testing.
- `persona_testing_qa_examples_5page.html` - HTML source used to create the five-page PDF.
- `persona_testing_qa_examples_6page_anonymized_cohere.pdf` - cover plus five content pages, anonymized/no-source, cohere-style-ci styled, with the same 11in x 8.5in landscape page dimensions.
- `persona_testing_qa_examples_6page_anonymized_cohere.html` - HTML source for the anonymized/no-source cohere-style-ci version, cover plus five content pages, with the same 11in x 8.5in landscape page dimensions.

## Answer Key

Use [answers/opinion_interview_question_answer_key.csv](answers/opinion_interview_question_answer_key.csv) when comparing AI-generated persona answers with the doctors' public interview answers. The answer key does not fabricate missing answers: video/audio-only, inaccessible, and moderator-prompt rows are labeled separately.
