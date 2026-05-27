export const KARAKA_RELATION_MAP = [
  {
    id: "karta",
    label: "kartā",
    triggerVibhaktis: ["prathama"],
    semanticHints: ["agent", "doer", "subject-role"],
    color: "#38bdf8",
    description: "Deterministic overlay hint for prathama-linked kartā relation inspection.",
  },
  {
    id: "karma",
    label: "karma",
    triggerVibhaktis: ["dvitiya"],
    semanticHints: ["object", "patient", "goal"],
    color: "#f97316",
    description: "Deterministic overlay hint for dvitīyā-linked karma relation inspection.",
  },
  {
    id: "karana",
    label: "karaṇa",
    triggerVibhaktis: ["trtiya"],
    semanticHints: ["instrument", "means"],
    color: "#22c55e",
    description: "Deterministic overlay hint for tṛtīyā-linked karaṇa relation inspection.",
  },
  {
    id: "sampradana",
    label: "sampradāna",
    triggerVibhaktis: ["caturthi"],
    semanticHints: ["recipient", "beneficiary"],
    color: "#a855f7",
    description: "Deterministic overlay hint for caturthī-linked sampradāna relation inspection.",
  },
  {
    id: "apadana",
    label: "apādāna",
    triggerVibhaktis: ["pancami"],
    semanticHints: ["source", "separation"],
    color: "#f43f5e",
    description: "Deterministic overlay hint for pañcamī-linked apādāna relation inspection.",
  },
  {
    id: "adhikarana",
    label: "adhikaraṇa",
    triggerVibhaktis: ["saptami"],
    semanticHints: ["location", "locus"],
    color: "#14b8a6",
    description: "Deterministic overlay hint for saptamī-linked adhikaraṇa relation inspection.",
  },
];

const VIBHAKTI_ALIASES = {
  prathama: "prathama",
  "prathamā": "prathama",
  nominative: "prathama",
  dvitiya: "dvitiya",
  "dvitīyā": "dvitiya",
  accusative: "dvitiya",
  trtiya: "trtiya",
  tritiya: "trtiya",
  "tṛtīyā": "trtiya",
  instrumental: "trtiya",
  caturthi: "caturthi",
  "caturthī": "caturthi",
  dative: "caturthi",
  pancami: "pancami",
  panchami: "pancami",
  "pañcamī": "pancami",
  ablative: "pancami",
  saptami: "saptami",
  "saptamī": "saptami",
  locative: "saptami",
};

export function normalizeVibhakti(value) {
  const normalized = String(value ?? "").trim().toLowerCase();
  return VIBHAKTI_ALIASES[normalized] || normalized;
}

export function getKarakaByVibhakti(vibhakti) {
  const normalized = normalizeVibhakti(vibhakti);
  return KARAKA_RELATION_MAP.find((relation) => relation.triggerVibhaktis.includes(normalized)) || null;
}

export function listKarakaRelations() {
  return KARAKA_RELATION_MAP.map((relation) => ({
    ...relation,
    triggerVibhaktis: [...relation.triggerVibhaktis],
    semanticHints: [...relation.semanticHints],
  }));
}
