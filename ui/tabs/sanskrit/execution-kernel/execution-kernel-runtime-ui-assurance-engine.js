"use strict";

const {
  buildRuntimeUiAssuranceRecord,
  normalizeRuntimeUiAssuranceRecord
} = require("./execution-kernel-runtime-ui-assurance-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiAssuranceEntries(record = {}) {
  const assuranceEntries = [
    "runtime-ui-assurance-surface",
    "runtime-ui-integrity-reference",
    "runtime-ui-governance-reference",
    "runtime-ui-certification-reference",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-controller-reference",
    "runtime-panel-reference",
    "runtime-readonly-reference",
    "ui-assurance-inspection-only",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    assuranceEntries.push("warning-reference-ui-assurance");
  }

  return freeze(assuranceEntries);
}

function createRuntimeUiAssuranceRecord(record = {}) {
  const assuranceEntries = deriveRuntimeUiAssuranceEntries(record);

  return buildRuntimeUiAssuranceRecord({
    ...record,

    uiAssuranceStatus: "ui-assurance-ready",
    uiAssuranceMode: "inspection-ui-assurance",

    assuranceEntryCount: assuranceEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    assuranceEntries,

    diagnostics: {
      readOnly: true,
      uiAssuranceBlocked: true,
      assuranceBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiAssuranceMetadataOnly: true
    }
  });
}

function inspectRuntimeUiAssuranceRecord(record = {}) {
  const normalized = normalizeRuntimeUiAssuranceRecord(record);

  return freeze({
    readOnly: true,
    assuranceEntryCount: normalized.assuranceEntries.length,
    uiAssuranceBlocked: true,
    assuranceBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiAssuranceRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiAssuranceEntries,
  createRuntimeUiAssuranceRecord,
  inspectRuntimeUiAssuranceRecord,
  compareRuntimeUiAssuranceRecords
};