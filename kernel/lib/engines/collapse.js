export const COLLAPSE_THRESHOLDS = Object.freeze({
  lambdaConnected: 1e-4,
  cpiPre: 0.85,
  syncPre: 0.9,
  entropyPre: 0.25,
  balancePre: 0.35
});

function clamp01(x) {
  return Math.max(0, Math.min(1, x));
}

function mean(arr) {
  let s = 0;
  for (const v of arr) s += v;
  return s / arr.length;
}

export function laplacianLambda2(vec) {
  const n = 7;
  const A = Array.from({ length: n }, () => new Float64Array(n));
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const wi = mean(vec.slice(i * 7, i * 7 + 7));
      const wj = mean(vec.slice(j * 7, j * 7 + 7));
      const w = 1 - Math.abs(wi - wj);
      A[i][j] = A[j][i] = w;
    }
  }
  const D = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    let s = 0;
    for (let j = 0; j < n; j++) s += A[i][j];
    D[i] = s;
  }
  const x = new Float64Array(n);
  let sx = 0;
  for (let i = 0; i < n; i++) {
    x[i] = mean(vec.slice(i * 7, i * 7 + 7)) - 0.5;
    sx += x[i];
  }
  const mu = sx / n;
  let num = 0;
  let den = 0;
  for (let i = 0; i < n; i++) {
    const yi = x[i] - mu;
    den += yi * yi;
    let Lyi = D[i] * yi;
    for (let j = 0; j < n; j++) Lyi -= A[i][j] * (x[j] - mu);
    num += yi * Lyi;
  }
  if (den < 1e-12) return 1e-5;
  return Math.max(0, num / den);
}

export function evaluateCollapse(vec, prev = null) {
  const lambda2 = laplacianLambda2(vec);
  let plv = 1;
  if (prev) {
    let re = 0;
    let im = 0;
    for (let i = 0; i < 49; i++) {
      const d = (vec[i] - prev[i]) * Math.PI * 2;
      re += Math.cos(d);
      im += Math.sin(d);
    }
    plv = Math.sqrt(re * re + im * im) / 49;
  }
  const energy = mean(vec.slice(28, 35));
  const sattva = vec[21];
  const entropy = clamp01(1 - sattva);
  const k = lambda2 <= COLLAPSE_THRESHOLDS.lambdaConnected ? 2 : energy > 0.85 ? 1 : 3;
  const cpi = clamp01(0.22 + plv * 0.36 + sattva * 0.3 + (k === 2 ? 0.22 : 0));
  const clusterBalanceRatio = k === 2 ? 0.5 : 0;
  let phase = "NORMAL";
  if (k === 1 && lambda2 > COLLAPSE_THRESHOLDS.lambdaConnected) phase = "COLLAPSED";
  if (
    k === 2 &&
    lambda2 <= COLLAPSE_THRESHOLDS.lambdaConnected &&
    cpi >= COLLAPSE_THRESHOLDS.cpiPre &&
    plv >= COLLAPSE_THRESHOLDS.syncPre &&
    entropy <= COLLAPSE_THRESHOLDS.entropyPre &&
    clusterBalanceRatio >= COLLAPSE_THRESHOLDS.balancePre
  ) {
    phase = "PRE_COLLAPSE";
  }
  return { k, lambda2, cpi, syncRatio: plv, entropy, clusterBalanceRatio, phase };
}
