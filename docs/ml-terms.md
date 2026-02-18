# ML Terms and Metrics Reference

This file defines ML/NLP evaluation terms used in ATLAS.

## Confusion Components
- `TP` (true positive): parser predicted an item and it is correct.
- `FP` (false positive): parser predicted an item that is not in ground truth.
- `FN` (false negative): parser missed an item that is in ground truth.
- `TN` (true negative): parser correctly did not predict an item.

## Core Classification Metrics
- `Precision`: how correct positive predictions are.
  - Formula: `precision = TP / (TP + FP)`
- `Recall`: how much of ground truth positives were found.
  - Formula: `recall = TP / (TP + FN)`
- `F1`: harmonic mean of precision and recall.
  - Formula: `f1 = 2 * precision * recall / (precision + recall)`
  - Equivalent form: `f1 = 2*TP / (2*TP + FP + FN)`
- `Accuracy`: overall fraction of correct predictions.
  - Formula: `accuracy = (TP + TN) / (TP + TN + FP + FN)`

## ATLAS Evaluation-Specific Terms
- `Intent precision/recall/F1`:
  - computed on instruction `type` matches (e.g., `altitude`, `speed`).
- `Slot precision/recall/F1`:
  - computed on structured tuples (`type`, `action`, `value`, `unit`).
- `Condition-aware slot matching (sequence eval)`:
  - for sequence benchmarks, slot comparison includes temporal condition:
  - tuple shape is (`type`, `action`, `value`, `unit`, `condition`).
- `Status accuracy`:
  - fraction of utterances where predicted `status` equals expected `status`.
- `Callsign accuracy`:
  - fraction of utterances where predicted `callsign` equals expected `callsign`.
- `Turn accuracy`:
  - for sequence datasets, fraction of turns where status + callsign + condition-aware slot set are correct.
- `Final state accuracy`:
  - for sequence datasets, fraction of sessions where persisted active state matches expected end-of-session state.
- `Readback mismatch detection`:
  - binary task where positive class means a mismatch exists between ATC clearance and pilot readback.
  - scored with precision/recall/F1/accuracy over pair-level decisions.
- `Severity-weighted error`:
  - applies risk weights per intent type to errors so high-risk misses count more.
  - `weighted_fp = sum(weight(type) * FP_count_by_type)`
  - `weighted_fn = sum(weight(type) * FN_count_by_type)`
  - `weighted_total_error = weighted_fp + weighted_fn`
- `Calibration`:
  - measures whether confidence scores match empirical correctness.
  - `ECE` (Expected Calibration Error): weighted average confidence-accuracy gap across bins.
  - `MCE` (Maximum Calibration Error): worst per-bin confidence-accuracy gap.
  - `Brier score`: mean squared error between confidence and correctness.
  - Formula: `brier = mean((confidence - correctness)^2)`
- `Hybrid comparison delta`:
  - compares baseline deterministic mode (`enable_hybrid=False`) vs hybrid mode (`enable_hybrid=True`) on the same dataset.
  - reported as metric deltas such as:
  - `delta.slot_f1 = hybrid.slot_f1 - baseline.slot_f1`
  - `delta.intent_f1 = hybrid.intent_f1 - baseline.intent_f1`
  - `delta.status_accuracy = hybrid.status_accuracy - baseline.status_accuracy`
- `Safety policy conformance metrics`:
  - `total_violations`: total count of safety-policy violations detected in parser outputs.
  - `violation_rate = total_violations / samples`.
  - violation categories currently include:
  - `silent_ok_without_instructions`
  - `ok_below_operational_threshold`
  - `unknown_with_instructions`
  - `conflict_without_conflict_note`
- `Blocking status rate`:
  - fraction of outputs in `unknown|ambiguous|conflict` (non-automatable statuses).
- `Non-ok detection recall`:
  - ability to detect expected non-`ok` failure modes.
  - Formula: `detected_non_ok / expected_non_ok`
- `Safety gate thresholds`:
  - `max_violations`: maximum allowed policy conformance violations.
  - `min_non_ok_recall`: minimum required recall for expected non-`ok` failure modes.
  - `max_blocking_status_rate`: maximum allowed absolute blocking-status fraction.
  - `max_blocking_rate_delta`: maximum allowed increase versus baseline blocking-status rate.

## Practical Interpretation
- High precision + low recall: conservative parser, misses many valid intents.
- Low precision + high recall: aggressive parser, adds many incorrect intents.
- F1 balances both and is useful when both false alarms and misses matter.

## Notes
- "Gold dataset" means trusted ground truth labels.
- ATLAS uses JSONL (`.jsonl`) so each line is one independent sample for easy diffing and streaming.
