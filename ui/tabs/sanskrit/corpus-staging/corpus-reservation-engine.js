"use strict";

const {
  buildCorpusReservationRecord,
  DEFAULT_CORPUS_RESERVATION
} = require("./corpus-reservation-map.js");

const {
  summarizeCorpusAllocation
} = require("./corpus-allocation-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function buildReservations(allocation = {}, requested = DEFAULT_CORPUS_RESERVATION) {
  const reservations = {};
  const warnings = [];

  Object.keys(requested).forEach((type) => {
    const requestedCount = Number(requested[type] || 0);
    const allocationItem = allocation[type] || {};
    const available = Number(allocationItem.remaining || 0);
    const used = Number(allocationItem.used || 0);
    const stagedCapacity = used > 0 ? Math.max(available, Math.min(used, requestedCount)) : available;
    const reserved = Math.min(requestedCount, stagedCapacity);
    const unreserved = Math.max(0, requestedCount - reserved);

    if (unreserved > 0) {
      warnings.push(type + ":reservationLimited");
    }

    reservations[type] = {
      requested: requestedCount,
      available,
      reserved,
      unreserved
    };
  });

  return freeze({
    reservations: freeze(reservations),
    warnings: freeze(warnings)
  });
}

function reserveCorpusCapacity(input = {}, requested = DEFAULT_CORPUS_RESERVATION) {
  const allocation = summarizeCorpusAllocation(input);
  const reservationPlan = buildReservations(allocation.allocation, requested);

  const errors = [];

  const totalRequested = Object.values(reservationPlan.reservations).reduce(
    (sum, item) => sum + Number(item.requested || 0),
    0
  );

  const totalReserved = Object.values(reservationPlan.reservations).reduce(
    (sum, item) => sum + Number(item.reserved || 0),
    0
  );

  const totalUnreserved = Object.values(reservationPlan.reservations).reduce(
    (sum, item) => sum + Number(item.unreserved || 0),
    0
  );

  return buildCorpusReservationRecord({
    reservations: reservationPlan.reservations,
    totalRequested,
    totalReserved,
    totalUnreserved,
    warnings: reservationPlan.warnings,
    errors,
    allocation
  });
}

function summarizeCorpusReservation(input = {}, requested = DEFAULT_CORPUS_RESERVATION) {
  const reservation = reserveCorpusCapacity(input, requested);

  return freeze({
    state: reservation.state,
    valid: reservation.state !== "RESERVATION_BLOCKED",
    reservations: reservation.reservations,
    totalRequested: reservation.totalRequested,
    totalReserved: reservation.totalReserved,
    totalUnreserved: reservation.totalUnreserved,
    warnings: reservation.warnings,
    errors: reservation.errors,
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

module.exports = {
  buildReservations,
  reserveCorpusCapacity,
  summarizeCorpusReservation
};