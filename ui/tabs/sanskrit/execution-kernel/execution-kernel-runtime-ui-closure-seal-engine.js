"use strict";

const {
  buildRuntimeUiClosureSealRecord,
  normalizeRuntimeUiClosureSealRecord
} = require("./execution-kernel-runtime-ui-closure-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiClosureSealEntries(record = {}) {
  const entries = [
    "runtime-ui-closure-surface",

    "runtime-ui-attestation-reference",
    "runtime-ui-provenance-reference",
    "runtime-ui-integrity-reference",
    "runtime-ui-registry-reference",

    "runtime-closure-reference",

    "closure-inspection-only",
    "closure-evidence-immutable",
    "closure-metadata-only",

    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-ui-closure");
  }

  return freeze(entries);
}

function createRuntimeUiClosureSealRecord(record = {}) {
  const entries = deriveRuntimeUiClosureSealEntries(record);

  return buildRuntimeUiClosureSealRecord({
    ...record,

    uiClosureSealStatus: "ui-closure-seal-ready",
    uiClosureSealMode: "inspection-ui-closure-seal",

    closureSealEntryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    closureSealEntries: entries,

    diagnostics: {
      readOnly: true,

      closureSealBlocked: true,
      attestationSealBlocked: true,
      provenanceSealBlocked: true,
      integritySealBlocked: true,
      registrySealBlocked: true,

      closureExecutionBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,

      canonicalWriteBlocked: true
    },

    metadata: {
      closureMetadataOnly: true
    }
  });
}

function inspectRuntimeUiClosureSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiClosureSealRecord(record);

  return freeze({
    readOnly: true,

    entryCount: normalized.closureSealEntries.length,

    closureSealBlocked: true,
    attestationSealBlocked: true,
    provenanceSealBlocked: true,
    integritySealBlocked: true,
    registrySealBlocked: true,

    closureExecutionBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,

    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiClosureSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiClosureSealEntries,
  createRuntimeUiClosureSealRecord,
  inspectRuntimeUiClosureSealRecord,
  compareRuntimeUiClosureSealRecords
};