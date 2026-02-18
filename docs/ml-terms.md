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
- `Status accuracy`:
  - fraction of utterances where predicted `status` equals expected `status`.
- `Callsign accuracy`:
  - fraction of utterances where predicted `callsign` equals expected `callsign`.
- `Readback mismatch detection`:
  - binary task where positive class means a mismatch exists between ATC clearance and pilot readback.
  - scored with precision/recall/F1/accuracy over pair-level decisions.
- `Severity-weighted error`:
  - applies risk weights per intent type to errors so high-risk misses count more.
  - `weighted_fp = sum(weight(type) * FP_count_by_type)`
  - `weighted_fn = sum(weight(type) * FN_count_by_type)`
  - `weighted_total_error = weighted_fp + weighted_fn`

## Practical Interpretation
- High precision + low recall: conservative parser, misses many valid intents.
- Low precision + high recall: aggressive parser, adds many incorrect intents.
- F1 balances both and is useful when both false alarms and misses matter.

## Notes
- "Gold dataset" means trusted ground truth labels.
- ATLAS uses JSONL (`.jsonl`) so each line is one independent sample for easy diffing and streaming.
