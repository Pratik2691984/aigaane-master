"use strict";

const {
  RULE_PRECEDENCE_SCHEMA_VERSION,
  RULE_PRECEDENCE_CONTRACTS,
  RULE_PRECEDENCE_RELATIONS,
  getRulePrecedenceSummary
} = require("./rule-precedence-map.js");

function normalizeRulePrecedenceRelation(relation) {
  return {
    id: String(relation.id || ""),
    type: String(relation.type || ""),
    sutra: relation.sutra === null || relation.sutra === undefined ? null : String(relation.sutra),
    label: String(relation.label || ""),
    summary: String(relation.summary || ""),
    priority: Number.isFinite(Number(relation.priority)) ? Number(relation.priority) : 0,
    diagnostics: Array.isArray(relation.diagnostics) ? relation.diagnostics.map(String) : []
  };
}

function buildRulePrecedenceGraphExport() {
  const summary = getRulePrecedenceSummary();

  return {
    schemaVersion: RULE_PRECEDENCE_SCHEMA_VERSION,
    contracts: { ...RULE_PRECEDENCE_CONTRACTS },
    ready: true,
    relationCount: RULE_PRECEDENCE_RELATIONS.length,
    relationTypes: Array.isArray(summary.relationTypes) ? summary.relationTypes.map(String) : [],
    relations: RULE_PRECEDENCE_RELATIONS.map(normalizeRulePrecedenceRelation),
    diagnostics: {
      normalized: true,
      deterministic: true,
      runtimeSafe: true,
      replaySafe: true,
      mutationFree: true,
      schedulerOnly: true
    }
  };
}

function scheduleRulesByPrecedence(candidateRules) {
  const rules = Array.isArray(candidateRules) ? candidateRules : [];

  return rules
    .map((rule, index) => ({
      ...rule,
      __sourceIndex: index,
      precedencePriority: Number.isFinite(Number(rule.precedencePriority))
        ? Number(rule.precedencePriority)
        : 0
    }))
    .sort((a, b) => {
      if (b.precedencePriority !== a.precedencePriority) {
        return b.precedencePriority - a.precedencePriority;
      }
      return a.__sourceIndex - b.__sourceIndex;
    })
    .map(({ __sourceIndex, ...rule }) => rule);
}

function getRuleSchedulerDiagnostics() {
  const graphExport = buildRulePrecedenceGraphExport();

  return {
    schemaVersion: graphExport.schemaVersion,
    ready: graphExport.ready,
    relationCount: graphExport.relationCount,
    contractsSatisfied: Object.values(graphExport.contracts).every(Boolean),
    diagnostics: { ...graphExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeRulePrecedenceRelation,
    buildRulePrecedenceGraphExport,
    scheduleRulesByPrecedence,
    getRuleSchedulerDiagnostics
  };
}