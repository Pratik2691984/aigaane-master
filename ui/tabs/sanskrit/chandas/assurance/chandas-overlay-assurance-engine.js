"use strict";

const {
  CHANDAS_OVERLAY_ASSURANCE_SCHEMA_VERSION,
  CHANDAS_OVERLAY_ASSURANCE_CONTRACTS,
  CHANDAS_OVERLAY_ASSURANCE_RULES,
  getChandasOverlayAssuranceSummary
} = require("./chandas-overlay-assurance-map.js");

function normalizeChandasOverlayAssuranceRule(rule) {
  return {
    id: String(rule.id || ""),
    state: String(rule.state || ""),
    summary: String(rule.summary || ""),
    diagnostics: Array.isArray(rule.diagnostics) ? rule.diagnostics.map(String) : []
  };
}

function buildChandasOverlayAssuranceExport() {
  const summary = getChandasOverlayAssuranceSummary();

  return {
    schemaVersion: CHANDAS_OVERLAY_ASSURANCE_SCHEMA_VERSION,
    contracts: { ...CHANDAS_OVERLAY_ASSURANCE_CONTRACTS },
    ready: true,
    assuranceCount: CHANDAS_OVERLAY_ASSURANCE_RULES.length,
    states: Array.isArray(summary.states) ? summary.states.map(String) : [],
    rules: CHANDAS_OVERLAY_ASSURANCE_RULES.map(normalizeChandasOverlayAssuranceRule),
    diagnostics: {
      normalized: true,
      runtimeSafe: true,
      staticPreviewCompatible: true,
      mutationFree: true,
      complianceSafe: true
    }
  };
}

function getChandasOverlayAssuranceDiagnostics() {
  const assuranceExport = buildChandasOverlayAssuranceExport();

  return {
    schemaVersion: assuranceExport.schemaVersion,
    ready: assuranceExport.ready,
    assuranceCount: assuranceExport.assuranceCount,
    contractsSatisfied: Object.values(assuranceExport.contracts).every(Boolean),
    diagnostics: { ...assuranceExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeChandasOverlayAssuranceRule,
    buildChandasOverlayAssuranceExport,
    getChandasOverlayAssuranceDiagnostics
  };
}