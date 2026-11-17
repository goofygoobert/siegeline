# Decisions made for you

Format: decision — reason — alternative considered.

## Preflight (answered by you)
- Name: **Siegeline**; repo goofygoobert/siegeline; GitHub Pages.
- Main target iPhone Safari (landscape, home-screen install); desktop browser also playable with mouse.
- Tone: grim and a bit gruesome (dark fantasy, some blood/ichor) but not horror, not cute.
- Deadline: ~12:00 on 2026-11-17.
- 5070: use whenever it is free, never alongside someone else's job; keep retrying.

## Mine
- Commit author is your GitHub no-reply address — keeps your real email out of a public repo — alternative: a bot name.
- Local server on 127.0.0.1:5193 — 8765/8740/8642 already belong to your other services.
- **World: The Ashen Marches** — best fit for the grim-not-horror tone, strongest silhouettes (armoured Wardens vs horned husks), and the most dramatic fire, light and night-time effects — alternatives: Saltreach (tides), Glasswind (bright desert). All three worlds' scripts are in art/blender/chars and art/blender/bg.
- **Characters are rigid toy parts on pivot rigs (empties), not skinned meshes** — robust, consistent, fast to render, fits the chunky toy style — alternative: armature + skin weights (fragile from code in one night).
- **Toon look: 3-band shading + inverted-hull outline in EEVEE, fixed ortho camera at 8° elevation, 96 px per world unit, key light upper-left** — readable at small sizes; same camera for the whole cast keeps scale consistent.
- **Colours are written as sRGB in scripts and converted to linear in the kit** — what you see in the script is what renders.
- **Plain Canvas 2D + DOM interface, no game library** — on iPhone Safari, Canvas 2D drawImage from a few atlases is GPU-backed and fast for ~100 sprites; DOM gives crisp text, real buttons and accessibility for menus and HUD; the bundle is ~90 kB — alternative: PixiJS (WebGL batching; more weight and complexity than this sprite count needs).
- **Vite for the build, hand-written service worker** — small, proven, no plugins to break — alternative: vite-plugin-pwa.
- **Battle sim at a fixed 30 Hz with render interpolation, seeded RNG** — same result on every phone, runs ~4000x real time headless for balance — alternative: variable step (non-deterministic).
- **System fonts only** — zero download, works offline, nothing sent to font hosts — alternative: a Google display font.
- **Ground line at y=400 of 540 logical px** — the bottom ~130 px is HUD on a phone; moved from 470 after the first screenshots.
- **Global speedScale 1.5 on walking speed** — the first build took ~30 s before the armies met; this keeps the data's relative speeds.
- **Auto-follow camera after 3.5 s without panning** — a 2600 px field on a phone screen needs the camera to find the fight; panning and aiming always take over.
- **Every unlocked unit, power and the hero are usable in any stage** (replays included) — simpler and friendlier than per-stage loadouts.
- **A loss still pays a few marks (2 per kill, max 40)** — so a loss is never wasted time, without making grinding losses worthwhile.
