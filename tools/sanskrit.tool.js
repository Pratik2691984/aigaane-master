// C:\aigaane-master\tools\sanskrit.tool.js
// UI Tool Adapter – Wraps Sanskrit Tab Controller

import { init as tabInit, render as tabRender, destroy as tabDestroy } from '../ui/tabs/sanskrit/controller.js';

let mountNode = null;

export const tool = {
  id: "sanskrit",
  type: "ui",
  subscriptions: ["phoneme_id"],
  timeout: 10,
  
  run(state) {
    if (!mountNode) return;
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