function rule({
  id,
  category,
  label,
  inputPattern,
  outputPattern,
  priority,
  stage,
  reversible = true,
  sourceLayer,
  notes,
}) {
  return {
    id,
    category,
    label,
    inputPattern,
    outputPattern,
    priority,
    stage,
    reversible,
    sourceLayer,
    notes,
    confidence: "deterministic",
  };
}

export const RULEFIRE_RULE_MAP = [
  rule({
    id: "sandhi_a_i_to_e",
    category: "sandhi",
    label: "a + i -> e",
    inputPattern: { kind: "sandhi", boundary: "a+i", left: "a", right: "i" },
    outputPattern: { boundary: "e", textReplacement: ["a i", "e"] },
    priority: 10,
    stage: "sandhiExecution",
    sourceLayer: "sandhi-execution",
    notes: "Deterministic visible boundary rule for a+i.",
  }),
  rule({
    id: "sandhi_a_u_to_o",
    category: "sandhi",
    label: "a + u -> o",
    inputPattern: { kind: "sandhi", boundary: "a+u", left: "a", right: "u" },
    outputPattern: { boundary: "o", textReplacement: ["a u", "o"] },
    priority: 11,
    stage: "sandhiExecution",
    sourceLayer: "sandhi-execution",
    notes: "Deterministic visible boundary rule for a+u.",
  }),
  rule({
    id: "sandhi_a_a_to_aa",
    category: "sandhi",
    label: "a + a -> aa",
    inputPattern: { kind: "sandhi", boundary: "a+a", left: "a", right: "a" },
    outputPattern: { boundary: "aa", textReplacement: ["a a", "aa"] },
    priority: 12,
    stage: "sandhiExecution",
    sourceLayer: "sandhi-execution",
    notes: "Deterministic visible boundary rule for a+a.",
  }),
  rule({
    id: "sandhi_t_t_to_tt",
    category: "sandhi",
    label: "t + t -> tt",
    inputPattern: { kind: "sandhi", boundary: "t+t", left: "t", right: "t" },
    outputPattern: { boundary: "tt", textReplacement: ["t t", "tt"] },
    priority: 13,
    stage: "sandhiExecution",
    sourceLayer: "sandhi-execution",
    notes: "Deterministic visible boundary rule for t+t.",
  }),
  rule({
    id: "subanta_a_masculine_prathama_eka",
    category: "subanta",
    label: "a-stem masculine prathama eka",
    inputPattern: { kind: "subanta", stemClass: "a-stem", linga: "masculine", vibhakti: "prathama", vacana: "eka" },
    outputPattern: { suffix: "ah", formRole: "nominal-pada" },
    priority: 20,
    stage: "subantaGeneration",
    sourceLayer: "subanta-generator",
    notes: "Deterministic lookup-backed subanta rule metadata.",
  }),
  rule({
    id: "subanta_a_masculine_dvitiya_eka",
    category: "subanta",
    label: "a-stem masculine dvitiya eka",
    inputPattern: { kind: "subanta", stemClass: "a-stem", linga: "masculine", vibhakti: "dvitiya", vacana: "eka" },
    outputPattern: { suffix: "am", formRole: "nominal-pada" },
    priority: 21,
    stage: "subantaGeneration",
    sourceLayer: "subanta-generator",
    notes: "Deterministic lookup-backed subanta rule metadata.",
  }),
  rule({
    id: "subanta_a_neuter_prathama_eka",
    category: "subanta",
    label: "a-stem neuter prathama eka",
    inputPattern: { kind: "subanta", stemClass: "a-stem", linga: "neuter", vibhakti: "prathama", vacana: "eka" },
    outputPattern: { suffix: "am", formRole: "nominal-pada" },
    priority: 22,
    stage: "subantaGeneration",
    sourceLayer: "subanta-generator",
    notes: "Deterministic lookup-backed subanta rule metadata.",
  }),
  rule({
    id: "subanta_aa_feminine_prathama_eka",
    category: "subanta",
    label: "aa-stem feminine prathama eka",
    inputPattern: { kind: "subanta", stemClass: "aa-stem", linga: "feminine", vibhakti: "prathama", vacana: "eka" },
    outputPattern: { suffix: "aa", formRole: "nominal-pada" },
    priority: 23,
    stage: "subantaGeneration",
    sourceLayer: "subanta-generator",
    notes: "Deterministic lookup-backed subanta rule metadata.",
  }),
  rule({
    id: "tinanta_bhu_lat_prathama_eka",
    category: "tinanta",
    label: "bhu lat prathama eka",
    inputPattern: { kind: "tinanta", dhatu: "bhu", lakara: "lat", purusha: "prathama", vacana: "eka" },
    outputPattern: { generatedForm: "bhavati", formRole: "verbal-pada" },
    priority: 30,
    stage: "tinantaGeneration",
    sourceLayer: "tinanta-generator",
    notes: "Deterministic lookup-backed tinanta rule metadata.",
  }),
  rule({
    id: "tinanta_gam_lat_prathama_eka",
    category: "tinanta",
    label: "gam lat prathama eka",
    inputPattern: { kind: "tinanta", dhatu: "gam", lakara: "lat", purusha: "prathama", vacana: "eka" },
    outputPattern: { generatedForm: "gacchati", formRole: "verbal-pada" },
    priority: 31,
    stage: "tinantaGeneration",
    sourceLayer: "tinanta-generator",
    notes: "Deterministic lookup-backed tinanta rule metadata.",
  }),
  rule({
    id: "tinanta_ni_lat_prathama_eka",
    category: "tinanta",
    label: "ni lat prathama eka",
    inputPattern: { kind: "tinanta", dhatu: "ni", lakara: "lat", purusha: "prathama", vacana: "eka" },
    outputPattern: { generatedForm: "nayati", formRole: "verbal-pada" },
    priority: 32,
    stage: "tinantaGeneration",
    sourceLayer: "tinanta-generator",
    notes: "Deterministic lookup-backed tinanta rule metadata.",
  }),
  rule({
    id: "prakriya_generate_subanta_pada",
    category: "prakriya",
    label: "Generate subanta pada",
    inputPattern: { kind: "prakriya", sourceType: "subanta", stage: "subantaGeneration" },
    outputPattern: { operation: "generate-subanta-pada" },
    priority: 40,
    stage: "subantaGeneration",
    sourceLayer: "prakriya-composition",
    notes: "Records explicit subanta pada generation in the structural prakriya pipeline.",
  }),
  rule({
    id: "prakriya_generate_tinanta_pada",
    category: "prakriya",
    label: "Generate tinanta pada",
    inputPattern: { kind: "prakriya", sourceType: "tinanta", stage: "tinantaGeneration" },
    outputPattern: { operation: "generate-tinanta-pada" },
    priority: 41,
    stage: "tinantaGeneration",
    sourceLayer: "prakriya-composition",
    notes: "Records explicit tinanta pada generation in the structural prakriya pipeline.",
  }),
  rule({
    id: "prakriya_assemble_padas",
    category: "prakriya",
    label: "Assemble padas",
    inputPattern: { kind: "prakriya", stage: "padaAssembly", requiresPadas: true },
    outputPattern: { operation: "assemble-padas" },
    priority: 42,
    stage: "padaAssembly",
    sourceLayer: "prakriya-composition",
    notes: "Records deterministic ordered pada assembly.",
  }),
  rule({
    id: "prakriya_apply_sandhi",
    category: "prakriya",
    label: "Apply sandhi",
    inputPattern: { kind: "prakriya", stage: "sandhiExecution" },
    outputPattern: { operation: "apply-sandhi" },
    priority: 43,
    stage: "sandhiExecution",
    sourceLayer: "prakriya-composition",
    notes: "Records deterministic sandhi execution inside prakriya composition.",
  }),
  rule({
    id: "prakriya_emit_sentence",
    category: "prakriya",
    label: "Emit sentence",
    inputPattern: { kind: "prakriya", stage: "sentenceComposition" },
    outputPattern: { operation: "emit-sentence" },
    priority: 44,
    stage: "sentenceComposition",
    sourceLayer: "prakriya-composition",
    notes: "Records final structural sentence emission.",
  }),
];

export function normalizeRulefireId(value) {
  return String(value ?? "")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "");
}

export function getRulefireRule(id) {
  const normalized = normalizeRulefireId(id);
  return RULEFIRE_RULE_MAP.find((ruleItem) => normalizeRulefireId(ruleItem.id) === normalized) || null;
}

export function listRulefireRules() {
  return RULEFIRE_RULE_MAP.map((ruleItem) => ({ ...ruleItem }));
}

export function groupRulefireRulesByCategory() {
  return listRulefireRules().reduce((groups, ruleItem) => {
    const category = ruleItem.category || "uncategorized";
    groups[category] = groups[category] || [];
    groups[category].push(ruleItem);
    return groups;
  }, {});
}

export function sortRulefireRulesByPriority(rules) {
  return [...(Array.isArray(rules) ? rules : [])].sort((left, right) => (
    (left.priority || 0) - (right.priority || 0)
    || normalizeRulefireId(left.id).localeCompare(normalizeRulefireId(right.id))
  ));
}

