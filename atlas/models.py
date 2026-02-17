from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Status = Literal["ok", "unknown", "ambiguous", "conflict"]


@dataclass(slots=True)
class Instruction:
    type: str
    action: str
    value: int | str | float | None
    unit: str | None = None
    condition: str | None = None
    update: Literal["new", "replace"] = "new"


@dataclass(slots=True)
class ParseResult:
    schema_version: str = "atlas.intent.v0.1"
    utterance_id: str | None = None
    speaker: str = "UNKNOWN"
    callsign: str | None = None
    instructions: list[Instruction] = field(default_factory=list)
    confidence: float = 0.0
    status: Status = "unknown"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "utterance_id": self.utterance_id,
            "speaker": self.speaker,
            "callsign": self.callsign,
            "instructions": [
                {
                    "type": item.type,
                    "action": item.action,
                    "value": item.value,
                    "unit": item.unit,
                    "condition": item.condition,
                    "update": item.update,
                }
                for item in self.instructions
            ],
            "confidence": round(self.confidence, 3),
            "status": self.status,
            "notes": self.notes,
        }
