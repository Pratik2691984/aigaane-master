export const DHATU_SEMANTIC_SAFETY_NOTE =
  "Dhātu semantic graph is deterministic placeholder metadata only; no authoritative semantic or grammatical correctness claim is made.";

export const DHATU_SEMANTIC_NODES = [
  {
    id: "dhatu_gam",
    type: "dhatu",
    label: "गम् / gam",
    semanticCluster: "motion",
    description: "Placeholder-safe dhatu node associated with motion semantics.",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "dhatu_bhu",
    type: "dhatu",
    label: "भू / bhū",
    semanticCluster: "being",
    description: "Placeholder-safe dhatu node associated with being semantics.",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "dhatu_ni",
    type: "dhatu",
    label: "नी / nī",
    semanticCluster: "guidance",
    description: "Placeholder-safe dhatu node associated with guidance semantics.",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "cluster_motion",
    type: "semantic_cluster",
    label: "motion",
    semanticCluster: "motion",
    description: "Deterministic placeholder semantic cluster for motion.",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "cluster_being",
    type: "semantic_cluster",
    label: "being",
    semanticCluster: "being",
    description: "Deterministic placeholder semantic cluster for being.",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "cluster_guidance",
    type: "semantic_cluster",
    label: "guidance",
    semanticCluster: "guidance",
    description: "Deterministic placeholder semantic cluster for guidance.",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "cluster_transition",
    type: "semantic_cluster",
    label: "transition",
    semanticCluster: "transition",
    description: "Deterministic placeholder semantic cluster for transition.",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
];

export const DHATU_SEMANTIC_EDGES = [
  {
    id: "edge.dhatu_gam.cluster_motion",
    source: "dhatu_gam",
    target: "cluster_motion",
    relation: "belongs_to_cluster",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "edge.dhatu_bhu.cluster_being",
    source: "dhatu_bhu",
    target: "cluster_being",
    relation: "belongs_to_cluster",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "edge.dhatu_ni.cluster_guidance",
    source: "dhatu_ni",
    target: "cluster_guidance",
    relation: "belongs_to_cluster",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "edge.cluster_motion.cluster_transition",
    source: "cluster_motion",
    target: "cluster_transition",
    relation: "suggests_transition",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "edge.cluster_guidance.cluster_motion",
    source: "cluster_guidance",
    target: "cluster_motion",
    relation: "guides_motion",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
  {
    id: "edge.cluster_being.cluster_transition",
    source: "cluster_being",
    target: "cluster_transition",
    relation: "state_to_transition",
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  },
];
