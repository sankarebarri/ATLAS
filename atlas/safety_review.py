from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from atlas.evaluate import evaluate_safety_dataset


def _load_baseline(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "safety" in payload:
        payload = payload["safety"]

    if not isinstance(payload, dict):
        raise ValueError("baseline payload must be an object")
    if "fallback_behavior" not in payload:
        raise ValueError("baseline missing fallback_behavior section")
    fallback = payload["fallback_behavior"]
    if not isinstance(fallback, dict):
        raise ValueError("baseline fallback_behavior must be an object")
    if "blocking_status_rate" not in fallback:
        raise ValueError("baseline missing fallback_behavior.blocking_status_rate")
    return payload


def run_safety_review(
    *,
    dataset: Path,
    min_non_ok_recall: float,
    max_violations: int,
    min_operational_threshold: float,
    max_blocking_status_rate: float | None = None,
    baseline_path: Path | None = None,
    max_blocking_rate_delta: float | None = None,
) -> tuple[dict, bool, list[str]]:
    report = evaluate_safety_dataset(dataset, min_operational_threshold=min_operational_threshold)
    safety = report["safety"]
    conformance = safety["policy_conformance"]
    failure = safety["failure_mode_detection"]
    fallback = safety["fallback_behavior"]

    violations = int(conformance["total_violations"])
    recall = float(failure["non_ok_detection_recall"])
    blocking_rate = float(fallback["blocking_status_rate"])

    reasons: list[str] = []
    if violations > max_violations:
        reasons.append(f"violations {violations} exceed max_violations {max_violations}")
    if recall < min_non_ok_recall:
        reasons.append(f"non_ok_detection_recall {recall} below min_non_ok_recall {min_non_ok_recall}")
    if max_blocking_status_rate is not None and blocking_rate > max_blocking_status_rate:
        reasons.append(
            f"blocking_status_rate {blocking_rate} exceeds max_blocking_status_rate {max_blocking_status_rate}"
        )

    baseline_used: dict[str, Any] | None = None
    if baseline_path is not None:
        try:
            baseline_used = _load_baseline(baseline_path)
            baseline_blocking = float(baseline_used["fallback_behavior"]["blocking_status_rate"])
            delta = blocking_rate - baseline_blocking
            report["safety"]["trend"] = {
                "baseline_blocking_status_rate": baseline_blocking,
                "current_blocking_status_rate": blocking_rate,
                "delta_blocking_status_rate": round(delta, 4),
            }
            if max_blocking_rate_delta is not None and delta > max_blocking_rate_delta:
                reasons.append(
                    f"blocking_status_rate delta {round(delta,4)} exceeds max_blocking_rate_delta {max_blocking_rate_delta}"
                )
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            reasons.append(f"invalid baseline_safety_json: {exc}")

    return report, len(reasons) == 0, reasons


def main() -> None:
    parser = argparse.ArgumentParser(description="ATLAS safety review gate")
    parser.add_argument("--dataset", default="data/gold/v0_noisy_slice.jsonl")
    parser.add_argument("--min-non-ok-recall", type=float, default=1.0)
    parser.add_argument("--max-violations", type=int, default=0)
    parser.add_argument("--min-operational-threshold", type=float, default=0.60)
    parser.add_argument("--max-blocking-status-rate", type=float, default=None)
    parser.add_argument("--baseline-safety-json", default=None)
    parser.add_argument("--max-blocking-rate-delta", type=float, default=None)
    args = parser.parse_args()

    report, passed, reasons = run_safety_review(
        dataset=Path(args.dataset),
        min_non_ok_recall=args.min_non_ok_recall,
        max_violations=args.max_violations,
        min_operational_threshold=args.min_operational_threshold,
        max_blocking_status_rate=args.max_blocking_status_rate,
        baseline_path=Path(args.baseline_safety_json) if args.baseline_safety_json else None,
        max_blocking_rate_delta=args.max_blocking_rate_delta,
    )

    output = {
        "passed": passed,
        "reasons": reasons,
        "report": report,
        "thresholds": {
            "min_non_ok_recall": args.min_non_ok_recall,
            "max_violations": args.max_violations,
            "min_operational_threshold": args.min_operational_threshold,
            "max_blocking_status_rate": args.max_blocking_status_rate,
            "baseline_safety_json": args.baseline_safety_json,
            "max_blocking_rate_delta": args.max_blocking_rate_delta,
        },
    }
    print(json.dumps(output, indent=2, sort_keys=False))

    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
