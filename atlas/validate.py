from __future__ import annotations

from atlas.models import Instruction


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
