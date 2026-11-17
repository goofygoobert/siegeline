# Scenery status (environment artist)

Complete, quality pass done (ids/formats per docs/asset-contract.md):
- [x] Backgrounds r1 + r1n (sky/far/mid/near, all four for both) + `bg/manifest.json` — ground line y=400 logical
- [x] castles atlas: keep_0..2, maw_0..2, ballista (`castles.webp/json`) — 10 deg elevation, 15 deg yaw like the cast
- [x] fx atlas: arrow, bolt, spit, fireball, ember_stone, fire_patch(6), blast(8), flare(6) (`fx.webp/json`)
- [x] title.webp 1920x1080 (real cast models from art/blender/chars)
- [x] worldmap.webp 2048x1024 + worldmap.json

Engine notes (ballista pivot offset, fx anchors/directions, sizes): docs/scenery-notes.md.
Rebuild everything: `art/blender/bg/render_all.sh` (renders on gpu5070, then tools/pack_scenery.py).
