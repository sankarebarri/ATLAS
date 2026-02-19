# Datasets

All evaluation and audit datasets live in `data/gold/`.

## Formats
- `*.jsonl`: one labeled sample per line, used by evaluation and data-quality tools.
- `*.json`: baseline/reference artifact used by safety gating logic.

## Core Parse Quality
- `data/gold/v0_slice.jsonl`
  - Purpose: clean baseline benchmark for parser correctness on canonical phrasing.
  - Use:
    ```bash
    python -m atlas.evaluate --dataset data/gold/v0_slice.jsonl
    python -m atlas.data_quality --dataset data/gold/v0_slice.jsonl
    ```

- `data/gold/v0_noisy_slice.jsonl`
  - Purpose: noisy/ASR-like utterances for robustness and safety-focused checks.
  - Use:
    ```bash
    python -m atlas.evaluate --dataset data/gold/v0_noisy_slice.jsonl
    python -m atlas.evaluate --safety-dataset data/gold/v0_noisy_slice.jsonl
    python -m atlas.data_quality --dataset data/gold/v0_noisy_slice.jsonl
    ```

## Specialized Evaluation Sets
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

## Safety Baseline Artifact
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
