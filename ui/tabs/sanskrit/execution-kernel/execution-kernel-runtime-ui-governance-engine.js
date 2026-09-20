"use strict";

const {
  buildRuntimeUiGovernanceRecord,
  normalizeRuntimeUiGovernanceRecord
} = require("./execution-kernel-runtime-ui-governance-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiGovernanceEntries(record = {}) {
  const governanceEntries = [
    "runtime-ui-governance-surface",
    "runtime-ui-certification-reference",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-controller-reference",
    "runtime-panel-reference",
    "runtime-view-reference",
    "runtime-session-reference",
    "runtime-readonly-reference",
    "ui-governance-inspection-only",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    governanceEntries.push("warning-reference-ui-governance");
  }

  return freeze(governanceEntries);
}

function createRuntimeUiGovernanceRecord(record = {}) {
  const governanceEntries = deriveRuntimeUiGovernanceEntries(record);

  return buildRuntimeUiGovernanceRecord({
    ...record,

    uiGovernanceStatus: "ui-governance-ready",
    uiGovernanceMode: "inspection-ui-governance",

    governanceEntryCount: governanceEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    governanceEntries,

    diagnostics: {
      readOnly: true,
      uiGovernanceBlocked: true,
      governanceBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiGovernanceMetadataOnly: true
    }
  });
}

function inspectRuntimeUiGovernanceRecord(record = {}) {
  const normalized = normalizeRuntimeUiGovernanceRecord(record);

  return freeze({
    readOnly: true,
    governanceEntryCount: normalized.governanceEntries.length,
    uiGovernanceBlocked: true,
    governanceBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiGovernanceRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiGovernanceEntries,
  createRuntimeUiGovernanceRecord,
  inspectRuntimeUiGovernanceRecord,
  compareRuntimeUiGovernanceRecords
};