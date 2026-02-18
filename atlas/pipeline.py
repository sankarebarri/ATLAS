from __future__ import annotations

from atlas.models import ParseResult
from atlas.normalize import normalize_callsign, normalize_text
from atlas.parse import parse_instruction
from atlas.segment import split_instructions
from atlas.validate import apply_confidence_policy, confidence_tier, detect_conflict, score_confidence


def parse_utterance(text: str, speaker: str = "ATC", utterance_id: str | None = None) -> dict:
    result = ParseResult(utterance_id=utterance_id, speaker=speaker)

    normalized = normalize_text(text)
    result.callsign = normalize_callsign(normalized)
    correction_mode = "CORRECTION" in normalized
    if correction_mode:
        result.notes.append("amendment_detected")

    instructions = []
    for segment in split_instructions(normalized):
        segment_items = parse_instruction(segment, correction_mode=correction_mode)
        instructions.extend(segment_items)

    result.instructions = instructions

    if not instructions:
        result.status = "unknown"
        result.confidence = 0.0
        result.confidence_tier = confidence_tier(result.confidence)
        result.notes.append(f"confidence_tier:{result.confidence_tier}")
        return result.to_dict()

    if detect_conflict(instructions):
        result.status = "conflict"
        result.confidence = 0.3
        result.confidence_tier = confidence_tier(result.confidence)
        result.notes.append(f"confidence_tier:{result.confidence_tier}")
        result.notes.append("slot_conflict_detected")
        return result.to_dict()

    result.confidence = score_confidence(instructions, has_callsign=result.callsign is not None)
    result.status = "ok"
    result.status, policy_notes, result.confidence_tier = apply_confidence_policy(
        status=result.status,
        confidence=result.confidence,
    )
    result.notes.extend(policy_notes)
    return result.to_dict()
