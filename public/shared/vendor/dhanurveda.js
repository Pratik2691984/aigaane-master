/* ═══════════════════════════════════════════════════════════════════════════
   Dhanurveda Studio — React Component
   ═══════════════════════════════════════════════════════════════════════════
   - 4 tabs: Catur-aṅginī · Āyudha · Vyūha · About
   - Army division cards + counter matrix
   - Weapons grid with astra/śastra filter
   - Battle formation explorer
   - Vault: dhanurveda.vault.v1
   - No JSX, no Babel
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var React = window.React;
  var ReactDOM = window.ReactDOM;
  var DATA = window.DHANURVEDA_DATA;
  if (!React || !ReactDOM || !DATA) {
    console.error('[Dhanurveda] Missing React, ReactDOM, or DHANURVEDA_DATA');
    return;
  }

  var h = React.createElement;
  var useEffect = React.useEffect;
  var useMemo = React.useMemo;
  var useReducer = React.useReducer;

  /* ═══════════════════════════════════════════════════════════════════════
     VAULT
     ═══════════════════════════════════════════════════════════════════════ */
  var VAULT_KEY = 'dhanurveda.vault.v1';

  function loadVault() {
    try {
      var raw = localStorage.getItem(VAULT_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  function saveVault(state) {
    try {
      localStorage.setItem(VAULT_KEY, JSON.stringify({
        weaponFilter: state.weaponFilter,
        savedAt: Date.now()
      }));
    } catch (e) {}
  }

  /* ═══════════════════════════════════════════════════════════════════════
     COUNTER MATRIX — static tactical table
     Rows = attacker, Cols = defender
     Value: 'strong' | 'weak' | 'neutral'
     ═══════════════════════════════════════════════════════════════════════ */
  var COUNTER_MATRIX = {
    ratha:  { ratha: 'neutral', gaja: 'weak',    ashva: 'strong', padati: 'strong' },
    gaja:   { ratha: 'strong',  gaja: 'neutral', ashva: 'strong', padati: 'strong' },
    ashva:  { ratha: 'weak',    gaja: 'weak',    ashva: 'neutral', padati: 'strong' },
    padati: { ratha: 'weak',    gaja: 'weak',    ashva: 'neutral', padati: 'neutral' }
  };

  /* ═══════════════════════════════════════════════════════════════════════
     REDUCER
     ═══════════════════════════════════════════════════════════════════════ */
  var initial = (function () {
    var v = loadVault() || {};
    var validFilters = ['all', 'astra', 'shastra'];
    return {
      tab: 'caturangini',
      selectedArmy: null,
      selectedWeapon: null,
      selectedVyuha: null,
      weaponFilter: validFilters.indexOf(v.weaponFilter) !== -1 ? v.weaponFilter : 'all'
    };
  })();

  function reducer(state, action) {
    switch (action.type) {
      case 'setTab':            return Object.assign({}, state, { tab: action.value });
      case 'selectArmy':        return Object.assign({}, state, { selectedArmy: state.selectedArmy === action.value ? null : action.value });
      case 'selectWeapon':      return Object.assign({}, state, { selectedWeapon: state.selectedWeapon === action.value ? null : action.value });
      case 'selectVyuha':       return Object.assign({}, state, { selectedVyuha: state.selectedVyuha === action.value ? null : action.value });
      case 'setWeaponFilter':   return Object.assign({}, state, { weaponFilter: action.value });
      default: return state;
    }
  }

  /* ═══════════════════════════════════════════════════════════════════════
     HELPERS
     ═══════════════════════════════════════════════════════════════════════ */
  function findArmy(id) {
    for (var i = 0; i < DATA.caturAngini.length; i++) {
      if (DATA.caturAngini[i].id === id) return DATA.caturAngini[i];
    }
    return null;
  }
  function findWeapon(id) {
    for (var i = 0; i < DATA.weapons.length; i++) {
      if (DATA.weapons[i].id === id) return DATA.weapons[i];
    }
    return null;
  }
  function findVyuha(id) {
    for (var i = 0; i < DATA.vyuhas.length; i++) {
      if (DATA.vyuhas[i].id === id) return DATA.vyuhas[i];
    }
    return null;
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 1 — CATUR-AṄGINĪ
     ═══════════════════════════════════════════════════════════════════════ */
  function CaturanginiTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;
    var selected = state.selectedArmy ? findArmy(state.selectedArmy) : null;

    return h('div', null,
      h('div', { className: 'dv-panel' },
        h('div', { className: 'dv-panel-title' }, 'Catur-aṅginī — Four-fold Army'),
        h('div', { style: { fontSize: '0.82rem', color: 'var(--dv-text-muted)', lineHeight: 1.6 } },
          'Classical Indian armies comprised four divisions — chariots, elephants, cavalry, and infantry. Click any card to see tactical details and how it interacts with the others.'
        )
      ),

      h('div', { className: 'dv-army-grid' },
        DATA.caturAngini.map(function (a) {
          var isSel = state.selectedArmy === a.id;
          return h('div', {
            key: a.id,
            className: 'dv-army-card' + (isSel ? ' selected' : ''),
            style: { borderColor: isSel ? a.color : undefined },
            onClick: function () { dispatch({ type: 'selectArmy', value: a.id }); }
          },
            h('div', { className: 'dv-army-head' },
              h('span', { className: 'dv-army-name', style: { color: a.color } }, a.name),
              h('span', { className: 'dv-army-dev indic' }, a.dev),
              h('span', { className: 'dv-army-iast' }, a.iast)
            ),
            h('div', { className: 'dv-army-en' }, a.en),
            h('div', { className: 'dv-army-role' }, a.role),
            h('div', { className: 'dv-army-terrain' }, h('strong', null, 'Terrain: '), a.terrain)
          );
        })
      ),

      h('div', { className: 'dv-panel', style: { marginTop: '1rem' } },
        h('div', { className: 'dv-panel-title' }, 'Counter Matrix — Attacker (row) vs Defender (column)'),
        h('table', { className: 'dv-counter-matrix' },
          h('thead', null, h('tr', null,
            h('th', null, ''),
            DATA.caturAngini.map(function (a) {
              return h('th', { key: a.id }, a.name);
            })
          )),
          h('tbody', null,
            DATA.caturAngini.map(function (attacker) {
              return h('tr', { key: attacker.id },
                h('th', { style: { textAlign: 'left' } }, attacker.name),
                DATA.caturAngini.map(function (defender) {
                  var v = COUNTER_MATRIX[attacker.id] && COUNTER_MATRIX[attacker.id][defender.id];
                  var label = v === 'strong' ? 'Strong' : v === 'weak' ? 'Weak' : 'Even';
                  return h('td', { key: defender.id, className: v || 'neutral' }, label);
                })
              );
            })
          )
        ),
        h('div', { style: { fontSize: '0.72rem', color: 'var(--dv-text-muted)', marginTop: '0.5rem', fontStyle: 'italic' } },
          'Red = attacker has advantage. Green = attacker is disadvantaged. "Even" = neutral matchup.'
        )
      ),

      selected ? h(ArmyDetail, { army: selected }) : null
    );
  }

  function ArmyDetail(props) {
    var a = props.army;
    return h('div', { className: 'dv-army-detail', style: { borderColor: a.color } },
      h('div', { className: 'dv-army-head' },
        h('span', { className: 'dv-army-name', style: { color: a.color, fontSize: '1.6rem' } }, a.name),
        h('span', { className: 'dv-army-dev indic', style: { fontSize: '1.2rem' } }, a.dev),
        h('span', { className: 'dv-army-iast' }, a.iast)
      ),
      h('div', { className: 'dv-army-role', style: { fontSize: '0.9rem' } }, a.role),

      h('h4', null, 'Strengths'),
      h('ul', null, a.strengths.map(function (s, i) { return h('li', { key: i }, s); })),

      h('h4', null, 'Weaknesses'),
      h('ul', null, a.weaknesses.map(function (w, i) { return h('li', { key: i }, w); })),

      h('h4', null, 'Weapons'),
      h('div', { className: 'dv-tag-grid' },
        a.weapons.map(function (w, i) {
          return h('span', { key: i, className: 'dv-tag dv-tag-weapon' }, w);
        })
      ),

      h('h4', null, 'Countered By'),
      h('div', { className: 'dv-tag-grid' },
        a.counters.map(function (c, i) {
          return h('span', { key: i, className: 'dv-tag dv-tag-counter' }, c);
        })
      ),

      h('div', { style: { fontSize: '0.72rem', color: 'var(--dv-text-muted)', marginTop: '0.75rem', fontFamily: 'JetBrains Mono, monospace' } },
        a.source
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 2 — ĀYUDHA
     ═══════════════════════════════════════════════════════════════════════ */
  function AyudhaTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;
    var selected = state.selectedWeapon ? findWeapon(state.selectedWeapon) : null;

    var filtered = useMemo(function () {
      return DATA.weapons.filter(function (w) {
        if (state.weaponFilter === 'all') return true;
        return w.type === state.weaponFilter;
      });
    }, [state.weaponFilter]);

    var astraCount = DATA.weapons.filter(function (w) { return w.type === 'astra'; }).length;
    var shastraCount = DATA.weapons.filter(function (w) { return w.type === 'shastra'; }).length;

    return h('div', null,
      h('div', { className: 'dv-panel' },
        h('div', { className: 'dv-panel-title' }, 'Āyudha Kośa — Weapons Compendium'),
        h('div', { className: 'dv-weapon-filters' },
          [
            { id: 'all',     label: 'All (' + DATA.weapons.length + ')' },
            { id: 'astra',   label: 'Astras (' + astraCount + ')' },
            { id: 'shastra', label: 'Śastras (' + shastraCount + ')' }
          ].map(function (f) {
            return h('button', {
              key: f.id,
              className: 'dv-nav-btn' + (state.weaponFilter === f.id ? ' active' : ''),
              onClick: function () { dispatch({ type: 'setWeaponFilter', value: f.id }); }
            }, f.label);
          })
        ),
        h('div', { style: { fontSize: '0.75rem', color: 'var(--dv-text-muted)' } },
          filtered.length + ' of ' + DATA.weapons.length + ' weapons shown'
        )
      ),

      h('div', { className: 'dv-weapon-grid' },
        filtered.map(function (w) {
          var isSel = state.selectedWeapon === w.id;
          return h('div', {
            key: w.id,
            className: 'dv-weapon-card' + (isSel ? ' selected' : ''),
            onClick: function () { dispatch({ type: 'selectWeapon', value: w.id }); }
          },
            h('div', { className: 'dv-weapon-head' },
              h('span', { className: 'dv-weapon-name' }, w.name),
              h('span', {
                className: 'dv-badge ' + (w.type === 'astra' ? 'dv-badge-astra' : 'dv-badge-shastra')
              }, w.type === 'astra' ? 'ASTRA' : 'ŚASTRA')
            ),
            h('div', { className: 'indic dv-weapon-dev', style: { marginBottom: '0.4rem' } }, w.dev),
            h('div', { className: 'dv-weapon-wielder' }, w.wielder),
            h('div', { className: 'dv-weapon-nature' }, w.nature)
          );
        })
      ),

      selected ? h(WeaponDetail, { weapon: selected }) : null
    );
  }

  function WeaponDetail(props) {
    var w = props.weapon;
    return h('div', { className: 'dv-weapon-detail' },
      h('div', { className: 'dv-weapon-head' },
        h('span', { className: 'dv-weapon-name', style: { fontSize: '1.4rem' } }, w.name),
        h('span', {
          className: 'dv-badge ' + (w.type === 'astra' ? 'dv-badge-astra' : 'dv-badge-shastra')
        }, w.type === 'astra' ? 'ASTRA' : 'ŚASTRA')
      ),
      h('div', { className: 'indic', style: { fontSize: '1.1rem', color: 'var(--dv-accent-hi)', marginBottom: '0.5rem' } }, w.dev),

      h('div', { className: 'dv-weapon-detail-row' },
        h('span', { className: 'dv-weapon-detail-label' }, 'Wielder'),
        h('span', null, w.wielder)
      ),
      h('div', { className: 'dv-weapon-detail-row' },
        h('span', { className: 'dv-weapon-detail-label' }, 'Nature'),
        h('span', null, w.nature)
      ),
      h('div', { className: 'dv-weapon-detail-row' },
        h('span', { className: 'dv-weapon-detail-label' }, 'Effect'),
        h('span', null, w.effect)
      ),
      h('div', { className: 'dv-weapon-detail-row' },
        h('span', { className: 'dv-weapon-detail-label' }, 'Counter'),
        h('span', null, w.counter)
      ),
      h('div', { className: 'dv-weapon-detail-row' },
        h('span', { className: 'dv-weapon-detail-label' }, 'Source'),
        h('span', { style: { fontFamily: 'JetBrains Mono, monospace', fontSize: '0.78rem', color: 'var(--dv-text-muted)' } }, w.source)
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 3 — VYŪHA
     ═══════════════════════════════════════════════════════════════════════ */
  function VyuhaTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;
    var selected = state.selectedVyuha ? findVyuha(state.selectedVyuha) : null;

    return h('div', null,
      h('div', { className: 'dv-panel' },
        h('div', { className: 'dv-panel-title' }, 'Vyūha — Battle Formations'),
        h('div', { style: { fontSize: '0.82rem', color: 'var(--dv-text-muted)', lineHeight: 1.6 } },
          'Classical Indian warfare deployed troops in geometric formations (vyūhas), each named after an animal, object, or cosmological shape. Click any card for tactical details.'
        )
      ),

      h('div', { className: 'dv-vyuha-grid' },
        DATA.vyuhas.map(function (v) {
          var isSel = state.selectedVyuha === v.id;
          var sideClass = v.side === 'Pāṇḍava' ? 'pandava' : 'kaurava';
          return h('div', {
            key: v.id,
            className: 'dv-vyuha-card' + (isSel ? ' selected' : ''),
            onClick: function () { dispatch({ type: 'selectVyuha', value: v.id }); }
          },
            h('div', { className: 'dv-vyuha-head' },
              h('span', { className: 'dv-vyuha-name' }, v.name),
              h('span', { className: 'dv-vyuha-dev indic' }, v.dev)
            ),
            h('div', { className: 'dv-vyuha-shape' }, v.shape),
            h('div', { className: 'dv-vyuha-deployer' }, h('strong', null, 'Deployer: '), v.deployer),
            h('div', null,
              h('span', { className: 'dv-vyuha-side ' + sideClass }, v.side.toUpperCase())
            )
          );
        })
      ),

      selected ? h(VyuhaDetail, { vyuha: selected }) : null
    );
  }

  function VyuhaDetail(props) {
    var v = props.vyuha;
    return h('div', { className: 'dv-vyuha-detail' },
      h('div', { className: 'dv-vyuha-head' },
        h('span', { className: 'dv-vyuha-name', style: { fontSize: '1.4rem' } }, v.name),
        h('span', { className: 'dv-vyuha-dev indic', style: { fontSize: '1.1rem' } }, v.dev)
      ),
      h('div', { className: 'dv-vyuha-shape', style: { fontSize: '0.8rem' } }, v.shape),

      h('div', { className: 'dv-vyuha-detail-row' },
        h('span', { className: 'dv-vyuha-detail-label' }, 'Deployer'),
        h('span', null, v.deployer)
      ),
      h('div', { className: 'dv-vyuha-detail-row' },
        h('span', { className: 'dv-vyuha-detail-label' }, 'Side'),
        h('span', null, v.side)
      ),
      h('div', { className: 'dv-vyuha-detail-row' },
        h('span', { className: 'dv-vyuha-detail-label' }, 'Purpose'),
        h('span', null, v.purpose)
      ),
      h('div', { className: 'dv-vyuha-detail-row' },
        h('span', { className: 'dv-vyuha-detail-label' }, 'Counters'),
        h('span', null, v.counterVyuhas.join(' · '))
      ),
      h('div', { className: 'dv-vyuha-detail-row' },
        h('span', { className: 'dv-vyuha-detail-label' }, 'Description'),
        h('span', null, v.description)
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 4 — ABOUT
     ═══════════════════════════════════════════════════════════════════════ */
  function AboutTab() {
    return h('div', null,
      h('div', { className: 'dv-panel' },
        h('div', { className: 'dv-panel-title' }, 'About Dhanurveda'),
        h('div', { className: 'dv-about-text' },
          h('p', null,
            'Dhanurveda — "the knowledge of the bow" — is the Upaveda of archery, martial sciences, and warfare. ' +
            'It is traditionally attributed to Bhṛgu, Viśvāmitra, Vasiṣṭha, and Paraśurāma, and elaborated in the ' +
            'Agni Purāṇa (chapters 249–252), the Vasiṣṭha Dhanurveda, and the battle books of the Mahābhārata.'
          ),
          h('p', null,
            'Unlike modern military science, Dhanurveda is inseparable from dharma. Combat is framed as dharma-yuddha — ' +
            'righteous warfare with strict ethical rules: no attacking the unarmed, the fleeing, the sleeping, or the surrendered.'
          ),
          h('p', null,
            h('strong', null, 'The four divisions (catur-aṅginī): ')
          ),
          h('ul', null,
            DATA.caturAngini.map(function (a, i) {
              return h('li', { key: i },
                h('strong', null, a.name), ' (', h('span', { className: 'indic' }, a.dev), ', ', a.iast, ') — ',
                a.en, ': ', a.role, '.'
              );
            })
          ),
          h('p', null,
            h('strong', null, 'Astras vs Śastras: '),
            'Astras are missile weapons released by mantra, capable of manifesting fire, water, wind, or other cosmic forces. ' +
            'Śastras are hand-held weapons — bows, swords, spears, discuses — wielded by physical skill.'
          ),
          h('p', null,
            h('strong', null, 'Note: '),
            'This studio presents Dhanurveda as a classical tradition for educational and historical study. ' +
            'It is not a training manual for modern combat.'
          )
        )
      ),

      h('div', { className: 'dv-panel' },
        h('div', { className: 'dv-panel-title' }, 'Sources'),
        h('ul', { style: { lineHeight: 1.8, paddingLeft: '1.4rem', fontSize: '0.85rem' } },
          h('li', null, 'Agni Purāṇa, chapters 249–252 (Dhanurveda section)'),
          h('li', null, 'Vasiṣṭha Dhanurveda Saṃhitā'),
          h('li', null, 'Mahābhārata — Bhīṣma Parva, Droṇa Parva, Karṇa Parva'),
          h('li', null, 'Nītiprakāśikā of Vaiśampāyana')
        )
      ),

      h('div', { className: 'dv-panel' },
        h('div', { className: 'dv-panel-title' }, 'From the Classical Texts'),
        h('div', { className: 'dv-verses' },
          DATA.verses.map(function (v, i) {
            return h('div', { key: i, className: 'dv-verse' },
              h('div', { className: 'dv-verse-dev indic' }, v.dev),
              h('div', { className: 'dv-verse-iast' }, v.iast),
              h('div', { className: 'dv-verse-trans' }, v.translation),
              h('div', { className: 'dv-verse-source' }, v.source)
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
    }, [state.weaponFilter]);

    var tabs = [
      { id: 'caturangini', label: 'Catur-aṅginī' },
      { id: 'ayudha',      label: 'Āyudha' },
      { id: 'vyuha',       label: 'Vyūha' },
      { id: 'about',       label: 'About' }
    ];

    return h('div', null,
      h('a', { className: 'dv-external-link', href: '/' }, '← Aigaane'),
      h('header', { className: 'dv-header glass' },
        h('div', { className: 'dv-header-inner' },
          h('div', { className: 'dv-brand' }, 'Dhanurveda Studio'),
          h('nav', { className: 'dv-nav' },
            tabs.map(function (t) {
              return h('button', {
                key: t.id,
                className: 'dv-nav-btn' + (state.tab === t.id ? ' active' : ''),
                onClick: function () { dispatch({ type: 'setTab', value: t.id }); }
              }, t.label);
            })
          )
        )
      ),

      h('main', { className: 'dv-container' },
        h('div', { style: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1rem' } },
          h('span', { className: 'dv-badge' }, '4 army divisions'),
          h('span', { className: 'dv-badge' }, '20 weapons'),
          h('span', { className: 'dv-badge' }, '10 formations'),
          h('span', { className: 'dv-badge' }, '12 verses')
        ),

        state.tab === 'caturangini' ? h(CaturanginiTab, { state: state, dispatch: dispatch }) :
        state.tab === 'ayudha'      ? h(AyudhaTab,      { state: state, dispatch: dispatch }) :
        state.tab === 'vyuha'       ? h(VyuhaTab,       { state: state, dispatch: dispatch }) :
        h(AboutTab)
      ),

      h('footer', { className: 'dv-footer-fixed' },
        h('span', null, 'Dhanurveda · Upaveda of Warfare · Educational use only'),
        h('button', {
          className: 'dv-btn dv-btn-primary',
          onClick: function () {
            var next =
              state.tab === 'caturangini' ? 'ayudha' :
              state.tab === 'ayudha'      ? 'vyuha' :
              state.tab === 'vyuha'       ? 'about' : 'caturangini';
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