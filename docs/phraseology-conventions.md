# Phraseology Conventions (v0)

## Scope
- English phraseology aligned with ICAO/FAA practice.
- Transcript input is already tokenized text (no audio handling).

## Normalization rules
- Uppercase all content for parser matching.
- Collapse repeated spaces and remove filler punctuation except decimal points.
- Normalize known airline name aliases (e.g., `AIR FRANCE` -> `AFR`, `SPEEDBIRD` -> `BAW`).
- Normalize instruction keywords (`TURN LEFT HEADING` => heading intent).

## Number conventions
- Flight levels represented as integer hundreds (`FL180`).
- Speeds represented in knots (`kt`).
- Frequencies represented in MHz with decimal (e.g., `121.500`).
- Headings represented as degrees true/magnetic as plain integer (`270`).

## Amendment conventions
- `CORRECTION` means subsequent instruction may replace a prior one.
- `THEN`, `UNTIL`, `AFTER` define temporal ordering/conditions.

## Fallback conventions
- Emit `unknown` if no supported instruction class is matched.
- Emit `ambiguous` if phrase maps equally to multiple actions.
- Emit `conflict` if same slot has incompatible simultaneous instructions.
