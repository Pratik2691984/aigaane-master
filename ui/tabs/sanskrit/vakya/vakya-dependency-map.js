export const VAKYA_DEPENDENCY_MAP = [
  {
    id: "finiteVerbAnchor",
    label: "finite verb anchor",
    sourceRole: "finite-verb",
    targetRole: "sentence",
    triggerKaraka: null,
    triggerMorphology: ["tinganta", "tiṅanta", "finite-verb", "finiteVerb"],
    description: "Deterministic anchor for explicit finite verbal morphology metadata.",
    confidence: "deterministic",
    color: "#38bdf8",
  },
  {
    id: "kartaToVerb",
    label: "kartā to verb",
    sourceRole: "karta",
    targetRole: "finite-verb",
    triggerKaraka: "karta",
    triggerMorphology: [],
    description: "Deterministic kāraka-to-anchor edge for explicit kartā metadata.",
    confidence: "deterministic",
    color: "#22c55e",
  },
  {
    id: "karmaToVerb",
    label: "karma to verb",
    sourceRole: "karma",
    targetRole: "finite-verb",
    triggerKaraka: "karma",
    triggerMorphology: [],
    description: "Deterministic kāraka-to-anchor edge for explicit karma metadata.",
    confidence: "deterministic",
    color: "#f97316",
  },
  {
    id: "karanaToVerb",
    label: "karaṇa to verb",
    sourceRole: "karana",
    targetRole: "finite-verb",
    triggerKaraka: "karana",
    triggerMorphology: [],
    description: "Deterministic kāraka-to-anchor edge for explicit karaṇa metadata.",
    confidence: "deterministic",
    color: "#14b8a6",
  },
  {
    id: "sampradanaToVerb",
    label: "sampradāna to verb",
    sourceRole: "sampradana",
    targetRole: "finite-verb",
    triggerKaraka: "sampradana",
    triggerMorphology: [],
    description: "Deterministic kāraka-to-anchor edge for explicit sampradāna metadata.",
    confidence: "deterministic",
    color: "#a855f7",
  },
  {
    id: "apadanaToVerb",
    label: "apādāna to verb",
    sourceRole: "apadana",
    targetRole: "finite-verb",
    triggerKaraka: "apadana",
    triggerMorphology: [],
    description: "Deterministic kāraka-to-anchor edge for explicit apādāna metadata.",
    confidence: "deterministic",
    color: "#f43f5e",
  },
  {
    id: "adhikaranaToVerb",
    label: "adhikaraṇa to verb",
    sourceRole: "adhikarana",
    targetRole: "finite-verb",
    triggerKaraka: "adhikarana",
    triggerMorphology: [],
    description: "Deterministic kāraka-to-anchor edge for explicit adhikaraṇa metadata.",
    confidence: "deterministic",
    color: "#0ea5e9",
  },
  {
    id: "modifierToHead",
    label: "modifier to head",
    sourceRole: "modifier",
    targetRole: "head",
    triggerKaraka: null,
    triggerMorphology: ["modifier"],
    description: "Reserved deterministic modifier relation; not inferred without explicit metadata.",
    confidence: "deterministic",
    color: "#facc15",
  },
  {
    id: "padaAdjacency",
    label: "pada adjacency",
    sourceRole: "pada",
    targetRole: "pada",
    triggerKaraka: null,
    triggerMorphology: ["adjacent"],
    description: "Reserved deterministic adjacency relation; not used as syntactic evidence.",
    confidence: "deterministic",
    color: "#94a3b8",
  },
  {
    id: "unresolvedCandidate",
    label: "unresolved candidate",
    sourceRole: "candidate",
    targetRole: "unresolved",
    triggerKaraka: null,
    triggerMorphology: ["unresolved"],
    description: "Read-only unresolved candidate when no deterministic anchor is available.",
    confidence: "deterministic",
    color: "#cbd5e1",
  },
];

export function normalizeDependencyRole(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[\s_]+/g, "-");
}

export function getDependencyRelationByKaraka(karaka) {
  const normalized = normalizeDependencyRole(karaka);
  if (!normalized) return null;
  return VAKYA_DEPENDENCY_MAP.find(
    (relation) => relation.triggerKaraka && normalizeDependencyRole(relation.triggerKaraka) === normalized,
  ) || null;
}

export function listVakyaDependencyRelations() {
  return VAKYA_DEPENDENCY_MAP.map((relation) => ({
    ...relation,
    triggerMorphology: [...relation.triggerMorphology],
  }));
}
