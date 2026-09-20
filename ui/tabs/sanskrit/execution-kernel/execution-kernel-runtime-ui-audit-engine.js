"use strict";

const {
  buildRuntimeUiAuditRecord,
  normalizeRuntimeUiAuditRecord
} = require("./execution-kernel-runtime-ui-audit-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiAuditEntries(record = {}) {
  const auditEntries = [
    "runtime-ui-audit-surface",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-controller-reference",
    "runtime-panel-reference",
    "runtime-view-reference",
    "runtime-session-reference",
    "runtime-workspace-reference",
    "runtime-readonly-reference",
    "ui-audit-inspection-only",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    auditEntries.push("warning-reference-ui-audit");
  }

  return freeze(auditEntries);
}

function createRuntimeUiAuditRecord(record = {}) {
  const auditEntries = deriveRuntimeUiAuditEntries(record);

  return buildRuntimeUiAuditRecord({
    ...record,

    uiAuditStatus: "ui-audit-ready",
    uiAuditMode: "inspection-ui-audit",

    auditEntryCount: auditEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    auditEntries,

    diagnostics: {
      readOnly: true,
      uiAuditBlocked: true,
      auditBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiAuditMetadataOnly: true
    }
  });
}

function inspectRuntimeUiAuditRecord(record = {}) {
  const normalized = normalizeRuntimeUiAuditRecord(record);

  return freeze({
    readOnly: true,
    auditEntryCount: normalized.auditEntries.length,
    uiAuditBlocked: true,
    auditBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiAuditRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiAuditEntries,
  createRuntimeUiAuditRecord,
  inspectRuntimeUiAuditRecord,
  compareRuntimeUiAuditRecords
};