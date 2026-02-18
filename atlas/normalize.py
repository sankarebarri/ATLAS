from __future__ import annotations

import re

AIRLINE_ALIASES = {
    "AIR FRANCE": "AFR",
    "AIRFRANCE": "AFR",
    "SPEEDBIRD": "BAW",
    "SPEED BIRD": "BAW",
    "AMERICAN": "AAL",
    "DELTA": "DAL",
    "UNITED": "UAL",
}

PHRASE_REPLACEMENTS = {
    "HEDING": "HEADING",
    "DECEND": "DESCEND",
    "LAMB": "LAM",
    "CAP TEA": "CPT",
    "PROCEED TOO": "PROCEED TO",
    "PROCEED VIA": "PROCEED TO",
    "CLEARED DIRECT TO": "CLEARED DIRECT",
    "CONTACT TOWER ON": "CONTACT",
    "CONTACT APPROACH ON": "CONTACT",
    "DESCEND TO LEVEL": "DESCEND LEVEL",
    "CLIMB TO LEVEL": "CLIMB LEVEL",
    "CLIMB AND MAINTAIN": "CLIMB",
    "DESCEND AND MAINTAIN": "DESCEND",
    "ONE TWO ONE DECIMAL FIVE": "121.5",
    "ONE TWENTY DECIMAL TWO FIVE": "120.25",
    "TWO SEVEN RIGHT": "27R",
    "TWO SEVEN LEFT": "27L",
    "THREE FOUR FIVE": "345",
    "ONE EIGHT ZERO": "180",
    "ONE NINER ZERO": "190",
    "ONE FIVE ZERO": "150",
    "FOUR SEVEN TWO ONE": "4721",
    "SEVEN THOUSAND": "7000",
    "FOURTEEN HUNDRED": "1400",
    "ONE THOUSAND EIGHT HUNDRED": "1800",
}

SPOKEN_DIGITS = {
    "ZERO": "0",
    "OH": "0",
    "O": "0",
    "ONE": "1",
    "TWO": "2",
    "THREE": "3",
    "FOUR": "4",
    "FIVE": "5",
    "SIX": "6",
    "SEVEN": "7",
    "EIGHT": "8",
    "NINE": "9",
    "NINER": "9",
}


def normalize_text(text: str) -> str:
    cleaned = text.upper().strip()
    cleaned = re.sub(r"[^A-Z0-9.\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    for noisy, normalized in PHRASE_REPLACEMENTS.items():
        cleaned = re.sub(rf"\b{re.escape(noisy)}\b", normalized, cleaned)

    for spoken, code in AIRLINE_ALIASES.items():
        cleaned = re.sub(rf"\b{re.escape(spoken)}\b", code, cleaned)

    return cleaned.strip()


def normalize_callsign(text: str) -> str | None:
    # Accept normalized ICAO code + number patterns (e.g., AFR 345).
    match = re.search(r"\b([A-Z]{3})\s?(\d{1,4})\b", text)
    if match:
        return f"{match.group(1)}{int(match.group(2))}"

    spoken_match = re.search(
        r"\b([A-Z]{3})\s+"
        r"(ZERO|OH|O|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|NINER)"
        r"(?:\s+(ZERO|OH|O|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|NINER)){1,3}\b",
        text,
    )
    if not spoken_match:
        return None

    parts = [part for part in spoken_match.groups()[1:] if part]
    digits = "".join(SPOKEN_DIGITS[token] for token in parts)
    return f"{spoken_match.group(1)}{int(digits)}"
