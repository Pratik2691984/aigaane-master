// C:\aigaane-master\tools\music.tool.js

import { init, render, destroy } from '../ui/tabs/music/controller.js';

let mountNode = null;

export const tool = {
  id: "music",
  type: "ui",
  subscriptions: ["pada_id", "shruti_ratio"],
  timeout: 20,
  
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