export function createSemanticQueryState() {
  return {
    query: "",
    results: [],
  };
}

export function renderSemanticQueryResults(container, results = []) {
  if (!container) return;
  container.textContent = "";
  const values = Array.isArray(results) ? results : [];
  if (values.length === 0) {
    const empty = document.createElement("div");
    empty.className = "semantic-query-empty";
    empty.textContent = "No query results";
    container.appendChild(empty);
    return;
  }
  values.forEach((result) => {
    const row = document.createElement("article");
    row.className = "semantic-query-result";
    const title = document.createElement("strong");
    title.textContent = result?.id || result?.sessionId || result?.stepId || "result";
    const detail = document.createElement("small");
    detail.textContent = result?.reason || result?.type || "";
    row.append(title, detail);
    container.appendChild(row);
  });
}

export default { createSemanticQueryState, renderSemanticQueryResults };
