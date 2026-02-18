from __future__ import annotations

from atlas.models import Instruction

CONFIDENCE_POLICY = {
    "high_threshold": 0.85,
    "medium_threshold": 0.60,
    "min_operational_threshold": 0.60,
}


def detect_conflict(instructions: list[Instruction]) -> bool:
    altitude_values = {
        instr.value
        for instr in instructions
        if instr.type == "altitude" and instr.action in {"maintain", "descend", "climb"}
    }
    if len(altitude_values) > 1:
        return True

    speed_values = {instr.value for instr in instructions if instr.type == "speed"}
    if len(speed_values) > 1:
        return True

    return False


def score_confidence(instructions: list[Instruction], has_callsign: bool) -> float:
    if not instructions:
        return 0.0
    base = min(0.45 + 0.12 * len(instructions), 0.92)
    if has_callsign:
        base += 0.05
    return min(base, 0.99)


def confidence_tier(score: float) -> str:
    if score >= CONFIDENCE_POLICY["high_threshold"]:
        return "high"
    if score >= CONFIDENCE_POLICY["medium_threshold"]:
        return "medium"
    return "low"


def apply_confidence_policy(status: str, confidence: float) -> tuple[str, list[str], str]:
    tier = confidence_tier(confidence)
    notes: list[str] = [f"confidence_tier:{tier}"]

    if status == "ok" and confidence < CONFIDENCE_POLICY["min_operational_threshold"]:
        notes.append("low_confidence_threshold_breach")
        return "ambiguous", notes, tier
    return status, notes, tier
