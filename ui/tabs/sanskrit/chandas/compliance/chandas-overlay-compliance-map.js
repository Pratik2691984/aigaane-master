"use strict";

/**
 * Deterministic Chandas Overlay Compliance Map
 *
 * Non-authoritative, inspection-only compliance metadata for overlay policy.
 * This layer does not execute metre logic, certify results, mutate registries,
 * or alter runtime derivation behavior.
 */

const CHANDAS_OVERLAY_COMPLIANCE_SCHEMA_VERSION = "chandas-overlay-compliance.v1";

const CHANDAS_OVERLAY_COMPLIANCE_STATES = Object.freeze({
  COMPLIANT: "COMPLIANT",
  REVIEW_REQUIRED: "REVIEW_REQUIRED",
  OBSERVABLE: "OBSERVABLE",
  NON_COMPLIANT: "NON_COMPLIANT"
});

const CHANDAS_OVERLAY_COMPLIANCE_CONTRACTS = Object.freeze({
  deterministic: true,
  inspectionOnly: true,
  nonAuthoritative: true,
  nonPerformative: true,
  runtimeIsolated: true,
  immutablePolicySafe: true,
  staticPreviewCompatible: true
});

const CHANDAS_OVERLAY_COMPLIANCE_RULES = Object.freeze([
  {
    id: "compliance.chandas.overlay.deterministic-export",
    state: CHANDAS_OVERLAY_COMPLIANCE_STATES.COMPLIANT,
    summary: "Compliance exports must be deterministic and schema-versioned.",
    diagnostics: ["deterministic-export", "schema-versioned"]
  },
  {
    id: "compliance.chandas.overlay.policy-readiness",
    state: CHANDAS_OVERLAY_COMPLIANCE_STATES.REVIEW_REQUIRED,
    summary: "Policy-ready overlays may be inspected for compliance readiness.",
    diagnostics: ["policy-readiness", "inspection-contract"]
  },
  {
    id: "compliance.chandas.overlay.static-preview",
    state: CHANDAS_OVERLAY_COMPLIANCE_STATES.OBSERVABLE,
    summary: "Static preview must receive normalized compliance summaries without backend dependency.",
    diagnostics: ["static-preview", "normalized-export"]
  },
  {
    id: "compliance.chandas.overlay.runtime-mutation",
    state: CHANDAS_OVERLAY_COMPLIANCE_STATES.NON_COMPLIANT,
    summary: "Any runtime mutation of overlay registries, snapshots, audit chains, certification state, governance state, or policy state is non-compliant.",
    diagnostics: ["mutation-detected", "immutable-chain-violation"]
  }
]);

function getChandasOverlayComplianceSummary() {
  return {
    schemaVersion: CHANDAS_OVERLAY_COMPLIANCE_SCHEMA_VERSION,
    contracts: CHANDAS_OVERLAY_COMPLIANCE_CONTRACTS,
    complianceCount: CHANDAS_OVERLAY_COMPLIANCE_RULES.length,
    states: Object.values(CHANDAS_OVERLAY_COMPLIANCE_STATES),
    rules: CHANDAS_OVERLAY_COMPLIANCE_RULES.map((rule) => ({ ...rule }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    CHANDAS_OVERLAY_COMPLIANCE_SCHEMA_VERSION,
    CHANDAS_OVERLAY_COMPLIANCE_STATES,
    CHANDAS_OVERLAY_COMPLIANCE_CONTRACTS,
    CHANDAS_OVERLAY_COMPLIANCE_RULES,
    getChandasOverlayComplianceSummary
  };
}