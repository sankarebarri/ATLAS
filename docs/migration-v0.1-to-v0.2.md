# ATLAS Contract Migration Notes: v0.1 -> v0.2

## Purpose
This note defines how downstream consumers should migrate from `atlas.intent.v0.1` to the planned `atlas.intent.v0.2` shape without breaking production parsing pipelines.

## Compatibility Strategy
- v0.2 is additive-first for existing top-level keys.
- Existing v0.1 fields remain available during migration:
  - `schema_version`, `utterance_id`, `speaker`, `callsign`
  - `instructions[]` core slot fields (`type`, `action`, `value`, `unit`, `condition`, `update`, `trace`)
  - `confidence`, `confidence_tier`, `status`, `notes`
- Consumers should branch on `schema_version` and use feature detection rather than positional assumptions.

## Planned v0.2 Additions
- top-level `context` object for sequence metadata:
  - `turn_index`
  - `session_id`
  - `callsign_source` (`explicit`, `inherited`)
- top-level `decision` object:
  - `hybrid_applied` (`bool`)
  - `conflict_source` (`intra_turn`, `history`, `none`)
- instruction-level temporal normalization:
  - `condition_type` (`then`, `after`, `until`, `none`)
  - `condition_value` (e.g. waypoint/fix string)

## Consumer Migration Checklist
1. Parse `schema_version` and route v0.1/v0.2 through explicit adapters.
2. Keep existing v0.1 extraction path unchanged for critical operations.
3. Add null-safe access for v0.2 fields (`context`, `decision`, condition normalization).
4. Gate strict validation by schema version.
5. Add regression tests covering mixed-version payloads.

## Example Adapter Pattern
```python
if payload["schema_version"] == "atlas.intent.v0.1":
    context = {"callsign_source": "explicit" if payload.get("callsign") else "unknown"}
else:
    context = payload.get("context", {})
```

## Rollout Plan
1. Producer emits v0.2 in shadow mode alongside v0.1-equivalent exports.
2. Consumers validate parity on core slots/status for one release cycle.
3. Switch consumers to v0.2-native fields.
4. Deprecate v0.1 adapters once all downstreams are migrated.
