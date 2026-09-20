export async function loadRuntimeRegistry(path = "runtime/registry/active-tabs.json") {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(`Runtime registry unavailable: HTTP ${response.status}`);
  }

  const registry = await response.json();

  if (!registry || !Array.isArray(registry.activeTabs)) {
    throw new Error("Runtime registry invalid: activeTabs missing");
  }

  return registry;
}