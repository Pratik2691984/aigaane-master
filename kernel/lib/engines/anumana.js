/** Deterministic Anumana. No Math.random. */

export const ANUMANA_PARAMS = Object.freeze({
  lambda: 0.9,
  alpha: 0.6,
  beta: 0.3,
  gamma: 0.8,
  resonanceFloor: 0.011,
  amplitude: 0.1
});

export function hash32(n) {
  let x = n >>> 0;
  x = Math.imul(x ^ (x >>> 16), 0x7feb352d);
  x = Math.imul(x ^ (x >>> 15), 0x846ca68b);
  return (x ^ (x >>> 16)) >>> 0;
}

export function unitNoise(pada_id, nakshatra_id, t, index) {
  const h = hash32(
    ((pada_id + 1) * 73856093) ^
      ((nakshatra_id + 1) * 19349663) ^
      ((t + 1) * 83492791) ^
      ((index + 1) * 39916801)
  );
  return (h / 4294967295) * 2 - 1;
}

export function phi(thetaDeg) {
  const rad = (thetaDeg * Math.PI) / 180;
  return Math.cos(rad) + 0.5 * Math.cos(2 * rad);
}

export function computeAnumana({ S, theta, A_prev = null, pada_id = 0, nakshatra_id = 0, t = 0 }) {
  const { lambda, alpha, beta, gamma, resonanceFloor, amplitude } = ANUMANA_PARAMS;
  const ph = phi(theta);
  const A_next = new Float64Array(49);
  const delta = new Float64Array(49);
  for (let i = 0; i < 49; i++) {
    const prev = A_prev && Number.isFinite(A_prev[i]) ? A_prev[i] : 0;
    const eps = unitNoise(pada_id, nakshatra_id, t, i) * amplitude;
    const next = lambda * prev + alpha * S[i] + beta * eps + gamma * ph;
    A_next[i] = Math.max(-1, Math.min(1, next));
    delta[i] = A_next[i] - prev;
  }
  let maxAbs = 0;
  let mean = 0;
  for (let i = 0; i < 49; i++) {
    mean += delta[i];
    const a = Math.abs(delta[i]);
    if (a > maxAbs) maxAbs = a;
  }
  mean /= 49;
  let varSum = 0;
  for (let i = 0; i < 49; i++) varSum += (delta[i] - mean) ** 2;
  const coherence = Math.max(0, Math.min(1, 1 - varSum / 49));
  const intensity = Math.max(Math.tanh(maxAbs), resonanceFloor);
  return { A_next, delta, phi: ph, coherence, intensity, t };
}
