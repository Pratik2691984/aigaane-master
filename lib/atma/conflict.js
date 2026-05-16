const ACTION_DOSHA_RESONANCE = {
  "mental:vata": 1.0,
  "mental:pitta": 0.55,
  "mental:kapha": 0.45,
  "physical:pitta": 1.0,
  "physical:kapha": 0.55,
  "physical:vata": 0.30,
  "rest:kapha": 1.0,
  "rest:vata": 0.70,
  "rest:pitta": 0.40,
  "eat:kapha": 0.85,
  "eat:pitta": 0.70,
  "eat:vata": 0.35
};

export function resonanceScore(currentDosha, action, agniFactor = 1) {
  let resonance = ACTION_DOSHA_RESONANCE[`${action}:${currentDosha}`] ?? 0.45;
  if (agniFactor < 0.2 && action === "eat") resonance *= 0.25;
  return Math.max(0, Math.min(1, resonance));
}

export function conflictScore(currentDosha, action, agniFactor = 1) {
  const resonance = resonanceScore(currentDosha, action, agniFactor);
  return Math.round(100 - (resonance * agniFactor * 100));
}

export function recommendationForDosha(currentDosha) {
  const recommendations = {
    vata: "Atmosphere is cold/dry. Prioritize hydration and creative ideation over heavy digestion.",
    pitta: "Heat is active. Choose precise effort, measured speech, and cooling pauses.",
    kapha: "Density is active. Favor light movement, warm stimulation, and simple momentum."
  };
  return recommendations[currentDosha] || recommendations.kapha;
}
