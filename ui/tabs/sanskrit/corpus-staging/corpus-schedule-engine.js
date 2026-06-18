"use strict";

const {
  buildCorpusScheduleRecord,
  DEFAULT_SECONDS_PER_WINDOW
} = require("./corpus-schedule-map.js");

const {
  planCorpusWindows
} = require("./corpus-window-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function buildScheduleFromWindows(windows = [], secondsPerWindow = DEFAULT_SECONDS_PER_WINDOW) {
  const safeSeconds = Number(secondsPerWindow || DEFAULT_SECONDS_PER_WINDOW);
  let elapsed = 0;

  const schedule = windows.map((window, index) => {
    const startSecond = Math.round(elapsed * 1000) / 1000;
    elapsed += safeSeconds;
    const endSecond = Math.round(elapsed * 1000) / 1000;

    return {
      scheduleId: "schedule-" + String(index + 1).padStart(3, "0"),
      windowId: String(window.windowId || ""),
      windowOrder: Number(window.windowOrder || index + 1),
      recordCount: Number(window.recordCount || 0),
      startSecond,
      endSecond,
      completionPercent: Math.round(((index + 1) / windows.length) * 100000) / 1000,
      previewOnly: true
    };
  });

  return freeze(schedule);
}

function planCorpusSchedule(input = {}, windowSize = 250, secondsPerWindow = DEFAULT_SECONDS_PER_WINDOW) {
  const windowPlan = planCorpusWindows(input, windowSize);
  const windows = Array.isArray(windowPlan.windows) ? windowPlan.windows : [];
  const schedule = buildScheduleFromWindows(windows, secondsPerWindow);

  return buildCorpusScheduleRecord({
    scheduleCount: schedule.length,
    schedule,
    totalEstimatedSeconds: schedule.length
      ? schedule[schedule.length - 1].endSecond
      : 0,
    secondsPerWindow,
    windowPlan
  });
}

function summarizeCorpusSchedule(input = {}, windowSize = 250, secondsPerWindow = DEFAULT_SECONDS_PER_WINDOW) {
  const plan = planCorpusSchedule(input, windowSize, secondsPerWindow);

  return freeze({
    state: plan.state,
    valid: plan.state !== "SCHEDULE_BLOCKED",
    scheduleCount: plan.scheduleCount,
    totalEstimatedSeconds: plan.totalEstimatedSeconds,
    secondsPerWindow: plan.secondsPerWindow,
    previewOnly: true,
    readOnly: true,
    scheduleExecutionAllowed: false,
    windowExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  buildScheduleFromWindows,
  planCorpusSchedule,
  summarizeCorpusSchedule
};