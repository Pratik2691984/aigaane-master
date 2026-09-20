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

from api.dhatu_semantic_derivation import query_payload


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query read-only dhatu semantic derivation placeholders.")
    parser.add_argument("--dhatu-id")
    parser.add_argument("--family")
    parser.add_argument("--domain")
    parser.add_argument("--relation")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    payload = query_payload(
        dhatu_id=args.dhatu_id,
        family=args.family,
        domain=args.domain,
        relation=args.relation,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for result in payload["results"]:
            domains = ",".join(result.get("usageDomains", []))
            print(f"{result['dhatuId']}\t{result['derivationFamilyId']}\t{domains}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
