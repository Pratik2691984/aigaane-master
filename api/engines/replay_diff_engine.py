from typing import Any, Dict, List, Set, Tuple
import copy
import json


class ReplayDiffEngine:
    def compare_replays(self, base_replay: Dict[str, Any], target_replay: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(base_replay, dict) or not isinstance(target_replay, dict):
            raise ValueError("Replay diff inputs must be dictionaries.")

        base_frames = self._timeline(base_replay)
        target_frames = self._timeline(target_replay)
        base_by_id = self._index_by_step_id(base_frames)
        target_by_id = self._index_by_step_id(target_frames)

        step_diffs = self._diff_indexed_items(base_by_id, target_by_id, "step")
        sutra_diffs = self._diff_sets(
            self._sutra_refs(base_frames),
            self._sutra_refs(target_frames),
            "sutra",
        )
        branch_diffs = self._diff_sets(
            self._branch_refs(base_replay, base_frames),
            self._branch_refs(target_replay, target_frames),
            "branch",
        )
        semantic_diffs = self._diff_indexed_items(
            self._semantic_index(base_replay, base_frames),
            self._semantic_index(target_replay, target_frames),
            "semantic",
        )

        return {
            "baseReplayId": self._replay_id(base_replay),
            "targetReplayId": self._replay_id(target_replay),
            "stepDiffs": step_diffs,
            "sutraDiffs": sutra_diffs,
            "branchDiffs": branch_diffs,
            "semanticDiffs": semantic_diffs,
            "summary": {
                "addedSteps": self._count_kind(step_diffs, "added"),
                "removedSteps": self._count_kind(step_diffs, "removed"),
                "changedSteps": self._count_kind(step_diffs, "changed"),
                "addedSutras": self._count_kind(sutra_diffs, "added"),
                "removedSutras": self._count_kind(sutra_diffs, "removed"),
                "addedBranches": self._count_kind(branch_diffs, "added"),
                "removedBranches": self._count_kind(branch_diffs, "removed"),
                "addedSemanticAnnotations": self._count_kind(semantic_diffs, "added"),
                "removedSemanticAnnotations": self._count_kind(semantic_diffs, "removed"),
                "changedSemanticAnnotations": self._count_kind(semantic_diffs, "changed"),
            },
        }

    def _timeline(self, replay: Dict[str, Any]) -> List[Dict[str, Any]]:
        timeline = replay.get("timeline", [])
        if not isinstance(timeline, list):
            return []
        return [copy.deepcopy(frame) for frame in timeline if isinstance(frame, dict)]

    def _replay_id(self, replay: Dict[str, Any]) -> str:
        replay_id = replay.get("replay_id") or replay.get("replayId")
        if replay_id:
            return str(replay_id)
        metadata = replay.get("metadata") if isinstance(replay.get("metadata"), dict) else {}
        session_id = metadata.get("session_id") or metadata.get("sessionId")
        return f"replay_{session_id}" if session_id else "unknown"

    def _index_by_step_id(self, frames: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        indexed = {}
        for index, frame in enumerate(frames):
            step_id = frame.get("step_id") or frame.get("stepId") or frame.get("frame_id") or f"index_{index}"
            indexed[str(step_id)] = frame
        return indexed

    def _diff_indexed_items(
        self,
        base_items: Dict[str, Dict[str, Any]],
        target_items: Dict[str, Dict[str, Any]],
        label: str,
    ) -> List[Dict[str, Any]]:
        diffs = []
        for item_id in sorted(set(base_items) | set(target_items)):
            if item_id not in base_items:
                diffs.append({"type": "added", f"{label}Id": item_id, "target": copy.deepcopy(target_items[item_id])})
            elif item_id not in target_items:
                diffs.append({"type": "removed", f"{label}Id": item_id, "base": copy.deepcopy(base_items[item_id])})
            elif self._stable_json(base_items[item_id]) != self._stable_json(target_items[item_id]):
                diffs.append(
                    {
                        "type": "changed",
                        f"{label}Id": item_id,
                        "base": copy.deepcopy(base_items[item_id]),
                        "target": copy.deepcopy(target_items[item_id]),
                    }
                )
        return diffs

    def _diff_sets(self, base_values: Set[str], target_values: Set[str], label: str) -> List[Dict[str, Any]]:
        diffs = []
        for value in sorted(target_values - base_values):
            diffs.append({"type": "added", f"{label}Id": value})
        for value in sorted(base_values - target_values):
            diffs.append({"type": "removed", f"{label}Id": value})
        return diffs

    def _sutra_refs(self, frames: List[Dict[str, Any]]) -> Set[str]:
        sutras: Set[str] = set()
        for frame in frames:
            self._collect_matching_values(frame, {"sutra", "sutra_id", "sutraId"}, sutras)
        return sutras

    def _branch_refs(self, replay: Dict[str, Any], frames: List[Dict[str, Any]]) -> Set[str]:
        branches: Set[str] = set()
        candidates = list(frames)
        for key in ("ambiguity_branches", "ambiguityBranches", "branches"):
            value = replay.get(key)
            if isinstance(value, list):
                candidates.extend(item for item in value if isinstance(item, dict))
        for candidate in candidates:
            for key in ("ambiguity_branch_ids", "ambiguityBranchIds"):
                value = candidate.get(key)
                if isinstance(value, list):
                    branches.update(str(item) for item in value)
            for key in ("branch_id", "branchId", "candidate_id", "candidateId", "selected_branch_id", "selectedBranchId"):
                if candidate.get(key):
                    branches.add(str(candidate[key]))
        return branches

    def _semantic_index(self, replay: Dict[str, Any], frames: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        annotations: Dict[str, Dict[str, Any]] = {}
        raw_annotations: List[Tuple[str, Dict[str, Any]]] = []
        for key in ("semanticAttributions", "semantic_attributions", "semantic_annotations", "semanticAnnotations"):
            value = replay.get(key)
            if isinstance(value, list):
                raw_annotations.extend((key, item) for item in value if isinstance(item, dict))
        for frame in frames:
            frame_id = str(frame.get("step_id") or frame.get("frame_id") or len(raw_annotations))
            for key in ("semanticAttributions", "semantic_attributions", "semantic_annotations", "semanticAnnotations"):
                value = frame.get(key)
                if isinstance(value, list):
                    raw_annotations.extend((frame_id, item) for item in value if isinstance(item, dict))
            semantic = frame.get("semantic")
            if isinstance(semantic, dict):
                raw_annotations.append((frame_id, semantic))

        for index, (scope, annotation) in enumerate(raw_annotations):
            annotation_id = (
                annotation.get("semantic_id")
                or annotation.get("semanticId")
                or annotation.get("semanticTag")
                or annotation.get("semantic_tag")
                or annotation.get("tag")
                or f"{scope}:{index}"
            )
            annotations[str(annotation_id)] = copy.deepcopy(annotation)
        return annotations

    def _collect_matching_values(self, value: Any, keys: Set[str], output: Set[str]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in keys and child:
                    output.add(str(child))
                else:
                    self._collect_matching_values(child, keys, output)
        elif isinstance(value, list):
            for child in value:
                self._collect_matching_values(child, keys, output)

    def _stable_json(self, value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _count_kind(self, diffs: List[Dict[str, Any]], kind: str) -> int:
        return sum(1 for diff in diffs if diff.get("type") == kind)
