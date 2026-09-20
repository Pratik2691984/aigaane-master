"use strict";

const UI_CERTIFICATION_SEAL_SCHEMA =
  "sanskrit-runtime-ui-certification-seal.v1";

const UI_CERTIFICATION_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_CERTIFICATION_SEAL_READY: "UI_CERTIFICATION_SEAL_READY",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function normalizeRuntimeUiCertificationSealRecord(input = {}) {
  return freeze({
    uiCertificationSealId: String(
      input.uiCertificationSealId || "runtime-ui-certification-seal"
    ),
    createdAt: String(input.createdAt || "static"),

    sourceGovernanceSealId: String(
      input.sourceGovernanceSealId || "runtime-ui-governance-seal"
    ),
    sourceAuditSealId: String(input.sourceAuditSealId || "runtime-ui-audit-seal"),
    sourceReplaySealId: String(input.sourceReplaySealId || "runtime-ui-replay-seal"),
    sourceSnapshotSealId: String(
      input.sourceSnapshotSealId || "runtime-ui-snapshot-seal"
    ),

    uiCertificationSealStatus: String(
      input.uiCertificationSealStatus || "ui-certification-seal-ready"
    ),
    uiCertificationSealMode: String(
      input.uiCertificationSealMode || "inspection-ui-certification-seal"
    ),

    certificationSealAllowed: false,
    governanceSealAllowed: false,
    auditSealAllowed: false,
    replaySealAllowed: false,
    snapshotSealAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    certificationSealEntryCount: asCount(input.certificationSealEntryCount),
    warningCount: asCount(input.warningCount),

    certificationSealEntries: freeze(
      Array.isArray(input.certificationSealEntries)
        ? input.certificationSealEntries
        : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiCertificationSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiCertificationSealRecord(input);

  return freeze({
    schemaVersion: UI_CERTIFICATION_SEAL_SCHEMA,
    state: normalized.certificationSealEntries.length
      ? UI_CERTIFICATION_SEAL_STATES.UI_CERTIFICATION_SEAL_READY
      : UI_CERTIFICATION_SEAL_STATES.EMPTY,
    ...normalized
  });
}

module.exports = {
  UI_CERTIFICATION_SEAL_SCHEMA,
  UI_CERTIFICATION_SEAL_STATES,
  normalizeRuntimeUiCertificationSealRecord,
  buildRuntimeUiCertificationSealRecord
};