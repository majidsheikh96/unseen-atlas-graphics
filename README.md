# Unseen Atlas — Motion Graphics

HyperFrames motion-graphics kit for the Unseen Atlas YouTube channel.

## How it works

1. Edit any HTML file in `compositions/` (or push changes here).
2. GitHub Actions renders all 16 clips automatically.
3. Rendered files upload straight to the Drive **09 - Motion Graphics** folder.

No local rendering needed.

## Compositions

| File | What it is |
|---|---|
| `chapter-opener.html` | Chapter title card (gold kicker + headline, transparent) |
| `location-tag.html` | Location stamp, lower-left (transparent, whoosh baked) |
| `stat-callout.html` | Count-up stat + gold track (transparent) |
| `hero-map.html` | Animated Socotra map (opaque) |
| `title-card.html` | Video title card (opaque) |
| `subscribe-cta.html` | Evergreen subscribe overlay (transparent — render once) |
| `end-card.html` | End screen (in redesign) |

## Manual render

Push to `main`, or trigger **Actions → Render motion graphics → Run workflow**.
Note: edits to `.github/workflows/` do NOT auto-trigger — use **Run workflow**.

## Rules for future videos (do not break)

1. **Binary files (MP3/JPG/PNG) must NEVER be pushed via the GitHub API** — the
   integration saves them as base64 text, corrupting them. Instead: upload the
   binary to the Drive assets folder, make it public ("Anyone with the link"),
   and add a `curl` download line at the top of `render-ci.sh` with a
   `file ... | grep` integrity check.
2. **All render logic lives in `render-ci.sh`** — the workflow file
   (`.github/workflows/render.yml`) is static and cannot be edited via API
   (GitHub App restriction). Never put video-specific logic in the workflow.
3. **Node version**: HyperFrames requires Node ≥ 22. If HyperFrames bumps its
   requirement, update `node-version` in `render.yml` (manual edit via web UI).
4. **FFmpeg** is installed in the workflow — do not remove that step.
5. **Hero map** is bespoke per video — render once manually, not in CI.
