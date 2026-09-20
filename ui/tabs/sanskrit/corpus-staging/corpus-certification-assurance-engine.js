"use strict";

const {
  buildCorpusCertificationAssuranceRecord
} = require("./corpus-certification-assurance-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveAssuranceStatus(packet = {}) {
  const invariants = packet.invariants || {};
  const locked =
    packet.canonicalWriteAllowed === false &&
    packet.promotionAllowed === false &&
    packet.importAllowed === false &&
    packet.executionAllowed === false &&
    invariants.unsafeWriteRefused === true;

  const accounted =
    Number(invariants.acceptedRecords) === 2000 &&
    Number(invariants.rejectedRecords) === 0;

  if (
    packet.schemaVersion === "sanskrit-bulk-corpus-certification.v1" &&
    packet.status === "certified-read-only" &&
    locked &&
    accounted
  ) {
    return "assurance-ready";
  }
  return "assurance-blocked";
}

function summarizeCorpusCertificationAssurance(packet = {}) {
  const status = deriveAssuranceStatus(packet);
  const record = buildCorpusCertificationAssuranceRecord({
    status,
    assured: status === "assurance-ready",
    failures: status === "assurance-ready" ? [] : ["packet-not-assured"],
    authorization: {
      certificationIsAuthorization: false,
      canonicalWrite: false,
      promotion: false,
      import: false,
      execution: false
    }
  });

  return freeze({
    ...record,
    previewOnly: true,
    readOnly: true,
    hardStop: true,
    nextGate: "MANUAL REVIEW / CERTIFIED"
  });
}

module.exports = {
  deriveAssuranceStatus,
  summarizeCorpusCertificationAssurance
};
