"use strict";

const {
  CHANDAS_OVERLAY_POLICY_SCHEMA_VERSION,
  CHANDAS_OVERLAY_POLICY_CONTRACTS,
  CHANDAS_OVERLAY_POLICY_RULES,
  getChandasOverlayPolicySummary
} = require("./chandas-overlay-policy-map.js");

function normalizeChandasOverlayPolicyRule(rule) {
  return {
    id: String(rule.id || ""),
    level: String(rule.level || ""),
    summary: String(rule.summary || ""),
    diagnostics: Array.isArray(rule.diagnostics) ? rule.diagnostics.map(String) : []
  };
}

function buildChandasOverlayPolicyExport() {
  const summary = getChandasOverlayPolicySummary();

  return {
    schemaVersion: CHANDAS_OVERLAY_POLICY_SCHEMA_VERSION,
    contracts: { ...CHANDAS_OVERLAY_POLICY_CONTRACTS },
    ready: true,
    policyCount: CHANDAS_OVERLAY_POLICY_RULES.length,
    levels: Array.isArray(summary.levels) ? summary.levels.map(String) : [],
    rules: CHANDAS_OVERLAY_POLICY_RULES.map(normalizeChandasOverlayPolicyRule),
    diagnostics: {
      normalized: true,
      runtimeSafe: true,
      staticPreviewCompatible: true,
      mutationFree: true
    }
  };
}

function getChandasOverlayPolicyDiagnostics() {
  const policyExport = buildChandasOverlayPolicyExport();

  return {
    schemaVersion: policyExport.schemaVersion,
    ready: policyExport.ready,
    policyCount: policyExport.policyCount,
    contractsSatisfied: Object.values(policyExport.contracts).every(Boolean),
    diagnostics: { ...policyExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeChandasOverlayPolicyRule,
    buildChandasOverlayPolicyExport,
    getChandasOverlayPolicyDiagnostics
  };
}