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

function renderCorpusCanonicalPanel(summary = {}) {
  const ledger = Array.isArray(summary.canonicalLedger)
    ? summary.canonicalLedger
    : [];

  const ledgerLines = ledger.map((item) => {
    return "- "
      + escapeHtml(item.canonicalId || "")
      + " ["
      + escapeHtml(item.status || "")
      + "] "
      + escapeHtml(item.message || "");
  });

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Canonical Status: " + escapeHtml(summary.canonicalStatus || "canonical-preview-ready"),
    "Certification Status: " + escapeHtml(summary.certificationStatus || "certification-blocked"),
    "Recommendation: " + escapeHtml(summary.recommendation || "hold"),
    "Canonical Ledger Count: " + escapeHtml(summary.canonicalLedgerCount || 0),
    "Accepted Record Count: " + escapeHtml(summary.acceptedRecordCount || 0),
    "Rejected Record Count: " + escapeHtml(summary.rejectedRecordCount || 0),

    "",
    "Canonical Ledger:",
    ...ledgerLines,

    "",
    "Preview Only: true",
    "Read Only: true",
    "Canonical Execution Allowed: false",
    "Certification Execution Allowed: false",
    "Promotion Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Canonical Preview",
    status: summary.valid ? "CANONICAL_PREVIEW_READY" : "CANONICAL_PREVIEW_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusCanonicalPanel
};