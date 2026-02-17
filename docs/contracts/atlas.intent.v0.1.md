# atlas.intent.v0.1

## Purpose
`atlas.intent.v0.1` defines a deterministic, auditable intent payload for ATC transcript parsing.

## Top-level contract
```json
{
  "schema_version": "atlas.intent.v0.1",
  "utterance_id": "optional-id",
  "speaker": "ATC",
  "callsign": "AFR345",
  "instructions": [],
  "confidence": 0.96,
  "status": "ok",
  "notes": []
}
```

## Fields
- `schema_version` (`string`, required): must equal `atlas.intent.v0.1`
- `utterance_id` (`string`, optional): upstream identifier
- `speaker` (`string`, required): `ATC`, `PILOT`, or `UNKNOWN`
- `callsign` (`string|null`, required): normalized callsign or `null`
- `instructions` (`array`, required): ordered list of structured instructions
- `confidence` (`number`, required): 0.0 to 1.0 confidence score
- `status` (`string`, required): one of `ok`, `unknown`, `ambiguous`, `conflict`
- `notes` (`array[string]`, optional): parse notes/warnings

## Instruction object
```json
{
  "type": "altitude",
  "action": "descend",
  "value": 180,
  "unit": "FL",
  "condition": null,
  "update": "new"
}
```

## Canonical instruction classes (v0)
1. `altitude`
2. `speed`
3. `heading`
4. `frequency`
5. `runway`
6. `waypoint`
7. `squawk`
8. `hold`
9. `direct`
10. `climb_rate`

## Status policy
- `ok`: parse yielded at least one unambiguous instruction
- `unknown`: no supported intent recognized
- `ambiguous`: multiple competing parses with no deterministic tie-break
- `conflict`: explicit contradiction detected in same utterance

## Examples
### Example 1: altitude + speed
```json
{
  "schema_version": "atlas.intent.v0.1",
  "speaker": "ATC",
  "callsign": "AFR345",
  "instructions": [
    {"type": "altitude", "action": "descend", "value": 180, "unit": "FL", "condition": null, "update": "new"},
    {"type": "speed", "action": "reduce", "value": 250, "unit": "kt", "condition": null, "update": "new"}
  ],
  "confidence": 0.96,
  "status": "ok",
  "notes": []
}
```

### Example 2: correction handling
```json
{
  "schema_version": "atlas.intent.v0.1",
  "speaker": "ATC",
  "callsign": "BAW42",
  "instructions": [
    {"type": "altitude", "action": "maintain", "value": 190, "unit": "FL", "condition": "until LAM", "update": "replace"},
    {"type": "altitude", "action": "descend", "value": 150, "unit": "FL", "condition": "then", "update": "new"}
  ],
  "confidence": 0.87,
  "status": "ok",
  "notes": ["amendment_detected"]
}
```
