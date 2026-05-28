# Deterministic Nirukta Etymology Layer

Node 32A adds a deterministic Nirukta-style inspection scaffold for the Sanskrit runtime. It is not historical linguistics, does not infer unknown roots, and does not claim authoritative Nirukta interpretation.

## Scope

The layer links visible generated forms to a small placeholder registry of dhatu lineage, pratipadika lineage, upasarga placeholders, semantic families, rulefire rules, sutra dependency references, and graph nodes.

## Registries

`nirukta-etymology-map.js` includes deterministic placeholder entries for:

- dhatu lineage: `gam`, `bhu`, `ni`
- pratipadika lineage: `rama`, `phala`, `sita`
- upasarga placeholders: `pra`, `pari`, `sam`, `vi`, `aa`

## Overlay Behavior

`buildNiruktaOverlay(input)` inspects generated padas from subanta, tinanta, and prakriya execution payloads. It matches only known lemmas in `NIRUKTA_ETYMOLOGY_MAP`. Unknown forms remain visible in `unresolved`.

## Graph And Backend Linkage

`attachNiruktaToGraph(graph, overlay)` returns a cloned graph with Nirukta candidate nodes, edges, and `metadata.niruktaAttached`. The backend exposes a compatible `nirukta` payload and marks `prakriya_graph.metadata.niruktaAttached`.

## Runtime Isolation

The layer does not mutate input forms, rulefire payloads, sutra dependency graphs, trace graphs, canonical registries, or ingestion files. Identical input produces identical output.

