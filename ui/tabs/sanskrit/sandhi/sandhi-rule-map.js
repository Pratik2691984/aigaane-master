export const SANDHI_RULE_MAP = [
  {
    id: "vowel.a_a.dirgha",
    category: "vowel",
    left: "a",
    right: "a",
    result: "ā",
    sutraReference: "placeholder-vowel-a-a",
    priority: 100,
    reversible: true,
    notes: "Deterministic vowel sandhi preview: a + a -> ā. Non-authoritative structural rule.",
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "vowel.a_i.guna",
    category: "vowel",
    left: "a",
    right: "i",
    result: "e",
    sutraReference: "placeholder-vowel-a-i",
    priority: 96,
    reversible: true,
    notes: "Deterministic vowel sandhi preview: a + i -> e. Non-authoritative structural rule.",
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "vowel.a_ii.guna",
    category: "vowel",
    left: "a",
    right: "ī",
    result: "e",
    sutraReference: "placeholder-vowel-a-ii",
    priority: 95,
    reversible: true,
    notes: "Deterministic vowel sandhi preview: a + ī -> e. Non-authoritative structural rule.",
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "vowel.a_u.guna",
    category: "vowel",
    left: "a",
    right: "u",
    result: "o",
    sutraReference: "placeholder-vowel-a-u",
    priority: 94,
    reversible: true,
    notes: "Deterministic vowel sandhi preview: a + u -> o. Non-authoritative structural rule.",
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "vowel.a_uu.guna",
    category: "vowel",
    left: "a",
    right: "ū",
    result: "o",
    sutraReference: "placeholder-vowel-a-uu",
    priority: 93,
    reversible: true,
    notes: "Deterministic vowel sandhi preview: a + ū -> o. Non-authoritative structural rule.",
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "vowel.a_r.vrddhi-safe",
    category: "vowel",
    left: "a",
    right: "ṛ",
    result: "ar",
    sutraReference: "placeholder-vowel-a-r",
    priority: 92,
    reversible: true,
    notes: "Deterministic placeholder-safe vowel sandhi preview: a + ṛ -> ar.",
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "vowel.a_e.vrddhi",
    category: "vowel",
    left: "a",
    right: "e",
    result: "ai",
    sutraReference: "placeholder-vowel-a-e",
    priority: 91,
    reversible: true,
    notes: "Deterministic vowel sandhi preview: a + e -> ai. Non-authoritative structural rule.",
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "vowel.a_o.vrddhi",
    category: "vowel",
    left: "a",
    right: "o",
    result: "au",
    sutraReference: "placeholder-vowel-a-o",
    priority: 90,
    reversible: true,
    notes: "Deterministic vowel sandhi preview: a + o -> au. Non-authoritative structural rule.",
    confidence: "deterministic",
    color: "#fbbf24",
  },
  {
    id: "visarga.ah_a.preview",
    category: "visarga",
    left: "aḥ",
    right: "a",
    result: "o 'a",
    sutraReference: "placeholder-visarga-ah-a",
    priority: 80,
    reversible: true,
    notes: "Deterministic visarga preview: aḥ + a -> o 'a. Structural preview only.",
    confidence: "deterministic",
    color: "#fb923c",
  },
  {
    id: "visarga.ah_i.placeholder",
    category: "visarga",
    left: "aḥ",
    right: "i",
    result: "a r i",
    sutraReference: "placeholder-visarga-ah-i",
    priority: 79,
    reversible: true,
    notes: "Placeholder-safe deterministic visarga preview: aḥ + i -> a r i.",
    confidence: "deterministic",
    color: "#fb923c",
  },
  {
    id: "consonant.t_t.gemination",
    category: "consonant",
    left: "t",
    right: "t",
    result: "tt",
    sutraReference: "placeholder-consonant-t-t",
    priority: 70,
    reversible: true,
    notes: "Deterministic consonant sandhi preview: t + t -> tt.",
    confidence: "deterministic",
    color: "#38bdf8",
  },
  {
    id: "consonant.n_d.cluster",
    category: "consonant",
    left: "n",
    right: "d",
    result: "nd",
    sutraReference: "placeholder-consonant-n-d",
    priority: 69,
    reversible: true,
    notes: "Deterministic consonant sandhi preview: n + d -> nd.",
    confidence: "deterministic",
    color: "#38bdf8",
  },
  {
    id: "consonant.m_p.cluster",
    category: "consonant",
    left: "m",
    right: "p",
    result: "mp",
    sutraReference: "placeholder-consonant-m-p",
    priority: 68,
    reversible: true,
    notes: "Deterministic consonant sandhi preview: m + p -> mp.",
    confidence: "deterministic",
    color: "#38bdf8",
  },
];

export function normalizeSandhiInput(value) {
  return String(value ?? "")
    .normalize("NFC")
    .trim()
    .replace(/\s+/g, " ");
}

export function listSandhiRules() {
  return [...SANDHI_RULE_MAP].sort((left, right) => {
    if (right.priority !== left.priority) return right.priority - left.priority;
    return left.id.localeCompare(right.id);
  });
}

export function matchSandhiRule(left, right) {
  const normalizedLeft = normalizeSandhiInput(left);
  const normalizedRight = normalizeSandhiInput(right);
  return listSandhiRules().find((rule) => rule.left === normalizedLeft && rule.right === normalizedRight) || null;
}

export function groupSandhiRulesByCategory() {
  return listSandhiRules().reduce((groups, rule) => {
    const category = rule.category || "uncategorized";
    if (!groups[category]) groups[category] = [];
    groups[category].push({ ...rule });
    return groups;
  }, {});
}
