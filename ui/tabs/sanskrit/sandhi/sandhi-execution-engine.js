import {
  listSandhiRules,
  normalizeSandhiInput,
} from "./sandhi-rule-map.js";

const EXECUTION_SAFETY_NOTE =
  "Deterministic sandhi execution preview only; no probabilistic parsing or authoritative grammatical claim is made.";

function stablePart(value) {
  return String(value ?? "unknown")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "") || "unknown";
}

function tokenText(token) {
  if (typeof token === "string" || typeof token === "number") return normalizeSandhiInput(token);
  if (!token || typeof token !== "object") return "";
  return normalizeSandhiInput(token.token ?? token.text ?? token.value ?? token.label ?? "");
}

function explicitTokens(input) {
  if (Array.isArray(input?.tokens)) {
    return input.tokens.map(tokenText).filter(Boolean);
  }
  return normalizeSandhiInput(input?.text)
    .split(/\s+/u)
    .filter(Boolean);
}

function boundaryForPair(leftToken, rightToken) {
  const rules = listSandhiRules();
  for (const rule of rules) {
    if (leftToken.endsWith(rule.left) && rightToken.startsWith(rule.right)) {
      return {
        leftBoundary: rule.left,
        rightBoundary: rule.right,
        rule,
      };
    }
  }

  return {
    leftBoundary: Array.from(leftToken).slice(-1)[0] || "",
    rightBoundary: Array.from(rightToken)[0] || "",
    rule: null,
  };
}

function applyBoundary(leftToken, rightToken, rule) {
  if (!rule) return `${leftToken} ${rightToken}`.trim();
  const leftStem = leftToken.slice(0, leftToken.length - rule.left.length);
  const rightTail = rightToken.slice(rule.right.length);
  return `${leftStem}${rule.result}${rightTail}`;
}

function buildTransition(leftToken, rightToken, index) {
  const boundary = boundaryForPair(leftToken, rightToken);
  const rule = boundary.rule;
  const matched = Boolean(rule);
  const originalBoundary = `${boundary.leftBoundary}+${boundary.rightBoundary}`;
  const transformedBoundary = matched ? rule.result : `${boundary.leftBoundary}${boundary.rightBoundary}`;
  const id = `sandhi.transition.${index}.${stablePart(originalBoundary)}.${matched ? stablePart(rule.id) : "unmatched"}`;

  return {
    id,
    leftToken,
    rightToken,
    boundary: originalBoundary,
    matched,
    category: rule?.category || "unmatched",
    ruleId: rule?.id || null,
    sutraReference: rule?.sutraReference || null,
    originalBoundary,
    transformedBoundary,
    reversible: Boolean(rule?.reversible),
    confidence: "deterministic",
    notes: rule?.notes || EXECUTION_SAFETY_NOTE,
  };
}

function buildTransformedTokens(tokens, transitions) {
  if (tokens.length < 2) return [...tokens];
  const output = [];
  let index = 0;

  while (index < tokens.length) {
    const transition = transitions[index];
    if (transition?.matched) {
      output.push(applyBoundary(tokens[index], tokens[index + 1], {
        left: transition.originalBoundary.split("+")[0],
        right: transition.originalBoundary.split("+")[1],
        result: transition.transformedBoundary,
      }));
      index += 2;
      continue;
    }
    output.push(tokens[index]);
    index += 1;
  }

  return output;
}

function buildTrace(transitions, enableTrace) {
  if (enableTrace === false) return [];
  return transitions.map((transition, index) => ({
    id: `sandhi.trace.${index}.${stablePart(transition.id)}`,
    step: index + 1,
    ruleId: transition.ruleId,
    category: transition.category,
    before: `${transition.leftToken} | ${transition.rightToken}`,
    after: transition.matched
      ? applyBoundary(transition.leftToken, transition.rightToken, {
          left: transition.originalBoundary.split("+")[0],
          right: transition.originalBoundary.split("+")[1],
          result: transition.transformedBoundary,
        })
      : `${transition.leftToken} | ${transition.rightToken}`,
    explanation: transition.matched
      ? `Applied ${transition.ruleId} by deterministic priority ordering.`
      : "No deterministic rule matched this visible boundary.",
  }));
}

function buildReversePreview(transitions, enableReversePreview) {
  if (enableReversePreview === false) return [];
  return transitions
    .filter((transition) => transition.matched && transition.reversible)
    .map((transition, index) => ({
      id: `sandhi.reverse.${index}.${stablePart(transition.ruleId)}`,
      transformed: transition.transformedBoundary,
      reconstructed: transition.originalBoundary,
      structuralOnly: true,
    }));
}

function collectWarnings(input) {
  const warnings = [];
  if (!input || typeof input !== "object") {
    warnings.push("Input was missing or not an object; deterministic empty execution returned.");
    return warnings;
  }
  if (Array.isArray(input.tokens)) {
    input.tokens.forEach((token, index) => {
      if (!tokenText(token)) warnings.push(`Skipped malformed token at index ${index}.`);
    });
  }
  return warnings;
}

export function executeSandhi(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const tokens = explicitTokens(source);
  const transitions = [];

  for (let index = 0; index < tokens.length - 1; index += 1) {
    transitions.push(buildTransition(tokens[index], tokens[index + 1], index));
  }

  const matchedCount = transitions.filter((transition) => transition.matched).length;
  const transitionCount = transitions.length;

  return {
    schemaVersion: "sandhi-execution.v1",
    status: "ready",
    executionType: "deterministic-sandhi",
    mode: normalizeSandhiInput(source.mode) || "preview",
    originalTokens: [...tokens],
    transformedTokens: buildTransformedTokens(tokens, transitions),
    transitions,
    trace: buildTrace(transitions, source.enableTrace),
    reversePreview: buildReversePreview(transitions, source.enableReversePreview),
    diagnostics: {
      tokenCount: tokens.length,
      transitionCount,
      matchedCount,
      unmatchedCount: transitionCount - matchedCount,
      warnings: collectWarnings(input),
      safetyNote: EXECUTION_SAFETY_NOTE,
    },
  };
}
