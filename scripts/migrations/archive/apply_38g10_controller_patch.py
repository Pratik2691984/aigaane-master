"""Apply Node 38G.10 corpus search NFC + empty-query wiring. No API/manifest/38H changes."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD_IMPORT = (
    'import { buildCorpusBrowserState, summarizeCorpusResults, computeVirtualWindow, VIRTUAL_CONFIG } '
    'from "./corpus/corpus-browser-engine.js";\n'
)
NEW_IMPORT = (
    'import { buildCorpusBrowserState, summarizeCorpusResults, computeVirtualWindow, VIRTUAL_CONFIG, nfcCorpusText } '
    'from "./corpus/corpus-browser-engine.js";\n'
)

OLD_FETCH = """  if (section === "search") {
    const searchQuery = query || "भू";
    const response = await fetch(`/api/sanskrit/search?q=${encodeURIComponent(searchQuery)}&limit=${limit}${typeParam}`);
    if (!response.ok) {
      return { valid: false, results: [], query: searchQuery };
    }
    return response.json();
  }
"""

NEW_FETCH = """  if (section === "search") {
    const searchQuery = nfcCorpusText(query).trim();
    if (!searchQuery) {
      const response = await fetch(`/api/sanskrit/search?limit=${limit}${typeParam}`);
      if (!response.ok) {
        return { valid: false, results: [], query: "" };
      }
      const payload = await response.json();
      payload.query = "";
      return payload;
    }
    const response = await fetch(`/api/sanskrit/search?q=${encodeURIComponent(searchQuery)}&limit=${limit}${typeParam}`);
    if (!response.ok) {
      return { valid: false, results: [], query: searchQuery };
    }
    const payload = await response.json();
    payload.query = searchQuery;
    return payload;
  }
"""

OLD_QUERY = '  const query = String(options.query ?? byId("corpus-browser-search-input")?.value ?? "").trim();\n'
NEW_QUERY = '  const query = nfcCorpusText(options.query ?? byId("corpus-browser-search-input")?.value ?? "").trim();\n'


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "nfcCorpusText(query).trim()" in text and 'query || "भू"' not in text:
        print("already patched")
        return 0
    missing = []
    if OLD_IMPORT not in text:
        missing.append("import")
    if OLD_FETCH not in text:
        missing.append("fetch")
    if OLD_QUERY not in text:
        missing.append("query")
    if missing:
        print("target blocks missing: " + ",".join(missing))
        return 1
    text = text.replace(OLD_IMPORT, NEW_IMPORT, 1)
    text = text.replace(OLD_FETCH, NEW_FETCH, 1)
    text = text.replace(OLD_QUERY, NEW_QUERY, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("patched " + str(TARGET))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())