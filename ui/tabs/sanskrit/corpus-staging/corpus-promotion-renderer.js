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

function renderCorpusPromotionPanel(summary = {}) {
  const advisory = Array.isArray(summary.advisory) ? summary.advisory : [];
  const blockers = Array.isArray(summary.blockers) ? summary.blockers : [];

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Promotion Status: " + escapeHtml(summary.promotionStatus || "promotion-ready"),
    "Promotion Confidence: " + escapeHtml(summary.promotionConfidence || 0),
    "Accepted Record Count: " + escapeHtml(summary.acceptedRecordCount || 0),
    "Rejected Record Count: " + escapeHtml(summary.rejectedRecordCount || 0),

    "",
    "Advisory:",
    ...advisory.map((item) => "- " + escapeHtml(item)),

    "",
    "Blockers:",
    ...blockers.map((item) => "- " + escapeHtml(item)),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Promotion Readiness Allowed: true",
    "Promotion Execution Allowed: false",
    "Admission Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Promotion Readiness",
    status: summary.valid ? "PROMOTION_READY" : "PROMOTION_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusPromotionPanel
};