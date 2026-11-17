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
