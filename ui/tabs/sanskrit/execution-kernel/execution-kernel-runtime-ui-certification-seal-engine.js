"use strict";

const {
  buildRuntimeUiCertificationSealRecord,
  normalizeRuntimeUiCertificationSealRecord
} = require("./execution-kernel-runtime-ui-certification-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiCertificationSealEntries(record = {}) {
  const entries = [
    "runtime-ui-certification-surface",
    "runtime-ui-governance-reference",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-certification-reference",
    "runtime-controller-reference",

    "certification-inspection-only",
    "certification-evidence-immutable",

    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-ui-certification");
  }

  return freeze(entries);
}

function createRuntimeUiCertificationSealRecord(record = {}) {
  const entries = deriveRuntimeUiCertificationSealEntries(record);

  return buildRuntimeUiCertificationSealRecord({
    ...record,

    uiCertificationSealStatus: "ui-certification-seal-ready",
    uiCertificationSealMode: "inspection-ui-certification-seal",

    certificationSealEntryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    certificationSealEntries: entries,

    diagnostics: {
      readOnly: true,

      certificationSealBlocked: true,
      governanceSealBlocked: true,
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
      certificationMetadataOnly: true
    }
  });
}

function inspectRuntimeUiCertificationSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiCertificationSealRecord(record);

  return freeze({
    readOnly: true,

    entryCount: normalized.certificationSealEntries.length,

    certificationSealBlocked: true,
    governanceSealBlocked: true,
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

function compareRuntimeUiCertificationSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiCertificationSealEntries,
  createRuntimeUiCertificationSealRecord,
  inspectRuntimeUiCertificationSealRecord,
  compareRuntimeUiCertificationSealRecords
};