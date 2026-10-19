// Sanskrit-only Runtime Loader — Manifest + Tab Mount

let manifest = { tools: [] };
let activeToolId = null;
let currentMountNode = null;
let manifestLoaded = false;
let queuedToolId = null;

async function importToolModule(path) {
if (path.endsWith('.html')) {
    return {};
  }

  if (path.endsWith('.jsx')) {
    const blobUrls = [];
    try {
      return await import(await bundleJsxModule(path, new Map(), blobUrls));
    } finally {
      blobUrls.forEach(url => URL.revokeObjectURL(url));
    }
  }

  try {
    return await import(path);
  } catch (err) {
    throw err;
  }
}

function getToolModulePath(tool) {
  if (tool.controller) return tool.controller;

  if (tool.path?.endsWith(".html")) {
    return tool.path.replace(/\/[^/]+\.html$/, "/controller.js");
  }

  return tool.path;
}

async function loadManifest() {
  try {
    const response = await fetch("/tools/manifest.json");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    manifest = await response.json();
    console.log("[App] Manifest loaded:", manifest);
  } catch (error) {
    console.error("[App] Failed to load manifest:", error);
    manifest = {
      version: "1.0",
      tools: [
        {
          id: "sanskrit",
          path: "/tools/sanskrit.tool.js",
          type: "ui",
          enabled: true,
        },
      ],
    };
  }

  for (const tool of manifest.tools || []) {
    try {
const modulePath = tool.path?.endsWith('.html')
        ? tool.path.replace(/\/[^/]+\.html$/, '/controller.js')
        : tool.path;
      const mod = await importToolModule(modulePath);
      tool.rawModule = mod;
      tool.module = mod.tool || mod;
      console.log(`[TIS] Loaded tool: ${tool.id}`);
    } catch (err) {
      console.warn(`[TIS] Failed to load tool ${tool.id}:`, err.message);
      tool.loadError = err;
      if (!tool.component) tool.enabled = false;
    }
  }

  manifestLoaded = true;
  return (manifest.tools || []).filter((tool) => tool.enabled !== false);
}

function isComponentTab(toolDef) {
  return Boolean(toolDef.component || toolDef.module?.component);
}

function resolveComponentMount(toolDef) {
  if (!toolDef) return null;
  if (toolDef.module?.component) return toolDef.module.component;
  if (toolDef.component && toolDef.rawModule?.[toolDef.component]) {
    return toolDef.rawModule[toolDef.component];
  }
  return null;
}

async function ensureToolModule(toolDef) {
  if (toolDef.module || !toolDef.path) return;
  const modulePath = toolDef.path.endsWith('.html')
    ? toolDef.path.replace(/\/[^/]+\.html$/, '/controller.js')
    : toolDef.path;
  const mod = await importToolModule(modulePath);
  toolDef.rawModule = mod;
  toolDef.module = mod.tool || mod;
  toolDef.loadError = null;
}

function getTabLoadErrorMessage(toolId) {
  if (toolId === 'collapse-lab') {
    return 'Collapse Lab failed to load. Check console for module path/transpile errors.';
  }
  return `Failed to load ${toolId} tab. Please refresh.`;
}

async function switchTab(toolId) {
  if (!manifestLoaded) {
    queuedToolId = toolId;
    return;
  }

  const viewport = document.getElementById("viewport");

  if (!viewport) {
    console.error("[App] Viewport not found");
    return;
  }

  if (activeToolId) {
    const previousTool = manifest.tools.find((tool) => tool.id === activeToolId);

    if (previousTool?.module?.destroy) {
      try {
        previousTool.module.destroy();
      } catch (error) {
        console.warn(`[App] Error destroying ${activeToolId}:`, error);
      }
    }
  }

  const toolDef =
    manifest.tools.find((tool) => tool.id === toolId && tool.enabled !== false) ||
    manifest.tools.find((tool) => tool.id === "sanskrit" && tool.enabled !== false);

  if (!toolDef) {
    viewport.innerHTML = '<div class="error">Sanskrit tool not found in manifest.</div>';
    console.error("[App] Sanskrit tool not found in manifest");
    return;
  }

  activeToolId = toolDef.id;

  try {
await ensureToolModule(toolDef);

    if (toolDef.view) {
      const viewRes = await fetch(toolDef.view);
      if (!viewRes.ok) throw new Error(`HTTP ${viewRes.status}: ${viewRes.statusText}`);
      viewport.innerHTML = await viewRes.text();
    } else if (toolDef.path?.endsWith('.html')) {
      const viewRes = await fetch(toolDef.path);
      if (!viewRes.ok) throw new Error(`HTTP ${viewRes.status}: ${viewRes.statusText}`);
      viewport.innerHTML = await viewRes.text();
    } else if (isComponentTab(toolDef)) {
      viewport.innerHTML = '<div data-component-mount></div>';
    } else {
      console.warn(`[App] Tool ${toolDef.id} has no init() export`);
    }

    document.querySelectorAll(".nav-btn").forEach((button) => {
      button.classList.toggle("active", button.dataset.tab === toolDef.id);
    });

await new Promise(resolve => requestAnimationFrame(resolve));

    currentMountNode = isComponentTab(toolDef)
      ? viewport.querySelector('[data-component-mount]') || viewport
      : viewport;

    if (toolDef.module?.init) {
      await toolDef.module.init(currentMountNode);
    } else {
      const mountComponent = resolveComponentMount(toolDef);
      if (mountComponent) {
        await mountComponent(currentMountNode);
      }
    }

    sync();
    console.log(`[App] Switched to tab: ${toolId}`);
  } catch (err) {
    console.error(`[App] Failed to load tab ${toolId}:`, err);
    viewport.innerHTML = `<div class="error">${getTabLoadErrorMessage(toolId)}</div>`;
  }
}

function attachNavigation() {
  document.querySelectorAll(".nav-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const tabName = button.dataset.tab || "sanskrit";
      switchTab(tabName);
    });
  });
}

async function init() {
  console.log("[App] Initializing Sanskrit-only runtime...");

  attachNavigation();
  await loadManifest();

  const defaultTab =
    queuedToolId ||
    document.querySelector(".nav-btn.active")?.dataset?.tab ||
    manifest.tools.find((tool) => tool.enabled !== false)?.id ||
    "sanskrit";

  await switchTab(defaultTab);
}

init().catch((error) => {
  console.error("[App] Fatal initialization error:", error);

  const viewport = document.getElementById("viewport");
  if (viewport) {
    viewport.innerHTML = '<div class="error">Failed to initialize Sanskrit engine.</div>';
  }
});

window.switchTab = switchTab;
window.getManifest = () => manifest;
window.sync = sync;
window.importToolModule = importToolModule;
