# Canonical Write Runbook v1

## Purpose

This runbook is the maintainer-facing operating guide for a future controlled production canonical dhatu write. It explains the gate order, review files, approval edit, command sequence, rollback reference, and post-write audit verification required before any production canonical registry mutation is considered.

## Current Default State

The current default state is blocked/no production write. `canonical_write_approval.v1.json` remains `NOT_APPROVED`, approval validation remains invalid, the command manifest remains refused, and production canonical registry files must remain unchanged.

## Required Warning

WARNING: Do not set `AIGAANE_ENABLE_CANONICAL_DHATU_WRITE` or `AIGAANE_ALLOW_TEST_CANONICAL_WRITE`, and do not run `scripts/promote_ready_dhatu_to_canonical.py`, before approval validation and release verification are READY and the human approval edit has been reviewed and committed.

## Full Gate Order

1. Build or review `promotion_readiness_lock.v1.json`.
2. Confirm `canonical_promotion_audit.v1.json` records no default production write.
3. Build or review `dhatu_promotion_evidence_report.v1.json`.
4. Build or review `canonical_write_authorization.v1.json`.
5. Review `canonical_write_approval.v1.json`; it must remain `NOT_APPROVED` until a maintainer explicitly edits it.
6. Run approval validation and review `canonical_write_approval_validation.v1.json`.
7. Prepare the command manifest and review `canonical_write_command_manifest.v1.json`.
8. Review the dry-run diff in `canonical_write_dry_run_diff.v1.json`.
9. Review the release checklist in `canonical_write_release_checklist.v1.json`.
10. Review the approval package in `canonical_write_approval_package.v1.md`.
11. Run release verification and review `canonical_write_release_verification.v1.json`.
12. Create the pre-write snapshot in `canonical_write_preflight_snapshot.v1.json`.
13. Only after approval validation, command manifest, dry-run diff, checklist, release verification, and pre-write snapshot are ready may a maintainer manually run the guarded writer command.
14. Run post-write audit verification and review `canonical_write_post_audit_verification.v1.json`.

## Required Files To Review

- `data/sanskrit/ingestion/promotion_readiness_lock.v1.json`
- `data/sanskrit/ingestion/canonical_promotion_audit.v1.json`
- `data/sanskrit/ingestion/dhatu_promotion_evidence_report.v1.json`
- `data/sanskrit/ingestion/canonical_write_authorization.v1.json`
- `data/sanskrit/ingestion/canonical_write_approval.v1.json`
- `data/sanskrit/ingestion/canonical_write_approval_validation.v1.json`
- `data/sanskrit/ingestion/canonical_write_command_manifest.v1.json`
- `data/sanskrit/ingestion/canonical_write_dry_run_diff.v1.json`
- `data/sanskrit/ingestion/canonical_write_release_checklist.v1.json`
- `data/sanskrit/ingestion/canonical_write_approval_package.v1.md`
- `data/sanskrit/ingestion/canonical_write_release_verification.v1.json`
- `data/sanskrit/ingestion/canonical_write_preflight_snapshot.v1.json`
- `data/sanskrit/ingestion/canonical_write_post_audit_verification.v1.json`

## Human Approval Edit Process

1. Review the approval package, dry-run diff, release checklist, release verification, and pre-write snapshot.
2. Confirm the authorized record ids match the readiness lock ready ids intended for production write.
3. Edit only `data/sanskrit/ingestion/canonical_write_approval.v1.json`.
4. Set `approvalStatus` to `APPROVED`, fill `approvedBy`, set `approvedAt`, and set `approvedRecordIds` to the approved subset of authorized ids.
5. Commit the approval file change before running any command that sets writer environment flags.
6. Regenerate approval validation, command manifest, dry-run diff, release checklist, approval package, release verification, and pre-write snapshot.
7. Proceed only if approval validation is valid, command status is `READY_FOR_MANUAL_EXECUTION`, release verification is ready, and the pre-write snapshot is safe to proceed.

## Required Commands After Approval

Run these after the human approval edit is committed:

```powershell
python scripts/validate_dhatu_canonical_write_approval.py
python scripts/prepare_dhatu_canonical_write_command.py
python scripts/diff_dhatu_canonical_write_dry_run.py
python scripts/build_dhatu_canonical_write_release_checklist.py
python scripts/build_dhatu_canonical_write_approval_package.py
python scripts/verify_dhatu_canonical_write_release.py
python scripts/snapshot_dhatu_pre_canonical_write_state.py
```

If, and only if, every gate is ready and the approval edit has been reviewed and committed, run the exact command shown in `canonical_write_command_manifest.v1.json`. After the controlled writer command completes, run:

```powershell
python scripts/verify_dhatu_post_canonical_write_audit.py
```

## Rollback Reference

Use `canonical_write_preflight_snapshot.v1.json` as the rollback reference. It records `currentGitHead`, `currentBranch`, canonical registry path, canonical registry record count, canonical registry SHA-256, ready record ids, planned records to add, and blocking reasons. The exact rollback reference should be checked before and after the write, and the production canonical registry hash/count should match the preflight snapshot before the write begins.

## Post-Write Audit Verification

Post-write audit verification is performed by `scripts/verify_dhatu_post_canonical_write_audit.py`. It compares the preflight snapshot, canonical promotion audit, dry-run diff, and canonical registry state. A successful production write must have the expected promoted count, expected record ids, expected before/after count delta, no unexpected registry mutation, and no blocking reasons.

## Exact Tag Sequence

1. `sanskrit-v29-promotion-readiness-lock-stable`
2. `sanskrit-v30-guarded-canonical-promotion-stable`
3. `sanskrit-v31-canonical-promotion-write-guard-stable`
4. `sanskrit-v32-promotion-evidence-report-stable`
5. `sanskrit-v33-canonical-write-authorization-stable`
6. `sanskrit-v34-canonical-write-approval-command-stable`
7. `sanskrit-v35-canonical-write-approval-validation-stable`
8. `sanskrit-v36-command-manifest-validation-gate-stable`
9. `sanskrit-v37-simulated-canonical-write-approval-stable`
10. `sanskrit-v38-canonical-write-dry-run-diff-stable`
11. `sanskrit-v39-canonical-write-release-checklist-stable`
12. `sanskrit-v40-canonical-write-approval-package-stable`
13. `sanskrit-v41-canonical-write-release-verification-stable`
14. `sanskrit-v42-prewrite-snapshot-stable`
15. `sanskrit-v43-post-canonical-write-audit-verification-stable`
