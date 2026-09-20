"use strict";

const {
  buildCorpusManualReviewRecord
} = require("./corpus-manual-review-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveManualReviewStatus(assurance = {}, attested = false) {
  const ready =
    assurance.status === "assurance-ready" &&
    assurance.assured === true &&
    assurance.hardStop === true &&
    assurance.canonicalWriteAllowed === false;

  if (!ready) {
    return "manual-review-blocked";
  }
  return attested ? "manual-review-attested" : "manual-review-pending";
}

function summarizeCorpusManualReview(assurance = {}, attested = false) {
  const status = deriveManualReviewStatus(assurance, attested);
  return freeze(
    buildCorpusManualReviewRecord({
      status,
      attested: status === "manual-review-attested",
      failures: status === "manual-review-blocked" ? ["assurance-not-ready"] : []
    })
  );
}

module.exports = {
  deriveManualReviewStatus,
  summarizeCorpusManualReview
};
