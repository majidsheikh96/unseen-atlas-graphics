#!/usr/bin/env python3
"""Download binary assets from Drive using OAuth (CI-safe)."""
import os
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

CLIENT_ID = "950969484933-umf8vj3nbrte6f5bpo87i4bh464vhb1f.apps.googleusercontent.com"

# file_id -> local path
ASSETS = {
    "1ZJl2uAhNB0rmxpbDHHvLWJwAIxrZhkA_": "assets/audio/clean-whoosh.mp3",
    "1fB2ZklD9qBftHg4nrIBuRlE02EF8ec86": "assets/audio/mouse-click.mp3",
    "1R3d5_9nUgsbjZwRlSUVvsiJFmhKN_G1A": "assets/avatar.jpg",
}

creds = Credentials(
    None,
    refresh_token=os.environ["GDRIVE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=os.environ["GDRIVE_CLIENT_SECRET"],
    scopes=["https://www.googleapis.com/auth/drive"],
)
drive = build("drive", "v3", credentials=creds)

for fid, path in ASSETS.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"Downloading {path}...")
    req = drive.files().get_media(fileId=fid)
    with open(path, "wb") as f:
        dl = MediaIoBaseDownload(f, req)
        done = False
        while not done:
            _, done = dl.next_chunk()
    size = os.path.getsize(path)
    print(f"  {path}: {size} bytes")
    if size < 1000:
        print(f"FATAL: {path} too small, download failed", file=sys.stderr)
        sys.exit(1)
print("All assets downloaded.")
