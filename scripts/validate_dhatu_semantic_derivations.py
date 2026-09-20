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

from api.dhatu_semantic_derivation import DEFAULT_DERIVATION_PATH, validate_derivations


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate dhatu semantic derivation placeholders.")
    parser.add_argument("--derivation-path", default=str(DEFAULT_DERIVATION_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    summary = validate_derivations(args.derivation_path)
    print(json.dumps({
        "derivationValidationStatus": summary["derivationValidationStatus"],
        "derivationRecordCount": summary["derivationRecordCount"],
        "relationCount": summary["relationCount"],
        "canonicalRegistryRecordCount": summary["canonicalRegistryRecordCount"],
        "duplicateDerivationIds": summary["duplicateDerivationIds"],
        "unresolvedRelationReferenceCount": len(summary["unresolvedRelationReferences"]),
    }, sort_keys=True))
    return 0 if summary["derivationValidationStatus"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
