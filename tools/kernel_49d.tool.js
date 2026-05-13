// C:\aigaane-master\tools\kernel_49d.tool.js
// 49D Kernel UI Adapter

import { init, render, destroy } from '../ui/tabs/kernel-49d/controller.js';

let mountNode = null;

export const tool = {
  id: "kernel-49d",
  type: "ui",
  subscriptions: ["pada_id", "nakshatra_id", "shruti_ratio", "rasa_id", "angle"],
  timeout_ms: 10,
  
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