// C:\aigaane-master\tools\astronomy.tool.js
// UI Tool Adapter – Wraps Astronomy Tab Controller

import { init as tabInit, render as tabRender, destroy as tabDestroy } from '../ui/tabs/astronomy/controller.js';

let mountNode = null;

export const tool = {
  id: "astronomy",
  type: "ui",
  subscriptions: ["pada_id", "nakshatra_id"],
  timeout: 10,
  
  run(state) {
    if (!mountNode) return;
    // Pass filtered state to original render
    tabRender(state, mountNode);
  },
  
  init(node) {
    mountNode = node;
    tabInit(mountNode);
  },
  
  destroy() {
    tabDestroy();
    mountNode = null;
  }
};