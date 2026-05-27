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
