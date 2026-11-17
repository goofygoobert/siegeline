# HANDOFF — current state
Updated 2026-11-17 (redesign phase 2 stop). World: Tales of the Brine (pirates vs sea-folklore monsters).

## Where things are
- **Live (unchanged look):** https://goofygoobert.github.io/siegeline/ — built from `main`.
- **Design preview:** https://goofygoobert.github.io/siegeline/preview/ — built from branch `redesign` by the same workflow, added only if its own tests and play-through pass. Own save slot (starts as a copy of the live save), no offline install. Re-publish after pushing `redesign`: `gh workflow run test-and-publish --ref main`.
- **Phase 2 slice is done and waiting for the owner's reply. Do not start phase 3 without it.**
- Read: `docs/design/critique.md`, `docs/design/art-direction.md`, `docs/review/review-3.md`, the "Redesign slice" section of `docs/decisions.md`.

## What the slice changed (branch `redesign`)
- New figure kit `art/blender/kit2.py`; Hatchguard (3 looks) and Drowner in `art/blender/chars/v2_*.py`; job/atlas `v2` in `cast.py` (loaded last, replaces old sprites of the same id). Render: `tools/render_chars.sh v2`, pack: `tools/pack_sprites.py v2`.
- Forts painted with the same sunset lighting (`art/blender/bg/castles.py`), grotto eyes removed, beach and mid layer repainted (`r1_lib.py`).
- HUD, result panel, Quartermaster: skin block at the end of `src/ui/style.css`; Quartermaster rows in `src/main.js` (`armoury`).
- Feel: `src/render/renderer.js` (decals, sparks, rings, recoil, hit-stop, spawn pop). Cannon rules: `src/sim/battle.js` + `data/game.json` (`directBonus`, `knockback`, `salvage`). Balance re-tuned (docs/balance.md, change 7).
- Tools: `tools/moment.mjs` (repeatable battle moment, `?test=1&seed=N`), `tools/impact.mjs`, `tools/uishots.mjs`, `tools/compare.py`, `tools/sheet.py`.

## Known weak points
- Everything outside the slice is still old art: other crew, Scuttler and other monsters, Kelpie, Mother Fathom, night cove, title, sea chart, stage select, settings.
- Open items in `docs/review/review-3.md` (powder icon, cannon button icon, Quartermaster backdrop, number pile-ups in dense fights).
- Gullwake not enlarged; no foreground layer yet.
- Sound never heard by a person. Nothing tested on a real iPhone (display font there is Copperplate; unseen).
- Boss fight ~4.5 min without upgrades.

## Phase 3 (after approval)
All crew, Captain, every monster, Kelpie, Mother Fathom on kit2; night cove; title; sea chart; every screen; sound cues; update `docs/next-regions.md` (still describes the first world's regions) to the new standard.
