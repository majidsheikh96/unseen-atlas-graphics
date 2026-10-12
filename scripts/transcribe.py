#!/usr/bin/env python3
"""Transcribe voiceover MP3s to SRT using faster-whisper.

- Input: voiceover/*.mp3
- Output: transcripts/*.srt (word-level timing for karaoke captions)
          transcripts/*.words.json (raw word timestamps)
- Post-processing: fixes known Whisper mishearings (e.g. Socotra variants).
- Uploads to the same auto-created Drive folder as motion graphics.

Usage: python3 scripts/transcribe.py [voiceover_dir] [output_dir]
"""
import json
import os
import re
import sys
from pathlib import Path

# Known Whisper mishearings -> correct spelling (case-insensitive)
CORRECTIONS = {
    r"\bpsychotra\b": "Socotra",
    r"\bsecotra\b": "Socotra",
    r"\bsocotora\b": "Socotra",
    r"\bsakotra\b": "Socotra",
}

MODEL_SIZE = os.environ.get("WHISPER_MODEL", "small")


def srt_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fix_text(text: str) -> str:
    for pattern, replacement in CORRECTIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def transcribe_file(model, audio_path: Path, out_dir: Path):
    print(f"Transcribing: {audio_path.name} ...")
    segments, info = model.transcribe(str(audio_path), word_timestamps=True)
    segments = list(segments)
    print(f"  detected language: {info.language} ({info.language_probability:.2f})")

    # Word-level SRT (one word per cue — for karaoke highlighting)
    srt_lines = []
    words_data = []
    idx = 1
    for seg in segments:
        for w in (seg.words or []):
            word = fix_text(w.word.strip())
            if not word:
                continue
            srt_lines.append(f"{idx}")
            srt_lines.append(f"{srt_timestamp(w.start)} --> {srt_timestamp(w.end)}")
            srt_lines.append(word)
            srt_lines.append("")
            words_data.append({"word": word, "start": w.start, "end": w.end})
            idx += 1

    stem = audio_path.stem
    srt_path = out_dir / f"{stem}.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    (out_dir / f"{stem}.words.json").write_text(
        json.dumps(words_data, indent=1), encoding="utf-8"
    )
    print(f"  wrote {srt_path.name} ({idx - 1} words)")
    return srt_path


def download_from_drive(drive, folder_id, dest: Path):
    """Download all MP3s from a Drive folder."""
    from googleapiclient.http import MediaIoBaseDownload
    import io

    resp = drive.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id,name)", pageSize=20).execute()
    for f in resp.get("files", []):
        if not f["name"].endswith(".mp3"):
            continue
        out = dest / f["name"]
        if out.exists():
            continue
        print(f"  downloading {f['name']} from Drive...")
        req = drive.files().get_media(fileId=f["id"])
        with open(out, "wb") as fh:
            dl = MediaIoBaseDownload(fh, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
        print(f"  saved {out.name}")


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("voiceover")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("transcripts")
    out.mkdir(parents=True, exist_ok=True)
    src.mkdir(parents=True, exist_ok=True)

    # If no local MP3s, try downloading from Drive voiceover folder
    if not list(src.glob("*.mp3")):
        print("No local MP3s, checking Drive...")
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            import json as _json

            creds = Credentials(
                None,
                refresh_token=os.environ.get("GDRIVE_REFRESH_TOKEN", ""),
                token_uri="https://oauth2.googleapis.com/token",
                client_id="950969484933-umf8vj3nbrte6f5bpo87i4bh464vhb1f.apps.googleusercontent.com",
                client_secret=os.environ.get("GDRIVE_CLIENT_SECRET", ""),
                scopes=["https://www.googleapis.com/auth/drive"],
            )
            drive = build("drive", "v3", credentials=creds)
            # Find video folder via video-config.json
            with open("video-config.json") as _f:
                slug = _json.load(_f).get("video_slug", "")
            resp = drive.files().list(
                q=f"'12hSLUK2pE20AMdXYAcCCeROSvozF-rMo' in parents "
                  f"and name='{slug}' and mimeType='application/vnd.google-apps.folder' "
                  f"and trashed=false",
                fields="files(id)", pageSize=2).execute()
            vf = resp.get("files", [])
            if vf:
                vo = drive.files().list(
                    q=f"'{vf[0]['id']}' in parents and name='voiceover' "
                      f"and mimeType='application/vnd.google-apps.folder' and trashed=false",
                    fields="files(id)", pageSize=2).execute()
                vof = vo.get("files", [])
                if vof:
                    download_from_drive(drive, vof[0]["id"], src)
        except Exception as e:
            print(f"  Drive download failed: {e}")

    from faster_whisper import WhisperModel

    print(f"Loading faster-whisper model: {MODEL_SIZE} ...")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

    mp3s = sorted(src.glob("*.mp3"))
    if not mp3s:
        print("No MP3s found.")
        return
    for mp3 in mp3s:
        transcribe_file(model, mp3, out)
    print(f"Done: {len(mp3s)} file(s) transcribed.")


if __name__ == "__main__":
    main()
