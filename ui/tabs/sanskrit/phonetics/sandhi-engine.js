import { lookupSandhiTransition } from "./sandhi-transition-map.js";

const SANDHI_TEXT_SAFETY_NOTE =
  "Deterministic sandhi boundary inspection only; no authoritative grammar claim is made.";

function normalizeInput(value) {
  return String(value ?? "").trim();
}

function splitTokens(input) {
  return normalizeInput(input).split(/\s+/).filter(Boolean);
}

function firstBoundary(token) {
  return token.match(/^[\u0915-\u0939]\u094d/u)?.[0] || token.slice(0, 1);
}

function lastBoundary(token) {
  return token.match(/[\u0915-\u0939]\u094d$/u)?.[0] || token.slice(-1);
}

export function inspectSandhiPair(left = "", right = "") {
  const normalizedLeft = normalizeInput(left);
  const normalizedRight = normalizeInput(right);
  const transition = lookupSandhiTransition(normalizedLeft, normalizedRight);

  return {
    input: {
      left: normalizedLeft,
      right: normalizedRight,
    },
    matched: Boolean(transition.matched),
    category: transition.category,
    result: transition.result,
    ruleId: transition.id,
    label: transition.label,
    safetyNote: transition.safetyNote,
  };
}

export function inspectSandhiText(input = "") {
  const normalizedInput = String(input ?? "");
  const tokens = splitTokens(normalizedInput);
  const transitions = [];

  for (let index = 0; index < tokens.length - 1; index += 1) {
    const leftToken = tokens[index];
    const rightToken = tokens[index + 1];
    const leftBoundary = lastBoundary(leftToken);
    const rightBoundary = firstBoundary(rightToken);
    const transition = inspectSandhiPair(leftBoundary, rightBoundary);

    transitions.push({
      index,
      leftToken,
      rightToken,
      leftBoundary,
      rightBoundary,
      ...transition,
    });
  }

  const matchedCount = transitions.filter((transition) => transition.matched).length;
  const transitionCount = transitions.length;

  return {
    input: normalizedInput,
    transitions,
    summary: {
      tokenCount: tokens.length,
      transitionCount,
      matchedCount,
      unmatchedCount: transitionCount - matchedCount,
    },
    safetyNote: SANDHI_TEXT_SAFETY_NOTE,
  };
}
