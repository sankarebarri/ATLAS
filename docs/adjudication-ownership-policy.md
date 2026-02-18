# Adjudication Reviewer Assignment and Ownership Policy

## Scope
This policy defines who owns annotation decisions for gold datasets and how reviewer assignment is enforced.

## Ownership Model
- Dataset ownership unit: file-level ownership under `data/gold/`.
- Required roles per dataset change:
  - `Label Author`: proposes label additions/changes.
  - `Adjudicator`: resolves conflicts raised by data-quality audit.
  - `Maintainer`: approves schema/policy consistency.

## Assignment Rules
1. Every PR touching `data/gold/*.jsonl` must assign exactly one adjudicator.
2. Adjudicator cannot be the same person as label author.
3. If `adjudication_items` from `atlas.data_quality` are non-empty, adjudicator approval is mandatory before merge.
4. If changes modify fallback semantics (`status`, safety notes), maintainer approval is also mandatory.

## Decision Logging Requirements
For each adjudicated conflict, PR description must include:
- conflicting row IDs
- chosen canonical label
- one-sentence rationale
- confirmation that `atlas.evaluate` was rerun

## Operational Checklist
- run: `python -m atlas.data_quality --dataset <changed_dataset>`
- run: `python -m atlas.evaluate --dataset <changed_dataset>`
- include adjudication summary in PR body
- request adjudicator + maintainer review

## Suggested CODEOWNERS Mapping
- `data/gold/*` -> annotation maintainers
- `docs/data-quality-adjudication.md` and this policy -> data-quality maintainers
