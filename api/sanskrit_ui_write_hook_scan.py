"""Scan UI sources for executable canonical-write bindings.

Documentation strings and <code> captions are not bindings.
"""

from __future__ import annotations

import re
from typing import List

_FLAG = "AIGAANE_ENABLE_CANONICAL_DHATU_WRITE"
_PROMOTE = "promote_ready_dhatu_to_canonical"

_STRIP_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
_STRIP_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_STRIP_LINE_COMMENT = re.compile(r"//.*?$", re.M)
_STRIP_CODE_TAG = re.compile(r"<code\b[^>]*>.*?</code>", re.I | re.S)
_STRIP_DQ = re.compile(r'"(?:\\.|[^"\\])*"')
_STRIP_SQ = re.compile(r"'(?:\\.|[^'\\])*'")
_STRIP_BT = re.compile(r"`(?:\\.|[^`\\])*`")

_EXEC_PATTERNS = [
    re.compile(r"process\.env\." + _FLAG),
    re.compile(r"process\.env\[['\"]" + _FLAG + r"['\"]\]"),
    re.compile(_FLAG + r"\s*="),
    re.compile(r"fetch\s*\([^)]*" + _PROMOTE),
    re.compile(r"\.addEventListener\s*\([^)]*" + _PROMOTE),
    re.compile(r"require\s*\(\s*['\"][^'\"]*" + _PROMOTE),
    re.compile(r"import\s+.*?" + _PROMOTE),
]


def strip_non_executable(source: str) -> str:
    text = _STRIP_HTML_COMMENT.sub(" ", source)
    text = _STRIP_BLOCK_COMMENT.sub(" ", text)
    text = _STRIP_LINE_COMMENT.sub(" ", text)
    text = _STRIP_CODE_TAG.sub(" ", text)
    text = _STRIP_DQ.sub('""', text)
    text = _STRIP_SQ.sub("''", text)
    text = _STRIP_BT.sub("``", text)
    return text


def executable_canonical_write_bindings(source: str) -> List[str]:
    body = strip_non_executable(source)
    found: List[str] = []
    if re.search(r"\b" + _FLAG + r"\b", body):
        found.append(_FLAG)
    if re.search(r"\b" + _PROMOTE + r"\b", body):
        found.append(_PROMOTE)
    for pattern in _EXEC_PATTERNS:
        if pattern.search(source) and pattern.search(body):
            found.append(pattern.pattern)
    seen = set()
    out = []
    for item in found:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
