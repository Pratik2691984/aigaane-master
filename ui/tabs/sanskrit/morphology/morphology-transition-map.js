export const MORPHOLOGY_TRANSITION_SAFETY_NOTE =
  "Morphology transition layer is deterministic placeholder metadata only; no authoritative morphology generation or grammatical correctness claim is made.";

export const MORPHOLOGY_TRANSITION_NODES = [
  {
    id: "dhatu_gam",
    type: "dhatu",
    label: "गम् / gam",
    stage: "root",
    description: "Placeholder-safe dhatu node for deterministic morphology transition preview.",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "dhatu_bhu",
    type: "dhatu",
    label: "भू / bhū",
    stage: "root",
    description: "Placeholder-safe dhatu node for deterministic morphology transition preview.",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "stem_gaccha",
    type: "stem",
    label: "gaccha",
    stage: "stem",
    description: "Placeholder-safe stem node; no generated morphology claim is made.",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "stem_bhava",
    type: "stem",
    label: "bhava",
    stage: "stem",
    description: "Placeholder-safe stem node; no generated morphology claim is made.",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "suffix_ti",
    type: "suffix",
    label: "ti",
    stage: "suffix",
    description: "Placeholder-safe suffix node for read-only transition inspection.",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "suffix_ta",
    type: "suffix",
    label: "ta",
    stage: "suffix",
    description: "Placeholder-safe suffix node for read-only transition inspection.",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "form_gacchati",
    type: "surface_form",
    label: "gacchati",
    stage: "surface",
    description: "Placeholder-safe surface-form node for deterministic preview.",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "form_bhavata",
    type: "surface_form",
    label: "bhavata",
    stage: "surface",
    description: "Placeholder-safe surface-form node for deterministic preview.",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
];

export const MORPHOLOGY_TRANSITION_EDGES = [
  {
    id: "edge.dhatu_gam.stem_gaccha",
    source: "dhatu_gam",
    target: "stem_gaccha",
    relation: "root_to_stem_placeholder",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "edge.stem_gaccha.suffix_ti",
    source: "stem_gaccha",
    target: "suffix_ti",
    relation: "stem_to_suffix_placeholder",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "edge.suffix_ti.form_gacchati",
    source: "suffix_ti",
    target: "form_gacchati",
    relation: "suffix_to_surface_placeholder",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "edge.dhatu_bhu.stem_bhava",
    source: "dhatu_bhu",
    target: "stem_bhava",
    relation: "root_to_stem_placeholder",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "edge.stem_bhava.suffix_ta",
    source: "stem_bhava",
    target: "suffix_ta",
    relation: "stem_to_suffix_placeholder",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
  {
    id: "edge.suffix_ta.form_bhavata",
    source: "suffix_ta",
    target: "form_bhavata",
    relation: "suffix_to_surface_placeholder",
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  },
];
