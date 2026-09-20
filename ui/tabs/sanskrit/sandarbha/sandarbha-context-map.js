export const SANDARBHA_CONTEXT_MAP = [
  {
    id: "localDependencyNeighborhood",
    label: "local dependency neighborhood",
    sourceLayer: "vakya-dependency",
    trigger: "dependency-edge",
    description: "Deterministic local context neighborhood from existing vākya dependency edges.",
    confidence: "deterministic",
    color: "#38bdf8",
  },
  {
    id: "karakaContinuity",
    label: "kāraka continuity",
    sourceLayer: "karaka-overlay",
    trigger: "repeated-or-adjacent-karaka",
    description: "Deterministic continuity candidate from repeated or adjacent explicit kāraka roles.",
    confidence: "deterministic",
    color: "#22c55e",
  },
  {
    id: "morphologyContinuity",
    label: "morphology continuity",
    sourceLayer: "morphology-transition",
    trigger: "repeated-vibhakti-linga-vacana",
    description: "Deterministic continuity candidate from repeated explicit morphology attributes.",
    confidence: "deterministic",
    color: "#a855f7",
  },
  {
    id: "derivationContinuity",
    label: "derivation continuity",
    sourceLayer: "derivation-graph",
    trigger: "shared-lineage",
    description: "Deterministic continuity candidate from shared explicit derivation lineage.",
    confidence: "deterministic",
    color: "#60a5fa",
  },
  {
    id: "semanticAdjacency",
    label: "semantic adjacency",
    sourceLayer: "semantic-overlay",
    trigger: "existing-semantic-edge",
    description: "Deterministic adjacency from existing semantic overlay identifiers.",
    confidence: "deterministic",
    color: "#16a34a",
  },
  {
    id: "finiteVerbContext",
    label: "finite verb context",
    sourceLayer: "vakya-dependency",
    trigger: "finite-verb-anchor",
    description: "Deterministic finite verb context from explicit vākya anchor metadata.",
    confidence: "deterministic",
    color: "#f97316",
  },
  {
    id: "pronounAntecedentCandidate",
    label: "pronoun antecedent candidate",
    sourceLayer: "token-metadata",
    trigger: "explicit-pronoun-marker",
    description: "Candidate-only pronoun context from explicit pronoun-like metadata; no antecedent resolution is claimed.",
    confidence: "deterministic",
    color: "#f43f5e",
  },
  {
    id: "unresolvedContextCandidate",
    label: "unresolved context candidate",
    sourceLayer: "sandarbha-context",
    trigger: "unresolved",
    description: "Read-only unresolved context candidate preserved without forced resolution.",
    confidence: "deterministic",
    color: "#94a3b8",
  },
];

export function normalizeSandarbhaRelation(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[\s_]+/g, "-");
}

export function getSandarbhaRelation(id) {
  const normalized = normalizeSandarbhaRelation(id);
  return SANDARBHA_CONTEXT_MAP.find((relation) => normalizeSandarbhaRelation(relation.id) === normalized) || null;
}

export function listSandarbhaRelations() {
  return SANDARBHA_CONTEXT_MAP.map((relation) => ({ ...relation }));
}
