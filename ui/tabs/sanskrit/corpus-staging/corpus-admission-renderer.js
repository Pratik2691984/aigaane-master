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

function renderCorpusAdmissionPanel(summary = {}) {
  const admissionReasons = Array.isArray(summary.admissionReasons)
    ? summary.admissionReasons
    : [];

  const rejectionReasons = Array.isArray(summary.rejectionReasons)
    ? summary.rejectionReasons
    : [];

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Admission Status: " + escapeHtml(summary.admissionStatus || "admission-ready"),
    "Accepted Record Count: " + escapeHtml(summary.acceptedRecordCount || 0),
    "Rejected Record Count: " + escapeHtml(summary.rejectedRecordCount || 0),

    "",
    "Admission Reasons:",
    ...admissionReasons.map((reason) => "- " + escapeHtml(reason)),

    "",
    "Rejection Reasons:",
    ...rejectionReasons.map((reason) => "- " + escapeHtml(reason)),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Admission Execution Allowed: false",
    "Forecast Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Admission",
    status: summary.valid ? "ADMISSION_READY" : "ADMISSION_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusAdmissionPanel
};