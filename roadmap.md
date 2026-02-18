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
- [ ] Build readback mismatch metric
- [ ] Add severity-weighted error reporting
- [ ] Add CI regression job with thresholds
- [ ] Block merge on regression threshold failures
- [ ] Produce reproducible evaluation report artifact

## Phase 3: Ambiguity and Hybrid Layer
- [ ] Add hybrid disambiguation layer (rules first, ML assist second)
- [ ] Define confidence threshold policy
- [ ] Add calibration/reliability analysis
- [ ] Improve ambiguous-case performance over deterministic baseline
- [ ] Preserve high-confidence deterministic performance

## Phase 4: Context and Sequencing
- [ ] Add multi-turn state tracking (amendments/cancellations)
- [ ] Support temporal conditions (`until`, `after`, `then`) across turns
- [ ] Add contradiction/conflict detection across history
- [ ] Pass sequence benchmarks for amendment/correction scenarios

## Phase 5: Integration and Developer Readiness
- [ ] Write contract migration notes (`v0.1 -> v0.2`)
- [ ] Add integration examples for downstream consumers
- [ ] Expand docs pack with minimal and realistic examples
- [ ] Add safety and limitations playbook
- [ ] Capture baseline performance profile
- [ ] Complete one downstream integration dry run

## Continuous Workstreams
- [ ] Data quality and annotation adjudication process
- [ ] Observability and parse trace logging
- [ ] Phraseology coverage expansion by region/procedure
- [ ] Safety review for failure modes and fallback behavior

## Next Up (Immediate)
- [x] Build first gold slice in `data/gold/`
- [x] Add parser trace metadata to every instruction
- [x] Add hand-curated ASR-like noisy subset in `data/gold/`
- [ ] Add CI workflow for tests + metrics
- [x] Add waypoint and squawk parser support
