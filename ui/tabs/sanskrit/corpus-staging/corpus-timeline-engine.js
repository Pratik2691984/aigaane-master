"use strict";

const {
  buildCorpusTimelineRecord
} = require("./corpus-timeline-map.js");

const {
  planCorpusSchedule
} = require("./corpus-schedule-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function buildTimelineFromSchedule(schedule = []) {
  const timeline = schedule.map((item, index) => {
    const startSecond = Number(item.startSecond || 0);
    const endSecond = Number(item.endSecond || 0);

    return {
      timelineId: "timeline-" + String(index + 1).padStart(3, "0"),
      scheduleId: String(item.scheduleId || ""),
      windowId: String(item.windowId || ""),
      order: Number(item.windowOrder || index + 1),
      recordCount: Number(item.recordCount || 0),
      startSecond,
      endSecond,
      durationSecond: Math.round((endSecond - startSecond) * 1000) / 1000,
      completionPercent: Number(item.completionPercent || 0),
      previewOnly: true
    };
  });

  return freeze(timeline);
}

function buildTimelineMarkers(timeline = []) {
  return freeze(timeline.map((item) => {
    return {
      markerId: "marker-" + String(item.order || 0).padStart(3, "0"),
      timelineId: item.timelineId,
      atSecond: item.endSecond,
      completionPercent: item.completionPercent,
      previewOnly: true
    };
  }));
}

function buildCorpusTimeline(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const schedulePlan = planCorpusSchedule(input, windowSize, secondsPerWindow);
  const schedule = Array.isArray(schedulePlan.schedule) ? schedulePlan.schedule : [];
  const timeline = buildTimelineFromSchedule(schedule);
  const markers = buildTimelineMarkers(timeline);

  return buildCorpusTimelineRecord({
    timelineCount: timeline.length,
    timeline,
    markers,
    totalEstimatedSeconds: schedulePlan.totalEstimatedSeconds,
    finalCompletionPercent: timeline.length
      ? timeline[timeline.length - 1].completionPercent
      : 0,
    schedulePlan
  });
}

function summarizeCorpusTimeline(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const timeline = buildCorpusTimeline(input, windowSize, secondsPerWindow);

  return freeze({
    state: timeline.state,
    valid: timeline.state !== "TIMELINE_BLOCKED",
    timelineCount: timeline.timelineCount,
    totalEstimatedSeconds: timeline.totalEstimatedSeconds,
    finalCompletionPercent: timeline.finalCompletionPercent,
    previewOnly: true,
    readOnly: true,
    timelineExecutionAllowed: false,
    scheduleExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  buildTimelineFromSchedule,
  buildTimelineMarkers,
  buildCorpusTimeline,
  summarizeCorpusTimeline
};