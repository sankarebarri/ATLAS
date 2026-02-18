from __future__ import annotations

import re
from dataclasses import dataclass, field

from atlas.normalize import normalize_text
from atlas.pipeline import parse_utterance
from atlas.validate import confidence_tier

CANCEL_TYPE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bCANCEL\s+SPEED\b"), "speed"),
    (re.compile(r"\bCANCEL\s+ALTITUDE\b"), "altitude"),
    (re.compile(r"\bCANCEL\s+(?:FLIGHT\s+)?LEVEL\b"), "altitude"),
    (re.compile(r"\bCANCEL\s+HEADING\b"), "heading"),
    (re.compile(r"\bCANCEL\s+HOLD\b"), "hold"),
    (re.compile(r"\bCANCEL\s+DIRECT\b"), "direct"),
    (re.compile(r"\bCANCEL\s+SQUAWK\b"), "squawk"),
    (re.compile(r"\bCANCEL\s+FREQUENCY\b"), "frequency"),
    (re.compile(r"\bCANCEL\s+RUNWAY\b"), "runway"),
]


@dataclass(slots=True)
class SequenceState:
    active_by_callsign: dict[str, dict[str, dict]] = field(default_factory=dict)
    history_by_callsign: dict[str, list[dict]] = field(default_factory=dict)
    last_callsign: str | None = None


def _extract_cancel_targets(normalized_text: str) -> list[str] | None:
    if "CANCEL" not in normalized_text:
        return None

    targets = [intent_type for pattern, intent_type in CANCEL_TYPE_PATTERNS if pattern.search(normalized_text)]
    if targets:
        return sorted(set(targets))

    # Bare cancel defaults to clearing all active instructions for the callsign.
    return []


def _has_temporal_link(normalized_text: str) -> bool:
    return bool(re.search(r"\b(THEN|AFTER|UNTIL)\b", normalized_text))


def _extract_temporal_condition(normalized_text: str) -> str | None:
    if normalized_text.startswith("THEN "):
        return "then"

    after_match = re.search(r"\bAFTER\s+([A-Z0-9]+)\b", normalized_text)
    if after_match:
        return f"after {after_match.group(1)}"

    until_match = re.search(r"\bUNTIL\s+([A-Z0-9]+)\b", normalized_text)
    if until_match:
        return f"until {until_match.group(1)}"

    return None


def _apply_temporal_condition(result: dict, temporal_condition: str, active: dict[str, dict]) -> None:
    instructions = result.get("instructions", [])
    if instructions:
        applied = False
        for instruction in instructions:
            if not instruction.get("condition"):
                instruction["condition"] = temporal_condition
                applied = True
        if applied:
            result["notes"].append(f"temporal_condition_applied:{temporal_condition}")
        return

    if not active:
        return

    for slot in active.values():
        slot["condition"] = temporal_condition
    result["notes"].append(f"temporal_condition_applied_to_active:{temporal_condition}")


def parse_turn_with_state(
    text: str,
    *,
    state: SequenceState,
    speaker: str = "ATC",
    utterance_id: str | None = None,
    enable_hybrid: bool = True,
) -> dict:
    normalized = normalize_text(text)
    result = parse_utterance(
        text,
        speaker=speaker,
        utterance_id=utterance_id,
        enable_hybrid=enable_hybrid,
    )

    if result.get("callsign") is None and result.get("instructions") and state.last_callsign:
        result["callsign"] = state.last_callsign
        result["notes"].append("callsign_inherited_from_context")
        if result.get("status") == "ambiguous" and "low_confidence_threshold_breach" in result.get("notes", []):
            result["status"] = "ok"
            result["confidence"] = max(float(result.get("confidence", 0.0)), 0.6)
            result["confidence_tier"] = confidence_tier(float(result["confidence"]))
            result["notes"].append("context_confidence_recovery")

    callsign = result.get("callsign")

    temporal_condition = _extract_temporal_condition(normalized)
    if _has_temporal_link(normalized):
        result["notes"].append("temporal_link_detected")

    if not callsign:
        return result

    state.last_callsign = callsign

    active = state.active_by_callsign.setdefault(callsign, {})
    history = state.history_by_callsign.setdefault(callsign, [])

    cancel_targets = _extract_cancel_targets(normalized)
    if cancel_targets is not None:
        if cancel_targets:
            for target in cancel_targets:
                if target in active:
                    del active[target]
                result["notes"].append(f"cancellation_applied:{target}")
        else:
            active.clear()
            result["notes"].append("cancellation_applied:all")

    if temporal_condition:
        _apply_temporal_condition(result, temporal_condition, active)

    contradictions: list[str] = []
    correction_mode = "amendment_detected" in result.get("notes", [])

    for instruction in result.get("instructions", []):
        prev = active.get(instruction["type"])
        if (
            prev
            and prev.get("value") != instruction.get("value")
            and not correction_mode
            and instruction.get("update") != "replace"
        ):
            contradictions.append(instruction["type"])

        active[instruction["type"]] = {
            "type": instruction.get("type"),
            "action": instruction.get("action"),
            "value": instruction.get("value"),
            "unit": instruction.get("unit"),
            "condition": instruction.get("condition"),
            "utterance_id": result.get("utterance_id"),
        }

    if contradictions:
        uniq = sorted(set(contradictions))
        result["notes"].append("history_conflict_detected")
        for slot_type in uniq:
            result["notes"].append(f"history_conflict:{slot_type}")
        if result.get("status") == "ok":
            result["status"] = "conflict"
            result["confidence"] = min(float(result.get("confidence", 0.0)), 0.4)
            result["confidence_tier"] = confidence_tier(float(result["confidence"]))

    history.append(result)
    return result


def parse_sequence(
    utterances: list[str],
    *,
    speaker: str = "ATC",
    enable_hybrid: bool = True,
) -> dict:
    state = SequenceState()
    turns = [
        parse_turn_with_state(
            utterance,
            state=state,
            speaker=speaker,
            utterance_id=f"turn-{idx + 1:04d}",
            enable_hybrid=enable_hybrid,
        )
        for idx, utterance in enumerate(utterances)
    ]

    return {
        "turns": turns,
        "state": {
            "active_by_callsign": state.active_by_callsign,
            "last_callsign": state.last_callsign,
        },
    }
