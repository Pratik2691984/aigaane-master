"use strict";

/**
 * Deterministic Sanskrit Lakāra Planning Map
 *
 * Inspection-first lakāra planning metadata for future controlled conjugation.
 * This layer identifies planned tense/mood/person/number candidates only.
 * It does not conjugate, mutate dhātus, mutate snapshots, or produce surface forms.
 */

const LAKARA_PLANNING_SCHEMA_VERSION = "sanskrit-lakara-planning.v1";

const LAKARA_PLANNING_TYPES = Object.freeze({
  LAKARA_PLAN: "LAKARA_PLAN",
  PURUSHA_PLAN: "PURUSHA_PLAN",
  VACANA_PLAN: "VACANA_PLAN",
  PADA_COMPATIBILITY: "PADA_COMPATIBILITY",
  DHATU_LAKARA_CANDIDATE: "DHATU_LAKARA_CANDIDATE",
  CONJUGATION_STATE: "CONJUGATION_STATE"
});

const LAKARA_PLANNING_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  nonMutating: true,
  runtimeIsolated: true,
  schedulerLinked: true,
  irLinked: true,
  queueLinked: true,
  traceLinked: true,
  checkpointLinked: true,
  executionGuardLinked: true,
  morphologyPlanningLinked: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const LAKARA_PLANNING_FIELDS = Object.freeze([
  {
    id: "lakara.lakara-plan",
    type: LAKARA_PLANNING_TYPES.LAKARA_PLAN,
    summary: "Non-executing lakāra planning candidate.",
    required: true,
    diagnostics: ["lakara-plan", "candidate-only"]
  },
  {
    id: "lakara.purusha-plan",
    type: LAKARA_PLANNING_TYPES.PURUSHA_PLAN,
    summary: "Non-executing puruṣa planning metadata.",
    required: false,
    diagnostics: ["purusha-plan", "person-compatible"]
  },
  {
    id: "lakara.vacana-plan",
    type: LAKARA_PLANNING_TYPES.VACANA_PLAN,
    summary: "Non-executing vacana planning metadata.",
    required: false,
    diagnostics: ["vacana-plan", "number-compatible"]
  },
  {
    id: "lakara.pada-compatibility",
    type: LAKARA_PLANNING_TYPES.PADA_COMPATIBILITY,
    summary: "Pada compatibility planning metadata for future conjugation.",
    required: false,
    diagnostics: ["pada-compatible", "voice-compatible"]
  },
  {
    id: "lakara.dhatu-lakara-candidate",
    type: LAKARA_PLANNING_TYPES.DHATU_LAKARA_CANDIDATE,
    summary: "Dhātu + lakāra planning candidate without conjugation execution.",
    required: true,
    diagnostics: ["dhatu-lakara", "non-executing"]
  },
  {
    id: "lakara.conjugation-state",
    type: LAKARA_PLANNING_TYPES.CONJUGATION_STATE,
    summary: "Planned conjugation state envelope without form generation.",
    required: true,
    diagnostics: ["conjugation-state", "surface-form-blocked"]
  }
]);

function getLakaraPlanningSummary() {
  return {
    schemaVersion: LAKARA_PLANNING_SCHEMA_VERSION,
    contracts: LAKARA_PLANNING_CONTRACTS,
    fieldCount: LAKARA_PLANNING_FIELDS.length,
    planningTypes: Object.values(LAKARA_PLANNING_TYPES),
    fields: LAKARA_PLANNING_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    LAKARA_PLANNING_SCHEMA_VERSION,
    LAKARA_PLANNING_TYPES,
    LAKARA_PLANNING_CONTRACTS,
    LAKARA_PLANNING_FIELDS,
    getLakaraPlanningSummary
  };
}