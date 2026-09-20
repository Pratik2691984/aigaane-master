import { SANDHI_TRANSITION_RULES } from "./sandhi-rules.js";

const UNKNOWN_SANDHI_SAFETY_NOTE =
  "No deterministic sandhi transition matched; no grammatical correctness claim is made.";

export function buildSandhiTransitionMap() {
  return SANDHI_TRANSITION_RULES.reduce((map, rule) => {
    map[`${rule.left}+${rule.right}`] = {
      ...rule,
      matched: true,
    };
    return map;
  }, {});
}

export function lookupSandhiTransition(left, right) {
  const map = buildSandhiTransitionMap();
  const normalizedLeft = String(left ?? "");
  const normalizedRight = String(right ?? "");
  const matched = map[`${normalizedLeft}+${normalizedRight}`];

  if (matched) return matched;

  return {
    matched: false,
    left: normalizedLeft,
    right: normalizedRight,
    result: `${normalizedLeft}${normalizedRight}`,
    category: "unknown",
    safetyNote: UNKNOWN_SANDHI_SAFETY_NOTE,
  };
}
