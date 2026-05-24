import { loadRuntimeRegistry } from "../loaders/registry-loader.js";

export async function bootstrapAigaaneRuntime() {
  const registry = await loadRuntimeRegistry();

  window.AIGAANE_RUNTIME_REGISTRY = registry;

  return registry;
}