# Asset contract (engine ⇄ art ⇄ audio)

The engine loads only what this file describes. Ids are fixed; names shown to players live in `data/`.

## Units of measure
- The game's logical screen is 540 px tall (width follows the phone's aspect, ~1170).
- **1 world unit (Blender) = 44 logical px.** A standard soldier (~1.9 u) is ~84 logical px tall.
- Sprites are packed at **72 px per world unit** (`ppu: 72` in the atlas json); the engine draws them at
  scale `44 / ppu`. On a 3x iPhone that is ~1.3 device px per sprite px, so it stays sharp.
- Player-side art faces **right (+X)**. Enemy art faces **left**. The engine never mirrors sprites.

## Sprite atlases — `public/assets/<group>.webp` + `public/assets/<group>.json`
```json
{ "image": "units.webp", "w": 2048, "h": 2048, "ppu": 72,
  "sprites": {
    "ashguard": {
      "anims": {
        "idle":   { "fps": 8,  "loop": true,  "frames": [[x, y, w, h, ax, ay], ...] },
        "walk":   { "fps": 10, "loop": true,  "frames": [...] },
        "attack": { "fps": 12, "loop": false, "frames": [...], "hit": 4 },
        "hit":    { "fps": 12, "loop": false, "frames": [...] },
        "die":    { "fps": 10, "loop": false, "frames": [...] }
      } } } }
```
- `[x, y, w, h]` is the trimmed frame rectangle in the atlas; `[ax, ay]` is the **feet/ground anchor**
  (character origin) measured from the frame's top-left, in sprite px. Anchor must not jitter between frames.
- `hit` = index of the frame where the blow lands / the shot leaves (engine applies damage then).
- Extra anims allowed per sprite (boss: `sweep`, `summon`, `spit`; those also carry `hit`).
- WebP with alpha, quality ~82. Keep each atlas ≤ 2048×2048 (iOS memory) — split into `units2` etc. if needed.

### Groups and sprite ids (region 1)
- `units`: `ashguard`, `torchbow`, `cinder_runner`, `bellringer`, `maulwright`, `lamplighter`, plus
  upgrade looks `<id>_t2` (level 5) and `<id>_t3` (level 10) for each of the six.
- `hero`: `marshal` (anims: idle, walk, attack, hit, die, plus `special` = raised-lantern flare, `hit` frame marks the flash).
- `enemies`: `husk`, `gnawer`, `spitter`, `bloater`, `brute`, `husk_warden` (mini-boss).
- `boss`: `cinder_matron` (idle, walk, sweep, summon, spit, hit, die).
- `castles`: `keep_0`, `keep_1`, `keep_2` (intact, damaged, ruined), `maw_0`, `maw_1`, `maw_2`,
  `ballista` (the keep's weapon arm, drawn rotated by the engine; anchor = pivot point; points right at 0°).
  Single-frame sprites use one anim `idle` with one frame.
- `fx`: `arrow`, `bolt` (burning ballista bolt, points right), `spit` (ember glob), `fireball`,
  `ember_stone` (ember rain), `fire_patch` (looping, 6 frames), `blast` (explosion, 8 frames),
  `flare` (hero flash ring, 6 frames).
- `ui`: portraits `p_<unitId>` (square, head-and-shoulders, ~96×96 px, for each of the six units and
  `p_marshal`), icons `i_ember_rain`, `i_rally`, `i_mark` (currency coin), `i_star`, `i_star_empty`,
  `i_energy`, `i_lock`.

## Backgrounds — `public/assets/bg/<regionId>_<layer>.webp`
- Region 1 id: `r1`. Layers: `sky` (static), `far` (parallax 0.15), `mid` (0.45), `near` (1.0, the ground strip
  units walk on, ground line at **y = 400 logical px from the top** (the phone HUD covers the bottom ~130 px; keep the earth below the line dark and plain)).
- Field width is **2600 logical px**. A layer with parallax `f` must be `1170 + (2600 - 1170) * f` logical px wide;
  render at **1.5 px per logical px** (height 810 px). `sky` is 1170×540 logical.
- Variant `r1n_*` (night / boss stage): at least `sky` and `far`; may reuse `mid`/`near`.
- `public/assets/bg/manifest.json`: `{ "r1": {"sky": "...", "far": {"file": "...", "parallax": 0.15}, ...}, "r1n": {...} }`.

## Screens art
- `public/assets/title.webp` 1920×1080 key art (hero and Wardens before the keep, Hollows coming over the ash).
  Keep the centre-left calm for the logo; nothing important in the outer 8% (phone notches).
- `public/assets/worldmap.webp` 2048×1024 painted map of six regions, plus `worldmap.json`:
  `{ "regions": [{ "id": "r1", "x": 0.18, "y": 0.62 }, ...] }` (normalised positions of each region's marker).
  Region names: r1 Cinderfold Vale, r2 The Bell Marshes, r3 Gilded Causeway, r4 Hollowdeep Mines,
  r5 The Ember Wastes, r6 The Cinder Maw.

## Audio — `public/assets/audio/*.m4a` (AAC, plays on iPhone and desktop) + `audio/manifest.json`
```json
{ "sfx": { "ui_tap": {"file": "ui_tap.m4a", "vol": 0.6}, ... },
  "music": { "battle": {"file": "battle.m4a", "vol": 0.5, "loopStart": 0.0, "loopEnd": 64.0}, ... } }
```
- SFX ids: `ui_tap`, `ui_back`, `ui_upgrade`, `ui_locked`, `unit_send`, `energy_full`, `hit_blade`,
  `hit_blunt`, `hit_claw`, `arrow_fire`, `arrow_hit`, `bolt_fire`, `bolt_hit`, `ballista_reload`, `spit`,
  `bloater_burst`, `warden_die`, `hollow_die`, `castle_hit`, `castle_crumble`, `coin`, `star`,
  `ember_rain`, `rally`, `bell`, `heal`, `hero_call`, `hero_flare`, `boss_roar`, `boss_warn`,
  `boss_slam`, `win`, `lose`.
- Music ids: `menu`, `map`, `battle`, `boss` (looping), `victory`, `defeat` (short stings, no loop).
