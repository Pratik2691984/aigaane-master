"use strict";

const {
  buildCorpusPostAttestationHoldRecord
} = require("./corpus-post-attestation-hold-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveHoldStatus(review = {}) {
  if (
    review.canonicalWriteAllowed === true ||
    review.status === "manual-review-blocked"
  ) {
    return "hold-blocked";
  }
  if (review.status === "manual-review-attested" && review.attested === true) {
    return "hold-active";
  }
  return "hold-waiting-attestation";
}

function summarizeCorpusPostAttestationHold(review = {}) {
  const status = deriveHoldStatus(review);
  return freeze(
    buildCorpusPostAttestationHoldRecord({
      status,
      holdActive: status !== "hold-blocked",
      waitingAttestation: status === "hold-waiting-attestation",
      failures: status === "hold-blocked" ? ["review-not-holdable"] : []
    })
  );
}

module.exports = {
  deriveHoldStatus,
  summarizeCorpusPostAttestationHold
};
