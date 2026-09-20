const MAX_POINTS = 1500;
const PHASE_NORMAL = 0;
const PHASE_PRE_COLLAPSE = 1;
const PHASE_COLLAPSED = 2;

const canvasContexts = new WeakMap();

function getCanvasContext(canvas) {
  if (!canvasContexts.has(canvas)) {
    canvasContexts.set(canvas, canvas.getContext("2d", { alpha: false }));
  }
  return canvasContexts.get(canvas);
}

function phaseCode(phase) {
  if (phase === "COLLAPSED") return PHASE_COLLAPSED;
  if (phase === "PRE_COLLAPSE") return PHASE_PRE_COLLAPSE;
  return PHASE_NORMAL;
}

function phaseColor(code, alpha = 1) {
  if (code === PHASE_COLLAPSED) return `rgba(57, 255, 140, ${alpha})`;
  if (code === PHASE_PRE_COLLAPSE) return `rgba(255, 177, 95, ${alpha})`;
  return `rgba(132, 126, 255, ${alpha})`;
}

function chronologicalIndex(state, offset) {
  const start = state.count === MAX_POINTS ? state.writeIndex : 0;
  return (start + offset) % MAX_POINTS;
}

function projectMetrics(metrics, output) {
  const cpi = Number.isFinite(metrics?.cpi) ? metrics.cpi : 0;
  const lambda2 = Number.isFinite(metrics?.lambda2) ? metrics.lambda2 : 0;
  output[0] = Math.max(0, Math.min(1, cpi));
  output[1] = Math.max(0, Math.min(1, Math.tanh(lambda2 * 80)));
}

function mapPoint(state, ringIndex, width, height, out) {
  const pad = 22;
  out[0] = pad + state.points[ringIndex * 2] * (width - pad * 2);
  out[1] = pad + (1 - state.points[ringIndex * 2 + 1]) * (height - pad * 2);
}

function drawOrbitPersistence(ctx, state, width, height) {
  if (state.count < 64) return;
  const newest = chronologicalIndex(state, state.count - 1);
  const newestX = state.points[newest * 2];
  const newestY = state.points[newest * 2 + 1];
  ctx.strokeStyle = "rgba(114, 242, 255, 0.12)";
  ctx.lineWidth = 1;

  for (let i = Math.max(0, state.count - 360); i < state.count - 36; i += 16) {
    const index = chronologicalIndex(state, i);
    const dx = newestX - state.points[index * 2];
    const dy = newestY - state.points[index * 2 + 1];
    if (dx * dx + dy * dy < 0.0012) {
      mapPoint(state, index, width, height, state.scratchA);
      ctx.beginPath();
      ctx.arc(state.scratchA[0], state.scratchA[1], 9, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
}

export function createPhaseSpaceState() {
  return {
    points: new Float32Array(MAX_POINTS * 2),
    phases: new Uint8Array(MAX_POINTS),
    projection: new Float32Array(2),
    scratchA: new Float32Array(2),
    scratchB: new Float32Array(2),
    count: 0,
    writeIndex: 0,
    cursorIndex: -1,
    rafId: 0
  };
}

export function resetPhaseSpaceState(state) {
  if (state.rafId) cancelAnimationFrame(state.rafId);
  state.points.fill(0);
  state.phases.fill(0);
  state.projection.fill(0);
  state.scratchA.fill(0);
  state.scratchB.fill(0);
  state.count = 0;
  state.writeIndex = 0;
  state.cursorIndex = -1;
  state.rafId = 0;
}

export function destroyPhaseSpaceState(state) {
  if (!state) return;
  if (state.rafId) cancelAnimationFrame(state.rafId);
  state.rafId = 0;
}

export function recordPhaseSpaceTensor(state, { phase, metrics }) {
  projectMetrics(metrics, state.projection);

  const ringIndex = state.writeIndex;
  state.points[ringIndex * 2] = state.projection[0];
  state.points[ringIndex * 2 + 1] = state.projection[1];
  state.phases[ringIndex] = phaseCode(phase);
  state.cursorIndex = ringIndex;
  state.writeIndex = (state.writeIndex + 1) % MAX_POINTS;
  state.count = Math.min(MAX_POINTS, state.count + 1);
  return ringIndex;
}

export function renderPhaseSpace(canvas, state, { replayIndex = null, mode = "LIVE" } = {}) {
  if (!canvas || !state) return;
  const ctx = getCanvasContext(canvas);
  const rect = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  const width = Math.max(320, Math.floor(rect.width || 520));
  const height = 260;

  if (canvas.width !== width * scale || canvas.height !== height * scale) {
    canvas.width = width * scale;
    canvas.height = height * scale;
  }

  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#03070f";
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = "rgba(114, 242, 255, 0.09)";
  ctx.lineWidth = 1;
  for (let i = 1; i < 4; i++) {
    const x = (width / 4) * i;
    const y = (height / 4) * i;
    ctx.beginPath();
    ctx.moveTo(x, 18);
    ctx.lineTo(x, height - 18);
    ctx.moveTo(18, y);
    ctx.lineTo(width - 18, y);
    ctx.stroke();
  }

  ctx.fillStyle = "rgba(169, 189, 202, 0.72)";
  ctx.font = "11px Consolas, monospace";
  ctx.fillText("CPI", width - 42, height - 10);
  ctx.save();
  ctx.translate(12, 48);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("lambda2", 0, 0);
  ctx.restore();

  if (state.count < 2) {
    ctx.fillStyle = "rgba(169, 189, 202, 0.7)";
    ctx.font = "12px Consolas, monospace";
    ctx.fillText("Waiting for trajectory", 24, 32);
    return;
  }

  drawOrbitPersistence(ctx, state, width, height);

  for (let i = 1; i < state.count; i++) {
    const previous = chronologicalIndex(state, i - 1);
    const current = chronologicalIndex(state, i);
    mapPoint(state, previous, width, height, state.scratchA);
    mapPoint(state, current, width, height, state.scratchB);
    ctx.strokeStyle = phaseColor(state.phases[current], 0.07 + (i / state.count) * 0.48);
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.moveTo(state.scratchA[0], state.scratchA[1]);
    ctx.lineTo(state.scratchB[0], state.scratchB[1]);
    ctx.stroke();
  }

  const cursor = mode === "REPLAY" && replayIndex !== null
    ? replayIndex
    : state.cursorIndex;
  if (cursor < 0) return;

  mapPoint(state, cursor, width, height, state.scratchA);
  ctx.shadowColor = phaseColor(state.phases[cursor], 0.95);
  ctx.shadowBlur = mode === "REPLAY" ? 22 : 16;
  ctx.fillStyle = phaseColor(state.phases[cursor], 0.95);
  ctx.beginPath();
  ctx.arc(state.scratchA[0], state.scratchA[1], mode === "REPLAY" ? 6.5 : 5.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
}

export default function PhaseSpaceView(root) {
  root.innerHTML = `
    <section class="collapse-card phase-space-panel">
      <div class="collapse-card-header compact">
        <div>
          <h3>Phase Space</h3>
          <p>CPI-lambda2 topology trace</p>
        </div>
        <div class="phase-space-key">
          <span style="--phase-color:#847eff">Normal</span>
          <span style="--phase-color:#ffb15f">Pre-collapse</span>
          <span style="--phase-color:#39ff8c">Collapsed</span>
        </div>
      </div>
      <canvas class="phase-space-canvas" aria-label="Phase space trajectory"></canvas>
    </section>
  `;
  return root.querySelector("canvas");
}
