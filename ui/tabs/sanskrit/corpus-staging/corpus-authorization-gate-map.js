"use strict";

const CORPUS_AUTHORIZATION_GATE_SCHEMA =
  "sanskrit-bulk-corpus-authorization-gate.v1";

const CORPUS_AUTHORIZATION_GATE_STATES = Object.freeze({
  PENDING: "PENDING",
  BLOCKED: "BLOCKED",
  AUTHORIZED: "AUTHORIZED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function normalizeCorpusAuthorizationGateInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_AUTHORIZATION_GATE_SCHEMA,
    status: String(input.status || "authorization-blocked"),
    authorized: input.authorized === true,
    hardStop: true,
    failures: freeze(asArray(input.failures)),
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false,
    executionAllowed: false,
    authorizationIsWrite: false,
    authorizationIsExecution: false
  });
}

function buildCorpusAuthorizationGateRecord(input = {}) {
  const normalized = normalizeCorpusAuthorizationGateInput(input);
  let state = CORPUS_AUTHORIZATION_GATE_STATES.BLOCKED;
  if (normalized.authorized === true) {
    state = CORPUS_AUTHORIZATION_GATE_STATES.AUTHORIZED;
  } else if (normalized.status === "authorization-pending") {
    state = CORPUS_AUTHORIZATION_GATE_STATES.PENDING;
  }
  return freeze({
    ...normalized,
    state,
    nextGate: "38H PROMOTION PREFLIGHT"
  });
}

module.exports = {
  CORPUS_AUTHORIZATION_GATE_SCHEMA,
  CORPUS_AUTHORIZATION_GATE_STATES,
  normalizeCorpusAuthorizationGateInput,
  buildCorpusAuthorizationGateRecord
};
