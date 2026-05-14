// anumana-engine.js – numerically stable + resonance floor + confidence
const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
const AXES = 7;
const EPS = 1e-6;
const RESONANCE_FLOOR = 0.011; // 1.1% minimum intensity

const PARAMS = { lambda: 0.9, alpha: 0.6, beta: 0.3, gamma: 0.8 };

function noise() { return (Math.random() - 0.5) * 0.1; }

function computePhi(theta) {
  const rad = (theta * Math.PI) / 180;
  return Math.cos(rad) + 0.5 * Math.cos(2 * rad);
}

function sanitizeVector(vec) {
  return vec.map(v => {
    if (!Number.isFinite(v)) return EPS;
    if (v < 0) return EPS;
    if (v > 1) return 1;
    return v === 0 ? EPS : v;
  });
}

function applyModulation(S_base, theta) {
  const rad = (theta * Math.PI) / 180;
  return S_base.map((v, i) => clamp(v + 0.1 * Math.sin(rad + i * 0.1), EPS, 1));
}

function computeCoherence(delta) {
  const mean = delta.reduce((a,b) => a+b, 0) / delta.length;
  const variance = delta.reduce((sum, v) => sum + (v - mean) ** 2, 0) / delta.length;
  return clamp(1 - variance, 0, 1);
}

export function computeAnumana({ S_base, theta, A_prev = null, S_birth = null }) {
  let S = sanitizeVector(S_base);
  S = applyModulation(S, theta);

  if (S_birth) {
    const birth = sanitizeVector(S_birth);
    S = S.map((v, i) => 0.7 * v + 0.3 * birth[i]);
  }

  const phi = computePhi(theta);
  const A_next = [];
  const delta = [];

  for (let i = 0; i < 49; i++) {
    const prev = (A_prev && Number.isFinite(A_prev[i])) ? A_prev[i] : 0;
    const next = PARAMS.lambda * prev +
                 PARAMS.alpha * S[i] +
                 PARAMS.beta * noise() +
                 PARAMS.gamma * phi;
    const clamped = clamp(next, -1, 1);
    A_next.push(clamped);
    delta.push(clamped - prev);
  }

  // Extract dominant axes
  const axisScores = new Array(AXES).fill(0);
  delta.forEach((v, i) => { axisScores[i % AXES] += Math.abs(v); });
  const sorted = axisScores.map((v, i) => ({ axis: i, value: v }))
                           .sort((a,b) => b.value - a.value);
  let primaryAxis = sorted[0].axis;
  const secondaryAxis = sorted[1]?.axis || 0;

  let coherence = computeCoherence(delta);
  let rawIntensity = Math.tanh(Math.max(...delta.map(Math.abs), EPS));

  // ✅ Apply resonance floor
  let intensity = Math.max(rawIntensity, RESONANCE_FLOOR);
  
  // ✅ Confidence calculation: coherence (70%) + intensity (30%)
  let confidence = (coherence * 0.7) + (intensity * 0.3);
  confidence = clamp(confidence, 0, 1);

  // If intensity was pulled up from floor, but delta is tiny, force primary axis to 1 (stability)
  if (rawIntensity < RESONANCE_FLOOR && coherence > 0.8) {
    primaryAxis = 1;  // Axis 1 = Stabilise
  }

  // Guard against NaN
  if (!Number.isFinite(coherence)) coherence = 0;
  if (!Number.isFinite(intensity)) intensity = RESONANCE_FLOOR;
  if (!Number.isFinite(confidence)) confidence = 0.5;

  return {
    S,
    A_next,
    delta,
    phi,
    theta,
    axisScores,
    primaryAxis,
    secondaryAxis,
    coherence,
    intensity,
    confidence,
    status: (coherence < 0.2 && rawIntensity < 0.01) ? 'degraded' : 'stable'
  };
}