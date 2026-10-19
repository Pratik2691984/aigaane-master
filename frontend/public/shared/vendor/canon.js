/* ═══════════════════════════════════════════════════════════════════════════
   Aigaane Canon — React Component
   ═══════════════════════════════════════════════════════════════════════════
   - Loads canon.db via sql.js (SQLite WASM)
   - Browse texts, chapters, verses
   - Full-text search via FTS5
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var React = window.React;
  var ReactDOM = window.ReactDOM;
  if (!React || !ReactDOM) {
    console.error('[Canon] React not loaded');
    return;
  }

  var h = React.createElement;
  var useState = React.useState;
  var useEffect = React.useEffect;
  var useRef = React.useRef;

  var DB_URL = '/sqlite/canon.db';

  /* ─── DB access helpers ─── */
  function query(db, sql, params) {
    var stmt = db.prepare(sql);
    if (params) stmt.bind(params);
    var rows = [];
    while (stmt.step()) rows.push(stmt.getAsObject());
    stmt.free();
    return rows;
  }

  /* ─── App ─── */
  function App() {
    var [db, setDb] = useState(null);
    var [error, setError] = useState(null);
    var [texts, setTexts] = useState([]);
    var [activeText, setActiveText] = useState(null);
    var [chapters, setChapters] = useState([]);
    var [activeChapter, setActiveChapter] = useState(null);
    var [verses, setVerses] = useState([]);
    var [searchQuery, setSearchQuery] = useState('');
    var [searchResults, setSearchResults] = useState(null);

    // Load DB on mount
    useEffect(function () {
      var cancelled = false;
      window.initSqlJs({
        locateFile: function (f) { return '/shared/vendor/' + f; }
      }).then(function (SQL) {
        return fetch(DB_URL).then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status + ' fetching canon.db');
          return r.arrayBuffer();
        }).then(function (buf) {
          if (cancelled) return;
          var database = new SQL.Database(new Uint8Array(buf));
          var rows = query(database, 'SELECT * FROM texts ORDER BY book');
          setTexts(rows);
          setDb(database);
        });
      }).catch(function (err) {
        if (!cancelled) setError(err.message);
      });
      return function () { cancelled = true; };
    }, []);

    // Load chapters when a text is selected
    function selectText(text) {
      setActiveText(text);
      setSearchQuery('');
      setSearchResults(null);
      var rows = query(db, 'SELECT DISTINCT chapter FROM verses WHERE book = ? ORDER BY chapter', [text.book]);
      setChapters(rows.map(function (r) { return r.chapter; }));
      if (rows.length > 0) {
        selectChapter(rows[0].chapter, text);
      }
    }

      // Load verses when a chapter is selected
    function selectChapter(ch, textOverride) {
      var book = (textOverride || activeText || {}).book;
      if (!book) {
        console.warn('[Canon] selectChapter called without active text');
        return;
      }
      setActiveChapter(ch);
      var rows = query(db,
        'SELECT * FROM verses WHERE book = ? AND chapter = ? ORDER BY verse',
        [book, ch]);
      setVerses(rows);
    }

    // Search — uses LIKE, works with Devanagari substrings
    function runSearch(q) {
      setSearchQuery(q);
      if (!q.trim()) { setSearchResults(null); return; }
      try {
        var like = '%' + q + '%';
        var rows = query(db, [
          'SELECT record_id, book, chapter, verse, text, iast, meter',
          'FROM verses',
          'WHERE text LIKE ? OR iast LIKE ?',
          'ORDER BY chapter, verse',
          'LIMIT 100'
        ].join(' '), [like, like]);
        setSearchResults(rows);
      } catch (e) {
        console.error('[Canon] search error:', e);
        setSearchResults([]);
      }
    }

    if (error) {
      return h('div', null,
        h('header', { className: 'cn-header' },
          h('div', { className: 'cn-header-inner' },
            h('div', { className: 'cn-brand' }, 'Aigaane · Canon'),
            h('a', { className: 'cn-back', href: '/' }, '← Aigaane')
          )
        ),
        h('div', { className: 'cn-loader' },
          h('div', { className: 'cn-error' }, 'Error: ' + error)
        )
      );
    }

    if (!db) {
      return h('div', { className: 'cn-loader' },
        h('div', { className: 'cn-loader-spinner' }),
        h('div', null, 'Loading canonical corpus…')
      );
    }

    return h('div', null,
      h('header', { className: 'cn-header' },
        h('div', { className: 'cn-header-inner' },
          h('div', { className: 'cn-brand' }, 'Aigaane · Canon'),
          h('a', { className: 'cn-back', href: '/' }, '← Aigaane')
        )
      ),
      h('main', { className: 'cn-container' },
        // Search bar always visible
        h('div', { className: 'cn-search-wrap' },
          h('input', {
            className: 'cn-search',
            type: 'text',
            placeholder: 'Search Devanagari, IAST, or meter…',
            value: searchQuery,
            onChange: function (e) { runSearch(e.target.value); }
          }),
          h('div', { className: 'cn-search-hint' },
            db ? (texts.length + ' texts · ' + '200 verses indexed') : 'Loading…'
          )
        ),

        // Search results view
        searchResults !== null ?
          h(SearchResults, { results: searchResults, query: searchQuery }) :

        // No text selected — show text list
        !activeText ?
          h('div', null,
            h('div', { className: 'cn-hero' },
              h('div', { className: 'cn-hero-dev indic' }, 'ग्रन्थाः'),
              h('h1', { className: 'cn-hero-title' }, 'Aigaane Canon'),
              h('p', { className: 'cn-hero-sub' },
                'Browse, search, and read classical Hindu scripture with Devanagari, IAST, and metrical analysis.')
            ),
            h('div', { className: 'cn-text-grid' },
              texts.map(function (t) {
                return h('div', {
                  key: t.book,
                  className: 'cn-text-card',
                  onClick: function () { selectText(t); }
                },
                  h('h3', null, t.book),
                  h('div', { className: 'cn-text-meta' },
                    h('span', null, t.total_verses + ' verses'),
                    h('span', null, t.total_chapters + ' chapters'),
                    t.room ? h('span', null, t.room) : null
                  )
                );
              })
            )
          ) :

        // Text selected — show chapters + verses
        h('div', null,
          h('div', { className: 'cn-breadcrumb' },
            h('a', { onClick: function () { setActiveText(null); setVerses([]); } }, 'Canon'),
            h('span', { className: 'cn-breadcrumb-sep' }, '›'),
            h('span', null, activeText.book)
          ),
          h('div', { className: 'cn-chapter-tabs' },
                        chapters.map(function (ch) {
              return h('button', {
                key: ch,
                className: 'cn-chapter-tab' + (ch === activeChapter ? ' active' : ''),
                onClick: function () { selectChapter(ch, activeText); }
              }, 'Chapter ' + ch);
            })
          ),
          h('div', { className: 'cn-verse-list' },
            verses.map(function (v) {
              return h(VerseCard, { key: v.record_id, verse: v });
            })
          )
        )
      )
    );
  }

  function VerseCard(props) {
    var v = props.verse;
    return h('div', { className: 'cn-verse' },
      h('div', { className: 'cn-verse-id' }, v.record_id),
      h('div', { className: 'cn-verse-text indic' }, v.text),
      v.iast ? h('div', { className: 'cn-verse-iast' }, v.iast) : null,
      h('div', { className: 'cn-verse-meta' },
        v.meter ? h('span', { className: 'cn-tag' }, v.meter) : null,
        h('span', null, 'Chapter ' + v.chapter + ' · Verse ' + v.verse)
      )
    );
  }

  function SearchResults(props) {
    var results = props.results;
    if (results.length === 0) {
      return h('div', { className: 'cn-search-status' },
        'No results for "' + props.query + '"');
    }
    return h('div', null,
      h('div', { className: 'cn-search-status' },
        results.length + ' result' + (results.length === 1 ? '' : 's') +
        ' for "' + props.query + '"'),
      h('div', { className: 'cn-verse-list' },
        results.map(function (v) {
          return h(VerseCard, { key: v.record_id, verse: v });
        })
      )
    );
  }

  var container = document.getElementById('root');
  if (!container) return;
  container.innerHTML = '';
  var root = ReactDOM.createRoot(container);
  root.render(h(App));
})();