"use strict";

const CERTIFICATION_SCHEMA = "sanskrit-runtime-certification.v1";

const CERTIFICATION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  CERTIFIED_FOR_INSPECTION: "CERTIFIED_FOR_INSPECTION",
  BLOCKED: "BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function asNonNegativeInteger(v) {
  const n = Number(v || 0);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.floor(n));
}

function normalizeRuntimeCertificationRecord(input = {}) {
  return freeze({
    certificationId: String(input.certificationId || "runtime-certification"),
    createdAt: String(input.createdAt || "static"),

    governanceId: String(input.governanceId || "runtime-governance"),
    governanceStatus: String(input.governanceStatus || "inspection-approved"),
    decision: String(input.decision || "approve-inspection-only"),

    certificationStatus: String(input.certificationStatus || "certified-for-inspection"),
    certificate: String(input.certificate || "controlled-runtime-inspection-only"),

    replayAllowed: Boolean(input.replayAllowed === true),
    executionAllowed: Boolean(input.executionAllowed === true),
    mutationAllowed: Boolean(input.mutationAllowed === true),
    publicationAllowed: Boolean(input.publicationAllowed === true),
    rollbackAllowed: Boolean(input.rollbackAllowed === true),
    canonicalWriteAllowed: Boolean(input.canonicalWriteAllowed === true),

    controlCount: asNonNegativeInteger(input.controlCount),
    findingCount: asNonNegativeInteger(input.findingCount),
    warningCount: asNonNegativeInteger(input.warningCount),

    controls: freeze([...(Array.isArray(input.controls) ? input.controls : [])]),
    attestations: freeze([...(Array.isArray(input.attestations) ? input.attestations : [])]),
    warnings: freeze([...(Array.isArray(input.warnings) ? input.warnings : [])]),

    diagnostics: freeze({ ...(isObject(input.diagnostics) ? input.diagnostics : {}) }),
    metadata: freeze({ ...(isObject(input.metadata) ? input.metadata : {}) })
  });
}

function buildRuntimeCertificationRecord(input = {}) {
  const normalized = normalizeRuntimeCertificationRecord(input);

  return freeze({
    schemaVersion: CERTIFICATION_SCHEMA,
    state: normalized.attestations.length > 0
      ? CERTIFICATION_STATES.CERTIFIED_FOR_INSPECTION
      : CERTIFICATION_STATES.EMPTY,

    ...normalized,

    certificationStatus: "certified-for-inspection",
    certificate: "controlled-runtime-inspection-only",

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false
  });
}

function validateRuntimeCertificationRecord(record = {}) {
  const errors = [];

  if (!isObject(record)) errors.push("record");

  if (typeof record.certificationStatus !== "string") {
    errors.push("certificationStatus");
  }

  if (typeof record.certificate !== "string") {
    errors.push("certificate");
  }

  [
    "replayAllowed",
    "executionAllowed",
    "mutationAllowed",
    "publicationAllowed",
    "rollbackAllowed",
    "canonicalWriteAllowed"
  ].forEach((field) => {
    if (typeof record[field] !== "boolean") {
      errors.push(field);
    }
  });

  if (
    !Number.isInteger(Number(record.controlCount)) ||
    Number(record.controlCount) < 0
  ) {
    errors.push("controlCount");
  }

  if (
    !Number.isInteger(Number(record.findingCount)) ||
    Number(record.findingCount) < 0
  ) {
    errors.push("findingCount");
  }

  if (
    !Number.isInteger(Number(record.warningCount)) ||
    Number(record.warningCount) < 0
  ) {
    errors.push("warningCount");
  }

  if (!Array.isArray(record.controls)) errors.push("controls");
  if (!Array.isArray(record.attestations)) errors.push("attestations");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  CERTIFICATION_SCHEMA,
  CERTIFICATION_STATES,
  normalizeRuntimeCertificationRecord,
  buildRuntimeCertificationRecord,
  validateRuntimeCertificationRecord
};