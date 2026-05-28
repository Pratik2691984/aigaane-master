"use strict";

/**
 * Deterministic Chandas Overlay Assurance Map
 *
 * Non-authoritative, inspection-only assurance metadata for overlay compliance.
 * This layer does not execute metre logic, certify results, mutate registries,
 * or alter runtime derivation behavior.
 */

const CHANDAS_OVERLAY_ASSURANCE_SCHEMA_VERSION = "chandas-overlay-assurance.v1";

const CHANDAS_OVERLAY_ASSURANCE_STATES = Object.freeze({
  ASSURED: "ASSURED",
  REVIEW_REQUIRED: "REVIEW_REQUIRED",
  OBSERVABLE: "OBSERVABLE",
  UNSAFE: "UNSAFE"
});

const CHANDAS_OVERLAY_ASSURANCE_CONTRACTS = Object.freeze({
  deterministic: true,
  inspectionOnly: true,
  nonAuthoritative: true,
  nonPerformative: true,
  runtimeIsolated: true,
  immutableComplianceSafe: true,
  staticPreviewCompatible: true
});

const CHANDAS_OVERLAY_ASSURANCE_RULES = Object.freeze([
  {
    id: "assurance.chandas.overlay.deterministic-summary",
    state: CHANDAS_OVERLAY_ASSURANCE_STATES.ASSURED,
    summary: "Assurance summaries must remain deterministic, normalized, and schema-versioned.",
    diagnostics: ["deterministic-summary", "schema-versioned"]
  },
  {
    id: "assurance.chandas.overlay.compliance-readiness",
    state: CHANDAS_OVERLAY_ASSURANCE_STATES.REVIEW_REQUIRED,
    summary: "Compliance-ready overlays may be inspected for assurance readiness.",
    diagnostics: ["compliance-readiness", "inspection-contract"]
  },
  {
    id: "assurance.chandas.overlay.static-preview",
    state: CHANDAS_OVERLAY_ASSURANCE_STATES.OBSERVABLE,
    summary: "Static preview must receive normalized assurance summaries without backend dependency.",
    diagnostics: ["static-preview", "normalized-export"]
  },
  {
    id: "assurance.chandas.overlay.runtime-coupling",
    state: CHANDAS_OVERLAY_ASSURANCE_STATES.UNSAFE,
    summary: "Any coupling to runtime metre, cadence, recitation, registry mutation, or certification mutation is unsafe.",
    diagnostics: ["runtime-coupling", "mutation-risk"]
  }
]);

function getChandasOverlayAssuranceSummary() {
  return {
    schemaVersion: CHANDAS_OVERLAY_ASSURANCE_SCHEMA_VERSION,
    contracts: CHANDAS_OVERLAY_ASSURANCE_CONTRACTS,
    assuranceCount: CHANDAS_OVERLAY_ASSURANCE_RULES.length,
    states: Object.values(CHANDAS_OVERLAY_ASSURANCE_STATES),
    rules: CHANDAS_OVERLAY_ASSURANCE_RULES.map((rule) => ({ ...rule }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    CHANDAS_OVERLAY_ASSURANCE_SCHEMA_VERSION,
    CHANDAS_OVERLAY_ASSURANCE_STATES,
    CHANDAS_OVERLAY_ASSURANCE_CONTRACTS,
    CHANDAS_OVERLAY_ASSURANCE_RULES,
    getChandasOverlayAssuranceSummary
  };
}