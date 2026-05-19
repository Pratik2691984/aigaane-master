from typing import Any, Dict, List
import copy

try:
    from api.engines.derivation_session import DerivationSession
except ModuleNotFoundError:
    from engines.derivation_session import DerivationSession


class DerivationReplayExporter:
    def export_replay(self, session: DerivationSession) -> Dict[str, Any]:
        if not hasattr(session, "steps"):
            raise ValueError("session must be a DerivationSession.")

        timeline = []
        ambiguity_branch_ids = self._ambiguity_branch_ids(getattr(session, "ambiguity_branches", []))

        for step in session.steps:
            frame = {
                "frame_id": f"frame_{step.step_id}",
                "step_id": step.step_id,
                "timestamp": session.created_at,
                "title": f"{step.engine}: {step.operation}",
                "engine": step.engine,
                "operation": step.operation,
                "input_state": copy.deepcopy(step.input_state),
                "output_state": copy.deepcopy(step.output_state),
            }
            if ambiguity_branch_ids:
                frame["ambiguity_branch_ids"] = copy.deepcopy(ambiguity_branch_ids)
            timeline.append(frame)

        return {
            "replay_id": f"replay_{session.session_id}",
            "timeline": timeline,
            "metadata": {
                "session_id": session.session_id,
                "created_at": session.created_at,
                "input_text": session.input_text,
                "total_frames": len(timeline),
            },
        }

    def _ambiguity_branch_ids(self, branches: List[Dict[str, Any]]) -> List[str]:
        branch_ids = []
        for index, branch in enumerate(branches):
            if not isinstance(branch, dict):
                branch_ids.append(f"branch_{index + 1}")
                continue
            branch_ids.append(
                branch.get("branch_id")
                or branch.get("candidate_id")
                or f"branch_{index + 1}"
            )
        return branch_ids
