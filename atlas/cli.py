from __future__ import annotations

import argparse
import json

from atlas.pipeline import parse_utterance


def main() -> None:
    parser = argparse.ArgumentParser(description="ATLAS deterministic parser")
    parser.add_argument("utterance", help="ATC transcript utterance")
    parser.add_argument("--speaker", default="ATC")
    parser.add_argument("--utterance-id", default=None)
    parser.add_argument("--trace", action="store_true", help="Include parse-stage trace payload")
    parser.add_argument("--trace-log", default=None, help="Optional JSONL file path for appending parse traces")
    args = parser.parse_args()

    output = parse_utterance(
        args.utterance,
        speaker=args.speaker,
        utterance_id=args.utterance_id,
        include_trace=args.trace,
        trace_log_path=args.trace_log,
    )
    print(json.dumps(output, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
