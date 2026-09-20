"use strict";

const {
  buildCorpusCertificationRecord
} = require("./corpus-certification-map.js");

const {
  summarizeCorpusPromotionApproval,
  buildCorpusPromotionApproval
} = require("./corpus-approval-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveCertificationStatus(approval = {}) {
  if (approval.valid === false) {
    return "certification-blocked";
  }

  if (
    approval.approvalStatus === "approval-ready" &&
    approval.recommendation === "manual-review-ready" &&
    approval.approvalExecutionAllowed === false &&
    approval.canonicalWriteAllowed === false &&
    approval.promotionAllowed === false
  ) {
    return "certification-ready";
  }

  return "certification-review";
}

function buildCertificationLedger(status) {
  if (status === "certification-ready") {
    return freeze([
      {
        certificationId: "certification-001",
        kind: "approval",
        status: "verified",
        message: "Promotion approval verified for certification.",
        previewOnly: true
      },
      {
        certificationId: "certification-002",
        kind: "safety",
        status: "locked",
        message: "Canonical write remains disabled.",
        previewOnly: true
      },
      {
        certificationId: "certification-003",
        kind: "evidence",
        status: "immutable",
        message: "Certification evidence is preview-only and read-only.",
        previewOnly: true
      }
    ]);
  }

  if (status === "certification-review") {
    return freeze([
      {
        certificationId: "certification-001",
        kind: "review",
        status: "review-required",
        message: "Corpus certification requires manual review.",
        previewOnly: true
      }
    ]);
  }

  return freeze([
    {
      certificationId: "certification-001",
      kind: "blocker",
      status: "blocked",
      message: "Corpus certification is blocked.",
      previewOnly: true
    }
  ]);
}

function buildCorpusCertification(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const approvalSummary = summarizeCorpusPromotionApproval(
    input,
    windowSize,
    secondsPerWindow
  );

  const approval = buildCorpusPromotionApproval(input, windowSize, secondsPerWindow);
  const certificationStatus = deriveCertificationStatus(approvalSummary);
  const certificationLedger = buildCertificationLedger(certificationStatus);

  return buildCorpusCertificationRecord({
    certificationStatus,
    certificationLedgerCount: certificationLedger.length,
    certificationLedger,
    acceptedRecordCount: approvalSummary.acceptedRecordCount,
    rejectedRecordCount: approvalSummary.rejectedRecordCount,
    approvalStatus: approvalSummary.approvalStatus,
    recommendation: approvalSummary.recommendation,
    approval
  });
}

function summarizeCorpusCertification(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const certification = buildCorpusCertification(input, windowSize, secondsPerWindow);

  return freeze({
    state: certification.state,
    valid: certification.state !== "CERTIFICATION_BLOCKED",
    certificationStatus: certification.certificationStatus,
    certificationLedgerCount: certification.certificationLedgerCount,
    certificationLedger: certification.certificationLedger,
    acceptedRecordCount: certification.acceptedRecordCount,
    rejectedRecordCount: certification.rejectedRecordCount,
    approvalStatus: certification.approvalStatus,
    recommendation: certification.recommendation,
    previewOnly: true,
    readOnly: true,
    certificationExecutionAllowed: false,
    approvalExecutionAllowed: false,
    promotionExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  deriveCertificationStatus,
  buildCertificationLedger,
  buildCorpusCertification,
  summarizeCorpusCertification
};