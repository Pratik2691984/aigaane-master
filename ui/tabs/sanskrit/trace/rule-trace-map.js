export const RULE_TRACE_SAFETY_NOTE =
  "Rule trace layer is deterministic structural metadata only; no authoritative Paninian interpretation or grammatical correctness claim is made.";

export const RULE_TRACE_NODES = [
  {
    id: "trace_ac_reference",
    type: "sutra_reference",
    label: "ac reference",
    stage: "sutra_reference",
    description: "Placeholder-safe trace node for ac reference context.",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "trace_hal_reference",
    type: "sutra_reference",
    label: "hal reference",
    stage: "sutra_reference",
    description: "Placeholder-safe trace node for hal reference context.",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "trace_sandhi_boundary",
    type: "sandhi",
    label: "sandhi boundary",
    stage: "boundary_inspection",
    description: "Deterministic trace node for structural sandhi boundary inspection.",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "trace_symbolic_class",
    type: "symbolic",
    label: "symbolic class",
    stage: "symbolic_compression",
    description: "Deterministic trace node for symbolic class compression metadata.",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "trace_derivation_overlay",
    type: "derivation_overlay",
    label: "derivation overlay",
    stage: "derivation_overlay",
    description: "Placeholder-safe trace node for derivation overlay inspection.",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "trace_semantic_cluster",
    type: "semantic_cluster",
    label: "semantic cluster",
    stage: "semantic_overlay",
    description: "Placeholder-safe trace node for semantic cluster overlay inspection.",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
];

export const RULE_TRACE_EDGES = [
  {
    id: "edge.trace_ac_reference.trace_symbolic_class",
    source: "trace_ac_reference",
    target: "trace_symbolic_class",
    relation: "feeds_symbolic_class",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "edge.trace_hal_reference.trace_symbolic_class",
    source: "trace_hal_reference",
    target: "trace_symbolic_class",
    relation: "feeds_symbolic_class",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "edge.trace_symbolic_class.trace_sandhi_boundary",
    source: "trace_symbolic_class",
    target: "trace_sandhi_boundary",
    relation: "informs_boundary_inspection",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "edge.trace_sandhi_boundary.trace_derivation_overlay",
    source: "trace_sandhi_boundary",
    target: "trace_derivation_overlay",
    relation: "feeds_derivation_overlay",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
  {
    id: "edge.trace_derivation_overlay.trace_semantic_cluster",
    source: "trace_derivation_overlay",
    target: "trace_semantic_cluster",
    relation: "feeds_semantic_overlay",
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  },
];
