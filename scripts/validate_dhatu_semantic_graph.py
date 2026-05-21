#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.dhatu_semantic_graph import validate_graph


def main(argv: Optional[List[str]] = None) -> int:
    summary = validate_graph()
    print(json.dumps({
        "graphValidationStatus": summary["graphValidationStatus"],
        "edgeCount": summary["edgeCount"],
        "duplicateEdgeIds": summary["duplicateEdgeIds"],
        "invalidReferenceCount": len(summary["invalidReferences"]),
        "traversalValidationStatus": summary["traversalValidationSummary"]["traversalValidationStatus"],
    }, sort_keys=True))
    return 0 if summary["graphValidationStatus"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
