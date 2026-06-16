"use strict";

const {
  buildRuntimeCertificationRecord,
  normalizeRuntimeCertificationRecord
} = require("./execution-kernel-runtime-certification-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function stableArray(v) {
  return Array.isArray(v) ? v : [];
}

function deriveRuntimeCertificationAttestations(decision = {}) {
  const controls = stableArray(decision.controls);

  const attestations = [
    "inspection-path-certified",
    "execution-denial-certified",
    "mutation-denial-certified",
    "publication-denial-certified",
    "rollback-denial-certified",
    "canonical-write-denial-certified"
  ];

  if (controls.includes("runtime-transition-review-required")) {
    attestations.push("runtime-transition-review-certified");
  }

  if (controls.includes("warning-review-required")) {
    attestations.push("warning-review-certified");
  }

  return freeze(attestations);
}

function createRuntimeCertificationRecord(decision = {}) {
  const controls = stableArray(decision.controls);
  const warnings = stableArray(decision.warnings);
  const attestations = deriveRuntimeCertificationAttestations(decision);

  return buildRuntimeCertificationRecord({
    governanceId: decision.governanceId || "runtime-governance",
    governanceStatus: decision.governanceStatus || "inspection-approved",
    decision: decision.decision || "approve-inspection-only",

    certificationStatus: "certified-for-inspection",
    certificate: "controlled-runtime-inspection-only",

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    controlCount: controls.length,
    findingCount: Number(decision.findingCount || 0),
    warningCount: warnings.length,

    controls,
    attestations,
    warnings,

    diagnostics: {
      certificationReady: true,
      readOnly: true,
      replayBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      attestationCount: attestations.length
    }
  });
}

function inspectRuntimeCertificationRecord(record = {}) {
  const normalized = normalizeRuntimeCertificationRecord(record);

  return freeze({
    ready: true,
    certificationStatus: "certified-for-inspection",
    certificate: "controlled-runtime-inspection-only",

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    controlCount: normalized.controlCount,
    findingCount: normalized.findingCount,
    warningCount: normalized.warningCount,
    attestationCount: normalized.attestations.length,

    readOnly: true,
    replayBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeCertificationRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeCertificationRecord(a)) ===
      JSON.stringify(normalizeRuntimeCertificationRecord(b)),

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,
    readOnly: true
  });
}

module.exports = {
  deriveRuntimeCertificationAttestations,
  createRuntimeCertificationRecord,
  inspectRuntimeCertificationRecord,
  compareRuntimeCertificationRecords
};