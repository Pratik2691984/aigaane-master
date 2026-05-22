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

from api.dhatu_semantic_derivation_graph import traverse_derivation_graph


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query semantic derivation graph placeholder bridges.")
    parser.add_argument("--dhatu-id")
    parser.add_argument("--family")
    parser.add_argument("--domain")
    parser.add_argument("--relation")
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--relation-type")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    payload = traverse_derivation_graph(
        dhatu_id=args.dhatu_id,
        family=args.family,
        domain=args.domain,
        relation=args.relation,
        max_depth=args.max_depth,
        relation_type=args.relation_type,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for path in payload["paths"]:
            print(f"{path['pathId']}\tdepth={path['depth']}\t{path['terminalNodeId']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
