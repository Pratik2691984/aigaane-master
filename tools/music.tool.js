// C:\aigaane-master\tools\music.tool.js
// UI Tool – Sonic Mandala Visualizer

import { init, render, destroy } from '../ui/tabs/music/controller.js';

let mountNode = null;

export const tool = {
  id: "music_ui",
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