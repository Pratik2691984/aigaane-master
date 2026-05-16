import { getCurrentGhatis } from "../lib/atma/chronos.js";
import { getSunriseSunset, agniCurve, getAbhijitWindow } from "../lib/atma/solar.js";
import { getTithi, lunarMultiplier } from "../lib/atma/lunar.js";
import { getDoshaAtGhati, getDoshaWindows } from "../lib/atma/dosha.js";
import { conflictScore, resonanceScore, recommendationForDosha } from "../lib/atma/conflict.js";

const DEFAULT_LOCATION = { lat: 28.6139, lon: 77.2090 };

let mountNode = null;
let updateInterval = null;
let currentLocation = null;
let currentAtmaState = null;
let currentCosmicAngle = 0;

function saveLocation(location) {
  localStorage.setItem("atma_location", JSON.stringify(location));
}

function loadLocation() {
  try {
    const raw = localStorage.getItem("atma_location");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function requestLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      saveLocation(DEFAULT_LOCATION);
      resolve(DEFAULT_LOCATION);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          lat: position.coords.latitude,
          lon: position.coords.longitude
        };
        saveLocation(location);
        resolve(location);
      },
      () => {
        saveLocation(DEFAULT_LOCATION);
        resolve(DEFAULT_LOCATION);
      },
      { maximumAge: 43200000, timeout: 5000 }
    );
  });
}

function getLogs() {
  try {
    return JSON.parse(localStorage.getItem("atma_logs") || "[]");
  } catch {
    return [];
  }
}

function saveLog(log) {
  const logs = getLogs();
  logs.push(log);
  localStorage.setItem("atma_logs", JSON.stringify(logs.slice(-50)));
}

function setText(selector, value) {
  const node = mountNode?.querySelector(selector);
  if (node) node.textContent = value;
}

function updateLogList() {
  const list = mountNode?.querySelector("#atma-log-list");
  if (!list) return;

  const logs = getLogs().slice(-5).reverse();
  if (logs.length === 0) {
    list.textContent = "No actions logged today.";
    return;
  }

  list.innerHTML = logs.map((log) => {
    const time = new Date(log.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const className = log.conflict < 20 ? "conflict-low" : log.conflict > 60 ? "conflict-high" : "conflict-mid";
    return `
      <div class="log-row ${className}">
        <strong>${time} · ${log.action} during ${log.dosha}</strong>
        <span>${Math.round(log.conflict)}%</span>
      </div>
    `;
  }).join("");
}

function animateMeter(targetConflict) {
  const meter = mountNode?.querySelector("#conflict-meter");
  const label = mountNode?.querySelector("#conflict-label");
  if (!meter || !label) return;

  const start = Number(meter.value || 0) * 100;
  const startTime = performance.now();
  const duration = 420;

  function step(now) {
    const progress = Math.min(1, (now - startTime) / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = start + (targetConflict - start) * eased;
    meter.value = value / 100;
    label.textContent = `${Math.round(value)}% conflict`;
    if (progress < 1) requestAnimationFrame(step);
  }

  requestAnimationFrame(step);
}

function applyFrictionResult(result, action) {
  const conflict = Number(result.conflict ?? 0);
  animateMeter(conflict);

  const recommendation = mountNode?.querySelector("#atma-recommendation");
  if (recommendation) {
    const suggestion = result.raga_suggestion
      ? ` Suggested remedy: ${result.raga_suggestion} / ${result.matrika_suggestion}.`
      : "";
    recommendation.textContent = `${result.label}: ${result.recommendation}${suggestion}`;
  }

  saveLog({
    timestamp: new Date().toISOString(),
    action,
    dosha: result.current_dosha,
    conflict,
    resonance: result.resonance_score,
    dosha_resonance: result.dosha_resonance
  });
  updateLogList();
}

async function updateConflict(action) {
  const state = currentAtmaState;
  if (!state) return;

  try {
    const response = await fetch("/api/atma/calculate-friction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        solar_time: state.currentGhatis,
        lunar_velocity: state.lunarBoost,
        user_action: action,
        current_dosha: state.dosha,
        agni_factor: state.agni,
        cosmic_angle: currentCosmicAngle
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    applyFrictionResult(await response.json(), action);
  } catch (err) {
    console.warn("[Atma] Backend friction unavailable, using local fallback:", err);
    const conflict = conflictScore(state.dosha, action, state.agni);
    const resonance = resonanceScore(state.dosha, action, state.agni);
    applyFrictionResult({
      current_dosha: state.dosha,
      conflict,
      resonance_score: resonance,
      dosha_resonance: state.dosha,
      label: conflict > 60 ? "High Friction" : conflict < 20 ? "Aligned" : "Mixed",
      recommendation: recommendationForDosha(state.dosha)
    }, action);
  }
}

function updateClockAndUI() {
  if (!mountNode || !currentLocation) return;

  const now = new Date();
  const { sunrise, sunset } = getSunriseSunset(now, currentLocation.lat, currentLocation.lon);
  const currentGhatis = getCurrentGhatis(sunrise, now);
  const sunriseGhati = (currentCosmicAngle / 360) * 60;
  const dosha = getDoshaAtGhati(currentGhatis, sunriseGhati);
  const tithi = getTithi(now);
  const lunarBoost = lunarMultiplier(tithi);
  const agni = Math.min(1, agniCurve(now.getHours() + now.getMinutes() / 60) * lunarBoost);
  const ghatisWhole = Math.floor(currentGhatis);
  const palas = Math.floor((currentGhatis - ghatisWhole) * 60);
  const windows = getDoshaWindows(sunriseGhati);
  const window = windows[dosha];

  currentAtmaState = {
    currentGhatis,
    dosha,
    tithi,
    lunarBoost,
    agni
  };

  setText("#vedic-time", `${ghatisWhole}:${palas.toString().padStart(2, "0")}`);
  setText("#current-dosha", dosha.toUpperCase());
  setText("#dosha-window", `${window.start.toFixed(0)}-${window.end.toFixed(0)} ghaṭī window`);
  setText("#agni-value", `${Math.round(agni * 100)}%`);
  setText("#tithi-value", `Tithi ${tithi} · lunar x${lunarBoost.toFixed(1)}`);

  const doshaNode = mountNode.querySelector("#current-dosha");
  if (doshaNode) doshaNode.dataset.dosha = dosha;

  const abhijit = getAbhijitWindow(sunrise, sunset);
  const abhijitNode = mountNode.querySelector("#abhijit-indicator");
  if (abhijitNode) abhijitNode.hidden = !(now >= abhijit.start && now <= abhijit.end);
}

async function init(node) {
  mountNode = node;
  currentLocation = loadLocation() || await requestLocation();

  const form = mountNode.querySelector("#daily-log-form");
  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const action = form.querySelector("#action-select")?.value || "mental";
      updateConflict(action);
    });
  }

  updateClockAndUI();
  updateLogList();
  if (updateInterval) clearInterval(updateInterval);
  updateInterval = setInterval(updateClockAndUI, 60000);
}

function render(state) {
  if (state?.angle !== undefined) currentCosmicAngle = Number(state.angle) || 0;
  updateClockAndUI();
}

function destroy() {
  if (updateInterval) clearInterval(updateInterval);
  updateInterval = null;
  mountNode = null;
}

export const tool = {
  id: "atma",
  type: "ui",
  subscriptions: ["angle"],
  timeout: 20,
  init,
  run: render,
  destroy
};
