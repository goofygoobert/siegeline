# Scenery notes (backgrounds, castles, fx, title, world map)

Sources: `art/blender/scenery.py` (painted-layer + castle helpers, bundled after kit.py), `art/blender/bg/`
(`r1_lib.py` palettes/layer builders, `r1_bgs.py`, `castles.py`, `fx.py`, `title.py`, `worldmap.py`, `map_lib.py`).
Build: `python3 tools/bundle_blend.py art/blender/bg/<x>.py art/build/<x>.py --lib art/blender/scenery.py [--lib ...]`,
render on the 5070 (`gpu5070 render art/build/<x>.py --frames 1-N --engine eevee --out art/out/scenery/<x>`), then
`.venv/bin/python tools/pack_scenery.py [castles fx bg title worldmap]`.
Libs: r1_bgs needs `--lib art/blender/bg/r1_lib.py`; worldmap needs `--lib art/blender/bg/map_lib.py`; title needs
the libs listed in `art/build/title_libs.txt` (r1_lib + the real cast files from art/blender/chars).

## Decisions / things the engine should know
- **Ground line** follows the updated contract: y = 400 logical (z=0 in the bg scripts, `BG_BOT` in scenery.py).
  The near layer's earth below the line is dark and calm (unit cards sit over it).
- **Backgrounds**: sky 1755x810 (opaque), far 2077, mid 2720, near 3900 (x810, alpha). r1n has all four layers.
- **Castles** (72 ppu, anchor = ground centre). Rendered like the cast: kit-style ortho camera at 10 deg elevation,
  castles yawed 15 deg toward the camera (keep turns its right side in, maw its left side).
  Keep ~6.9 u tall, Maw ~6.5 u tall (incl. spikes), ~5.8 u wide. Smoke on damaged states raises the trimmed top.
- **Ballista pivot on keep_0/keep_1**: offset from the keep anchor = **(+2.22, -4.23) world units**
  = (+160, -305) sprite px at 72 ppu = **(+98, -186) logical px** (x right, y up is negative). keep_2 has no ballista
  (platform collapsed): hide the arm. The ballista sprite is not yawed (pure side view) so it reads when rotated.
- **fx**: anchor = centre of the 4x4 u render cell, i.e. projectile centre; for `fire_patch` the anchor is its
  ground contact (flames rise above it); `blast` and `flare` are centred. Flipbooks are stored as anim `idle`
  (fire_patch loop 10 fps, blast 14 fps once, flare 14 fps once). Directions: `arrow`, `bolt` point right;
  `spit` and `fireball` are enemy shots travelling LEFT (trails to the right); `ember_stone` falls DOWN (trail up).
- **worldmap.json** marker positions are computed from the same camera maths as the render (map_lib.project).

## File sizes
<!-- sizes -->
| file | size |
|---|---|
| castles.webp | 141.6 KB |
| castles.json | 0.7 KB |
| fx.webp | 174.8 KB |
| fx.json | 1.2 KB |
| title.webp | 101.3 KB |
| worldmap.webp | 61.6 KB |
| worldmap.json | 0.3 KB |
| bg/r1_far.webp | 30.1 KB |
| bg/r1_mid.webp | 59.7 KB |
| bg/r1_near.webp | 41.7 KB |
| bg/r1_sky.webp | 22.2 KB |
| bg/r1n_far.webp | 24.8 KB |
| bg/r1n_mid.webp | 54.8 KB |
| bg/r1n_near.webp | 38.5 KB |
| bg/r1n_sky.webp | 23.2 KB |
| bg/manifest.json | 0.4 KB |
| **total** | **776.9 KB** |
<!-- /sizes -->
