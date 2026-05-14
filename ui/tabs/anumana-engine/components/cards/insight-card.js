export function renderInsightCard(nakshatra, pada, vector49) {
  const container = document.createElement("div");
  container.className = "insight-card";

  const dominant = vector49.indexOf(Math.max(...vector49));

  const meaning = `
    Under ${nakshatra} (Pada ${pada}),
    the dominant energy channel is ${dominant}.

    This indicates a phase of ${
      dominant % 2 === 0 ? "expansion" : "internal reflection"
    }.

    Your system is currently biased toward ${
      dominant < 24 ? "action" : "integration"
    }.
  `;

  container.innerHTML = `
    <h3>🌌 Insight</h3>
    <p>${meaning}</p>
  `;

  return container;
}