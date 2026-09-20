# Sanskrit Dhatu Semantic Platform

## Platform Overview

The Sanskrit dhatu semantic platform is a read-only sidecar over the canonical dhatu registry. It exposes semantic search, graph neighbors, graph traversal, placeholder derivation metadata, and placeholder derivation graph traversal without mutating `data/sanskrit/dhatus/index.json`.

The public index endpoint is:

`GET /api/dhatu/semantic`

It summarizes endpoint paths, documentation paths, example fixture roots, the v70 checkpoint, validator status, milestone tags, and the platform safety policy.

## Static Preview Behavior

`python -m http.server 3000` is static-only: it serves the browser UI and fixture files, but `/api/*` routes return 404 unless a backend runtime is active. In static preview the Sanskrit tab keeps using read-only semantic fixture/fallback data, expected 404/501 API misses are handled as controlled fallback events, analysis fallback is expected and safe, and no canonical mutation occurs.

For static inspection, use the Sanskrit tab's read-only **Static Semantic Fixture Browser** instead of direct `/api/*` URLs. The browser panel displays loaded fixture availability, semantic record counts, clusters, graph nodes, neighbors, derivation graph availability, and a safe JSON preview rendered as escaped text with no eval and no mutation.

Static fixture inspection links use URL hashes such as `#sanskrit-static-fixtures?cluster=motion&dhatuId=01.0005&nodeId=motion&section=neighbors`. They are static-preview-only state restoration links; `/api/*` still returns 404 under `python -m http.server 3000` unless a backend runtime is active.

## Endpoint Index

| Endpoint | Purpose |
| --- | --- |
| `/api/dhatu/semantic/search` | Search semantic sidecar records by dhatu id, root, IAST, cluster, gloss, or action. |
| `/api/dhatu/semantic/neighbors` | Return bounded semantic graph neighbors for a selected node. |
| `/api/dhatu/semantic/traverse` | Return deterministic traversal paths through the semantic graph. |
| `/api/dhatu/semantic/derivations` | Return placeholder-only derivation metadata. |
| `/api/dhatu/semantic/derivation-graph` | Bridge semantic graph nodes to placeholder derivation families. |

## Safety Policy

The semantic platform is read-only. It does not require canonical write environment flags, does not run the canonical writer, and does not mutate promotion artifacts.

Derivation and derivation graph records remain placeholder-only. No exact Paninian derivation claim is made, no exact sutra assertion is made, and no grammatical correctness guarantee is provided. Derivation confidence values remain `unreviewed`, and review statuses remain `placeholder-local-review-required`.

## v53-v72 Milestone Summary

| Node | Summary |
| --- | --- |
| v53 | Semantic layer foundation |
| v54 | Semantic query engine |
| v55 | Semantic search API |
| v56 | Semantic API examples and docs |
| v57 | Semantic graph neighbors |
| v58 | Semantic platform continuity checkpoint |
| v59 | Semantic platform continuity checkpoint |
| v60 | Semantic graph API helper |
| v61 | Semantic traversal API |
| v62 | UI-ready semantic fixtures |
| v63 | Sanskrit semantic panels |
| v64 | Interactive semantic controls |
| v65 | Semantic graph visualization |
| v66 | Semantic graph accessibility |
| v67 | Semantic derivation placeholder layer |
| v68 | Derivation Intelligence UI |
| v69 | Semantic derivation graph bridge |
| v70 | Derivation Graph Intelligence UI and platform checkpoint |
| v71 | Public read-only semantic API index |
| v72 | Semantic Platform Status UI panel |

## Checkpoint Location

- JSON: `data/sanskrit/dhatus/semantic/releases/v70/semantic_platform_checkpoint.v70.json`
- Markdown: `data/sanskrit/dhatus/semantic/releases/v70/semantic_platform_checkpoint.v70.md`

## Validator Commands

```powershell
python scripts/build_dhatu_semantic_platform_checkpoint.py
python scripts/validate_dhatu_semantic_derivations.py
python scripts/validate_dhatu_semantic_derivation_graph.py
python scripts/validate_dhatu_semantic_graph.py
python scripts/validate_dhatu_semantic_layer.py
python scripts/smoke_dhatu_semantic_platform_index.py
```

## UI Integration References

- `data/sanskrit/dhatus/semantic/UI_INTEGRATION.md`
- `data/sanskrit/dhatus/semantic/examples/ui/`
- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_platform_status_panel.v1.json`
- `data/sanskrit/dhatus/semantic/derivations/examples/graph/ui_semantic_derivation_graph_panel.v1.json`
- `ui/tabs/sanskrit/view.html`
- `ui/tabs/sanskrit/controller.js`
- `ui/tabs/sanskrit/style.css`

## Semantic Platform Status Panel

The Sanskrit tab renders a read-only **Semantic Platform Status** panel from deterministic local fixture-compatible data. It displays `READY` platform state, the v53-v72 milestone span, canonical and semantic record counts, validator summaries, available semantic API endpoints, documentation and example references, the v70 checkpoint location, UI readiness, and the placeholder-safe policy. It has no backend fetch requirement, no mutation hooks, and no canonical write logic.
