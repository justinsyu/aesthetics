# Opinion Benchmark Answer Key

## Purpose

This folder adds answer-status and answer-summary fields to the opinion-filtered interview benchmark. The goal is to support comparison between an AI-generated persona response and the doctor's actual public response when that response is available.

## Answer Rules

- Do not fabricate missing answers.
- Use concise paraphrased summaries rather than long transcript excerpts.
- Preserve the URL and answer basis so reviewers can inspect the original source.
- Mark video-only, audio-only, inaccessible, or moderator-prompt cases honestly.
- Treat page summaries as lower-confidence than transcripts or article quotes.

## Answer Status Values

| Status | Meaning |
|---|---|
| `summarized_from_transcript` | The source exposed transcript text that supported a concise paraphrased answer summary. |
| `summarized_from_article_quotes` | The source provided article text or quotes sufficient to summarize the doctor's answer. |
| `summarized_from_page_summary` | The page summary described the answer/content enough for a limited summary, but not a full transcript. |
| `answer_available_video_audio_not_summarized` | The answer appears to be in video/audio, but no accessible text answer was summarized. |
| `answer_not_available` | No answer was available from the source checked. |
| `not_doctor_answer_or_moderator_prompt` | The row is useful as a prompt/framing reference, but the answer is from someone else or the doctor is moderating. |
| `source_inaccessible` | The source could not be accessed sufficiently to summarize the answer. |

## Files

- `opinion_interview_question_answer_key.csv` - consolidated answer-augmented benchmark.
- `*_answers.csv` - per-doctor answer summaries and status fields.

## Current Coverage

| Answer status | Rows |
|---|---:|
| `summarized_from_article_quotes` | 50 |
| `summarized_from_transcript` | 28 |
| `summarized_from_page_summary` | 17 |
| `answer_available_video_audio_not_summarized` | 37 |
| `not_doctor_answer_or_moderator_prompt` | 3 |
| `source_inaccessible` | 1 |

Total opinion-filtered benchmark rows: 136.

