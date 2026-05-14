// /tools/kernel_49d.tool.js
import { init, render, destroy } from '../ui/tabs/kernel-49d/controller.js';

let mountNode = null;

export const tool = {
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