# Deterministic Subanta Morphology Generator

This module is a read-only subanta generation preview layer for the Sanskrit tab. It performs deterministic suffix attachment for a small initial set of noun stem classes. It does not perform probabilistic parsing, hidden intent detection, canonical registry mutation, or authoritative grammatical adjudication.

## Supported Stem Classes

- `a-stem` masculine, sample `राम`
- `a-stem` neuter, sample `फल`
- `ā-stem` feminine, sample `सीता`

## Supported Vibhaktis

- `prathama`
- `dvitiya`
- `trtiya`
- `caturthi`
- `pancami`
- `sasthi`
- `saptami`

## Supported Vacanas

- `eka`
- `dvi`
- `bahu` / `बहु`

## Suffix Attachment

The generator matches `stemClass`, `linga`, `vibhakti`, and `vacana` against the explicit rule map. A-stem masculine and neuter rules append suffixes to the supplied stem. Ā-stem feminine rules remove final `ā` or `ा` before attaching the deterministic suffix. Unsupported combinations remain explicit diagnostics and do not produce inferred forms.

## Reverse Preview

Reverse preview metadata is structural only. It records the generated form, original stem, and suffix used in the current execution. It is not an authoritative reconstruction or grammatical proof.

## Runtime Isolation

`generateSubanta(input)` normalizes values into local metadata, never mutates source inputs, never writes canonical registries, and returns stable output for identical input.
