export const SUTRA_REFERENCE_SAFETY_NOTE =
  "Sūtra reference overlay is deterministic structural metadata only; no authoritative sūtra interpretation or grammatical correctness claim is made.";

export const SUTRA_REFERENCE_NODES = [
  {
    id: "maheshvara_01",
    type: "maheshvara_sutra",
    label: "अइउण्",
    referenceCode: "MŚ-01",
    description: "Placeholder-safe Maheshvara sūtra reference node.",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "maheshvara_02",
    type: "maheshvara_sutra",
    label: "ऋऌक्",
    referenceCode: "MŚ-02",
    description: "Placeholder-safe Maheshvara sūtra reference node.",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "maheshvara_03",
    type: "maheshvara_sutra",
    label: "एओङ्",
    referenceCode: "MŚ-03",
    description: "Placeholder-safe Maheshvara sūtra reference node.",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "maheshvara_04",
    type: "maheshvara_sutra",
    label: "ऐऔच्",
    referenceCode: "MŚ-04",
    description: "Placeholder-safe Maheshvara sūtra reference node.",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "pratyahara_ac",
    type: "pratyahara",
    label: "अच्",
    referenceCode: "PR-AC",
    description: "Deterministic pratyāhāra reference node for vowel-class compression.",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "pratyahara_hal",
    type: "pratyahara",
    label: "हल्",
    referenceCode: "PR-HAL",
    description: "Deterministic pratyāhāra reference node for consonant-class compression.",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "symbolic_ac",
    type: "symbolic_class",
    label: "ac symbolic class",
    referenceCode: "SYM-AC",
    description: "Symbolic class reference linked from pratyāhāra metadata.",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "symbolic_hal",
    type: "symbolic_class",
    label: "hal symbolic class",
    referenceCode: "SYM-HAL",
    description: "Symbolic class reference linked from pratyāhāra metadata.",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
];

export const SUTRA_REFERENCE_EDGES = [
  {
    id: "edge.maheshvara_01.pratyahara_ac",
    source: "maheshvara_01",
    target: "pratyahara_ac",
    relation: "supports_pratyahara",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "edge.maheshvara_02.pratyahara_ac",
    source: "maheshvara_02",
    target: "pratyahara_ac",
    relation: "supports_pratyahara",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "edge.maheshvara_03.pratyahara_ac",
    source: "maheshvara_03",
    target: "pratyahara_ac",
    relation: "supports_pratyahara",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "edge.maheshvara_04.pratyahara_ac",
    source: "maheshvara_04",
    target: "pratyahara_ac",
    relation: "supports_pratyahara",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "edge.pratyahara_ac.symbolic_ac",
    source: "pratyahara_ac",
    target: "symbolic_ac",
    relation: "compresses_to_symbolic_class",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
  {
    id: "edge.pratyahara_hal.symbolic_hal",
    source: "pratyahara_hal",
    target: "symbolic_hal",
    relation: "compresses_to_symbolic_class",
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  },
];
