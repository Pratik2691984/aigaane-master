"""SamasaNode semantic validator (P1-A).

Enforces P1-P15 invariants that JSON Schema cannot express.
Runs on a well-formed SamasaNode dict (schema must pass first).
"""

from __future__ import annotations

import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from typing import Any


# ---- Configuration ----

MAX_DEPTH = 8
MAX_NODES = 64

NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://aigaane.in/schemas/samasa_node")

_PATH_RE = re.compile(r"children\[(\d+)\]")


@dataclass(frozen=True)
class Violation:
    code: str
    path: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.code}] {self.path}: {self.message}"


# ---- Public API ----

def validate_samasa_tree(node: dict) -> list[Violation]:
    """Run P1-P15 checks on a SamasaNode tree. Assumes JSON Schema passed."""
    violations: list[Violation] = []

    # P15 first
    input_surface = node.get("input_surface", "")
    if not isinstance(input_surface, str) or not input_surface:
        violations.append(Violation(
            "P15_RootInputMissing", "root.input_surface",
            "Root input_surface must be a non-empty string."
        ))

    # P14 — output_script consistent across tree
    root_script = node.get("output_script")
    for path, n in _iter_nodes(node, "root"):
        if n.get("output_script") != root_script:
            violations.append(Violation(
                "P14_ScriptMismatchAcrossTree",
                f"{path}.output_script",
                f"Expected '{root_script}', got '{n.get('output_script')}'.",
            ))

    # P10 — max depth
    _check_depth(node, violations, depth=0, path="root")

    # P11 — max nodes
    count = sum(1 for _ in _iter_nodes(node, "root"))
    if count > MAX_NODES:
        violations.append(Violation(
            "P11_MaxNodesExceeded", "root",
            f"Total nodes {count} > MAX_NODES {MAX_NODES}.",
            {"count": count, "max": MAX_NODES},
        ))

    # Main walk — P1, P3, P4, P6, P8, P12, P13
    _node_ids_seen: list[str] = []
    _walk(node, violations, "root", _node_ids_seen)

    # P7 — sibling analyses distinct analysis_index (only if ambiguity_group present)
    _check_ambiguity_siblings(node, violations)

    return violations


def compute_node_id(
    normalized: str,
    samasa_type: str,
    analysis_index: int,
    path_signature: str,
) -> str:
    """P13 — recomputable node_id formula."""
    key = f"a{analysis_index}|p{path_signature}|{normalized}|{samasa_type}"
    return str(uuid.uuid5(NAMESPACE, key))


# ---- Checks ----

def _iter_nodes(node: dict, path: str):
    yield path, node
    for i, child in enumerate(node.get("children") or []):
        yield from _iter_nodes(child, f"{path}.children[{i}]")


def _check_depth(node: dict, out: list[Violation], depth: int, path: str) -> None:
    if depth > MAX_DEPTH:
        out.append(Violation(
            "P10_MaxDepthExceeded", path,
            f"Depth {depth} > MAX_DEPTH {MAX_DEPTH}.",
            {"depth": depth, "max": MAX_DEPTH},
        ))
        return
    for i, child in enumerate(node.get("children") or []):
        _check_depth(child, out, depth + 1, f"{path}.children[{i}]")


def _walk(node: dict, out: list[Violation], path: str, node_ids: list[str]) -> None:
    norm = node.get("normalized", "")

    # P1 — NFC normalization
    if isinstance(norm, str) and norm != unicodedata.normalize("NFC", norm):
        out.append(Violation(
            "P1_NormalizedNotNFC", f"{path}.normalized",
            "normalized is not NFC.",
        ))

    # P4 — internal_sandhi rule_id regex (exists check deferred)
    for j, s in enumerate(node.get("internal_sandhi") or []):
        rule_id = s.get("rule_id", "")
        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", str(rule_id)):
            out.append(Violation(
                "P4_SandhiRuleFormatInvalid",
                f"{path}.internal_sandhi[{j}].rule_id",
                f"rule_id '{rule_id}' does not match N.N.N pattern.",
            ))

    # P3 — surface reconstruction from children + internal_sandhi
    children = node.get("children")
    if children:
        combined = "".join(c.get("surface", "") for c in children)
        transformed = combined
        for s in node.get("internal_sandhi") or []:
            before = s.get("before", "")
            after = s.get("after", "")
            if before and transformed.startswith(before):
                transformed = after + transformed[len(before):]
            elif before and before in transformed:
                transformed = transformed.replace(before, after, 1)
        if transformed != node.get("surface"):
            out.append(Violation(
                "P3_SurfaceNotReconstructable",
                f"{path}.surface",
                f"children+internal_sandhi yield '{transformed}' != parent '{node.get('surface')}'.",
                {"children_combined": combined, "after_sandhi": transformed},
            ))

    # P8 — analysis_index 0 when no ambiguity_group
    if node.get("ambiguity_group") is None and node.get("analysis_index", 0) != 0:
        out.append(Violation(
            "P8_AnalysisIndexWithoutGroup",
            f"{path}.analysis_index",
            "analysis_index must be 0 when ambiguity_group is null.",
        ))

    # P12 — duplicate node_id
    nid = node.get("node_id", "")
    if nid in node_ids:
        out.append(Violation(
            "P12_NodeIdDuplicate", f"{path}.node_id",
            f"node_id '{nid}' appears more than once.",
        ))
    else:
        node_ids.append(nid)

    # P13 — node_id recomputable
    try:
        expected = compute_node_id(
            node.get("normalized", ""),
            node.get("samasa_type", ""),
            node.get("analysis_index", 0),
            _path_signature(path),
        )
        if nid != expected:
            out.append(Violation(
                "P13_NodeIdMismatch", f"{path}.node_id",
                f"stored '{nid}' != recomputed '{expected}'.",
            ))
    except Exception as e:
        out.append(Violation(
            "P13_NodeIdComputationError", f"{path}.node_id",
            f"recomputation failed: {e}",
        ))

    for i, child in enumerate(children or []):
        _walk(child, out, f"{path}.children[{i}]", node_ids)


def _check_ambiguity_siblings(root: dict, out: list[Violation]) -> None:
    """P7 — analyses sharing ambiguity_group have distinct analysis_index."""
    analyses = root.get("_analyses") or []
    if not analyses:
        return
    by_group: dict[str, list[dict]] = {}
    for a in analyses:
        grp = a.get("ambiguity_group")
        if grp is not None:
            by_group.setdefault(grp, []).append(a)
    for grp, members in by_group.items():
        indices = [m.get("analysis_index") for m in members]
        if len(set(indices)) != len(indices):
            out.append(Violation(
                "P7_AmbiguityIndexCollision", f"analysis_group[{grp}]",
                f"Duplicate analysis_index within group: {indices}.",
            ))


def _path_signature(path: str) -> str:
    if path == "root":
        return "0"
    indices = [0] + [int(m.group(1)) for m in _PATH_RE.finditer(path)]
    return ".".join(str(i) for i in indices)