// C:\aigaane-master\ui\tabs\astronomy\controller.js
// Astronomy Tab – Pure Projection of Canonical State

let mountNode = null;

const NAKSHATRA_LIST = [
  "Ashvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣā", "Ārdrā", "Punarvasu", "Puṣya", "Āśleṣā",
  "Maghā", "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Chitrā", "Svāti", "Viśākhā", "Anurādhā", "Jyeṣṭhā",
  "Mūla", "Pūrva Aṣāḍhā", "Uttara Aṣāḍhā", "Śravaṇā", "Dhanisṭhā", "Śatabhiṣā", "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"
];

function renderWheel(padaId) {
  const wheel = mountNode?.querySelector('#nakshatraWheel');
  if (!wheel) return;
  
  const nakshatraIndex = Math.floor(padaId / 4);
  
  if (wheel.children.length === 0) {
    for (let i = 0; i < NAKSHATRA_LIST.length; i++) {
      const div = document.createElement('div');
      div.className = 'nakshatra-segment';
      div.textContent = (i + 1).toString();
      div.title = NAKSHATRA_LIST[i];
      wheel.appendChild(div);
    }
  }
  
  Array.from(wheel.children).forEach((child, idx) => {
    child.classList.toggle('active', idx === nakshatraIndex);
  });
}

function updateDetails(state) {
  if (!state) return;
  
  const padaId = state.pada_id;  // 0-based (0-107)
  const displayPada = padaId + 1;  // Convert to 1-based for display
  const quarter = (padaId % 4) + 1;
  const nakshatraIndex = Math.floor(padaId / 4);
  const nakshatraName = NAKSHATRA_LIST[nakshatraIndex];
  
  const padaEl = mountNode?.querySelector('#padaValue');
  const nakshatraEl = mountNode?.querySelector('#nakshatraName');
  const quarterEl = mountNode?.querySelector('#padaQuarter');
  
  if (padaEl) padaEl.innerText = displayPada;
  if (nakshatraEl) nakshatraEl.innerText = nakshatraName;
  if (quarterEl) quarterEl.innerText = quarter;
}

export function init(node) {
  mountNode = node;
  console.log('[Astronomy] Tab mounted');
}

export function render(state, node) {
  if (node) mountNode = node;
  if (!mountNode) return;
  if (!state) {
    console.error('[Astronomy] State is undefined!');
    return;
  }
  
  const padaId = state.pada_id;
  console.log('[Astronomy] render - pada_id:', padaId, 'nakshatra_id:', state.nakshatra_id);
  
  renderWheel(padaId);
  updateDetails(state);  // ✅ PASS THE FULL STATE, NOT JUST padaId
}

export function destroy() {
  mountNode = null;
  console.log('[Astronomy] Tab destroyed');
}