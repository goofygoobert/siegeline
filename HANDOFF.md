# HANDOFF — current state
Updated 2026-11-17 05:30.

## Where things are
- **Live:** https://goofygoobert.github.io/siegeline/ (published by CI only when data checks, sim tests, build and the full play-through pass).
- Region 1 (Cinderfold Vale) is complete and playable: title, world map (6 regions, r1 open), stage select, 5 stages + boss, 6 units (+ level 5/10 looks), hero, ballista, 2 powers, Armoury upgrades, tutorial, results with stars, settings, saves with export/import, music + sfx, offline install.
- All art and audio are delivered by the three helper agents (finished). Scripts to rebuild: `tools/render_chars.sh` + `tools/pack_sprites.py` (characters), `art/blender/bg/render_all.sh` + `tools/pack_scenery.py` (scenery), `tools/audio/*.py` (sound).

## How to check things
- `npm test` — data schema + sim tests. `npm run balance` — balance grid. `node tools/tune.mjs` — re-tune stage power.
- `npm run build && tools/serve.sh` then `node tools/playthrough.mjs` (full scripted run + save tests), `node tools/shots.mjs`, `node tools/perf.mjs`.

## Next steps (in order)
1. Fresh reviewer pass on the published build, fix findings, second reviewer confirms.
2. Final balance run → docs/balance.md. 3. Morning report.

## Known issues
- Frame rate not measured on a real phone (headless software rendering only; see docs/performance.md).
- Audio not yet heard by a person (analysed only).
