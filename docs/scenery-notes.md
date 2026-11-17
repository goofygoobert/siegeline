# Scenery notes (backgrounds, castles, fx, title, world map) — Tales of the Brine

World: docs/world-pirates.md. The previous Ashen Marches scenery is in git tag `ashen-marches-v1`; ids, sizes,
layer widths and json formats are unchanged, only the looks changed.

Sources: `art/blender/scenery.py` (painted-layer helpers, coastal props, 3D castle builders `gullwake`, `long_tom`,
`grotto`; bundled after kit.py), `art/blender/bg/` (`r1_lib.py` Saltwick Cove palettes/layer builders, `r1_bgs.py`,
`castles.py`, `fx.py`, `title.py`, `worldmap.py`, `map_lib.py`).
Build: `python3 tools/bundle_blend.py art/blender/bg/<x>.py art/build/<x>.py --lib art/blender/scenery.py [--lib ...]`,
render on the 5070 (`gpu5070 render art/build/<x>.py --frames 1-N --engine eevee --out art/out/scenery/<x>`), then
`.venv/bin/python tools/pack_scenery.py [castles fx bg title worldmap]`. Or all at once: `art/blender/bg/render_all.sh`.
Libs: r1_bgs needs `--lib art/blender/bg/r1_lib.py`; worldmap needs `--lib art/blender/bg/map_lib.py`; title needs
the libs listed in `art/build/title_libs.txt` (scenery, r1_lib, cast.py, chars/_crew.py, chars/_deep.py + the cast files).
pack_scenery.py writes every file atomically (temp file + os.replace; atlas image before its json).

## What is where
- **r1 Saltwick Cove** (sunset): sky = sunset gradient, low sun, lit clouds, gulls; far = sea to the horizon (y≈272
  logical), glitter path, distant islands, lighthouse island with beam, ship silhouettes; mid = headland cliffs, sea arch,
  sea stack, rocky shore with foam, beached wreck, nets on poles, rickety jetty + stilt shack, lantern posts;
  near = sand/shingle beach (lit crest at the ground line, plain dark sand below y=400), sea-creature ribs, anchor,
  broken mast, crates/barrels/rope, driftwood.
- **r1n** (boss night): same layout under a huge green moon, green fog, ghost lights (wisps) on a dark sea; lanterns stay
  warm. All four layers exist for both variants.
- **castles**: keep_0..2 = **The Gullwake** (galleon on the rocks rebuilt as a fort: gun ports, palisade, crow's nest,
  big brass lantern on the stern castle, Long Tom's carriage on the forecastle). keep_1 = holes, snapped topmast,
  cracked lantern, fire + smoke. keep_2 = hull broken in half, mast down, lantern fallen, fires.
  maw_0..2 = **The Drowned Grotto** (fish-skull sea cave of rock, bone, coral, barnacles, kelp; green throat and eyes;
  snout/underbite and tusks jut LEFT). maw_1 = glowing cracks, broken fangs/fin ray; maw_2 = collapsed, green ghost-fire.
- **ballista** sprite = **Long Tom**, the cannon BARREL only (brass, trunnions, cap-square), pointing right. The wooden
  carriage (cheeks + wheels) is part of keep_0/keep_1 so it stays level while the barrel rotates.

## Decisions / things the engine should know
- **Ground line** y = 400 logical (z=0 in the bg scripts, `BG_BOT` in scenery.py). Near layer below it is dark plain sand.
- **Backgrounds**: sky 1755x810 (opaque), far 2077, mid 2720, near 3900 (x810, alpha). Parallax 0.15 / 0.45 / 1.0.
- **Castles** (72 ppu, anchor = ground centre). Kit-style ortho camera at 10 deg elevation, castles yawed 15 deg toward
  the camera (keep turns its bow/right side in, grotto its left side). Gullwake ~7.3 u tall to the pennant (~5.9 u wide
  + bowsprit); Grotto ~6.4 u tall to the fin rays, ~6.3 u wide incl. the underbite.
- **Cannon pivot — UNCHANGED**: Long Tom's trunnion sits at the old ballista pivot. Offset from the keep anchor =
  **(+2.22, -4.23) world units** = (+160, -305) sprite px at 72 ppu = **(+98, -186) logical px** (x right, y up negative).
  In the model: keep-local (2.3, 0, 4.4) before the 15 deg yaw. The `ballista` sprite anchor = trunnion centre; the
  barrel points right at 0 deg and is a pure side view (not yawed). keep_2 has no carriage (hull broken): hide the
  weapon as before. castles render frame 8 is a check render of keep_0 with Long Tom mounted (not packed).
- **fx**: anchor = centre of the 4x4 u render cell = projectile centre; `fire_patch` anchor = its ground contact;
  `blast` and `flare` centred. Flipbooks use anim `idle` (fire_patch loop 10 fps, blast 14 fps once, flare 14 fps once).
  arrow = musket ball with spark trail, bolt = flaming cannonball (both point RIGHT, trails to the left);
  spit = glowing ink glob, fireball = big ink bomb (enemy shots travelling LEFT, trails to the right);
  ember_stone = Broadside cannonball falling DOWN (fire/smoke trail up); fire_patch = burning tar (6-frame loop);
  blast = cannon/tar explosion with wooden splinters (8); flare = flare-pistol burst ring (6).
- **title.webp** 1920x1080: Gullwake + crew + Captain Halloran left, the Deep (Drowners, Scuttlers, Barnacle Troll,
  Inkspitter, Kelpie, tentacles) up the beach right, sunset sky with the green moon rising. Calm sky centre-left for
  the logo; nothing important in the outer 8%. Uses the real cast models from art/blender/chars.
- **worldmap**: sea chart (parchment border + neatline, compass rose, rhumb lines, depth bands, raised islands),
  six regions joined by a dotted red sailing route. Marker positions in worldmap.json are computed from the same
  camera maths as the render (map_lib.project); all markers have x 0.17–0.85, y 0.32–0.65.

## File sizes
<!-- sizes -->
| file | size |
|---|---|
| castles.webp | 210.9 KB |
| castles.json | 0.7 KB |
| fx.webp | 199.1 KB |
| fx.json | 1.2 KB |
| title.webp | 134.5 KB |
| worldmap.webp | 76.5 KB |
| worldmap.json | 0.3 KB |
| bg/r1_far.webp | 33.7 KB |
| bg/r1_mid.webp | 72.0 KB |
| bg/r1_near.webp | 65.8 KB |
| bg/r1_sky.webp | 21.0 KB |
| bg/r1n_far.webp | 31.5 KB |
| bg/r1n_mid.webp | 71.4 KB |
| bg/r1n_near.webp | 63.3 KB |
| bg/r1n_sky.webp | 20.9 KB |
| bg/manifest.json | 0.4 KB |
| **total** | **1003.2 KB** |
<!-- /sizes -->
