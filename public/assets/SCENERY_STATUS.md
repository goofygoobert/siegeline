# Scenery status (environment artist) — Tales of the Brine re-theme

Complete (pass 1 + polish). Ids/formats/sizes unchanged (docs/asset-contract.md). Old art: git tag `ashen-marches-v1`.
- [x] Backgrounds r1 Saltwick Cove (sunset) + r1n (green moon, green fog, ghost lights) — all four layers each,
      ground line y=400 logical, plain dark sand below it. `bg/manifest.json` unchanged in format.
- [x] castles atlas: keep_0..2 = The Gullwake (wrecked galleon fort), maw_0..2 = The Drowned Grotto (fish-skull sea cave),
      ballista = Long Tom barrel. **Pivot offset unchanged: (+98, -186) logical from the keep anchor**; keep_2 has no weapon.
- [x] fx atlas: musket ball, flaming cannonball, ink glob, ink bomb, falling cannonball, burning tar (6), explosion with
      splinters (8), flare-pistol burst (6) — same ids, anchors and directions as before
- [x] title.webp 1920x1080 (real cast models)
- [x] worldmap.webp 2048x1024 + worldmap.json (sea chart; markers x 0.17-0.85, y 0.32-0.65)

Engine notes (pivot, fx anchors/directions, sizes): docs/scenery-notes.md.
Rebuild everything: `art/blender/bg/render_all.sh` (renders on gpu5070, then tools/pack_scenery.py, atomic writes).
