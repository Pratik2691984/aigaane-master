"use strict";

const {
  CHANDAS_OVERLAY_COMPLIANCE_SCHEMA_VERSION,
  CHANDAS_OVERLAY_COMPLIANCE_CONTRACTS,
  CHANDAS_OVERLAY_COMPLIANCE_RULES,
  getChandasOverlayComplianceSummary
} = require("./chandas-overlay-compliance-map.js");

function normalizeChandasOverlayComplianceRule(rule) {
  return {
    id: String(rule.id || ""),
    state: String(rule.state || ""),
    summary: String(rule.summary || ""),
    diagnostics: Array.isArray(rule.diagnostics) ? rule.diagnostics.map(String) : []
  };
}

function buildChandasOverlayComplianceExport() {
  const summary = getChandasOverlayComplianceSummary();

  return {
    schemaVersion: CHANDAS_OVERLAY_COMPLIANCE_SCHEMA_VERSION,
    contracts: { ...CHANDAS_OVERLAY_COMPLIANCE_CONTRACTS },
    ready: true,
    complianceCount: CHANDAS_OVERLAY_COMPLIANCE_RULES.length,
    states: Array.isArray(summary.states) ? summary.states.map(String) : [],
    rules: CHANDAS_OVERLAY_COMPLIANCE_RULES.map(normalizeChandasOverlayComplianceRule),
    diagnostics: {
      normalized: true,
      runtimeSafe: true,
      staticPreviewCompatible: true,
      mutationFree: true,
      policySafe: true
    }
  };
}

function getChandasOverlayComplianceDiagnostics() {
  const complianceExport = buildChandasOverlayComplianceExport();

  return {
    schemaVersion: complianceExport.schemaVersion,
    ready: complianceExport.ready,
    complianceCount: complianceExport.complianceCount,
    contractsSatisfied: Object.values(complianceExport.contracts).every(Boolean),
    diagnostics: { ...complianceExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeChandasOverlayComplianceRule,
    buildChandasOverlayComplianceExport,
    getChandasOverlayComplianceDiagnostics
  };
}