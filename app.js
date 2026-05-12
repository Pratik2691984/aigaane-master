// C:\aigaane-master\app.js
// TIS v1.0 Orchestrator – Manifest Loader, Tool Dispatcher, Tab Manager

import { resolveResonance } from './api/resolve_resonance.js';
import { validateState } from './shared/invariant.js';
import { runTools } from './shared/tool_runner.js';

let manifest = null;
let activeToolId = null;
let currentMountNode = null;

async function loadManifest() {
  const res = await fetch('/tools/manifest.json');  // ✅ Absolute path
  manifest = await res.json();
  // ...
  
  for (const tool of manifest.tools) {
    try {
      const mod = await import(tool.path);
      tool.module = mod.tool;
      console.log(`[TIS] Loaded tool: ${tool.id}`);
    } catch (err) {
      console.warn(`[TIS] Failed to load tool ${tool.id}:`, err.message);
      tool.enabled = false;
    }
  }
  
  return manifest.tools.filter(t => t.enabled !== false);
}

async function switchTab(toolId) {
  const viewport = document.getElementById('viewport');
  
  if (activeToolId) {
    const prevTool = manifest.tools.find(t => t.id === activeToolId);
    if (prevTool?.module?.destroy) {
      prevTool.module.destroy();
    }
  }
  
  activeToolId = toolId;
  const toolDef = manifest.tools.find(t => t.id === toolId);
  if (!toolDef) return;
  
  const viewRes = await fetch(`/ui/tabs/${toolId}/view.html`);  // ✅ Absolute path
  const html = await viewRes.text();
  viewport.innerHTML = html;
  
  document.getElementById('tab-style').href = `./ui/tabs/${toolId}/style.css`;
  
  await new Promise(resolve => requestAnimationFrame(resolve));
  
  currentMountNode = document.getElementById('viewport');
  if (toolDef.module?.init) {
    toolDef.module.init(currentMountNode);
  }
  
  sync();
}

async function sync() {
  const slider = document.getElementById('main-slider');
  const readout = document.getElementById('angle-readout');
  
  const angle = parseFloat(slider.value);
  readout.innerText = `${angle.toFixed(1)}°`;
  
  const state = resolveResonance(angle);
  console.log('[app.js] Resolved state:', state);
  
  validateState(state);
  
  const enabledTools = manifest.tools.filter(t => t.enabled !== false);
  await runTools(state, enabledTools);
}

document.body.addEventListener('click', () => {
  if (!window.audioUnlocked) {
    window.audioUnlocked = true;
    console.log('[Audio] Unlocked by user gesture');
  }
});

document.getElementById('main-slider').oninput = sync;

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const tabName = e.target.dataset.tab;
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    switchTab(tabName);
  });
});

async function init() {
  await loadManifest();
  await switchTab('astronomy');
  sync();
}

init().catch(console.error);

window.switchTab = switchTab;