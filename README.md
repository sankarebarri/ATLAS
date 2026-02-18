# ATLAS
Air Traffic Language Analysis System

ATLAS is a research-first system for converting ATC transcripts into structured, machine-readable operational intent.

## Purpose
ATC phraseology is compressed, safety-critical, and context-dependent. ATLAS focuses on deterministic, auditable language parsing so downstream systems can reason over clearances, restrictions, and readbacks.

## Current Status
This repository now includes:
- phase-0 docs (`docs/contracts`, glossary, phraseology conventions)
- deterministic baseline parser skeleton
- support for callsign extraction and these instruction types:
  - altitude
  - speed
  - heading
  - frequency
  - runway
  - waypoint
  - squawk
  - hold
  - direct
  - climb_rate
- explicit fallback statuses (`ok`, `unknown`, `conflict`)
- amendment detection for `correction` utterances

## Scope (v0)
- Text transcripts first. Audio ingestion comes later.
- English ICAO/FAA-aligned phraseology.
- High-frequency instruction classes before long-tail coverage.
- Single-utterance parsing first, multi-turn context second.

## Non-Goals (v0)
- Operational ATC automation or certified decision authority.
- End-to-end speech recognition.
- Full trajectory conflict prediction.

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

Run a parse:
```bash
python -m atlas.cli "Air France 345, descend flight level 180, reduce speed to 250 knots"
```

Run evaluation on the gold slice:
```bash
python -m atlas.evaluate --dataset data/gold/v0_slice.jsonl
```

## Core Pipeline
`ingest -> normalize -> segment -> parse -> validate -> export`

## Output Contract
See `docs/contracts/atlas.intent.v0.1.md`.

## Example Output
```json
{
  "schema_version": "atlas.intent.v0.1",
  "utterance_id": null,
  "speaker": "ATC",
  "callsign": "AFR345",
  "instructions": [
    {
      "type": "altitude",
      "action": "descend",
      "value": 180,
      "unit": "FL",
      "condition": null,
      "update": "new"
    },
    {
      "type": "speed",
      "action": "reduce",
      "value": 250,
      "unit": "kt",
      "condition": null,
      "update": "new"
    }
  ],
  "confidence": 0.74,
  "status": "ok",
  "notes": []
}
```

## Evaluation Priorities
- intent precision/recall/F1
- slot extraction F1
- readback mismatch detection quality
- severity-weighted error tracking for high-risk intents
- calibration and threshold behavior under ASR noise

## Safety and Limitations
- Research/prototype component, not certified ATM software.
- Low-confidence outputs must not be promoted without fallback policy.
- Performance depends on transcript quality and phraseology coverage.
- Regional procedures and non-standard phraseology require targeted tests.

## Project Roadmap
Execution milestones are in `roadmap.md`.

## Contributor Guide
Daily development workflow and push checklist are in `documentation.md`.
