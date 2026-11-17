# Brief for art helpers (phase 3): rebuild characters with the carved-figure kit

You are rebuilding characters for Siegeline (pirates vs sea-folklore monsters, phone game) to an agreed art standard.
Work only in the repo `/home/jack/game`. You have never seen this project: read these first, in order:
1. `docs/design/art-direction.md` — the standard. Shape language, palette, lighting, silhouette hooks, animation rules.
2. `docs/world-pirates.md` — who each character is.
3. `art/blender/kit2.py` — the kit (Fig, loft, slab, orb, cone, block, body, fists, boots, bare_feet, head_crew, chain, toggle, turn, pose, keys, blend, run_anims, V2 palette).
4. `art/blender/chars/v2_ashguard.py` and `art/blender/chars/v2_husk.py` — the two finished reference characters. Copy their structure.
5. `art/blender/cast.py` — animation sets (frame counts per anim are fixed there) and render jobs.

## Hard rules
- Create ONLY the files named in your task (`art/blender/chars/v2_<id>.py`). Do not edit any other file (not kit2.py, cast.py, kit.py, tools, src, data). If you need a helper function, define it inside your own file with a unique prefix. If something in the kit truly blocks you, work around it in your file and say so in your report.
- Do not run git. Do not start browsers, dev servers or npm. Do not render or run Blender on this machine (a shared Jetson): all rendering goes to the PC through the test job below.
- Original designs only: nothing from pirate films, shows or other games. Folklore creatures are fine as our own designs.
- Each file starts with `from kit import *` and registers specs exactly like the references:
  `register(dict(id="<id>", facing=-1 for monsters, v2=<fig function>, anims=dict(idle=..., walk=..., attack=..., hit=..., die=...)))`.
  Crew have three looks: ids `<id>`, `<id>_t2`, `<id>_t3` (spec["tier"] 1/2/3): t2 adds gear (leather, iron, a feather), t3 adds brass/gold trim and a glowing green-gold "cursed" weapon (`V2["cursed"]`, glow 0.35). Monsters have one look.
- Anim functions have the signature `fn(t, i, n)` and return a pose dict (see kit2.pose docstring). idle and walk loop (t = i/n); the others run 0..1. In attack-type anims the strike must land at the `hit` frame index given in cast.ANIMSETS (attack: frame 5 of 10, so the strike key sits at t≈0.56, after a held wind-up), with a swipe/flash toggle visible on that frame.
- Figures face +X, near side is -Y, feet at z=0. Monsters are mirrored by the pipeline (`facing=-1`); build them facing +X too.
- Heights (world units; the Hatchguard is 1.95): given per character in your task. Keep everything inside the render cell: nothing further than about 2.6 units in front of or behind the feet, and for death poses lying down count the full body length.
- Every figure must pass the silhouette test from the art direction at 40 px tall. Crew: upright, square, warm, readable face (eyes not covered). Monsters: hunched/lopsided, dark with glow, but keep the head, eyes and one signature shape clearly readable against a dark background (the Drowner needed lighter skin and bigger glowing eyes; learn from that).
- Die: crew stagger and end lying on the sand. Monsters come apart wetly and end as a low ink puddle with a few remains (see `dr_die`).

## How to test (the only way to see your work)
Run, with the Bash tool and `dangerouslyDisableSandbox: true` (the sandbox has no route to the render PC):
```
cd /home/jack/game && tools/render_chars.sh <your test job>
```
It bundles your files, renders every frame on the RTX 5070 PC and prints `OK <job> (N/N frames)` or an error. Jobs queue if another helper is rendering; just wait. If it prints SYNTAX or FAIL, read `art/build/<job>.log`, and for script errors run
`gpu5070 logs -n 400 <job id from the log> | grep -n "FAILED\|Error\|Traceback" -A8` (also unsandboxed).
Then make a contact sheet and LOOK at it with the Read tool (write it under `$TMPDIR`, run this one sandboxed):
```
cd /home/jack/game && .venv/bin/python tools/sheet.py <your test job> $TMPDIR/<name>.png 1,12,20,22,24,28,37,40 0.5
```
(frame numbers: idle 1-8, walk 9-16, attack 17-26, hit 27-30, die 31-40; the hero adds special 41-50; the boss set is different, see cast.ANIMSETS["v2boss"].) Crop/zoom with PIL if you need a closer look. Iterate until each figure reads clearly: expect 4-8 render rounds. Check specifically: face readable, silhouette hook obvious, no limb detached at a joint, feet on the ground line, strike pose stretched and clear, death ends flat on the ground, nothing clipped at a cell edge.

## Report back (short)
For each character: the file, the silhouette hook you built, anything that still looks weak, anything in the kit you had to work around, and the path of your final contact sheet(s).
