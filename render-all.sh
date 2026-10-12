#!/bin/bash
# Render all Unseen Atlas video #1 motion graphics (updated 2026-10-12)
# Transparent overlays -> WebM with alpha (for CapCut). Opaque -> MP4.
cd ~/workspace/hyperframes/unseen-atlas-video-01-graphics
export TMPDIR=~/workspace/.hf-tmp
HF="npx --yes hyperframes@0.8.149 render -q standard --quiet"
R=compositions
WEBM="--format webm"

# Chapter openers x4 (transparent overlay)
$HF $WEBM -c $R/chapter-opener.html --variables '{"chapter_kicker":"CHAPTER 1","chapter_title":"The Most Alien Place on Earth"}' -o renders/chapter-1-opener.webm
$HF $WEBM -c $R/chapter-opener.html --variables '{"chapter_kicker":"CHAPTER 2","chapter_title":"The Tree That Bleeds"}' -o renders/chapter-2-opener.webm
$HF $WEBM -c $R/chapter-opener.html --variables '{"chapter_kicker":"CHAPTER 3","chapter_title":"The Upside-Down Forest"}' -o renders/chapter-3-opener.webm
$HF $WEBM -c $R/chapter-opener.html --variables '{"chapter_kicker":"CHAPTER 4","chapter_title":"Why the World Barely Knows It"}' -o renders/chapter-4-opener.webm

# Location tags x6 (transparent overlay, whoosh baked)
$HF $WEBM -c $R/location-tag.html --variables '{"location_name":"Socotra, Yemen"}' -o renders/location-socotra-yemen.webm
$HF $WEBM -c $R/location-tag.html --variables '{"location_name":"Indian Ocean"}' -o renders/location-indian-ocean.webm
$HF $WEBM -c $R/location-tag.html --variables '{"location_name":"Horn of Africa"}' -o renders/location-horn-of-africa.webm
$HF $WEBM -c $R/location-tag.html --variables '{"location_name":"Dragon'"'"'s Blood Tree"}' -o renders/location-dragons-blood-tree.webm
$HF $WEBM -c $R/location-tag.html --variables '{"location_name":"Cucumber Tree"}' -o renders/location-cucumber-tree.webm
$HF $WEBM -c $R/location-tag.html --variables '{"location_name":"Desert Rose"}' -o renders/location-desert-rose.webm

# Stat callouts x3 (transparent overlay)
$HF $WEBM -c $R/stat-callout.html --variables '{"stat_value":307,"stat_suffix":"","stat_label":"Endemic plant species","stat_caption":"Nearly a third of Socotra\u2019s flora exists nowhere else on Earth","stat_max":400}' -o renders/stat-307-species.webm
$HF $WEBM -c $R/stat-callout.html --variables '{"stat_value":18,"stat_suffix":"","stat_label":"Million years of isolation","stat_caption":"Longer than humanity has existed","stat_max":20}' -o renders/stat-18-million-years.webm
$HF $WEBM -c $R/stat-callout.html --variables '{"stat_value":80000,"stat_suffix":"","stat_label":"Adult dragon\u2019s blood trees counted","stat_caption":"Almost no young ones left","stat_max":100000}' -o renders/stat-80000-trees.webm

# Title card (opaque) + hero map (opaque)
$HF -c $R/title-card.html --variables '{"series_name":"IMPOSSIBLE PLACES","video_title":"The Island That Shouldn'"'"'t Exist"}' -o renders/title-card.mp4
$HF -c $R/hero-map.html -o renders/hero-map.mp4

# Subscribe CTA (transparent overlay — render ONCE, reuse in every video forever)
$HF $WEBM -c $R/subscribe-cta.html -o renders/subscribe-cta.webm

echo "=== DONE ==="
ls -la renders/ | wc -l
