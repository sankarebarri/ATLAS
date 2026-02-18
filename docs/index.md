# ATLAS

ATLAS (Air Traffic Language Analysis System) parses ATC transcript text into structured, auditable intent payloads.

## What ATLAS Does
- extracts callsigns and instruction slots from ATC phraseology
- assigns explicit parser status (`ok`, `unknown`, `ambiguous`, `conflict`)
- applies confidence policy and fallback behavior
- supports deterministic + hybrid disambiguation behavior
- supports multi-turn sequence handling (amendments, cancellations, temporal links)
- provides evaluation, safety, and data-quality gates for regression control

## Typical Use Cases
- downstream automation pipelines that need structured intent data
- readback mismatch detection workflows
- safety/fallback policy monitoring for parser outputs
- benchmark-driven parser iteration using gold datasets

## Start Here
- Setup and runbook: `documentation.md`
- Output contract: `contracts/atlas.intent.v0.1.md`
- Phraseology support: `phraseology-conventions.md`
- Safety and gating: `safety-limitations-playbook.md`

## Current Boundaries
ATLAS is a research-grade parser component and not certified ATM decision software.

Use explicit gating (`data_quality`, `safety_gate`) before operational adoption.
