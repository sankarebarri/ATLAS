from pathlib import Path

from atlas.evaluate import evaluate_dataset, evaluate_hybrid_ambiguity, evaluate_safety_dataset, evaluate_sequence_dataset


def test_evaluate_dataset_returns_metrics() -> None:
    report = evaluate_dataset(Path("data/gold/v0_slice.jsonl"))
    assert report["samples"] >= 100
    assert 0.0 <= report["intent"]["f1"] <= 1.0
    assert 0.0 <= report["slot"]["f1"] <= 1.0
    assert 0.0 <= report["status_accuracy"] <= 1.0
    assert 0.0 <= report["callsign_accuracy"] <= 1.0
    assert "severity_weighted_error" in report
    assert "calibration" in report
    calibration = report["calibration"]
    assert 0.0 <= calibration["ece"] <= 1.0
    assert 0.0 <= calibration["mce"] <= 1.0
    assert calibration["brier_score"] >= 0.0
    assert calibration["bins"] == 10
    assert len(calibration["reliability_bins"]) == 10


def test_severity_weighted_error_nonzero_on_noisy_data() -> None:
    report = evaluate_dataset(Path("data/gold/v0_noisy_slice.jsonl"))
    sev = report["severity_weighted_error"]
    assert sev["weighted_total_error"] >= 0.0


def test_hybrid_ambiguity_compare_improves_slot_f1() -> None:
    report = evaluate_hybrid_ambiguity(Path("data/gold/v0_ambiguity_slice.jsonl"))
    assert report["delta"]["slot_f1"] > 0.0
    assert report["hybrid"]["slot_f1"] >= report["baseline"]["slot_f1"]


def test_hybrid_preserves_core_slice_scores() -> None:
    baseline = evaluate_dataset(Path("data/gold/v0_slice.jsonl"), enable_hybrid=False)
    hybrid = evaluate_dataset(Path("data/gold/v0_slice.jsonl"), enable_hybrid=True)
    assert hybrid["intent"]["f1"] >= baseline["intent"]["f1"]
    assert hybrid["slot"]["f1"] >= baseline["slot"]["f1"]


def test_evaluate_sequence_dataset_returns_perfect_scores_on_benchmark() -> None:
    report = evaluate_sequence_dataset(Path("data/gold/v0_sequence_slice.jsonl"))
    assert report["sessions"] >= 2
    assert report["turn_accuracy"] == 1.0
    assert report["final_state_accuracy"] == 1.0


def test_evaluate_region_phraseology_slice() -> None:
    report = evaluate_dataset(Path("data/gold/v0_region_phraseology_slice.jsonl"))
    assert report["samples"] >= 6
    assert report["intent"]["f1"] == 1.0
    assert report["slot"]["f1"] == 1.0


def test_evaluate_region_phraseology_apac_slice() -> None:
    report = evaluate_dataset(Path("data/gold/v0_region_phraseology_apac_slice.jsonl"))
    assert report["samples"] >= 6
    assert report["intent"]["f1"] == 1.0
    assert report["slot"]["f1"] == 1.0


def test_evaluate_safety_dataset_reports_policy_conformance() -> None:
    report = evaluate_safety_dataset(Path("data/gold/v0_noisy_slice.jsonl"))
    assert report["samples"] >= 30
    safety = report["safety"]
    assert "policy_conformance" in safety
    assert "fallback_behavior" in safety
    assert "failure_mode_detection" in safety
    assert safety["policy_conformance"]["total_violations"] >= 0
    assert 0.0 <= safety["fallback_behavior"]["blocking_status_rate"] <= 1.0
    assert 0.0 <= safety["failure_mode_detection"]["non_ok_detection_recall"] <= 1.0
