"use strict";

const {
  buildRuntimeUiAuditSealRecord,
  normalizeRuntimeUiAuditSealRecord
} = require("./execution-kernel-runtime-ui-audit-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiAuditSealEntries(record = {}) {
  const auditSealEntries = [
    "runtime-ui-audit-seal-surface",
    "runtime-ui-replay-seal-reference",
    "runtime-ui-snapshot-seal-reference",
    "runtime-ui-seal-reference",
    "runtime-audit-evidence-reference",
    "runtime-controller-reference",
    "runtime-readonly-reference",
    "ui-audit-seal-inspection-only",
    "ui-audit-seal-immutable",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    auditSealEntries.push("warning-reference-ui-audit-seal");
  }

  return freeze(auditSealEntries);
}

function createRuntimeUiAuditSealRecord(record = {}) {
  const auditSealEntries = deriveRuntimeUiAuditSealEntries(record);

  return buildRuntimeUiAuditSealRecord({
    ...record,

    uiAuditSealStatus: "ui-audit-seal-ready",
    uiAuditSealMode: "inspection-ui-audit-seal",

    auditSealEntryCount: auditSealEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    auditSealEntries,

    diagnostics: {
      readOnly: true,
      immutableAuditSeal: true,
      auditSealBlocked: true,
      replaySealBlocked: true,
      snapshotSealBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiAuditSealMetadataOnly: true,
      sourceLayer: "runtime-ui-replay-seal"
    }
  });
}

function inspectRuntimeUiAuditSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiAuditSealRecord(record);

  return freeze({
    readOnly: true,
    immutableAuditSeal: true,
    auditSealEntryCount: normalized.auditSealEntries.length,
    auditSealBlocked: true,
    replaySealBlocked: true,
    snapshotSealBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiAuditSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiAuditSealEntries,
  createRuntimeUiAuditSealRecord,
  inspectRuntimeUiAuditSealRecord,
  compareRuntimeUiAuditSealRecords
};