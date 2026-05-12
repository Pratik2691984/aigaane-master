// C:\aigaane-master\tools\astronomy.tool.js

import { init, render, destroy } from '../ui/tabs/astronomy/controller.js';

let mountNode = null;

export const tool = {
  id: "astronomy",
  type: "ui",
  subscriptions: ["pada_id", "nakshatra_id"],
  timeout: 10,
  
  run(state) {
    if (!mountNode) return;
    render(state, mountNode);
  },
  
  init(node) {
    mountNode = node;
    init(mountNode);
  },
  
  destroy() {
    destroy();
    mountNode = null;
  }
};