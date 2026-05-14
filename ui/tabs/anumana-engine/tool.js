import { getMoonState } from '/app/core/lunar-engine.js';
import { getNakshatraProfile } from '/app/core/nakshatra-engine.js';
import { computeAnumana } from '/app/core/anumana-engine.js';
import { toFlowOutput } from '/app/core/translator.js';
import { renderMathCard } from './components/cards/math-card.js';
import { renderActionCard } from './components/cards/action-card.js';
import { renderInsightCard } from './components/cards/insight-card.js';
import { renderPredictiveCard } from './components/cards/predictive-card.js';
import { simulateFuture, getPredictiveAlerts } from '/app/core/predictive.js';

let updateInterval = null;
let mountNode = null;
let previousA = null;
let userBirthVector = null;
let selectedAxis = 1;          // default Axis 1 (Stability)

// Load balanced baseline config
async function loadBalancedBaseline() {
  try {
    const res = await fetch('/config/balanced_state.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const config = await res.json();
    console.log('[Anumana] Loaded balanced baseline config:', config);
    userBirthVector = generateBirthVectorFromConfig(config);
  } catch (err) {
    console.warn('[Anumana] Could not load balanced_state.json, using no personalisation:', err);
    userBirthVector = null;
  }
}

function generateBirthVectorFromConfig(config) {
  const birthVec = new Array(49).fill(0.5);
  const axisIdx = config.primary_axis !== undefined ? config.primary_axis : 1;
  const emphasis = config.coherence !== undefined ? config.coherence : 1.0;
  for (let layer = 0; layer < 7; layer++) {
    const idx = layer * 7 + axisIdx;
    birthVec[idx] = 0.9 * emphasis;
  }
  const floor = config.resonance_floor !== undefined ? config.resonance_floor : 0.011;
  for (let i = 0; i < 49; i++) {
    birthVec[i] = Math.max(birthVec[i], floor);
  }
  return birthVec;
}

loadBalancedBaseline();

function updateElement(container, renderFn, data) {
  if (!container) return;
  try {
    const newElement = renderFn(data);
    if (container.firstChild) {
      container.replaceChild(newElement, container.firstChild);
    } else {
      container.appendChild(newElement);
    }
  } catch (err) {
    console.error('Render error:', err);
    container.innerHTML = '<div class="glass-card" style="color:#f87171;">⚠️ Render failed</div>';
  }
}

function renderAll(profile, engine, flow, alerts) {
  const mathDiv = document.getElementById('anumana-math');
  const actionDiv = document.getElementById('anumana-action');
  const insightDiv = document.getElementById('anumana-insight');
  const predictiveDiv = document.getElementById('anumana-predictive');
  if (!mathDiv || !actionDiv || !insightDiv || !predictiveDiv) return;

  if (!engine || !engine.S) {
    updateElement(insightDiv, () => {
      const errorCard = document.createElement('div');
      errorCard.className = 'glass-card';
      errorCard.style.borderLeft = '4px solid #f87171';
      errorCard.innerHTML = `<h3>⚠️ Engine Error</h3><p>Unable to compute Anumāna.</p>`;
      return errorCard;
    }, null);
    return;
  }

  updateElement(mathDiv, renderMathCard, engine.S);
  updateElement(actionDiv, renderActionCard, flow);
  updateElement(insightDiv, renderInsightCard, { nakshatra: profile.name, pada: profile.pada, engine });
  updateElement(predictiveDiv, renderPredictiveCard, alerts);
}

function update() {
  try {
    const moon = getMoonState();
    const profile = getNakshatraProfile(moon.nakshatraIndex, moon.pada);

    // Emphasise selected axis in S_base
    const modifiedS_base = profile.S_base.map((val, idx) => {
      const axis = idx % 7;
      return axis === selectedAxis ? Math.min(1.0, val * 1.2) : val;
    });

    const engine = computeAnumana({
      S_base: modifiedS_base,
      theta: moon.theta,
      A_prev: previousA,
      S_birth: userBirthVector
    });

    if (!engine) throw new Error('computeAnumana returned undefined');
    previousA = engine.A_next;

    const flow = toFlowOutput(engine);
    flow.coherence = engine.coherence;
    flow.intensity = engine.intensity;
    flow.confidence = engine.confidence;

    const forecast = simulateFuture(engine, profile, 30);
    const alerts = getPredictiveAlerts(forecast, moon.theta);

    renderAll(profile, engine, flow, alerts);
  } catch (err) {
    console.error('[Anumana] Update failed:', err);
    const insightDiv = document.getElementById('anumana-insight');
    if (insightDiv) {
      const errorCard = document.createElement('div');
      errorCard.className = 'glass-card';
      errorCard.style.borderLeft = '4px solid #f87171';
      errorCard.innerHTML = `<h3>⚠️ Recalibrating</h3><p>Low resonance stability detected.</p>`;
      insightDiv.innerHTML = '';
      insightDiv.appendChild(errorCard);
    }
  }
}

// Switch axis and force re‑render
function setAxis(axis) {
  selectedAxis = axis;
  console.log(`[Anumana] Axis switched to ${axis}`);
  // Update active class on buttons (if they exist)
  document.querySelectorAll('.axis-btn').forEach(btn => {
    const val = parseInt(btn.dataset.axis, 10);
    btn.classList.toggle('active', val === axis);
  });
  update(); // immediate re‑compute
}

export const tool = {
  init(node) {
    mountNode = node;
    if (!mountNode) return;
    mountNode.innerHTML = '';

    mountNode.innerHTML = `
      <div class="anumana-container">
        <div class="anumana-toolbar">
          <button id="anumana-mode-academic" class="mode-btn active">📐 Academic</button>
          <button id="anumana-mode-intuitive" class="mode-btn">🧘 Intuitive</button>
        </div>
        <!-- Axis selector -->
        <div class="axis-selector">
          ${[1,2,3,4,5,6,7].map(ax => `
            <button class="axis-btn ${ax === selectedAxis ? 'active' : ''}" data-axis="${ax}">Axis ${ax}</button>
          `).join('')}
        </div>
        <div id="anumana-math" class="anumana-math"></div>
        <div id="anumana-action" class="anumana-action"></div>
        <div id="anumana-insight" class="anumana-insight"></div>
        <div id="anumana-predictive" class="anumana-predictive"></div>
      </div>
    `;

    // Attach CSS link
    const link = document.getElementById('tab-style');
    if (link) link.href = '/ui/tabs/anumana-engine/style.css';

    // ========== EVENT DELEGATION (Fixes Axis clicks) ==========
    // Listen on the whole mountNode – catches clicks even if DOM re-renders
    mountNode.addEventListener('click', (e) => {
      // Axis button click
      const axisBtn = e.target.closest('.axis-btn');
      if (axisBtn) {
        const axis = parseInt(axisBtn.dataset.axis, 10);
        setAxis(axis);
        return;
      }
      
      // Mode toggle click (Academic/Intuitive)
      const modeBtn = e.target.closest('.mode-btn');
      if (modeBtn) {
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        modeBtn.classList.add('active');
        const mathDiv = document.getElementById('anumana-math');
        const actionDiv = document.getElementById('anumana-action');
        const insightDiv = document.getElementById('anumana-insight');
        const predictiveDiv = document.getElementById('anumana-predictive');
        if (mathDiv && actionDiv && insightDiv && predictiveDiv) {
          const isIntuitive = modeBtn.id.includes('intuitive');
          mathDiv.style.display = isIntuitive ? 'none' : 'block';
          actionDiv.style.display = 'block';
          insightDiv.style.display = 'block';
          predictiveDiv.style.display = 'block';
        }
      }
    });

    // Initial update
    update();
    updateInterval = setInterval(update, 2000);
  },

  destroy() {
    if (updateInterval) clearInterval(updateInterval);
    if (mountNode) mountNode.innerHTML = '';
    mountNode = null;
    previousA = null;
  }
};

if (typeof window !== 'undefined') window.tool = tool;