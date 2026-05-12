// C:\aigaane-master\app.js
// TIS v1.0 Orchestrator – Manifest Loader, Tool Dispatcher, Tab Manager

import { resolveResonance } from './api/resolve_resonance.js';
import { validateState, deepFreeze } from './shared/invariant.js';
import { runTools } from './shared/tool_runner.js';

let manifest = null;
let activeToolId = null;
let currentMountNode = null;

async function loadManifest() {
  const res = await fetch('./tools/manifest.json');
  manifest = await res.json();
  
  // Load modules for all tools
  for (const tool of manifest.tools) {
    try {
      const mod = await import(tool.path);
      tool.module = mod.tool;
    } catch (err) {
      console.warn(`[TIS] Failed to load tool ${tool.id}:`, err.message);
      tool.enabled = false;
    }
  }
  
  return manifest.tools.filter(t => t.enabled !== false);
}

async function switchTab(toolId) {
  const viewport = document.getElementById('viewport');
  
  // Destroy previous UI tool
  if (activeToolId) {
    const prevTool = manifest.tools.find(t => t.id === activeToolId);
    if (prevTool?.module?.destroy) {
      prevTool.module.destroy();
    }
  }
  
  activeToolId = toolId;
  const toolDef = manifest.tools.find(t => t.id === toolId);
  if (!toolDef) return;
  
  // Load view.html
  const viewRes = await fetch(`./ui/tabs/${toolId}/view.html`);
  const html = await viewRes.text();
  viewport.innerHTML = html;
  
  // Load style.css
  document.getElementById('tab-style').href = `./ui/tabs/${toolId}/style.css`;
  
  // Ensure DOM is painted
  await new Promise(resolve => requestAnimationFrame(resolve));
  
  // Mount tool
  currentMountNode = document.getElementById('viewport');
  if (toolDef.module?.init) {
    toolDef.module.init(currentMountNode);
  }
  
  // Initial sync
  sync();
}

async function sync() {
  const slider = document.getElementById('main-slider');
  const readout = document.getElementById('angle-readout');
  
  const angle = parseFloat(slider.value);
  readout.innerText = `${angle.toFixed(1)}°`;
  
  // Pure resolver → canonical state
  const state = resolveResonance(angle);
  
  // Validate invariants (dev only, throws on error)
  validateState(state);
  
  // Run all enabled tools (UI + background)
  const enabledTools = manifest.tools.filter(t => t.enabled !== false);
  await runTools(state, enabledTools);
}

// Audio unlock (browser policy)
document.body.addEventListener('click', () => {
  if (!window.audioUnlocked) {
    window.audioUnlocked = true;
    console.log('[Audio] Unlocked by user gesture');
  }
});

// Slider binding
document.getElementById('main-slider').oninput = sync;

// Tab navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const tabName = e.target.dataset.tab;
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    switchTab(tabName);
  });
});

// Initialization
async function init() {
  await loadManifest();
  await switchTab('astronomy');
  sync();
}

init().catch(console.error);

window.switchTab = switchTab;