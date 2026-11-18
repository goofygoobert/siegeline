# HANDOFF — current state
Updated 2026-11-17 (redesign phase 3 done on branch `redesign`; not yet merged to `main`). World: Tales of the Brine.

## Where things are
- **Live (old look):** https://goofygoobert.github.io/siegeline/ — built from `main`.
- **Preview (full region redesign):** https://goofygoobert.github.io/siegeline/preview/ — built from `redesign` by the same workflow, added only if its own tests and play-through pass. Re-publish: `gh workflow run test-and-publish --ref main`. Own save slot, no offline install.
- **To go live:** merge `redesign` into `main` and push (the gate runs). Then remove the preview step from the workflow if no longer wanted. Waiting for the owner's word.
- Read: `docs/design/art-direction.md`, `docs/design/helper-brief.md`, `docs/review/review-4.md`, the "Roll-out" sections of `docs/decisions.md` and `docs/performance.md`, `docs/next-regions.md`.

## How to rebuild art
- Crew: `tools/render_chars.sh v2` then `tools/pack_sprites.py units unitsb unitsc`. Captain and monsters: `v2field` then `hero enemies`. Boss: `v2boss` then `boss`. Portraits: `ui` then `ui`. Then `node tools/atlas_manifest.mjs`.
- Forts: `art/blender/bg/render_all.sh castles`; backgrounds: `bg`; title: `title` (libs listed in `art/blender/bg/title_libs.txt`).
- One character while working: add its id to a `look_*` job in `art/blender/cast.py` and to `MINE` in `tools/render_chars.sh`; view with `tools/sheet.py`.

## Known weak points
- Open items in `docs/review/review-4.md` (Mother Fathom's face, monsters evenly lit, title composition, cooldown display, number pile-ups, no monster portraits).
- No foreground layer; fort not re-modelled (only drawn 1.2x); no new sound cues.
- Texture memory on a real iPhone not measured (24 atlas pages; a boss battle loads about 14).
- Sound never heard by a person. Nothing tested on a real iPhone. Display font on iPhone (Copperplate) unseen.
- `docs/asset-contract.md` still describes the old atlas names.
- Boss fight about 4.5 minutes without upgrades.

## Phase 4 parts 3 and 4 (branch `phase4`, not live)
- **Rules:** traits and effects live in `src/sim/battle.js` (search `airborne`, `shell`, `siege`, `slip`, `vault`, `net`); skills are data (`data/units.json` → `skills`) applied by `applySkill` in `src/sim/stats.js`.
- **Design data:** `data/design/roster.json` (traits, crew strong/weak, intended and wrong loadouts per stage). `node tools/gen_counters.mjs` rewrites the tables in `docs/design/strategy.md`.
- **Proof:** `node tools/strategy_proof.mjs 40 24` (about 5 minutes) → `docs/balance-strategy.md`, copied into `docs/balance.md`. `node tools/tune_loadouts.mjs 30 [stage]` finds the stage power where the intended crew wins about 85%.
- **Screens:** `prepScreen` (scouting + loadout) and `tavern` in `src/main.js`; styles at the end of `src/ui/style.css`.
- **Polish checks:** `tools/polish_check.py`, `tools/screens.mjs` (see `docs/design/polish-log.md`).
- **New cast art:** `art/blender/chars/v2_{harpooner,netcaster,gallows_gull,bellback,tide_nurse}.py`, in the `v2` / `v2field` jobs.
- **Save version 3** migrates six-stage saves (tested in `tools/test_sim.mjs`).
