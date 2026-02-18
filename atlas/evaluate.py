from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from atlas.pipeline import parse_utterance


def _safe_div(num: int, den: int) -> float:
    return num / den if den else 0.0


def _f1(tp: int, fp: int, fn: int) -> float:
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    return _safe_div(2 * precision * recall, precision + recall)


def _canonical_value(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 3)
    return value


def _instruction_type_counter(instructions: list[dict[str, Any]]) -> Counter[str]:
    return Counter(item["type"] for item in instructions)


def _slot_counter(instructions: list[dict[str, Any]]) -> Counter[tuple[Any, ...]]:
    return Counter(
        (
            item.get("type"),
            item.get("action"),
            _canonical_value(item.get("value")),
            item.get("unit"),
        )
        for item in instructions
    )


def _count_overlap(left: Counter[Any], right: Counter[Any]) -> int:
    keys = set(left) | set(right)
    return sum(min(left.get(k, 0), right.get(k, 0)) for k in keys)


def evaluate_dataset(path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    intent_tp = intent_fp = intent_fn = 0
    slot_tp = slot_fp = slot_fn = 0
    status_correct = 0
    callsign_correct = 0

    for row in rows:
        expected = row["expected"]
        predicted = parse_utterance(
            text=row["utterance"],
            speaker=row.get("speaker", "ATC"),
            utterance_id=row.get("id"),
        )

        expected_types = _instruction_type_counter(expected.get("instructions", []))
        predicted_types = _instruction_type_counter(predicted.get("instructions", []))
        tp_i = _count_overlap(expected_types, predicted_types)
        intent_tp += tp_i
        intent_fp += sum(predicted_types.values()) - tp_i
        intent_fn += sum(expected_types.values()) - tp_i

        expected_slots = _slot_counter(expected.get("instructions", []))
        predicted_slots = _slot_counter(predicted.get("instructions", []))
        tp_s = _count_overlap(expected_slots, predicted_slots)
        slot_tp += tp_s
        slot_fp += sum(predicted_slots.values()) - tp_s
        slot_fn += sum(expected_slots.values()) - tp_s

        if predicted.get("status") == expected.get("status"):
            status_correct += 1
        if predicted.get("callsign") == expected.get("callsign"):
            callsign_correct += 1

    n = len(rows)
    return {
        "dataset": str(path),
        "samples": n,
        "intent": {
            "precision": round(_safe_div(intent_tp, intent_tp + intent_fp), 4),
            "recall": round(_safe_div(intent_tp, intent_tp + intent_fn), 4),
            "f1": round(_f1(intent_tp, intent_fp, intent_fn), 4),
            "tp": intent_tp,
            "fp": intent_fp,
            "fn": intent_fn,
        },
        "slot": {
            "precision": round(_safe_div(slot_tp, slot_tp + slot_fp), 4),
            "recall": round(_safe_div(slot_tp, slot_tp + slot_fn), 4),
            "f1": round(_f1(slot_tp, slot_fp, slot_fn), 4),
            "tp": slot_tp,
            "fp": slot_fp,
            "fn": slot_fn,
        },
        "status_accuracy": round(_safe_div(status_correct, n), 4),
        "callsign_accuracy": round(_safe_div(callsign_correct, n), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate ATLAS parser on a gold JSONL dataset")
    parser.add_argument("--dataset", default="data/gold/v0_slice.jsonl", help="Path to gold dataset JSONL")
    args = parser.parse_args()

    report = evaluate_dataset(Path(args.dataset))
    print(json.dumps(report, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
