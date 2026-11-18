# Polish log (part 4)

Every fix made in the professional-finish pass, with how it was found. Re-run the checks with:

- `.venv/bin/python tools/polish_check.py` — contact sheets of every packed sprite on dark, light and magenta at 1x
  and 3x (`docs/design/polish/sheet-*.png`) and an automated report (`docs/design/polish/report.md`): pale edge
  fringes, frames packed closer than 2 px, feet against the anchor.
- `VW=667 VH=375 node tools/screens.mjs docs/design/polish/se` and
  `VW=844 VH=390 NOTCH=1 node tools/screens.mjs docs/design/polish/notch` — every screen at iPhone SE size and at a
  notched size with the landscape safe areas (47 pt sides, 21 pt bottom) applied.

## Sprites

| Check | Result | Fix / note |
|---|---|---|
| Edge fringe (pale halo on the outline) | 0 sprites over 12% | Already fixed in round 2: no white copies, no halo, no contour pass; the ink line is thin and coloured. The blast effect is exempt (it is meant to glow). |
| Colour bleed between packed frames | 0 pairs closer than 2 px | Packer keeps padding; checked across all 26 atlas pages. |
| Magenta / background bleed | none seen on the magenta sheet | Renders have true alpha; no keyed background. |
| Hovering (feet above the anchor) | 0 sprites | The owner's "hovering" complaint was the outline and halo, removed in round 2; the anchors themselves are on the feet. |
| Feet below the anchor | all within perspective except the Scuttler (15 px) | The camera looks slightly down, so the near foot sits lower than the centre of the feet. The Scuttler's crab legs splay toward the camera; its contact shadow is drawn at the anchor, so it reads as standing. Left as is. |
| Clipped parts | packer warning only for the Anchorman's level-10 look (anchor touches the top of the render cell on some walk frames) | Open: needs a taller render cell for that one look. |
| Poke-through | checked on the helpers' sheets for the five new characters | Netcaster: the net disappears in her death rather than dropping (helper note); harmless. |
| Draw order | fliers draw over the ground fight; nets, shell bars and crack marks draw over the figure they belong to; shadows stay on the sand under fliers | Added in part 3 (`drawEntity`). |

## Screens

| Screen | Found at | Fix |
|---|---|---|
| Stage path | SE: stage names overlapped each other with eight stages | Only the stage you are heading for shows its name; every other stage is named on its loadout screen. |
| Region top bar | SE: "Tavern" and "Quartermaster" did not fit | Icon-only buttons under 720 pt (the names stay as accessible labels). |
| Scouting + loadout | SE and notched: a second row of monsters / crew was cut off | Smaller monster and crew cards; both lists scroll if a later region has more. |
| Scouting + loadout | phone: the row of chosen-crew portraits spilled out of its panel | Removed (it repeated the check marks); a "3 of 4 places filled" line instead. |
| Results | win screens with a new recruit pushed the Next / Retry / Map buttons out of view | With news to show, the star checklist steps aside (the big stars already say it) and the recruit card is compact. |
| Tavern, Quartermaster | notched: two narrow columns truncated names ("Hatchg…") | One wide column until two full cards fit. |
| Settings | notched: Export and Import sit at the bottom edge and need a small scroll | Unchanged (pre-existing, the sheet scrolls). |

## Not yet checked

- A real iPhone (notch, home indicator, Safari's own bars). The notched size here is simulated.
- Sound for the new events (nets, bells, the leap): they reuse existing cues and nobody has heard them.
