"use strict";

const CORPUS_ADVISORY_SCHEMA = "sanskrit-bulk-corpus-promotion-advisory.v1";

const CORPUS_ADVISORY_STATES = Object.freeze({
  EMPTY: "EMPTY",
  ADVISORY_READY: "ADVISORY_READY",
  ADVISORY_BLOCKED: "ADVISORY_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeCorpusAdvisoryInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_ADVISORY_SCHEMA,
    advisoryStatus: String(input.advisoryStatus || "advisory-ready"),
    recommendation: String(input.recommendation || "hold"),
    advisoryPacketCount: asCount(input.advisoryPacketCount),
    advisoryPackets: freeze(asArray(input.advisoryPackets)),
    promotionConfidence: asCount(input.promotionConfidence),
    acceptedRecordCount: asCount(input.acceptedRecordCount),
    rejectedRecordCount: asCount(input.rejectedRecordCount),
    readiness: freeze(isObject(input.readiness) ? input.readiness : {}),
    previewOnly: true,
    readOnly: true,
    advisoryExecutionAllowed: false,
    promotionExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusAdvisoryRecord(input = {}) {
  const normalized = normalizeCorpusAdvisoryInput(input);

  let state = CORPUS_ADVISORY_STATES.ADVISORY_READY;

  if (normalized.advisoryPacketCount === 0) {
    state = CORPUS_ADVISORY_STATES.EMPTY;
  }

  if (
    normalized.advisoryStatus === "advisory-blocked" ||
    (normalized.readiness && normalized.readiness.valid === false)
  ) {
    state = CORPUS_ADVISORY_STATES.ADVISORY_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_ADVISORY_SCHEMA,
  CORPUS_ADVISORY_STATES,
  normalizeCorpusAdvisoryInput,
  buildCorpusAdvisoryRecord
};