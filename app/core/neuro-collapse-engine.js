const clamp = (value, min = 0, max = 1) => Math.max(min, Math.min(max, value));
const EPS = 1e-9;
const SIZE = 7;
const VECTOR_SIZE = SIZE * SIZE;

function makeVector(seed = 0.17) {
  return Array.from({ length: VECTOR_SIZE }, (_, index) => {
    const wave = Math.sin(seed * 13.37 + index * 0.73) * 0.5 + 0.5;
    return clamp(0.22 + wave * 0.34);
  });
}

function normalizeVector(vector) {
  const source = Array.isArray(vector) && vector.length === VECTOR_SIZE ? vector : makeVector();
  return source.map(value => clamp(Number.isFinite(value) ? value : 0, 0, 1));
}

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / Math.max(values.length, 1);
}

function variance(values) {
  const avg = mean(values);
  return mean(values.map(value => (value - avg) ** 2));
}

function estimateK({ coupling, noise, drift }) {
  const collapseDrive = coupling - noise * 1.7 + drift * 0.8;
  if (collapseDrive >= 3.15) return 1;
  if (collapseDrive >= 1.65) return 2;
  return Math.max(3, Math.min(7, Math.round(7 - collapseDrive * 1.7)));
}

function estimateClusterSizes(k, coupling, noise) {
  if (k <= 1) return [VECTOR_SIZE];
  if (k === 2) {
    const skew = clamp(noise * 0.08 + Math.abs(coupling - 2.35) * 0.025, 0.04, 0.18);
    const smaller = Math.max(1, Math.round(VECTOR_SIZE * (0.5 - skew)));
    return [VECTOR_SIZE - smaller, smaller];
  }

  const clusters = [];
  let remaining = VECTOR_SIZE;
  for (let i = 0; i < k; i++) {
    const size = i === k - 1 ? remaining : Math.max(1, Math.round(VECTOR_SIZE / k + Math.sin(i * 1.7) * noise * 2));
    clusters.push(size);
    remaining -= size;
  }
  return clusters;
}

export function computePLV(currentState = {}, previousState = {}) {
  const current = normalizeVector(currentState.vector);
  const previous = normalizeVector(previousState?.vector || current);
  let real = 0;
  let imag = 0;

  for (let i = 0; i < VECTOR_SIZE; i++) {
    const phaseDelta = (current[i] - previous[i]) * Math.PI * 2;
    real += Math.cos(phaseDelta);
    imag += Math.sin(phaseDelta);
  }

  return clamp(Math.sqrt(real ** 2 + imag ** 2) / VECTOR_SIZE);
}

export function computeEntropy(values = []) {
  const vector = normalizeVector(values.length === VECTOR_SIZE ? values : makeVector());
  const total = vector.reduce((sum, value) => sum + Math.max(value, EPS), 0);
  const h = vector.reduce((sum, value) => {
    const p = Math.max(value, EPS) / total;
    return sum - p * Math.log(p);
  }, 0);
  return clamp(h / Math.log(VECTOR_SIZE));
}

export function computeClusterEntropy(clusterSizes, totalNodes) {
  const EPS = 1e-12;
  if (!clusterSizes || clusterSizes.length <= 1) return 0;

  let H = 0;
  for (const size of clusterSizes) {
    const p = size / totalNodes;
    if (p > 0) H -= p * Math.log2(p + EPS);
  }

  const k = clusterSizes.length;
  const Hmax = Math.log2(k + EPS);

  return Hmax > EPS ? Math.min(1, Math.max(0, H / Hmax)) : 0;
}

export function computeResidualClusterMass(clusterSizes, totalNodes) {
  if (!clusterSizes || clusterSizes.length <= 1) return 0;
  const sorted = [...clusterSizes].sort((a, b) => b - a);
  const residual = totalNodes - sorted[0];
  return residual / totalNodes;
}

export function computeClusterBalanceRatio(clusterSizes) {
  if (!clusterSizes || clusterSizes.length !== 2) return 0;
  const [clusterA, clusterB] = clusterSizes;
  const larger = Math.max(clusterA, clusterB);
  if (larger <= 0) return 0;
  return Math.min(clusterA, clusterB) / larger;
}

export function computeSpectralGap(k = 3, coupling = 1, noise = 0) {
  if (k <= 1) return Math.max(1e-5, 0.006 + coupling * 0.018 - noise * 0.003);
  if (k === 2) return Math.max(0, 8e-7 + noise * 2e-6);
  return clamp(0.0008 + coupling * 0.002 + noise * 0.001, 0, 0.018);
}

export function computeNetworkCPI({ plv = 0, lambda2 = 0, entropy = 1, coupling = 1, k = 3 } = {}) {
  const bridgeTerm = k === 2 ? 0.22 : k === 1 ? 0.14 : 0;
  const synchrony = plv * 0.36 + clamp(coupling / 5) * 0.3;
  const entropyPressure = (1 - entropy) * 0.12;
  const spectralPenalty = k === 2 ? clamp(lambda2 * 9000) * 0.18 : 0;
  return clamp(0.22 + synchrony + entropyPressure + bridgeTerm - spectralPenalty);
}

export function detectCollapseState({
  k,
  lambda2,
  cpi,
  syncRatio,
  entropy,
  clusterBalanceRatio
}) {
  const LAMBDA_CONNECTED = 1e-4;
  const CPI_PRE = 0.85;
  const SYNC_PRE = 0.9;
  const ENTROPY_PRE = 0.25;
  const BALANCE_PRE = 0.35;

  if (k === 1 && lambda2 > LAMBDA_CONNECTED) {
    return "COLLAPSED";
  }

  if (
    k === 2 &&
    lambda2 <= LAMBDA_CONNECTED &&
    cpi >= CPI_PRE &&
    syncRatio >= SYNC_PRE &&
    entropy <= ENTROPY_PRE &&
    clusterBalanceRatio >= BALANCE_PRE
  ) {
    return "PRE_COLLAPSE";
  }

  return "NORMAL";
}

export function projectTo49D(currentState = {}, previousState = {}) {
  const previous = normalizeVector(previousState?.vector);
  const noise = clamp(currentState.noise ?? 0.35);
  const coupling = clamp(currentState.coupling ?? 1.2, 0, 5);
  const speed = clamp(currentState.speed ?? 1, 0.25, 3);
  const time = (previousState?.time || 0) + 0.018 * speed;
  const drift = mean(previous.map((value, index) => Math.abs(value - (previous[(index + 7) % VECTOR_SIZE] || value))));
  const k = estimateK({ coupling, noise, drift });
  const target = k === 1 ? 0.94 : k === 2 ? 0.72 : 0.42;

  const vector = previous.map((value, index) => {
    const row = Math.floor(index / SIZE);
    const col = index % SIZE;
    const wave = Math.sin(time * (1.3 + coupling * 0.18) + row * 0.9 + col * 0.45);
    const fragment = Math.sin(index * 2.17 + time * 2.2) * noise * 0.25;
    const basin = target + wave * 0.08 + fragment;
    const inertia = k === 1 ? 0.22 : k === 2 ? 0.35 : 0.55;
    return clamp(value * inertia + basin * (1 - inertia));
  });

  return { vector, time, k };
}

function buildTensor({ vector, phase, k, cpi, lambda2, entropy, coupling, noise, previousVector }) {
  const tensor = Array.from({ length: SIZE }, () => Array(SIZE).fill(0));
  const momentum = previousVector
    ? mean(vector.map((value, index) => Math.abs(value - previousVector[index])))
    : 0;
  const spread = clamp(Math.sqrt(variance(vector)) * 3);

  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const index = row * SIZE + col;
      const base = vector[index];
      if (phase === "COLLAPSED") {
        tensor[row][col] = row === 0 && col === 0 ? 1 : clamp(cpi * (0.42 - (row + col) * 0.025));
      } else if (phase === "PRE_COLLAPSE") {
        tensor[row][col] = clamp(0.36 + (row === 1 || col === 1 ? 0.36 : 0.08) + coupling * 0.06 - lambda2 * 1000);
      } else {
        const fragmentBias = row === 2 || row === 3 ? 0.22 : 0;
        tensor[row][col] = clamp(base * 0.32 + entropy * 0.28 + spread * 0.25 + fragmentBias + noise * 0.12);
      }
    }
  }

  tensor[0][0] = phase === "COLLAPSED" ? 1 : clamp(cpi);
  tensor[1][1] = phase === "PRE_COLLAPSE" ? clamp(0.9 + coupling * 0.02) : clamp(coupling / 5);
  tensor[2][2] = clamp(entropy);
  tensor[3][3] = clamp(k / 7);
  tensor[4][4] = clamp(coupling / 5);
  tensor[5][5] = clamp(noise);
  tensor[6][6] = clamp(momentum * 8);

  return tensor;
}

export function runNeuroCollapseFrame(state = {}, previousState = {}) {
  const noise = clamp(state.noise ?? 0.35);
  const coupling = clamp(state.coupling ?? 1.2, 0, 5);
  const projected = projectTo49D({ ...state, noise, coupling }, previousState);
  const previousVector = previousState?.vector ? normalizeVector(previousState.vector) : null;
  const plv = computePLV(projected, previousState);
  const k = projected.k;
  const clusterSizes = estimateClusterSizes(k, coupling, noise);
  const clusterBalanceRatio = computeClusterBalanceRatio(clusterSizes);
  const entropy = k === 2 ? clamp(1 - clusterBalanceRatio) : computeClusterEntropy(clusterSizes, VECTOR_SIZE);
  const residualMass = computeResidualClusterMass(clusterSizes, VECTOR_SIZE);
  const syncRatio = clamp(plv * 0.82 + coupling / 5 * 0.28 - noise * 0.06);
  const lambda2 = computeSpectralGap(k, coupling, noise);
  const cpi = computeNetworkCPI({ plv: syncRatio, lambda2, entropy, coupling, k });
  const modularity = clamp((k - 1) / 6 + noise * 0.18 - coupling * 0.035);
  const phase = detectCollapseState({ cpi, lambda2, k, syncRatio, entropy, clusterBalanceRatio });
  const tensor = buildTensor({
    vector: projected.vector,
    phase,
    k,
    cpi,
    lambda2,
    entropy,
    coupling,
    noise,
    previousVector
  });
  const sensitivity = clamp(Math.abs(coupling - noise * 1.7) / 5 + (phase === "PRE_COLLAPSE" ? 0.28 : 0));

  return {
    vector: projected.vector,
    time: projected.time,
    metrics: { cpi, lambda2, entropy, residualMass, clusterBalanceRatio, k, modularity, syncRatio },
    tensor,
    sensitivity,
    phase
  };
}
