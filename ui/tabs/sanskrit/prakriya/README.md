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
