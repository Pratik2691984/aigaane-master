"use strict";

const {
  buildCorpusAdvisoryRecord
} = require("./corpus-advisory-map.js");

const {
  summarizeCorpusPromotionReadiness,
  buildCorpusPromotionReadiness
} = require("./corpus-promotion-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveAdvisoryStatus(readiness = {}) {
  if (readiness.valid === false) {
    return "advisory-blocked";
  }

  if (
    readiness.promotionStatus === "promotion-ready" &&
    Number(readiness.promotionConfidence || 0) === 100 &&
    readiness.promotionExecutionAllowed === false &&
    readiness.canonicalWriteAllowed === false &&
    readiness.promotionAllowed === false
  ) {
    return "advisory-ready";
  }

  return "advisory-review";
}

function derivePromotionRecommendation(status) {
  if (status === "advisory-ready") {
    return "manual-review-ready";
  }

  if (status === "advisory-review") {
    return "review-required";
  }

  return "hold";
}

function buildAdvisoryPackets(status) {
  if (status === "advisory-ready") {
    return freeze([
      {
        packetId: "advisory-001",
        kind: "readiness",
        message: "Promotion readiness is complete.",
        severity: "info",
        previewOnly: true
      },
      {
        packetId: "advisory-002",
        kind: "safety",
        message: "Canonical write remains locked.",
        severity: "guard",
        previewOnly: true
      },
      {
        packetId: "advisory-003",
        kind: "recommendation",
        message: "Manual promotion review may begin.",
        severity: "review",
        previewOnly: true
      }
    ]);
  }

  if (status === "advisory-review") {
    return freeze([
      {
        packetId: "advisory-001",
        kind: "review",
        message: "Promotion advisory requires manual review.",
        severity: "review",
        previewOnly: true
      }
    ]);
  }

  return freeze([
    {
      packetId: "advisory-001",
      kind: "blocker",
      message: "Promotion readiness is blocked.",
      severity: "blocker",
      previewOnly: true
    }
  ]);
}

function buildCorpusPromotionAdvisory(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const readinessSummary = summarizeCorpusPromotionReadiness(
    input,
    windowSize,
    secondsPerWindow
  );

  const readiness = buildCorpusPromotionReadiness(input, windowSize, secondsPerWindow);
  const advisoryStatus = deriveAdvisoryStatus(readinessSummary);
  const advisoryPackets = buildAdvisoryPackets(advisoryStatus);

  return buildCorpusAdvisoryRecord({
    advisoryStatus,
    recommendation: derivePromotionRecommendation(advisoryStatus),
    advisoryPacketCount: advisoryPackets.length,
    advisoryPackets,
    promotionConfidence: readinessSummary.promotionConfidence,
    acceptedRecordCount: readinessSummary.acceptedRecordCount,
    rejectedRecordCount: readinessSummary.rejectedRecordCount,
    readiness
  });
}

function summarizeCorpusPromotionAdvisory(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const advisory = buildCorpusPromotionAdvisory(input, windowSize, secondsPerWindow);

  return freeze({
    state: advisory.state,
    valid: advisory.state !== "ADVISORY_BLOCKED",
    advisoryStatus: advisory.advisoryStatus,
    recommendation: advisory.recommendation,
    advisoryPacketCount: advisory.advisoryPacketCount,
    advisoryPackets: advisory.advisoryPackets,
    promotionConfidence: advisory.promotionConfidence,
    acceptedRecordCount: advisory.acceptedRecordCount,
    rejectedRecordCount: advisory.rejectedRecordCount,
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

module.exports = {
  deriveAdvisoryStatus,
  derivePromotionRecommendation,
  buildAdvisoryPackets,
  buildCorpusPromotionAdvisory,
  summarizeCorpusPromotionAdvisory
};