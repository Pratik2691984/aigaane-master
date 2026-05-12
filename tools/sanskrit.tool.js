// C:\aigaane-master\tools\sanskrit.tool.js

import { init, render, destroy } from '../ui/tabs/sanskrit/controller.js';

let mountNode = null;

export const tool = {
  id: "sanskrit",
  type: "ui",
  subscriptions: ["phoneme_id"],
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