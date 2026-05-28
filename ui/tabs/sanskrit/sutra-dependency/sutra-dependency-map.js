function dependency(id, ruleId, dependsOn, dependencyType, stage, sourceLayer, notes) {
  return {
    id,
    ruleId,
    dependsOn,
    dependencyType,
    stage,
    sourceLayer,
    notes,
    confidence: "deterministic",
  };
}

export const SUTRA_DEPENDENCY_MAP = [
  dependency("dep.sandhi_a_i_to_e.symbolic_ac", "sandhi_a_i_to_e", "symbolic_ac", "symbolic-class", "sandhiExecution", "sutra-reference", "Visible a+i sandhi depends on the placeholder ac symbolic class."),
  dependency("dep.sandhi_a_u_to_o.symbolic_ac", "sandhi_a_u_to_o", "symbolic_ac", "symbolic-class", "sandhiExecution", "sutra-reference", "Visible a+u sandhi depends on the placeholder ac symbolic class."),
  dependency("dep.sandhi_a_a_to_aa.symbolic_ac", "sandhi_a_a_to_aa", "symbolic_ac", "symbolic-class", "sandhiExecution", "sutra-reference", "Visible a+a sandhi depends on the placeholder ac symbolic class."),
  dependency("dep.sandhi_t_t_to_tt.symbolic_hal", "sandhi_t_t_to_tt", "symbolic_hal", "symbolic-class", "sandhiExecution", "sutra-reference", "Visible t+t sandhi depends on the placeholder hal symbolic class."),

  dependency("dep.subanta_a_masculine_prathama_eka.suffix", "subanta_a_masculine_prathama_eka", "subanta_nominal_suffix_selection", "stage-placeholder", "subantaGeneration", "subanta-generator", "Lookup-backed masculine prathama eka depends on nominal suffix selection metadata."),
  dependency("dep.subanta_a_masculine_dvitiya_eka.suffix", "subanta_a_masculine_dvitiya_eka", "subanta_nominal_suffix_selection", "stage-placeholder", "subantaGeneration", "subanta-generator", "Lookup-backed masculine dvitiya eka depends on nominal suffix selection metadata."),
  dependency("dep.subanta_a_neuter_prathama_eka.suffix", "subanta_a_neuter_prathama_eka", "subanta_nominal_suffix_selection", "stage-placeholder", "subantaGeneration", "subanta-generator", "Lookup-backed neuter prathama eka depends on nominal suffix selection metadata."),
  dependency("dep.subanta_aa_feminine_prathama_eka.suffix", "subanta_aa_feminine_prathama_eka", "subanta_nominal_suffix_selection", "stage-placeholder", "subantaGeneration", "subanta-generator", "Lookup-backed feminine prathama eka depends on nominal suffix selection metadata."),

  dependency("dep.tinanta_bhu_lat_prathama_eka.lat", "tinanta_bhu_lat_prathama_eka", "tinanta_lat_parasmaipada_selection", "stage-placeholder", "tinantaGeneration", "tinanta-generator", "Lookup-backed bhu lat form depends on lat parasmaipada selection metadata."),
  dependency("dep.tinanta_gam_lat_prathama_eka.lat", "tinanta_gam_lat_prathama_eka", "tinanta_lat_parasmaipada_selection", "stage-placeholder", "tinantaGeneration", "tinanta-generator", "Lookup-backed gam lat form depends on lat parasmaipada selection metadata."),
  dependency("dep.tinanta_ni_lat_prathama_eka.lat", "tinanta_ni_lat_prathama_eka", "tinanta_lat_parasmaipada_selection", "stage-placeholder", "tinantaGeneration", "tinanta-generator", "Lookup-backed ni lat form depends on lat parasmaipada selection metadata."),

  dependency("dep.prakriya_generate_subanta_pada.stage", "prakriya_generate_subanta_pada", "subanta_generation_stage", "pipeline-stage", "subantaGeneration", "prakriya-composition", "Subanta pada emission depends on the subanta generation stage."),
  dependency("dep.prakriya_generate_tinanta_pada.stage", "prakriya_generate_tinanta_pada", "tinanta_generation_stage", "pipeline-stage", "tinantaGeneration", "prakriya-composition", "Tinanta pada emission depends on the tinanta generation stage."),
  dependency("dep.prakriya_assemble_padas.stage", "prakriya_assemble_padas", "pada_assembly_stage", "pipeline-stage", "padaAssembly", "prakriya-composition", "Pada assembly depends on deterministic pada assembly stage metadata."),
  dependency("dep.prakriya_apply_sandhi.stage", "prakriya_apply_sandhi", "sandhi_execution_stage", "pipeline-stage", "sandhiExecution", "prakriya-composition", "Prakriya sandhi application depends on sandhi execution stage metadata."),
  dependency("dep.prakriya_emit_sentence.stage", "prakriya_emit_sentence", "sentence_emission_stage", "pipeline-stage", "sentenceComposition", "prakriya-composition", "Sentence emission depends on final sentence composition stage metadata."),
];

export function normalizeSutraDependencyId(value) {
  return String(value ?? "")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "");
}

export function listSutraDependencies() {
  return SUTRA_DEPENDENCY_MAP.map((item) => ({ ...item }));
}

export function buildSutraDependencyIndex() {
  return listSutraDependencies().reduce((index, item) => {
    const ruleId = normalizeSutraDependencyId(item.ruleId);
    index[ruleId] = index[ruleId] || [];
    index[ruleId].push(item);
    return index;
  }, {});
}

export function getSutraDependenciesForRule(ruleId) {
  const index = buildSutraDependencyIndex();
  return [...(index[normalizeSutraDependencyId(ruleId)] || [])];
}

export function groupSutraDependenciesByStage() {
  return listSutraDependencies().reduce((groups, item) => {
    const stage = item.stage || "unresolved";
    groups[stage] = groups[stage] || [];
    groups[stage].push(item);
    return groups;
  }, {});
}

