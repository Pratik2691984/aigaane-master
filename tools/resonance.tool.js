// C:\aigaane-master\tools\resonance.tool.js

import { init, render, destroy } from '../ui/tabs/resonance/controller.js';

let mountNode = null;

export const tool = {
  id: "resonance",
  type: "ui",
  subscriptions: ["rasa_id", "pada_id"],
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