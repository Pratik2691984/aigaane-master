"use strict";

const CORPUS_CERTIFICATION_ASSURANCE_SCHEMA =
  "sanskrit-bulk-corpus-certification-assurance.v1";

const CORPUS_CERTIFICATION_ASSURANCE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  ASSURANCE_READY: "ASSURANCE_READY",
  ASSURANCE_BLOCKED: "ASSURANCE_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeCorpusCertificationAssuranceInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_CERTIFICATION_ASSURANCE_SCHEMA,
    status: String(input.status || "assurance-blocked"),
    assured: input.assured === true,
    hardStop: true,
    failures: freeze(asArray(input.failures)),
    authorization: freeze({
      certificationIsAuthorization: false,
      canonicalWrite: false,
      promotion: false,
      import: false,
      execution: false
    }),
    previewOnly: true,
    readOnly: true,
    assuranceExecutionAllowed: false,
    certificationExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusCertificationAssuranceRecord(input = {}) {
  const normalized = normalizeCorpusCertificationAssuranceInput(input);
  let state = CORPUS_CERTIFICATION_ASSURANCE_STATES.ASSURANCE_READY;
  if (!normalized.assured || normalized.failures.length > 0) {
    state = CORPUS_CERTIFICATION_ASSURANCE_STATES.ASSURANCE_BLOCKED;
  }
  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_CERTIFICATION_ASSURANCE_SCHEMA,
  CORPUS_CERTIFICATION_ASSURANCE_STATES,
  normalizeCorpusCertificationAssuranceInput,
  buildCorpusCertificationAssuranceRecord
};
