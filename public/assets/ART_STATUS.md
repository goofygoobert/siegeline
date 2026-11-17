# Character art status — Tales of the Brine (pirates vs. the Deep)

Pass 2 (pirate re-theme, quality pass done) — every id from docs/asset-contract.md is packed and usable. Same ids, anims, hit frames
and json format as before; only the looks changed (see docs/world-pirates.md, docs/art-guide.md).

| group | files | ids (display name) |
|---|---|---|
| units | units / units2 / units3 | ashguard (Hatchguard), torchbow (Blackpowder), cinder_runner (Rope Rat), bellringer (Shantyman), maulwright (Anchorman), lamplighter (Sawbones) + `_t2`, `_t3` |
| hero | hero.webp/json | marshal (Captain Rook Halloran): idle, walk, attack, hit, die, special (flare pistol, flash on frame 4) |
| enemies | enemies | husk (Drowner), gnawer (Scuttler), spitter (Inkspitter), bloater (Pufferghast), brute (Barnacle Troll), husk_warden (The Kelpie) |
| boss | boss.webp/json | cinder_matron (Mother Fathom): idle, walk, sweep, summon, spit, hit, die |
| ui | ui.webp/json | p_* portraits (96×96), i_ember_rain (Broadside cannon), i_rally (Sea Shanty), i_mark (doubloon), i_star, i_star_empty, i_energy (powder keg), i_lock |

Notes for the engine
- Pages unchanged: `units.json` (base six), `units2.json` (`_t2`), `units3.json` (`_t3`). Repacks are atomic.
- `boss.json` carries its own `ppu` (currently below 72: she does not fit one 2048² page at 72); draw at 44/ppu.
- Frames that are pixel-identical are stored once. UI sprites: one `idle` frame, anchor = centre.

Atlases: units 1664×2048, units2 2036×2040, units3 2044×2040, hero 888×2048, enemies 2048×2048 (full page),
boss 2048×2040 at ppu 56, ui 1372×100. No frame touches a cell edge (no clipped limbs/props).

Quality pass fixes: boss back to ppu 56 (lure/crown trimmed, sweep hold frames 4–6 identical and deduped),
tentacle curls up in front at rest (no longer dips below the ground), Anchorman's anchor held forward and kept above
ground on the slam, Captain falls forward (plume no longer pokes below ground), gold-braided captain's tricorn,
Sawbones' bottle is dark glass (no longer reads as a torch), smaller spectacles, t3 musket brass + cursed gem
instead of a fully glowing barrel, lighter Broadside cannon icon, bulbous Inkspitter mantle.

Known issues: the Scuttler's die is a sink-and-curl rather than a flip; portraits of the Captain crop the tip of
the plume; enemies page is full (a new enemy would spill into `enemies2.json`).
