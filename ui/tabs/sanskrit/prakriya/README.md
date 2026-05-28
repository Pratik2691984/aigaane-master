# Deterministic Prakriya Composition Pipeline

This module composes existing deterministic Sanskrit tab generators into a sentence-level structural prakriyā preview. It does not perform unrestricted Sanskrit parsing, semantic interpretation, dependency inference, agreement correction, probabilistic NLP, or authoritative grammatical adjudication.

## Scope

The pipeline coordinates:

- Subanta generation through the existing 31B engine
- Tiṅanta generation through the existing 31C engine
- Deterministic pada assembly
- Optional sandhi execution through the existing 31A engine
- Trace timeline emission
- Structural reverse preview metadata

## Sentence Assembly Limits

Sentence assembly is a dependency-safe structural preview. The engine uses generated padas in deterministic order and never guesses missing morphology or repairs unsupported combinations.

## Sandhi Integration

When `enableSandhi` is not `false`, generated padas are passed to the deterministic sandhi execution engine. Only explicit sandhi rules can match; unmatched boundaries remain visible and unchanged.

## Reverse Preview

Reverse preview records generated padas and sandhi transformations as structural metadata only. It is not an authoritative reconstruction.

## Trace Timeline

Trace nodes use stable ordered stages: subanta generation, tiṅanta generation, pada assembly, sandhi execution, sentence composition, reverse preview, and unresolved composition.

## Runtime Isolation

`executePrakriya(input)` does not mutate input objects, canonical registries, existing overlay state, or source generator outputs. Identical input returns identical output.

## Node 31E - Prakriya Trace Graph

`buildPrakriyaTraceGraph(execution)` projects a deterministic 31D execution into graph-safe nodes and edges. This is a structural graph projection only; it does not add missing derivation steps, infer grammar, or make authoritative prakriya claims.

Node types:

- `input`
- `subantaGeneration`
- `tinantaGeneration`
- `padaAssembly`
- `sandhiExecution`
- `sentenceComposition`
- `reversePreview`
- `diagnostic`
- `unresolved`

Edge types:

- `feeds`
- `transforms`
- `assembles`
- `appliesSandhi`
- `reversesTo`
- `annotates`
- `unresolved`

`serializePrakriyaTraceGraph(graph)` returns stable JSON-safe graph text for inspection and later storage. `attachPrakriyaOverlay(graph, overlayData)` returns a new graph with deterministic overlay annotations and does not mutate the original graph.

`renderPrakriyaTraceGraph(containerOrId, graph)` uses simple read-only DOM rendering. It does not require D3, canvas, vis-network, or external libraries. The renderer lists diagnostics, ordered nodes, directed edges, overlay annotations, unresolved warnings, and a serialized JSON preview.

Runtime isolation remains the same as the composition engine: graph construction never mutates execution objects, overlay inputs, canonical registries, or existing overlay state. Identical execution input produces identical graph output.

## Node 31F - Prakriya Overlay Integration Bridge

`prakriya-overlay-bridge.js` makes the prakriya trace graph the central read-only spine for deterministic overlay data. It attaches compact overlay payloads from karaka, vakya, chandas, sandarbha, semantic, and rule-trace layers onto `node.overlays` and `edge.overlays`.

The bridge exports:

- `cloneGraph(graph)`
- `attachOverlayToNode(graph, nodeId, overlayType, overlayData)`
- `attachOverlayToEdge(graph, edgeId, overlayType, overlayData)`
- `findNodeByOriginalId(graph, originalId)`
- `findEdgeByEndpoint(graph, source, target, type)`
- `attachAllOverlays(graph, execution, options = {})`

All bridge operations clone graph input and preserve execution input. Existing `build...Overlay` functions keep their current behavior; the new `attach...Overlay` functions only add deterministic graph-spine integration when called by the bridge.

`attachAllOverlays` returns a unified graph with `metadata.overlaysAttached`, renderer-compatible `overlays` objects on nodes and edges, and updated overlay diagnostics. It does not add backend work, external graph libraries, or authoritative grammar claims.
