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


def _counter_difference_items(left: Counter[tuple[Any, ...]], right: Counter[tuple[Any, ...]]) -> list[dict[str, Any]]:
    diff = left - right
    items: list[dict[str, Any]] = []
    for (itype, action, value, unit), count in diff.items():
        for _ in range(count):
            items.append({"type": itype, "action": action, "value": value, "unit": unit})
    return items


def compare_readback(atc_utterance: str, pilot_utterance: str) -> dict[str, Any]:
    atc = parse_utterance(atc_utterance, speaker="ATC")
    pilot = parse_utterance(pilot_utterance, speaker="PILOT")

    atc_slots = _slot_counter(atc.get("instructions", []))
    pilot_slots = _slot_counter(pilot.get("instructions", []))

    missing_in_pilot = _counter_difference_items(atc_slots, pilot_slots)
    unexpected_in_pilot = _counter_difference_items(pilot_slots, atc_slots)

    callsign_mismatch = False
    if atc.get("callsign") and pilot.get("callsign") and atc["callsign"] != pilot["callsign"]:
        callsign_mismatch = True

    mismatch_detected = bool(missing_in_pilot or unexpected_in_pilot or callsign_mismatch)

    return {
        "callsign_expected": atc.get("callsign"),
        "callsign_readback": pilot.get("callsign"),
        "callsign_mismatch": callsign_mismatch,
        "missing_in_readback": missing_in_pilot,
        "unexpected_in_readback": unexpected_in_pilot,
        "mismatch_detected": mismatch_detected,
    }


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


def evaluate_readback_dataset(path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    tp = fp = fn = tn = 0
    for row in rows:
        result = compare_readback(row["atc_utterance"], row["pilot_utterance"])
        predicted = bool(result["mismatch_detected"])
        expected = bool(row["expected_mismatch"])

        if predicted and expected:
            tp += 1
        elif predicted and not expected:
            fp += 1
        elif not predicted and expected:
            fn += 1
        else:
            tn += 1

    n = len(rows)
    return {
        "dataset": str(path),
        "samples": n,
        "readback_mismatch": {
            "precision": round(_safe_div(tp, tp + fp), 4),
            "recall": round(_safe_div(tp, tp + fn), 4),
            "f1": round(_f1(tp, fp, fn), 4),
            "accuracy": round(_safe_div(tp + tn, n), 4),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate ATLAS parser on gold datasets")
    parser.add_argument("--dataset", default=None, help="Path to single-utterance gold dataset JSONL")
    parser.add_argument("--readback-dataset", default=None, help="Path to readback-pair gold dataset JSONL")
    args = parser.parse_args()

    if args.readback_dataset:
        report = evaluate_readback_dataset(Path(args.readback_dataset))
    else:
        dataset = args.dataset or "data/gold/v0_slice.jsonl"
        report = evaluate_dataset(Path(dataset))

    print(json.dumps(report, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
