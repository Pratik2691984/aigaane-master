"use strict";

const UI_IMPORT_SEAL_SCHEMA = "sanskrit-runtime-ui-import-seal.v1";

const UI_IMPORT_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_IMPORT_SEAL_READY: "UI_IMPORT_SEAL_READY",
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

function normalizeRuntimeUiImportSealRecord(input = {}) {
  return freeze({
    uiImportSealId: String(input.uiImportSealId || "runtime-ui-import-seal"),
    createdAt: String(input.createdAt || "static"),

    sourceExportSealId: String(input.sourceExportSealId || "runtime-ui-export-seal"),
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

    uiImportSealStatus: String(input.uiImportSealStatus || "ui-import-seal-ready"),
    uiImportSealMode: String(input.uiImportSealMode || "inspection-ui-import-seal"),

    importSealAllowed: false,
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

    importSealEntryCount: asCount(input.importSealEntryCount),
    warningCount: asCount(input.warningCount),

    importSealEntries: freeze(
      Array.isArray(input.importSealEntries) ? input.importSealEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiImportSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiImportSealRecord(input);

  return freeze({
    schemaVersion: UI_IMPORT_SEAL_SCHEMA,
    state: normalized.importSealEntries.length
      ? UI_IMPORT_SEAL_STATES.UI_IMPORT_SEAL_READY
      : UI_IMPORT_SEAL_STATES.EMPTY,
    ...normalized
  });
}

module.exports = {
  UI_IMPORT_SEAL_SCHEMA,
  UI_IMPORT_SEAL_STATES,
  normalizeRuntimeUiImportSealRecord,
  buildRuntimeUiImportSealRecord
};