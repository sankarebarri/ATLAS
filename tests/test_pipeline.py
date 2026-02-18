from atlas.pipeline import parse_utterance


def test_parses_altitude_and_speed_with_callsign() -> None:
    out = parse_utterance("Air France 345 descend flight level 180, reduce speed to 250 knots")
    assert out["callsign"] == "AFR345"
    assert out["status"] == "ok"
    assert [item["type"] for item in out["instructions"]] == ["altitude", "speed"]
    for item in out["instructions"]:
        assert item["trace"]["rule"] == item["type"]
        assert item["trace"]["segment"]
        assert item["trace"]["pattern"]


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
    direct = next(item for item in out["instructions"] if item["type"] == "direct")
    assert direct["action"] == "direct"
    assert direct["value"] == "LAM"


def test_parses_squawk_instruction() -> None:
    out = parse_utterance("UAL13 squawk 4721")
    assert out["status"] == "ok"
    squawk = next(item for item in out["instructions"] if item["type"] == "squawk")
    assert squawk["action"] == "assign"
    assert squawk["value"] == "4721"


def test_parses_waypoint_hold_and_climb_rate() -> None:
    out = parse_utterance("AAL22 proceed to DINKY and hold at DINKY and climb at 1800 fpm")
    assert out["status"] == "ok"
    types = {item["type"] for item in out["instructions"]}
    assert {"waypoint", "hold", "climb_rate"}.issubset(types)


def test_noisy_spoken_callsign_and_altitude() -> None:
    out = parse_utterance("air france three four five descend flight level one eight zero")
    assert out["callsign"] == "AFR345"
    altitude = next(item for item in out["instructions"] if item["type"] == "altitude")
    assert altitude["value"] == 180


def test_noisy_spoken_frequency_and_runway() -> None:
    out = parse_utterance("United 521 contact one two one decimal five runway two seven right")
    types = {item["type"] for item in out["instructions"]}
    assert {"frequency", "runway"}.issubset(types)
    runway = next(item for item in out["instructions"] if item["type"] == "runway")
    assert runway["value"] == "27R"


def test_noisy_spoken_squawk_and_rate() -> None:
    out = parse_utterance("AAL505 squawk seven thousand and DAL777 climb at fourteen hundred fpm")
    squawk = next(item for item in out["instructions"] if item["type"] == "squawk")
    assert squawk["value"] == "7000"
    rate = next(item for item in out["instructions"] if item["type"] == "climb_rate")
    assert rate["value"] == 1400
