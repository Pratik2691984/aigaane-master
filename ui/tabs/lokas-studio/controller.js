import {
  lokasData,
  narakasData,
  aparadhasData,
  promptTemplates,
  gunaProfiles,
  pingalaPatterns
} from "./data.js";

let mountNode = null;
let currentPanel = "lokas";
let searchTerm = "";
let selectedLoka = null;
let listeners = [];
let gunaState = { Sattva: 60, Rajas: 25, Tamas: 15 };

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

function textMatches(value, term = searchTerm) {
  return String(value || "").toLowerCase().includes(term);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function writeEmpty(target, label) {
  if (target) target.innerHTML = `<div class="lokas-empty">${escapeHtml(label)}</div>`;
}

function formatValue(value) {
  return Number(value).toFixed(2);
}

function filterLokas() {
  return lokasData.filter((loka) => [
    loka.name,
    loka.category,
    loka.guna,
    loka.desc,
    loka.scriptures
  ].some((value) => textMatches(value)));
}

function filterNarakas() {
  return narakasData.filter((naraka) => [
    naraka.name,
    naraka.cause,
    naraka.consequence,
    naraka.category
  ].some((value) => textMatches(value)));
}

function filterAparadhas() {
  const namaAparadhas = aparadhasData.namaAparadhas.filter((item) => [
    item.title,
    item.note
  ].some((value) => textMatches(value)));

  const sevaAparadhas = aparadhasData.sevaAparadhas.filter((item) => textMatches(item));
  return { namaAparadhas, sevaAparadhas };
}

function filterPrompts() {
  return Object.entries(promptTemplates).filter(([key, template]) => [
    key,
    template.title,
    template.guna,
    template.prompt,
    template.suggestedEngine,
    template.physicsHint
  ].some((value) => textMatches(value)));
}

function filterGunas() {
  return Object.entries(gunaProfiles).filter(([key, profile]) => [
    key,
    profile.title,
    ...profile.traits
  ].some((value) => textMatches(value)));
}

function filterPingala() {
  return pingalaPatterns.filter((pattern) => [
    pattern.name,
    pattern.id,
    pattern.legend,
    pattern.pattern.join(""),
    pattern.pattern.join(","),
    pattern.matras.join(",")
  ].some((value) => textMatches(value)));
}

function normalizeGunas(changedKey, rawValue) {
  const value = Math.max(0, Math.min(100, Number(rawValue)));
  const otherKeys = Object.keys(gunaState).filter((key) => key !== changedKey);
  const remainder = 100 - value;
  const otherTotal = otherKeys.reduce((sum, key) => sum + gunaState[key], 0);

  gunaState[changedKey] = value;
  if (otherTotal <= 0) {
    const split = remainder / otherKeys.length;
    otherKeys.forEach((key) => {
      gunaState[key] = split;
    });
  } else {
    otherKeys.forEach((key) => {
      gunaState[key] = (gunaState[key] / otherTotal) * remainder;
    });
  }

  const rounded = Object.fromEntries(Object.entries(gunaState).map(([key, amount]) => [key, Math.round(amount)]));
  const drift = 100 - Object.values(rounded).reduce((sum, amount) => sum + amount, 0);
  rounded[changedKey] += drift;
  gunaState = rounded;
}

function deriveGunaProfile() {
  const s = gunaState.Sattva / 100;
  const r = gunaState.Rajas / 100;
  const t = gunaState.Tamas / 100;
  const sattvaBase = gunaProfiles.Sattva.base;
  const rajasBase = gunaProfiles.Rajas.base;
  const tamasBase = gunaProfiles.Tamas.base;

  return {
    noise: sattvaBase.noise * s + rajasBase.noise * r + tamasBase.noise * t,
    coupling: sattvaBase.coupling * s + rajasBase.coupling * r + tamasBase.coupling * t,
    coherenceBias: sattvaBase.coherenceBias * s + rajasBase.coherenceBias * r + tamasBase.coherenceBias * t,
    fragmentationBias: sattvaBase.fragmentationBias * s + rajasBase.fragmentationBias * r + tamasBase.fragmentationBias * t
  };
}

export function renderLokas() {
  const target = qs("#lokas-cards");
  if (!target) return;

  const results = filterLokas();
  if (!results.length) {
    writeEmpty(target, "No Lokas match this search.");
    return;
  }

  target.innerHTML = results.map((loka) => {
    const profile = loka.collapseProfile;
    return `
      <article class="lokas-card is-selectable ${selectedLoka?.id === loka.id ? "is-selected" : ""}" data-loka-id="${escapeHtml(loka.id)}">
        <span class="lokas-badge">${escapeHtml(loka.category)}</span>
        <span class="lokas-badge lokas-guna" data-guna="${escapeHtml(loka.guna)}">${escapeHtml(loka.guna)}</span>
        <h2>${escapeHtml(loka.name)}</h2>
        <p>${escapeHtml(loka.desc)}</p>
        <small>${escapeHtml(loka.scriptures)}</small>
        <div class="lokas-metrics">
          <span>S ${profile.sattva}</span>
          <span>R ${profile.rajas}</span>
          <span>T ${profile.tamas}</span>
          <span>Noise ${formatValue(profile.noise)}</span>
          <span>Coherence ${formatValue(profile.coherenceBias)}</span>
        </div>
      </article>
    `;
  }).join("");

  qsa("[data-loka-id]").forEach((card) => {
    on(card, "click", () => {
      selectedLoka = lokasData.find((loka) => loka.id === card.dataset.lokaId) || null;
      if (selectedLoka) {
        gunaState = {
          Sattva: selectedLoka.collapseProfile.sattva,
          Rajas: selectedLoka.collapseProfile.rajas,
          Tamas: selectedLoka.collapseProfile.tamas
        };
      }
      renderLokas();
      renderGunaMixer();
      updateStudioMessage(selectedLoka ? `Selected: ${selectedLoka.name}` : "No Loka selected.");
    });
  });
}

export function renderNarakas() {
  const target = qs("#narakas-table");
  if (!target) return;

  const results = filterNarakas();
  if (!results.length) {
    writeEmpty(target, "No Narakas match this search.");
    return;
  }

  target.innerHTML = `
    <table class="lokas-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Guna</th>
          <th>Cause</th>
          <th>Consequence</th>
        </tr>
      </thead>
      <tbody>
        ${results.map((naraka) => `
          <tr>
            <td>${naraka.id}</td>
            <td><strong>${escapeHtml(naraka.name)}</strong></td>
            <td><span class="lokas-badge lokas-guna" data-guna="${escapeHtml(naraka.guna)}">${escapeHtml(naraka.guna)}</span></td>
            <td>${escapeHtml(naraka.cause)}</td>
            <td>${escapeHtml(naraka.consequence)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

export function renderAparadhas() {
  const target = qs("#aparadhas-panel");
  if (!target) return;

  const { namaAparadhas, sevaAparadhas } = filterAparadhas();
  const namaMarkup = namaAparadhas.length
    ? namaAparadhas.map((item) => `
      <article class="lokas-card">
        <span class="lokas-badge">${item.id}</span>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.note)}</p>
      </article>
    `).join("")
    : `<div class="lokas-empty">No Nama Aparadhas match this search.</div>`;

  const sevaMarkup = sevaAparadhas.length
    ? `<ol class="lokas-list">${sevaAparadhas.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`
    : `<div class="lokas-empty">No Seva Aparadhas match this search.</div>`;

  target.innerHTML = `
    <div class="lokas-aparadhas">
      <section>
        <h2>10 Nāmāparādhas</h2>
        <div class="lokas-grid">${namaMarkup}</div>
      </section>
      <section class="lokas-card">
        <h2>32 Seva-Aparādhas</h2>
        ${sevaMarkup}
      </section>
    </div>
  `;
}

export function renderGunaMixer() {
  const target = qs("#guna-mixer");
  if (!target) return;

  const derived = deriveGunaProfile();
  const profileEntries = filterGunas();
  const profilesMarkup = profileEntries.length
    ? profileEntries.map(([key, profile]) => `
      <article class="lokas-card">
        <span class="lokas-badge lokas-guna" data-guna="${escapeHtml(key)}">${escapeHtml(key)}</span>
        <h3>${escapeHtml(profile.title)}</h3>
        <ul class="lokas-list">${profile.traits.map((trait) => `<li>${escapeHtml(trait)}</li>`).join("")}</ul>
      </article>
    `).join("")
    : `<div class="lokas-empty">No Guna profiles match this search.</div>`;

  target.innerHTML = `
    <div class="lokas-guna-layout">
      <section class="lokas-card">
        <h2>Preview-only Guna Mixer</h2>
        ${Object.keys(gunaState).map((key) => `
          <label class="lokas-slider">
            <span>${escapeHtml(key)} <strong>${gunaState[key]}%</strong></span>
            <input type="range" min="0" max="100" value="${gunaState[key]}" data-guna-slider="${escapeHtml(key)}">
          </label>
        `).join("")}
      </section>
      <section class="lokas-card">
        <h2>Derived Profile</h2>
        <div class="lokas-metrics lokas-metrics-large">
          <span>noise ${formatValue(derived.noise)}</span>
          <span>coupling ${formatValue(derived.coupling)}</span>
          <span>coherenceBias ${formatValue(derived.coherenceBias)}</span>
          <span>fragmentationBias ${formatValue(derived.fragmentationBias)}</span>
        </div>
        <p class="lokas-muted">Preview only. No engine calls are made from this mixer.</p>
      </section>
    </div>
    <div class="lokas-grid">${profilesMarkup}</div>
  `;

  qsa("[data-guna-slider]").forEach((slider) => {
    on(slider, "input", () => {
      normalizeGunas(slider.dataset.gunaSlider, slider.value);
      renderGunaMixer();
    });
  });
}

async function copyPrompt(prompt) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(prompt);
    return "copied";
  }

  alert(prompt);
  return "alerted";
}

export function renderPromptTemplates() {
  const target = qs("#prompt-templates");
  if (!target) return;

  const results = filterPrompts();
  if (!results.length) {
    writeEmpty(target, "No prompt templates match this search.");
    return;
  }

  target.innerHTML = results.map(([key, template]) => `
    <article class="lokas-card is-selectable" data-prompt-key="${escapeHtml(key)}">
      <span class="lokas-badge lokas-guna" data-guna="${escapeHtml(template.guna)}">${escapeHtml(template.guna)}</span>
      <span class="lokas-badge">${escapeHtml(template.suggestedEngine)}</span>
      <h3>${escapeHtml(template.title)}</h3>
      <pre>${escapeHtml(template.prompt)}</pre>
      <small>${escapeHtml(template.physicsHint)}</small>
      <small>Click to copy prompt.</small>
    </article>
  `).join("");

  qsa("[data-prompt-key]").forEach((card) => {
    on(card, "click", () => {
      const template = promptTemplates[card.dataset.promptKey];
      if (template) {
        copyPrompt(template.prompt)
          .then((result) => {
            updateStudioMessage(result === "copied"
              ? "Prompt copied to clipboard."
              : "Clipboard unavailable. Prompt displayed in an alert.");
          })
          .catch(() => alert(template.prompt));
      }
    });
  });
}

export function renderPingalaPanel() {
  const target = qs("#pingala-panel");
  if (!target) return;

  const results = filterPingala();
  if (!results.length) {
    writeEmpty(target, "No Pingala patterns match this search.");
    return;
  }

  target.innerHTML = results.map((pattern) => {
    const matraTotal = pattern.matras.reduce((sum, amount) => sum + amount, 0);
    return `
      <article class="lokas-card">
        <span class="lokas-badge">${escapeHtml(pattern.id)}</span>
        <h2>${escapeHtml(pattern.name)}</h2>
        <p>${escapeHtml(pattern.legend)}</p>
        <div class="lokas-pingala-grid">
          ${pattern.pattern.map((value, index) => `
            <button class="lokas-pingala-cell" type="button" data-pingala-cell="${index}">
              <strong>${value === 0 ? "Laghu" : "Guru"}</strong>
              <span>${pattern.matras[index]} mātra${pattern.matras[index] === 1 ? "" : "s"}</span>
            </button>
          `).join("")}
        </div>
        <div class="lokas-note">Mātra total: <strong>${matraTotal}</strong>. Placeholder-safe pattern only; no exact shloka matching is claimed.</div>
      </article>
    `;
  }).join("");
}

function updateStudioMessage(message) {
  const messageNode = qs("[data-studio-message]");
  if (messageNode) messageNode.textContent = message;
}

function renderCurrentPanel() {
  if (currentPanel === "lokas") renderLokas();
  if (currentPanel === "narakas") renderNarakas();
  if (currentPanel === "aparadhas") renderAparadhas();
  if (currentPanel === "gunas") renderGunaMixer();
  if (currentPanel === "studio") renderPromptTemplates();
  if (currentPanel === "pingala") renderPingalaPanel();
}

function setupSearch() {
  const input = qs("#lokas-search");
  on(input, "input", () => {
    searchTerm = input.value.trim().toLowerCase();
    renderCurrentPanel();
  });
}

function setupInternalTabs() {
  qsa("[data-lokas-panel-target]").forEach((tab) => {
    on(tab, "click", () => {
      currentPanel = tab.dataset.lokasPanelTarget || "lokas";
      qsa("[data-lokas-panel-target]").forEach((item) => {
        item.classList.toggle("active", item === tab);
      });
      qsa("[data-panel]").forEach((panel) => {
        panel.classList.toggle("hidden", panel.dataset.panel !== currentPanel);
      });
      renderCurrentPanel();
    });
  });
}

function setupStudioActions() {
  on(qs('[data-action="generate-selected"]'), "click", () => {
    if (!selectedLoka) {
      updateStudioMessage("Select a Loka card first, then generate its prompt.");
      return;
    }

    const template = promptTemplates[selectedLoka.promptKey];
    if (!template) {
      updateStudioMessage(`No prompt template exists yet for ${selectedLoka.name}.`);
      return;
    }

    const preview = [
      template.title,
      "",
      template.prompt,
      "",
      `Physics hint: ${template.physicsHint}`,
      `Suggested engine: ${template.suggestedEngine}`
    ].join("\n");
    copyPrompt(preview)
      .then((result) => {
        const copyStatus = result === "copied"
          ? "Prompt copied to clipboard."
          : "Clipboard unavailable. Prompt displayed in an alert.";
        updateStudioMessage(`${preview}\n\n${copyStatus}`);
      })
      .catch(() => {
        alert(preview);
        updateStudioMessage(preview);
      });
  });

  on(qs('[data-action="run-simulation"]'), "click", () => {
    updateStudioMessage("Simulation connection placeholder: future versions can route this Loka profile into Collapse Lab, Nakshatra Engine, Sonic Mandala, or Anumana Engine.");
  });
}

export async function init(root) {
  mountNode = root?.querySelector?.("[data-lokas-studio]") || root || document.querySelector("[data-lokas-studio]");
  currentPanel = "lokas";
  searchTerm = "";
  selectedLoka = null;
  listeners = [];
  gunaState = { Sattva: 60, Rajas: 25, Tamas: 15 };

  if (!mountNode) return;

  setupSearch();
  setupInternalTabs();
  setupStudioActions();
  renderLokas();
  renderNarakas();
  renderAparadhas();
  renderGunaMixer();
  renderPromptTemplates();
  renderPingalaPanel();
}

export function destroy() {
  listeners.forEach(({ target, event, handler }) => target.removeEventListener(event, handler));
  listeners = [];
  mountNode = null;
  currentPanel = "lokas";
  searchTerm = "";
  selectedLoka = null;
  gunaState = { Sattva: 60, Rajas: 25, Tamas: 15 };
}

export const tool = { init, destroy };
export default { init, destroy };
