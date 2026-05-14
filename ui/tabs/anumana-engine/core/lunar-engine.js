// lunar-engine.js

const NAKSHATRA_SIZE = 13 + 20 / 60; // 13.3333°
const PADA_SIZE = NAKSHATRA_SIZE / 4;

// Simple deterministic moon cycle (approximation)
export function getMoonState(timestamp = Date.now()) {
  const days = timestamp / (1000 * 60 * 60 * 24);

  // Mean moon motion ~13.176° per day
  const longitude = (days * 13.176396) % 360;

  const nakshatraIndex = Math.floor(longitude / NAKSHATRA_SIZE);
  const pada = Math.floor((longitude % NAKSHATRA_SIZE) / PADA_SIZE) + 1;

  const theta = (days * 12.19075) % 360; // phase approximation

  return {
    longitude,
    nakshatraIndex,
    pada,
    theta,
    phase: getPhase(theta)
  };
}

function getPhase(theta) {
  if (theta < 45) return "New";
  if (theta < 135) return "Waxing";
  if (theta < 225) return "Full";
  if (theta < 315) return "Waning";
  return "New";
}