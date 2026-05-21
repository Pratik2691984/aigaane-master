# Canonical Write Approval Package

## Current Release Status

- Release status: `BLOCKED`
- Safe to write production: `false`
- Evidence release gate: `BLOCKED`
- Command status: `REFUSED_APPROVAL_INVALID`

## Authorized Record IDs

- `01.STAGED.0001`
- `01.STAGED.0002`
- `01.STAGED.0003`

## Ready Record IDs

- `01.STAGED.0001`
- `01.STAGED.0002`
- `01.STAGED.0003`

## Records That Would Be Added

- None in the current default package.

## Records Blocked Or Skipped

- `01.STAGED.0001`
- `01.STAGED.0002`
- `01.STAGED.0003`
- `01.STAGED.0004`
- `01.STAGED.0005`
- `01.STAGED.0006`
- `01.STAGED.0007`
- `01.STAGED.0008`
- `01.STAGED.0009`
- `01.STAGED.0010`
- `01.STAGED.0011`
- `01.STAGED.0012`

## Exact Manual Approval Instructions

1. Do not run any command yet.
2. Inspect this package, `canonical_write_release_checklist.v1.json`, and `canonical_write_dry_run_diff.v1.json`.
3. If and only if approving production write, edit `data/sanskrit/ingestion/canonical_write_approval.v1.json`.
4. Set `approvalStatus` to `APPROVED`, set `approvedBy`, set `approvedAt`, and set `approvedRecordIds` to exactly the authorized ready IDs.
5. Commit the approval edit before running any production write command.
6. Regenerate approval validation, command manifest, dry-run diff, release checklist, and this package.

## Exact Command Sequence After Approval

```powershell
python scripts/validate_dhatu_canonical_write_approval.py
python scripts/prepare_dhatu_canonical_write_command.py
python scripts/diff_dhatu_canonical_write_dry_run.py
python scripts/build_dhatu_canonical_write_release_checklist.py
python scripts/build_dhatu_canonical_write_approval_package.py
$env:AIGAANE_ALLOW_TEST_CANONICAL_WRITE='1'; $env:AIGAANE_ENABLE_CANONICAL_DHATU_WRITE='1'; python scripts/promote_ready_dhatu_to_canonical.py
```

## Warning

No command should be run until human approval is edited, reviewed, and committed. This package does not approve or execute a canonical write.

## Blocking Reasons

- `Approval validation is not valid.`
- `Authorization is not ready for manual write.`
- `Command manifest is not ready for manual execution.`
- `Approval status is not APPROVED.`
- `Approval does not include every authorized ready record id.`
- `Approval token missing approvedBy.`
- `Approval token missing approvedAt.`
- `Approval validation failed.`
- `Authorization packet is not marked AUTHORIZED_FOR_MANUAL_WRITE.`
- `Evidence release gate is not READY_FOR_CONTROLLED_WRITE.`
- `Approved record ids do not match authorized ready record ids.`
- `Required environment guard is not currently satisfied: AIGAANE_ALLOW_TEST_CANONICAL_WRITE.`
- `Required environment guard is not currently satisfied: AIGAANE_ENABLE_CANONICAL_DHATU_WRITE.`
- `Command manifest is not READY_FOR_MANUAL_EXECUTION.`
