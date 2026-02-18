# ATLAS Examples

## Minimal Example
Input:
`AAL77 descend flight level 180`

Expected core output:
- `callsign: AAL77`
- `status: ok`
- one `altitude` instruction with `value: 180`, `unit: FL`

## Realistic Controller Sequence Example
Turns:
1. `AAL77 descend flight level 180`
2. `AAL77 correction descend flight level 150`
3. `AAL77 until LAM`

Expected state behavior:
- turn 2 replaces active altitude to `150`
- turn 3 applies temporal condition `until LAM` to active altitude
- final active slot is altitude `150 FL` with `condition: until LAM`

## Ambiguous Maintain Example
Input:
`AAL77 maintain 250`

Behavior:
- deterministic rule is ambiguous in isolation
- hybrid layer resolves to `speed` (`250 kt`)
- notes include hybrid disambiguation metadata

## Readback Mismatch Example
ATC:
`AFR345 descend flight level 180`

Pilot:
`AFR345 descend flight level 170`

Mismatch result:
- `mismatch_detected: true`
- one missing expected altitude slot in readback
