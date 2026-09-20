export function renderInsightCard(data = {}) {
  const { engine = {}, nakshatra = '', pada = 0 } = data;
  const { primaryAxis = 0, coherence = 0, intensity = 0, phi = 0, confidence = 0 } = engine;

  const mode = phi > 0.5 ? 'Action phase' : (phi < -0.5 ? 'Reflection phase' : 'Neutral phase');
  const isResonanceFloor = intensity <= 0.012; // 1.2% threshold
  
  const container = document.createElement('div');
  container.className = 'glass-card';
  if (isResonanceFloor) {
    container.classList.add('resonance-floor-active');
  }
  
  container.innerHTML = `
    <h3>🌌 Anumāna Insight</h3>
    <p><strong>${nakshatra}</strong> (Pada ${pada})</p>
    <p>Primary Axis: ${primaryAxis}</p>
    <p>Coherence: ${(coherence * 100).toFixed(1)}%</p>
    <p>Intensity: <span class="${isResonanceFloor ? 'resonance-value' : ''}">${(intensity * 100).toFixed(1)}%</span></p>
    <p>Confidence: ${(confidence * 100).toFixed(1)}%</p>
    <p>Current Mode: ${mode}</p>
    ${isResonanceFloor ? '<p style="color:#00f2ff;">✨ Resonance Floor active – system stabilised</p>' : ''}
  `;
  return container;
}