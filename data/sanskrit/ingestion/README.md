# Dhātupāṭha Ingestion Framework

`scripts/preview_dhatu_batch_promotion.py` builds a dry-run-only promotion preview from staged batch JSON after the large-scale validator passes. It writes only `data/sanskrit/ingestion/promotion_preview.v1.json`, reports staged totals and duplicate candidate risks, and does not modify canonical dhatu, goldset, or staged batch files.

`scripts/plan_dhatu_canonical_promotion.py` converts that preview into a deterministic canonical promotion plan at `data/sanskrit/ingestion/canonical_promotion_plan.v1.json`. It assigns proposed canonical ids only inside the plan, classifies staged records as ready, needs-review, or blocked, and leaves canonical registry and goldset files untouched.

`scripts/apply_dhatu_review_decisions.py` applies explicit local decisions from `review_decisions.v1.json` and writes only `canonical_promotion_plan.reviewed.v1.json`. Missing decisions default to defer, rejected records become blocked, and no review decision promotes or mutates canonical dhatu files.

`scripts/lock_dhatu_promotion_readiness.py` snapshots reviewed readiness into `promotion_readiness_lock.v1.json`. It lists ready, deferred, and blocked staged root ids while keeping `canonicalWriteEnabled` false; promotion remains a later explicit workflow.

`scripts/promote_ready_dhatu_to_canonical.py` is the final controlled writer gate. By default it refuses canonical writes, emits `canonical_promotion_audit.v1.json`, and requires `AIGAANE_ENABLE_CANONICAL_DHATU_WRITE=1` before any ready staged id can be considered for canonical promotion. The enabled path still refuses mutation unless the second guard `AIGAANE_ALLOW_TEST_CANONICAL_WRITE=1` is also present; this is intended for temporary copied registry fixtures only until production canonical mutation is separately approved. The audit records guard status, before/after registry counts, and contract checks for duplicate ids, unsafe overwrites, staged-batch presence, review approval, and readiness-lock membership.

`scripts/report_dhatu_promotion_evidence.py` compiles the release evidence from the manifest, preview, canonical promotion plan, review decisions, readiness lock, and canonical promotion audit. It writes `dhatu_promotion_evidence_report.v1.json` with counts, guard policy, contract summary, ready/skipped ids, and a release gate status. The current default status remains `BLOCKED` until both canonical write guards are satisfied.

`scripts/authorize_dhatu_canonical_write.py` prepares the final production-write authorization packet from the canonical promotion audit, evidence report, readiness lock, and approval validation. It writes `canonical_write_authorization.v1.json` with required environment flags, authorized ready ids, blocked non-ready ids, evidence summary, approval validation summary, and safety checks. The status advances to `AUTHORIZED_FOR_MANUAL_WRITE` only when approval validation is valid, approved ids exactly match authorized ready ids, and evidence/release gates are ready; otherwise it remains `AWAITING_HUMAN_APPROVAL`. This node does not set environment flags or mutate the production canonical registry.

`canonical_write_approval.v1.json` is the human approval token and defaults to `NOT_APPROVED`. `scripts/prepare_dhatu_canonical_write_command.py` reads that token plus approval validation, authorization, readiness lock, and evidence report, then writes `canonical_write_command_manifest.v1.json`. The command manifest previews exact PowerShell and cmd controlled writer commands but refuses by default with `REFUSED_APPROVAL_INVALID`; it does not run the writer, set environment flags, or mutate canonical files.

`scripts/validate_dhatu_canonical_write_approval.py` validates the human approval token against the authorization, readiness lock, and evidence report before any command can be treated as executable. It writes `canonical_write_approval_validation.v1.json`, requires approved ids to stay within the authorized ready ids, and fails approved tokens that contain no approved records. The default token validates as `NOT_APPROVED` and invalid.

`scripts/simulate_dhatu_canonical_write_approval.py` writes `canonical_write_approval.simulated.v1.json`, a `testOnly` approval fixture whose approved ids mirror the authorized ready ids. It exists only to prove the approval -> validation -> command-manifest chain can become ready under explicit test paths; it must not overwrite `canonical_write_approval.v1.json` or trigger canonical mutation.

`scripts/diff_dhatu_canonical_write_dry_run.py` writes `canonical_write_dry_run_diff.v1.json`, a deterministic dry-run report of records the guarded writer would add. It reads the command manifest, approval validation, readiness lock, promotion preview, promotion plan, and current canonical index, then reports before/after counts, additions, blocked records, duplicate ids, and contract checks without mutating canonical files.

`scripts/build_dhatu_canonical_write_release_checklist.py` writes `canonical_write_release_checklist.v1.json`, the final rollup of every canonical-write gate. It remains `BLOCKED` and `safeToWriteProduction: false` unless approval validation, authorization, command manifest, and dry-run diff are all green.

`scripts/build_dhatu_canonical_write_approval_package.py` writes `canonical_write_approval_package.v1.md`, a human-readable maintainer package summarizing release status, authorized and ready ids, dry-run additions and blocked records, exact approval instructions, and the post-approval command sequence. It warns that no command should be run until human approval is edited and committed.

`scripts/verify_dhatu_canonical_write_release.py` writes `canonical_write_release_verification.v1.json`, the final consistency check over authorization, approval, approval validation, command manifest, dry-run diff, release checklist, approval package, readiness lock, and manifest. The default verification remains `BLOCKED` and `safeToProceed: false`.

`scripts/snapshot_dhatu_pre_canonical_write_state.py` writes `canonical_write_preflight_snapshot.v1.json`, a non-mutating snapshot of git head, branch, canonical registry count and hash, approval status, command status, verification status, ready ids, dry-run additions, and rollback reference before any production write can be considered. The default snapshot remains `BLOCKED_PREWRITE`.

`scripts/verify_dhatu_post_canonical_write_audit.py` writes `canonical_write_post_audit_verification.v1.json`, a post-write audit integrity check that compares the preflight snapshot, promotion audit, dry-run diff, and canonical registry hash/count. It is exercised only against test or temporary registries until a production write is explicitly approved.

`canonical_write_runbook.v1.md` is the final maintainer runbook for the manual production-write process. It documents the blocked default state, gate order, required review files, human approval edit process, post-approval commands, rollback reference, post-write audit verification, and exact v29-through-v43 tag sequence without changing approval or canonical registry files.

`scripts/index_dhatu_canonical_promotion_closeout.py` writes `canonical_promotion_closeout_index.v1.json`, a non-mutating index of the canonical promotion closeout package. It records required artifact paths, existence checks, gate statuses, blocking reasons, and the recommended next action while keeping the default state blocked/no production write.

`fixtures/baseline_blocked/` stores immutable blocked-state copies of the canonical write gate artifacts for regression tests. `fixtures/executed_write/` stores the approved/executed artifact state captured after the production promotion commit, so tests can distinguish historical safety defaults from the current live repository state.

`scripts/archive_dhatu_release_state.py` copies the completed v50 canonical promotion state into `releases/v50/` without mutating the canonical registry. It writes immutable v50 snapshots, computes artifact SHA-256 hashes, refuses overwrite unless `--force` is supplied, and records merge-readiness metadata in `release_archive_manifest.v50.json`.

`scripts/report_dhatu_merge_readiness.py` writes `releases/v50/merge_readiness_report.v50.json`, a PR-facing merge-readiness summary for merging `release/dhatu-canonical-write-approval` into `feature/dhatu-goldset`. It verifies the v50/v51 tag references, fixture integrity, 13-record canonical registry, three promoted records, post-write verification, and duplicate-id safety.

`data/sanskrit/dhatus/semantic/` contains a read-only semantic sidecar foundation for canonical dhatu records. `scripts/validate_dhatu_semantic_layer.py` verifies that semantic ids exist in the canonical registry, action vectors reference known semantic clusters, the three promoted roots are covered, manifest counts match, and `data/sanskrit/dhatus/index.json` is not mutated.

`scripts/query_dhatu_semantics.py` and `api/dhatu_semantic_query.py` provide read-only semantic lookup over the canonical dhatu sidecar layer. They support dhatu id, Devanagari root, IAST, semantic cluster, gloss, and action-vector queries while filtering every result back through the canonical registry.

`api/kernel_api.py` exposes the same semantic query engine through `/api/dhatu/semantic/search`, with `scripts/smoke_dhatu_semantic_api.py` covering direct helper calls without starting a server.

`data/sanskrit/dhatus/semantic/SEMANTIC_API.md` documents semantic query usage, and `scripts/export_dhatu_semantic_examples.py` regenerates deterministic response fixtures under `data/sanskrit/dhatus/semantic/examples/`.

`data/sanskrit/dhatus/semantic/edges/semantic_edges.v1.json` adds a safe placeholder graph for dhatu semantic relationships. `scripts/validate_dhatu_semantic_graph.py` and `scripts/query_dhatu_semantic_neighbors.py` validate and traverse this graph without making exact grammatical or Paninian derivation claims.

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
