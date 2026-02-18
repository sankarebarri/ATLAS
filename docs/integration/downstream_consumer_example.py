from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from atlas.evaluate import compare_readback
from atlas.sequence import SequenceState, parse_turn_with_state


def main() -> None:
    state = SequenceState()

    turns = [
        "AAL77 descend flight level 180",
        "AAL77 correction descend flight level 150",
        "AAL77 until LAM",
    ]

    parsed_turns = [
        parse_turn_with_state(turn, state=state, speaker="ATC", utterance_id=f"example-{idx + 1}")
        for idx, turn in enumerate(turns)
    ]

    readback = compare_readback(
        "AAL77 descend flight level 150",
        "AAL77 descend flight level 140",
    )

    payload = {
        "turns": parsed_turns,
        "active_state": state.active_by_callsign,
        "readback_mismatch": readback,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
