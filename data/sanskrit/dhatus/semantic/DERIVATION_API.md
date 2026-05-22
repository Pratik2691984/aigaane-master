# Dhatu Semantic Derivation API

## Purpose

The semantic derivation layer is a read-only placeholder scaffold for future derivational intelligence. It records local semantic families, lineages, usage domains, conceptual affix hints, and proto-relations without making authoritative Paninian or grammatical claims.

## Safety Contract

- No exact sutra ids are asserted.
- No grammatical correctness guarantee is provided.
- No metadata is treated as a canonical derivation.
- Every record must keep `reviewStatus` set to `placeholder-local-review-required`.
- Every confidence value must remain `unreviewed`.
- Sources must remain placeholder-only.
- `data/sanskrit/dhatus/index.json` must not be mutated.

## API

`GET /api/dhatu/semantic/derivations`

Supported query parameters:

- `dhatuId`
- `family`
- `domain`
- `relation`

Example helper calls:

```python
from api.dhatu_semantic_derivation import query_derivations, validate_derivations
from api.kernel_api import build_dhatu_semantic_derivations_response

motion = query_derivations(domain="motion")
payload = build_dhatu_semantic_derivations_response(family="motion-transition")
summary = validate_derivations()
```

Example CLI calls:

```powershell
python scripts/query_dhatu_semantic_derivations.py --dhatu-id 01.0005 --json
python scripts/query_dhatu_semantic_derivations.py --family motion-transition --json
python scripts/query_dhatu_semantic_derivations.py --domain motion --json
python scripts/query_dhatu_semantic_derivations.py --relation motion-guidance-adjacent --json
```

Validation:

```powershell
python scripts/validate_dhatu_semantic_derivations.py
```

UI-ready example fixtures:

```powershell
python scripts/export_dhatu_semantic_derivation_examples.py
```

The exported fixtures live under `data/sanskrit/dhatus/semantic/derivations/examples/`.

## Sanskrit Tab Panel

The Sanskrit tab renders this layer as a read-only **Derivation Intelligence** panel. The panel is placeholder-only, uses local fixture-compatible data, and can filter by derivation family, usage domain, and proto relation. All derivation claims require future review. No exact Paninian derivation claim is made, and no grammatical authority is implied.
