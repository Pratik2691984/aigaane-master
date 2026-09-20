"use strict";

/**
 * Deterministic Sanskrit Sandhi Planning Map
 *
 * Inspection-first sandhi planning metadata for future controlled derivation.
 * This layer identifies planned boundary candidates only. It does not apply
 * sandhi, mutate text, mutate snapshots, or produce surface forms.
 */

const SANDHI_PLANNING_SCHEMA_VERSION = "sanskrit-sandhi-planning.v1";

const SANDHI_PLANNING_TYPES = Object.freeze({
  VOWEL_BOUNDARY: "VOWEL_BOUNDARY",
  CONSONANT_BOUNDARY: "CONSONANT_BOUNDARY",
  VISARGA_BOUNDARY: "VISARGA_BOUNDARY",
  ANUSVARA_BOUNDARY: "ANUSVARA_BOUNDARY",
  INTERNAL_BOUNDARY: "INTERNAL_BOUNDARY",
  EXTERNAL_BOUNDARY: "EXTERNAL_BOUNDARY"
});

const SANDHI_PLANNING_CONTRACTS = Object.freeze({
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
  replaySafe: true,
  staticPreviewCompatible: true
});

const SANDHI_PLANNING_FIELDS = Object.freeze([
  {
    id: "sandhi.vowel-boundary",
    type: SANDHI_PLANNING_TYPES.VOWEL_BOUNDARY,
    summary: "Non-executing vowel boundary planning candidate.",
    required: true,
    diagnostics: ["vowel-boundary", "candidate-only"]
  },
  {
    id: "sandhi.consonant-boundary",
    type: SANDHI_PLANNING_TYPES.CONSONANT_BOUNDARY,
    summary: "Non-executing consonant boundary planning candidate.",
    required: false,
    diagnostics: ["consonant-boundary", "candidate-only"]
  },
  {
    id: "sandhi.visarga-boundary",
    type: SANDHI_PLANNING_TYPES.VISARGA_BOUNDARY,
    summary: "Non-executing visarga boundary planning candidate.",
    required: false,
    diagnostics: ["visarga-boundary", "candidate-only"]
  },
  {
    id: "sandhi.anusvara-boundary",
    type: SANDHI_PLANNING_TYPES.ANUSVARA_BOUNDARY,
    summary: "Non-executing anusvāra boundary planning candidate.",
    required: false,
    diagnostics: ["anusvara-boundary", "candidate-only"]
  },
  {
    id: "sandhi.internal-boundary",
    type: SANDHI_PLANNING_TYPES.INTERNAL_BOUNDARY,
    summary: "Internal sandhi planning boundary within a derivational unit.",
    required: false,
    diagnostics: ["internal-boundary", "derivation-local"]
  },
  {
    id: "sandhi.external-boundary",
    type: SANDHI_PLANNING_TYPES.EXTERNAL_BOUNDARY,
    summary: "External sandhi planning boundary between derivational units.",
    required: false,
    diagnostics: ["external-boundary", "unit-boundary"]
  }
]);

function getSandhiPlanningSummary() {
  return {
    schemaVersion: SANDHI_PLANNING_SCHEMA_VERSION,
    contracts: SANDHI_PLANNING_CONTRACTS,
    fieldCount: SANDHI_PLANNING_FIELDS.length,
    planningTypes: Object.values(SANDHI_PLANNING_TYPES),
    fields: SANDHI_PLANNING_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    SANDHI_PLANNING_SCHEMA_VERSION,
    SANDHI_PLANNING_TYPES,
    SANDHI_PLANNING_CONTRACTS,
    SANDHI_PLANNING_FIELDS,
    getSandhiPlanningSummary
  };
}