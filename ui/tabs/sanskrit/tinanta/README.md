# Deterministic Tinanta Morphology Generator

This module is a read-only tiṅanta generation preview for the Sanskrit tab. It uses direct deterministic lookup rules for an initial laṭ/parasmaipada set and does not perform probabilistic parsing, intent guessing, canonical registry mutation, or authoritative grammatical adjudication.

## Supported Roots

- `bhū` / `भू`
- `gam` / `गम्`
- `nī` / `नी`

## Supported Cells

The generator supports all 9 laṭ/parasmaipada cells for each root:

- Puruṣa: `prathama`, `madhyama`, `uttama`
- Vacana: `eka`, `dvi`, `bahu`

This yields 27 direct rule entries.

## Present-Stem Strategy

Present stems are selected only from explicit metadata:

- `bhū` -> `bhava`
- `gam` -> `gaccha`
- `nī` -> `naya`

The emitted form comes from `rule.generatedForm`; this first version intentionally avoids sandhi execution or derivational inference inside the generator.

## Reverse Preview

Reverse preview and reverse lookup are structural metadata only. They map a supported generated form back to its deterministic rule tuple and are not authoritative grammatical reconstruction.

## Paradigm Generation

`generateTinantaParadigm(input)` returns the 9 supported laṭ/parasmaipada forms for a supported root and explicit or default `lakara`/`pada` metadata.

## Runtime Isolation

All functions normalize values into local metadata, never mutate input objects, never write canonical registries, and return stable output for identical input.
