export function renderMathCard(vector49) {
  const container = document.createElement("div");
  container.className = "math-card";

  const grid = document.createElement("div");
  grid.className = "math-grid";

  vector49.forEach((value, index) => {
    const cell = document.createElement("div");
    cell.className = "math-cell";

    // Normalize value (-1 → 1 assumed)
    const intensity = Math.floor((value + 1) * 127);

    cell.style.backgroundColor = `rgb(${intensity}, ${50}, ${255 - intensity})`;

    cell.innerText = value.toFixed(2);
    grid.appendChild(cell);
  });

  container.appendChild(grid);
  return container;
}