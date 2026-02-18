from pathlib import Path

from atlas.safety_review import run_safety_review


def test_safety_review_passes_on_noisy_slice() -> None:
    report, passed, reasons = run_safety_review(
        dataset=Path("data/gold/v0_noisy_slice.jsonl"),
        min_non_ok_recall=1.0,
        max_violations=0,
        min_operational_threshold=0.60,
    )
    assert passed is True
    assert reasons == []
    assert report["safety"]["policy_conformance"]["total_violations"] == 0


def test_safety_review_fails_with_impossible_threshold() -> None:
    _report, passed, reasons = run_safety_review(
        dataset=Path("data/gold/v0_noisy_slice.jsonl"),
        min_non_ok_recall=1.1,
        max_violations=0,
        min_operational_threshold=0.60,
    )
    assert passed is False
    assert any("non_ok_detection_recall" in reason for reason in reasons)


def test_safety_review_with_baseline_trend_passes() -> None:
    _report, passed, reasons = run_safety_review(
        dataset=Path("data/gold/v0_noisy_slice.jsonl"),
        min_non_ok_recall=1.0,
        max_violations=0,
        min_operational_threshold=0.60,
        baseline_path=Path("data/gold/safety_baseline.noisy.json"),
        max_blocking_rate_delta=0.05,
    )
    assert passed is True
    assert reasons == []


def test_safety_review_with_tight_blocking_delta_fails() -> None:
    _report, passed, reasons = run_safety_review(
        dataset=Path("data/gold/v0_noisy_slice.jsonl"),
        min_non_ok_recall=1.0,
        max_violations=0,
        min_operational_threshold=0.60,
        baseline_path=Path("data/gold/safety_baseline.noisy.json"),
        max_blocking_rate_delta=-0.0001,
    )
    assert passed is False
    assert any("max_blocking_rate_delta" in reason for reason in reasons)


def test_safety_review_handles_invalid_baseline_file_without_exception(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    baseline.write_text('{"invalid": true}\n', encoding="utf-8")
    _report, passed, reasons = run_safety_review(
        dataset=Path("data/gold/v0_noisy_slice.jsonl"),
        min_non_ok_recall=1.0,
        max_violations=0,
        min_operational_threshold=0.60,
        baseline_path=baseline,
        max_blocking_rate_delta=0.05,
    )
    assert passed is False
    assert any("invalid baseline_safety_json" in reason for reason in reasons)
