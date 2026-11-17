# Siegeline — project rules

Original side-scrolling castle battle game for phone browsers (iPhone first, also desktop).
Everything is original: never copy another game's names, characters, art, sounds or UI.

## Rules
- Jetson (this machine) is shared with other services: check `free -m` before builds/browser tests,
  one heavy task at a time, stop anything that takes available memory under 700 MB.
- All 3D modelling/rendering goes through `gpu5070` (see the gpu-5070 skill). Never render on the Jetson.
  If the PC is busy/asleep: `gpu5070 wake`, retry every few minutes, keep doing engine work meanwhile.
- Ports in use by other services: 8765, 8740, 8642. Dev server: 127.0.0.1:5193.
- Free assets only; log every source + licence in docs/credits.md. No secrets or personal data in repo.
- Commit + push at every milestone. Only publish builds that pass the play-through test.
- Engine and data formats are world-independent: a world = art + names + data files.

## Layout
- `src/` game code (sim/ is pure logic, no DOM; render/, ui/, audio/, save/)
- `data/` units, enemies, stages, regions, upgrades (JSON, checked by `data/schema/`)
- `art/blender/` character kit + per-character scripts; `art/out/` rendered frames (gitignored);
  `public/assets/` packed atlases shipped with the game
- `tools/` build, atlas packing, balance runner, screenshot runner
- `docs/` design, art guide, decisions, balance, performance, credits, worlds/

## Run
- `npm run dev` (Vite on 127.0.0.1:5193) · `npm run build` → `dist/` · `npm test` (sim + data checks)
- `npm run balance` high-speed headless simulation of every stage
- Python tools use `.venv/bin/python`
