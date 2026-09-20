"use strict";

const {
  buildCorpusApprovalRecord
} = require("./corpus-approval-map.js");

const {
  summarizeCorpusPromotionAdvisory,
  buildCorpusPromotionAdvisory
} = require("./corpus-advisory-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveApprovalStatus(advisory = {}) {
  if (advisory.valid === false) {
    return "approval-blocked";
  }

  if (
    advisory.advisoryStatus === "advisory-ready" &&
    advisory.recommendation === "manual-review-ready" &&
    advisory.advisoryExecutionAllowed === false &&
    advisory.canonicalWriteAllowed === false &&
    advisory.promotionAllowed === false
  ) {
    return "approval-ready";
  }

  return "approval-review";
}

function buildApprovalLedger(status) {
  if (status === "approval-ready") {
    return freeze([
      {
        approvalId: "approval-001",
        kind: "advisory",
        status: "accepted",
        message: "Promotion advisory accepted for manual review.",
        previewOnly: true
      },
      {
        approvalId: "approval-002",
        kind: "safety",
        status: "locked",
        message: "Canonical write remains disabled.",
        previewOnly: true
      },
      {
        approvalId: "approval-003",
        kind: "promotion",
        status: "not-executed",
        message: "Promotion execution is not allowed in this layer.",
        previewOnly: true
      }
    ]);
  }

  if (status === "approval-review") {
    return freeze([
      {
        approvalId: "approval-001",
        kind: "review",
        status: "review-required",
        message: "Promotion approval requires manual review.",
        previewOnly: true
      }
    ]);
  }

  return freeze([
    {
      approvalId: "approval-001",
      kind: "blocker",
      status: "blocked",
      message: "Promotion approval is blocked.",
      previewOnly: true
    }
  ]);
}

function buildCorpusPromotionApproval(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const advisorySummary = summarizeCorpusPromotionAdvisory(
    input,
    windowSize,
    secondsPerWindow
  );

  const advisory = buildCorpusPromotionAdvisory(input, windowSize, secondsPerWindow);
  const approvalStatus = deriveApprovalStatus(advisorySummary);
  const approvalLedger = buildApprovalLedger(approvalStatus);

  return buildCorpusApprovalRecord({
    approvalStatus,
    approvalLedgerCount: approvalLedger.length,
    approvalLedger,
    recommendation: advisorySummary.recommendation,
    advisoryStatus: advisorySummary.advisoryStatus,
    acceptedRecordCount: advisorySummary.acceptedRecordCount,
    rejectedRecordCount: advisorySummary.rejectedRecordCount,
    advisory
  });
}

function summarizeCorpusPromotionApproval(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const approval = buildCorpusPromotionApproval(input, windowSize, secondsPerWindow);

  return freeze({
    state: approval.state,
    valid: approval.state !== "APPROVAL_BLOCKED",
    approvalStatus: approval.approvalStatus,
    approvalLedgerCount: approval.approvalLedgerCount,
    approvalLedger: approval.approvalLedger,
    recommendation: approval.recommendation,
    advisoryStatus: approval.advisoryStatus,
    acceptedRecordCount: approval.acceptedRecordCount,
    rejectedRecordCount: approval.rejectedRecordCount,
    previewOnly: true,
    readOnly: true,
    approvalExecutionAllowed: false,
    advisoryExecutionAllowed: false,
    promotionExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  deriveApprovalStatus,
  buildApprovalLedger,
  buildCorpusPromotionApproval,
  summarizeCorpusPromotionApproval
};