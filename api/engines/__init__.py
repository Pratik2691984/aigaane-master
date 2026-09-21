# api/engines/__init__.py
#
# Namespace extension: expose repo-root engines/ as a subpackage
# of this package, so `from engines.phonology.sandhi import ...`
# resolves even when api/ has priority on sys.path.

from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
_root_engines = _repo_root / "engines"

if _root_engines.is_dir():
    p = str(_root_engines)
    if p not in __path__:
        __path__.append(p)
