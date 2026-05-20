from typing import Any, Dict, List
import csv
import io
import json
from xml.sax.saxutils import escape


class ScholarlyExportEngine:
    def export(self, payload: Dict[str, Any]) -> Dict[str, str]:
        if not isinstance(payload, dict):
            raise ValueError("Scholarly export input must be a dictionary.")
        return {
            "jsonld": self.export_jsonld(payload),
            "markdown": self.export_markdown(payload),
            "csv": self.export_csv(payload),
            "teiXml": self.export_tei_xml(payload),
        }

    def export_jsonld(self, payload: Dict[str, Any]) -> str:
        document = {
            "@context": {
                "aigaane": "https://aigaane.local/schema#",
                "input": "aigaane:input",
                "output": "aigaane:output",
                "derivationSteps": "aigaane:derivationSteps",
                "sutraReferences": "aigaane:sutraReferences",
                "ambiguityDecisions": "aigaane:ambiguityDecisions",
                "provenanceScore": "aigaane:provenanceScore",
                "semanticAttributions": "aigaane:semanticAttributions",
            },
            "@type": "aigaane:DerivationExport",
            "input": self._input(payload),
            "output": self._output(payload),
            "derivationSteps": self._steps(payload),
            "sutraReferences": sorted(self._sutras(payload)),
            "ambiguityDecisions": self._ambiguities(payload),
            "provenanceScore": payload.get("provenanceScore") or payload.get("provenance_score"),
            "semanticAttributions": self._semantic_attributions(payload),
        }
        return json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)

    def export_markdown(self, payload: Dict[str, Any]) -> str:
        lines = [
            "# Aigaane Derivation Report",
            "",
            f"- Input: {self._input(payload)}",
            f"- Output: {self._output(payload)}",
            f"- Provenance score: {self._provenance_value(payload)}",
            "",
            "## Derivation Steps",
        ]
        for step in self._steps(payload):
            lines.append(f"- {step.get('step_id') or step.get('stepId') or step.get('node_id')}: {step.get('operation') or step.get('title') or '-'}")
        lines.extend(["", "## Sutra References"])
        for sutra in sorted(self._sutras(payload)):
            lines.append(f"- {sutra}")
        lines.extend(["", "## Ambiguity Decisions"])
        for branch in self._ambiguities(payload):
            lines.append(f"- {branch.get('branch_id') or branch.get('candidate_id')}: {branch.get('status') or branch.get('decision') or '-'}")
        lines.extend(["", "## Semantic Attributions"])
        for attribution in self._semantic_attributions(payload):
            lines.append(f"- {attribution.get('stepId') or attribution.get('step_id')}: {attribution.get('semanticTag') or attribution.get('semantic_tag')}")
        return "\n".join(lines)

    def export_csv(self, payload: Dict[str, Any]) -> str:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=["step_id", "operation", "sutra", "semantic_tags"])
        writer.writeheader()
        for step in self._steps(payload):
            writer.writerow(
                {
                    "step_id": step.get("step_id") or step.get("stepId") or step.get("node_id") or "",
                    "operation": step.get("operation") or step.get("title") or "",
                    "sutra": self._first_value(step, {"sutra", "sutra_id", "sutraId"}) or "",
                    "semantic_tags": ";".join(sorted(self._semantic_tags(step))),
                }
            )
        return buffer.getvalue()

    def export_tei_xml(self, payload: Dict[str, Any]) -> str:
        steps = "".join(
            f'<step xml:id="{escape(str(step.get("step_id") or step.get("stepId") or step.get("node_id") or ""))}" sutra="{escape(str(self._first_value(step, {"sutra", "sutra_id", "sutraId"}) or ""))}">{escape(str(step.get("operation") or step.get("title") or ""))}</step>'
            for step in self._steps(payload)
        )
        return (
            "<TEI><text><body><div type=\"derivation\">"
            f"<ab type=\"input\">{escape(str(self._input(payload)))}</ab>"
            f"<ab type=\"output\">{escape(str(self._output(payload)))}</ab>"
            f"<list>{steps}</list>"
            "</div></body></text></TEI>"
        )

    def _input(self, payload: Dict[str, Any]) -> Any:
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        return payload.get("input") or payload.get("input_text") or metadata.get("input_text") or ""

    def _output(self, payload: Dict[str, Any]) -> Any:
        if payload.get("output"):
            return payload["output"]
        steps = self._steps(payload)
        if steps:
            return steps[-1].get("output_state") or steps[-1].get("outputState") or ""
        return ""

    def _steps(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in ("steps", "timeline", "nodes"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return []

    def _ambiguities(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in ("ambiguity_branches", "ambiguityBranches", "branches"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return []

    def _semantic_attributions(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in ("semanticAttributions", "semantic_attributions", "semantic_annotations", "semanticAnnotations"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return []

    def _sutras(self, value: Any) -> set:
        sutras = set()
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"sutra", "sutra_id", "sutraId"} and child:
                    sutras.add(str(child))
                else:
                    sutras.update(self._sutras(child))
        elif isinstance(value, list):
            for child in value:
                sutras.update(self._sutras(child))
        return sutras

    def _semantic_tags(self, value: Any) -> set:
        tags = set()
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"semanticTag", "semantic_tag", "tag"} and child:
                    tags.add(str(child))
                else:
                    tags.update(self._semantic_tags(child))
        elif isinstance(value, list):
            for child in value:
                tags.update(self._semantic_tags(child))
        return tags

    def _first_value(self, value: Any, keys: set) -> Any:
        if isinstance(value, dict):
            for key in keys:
                if value.get(key):
                    return value[key]
            for child in value.values():
                found = self._first_value(child, keys)
                if found:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = self._first_value(child, keys)
                if found:
                    return found
        return None

    def _provenance_value(self, payload: Dict[str, Any]) -> Any:
        score = payload.get("provenanceScore") or payload.get("provenance_score")
        if isinstance(score, dict):
            return score.get("score")
        return score if score is not None else "-"
