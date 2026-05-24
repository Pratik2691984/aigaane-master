const SLIDERS = [
  { key: "noise", label: "Noise", min: 0, max: 1, step: 0.01 },
  { key: "coupling", label: "Coupling", min: 0, max: 5, step: 0.01 },
  { key: "gamma", label: "Gamma", min: 0.3, max: 1.2, step: 0.01 },
  { key: "speed", label: "Speed", min: 0.25, max: 3, step: 0.01 }
];

export function ControlsPanel(
  root,
  state,
  onChange,
  onReset,
  onToggle,
  onExportJson,
  onExportCsv,
  replay,
  summary,
  onToggleReplay,
  onScrubReplay,
  onPlayReplay,
  onPauseReplay,
  onStepReplayBack,
  onStepReplayForward
) {
  const replayMax = Math.max(0, (replay?.total || 0) - 1);
  const replayIndex = Math.max(0, Math.min(replay?.index || 0, replayMax));
  const replayDisabled = replayMax === 0 ? "disabled" : "";
  const liveDisabled = replay?.active ? "disabled" : "";
  root.innerHTML = `
    <section class="collapse-card controls-panel">
      <div class="collapse-card-header compact">
        <div>
          <h3>Controls</h3>
          <p>Live collapse parameters</p>
        </div>
        <div class="button-row">
          <button type="button" class="collapse-button" data-action="toggle" ${liveDisabled}>${state.running ? "Pause" : "Play"}</button>
          <button type="button" class="collapse-button secondary" data-action="reset">Reset</button>
          <button type="button" class="collapse-button secondary" data-action="export-json">Export JSON</button>
          <button type="button" class="collapse-button secondary" data-action="export-csv">Export CSV</button>
          <button type="button" class="collapse-button secondary ${replay?.active ? "active" : ""}" data-action="replay-toggle">${replay?.active ? "Exit Replay" : "Replay"}</button>
        </div>
      </div>
      <div class="session-summary">
        <div><span>Residual</span><b>${(summary?.currentResidualMass ?? 0).toFixed(3)}</b></div>
        <div><span>Min Residual</span><b>${(summary?.minResidualMass ?? 0).toFixed(3)}</b></div>
        <div><span>Pre-collapse</span><b>${(summary?.preCollapseTime ?? 0).toFixed(1)}s</b></div>
        <div><span>Collapses</span><b>${summary?.collapseCount ?? 0}</b></div>
      </div>
      <p class="export-note">After export, move JSON files to experimental_logs/json/sessions and CSV files to experimental_logs/csv/metrics.</p>
      <div class="slider-stack">
        ${SLIDERS.map(slider => `
          <label class="collapse-slider">
            <span>${slider.label}<b data-readout="${slider.key}">${state[slider.key].toFixed(2)}</b></span>
            <input
              type="range"
              min="${slider.min}"
              max="${slider.max}"
              step="${slider.step}"
              value="${state[slider.key]}"
              data-key="${slider.key}"
              aria-label="${slider.label}"
              ${liveDisabled}
            />
          </label>
        `).join("")}
      </div>
      <div class="replay-panel ${replay?.active ? "active" : ""}">
        <div class="replay-actions">
          <button type="button" class="collapse-button secondary" data-action="replay-back" ${replayDisabled}>Back</button>
          <button type="button" class="collapse-button secondary" data-action="replay-play" ${replayDisabled}>Play Replay</button>
          <button type="button" class="collapse-button secondary" data-action="replay-pause" ${replayDisabled}>Pause Replay</button>
          <button type="button" class="collapse-button secondary" data-action="replay-forward" ${replayDisabled}>Forward</button>
        </div>
        <label class="collapse-slider replay-scrub">
          <span>Replay Frame<b>${replayIndex + (replay?.total ? 1 : 0)} / ${replay?.total || 0}</b></span>
          <input
            type="range"
            min="0"
            max="${replayMax}"
            step="1"
            value="${replayIndex}"
            data-action="replay-scrub"
            aria-label="Replay Frame"
            ${replayDisabled}
          />
        </label>
      </div>
    </section>
  `;

  root.querySelectorAll("input[type='range']").forEach(input => {
    input.addEventListener("input", () => {
      const key = input.dataset.key;
      const value = Number(input.value);
      const readout = root.querySelector(`[data-readout="${key}"]`);
      if (readout) readout.textContent = value.toFixed(2);
      onChange({ [key]: value });
    });
  });

  root.querySelector("[data-action='reset']")?.addEventListener("click", onReset);
  root.querySelector("[data-action='toggle']")?.addEventListener("click", onToggle);
  root.querySelector("[data-action='export-json']")?.addEventListener("click", onExportJson);
  root.querySelector("[data-action='export-csv']")?.addEventListener("click", onExportCsv);
  root.querySelector("[data-action='replay-toggle']")?.addEventListener("click", onToggleReplay);
  root.querySelector("[data-action='replay-play']")?.addEventListener("click", onPlayReplay);
  root.querySelector("[data-action='replay-pause']")?.addEventListener("click", onPauseReplay);
  root.querySelector("[data-action='replay-back']")?.addEventListener("click", onStepReplayBack);
  root.querySelector("[data-action='replay-forward']")?.addEventListener("click", onStepReplayForward);
  root.querySelector("[data-action='replay-scrub']")?.addEventListener("input", event => {
    onScrubReplay(Number(event.target.value));
  });
}
