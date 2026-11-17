# Character art status

Pass 2 (05:04) — all ids from docs/asset-contract.md are packed and usable. Same ids/json format as pass 1.
Pass 2 changes: props fixed into the hands for enemies (brute club, warden cleaver, husk claws), t2 looks
stronger (red half-cape, steel skullcap/crest), lighter enemy and steel tones for phone readability, boss bone
mask + wide spiked mantle + torn skirt, no frame clips at cell edges, bigger gnawer, portraits hide poles.

Pages are now stable: units.json (base six), units2.json (all `_t2`), units3.json (all `_t3`),
hero.json, enemies.json, boss.json (ppu 56 — see docs/art-guide.md), ui.json. Repacks are atomic
(written to .tmp, then swapped in).

| group | files | ids |
|---|---|---|
| units | units / units2 / units3 | ashguard, torchbow, cinder_runner, bellringer, maulwright, lamplighter + `_t2`, `_t3` |
| hero | hero.webp/json | marshal (idle, walk, attack, hit, die, special) |
| enemies | enemies | husk, gnawer, spitter, bloater, brute, husk_warden |
| boss | boss.webp/json | cinder_matron (idle, walk, sweep, summon, spit, hit, die) |
| ui | ui.webp/json | p_ashguard … p_lamplighter, p_marshal (96×96), i_ember_rain, i_rally, i_mark, i_star, i_star_empty, i_energy, i_lock (96×96) |

Notes for the engine
- Pages: `units.json` (base six), `units2.json` (`_t2`), `units3.json` (`_t3`) — pinned, stable.
  Each page is a complete atlas json per the contract; one sprite id lives in exactly one page.
  `enemies.webp` is a full 2048² page: if it ever overflows, `enemies2.json` appears (merge `sprites`).
- `boss.json` has `"ppu": 56` (does not fit one 2048² page at 72); draw at 44/ppu as the contract says.
- Frames that are pixel-identical are stored once (the same rect appears more than once in `frames`).
- UI sprites: one anim `idle` with one frame, anchor = centre of the 96×96 frame.
