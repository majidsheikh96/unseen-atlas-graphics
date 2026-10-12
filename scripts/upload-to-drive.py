#!/usr/bin/env python3
"""Upload rendered motion graphics to a Google Drive folder.

Uses an OAuth refresh token from the GDRIVE_REFRESH_TOKEN env var
(authenticates as the channel owner — no service-account quota limits).
If a file with the same name already exists in the folder, it is updated
in place (no duplicates).
"""
import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
# OAuth client for "Unseen Atlas Drive Upload" (Desktop app)
CLIENT_ID = "950969484933-umf8vj3nbrte6f5bpo87i4bh464vhb1f.apps.googleusercontent.com"
CLIENT_SECRET = os.environ.get("GDRIVE_CLIENT_SECRET", "")
TOKEN_URI = "https://oauth2.googleapis.com/token"
# Parent folder for all auto-created per-video motion graphics folders
GRAPHICS_PARENT_ID = "1T93-b-4rLh6H_x6kMgaqG-IYMBOgjm1j"


def get_or_create_folder(drive, name, parent_id):
    """Find a subfolder by name, or create it. Returns folder ID."""
    resp = (
        drive.files()
        .list(
            q=f"'{parent_id}' in parents and name='{name}' "
            f"and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id,name)",
            pageSize=5,
        )
        .execute()
    )
    files = resp.get("files", [])
    if files:
        print(f"Using existing folder: {name}")
        return files[0]["id"]
    created = (
        drive.files()
        .create(
            body={
                "name": name,
                "parents": [parent_id],
                "mimeType": "application/vnd.google-apps.folder",
            },
            fields="id",
        )
        .execute()
    )
    print(f"Created folder: {name}")
    return created["id"]


def main():
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("renders")

    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN", "")
    if not refresh_token:
        print("FATAL: GDRIVE_REFRESH_TOKEN secret is empty or not set.", file=sys.stderr)
        sys.exit(1)
    print(f"Refresh token length: {len(refresh_token)} chars")

    folder_id = os.environ.get("GDRIVE_FOLDER_ID", "")
    if not folder_id:
        # Auto mode: read video slug from video-config.json, create/find subfolder
        config_path = Path("video-config.json")
        if config_path.exists():
            with open(config_path) as f:
                video_slug = json.load(f).get("video_slug", "uncategorized")
        else:
            video_slug = "uncategorized"
        print(f"Auto mode: video slug = {video_slug}")
        folder_id = get_or_create_folder(drive, video_slug, GRAPHICS_PARENT_ID)
    print(f"Folder ID: {folder_id}")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    drive = build("drive", "v3", credentials=creds)
    print("Authenticated as channel owner via OAuth.")

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
