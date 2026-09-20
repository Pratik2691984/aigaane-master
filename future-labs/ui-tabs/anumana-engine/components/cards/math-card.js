// math-card.js – renders 49D grid with improved energy mapping
export function renderMathCard(vector49) {
  const container = document.createElement('div');
  container.className = 'glass-card';

  const title = document.createElement('h3');
  title.innerText = '49D Field (Tattva Matrix)';
  container.appendChild(title);

  const grid = document.createElement('div');
  grid.className = 'grid-49';

  vector49.forEach((value, i) => {
    const cell = document.createElement('div');
    cell.className = `cell ${getEnergyClass(value)}`;
    cell.title = `L${Math.floor(i / 7) + 1} A${(i % 7) + 1} = ${value.toFixed(2)}`;
    cell.innerText = value.toFixed(1);
    grid.appendChild(cell);
  });

  container.appendChild(grid);
  return container;
}

// Floating‑point safe thresholds
function getEnergyClass(v) {
  if (v > 0.8) return 'energy-3';
  if (v > 0.5) return 'energy-2';
  if (v > 0.1) return 'energy-1';
  return 'energy-0';
}