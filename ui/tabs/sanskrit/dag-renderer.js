function text(value, fallback = "-") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function clear(node) {
  if (!node) return;
  while (node.firstChild) node.removeChild(node.firstChild);
}

function semanticTags(node) {
  const tags = [];
  const semantic = node?.semantic;
  if (semantic?.semanticTag) tags.push(semantic.semanticTag);
  if (semantic?.semantic_tag) tags.push(semantic.semantic_tag);
  const attributions = node?.semanticAttributions || node?.semantic_attributions || [];
  if (Array.isArray(attributions)) {
    attributions.forEach((item) => {
      if (item?.semanticTag) tags.push(item.semanticTag);
      if (item?.semantic_tag) tags.push(item.semantic_tag);
    });
  }
  return [...new Set(tags.map(String))];
}

function isRejected(node, graph) {
  const ids = Array.isArray(node?.ambiguity_branch_ids) ? node.ambiguity_branch_ids : [];
  const branches = Array.isArray(graph?.ambiguity_branches) ? graph.ambiguity_branches : [];
  return branches.some((branch) => ids.includes(branch?.branch_id || branch?.candidate_id) && ["rejected", "discarded"].includes(String(branch?.status || branch?.decision).toLowerCase()));
}

function isSelected(node, graph) {
  if (node?.selected === true || node?.is_selected === true) return true;
  const selectedPath = graph?.selected_path || graph?.selectedPath || [];
  return Array.isArray(selectedPath) && selectedPath.includes(node?.node_id || node?.step_id);
}

export function renderDerivationDag(container, graph = {}) {
  clear(container);
  if (!container) return;

  const nodes = Array.isArray(graph?.nodes) ? graph.nodes : [];
  const edges = Array.isArray(graph?.edges) ? graph.edges : [];
  const edgeMap = new Map();
  edges.forEach((edge) => {
    const source = edge?.source || edge?.from;
    if (!source) return;
    const list = edgeMap.get(source) || [];
    list.push(edge?.target || edge?.to);
    edgeMap.set(source, list);
  });

  const shell = document.createElement("div");
  shell.className = "dag-renderer";

  nodes.forEach((node) => {
    const nodeId = node?.node_id || node?.id || node?.step_id;
    const card = document.createElement("article");
    card.className = "dag-node";
    card.classList.toggle("selected", isSelected(node, graph));
    card.classList.toggle("rejected", isRejected(node, graph));

    const title = document.createElement("strong");
    title.textContent = text(node?.title || node?.operation || nodeId);
    const meta = document.createElement("small");
    meta.textContent = `${text(node?.engine)} · ${text(node?.output_state?.sutra || node?.sutra || node?.sutra_id)}`;

    const outgoing = document.createElement("span");
    outgoing.className = "dag-edge-label";
    const targets = edgeMap.get(nodeId) || [];
    outgoing.textContent = targets.length ? `to ${targets.map(text).join(", ")}` : "terminal";

    const tags = document.createElement("div");
    tags.className = "dag-tags";
    semanticTags(node).forEach((tag) => {
      const chip = document.createElement("span");
      chip.className = "dag-tag";
      chip.textContent = tag;
      tags.appendChild(chip);
    });

    card.append(title, meta, outgoing, tags);
    shell.appendChild(card);
  });

  if (nodes.length === 0) {
    const empty = document.createElement("div");
    empty.className = "dag-empty";
    empty.textContent = "No graph nodes";
    shell.appendChild(empty);
  }

  container.appendChild(shell);
}

export default { renderDerivationDag };
