from pathlib import Path
from typing import Any, Dict, List, Optional
import json

try:
    from api.engines.derivation_session import DerivationSession
except ModuleNotFoundError:
    from engines.derivation_session import DerivationSession


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STORAGE_DIR = ROOT / "debug_sessions"


class DebugSessionStorage:
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir) if storage_dir is not None else DEFAULT_STORAGE_DIR

    def _ensure_storage_dir(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id is required.")
        normalized_session_id = session_id.strip()
        if any(separator in normalized_session_id for separator in ("/", "\\")):
            raise ValueError("session_id must not contain path separators.")
        return self.storage_dir / f"{normalized_session_id}.json"

    def _read_payload(self, path: Path) -> Dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed session JSON: {path.name}") from exc
        except OSError as exc:
            raise ValueError(f"Unable to read session: {path.name}") from exc

        if not isinstance(payload, dict):
            raise ValueError("Invalid session payload.")
        return payload

    def save_session(self, session: DerivationSession) -> str:
        if not hasattr(session, "session_id") or not callable(getattr(session, "to_dict", None)):
            raise ValueError("session must be a DerivationSession.")

        self._ensure_storage_dir()
        path = self._session_path(session.session_id)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(session.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        return str(Path("debug_sessions") / path.name).replace("\\", "/")

    def load_session(self, session_id: str) -> DerivationSession:
        self._ensure_storage_dir()
        path = self._session_path(session_id)
        if not path.exists():
            raise ValueError("Session not found.")

        payload = self._read_payload(path)
        try:
            return DerivationSession.from_dict(payload)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid session payload.") from exc

    def list_sessions(self) -> List[Dict[str, Any]]:
        self._ensure_storage_dir()
        sessions: List[Dict[str, Any]] = []
        for path in sorted(self.storage_dir.glob("*.json")):
            payload = self._read_payload(path)
            try:
                session = DerivationSession.from_dict(payload)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("Invalid session payload.") from exc
            sessions.append(
                {
                    "session_id": session.session_id,
                    "created_at": session.created_at,
                    "step_count": len(session.steps),
                }
            )
        return sessions

    def delete_session(self, session_id: str) -> bool:
        self._ensure_storage_dir()
        path = self._session_path(session_id)
        if not path.exists():
            return False
        path.unlink()
        return True
