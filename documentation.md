# ATLAS Documentation

## Purpose
This file is the day-to-day operating guide for building ATLAS and keeping project status current.

## Project Structure
- `atlas/`: parser implementation
- `tests/`: automated tests
- `docs/`: schema and domain docs
- `roadmap.md`: checklist tracker (single source of truth for progress)

## References
- ML metrics glossary: `docs/ml-terms.md`

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Run the Parser
```bash
python -m atlas.cli "Air France 345, descend flight level 180, reduce speed to 250 knots"
```

## Run Tests
```bash
pytest -q
```

## Run Evaluation
```bash
python -m atlas.evaluate --dataset data/gold/v0_slice.jsonl
python -m atlas.evaluate --dataset data/gold/v0_noisy_slice.jsonl
python -m atlas.evaluate --readback-dataset data/gold/readback_pairs.v0.jsonl
python -m atlas.evaluate --dataset data/gold/v0_noisy_slice.jsonl --severity-weights my_weights.json
python -m atlas.evaluate --dataset data/gold/v0_noisy_slice.jsonl --write-report --report-label noisy
```
This reports:
- intent precision/recall/F1
- slot precision/recall/F1
- status accuracy
- callsign accuracy
- readback mismatch precision/recall/F1/accuracy
- severity-weighted error totals (`weighted_fp`, `weighted_fn`, `weighted_total_error`)
- reproducible report artifacts (`report_artifacts`) as JSON + markdown

Report artifact notes:
- reports are written under `reports/` by default.
- filenames use UTC timestamp + label, e.g. `20260218T120000Z_noisy.json`.

Dataset notes:
- `data/gold/v0_slice.jsonl`: cleaner synthetic baseline.
- `data/gold/v0_noisy_slice.jsonl`: hand-curated ASR-like noise/variant set.
- `data/gold/readback_pairs.v0.jsonl`: ATC/pilot paired readback-mismatch set.

## Development Workflow
1. Pick one unchecked task in `roadmap.md`.
2. Implement only that slice.
3. Add or update tests for the change.
4. Run `pytest -q`.
5. Mark the roadmap checkbox from `[ ]` to `[x]` (or `[~]` if partial).
6. Update docs if contract or behavior changed.

## How to Update Roadmap
- Use `[x]` only when:
  - code is implemented,
  - tests exist or are updated,
  - tests pass locally.
- Use `[~]` when implementation exists but one of the above is incomplete.
- Keep "Next Up" focused on the next 3-5 concrete tasks only.

## Commit and Push Policy
Before pushing to GitHub, verify:
```bash
git status --short
pytest -q
```

Push only when all are true:
- Working tree has only intentional changes.
- Tests pass.
- `roadmap.md` reflects actual state.
- Related docs are updated.

Suggested commands:
```bash
git add .
git commit -m "feat: <short description>"
git push
```

## Current Baseline Capabilities
- callsign extraction/normalization
- deterministic parsing for altitude, speed, heading, frequency, runway, waypoint, squawk, hold, direct, climb_rate
- per-instruction trace metadata (`rule`, `pattern`, `segment`) for parser auditability
- confidence policy with tiers (`low`, `medium`, `high`) and low-confidence downgrade to `ambiguous`
- fallback statuses: `ok`, `unknown`, `ambiguous`, `conflict`
- basic amendment detection via `CORRECTION`
- evaluation runner over gold JSONL datasets (`atlas.evaluate`)

## Known Gaps
- no CI metrics/regression gates yet
