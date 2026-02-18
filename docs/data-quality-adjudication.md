# Data Quality and Annotation Adjudication

## Goal
Provide a repeatable process to detect labeling issues in gold datasets and route disagreements to adjudication.

## Audit Command
Run dataset audit:

```bash
python -m atlas.data_quality --dataset data/gold/v0_slice.jsonl
```

Behavior:
- exits `0` when no hard errors are found.
- exits `2` when hard validation errors are found.

## What the Auditor Checks
- duplicate or missing `id`
- invalid `expected.status`
- malformed `expected.instructions`
- canonical field sanity (callsign format, squawk octal validity, runway/frequency/heading/speed/FL range checks)
- same normalized utterance with conflicting expected labels

## Report Fields
- `errors`: hard issues that should block merge.
- `warnings`: suspicious but non-blocking patterns.
- `adjudication_items`: disagreement candidates requiring human decision.
- `summary`: counts for quick CI/pipeline gating.

## Adjudication Workflow
1. Run the audit over changed datasets.
2. Fix all hard `errors` before merge.
3. For each `adjudication_item`, choose a canonical label and update conflicting rows.
4. Record decision rationale in PR description or dataset change notes.
5. Re-run `python -m atlas.evaluate` for affected datasets.

## Suggested Merge Policy
- block merge on `summary.error_count > 0`
- require explicit reviewer sign-off for non-empty `adjudication_items`

## Reviewer Ownership Policy
Reviewer assignment and ownership requirements are defined in:
- `docs/adjudication-ownership-policy.md`
