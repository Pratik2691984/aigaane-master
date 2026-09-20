export const CHANDAS_PROSODY_MAP = [
  {
    id: "laghuSyllable",
    label: "laghu syllable",
    trigger: "short-open-syllable",
    description: "Short open syllable counted as laghu by deterministic inspection.",
    confidence: "deterministic",
    color: "#38bdf8",
  },
  {
    id: "guruSyllable",
    label: "guru syllable",
    trigger: "heavy-syllable",
    description: "Heavy syllable counted as guru by deterministic inspection.",
    confidence: "deterministic",
    color: "#f97316",
  },
  {
    id: "longVowelGuru",
    label: "long vowel guru",
    trigger: "long-vowel",
    description: "Long vowel syllable marked guru.",
    confidence: "deterministic",
    color: "#f59e0b",
  },
  {
    id: "closedSyllableGuru",
    label: "closed syllable guru",
    trigger: "consonant-cluster",
    description: "Short vowel followed by consonant cluster marked guru.",
    confidence: "deterministic",
    color: "#fb7185",
  },
  {
    id: "anusvaraGuru",
    label: "anusvāra guru",
    trigger: "anusvara-after-vowel",
    description: "Anusvāra after vowel marks syllable guru.",
    confidence: "deterministic",
    color: "#a855f7",
  },
  {
    id: "visargaGuru",
    label: "visarga guru",
    trigger: "visarga-after-vowel",
    description: "Visarga after vowel marks syllable guru.",
    confidence: "deterministic",
    color: "#ec4899",
  },
  {
    id: "matraCount",
    label: "mātrā count",
    trigger: "laghu-guru-weight",
    description: "Laghu counts one mātrā and guru counts two mātrā.",
    confidence: "deterministic",
    color: "#22c55e",
  },
  {
    id: "ganaGrouping",
    label: "gaṇa grouping",
    trigger: "three-syllable-group",
    description: "Complete triples are mapped to deterministic gaṇa names.",
    confidence: "deterministic",
    color: "#14b8a6",
  },
  {
    id: "padaBoundaryCandidate",
    label: "pāda boundary candidate",
    trigger: "eight-syllable-window",
    description: "Eight-syllable windows are shown as structural pāda candidates.",
    confidence: "deterministic",
    color: "#60a5fa",
  },
    {
    id: "caesuraCandidate",
    label: "caesura candidate",
    trigger: "deterministic-pada-midpoint",
    description: "Candidate pause point derived from explicit pāda midpoint inspection.",
    confidence: "deterministic-candidate",
    color: "#c084fc",
  },
  {
    id: "padaRhythmCandidate",
    label: "pāda rhythm candidate",
    trigger: "pada-laghu-guru-sequence",
    description: "Deterministic laghu/guru rhythm signature for each pāda candidate.",
    confidence: "deterministic-candidate",
    color: "#2dd4bf",
  },
    {
    id: "chandasStructuralNode",
    label: "chandas structural node",
    trigger: "overlay-structural-projection",
    description: "Deterministic graph node projected from explicit chandas overlay components.",
    confidence: "deterministic",
    color: "#818cf8",
  },
  {
    id: "chandasStructuralEdge",
    label: "chandas structural edge",
    trigger: "overlay-structural-dependency",
    description: "Deterministic structural dependency edge between explicit chandas overlay components.",
    confidence: "deterministic",
    color: "#a78bfa",
  },
    {
    id: "recitationFlowCandidate",
    label: "recitation flow candidate",
    trigger: "pada-sequence-transition",
    description: "Deterministic transition candidate between explicit pāda rhythm segments.",
    confidence: "deterministic-candidate",
    color: "#fb923c",
  },
  {
    id: "breathWindowCandidate",
    label: "breath window candidate",
    trigger: "pada-boundary-pause-window",
    description: "Candidate breath window derived from explicit pāda boundary inspection.",
    confidence: "deterministic-candidate",
    color: "#67e8f9",
  },
    {
    id: "recitationTimingCandidate",
    label: "recitation timing candidate",
    trigger: "matra-duration-projection",
    description: "Deterministic timing projection derived only from explicit laghu/guru mātrā counts.",
    confidence: "deterministic-candidate",
    color: "#facc15",
  },
  {
    id: "padaTimingSummary",
    label: "pāda timing summary",
    trigger: "pada-matra-duration-summary",
    description: "Deterministic pāda duration summary derived from explicit syllable mātrā counts.",
    confidence: "deterministic-candidate",
    color: "#4ade80",
  },
  {
    id: "metreCandidate",
    label: "metre candidate",
    trigger: "explicit-pattern-match",
    description: "Metre candidates require explicit deterministic pattern matches.",
    confidence: "deterministic",
    color: "#eab308",
  },
  {
    id: "unresolvedProsodyCandidate",
    label: "unresolved prosody candidate",
    trigger: "incomplete-trailing-syllables",
    description: "Incomplete trailing syllable groups are retained without forced scansion.",
    confidence: "deterministic",
    color: "#94a3b8",
  },
];

export const CHANDAS_GANA_MAP = {
  "laghu-guru-guru": "ya",
  "guru-guru-guru": "ma",
  "guru-guru-laghu": "ta",
  "guru-laghu-guru": "ra",
  "laghu-guru-laghu": "ja",
  "guru-laghu-laghu": "bha",
  "laghu-laghu-laghu": "na",
  "laghu-laghu-guru": "sa",
};

export const CHANDAS_METRE_REGISTRY = [
  {
    id: "gayatri",
    label: "Gāyatrī",
    padaCount: 3,
    syllablesPerPada: 8,
    totalSyllables: 24,
    matraPattern: null,
    confidence: "deterministic-candidate",
    notes: "Candidate only; no authoritative scansion claim.",
  },
  {
    id: "anustubh",
    label: "Anuṣṭubh",
    padaCount: 4,
    syllablesPerPada: 8,
    totalSyllables: 32,
    matraPattern: null,
    confidence: "deterministic-candidate",
    notes: "Candidate only; no authoritative scansion claim.",
  },
  {
    id: "tristubh",
    label: "Triṣṭubh",
    padaCount: 4,
    syllablesPerPada: 11,
    totalSyllables: 44,
    matraPattern: null,
    confidence: "deterministic-candidate",
    notes: "Candidate only; no authoritative scansion claim.",
  },
  {
    id: "jagati",
    label: "Jagatī",
    padaCount: 4,
    syllablesPerPada: 12,
    totalSyllables: 48,
    matraPattern: null,
    confidence: "deterministic-candidate",
    notes: "Candidate only; no authoritative scansion claim.",
  },
  {
    id: "usnih",
    label: "Uṣṇih",
    padaCount: 3,
    syllablesPerPada: null,
    totalSyllables: 28,
    matraPattern: null,
    confidence: "deterministic-candidate",
    notes: "Candidate only; no authoritative scansion claim.",
  },
  {
    id: "pankti",
    label: "Paṅkti",
    padaCount: 5,
    syllablesPerPada: 8,
    totalSyllables: 40,
    matraPattern: null,
    confidence: "deterministic-candidate",
    notes: "Candidate only; no authoritative scansion claim.",
  },
  {
    id: "brhati",
    label: "Bṛhatī",
    padaCount: 4,
    syllablesPerPada: null,
    totalSyllables: 36,
    matraPattern: null,
    confidence: "deterministic-candidate",
    notes: "Candidate only; no authoritative scansion claim.",
  },
];

export function normalizeMetreId(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[\s_]+/g, "-");
}

export function getChandasMetre(id) {
  const normalized = normalizeMetreId(id);
  return (
    CHANDAS_METRE_REGISTRY.find(
      (metre) => normalizeMetreId(metre.id) === normalized,
    ) || null
  );
}

export function listChandasMetres() {
  return CHANDAS_METRE_REGISTRY.map((metre) => ({ ...metre }));
}

export function matchMetreBySyllableCount(syllableCount) {
  const count = Number(syllableCount || 0);

  return CHANDAS_METRE_REGISTRY
    .filter((metre) => metre.totalSyllables === count)
    .map((metre) => ({ ...metre }));
}

export function groupMetresByPadaCount() {
  return CHANDAS_METRE_REGISTRY.reduce((groups, metre) => {
    const key = String(metre.padaCount || "unknown");

    if (!groups[key]) {
      groups[key] = [];
    }

    groups[key].push({ ...metre });

    return groups;
  }, {});
}

export function normalizeChandasRelation(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[\s_]+/g, "-");
}

export function getChandasRelation(id) {
  const normalized = normalizeChandasRelation(id);
  return CHANDAS_PROSODY_MAP.find((relation) => normalizeChandasRelation(relation.id) === normalized) || null;
}

export function listChandasRelations() {
  return CHANDAS_PROSODY_MAP.map((relation) => ({ ...relation }));
}
