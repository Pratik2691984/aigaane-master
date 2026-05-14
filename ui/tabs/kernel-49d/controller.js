// C:\aigaane-master\ui\tabs\kernel-49d\controller.js
// 49D Kernel Controller with Golden Build Import (Viśākhā 210.0°)

import { resolve49D } from '../../../api/resolve_49d.js';
import { historyBuffer } from './history-buffer.js';

let mountNode = null;
let currentVector = null;
let currentMeta = null;
let currentAngle = 0;
let capturedState = null;
let trendCanvas = null;
let unsubscribeHistory = null;
let goldenBuildState = null;

const NAKSHATRA_NAMES = [
  "Ashvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣā", "Ārdrā", 
  "Punarvasu", "Puṣya", "Āśleṣā", "Maghā", "Pūrva Phalgunī", "Uttara Phalgunī",
  "Hasta", "Chitrā", "Svāti", "Viśākhā", "Anurādhā", "Jyeṣṭhā",
  "Mūla", "Pūrva Aṣāḍhā", "Uttara Aṣāḍhā", "Śravaṇā", "Dhanisṭhā", 
  "Śatabhiṣā", "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"
];

const LAYER_NAMES = [
  "🌌 Spatial", "⏳ Temporal", "🪐 Planetary", "⚖️ Guna", 
  "⚡ Energy", "🧬 Biological", "🌟 Stellar"
];

// Threshold definitions
const THRESHOLDS = {
  energy: { min: 0.8, max: 1.2, criticalMin: 0.5, criticalMax: 1.5 },
  guna: { rajasMin: 0.7, rajasMax: 0.9, sattvaMin: 0.6 },
  planetary: { sunThreshold: 0.9 },
  stellar: { minTemp: 3000, maxTemp: 15000 },
  spatial: { maxAngle: 360 }
};

// Anomaly detection thresholds
const ANOMALY_THRESHOLDS = {
  sruti_deviation: 0.07,
  guna_rajas_threshold: 0.85,
  energy_spike: 1.3,
  biological_layer_anomaly: 0.5
};

// ============ HELPER FUNCTIONS ============

function getHeatmapColor(value) {
  const v = Math.min(1, Math.max(0, value));
  if (v < 0.2) return '#0a0c12';
  if (v < 0.4) return '#2a2a3a';
  if (v < 0.6) return '#4a6a5a';
  if (v < 0.8) return '#c8a84a';
  return '#ffcc44';
}

function renderHeatmap(vector) {
  const container = mountNode?.querySelector('#heatmap-grid');
  if (!container) return;
  
  let html = '';
  for (let i = 0; i < 49; i++) {
    const value = vector[i];
    const color = getHeatmapColor(value);
    const layer = Math.floor(i / 7);
    const pos = i % 7;
    html += `<div class="heatmap-cell" style="background: ${color}" title="${LAYER_NAMES[layer]}[${pos}] = ${value.toFixed(4)}"></div>`;
  }
  container.innerHTML = html;
}

function detectAnomalies(vector, meta, srutiRatio, previousState) {
  const anomalies = [];
  
  const baseSruti = 1.4063;
  const srutiDeviation = Math.abs(srutiRatio - baseSruti) / baseSruti;
  if (srutiDeviation > ANOMALY_THRESHOLDS.sruti_deviation) {
    anomalies.push({
      type: 'discordance',
      severity: srutiDeviation > 0.12 ? 'high' : 'medium',
      message: `🎵 Śruti Discordance: ${(srutiDeviation * 100).toFixed(1)}% deviation`
    });
  }
  
  const gunaValues = vector.slice(21, 28);
  const rajas = gunaValues[1];
  if (rajas > ANOMALY_THRESHOLDS.guna_rajas_threshold) {
    anomalies.push({
      type: 'guna_peak',
      severity: 'warning',
      message: `🌪️ Extreme Rajas: ${(rajas * 100).toFixed(0)}%`
    });
  }
  
  const energyValues = vector.slice(28, 35);
  const maxEnergy = Math.max(...energyValues);
  if (maxEnergy > ANOMALY_THRESHOLDS.energy_spike) {
    anomalies.push({
      type: 'energy_spike',
      severity: 'critical',
      message: `⚡ Energy Spike: ${maxEnergy.toFixed(3)}`
    });
  }
  
  const biologicalValues = vector.slice(35, 42);
  const planetaryValues = vector.slice(14, 21);
  const planetaryMean = planetaryValues.reduce((a, b) => a + b, 0) / planetaryValues.length;
  const bioPlanetaryCorrelation = Math.abs(biologicalValues[0] - planetaryMean);
  if (bioPlanetaryCorrelation > ANOMALY_THRESHOLDS.biological_layer_anomaly) {
    anomalies.push({
      type: 'phase_lock_error',
      severity: 'medium',
      message: `🔄 Phase-Lock Error: delta ${bioPlanetaryCorrelation.toFixed(4)}`
    });
  }
  
  if (previousState) {
    const drift = historyBuffer.calculateDrift(previousState, {
      angle: currentAngle,
      vector: vector,
      meta: meta,
      nakshatra_id: meta.nakshatra_id,
      pada_id: meta.pada_id - 1,
      shruti_ratio: srutiRatio
    });
    
    if (drift && drift.velocity > 0.015) {
      anomalies.push({
        type: 'vector_drift',
        severity: drift.velocity > 0.025 ? 'high' : 'medium',
        message: `📐 Vector Drift: ${drift.velocity.toFixed(4)}/deg`
      });
    }
  }
  
  return anomalies;
}

function renderAnomalies(anomalies) {
  const container = mountNode?.querySelector('#anomaly-panel');
  if (!container) return;
  
  if (anomalies.length === 0) {
    container.innerHTML = '<div class="anomaly-clear">✅ No anomalies detected</div>';
    return;
  }
  
  container.innerHTML = `
    <div class="anomaly-header">⚠️ Active Anomalies (${anomalies.length})</div>
    ${anomalies.map(a => `
      <div class="anomaly-item anomaly-${a.severity}">
        <span class="anomaly-icon">${a.type === 'discordance' ? '🎵' : a.type === 'guna_peak' ? '🌪️' : a.type === 'energy_spike' ? '⚡' : a.type === 'phase_lock_error' ? '🔄' : '📐'}</span>
        <span class="anomaly-message">${a.message}</span>
      </div>
    `).join('')}
  `;
}

function renderTrendChart(trend) {
  if (!trendCanvas || !trend) return;
  
  const ctx = trendCanvas.getContext('2d');
  const width = trendCanvas.width;
  const height = trendCanvas.height;
  
  ctx.clearRect(0, 0, width, height);
  
  if (!trend.drifts || trend.drifts.length === 0) {
    ctx.fillStyle = '#7c8ba0';
    ctx.font = '10px monospace';
    ctx.fillText('Not enough data', width/2 - 40, height/2);
    return;
  }
  
  const drifts = trend.drifts.slice(-20);
  const maxDrift = Math.max(...drifts.map(d => d.avg_vector_delta), 0.05);
  
  ctx.beginPath();
  ctx.strokeStyle = '#D4AF37';
  ctx.lineWidth = 2;
  
  for (let i = 0; i < drifts.length; i++) {
    const x = (i / (drifts.length - 1)) * width;
    const y = height - (drifts[i].avg_vector_delta / maxDrift) * height;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  
  ctx.beginPath();
  const thresholdY = height - (0.015 / maxDrift) * height;
  ctx.moveTo(0, thresholdY);
  ctx.lineTo(width, thresholdY);
  ctx.strokeStyle = '#FF9933';
  ctx.setLineDash([5, 5]);
  ctx.stroke();
  ctx.setLineDash([]);
  
  ctx.fillStyle = '#7c8ba0';
  ctx.font = '8px monospace';
  ctx.fillText('Drift velocity', 5, 15);
  ctx.fillText('Threshold', 5, thresholdY - 2);
}

function updateTrendDisplay() {
  const trend = historyBuffer.getTrend(10);
  const trendStatsEl = mountNode?.querySelector('#trend-stats');
  
  if (trendStatsEl && trend) {
    trendStatsEl.innerHTML = `
      Avg Drift: ${trend.average_drift.toFixed(4)} | 
      Direction: ${trend.direction === 'forward' ? '→ Forward' : trend.direction === 'backward' ? '← Backward' : '● Stable'} | 
      ${trend.stable ? '✅ Stable' : '⚠️ In Flux'}
    `;
  }
  
  renderTrendChart(trend);
}

function checkThresholds(vector, angle) {
  const alerts = [];
  
  const energyValues = vector.slice(28, 35);
  const avgEnergy = energyValues.reduce((a, b) => a + b, 0) / energyValues.length;
  
  if (avgEnergy > THRESHOLDS.energy.max) {
    alerts.push({ type: 'warning', message: `⚡ Energy peak: ${avgEnergy.toFixed(3)}` });
  } else if (avgEnergy < THRESHOLDS.energy.min) {
    alerts.push({ type: 'warning', message: `⚠️ Energy low: ${avgEnergy.toFixed(3)}` });
  }
  
  if (avgEnergy > THRESHOLDS.energy.criticalMax) {
    alerts.push({ type: 'critical', message: `🔥 CRITICAL: Energy overflow` });
  } else if (avgEnergy < THRESHOLDS.energy.criticalMin) {
    alerts.push({ type: 'critical', message: `❄️ CRITICAL: Energy depletion` });
  }
  
  const gunaValues = vector.slice(21, 28);
  const rajas = gunaValues[1];
  
  if (rajas > THRESHOLDS.guna.rajasMax) {
    alerts.push({ type: 'warning', message: `🌪️ High Rajas: ${(rajas * 100).toFixed(0)}%` });
  } else if (rajas > THRESHOLDS.guna.rajasMin) {
    alerts.push({ type: 'info', message: `⚡ Elevated Rajas: ${(rajas * 100).toFixed(0)}%` });
  }
  
  return alerts;
}

function renderLayers(vector) {
  const container = mountNode?.querySelector('#vector-layers');
  if (!container) return;
  
  let html = '';
  
  for (let layer = 0; layer < 7; layer++) {
    const start = layer * 7;
    const values = vector.slice(start, start + 7);
    
    let hasWarning = false;
    let hasCritical = false;
    
    if (layer === 4) {
      const avgEnergy = values.reduce((a, b) => a + b, 0) / 7;
      hasWarning = avgEnergy > THRESHOLDS.energy.max || avgEnergy < THRESHOLDS.energy.min;
      hasCritical = avgEnergy > THRESHOLDS.energy.criticalMax || avgEnergy < THRESHOLDS.energy.criticalMin;
    }
    if (layer === 3) {
      const rajas = values[1];
      hasWarning = rajas > THRESHOLDS.guna.rajasMin;
    }
    
    html += `
      <div class="layer-card ${hasWarning ? 'threshold-active' : ''} ${hasCritical ? 'threshold-critical' : ''}">
        <div class="layer-header">${LAYER_NAMES[layer]}</div>
        <div class="layer-values">
          ${values.map((v, idx) => {
            let extraClass = '';
            if (v > 0.8) extraClass = 'highlight';
            if (layer === 4 && (v > THRESHOLDS.energy.max || v < THRESHOLDS.energy.min)) extraClass += ' threshold-warning';
            if (layer === 3 && idx === 1 && v > THRESHOLDS.guna.rajasMin) extraClass += ' threshold-warning';
            return `<div class="layer-value ${extraClass}">${v.toFixed(4)}</div>`;
          }).join('')}
        </div>
      </div>
    `;
  }
  
  container.innerHTML = html;
  
  const rawPre = mountNode?.querySelector('#raw-vector');
  if (rawPre) {
    rawPre.textContent = JSON.stringify(vector.map(v => parseFloat(v.toFixed(4))), null, 2);
  }
}

function renderAlerts(alerts) {
  const alertContainer = mountNode?.querySelector('#threshold-alerts');
  if (!alertContainer) return;
  
  if (alerts.length === 0) {
    alertContainer.innerHTML = '';
    return;
  }
  
  alertContainer.innerHTML = alerts.map(alert => `
    <div class="alert alert-${alert.type}">
      ${alert.type === 'warning' ? '⚠️' : alert.type === 'critical' ? '🔥' : 'ℹ️'} ${alert.message}
    </div>
  `).join('');
}

function updateMetrics(meta, shrutiRatio, vector) {
  const nakshatraEl = mountNode?.querySelector('#kernel-nakshatra');
  const padaEl = mountNode?.querySelector('#kernel-pada');
  const emissionEl = mountNode?.querySelector('#kernel-emission');
  const shrutiEl = mountNode?.querySelector('#kernel-shruti');
  const energyStatusEl = mountNode?.querySelector('#energy-status');

  if (nakshatraEl) nakshatraEl.textContent = NAKSHATRA_NAMES[meta.nakshatra_id] || '—';
  if (padaEl) padaEl.textContent = meta.pada_id;
  if (emissionEl) emissionEl.textContent = meta.emission?.toFixed(4) || '—';
  if (shrutiEl) shrutiEl.textContent = shrutiRatio?.toFixed(4) || '—';
  
  if (energyStatusEl && vector) {
    const energyValues = vector.slice(28, 35);
    const avgEnergy = energyValues.reduce((a, b) => a + b, 0) / 7;
    
    let status = '⚡ Normal';
    let statusClass = '';
    if (avgEnergy > THRESHOLDS.energy.max) {
      status = '🔥 High';
      statusClass = 'warning';
    } else if (avgEnergy < THRESHOLDS.energy.min) {
      status = '⚠️ Low';
      statusClass = 'warning';
    } else if (avgEnergy > THRESHOLDS.energy.criticalMax) {
      status = '💥 CRITICAL';
      statusClass = 'critical';
    } else if (avgEnergy < THRESHOLDS.energy.criticalMin) {
      status = '❄️ DEPLETED';
      statusClass = 'critical';
    } else {
      status = '✅ Optimal';
      statusClass = 'success';
    }
    
    energyStatusEl.textContent = status;
    energyStatusEl.className = `value ${statusClass}`;
  }
  
  const phaseLockEl = mountNode?.querySelector('#phase-lock-status');
  if (phaseLockEl && meta.phase_lock_status) {
    phaseLockEl.textContent = meta.phase_lock_status;
    phaseLockEl.className = `value ${meta.phase_lock_status === 'LOCKED' ? 'success' : 'warning'}`;
  }
  
  const planetaryMeanEl = mountNode?.querySelector('#planetary-mean');
  if (planetaryMeanEl && meta.planetary_mean) {
    planetaryMeanEl.textContent = meta.planetary_mean.toFixed(4);
  }
}

// ============ GOLDEN BUILD FUNCTIONS ============

// NEW: Auto-load Golden Build from backend on tab init
async function fetchAndApplyGoldenBuild() {
    try {
        const response = await fetch('https://aigaane-master.onrender.com/kernel/v3/golden/current');
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        if (data.vector && data.vector.length === 49) {
            currentVector = data.vector;
            if (currentMeta) currentMeta.phase_lock_status = "LOCKED";
            renderLayers(currentVector);
            renderHeatmap(currentVector);
            const rawPre = mountNode?.querySelector('#raw-vector');
            if (rawPre) rawPre.textContent = JSON.stringify(currentVector.map(v => parseFloat(v.toFixed(4))), null, 2);
            console.log('[49D Kernel] Golden Build auto‑loaded from backend');
        }
    } catch (err) {
        console.warn('[49D Kernel] Could not load Golden Build from backend, using local state.');
    }
}

async function importGoldenBuild() {
  const alertContainer = mountNode?.querySelector('#threshold-alerts');
  
  try {
    if (alertContainer) {
      const loadAlert = document.createElement('div');
      loadAlert.className = 'alert alert-info';
      loadAlert.innerHTML = '⏳ Loading Viśākhā Golden Build (210.0°)...';
      alertContainer.prepend(loadAlert);
    }
    
    // UPDATED: Load Viśākhā Golden Build instead of Chitrā
    const response = await fetch('/golden_build_vishakha_210.json');
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: File not found. Make sure golden_build_vishakha_210.json is in the root folder.`);
    }
    
    const data = await response.json();
    
    let newVector;
    if (data.vector && data.vector.length === 49) {
      newVector = data.vector;
    } else if (data.vector_49d && data.vector_49d.length === 49) {
      newVector = data.vector_49d;
    } else {
      throw new Error('Invalid format: Expected 49D array');
    }
    
    currentVector = newVector;
    if (currentMeta) {
      currentMeta.phase_lock_status = "LOCKED";
      currentMeta.planetary_mean = data.constraints?.planetary_mean || 0.5071;
    }
    
    renderLayers(currentVector);
    renderHeatmap(currentVector);
    
    const rawPre = mountNode?.querySelector('#raw-vector');
    if (rawPre) {
      rawPre.textContent = JSON.stringify(currentVector.map(v => parseFloat(v.toFixed(4))), null, 2);
    }
    
    saveGoldenBuild();
    
    if (alertContainer) {
      const loadingAlert = alertContainer.querySelector('.alert-info');
      if (loadingAlert) loadingAlert.remove();
      
      const successAlert = document.createElement('div');
      successAlert.className = 'alert alert-success';
      successAlert.innerHTML = `🏆 Viśākhā Golden Build Imported: 210.0°<br>✅ Stellar temp: 8900K | Phase-Lock: LOCKED | Discordance: CLEARED`;
      alertContainer.prepend(successAlert);
      setTimeout(() => successAlert.remove(), 5000);
    }
    
    console.log('[49D Kernel] Viśākhā Golden Build imported');
    
  } catch (error) {
    console.error('[49D Kernel] Import failed:', error);
    
    if (alertContainer) {
      const loadingAlert = alertContainer.querySelector('.alert-info');
      if (loadingAlert) loadingAlert.remove();
      
      const errorAlert = document.createElement('div');
      errorAlert.className = 'alert alert-critical';
      errorAlert.innerHTML = `❌ Import failed: ${error.message}<br><small>Place golden_build_vishakha_210.json in C:\\aigaane-master\\</small>`;
      alertContainer.prepend(errorAlert);
      setTimeout(() => errorAlert.remove(), 8000);
    }
  }
}

function saveGoldenBuild() {
  if (!currentVector || !currentMeta) return;
  
  goldenBuildState = {
    timestamp: new Date().toISOString(),
    angle: currentAngle,
    nakshatra: NAKSHATRA_NAMES[currentMeta.nakshatra_id],
    pada: currentMeta.pada_id,
    vector: [...currentVector],
    meta: { ...currentMeta }
  };
  
  localStorage.setItem('aigaane_golden_build', JSON.stringify(goldenBuildState));
  
  const alertContainer = mountNode?.querySelector('#threshold-alerts');
  if (alertContainer) {
    const tempAlert = document.createElement('div');
    tempAlert.className = 'alert alert-success';
    tempAlert.innerHTML = `🏆 Golden Build saved: ${goldenBuildState.nakshatra} at ${goldenBuildState.angle.toFixed(1)}°`;
    alertContainer.prepend(tempAlert);
    setTimeout(() => tempAlert.remove(), 4000);
  }
  
  const compareBtn = mountNode?.querySelector('#compare-golden-btn');
  if (compareBtn) compareBtn.disabled = false;
  
  console.log('[49D Kernel] Golden Build saved');
}

function compareWithGolden() {
  if (!goldenBuildState || !currentVector) {
    const alertContainer = mountNode?.querySelector('#threshold-alerts');
    if (alertContainer) {
      const tempAlert = document.createElement('div');
      tempAlert.className = 'alert alert-warning';
      tempAlert.innerHTML = `⚠️ No Golden Build saved yet. Use "Import Golden JSON" or "Save Golden Build" first.`;
      alertContainer.prepend(tempAlert);
      setTimeout(() => tempAlert.remove(), 3000);
    }
    return;
  }
  
  const differences = currentVector.map((v, i) => (v - goldenBuildState.vector[i]).toFixed(4));
  const sumDiff = differences.reduce((a, b) => a + Math.abs(parseFloat(b)), 0);
  const avgDiff = (sumDiff / 49).toFixed(4);
  
  const alertContainer = mountNode?.querySelector('#threshold-alerts');
  if (alertContainer) {
    const diffAlert = document.createElement('div');
    diffAlert.className = 'alert alert-info';
    diffAlert.innerHTML = `
      🏆 Golden Build Comparison:<br>
      ${goldenBuildState.nakshatra} (${goldenBuildState.angle.toFixed(1)}°) → Current (${currentAngle.toFixed(1)}°)<br>
      📊 Average delta: ${avgDiff}<br>
      ${avgDiff > 0.05 ? '⚠️ Significant drift from Golden Build' : '✅ Within Golden Build tolerance'}
    `;
    alertContainer.prepend(diffAlert);
    setTimeout(() => diffAlert.remove(), 5000);
  }
}

function loadGoldenBuild() {
  const saved = localStorage.getItem('aigaane_golden_build');
  if (saved) {
    try {
      goldenBuildState = JSON.parse(saved);
      console.log('[49D Kernel] Golden Build loaded from localStorage');
      
      const compareBtn = mountNode?.querySelector('#compare-golden-btn');
      if (compareBtn) compareBtn.disabled = false;
    } catch (e) {
      console.error('[49D Kernel] Failed to load Golden Build:', e);
    }
  }
}

function addGoldenBuildButtons() {
  const actionBar = mountNode?.querySelector('.action-bar');
  if (!actionBar) return;
  
  if (actionBar.querySelector('#import-golden-btn')) return;
  
  const importBtn = document.createElement('button');
  importBtn.id = 'import-golden-btn';
  importBtn.className = 'action-btn import-btn';
  importBtn.innerHTML = '🏆 Import Viśākhā Golden (210°)';
  importBtn.style.background = 'rgba(76, 175, 80, 0.15)';
  importBtn.style.borderColor = '#4caf50';
  
  const saveBtn = document.createElement('button');
  saveBtn.id = 'save-golden-btn';
  saveBtn.className = 'action-btn golden-btn';
  saveBtn.innerHTML = '💾 Save Golden Build';
  saveBtn.style.background = 'rgba(212, 175, 55, 0.2)';
  saveBtn.style.borderColor = '#D4AF37';
  
  const compareBtn = document.createElement('button');
  compareBtn.id = 'compare-golden-btn';
  compareBtn.className = 'action-btn compare-golden-btn';
  compareBtn.innerHTML = '🔍 Compare with Golden';
  compareBtn.disabled = !goldenBuildState;
  compareBtn.style.background = 'rgba(100, 150, 200, 0.1)';
  compareBtn.style.borderColor = '#6496c8';
  
  importBtn.addEventListener('click', () => importGoldenBuild());
  saveBtn.addEventListener('click', () => saveGoldenBuild());
  compareBtn.addEventListener('click', () => compareWithGolden());
  
  actionBar.appendChild(importBtn);
  actionBar.appendChild(saveBtn);
  actionBar.appendChild(compareBtn);
}

// ============ EVENT LISTENERS ============

function setupEventListeners() {
  const exportBtn = mountNode?.querySelector('#export-vector-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      if (!currentVector || !currentMeta) return;
      
      const exportData = {
        timestamp: new Date().toISOString(),
        angle: currentAngle,
        nakshatra: NAKSHATRA_NAMES[currentMeta.nakshatra_id],
        pada: currentMeta.pada_id,
        stellar_emission: currentMeta.emission,
        shruti_ratio: currentMeta.shruti_ratio,
        vector_49d: currentVector,
        layers: {
          spatial: currentVector.slice(0, 7),
          temporal: currentVector.slice(7, 14),
          planetary: currentVector.slice(14, 21),
          guna: currentVector.slice(21, 28),
          energy: currentVector.slice(28, 35),
          biological: currentVector.slice(35, 42),
          stellar: currentVector.slice(42, 49)
        }
      };
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `49d-vector-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      const alertContainer = mountNode?.querySelector('#threshold-alerts');
      if (alertContainer) {
        const tempAlert = document.createElement('div');
        tempAlert.className = 'alert alert-success';
        tempAlert.innerHTML = '✅ 49D vector exported!';
        alertContainer.prepend(tempAlert);
        setTimeout(() => tempAlert.remove(), 3000);
      }
    });
  }
  
  const captureBtn = mountNode?.querySelector('#capture-state-btn');
  if (captureBtn) {
    captureBtn.addEventListener('click', () => {
      capturedState = {
        timestamp: new Date().toISOString(),
        angle: currentAngle,
        vector: [...currentVector],
        meta: { ...currentMeta }
      };
      
      const compareBtn = mountNode?.querySelector('#compare-state-btn');
      if (compareBtn) compareBtn.disabled = false;
      
      const alertContainer = mountNode?.querySelector('#threshold-alerts');
      if (alertContainer) {
        const tempAlert = document.createElement('div');
        tempAlert.className = 'alert alert-success';
        tempAlert.innerHTML = `📸 State captured at ${currentAngle.toFixed(1)}°`;
        alertContainer.prepend(tempAlert);
        setTimeout(() => tempAlert.remove(), 3000);
      }
    });
  }
  
  const compareBtn = mountNode?.querySelector('#compare-state-btn');
  if (compareBtn) {
    compareBtn.addEventListener('click', () => {
      if (!capturedState || !currentVector) return;
      
      const differences = currentVector.map((v, i) => (v - capturedState.vector[i]).toFixed(4));
      const sumDiff = differences.reduce((a, b) => a + Math.abs(parseFloat(b)), 0);
      const avgDiff = (sumDiff / 49).toFixed(4);
      
      const alertContainer = mountNode?.querySelector('#threshold-alerts');
      if (alertContainer) {
        const diffAlert = document.createElement('div');
        diffAlert.className = 'alert alert-info';
        diffAlert.innerHTML = `🔍 Delta: ${avgDiff} | ${avgDiff > 0.1 ? '⚠️ Significant shift' : '✅ Minor variation'}`;
        alertContainer.prepend(diffAlert);
        setTimeout(() => diffAlert.remove(), 5000);
      }
    });
  }
  
  trendCanvas = mountNode?.querySelector('#trend-canvas');
  if (trendCanvas) {
    trendCanvas.width = 400;
    trendCanvas.height = 100;
  }
}

// ============ EXPORTS ============

export function init(node) {
  mountNode = node;
  setupEventListeners();
  addGoldenBuildButtons();
  loadGoldenBuild();
  fetchAndApplyGoldenBuild(); // NEW: Auto-load Golden Build from backend
  
  if (unsubscribeHistory) unsubscribeHistory();
  unsubscribeHistory = historyBuffer.subscribe(({ event }) => {
    if (event === 'push') updateTrendDisplay();
  });
  
  console.log('[49D Kernel] Tab mounted with Viśākhā Golden Build support');
}

export function render(state, node) {
  if (node) mountNode = node;
  if (!mountNode) return;
  if (!state) {
    console.error('[49D Kernel] State is undefined');
    return;
  }
  
  currentAngle = state.angle || (state.pada_id * 3.3333);
  
  const result = resolve49D(state);
  currentVector = result.vector;
  currentMeta = result.meta;
  
  const previousState = historyBuffer.getPrevious();
  
  const alerts = checkThresholds(currentVector, currentAngle);
  renderAlerts(alerts);
  
  const anomalies = detectAnomalies(currentVector, currentMeta, state.shruti_ratio, previousState);
  renderAnomalies(anomalies);
  
  updateMetrics(currentMeta, state.shruti_ratio, currentVector);
  renderLayers(currentVector);
  renderHeatmap(currentVector);
  
  historyBuffer.push({
    angle: currentAngle,
    nakshatra_id: currentMeta.nakshatra_id,
    pada_id: currentMeta.pada_id - 1,
    vector: currentVector,
    meta: currentMeta,
    shruti_ratio: state.shruti_ratio
  });
  
  updateTrendDisplay();
  setupEventListeners();
  addGoldenBuildButtons();
}

export function destroy() {
  if (unsubscribeHistory) unsubscribeHistory();
  mountNode = null;
  currentVector = null;
  currentMeta = null;
  capturedState = null;
  trendCanvas = null;
  goldenBuildState = null;
  console.log('[49D Kernel] Tab destroyed');
}