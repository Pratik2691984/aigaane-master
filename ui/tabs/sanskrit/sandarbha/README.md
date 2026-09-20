# Sandarbha Context Resolution

Status: READ_ONLY_DETERMINISTIC_OVERLAY

This layer provides deterministic context-neighborhood inspection from explicit metadata. It is not discourse interpretation, unrestricted semantic understanding, or full anaphora resolution.

## Local Dependency Neighborhoods

Existing vākya dependency edges can create local context neighborhoods. The layer reads those edges directly and does not infer hidden dependencies.

## Continuity Candidates

- kāraka continuity is emitted only for adjacent repeated explicit kāraka roles
- morphology continuity is emitted only for repeated explicit vibhakti, linga, or vacana signatures
- derivation continuity is emitted only when explicit derivation lineage metadata overlaps

## Pronoun Candidate Limits

Explicit pronoun-like token metadata can create `pronounAntecedentCandidate` entries. These remain candidate-only unless an upstream deterministic layer supplies explicit antecedent metadata. No antecedent is guessed from meaning.

## Linkage

The engine accepts morphology transitions, kāraka overlays, vākya dependency overlays, semantic overlays, derivation graphs, and rule trace chains. It inspects these inputs without mutation and preserves unresolved candidates.

## Runtime Isolation

- no canonical dhātu registry mutation
- no probabilistic NLP
- no hidden meaning inference
- no unrestricted context resolution
- no runtime architecture changes
- read-only DOM rendering
