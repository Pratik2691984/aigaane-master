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

`GET /api/dhatu/semantic/derivation-graph`

Supported query parameters:

- `dhatuId`
- `family`
- `domain`
- `relation`
- `maxDepth`
- `relationType`

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
python scripts/query_dhatu_semantic_derivation_graph.py --domain motion --max-depth 2 --json
python scripts/query_dhatu_semantic_derivation_graph.py --relation-type semantic_family_bridge --json
```

Validation:

```powershell
python scripts/validate_dhatu_semantic_derivations.py
python scripts/validate_dhatu_semantic_derivation_graph.py
```

UI-ready example fixtures:

```powershell
python scripts/export_dhatu_semantic_derivation_examples.py
python scripts/export_dhatu_semantic_derivation_graph_examples.py
```

The exported fixtures live under `data/sanskrit/dhatus/semantic/derivations/examples/`.

Bridge graph fixtures live under `data/sanskrit/dhatus/semantic/derivations/examples/graph/`. The bridge graph connects semantic clusters, derivation family nodes, and derivation records with placeholder-only edges such as `motion -> motion_transition_family`, `guidance -> directional_guidance_family`, and `stability -> grounding_stability_family`.

## Sanskrit Tab Panel

The Sanskrit tab renders this layer as a read-only **Derivation Intelligence** panel. The panel is placeholder-only, uses local fixture-compatible data, and can filter by derivation family, usage domain, and proto relation. All derivation claims require future review. No exact Paninian derivation claim is made, and no grammatical authority is implied.

The semantic derivation graph bridge is also read-only. It performs bounded traversal only, never generates derivations, never mutates canonical records, and keeps every bridge confidence value at `unreviewed` with review status `placeholder-local-review-required`.

The Sanskrit tab renders the bridge as **Derivation Graph Intelligence**. This UI is placeholder-only and read-only; no exact Paninian derivation claim is made, no exact sutra assertion is made, and no grammatical correctness guarantee is provided.

## v70 Platform Checkpoint

`scripts/build_dhatu_semantic_platform_checkpoint.py` writes the v70 semantic platform checkpoint under `data/sanskrit/dhatus/semantic/releases/v70/`. The checkpoint freezes the read-only v53-v70 semantic stack, records validator results, and keeps derivation confidence and review status in placeholder-safe form.
