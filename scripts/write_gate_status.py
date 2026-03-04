from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Write gate status evidence as JSON.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--status", required=True, choices=("PASS", "FAIL"))
    parser.add_argument("--details", default="")
    args = parser.parse_args()

    payload = {
        "gate": args.gate,
        "status": args.status,
        "details": args.details,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
