"use strict";

/**
 * Deterministic Sanskrit Morphology Planning Map
 *
 * Inspection-first morphology planning metadata for future controlled derivation.
 * This layer identifies planned morphology candidates only. It does not apply
 * inflection, mutate stems, mutate snapshots, or produce surface forms.
 */

const MORPHOLOGY_PLANNING_SCHEMA_VERSION = "sanskrit-morphology-planning.v1";

const MORPHOLOGY_PLANNING_TYPES = Object.freeze({
  STEM_PLAN: "STEM_PLAN",
  ROOT_PLAN: "ROOT_PLAN",
  AFFIX_PLAN: "AFFIX_PLAN",
  PADA_PLAN: "PADA_PLAN",
  GANA_PLAN: "GANA_PLAN",
  DERIVATIONAL_STATE: "DERIVATIONAL_STATE"
});

const MORPHOLOGY_PLANNING_CONTRACTS = Object.freeze({
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
  replaySafe: true,
  staticPreviewCompatible: true
});

const MORPHOLOGY_PLANNING_FIELDS = Object.freeze([
  {
    id: "morphology.stem-plan",
    type: MORPHOLOGY_PLANNING_TYPES.STEM_PLAN,
    summary: "Non-executing stem planning candidate.",
    required: true,
    diagnostics: ["stem-plan", "candidate-only"]
  },
  {
    id: "morphology.root-plan",
    type: MORPHOLOGY_PLANNING_TYPES.ROOT_PLAN,
    summary: "Non-executing root planning candidate linked to dhātu metadata.",
    required: false,
    diagnostics: ["root-plan", "dhatu-compatible"]
  },
  {
    id: "morphology.affix-plan",
    type: MORPHOLOGY_PLANNING_TYPES.AFFIX_PLAN,
    summary: "Non-executing affix/pratyaya planning candidate.",
    required: false,
    diagnostics: ["affix-plan", "pratyaya-compatible"]
  },
  {
    id: "morphology.pada-plan",
    type: MORPHOLOGY_PLANNING_TYPES.PADA_PLAN,
    summary: "Non-executing pada metadata planning candidate.",
    required: false,
    diagnostics: ["pada-plan", "voice-compatible"]
  },
  {
    id: "morphology.gana-plan",
    type: MORPHOLOGY_PLANNING_TYPES.GANA_PLAN,
    summary: "Non-executing gaṇa metadata planning candidate.",
    required: false,
    diagnostics: ["gana-plan", "class-compatible"]
  },
  {
    id: "morphology.derivational-state",
    type: MORPHOLOGY_PLANNING_TYPES.DERIVATIONAL_STATE,
    summary: "Planned derivational state envelope without morphology execution.",
    required: true,
    diagnostics: ["derivational-state", "non-executing"]
  }
]);

function getMorphologyPlanningSummary() {
  return {
    schemaVersion: MORPHOLOGY_PLANNING_SCHEMA_VERSION,
    contracts: MORPHOLOGY_PLANNING_CONTRACTS,
    fieldCount: MORPHOLOGY_PLANNING_FIELDS.length,
    planningTypes: Object.values(MORPHOLOGY_PLANNING_TYPES),
    fields: MORPHOLOGY_PLANNING_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    MORPHOLOGY_PLANNING_SCHEMA_VERSION,
    MORPHOLOGY_PLANNING_TYPES,
    MORPHOLOGY_PLANNING_CONTRACTS,
    MORPHOLOGY_PLANNING_FIELDS,
    getMorphologyPlanningSummary
  };
}