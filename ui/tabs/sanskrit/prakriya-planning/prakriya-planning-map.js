"use strict";

/**
 * Deterministic Sanskrit Prakriyā Planning Map
 *
 * Converts derivation graph planning into ordered prakriyā workflow metadata.
 * This layer plans derivational stages only. It does not execute rules,
 * mutate snapshots, apply sandhi, conjugate, inflect, or produce surface forms.
 */

const PRAKRIYA_PLANNING_SCHEMA_VERSION = "sanskrit-prakriya-planning.v1";

const PRAKRIYA_STAGE_TYPES = Object.freeze({
  DHATU_STAGE: "DHATU_STAGE",
  MORPHOLOGY_STAGE: "MORPHOLOGY_STAGE",
  LAKARA_STAGE: "LAKARA_STAGE",
  SANDHI_STAGE: "SANDHI_STAGE",
  TERMINAL_STAGE: "TERMINAL_STAGE",
  DIAGNOSTIC_STAGE: "DIAGNOSTIC_STAGE"
});

const PRAKRIYA_PLANNING_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  nonMutating: true,
  runtimeIsolated: true,
  schedulerLinked: true,
  queueLinked: true,
  traceLinked: true,
  checkpointLinked: true,
  executionGuardLinked: true,
  derivationGraphLinked: true,
  sandhiPlanningLinked: true,
  morphologyPlanningLinked: true,
  lakaraPlanningLinked: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const PRAKRIYA_PLANNING_FIELDS = Object.freeze([
  {
    id: "prakriya.dhatu-stage",
    type: PRAKRIYA_STAGE_TYPES.DHATU_STAGE,
    order: 10,
    summary: "Initial dhātu planning stage.",
    required: true,
    diagnostics: ["dhatu-stage", "workflow-start"]
  },
  {
    id: "prakriya.morphology-stage",
    type: PRAKRIYA_STAGE_TYPES.MORPHOLOGY_STAGE,
    order: 20,
    summary: "Morphology planning stage linked to planned stem/root/affix metadata.",
    required: true,
    diagnostics: ["morphology-stage", "morphology-linked"]
  },
  {
    id: "prakriya.lakara-stage",
    type: PRAKRIYA_STAGE_TYPES.LAKARA_STAGE,
    order: 30,
    summary: "Lakāra planning stage linked to tense/mood/person/number metadata.",
    required: true,
    diagnostics: ["lakara-stage", "lakara-linked"]
  },
  {
    id: "prakriya.sandhi-stage",
    type: PRAKRIYA_STAGE_TYPES.SANDHI_STAGE,
    order: 40,
    summary: "Sandhi planning stage linked to non-executing boundary candidates.",
    required: true,
    diagnostics: ["sandhi-stage", "sandhi-linked"]
  },
  {
    id: "prakriya.terminal-stage",
    type: PRAKRIYA_STAGE_TYPES.TERMINAL_STAGE,
    order: 50,
    summary: "Terminal planning stage without surface-form production.",
    required: true,
    diagnostics: ["terminal-stage", "surface-form-blocked"]
  },
  {
    id: "prakriya.diagnostic-stage",
    type: PRAKRIYA_STAGE_TYPES.DIAGNOSTIC_STAGE,
    order: 60,
    summary: "Normalized diagnostic planning stage for workflow inspection.",
    required: false,
    diagnostics: ["diagnostic-stage", "inspection-safe"]
  }
]);

function getPrakriyaPlanningSummary() {
  return {
    schemaVersion: PRAKRIYA_PLANNING_SCHEMA_VERSION,
    contracts: PRAKRIYA_PLANNING_CONTRACTS,
    fieldCount: PRAKRIYA_PLANNING_FIELDS.length,
    stageTypes: Object.values(PRAKRIYA_STAGE_TYPES),
    fields: PRAKRIYA_PLANNING_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    PRAKRIYA_PLANNING_SCHEMA_VERSION,
    PRAKRIYA_STAGE_TYPES,
    PRAKRIYA_PLANNING_CONTRACTS,
    PRAKRIYA_PLANNING_FIELDS,
    getPrakriyaPlanningSummary
  };
}