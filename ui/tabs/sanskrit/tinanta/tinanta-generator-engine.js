import {
  buildTinantaKey,
  listTinantaRules,
  matchTinantaRule,
  normalizeTinantaInput,
  reverseLookupTinanta,
} from "./tinanta-rule-map.js";

const GENERATOR_SAFETY_NOTE =
  "Deterministic tiṅanta generation preview only; no probabilistic parsing or grammatical intent guessing is performed.";

function stablePart(value) {
  return String(value ?? "unknown")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "") || "unknown";
}

function safeInput(input) {
  const source = input && typeof input === "object" ? input : {};
  return {
    dhatu: normalizeTinantaInput(source.dhatu),
    lakara: normalizeTinantaInput(source.lakara),
    pada: normalizeTinantaInput(source.pada),
    purusha: normalizeTinantaInput(source.purusha),
    vacana: normalizeTinantaInput(source.vacana),
  };
}

function buildWarnings(rawInput, input, rule) {
  const warnings = [];
  if (!rawInput || typeof rawInput !== "object") warnings.push("Input was missing or not an object; deterministic empty generation returned.");
  if (!input.dhatu) warnings.push("No dhatu supplied.");
  if (!input.lakara) warnings.push("No lakara supplied.");
  if (!input.pada) warnings.push("No pada supplied.");
  if (!input.purusha) warnings.push("No purusha supplied.");
  if (!input.vacana) warnings.push("No vacana supplied.");
  if (input.dhatu && input.lakara && input.pada && input.purusha && input.vacana && !rule) {
    warnings.push(`Unsupported deterministic tinanta key: ${buildTinantaKey(input)}.`);
  }
  return warnings;
}

function buildTransformations(rule) {
  if (!rule) return [];
  return [
    {
      id: `tinanta.transform.stem.${stablePart(rule.id)}`,
      type: "present-stem-selection",
      before: rule.dhatu,
      after: rule.presentStem,
      explanation: "Selected present stem from direct deterministic rule metadata.",
    },
    {
      id: `tinanta.transform.affix.${stablePart(rule.id)}`,
      type: "affix-selection",
      before: rule.presentStem,
      after: rule.generatedForm,
      explanation: `Applied direct laṭ/parasmaipada ${rule.purusha} ${rule.vacana} affix ${rule.affix}.`,
    },
  ];
}

function buildTrace(rule, enableTrace) {
  if (enableTrace === false || !rule) return [];
  return [
    {
      id: `tinanta.trace.1.${stablePart(rule.id)}`,
      step: 1,
      operation: "rule-key-match",
      before: `${rule.dhatu}|${rule.lakara}|${rule.pada}|${rule.purusha}|${rule.vacana}`,
      after: rule.id,
    },
    {
      id: `tinanta.trace.2.${stablePart(rule.id)}`,
      step: 2,
      operation: "direct-form-generation",
      before: `${rule.presentStem}+${rule.affix}`,
      after: rule.generatedForm,
    },
  ];
}

function buildReversePreview(rule, enableReversePreview) {
  if (enableReversePreview === false || !rule?.reversible) return [];
  return [
    {
      id: `tinanta.reverse.${stablePart(rule.id)}`,
      generated: rule.generatedForm,
      reconstructed: {
        dhatu: rule.dhatu,
        lakara: rule.lakara,
        pada: rule.pada,
        purusha: rule.purusha,
        vacana: rule.vacana,
      },
      structuralOnly: true,
    },
  ];
}

function outputFromRule(rawInput, normalized, rule) {
  const supported = Boolean(rule);
  return {
    schemaVersion: "tinanta-generator.v1",
    status: "ready",
    generatorType: "deterministic-tinanta",
    input: { ...normalized },
    matched: supported,
    ruleId: supported ? rule.id : null,
    generatedForm: supported ? rule.generatedForm : "",
    presentStem: supported ? rule.presentStem : "",
    affix: supported ? rule.affix : "",
    transformations: supported ? buildTransformations(rule) : [],
    trace: supported ? buildTrace(rule, rawInput?.enableTrace) : [],
    reversePreview: supported ? buildReversePreview(rule, rawInput?.enableReversePreview) : [],
    diagnostics: {
      supported,
      warnings: buildWarnings(rawInput, normalized, rule),
      safetyNote: GENERATOR_SAFETY_NOTE,
    },
  };
}

export function generateTinanta(input = {}) {
  const normalized = safeInput(input);
  const rule = matchTinantaRule(normalized);
  return outputFromRule(input, normalized, rule);
}

export function reverseTinanta(form) {
  const rule = reverseLookupTinanta(form);
  return {
    schemaVersion: "tinanta-reverse.v1",
    status: "ready",
    matched: Boolean(rule),
    generatedForm: normalizeTinantaInput(form),
    reconstructed: rule ? {
      dhatu: rule.dhatu,
      lakara: rule.lakara,
      pada: rule.pada,
      purusha: rule.purusha,
      vacana: rule.vacana,
    } : null,
    ruleId: rule?.id || null,
    diagnostics: {
      supported: Boolean(rule),
      warnings: rule ? [] : ["Unsupported deterministic tiṅanta reverse lookup form."],
      safetyNote: "Reverse lookup is structural metadata only, not authoritative reconstruction.",
    },
  };
}

export function generateTinantaParadigm(input = {}) {
  const source = safeInput(input);
  const dhatu = source.dhatu;
  const lakara = source.lakara || "laṭ";
  const pada = source.pada || "parasmaipada";
  const rules = listTinantaRules().filter((rule) => (
    matchTinantaRule({ dhatu, lakara, pada, purusha: rule.purusha, vacana: rule.vacana })?.id === rule.id
  ));

  return {
    schemaVersion: "tinanta-paradigm.v1",
    status: "ready",
    generatorType: "deterministic-tinanta-paradigm",
    input: { dhatu, lakara, pada },
    forms: rules.map((rule) => outputFromRule(input, {
      dhatu,
      lakara,
      pada,
      purusha: rule.purusha,
      vacana: rule.vacana,
    }, rule)),
    diagnostics: {
      supported: rules.length > 0,
      formCount: rules.length,
      warnings: rules.length > 0 ? [] : ["Unsupported deterministic tiṅanta paradigm request."],
      safetyNote: GENERATOR_SAFETY_NOTE,
    },
  };
}
