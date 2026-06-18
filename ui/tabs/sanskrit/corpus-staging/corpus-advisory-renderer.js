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

function renderCorpusAdvisoryPanel(summary = {}) {
  const packets = Array.isArray(summary.advisoryPackets)
    ? summary.advisoryPackets
    : [];

  const packetLines = packets.map((packet) => {
    return "- "
      + escapeHtml(packet.packetId || "")
      + " ["
      + escapeHtml(packet.severity || "")
      + "] "
      + escapeHtml(packet.message || "");
  });

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Advisory Status: " + escapeHtml(summary.advisoryStatus || "advisory-ready"),
    "Recommendation: " + escapeHtml(summary.recommendation || "hold"),
    "Advisory Packet Count: " + escapeHtml(summary.advisoryPacketCount || 0),
    "Promotion Confidence: " + escapeHtml(summary.promotionConfidence || 0),
    "Accepted Record Count: " + escapeHtml(summary.acceptedRecordCount || 0),
    "Rejected Record Count: " + escapeHtml(summary.rejectedRecordCount || 0),

    "",
    "Advisory Packets:",
    ...packetLines,

    "",
    "Preview Only: true",
    "Read Only: true",
    "Advisory Execution Allowed: false",
    "Promotion Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Promotion Advisory",
    status: summary.valid ? "ADVISORY_READY" : "ADVISORY_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusAdvisoryPanel
};