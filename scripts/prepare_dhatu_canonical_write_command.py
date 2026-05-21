#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import ROOT


DEFAULT_AUTHORIZATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_authorization.v1.json"
)
DEFAULT_APPROVAL_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval.v1.json"
DEFAULT_APPROVAL_VALIDATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval_validation.v1.json"
)
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_EVIDENCE_REPORT_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "dhatu_promotion_evidence_report.v1.json"
)
DEFAULT_COMMAND_MANIFEST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_command_manifest.v1.json"
)


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def display_path(path: Any) -> str:
    resolved = resolve_path(path)
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def load_json(path: Any) -> Dict[str, Any]:
    resolved = resolve_path(path)
    with resolved.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Command manifest source must be a JSON object: {display_path(resolved)}")
    return payload


def build_refusal_reasons(
    authorization: Dict[str, Any],
    approval: Dict[str, Any],
    approval_validation: Dict[str, Any],
    evidence: Dict[str, Any],
    approved_record_ids: List[str],
) -> List[str]:
    reasons: List[str] = []
    if approval_validation.get("approvalValid") is not True:
        reasons.append("Approval validation failed.")
        reasons.extend(approval_validation.get("refusalReasons", []))
    if authorization.get("authorizationStatus") != "AUTHORIZED_FOR_MANUAL_WRITE":
        reasons.append("Authorization packet is not marked AUTHORIZED_FOR_MANUAL_WRITE.")
    if evidence.get("releaseGateStatus") != "READY_FOR_CONTROLLED_WRITE":
        reasons.append("Evidence release gate is not READY_FOR_CONTROLLED_WRITE.")
    if sorted(approved_record_ids) != sorted(authorization.get("authorizedRecordIds", [])):
        reasons.append("Approved record ids do not match authorized ready record ids.")
    for name, requirement in sorted(authorization.get("requiredEnvironment", {}).items()):
        if requirement.get("currentlySatisfied") is not True:
            reasons.append(f"Required environment guard is not currently satisfied: {name}.")
    return list(dict.fromkeys(reasons))


def authorization_is_ready(authorization: Dict[str, Any]) -> bool:
    return authorization.get("authorizationStatus") == "AUTHORIZED_FOR_MANUAL_WRITE"


def build_command_status(approval_validation: Dict[str, Any], authorization: Dict[str, Any]) -> str:
    if approval_validation.get("approvalValid") is not True:
        return "REFUSED_APPROVAL_INVALID"
    if not authorization_is_ready(authorization):
        return "REFUSED_AUTHORIZATION_NOT_READY"
    return "READY_FOR_MANUAL_EXECUTION"


def build_required_environment(authorization: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return authorization.get("requiredEnvironment", {})


def build_command_preview(required_environment: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    env = {name: requirement.get("requiredValue", "1") for name, requirement in sorted(required_environment.items())}
    exact_powershell = "; ".join([f"$env:{name}='{value}'" for name, value in env.items()])
    exact_powershell = f"{exact_powershell}; python scripts/promote_ready_dhatu_to_canonical.py"
    exact_cmd = " && ".join([f"set {name}={value}" for name, value in env.items()])
    exact_cmd = f"{exact_cmd} && python scripts\\promote_ready_dhatu_to_canonical.py"
    return {
        "description": "Preview only. This manifest does not execute the canonical writer.",
        "environment": env,
        "argv": [
            "python",
            "scripts/promote_ready_dhatu_to_canonical.py",
        ],
        "powershellPreview": exact_powershell,
        "cmdPreview": exact_cmd,
    }


def build_approval_validation_summary(approval_validation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "approvalStatus": approval_validation.get("approvalStatus"),
        "approvalValid": approval_validation.get("approvalValid") is True,
        "approvedCount": len(approval_validation.get("approvedRecordIds", [])),
        "missingAuthorizedCount": len(approval_validation.get("missingAuthorizedRecordIds", [])),
        "unexpectedApprovedCount": len(approval_validation.get("unexpectedApprovedRecordIds", [])),
        "refusalCount": len(approval_validation.get("refusalReasons", [])),
    }


def build_authorization_summary(authorization: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "authorizationStatus": authorization.get("authorizationStatus"),
        "authorizationReady": authorization_is_ready(authorization),
        "authorizedCount": len(authorization.get("authorizedRecordIds", [])),
        "blockedCount": len(authorization.get("blockedRecordIds", [])),
        "humanApprovalRequired": authorization.get("humanApprovalRequired") is True,
    }


def build_safety_checks(
    authorization: Dict[str, Any],
    approval: Dict[str, Any],
    approval_validation: Dict[str, Any],
    readiness_lock: Dict[str, Any],
    evidence: Dict[str, Any],
    approved_record_ids: List[str],
) -> Dict[str, Any]:
    authorized_ids = sorted(authorization.get("authorizedRecordIds", []))
    ready_ids = sorted(readiness_lock.get("readyRecordIds", []))
    return {
        "writerExecuted": False,
        "canonicalRegistryMutation": False,
        "goldsetMutation": False,
        "batchMutation": False,
        "approvalTokenApproved": approval.get("approvalStatus") == "APPROVED",
        "approvalValidationValid": approval_validation.get("approvalValid") is True,
        "approvalMetadataPresent": bool(approval.get("approvedBy")) and bool(approval.get("approvedAt")),
        "approvedIdsMatchAuthorization": sorted(approved_record_ids) == authorized_ids,
        "authorizedIdsMatchReadinessLock": authorized_ids == ready_ids,
        "authorizationReady": authorization_is_ready(authorization),
        "authorizationHumanApprovalRequired": authorization.get("humanApprovalRequired") is True,
        "evidenceReleaseGateReady": evidence.get("releaseGateStatus") == "READY_FOR_CONTROLLED_WRITE",
    }


def build_command_manifest(
    authorization_path: Any = DEFAULT_AUTHORIZATION_PATH,
    approval_path: Any = DEFAULT_APPROVAL_PATH,
    approval_validation_path: Any = DEFAULT_APPROVAL_VALIDATION_PATH,
    readiness_lock_path: Any = DEFAULT_READINESS_LOCK_PATH,
    evidence_path: Any = DEFAULT_EVIDENCE_REPORT_PATH,
) -> Dict[str, Any]:
    authorization = load_json(authorization_path)
    approval = load_json(approval_path)
    approval_validation = load_json(approval_validation_path)
    readiness_lock = load_json(readiness_lock_path)
    evidence = load_json(evidence_path)
    approved_record_ids = sorted(approval_validation.get("approvedRecordIds", []))
    refusal_reasons = build_refusal_reasons(
        authorization,
        approval,
        approval_validation,
        evidence,
        approved_record_ids,
    )
    required_environment = build_required_environment(authorization)
    command_preview = build_command_preview(required_environment)
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/prepare_dhatu_canonical_write_command.py",
        "commandStatus": build_command_status(approval_validation, authorization),
        "commandPreview": command_preview,
        "approvalValidationSummary": build_approval_validation_summary(approval_validation),
        "authorizationSummary": build_authorization_summary(authorization),
        "exactPowerShellCommand": command_preview["powershellPreview"],
        "exactCmdCommand": command_preview["cmdPreview"],
        "requiredEnvironment": required_environment,
        "approvedRecordIds": approved_record_ids,
        "blockedRecordIds": sorted(set(readiness_lock.get("readyRecordIds", [])) - set(approved_record_ids))
        + sorted(authorization.get("blockedRecordIds", [])),
        "safetyChecks": build_safety_checks(
            authorization,
            approval,
            approval_validation,
            readiness_lock,
            evidence,
            approved_record_ids,
        ),
        "refusalReasons": refusal_reasons,
    }


def write_command_manifest(manifest: Dict[str, Any], path: Any = DEFAULT_COMMAND_MANIFEST_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(manifest: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "commandStatus": manifest["commandStatus"],
        "approvedCount": len(manifest["approvedRecordIds"]),
        "blockedCount": len(manifest["blockedRecordIds"]),
        "refusalCount": len(manifest["refusalReasons"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a dry command manifest for canonical dhatu write.")
    parser.add_argument("--authorization", default=str(DEFAULT_AUTHORIZATION_PATH))
    parser.add_argument("--approval", default=str(DEFAULT_APPROVAL_PATH))
    parser.add_argument(
        "--approval-validation",
        "--approval-validation-file",
        dest="approval_validation",
        default=str(DEFAULT_APPROVAL_VALIDATION_PATH),
    )
    parser.add_argument("--readiness-lock", default=str(DEFAULT_READINESS_LOCK_PATH))
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_REPORT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_COMMAND_MANIFEST_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        manifest = build_command_manifest(
            args.authorization,
            args.approval,
            args.approval_validation,
            args.readiness_lock,
            args.evidence,
        )
        write_command_manifest(manifest, args.output)
        print(json.dumps(build_summary(manifest), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical write command manifest failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
