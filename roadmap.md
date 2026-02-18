# ATLAS Roadmap Checklist

This checklist is the living execution board for ATLAS. Mark items as complete as work lands.

Legend:
- `[ ]` not started
- `[~]` in progress
- `[x]` complete

## Phase 0: Contract and Scope
- [x] Define output schema spec `atlas.intent.v0.1`
- [x] Create phraseology scope docs
- [x] Define fallback taxonomy (`ok`, `unknown`, `ambiguous`, `conflict`)
- [x] Add docs scaffolding:
  - [x] `docs/contracts/atlas.intent.v0.1.md`
  - [x] `docs/glossary.md`
  - [x] `docs/phraseology-conventions.md`
- [x] Include confidence and status in schema
- [x] Document v0 scope and non-goals
- [x] Represent at least 10 canonical classes in schema examples/documentation

## Phase 1: Deterministic Baseline Parser
- [x] Build parser pipeline modules (`ingest/normalize/segment/parse/validate/export`)
- [x] Implement callsign normalization
- [x] Implement instruction parsing: altitude
- [x] Implement instruction parsing: speed
- [x] Implement instruction parsing: heading
- [x] Implement instruction parsing: frequency
- [x] Implement instruction parsing: runway
- [x] Implement instruction parsing: waypoint
- [x] Implement instruction parsing: squawk
- [x] Implement instruction parsing: hold
- [x] Implement instruction parsing: direct
- [x] Implement instruction parsing: climb_rate
- [x] Add basic amendment/correction handling
- [x] Emit explicit fallback states for failed parses
- [x] Ensure no silent parse failures with traceable parser decisions

## Phase 2: Evaluation and CI Gates
- [x] Build first gold dataset slice (100-300 utterances)
- [x] Include amendment and edge-case examples in gold data
- [x] Build metric harness for intent precision/recall/F1
- [x] Build metric harness for slot extraction F1
- [x] Build readback mismatch metric
- [x] Add severity-weighted error reporting
- [x] Add CI regression job with thresholds
- [x] Block merge on regression threshold failures
- [x] Produce reproducible evaluation report artifact

## Phase 3: Ambiguity and Hybrid Layer
- [x] Add hybrid disambiguation layer (rules first, ML assist second)
- [x] Define confidence threshold policy
- [x] Add calibration/reliability analysis
- [x] Improve ambiguous-case performance over deterministic baseline
- [x] Preserve high-confidence deterministic performance

## Phase 4: Context and Sequencing
- [x] Add multi-turn state tracking (amendments/cancellations)
- [x] Support temporal conditions (`until`, `after`, `then`) across turns
- [x] Add contradiction/conflict detection across history
- [x] Pass sequence benchmarks for amendment/correction scenarios

## Phase 5: Integration and Developer Readiness
- [x] Write contract migration notes (`v0.1 -> v0.2`)
- [x] Add integration examples for downstream consumers
- [x] Expand docs pack with minimal and realistic examples
- [x] Add safety and limitations playbook
- [x] Capture baseline performance profile
- [x] Complete one downstream integration dry run

## Continuous Workstreams
- [x] Data quality and annotation adjudication process
- [x] Observability and parse trace logging
- [x] Phraseology coverage expansion by region/procedure
- [x] Safety review for failure modes and fallback behavior

## Next Up (Immediate)
- [x] Continue phraseology expansion with additional region-specific corpora
- [x] Add CI thresholds for safety metrics trend regression
- [x] Add adjudication reviewer assignment/ownership policy
