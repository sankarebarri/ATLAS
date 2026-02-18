from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from atlas.normalize import normalize_text

VALID_STATUSES = {"ok", "unknown", "ambiguous", "conflict"}
CALLSIGN_PATTERN = re.compile(r"^[A-Z]{3}\d{1,4}$")
RUNWAY_PATTERN = re.compile(r"^\d{1,2}[LRC]?$")
SQUAWK_PATTERN = re.compile(r"^[0-7]{4}$")


def _slot_counter(instructions: list[dict[str, Any]]) -> Counter[tuple[Any, ...]]:
    return Counter(
        (
            item.get("type"),
            item.get("action"),
            item.get("value"),
            item.get("unit"),
            item.get("condition"),
        )
        for item in instructions
    )


def _emit_issue(container: list[dict[str, Any]], row_id: str | None, field: str, message: str) -> None:
    container.append({"row_id": row_id, "field": field, "message": message})


def audit_gold_dataset(path: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    adjudication_items: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []

    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            _emit_issue(errors, None, "jsonl", f"invalid JSON at line {idx}: {exc.msg}")
            continue
        if not isinstance(payload, dict):
            _emit_issue(errors, None, "jsonl", f"line {idx} payload must be object")
            continue
        rows.append(payload)

    seen_ids: set[str] = set()
    norm_utterance_rows: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    for idx, row in enumerate(rows, start=1):
        row_id = row.get("id")
        if not row_id:
            _emit_issue(errors, None, "id", f"missing id at line {idx}")
        elif row_id in seen_ids:
            _emit_issue(errors, row_id, "id", "duplicate id")
        else:
            seen_ids.add(row_id)

        utterance = row.get("utterance")
        if not isinstance(utterance, str) or not utterance.strip():
            _emit_issue(errors, row_id, "utterance", "missing or empty utterance")
            continue

        expected = row.get("expected")
        if not isinstance(expected, dict):
            _emit_issue(errors, row_id, "expected", "missing expected object")
            continue

        status = expected.get("status")
        if status not in VALID_STATUSES:
            _emit_issue(errors, row_id, "expected.status", f"invalid status: {status}")

        callsign = expected.get("callsign")
        if callsign is not None and (not isinstance(callsign, str) or not CALLSIGN_PATTERN.match(callsign)):
            _emit_issue(warnings, row_id, "expected.callsign", f"non-canonical callsign format: {callsign}")

        instructions = expected.get("instructions")
        if not isinstance(instructions, list):
            _emit_issue(errors, row_id, "expected.instructions", "instructions must be a list")
            continue

        if status == "unknown" and instructions:
            _emit_issue(warnings, row_id, "expected.instructions", "unknown status should generally have empty instructions")

        for inst_idx, instruction in enumerate(instructions, start=1):
            if not isinstance(instruction, dict):
                _emit_issue(errors, row_id, "expected.instructions", f"instruction #{inst_idx} must be object")
                continue

            itype = instruction.get("type")
            action = instruction.get("action")
            if not isinstance(itype, str) or not itype:
                _emit_issue(errors, row_id, f"instruction[{inst_idx}].type", "missing type")
            if not isinstance(action, str) or not action:
                _emit_issue(errors, row_id, f"instruction[{inst_idx}].action", "missing action")

            value = instruction.get("value")
            unit = instruction.get("unit")

            if itype == "runway" and isinstance(value, str) and not RUNWAY_PATTERN.match(value):
                _emit_issue(warnings, row_id, f"instruction[{inst_idx}].value", f"non-standard runway value: {value}")
            if itype == "squawk" and isinstance(value, str) and not SQUAWK_PATTERN.match(value):
                _emit_issue(errors, row_id, f"instruction[{inst_idx}].value", f"invalid squawk code: {value}")
            if itype == "frequency" and isinstance(value, (float, int)):
                if not 100.0 <= float(value) <= 136.975:
                    _emit_issue(warnings, row_id, f"instruction[{inst_idx}].value", f"frequency out of typical range: {value}")
            if itype == "heading" and isinstance(value, int):
                if not 1 <= value <= 360:
                    _emit_issue(warnings, row_id, f"instruction[{inst_idx}].value", f"heading out of range: {value}")
            if itype == "altitude" and unit == "FL" and isinstance(value, int):
                if not 10 <= value <= 450:
                    _emit_issue(warnings, row_id, f"instruction[{inst_idx}].value", f"flight level out of range: {value}")
            if itype == "speed" and isinstance(value, int):
                if not 100 <= value <= 400:
                    _emit_issue(warnings, row_id, f"instruction[{inst_idx}].value", f"speed out of range: {value}")

        normalized_utt = normalize_text(utterance)
        norm_utterance_rows[normalized_utt].append(
            {
                "id": row_id,
                "status": status,
                "callsign": callsign,
                "slots": _slot_counter(instructions),
            }
        )

    for normalized_utt, grouped in norm_utterance_rows.items():
        if len(grouped) < 2:
            continue
        signatures = {(item["status"], item["callsign"], tuple(sorted(item["slots"].items()))) for item in grouped}
        if len(signatures) > 1:
            adjudication_items.append(
                {
                    "type": "label_conflict",
                    "normalized_utterance": normalized_utt,
                    "row_ids": [item["id"] for item in grouped],
                    "message": "same normalized utterance has conflicting expected labels",
                }
            )

    return {
        "dataset": str(path),
        "samples": len(rows),
        "errors": errors,
        "warnings": warnings,
        "adjudication_items": adjudication_items,
        "summary": {
            "error_count": len(errors),
            "warning_count": len(warnings),
            "adjudication_count": len(adjudication_items),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit ATLAS gold dataset quality and adjudication candidates")
    parser.add_argument("--dataset", default="data/gold/v0_slice.jsonl")
    args = parser.parse_args()

    report = audit_gold_dataset(Path(args.dataset))
    print(json.dumps(report, indent=2, sort_keys=False))

    if report["summary"]["error_count"] > 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
