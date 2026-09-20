import { executeSandhi } from "../sandhi/sandhi-execution-engine.js";
import { generateSubanta } from "../subanta/subanta-generator-engine.js";
import { generateTinanta } from "../tinanta/tinanta-generator-engine.js";
import { buildPrakriyaStageSequence } from "./prakriya-composition-map.js";

const PRAKRIYA_SAFETY_NOTE =
  "Deterministic prakriya composition preview only; no unrestricted parsing, semantic interpretation, or agreement correction is performed.";

function stablePart(value) {
  return String(value ?? "unknown")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "") || "unknown";
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function clonePlain(value) {
  if (!value || typeof value !== "object") return value;
  return JSON.parse(JSON.stringify(value));
}

function generatedPada(id, sourceType, generation) {
  return {
    id,
    sourceType,
    sourceRuleId: generation.ruleId || null,
    generatedForm: generation.generatedForm || "",
    diagnostics: {
      supported: Boolean(generation.diagnostics?.supported),
      warnings: [...(generation.diagnostics?.warnings || [])],
    },
  };
}

function unresolvedPada(id, sourceType, warnings) {
  return {
    id,
    sourceType,
    sourceRuleId: null,
    generatedForm: "",
    diagnostics: {
      supported: false,
      warnings,
    },
  };
}

function orderPadas(padas, sentenceOrder) {
  if (!Array.isArray(sentenceOrder) || sentenceOrder.length === 0) return [...padas];
  const byId = new Map(padas.map((pada) => [pada.id, pada]));
  const ordered = [];
  sentenceOrder.forEach((id) => {
    const pada = byId.get(String(id));
    if (pada) {
      ordered.push(pada);
      byId.delete(String(id));
    }
  });
  return [...ordered, ...byId.values()];
}

function buildTrace(stages, padas, sentenceAssembly, sandhiExecution, enableTrace) {
  if (enableTrace === false) return [];
  const trace = [];
  const push = (stage, before, after, operation) => {
    trace.push({
      id: `prakriya.trace.${trace.length + 1}.${stablePart(stage)}`,
      step: trace.length + 1,
      stage,
      before,
      after,
      operation,
    });
  };

  stages.forEach((stage) => {
    if (stage.id === "subantaGeneration") {
      push(stage.id, "nounInputs", `${padas.filter((pada) => pada.sourceType === "subanta").length} noun padas`, "generate-subanta-components");
    } else if (stage.id === "tinantaGeneration") {
      push(stage.id, "verbInput", `${padas.filter((pada) => pada.sourceType === "tinanta").length} verb padas`, "generate-tinanta-component");
    } else if (stage.id === "padaAssembly") {
      push(stage.id, padas.map((pada) => pada.id).join(" "), sentenceAssembly.preSandhiText, "assemble-padas");
    } else if (stage.id === "sandhiExecution") {
      push(stage.id, sentenceAssembly.preSandhiText, sentenceAssembly.postSandhiText, "execute-deterministic-sandhi");
    } else if (stage.id === "sentenceComposition") {
      push(stage.id, sentenceAssembly.preSandhiText, sentenceAssembly.postSandhiText, "emit-structural-sentence");
    }
  });

  (sandhiExecution?.trace || []).forEach((node) => {
    trace.push({
      id: `prakriya.trace.${trace.length + 1}.${stablePart(node.id)}`,
      step: trace.length + 1,
      stage: "sandhiExecution",
      before: node.before,
      after: node.after,
      operation: node.operation || node.explanation || "sandhi-trace",
    });
  });

  return trace;
}

function buildReversePreview(padas, sandhiExecution, enableReversePreview) {
  if (enableReversePreview === false) return [];
  const reverse = padas
    .filter((pada) => pada.generatedForm)
    .map((pada, index) => ({
      id: `prakriya.reverse.${index}.${stablePart(pada.id)}`,
      generated: pada.generatedForm,
      reconstructed: {
        sourceType: pada.sourceType,
        sourceRuleId: pada.sourceRuleId,
      },
      structuralOnly: true,
    }));

  (sandhiExecution?.reversePreview || []).forEach((item, index) => {
    reverse.push({
      id: `prakriya.reverse.sandhi.${index}.${stablePart(item.id)}`,
      generated: item.transformed,
      reconstructed: item.reconstructed,
      structuralOnly: true,
    });
  });

  return reverse;
}

function collectWarnings(padas, input) {
  const warnings = [];
  if (!input || typeof input !== "object") warnings.push("Input was missing or not an object; deterministic empty composition returned.");
  if (!Array.isArray(input?.nounInputs)) warnings.push("nounInputs missing or not an array.");
  if (!input?.verbInput || typeof input.verbInput !== "object") warnings.push("verbInput missing or not an object.");
  padas.forEach((pada) => {
    (pada.diagnostics?.warnings || []).forEach((warning) => warnings.push(`${pada.id}: ${warning}`));
  });
  return warnings;
}

export function executePrakriya(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const stages = buildPrakriyaStageSequence();
  const generatedPadas = [];

  asArray(source.nounInputs).forEach((nounInput, index) => {
    const generation = generateSubanta({
      ...(nounInput && typeof nounInput === "object" ? nounInput : {}),
      enableTrace: source.enableTrace,
      enableReversePreview: source.enableReversePreview,
    });
    const pada = generatedPada(`pada.subanta.${index}`, "subanta", generation);
    if (!pada.generatedForm) {
      generatedPadas.push(unresolvedPada(pada.id, "subanta", pada.diagnostics.warnings));
    } else {
      generatedPadas.push(pada);
    }
  });

  const verbGeneration = generateTinanta({
    ...(source.verbInput && typeof source.verbInput === "object" ? source.verbInput : {}),
    enableTrace: source.enableTrace,
    enableReversePreview: source.enableReversePreview,
  });
  const verbPada = generatedPada("pada.tinanta.0", "tinanta", verbGeneration);
  generatedPadas.push(verbPada.generatedForm ? verbPada : unresolvedPada(verbPada.id, "tinanta", verbPada.diagnostics.warnings));

  const orderedPadas = orderPadas(generatedPadas, source.sentenceOrder);
  const visiblePadas = orderedPadas.filter((pada) => pada.generatedForm);
  const preSandhiText = visiblePadas.map((pada) => pada.generatedForm).join(" ");
  const sandhiExecution = source.enableSandhi === false
    ? null
    : executeSandhi({
        text: preSandhiText,
        tokens: visiblePadas.map((pada, index) => ({ token: pada.generatedForm, index, id: pada.id })),
        mode: "prakriya-composition",
        enableTrace: source.enableTrace,
        enableReversePreview: source.enableReversePreview,
      });
  const postSandhiText = sandhiExecution?.transformedTokens?.length
    ? sandhiExecution.transformedTokens.join(" ")
    : preSandhiText;

  const unresolvedCount = generatedPadas.filter((pada) => !pada.diagnostics.supported).length;
  const sandhiAppliedCount = (sandhiExecution?.transitions || []).filter((transition) => transition.matched).length;

  return {
    schemaVersion: "prakriya-composition.v1",
    status: "ready",
    executionType: "deterministic-prakriya",
    inputs: clonePlain(source) || {},
    stages,
    generatedPadas,
    sentenceAssembly: {
      orderedPadas: orderedPadas.map((pada) => pada.id),
      preSandhiText,
      postSandhiText,
    },
    sandhiTransitions: sandhiExecution?.transitions || [],
    trace: buildTrace(stages, generatedPadas, { preSandhiText, postSandhiText }, sandhiExecution, source.enableTrace),
    reversePreview: buildReversePreview(generatedPadas, sandhiExecution, source.enableReversePreview),
    diagnostics: {
      generatedPadaCount: visiblePadas.length,
      sandhiAppliedCount,
      unresolvedCount,
      warnings: collectWarnings(generatedPadas, input),
      safetyNote: PRAKRIYA_SAFETY_NOTE,
    },
  };
}

export function buildPrakriyaPreview(input = {}) {
  return executePrakriya({
    ...((input && typeof input === "object") ? input : {}),
    enableTrace: true,
    enableReversePreview: true,
  });
}
