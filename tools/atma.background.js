let lastCount = 0;

export const tool = {
  id: "atma_background",
  type: "background",
  run() {
    let logs = [];
    try {
      logs = JSON.parse(localStorage.getItem("atma_logs") || "[]");
    } catch {
      logs = [];
    }

    if (logs.length > lastCount) {
      const latest = logs[logs.length - 1];
      console.log(`[Atma] ${logs.length} logged actions. Last conflict: ${latest.conflict}`);
      lastCount = logs.length;
    }
  },
  destroy() {}
};
