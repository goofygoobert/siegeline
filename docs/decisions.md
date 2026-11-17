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
