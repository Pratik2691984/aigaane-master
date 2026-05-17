// TIS v1.0 Orchestrator – Manifest Loader, Tool Dispatcher, Tab Manager

const API_BASE = '';

import { resolveResonance } from '/lib/resolve_resonance.js';
import { validateState } from '/shared/invariant.js';
import { runTools } from '/shared/tool_runner.js';

let manifest = null;
let activeToolId = null;
let currentMountNode = null;
let manifestLoaded = false;
let queuedToolId = null;

async function importToolModule(path) {
  try {
    return await import(path);
  } catch (err) {
    if (!path.endsWith('.jsx')) throw err;
    const blobUrls = [];
    try {
      return await import(await bundleJsxModule(path, new Map(), blobUrls));
    } finally {
      blobUrls.forEach(url => URL.revokeObjectURL(url));
    }
  }
}

async function bundleJsxModule(path, cache, blobUrls) {
  if (cache.has(path)) return cache.get(path);

  const res = await fetch(path);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  let source = await res.text();
  const sourceUrl = new URL(path, window.location.origin);
  const importPattern = /from\s+["'](\.[^"']+\.(?:js|jsx))["']/g;
  const replacements = [];
  let match = importPattern.exec(source);

  while (match) {
    const relativePath = match[1];
    const absolutePath = new URL(relativePath, sourceUrl);
    const replacementUrl = absolutePath.pathname.endsWith('.jsx')
      ? await bundleJsxModule(absolutePath.href, cache, blobUrls)
      : absolutePath.href;
    replacements.push([relativePath, replacementUrl]);
    match = importPattern.exec(source);
  }

  for (const [relativePath, blobUrl] of replacements) {
    source = source.replaceAll(`from "${relativePath}"`, `from "${blobUrl}"`);
    source = source.replaceAll(`from '${relativePath}'`, `from "${blobUrl}"`);
  }

  const blobUrl = URL.createObjectURL(new Blob([source], { type: 'text/javascript' }));
  blobUrls.push(blobUrl);
  cache.set(path, blobUrl);
  return blobUrl;
}

async function loadManifest() {
  try {
    const res = await fetch('/tools/manifest.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    manifest = await res.json();
    console.log('[TIS] Manifest loaded successfully');
  } catch (err) {
    console.error('[TIS] Failed to load manifest:', err);
    manifest = { tools: [] };
    return [];
  }

  for (const tool of manifest.tools) {
    try {
      const mod = await importToolModule(tool.path);
      tool.module = mod.tool;
      console.log(`[TIS] Loaded tool: ${tool.id}`);
    } catch (err) {
      console.warn(`[TIS] Failed to load tool ${tool.id}:`, err.message);
      tool.enabled = false;
    }
  }

  manifestLoaded = true;
  return manifest.tools.filter(t => t.enabled !== false);
}

async function switchTab(toolId) {
  if (!manifestLoaded) {
    queuedToolId = toolId;
    return;
  }

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
    if (toolDef.view) {
      const viewRes = await fetch(toolDef.view);
      if (!viewRes.ok) throw new Error(`HTTP ${viewRes.status}: ${viewRes.statusText}`);
      viewport.innerHTML = await viewRes.text();
    } else if (toolDef.component || toolDef.module?.component) {
      viewport.innerHTML = '';
    } else {
      const viewRes = await fetch(`/ui/tabs/${toolId}/view.html`);
      if (!viewRes.ok) throw new Error(`HTTP ${viewRes.status}: ${viewRes.statusText}`);
      viewport.innerHTML = await viewRes.text();
    }

    const styleLink = document.getElementById('tab-style');
    if (styleLink) styleLink.href = toolDef.style || `/ui/tabs/${toolId}/style.css`;

    await new Promise(resolve => requestAnimationFrame(resolve));

    currentMountNode = document.getElementById('viewport');
    if (toolDef.module?.init) toolDef.module.init(currentMountNode);

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
    const rawState = resolveResonance(angle);
    // Clone to make it mutable (fixes "object is not extensible")
    const state = { ...rawState };

    // Now safe to add properties
    state.plugins = state.plugins || [];
    state.items = state.items || [];
    if (state.resonance === undefined) state.resonance = {};
    if (state.resonance.tools === undefined) state.resonance.tools = [];

    console.log('[app.js] Resolved state:', state);
    validateState(state);
    const enabledTools = (manifest?.tools?.filter(t => t.enabled !== false)) || [];
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
  if (slider) slider.oninput = sync;
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

window.addEventListener('sliderMoved', (e) => {
  const angle = e.detail;
  console.log('[Manual] Slider moved to', angle);
  if (typeof sync === 'function') sync();
  else {
    const state = resolveResonance(angle);
    // FIX: same safe initializers
    state.plugins = state.plugins || [];
    state.items = state.items || [];
    if (state.resonance === undefined) state.resonance = {};
    if (state.resonance.tools === undefined) state.resonance.tools = [];
    validateState(state);
    const enabledTools = manifest?.tools?.filter(t => t.enabled !== false) || [];
    runTools(state, enabledTools);
  }
});

setInterval(() => {
  const slider = document.getElementById('main-slider');
  const readout = document.getElementById('angle-readout');
  if (slider && readout) {
    const currentValue = parseFloat(slider.value);
    const displayedValue = parseFloat(readout.innerText);
    if (Math.abs(currentValue - displayedValue) > 0.1) {
      readout.innerText = currentValue.toFixed(1) + '°';
      if (typeof sync === 'function') sync();
    }
  }
}, 200);

async function init() {
  console.log('[App] Initializing Aigaane V3 PRO...');
  await loadManifest();
  await switchTab(queuedToolId || 'astronomy');
  sync();
}

init().catch(err => {
  console.error('[App] Fatal initialization error:', err);
  const viewport = document.getElementById('viewport');
  if (viewport) viewport.innerHTML = '<div class="error">Failed to initialize engine. Please refresh the page.</div>';
});

window.switchTab = switchTab;
window.getManifest = () => manifest;
window.sync = sync;
