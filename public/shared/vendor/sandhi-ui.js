/* ═══════════════════════════════════════════════════════════════════════════
   Sandhi UI — Full-sentence sandhi chain panel
   ═══════════════════════════════════════════════════════════════════════════
   Adds a second form to the Sandhi sub-view that consumes SANDHI_ENGINE
   and renders a junction-by-junction rule tree.

   Exposes one function:  SANDHI_UI.appendChainForm(fragment, el, renderError)

   Called by app.js inside buildSandhiSubView() right before `return fragment`.
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  function renderChainResult(node, result) {
    var nodes = [];

    // Final chained result
    nodes.push(createEl('div', { class: 'output-result', style: 'margin-bottom: 1rem;' }, [
      createEl('div', { class: 'output-eq' }, [
        createEl('span', { class: 'in', text: result.original }),
        createEl('span', { class: 'arrow', text: ' → ' }),
        createEl('span', { class: 'out', text: result.result }),
      ]),
    ]));

    // Summary badges
    var resolved   = result.junctions.filter(function (j) { return j.status === 'resolved'; }).length;
    var unchanged  = result.junctions.filter(function (j) { return j.status === 'unchanged'; }).length;
    var unresolved = result.junctions.filter(function (j) { return j.status === 'unresolved'; }).length;

    var badges = [createEl('span', { class: 'rule-tag', text: resolved + ' resolved' })];
    if (unchanged)  badges.push(createEl('span', { class: 'rule-tag rule-none', text: unchanged + ' unchanged' }));
    if (unresolved) badges.push(createEl('span', {
      class: 'rule-tag',
      style: 'background: rgba(248,113,113,0.12); border-color: rgba(248,113,113,0.3); color: #f87171;',
      text: unresolved + ' unresolved'
    }));
    nodes.push(createEl('div', { class: 'paradigm-header' }, badges));

    // Junction list
    var junctionList = createEl('div', { class: 'sandhi-junctions' });

    result.junctions.forEach(function (j, i) {
      var statusClass = j.status === 'resolved' ? 'sj-resolved'
                      : j.status === 'unchanged' ? 'sj-unchanged'
                      : 'sj-unresolved';

      var children = [
        createEl('div', { class: 'sj-head' }, [
          createEl('span', { class: 'sj-num', text: 'Junction ' + (i + 1) }),
          createEl('span', { class: 'sj-status', text: j.status }),
        ]),
        createEl('div', { class: 'sj-equation' }, [
          createEl('span', { class: 'sj-before', text: j.left + ' + ' + j.right }),
          createEl('span', { class: 'sj-arrow', text: ' → ' }),
          createEl('span', { class: 'sj-after', text: j.result }),
        ]),
      ];

      if (j.chain && j.chain.length) {
        var chainChildren = [createEl('span', { class: 'sj-chain-label', text: 'Sūtra chain: ' })];
        j.chain.forEach(function (s, k) {
          if (k > 0) chainChildren.push(createEl('span', { class: 'sj-chain-sep', text: ' → ' }));
          chainChildren.push(createEl('code', { class: 'sj-sutra', text: s }));
        });
        children.push(createEl('div', { class: 'sj-chain' }, chainChildren));
      }

      if (j.name && j.name !== '—') {
        children.push(createEl('div', { class: 'sj-name' }, j.name));
      }

      junctionList.appendChild(createEl('div', { class: 'sandhi-junction ' + statusClass }, children));
    });

    nodes.push(junctionList);

    node.replaceChildren.apply(node, nodes);
    node.classList.add('has-success');
    node.classList.remove('has-error');
  }

  // We pull `el` and `renderError` from the caller because app.js keeps them private.
  var createEl = null;
  var renderErrorFn = null;

  function appendChainForm(fragment, elFn, renderErrorRef) {
    createEl = elFn;
    renderErrorFn = renderErrorRef;

    // --- Full-sentence sandhi chain form ---
    var chainInput = createEl('textarea', { attrs: {
      rows: '3', maxlength: '2000', spellcheck: 'false',
      placeholder: 'rāmaḥ gacchati iti'
    } });
    chainInput.value = 'rāmaḥ gacchati iti';

    var chainOutput = createEl('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      createEl('p', { class: 'placeholder', text: 'Chained result and rule tree will appear here.' }),
    ]);

    var chainForm = createEl('form', { class: 'form' }, [
      createEl('label', {}, [
        createEl('span', { class: 'label', text: 'Sanskrit tokens (IAST, space-separated)' }),
        chainInput,
        createEl('small', { class: 'hint', text: 'Each space is a word boundary — e.g. rāmaḥ gacchati iti' }),
      ]),
      createEl('div', { class: 'form-actions' }, [
        createEl('button', { class: 'btn btn-primary', text: 'Apply Sandhi Chain', attrs: { type: 'submit' } }),
      ]),
    ]);

    var sectionChain = createEl('section', { class: 'panel' }, [
      createEl('header', { class: 'panel-head' }, [
        createEl('h3', { text: 'Full-Sentence Sandhi Chain' }),
        createEl('p', { class: 'panel-sub', text: 'Client-side Pāṇinian joiner — 22 core rules, full sūtra chains, honest unresolved flags.' }),
      ]),
      chainForm,
      chainOutput,
    ]);

    fragment.appendChild(sectionChain);

    chainForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var raw = chainInput.value.trim();
      if (!raw) {
        renderErrorFn(chainOutput, 'Enter tokens to chain.');
        return;
      }
      if (!window.SANDHI_ENGINE) {
        renderErrorFn(chainOutput, 'Sandhi engine not loaded.');
        return;
      }
      var tokens = raw.split(/\s+/).filter(Boolean);
      if (tokens.length < 2) {
        renderErrorFn(chainOutput, 'Enter at least two tokens separated by spaces.');
        return;
      }
      var result = window.SANDHI_ENGINE.applyChain(tokens);
      renderChainResult(chainOutput, result);
    });
  }

  window.SANDHI_UI = {
    version: '1.0.0',
    appendChainForm: appendChainForm
  };
})();