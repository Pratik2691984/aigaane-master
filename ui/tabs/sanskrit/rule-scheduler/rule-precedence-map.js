"use strict";

/**
 * Deterministic Sanskrit Rule Precedence Map
 *
 * Inspection-first precedence metadata for future Paninian scheduling.
 * This file does not apply rules, mutate derivation state, or perform Sanskrit generation.
 */

const RULE_PRECEDENCE_SCHEMA_VERSION = "sanskrit-rule-precedence.v1";

const RULE_PRECEDENCE_RELATION_TYPES = Object.freeze({
  VIPRATISHEDHA: "VIPRATISHEDHA",
  ASIDDHATVA: "ASIDDHATVA",
  ANTARANGA: "ANTARANGA",
  BAHIRANGA: "BAHIRANGA",
  GENERAL_ORDER: "GENERAL_ORDER"
});

const RULE_PRECEDENCE_CONTRACTS = Object.freeze({
  deterministic: true,
  inspectionOnly: true,
  nonPerformative: true,
  runtimeIsolated: true,
  immutableSafe: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const RULE_PRECEDENCE_RELATIONS = Object.freeze([
  {
    id: "precedence.vipratisedha.param-karyam",
    type: RULE_PRECEDENCE_RELATION_TYPES.VIPRATISHEDHA,
    sutra: "1.4.2",
    label: "vipratiṣedhe paraṃ kāryam",
    summary: "When two rules conflict, the later rule is marked as higher precedence for deterministic scheduling.",
    priority: 100,
    diagnostics: ["conflict-arbitration", "later-rule-precedence"]
  },
  {
    id: "precedence.asiddhatva.placeholder",
    type: RULE_PRECEDENCE_RELATION_TYPES.ASIDDHATVA,
    sutra: "8.2.1",
    label: "pūrvatra asiddham",
    summary: "Asiddhatva is reserved as a scheduling-blocking relation for future derivation passes.",
    priority: 90,
    diagnostics: ["blocking-placeholder", "future-pass-safe"]
  },
  {
    id: "precedence.antaranga.preference",
    type: RULE_PRECEDENCE_RELATION_TYPES.ANTARANGA,
    sutra: null,
    label: "antaraṅga preference",
    summary: "Inner operations may be scheduled before outer operations when explicitly encoded.",
    priority: 80,
    diagnostics: ["inner-operation", "metadata-edge"]
  },
  {
    id: "precedence.bahiranga.deferred",
    type: RULE_PRECEDENCE_RELATION_TYPES.BAHIRANGA,
    sutra: null,
    label: "bahiraṅga deferred",
    summary: "Outer operations may be deferred behind encoded inner operations.",
    priority: 70,
    diagnostics: ["outer-operation", "metadata-edge"]
  },
  {
    id: "precedence.general.source-order",
    type: RULE_PRECEDENCE_RELATION_TYPES.GENERAL_ORDER,
    sutra: null,
    label: "source order",
    summary: "General deterministic fallback ordering preserves explicit source order.",
    priority: 10,
    diagnostics: ["fallback-order", "stable-sort"]
  }
]);

function getRulePrecedenceSummary() {
  return {
    schemaVersion: RULE_PRECEDENCE_SCHEMA_VERSION,
    contracts: RULE_PRECEDENCE_CONTRACTS,
    relationCount: RULE_PRECEDENCE_RELATIONS.length,
    relationTypes: Object.values(RULE_PRECEDENCE_RELATION_TYPES),
    relations: RULE_PRECEDENCE_RELATIONS.map((relation) => ({ ...relation }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    RULE_PRECEDENCE_SCHEMA_VERSION,
    RULE_PRECEDENCE_RELATION_TYPES,
    RULE_PRECEDENCE_CONTRACTS,
    RULE_PRECEDENCE_RELATIONS,
    getRulePrecedenceSummary
  };
}