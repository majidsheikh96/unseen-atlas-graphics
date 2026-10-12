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


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("voiceover")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("transcripts")
    out.mkdir(parents=True, exist_ok=True)

    from faster_whisper import WhisperModel

    print(f"Loading faster-whisper model: {MODEL_SIZE} ...")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

    mp3s = sorted(src.glob("*.mp3"))
    if not mp3s:
        print("No MP3s found in voiceover/.")
        return
    for mp3 in mp3s:
        transcribe_file(model, mp3, out)
    print(f"Done: {len(mp3s)} file(s) transcribed.")


if __name__ == "__main__":
    main()
