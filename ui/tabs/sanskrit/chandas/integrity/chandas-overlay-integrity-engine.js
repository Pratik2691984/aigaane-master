"use strict";

const {
  CHANDAS_OVERLAY_INTEGRITY_SCHEMA_VERSION,
  CHANDAS_OVERLAY_INTEGRITY_CONTRACTS,
  CHANDAS_OVERLAY_INTEGRITY_RULES,
  getChandasOverlayIntegritySummary
} = require("./chandas-overlay-integrity-map.js");

function normalizeChandasOverlayIntegrityRule(rule) {
  return {
    id: String(rule.id || ""),
    state: String(rule.state || ""),
    summary: String(rule.summary || ""),
    diagnostics: Array.isArray(rule.diagnostics) ? rule.diagnostics.map(String) : []
  };
}

function buildChandasOverlayIntegrityExport() {
  const summary = getChandasOverlayIntegritySummary();

  return {
    schemaVersion: CHANDAS_OVERLAY_INTEGRITY_SCHEMA_VERSION,
    contracts: { ...CHANDAS_OVERLAY_INTEGRITY_CONTRACTS },
    ready: true,
    integrityCount: CHANDAS_OVERLAY_INTEGRITY_RULES.length,
    states: Array.isArray(summary.states) ? summary.states.map(String) : [],
    rules: CHANDAS_OVERLAY_INTEGRITY_RULES.map(normalizeChandasOverlayIntegrityRule),
    diagnostics: {
      normalized: true,
      runtimeSafe: true,
      staticPreviewCompatible: true,
      mutationFree: true,
      assuranceSafe: true,
      replaySafe: true
    }
  };
}

function getChandasOverlayIntegrityDiagnostics() {
  const integrityExport = buildChandasOverlayIntegrityExport();

  return {
    schemaVersion: integrityExport.schemaVersion,
    ready: integrityExport.ready,
    integrityCount: integrityExport.integrityCount,
    contractsSatisfied: Object.values(integrityExport.contracts).every(Boolean),
    diagnostics: { ...integrityExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeChandasOverlayIntegrityRule,
    buildChandasOverlayIntegrityExport,
    getChandasOverlayIntegrityDiagnostics
  };
}