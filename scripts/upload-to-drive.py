#!/usr/bin/env python3
"""Upload rendered motion graphics to a Google Drive folder.

Uses a service-account JSON key from the GDRIVE_SERVICE_ACCOUNT env var.
If a file with the same name already exists in the folder, it is updated
in place (no duplicates).
"""
import json
import os
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("renders")

    key_raw = os.environ.get("GDRIVE_SERVICE_ACCOUNT", "")
    if not key_raw:
        print("FATAL: GDRIVE_SERVICE_ACCOUNT secret is empty or not set.", file=sys.stderr)
        sys.exit(1)
    print(f"Key length: {len(key_raw)} chars")
    try:
        key = json.loads(key_raw)
    except json.JSONDecodeError as e:
        print(f"FATAL: GDRIVE_SERVICE_ACCOUNT is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Service account: {key.get('client_email', 'MISSING EMAIL')}")

    folder_id = os.environ.get("GDRIVE_FOLDER_ID", "")
    if not folder_id:
        print("FATAL: GDRIVE_FOLDER_ID secret is empty or not set.", file=sys.stderr)
        sys.exit(1)
    print(f"Folder ID: {folder_id}")

    creds = service_account.Credentials.from_service_account_info(key, scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds)

    # Map existing file names -> ids in the target folder
    existing = {}
    page_token = None
    while True:
        resp = (
            drive.files()
            .list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id,name),nextPageToken",
                pageToken=page_token,
                pageSize=100,
            )
            .execute()
        )
        for f in resp.get("files", []):
            existing[f["name"]] = f["id"]
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    files = sorted(p for p in src_dir.iterdir() if p.is_file())
    if not files:
        print("No files to upload.")
        return

    for path in files:
        media = MediaFileUpload(str(path), resumable=True)
        if path.name in existing:
            drive.files().update(
                fileId=existing[path.name], media_body=media
            ).execute()
            print(f"updated: {path.name}")
        else:
            drive.files().create(
                body={"name": path.name, "parents": [folder_id]},
                media_body=media,
                fields="id",
            ).execute()
            print(f"uploaded: {path.name}")

    print(f"Done: {len(files)} files in Drive folder.")


if __name__ == "__main__":
    main()
