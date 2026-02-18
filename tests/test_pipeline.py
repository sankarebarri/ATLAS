from atlas.pipeline import parse_utterance


def test_parses_altitude_and_speed_with_callsign() -> None:
    out = parse_utterance("Air France 345 descend flight level 180, reduce speed to 250 knots")
    assert out["callsign"] == "AFR345"
    assert out["status"] == "ok"
    assert [item["type"] for item in out["instructions"]] == ["altitude", "speed"]


def test_parses_heading_frequency_and_runway() -> None:
    out = parse_utterance("UAL12 turn left heading 270 and contact 121.5 runway 27L")
    assert out["callsign"] == "UAL12"
    assert out["status"] == "ok"
    types = {item["type"] for item in out["instructions"]}
    assert {"heading", "frequency", "runway"}.issubset(types)


def test_detects_conflict_for_multiple_altitudes() -> None:
    out = parse_utterance("AAL77 maintain 190 and descend 150")
    assert out["status"] == "conflict"
    assert "slot_conflict_detected" in out["notes"]


def test_marks_correction_as_replace() -> None:
    out = parse_utterance("Speedbird 42 correction maintain 190 until LAM then descend 150")
    assert out["callsign"] == "BAW42"
    assert out["status"] == "conflict"
    assert "amendment_detected" in out["notes"]
    assert all(item["update"] == "replace" for item in out["instructions"])


def test_unknown_when_no_supported_intent() -> None:
    out = parse_utterance("Hello aircraft how are you")
    assert out["status"] == "unknown"
    assert out["instructions"] == []


def test_parses_direct_waypoint_instruction() -> None:
    out = parse_utterance("DAL220 proceed direct LAM")
    assert out["status"] == "ok"
    waypoint = next(item for item in out["instructions"] if item["type"] == "waypoint")
    assert waypoint["action"] == "direct"
    assert waypoint["value"] == "LAM"


def test_parses_squawk_instruction() -> None:
    out = parse_utterance("UAL13 squawk 4721")
    assert out["status"] == "ok"
    squawk = next(item for item in out["instructions"] if item["type"] == "squawk")
    assert squawk["action"] == "assign"
    assert squawk["value"] == "4721"
