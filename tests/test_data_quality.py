import json
from pathlib import Path

from atlas.data_quality import audit_gold_dataset


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_audit_dataset_detects_duplicate_ids_and_invalid_squawk(tmp_path: Path) -> None:
    dataset = tmp_path / "bad.jsonl"
    _write_jsonl(
        dataset,
        [
            {
                "id": "row-1",
                "utterance": "AAL77 squawk 8888",
                "speaker": "ATC",
                "expected": {
                    "status": "ok",
                    "callsign": "AAL77",
                    "instructions": [{"type": "squawk", "action": "assign", "value": "8888", "unit": "octal"}],
                },
            },
            {
                "id": "row-1",
                "utterance": "AAL77 descend flight level 180",
                "speaker": "ATC",
                "expected": {
                    "status": "ok",
                    "callsign": "AAL77",
                    "instructions": [{"type": "altitude", "action": "descend", "value": 180, "unit": "FL"}],
                },
            },
        ],
    )

    report = audit_gold_dataset(dataset)
    assert report["summary"]["error_count"] >= 2
    messages = [item["message"] for item in report["errors"]]
    assert any("duplicate id" in msg for msg in messages)
    assert any("invalid squawk code" in msg for msg in messages)


def test_audit_dataset_detects_adjudication_candidate_on_conflicting_labels(tmp_path: Path) -> None:
    dataset = tmp_path / "conflict.jsonl"
    _write_jsonl(
        dataset,
        [
            {
                "id": "row-1",
                "utterance": "AAL77 descend flight level 180",
                "speaker": "ATC",
                "expected": {
                    "status": "ok",
                    "callsign": "AAL77",
                    "instructions": [{"type": "altitude", "action": "descend", "value": 180, "unit": "FL"}],
                },
            },
            {
                "id": "row-2",
                "utterance": "AAL77 descend flight level 180",
                "speaker": "ATC",
                "expected": {
                    "status": "ok",
                    "callsign": "AAL77",
                    "instructions": [{"type": "altitude", "action": "descend", "value": 170, "unit": "FL"}],
                },
            },
        ],
    )

    report = audit_gold_dataset(dataset)
    assert report["summary"]["error_count"] == 0
    assert report["summary"]["adjudication_count"] == 1
    item = report["adjudication_items"][0]
    assert item["type"] == "label_conflict"
    assert set(item["row_ids"]) == {"row-1", "row-2"}


def test_audit_clean_slice_has_no_hard_errors() -> None:
    report = audit_gold_dataset(Path("data/gold/v0_slice.jsonl"))
    assert report["summary"]["error_count"] == 0


def test_audit_dataset_handles_invalid_json_line_without_crash(tmp_path: Path) -> None:
    dataset = tmp_path / "invalid.jsonl"
    dataset.write_text("{bad json}\n", encoding="utf-8")
    report = audit_gold_dataset(dataset)
    assert report["summary"]["error_count"] == 1
    assert "invalid JSON at line 1" in report["errors"][0]["message"]
