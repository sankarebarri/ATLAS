from __future__ import annotations

import re

from atlas.models import Instruction


MAINTAIN_GENERIC_PATTERN = re.compile(r"\bMAINTAIN\s+(\d{2,3})\b")


def _ml_assist_type(value: int) -> tuple[str, float]:
    """Simple numeric prior as a stand-in for ML assist."""
    speed_score = 0.45
    altitude_score = 0.45

    if value <= 260:
        speed_score += 0.35
    elif value >= 290:
        altitude_score += 0.35
    else:
        speed_score += 0.15
        altitude_score += 0.15

    if value <= 220:
        speed_score += 0.1
    if value >= 320:
        altitude_score += 0.1

    if speed_score >= altitude_score:
        return "speed", round(speed_score, 3)
    return "altitude", round(altitude_score, 3)


def _resolved_instruction(
    *,
    chosen_type: str,
    value: int,
    segment: str,
    mode: str,
    correction_mode: bool,
) -> Instruction:
    if chosen_type == "speed":
        return Instruction(
            type="speed",
            action="maintain",
            value=value,
            unit="kt",
            update="replace" if correction_mode else "new",
            trace={
                "rule": "hybrid_disambiguation",
                "pattern": MAINTAIN_GENERIC_PATTERN.pattern,
                "segment": segment,
                "resolution_mode": mode,
                "selected_type": "speed",
                "candidate_types": "speed|altitude",
            },
        )

    return Instruction(
        type="altitude",
        action="maintain",
        value=value,
        unit="FL",
        update="replace" if correction_mode else "new",
        trace={
            "rule": "hybrid_disambiguation",
            "pattern": MAINTAIN_GENERIC_PATTERN.pattern,
            "segment": segment,
            "resolution_mode": mode,
            "selected_type": "altitude",
            "candidate_types": "speed|altitude",
        },
    )


def hybrid_disambiguate_segment(
    segment: str,
    segment_items: list[Instruction],
    *,
    correction_mode: bool = False,
    explicit_altitude_context: bool = False,
) -> tuple[list[Instruction], list[str]]:
    match = MAINTAIN_GENERIC_PATTERN.search(segment)
    if not match:
        return segment_items, []

    value = int(match.group(1))

    should_apply = not segment_items or (
        len(segment_items) == 1
        and segment_items[0].type == "altitude"
        and segment_items[0].action == "maintain"
        and segment_items[0].trace.get("rule") == "altitude"
    )
    if not should_apply:
        return segment_items, []

    notes = ["hybrid_disambiguation_applied"]

    if re.search(r"\b(SPEED|KNOT|KNOTS|KT)\b", segment):
        chosen_type = "speed"
        mode = "rules"
    elif re.search(r"\b(FLIGHT LEVEL|LEVEL|FL\d{2,3})\b", segment):
        chosen_type = "altitude"
        mode = "rules"
    elif explicit_altitude_context:
        chosen_type = "altitude"
        mode = "rules"
        notes.append("hybrid_context_bias:altitude")
    else:
        chosen_type, assist_score = _ml_assist_type(value)
        mode = "ml_assist"
        notes.append(f"hybrid_ml_assist:{chosen_type}:{assist_score}")

    return [
        _resolved_instruction(
            chosen_type=chosen_type,
            value=value,
            segment=segment,
            mode=mode,
            correction_mode=correction_mode,
        )
    ], notes
