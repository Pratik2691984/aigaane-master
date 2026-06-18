"use strict";

const UI_EXPORT_SEAL_SCHEMA = "sanskrit-runtime-ui-export-seal.v1";

const UI_EXPORT_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_EXPORT_SEAL_READY: "UI_EXPORT_SEAL_READY",
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

function normalizeRuntimeUiExportSealRecord(input = {}) {
  return freeze({
    uiExportSealId: String(input.uiExportSealId || "runtime-ui-export-seal"),
    createdAt: String(input.createdAt || "static"),

    sourceCertificationSealId: String(
      input.sourceCertificationSealId || "runtime-ui-certification-seal"
    ),
    sourceGovernanceSealId: String(
      input.sourceGovernanceSealId || "runtime-ui-governance-seal"
    ),
    sourceAuditSealId: String(input.sourceAuditSealId || "runtime-ui-audit-seal"),
    sourceReplaySealId: String(input.sourceReplaySealId || "runtime-ui-replay-seal"),
    sourceSnapshotSealId: String(
      input.sourceSnapshotSealId || "runtime-ui-snapshot-seal"
    ),

    uiExportSealStatus: String(input.uiExportSealStatus || "ui-export-seal-ready"),
    uiExportSealMode: String(input.uiExportSealMode || "inspection-ui-export-seal"),

    exportSealAllowed: false,
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

    exportSealEntryCount: asCount(input.exportSealEntryCount),
    warningCount: asCount(input.warningCount),

    exportSealEntries: freeze(
      Array.isArray(input.exportSealEntries) ? input.exportSealEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiExportSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiExportSealRecord(input);

  return freeze({
    schemaVersion: UI_EXPORT_SEAL_SCHEMA,
    state: normalized.exportSealEntries.length
      ? UI_EXPORT_SEAL_STATES.UI_EXPORT_SEAL_READY
      : UI_EXPORT_SEAL_STATES.EMPTY,
    ...normalized
  });
}

module.exports = {
  UI_EXPORT_SEAL_SCHEMA,
  UI_EXPORT_SEAL_STATES,
  normalizeRuntimeUiExportSealRecord,
  buildRuntimeUiExportSealRecord
};