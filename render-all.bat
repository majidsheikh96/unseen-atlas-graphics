@echo off
REM ============================================================
REM  Unseen Atlas — motion graphics renderer (Windows)
REM
REM  SETUP (one time):
REM  1. Install Node.js LTS from https://nodejs.org (accept defaults)
REM  2. Double-click this file — it renders everything automatically.
REM     No paths to set: it runs from its own folder.
REM
REM  OUTPUT: renders\ folder inside the project (auto-syncs to
REM  Drive). Transparent overlays render as WebM with alpha for
REM  CapCut; title card + hero map render as MP4.
REM ============================================================

REM run from this file's own folder = the project folder (Drive synced)
cd /d "%~dp0"
if not exist "renders" mkdir renders

set HF=npx --yes hyperframes@0.8.149 render -q standard --quiet

echo === Chapter openers (4) ===
%HF% --format webm -c compositions\chapter-opener.html --variables "{\"chapter_kicker\":\"CHAPTER 1\",\"chapter_title\":\"The Most Alien Place on Earth\"}" -o renders\chapter-1-opener.webm
%HF% --format webm -c compositions\chapter-opener.html --variables "{\"chapter_kicker\":\"CHAPTER 2\",\"chapter_title\":\"The Tree That Bleeds\"}" -o renders\chapter-2-opener.webm
%HF% --format webm -c compositions\chapter-opener.html --variables "{\"chapter_kicker\":\"CHAPTER 3\",\"chapter_title\":\"The Upside-Down Forest\"}" -o renders\chapter-3-opener.webm
%HF% --format webm -c compositions\chapter-opener.html --variables "{\"chapter_kicker\":\"CHAPTER 4\",\"chapter_title\":\"Why the World Barely Knows It\"}" -o renders\chapter-4-opener.webm

echo === Location tags (6) ===
%HF% --format webm -c compositions\location-tag.html --variables "{\"location_name\":\"Socotra, Yemen\"}" -o renders\location-socotra-yemen.webm
%HF% --format webm -c compositions\location-tag.html --variables "{\"location_name\":\"Indian Ocean\"}" -o renders\location-indian-ocean.webm
%HF% --format webm -c compositions\location-tag.html --variables "{\"location_name\":\"Horn of Africa\"}" -o renders\location-horn-of-africa.webm
%HF% --format webm -c compositions\location-tag.html --variables "{\"location_name\":\"Dragon's Blood Tree\"}" -o renders\location-dragons-blood-tree.webm
%HF% --format webm -c compositions\location-tag.html --variables "{\"location_name\":\"Cucumber Tree\"}" -o renders\location-cucumber-tree.webm
%HF% --format webm -c compositions\location-tag.html --variables "{\"location_name\":\"Desert Rose\"}" -o renders\location-desert-rose.webm

echo === Stat callouts (3) ===
%HF% --format webm -c compositions\stat-callout.html --variables "{\"stat_value\":307,\"stat_suffix\":\"\",\"stat_label\":\"Endemic plant species\",\"stat_caption\":\"Nearly a third of Socotra's flora exists nowhere else on Earth\",\"stat_max\":400}" -o renders\stat-307-species.webm
%HF% --format webm -c compositions\stat-callout.html --variables "{\"stat_value\":18,\"stat_suffix\":\"\",\"stat_label\":\"Million years of isolation\",\"stat_caption\":\"Longer than humanity has existed\",\"stat_max\":20}" -o renders\stat-18-million-years.webm
%HF% --format webm -c compositions\stat-callout.html --variables "{\"stat_value\":80000,\"stat_suffix\":\"\",\"stat_label\":\"Adult dragon's blood trees counted\",\"stat_caption\":\"Almost no young ones left\",\"stat_max\":100000}" -o renders\stat-80000-trees.webm

echo === Title card + hero map ===
%HF% -c compositions\title-card.html --variables "{\"series_name\":\"IMPOSSIBLE PLACES\",\"video_title\":\"The Island That Shouldn't Exist\"}" -o renders\title-card.mp4
%HF% -c compositions\hero-map.html -o renders\hero-map.mp4

echo === Subscribe CTA (render once, reuse forever) ===
%HF% --format webm -c compositions\subscribe-cta.html -o renders\subscribe-cta.webm

echo.
echo === DONE — check the renders folder ===
pause
