export const ACTION_DOSHA_R = Object.freeze({
  mental: Object.freeze({ vata: 1, pitta: 0.55, kapha: 0.45 }),
  physical: Object.freeze({ vata: 0.3, pitta: 1, kapha: 0.55 }),
  rest: Object.freeze({ vata: 0.7, pitta: 0.4, kapha: 1 }),
  eat: Object.freeze({ vata: 0.35, pitta: 0.7, kapha: 0.85 })
});

export const REMEDIES = Object.freeze({
  vata: Object.freeze({ raga: "Bhairav", matrika: "LAM", tag: "grounding" }),
  pitta: Object.freeze({ raga: "Yaman", matrika: "SHAM", tag: "cooling" }),
  kapha: Object.freeze({ raga: "Bhairavi", matrika: "RAM", tag: "activation" })
});

const ALIASES = {
  "mental-work": "mental",
  study: "mental",
  planning: "mental",
  "physical-work": "physical",
  exercise: "physical",
  meal: "eat",
  eating: "eat",
  sleep: "rest"
};

export function calculateFriction({
  user_action,
  current_dosha,
  agni_factor,
  lunar_velocity = 1,
  cosmic_angle = 0
}) {
  const action = ALIASES[(user_action || "").toLowerCase()] || (user_action || "").toLowerCase();
  const dosha = (current_dosha || "").toLowerCase();
  const row = ACTION_DOSHA_R[action];
  if (!row || row[dosha] == null) {
    throw new Error("Unknown action x dosha pair: " + action + " x " + dosha);
  }
  const agni = Math.max(0, Math.min(1, Number(agni_factor) || 0));
  const lunar = Math.max(0.5, Math.min(1.5, Number(lunar_velocity) || 1));
  let R = row[dosha];
  const flags = [];
  if (agni < 0.2) {
    flags.push("metabolic_low");
    if (action === "eat") {
      R *= 0.25;
      flags.push("heavy_digestion_penalty");
    }
  }
  R = Math.max(0, Math.min(1, R * lunar));
  const conflict = Number((100 - R * agni * 100).toFixed(2));
  const remedy = REMEDIES[dosha];
  return {
    user_action: action,
    current_dosha: dosha,
    cosmic_angle,
    agni_factor: agni,
    lunar_velocity: lunar,
    resonance_score: Number(R.toFixed(4)),
    conflict,
    label: conflict < 20 ? "Aligned" : conflict < 60 ? "Mixed" : "High Friction",
    flags,
    raga_suggestion: conflict > 50 ? remedy.raga : null,
    matrika_suggestion: conflict > 50 ? remedy.matrika : null,
    tag: remedy.tag
  };
}
