// Sanskrit-only Runtime Loader — Manifest + Tab Mount

let manifest = { tools: [] };
let activeToolId = null;
let currentMountNode = null;
let manifestLoaded = false;
let queuedToolId = null;

async function importToolModule(path) {
  return import(path);
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
      const modulePath = getToolModulePath(tool);
      if (!modulePath) continue;

      const module = await importToolModule(modulePath);
      tool.rawModule = module;
      tool.module = module.tool || module.default || module;
      console.log(`[App] Loaded tool module: ${tool.id}`);
    } catch (error) {
      console.warn(`[App] Failed to load tool ${tool.id}:`, error);
      tool.enabled = false;
    }
  }

  manifestLoaded = true;
  return (manifest.tools || []).filter((tool) => tool.enabled !== false);
}

async function switchTab(toolId = "sanskrit") {
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
    if (!toolDef.module && getToolModulePath(toolDef)) {
      const module = await importToolModule(getToolModulePath(toolDef));
      toolDef.rawModule = module;
      toolDef.module = module.tool || module.default || module;
    }

    const viewPath =
      toolDef.view ||
      (toolDef.path?.endsWith(".html") ? toolDef.path : `/ui/tabs/${toolDef.id}/view.html`);

    const viewResponse = await fetch(viewPath);

    if (!viewResponse.ok) {
      throw new Error(`Failed to fetch ${viewPath}: HTTP ${viewResponse.status}`);
    }

    viewport.innerHTML = await viewResponse.text();

    const styleLink = document.getElementById("tab-style");
    if (styleLink) {
      styleLink.href = toolDef.style || `/ui/tabs/${toolDef.id}/style.css`;
    }

    await new Promise((resolve) => requestAnimationFrame(resolve));

    currentMountNode = viewport;

    if (toolDef.module?.init) {
      toolDef.module.init(currentMountNode);
    } else {
      console.warn(`[App] Tool ${toolDef.id} has no init() export`);
    }

    document.querySelectorAll(".nav-btn").forEach((button) => {
      button.classList.toggle("active", button.dataset.tab === toolDef.id);
    });

    console.log(`[App] Switched to tab: ${toolDef.id}`);
  } catch (error) {
    console.error(`[App] Failed to load tab ${toolDef.id}:`, error);
    viewport.innerHTML = `<div class="error">Failed to load ${toolDef.id} tab. Please refresh.</div>`;
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