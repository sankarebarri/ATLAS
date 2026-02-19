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
pip install -e .[dev,docs]
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

## Dataset Catalog
All datasets live in `data/gold/`.

Format notes:
- `*.jsonl`: one labeled sample per line, used by evaluation and data-quality tools.
- `*.json`: baseline/reference artifact used by safety gating logic.

### Core Parse Quality
- `data/gold/v0_slice.jsonl`
  - Purpose: clean baseline benchmark for parser correctness on canonical phrasing.
  - Use:
    ```bash
    python -m atlas.evaluate --dataset data/gold/v0_slice.jsonl
    python -m atlas.data_quality --dataset data/gold/v0_slice.jsonl
    ```

- `data/gold/v0_noisy_slice.jsonl`
  - Purpose: noisy/ASR-like utterances for robustness and safety-focused behavior checks.
  - Use:
    ```bash
    python -m atlas.evaluate --dataset data/gold/v0_noisy_slice.jsonl
    python -m atlas.evaluate --safety-dataset data/gold/v0_noisy_slice.jsonl
    python -m atlas.data_quality --dataset data/gold/v0_noisy_slice.jsonl
    ```

### Specialized Evaluation Sets
- `data/gold/readback_pairs.v0.jsonl`
  - Purpose: readback mismatch detection quality.
  - Use:
    ```bash
    python -m atlas.evaluate --readback-dataset data/gold/readback_pairs.v0.jsonl
    ```

- `data/gold/v0_ambiguity_slice.jsonl`
  - Purpose: deterministic vs hybrid disambiguation comparison on ambiguous phraseology.
  - Use:
    ```bash
    python -m atlas.evaluate --hybrid-compare --dataset data/gold/v0_ambiguity_slice.jsonl
    python -m atlas.data_quality --dataset data/gold/v0_ambiguity_slice.jsonl
    ```

- `data/gold/v0_sequence_slice.jsonl`
  - Purpose: multi-turn sequencing behavior (amendments, cancellations, temporal context).
  - Use:
    ```bash
    python -m atlas.evaluate --sequence-dataset data/gold/v0_sequence_slice.jsonl
    ```

- `data/gold/v0_region_phraseology_slice.jsonl`
  - Purpose: regional/procedural phraseology coverage beyond baseline wording.
  - Use:
    ```bash
    python -m atlas.evaluate --dataset data/gold/v0_region_phraseology_slice.jsonl
    python -m atlas.data_quality --dataset data/gold/v0_region_phraseology_slice.jsonl
    ```

- `data/gold/v0_region_phraseology_apac_slice.jsonl`
  - Purpose: additional APAC-oriented phraseology coverage.
  - Use:
    ```bash
    python -m atlas.evaluate --dataset data/gold/v0_region_phraseology_apac_slice.jsonl
    python -m atlas.data_quality --dataset data/gold/v0_region_phraseology_apac_slice.jsonl
    ```

### Safety Baseline Artifact
- `data/gold/safety_baseline.noisy.json`
  - Purpose: baseline reference metrics used to detect safety regression deltas in CI.
  - Use:
    ```bash
    python -m atlas.safety_review \
      --dataset data/gold/v0_noisy_slice.jsonl \
      --baseline-safety-json data/gold/safety_baseline.noisy.json \
      --min-non-ok-recall 1.0 \
      --max-violations 0 \
      --max-blocking-status-rate 0.25 \
      --max-blocking-rate-delta 0.05
    ```

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
- Datasets: `docs/datasets.md`
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
