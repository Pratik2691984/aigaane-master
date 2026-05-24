import { runNeuroCollapseFrame } from "../../../app/core/neuro-collapse-engine.js";
import { TensorHeatmap, renderTensorHeatmap } from "./TensorHeatmap.jsx";
import { MetricTimeline, renderMetricTimeline } from "./MetricTimeline.jsx";
import { PhaseBanner, renderPhaseBanner } from "./PhaseBanner.jsx";
import { ControlsPanel } from "./ControlsPanel.jsx";
import PhaseSpaceView, {
  createPhaseSpaceState,
  destroyPhaseSpaceState,
  recordPhaseSpaceTensor,
  renderPhaseSpace,
  resetPhaseSpaceState
} from "./PhaseSpaceView.jsx";

const DEFAULT_STATE = {
  noise: 0.38,
  coupling: 1.15,
  gamma: 0.82,
  speed: 1,
  running: true
};

const EMPTY_METRICS = {
  cpi: 0,
  lambda2: 0,
  entropy: 0,
  residualMass: 0,
  clusterBalanceRatio: 0,
  k: 0,
  modularity: 0,
  syncRatio: 0
};

let mountNode = null;
let rafId = null;
let lastTick = 0;
let lastReplayTick = 0;

// Hook-shaped helpers keep this component aligned with the requested React contract
// while remaining browser-safe in this no-build app.
function useState(initialValue) {
  let value = structuredClone(initialValue);
  const setValue = update => {
    value = typeof update === "function" ? update(value) : { ...value, ...update };
    return value;
  };
  return [() => value, setValue];
}

function useRef(current = null) {
  return { current };
}

function useEffect(effect) {
  const cleanup = effect();
  return typeof cleanup === "function" ? cleanup : () => {};
}

const [getState, setState] = useState(DEFAULT_STATE);
const refs = {
  heatmap: useRef(null),
  timeline: useRef(null),
  phaseSpace: useRef(null),
  phase: useRef(null),
  controls: useRef(null),
  controlsState: useRef(structuredClone(DEFAULT_STATE)),
  engineOutput: useRef(null),
  timelineBuffer: useRef({ cpi: [], lambda2: [], entropy: [] }),
  exportFrames: useRef([]),
  replayFrames: useRef([]),
  replayState: useRef({ active: false, playing: false, index: 0, wasRunning: false }),
  phaseHistory: useRef([]),
  tensorFrameBuffer: useRef([]),
  metrics: useRef(EMPTY_METRICS),
  phaseState: useRef("NORMAL"),
  sessionSummary: useRef({ minResidualMass: 0, currentResidualMass: 0, preCollapseTime: 0, collapseCount: 0, wasCollapsed: false }),
  phaseSpaceState: useRef(createPhaseSpaceState())
};

function pushRingArray(target, value, limit = 120) {
  target.push(value);
  if (target.length > limit) {
    target.splice(0, target.length - limit);
  }
}

function pushMetricHistory(metrics) {
  pushRingArray(refs.timelineBuffer.current.cpi, metrics.cpi);
  pushRingArray(refs.timelineBuffer.current.lambda2, metrics.lambda2);
  pushRingArray(refs.timelineBuffer.current.entropy, metrics.entropy);
}

function pushExportFrame(output) {
  const { metrics, phase, time } = output;
  pushRingArray(refs.exportFrames.current, {
    t: time,
    phase,
    cpi: metrics.cpi,
    lambda2: metrics.lambda2,
    entropy: metrics.entropy,
    residualMass: metrics.residualMass,
    syncRatio: metrics.syncRatio,
    clusterBalanceRatio: metrics.clusterBalanceRatio,
    k: metrics.k,
    modularity: metrics.modularity
  }, 5000);
}

function pushReplayFrame(output, phaseSpaceIndex) {
  pushRingArray(refs.replayFrames.current, {
    t: output.time,
    phase: output.phase,
    metrics: { ...output.metrics },
    tensor: output.tensor.map(row => [...row]),
    phaseSpaceIndex
  }, 1500);
  const replay = refs.replayState.current;
  if (!replay.active) {
    replay.index = refs.replayFrames.current.length - 1;
  }
}

function updateSessionSummary(metrics, phase, frameSeconds) {
  const summary = refs.sessionSummary.current;
  const residual = Number.isFinite(metrics.residualMass) ? metrics.residualMass : 0;
  summary.currentResidualMass = residual;
  summary.minResidualMass = summary.preCollapseTime || summary.collapseCount
    ? Math.min(summary.minResidualMass, residual)
    : residual;
  if (phase === "PRE_COLLAPSE") summary.preCollapseTime += frameSeconds;
  if (phase === "COLLAPSED" && !summary.wasCollapsed) summary.collapseCount += 1;
  summary.wasCollapsed = phase === "COLLAPSED";
}

function setControls(update) {
  const next = setState(update);
  refs.controlsState.current = structuredClone(next);
  return next;
}

function clearHeatmap() {
  const canvas = refs.heatmap.current;
  if (!canvas) return;
  const ctx = canvas.getContext("2d", { alpha: false });
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#03070f";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function resetRuntime() {
  refs.phaseHistory.current = [];
  refs.timelineBuffer.current = { cpi: [], lambda2: [], entropy: [] };
  refs.exportFrames.current = [];
  refs.replayFrames.current = [];
  refs.replayState.current = { active: false, playing: false, index: 0, wasRunning: false };
  refs.engineOutput.current = null;
  refs.tensorFrameBuffer.current = [];
  refs.metrics.current = EMPTY_METRICS;
  refs.phaseState.current = "NORMAL";
  refs.sessionSummary.current = { minResidualMass: 0, currentResidualMass: 0, preCollapseTime: 0, collapseCount: 0, wasCollapsed: false };
  resetPhaseSpaceState(refs.phaseSpaceState.current);
  lastTick = 0;
  lastReplayTick = 0;
}

function clampReplayIndex(index) {
  return Math.max(0, Math.min(index, refs.replayFrames.current.length - 1));
}

function syncReplayControls() {
  const root = refs.controls.current;
  if (!root) return;
  const input = root.querySelector("[data-action='replay-scrub']");
  const readout = root.querySelector(".replay-scrub b");
  const total = refs.replayFrames.current.length;
  const index = refs.replayState.current.index;
  if (input) input.value = String(index);
  if (readout) readout.textContent = `${total ? index + 1 : 0} / ${total}`;
}

function renderReplayFrame(index) {
  const frame = refs.replayFrames.current[clampReplayIndex(index)];
  if (!frame) return;
  refs.replayState.current.index = clampReplayIndex(index);
  refs.metrics.current = frame.metrics;
  refs.phaseState.current = frame.phase;
  refs.tensorFrameBuffer.current = renderTensorHeatmap(refs.heatmap.current, {
    tensor: frame.tensor,
    phase: frame.phase
  });
  renderPhaseBanner(refs.phase.current, frame.phase, frame.metrics);
  renderPhaseSpace(refs.phaseSpace.current, refs.phaseSpaceState.current, {
    replayIndex: frame.phaseSpaceIndex,
    mode: "REPLAY"
  });
  syncReplayControls();
}

function stepReplay(delta) {
  if (!refs.replayState.current.active || refs.replayFrames.current.length === 0) return;
  refs.replayState.current.playing = false;
  renderReplayFrame(refs.replayState.current.index + delta);
  updateControls();
}

function frame() {
  const state = refs.controlsState.current;
  if (!mountNode) return;

  if (refs.replayState.current.active) {
    const now = performance.now();
    if (refs.replayState.current.playing && refs.replayFrames.current.length > 0) {
      const interval = 1000 / Math.max(1, 18 * state.speed);
      if (!lastReplayTick || now - lastReplayTick >= interval) {
        const nextIndex = refs.replayState.current.index + 1;
        if (nextIndex >= refs.replayFrames.current.length) {
          refs.replayState.current.playing = false;
          updateControls();
        } else {
          renderReplayFrame(nextIndex);
        }
        lastReplayTick = now;
      }
    }
  } else if (state.running) {
    const now = performance.now();
    const interval = 1000 / (36 * state.speed);
    if (!lastTick || now - lastTick >= interval) {
      refs.engineOutput.current = runNeuroCollapseFrame(state, refs.engineOutput.current);
      refs.metrics.current = refs.engineOutput.current.metrics;
      refs.phaseState.current = refs.engineOutput.current.phase;
      const phaseSpaceIndex = recordPhaseSpaceTensor(
        refs.phaseSpaceState.current,
        {
          tensor: refs.engineOutput.current.tensor,
          phase: refs.phaseState.current,
          metrics: refs.metrics.current
        }
      );
      updateSessionSummary(refs.metrics.current, refs.phaseState.current, interval / 1000);
      pushMetricHistory(refs.metrics.current);
      pushExportFrame(refs.engineOutput.current);
      pushReplayFrame(refs.engineOutput.current, phaseSpaceIndex);
      pushRingArray(refs.phaseHistory.current, refs.phaseState.current);
      refs.tensorFrameBuffer.current = renderTensorHeatmap(refs.heatmap.current, {
        tensor: refs.engineOutput.current.tensor,
        phase: refs.phaseState.current
      });
      renderPhaseSpace(refs.phaseSpace.current, refs.phaseSpaceState.current, {
        replayIndex: phaseSpaceIndex,
        mode: "LIVE"
      });
      renderMetricTimeline(refs.timeline.current, refs.timelineBuffer.current);
      renderPhaseBanner(refs.phase.current, refs.phaseState.current, refs.metrics.current);
      lastTick = now;
    }
  }

  rafId = requestAnimationFrame(frame);
}

function updateControls() {
  if (!refs.controls.current) return;
  ControlsPanel(
    refs.controls.current,
    getState(),
    patch => {
      setControls(patch);
    },
    reset,
    toggleRunning,
    exportJson,
    exportCsv,
    {
      active: refs.replayState.current.active,
      playing: refs.replayState.current.playing,
      index: refs.replayState.current.index,
      total: refs.replayFrames.current.length
    },
    refs.sessionSummary.current,
    toggleReplay,
    scrubReplay,
    playReplay,
    pauseReplay,
    stepReplayBack,
    stepReplayForward
  );
}

function downloadBlob(filename, contents, type) {
  const blob = new Blob([contents], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function exportJson() {
  const payload = {
    timestamp: new Date().toISOString(),
    totalFrames: refs.exportFrames.current.length,
    controls: { ...refs.controlsState.current },
    frames: refs.exportFrames.current,
    replayFrames: refs.replayFrames.current
  };
  downloadBlob(
    "collapse-lab-session.json",
    JSON.stringify(payload, null, 2),
    "application/json"
  );
}

function formatCsvValue(value) {
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "";
  const text = String(value ?? "");
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function exportCsv() {
  const columns = ["t", "phase", "cpi", "lambda2", "entropy", "residualMass", "syncRatio", "clusterBalanceRatio", "k", "modularity"];
  const rows = refs.exportFrames.current.map(frame =>
    columns.map(column => formatCsvValue(frame[column])).join(",")
  );
  downloadBlob(
    "collapse-lab-session.csv",
    [columns.join(","), ...rows].join("\n"),
    "text/csv"
  );
}

function toggleReplay() {
  const replay = refs.replayState.current;
  if (replay.active) {
    const shouldResume = replay.wasRunning;
    refs.replayState.current = { active: false, playing: false, index: replay.index, wasRunning: false };
    setControls({ running: shouldResume });
    lastReplayTick = 0;
  } else {
    refs.replayState.current = {
      active: true,
      playing: false,
      index: clampReplayIndex(refs.replayFrames.current.length - 1),
      wasRunning: refs.controlsState.current.running
    };
    setControls({ running: false });
    renderReplayFrame(refs.replayState.current.index);
  }
  updateControls();
}

function scrubReplay(index) {
  if (!refs.replayState.current.active) return;
  refs.replayState.current.playing = false;
  renderReplayFrame(Number(index));
  updateControls();
}

function playReplay() {
  if (!refs.replayState.current.active || refs.replayFrames.current.length === 0) return;
  refs.replayState.current.playing = true;
  lastReplayTick = 0;
  updateControls();
}

function pauseReplay() {
  refs.replayState.current.playing = false;
  updateControls();
}

function stepReplayBack() {
  stepReplay(-1);
}

function stepReplayForward() {
  stepReplay(1);
}

function reset() {
  setControls({ ...DEFAULT_STATE, running: false });
  resetRuntime();
  clearHeatmap();
  renderPhaseSpace(refs.phaseSpace.current, refs.phaseSpaceState.current, { mode: "LIVE" });
  renderMetricTimeline(refs.timeline.current, refs.timelineBuffer.current);
  renderPhaseBanner(refs.phase.current, refs.phaseState.current, refs.metrics.current);
  updateControls();
}

function toggleRunning() {
  const state = refs.controlsState.current;
  setControls({ running: !state.running });
  updateControls();
}

export function CollapseLab(node) {
  mountNode = node;
  mountNode.innerHTML = `
    <div class="collapse-lab">
      <div class="collapse-shell">
        <div data-phase-slot></div>
        <div class="collapse-grid">
          <div class="collapse-main">
            <div data-heatmap-slot></div>
            <div data-phase-space-slot></div>
          </div>
          <div class="collapse-side">
            <div data-controls-slot></div>
            <div data-timeline-slot></div>
          </div>
        </div>
      </div>
    </div>
  `;

  refs.phase.current = PhaseBanner(mountNode.querySelector("[data-phase-slot]"));
  refs.heatmap.current = TensorHeatmap(mountNode.querySelector("[data-heatmap-slot]"));
  refs.timeline.current = MetricTimeline(mountNode.querySelector("[data-timeline-slot]"));
  refs.phaseSpace.current = PhaseSpaceView(mountNode.querySelector("[data-phase-space-slot]"));
  refs.controls.current = mountNode.querySelector("[data-controls-slot]");
  resetRuntime();
  updateControls();
  renderPhaseBanner(refs.phase.current, refs.phaseState.current, refs.metrics.current);
  renderMetricTimeline(refs.timeline.current, refs.timelineBuffer.current);
  renderPhaseSpace(refs.phaseSpace.current, refs.phaseSpaceState.current, { mode: "LIVE" });
  clearHeatmap();

  return useEffect(() => {
    rafId = requestAnimationFrame(frame);
    return destroy;
  });
}

export function init(node) {
  destroy();
  setControls(DEFAULT_STATE);
  CollapseLab(node);
}

export function render() {
  if (!refs.engineOutput.current) {
    refs.engineOutput.current = runNeuroCollapseFrame(refs.controlsState.current, refs.engineOutput.current);
  }
}

export function destroy() {
  if (rafId) cancelAnimationFrame(rafId);
  rafId = null;
  destroyPhaseSpaceState(refs.phaseSpaceState.current);
  mountNode = null;
  resetRuntime();
}

export const tool = {
  init,
  render,
  destroy,
  component: CollapseLab
};
