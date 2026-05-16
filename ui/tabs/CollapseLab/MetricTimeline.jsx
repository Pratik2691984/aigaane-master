const SERIES = [
  { key: "cpi", label: "CPI", color: "#72f2ff" },
  { key: "lambda2", label: "lambda2", shortLabel: "λ₂", color: "#39ff8c" },
  { key: "entropy", label: "Entropy", shortLabel: "H", color: "#b960ff" }
];

const canvasContexts = new WeakMap();

function getCanvasContext(canvas) {
  if (!canvasContexts.has(canvas)) {
    canvasContexts.set(canvas, canvas.getContext("2d", { alpha: false }));
  }
  return canvasContexts.get(canvas);
}

function normalizeSeries(values) {
  const samples = values.slice(-120).filter(Number.isFinite);
  if (samples.length === 0) return [];
  const min = Math.min(...samples);
  const max = Math.max(...samples);
  const range = max - min;
  if (range < 1e-12) return samples.map(() => 0.5);
  return samples.map(value => (value - min) / range);
}

function drawGrid(ctx, width, height, pad) {
  ctx.strokeStyle = "rgba(114, 242, 255, 0.11)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad + i * ((height - pad * 2) / 4);
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(width - pad, y);
    ctx.stroke();
  }
}

function drawLine(ctx, samples, color, width, height, pad) {
  if (samples.length < 2) return;
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  samples.forEach((value, index) => {
    const x = pad + (index / 119) * (width - pad * 2);
    const y = height - pad - value * (height - pad * 2);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

function drawLabels(ctx, width, pad) {
  ctx.font = "12px Consolas, monospace";
  ctx.textBaseline = "top";
  let x = pad;
  SERIES.forEach(series => {
    ctx.fillStyle = series.color;
    ctx.fillText(series.shortLabel || series.label, x, 10);
    x += ctx.measureText(series.shortLabel || series.label).width + 18;
  });
}

export function MetricTimeline(root) {
  root.innerHTML = `
    <section class="collapse-card collapse-timeline-card">
      <div class="collapse-card-header compact">
        <div>
          <h3>Metric Timeline</h3>
          <p>Last 120 frames</p>
        </div>
        <div class="metric-key">
          ${SERIES.map(item => `<span style="--line:${item.color}">${item.shortLabel || item.label}</span>`).join("")}
        </div>
      </div>
      <canvas class="collapse-timeline" aria-label="CPI, lambda2, and entropy timeline"></canvas>
    </section>
  `;
  return root.querySelector("canvas");
}

export function renderMetricTimeline(canvas, history) {
  if (!canvas || !history) return;
  const ctx = getCanvasContext(canvas);
  const rect = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  const width = Math.max(320, Math.floor(rect.width || 520));
  const height = 220;

  if (canvas.width !== width * scale || canvas.height !== height * scale) {
    canvas.width = width * scale;
    canvas.height = height * scale;
  }

  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#03070f";
  ctx.fillRect(0, 0, width, height);

  const pad = 24;
  drawGrid(ctx, width, height, pad);
  SERIES.forEach(series => {
    drawLine(ctx, normalizeSeries(history[series.key] || []), series.color, width, height, pad);
  });
  drawLabels(ctx, width, pad);
}
