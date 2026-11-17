# HANDOFF — current state
Updated 2026-11-17 07:20. Region 1 done and published.

## Where things are
- **Live:** https://goofygoobert.github.io/siegeline/ · worlds page: https://goofygoobert.github.io/siegeline/worlds/
- CI (`.github/workflows/pages.yml`) publishes only when data checks, sim tests, build and the full play-through pass.
- Region 1 (Cinderfold Vale) complete: title, world map (6 regions, r1 open, others locked), stage select, 5 stages + Cinder Matron boss, 6 units with level 5/10 looks, hero, ballista, Ember Rain and Rally Bell, Armoury, tutorial, results with stars, settings, saves (auto, backup slot, migration, export/import), music + 33 sfx, offline install.
- Two fresh reviews done (docs/review/review-1.md, review-2.md). Their findings are fixed except the known issues below.

## How to check things
- `npm test` · `npm run balance` · `node tools/tune.mjs [stageId]`
- `npm run build && tools/serve.sh`, then `node tools/playthrough.mjs`, `node tools/shots.mjs` (VW/VH env), `node tools/perf.mjs <url> <label> [quick]`, `node tools/record.mjs` (frames → encode on the 5070 with `gpu5070 encode`).
- Art: `tools/render_chars.sh <id>` + `tools/pack_sprites.py`; scenery: `art/blender/bg/render_all.sh` + `tools/pack_scenery.py`; audio: `tools/audio/*.py`.

## Known issues
- Torchbow and Bellringer portraits look alike (names on cards help; re-render portraits with more distinct headgear).
- Frame rate not measured on a real iPhone (headless software rendering only).
- Audio checked by analysis only, never heard by a person.
- Boss fight ~3–3.5 min; humans who use the winded window should be faster.

## Next
See docs/next-regions.md (regions 2–4 plan and what's needed from the owner).
