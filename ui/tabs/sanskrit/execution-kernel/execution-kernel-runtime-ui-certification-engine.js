"use strict";

const {
  buildRuntimeUiCertificationRecord,
  normalizeRuntimeUiCertificationRecord
} = require("./execution-kernel-runtime-ui-certification-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiCertificationEntries(record = {}) {
  const certificationEntries = [
    "runtime-ui-certification-surface",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-controller-reference",
    "runtime-panel-reference",
    "runtime-view-reference",
    "runtime-session-reference",
    "runtime-readonly-reference",
    "ui-certification-inspection-only",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    certificationEntries.push("warning-reference-ui-certification");
  }

  return freeze(certificationEntries);
}

function createRuntimeUiCertificationRecord(record = {}) {
  const certificationEntries = deriveRuntimeUiCertificationEntries(record);

  return buildRuntimeUiCertificationRecord({
    ...record,

    uiCertificationStatus: "ui-certification-ready",
    uiCertificationMode: "inspection-ui-certification",

    certificationEntryCount: certificationEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    certificationEntries,

    diagnostics: {
      readOnly: true,
      uiCertificationBlocked: true,
      certificationBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiCertificationMetadataOnly: true
    }
  });
}

function inspectRuntimeUiCertificationRecord(record = {}) {
  const normalized = normalizeRuntimeUiCertificationRecord(record);

  return freeze({
    readOnly: true,
    certificationEntryCount: normalized.certificationEntries.length,
    uiCertificationBlocked: true,
    certificationBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiCertificationRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiCertificationEntries,
  createRuntimeUiCertificationRecord,
  inspectRuntimeUiCertificationRecord,
  compareRuntimeUiCertificationRecords
};