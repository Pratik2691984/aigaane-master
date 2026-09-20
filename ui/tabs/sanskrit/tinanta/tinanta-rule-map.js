const ROOTS = [
  {
    dhatu: "bhū",
    rootDevanagari: "भू",
    presentStem: "bhava",
    forms: {
      prathama: { eka: ["ti", "bhavati"], dvi: ["taḥ", "bhavataḥ"], bahu: ["nti", "bhavanti"] },
      madhyama: { eka: ["si", "bhavasi"], dvi: ["thaḥ", "bhavathaḥ"], bahu: ["tha", "bhavatha"] },
      uttama: { eka: ["āmi", "bhavāmi"], dvi: ["āvaḥ", "bhavāvaḥ"], bahu: ["āmaḥ", "bhavāmaḥ"] },
    },
  },
  {
    dhatu: "gam",
    rootDevanagari: "गम्",
    presentStem: "gaccha",
    forms: {
      prathama: { eka: ["ti", "gacchati"], dvi: ["taḥ", "gacchataḥ"], bahu: ["nti", "gacchanti"] },
      madhyama: { eka: ["si", "gacchasi"], dvi: ["thaḥ", "gacchathaḥ"], bahu: ["tha", "gacchatha"] },
      uttama: { eka: ["āmi", "gacchāmi"], dvi: ["āvaḥ", "gacchāvaḥ"], bahu: ["āmaḥ", "gacchāmaḥ"] },
    },
  },
  {
    dhatu: "nī",
    rootDevanagari: "नी",
    presentStem: "naya",
    forms: {
      prathama: { eka: ["ti", "nayati"], dvi: ["taḥ", "nayataḥ"], bahu: ["nti", "nayanti"] },
      madhyama: { eka: ["si", "nayasi"], dvi: ["thaḥ", "nayathaḥ"], bahu: ["tha", "nayatha"] },
      uttama: { eka: ["āmi", "nayāmi"], dvi: ["āvaḥ", "nayāvaḥ"], bahu: ["āmaḥ", "nayāmaḥ"] },
    },
  },
];

const ROOT_ALIASES = {
  bhu: "bhū",
  "bhū": "bhū",
  "भू": "bhū",
  gam: "gam",
  "गम्": "gam",
  "गम": "gam",
  ni: "nī",
  "nī": "nī",
  "नी": "nī",
};

const LAKARA_ALIASES = {
  lat: "laṭ",
  "laṭ": "laṭ",
  "लट्": "laṭ",
};

const PADA_ALIASES = {
  parasmaipada: "parasmaipada",
  parasmai: "parasmaipada",
  "परस्मैपद": "parasmaipada",
};

const PURUSHA_ALIASES = {
  prathama: "prathama",
  third: "prathama",
  madhyama: "madhyama",
  second: "madhyama",
  uttama: "uttama",
  first: "uttama",
};

const VACANA_ALIASES = {
  eka: "eka",
  singular: "eka",
  dvi: "dvi",
  dual: "dvi",
  bahu: "bahu",
  "बहु": "bahu",
  plural: "bahu",
};

function buildRules() {
  return ROOTS.flatMap((root) => (
    Object.entries(root.forms).flatMap(([purusha, vacanas]) => (
      Object.entries(vacanas).map(([vacana, [affix, generatedForm]]) => ({
        id: `tinanta.${root.dhatu}.lat.parasmaipada.${purusha}.${vacana}`,
        dhatu: root.dhatu,
        rootDevanagari: root.rootDevanagari,
        lakara: "laṭ",
        pada: "parasmaipada",
        purusha,
        vacana,
        presentStem: root.presentStem,
        affix,
        generatedForm,
        operations: [
          "deterministic-root-lookup",
          "present-stem-selection",
          "parasmaipada-affix-selection",
          "direct-form-emission",
        ],
        reversible: true,
        notes: "Direct deterministic laṭ/parasmaipada tiṅanta generation metadata; non-authoritative preview.",
        confidence: "deterministic",
      }))
    ))
  ));
}

export const TINANTA_RULE_MAP = buildRules();

export const TINANTA_REVERSE_MAP = TINANTA_RULE_MAP.reduce((map, rule) => {
  map[rule.generatedForm] = { ...rule };
  return map;
}, {});

export function normalizeTinantaInput(value) {
  return String(value ?? "")
    .normalize("NFC")
    .trim()
    .replace(/\s+/g, " ");
}

function normalizeKey(value) {
  return normalizeTinantaInput(value).toLowerCase();
}

function normalizeDhatu(value) {
  const normalized = normalizeTinantaInput(value);
  return ROOT_ALIASES[normalized] || ROOT_ALIASES[normalized.toLowerCase()] || normalized.toLowerCase();
}

function normalizeLakara(value) {
  const key = normalizeKey(value);
  return LAKARA_ALIASES[key] || key;
}

function normalizePada(value) {
  const key = normalizeKey(value);
  return PADA_ALIASES[key] || key;
}

function normalizePurusha(value) {
  const key = normalizeKey(value);
  return PURUSHA_ALIASES[key] || key;
}

function normalizeVacana(value) {
  const key = normalizeKey(value);
  return VACANA_ALIASES[key] || key;
}

export function buildTinantaKey(input = {}) {
  return [
    normalizeDhatu(input.dhatu),
    normalizeLakara(input.lakara),
    normalizePada(input.pada),
    normalizePurusha(input.purusha),
    normalizeVacana(input.vacana),
  ].join("|");
}

export function matchTinantaRule(input = {}) {
  const key = buildTinantaKey(input);
  return TINANTA_RULE_MAP.find((rule) => (
    `${rule.dhatu}|${rule.lakara}|${rule.pada}|${rule.purusha}|${rule.vacana}` === key
  )) || null;
}

export function reverseLookupTinanta(form) {
  return TINANTA_REVERSE_MAP[normalizeTinantaInput(form)] || null;
}

export function listTinantaRules() {
  return [...TINANTA_RULE_MAP].sort((left, right) => left.id.localeCompare(right.id));
}

export function listTinantaRoots() {
  return ROOTS.map((root) => ({
    dhatu: root.dhatu,
    rootDevanagari: root.rootDevanagari,
    lakara: "laṭ",
    pada: "parasmaipada",
    presentStem: root.presentStem,
  }));
}
