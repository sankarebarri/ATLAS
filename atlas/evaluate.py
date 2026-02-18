from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from atlas.pipeline import parse_utterance

DEFAULT_SEVERITY_WEIGHTS: dict[str, float] = {
    "altitude": 5.0,
    "heading": 4.0,
    "speed": 4.0,
    "runway": 5.0,
    "frequency": 3.0,
    "direct": 3.0,
    "waypoint": 3.0,
    "hold": 3.0,
    "squawk": 2.0,
    "climb_rate": 2.0,
}


def _safe_div(num: float, den: float) -> float:
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


def _weighted_error_totals(
    expected_slots: Counter[tuple[Any, ...]],
    predicted_slots: Counter[tuple[Any, ...]],
    severity_weights: dict[str, float],
) -> dict[str, float]:
    weighted_fp = 0.0
    weighted_fn = 0.0

    over_pred = predicted_slots - expected_slots
    for (itype, _action, _value, _unit), count in over_pred.items():
        weighted_fp += severity_weights.get(str(itype), 1.0) * count

    missed = expected_slots - predicted_slots
    for (itype, _action, _value, _unit), count in missed.items():
        weighted_fn += severity_weights.get(str(itype), 1.0) * count

    return {
        "weighted_fp": round(weighted_fp, 4),
        "weighted_fn": round(weighted_fn, 4),
        "weighted_total_error": round(weighted_fp + weighted_fn, 4),
    }


def _is_utterance_correct(expected: dict[str, Any], predicted: dict[str, Any]) -> bool:
    if expected.get("status") != predicted.get("status"):
        return False
    if expected.get("callsign") != predicted.get("callsign"):
        return False
    return _slot_counter(expected.get("instructions", [])) == _slot_counter(predicted.get("instructions", []))


def _calibration_report(confidences: list[float], correctness: list[int], bins: int = 10) -> dict[str, Any]:
    n = len(confidences)
    if n == 0:
        return {
            "bins": bins,
            "ece": 0.0,
            "mce": 0.0,
            "brier_score": 0.0,
            "reliability_bins": [],
        }

    ece = 0.0
    mce = 0.0
    reliability_bins: list[dict[str, Any]] = []

    for i in range(bins):
        low = i / bins
        high = (i + 1) / bins
        # Include right edge only on final bin so 1.0 is captured.
        bucket_idx = [
            idx
            for idx, conf in enumerate(confidences)
            if (low <= conf < high) or (i == bins - 1 and low <= conf <= high)
        ]
        count = len(bucket_idx)
        if count == 0:
            reliability_bins.append(
                {
                    "bin": i + 1,
                    "low": round(low, 3),
                    "high": round(high, 3),
                    "count": 0,
                    "avg_confidence": None,
                    "accuracy": None,
                    "gap": None,
                }
            )
            continue

        avg_conf = sum(confidences[idx] for idx in bucket_idx) / count
        acc = sum(correctness[idx] for idx in bucket_idx) / count
        gap = abs(acc - avg_conf)
        ece += (count / n) * gap
        mce = max(mce, gap)
        reliability_bins.append(
            {
                "bin": i + 1,
                "low": round(low, 3),
                "high": round(high, 3),
                "count": count,
                "avg_confidence": round(avg_conf, 4),
                "accuracy": round(acc, 4),
                "gap": round(gap, 4),
            }
        )

    brier = sum((conf - corr) ** 2 for conf, corr in zip(confidences, correctness, strict=True)) / n
    return {
        "bins": bins,
        "ece": round(ece, 4),
        "mce": round(mce, 4),
        "brier_score": round(brier, 4),
        "reliability_bins": reliability_bins,
    }


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


def evaluate_dataset(path: Path, severity_weights: dict[str, float] | None = None) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    weights = severity_weights or DEFAULT_SEVERITY_WEIGHTS

    intent_tp = intent_fp = intent_fn = 0
    slot_tp = slot_fp = slot_fn = 0
    status_correct = 0
    callsign_correct = 0
    weighted_fp = 0.0
    weighted_fn = 0.0
    confidences: list[float] = []
    correctness: list[int] = []

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

        weighted = _weighted_error_totals(expected_slots, predicted_slots, weights)
        weighted_fp += weighted["weighted_fp"]
        weighted_fn += weighted["weighted_fn"]

        if predicted.get("status") == expected.get("status"):
            status_correct += 1
        if predicted.get("callsign") == expected.get("callsign"):
            callsign_correct += 1
        confidences.append(float(predicted.get("confidence", 0.0)))
        correctness.append(1 if _is_utterance_correct(expected, predicted) else 0)

    n = len(rows)
    weighted_total = weighted_fp + weighted_fn
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
        "severity_weighted_error": {
            "weights": weights,
            "weighted_fp": round(weighted_fp, 4),
            "weighted_fn": round(weighted_fn, 4),
            "weighted_total_error": round(weighted_total, 4),
            "weighted_error_per_sample": round(_safe_div(weighted_total, n), 4),
        },
        "calibration": _calibration_report(confidences, correctness, bins=10),
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


def _load_weights(path: str | None) -> dict[str, float] | None:
    if not path:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return {str(k): float(v) for k, v in payload.items()}


def _slugify_label(label: str) -> str:
    text = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in label.strip().lower())
    text = "-".join(part for part in text.split("-") if part)
    return text or "report"


def _render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# ATLAS Evaluation Report",
        "",
        f"- Dataset: `{report.get('dataset')}`",
        f"- Samples: `{report.get('samples')}`",
        "",
    ]

    if "intent" in report:
        intent = report["intent"]
        slot = report["slot"]
        lines.extend(
            [
                "## Core Metrics",
                "",
                f"- Intent F1: `{intent['f1']}` (P `{intent['precision']}`, R `{intent['recall']}`)",
                f"- Slot F1: `{slot['f1']}` (P `{slot['precision']}`, R `{slot['recall']}`)",
                f"- Status Accuracy: `{report['status_accuracy']}`",
                f"- Callsign Accuracy: `{report['callsign_accuracy']}`",
                "",
            ]
        )
        if "severity_weighted_error" in report:
            sev = report["severity_weighted_error"]
            lines.extend(
                [
                    "## Severity-Weighted Error",
                    "",
                    f"- Weighted FP: `{sev['weighted_fp']}`",
                    f"- Weighted FN: `{sev['weighted_fn']}`",
                    f"- Weighted Total Error: `{sev['weighted_total_error']}`",
                    f"- Weighted Error / Sample: `{sev['weighted_error_per_sample']}`",
                    "",
                ]
            )
        if "calibration" in report:
            cal = report["calibration"]
            lines.extend(
                [
                    "## Calibration",
                    "",
                    f"- ECE: `{cal['ece']}`",
                    f"- MCE: `{cal['mce']}`",
                    f"- Brier Score: `{cal['brier_score']}`",
                    f"- Bins: `{cal['bins']}`",
                    "",
                ]
            )

    if "readback_mismatch" in report:
        rb = report["readback_mismatch"]
        lines.extend(
            [
                "## Readback Mismatch",
                "",
                f"- F1: `{rb['f1']}` (P `{rb['precision']}`, R `{rb['recall']}`)",
                f"- Accuracy: `{rb['accuracy']}`",
                f"- Counts: TP `{rb['tp']}`, FP `{rb['fp']}`, FN `{rb['fn']}`, TN `{rb['tn']}`",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def write_report_artifacts(
    report: dict[str, Any],
    output_dir: Path,
    label: str,
    timestamp: str | None = None,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = timestamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = _slugify_label(label)
    stem = f"{ts}_{slug}"
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate ATLAS parser on gold datasets")
    parser.add_argument("--dataset", default=None, help="Path to single-utterance gold dataset JSONL")
    parser.add_argument("--readback-dataset", default=None, help="Path to readback-pair gold dataset JSONL")
    parser.add_argument("--severity-weights", default=None, help="Optional JSON file with per-intent weights")
    parser.add_argument("--write-report", action="store_true", help="Write timestamped JSON and markdown reports")
    parser.add_argument("--report-dir", default="reports", help="Directory for report artifacts")
    parser.add_argument("--report-label", default="evaluation", help="Label used in report filename")
    args = parser.parse_args()

    if args.readback_dataset:
        report = evaluate_readback_dataset(Path(args.readback_dataset))
    else:
        dataset = args.dataset or "data/gold/v0_slice.jsonl"
        report = evaluate_dataset(Path(dataset), severity_weights=_load_weights(args.severity_weights))

    if args.write_report:
        artifact_paths = write_report_artifacts(
            report=report,
            output_dir=Path(args.report_dir),
            label=args.report_label,
        )
        report["report_artifacts"] = artifact_paths

    print(json.dumps(report, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
