# Art guide — The Ashen Marches (region 1 cast)

Grim ember-dusk fantasy: a little gruesome (dark ichor, bone, ember cracks), never horror, never cute.
All characters are original toy-like figures built in code from rounded parts (`art/blender/kit.py`).

## Palette (sRGB hex)
| role | hex | used for |
|---|---|---|
| ember-red tabard | `#8c2a1e` | Warden tabards, capes, shield faces |
| deep red | `#5e1c15` | hoods, robe trim shadows |
| blackened steel | `#565a64` (plate) / `#3a3c44` (dark) | Warden helms, plate, blades |
| brass trim | `#d49a3a` | rims, bands, t3 gilding |
| lantern glow | `#ffb347` | lanterns, lamps, healer light |
| leather / wood | `#5a3b26` / `#6b4a2c` | belts, bows, hafts |
| ash-white robe | `#d9d3c7` | Lamplighter |
| Warden skin | `#c99a7a` | the few faces shown |
| Hollow skin | `#3a3838` (body) / `#4c4847` (limbs) | Hollow Host |
| bone | `#d8cfb5` | horns, claws, ribs, clubs |
| ember eyes/cracks | `#ff7a1a` | glowing eyes, cracks, throats, censer |
| dried blood | `#5a0f12` | claw tips, cleaver edge, robe hem |
| rust | `#7a4a2a` | Husk Warden armour scraps |

## Shape language (players vs enemies differ by SHAPE first, colour second)
- **Lantern Wardens (players, face right +X):** upright posture (0–6° lean), squared boxy parts with
  bevels, flat-topped helms, tower shields, symmetric silhouettes, warm accents (red tabard, brass, lantern
  orange). Tiers: **t2** (level 5) adds boxy steel pauldrons, a chest plate, greaves and a red helm crest,
  bulk +6%; **t3** (level 10) turns pauldrons/rims brass and the weapon glows ember. Same proportions, so
  the unit still reads as itself.
- **Hollow Host (enemies, face left −X):** hunched 15–25° forward, thin jagged limbs (limb width ~0.65×),
  horns/spikes/claws, asymmetric (one broken horn, one bigger arm), cold charcoal bodies with bone and
  glowing ember eyes/cracks, dried-blood accents. Eyes are slanted glowing slits, never round.

## Proportions (world units; 1 u = 44 logical px)
- Standard figure ~1.9 u tall: big head (r 0.36), short legs (hip 0.62), chunky torso.
- Scales: Ashguard 1.0 (bulk 1.3), Torchbow 0.95, Cinder Runner 0.95 (lean), Bellringer 1.0,
  Maulwright 1.4, Lamplighter 1.0, Marshal 1.25, Husk 1.0, Gnawer ~0.75 u tall quadruped, Spitter 1.0,
  Bloater 1.1 (round), Brute 1.6, Husk Warden 1.5, Cinder Matron 2.6.

## Materials, light, outline, camera
- Toon shader: 3 constant bands (shadow 30%, mid 62%, lit 100%) × base colour, plus a faint rim.
  Glowing parts are emissive (no bloom) — keep them bright orange/yellow so they read as light.
- Key sun from upper-left-front, soft fill from the right; identical for the whole cast.
- Outline: inverted hull, 0.026 u, near-black `#030202`.
- Camera: orthographic, 10° elevation; characters turned 25° toward the camera (3/4 view) so the
  chest, shield face and both eyes read. Rendered at 96 px/u, packed at 72 px/u.
- Ground is world z = 0; the sprite anchor is the feet point (cell anchor is fixed per render job,
  so it never jitters).

## Pipeline
- `art/blender/cast.py` — pure data: render jobs (cell size, ids), anim lists (frames, fps, hit frame),
  atlas groups. Shared by the Blender scripts and the packer.
- `art/blender/chars/*.py` — one script per character (with its t2/t3 tiers), `register(SPEC)`.
- `tools/render_chars.sh units|field|boss|ui` — bundles kit + cast + chars, compile-checks,
  renders the whole job in ONE gpu5070 EEVEE job (all characters on one grid), contact sheet.
- `tools/pack_sprites.py` — cuts cells, downsizes, trims, dedupes, packs WebP + json per the contract.

## Atlas sizes
(filled in by the latest pack — see bottom of this file)
