const VIBHAKTIS = ["prathama", "dvitiya", "trtiya", "caturthi", "pancami", "sasthi", "saptami"];
const VACANAS = ["eka", "dvi", "bahu"];

const LINGA_COLORS = {
  masculine: "#38bdf8",
  neuter: "#22c55e",
  feminine: "#f472b6",
};

const VACANA_ALIASES = {
  एक: "eka",
  द्वि: "dvi",
  बहु: "bahu",
  singular: "eka",
  dual: "dvi",
  plural: "bahu",
};

const LINGA_ALIASES = {
  pum: "masculine",
  pullinga: "masculine",
  "puṃ": "masculine",
  "puṃlinga": "masculine",
  napumsaka: "neuter",
  napuṃsaka: "neuter",
  stri: "feminine",
  strī: "feminine",
  strilinga: "feminine",
  strīlinga: "feminine",
};

const STEM_CLASS_ALIASES = {
  a: "a-stem",
  akārānta: "a-stem",
  "a-stem-masculine": "a-stem",
  "a-stem-neuter": "a-stem",
  ā: "ā-stem",
  "aa-stem": "ā-stem",
  ākārānta: "ā-stem",
  "ā-stem-feminine": "ā-stem",
};

const TABLES = [
  {
    stemClass: "a-stem",
    linga: "masculine",
    baseStrategy: "identity",
    suffixes: {
      prathama: { eka: "ः", dvi: "ौ", bahu: "ाः" },
      dvitiya: { eka: "म्", dvi: "ौ", bahu: "ान्" },
      trtiya: { eka: "ेण", dvi: "ाभ्याम्", bahu: "ैः" },
      caturthi: { eka: "ाय", dvi: "ाभ्याम्", bahu: "ेभ्यः" },
      pancami: { eka: "ात्", dvi: "ाभ्याम्", bahu: "ेभ्यः" },
      sasthi: { eka: "स्य", dvi: "योः", bahu: "ानाम्" },
      saptami: { eka: "े", dvi: "योः", bahu: "ेषु" },
    },
  },
  {
    stemClass: "a-stem",
    linga: "neuter",
    baseStrategy: "identity",
    suffixes: {
      prathama: { eka: "म्", dvi: "े", bahu: "ानि" },
      dvitiya: { eka: "म्", dvi: "े", bahu: "ानि" },
      trtiya: { eka: "ेण", dvi: "ाभ्याम्", bahu: "ैः" },
      caturthi: { eka: "ाय", dvi: "ाभ्याम्", bahu: "ेभ्यः" },
      pancami: { eka: "ात्", dvi: "ाभ्याम्", bahu: "ेभ्यः" },
      sasthi: { eka: "स्य", dvi: "योः", bahu: "ानाम्" },
      saptami: { eka: "े", dvi: "योः", bahu: "ेषु" },
    },
  },
  {
    stemClass: "ā-stem",
    linga: "feminine",
    baseStrategy: "drop-final-aa",
    suffixes: {
      prathama: { eka: "ा", dvi: "े", bahu: "ाः" },
      dvitiya: { eka: "ाम्", dvi: "े", bahu: "ाः" },
      trtiya: { eka: "या", dvi: "ाभ्याम्", bahu: "ाभिः" },
      caturthi: { eka: "यै", dvi: "ाभ्याम्", bahu: "ाभ्यः" },
      pancami: { eka: "याः", dvi: "ाभ्याम्", bahu: "ाभ्यः" },
      sasthi: { eka: "याः", dvi: "योः", bahu: "ानाम्" },
      saptami: { eka: "याम्", dvi: "योः", bahu: "ासु" },
    },
  },
];

function buildRules() {
  return TABLES.flatMap((table) => (
    VIBHAKTIS.flatMap((vibhakti) => (
      VACANAS.map((vacana) => ({
        id: `subanta.${table.linga}.${table.stemClass.replace(/[^\p{Letter}\p{Number}]+/gu, "_")}.${vibhakti}.${vacana}`,
        stemClass: table.stemClass,
        linga: table.linga,
        vibhakti,
        vacana,
        suffix: table.suffixes[vibhakti][vacana],
        resultingPattern: table.baseStrategy === "drop-final-aa" ? "drop final ā/ा, then append suffix" : "append suffix to stem",
        baseStrategy: table.baseStrategy,
        reversible: true,
        notes: "Deterministic subanta suffix attachment preview; non-authoritative morphology execution metadata.",
        confidence: "deterministic",
        color: LINGA_COLORS[table.linga],
      }))
    ))
  ));
}

export const SUBANTA_RULE_MAP = buildRules();

export const SUBANTA_SAMPLE_PARADIGMS = [
  {
    stem: "राम",
    iast: "rāma",
    stemClass: "a-stem",
    linga: "masculine",
    notes: "Deterministic sample paradigm for a-stem masculine preview.",
  },
  {
    stem: "फल",
    iast: "phala",
    stemClass: "a-stem",
    linga: "neuter",
    notes: "Deterministic sample paradigm for a-stem neuter preview.",
  },
  {
    stem: "सीता",
    iast: "sītā",
    stemClass: "ā-stem",
    linga: "feminine",
    notes: "Deterministic sample paradigm for ā-stem feminine preview.",
  },
];

export function normalizeSubantaInput(value) {
  return String(value ?? "")
    .normalize("NFC")
    .trim()
    .replace(/\s+/g, " ");
}

function normalizeKey(value) {
  return normalizeSubantaInput(value).toLowerCase();
}

export function normalizeVacana(value) {
  const key = normalizeKey(value);
  return VACANA_ALIASES[key] || key;
}

export function normalizeLinga(value) {
  const key = normalizeKey(value);
  return LINGA_ALIASES[key] || key;
}

export function normalizeStemClass(value) {
  const key = normalizeKey(value);
  return STEM_CLASS_ALIASES[key] || key;
}

export function listSubantaRules() {
  return [...SUBANTA_RULE_MAP].sort((left, right) => left.id.localeCompare(right.id));
}

export function matchSubantaRule(input = {}) {
  const stemClass = normalizeStemClass(input.stemClass);
  const linga = normalizeLinga(input.linga);
  const vibhakti = normalizeKey(input.vibhakti);
  const vacana = normalizeVacana(input.vacana);
  return listSubantaRules().find((rule) => (
    rule.stemClass === stemClass
    && rule.linga === linga
    && rule.vibhakti === vibhakti
    && rule.vacana === vacana
  )) || null;
}

export function groupSubantaRulesByLinga() {
  return listSubantaRules().reduce((groups, rule) => {
    if (!groups[rule.linga]) groups[rule.linga] = [];
    groups[rule.linga].push({ ...rule });
    return groups;
  }, {});
}
