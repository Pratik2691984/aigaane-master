# Dhatu Semantic UI Integration

## Purpose

This document describes the read-only Semantic Dhātu Intelligence panel in the Sanskrit tab. The panel is backed by deterministic semantic search, neighbor, and traversal fixture shapes.

## No Runtime Mutation Policy

The Sanskrit tab should consume these panel fixtures as read-only examples. Exporting or displaying them must not mutate `data/sanskrit/dhatus/index.json`, semantic source files, graph edges, promotion artifacts, or canonical write approvals.

## Panel Fixture Consumption

The Sanskrit tab can load panel fixtures from `data/sanskrit/dhatus/semantic/examples/ui/` and render each `cards[]` entry as a normalized frontend card. Each card has `cardId`, `cardType`, `label`, `value`, and `metadata`, so the UI does not need to infer display fields from raw semantic API payloads.

Recommended frontend sections:

- Search Results
- Semantic Neighbors
- Traversal Paths
- Safety Notes

## Example File Paths

- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_search_panel.v1.json`
- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_neighbor_panel.v1.json`
- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_traversal_panel.v1.json`
- `data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_combined_panel.v1.json`

Regenerate fixtures with:

```powershell
python scripts/export_dhatu_semantic_ui_examples.py
```

## Future API Endpoints

- `/api/dhatu/semantic/search`
- `/api/dhatu/semantic/neighbors`
- `/api/dhatu/semantic/traverse`

## Safety Notes

Semantic graph links are foundation-placeholder UI context only. They do not make exact Pāṇinian derivation claims.
