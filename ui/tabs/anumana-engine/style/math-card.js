export function renderMathCard(containerId, S, delta = []) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  const card = document.createElement("div");
  card.className = "glass-card";

  const title = document.createElement("h3");
  title.innerText = "49D Field";

  const grid = document.createElement("div");
  grid.className = "grid-49";

  S.forEach((value, i) => {
    const cell = document.createElement("div");

    const energyClass = getEnergyClass(value);
    cell.className = `cell ${energyClass}`;

    if (Math.abs(delta[i] || 0) > 0.1) {
      cell.classList.add("pulse");
    }

    const L = Math.floor(i / 7) + 1;
    const A = (i % 7) + 1;

    cell.title = `L${L}A${A}`;
    cell.innerText = value.toFixed(1);

    grid.appendChild(cell);
  });

  card.appendChild(title);
  card.appendChild(grid);
  container.appendChild(card);
}

function getEnergyClass(v) {
  if (v === 1) return "energy-3";
  if (v === 0.6) return "energy-2";
  if (v === 0.2) return "energy-1";
  return "energy-0";
}