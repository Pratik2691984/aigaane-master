"use strict";

const CORPUS_RESERVATION_SCHEMA = "sanskrit-bulk-corpus-reservation.v1";

const DEFAULT_CORPUS_RESERVATION = Object.freeze({
  dhatu: 1400,
  sutra: 400,
  stotra: 200
});

const CORPUS_RESERVATION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  RESERVATION_READY: "RESERVATION_READY",
  RESERVATION_WARNING: "RESERVATION_WARNING",
  RESERVATION_BLOCKED: "RESERVATION_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeCorpusReservationInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_RESERVATION_SCHEMA,
    reservations: freeze(isObject(input.reservations) ? input.reservations : {}),
    totalRequested: asCount(input.totalRequested),
    totalReserved: asCount(input.totalReserved),
    totalUnreserved: asCount(input.totalUnreserved),
    warnings: freeze(asArray(input.warnings)),
    errors: freeze(asArray(input.errors)),
    allocation: freeze(isObject(input.allocation) ? input.allocation : {}),
    previewOnly: true,
    readOnly: true,
    reservationWriteAllowed: false,
    allocationWriteAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusReservationRecord(input = {}) {
  const normalized = normalizeCorpusReservationInput(input);

  let state = CORPUS_RESERVATION_STATES.RESERVATION_READY;

  if (normalized.totalRequested === 0 && normalized.totalReserved === 0) {
    state = CORPUS_RESERVATION_STATES.EMPTY;
  }

  if (
    normalized.errors.length ||
    (normalized.allocation && normalized.allocation.valid === false)
  ) {
    state = CORPUS_RESERVATION_STATES.RESERVATION_BLOCKED;
  } else if (normalized.warnings.length || normalized.totalUnreserved > 0) {
    state = CORPUS_RESERVATION_STATES.RESERVATION_WARNING;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_RESERVATION_SCHEMA,
  CORPUS_RESERVATION_STATES,
  DEFAULT_CORPUS_RESERVATION,
  normalizeCorpusReservationInput,
  buildCorpusReservationRecord
};