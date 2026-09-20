#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.dhatu_semantic_derivation_graph import validate_derivation_graph


def main(argv: Optional[List[str]] = None) -> int:
    summary = validate_derivation_graph()
    print(json.dumps({
        "derivationGraphValidationStatus": summary["derivationGraphValidationStatus"],
        "edgeCount": summary["edgeCount"],
        "familyNodeCount": summary["familyNodeCount"],
        "canonicalRegistryRecordCount": summary["canonicalRegistryRecordCount"],
        "duplicateEdgeIds": summary["duplicateEdgeIds"],
        "invalidReferenceCount": len(summary["invalidReferences"]),
    }, sort_keys=True))
    return 0 if summary["derivationGraphValidationStatus"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
