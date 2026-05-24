export function renderActionCard(flow) {
  const container = document.createElement('div');
  container.className = 'glass-card';

  // Use flow.confidence directly from translator (already computed with 70/30 formula)
  const confidencePercent = flow.confidence !== undefined ? (flow.confidence * 100).toFixed(0) : 0;
  let confidenceText = 'Low';
  if (flow.confidence > 0.6) confidenceText = 'High';
  else if (flow.confidence > 0.3) confidenceText = 'Medium';

  container.innerHTML = `
    <h3>🎯 Pravṛtti (Action)</h3>
    <p><strong>Best:</strong> ${flow.best || 'Observe and align'}</p>
    <p><strong>Avoid:</strong> ${flow.avoid || 'Proceed with awareness'}</p>
    <p><strong>Mode:</strong> ${flow.mode}</p>
    <p><strong>Confidence:</strong> ${confidenceText} (${confidencePercent}%)</p>
  `;

  // Energy bars (optional)
  if (flow.energy && flow.energy.length) {
    const energyDiv = document.createElement('div');
    energyDiv.style.marginTop = '12px';
    flow.energy.forEach((val, idx) => {
      const bar = document.createElement('div');
      bar.style.margin = '4px 0';
      bar.innerHTML = `<small>Axis ${idx + 1}</small><div class="energy-bar" style="width: ${val}%"></div>`;
      energyDiv.appendChild(bar);
    });
    container.appendChild(energyDiv);
  }

  return container;
}