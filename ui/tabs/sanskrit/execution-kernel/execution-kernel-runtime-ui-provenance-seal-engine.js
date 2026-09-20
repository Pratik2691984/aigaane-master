"use strict";

const {
  buildRuntimeUiProvenanceSealRecord,
  normalizeRuntimeUiProvenanceSealRecord
} = require("./execution-kernel-runtime-ui-provenance-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiProvenanceSealEntries(record = {}) {
  const entries = [
    "runtime-ui-provenance-surface",

    "runtime-ui-integrity-reference",
    "runtime-ui-registry-reference",
    "runtime-ui-evidence-reference",
    "runtime-ui-ledger-reference",

    "runtime-provenance-reference",

    "provenance-inspection-only",
    "provenance-evidence-immutable",
    "provenance-metadata-only",

    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-ui-provenance");
  }

  return freeze(entries);
}

function createRuntimeUiProvenanceSealRecord(record = {}) {
  const entries = deriveRuntimeUiProvenanceSealEntries(record);

  return buildRuntimeUiProvenanceSealRecord({
    ...record,

    uiProvenanceSealStatus: "ui-provenance-seal-ready",
    uiProvenanceSealMode: "inspection-ui-provenance-seal",

    provenanceSealEntryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    provenanceSealEntries: entries,

    diagnostics: {
      readOnly: true,

      provenanceSealBlocked: true,
      integritySealBlocked: true,
      registrySealBlocked: true,
      evidenceSealBlocked: true,
      ledgerSealBlocked: true,

      provenanceExecutionBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,

      canonicalWriteBlocked: true
    },

    metadata: {
      provenanceMetadataOnly: true
    }
  });
}

function inspectRuntimeUiProvenanceSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiProvenanceSealRecord(record);

  return freeze({
    readOnly: true,

    entryCount: normalized.provenanceSealEntries.length,

    provenanceSealBlocked: true,
    integritySealBlocked: true,
    registrySealBlocked: true,
    evidenceSealBlocked: true,
    ledgerSealBlocked: true,

    provenanceExecutionBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,

    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiProvenanceSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiProvenanceSealEntries,
  createRuntimeUiProvenanceSealRecord,
  inspectRuntimeUiProvenanceSealRecord,
  compareRuntimeUiProvenanceSealRecords
};