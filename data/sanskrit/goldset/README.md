# Canonical Dhatu Goldset

The goldset is the permanent regression truth layer for curated Sanskrit dhatu records. It is separate from the normal canonical registry and exists so tests can detect accidental changes to high-value records as the registry grows.

The normal dhatu registry lives in `data/sanskrit/dhatus/`.

The goldset lives in `data/sanskrit/goldset/`.

Goldset v1 is immutable regression truth. Do not silently mutate v1 expectations when canonical records change. Instead, create a new `v1.1` or `v2` goldset and document why the expectation changed.

This first goldset contains 10 records:

- `01.0001` भू
- `01.0002` एध्
- `02.0001` अद्
- `03.0001` हु
- `04.0001` दिव्
- `06.0001` तुद्
- `07.0001` रुध्
- `08.0001` तनु
- `09.0001` क्री
- `10.0001` चुर्

`expected_records.v1.json` must match the canonical records exactly. `expected_prakriya_refs.v1.json` stores referee trace stubs for deterministic goldset lookups; it is not a full derivation generator.

Node 20C adds a Prakriya Referee layer that resolves canonical forms and stable trace references from existing data. Full sutra execution and trace normalization will be refined later in Node 20C.1.

`semantic_enrichment.v1.json` is a semantic overlay for the goldset, not canonical grammar data. It must not mutate or replace records in `data/sanskrit/dhatus/`; it only adds reviewable, machine-readable labels for regression and future query/referee work.

Bija, chakra, mantra, sonic, deity, mandala, and 49D vector layers belong to separate future registries and must not be added to the dhatu goldset overlay.
