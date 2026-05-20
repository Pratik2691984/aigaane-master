# Aigaane Sanskrit Goldset

This directory contains frozen expected data for regression checks against the canonical Sanskrit registries.

The first goldset seeds only two dhatus:

- `01.0001` भू / भवति
- `01.0002` एध् / एधते

The records in `expected_records.v1.json` are copied from `data/sanskrit/dhatus/01_bhvadi.json`. Tests compare them back to the canonical registry so changes to curated dhatu data are deliberate and visible.

`expected_prakriya_refs.v1.json` is intentionally a stub for now.
