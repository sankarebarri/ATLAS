from __future__ import annotations

import re

AIRLINE_ALIASES = {
    "AIR FRANCE": "AFR",
    "SPEEDBIRD": "BAW",
    "AMERICAN": "AAL",
    "DELTA": "DAL",
    "UNITED": "UAL",
}


def normalize_text(text: str) -> str:
    cleaned = text.upper().strip()
    cleaned = re.sub(r"[^A-Z0-9.\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    for spoken, code in AIRLINE_ALIASES.items():
        cleaned = cleaned.replace(spoken, code)
    return cleaned


def normalize_callsign(text: str) -> str | None:
    # Accept normalized ICAO code + number patterns (e.g., AFR 345).
    match = re.search(r"\b([A-Z]{3})\s?(\d{1,4})\b", text)
    if not match:
        return None
    return f"{match.group(1)}{int(match.group(2))}"
