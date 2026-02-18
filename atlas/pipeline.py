from __future__ import annotations

from atlas.disambiguate import hybrid_disambiguate_segment
from atlas.models import ParseResult
from atlas.normalize import normalize_callsign, normalize_text
from atlas.observability import build_parse_trace
from atlas.parse import parse_instruction
from atlas.segment import split_instructions
from atlas.trace_log import append_trace_jsonl
from atlas.validate import apply_confidence_policy, confidence_tier, detect_conflict, score_confidence


def parse_utterance(
    text: str,
    speaker: str = "ATC",
    utterance_id: str | None = None,
    enable_hybrid: bool = True,
    include_trace: bool = False,
    trace_log_path: str | None = None,
) -> dict:
    result = ParseResult(utterance_id=utterance_id, speaker=speaker)

    normalized = normalize_text(text)
    result.callsign = normalize_callsign(normalized)
    correction_mode = "CORRECTION" in normalized
    if correction_mode:
        result.notes.append("amendment_detected")

    segments = split_instructions(normalized)
    parsed_by_segment = [parse_instruction(segment, correction_mode=correction_mode) for segment in segments]

    explicit_altitude_context = any(
        instr.type == "altitude" and instr.action in {"climb", "descend"}
        for segment_items in parsed_by_segment
        for instr in segment_items
    )

    instructions = []
    for segment, segment_items in zip(segments, parsed_by_segment, strict=True):
        if not enable_hybrid:
            instructions.extend(segment_items)
            continue

        resolved_items, hybrid_notes = hybrid_disambiguate_segment(
            segment,
            segment_items,
            correction_mode=correction_mode,
            explicit_altitude_context=explicit_altitude_context,
        )
        instructions.extend(resolved_items)
        result.notes.extend(hybrid_notes)

    result.instructions = instructions

    def export_result() -> dict:
        output = result.to_dict()
        should_build_trace = include_trace or trace_log_path is not None
        trace_payload = None
        if should_build_trace:
            trace_payload = build_parse_trace(
                utterance_id=utterance_id,
                speaker=speaker,
                raw_text=text,
                normalized_text=normalized,
                segments=segments,
                parsed_by_segment=[
                    [
                        {
                            "type": item.type,
                            "action": item.action,
                            "value": item.value,
                            "unit": item.unit,
                        }
                        for item in segment_items
                    ]
                    for segment_items in parsed_by_segment
                ],
                output=output,
            )
        if include_trace and trace_payload is not None:
            output["trace"] = trace_payload
        if trace_log_path is not None and trace_payload is not None:
            append_trace_jsonl(
                trace_log_path,
                {
                    "utterance_id": utterance_id,
                    "speaker": speaker,
                    "text": text,
                    "status": output.get("status"),
                    "confidence": output.get("confidence"),
                    "confidence_tier": output.get("confidence_tier"),
                    "callsign": output.get("callsign"),
                    "notes": output.get("notes", []),
                    "trace": trace_payload,
                },
            )
        return output

    if not instructions:
        result.status = "unknown"
        result.confidence = 0.0
        result.confidence_tier = confidence_tier(result.confidence)
        result.notes.append(f"confidence_tier:{result.confidence_tier}")
        return export_result()

    if detect_conflict(instructions):
        result.status = "conflict"
        result.confidence = 0.3
        result.confidence_tier = confidence_tier(result.confidence)
        result.notes.append(f"confidence_tier:{result.confidence_tier}")
        result.notes.append("slot_conflict_detected")
        return export_result()

    result.confidence = score_confidence(instructions, has_callsign=result.callsign is not None)
    result.status = "ok"
    result.status, policy_notes, result.confidence_tier = apply_confidence_policy(
        status=result.status,
        confidence=result.confidence,
    )
    result.notes.extend(policy_notes)
    return export_result()
