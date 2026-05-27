export const SANDHI_RULE_SAFETY_NOTE =
  "Sandhi transition rules are deterministic structural inspection metadata only; no authoritative grammatical correctness claim is made.";

export const SANDHI_TRANSITION_RULES = [
  {
    id: "vowel_a_a",
    category: "vowel",
    left: "अ",
    right: "अ",
    result: "आ",
    label: "अ + अ -> आ",
    safetyNote: SANDHI_RULE_SAFETY_NOTE,
  },
  {
    id: "vowel_a_i",
    category: "vowel",
    left: "अ",
    right: "इ",
    result: "ए",
    label: "अ + इ -> ए",
    safetyNote: SANDHI_RULE_SAFETY_NOTE,
  },
  {
    id: "vowel_a_u",
    category: "vowel",
    left: "अ",
    right: "उ",
    result: "ओ",
    label: "अ + उ -> ओ",
    safetyNote: SANDHI_RULE_SAFETY_NOTE,
  },
  {
    id: "visarga_sibilant",
    category: "visarga",
    left: "ः",
    right: "स",
    result: "स्स",
    label: "ः + स -> स्स",
    safetyNote: SANDHI_RULE_SAFETY_NOTE,
  },
  {
    id: "nasal_guttural",
    category: "nasal",
    left: "न्",
    right: "क",
    result: "ङ्क",
    label: "न् + क -> ङ्क",
    safetyNote: SANDHI_RULE_SAFETY_NOTE,
  },
];
