# ATLAS Documentation

## Purpose
This document is the day-to-day operator and contributor guide for ATLAS.

## Project Structure
- `atlas/`: parser/runtime code
- `tests/`: automated regression coverage
- `data/gold/`: labeled benchmark datasets
- `docs/`: contracts, phraseology, safety, integration, and policy docs
- `roadmap.md`: execution tracker
- `justfile`: common local commands

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Quick Run
```bash
python -m atlas.cli "Air France 345, descend flight level 180, reduce speed to 250 knots"
python -m atlas.cli --trace "AAL77 descend flight level 180 and reduce speed to 250"
python -m atlas.cli --trace-log /tmp/atlas_trace.jsonl "AAL77 descend flight level 180"
```

## Test and Validation
```bash
pytest -q
```

```bash
just test
just eval_clean
just eval_noisy
just eval_readback
just eval_region
just eval_region_apac
just eval_safety
just data_quality
just safety_gate
just docs_build
```

## Evaluation Commands
```bash
python -m atlas.evaluate --dataset data/gold/v0_slice.jsonl
python -m atlas.evaluate --dataset data/gold/v0_noisy_slice.jsonl
python -m atlas.evaluate --readback-dataset data/gold/readback_pairs.v0.jsonl
python -m atlas.evaluate --hybrid-compare --dataset data/gold/v0_ambiguity_slice.jsonl
python -m atlas.evaluate --sequence-dataset data/gold/v0_sequence_slice.jsonl
python -m atlas.evaluate --dataset data/gold/v0_region_phraseology_slice.jsonl
python -m atlas.evaluate --dataset data/gold/v0_region_phraseology_apac_slice.jsonl
python -m atlas.evaluate --safety-dataset data/gold/v0_noisy_slice.jsonl
```

## Data Quality and Adjudication
Run audits before dataset merges:

```bash
python -m atlas.data_quality --dataset data/gold/v0_slice.jsonl
```

References:
- `docs/data-quality-adjudication.md`
- `docs/adjudication-ownership-policy.md`

## Safety Gate
Strict safety regression gate:

```bash
python -m atlas.safety_review \
  --dataset data/gold/v0_noisy_slice.jsonl \
  --min-non-ok-recall 1.0 \
  --max-violations 0 \
  --max-blocking-status-rate 0.25 \
  --baseline-safety-json data/gold/safety_baseline.noisy.json \
  --max-blocking-rate-delta 0.05
```

## Dataset Inventory
- `data/gold/v0_slice.jsonl`: core clean benchmark
- `data/gold/v0_noisy_slice.jsonl`: ASR-like/noisy benchmark
- `data/gold/readback_pairs.v0.jsonl`: readback mismatch benchmark
- `data/gold/v0_ambiguity_slice.jsonl`: deterministic vs hybrid ambiguity benchmark
- `data/gold/v0_sequence_slice.jsonl`: multi-turn sequence benchmark
- `data/gold/v0_region_phraseology_slice.jsonl`: regional/procedure phraseology set
- `data/gold/v0_region_phraseology_apac_slice.jsonl`: additional APAC phraseology set
- `data/gold/safety_baseline.noisy.json`: safety trend baseline for CI gate

## Core Capabilities
- deterministic slot extraction (altitude, speed, heading, frequency, runway, waypoint, squawk, hold, direct, climb_rate)
- explicit statuses (`ok`, `unknown`, `ambiguous`, `conflict`)
- confidence policy with threshold downgrades
- hybrid disambiguation for ambiguous maintain phrases
- multi-turn state tracking (amendments, cancellations, temporal conditions)
- parse-stage observability traces and optional JSONL trace sink
- evaluation, safety, and data-quality gates for CI

## Known Residual Risks
- `SequenceState.history_by_callsign` is unbounded for long-lived sessions.
- trace-log sink is append-only and relies on external retention/rotation policy.
- phraseology coverage is expanded but still incomplete for global procedures.

## Contributor Workflow
1. Implement a scoped change.
2. Add/adjust tests.
3. Run `pytest -q` and relevant `just` targets.
4. Update docs/contracts/policies if behavior changed.
5. Update `roadmap.md` only when code + tests + docs are aligned.

## Related Docs
- Contract: `docs/contracts/atlas.intent.v0.1.md`
- Phraseology conventions: `docs/phraseology-conventions.md`
- Metrics glossary: `docs/ml-terms.md`
- Safety playbook: `docs/safety-limitations-playbook.md`
- Integration examples: `docs/integration-examples.md`
- Migration notes: `docs/migration-v0.1-to-v0.2.md`

## MkDocs and GitHub Pages
Build docs locally:

```bash
mkdocs build --strict
```

Serve docs locally:

```bash
mkdocs serve
```

GitHub Actions integration:
- CI workflow (`.github/workflows/ci.yml`) runs `mkdocs build --strict`.
- Pages workflow (`.github/workflows/pages.yml`) deploys docs on push to `main`.
