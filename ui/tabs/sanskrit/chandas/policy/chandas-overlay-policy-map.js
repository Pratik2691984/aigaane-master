"use strict";

/**
 * Deterministic Chandas Overlay Policy Map
 *
 * Non-authoritative, inspection-only policy metadata for overlay governance.
 * This layer does not execute metre logic, certify results, mutate registries,
 * or affect runtime derivation behavior.
 */

const CHANDAS_OVERLAY_POLICY_SCHEMA_VERSION = "chandas-overlay-policy.v1";

const CHANDAS_OVERLAY_POLICY_LEVELS = Object.freeze({
  STRICT: "STRICT",
  REVIEW: "REVIEW",
  OBSERVE: "OBSERVE",
  BLOCKED: "BLOCKED"
});

const CHANDAS_OVERLAY_POLICY_CONTRACTS = Object.freeze({
  deterministic: true,
  inspectionOnly: true,
  nonAuthoritative: true,
  nonPerformative: true,
  runtimeIsolated: true,
  immutableGovernanceSafe: true,
  staticPreviewCompatible: true
});

const CHANDAS_OVERLAY_POLICY_RULES = Object.freeze([
  {
    id: "policy.chandas.overlay.runtime-isolation",
    level: CHANDAS_OVERLAY_POLICY_LEVELS.STRICT,
    summary: "Policy exports must not invoke runtime metre, cadence, or recitation engines.",
    diagnostics: ["runtime-isolation", "no-engine-execution"]
  },
  {
    id: "policy.chandas.overlay.governance-readiness",
    level: CHANDAS_OVERLAY_POLICY_LEVELS.REVIEW,
    summary: "Governance-certified overlays may be inspected for policy readiness.",
    diagnostics: ["governance-readiness", "inspection-contract"]
  },
  {
    id: "policy.chandas.overlay.static-preview",
    level: CHANDAS_OVERLAY_POLICY_LEVELS.OBSERVE,
    summary: "Static preview must receive normalized policy summaries without backend dependency.",
    diagnostics: ["static-preview", "normalized-export"]
  },
  {
    id: "policy.chandas.overlay.mutation-block",
    level: CHANDAS_OVERLAY_POLICY_LEVELS.BLOCKED,
    summary: "Policy layer must not mutate overlay registries, snapshots, audit chains, or certification state.",
    diagnostics: ["mutation-blocked", "immutable-chain-safe"]
  }
]);

function getChandasOverlayPolicySummary() {
  return {
    schemaVersion: CHANDAS_OVERLAY_POLICY_SCHEMA_VERSION,
    contracts: CHANDAS_OVERLAY_POLICY_CONTRACTS,
    policyCount: CHANDAS_OVERLAY_POLICY_RULES.length,
    levels: Object.values(CHANDAS_OVERLAY_POLICY_LEVELS),
    rules: CHANDAS_OVERLAY_POLICY_RULES.map((rule) => ({ ...rule }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    CHANDAS_OVERLAY_POLICY_SCHEMA_VERSION,
    CHANDAS_OVERLAY_POLICY_LEVELS,
    CHANDAS_OVERLAY_POLICY_CONTRACTS,
    CHANDAS_OVERLAY_POLICY_RULES,
    getChandasOverlayPolicySummary
  };
}