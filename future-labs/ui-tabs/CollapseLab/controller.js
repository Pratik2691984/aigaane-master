const COLLAPSE_LAB_MODULE = new URL("./CollapseLab.jsx", import.meta.url).href;

let activeModule = null;

async function loadCollapseLabModule() {
  if (activeModule) return activeModule;

  if (typeof window.importToolModule === "function") {
    activeModule = await window.importToolModule(COLLAPSE_LAB_MODULE);
    return activeModule;
  }

  throw new Error("Collapse Lab module loader is unavailable.");
}

export async function init(node) {
  const mod = await loadCollapseLabModule();
  const tool = mod.tool || mod;
  const mount = node.querySelector("[data-collapse-lab-wrapper]") || node;

  if (tool.init) {
    await tool.init(mount);
    return;
  }

  if (tool.component) {
    await tool.component(mount);
    return;
  }

  if (mod.CollapseLab) {
    await mod.CollapseLab(mount);
    return;
  }

  throw new Error("Collapse Lab module did not expose an init or component entry.");
}

export function render(state) {
  const tool = activeModule?.tool || activeModule;
  if (tool?.render) tool.render(state);
}

export function destroy() {
  const tool = activeModule?.tool || activeModule;
  if (tool?.destroy) tool.destroy();
}

export const tool = {
  init,
  render,
  destroy
};
