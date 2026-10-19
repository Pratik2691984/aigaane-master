/* ═══════════════════════════════════════════════════════════════════════════
   Āyurveda Studio — React Component
   ═══════════════════════════════════════════════════════════════════════════
   - 4 tabs: Prakṛti · Guṇas · Dinacaryā · About
   - Quiz scoring with primary/secondary doṣa + ranked bars
   - Guṇa grid with domain + pacifies filters
   - Dinacaryā side-by-side cards (dominant highlighted if quiz taken)
   - Vault: ayurveda.vault.v1 (localStorage)
   - No JSX, no Babel
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var React = window.React;
  var ReactDOM = window.ReactDOM;
  var DATA = window.AYURVEDA_DATA;
  if (!React || !ReactDOM || !DATA) {
    console.error('[Āyurveda] Missing React, ReactDOM, or AYURVEDA_DATA');
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
  var VAULT_KEY = 'ayurveda.vault.v1';

  function loadVault() {
    try {
      var raw = localStorage.getItem(VAULT_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  function saveVault(state) {
    try {
      localStorage.setItem(VAULT_KEY, JSON.stringify({
        answers: state.answers,
        result: state.result,
        savedAt: Date.now()
      }));
    } catch (e) {}
  }

  /* ═══════════════════════════════════════════════════════════════════════
     SCORING
     ═══════════════════════════════════════════════════════════════════════ */
  function computeResult(answers) {
    var scores = { vata: 0, pitta: 0, kapha: 0 };
    DATA.quizQuestions.forEach(function (q) {
      var sel = answers[q.id];
      if (sel == null) return;
      var opt = q.options[sel];
      if (!opt) return;
      scores[opt.dosha] += opt.weight;
    });
    var total = scores.vata + scores.pitta + scores.kapha;
    if (total === 0) return null;

    var ranked = [
      { id: 'vata',  score: scores.vata,  pct: Math.round(scores.vata  / total * 100) },
      { id: 'pitta', score: scores.pitta, pct: Math.round(scores.pitta / total * 100) },
      { id: 'kapha', score: scores.kapha, pct: Math.round(scores.kapha / total * 100) }
    ].sort(function (a, b) { return b.score - a.score; });

    // adjust pcts so they sum to 100
    var sumPct = ranked.reduce(function (s, r) { return s + r.pct; }, 0);
    if (sumPct !== 100 && ranked[0]) ranked[0].pct += (100 - sumPct);

    return {
      ranked: ranked,
      primary: ranked[0].id,
      secondary: ranked[1] && ranked[1].score > 0 ? ranked[1].id : null,
      scores: scores,
      total: total,
      completedAt: Date.now()
    };
  }

  /* ═══════════════════════════════════════════════════════════════════════
     REDUCER
     ═══════════════════════════════════════════════════════════════════════ */
  var initial = (function () {
    var v = loadVault() || {};
    var answers = (v.answers && typeof v.answers === 'object') ? v.answers : {};
    var result = null;
    // Recompute result from answers if we have them — ignore stored result to avoid stale data
    if (Object.keys(answers).length > 0) {
      result = computeResult(answers);
    }
    return {
      tab: 'prakriti',
      answers: answers,
      result: result,
      currentQ: 0,
      gunaFilter: 'all',
      doshaFilterGuna: 'all'
    };
  })();

  function reducer(state, action) {
    switch (action.type) {
      case 'setTab':     return Object.assign({}, state, { tab: action.value });
      case 'answer':
        var nextAnswers = Object.assign({}, state.answers, { [action.qid]: action.choice });
        var nextResult = computeResult(nextAnswers);
        return Object.assign({}, state, { answers: nextAnswers, result: nextResult });
      case 'nextQ':      return Object.assign({}, state, { currentQ: Math.min(state.currentQ + 1, DATA.quizQuestions.length - 1) });
      case 'prevQ':      return Object.assign({}, state, { currentQ: Math.max(state.currentQ - 1, 0) });
      case 'gotoQ':      return Object.assign({}, state, { currentQ: action.value });
      case 'resetQuiz':
        return Object.assign({}, state, { answers: {}, result: null, currentQ: 0 });
      case 'setGunaFilter':      return Object.assign({}, state, { gunaFilter: action.value });
      case 'setDoshaFilterGuna': return Object.assign({}, state, { doshaFilterGuna: action.value });
      default: return state;
    }
  }

  /* ═══════════════════════════════════════════════════════════════════════
     SHARED COMPONENTS
     ═══════════════════════════════════════════════════════════════════════ */
  function ProgressBar(props) {
    var pct = props.total > 0 ? Math.round(props.current / props.total * 100) : 0;
    return h('div', { className: 'ay-progress-bar' },
      h('div', { className: 'ay-progress-fill', style: { width: pct + '%' } })
    );
  }

  function DoshaBadge(props) {
    var d = DATA.doshas[props.id];
    if (!d) return null;
    return h('span', {
      className: 'ay-badge',
      style: { color: d.color, borderColor: d.color, background: 'transparent' }
    }, props.label || d.name);
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 1 — PRAKṚTI (QUIZ)
     ═══════════════════════════════════════════════════════════════════════ */
  function PrakritiTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;

    var q = DATA.quizQuestions[state.currentQ];
    var answeredCount = Object.keys(state.answers).length;
    var total = DATA.quizQuestions.length;
    var allAnswered = answeredCount === total;

    // If quiz complete and result exists, show result view
    if (allAnswered && state.result) {
      return h(ResultView, { state: state, dispatch: dispatch });
    }

    return h('div', null,
      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-quiz-progress' },
          h('span', null, 'Question ' + (state.currentQ + 1) + ' / ' + total),
          h(ProgressBar, { current: answeredCount, total: total }),
          h('span', null, answeredCount + ' answered')
        ),

        h('div', { className: 'ay-question-domain' }, q.domain),
        h('div', { className: 'ay-question' }, q.question),

        h('div', null,
          q.options.map(function (opt, i) {
            var isSelected = state.answers[q.id] === i;
            return h('button', {
              key: i,
              className: 'ay-option' + (isSelected ? ' selected' : ''),
              onClick: function () {
                dispatch({ type: 'answer', qid: q.id, choice: i });
                // auto-advance after brief delay
                setTimeout(function () {
                  if (state.currentQ < total - 1) dispatch({ type: 'nextQ' });
                }, 200);
              }
            }, opt.label);
          })
        ),

        h('div', { className: 'ay-quiz-actions' },
          h('button', {
            className: 'ay-btn',
            disabled: state.currentQ === 0,
            onClick: function () { dispatch({ type: 'prevQ' }); }
          }, '← Previous'),
          h('button', {
            className: 'ay-btn',
            disabled: state.currentQ === total - 1,
            onClick: function () { dispatch({ type: 'nextQ' }); }
          }, 'Next →'),
          h('span', { style: { flex: 1 } }),
          h('button', {
            className: 'ay-btn',
            onClick: function () {
              if (window.confirm('Reset all answers and start over?')) {
                dispatch({ type: 'resetQuiz' });
              }
            }
          }, 'Reset')
        )
      ),

      h('div', { className: 'ay-panel', style: { background: 'transparent', border: '1px dashed var(--ay-border)' } },
        h('div', { style: { fontSize: '0.78rem', color: 'var(--ay-text-muted)', lineHeight: 1.6 } },
          'Answer all 20 questions to see your Prakṛti breakdown. Results save automatically to this browser.'
        )
      )
    );
  }

  function ResultView(props) {
    var state = props.state;
    var dispatch = props.dispatch;
    var result = state.result;

    var primary = DATA.doshas[result.primary];
    var secondary = result.secondary ? DATA.doshas[result.secondary] : null;

    return h('div', null,
      h('div', { className: 'ay-result-primary' },
        h('div', { className: 'ay-result-title' }, 'Your Prakṛti'),
        h('div', { className: 'ay-result-name', style: { color: primary.color } },
          primary.name + (secondary ? ' · ' + secondary.name : '')),
        h('div', { className: 'ay-result-sub' },
          primary.dev + (secondary ? ' · ' + secondary.dev : '')
        ),
        h('div', { className: 'ay-result-sub', style: { marginTop: '0.5rem' } },
          primary.element
        )
      ),

      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, 'Doṣa Distribution'),
        h('div', { className: 'ay-bars' },
          result.ranked.map(function (r) {
            var d = DATA.doshas[r.id];
            return h('div', { key: r.id, className: 'ay-bar-row' },
              h('div', { className: 'ay-bar-name', style: { color: d.color } }, d.name),
              h('div', { className: 'ay-bar-track' },
                h('div', { className: 'ay-bar-fill ' + r.id, style: { width: r.pct + '%' } })
              ),
              h('div', { className: 'ay-bar-pct' }, r.pct + '%')
            );
          })
        )
      ),

      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, primary.name + ' — Balanced Signs'),
        h('ul', { style: { lineHeight: 1.8, paddingLeft: '1.4rem', margin: 0 } },
          primary.signsBalanced.map(function (s, i) { return h('li', { key: i }, s); })
        )
      ),

      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, primary.name + ' — Aggravated Signs'),
        h('ul', { style: { lineHeight: 1.8, paddingLeft: '1.4rem', margin: 0 } },
          primary.signsAggravated.map(function (s, i) { return h('li', { key: i }, s); })
        )
      ),

      h('div', { style: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap' } },
        h('button', {
          className: 'ay-btn ay-btn-primary',
          onClick: function () { dispatch({ type: 'setTab', value: 'dinacarya' }); }
        }, 'View Dinacaryā →'),
        h('button', {
          className: 'ay-btn',
          onClick: function () {
            if (window.confirm('Retake the quiz? Current answers will be cleared.')) {
              dispatch({ type: 'resetQuiz' });
            }
          }
        }, 'Retake Quiz')
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 2 — GUṆAS
     ═══════════════════════════════════════════════════════════════════════ */
  function GunasTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;

    var filtered = useMemo(function () {
      return DATA.gunas.filter(function (g) {
        if (state.gunaFilter !== 'all' && g.category !== state.gunaFilter) return false;
        if (state.doshaFilterGuna !== 'all') {
          var d = state.doshaFilterGuna;
          if (g.pacifies.indexOf(d) === -1 && g.aggravates.indexOf(d) === -1) return false;
        }
        return true;
      });
    }, [state.gunaFilter, state.doshaFilterGuna]);

    var categories = useMemo(function () {
      var set = {};
      DATA.gunas.forEach(function (g) { set[g.category] = true; });
      return ['all'].concat(Object.keys(set));
    }, []);

    return h('div', null,
      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, 'Filter by Category'),
        h('div', { className: 'ay-guna-filters' },
          categories.map(function (c) {
            return h('button', {
              key: c,
              className: 'ay-nav-btn' + (state.gunaFilter === c ? ' active' : ''),
              onClick: function () { dispatch({ type: 'setGunaFilter', value: c }); }
            }, c === 'all' ? 'All Categories' : c);
          })
        ),

        h('div', { className: 'ay-panel-title', style: { marginTop: '1rem' } }, 'Filter by Doṣa Effect'),
        h('div', { className: 'ay-guna-filters' },
          [
            { id: 'all',    label: 'Any Doṣa' },
            { id: 'vata',   label: 'Affects Vāta' },
            { id: 'pitta',  label: 'Affects Pitta' },
            { id: 'kapha',  label: 'Affects Kapha' }
          ].map(function (d) {
            return h('button', {
              key: d.id,
              className: 'ay-nav-btn' + (state.doshaFilterGuna === d.id ? ' active' : ''),
              onClick: function () { dispatch({ type: 'setDoshaFilterGuna', value: d.id }); }
            }, d.label);
          })
        )
      ),

      h('div', { style: { fontSize: '0.78rem', color: 'var(--ay-text-muted)', marginBottom: '0.75rem' } },
        filtered.length + ' of ' + DATA.gunas.length + ' guṇas'
      ),

      h('div', { className: 'ay-guna-grid' },
        filtered.map(function (g) {
          return h(GunaCard, { key: g.id, guna: g });
        })
      )
    );
  }

  function GunaCard(props) {
    var g = props.guna;
    return h('div', { className: 'ay-guna-card' },
      h('div', { className: 'ay-guna-head' },
        h('span', { className: 'ay-guna-name' }, g.name),
        h('span', { className: 'ay-guna-dev indic' }, g.dev)
      ),
      h('div', { className: 'ay-guna-en' }, g.en + ' · ' + g.category),
      h('div', { className: 'ay-guna-desc' }, g.desc),

      h('div', { className: 'ay-guna-meta' },
        g.pacifies.map(function (d, i) {
          return h('span', { key: 'p' + i, className: 'ay-tag ay-tag-pacifies' }, '↓ ' + d);
        }),
        g.aggravates.map(function (d, i) {
          return h('span', { key: 'a' + i, className: 'ay-tag ay-tag-aggravates' }, '↑ ' + d);
        })
      ),

      h('div', { className: 'ay-guna-meta' },
        g.rasa.map(function (r, i) {
          return h('span', { key: 'r' + i, className: 'ay-tag ay-tag-rasa' }, r);
        })
      ),

      h('div', { className: 'ay-guna-sub' },
        h('div', null, h('strong', null, 'Foods: '), g.foods.join(', ')),
        h('div', null, h('strong', null, 'Herbs: '), g.herbs.join(', '))
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 3 — DINACARYĀ
     ═══════════════════════════════════════════════════════════════════════ */
  function DinacaryaTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;

    var primary = state.result ? state.result.primary : null;

    return h('div', null,
      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, 'Dinacaryā — Daily Routine'),
        h('div', { style: { fontSize: '0.85rem', color: 'var(--ay-text-muted)', lineHeight: 1.6 } },
          primary
            ? 'Your dominant doṣa is highlighted below based on your Prakṛti result. Apply its routine first, then read the others for balance.'
            : 'Take the Prakṛti quiz to highlight your dominant doṣa below. Until then, all three routines are shown for reference.'
        )
      ),

      h('div', { className: 'ay-dina-grid' },
        ['vata', 'pitta', 'kapha'].map(function (id) {
          var d = DATA.doshas[id];
          var r = DATA.dinacaryaRules[id];
          var isDominant = primary === id;
          return h('div', {
            key: id,
            className: 'ay-dina-card' + (isDominant ? ' dominant' : '')
          },
            h('div', { className: 'ay-dina-head' },
              h('div', null,
                h('div', { className: 'ay-dina-name', style: { color: d.color } }, d.name),
                h('div', { className: 'ay-dina-dev indic' }, d.dev)
              ),
              isDominant ? h('span', { className: 'ay-badge' }, 'DOMINANT') : null
            ),

            [
              ['Wake',      r.wake],
              ['Morning',   r.morning],
              ['Breakfast', r.breakfast],
              ['Midday',    r.midday],
              ['Afternoon', r.afternoon],
              ['Evening',   r.evening],
              ['Night',     r.night],
              ['Oil',       r.oil],
              ['Diet',      r.diet],
              ['Exercise',  r.exercise],
              ['Sleep',     r.sleep]
            ].map(function (row, i) {
              return h('div', { key: i, className: 'ay-dina-row' },
                h('div', { className: 'ay-dina-label' }, row[0]),
                h('div', null, row[1])
              );
            }),

            h('div', { className: 'ay-guna-sub' },
              h('strong', null, 'Supporting herbs: '),
              r.herbs.join(', ')
            )
          );
        })
      )
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     TAB 4 — ABOUT
     ═══════════════════════════════════════════════════════════════════════ */
  function AboutTab() {
    return h('div', null,
      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, 'About Āyurveda'),
        h('div', { className: 'ay-about-text' },
          h('p', null,
            'Āyurveda — "the knowledge of life" — is the Upaveda of medicine, traditionally attributed to ' +
            'the sage Ātreya and compiled by Caraka, with surgical traditions preserved by Suśruta. ' +
            'Its foundational framework is the three doṣas: Vāta (motion), Pitta (transformation), and Kapha (structure).'
          ),
          h('p', null,
            h('strong', null, 'The three doṣas: ')
          ),
          h('ul', null,
            h('li', null, h('strong', null, 'Vāta'), ' — Air + Ether. Governs movement, nerve impulses, breath, elimination.'),
            h('li', null, h('strong', null, 'Pitta'), ' — Fire + Water. Governs digestion, metabolism, intellect, vision.'),
            h('li', null, h('strong', null, 'Kapha'), ' — Water + Earth. Governs structure, lubrication, immunity, calm.')
          ),
          h('p', null,
            'Prakṛti is your innate constitution — fixed at birth. Vikṛti is your current imbalance. ' +
            'This studio helps you identify your Prakṛti, explore the 20 qualities (guṇas) that govern ' +
            'balance, and apply a daily routine (dinacaryā) tuned to your constitution.'
          ),
          h('p', null,
            h('strong', null, 'Note: '), 'This is an educational tool, not medical advice. For treatment of specific ' +
            'conditions, consult a qualified Āyurvedic practitioner (Vaidya).'
          )
        )
      ),

      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, 'The Three Doṣas at a Glance'),
        h('div', null,
          ['vata', 'pitta', 'kapha'].map(function (id) {
            var d = DATA.doshas[id];
            return h('div', { key: id, style: { marginBottom: '1rem' } },
              h('div', { style: { display: 'flex', gap: '0.5rem', alignItems: 'baseline', marginBottom: '0.4rem' } },
                h('span', { className: 'ay-guna-name', style: { color: d.color } }, d.name),
                h('span', { className: 'ay-guna-dev indic' }, d.dev),
                h('span', { className: 'ay-guna-en' }, d.en)
              ),
              h('div', { style: { fontSize: '0.82rem', lineHeight: 1.55 } },
                h('div', null, h('strong', null, 'Elements: '), d.element),
                h('div', null, h('strong', null, 'Location: '), d.location),
                h('div', null, h('strong', null, 'Peak hours: '), d.time),
                h('div', null, h('strong', null, 'Season: '), d.season),
                h('div', null, h('strong', null, 'Qualities: '), d.qualities.join(', '))
              )
            );
          })
        )
      ),

      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, 'Six Tastes (Rasas)'),
        h('div', { className: 'ay-guna-grid' },
          DATA.rasas.map(function (r) {
            var eff = r.doshaEffect;
            return h('div', { key: r.id, className: 'ay-guna-card' },
              h('div', { className: 'ay-guna-head' },
                h('span', { className: 'ay-guna-name' }, r.name),
                h('span', { className: 'ay-guna-dev indic' }, r.dev)
              ),
              h('div', { className: 'ay-guna-en' }, r.en + ' · ' + r.elements),
              h('div', { className: 'ay-guna-meta' },
                h('span', { className: 'ay-tag ay-tag-rasa' }, 'Vāta ' + eff.vata),
                h('span', { className: 'ay-tag ay-tag-rasa' }, 'Pitta ' + eff.pitta),
                h('span', { className: 'ay-tag ay-tag-rasa' }, 'Kapha ' + eff.kapha)
              ),
              h('div', { className: 'ay-guna-sub' }, h('strong', null, 'Examples: '), r.examples)
            );
          })
        )
      ),

      h('div', { className: 'ay-panel' },
        h('div', { className: 'ay-panel-title' }, 'From the Classical Texts'),
        h('div', { className: 'ay-verses' },
          DATA.verses.map(function (v, i) {
            return h('div', { key: i, className: 'ay-verse' },
              h('div', { className: 'ay-verse-dev indic' }, v.dev),
              h('div', { className: 'ay-verse-iast' }, v.iast),
              h('div', { className: 'ay-verse-trans' }, v.translation),
              h('div', { className: 'ay-verse-source' }, v.source)
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

    // Persist answers + result
    useEffect(function () {
      var t = setTimeout(function () { saveVault(state); }, 400);
      return function () { clearTimeout(t); };
    }, [state.answers]);

    return h('div', null,
      h('a', { className: 'ay-external-link', href: '/' }, '← Aigaane'),
      h('header', { className: 'ay-header glass' },
        h('div', { className: 'ay-header-inner' },
          h('div', { className: 'ay-brand' }, 'Āyurveda Studio'),
          h('nav', { className: 'ay-nav' },
            [
              { id: 'prakriti',  label: 'Prakṛti' },
              { id: 'gunas',     label: 'Guṇas' },
              { id: 'dinacarya', label: 'Dinacaryā' },
              { id: 'about',     label: 'About' }
            ].map(function (t) {
              return h('button', {
                key: t.id,
                className: 'ay-nav-btn' + (state.tab === t.id ? ' active' : ''),
                onClick: function () { dispatch({ type: 'setTab', value: t.id }); }
              }, t.label);
            })
          )
        )
      ),

      h('main', { className: 'ay-container' },
        // Status badges
        h('div', { style: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1rem' } },
          h('span', { className: 'ay-badge' }, '20 questions'),
          h('span', { className: 'ay-badge' }, '20 guṇas'),
          h('span', { className: 'ay-badge' }, '3 doṣas'),
          state.result ? h('span', { className: 'ay-badge' },
            'Prakṛti: ' + DATA.doshas[state.result.primary].name
          ) : null
        ),

        state.tab === 'prakriti'  ? h(PrakritiTab,  { state: state, dispatch: dispatch }) :
        state.tab === 'gunas'     ? h(GunasTab,     { state: state, dispatch: dispatch }) :
        state.tab === 'dinacarya' ? h(DinacaryaTab, { state: state, dispatch: dispatch }) :
        h(AboutTab)
      ),

      h('footer', { className: 'ay-footer-fixed' },
        h('span', null, 'Āyurveda · Upaveda of Medicine · Educational use only'),
        h('button', {
          className: 'ay-btn ay-btn-primary',
          onClick: function () {
            var nextTab =
              state.tab === 'prakriti'  ? (state.result ? 'dinacarya' : 'prakriti') :
              state.tab === 'gunas'     ? 'prakriti' :
              state.tab === 'dinacarya' ? 'prakriti' : 'prakriti';
            dispatch({ type: 'setTab', value: nextTab });
          }
        }, state.tab === 'prakriti' && state.result ? 'View Routine →' : 'Start Prakṛti Quiz')
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