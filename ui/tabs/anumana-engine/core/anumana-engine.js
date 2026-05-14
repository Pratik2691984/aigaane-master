// anumana-engine.js

const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

const AXES = 7;

// Default parameters
const PARAMS = {
  lambda: 0.9,
  alpha: 0.6,
  beta: 0.3,
  gamma: 0.8
};

// Noise generator
function noise() {
  return (Math.random() - 0.5) * 0.1;
}

// Φ_total
function computePhi(theta) {
  const rad = (theta * Math.PI) / 180;
  return Math.cos(rad) + 0.5 * Math.cos(2 * rad);
}

// Modulation
function applyModulation(S_base, theta) {
  const rad = (theta * Math.PI) / 180;

  return S_base.map((v, i) => {
    const mod = 0.1 * Math.sin(rad + i * 0.1);
    return clamp(v + mod, 0, 1);
  });
}

// Main engine
export function computeAnumana({
  S_base,
  theta,
  A_prev = null,
  S_birth = null
}) {
  const phi = computePhi(theta);

  let S = applyModulation(S_base, theta);

  // Personalization (birth vector)
  if (S_birth) {
    S = S.map((v, i) => 0.7 * v + 0.3 * S_birth[i]);
  }

  const A_next = [];
  const delta = [];

  for (let i = 0; i < 49; i++) {
    const prev = A_prev ? A_prev[i] : 0;

    const next =
      PARAMS.lambda * prev +
      PARAMS.alpha * S[i] +
      PARAMS.beta * noise() +
      PARAMS.gamma * phi;

    const clamped = clamp(next, -1, 1);

    A_next.push(clamped);
    delta.push(clamped - prev);
  }

  const dominant = extractDominantAxes(delta);

  return {
    S,
    A_next,
    delta,
    phi,
    ...dominant,
    coherence: computeCoherence(delta),
    intensity: Math.tanh(Math.max(...delta.map(Math.abs)))
  };
}

// Axis aggregation
function extractDominantAxes(delta) {
  const axisScores = new Array(AXES).fill(0);

  delta.forEach((v, i) => {
    const axis = i % AXES;
    axisScores[axis] += Math.abs(v);
  });

  const sorted = axisScores
    .map((v, i) => ({ axis: i, value: v }))
    .sort((a, b) => b.value - a.value);

  return {
    axisScores,
    primaryAxis: sorted[0].axis,
    secondaryAxis: sorted[1].axis
  };
}

// Coherence
function computeCoherence(delta) {
  const mean =
    delta.reduce((a, b) => a + b, 0) / delta.length;

  const variance =
    delta.reduce((a, b) => a + (b - mean) ** 2, 0) /
    delta.length;

  return clamp(1 - variance, 0, 1);
}