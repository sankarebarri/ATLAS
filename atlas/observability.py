from __future__ import annotations

import time
from typing import Any


def build_parse_trace(
    *,
    utterance_id: str | None,
    speaker: str,
    raw_text: str,
    normalized_text: str,
    segments: list[str],
    parsed_by_segment: list[list[dict[str, Any]]],
    output: dict[str, Any],
) -> list[dict[str, Any]]:
    start = time.perf_counter()
    events: list[dict[str, Any]] = []

    def add(stage: str, payload: dict[str, Any]) -> None:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        events.append(
            {
                "stage": stage,
                "t_ms": round(elapsed_ms, 3),
                **payload,
            }
        )

    add(
        "ingest",
        {
            "utterance_id": utterance_id,
            "speaker": speaker,
            "raw_text_length": len(raw_text),
        },
    )
    add(
        "normalize",
        {
            "normalized_text": normalized_text,
            "callsign": output.get("callsign"),
            "correction_mode": "amendment_detected" in output.get("notes", []),
            "segment_count": len(segments),
        },
    )

    for idx, (segment, parsed_items) in enumerate(zip(segments, parsed_by_segment, strict=True), start=1):
        add(
            "segment",
            {
                "index": idx,
                "segment": segment,
                "parsed_instruction_count": len(parsed_items),
                "parsed_instruction_types": [item.get("type") for item in parsed_items],
            },
        )

    add(
        "finalize",
        {
            "status": output.get("status"),
            "confidence": output.get("confidence"),
            "confidence_tier": output.get("confidence_tier"),
            "instruction_count": len(output.get("instructions", [])),
            "note_count": len(output.get("notes", [])),
        },
    )
    return events
