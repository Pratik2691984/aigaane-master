// Anumāna Engine Tool – conforms to TIS spec (init/destroy)
import { getMoonState } from './core/lunar-engine.js';
import { getNakshatraProfile } from './core/nakshatra-engine.js';
import { computeAnumana } from './core/anumana-engine.js';
import { toFlowOutput } from './core/translator.js';
import { renderMathCard } from './components/cards/math-card.js';
import { renderActionCard } from './components/cards/action-card.js';
import { renderInsightCard } from './components/cards/insight-card.js';

let updateInterval = null;
let mountNode = null;

function renderAll(data) {
  const { vector49, nakshatra, pada } = data;

  const mathDiv = document.getElementById('anumana-math');
  const actionDiv = document.getElementById('anumana-action');
  const insightDiv = document.getElementById('anumana-insight');

  if (!mathDiv || !actionDiv || !insightDiv) return;

  mathDiv.innerHTML = '';
  actionDiv.innerHTML = '';
  insightDiv.innerHTML = '';

  mathDiv.appendChild(renderMathCard(vector49));
  actionDiv.appendChild(renderActionCard(vector49));
  insightDiv.appendChild(renderInsightCard(nakshatra, pada, vector49));
}

function update() {
  const moon = getMoonState();
  const profile = getNakshatraProfile(moon.nakshatraIndex, moon.pada);
  const engine = computeAnumana({
    S_base: profile.S_base,
    theta: moon.theta
  });
  const flow = toFlowOutput(engine);

  renderAll({
    vector49: engine.S,
    nakshatra: profile.name,
    pada: profile.pada,
    engine: engine,
    flow: flow
  });
}

export const tool = {
  init(node) {
    mountNode = node;
    if (!mountNode) return;

    // Inject the required HTML structure
    mountNode.innerHTML = `
      <div class="anumana-container">
        <div class="anumana-toolbar">
          <button id="anumana-mode-academic" class="mode-btn active">📐 Academic</button>
          <button id="anumana-mode-intuitive" class="mode-btn">🧘 Intuitive</button>
        </div>
        <div id="anumana-math" class="anumana-math"></div>
        <div id="anumana-action" class="anumana-action"></div>
        <div id="anumana-insight" class="anumana-insight"></div>
      </div>
    `;

    // Load the theme CSS dynamically (if not already loaded)
    const link = document.getElementById('tab-style');
    if (link) link.href = '/ui/tabs/anumana-engine/style.css';

    // Mode switching
    const academicBtn = document.getElementById('anumana-mode-academic');
    const intuitiveBtn = document.getElementById('anumana-mode-intuitive');
    const mathDiv = document.getElementById('anumana-math');
    const actionDiv = document.getElementById('anumana-action');

    academicBtn.addEventListener('click', () => {
      academicBtn.classList.add('active');
      intuitiveBtn.classList.remove('active');
      mathDiv.style.display = 'block';
      actionDiv.style.display = 'block';
      // Optionally adjust insight layout
    });

    intuitiveBtn.addEventListener('click', () => {
      intuitiveBtn.classList.add('active');
      academicBtn.classList.remove('active');
      mathDiv.style.display = 'none';   // hide raw grid in intuitive mode
      actionDiv.style.display = 'block';
    });

    // Start live updates
    update();
    updateInterval = setInterval(update, 2000);
  },

  destroy() {
    if (updateInterval) {
      clearInterval(updateInterval);
      updateInterval = null;
    }
    if (mountNode) mountNode.innerHTML = '';
    mountNode = null;
  }
};

// Auto‑register for TIS (global expected)
if (typeof window !== 'undefined') {
  window.tool = tool;
}