# Dhātupāṭha Ingestion Framework

`scripts/preview_dhatu_batch_promotion.py` builds a dry-run-only promotion preview from staged batch JSON after the large-scale validator passes. It writes only `data/sanskrit/ingestion/promotion_preview.v1.json`, reports staged totals and duplicate candidate risks, and does not modify canonical dhatu, goldset, or staged batch files.

`scripts/plan_dhatu_canonical_promotion.py` converts that preview into a deterministic canonical promotion plan at `data/sanskrit/ingestion/canonical_promotion_plan.v1.json`. It assigns proposed canonical ids only inside the plan, classifies staged records as ready, needs-review, or blocked, and leaves canonical registry and goldset files untouched.

`scripts/apply_dhatu_review_decisions.py` applies explicit local decisions from `review_decisions.v1.json` and writes only `canonical_promotion_plan.reviewed.v1.json`. Missing decisions default to defer, rejected records become blocked, and no review decision promotes or mutates canonical dhatu files.

`scripts/lock_dhatu_promotion_readiness.py` snapshots reviewed readiness into `promotion_readiness_lock.v1.json`. It lists ready, deferred, and blocked staged root ids while keeping `canonicalWriteEnabled` false; promotion remains a later explicit workflow.

`scripts/promote_ready_dhatu_to_canonical.py` is the final controlled writer gate. By default it refuses canonical writes, emits `canonical_promotion_audit.v1.json`, and requires `AIGAANE_ENABLE_CANONICAL_DHATU_WRITE=1` before any ready staged id can be considered for canonical promotion. The enabled path still refuses mutation unless the second guard `AIGAANE_ALLOW_TEST_CANONICAL_WRITE=1` is also present; this is intended for temporary copied registry fixtures only until production canonical mutation is separately approved. The audit records guard status, before/after registry counts, and contract checks for duplicate ids, unsafe overwrites, staged-batch presence, review approval, and readiness-lock membership.

`scripts/report_dhatu_promotion_evidence.py` compiles the release evidence from the manifest, preview, canonical promotion plan, review decisions, readiness lock, and canonical promotion audit. It writes `dhatu_promotion_evidence_report.v1.json` with counts, guard policy, contract summary, ready/skipped ids, and a release gate status. The current default status remains `BLOCKED` until both canonical write guards are satisfied.

`scripts/authorize_dhatu_canonical_write.py` prepares the final production-write authorization packet from the canonical promotion audit, evidence report, and readiness lock. It writes `canonical_write_authorization.v1.json` with required environment flags, authorized ready ids, blocked non-ready ids, evidence summary, and safety checks. This node does not set environment flags or mutate the production canonical registry; the default authorization status remains `AWAITING_HUMAN_APPROVAL`.

`canonical_write_approval.v1.json` is the human approval token and defaults to `NOT_APPROVED`. `scripts/prepare_dhatu_canonical_write_command.py` reads that token plus the authorization, readiness lock, and evidence report, then writes `canonical_write_command_manifest.v1.json`. The command manifest previews the controlled writer command but refuses by default with `REFUSED_NOT_APPROVED`; it does not run the writer or mutate canonical files.

`scripts/validate_dhatu_canonical_write_approval.py` validates the human approval token against the authorization, readiness lock, and evidence report before any command can be treated as executable. It writes `canonical_write_approval_validation.v1.json`, requires approved ids to stay within the authorized ready ids, and fails approved tokens that contain no approved records. The default token validates as `NOT_APPROVED` and invalid.

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
