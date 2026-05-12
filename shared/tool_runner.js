// C:\aigaane-master\shared\tool_runner.js
// TIS v1.0 Execution Firewall – Diff, Filter, Clone, Freeze, Timeout

let prevState = null;

function getNested(obj, path) {
  return path.split('.').reduce((o, k) => o?.[k], obj);
}

function setNested(obj, path, value) {
  const keys = path.split('.');
  let curr = obj;
  keys.forEach((key, i) => {
    if (i === keys.length - 1) {
      curr[key] = value;
    } else {
      curr[key] = curr[key] || {};
      curr = curr[key];
    }
  });
}

export async function runTools(currentState, tools) {
  if (prevState === null) {
    prevState = {};
  }
  
  console.log('[tool_runner] Running tools with state:', currentState);
  
  for (const toolDef of tools) {
    const tool = toolDef.module;
    if (!tool) {
      console.warn(`[tool_runner] No module for tool ${toolDef.id}`);
      continue;
    }
    
    const hasChanged = toolDef.subscriptions.some(path => {
      const prev = getNested(prevState, path);
      const curr = getNested(currentState, path);
      return prev !== curr;
    });
    
    if (!hasChanged && !toolDef.always_run) continue;
    
    const filtered = {};
    toolDef.subscriptions.forEach(path => {
      const value = getNested(currentState, path);
      setNested(filtered, path, value);
    });
    
    console.log(`[tool_runner] Tool ${toolDef.id} - filtered:`, filtered);
    
    const safeState = Object.freeze(structuredClone(filtered));
    
    try {
      await Promise.race([
        Promise.resolve().then(() => tool.run(safeState)),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error(`Tool ${toolDef.id} timeout`)), toolDef.timeout_ms || 10)
        )
      ]);
    } catch (err) {
      console.warn(`[TIS Error] ${toolDef.id}:`, err.message);
    }
  }
  
  prevState = currentState;
}