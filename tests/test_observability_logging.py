import json
from pathlib import Path

from atlas.pipeline import parse_utterance


def test_trace_log_writes_jsonl_record(tmp_path: Path) -> None:
    log_path = tmp_path / "trace" / "parse_trace.jsonl"
    out = parse_utterance(
        "AAL77 descend flight level 180",
        trace_log_path=str(log_path),
    )

    assert out["status"] in {"ok", "ambiguous", "conflict", "unknown"}
    assert log_path.exists()

    rows = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 1
    row = rows[0]
    assert row["text"] == "AAL77 descend flight level 180"
    assert row["status"] == out["status"]
    assert isinstance(row["trace"], list)
    assert any(event["stage"] == "finalize" for event in row["trace"])


def test_trace_log_appends_multiple_records(tmp_path: Path) -> None:
    log_path = tmp_path / "trace.jsonl"
    parse_utterance("AAL77 descend flight level 180", trace_log_path=str(log_path))
    parse_utterance("hello aircraft how are you", trace_log_path=str(log_path))

    rows = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 2
