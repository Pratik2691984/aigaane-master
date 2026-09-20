"use strict";

function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderCorpusReservationPanel(summary = {}) {
  const reservations = summary.reservations || {};
  const warnings = Array.isArray(summary.warnings) ? summary.warnings : [];
  const errors = Array.isArray(summary.errors) ? summary.errors : [];

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Total Requested: " + escapeHtml(summary.totalRequested || 0),
    "Total Reserved: " + escapeHtml(summary.totalReserved || 0),
    "Total Unreserved: " + escapeHtml(summary.totalUnreserved || 0),

    "",
    "Reservations:",
    "- dhatu: " + escapeHtml((reservations.dhatu && reservations.dhatu.reserved) || 0)
      + " / " + escapeHtml((reservations.dhatu && reservations.dhatu.requested) || 0),
    "- sutra: " + escapeHtml((reservations.sutra && reservations.sutra.reserved) || 0)
      + " / " + escapeHtml((reservations.sutra && reservations.sutra.requested) || 0),
    "- stotra: " + escapeHtml((reservations.stotra && reservations.stotra.reserved) || 0)
      + " / " + escapeHtml((reservations.stotra && reservations.stotra.requested) || 0),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning)),

    "",
    "Errors:",
    ...errors.map((error) => "- " + escapeHtml(error)),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Reservation Write Allowed: false",
    "Allocation Write Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Reservation",
    status: summary.valid ? "RESERVATION_READY" : "RESERVATION_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusReservationPanel
};