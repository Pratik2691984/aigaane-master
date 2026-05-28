# Deterministic Rule-Firing Engine

Node 31G introduces a controlled rule-firing substrate for already implemented lookup-driven Sanskrit layers. It is not a full Ashtadhyayi engine, does not perform probabilistic parsing, and does not claim authoritative Paninian correctness.

## Scope

The rulefire layer records explicit ordered applications for deterministic sandhi, subanta, tinanta, and prakriya composition metadata already present in the runtime.

## Rule Registry

`rulefire-map.js` exports `RULEFIRE_RULE_MAP` and helpers for lookup, normalization, category grouping, and stable priority sorting. Each registry entry has an explicit `inputPattern`, `outputPattern`, `priority`, stage, source layer, reversibility flag, notes, and deterministic confidence.

## Eligibility

`evaluateRuleEligibility(rule, state)` checks only explicit `inputPattern` fields against visible state metadata. Unsupported inputs remain unresolved. The engine does not infer hidden grammar, repair malformed state, or guess missing morphology.

## Execution

`executeRulefire(input)` normalizes a safe state, filters enabled categories and stages, sorts rules by ascending priority, and fires only eligible deterministic rules. Each fired rule produces a new state snapshot; source input objects are never mutated.

## Snapshots And Trace

Snapshots preserve the initial state and each state caused by a fired rule. Trace entries are stable, ordered, graph-safe records of the rule id, operation, before state, and after state. Reverse preview is structural metadata only.

## Graph Projection

`graphProjection` emits rule nodes and transition edges suitable for the prakriya trace graph. `attachRulefireToGraph(graph, rulefire)` returns a cloned graph with rulefire nodes, bridge edges, and metadata recording that rulefire was attached.

## Backend Compatibility

The backend analyze payload exposes a minimal deterministic `rulefire` projection so `/api/v3/analyze` remains compatible even though the JavaScript rulefire engine runs in the frontend.

## Runtime Isolation

The engine does not mutate canonical registries, ingestion files, source generators, graph inputs, execution inputs, or existing overlay state. Identical input returns identical output.

