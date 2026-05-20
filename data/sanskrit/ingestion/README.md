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

`raw/dhatupatha_controlled_batch_01.csv` is a validation-ready controlled expansion batch. It should be dry-run first and should not be written into the canonical registry until its ids, gaṇa assignments, and philological details are reviewed.
