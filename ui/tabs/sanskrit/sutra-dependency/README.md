# Deterministic Sutra Dependency Resolver

Node 31H adds the first read-only dependency resolver between rulefire rules, sutra reference placeholders, rule-trace metadata, and the prakriya graph. It is not a full Ashtadhyayi executor and does not claim authoritative Paninian correctness.

## Dependency Map

`sutra-dependency-map.js` stores explicit deterministic links from currently implemented rulefire ids to placeholder references such as `symbolic_ac`, `symbolic_hal`, nominal suffix selection, tinanta selection, and prakriya stage markers.

Dependencies absent from the map are not inferred. Unknown rules remain visible through safe diagnostics.

## Rulefire Linkage

`buildSutraDependencyGraph(input)` accepts a rulefire payload, rule trace overlay, sutra reference overlay, and optional enabled stages. Fired rule ids are matched only against the dependency map. The output is a graph-safe read-only projection with dependency nodes, edges, unresolved references, and diagnostics.

## Graph Attachment

`attachSutraDependenciesToRulefire(rulefire, dependencyGraph)` returns a cloned rulefire payload with dependency metadata. `attachSutraDependenciesToGraph(graph, dependencyGraph)` returns a cloned prakriya graph with dependency nodes, dependency edges, and `metadata.dependenciesAttached`.

## Backend Payload

The Python backend exposes a minimal `sutra_dependency` payload and marks `prakriya_graph.metadata.dependenciesAttached` so `/api/v3/analyze` remains compatible while the richer JavaScript dependency resolver runs in the frontend.

## Runtime Isolation

The resolver does not mutate rulefire input, trace graph input, canonical registries, ingestion files, or existing overlay payloads. Identical input produces identical dependency graph output.

