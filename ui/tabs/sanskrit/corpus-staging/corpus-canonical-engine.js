"use strict";

const {
  buildCorpusCanonicalRecord
} = require("./corpus-canonical-map.js");

const {
  summarizeCorpusCertification,
  buildCorpusCertification
} = require("./corpus-certification-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveCanonicalStatus(certification = {}) {
  if (certification.valid === false) {
    return "canonical-preview-blocked";
  }

  if (
    certification.certificationStatus === "certification-ready" &&
    certification.certificationExecutionAllowed === false &&
    certification.canonicalWriteAllowed === false &&
    certification.promotionAllowed === false
  ) {
    return "canonical-preview-ready";
  }

  return "canonical-preview-review";
}

function buildCanonicalLedger(status) {
  if (status === "canonical-preview-ready") {
    return freeze([
      {
        canonicalId: "canonical-001",
        kind: "certification",
        status: "verified",
        message: "Certification verified for canonical preview.",
        previewOnly: true
      },
      {
        canonicalId: "canonical-002",
        kind: "safety",
        status: "locked",
        message: "Canonical write execution remains disabled.",
        previewOnly: true
      },
      {
        canonicalId: "canonical-003",
        kind: "preview",
        status: "not-executed",
        message: "Canonical promotion is preview-only in Phase 11.",
        previewOnly: true
      }
    ]);
  }

  if (status === "canonical-preview-review") {
    return freeze([
      {
        canonicalId: "canonical-001",
        kind: "review",
        status: "review-required",
        message: "Canonical preview requires manual review.",
        previewOnly: true
      }
    ]);
  }

  return freeze([
    {
      canonicalId: "canonical-001",
      kind: "blocker",
      status: "blocked",
      message: "Canonical preview is blocked.",
      previewOnly: true
    }
  ]);
}

function buildCorpusCanonicalPreview(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const certificationSummary = summarizeCorpusCertification(
    input,
    windowSize,
    secondsPerWindow
  );

  const certification = buildCorpusCertification(input, windowSize, secondsPerWindow);
  const canonicalStatus = deriveCanonicalStatus(certificationSummary);
  const canonicalLedger = buildCanonicalLedger(canonicalStatus);

  return buildCorpusCanonicalRecord({
    canonicalStatus,
    canonicalLedgerCount: canonicalLedger.length,
    canonicalLedger,
    acceptedRecordCount: certificationSummary.acceptedRecordCount,
    rejectedRecordCount: certificationSummary.rejectedRecordCount,
    certificationStatus: certificationSummary.certificationStatus,
    recommendation: certificationSummary.recommendation,
    certification
  });
}

function summarizeCorpusCanonicalPreview(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const canonical = buildCorpusCanonicalPreview(input, windowSize, secondsPerWindow);

  return freeze({
    state: canonical.state,
    valid: canonical.state !== "CANONICAL_PREVIEW_BLOCKED",
    canonicalStatus: canonical.canonicalStatus,
    canonicalLedgerCount: canonical.canonicalLedgerCount,
    canonicalLedger: canonical.canonicalLedger,
    acceptedRecordCount: canonical.acceptedRecordCount,
    rejectedRecordCount: canonical.rejectedRecordCount,
    certificationStatus: canonical.certificationStatus,
    recommendation: canonical.recommendation,
    previewOnly: true,
    readOnly: true,
    canonicalExecutionAllowed: false,
    certificationExecutionAllowed: false,
    promotionExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  deriveCanonicalStatus,
  buildCanonicalLedger,
  buildCorpusCanonicalPreview,
  summarizeCorpusCanonicalPreview
};