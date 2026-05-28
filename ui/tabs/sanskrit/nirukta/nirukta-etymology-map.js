function entry({
  id,
  lemma,
  devanagari,
  category,
  lineageType,
  semanticFamily,
  gloss,
  linkedDhatuId = null,
  linkedPratipadikaId = null,
  linkedRulefireRules = [],
  linkedSutraDependencies = [],
  notes,
}) {
  return {
    id,
    lemma,
    devanagari,
    category,
    lineageType,
    semanticFamily,
    gloss,
    linkedDhatuId,
    linkedPratipadikaId,
    linkedRulefireRules,
    linkedSutraDependencies,
    notes,
    confidence: "deterministic-placeholder",
  };
}

export const NIRUKTA_ETYMOLOGY_MAP = [
  entry({
    id: "nirukta.dhatu.gam",
    lemma: "gam",
    devanagari: "gam",
    category: "dhatu",
    lineageType: "dhatu-lineage",
    semanticFamily: "motion",
    gloss: "motion / going / transition",
    linkedDhatuId: "gam",
    linkedRulefireRules: ["tinanta_gam_lat_prathama_eka"],
    linkedSutraDependencies: ["tinanta_lat_parasmaipada_selection"],
    notes: "Deterministic placeholder dhatu lineage for current tinanta runtime.",
  }),
  entry({
    id: "nirukta.dhatu.bhu",
    lemma: "bhu",
    devanagari: "bhū",
    category: "dhatu",
    lineageType: "dhatu-lineage",
    semanticFamily: "being",
    gloss: "being / becoming / existence",
    linkedDhatuId: "bhu",
    linkedRulefireRules: ["tinanta_bhu_lat_prathama_eka"],
    linkedSutraDependencies: ["tinanta_lat_parasmaipada_selection"],
    notes: "Deterministic placeholder dhatu lineage for current tinanta runtime.",
  }),
  entry({
    id: "nirukta.dhatu.ni",
    lemma: "ni",
    devanagari: "nī",
    category: "dhatu",
    lineageType: "dhatu-lineage",
    semanticFamily: "guidance",
    gloss: "leading / guidance / direction",
    linkedDhatuId: "ni",
    linkedRulefireRules: ["tinanta_ni_lat_prathama_eka"],
    linkedSutraDependencies: ["tinanta_lat_parasmaipada_selection"],
    notes: "Deterministic placeholder dhatu lineage for current tinanta runtime.",
  }),
  entry({
    id: "nirukta.pratipadika.rama",
    lemma: "rama",
    devanagari: "rāma",
    category: "pratipadika",
    lineageType: "pratipadika-lineage",
    semanticFamily: "nominal-family",
    gloss: "masculine a-stem nominal placeholder lineage",
    linkedPratipadikaId: "rama",
    linkedRulefireRules: ["subanta_a_masculine_prathama_eka", "subanta_a_masculine_dvitiya_eka"],
    linkedSutraDependencies: ["subanta_nominal_suffix_selection"],
    notes: "Deterministic placeholder pratipadika lineage for current subanta runtime.",
  }),
  entry({
    id: "nirukta.pratipadika.phala",
    lemma: "phala",
    devanagari: "phala",
    category: "pratipadika",
    lineageType: "pratipadika-lineage",
    semanticFamily: "nominal-family",
    gloss: "neuter a-stem nominal placeholder lineage",
    linkedPratipadikaId: "phala",
    linkedRulefireRules: ["subanta_a_neuter_prathama_eka"],
    linkedSutraDependencies: ["subanta_nominal_suffix_selection"],
    notes: "Deterministic placeholder pratipadika lineage for current subanta runtime.",
  }),
  entry({
    id: "nirukta.pratipadika.sita",
    lemma: "sita",
    devanagari: "sītā",
    category: "pratipadika",
    lineageType: "pratipadika-lineage",
    semanticFamily: "nominal-family",
    gloss: "feminine ā-stem nominal placeholder lineage",
    linkedPratipadikaId: "sita",
    linkedRulefireRules: ["subanta_aa_feminine_prathama_eka"],
    linkedSutraDependencies: ["subanta_nominal_suffix_selection"],
    notes: "Deterministic placeholder pratipadika lineage for current subanta runtime.",
  }),
  ...["pra", "pari", "sam", "vi", "aa"].map((lemma) => entry({
    id: `nirukta.upasarga.${lemma}`,
    lemma,
    devanagari: lemma === "aa" ? "ā" : lemma,
    category: "upasarga",
    lineageType: "upasarga-placeholder",
    semanticFamily: "upasarga-placeholder",
    gloss: `${lemma} upasarga placeholder`,
    notes: "Registered upasarga placeholder only; no historical or semantic derivation is asserted.",
  })),
];

export function normalizeNiruktaLemma(value) {
  return String(value ?? "")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/\u0101/g, "aa")
    .replace(/\u012b/g, "ii")
    .replace(/\u016b/g, "uu")
    .replace(/[ḥṃ]/gu, "")
    .replace(/[^\p{Letter}\p{Number}]+/gu, "")
    .replace(/aa$/, "a");
}

export function getNiruktaEntry(lemma) {
  const normalized = normalizeNiruktaLemma(lemma);
  return NIRUKTA_ETYMOLOGY_MAP.find((item) => normalizeNiruktaLemma(item.lemma) === normalized) || null;
}

export function listNiruktaEntries() {
  return NIRUKTA_ETYMOLOGY_MAP.map((item) => ({ ...item }));
}

export function groupNiruktaEntriesByCategory() {
  return listNiruktaEntries().reduce((groups, item) => {
    groups[item.category] = groups[item.category] || [];
    groups[item.category].push(item);
    return groups;
  }, {});
}

export function findNiruktaBySemanticFamily(family) {
  const normalized = normalizeNiruktaLemma(family);
  return listNiruktaEntries().filter((item) => normalizeNiruktaLemma(item.semanticFamily) === normalized);
}

