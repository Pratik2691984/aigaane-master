// predictive-card.js – uses Chart.js (CDN already in view.html)
let chartInstance = null;

export function renderPredictiveCard(alerts) {
  const container = document.createElement('div');
  const isFloorActive = alerts.intensityValue !== undefined && alerts.intensityValue <= 0.012;
  
  container.className = `glass-card predictive-layer ${isFloorActive ? 'status-stabilized' : ''}`;
  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <h3 style="margin:0;">🔮 Forecast (next minute)</h3>
      ${isFloorActive ? '<span class="floor-badge">Resonance Floor Active</span>' : ''}
    </div>
    
    <div class="sparkline-container" style="height: 50px; margin: 10px 0;">
      <canvas id="intensitySparkline" width="400" height="50" style="width:100%; height:50px;"></canvas>
    </div>

    <div class="metrics-grid" style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
      <p>Coherence: <span class="trend-${alerts.coherenceTrend}">${alerts.coherenceTrend}</span></p>
      <p>Intensity: <span class="trend-${alerts.intensityTrend}">${(alerts.intensityValue * 100).toFixed(1)}%</span></p>
      <p>Max coherence in ~${alerts.maxCoherenceIn}s</p>
    </div>
    
    <div class="recommendation-zone" style="margin-top: 12px;">
      <p><strong>Recommendation:</strong> ${alerts.recommendation}</p>
    </div>
  `;

  // Draw Chart.js sparkline if history exists and Chart is available
  if (alerts.history && alerts.history.length > 1 && window.Chart) {
    const canvas = container.querySelector('#intensitySparkline');
    if (canvas) {
      // Destroy previous instance if exists
      if (chartInstance) {
        try { chartInstance.destroy(); } catch(e) {}
      }
      const ctx = canvas.getContext('2d');
      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [{
            data: alerts.history.map(v => v * 100), // scale to percentage
            borderColor: '#00f2ff',
            borderWidth: 2,
            pointRadius: 0,
            fill: true,
            backgroundColor: 'rgba(0, 242, 255, 0.1)',
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
          scales: { x: { display: false }, y: { display: false, min: 0, max: 10 } }
        }
      });
    }
  }
  
  return container;
}