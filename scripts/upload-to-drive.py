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
# Parent folder containing all per-video folders (Unseen Atlas / videos)
VIDEOS_PARENT_ID = "12hSLUK2pE20AMdXYAcCCeROSvozF-rMo"
# Name of the motion graphics subfolder inside each video folder
GRAPHICS_FOLDER_NAME = "09 - Motion Graphics"


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


def find_video_folder(drive, video_slug):
    """Find the video's own folder by slug. Returns folder ID or None."""
    resp = (
        drive.files()
        .list(
            q=f"'{VIDEOS_PARENT_ID}' in parents and name contains '{video_slug}' "
            f"and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id,name)",
            pageSize=5,
        )
        .execute()
    )
    files = resp.get("files", [])
    return files[0]["id"] if files else None


# Shared pools (copied into each video folder once)
SFX_POOL_ID = "1Gy43O01w6lxB7Mmf-2JJ0xx0eurFZxJH"
MUSIC_POOL_ID = "1QDwiKY8WsUJgqiLzxMWXW6-ykX0FVOB7"


def sync_shared_assets(drive, video_folder_id):
    """Copy SFX + Music pools into the video folder (once, skips existing)."""
    for pool_id, sub in [(SFX_POOL_ID, "SFX"), (MUSIC_POOL_ID, "Music")]:
        dest = get_or_create_folder(drive, sub, video_folder_id)
        # existing names in destination
        existing = set()
        pt = None
        while True:
            resp = drive.files().list(
                q=f"'{dest}' in parents and trashed=false",
                fields="files(name),nextPageToken", pageToken=pt, pageSize=100,
            ).execute()
            existing.update(f["name"] for f in resp.get("files", []))
            pt = resp.get("nextPageToken")
            if not pt:
                break
        # pool files
        pt = None
        copied = 0
        while True:
            resp = drive.files().list(
                q=f"'{pool_id}' in parents and trashed=false",
                fields="files(id,name),nextPageToken", pageToken=pt, pageSize=100,
            ).execute()
            for f in resp.get("files", []):
                if f["name"] not in existing:
                    drive.files().copy(
                        fileId=f["id"],
                        body={"name": f["name"], "parents": [dest]},
                        fields="id",
                    ).execute()
                    copied += 1
            pt = resp.get("nextPageToken")
            if not pt:
                break
        print(f"  {sub}: {copied} new file(s) copied")


def main():
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("renders")

    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN", "")
    if not refresh_token:
        print("FATAL: GDRIVE_REFRESH_TOKEN secret is empty or not set.", file=sys.stderr)
        sys.exit(1)
    print(f"Refresh token length: {len(refresh_token)} chars")

    folder_id = os.environ.get("GDRIVE_FOLDER_ID", "")
    if not folder_id:
        # Auto mode: find the video's own folder, create/find its graphics subfolder
        config_path = Path("video-config.json")
        if config_path.exists():
            with open(config_path) as f:
                video_slug = json.load(f).get("video_slug", "")
        else:
            video_slug = ""
        if not video_slug:
            print("FATAL: video-config.json missing video_slug and no GDRIVE_FOLDER_ID.",
                  file=sys.stderr)
            sys.exit(1)
        print(f"Auto mode: video slug = {video_slug}")
        video_folder = find_video_folder(drive, video_slug)
        if not video_folder:
            print(f"FATAL: video folder '{video_slug}' not found in Drive.",
                  file=sys.stderr)
            sys.exit(1)
        # One-time: copy shared SFX + Music pools into this video's folder
        print("Syncing shared assets...")
        sync_shared_assets(drive, video_folder)
        folder_id = get_or_create_folder(drive, GRAPHICS_FOLDER_NAME, video_folder)
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
