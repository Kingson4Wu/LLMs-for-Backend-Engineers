# Offline tutoring-contract evaluation

This directory checks whether a tutoring prompt can be reviewed against a
specific, complete book artifact. It does not call Codex, Claude Code, ChatGPT,
DeepSeek, or any other model; it does not judge a model; and it does not produce
a model-quality score.

Public development cases in `development/` are structural regression fixtures.
They require a learner task, Chinese source locations (`chapter_id`, title,
path, and heading), the three response labels (`book_evidence`, `inference`,
and `external_verification`), a comprehension question, prohibited claims,
figure-format limitations, and numerical goldens when a formula is in scope.

Run their offline validation:

```bash
python3 tools/book-kit/validate_tutoring_cases.py --development
```

To prepare a human-review packet after a user has supplied an exported complete
Markdown or PDF and a tutor transcript, run:

```bash
python3 tools/book-kit/validate_tutoring_cases.py \
  --case evals/tutoring/development/softmax-evidence-boundary.json \
  --execution-report private-session.json \
  --artifact Understanding-LLMs.md \
  --output tutoring-execution-report.json
```

The report records the supplied artifact identity and verifies its SHA-256. Its
findings are advisory evidence for a human reviewer, not an automatic pass,
fail, or score. In particular, figure availability and visual detail vary by
Markdown extraction, PDF upload, reader, and assistive technology; reviewers
must assess the actual artifact and tutor response.

Private holdouts belong under `holdout/` but their JSON is intentionally ignored
and excluded from CI. A reviewer, not a model judge, compares a transcript to
the case and records an adjudication. This keeps the method compatible with
local TUI tools such as Codex or Claude Code and upload/chat tools such as
ChatGPT or DeepSeek, without assuming they share a tool API or render figures
the same way.

For a release-level trial, start with `human-review-template.json`. Run the
same representative task through both `ai-downloads-artifact` and
`user-supplies-artifact`, then record the actual tool/model, complete-book
identity, transcript reference, source locations checked, and human judgement.
The template intentionally begins as `unreviewed`; copying it is not evidence
that a trial occurred.
