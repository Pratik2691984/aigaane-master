const CHANNELS = [
  { name: "Global Coherence", color: [57, 255, 140] },
  { name: "Boundary Tension", color: [255, 152, 48] },
  { name: "Entropy", color: [185, 96, 255] },
  { name: "Fragmentation", color: [64, 154, 255] },
  { name: "Coupling", color: [255, 74, 96] },
  { name: "Noise", color: [246, 250, 255] },
  { name: "Momentum", color: [255, 232, 77] }
];

const canvasContexts = new WeakMap();

function getCanvasContext(canvas) {
  if (!canvasContexts.has(canvas)) {
    canvasContexts.set(canvas, canvas.getContext("2d", { alpha: false }));
  }
  return canvasContexts.get(canvas);
}

function colorForCell(row, col, value, phase) {
  let channel = CHANNELS[row] || CHANNELS[0];
  if (phase === "COLLAPSED" && row === 0 && col === 0) channel = CHANNELS[0];
  if (phase === "PRE_COLLAPSE" && (row === 1 || col === 1)) channel = CHANNELS[1];
  if (phase === "NORMAL" && (row === 2 || row === 3)) channel = row === 2 ? CHANNELS[2] : CHANNELS[3];
  const [r, g, b] = channel.color;
  return `rgba(${Math.round(r * value)}, ${Math.round(g * value)}, ${Math.round(b * value)}, ${0.34 + value * 0.66})`;
}

export function renderTensorHeatmap(canvas, { tensor, phase }) {
  if (!canvas || !Array.isArray(tensor)) return [];
  const ctx = getCanvasContext(canvas);
  const rect = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  const width = Math.max(280, Math.floor(rect.width || 420));
  const height = width;

  if (canvas.width !== width * scale || canvas.height !== height * scale) {
    canvas.width = width * scale;
    canvas.height = height * scale;
  }

  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#03070f";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const rows = tensor.length;
  const cols = tensor[0]?.length || 0;
  if (!rows || !cols) return [];
  const cellWidth = canvas.width / cols;
  const cellHeight = canvas.height / rows;
  const nextGlow = [];

  for (let row = 0; row < rows; row++) {
    nextGlow[row] = [];
    for (let col = 0; col < cols; col++) {
      const raw = Number.isFinite(tensor[row]?.[col]) ? tensor[row][col] : 0;
      const value = Math.max(0, Math.min(1, raw));
      nextGlow[row][col] = value;

      const x = col * cellWidth + 1;
      const y = row * cellHeight + 1;
      const drawWidth = Math.max(0, cellWidth - 2);
      const drawHeight = Math.max(0, cellHeight - 2);
      ctx.fillStyle = colorForCell(row, col, value, phase);
      ctx.shadowColor = colorForCell(row, col, Math.min(1, value + 0.2), phase);
      ctx.shadowBlur = 12 * value;
      ctx.fillRect(x, y, drawWidth, drawHeight);
      ctx.shadowBlur = 0;
      ctx.strokeStyle = `rgba(114, 242, 255, ${0.08 + value * 0.16})`;
      ctx.lineWidth = scale;
      ctx.strokeRect(x, y, drawWidth, drawHeight);
    }
  }

  if (phase === "COLLAPSED") {
    ctx.fillStyle = `rgba(57, 255, 140, ${0.14 + Math.sin(Date.now() / 80) * 0.06})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  return nextGlow;
}

export function TensorHeatmap(root) {
  root.innerHTML = `
    <section class="collapse-card collapse-heatmap-card">
      <div class="collapse-card-header">
        <div>
          <h3>Tensor Ignition</h3>
          <p>7 x 7 neuro-collapse field</p>
        </div>
        <div class="collapse-legend">
          ${CHANNELS.map(item => `<span><i style="background: rgb(${item.color.join(",")})"></i>${item.name}</span>`).join("")}
        </div>
      </div>
      <canvas class="collapse-heatmap" aria-label="Neuro-collapse tensor heatmap"></canvas>
    </section>
  `;
  return root.querySelector("canvas");
}
