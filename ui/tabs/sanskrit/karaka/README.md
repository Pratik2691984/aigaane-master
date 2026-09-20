# Kāraka Relation Overlay

Status: READ_ONLY_DETERMINISTIC_OVERLAY

This layer provides deterministic inspection metadata for selected kāraka relations. It is not a syntactic parser, does not infer hidden syntax, and does not claim authoritative Sanskrit grammatical correctness.

## Relation Registry

- prathama -> karta
- dvitiya -> karma
- trtiya -> karana
- caturthi -> sampradana
- pancami -> apadana
- saptami -> adhikarana

## Morphology Linkage

The overlay inspects supplied morphology transition entries for explicit vibhakti metadata. Entries without recognized vibhakti metadata remain unmatched.

## Overlay Inputs

The engine accepts morphology transitions, semantic overlays, derivation graph metadata, and rule-trace metadata. It only matches kāraka candidates from morphology transition data and does not mutate any supplied input object.

## Runtime Isolation

- no canonical dhātu registry mutation
- no probabilistic NLP parsing
- no runtime architecture changes
- deterministic output for identical input
- read-only DOM rendering
