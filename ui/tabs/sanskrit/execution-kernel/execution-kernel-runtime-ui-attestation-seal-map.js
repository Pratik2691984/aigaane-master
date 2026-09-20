"use strict";

const UI_ATTESTATION_SEAL_SCHEMA =
  "sanskrit-runtime-ui-attestation-seal.v1";

const UI_ATTESTATION_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_ATTESTATION_SEAL_READY: "UI_ATTESTATION_SEAL_READY",
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

function normalizeRuntimeUiAttestationSealRecord(input = {}) {
  return freeze({
    uiAttestationSealId: String(
      input.uiAttestationSealId || "runtime-ui-attestation-seal"
    ),
    createdAt: String(input.createdAt || "static"),

    sourceProvenanceSealId: String(
      input.sourceProvenanceSealId || "runtime-ui-provenance-seal"
    ),
    sourceIntegritySealId: String(
      input.sourceIntegritySealId || "runtime-ui-integrity-seal"
    ),
    sourceRegistrySealId: String(
      input.sourceRegistrySealId || "runtime-ui-registry-seal"
    ),
    sourceEvidenceSealId: String(
      input.sourceEvidenceSealId || "runtime-ui-evidence-seal"
    ),

    uiAttestationSealStatus: String(
      input.uiAttestationSealStatus || "ui-attestation-seal-ready"
    ),
    uiAttestationSealMode: String(
      input.uiAttestationSealMode || "inspection-ui-attestation-seal"
    ),

    attestationSealAllowed: false,
    provenanceSealAllowed: false,
    integritySealAllowed: false,
    registrySealAllowed: false,
    evidenceSealAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    attestationSealEntryCount: asCount(input.attestationSealEntryCount),
    warningCount: asCount(input.warningCount),

    attestationSealEntries: freeze(
      Array.isArray(input.attestationSealEntries)
        ? input.attestationSealEntries
        : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiAttestationSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiAttestationSealRecord(input);

  return freeze({
    schemaVersion: UI_ATTESTATION_SEAL_SCHEMA,
    state: normalized.attestationSealEntries.length
      ? UI_ATTESTATION_SEAL_STATES.UI_ATTESTATION_SEAL_READY
      : UI_ATTESTATION_SEAL_STATES.EMPTY,
    ...normalized
  });
}

module.exports = {
  UI_ATTESTATION_SEAL_SCHEMA,
  UI_ATTESTATION_SEAL_STATES,
  normalizeRuntimeUiAttestationSealRecord,
  buildRuntimeUiAttestationSealRecord
};