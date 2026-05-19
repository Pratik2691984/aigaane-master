from typing import Any, Dict, List
import copy

try:
    from api.engines.derivation_session import DerivationSession
except ModuleNotFoundError:
    from engines.derivation_session import DerivationSession


class DerivationGraphExporter:
    def export_session_graph(self, session: DerivationSession) -> Dict[str, Any]:
        if not hasattr(session, "steps"):
            raise ValueError("session must be a DerivationSession.")

        nodes = []
        edges = []
        ambiguity_branch_ids = self._ambiguity_branch_ids(getattr(session, "ambiguity_branches", []))

        for index, step in enumerate(session.steps):
            node = {
                "node_id": f"node_{step.step_id}",
                "step_id": step.step_id,
                "title": f"{step.engine}: {step.operation}",
                "engine": step.engine,
                "operation": step.operation,
                "input_state": copy.deepcopy(step.input_state),
                "output_state": copy.deepcopy(step.output_state),
                "timestamp": session.created_at,
            }
            if ambiguity_branch_ids:
                node["ambiguity_branch_ids"] = copy.deepcopy(ambiguity_branch_ids)
            nodes.append(node)

            if step.parent_step_id:
                edges.append(
                    {
                        "edge_id": f"edge_{step.parent_step_id}_to_{step.step_id}",
                        "source": f"node_{step.parent_step_id}",
                        "target": f"node_{step.step_id}",
                        "relation": "derives_to",
                    }
                )

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "session_id": session.session_id,
                "created_at": session.created_at,
                "input_text": session.input_text,
                "total_nodes": len(nodes),
                "total_edges": len(edges),
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
