"use strict";

/**
 * Deterministic Chandas Overlay Integrity Map
 *
 * Non-authoritative, inspection-only integrity metadata for overlay assurance.
 * This layer does not execute metre logic, mutate registries,
 * alter replay state, or affect runtime derivation behavior.
 */

const CHANDAS_OVERLAY_INTEGRITY_SCHEMA_VERSION = "chandas-overlay-integrity.v1";

const CHANDAS_OVERLAY_INTEGRITY_STATES = Object.freeze({
  VERIFIED: "VERIFIED",
  REVIEW_REQUIRED: "REVIEW_REQUIRED",
  OBSERVABLE: "OBSERVABLE",
  COMPROMISED: "COMPROMISED"
});

const CHANDAS_OVERLAY_INTEGRITY_CONTRACTS = Object.freeze({
  deterministic: true,
  inspectionOnly: true,
  nonAuthoritative: true,
  nonPerformative: true,
  runtimeIsolated: true,
  immutableAssuranceSafe: true,
  staticPreviewCompatible: true
});

const CHANDAS_OVERLAY_INTEGRITY_RULES = Object.freeze([
  {
    id: "integrity.chandas.overlay.deterministic-chain",
    state: CHANDAS_OVERLAY_INTEGRITY_STATES.VERIFIED,
    summary: "Integrity summaries must remain deterministic, normalized, and replay-safe.",
    diagnostics: ["deterministic-chain", "replay-safe"]
  },
  {
    id: "integrity.chandas.overlay.assurance-readiness",
    state: CHANDAS_OVERLAY_INTEGRITY_STATES.REVIEW_REQUIRED,
    summary: "Assurance-ready overlays may be inspected for integrity readiness.",
    diagnostics: ["assurance-readiness", "inspection-contract"]
  },
  {
    id: "integrity.chandas.overlay.static-preview",
    state: CHANDAS_OVERLAY_INTEGRITY_STATES.OBSERVABLE,
    summary: "Static preview must receive normalized integrity summaries without backend dependency.",
    diagnostics: ["static-preview", "normalized-export"]
  },
  {
    id: "integrity.chandas.overlay.runtime-mutation",
    state: CHANDAS_OVERLAY_INTEGRITY_STATES.COMPROMISED,
    summary: "Any mutation of overlay registries, replay chains, audit chains, governance state, policy state, compliance state, or assurance state compromises integrity.",
    diagnostics: ["runtime-mutation", "integrity-compromised"]
  }
]);

function getChandasOverlayIntegritySummary() {
  return {
    schemaVersion: CHANDAS_OVERLAY_INTEGRITY_SCHEMA_VERSION,
    contracts: CHANDAS_OVERLAY_INTEGRITY_CONTRACTS,
    integrityCount: CHANDAS_OVERLAY_INTEGRITY_RULES.length,
    states: Object.values(CHANDAS_OVERLAY_INTEGRITY_STATES),
    rules: CHANDAS_OVERLAY_INTEGRITY_RULES.map((rule) => ({ ...rule }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    CHANDAS_OVERLAY_INTEGRITY_SCHEMA_VERSION,
    CHANDAS_OVERLAY_INTEGRITY_STATES,
    CHANDAS_OVERLAY_INTEGRITY_CONTRACTS,
    CHANDAS_OVERLAY_INTEGRITY_RULES,
    getChandasOverlayIntegritySummary
  };
}