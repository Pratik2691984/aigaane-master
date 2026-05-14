export function renderActionCard(vector49) {
  const container = document.createElement("div");
  container.className = "action-card";

  const maxIndex = vector49.indexOf(Math.max(...vector49));

  const actionMap = {
    0: "Initiate communication",
    1: "Pause and observe",
    2: "Take decisive action",
    3: "Avoid conflict",
    4: "Focus on learning",
    5: "Stabilize emotions",
    6: "Collaborate with others"
  };

  const action = actionMap[maxIndex % 7];

  container.innerHTML = `
    <h3>🎯 Recommended Action</h3>
    <p>${action}</p>
  `;

  return container;
}