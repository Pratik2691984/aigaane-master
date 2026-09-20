#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.dhatu_semantic_graph import get_neighbors


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query dhatu semantic graph neighbors.")
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--relation-type")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    payload = get_neighbors(args.node_id, depth=args.depth, relation_type=args.relation_type)
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for neighbor in payload["neighbors"]:
            print(f"{neighbor['nodeId']}\t{neighbor['nodeType']}\tdepth={neighbor['depth']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
