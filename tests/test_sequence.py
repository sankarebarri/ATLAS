from atlas.sequence import SequenceState, parse_sequence, parse_turn_with_state


def test_sequence_amendment_replaces_prior_instruction() -> None:
    state = SequenceState()
    parse_turn_with_state("AAL77 descend flight level 180", state=state)
    second = parse_turn_with_state("AAL77 correction descend flight level 150", state=state)

    assert second["status"] == "ok"
    assert "amendment_detected" in second["notes"]
    assert state.active_by_callsign["AAL77"]["altitude"]["value"] == 150


def test_sequence_cancellation_removes_active_slot() -> None:
    state = SequenceState()
    parse_turn_with_state("AAL77 reduce speed to 250", state=state)
    second = parse_turn_with_state("AAL77 cancel speed restrictions", state=state)

    assert "cancellation_applied:speed" in second["notes"]
    assert "speed" not in state.active_by_callsign["AAL77"]


def test_sequence_detects_history_conflict_without_correction() -> None:
    state = SequenceState()
    parse_turn_with_state("AAL77 descend flight level 180", state=state)
    second = parse_turn_with_state("AAL77 descend flight level 160", state=state)

    assert second["status"] == "conflict"
    assert "history_conflict_detected" in second["notes"]
    assert "history_conflict:altitude" in second["notes"]


def test_sequence_inherits_callsign_for_temporal_followup() -> None:
    state = SequenceState()
    parse_turn_with_state("AAL77 hold at LAM", state=state)
    second = parse_turn_with_state("then descend flight level 120", state=state)

    assert second["callsign"] == "AAL77"
    assert "callsign_inherited_from_context" in second["notes"]
    assert "temporal_link_detected" in second["notes"]
    altitude = next(item for item in second["instructions"] if item["type"] == "altitude")
    assert altitude["condition"] == "then"
    assert "temporal_condition_applied:then" in second["notes"]


def test_sequence_applies_after_condition_to_new_instruction() -> None:
    state = SequenceState()
    parse_turn_with_state("AAL77 hold at LAM", state=state)
    second = parse_turn_with_state("AAL77 after LAM descend flight level 130", state=state)

    altitude = next(item for item in second["instructions"] if item["type"] == "altitude")
    assert altitude["condition"] == "after LAM"
    assert state.active_by_callsign["AAL77"]["altitude"]["condition"] == "after LAM"


def test_sequence_applies_until_condition_to_existing_active_slot() -> None:
    state = SequenceState()
    parse_turn_with_state("AAL77 reduce speed to 240", state=state)
    second = parse_turn_with_state("AAL77 until LAM", state=state)

    assert second["instructions"] == []
    assert "temporal_condition_applied_to_active:until LAM" in second["notes"]
    assert state.active_by_callsign["AAL77"]["speed"]["condition"] == "until LAM"


def test_parse_sequence_returns_state_snapshot() -> None:
    out = parse_sequence([
        "AAL77 descend flight level 180",
        "AAL77 correction descend flight level 150",
    ])

    assert len(out["turns"]) == 2
    assert out["state"]["active_by_callsign"]["AAL77"]["altitude"]["value"] == 150
