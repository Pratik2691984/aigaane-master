# Dhatu Semantic UI Integration

## Purpose

This document describes the read-only Semantic Dhatu Intelligence panel in the Sanskrit tab. The panel is backed by deterministic semantic search, neighbor, traversal, and derivation-placeholder fixture shapes.

## No Runtime Mutation Policy

The Sanskrit tab should consume these panel fixtures as read-only examples. Exporting or displaying them must not mutate `data/sanskrit/dhatus/index.json`, semantic source files, graph edges, derivation placeholder metadata, promotion artifacts, or canonical write approvals.

## Panel Fixture Consumption

The Sanskrit tab can load panel fixtures from `data/sanskrit/dhatus/semantic/examples/ui/` and render each `cards[]` entry as a normalized frontend card. Each card has `cardId`, `cardType`, `label`, `value`, and `metadata`, so the UI does not need to infer display fields from raw semantic API payloads.

The current Sanskrit tab integration adds read-only client-side query controls for search text, cluster, action, gloss, traversal depth, and relation type. These controls filter fixture-compatible semantic cards in the browser and fall back to static panel data if fixture loading is unavailable.

The Semantic Graph View is also client-side and read-only. It renders lightweight HTML/CSS graph nodes, relation labels, selected-node highlighting, traversal-path highlighting, and a screen-reader-friendly relation legend from fixture-compatible fallback graph data.

The Sanskrit tab includes a read-only **Derivation Intelligence** panel for the Semantic Derivation Placeholder layer. It may load fixture-compatible local data from `data/sanskrit/dhatus/semantic/derivations/` and should continue to work without a backend server. UI copy must keep these records labelled as placeholders requiring future review, and must not present any relation as a grammatical derivation or exact Paninian source.

Graph visualization accessibility:

- The Semantic Dhatu Intelligence and Semantic Graph View sections expose labelled regions.
- Graph nodes are keyboard-focusable buttons.
- Enter and Space activate the focused semantic node.
- The selected node state is exposed with `aria-pressed`.
- The selected-node summary updates in an `aria-live` region.

Recommended frontend sections:

- Search Results
- Semantic Neighbors
- Traversal Paths
- Derivation Placeholders
- Safety Notes

The Derivation Intelligence panel should display selected dhatu id, root, IAST, derivation family id, semantic lineage, usage domains, conceptual affix hints, proto derivation relations, semantic transformation notes, placeholder Panini relation, review status, and a visible safety note. Family, usage-domain, and relation filters are read-only local filters.

The semantic derivation graph bridge is exposed in the Sanskrit tab as a read-only **Derivation Graph Intelligence** panel. It uses UI-ready fixtures in `data/sanskrit/dhatus/semantic/derivations/examples/graph/` and connects semantic cluster nodes to derivation family nodes and derivation placeholder records for bounded, read-only traversal.

Supported control values include the motion, guidance, and stability clusters; traversal depths 1 and 2; and relation filters `guides`, `associated_with`, `transitions_to`, and `grounds`.

The graph view initially displays `gam / 01.0005`, `motion`, `guidance`, `stability`, `ni / 01.0008`, and `stha / 01.0013` with relation edges among those nodes.

## Example File Paths

- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_search_panel.v1.json`
- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_neighbor_panel.v1.json`
- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_traversal_panel.v1.json`
- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_combined_panel.v1.json`
- `data/sanskrit/dhatus/semantic/derivations/examples/ui_semantic_derivation_panel.v1.json`

Regenerate fixtures with:

```powershell
python scripts/export_dhatu_semantic_ui_examples.py
python scripts/export_dhatu_semantic_derivation_examples.py
```

## Future API Endpoints

- `/api/dhatu/semantic/search`
- `/api/dhatu/semantic/neighbors`
- `/api/dhatu/semantic/traverse`
- `/api/dhatu/semantic/derivations`
- `/api/dhatu/semantic/derivation-graph`

## Safety Notes

Semantic graph links are foundation-placeholder UI context only. They do not make exact Paninian derivation claims.

Semantic derivation metadata is also placeholder-only. It provides no exact sutra assertion, no authoritative Paninian claim, and no grammatical correctness guarantee.

All derivation claims require future review. No exact Paninian derivation claim is made, and the semantic derivation layer remains read-only.

The derivation graph bridge is also placeholder-only. It makes no exact sutra reference, does not generate derivations, and does not mutate canonical or semantic source data.

The Derivation Graph Intelligence UI is placeholder-only and read-only. No exact Paninian derivation claim is made, no exact sutra assertion is made, and no grammatical correctness guarantee is provided.

The v70 semantic platform checkpoint freezes the v53-v70 Sanskrit semantic intelligence stack in `data/sanskrit/dhatus/semantic/releases/v70/`. It summarizes validator status, UI fixture coverage, graph and derivation counts, and the read-only safety contract.

The Sanskrit tab also includes a read-only **Semantic Platform Status** panel backed by `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_platform_status_panel.v1.json`. It renders platform status, the v53-v72 milestone span, canonical registry count, semantic record count, validator summaries, public API endpoints, documentation references, checkpoint paths, UI readiness, and the placeholder-safe policy. The panel uses deterministic local fallback data and does not require a live backend fetch.
