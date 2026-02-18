from pathlib import Path

from atlas.evaluate import compare_readback, evaluate_readback_dataset


def test_compare_readback_detects_slot_mismatch() -> None:
    result = compare_readback("AFR345 descend flight level 180", "AFR345 descend flight level 170")
    assert result["mismatch_detected"] is True
    assert result["missing_in_readback"]


def test_compare_readback_detects_callsign_mismatch() -> None:
    result = compare_readback("AFR345 descend flight level 180", "AFR346 descend flight level 180")
    assert result["mismatch_detected"] is True
    assert result["callsign_mismatch"] is True


def test_compare_readback_accepts_matching_readback() -> None:
    result = compare_readback("UAL12 turn left heading 270", "UAL12 turn left heading 270")
    assert result["mismatch_detected"] is False


def test_evaluate_readback_dataset_returns_metrics() -> None:
    report = evaluate_readback_dataset(Path("data/gold/readback_pairs.v0.jsonl"))
    assert report["samples"] >= 10
    mismatch = report["readback_mismatch"]
    assert 0.0 <= mismatch["precision"] <= 1.0
    assert 0.0 <= mismatch["recall"] <= 1.0
    assert 0.0 <= mismatch["f1"] <= 1.0
    assert 0.0 <= mismatch["accuracy"] <= 1.0
