#!/bin/bash
# CI render script
# Transparent overlays -> WebM with alpha (CapCut). Opaque -> MP4.
set -e
export TMPDIR="${RUNNER_TEMP:-/tmp}/.hf-tmp"
mkdir -p "$TMPDIR" renders
R=compositions
WEBM="--format webm"

# RENDER_MODE=full (default, all 15) or quick (first 3 only, ~2 min for testing)
QUICK_COUNT=0
hf() {
  if [ "${RENDER_MODE:-full}" = "quick" ] && [ "$QUICK_COUNT" -ge 3 ]; then
    echo "  (quick mode: skipping)"
    return 0
  fi
  npx --yes hyperframes@0.8.149 render -q standard --quiet "$@"
  QUICK_COUNT=$((QUICK_COUNT + 1))
}

# Download binary assets (pushed as text via API, so fetch correct binaries from Drive)
mkdir -p assets/audio
curl -sL "https://drive.google.com/uc?export=download&id=1ZJl2uAhNB0rmxpbDHHvLWJwAIxrZhkA_" -o assets/audio/clean-whoosh.mp3
curl -sL "https://drive.google.com/uc?export=download&id=1fB2ZklD9qBftHg4nrIBuRlE02EF8ec86" -o assets/audio/mouse-click.mp3
curl -sL "https://drive.google.com/uc?export=download&id=1R3d5_9nUgsbjZwRlSUVvsiJFmhKN_G1A" -o assets/avatar.jpg
file assets/audio/clean-whoosh.mp3 | grep -q "MPEG" || { echo "FATAL: whoosh download corrupt"; exit 1; }

# Chapter openers x4
hf $WEBM -c $R/chapter-opener.html --variables '{"chapter_kicker":"CHAPTER 1","chapter_title":"The Most Alien Place on Earth"}' -o renders/chapter-1-opener.webm
hf $WEBM -c $R/chapter-opener.html --variables '{"chapter_kicker":"CHAPTER 2","chapter_title":"The Tree That Bleeds"}' -o renders/chapter-2-opener.webm
hf $WEBM -c $R/chapter-opener.html --variables '{"chapter_kicker":"CHAPTER 3","chapter_title":"The Upside-Down Forest"}' -o renders/chapter-3-opener.webm
hf $WEBM -c $R/chapter-opener.html --variables '{"chapter_kicker":"CHAPTER 4","chapter_title":"Why the World Barely Knows It"}' -o renders/chapter-4-opener.webm

# Location tags x6 (whoosh baked)
hf $WEBM -c $R/location-tag.html --variables '{"location_name":"Socotra, Yemen"}' -o renders/location-socotra-yemen.webm
hf $WEBM -c $R/location-tag.html --variables '{"location_name":"Indian Ocean"}' -o renders/location-indian-ocean.webm
hf $WEBM -c $R/location-tag.html --variables '{"location_name":"Horn of Africa"}' -o renders/location-horn-of-africa.webm
hf $WEBM -c $R/location-tag.html --variables '{"location_name":"Dragons Blood Tree"}' -o renders/location-dragons-blood-tree.webm
hf $WEBM -c $R/location-tag.html --variables '{"location_name":"Cucumber Tree"}' -o renders/location-cucumber-tree.webm
hf $WEBM -c $R/location-tag.html --variables '{"location_name":"Desert Rose"}' -o renders/location-desert-rose.webm

# Stat callouts x3
hf $WEBM -c $R/stat-callout.html --variables '{"stat_value":307,"stat_suffix":"","stat_label":"Endemic plant species","stat_caption":"Nearly a third of Socotras flora exists nowhere else on Earth","stat_max":400}' -o renders/stat-307-species.webm
hf $WEBM -c $R/stat-callout.html --variables '{"stat_value":18,"stat_suffix":"","stat_label":"Million years of isolation","stat_caption":"Longer than humanity has existed","stat_max":20}' -o renders/stat-18-million-years.webm
hf $WEBM -c $R/stat-callout.html --variables '{"stat_value":80000,"stat_suffix":"","stat_label":"Adult dragons blood trees counted","stat_caption":"Almost no young ones left","stat_max":100000}' -o renders/stat-80000-trees.webm

# Title card (opaque) — hero map is bespoke, rendered once manually
hf -c $R/title-card.html --variables '{"series_name":"IMPOSSIBLE PLACES","video_title":"The Island That Shouldnt Exist"}' -o renders/title-card.mp4

# Subscribe CTA (render once, reuse forever)
hf $WEBM -c $R/subscribe-cta.html -o renders/subscribe-cta.webm

echo "=== DONE ==="
ls -la renders/
