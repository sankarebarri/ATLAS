from pathlib import Path

from atlas.evaluate import evaluate_dataset


def test_evaluate_dataset_returns_metrics() -> None:
    report = evaluate_dataset(Path("data/gold/v0_slice.jsonl"))
    assert report["samples"] >= 100
    assert 0.0 <= report["intent"]["f1"] <= 1.0
    assert 0.0 <= report["slot"]["f1"] <= 1.0
    assert 0.0 <= report["status_accuracy"] <= 1.0
    assert 0.0 <= report["callsign_accuracy"] <= 1.0
