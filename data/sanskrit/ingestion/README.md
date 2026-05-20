# Dhātupāṭha Ingestion Framework

`scripts/preview_dhatu_batch_promotion.py` builds a dry-run-only promotion preview from staged batch JSON after the large-scale validator passes. It writes only `data/sanskrit/ingestion/promotion_preview.v1.json`, reports staged totals and duplicate candidate risks, and does not modify canonical dhatu, goldset, or staged batch files.

`scripts/plan_dhatu_canonical_promotion.py` converts that preview into a deterministic canonical promotion plan at `data/sanskrit/ingestion/canonical_promotion_plan.v1.json`. It assigns proposed canonical ids only inside the plan, classifies staged records as ready, needs-review, or blocked, and leaves canonical registry and goldset files untouched.

`scripts/apply_dhatu_review_decisions.py` applies explicit local decisions from `review_decisions.v1.json` and writes only `canonical_promotion_plan.reviewed.v1.json`. Missing decisions default to defer, rejected records become blocked, and no review decision promotes or mutates canonical dhatu files.

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

`promotion_batches.v1.json` coordinates actual approved promotion runs. It does not approve candidates itself; approval remains in `verified_promotions.v1.json`, while canonical preference, editorial, recension, and source attribution layers provide cross-checks. Batch execution defaults to dry-run and requires `--write` for any canonical mutation through the existing safe promotion path.

Node 22A prepares large-scale ingestion only. `large_scale_manifest.v1.json` and the gaṇa-wise folders under `raw/dhatupatha_batches/` are local-only staging zones for future reviewed intake; no bulk canonical import happens in this node. Canonical mutation remains gated by verified promotion and approved promotion batch workflows.

`raw/dhatupatha_controlled_batch_01.csv` is a validation-ready controlled expansion batch. It should be dry-run first and should not be written into the canonical registry until its ids, gaṇa assignments, and philological details are reviewed.
