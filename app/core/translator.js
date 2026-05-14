const AXIS_MAP = [
  "Create", "Stabilize", "Transform", "Connect",
  "Express", "Analyze", "Release"
];

export function toFlowOutput(engine) {
  if (!engine || !engine.axisScores || engine.status === 'degraded') {
    return {
      best: "Stabilize and observe",
      avoid: "Overreacting",
      mode: "Recovery",
      energy: [20, 20, 20, 20, 20, 20, 20],
      coherence: 0,
      intensity: RESONANCE_FLOOR,
      confidence: 0
    };
  }

  const { primaryAxis, coherence, intensity, phi, axisScores, confidence } = engine;

  let best = "";
  let avoid = "";

  if (primaryAxis === 2 && intensity > 0.5) best = "Make a decisive shift";
  else if (primaryAxis === 1) best = "Stabilize and consolidate";
  else if (primaryAxis === 6) best = "Let go and release";
  else best = "Observe and align";

  if (coherence < 0.3) avoid = "Avoid major decisions";
  else avoid = "Proceed with awareness";

  const energy = buildEnergy(axisScores);

  return {
    energy,
    best,
    avoid,
    mode: phi > 0.5 ? "Act" : phi < -0.5 ? "Reflect" : "Neutral",
    coherence,
    intensity,
    confidence
  };
}

function buildEnergy(scores) {
  const max = Math.max(...scores, 0.001);
  return scores.map(s => Math.round((s / max) * 100));
}