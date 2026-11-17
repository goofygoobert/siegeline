# Siegeline: playtest review 2

Sources: pt = `docs/shots/playthrough`, plus `se`, `notch`, `rec_*`, and my own `tools/shots.mjs` run against the live URL. `rec_*` and `docs/shots/0*` come from an older build (they say "LANTERN KEEP" where pt says "KEEP").

## The 22 items from review 1

| # | Item | Status | Note |
|---|---|---|---|
| 1 | HUD over result modal | Fixed | Modal now sits above the HUD |
| 2 | Victory buttons clipped | Fixed | Fits with the unlock line |
| 3 | Stage sheet hides content | Fixed | Opaque, fits on SE (see F) |
| 4 | Settings overflow / toast | Partly | Fits on SE; the error toast still covers Sound effects (pt/25) |
| 5 | Old scenes behind screens | Fixed | Solid Armoury and map backgrounds |
| 6 | Region clear unlocks nothing | Partly | Continue + CLEARED chip; still no "more regions coming" on the map (pt/23) |
| 7 | White blobs, stacked numbers | Partly | White-out gone; numbers still stack ("43/43", pt/19) |
| 8 | Cards hard to tell apart | Partly | Names and an affordable glow added; Torchbow and Bellringer portraits still match |
| 9 | Boss grind | Partly | Telegraphs and winded window added; still a 4:25 win, keep 680/2000 (pt/22) |
| 10 | Dead opening, stage 3 | Partly | First enemy at about 0:11 (rec); not rechecked on the current build |
| 11 | Tutorial card unaffordable | Fixed | 57 embers, card lit |
| 12 | Time star never earned | Fixed | Earned on stages 1, 3 and 4 |
| 13 | Same loss tip | Fixed | Bloater tip + "290 health left. So close." |
| 14 | Coin pill over gate label | Fixed | |
| 15 | SE HUD | Partly | Shows KEEP; ember meter still floats over the lane (se/08) |
| 16 | Right buttons crowd gate | Not fixed | Three stacked buttons now cover the gate (pt/19, 21) |
| 17 | Locked items lack hint | Fixed | "3)" orphans onto its own line (pt/14) |
| 18 | Title tagline / version | Partly | Darker scrim; tagline still crosses the tower, version text on lava |
| 19 | Map pixelated, no locks | Partly | Lock icons touch the names; terrain stair-steps; "The Cinder Maw" clipped on SE |
| 20 | Copy | Partly | Time line good; "+ 165  marks" still has a double gap |
| 21 | Node stars invisible | Fixed | |
| 22 | Rec loads wrong stage | Not a bug | Script jump by design |

10 fixed, 10 partly fixed, 1 not fixed, 1 not a bug.

## New findings

### Major
- **A. The public URL serves an old build.** The live site shows "LANTERN KEEP" and none of the newest polish, while the dev build reports the same `fa47e1f` stamp on newer code. Friends would get the old game. Fix: deploy HEAD, and add a dirty flag or build time to the version string.
- **B. Boss callouts overlap into gibberish.** Where: rec_09 (1:46–2:05), rec_12 (3:29–3:40). The cause is that `callout()` (src/main.js:383) appends each callout with no queue. The text is also red on a red sky, over the boss. Fix: use one slot, where a warning replaces the current callout and the rest wait. Add a dark plate and keep it clear of the sprite.
- **C. The boss is still too long.** Over 4 min, the line is pushed back to the keep. Fix: cut boss HP by a further 15–20%, or lengthen the winded window.

### Minor
- **D.** The tutorial tip box touches the right screen edge (pt/04, 05, 08). Fix: centre it with max-width 60vw.
- **E.** The loader probes `ui|fx|castles|enemies 2–8.json` until it hits a 404. That is about 35 failed requests a session, including 503s from Pages. Fix: write a page-count manifest at build time.
- **F.** "Fight 🪙120" reads like a price. Fix: add a line "First clear: +120 marks".
- **G.** The HUD clock says 1:55 while the results say "you took 1:48" (pt/07). Fix: freeze the clock during tutorial holds.
- **H.** The Settings sheet has no bottom padding, so Import touches the edge (pt/25). The Armoury tabs touch the header (pt/14). Fix: 16 px plus the safe-area inset on the sheet, and a 12 px gap on the tabs.
- **I.** No aim arc shows while aiming (se/07, notch/07), which design §8 promises.

### Polish
The hero button is square while the other powers are round. "Lamplighter" fills its card edge to edge. The coin stack covers the first digit while it animates ("I65"). The settings icon looks like a sun. Regenerate `rec_*` and `docs/shots/0*`.

## Verdict
Close. Review 1's blockers are gone and the loop reads clearly. Before sharing: redeploy (A), queue the callouts (B), and shorten the boss (C). Then fix item 16 and the floating ember meter.
