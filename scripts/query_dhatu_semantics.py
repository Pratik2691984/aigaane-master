#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.dhatu_semantic_query import query_payload


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query canonical dhatu semantic sidecar records.")
    parser.add_argument("--dhatu-id")
    parser.add_argument("--root")
    parser.add_argument("--iast")
    parser.add_argument("--cluster")
    parser.add_argument("--gloss")
    parser.add_argument("--action")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    payload = query_payload(
        dhatu_id=args.dhatu_id,
        root=args.root,
        iast=args.iast,
        cluster=args.cluster,
        gloss=args.gloss,
        action=args.action,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for result in payload["results"]:
            print(f"{result['dhatuId']}\t{result['root']}\t{result['iast']}\t{result['gloss']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
