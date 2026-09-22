/* ═══════════════════════════════════════════════════════════════════════════
   Upaveda Cabinet — React Component
   ═══════════════════════════════════════════════════════════════════════════
   - Hero section introducing Upavedas
   - Filter row: All / Medicine / Music / Architecture / Warfare
   - 4 studio cards in classical order
   - Footer links back to main app
   - Data source: window.UPAVEDAS_DATA (shared with Sanskrit tab Studios view)
   - No JSX, no Babel
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var React = window.React;
  var ReactDOM = window.ReactDOM;
  var DATA = window.UPAVEDAS_DATA;
  if (!React || !ReactDOM || !DATA) {
    console.error('[Upaveda Cabinet] Missing React, ReactDOM, or UPAVEDAS_DATA');
    return;
  }

  var h = React.createElement;
  var useState = React.useState;
  var useMemo = React.useMemo;

  /* ═══════════════════════════════════════════════════════════════════════
     FILTER DEFINITIONS
     Each studio belongs to a category. Filter shows only matching.
     ═══════════════════════════════════════════════════════════════════════ */
  var FILTERS = [
    { id: 'all',          label: 'All' },
    { id: 'medicine',     label: 'Medicine',     matches: ['ayurveda'] },
    { id: 'music',        label: 'Music',        matches: ['gandharvaveda'] },
    { id: 'architecture', label: 'Architecture', matches: ['sthapatyaveda'] },
    { id: 'warfare',      label: 'Warfare',      matches: ['dhanurveda'] }
  ];

  /* ═══════════════════════════════════════════════════════════════════════
     COMPONENTS
     ═══════════════════════════════════════════════════════════════════════ */
  function Hero(props) {
    var intro = props.intro;
    return h('div', { className: 'uv-hero' },
      h('div', { className: 'uv-hero-dev indic' }, intro.dev),
      h('h1', { className: 'uv-hero-title' }, intro.title),
      h('div', { className: 'uv-hero-iast' }, intro.iast),
      h('div', { className: 'uv-hero-sub' }, intro.subtitle),
      h('p', { className: 'uv-hero-body' }, intro.body)
    );
  }

  function FilterRow(props) {
    return h('div', { className: 'uv-filters' },
      FILTERS.map(function (f) {
        return h('button', {
          key: f.id,
          className: 'uv-filter-btn' + (props.active === f.id ? ' active' : ''),
          onClick: function () { props.onChange(f.id); }
        }, f.label);
      })
    );
  }

  function StudioCard(props) {
    var s = props.studio;
    var dimmed = props.dimmed;

    return h('div', {
      className: 'uv-studio-card' + (dimmed ? ' dimmed' : ''),
      style: {
        '--uv-card-accent': s.accent,
        '--uv-card-accent-hi': s.accentHi
      }
    },
      // Header
      h('div', { className: 'uv-card-head' },
        h('span', { className: 'uv-card-name' }, s.name),
        h('span', { className: 'uv-card-dev indic' }, s.dev),
        h('span', { className: 'uv-card-status live' }, 'LIVE')
      ),
      h('div', { className: 'uv-card-iast' }, s.iast),
      h('div', { className: 'uv-card-en' }, s.en),

      // Tagline + description
      h('div', { className: 'uv-card-tagline' }, s.tagline),
      h('div', { className: 'uv-card-desc' }, s.description),

      // Features list
      h('ul', { className: 'uv-card-features' },
        s.features.map(function (f, i) {
          return h('li', { key: i }, f);
        })
      ),

      // Source citation
      h('div', { className: 'uv-card-source' }, s.source),

      // Launch button
      h('a', {
        className: 'uv-card-action',
        href: s.link
      }, s.linkLabel + ' →')
    );
  }

  function FooterStrip(props) {
    return h('div', { className: 'uv-footer-strip' },
      props.links.map(function (l, i) {
        return h('a', {
          key: i,
          className: 'uv-footer-link',
          href: l.href,
          target: l.external ? '_blank' : undefined,
          rel: l.external ? 'noopener noreferrer' : undefined
        }, l.label);
      })
    );
  }

  /* ═══════════════════════════════════════════════════════════════════════
     APP
     ═══════════════════════════════════════════════════════════════════════ */
  function App() {
    var [filter, setFilter] = useState('all');

    // Which studio IDs should be shown (per filter)
    var activeFilter = useMemo(function () {
      for (var i = 0; i < FILTERS.length; i++) {
        if (FILTERS[i].id === filter) return FILTERS[i];
      }
      return FILTERS[0];
    }, [filter]);

    // Sort studios by order, then mark dimmed ones
    var orderedStudios = useMemo(function () {
      var list = DATA.studios.slice().sort(function (a, b) {
        return (a.order || 0) - (b.order || 0);
      });
      return list;
    }, []);

    function isDimmed(studio) {
      if (!activeFilter.matches) return false;
      return activeFilter.matches.indexOf(studio.id) === -1;
    }

    return h('div', null,

      // Top header
      h('header', { className: 'uv-header' },
        h('div', { className: 'uv-header-inner' },
          h('div', { className: 'uv-brand' }, 'Aigaane · Upaveda Cabinet'),
          h('a', { className: 'uv-back', href: '/' }, '← Aigaane')
        )
      ),

      // Main content
      h('main', { className: 'uv-container' },
        h(Hero, { intro: DATA.intro }),

        h(FilterRow, { active: filter, onChange: setFilter }),

        h('div', { className: 'uv-studio-grid' },
          orderedStudios.map(function (s) {
            return h(StudioCard, {
              key: s.id,
              studio: s,
              dimmed: isDimmed(s)
            });
          })
        ),

        h(FooterStrip, { links: DATA.links })
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