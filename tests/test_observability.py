from atlas.pipeline import parse_utterance


def test_parse_trace_includes_pipeline_stages() -> None:
    out = parse_utterance(
        "AAL77 descend flight level 180 and reduce speed to 250",
        include_trace=True,
    )

    assert "trace" in out
    trace = out["trace"]
    assert isinstance(trace, list)
    assert len(trace) >= 4

    stages = [event["stage"] for event in trace]
    assert "ingest" in stages
    assert "normalize" in stages
    assert "segment" in stages
    assert "finalize" in stages


def test_parse_trace_finalize_reflects_output_status() -> None:
    out = parse_utterance("hello aircraft how are you", include_trace=True)
    finalize = next(event for event in out["trace"] if event["stage"] == "finalize")
    assert finalize["status"] == out["status"]
    assert finalize["instruction_count"] == len(out["instructions"])


def test_trace_not_emitted_by_default() -> None:
    out = parse_utterance("AAL77 descend flight level 180")
    assert "trace" not in out
