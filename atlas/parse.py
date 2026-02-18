from __future__ import annotations

import re

from atlas.models import Instruction


ALTITUDE_PATTERNS = [
    re.compile(r"\b(DESCEND|CLIMB|MAINTAIN)\b\s+(?:FLIGHT LEVEL\s+)?(\d{2,3})\b"),
]
SPEED_PATTERN = re.compile(r"\b(REDUCE|MAINTAIN|INCREASE)\s+SPEED\s+(?:TO\s+)?(\d{2,3})\b")
HEADING_PATTERN = re.compile(r"\b(?:TURN\s+(LEFT|RIGHT)\s+)?HEADING\s+(\d{2,3})\b")
FREQ_PATTERN = re.compile(r"\b(?:CONTACT|MONITOR)\s+([0-9]{3}\.[0-9]{1,3})\b")
RUNWAY_PATTERN = re.compile(r"\b(?:CLEARED\s+)?(?:ILS\s+)?(?:APPROACH\s+)?RUNWAY\s+([0-9]{1,2}[LRC]?)\b")
WAYPOINT_PATTERN = re.compile(r"\b(?:PROCEED\s+TO|REPORT\s+OVER|CROSS)\s+([A-Z]{2,6})\b")
DIRECT_PATTERN = re.compile(r"\b(?:DIRECT|PROCEED\s+DIRECT)\s+([A-Z]{2,6})\b")
SQUAWK_PATTERN = re.compile(r"\bSQUAWK\s+([0-7]{4})\b")
HOLD_PATTERN = re.compile(r"\bHOLD(?:\s+AT)?\s+([A-Z]{2,6})\b")
CLIMB_RATE_PATTERN = re.compile(r"\b(CLIMB|DESCEND)\s+AT\s+(\d{3,4})\s*(?:FEET PER MINUTE|FPM)\b")
UNTIL_PATTERN = re.compile(r"\bUNTIL\s+([A-Z0-9]+)\b")


def parse_instruction(segment: str, correction_mode: bool = False) -> list[Instruction]:
    found: list[Instruction] = []

    condition = None
    until_match = UNTIL_PATTERN.search(segment)
    if until_match:
        condition = f"until {until_match.group(1)}"

    for pattern in ALTITUDE_PATTERNS:
        match = pattern.search(segment)
        if match:
            action = match.group(1).lower()
            value = int(match.group(2))
            found.append(
                Instruction(
                    type="altitude",
                    action=action,
                    value=value,
                    unit="FL",
                    condition=condition,
                    update="replace" if correction_mode else "new",
                )
            )

    speed_match = SPEED_PATTERN.search(segment)
    if speed_match:
        found.append(
            Instruction(
                type="speed",
                action=speed_match.group(1).lower(),
                value=int(speed_match.group(2)),
                unit="kt",
                update="replace" if correction_mode else "new",
            )
        )

    heading_match = HEADING_PATTERN.search(segment)
    if heading_match:
        turn = heading_match.group(1).lower() if heading_match.group(1) else "maintain"
        found.append(
            Instruction(
                type="heading",
                action=turn,
                value=int(heading_match.group(2)),
                unit="deg",
                update="replace" if correction_mode else "new",
            )
        )

    freq_match = FREQ_PATTERN.search(segment)
    if freq_match:
        found.append(
            Instruction(
                type="frequency",
                action="contact",
                value=float(freq_match.group(1)),
                unit="MHz",
                update="replace" if correction_mode else "new",
            )
        )

    runway_match = RUNWAY_PATTERN.search(segment)
    if runway_match:
        found.append(
            Instruction(
                type="runway",
                action="assign",
                value=runway_match.group(1),
                unit=None,
                update="replace" if correction_mode else "new",
            )
        )

    direct_match = DIRECT_PATTERN.search(segment)
    if direct_match:
        found.append(
            Instruction(
                type="direct",
                action="direct",
                value=direct_match.group(1),
                unit=None,
                update="replace" if correction_mode else "new",
            )
        )

    waypoint_match = WAYPOINT_PATTERN.search(segment)
    if waypoint_match:
        found.append(
            Instruction(
                type="waypoint",
                action="navigate",
                value=waypoint_match.group(1),
                unit=None,
                update="replace" if correction_mode else "new",
            )
        )

    squawk_match = SQUAWK_PATTERN.search(segment)
    if squawk_match:
        found.append(
            Instruction(
                type="squawk",
                action="assign",
                value=squawk_match.group(1),
                unit="octal",
                update="replace" if correction_mode else "new",
            )
        )

    hold_match = HOLD_PATTERN.search(segment)
    if hold_match:
        found.append(
            Instruction(
                type="hold",
                action="hold",
                value=hold_match.group(1),
                unit=None,
                update="replace" if correction_mode else "new",
            )
        )

    climb_rate_match = CLIMB_RATE_PATTERN.search(segment)
    if climb_rate_match:
        found.append(
            Instruction(
                type="climb_rate",
                action=climb_rate_match.group(1).lower(),
                value=int(climb_rate_match.group(2)),
                unit="fpm",
                update="replace" if correction_mode else "new",
            )
        )

    return found
