// translator.js

const AXIS_MAP = [
  "Create",
  "Stabilize",
  "Transform",
  "Connect",
  "Express",
  "Analyze",
  "Release"
];

export function toFlowOutput(engine) {
  const { primaryAxis, coherence, intensity, phi } = engine;

  let best = "";
  let avoid = "";

  if (primaryAxis === 2 && intensity > 0.5)
    best = "Make a decisive shift";
  else if (primaryAxis === 1)
    best = "Stabilize and consolidate";
  else if (primaryAxis === 6)
    best = "Let go and release";

  if (coherence < 0.3)
    avoid = "Avoid major decisions";

  return {
    energy: buildEnergy(engine.axisScores),
    best,
    avoid,
    mode: phi > 0.5 ? "Act" : phi < -0.5 ? "Reflect" : "Wait"
  };
}

function buildEnergy(scores) {
  const max = Math.max(...scores);

  return scores.map(s => Math.round((s / max) * 100));
}