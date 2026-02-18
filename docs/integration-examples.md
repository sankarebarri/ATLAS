# Integration Examples

## Minimal Single-Utterance Integration
Use when you only need immediate intent extraction.

```python
from atlas import parse_utterance

out = parse_utterance("AAL77 descend flight level 180")
if out["status"] == "ok":
    for item in out["instructions"]:
        print(item["type"], item["value"], item["unit"])
```

## Stateful Multi-Turn Integration
Use when instructions can be amended/cancelled across turns.

```python
from atlas import parse_turn_with_state
from atlas.sequence import SequenceState

state = SequenceState()
turn1 = parse_turn_with_state("AAL77 descend flight level 180", state=state)
turn2 = parse_turn_with_state("AAL77 correction descend flight level 150", state=state)
active = state.active_by_callsign["AAL77"]
```

## Readback Mismatch Integration
Use for ATC-vs-pilot consistency checks.

```python
from atlas.evaluate import compare_readback

result = compare_readback(
    "AFR345 descend flight level 180",
    "AFR345 descend flight level 170",
)
if result["mismatch_detected"]:
    alert = {
        "callsign": result["callsign_expected"],
        "missing": result["missing_in_readback"],
        "unexpected": result["unexpected_in_readback"],
    }
```

## Integration Guardrails
- Treat `status in {"ambiguous", "conflict", "unknown"}` as non-automatable.
- Persist `notes` and instruction `trace` for auditability.
- Require explicit policy for low-confidence outputs.

## Runnable Example
Execute the end-to-end example consumer:

```bash
python docs/integration/downstream_consumer_example.py
```

This script outputs:
- parsed turns
- final active sequence state
- readback mismatch check payload
