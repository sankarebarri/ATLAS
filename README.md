# ATLAS
Air Traffic Language Analysis System

ATLAS is a research-first system for converting ATC transcripts into structured, machine-readable operational intent.

## Purpose
ATC phraseology is compressed, safety-critical, and context-dependent. ATLAS focuses on deterministic, auditable language parsing so downstream systems can reason over clearances, restrictions, and readbacks.

## Scope (v0)
- Text transcripts first. Audio ingestion comes later.
- English ICAO/FAA-aligned phraseology.
- High-frequency instruction classes before long-tail coverage.
- Single-utterance parsing first, multi-turn context second.

## Non-Goals (v0)
- Operational ATC automation or certified decision authority.
- End-to-end speech recognition.
- Full trajectory conflict prediction.

## Core Pipeline
`ingest -> normalize -> segment -> parse -> validate -> export`

## Core Capabilities
- callsign extraction and normalization
- instruction segmentation for multi-intent utterances
- slot extraction for altitude, speed, heading, frequency, runway, waypoint
- clearance/intent typing
- readback detection and mismatch surfacing
- explicit fallback states (`unknown`, `ambiguous`, `conflict`)

## Output Contract (Suggested `v0.1`)
```json
{
  "schema_version": "atlas.intent.v0.1",
  "utterance_id": "optional-id",
  "speaker": "ATC",
  "callsign": "AFR345",
  "instructions": [
    {
      "type": "altitude",
      "action": "descend",
      "value": 180,
      "unit": "FL"
    },
    {
      "type": "speed",
      "action": "reduce",
      "value": 250,
      "unit": "kt"
    }
  ],
  "confidence": 0.96,
  "status": "ok"
}
```

`status` values:
- `ok`
- `unknown`
- `ambiguous`
- `conflict`

## Minimal Example
Input:
`Air France 345, descend flight level 180, reduce speed to 250 knots.`

Expected parse:
- callsign: `AFR345`
- intent: altitude + speed instruction
- normalized slots: `FL180`, `250 kt`

## Edge-Case Example
Input:
`Speedbird 42, descend one seven zero... correction, maintain one nine zero until LAM, then descend one five zero.`

Expected parse behavior:
- detect amendment (`correction`)
- preserve temporal condition (`until LAM`)
- output ordered instructions with explicit update semantics

## Evaluation Priorities
- intent precision/recall/F1
- slot extraction F1
- readback mismatch detection quality
- severity-weighted error tracking for high-risk intents
- calibration and threshold behavior under ASR noise

## Interoperability
ATLAS is independently usable and ecosystem-compatible.

Typical integrations:
- consume transcript input from ASR pipelines
- provide structured intent outputs to trajectory/conflict systems
- exchange versioned contracts with related research tools

Contract references:
- current execution plan: `roadmap.md`
- contract and docs milestones: `roadmap.md#phase-0-contract-and-scope`

## Research Claims vs Production Claims
Research claims:
- deterministic grammar baselines improve auditability
- structured outputs can be benchmarked with transparent metrics

Production claims:
- none yet
- operational use requires validation, monitoring, safety case, and regulatory alignment

## Safety and Limitations
- Research/prototype component, not certified ATM software.
- Low-confidence outputs must not be promoted without fallback policy.
- Performance depends on transcript quality and phraseology coverage.
- Regional procedures and non-standard phraseology require targeted tests.

## Project Roadmap
Execution milestones are in `roadmap.md`.
