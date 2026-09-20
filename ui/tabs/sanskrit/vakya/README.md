# Vākya Dependency Inspection

Status: READ_ONLY_DETERMINISTIC_OVERLAY

This layer provides deterministic sentence dependency inspection from explicit metadata. It is not a Sanskrit parser, does not infer hidden syntax, and does not claim authoritative syntactic resolution.

## Finite Verb Anchor Design

Finite verb anchors are created only when morphology transition metadata explicitly marks a token as tiṅanta or finite verbal morphology. Without such an anchor, dependency edges are not guessed.

## Kāraka-to-Verb Linkage

When a deterministic finite verb anchor exists, explicit kāraka overlay nodes can link to it with stable relation ids:

- karta -> kartaToVerb
- karma -> karmaToVerb
- karana -> karanaToVerb
- sampradana -> sampradanaToVerb
- apadana -> apadanaToVerb
- adhikarana -> adhikaranaToVerb

## Unresolved Candidates

If no finite verb anchor exists, kāraka candidates remain `unresolvedCandidate` nodes and diagnostics include a warning. The layer does not use adjacency or heuristics as syntactic evidence.

## Overlay Linkage

The engine accepts tokens, morphology transitions, kāraka overlays, semantic overlays, derivation graphs, and rule trace chains. It reads these inputs without mutation and emits a stable overlay for identical input.

## Runtime Isolation

- no canonical dhātu registry mutation
- no probabilistic NLP parsing
- no hidden syntax inference
- no runtime architecture changes
- read-only DOM rendering
