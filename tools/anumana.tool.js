import { init, render, destroy } from '../ui/tabs/anumana/controller.js';

let mountNode = null;

export const tool = {
  id: "anumana",
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