#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_search_response


def main() -> int:
    searches = {
        "cluster_motion": build_dhatu_semantic_search_response(cluster="motion"),
        "action_guidance": build_dhatu_semantic_search_response(action="guidance"),
        "gloss_stand": build_dhatu_semantic_search_response(gloss="stand"),
    }
    summary = {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/smoke_dhatu_semantic_api.py",
        "searches": {
            name: {
                "resultCount": payload["resultCount"],
                "firstDhatuId": payload["results"][0]["dhatuId"] if payload["results"] else None,
            }
            for name, payload in searches.items()
        },
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
