# Dhātupāṭha Ingestion Framework

Dhātupāṭha ingestion is staged, local-only, and governed. The importer must use local files under `raw/`; code in this repository must not scrape online sources.

Every batch must run in dry-run mode before write mode. Write mode goes through the existing dhātu importer, rebuilds `data/sanskrit/dhatus/index.json`, and writes a batch report under `data/sanskrit/ingestion/reports/`.

The goldset protects canonical truth while ingestion expands normal registry coverage. Goldset expected records live separately under `data/sanskrit/goldset/` and must continue to pass exact regression checks after every batch.

Recommended staged path:

- `21A.1`: 25-50 records
- `21A.2`: around 250 records
- `21A.3`: full gaṇa-by-gaṇa coverage
- `21A.4`: complete dhātupāṭha

Large ingestion should proceed by small, reviewable batches with reports committed only when intentionally promoted.

`source_attribution.v1.json` tracks local provenance for ingestion and promotion decisions. It uses a lightweight entity/activity/agent model inspired by provenance systems, but it remains plain local JSON with no external dependency. This attribution layer does not mutate canonical dhatu records and does not grant promotion approval by itself; verified promotion still depends on the separate review manifest and importer validation.

`recensions.v1.json` stores local variant and recension readings for dhatu review. It separates attested readings, alternate upadesha forms, alternate meanings, ordering questions, and editorial notes from canonical registry truth. This file is a read-only review aid, not a promotion mechanism. Promotion still happens only through `verified_promotions.v1.json` and `scripts/promote_verified_dhatus.py`.

`editorial_resolutions.v1.json` records editorial decisions and recommendations only. It provides review rationale, evidence scoring, and reversible machine-readable actions for variant readings, but it does not promote or mutate canonical dhatu records. Promotion still happens only through `verified_promotions.v1.json` and `scripts/promote_verified_dhatus.py`.

`canonical_preferences.v1.json` stores deterministic canonical preference recommendations resolved from recensions, editorial decisions, source attribution, and verified promotion metadata. It is read-only, keeps auto-promotion disabled, and does not mutate canonical dhatu JSON.

`raw/dhatupatha_controlled_batch_01.csv` is a validation-ready controlled expansion batch. It should be dry-run first and should not be written into the canonical registry until its ids, gaṇa assignments, and philological details are reviewed.
