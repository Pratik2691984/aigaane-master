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

function renderCorpusCertificationPanel(summary = {}) {
  const ledger = Array.isArray(summary.certificationLedger)
    ? summary.certificationLedger
    : [];

  const ledgerLines = ledger.map((item) => {
    return "- "
      + escapeHtml(item.certificationId || "")
      + " ["
      + escapeHtml(item.status || "")
      + "] "
      + escapeHtml(item.message || "");
  });

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Certification Status: " + escapeHtml(summary.certificationStatus || "certification-ready"),
    "Approval Status: " + escapeHtml(summary.approvalStatus || "approval-blocked"),
    "Recommendation: " + escapeHtml(summary.recommendation || "hold"),
    "Certification Ledger Count: " + escapeHtml(summary.certificationLedgerCount || 0),
    "Accepted Record Count: " + escapeHtml(summary.acceptedRecordCount || 0),
    "Rejected Record Count: " + escapeHtml(summary.rejectedRecordCount || 0),

    "",
    "Certification Ledger:",
    ...ledgerLines,

    "",
    "Preview Only: true",
    "Read Only: true",
    "Certification Execution Allowed: false",
    "Approval Execution Allowed: false",
    "Promotion Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Certification",
    status: summary.valid ? "CERTIFICATION_READY" : "CERTIFICATION_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusCertificationPanel
};