// C:\aigaane-master\app.js
// TIS v1.0 Orchestrator – Manifest Loader, Tool Dispatcher, Tab Manager
//
// API Configuration:
// - For local development, set to '' (empty string) or 'http://localhost:8000'
// - For production with Render backend, set to 'https://aigaane-master.onrender.com'
// - For GoDaddy frontend (no backend API used yet), keep empty (no change needed).

const API_BASE = '';  // Change to your Render URL when you add backend calls

import { resolveResonance } from '/api/resolve_resonance.js';
import { validateState } from '/shared/invariant.js';
import { runTools } from '/shared/tool_runner.js';

let manifest = null;
let activeToolId = null;
let currentMountNode = null;

async function loadManifest() {
  try {
    const res = await fetch('/tools/manifest.json');
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    manifest = await res.json();
    console.log('[TIS] Manifest loaded successfully');
  } catch (err) {
    console.error('[TIS] Failed to load manifest:', err);
    manifest = { tools: [] };
    return [];
  }
  
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
  if (!viewport) {
    console.error('[App] Viewport not found');
    return;
  }
  
  if (activeToolId) {
    const prevTool = manifest.tools.find(t => t.id === activeToolId);
    if (prevTool?.module?.destroy) {
      try {
        prevTool.module.destroy();
      } catch (err) {
        console.warn(`[App] Error destroying ${activeToolId}:`, err);
      }
    }
  }
  
  activeToolId = toolId;
  const toolDef = manifest.tools.find(t => t.id === toolId);
  if (!toolDef) {
    console.error(`[App] Tool ${toolId} not found in manifest`);
    return;
  }
  
  try {
    const viewRes = await fetch(`/ui/tabs/${toolId}/view.html`);
    if (!viewRes.ok) {
      throw new Error(`HTTP ${viewRes.status}: ${viewRes.statusText}`);
    }
    const html = await viewRes.text();
    viewport.innerHTML = html;
    
    const styleLink = document.getElementById('tab-style');
    if (styleLink) {
      styleLink.href = `/ui/tabs/${toolId}/style.css`;
    }
    
    await new Promise(resolve => requestAnimationFrame(resolve));
    
    currentMountNode = document.getElementById('viewport');
    if (toolDef.module?.init) {
      toolDef.module.init(currentMountNode);
    }
    
    sync();
    console.log(`[App] Switched to tab: ${toolId}`);
  } catch (err) {
    console.error(`[App] Failed to load tab ${toolId}:`, err);
    viewport.innerHTML = `<div class="error">Failed to load ${toolId} tab. Please refresh.</div>`;
  }
}

async function sync() {
  const slider = document.getElementById('main-slider');
  const readout = document.getElementById('angle-readout');
  
  if (!slider || !readout) return;
  
  const angle = parseFloat(slider.value);
  readout.innerText = `${angle.toFixed(1)}°`;
  
  try {
    const state = resolveResonance(angle);
    console.log('[app.js] Resolved state:', state);
    
    validateState(state);
    
    const enabledTools = manifest?.tools?.filter(t => t.enabled !== false) || [];
    await runTools(state, enabledTools);
  } catch (err) {
    console.error('[App] Sync error:', err);
  }
}

document.body.addEventListener('click', () => {
  if (!window.audioUnlocked) {
    window.audioUnlocked = true;
    console.log('[Audio] Unlocked by user gesture');
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const slider = document.getElementById('main-slider');
  if (slider) {
    slider.oninput = sync;
  }
});

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const tabName = e.target.dataset.tab;
    if (!tabName) return;
    
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    switchTab(tabName);
  });
});

async function init() {
  console.log('[App] Initializing Aigaane V3 PRO...');
  await loadManifest();
  await switchTab('astronomy');
  sync();
}

init().catch(err => {
  console.error('[App] Fatal initialization error:', err);
  const viewport = document.getElementById('viewport');
  if (viewport) {
    viewport.innerHTML = '<div class="error">Failed to initialize engine. Please refresh the page.</div>';
  }
});

window.switchTab = switchTab;
window.getManifest = () => manifest;