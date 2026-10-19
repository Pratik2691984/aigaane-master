/* ═══════════════════════════════════════════════════════════════════════════
   Sthāpatyaveda Studio — React Component
   ═══════════════════════════════════════════════════════════════════════════
   - 4 tabs: Maṇḍala · Directions · Māna · About
   - Interactive 9×9 Vāstu Puruṣa Maṇḍala with 3 mode overlays
   - 8-direction compass + home facing selector
   - Aṅgula/Hasta/Daṇḍa/Yojana converter + temple proportions
   - Vault: sthapatyaveda.vault.v1
   - No JSX, no Babel
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var React = window.React;
  var ReactDOM = window.ReactDOM;
  var DATA = window.STHAPATYAVEDA_DATA;
  if (!React || !ReactDOM || !DATA) {
    console.error('[Sthāpatyaveda] Missing React, ReactDOM, or STHAPATYAVEDA_DATA');
    return;
  }

  var h = React.createElement;
  var useState = React.useState;
  var useEffect = React.useEffect;
  var useMemo = React.useMemo;
  var useReducer = React.useReducer;

  /* ═══════════════════════════════════════════════════════════════════════
     VAULT
     ═══════════════════════════════════════════════════════════════════════ */
  var VAULT_KEY = 'sthapatyaveda.vault.v1';

  function loadVault() {
    try {
      var raw = localStorage.getItem(VAULT_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  function saveVault(state) {
    try {
      localStorage.setItem(VAULT_KEY, JSON.stringify({
        mandalaMode: state.mandalaMode,
        facingDirection: state.facingDirection,
        converterFrom: state.converterFrom,
        converterTo: state.converterTo,
        templeScale: state.templeScale,
        savedAt: Date.now()
      }));
    } catch (e) {}
  }

  /* ═══════════════════════════════════════════════════════════════════════
     HELPERS
     ═══════════════════════════════════════════════════════════════════════ */
  function findPada(num) {
    for (var i = 0; i < DATA.padas.length; i++) {
      if (DATA.padas[i].num === num) return DATA.padas[i];
    }
    return null;
  }

  function findDirection(id) {
    for (var i = 0; i < DATA.directions.length; i++) {
      if (DATA.directions[i].id === id) return DATA.directions[i];
    }
    return null;
  }

  function findUnit(id) {
    for (var i = 0; i < DATA.units.length; i++) {
      if (DATA.units[i].id === id) return DATA.units[i];
    }
    return null;
  }

  function convertUnits(value, fromId, toId) {
    var from = findUnit(fromId);
    var to = findUnit(toId);
    if (!from || !to) return 0;
    return value * from.toAngula / to.toAngula;
  }

  function formatNumber(n) {
    if (!Number.isFinite(n)) return '—';
    if (Math.abs(n) >= 1000) return n.toFixed(2);
    if (Math.abs(n) >= 1) return n.toFixed(3);
    return n.toFixed(5);
  }

  /* ═══════════════════════════════════════════════════════════════════════
     REDUCER
     ═══════════════════════════════════════════════════════════════════════ */
  var initial = (function () {
    var v = loadVault() || {};
    var validModes = ['house', 'temple', 'cosmic'];
    var validDirIds = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'];
    var validUnitIds = DATA.units.map(function (u) { return u.id; });
    var validScales = ['small', 'medium', 'large', 'grand'];

    return {
      tab: 'mandala',
      mandalaMode: validModes.indexOf(v.mandalaMode) !== -1 ? v.mandalaMode : 'house',
      selectedPada: null,
      selectedDirection: null,
      facingDirection: validDirIds.indexOf(v.facingDirection) !== -1 ? v.facingDirection : null,
      converterInput: 1,
      converterFrom: validUnitIds.indexOf(v.converterFrom) !== -1 ? v.converterFrom : 'hasta',
      converterTo:   validUnitIds.indexOf(v.converterTo)   !== -1 ? v.converterTo   : 'angula',
      templeScale:   validScales.indexOf(v.templeScale)    !== -1 ? v.templeScale   : 'medium'
    };
  })();

  function reducer(state, action) {
    switch (action.type) {
      case 'setTab':              return Object.assign({}, state, { tab: action.value });
      case 'setMandalaMode':      return Object.assign({}, state, { mandalaMode: action.value });
      case 'selectPada':          return Object.assign({}, state, { selectedPada: state.selectedPada === action.value ? null : action.value });
      case 'selectDirection':     return Object.assign({}, state, { selectedDirection: state.selectedDirection === action.value ? null : action.value });
      case 'setFacingDirection':  return Object.assign({}, state, { facingDirection: state.facingDirection === action.value ? null : action.value });
      case 'setConverterInput':   return Object.assign({}, state, { converterInput: action.value });
      case 'setConverterFrom':    return Object.assign({}, state, { converterFrom: action.value });
      case 'setConverterTo':      return Object.assign({}, state, { converterTo: action.value });
      case 'setTempleScale':      return Object.assign({}, state, { templeScale: action.value });
      case 'swapConverter':       return Object.assign({}, state, { converterFrom: state.converterTo, converterTo: state.converterFrom });
      default: return state;
    }
  }

  /* ═══════════════════════════════════════════════════════════════════════
     COMPONENTS — shared
     ═══════════════════════════════════════════════════════════════════════ */
  function DirectionBadge(props) {
    var d = findDirection(props.id);
    if (!d) return null;
    return h('span', {
      className: 'st-badge',
      style: { color: d.color, borderColor: d.color, background: 'transparent' }
    }, props.label || d.name);
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 1 — MAṆḌALA
     ═══════════════════════════════════════════════════════════════════════ */
  function MandalaTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;

    var mode = state.mandalaMode;
    var selectedPada = state.selectedPada ? findPada(state.selectedPada) : null;

    return h('div', null,
      h('div', { className: 'st-panel' },
        h('div', { className: 'st-panel-title' }, 'Vāstu Puruṣa Maṇḍala — 81 Padas'),
        h('div', { style: { display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' } },
          h('label', { style: { fontSize: '0.75rem', color: 'var(--st-text-muted)' } }, 'Overlay:'),
          [
            { id: 'house',  label: 'House (Gṛha)' },
            { id: 'temple', label: 'Temple (Devālaya)' },
            { id: 'cosmic', label: 'Cosmic (Puruṣa)' }
          ].map(function (m) {
            return h('button', {
              key: m.id,
              className: 'st-nav-btn' + (mode === m.id ? ' active' : ''),
              onClick: function () { dispatch({ type: 'setMandalaMode', value: m.id }); }
            }, m.label);
          })
        ),
        h('div', { style: { fontSize: '0.78rem', color: 'var(--st-text-muted)', marginTop: '0.5rem', lineHeight: 1.6 } },
          'Click any cell to see its presiding deity and recommended placements. The grid is oriented with North at the top.'
        )
      ),

      h('div', { className: 'st-mandala-wrap' },
        h('div', { className: 'st-mandala' },
          DATA.padas.map(function (p) {
            var isSelected = state.selectedPada === p.num;
            return h('button', {
              key: p.num,
              className: 'st-pada dir-' + p.direction.toLowerCase() + (isSelected ? ' selected' : ''),
              onClick: function () { dispatch({ type: 'selectPada', value: p.num }); },
              title: p.deity + ' · ' + p.direction.toUpperCase()
            },
              h('span', { className: 'st-pada-num' }, p.num),
              h('span', { className: 'st-pada-deity' }, p.deity)
            );
          })
        )
      ),

      selectedPada ? h(PadaDetail, { pada: selectedPada, mode: mode }) : null
    );
  }

  function PadaDetail(props) {
    var p = props.pada;
    var m = props.mode;
    var d = findDirection(p.direction.toLowerCase());

    var useText = p[m] ? p[m].use : '—';
    var avoidText = p[m] ? p[m].avoid : '—';

    return h('div', { className: 'st-pada-detail' },
      h('div', { className: 'st-pada-detail-head' },
        h('span', { className: 'st-pada-detail-name' }, p.deity),
        h('span', { className: 'st-pada-detail-dev indic' }, p.dev),
        h('span', { className: 'st-pada-detail-iast' }, p.iast),
        d ? h(DirectionBadge, { id: d.id, label: d.name }) : null
      ),
      h('div', { className: 'st-pada-detail-row' },
        h('span', { className: 'st-pada-detail-label' }, 'Pada'),
        h('span', null, '#' + p.num + ' (row ' + p.row + ', col ' + p.col + ')')
      ),
      h('div', { className: 'st-pada-detail-row' },
        h('span', { className: 'st-pada-detail-label' }, 'Direction'),
        h('span', null, d ? d.name + ' (' + d.iast + ') — ' + d.element : p.direction.toUpperCase())
      ),
      h('div', { className: 'st-pada-detail-row' },
        h('span', { className: 'st-pada-detail-label' }, 'Mode'),
        h('span', null, m === 'house' ? 'House (Gṛha)' : m === 'temple' ? 'Temple (Devālaya)' : 'Cosmic (Puruṣa)')
      ),
      h('div', { className: 'st-pada-detail-row' },
        h('span', { className: 'st-pada-detail-label' }, 'Recommended'),
        h('span', null, useText)
      ),
      h('div', { className: 'st-pada-detail-row' },
        h('span', { className: 'st-pada-detail-label' }, 'Avoid'),
        h('span', null, avoidText)
      ),
      d ? h('div', { className: 'st-pada-detail-row' },
        h('span', { className: 'st-pada-detail-label' }, 'Deity/Planet'),
        h('span', null, d.deity + ' · ' + d.planet)
      ) : null
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 2 — DIRECTIONS
     ═══════════════════════════════════════════════════════════════════════ */
  function DirectionsTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;

    var selectedDir = state.selectedDirection ? findDirection(state.selectedDirection) : null;

    var ordered = ['nw', 'n', 'ne', 'w', 'c', 'e', 'sw', 's', 'se'];
    var compassMap = ordered.map(function (id) {
      return { id: id, dir: findDirection(id) };
    }).filter(function (x) { return x.dir; });

    return h('div', null,
      h('div', { className: 'st-panel' },
        h('div', { className: 'st-panel-title' }, 'Vāstu Compass — 8 Directions + Center'),
        h('div', { style: { fontSize: '0.78rem', color: 'var(--st-text-muted)', lineHeight: 1.6, marginBottom: '0.75rem' } },
          'Click a direction to see its element, presiding deity, planet, and recommended placements.'
        ),
        h('div', { style: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' } },
          h('label', { style: { fontSize: '0.72rem', color: 'var(--st-text-muted)' } }, 'My home faces:'),
          ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'].map(function (id) {
            var d = findDirection(id);
            var isActive = state.facingDirection === id;
            return h('button', {
              key: id,
              className: 'st-nav-btn' + (isActive ? ' active' : ''),
              onClick: function () { dispatch({ type: 'setFacingDirection', value: id }); }
            }, d.name);
          }),
          state.facingDirection ? h('button', {
            className: 'st-btn',
            style: { fontSize: '0.68rem', padding: '0.3rem 0.7rem' },
            onClick: function () { dispatch({ type: 'setFacingDirection', value: state.facingDirection }); }
          }, 'Clear') : null
        )
      ),

      h('div', { className: 'st-compass' },
        compassMap.map(function (x) {
          var d = x.dir;
          var isSelected = state.selectedDirection === d.id;
          var isFacing = state.facingDirection === d.id;
          var cls = 'st-dir-card pos-' + d.id;
          if (isSelected) cls += ' selected';
          if (isFacing) cls += ' facing';
          if (d.id === 'c') cls += ' center';

          return h('button', {
            key: d.id,
            className: cls,
            style: { borderColor: isSelected || isFacing ? d.color : undefined },
            onClick: function () { dispatch({ type: 'selectDirection', value: d.id }); }
          },
            h('div', { className: 'st-dir-name', style: { color: d.color } }, d.name),
            h('div', { className: 'st-dir-dev indic' }, d.dev),
            h('div', { className: 'st-dir-iast' }, d.iast),
            h('div', { className: 'st-dir-meta' },
              h('div', null, h('strong', null, 'Element: '), d.element),
              h('div', null, h('strong', null, 'Deity: '), d.deity),
              h('div', null, h('strong', null, 'Planet: '), d.planet)
            )
          );
        })
      ),

      selectedDir ? h('div', { className: 'st-dir-detail', style: { borderColor: selectedDir.color } },
        h('div', { className: 'st-pada-detail-head' },
          h('span', { className: 'st-pada-detail-name', style: { color: selectedDir.color } }, selectedDir.name),
          h('span', { className: 'st-pada-detail-dev indic' }, selectedDir.dev),
          h('span', { className: 'st-pada-detail-iast' }, selectedDir.iast)
        ),
        h('div', { style: { fontSize: '0.85rem', color: 'var(--st-text-muted)', marginBottom: '0.75rem' } },
          selectedDir.degreeRange
        ),
        h('h4', null, 'Best For'),
        h('ul', null, selectedDir.bestFor.map(function (b, i) { return h('li', { key: i }, b); })),
        h('h4', null, 'Avoid'),
        h('ul', null, selectedDir.avoidFor.map(function (a, i) { return h('li', { key: i }, a); })),
        h('div', { style: { fontSize: '0.82rem', marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--st-border)', fontStyle: 'italic', color: 'var(--st-text-muted)' } },
          selectedDir.notes
        )
      ) : null,

      state.facingDirection ? h(FacingSummary, { id: state.facingDirection }) : null
    );
  }

  function FacingSummary(props) {
    var d = findDirection(props.id);
    if (!d) return null;
    var oppositeMap = { n: 's', ne: 'sw', e: 'w', se: 'nw', s: 'n', sw: 'ne', w: 'e', nw: 'se' };
    var opp = findDirection(oppositeMap[d.id]);

    return h('div', { className: 'st-panel', style: { borderColor: d.color, borderWidth: '2px' } },
      h('div', { className: 'st-panel-title', style: { color: d.color } }, 'Your Home — ' + d.name + ' Facing'),
      h('div', { style: { fontSize: '0.85rem', lineHeight: 1.6 } },
        h('p', null, 'Your entrance faces ' + d.name + ' (' + d.iast + '), the direction of ' + d.deity + ', ruled by ' + d.planet + '.'),
        h('p', null, h('strong', null, 'Best placements in the ' + d.name + ' zone: '), d.bestFor.join(', ')),
        h('p', null, h('strong', null, 'Avoid in this zone: '), d.avoidFor.join(', ')),
        opp ? h('p', { style: { color: 'var(--st-text-muted)' } },
          'The opposite direction is ' + opp.name + ' (' + opp.iast + ') — where your building "backs onto" — traditionally ideal for heavy storage and the master bedroom.'
        ) : null
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 3 — MĀNA
     ═══════════════════════════════════════════════════════════════════════ */
  function ManaTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;

    var inputVal = parseFloat(state.converterInput) || 0;
    var converted = convertUnits(inputVal, state.converterFrom, state.converterTo);
    var fromUnit = findUnit(state.converterFrom);
    var toUnit = findUnit(state.converterTo);

    var proportions = DATA.templeProportions[state.templeScale];

    return h('div', { className: 'st-mana-grid' },

      // ── Converter ──
      h('div', { className: 'st-panel' },
        h('div', { className: 'st-panel-title' }, 'Māna Converter'),
        h('div', { className: 'st-converter' },
          h('div', { className: 'st-converter-field', style: { flex: 1, minWidth: '120px' } },
            h('label', { className: 'st-converter-label' }, 'Value'),
            h('input', {
              className: 'st-input',
              type: 'number',
              step: 'any',
              value: state.converterInput,
              onChange: function (e) { dispatch({ type: 'setConverterInput', value: e.target.value }); },
              style: { maxWidth: '100%' }
            })
          ),
          h('div', { className: 'st-converter-field' },
            h('label', { className: 'st-converter-label' }, 'From'),
            h('select', {
              className: 'st-select',
              value: state.converterFrom,
              onChange: function (e) { dispatch({ type: 'setConverterFrom', value: e.target.value }); }
            },
              DATA.units.map(function (u) {
                return h('option', { key: u.id, value: u.id }, u.name);
              })
            )
          ),
          h('div', { className: 'st-converter-field', style: { paddingTop: '1.2rem' } },
            h('button', {
              className: 'st-btn',
              onClick: function () { dispatch({ type: 'swapConverter' }); },
              title: 'Swap units'
            }, '⇄')
          ),
          h('div', { className: 'st-converter-field' },
            h('label', { className: 'st-converter-label' }, 'To'),
            h('select', {
              className: 'st-select',
              value: state.converterTo,
              onChange: function (e) { dispatch({ type: 'setConverterTo', value: e.target.value }); }
            },
              DATA.units.map(function (u) {
                return h('option', { key: u.id, value: u.id }, u.name);
              })
            )
          )
        ),

        h('div', { className: 'st-converter-result' },
          formatNumber(converted) + ' ' + (toUnit ? toUnit.name : '')
        ),
        h('div', { style: { fontSize: '0.72rem', color: 'var(--st-text-muted)', textAlign: 'center', marginTop: '-0.5rem', marginBottom: '0.75rem' } },
          inputVal + ' ' + (fromUnit ? fromUnit.name : '') + ' = ' + formatNumber(converted) + ' ' + (toUnit ? toUnit.name : '')
        ),

        h('table', { className: 'st-converter-table' },
          h('thead', null, h('tr', null,
            h('th', null, 'Unit'),
            h('th', null, 'Aṅgulas'),
            h('th', null, 'Metric')
          )),
          h('tbody', null,
            DATA.units.map(function (u) {
              var value = inputVal * (fromUnit ? fromUnit.toAngula : 1) / u.toAngula;
              return h('tr', { key: u.id },
                h('td', null, h('span', { className: 'indic' }, u.dev), ' ', u.name),
                h('td', { className: 'font-mono' }, formatNumber(value)),
                h('td', { style: { color: 'var(--st-text-muted)', fontSize: '0.75rem' } }, u.metric)
              );
            })
          )
        )
      ),

      // ── Temple Proportions ──
      h('div', { className: 'st-panel' },
        h('div', { className: 'st-panel-title' }, 'Temple Proportions'),
        h('div', { style: { marginBottom: '0.75rem' } },
          h('label', { style: { fontSize: '0.72rem', color: 'var(--st-text-muted)', marginRight: '0.5rem' } }, 'Scale:'),
          h('select', {
            className: 'st-select',
            value: state.templeScale,
            onChange: function (e) { dispatch({ type: 'setTempleScale', value: e.target.value }); }
          },
            ['small', 'medium', 'large', 'grand'].map(function (k) {
              return h('option', { key: k, value: k }, DATA.templeProportions[k].label);
            })
          )
        ),
        h('table', { className: 'st-proportions-table' },
          h('thead', null, h('tr', null,
            h('th', null, 'Element'),
            h('th', null, 'Hasta'),
            h('th', null, 'Note')
          )),
          h('tbody', null,
            ['garbhagriha', 'antarala', 'mandapa', 'shikhara', 'gopuram', 'prakara'].map(function (key) {
              var val = proportions[key];
              if (!val) return null;
              return h('tr', { key: key },
                h('td', { style: { textTransform: 'capitalize' } }, key),
                h('td', { className: 'hasta' }, val.hasta + ' hasta'),
                h('td', { className: 'note' }, val.note)
              );
            })
          )
        ),
        h('div', { style: { fontSize: '0.72rem', color: 'var(--st-text-muted)', marginTop: '0.75rem', fontStyle: 'italic', lineHeight: 1.5 } },
          'Values are illustrative conversions based on Mānasāra ratios for educational use. Traditional sthapatis apply local variants.'
        )
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 4 — ABOUT
     ═══════════════════════════════════════════════════════════════════════ */
  function AboutTab() {
    return h('div', null,
      h('div', { className: 'st-panel' },
        h('div', { className: 'st-panel-title' }, 'About Sthāpatyaveda'),
        h('div', { style: { lineHeight: 1.7, fontSize: '0.88rem' } },
          h('p', null,
            'Sthāpatyaveda — "the knowledge of the sthapati (master builder)" — is the Upaveda of architecture, sculpture, and town planning. Its foundational text is the Mānasāra (58 chapters), with the Māyamatam, Samarāṅgaṇa Sūtradhāra, and Viśvakarmā Prakāśa completing the canon.'
          ),
          h('p', null,
            'Every traditional building begins with the Vāstu Puruṣa Maṇḍala — an 81-square cosmic grid that maps the body of the primordial being onto the site. The Brahmā-sthāna (center) is left open; each peripheral pada is assigned a deity and a function. The sthapati aligns walls, doors, and rooms to this grid.'
          ),
          h('p', null,
            h('strong', null, 'Note: '),
            'This studio presents Vāstu Śāstra as a classical tradition. It is not a substitute for a modern architect, structural engineer, or building code compliance.'
          )
        )
      ),

      h('div', { className: 'st-panel' },
        h('div', { className: 'st-panel-title' }, 'Three Regional Styles'),
        h('div', { className: 'st-styles-grid' },
          DATA.styles.map(function (s) {
            return h('div', { key: s.id, className: 'st-style-card' },
              h('div', { className: 'st-style-head' },
                h('span', { className: 'st-style-name' }, s.name),
                h('span', { className: 'st-style-dev indic' }, s.dev)
              ),
              h('div', { className: 'st-style-region' }, s.region + ' · ' + s.iast),
              h('div', { className: 'st-style-body' },
                h('div', null, h('strong', null, 'Signature: '), s.feature),
                h('div', null, h('strong', null, 'Key element: '), s.keyElement),
                h('div', null, h('strong', null, 'Ground plan: '), s.groundPlan),
                h('div', { style: { marginTop: '0.5rem' } }, s.description),
                h('div', { style: { marginTop: '0.5rem' } },
                  h('strong', null, 'Examples: '),
                  s.examples.join(' · ')
                )
              )
            );
          })
        )
      ),

      h('div', { className: 'st-panel' },
        h('div', { className: 'st-panel-title' }, 'Measurement System — Māna'),
        h('div', { style: { fontSize: '0.85rem', lineHeight: 1.7 } },
          h('p', null,
            'Classical Indian architecture uses proportional measurement, not absolute units. All dimensions derive from the aṅgula (finger-width) of the patron or the deity being housed — so buildings scale with their purpose.'
          ),
          h('ul', { style: { lineHeight: 1.8, paddingLeft: '1.4rem' } },
            DATA.units.map(function (u, i) {
              return h('li', { key: i },
                h('strong', null, u.name), ' (', h('span', { className: 'indic' }, u.dev), ', ', u.iast, ') — ',
                u.metric, '. ',
                u.desc
              );
            })
          )
        )
      ),

      h('div', { className: 'st-panel' },
        h('div', { className: 'st-panel-title' }, 'From the Classical Texts'),
        h('div', { className: 'st-verses' },
          DATA.verses.map(function (v, i) {
            return h('div', { key: i, className: 'st-verse' },
              h('div', { className: 'st-verse-dev indic' }, v.dev),
              h('div', { className: 'st-verse-iast' }, v.iast),
              h('div', { className: 'st-verse-trans' }, v.translation),
              h('div', { className: 'st-verse-source' }, v.source)
            );
          })
        )
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     APP
     ═══════════════════════════════════════════════════════════════════════ */
  function App() {
    var [state, dispatch] = useReducer(reducer, initial);

    useEffect(function () {
      var t = setTimeout(function () { saveVault(state); }, 400);
      return function () { clearTimeout(t); };
    }, [state.mandalaMode, state.facingDirection, state.converterFrom, state.converterTo, state.templeScale]);

    var tabs = [
      { id: 'mandala',    label: 'Maṇḍala' },
      { id: 'directions', label: 'Directions' },
      { id: 'mana',       label: 'Māna' },
      { id: 'about',      label: 'About' }
    ];

    return h('div', null,
      h('a', { className: 'st-external-link', href: '/' }, '← Aigaane'),
      h('header', { className: 'st-header glass' },
        h('div', { className: 'st-header-inner' },
          h('div', { className: 'st-brand' }, 'Sthāpatyaveda Studio'),
          h('nav', { className: 'st-nav' },
            tabs.map(function (t) {
              return h('button', {
                key: t.id,
                className: 'st-nav-btn' + (state.tab === t.id ? ' active' : ''),
                onClick: function () { dispatch({ type: 'setTab', value: t.id }); }
              }, t.label);
            })
          )
        )
      ),

      h('main', { className: 'st-container' },
        h('div', { style: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1rem' } },
          h('span', { className: 'st-badge' }, '81 padas'),
          h('span', { className: 'st-badge' }, '9 directions'),
          h('span', { className: 'st-badge' }, '4 māna units'),
          h('span', { className: 'st-badge' }, '3 styles')
        ),

        state.tab === 'mandala'    ? h(MandalaTab,    { state: state, dispatch: dispatch }) :
        state.tab === 'directions' ? h(DirectionsTab, { state: state, dispatch: dispatch }) :
        state.tab === 'mana'       ? h(ManaTab,       { state: state, dispatch: dispatch }) :
        h(AboutTab)
      ),

      h('footer', { className: 'st-footer-fixed' },
        h('span', null, 'Sthāpatyaveda · Upaveda of Architecture · Educational use only'),
        h('button', {
          className: 'st-btn st-btn-primary',
          onClick: function () {
            var next =
              state.tab === 'mandala'    ? 'directions' :
              state.tab === 'directions' ? 'mana' :
              state.tab === 'mana'       ? 'about' : 'mandala';
            dispatch({ type: 'setTab', value: next });
          }
        }, 'Next →')
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     MOUNT
     ═══════════════════════════════════════════════════════════════════════ */
  var container = document.getElementById('root');
  if (!container) return;
  container.innerHTML = '';
  var root = ReactDOM.createRoot(container);
  root.render(h(App));
})();