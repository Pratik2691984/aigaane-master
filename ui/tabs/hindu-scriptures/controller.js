import {
  scriptureTreeData,
  scriptureCategories,
  scriptureGlossary
} from "./scripture-data.js";

let mountNode = null;
let selectedNodeId = "sastra-root";
let activeFilter = "all";
let searchTerm = "";
let expandedIds = new Set(["sastra-root", "sruti", "smriti", "secular-supporting"]);
let listeners = [];
let nodeIndex = new Map();
let parentIndex = new Map();

function qs(selector) {
  return mountNode?.querySelector(selector) || null;
}

function qsa(selector) {
  return Array.from(mountNode?.querySelectorAll(selector) || []);
}

function on(target, event, handler) {
  if (!target) return;
  target.addEventListener(event, handler);
  listeners.push({ target, event, handler });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function indexTree(node, parent = null) {
  nodeIndex.set(node.id, node);
  if (parent) parentIndex.set(node.id, parent.id);
  (node.children || []).forEach((child) => indexTree(child, node));
}

function flattenText(value) {
  if (value == null) return "";
  if (Array.isArray(value)) return value.map(flattenText).join(" ");
  if (typeof value === "object") return Object.values(value).map(flattenText).join(" ");
  return String(value);
}

function nodeSearchText(node) {
  return [
    node.name,
    node.type,
    node.layer,
    node.category,
    node.canonicalStatus,
    node.essence,
    node.notes,
    node.keywords,
    node.sakhas,
    node.components,
    node.items,
    node.groups,
    node.subgroups,
    node.foundationalText,
    node.majorCommentaries,
    node.relatedNodes,
    node.aigaaneLink
  ].map(flattenText).join(" ").toLowerCase();
}

function categoryMatches(node) {
  if (activeFilter === "all") return true;
  if (activeFilter === "aigaane-link") return Boolean(node.aigaaneLink);
  const category = scriptureCategories.find((item) => item.id === activeFilter);
  return Boolean(
    category?.matches?.includes(node.category) ||
    node.layer === activeFilter ||
    node.type === activeFilter
  );
}

function nodeMatchesSelf(node) {
  const searchMatches = !searchTerm || nodeSearchText(node).includes(searchTerm);
  return searchMatches && categoryMatches(node);
}

function nodeMatchesTree(node) {
  return nodeMatchesSelf(node) || (node.children || []).some(nodeMatchesTree);
}

function findFirstMatchingNode(node) {
  if (!searchTerm && nodeMatchesSelf(node)) return node;
  for (const child of node.children || []) {
    const match = findFirstMatchingNode(child);
    if (match) return match;
  }
  if (nodeMatchesSelf(node)) return node;
  return null;
}

function findFirstNameMatch(node) {
  if (searchTerm && String(node.name || "").toLowerCase().includes(searchTerm) && categoryMatches(node)) {
    return node;
  }
  for (const child of node.children || []) {
    const match = findFirstNameMatch(child);
    if (match) return match;
  }
  return null;
}

function getPathToNode(id) {
  const path = [];
  let current = nodeIndex.get(id);
  while (current) {
    path.unshift(current);
    const parentId = parentIndex.get(current.id);
    current = parentId ? nodeIndex.get(parentId) : null;
  }
  return path;
}

function renderValue(label, value) {
  if (!value || (Array.isArray(value) && !value.length)) return "";
  if (Array.isArray(value)) {
    return `
      <div class="scriptures-card">
        <h3>${escapeHtml(label)}</h3>
        <ul>${value.map((item) => `<li>${escapeHtml(flattenText(item))}</li>`).join("")}</ul>
      </div>
    `;
  }
  if (typeof value === "object") {
    return `
      <div class="scriptures-card">
        <h3>${escapeHtml(label)}</h3>
        <dl>
          ${Object.entries(value).map(([key, item]) => `
            <dt>${escapeHtml(key)}</dt>
            <dd>${escapeHtml(flattenText(item))}</dd>
          `).join("")}
        </dl>
      </div>
    `;
  }
  return `
    <div class="scriptures-card">
      <h3>${escapeHtml(label)}</h3>
      <p>${escapeHtml(value)}</p>
    </div>
  `;
}

function renderGroups(groups, label = "Groups") {
  if (!groups?.length) return "";
  return `
    <div class="scriptures-card">
      <h3>${escapeHtml(label)}</h3>
      ${groups.map((group) => `
        <div class="scriptures-group">
          <strong>${escapeHtml(group.name || group.gunaClassification || "Group")}</strong>
          ${group.gunaClassification ? `<span class="scriptures-badge">${escapeHtml(group.gunaClassification)}</span>` : ""}
          ${(group.texts || group.items) ? `
            <ul>
              ${(group.texts || group.items).map((item) => {
                if (typeof item === "object") {
                  return `<li><strong>${escapeHtml(item.name)}</strong>${item.essence ? ` — ${escapeHtml(item.essence)}` : ""}</li>`;
                }
                return `<li>${escapeHtml(item)}</li>`;
              }).join("")}
            </ul>
          ` : ""}
        </div>
      `).join("")}
    </div>
  `;
}

function renderAigaaneLink(link) {
  if (!link) return "";
  return `
    <div class="scriptures-card scriptures-aigaane-link">
      <h3>Aigaane Integration Preview</h3>
      <dl>
        <dt>Module Context</dt>
        <dd>${escapeHtml(link.module)}</dd>
        <dt>Future Target</dt>
        <dd>${escapeHtml(link.futureTarget)}</dd>
        <dt>Note</dt>
        <dd>${escapeHtml(link.note)}</dd>
      </dl>
      <p>This is metadata only.</p>
    </div>
  `;
}

function renderBreadcrumb(node) {
  const target = qs("#scripture-breadcrumb");
  if (!target) return;
  target.innerHTML = getPathToNode(node.id)
    .map((item) => `<span>${escapeHtml(item.name)}</span>`)
    .join("<b>/</b>");
}

export function renderDetails(node) {
  const target = qs("#scripture-details");
  if (!target || !node) return;

  renderBreadcrumb(node);
  target.innerHTML = `
    <article>
      <div class="scriptures-detail-heading">
        <span class="scriptures-badge">${escapeHtml(node.layer || "node")}</span>
        <span class="scriptures-badge">${escapeHtml(node.type || "type")}</span>
        <span class="scriptures-badge">${escapeHtml(node.category || "category")}</span>
        <span class="scriptures-badge">${escapeHtml(node.canonicalStatus || "status")}</span>
        <h2>${escapeHtml(node.name)}</h2>
        <p>${escapeHtml(node.essence || "No essence provided.")}</p>
      </div>
      <div class="scriptures-detail-grid">
        ${renderValue("Śākhās", node.sakhas)}
        ${renderValue("Stats", node.components?.stats)}
        ${renderValue("Components", node.components)}
        ${renderValue("Items", node.items)}
        ${renderGroups(node.groups)}
        ${renderGroups(node.subgroups, "Subgroups")}
        ${renderValue("Foundational Text", node.foundationalText)}
        ${renderValue("Major Commentaries", node.majorCommentaries)}
        ${renderAigaaneLink(node.aigaaneLink)}
        ${renderValue("Notes", node.notes)}
        ${renderValue("Keywords", node.keywords)}
        ${renderValue("Related Nodes", node.relatedNodes)}
      </div>
      <div class="scriptures-card">
        <h3>Glossary Hints</h3>
        <div class="scriptures-glossary">
          ${Object.entries(scriptureGlossary).slice(0, 8).map(([term, note]) => `
            <span><strong>${escapeHtml(term)}</strong>: ${escapeHtml(note)}</span>
          `).join("")}
        </div>
      </div>
    </article>
  `;
}

function renderNode(node, depth = 0) {
  if (!nodeMatchesTree(node)) return "";
  const hasChildren = Boolean(node.children?.length);
  const expanded = expandedIds.has(node.id) || Boolean(searchTerm);
  const isActive = selectedNodeId === node.id;
  const children = hasChildren && expanded
    ? `<div class="scriptures-tree-children">${node.children.map((child) => renderNode(child, depth + 1)).join("")}</div>`
    : "";

  return `
    <div class="scriptures-tree-branch" data-depth="${depth}">
      <div class="scriptures-tree-node ${isActive ? "active" : ""}" style="--scripture-depth:${depth}">
        <button class="scriptures-toggle" type="button" data-scripture-toggle="${escapeHtml(node.id)}" ${hasChildren ? "" : "disabled"}>${hasChildren ? (expanded ? "-" : "+") : "•"}</button>
        <button class="scriptures-node-label" type="button" data-scripture-node="${escapeHtml(node.id)}">
          <span>${escapeHtml(node.name)}</span>
          <small>${escapeHtml(node.type || "")}</small>
        </button>
      </div>
      ${children}
    </div>
  `;
}

export function renderTree() {
  const target = qs("#scripture-tree");
  const empty = qs("#scripture-empty");
  if (!target) return;

  const markup = renderNode(scriptureTreeData);
  target.innerHTML = markup;
  if (empty) empty.classList.toggle("hidden", Boolean(markup.trim()));

  qsa("[data-scripture-node]").forEach((button) => {
    on(button, "click", () => {
      selectedNodeId = button.dataset.scriptureNode;
      const selected = nodeIndex.get(selectedNodeId);
      if (selected?.children?.length) expandedIds.add(selected.id);
      renderTree();
      renderDetails(selected);
    });
  });

  qsa("[data-scripture-toggle]").forEach((button) => {
    on(button, "click", () => {
      const id = button.dataset.scriptureToggle;
      if (expandedIds.has(id)) expandedIds.delete(id);
      else expandedIds.add(id);
      renderTree();
    });
  });
}

export function searchScriptures(term) {
  searchTerm = term.trim().toLowerCase();
  const match = findFirstNameMatch(scriptureTreeData) || findFirstMatchingNode(scriptureTreeData);
  if (match) {
    selectedNodeId = match.id;
    getPathToNode(match.id).forEach((item) => expandedIds.add(item.id));
    renderDetails(match);
  }
  renderTree();
}

function bindSearch() {
  const input = qs("#scripture-search");
  on(input, "input", () => searchScriptures(input.value));
}

function bindFilters() {
  qsa("[data-scripture-filter]").forEach((button) => {
    on(button, "click", () => {
      activeFilter = button.dataset.scriptureFilter || "all";
      qsa("[data-scripture-filter]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      const match = findFirstMatchingNode(scriptureTreeData);
      if (match) {
        selectedNodeId = match.id;
        getPathToNode(match.id).forEach((item) => expandedIds.add(item.id));
        renderDetails(match);
      }
      renderTree();
    });
  });
}

export async function init(root) {
  console.info("[Hindu Scriptures] init");
  mountNode = root?.querySelector?.("[data-scriptures-tab]") || root || document.querySelector("[data-scriptures-tab]");
  selectedNodeId = "sastra-root";
  activeFilter = "all";
  searchTerm = "";
  expandedIds = new Set(["sastra-root", "sruti", "smriti", "secular-supporting"]);
  listeners = [];
  nodeIndex = new Map();
  parentIndex = new Map();

  if (!mountNode) return;

  indexTree(scriptureTreeData);
  bindSearch();
  bindFilters();
  renderTree();
  renderDetails(scriptureTreeData);
}

export function destroy() {
  listeners.forEach(({ target, event, handler }) => target.removeEventListener(event, handler));
  listeners = [];
  mountNode = null;
  selectedNodeId = "sastra-root";
  searchTerm = "";
  activeFilter = "all";
  expandedIds = new Set();
  nodeIndex = new Map();
  parentIndex = new Map();
}

export const tool = { init, destroy };
export default { init, destroy };
