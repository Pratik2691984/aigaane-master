// predictive.js – with stable angle detection and history tracking
import { computeAnumana } from './anumana-engine.js';

let historyBuffer = []; // stores last 30 intensity values
const MAX_HISTORY = 30;

export function simulateFuture(engine, profile, steps = 30, thetaStepDeg = 0.000305) {
  if (!engine || !profile || !profile.S_base) return [];

  let simState = {
    A_prev: engine.A_next,
    S_base: profile.S_base,
    theta: engine.theta,
    S_birth: null
  };

  const forecast = [];

  for (let step = 1; step <= steps; step++) {
    const nextTheta = (simState.theta + thetaStepDeg * step) % 360;
    const nextEngine = computeAnumana({
      S_base: simState.S_base,
      theta: nextTheta,
      A_prev: simState.A_prev,
      S_birth: simState.S_birth
    });

    forecast.push({
      step,
      coherence: nextEngine.coherence,
      intensity: nextEngine.intensity,
      primaryAxis: nextEngine.primaryAxis,
      phi: nextEngine.phi,
      deltaAvg: nextEngine.delta.reduce((a,b) => a + Math.abs(b), 0) / 49
    });

    simState.A_prev = nextEngine.A_next;
  }

  return forecast;
}

export function getPredictiveAlerts(forecast, currentAngle = null) {
  if (!forecast.length) return {};

  const coherenceTrend = forecast.map(f => f.coherence);
  const intensityTrend = forecast.map(f => f.intensity);

  const coherenceRising = coherenceTrend[coherenceTrend.length-1] > coherenceTrend[0];
  const intensityRising = intensityTrend[intensityTrend.length-1] > intensityTrend[0];

  let maxCoherenceStep = 0;
  let maxCoherence = 0;
  coherenceTrend.forEach((c, i) => {
    if (c > maxCoherence) {
      maxCoherence = c;
      maxCoherenceStep = i;
    }
  });

  // Stable angle detection (multiples of 90°)
  const isStableAngle = (angle) => angle !== null && Math.abs(angle % 90) < 0.1;
  let recommendation = coherenceRising ? 'Prepare for stable phase' : 'Expect turbulence';
  
  if (isStableAngle(currentAngle) && !coherenceRising && !intensityRising) {
    recommendation = 'Stable phase – no action needed';
  }

  // Build history for sparkline (last intensity values from forecast + current)
  const history = [...historyBuffer];
  if (forecast.length) {
    history.push(forecast[0].intensity);
    while (history.length > MAX_HISTORY) history.shift();
  }
  historyBuffer = history;

  return {
    coherenceTrend: coherenceRising ? 'rising' : 'falling',
    intensityTrend: intensityRising ? 'rising' : 'falling',
    maxCoherenceIn: maxCoherenceStep * 2,
    maxCoherenceValue: maxCoherence,
    recommendation,
    intensityValue: forecast[0]?.intensity || 0,
    history: [...history] // copy for sparkline
  };
}