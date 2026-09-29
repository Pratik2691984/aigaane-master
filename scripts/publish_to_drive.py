"""
scripts/publish_to_drive.py
Uploads corpus/ envelopes to AIGAANE_HINDU_SCRIPTURE_CANON on Google Drive.
Uses google-auth. Updates existing files. Creates missing folders.
"""
import json
import pathlib
import sys
from typing import Optional

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
except ImportError:
    print("[ERROR] Missing Google libraries. Run:")
    print("  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
TOKEN_FILE = ROOT / "token.json"
ROOT_FOLDER_NAME = "AIGAANE_HINDU_SCRIPTURE_CANON"


def get_credentials():
    if not TOKEN_FILE.exists():
        print(f"[ERROR] token.json not found at {TOKEN_FILE}")
        print("You need Google Drive OAuth credentials.")
        print("See setup instructions in the next message.")
        sys.exit(1)
    return Credentials.from_authorized_user_file(str(TOKEN_FILE), ["https://www.googleapis.com/auth/drive"])


class DriveSync:
    def __init__(self, creds):
        self.service = build("drive", "v3", credentials=creds)
        self.cache = {}
        self.root_id = self._find_root()

    def _find_root(self) -> str:
        res = self.service.files().list(
            q=f"name='{ROOT_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id,name)"
        ).execute()
        files = res.get("files", [])
        if not files:
            print(f"[ERROR] Folder '{ROOT_FOLDER_NAME}' not found on Drive.")
            sys.exit(1)
        return files[0]["id"]

    def get_folder(self, name: str, parent_id: str) -> str:
        key = f"{parent_id}/{name}"
        if key in self.cache:
            return self.cache[key]
        res = self.service.files().list(
            q=f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id)"
        ).execute()
        files = res.get("files", [])
        if files:
            fid = files[0]["id"]
        else:
            meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
            fid = self.service.files().create(body=meta, fields="id").execute()["id"]
            print(f"  [MKDIR] {name}")
        self.cache[key] = fid
        return fid

    def resolve_path(self, segments: list) -> str:
        cur = self.root_id
        for seg in segments:
            cur = self.get_folder(seg, cur)
        return cur

    def upload(self, local_path: pathlib.Path, drive_segments: list):
        folder_id = self.resolve_path(drive_segments)
        name = local_path.name
        res = self.service.files().list(
            q=f"name='{name}' and '{folder_id}' in parents and trashed=false",
            fields="files(id)"
        ).execute()
        existing = res.get("files", [])
        media = MediaFileUpload(str(local_path), mimetype="application/json", resumable=True)
        if existing:
            fid = existing[0]["id"]
            self.service.files().update(fileId=fid, media_body=media).execute()
            print(f"  [UPDATE] {'/'.join(drive_segments)}/{name}")
        else:
            meta = {"name": name, "parents": [folder_id]}
            self.service.files().create(body=meta, media_body=media, fields="id").execute()
            print(f"  [CREATE] {'/'.join(drive_segments)}/{name}")


def main():
    print("=== Google Drive Publish ===\n")
    creds = get_credentials()
    sync = DriveSync(creds)
    print(f"[OK] Connected. Root folder ID: {sync.root_id}\n")

    # Find every envelope in corpus/stotra/ or corpus/<cabinet>/...
    published = 0
    for env in sorted(CORPUS.rglob("*.json")):
        if env.name == "manifest.json":
            continue

        # Determine the Drive path from the corpus path
        rel = env.relative_to(CORPUS)
        parts = list(rel.parts)
        # e.g. corpus/stotra/gita/chapter_01/chapter_01.json
        #      -> stotra maps to CABINET_SMRITI_ITIHASA? Not reliably.

        # Instead read the envelope to get the canonical path
        try:
            data = json.loads(env.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[SKIP] {env}: {e}")
            continue

        meta = data.get("file_metadata", {})
        cabinet = meta.get("cabinet")
        room = meta.get("room")
        section = meta.get("section")
        if not (cabinet and room and section):
            print(f"[SKIP] {env}: missing cabinet/room/section")
            continue

        # Drive path: CABINET_xxx/ROOM/chapter_01
        section_slug = str(section).lower().replace(" ", "_")
        segments = [cabinet, room, section_slug]
        sync.upload(env, segments)
        published += 1

    print(f"\n[DONE] {published} envelopes published.")


if __name__ == "__main__":
    main()