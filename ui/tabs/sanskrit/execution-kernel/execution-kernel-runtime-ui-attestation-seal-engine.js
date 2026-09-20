"use strict";

const {
  buildRuntimeUiAttestationSealRecord,
  normalizeRuntimeUiAttestationSealRecord
} = require("./execution-kernel-runtime-ui-attestation-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiAttestationSealEntries(record = {}) {
  const entries = [
    "runtime-ui-attestation-surface",

    "runtime-ui-provenance-reference",
    "runtime-ui-integrity-reference",
    "runtime-ui-registry-reference",
    "runtime-ui-evidence-reference",

    "runtime-attestation-reference",

    "attestation-inspection-only",
    "attestation-evidence-immutable",
    "attestation-metadata-only",

    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-ui-attestation");
  }

  return freeze(entries);
}

function createRuntimeUiAttestationSealRecord(record = {}) {
  const entries = deriveRuntimeUiAttestationSealEntries(record);

  return buildRuntimeUiAttestationSealRecord({
    ...record,

    uiAttestationSealStatus: "ui-attestation-seal-ready",
    uiAttestationSealMode: "inspection-ui-attestation-seal",

    attestationSealEntryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    attestationSealEntries: entries,

    diagnostics: {
      readOnly: true,

      attestationSealBlocked: true,
      provenanceSealBlocked: true,
      integritySealBlocked: true,
      registrySealBlocked: true,
      evidenceSealBlocked: true,

      attestationExecutionBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,

      canonicalWriteBlocked: true
    },

    metadata: {
      attestationMetadataOnly: true
    }
  });
}

function inspectRuntimeUiAttestationSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiAttestationSealRecord(record);

  return freeze({
    readOnly: true,

    entryCount: normalized.attestationSealEntries.length,

    attestationSealBlocked: true,
    provenanceSealBlocked: true,
    integritySealBlocked: true,
    registrySealBlocked: true,
    evidenceSealBlocked: true,

    attestationExecutionBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,

    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiAttestationSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiAttestationSealEntries,
  createRuntimeUiAttestationSealRecord,
  inspectRuntimeUiAttestationSealRecord,
  compareRuntimeUiAttestationSealRecords
};