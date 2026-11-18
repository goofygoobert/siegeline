# Art guide — Tales of the Brine (region 1 cast)

Rollicking but spooky pirate tale: lantern-lit coves, sea-fog, green moonlight. A little slime, ink and splintered
wood, never horror. The Gullwake Crew (pirates, players) against the Deep (sea-folklore monsters, enemies).
All characters are original toy-like figures built in code from rounded parts (`art/blender/kit.py`).
Nothing imitates a pirate film or game: no recognisable characters, costumes, flags or logos.
(The previous world, The Ashen Marches, is kept in git tag `ashen-marches-v1`.)

## Palette (sRGB hex)
| role | hex | used for |
|---|---|---|
| deep navy | `#1f3a5a` | crew coats, jumpers, trousers |
| sea-red | `#b0302a` | sashes, bandana, squeezebox, lapels |
| canvas | `#e8dcc0` | shirts, apron, bellows, breeches |
| brass / gold | `#d4a23a` | buttons, buckles, trim, t3 gilding, doubloons |
| tar-black | `#2a2420` | tricorns, boots, Anchorman's vest |
| lantern glow | `#ffb347` | lantern, muzzle flash, flare, music notes |
| cursed green-gold | `#c7ff6b` | t3 weapons, t3 rivets/notes (crew magic is green-GOLD, warmer than the monsters' green) |
| iron | `#4d4f54` | musket barrel, anchor, hatch bands |
| crew skin | `#c99a7a` | faces, bare arms, Rope Rat's bare feet |
| drowned green-grey | `#4a6a5e` | Drowner, monster skin |
| deep teal | `#1e4a4e` | Scuttler shell, fins, Kelpie, Inkspitter body |
| bone / shell | `#d8cfb5` | claws, barnacles, spines, teeth, whale bone |
| sickly green glow | `#7dff9a` | ALL monster eyes, cracks, ink-sac core, the boss's lure and tentacle barbs |
| ink-purple | `#3a1e4a` | ink sac, Inkspitter head, drips, boss throat |
| kelp | `#335729` | kelp hair, manes, beards |
| coral | `#db7361` | Barnacle Troll and Mother Fathom's crown (sparingly) |

## Shape language (crew vs Deep differ by SHAPE first, colour second)
- **Gullwake Crew (players, face right +X):** upright (0–6° lean), square boxy torsos, symmetric, big readable hats.
  Warm accents (sea-red, brass, lantern orange). Every unit has its own hat/head silhouette AND dominant colour
  so the portraits never look alike:

  | id | name | head | dominant colour | prop |
  |---|---|---|---|---|
  | ashguard | Hatchguard | red polka-dot bandana, brown beard | red + wood | hatch-door shield, short cutlass |
  | torchbow | Blackpowder | black tricorn, moustache | navy coat + black | long flintlock, powder horn |
  | cinder_runner | Rope Rat | spiky ginger hair | red/white stripes | two knives, navy neckerchief, bare feet |
  | bellringer | Shantyman | yellow sou'wester, big grey beard | yellow + navy | red squeezebox, music notes |
  | maulwright | Anchorman | bald, black handlebar moustache | skin + tar-black vest | ship's anchor |
  | lamplighter | Sawbones | white hair puffs, brass spectacles, red nose | canvas apron + brown | lantern + bottle of grog |
  | marshal | Capt. Rook Halloran | huge black tricorn, white plume, gold trim | long red coat | cutlass + flare pistol |

  Tiers: **t2** (level 5) bulk +6%, leather jerkin (shirt shows in the front gap), leather bracers, boot cuffs,
  red sash tails at the hip, a white feather in the hat (hatless heads get a red headband + feather).
  **t3** (level 10) adds gold jerkin trim, a doubloon necklace, gold bracer bands / hat trim / earring, and the weapon
  turns cursed green-gold and glows. Same proportions, so the unit still reads as itself.
- **The Deep (enemies, face left −X):** hunched 15–25° forward, thin lopsided limbs (limb width ~0.65×),
  finned, tentacled, barnacled, kelp-draped, asymmetric (one bigger arm). Wet green-grey/teal bodies with
  shell-white claws and spines, glowing sickly-green slit eyes and cracks, ink-purple accents.
  Scuttler is a six-legged crab (big claw on the camera side); Pufferghast is a spiny ball on stubby legs;
  the Kelpie rears upright on hind legs with a long horse skull and kelp mane.

## Proportions (world units; 1 u = 44 logical px)
- Standard figure ~1.9 u tall: big head (r 0.36), short legs (hip 0.62), chunky torso.
- Scales: Hatchguard 1.0 (bulk 1.32), Blackpowder 0.95, Rope Rat 0.95 (lean), Shantyman 1.0 (bulk 1.25),
  Anchorman 1.4, Sawbones 1.0, Captain 1.25 (+ big hat), Drowner 1.0, Scuttler ~0.8 u tall crab (scale 1.2),
  Inkspitter 1.0 (+ tall mantle), Pufferghast 1.1 (round), Barnacle Troll 1.6, Kelpie 1.5, Mother Fathom 2.6
  (+ lure, ~6 u to the bulb; tentacle reach ~4 u in front).

## Materials, light, outline, camera (unchanged from the previous world, so the game's scale still works)
- Toon shader: 3 constant bands (shadow 30%, mid 62%, lit 100%) × base colour, plus a faint rim.
  Glowing parts are emissive (no bloom): monster glow is green, crew glow is lantern orange / cursed green-gold.
- Key sun from upper-left-front, soft fill from the right; identical for the whole cast.
- Outline: inverted hull, 0.026 u, near-black `#030202`.
- Camera: orthographic, 10° elevation; characters turned 25° toward the camera (3/4 view) so the
  chest, shield face and both eyes read. Rendered at 96 px/u, packed at 72 px/u.
- Ground is world z = 0; the sprite anchor is the feet point (cell anchor fixed per render job → no jitter).

## Pipeline
- `art/blender/cast.py` — pure data: render jobs (cell size, ids), anim lists (frames, fps, hit frame), atlas groups.
- `art/blender/kit.py` — shared builders: humanoid / quad / crab rigs, crew hats (`tricorn`, `souwester`, `beanie`,
  `bandana`, `bald`, `hair`, `whitehair`), `crew_face` (nose, beard, moustache, spectacles), props (`cutlass`,
  `musket`, `pistol`, `anchor`, `bottle`, `driftclub`, `knife`, `lantern`, `claws`, hatch shield, accordion, coat),
  Deep parts (`kelp_hair`, `barnacles`, `dorsal_fin`, `rags`, `gills`, `face_tentacles`, `tentacle`).
- `art/blender/chars/_crew.py`, `_deep.py` — shared colour sets; one script per character (crew scripts make t1–t3).
- `tools/render_chars.sh units|field|boss|ui|one:ID,ID` — bundles kit + cast + chars, compile-checks, renders the
  whole job in ONE gpu5070 EEVEE job.
- `tools/pack_sprites.py [--sheets]` — cuts cells, downsizes, trims, dedupes, MaxRects-packs WebP (q82) + json per
  the contract. Writes `*.tmp` then swaps into place (the engine loads live). `--sheets` writes
  `art/out/review_<page>.png`.
- Gotcha: read a hand's `matrix_world` only after `bpy.context.view_layer.update()` (the kit does this).
  Weapon direction = arm angle + torso lean + grip (degrees from up, positive = forward). Muskets/pistols turn
  forward through the keyable grip (`gR`/`gL`) in the attack/special tables.

## Decisions (contract points settled here)
- **Ids unchanged:** internal ids stay (`ashguard` = Hatchguard, `cinder_matron` = Mother Fathom, …).
- **Pages:** `units` (base six), `units2` (`_t2`), `units3` (`_t3`). Any group that outgrows 2048² spills into
  `<group>2`; an id never spans two pages.
- **Boss ppu:** `boss.json` says `"ppu": 56` (draw at 44/ppu as usual).
- **Hit frames:** Blackpowder's muzzle flash, Shantyman's big squeeze + notes, Sawbones' raised bottle + lantern
  flare, the Scuttler's claw snapping shut and the Captain's flare all peak on the contract's hit frame (4).
- **Sweep timing (boss):** frames 0–6 = tentacle raised and cocked behind her, tip barbs and lure glowing brighter
  (the warning); frame 7 swing; the lash lands forward-down on frame 8.
- **UI:** portraits and icons are untrimmed 96×96, anchor at the centre, one `idle` frame. Long props (musket,
  anchor) are hidden in portraits so the face and hat read. Icons: `i_ember_rain` = Broadside (cannon firing
  cannonballs), `i_rally` = Sea Shanty (squeezebox, ship's bell, notes), `i_mark` = doubloon (anchor-stamped gold
  coin), `i_energy` = powder keg (lit fuse), stars and lock unchanged.

## Atlas sizes (written by tools/pack_sprites.py)
| file | size | ppu | bytes | ids |
|---|---|---|---|---|
| units.webp | 2044x2020 | 104 | 552 KB | ashguard, torchbow |
| units2.webp | 2048x1648 | 104 | 524 KB | cinder_runner, bellringer |
| units3.webp | 2048x2032 | 104 | 365 KB | maulwright |
| units4.webp | 2028x2024 | 104 | 481 KB | maulwright, lamplighter |
| unitsb.webp | 1716x2044 | 80 | 584 KB | ashguard_t2, torchbow_t2, cinder_runner_t2 |
| unitsb2.webp | 1928x968 | 80 | 211 KB | bellringer_t2 |
| unitsb3.webp | 1916x2012 | 80 | 370 KB | maulwright_t2 |
| unitsb4.webp | 1072x1996 | 80 | 274 KB | lamplighter_t2 |
| unitsc.webp | 1712x2048 | 80 | 609 KB | ashguard_t3, torchbow_t3, cinder_runner_t3 |
| unitsc2.webp | 1928x968 | 80 | 215 KB | bellringer_t3 |
| unitsc3.webp | 1656x1984 | 80 | 394 KB | maulwright_t3 |
| unitsc4.webp | 880x2040 | 80 | 276 KB | lamplighter_t3 |
| hero.webp | 1364x2012 | 80 | 394 KB | marshal |
| enemies.webp | 1328x2048 | 104 | 677 KB | husk, gnawer |
| enemies2.webp | 2000x2048 | 104 | 860 KB | spitter, bloater |
| enemies3.webp | 2000x2048 | 104 | 585 KB | brute |
| enemies4.webp | 1060x1992 | 104 | 264 KB | brute |
| enemies5.webp | 1952x2016 | 104 | 648 KB | husk_warden |
| enemies6.webp | 756x1716 | 104 | 160 KB | husk_warden |
| boss.webp | 1236x1964 | 64 | 202 KB | cinder_matron |
| boss2.webp | 1300x2024 | 64 | 203 KB | cinder_matron |
| boss3.webp | 1888x1948 | 64 | 285 KB | cinder_matron |
| boss4.webp | 1220x1684 | 64 | 213 KB | cinder_matron |
| boss5.webp | 2004x2044 | 64 | 325 KB | cinder_matron |
| boss6.webp | 1876x2012 | 64 | 258 KB | cinder_matron |
| ui.webp | 1940x972 | 72 | 70 KB | p_ashguard, p_torchbow, p_cinder_runner, p_bellringer, p_maulwright, p_lamplighter, p_marshal, i_ember_rain, i_rally, i_mark, i_star, i_star_empty, i_energy, i_lock |
