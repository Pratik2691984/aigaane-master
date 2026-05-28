export const PRAKRIYA_COMPOSITION_MAP = [
  {
    id: "subantaGeneration",
    label: "Subanta Generation",
    stageOrder: 10,
    description: "Generate explicit noun padas from deterministic subanta inputs.",
    reversible: true,
    confidence: "deterministic",
    color: "#f472b6",
  },
  {
    id: "tinantaGeneration",
    label: "Tinanta Generation",
    stageOrder: 20,
    description: "Generate explicit verb pada from deterministic tinanta input.",
    reversible: true,
    confidence: "deterministic",
    color: "#2dd4bf",
  },
  {
    id: "padaAssembly",
    label: "Pada Assembly",
    stageOrder: 30,
    description: "Assemble generated padas in deterministic structural order.",
    reversible: true,
    confidence: "deterministic",
    color: "#38bdf8",
  },
  {
    id: "sandhiExecution",
    label: "Sandhi Execution",
    stageOrder: 40,
    description: "Optionally execute deterministic sandhi across adjacent padas.",
    reversible: true,
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "sentenceComposition",
    label: "Sentence Composition",
    stageOrder: 50,
    description: "Emit sentence-level structural preview without semantic interpretation.",
    reversible: true,
    confidence: "deterministic",
    color: "#22c55e",
  },
  {
    id: "reversePreview",
    label: "Reverse Preview",
    stageOrder: 60,
    description: "Collect structural reverse metadata from generated components.",
    reversible: true,
    confidence: "deterministic",
    color: "#a855f7",
  },
  {
    id: "unresolvedComposition",
    label: "Unresolved Composition",
    stageOrder: 70,
    description: "Preserve unsupported components as explicit unresolved diagnostics.",
    reversible: false,
    confidence: "deterministic",
    color: "#94a3b8",
  },
];

export function normalizePrakriyaStage(value) {
  return String(value ?? "")
    .normalize("NFC")
    .trim()
    .replace(/\s+/g, " ");
}

export function listPrakriyaStages() {
  return [...PRAKRIYA_COMPOSITION_MAP].sort((left, right) => {
    if (left.stageOrder !== right.stageOrder) return left.stageOrder - right.stageOrder;
    return left.id.localeCompare(right.id);
  });
}

export function buildPrakriyaStageSequence() {
  return listPrakriyaStages().map((stage) => ({ ...stage }));
}
