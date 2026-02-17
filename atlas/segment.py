from __future__ import annotations

import re


def split_instructions(text: str) -> list[str]:
    parts = re.split(r"\bTHEN\b|,|\bAND\b", text)
    return [part.strip() for part in parts if part.strip()]
