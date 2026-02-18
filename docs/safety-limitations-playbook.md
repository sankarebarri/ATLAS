# Safety and Limitations Playbook

## Operational Position
ATLAS is a research/parser component and not a certified ATM decision authority.

## Failure Handling Policy
- `ok`: can be consumed with normal downstream checks.
- `ambiguous`: require human review or conservative fallback.
- `conflict`: block automation and escalate.
- `unknown`: no actionable extraction; request clarification.

## Mandatory Safeguards
- Never execute operational control actions from `ambiguous/conflict/unknown` outputs.
- Log `notes` and `trace` with each consumed instruction.
- Apply confidence thresholds before downstream actioning.
- Keep deterministic and hybrid eval baselines in CI.

## Known Limitations
- Phraseology coverage is limited to current supported intent classes.
- Performance depends on transcript quality and normalization rules.
- Non-English or region-specific variants may degrade extraction quality.
- Temporal/context support is limited to currently modeled patterns.

## Incident Response Pattern
1. Capture raw utterance and parser output.
2. Classify by `status` and `notes`.
3. Compare with gold-style expected payload.
4. Add regression case to `data/gold/`.
5. Patch parser/rules and rerun full evaluation.

## Safety Review Command
Run an explicit safety review over a labeled dataset:

```bash
python -m atlas.evaluate --safety-dataset data/gold/v0_noisy_slice.jsonl
```

Safety report includes:
- policy conformance violations (fallback/status-policy checks)
- fallback behavior distribution (`ok/unknown/ambiguous/conflict`)
- non-`ok` failure-mode detection recall against expected labels

## Safety Gate (CI)
Use the strict gate to fail on safety regressions:

```bash
python -m atlas.safety_review --dataset data/gold/v0_noisy_slice.jsonl --min-non-ok-recall 1.0 --max-violations 0 --max-blocking-status-rate 0.25 --baseline-safety-json data/gold/safety_baseline.noisy.json --max-blocking-rate-delta 0.05
```
