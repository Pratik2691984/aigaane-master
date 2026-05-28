import {
  matchSubantaRule,
  normalizeLinga,
  normalizeStemClass,
  normalizeSubantaInput,
  normalizeVacana,
  SUBANTA_SAMPLE_PARADIGMS,
} from "./subanta-rule-map.js";

const GENERATOR_SAFETY_NOTE =
  "Deterministic subanta generation preview only; no probabilistic parsing or unrestricted grammatical inference is performed.";

function stablePart(value) {
  return String(value ?? "unknown")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "") || "unknown";
}

function normalizedSource(input) {
  const source = input && typeof input === "object" ? input : {};
  const sample = SUBANTA_SAMPLE_PARADIGMS.find((item) => item.stem === normalizeSubantaInput(source.stem));
  return {
    stem: normalizeSubantaInput(source.stem),
    stemClass: normalizeStemClass(source.stemClass || sample?.stemClass),
    linga: normalizeLinga(source.linga || sample?.linga),
    vibhakti: normalizeSubantaInput(source.vibhakti).toLowerCase(),
    vacana: normalizeVacana(source.vacana),
  };
}

function stemBase(stem, rule) {
  if (rule?.baseStrategy === "drop-final-aa") {
    if (stem.endsWith("ा")) return stem.slice(0, -1);
    if (stem.endsWith("ā")) return stem.slice(0, -1);
  }
  return stem;
}

function applySuffix(stem, rule) {
  if (!stem || !rule) return "";
  return `${stemBase(stem, rule)}${rule.suffix}`;
}

function buildWarnings(rawInput, input, rule) {
  const warnings = [];
  if (!rawInput || typeof rawInput !== "object") warnings.push("Input was missing or not an object; deterministic empty generation returned.");
  if (!input.stem) warnings.push("No stem supplied.");
  if (!input.stemClass) warnings.push("No supported stem class supplied.");
  if (!input.linga) warnings.push("No supported linga supplied.");
  if (!input.vibhakti) warnings.push("No supported vibhakti supplied.");
  if (!input.vacana) warnings.push("No supported vacana supplied.");
  if (input.stem && input.stemClass && input.linga && input.vibhakti && input.vacana && !rule) {
    warnings.push("Unsupported deterministic subanta combination; no suffix was inferred.");
  }
  return warnings;
}

function buildTransformations(input, rule, generatedForm) {
  if (!rule) return [];
  const base = stemBase(input.stem, rule);
  return [
    {
      id: `subanta.transform.base.${stablePart(rule.id)}`,
      type: "stem-base",
      before: input.stem,
      after: base,
      explanation: rule.baseStrategy === "drop-final-aa" ? "Removed final ā/ा before suffix attachment." : "Stem base preserved for suffix attachment.",
    },
    {
      id: `subanta.transform.suffix.${stablePart(rule.id)}`,
      type: "suffix-attachment",
      before: base,
      after: generatedForm,
      explanation: `Attached deterministic ${rule.vibhakti} ${rule.vacana} suffix ${rule.suffix}.`,
    },
  ];
}

function buildTrace(input, rule, generatedForm, enableTrace) {
  if (enableTrace === false || !rule) return [];
  return [
    {
      id: `subanta.trace.1.${stablePart(rule.id)}`,
      step: 1,
      operation: "rule-match",
      before: `${input.stemClass}; ${input.linga}; ${input.vibhakti}; ${input.vacana}`,
      after: rule.id,
    },
    {
      id: `subanta.trace.2.${stablePart(rule.id)}`,
      step: 2,
      operation: "suffix-attachment",
      before: input.stem,
      after: generatedForm,
    },
  ];
}

function buildReversePreview(input, rule, generatedForm, enableReversePreview) {
  if (enableReversePreview === false || !rule?.reversible || !generatedForm) return [];
  return [
    {
      id: `subanta.reverse.${stablePart(rule.id)}`,
      generated: generatedForm,
      reconstructedStem: input.stem,
      suffix: rule.suffix,
      structuralOnly: true,
    },
  ];
}

export function generateSubanta(input = {}) {
  const safeInput = normalizedSource(input);
  const rule = matchSubantaRule(safeInput);
  const generatedForm = rule ? applySuffix(safeInput.stem, rule) : "";
  const supported = Boolean(rule && safeInput.stem);

  return {
    schemaVersion: "subanta-generator.v1",
    status: "ready",
    generatorType: "deterministic-subanta",
    input: { ...safeInput },
    matched: supported,
    ruleId: supported ? rule.id : null,
    generatedForm: supported ? generatedForm : "",
    suffix: supported ? rule.suffix : "",
    transformations: supported ? buildTransformations(safeInput, rule, generatedForm) : [],
    trace: supported ? buildTrace(safeInput, rule, generatedForm, input?.enableTrace) : [],
    reversePreview: supported ? buildReversePreview(safeInput, rule, generatedForm, input?.enableReversePreview) : [],
    diagnostics: {
      supported,
      warnings: buildWarnings(input, safeInput, rule),
      safetyNote: GENERATOR_SAFETY_NOTE,
    },
  };
}
