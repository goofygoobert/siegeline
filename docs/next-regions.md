# Plan: the next three regions (Tales of the Brine)

Each region reuses the engine, saves, UI and tools unchanged. It needs data files (units, enemies, stages), Blender scripts for the new cast and scenery, one music variation, and a balance pass. Internal ids in `data/` keep their first-world names (for example `wailer`, `tithe_spear`); only display names and art change.

## The standard every region inherits

Nothing ships that does not meet `docs/design/art-direction.md`. In practice:

- **Characters** are built with `art/blender/kit2.py`, never the old rigid kit: lofted parts, two-bone limbs, built faces, trailing bits, a held wind-up and a stretched strike. One file per character in `art/blender/chars/v2_<id>.py`, registered in `cast.py` with a `v2*` animation set. Each new character names its silhouette hook in the file header and must be recognisable filled black at 40 px.
- **Light tells the side.** Crew are lit from the front by the scene's key light; monsters have it behind them, dark with their own glow. A region changes the key colour and the glow colour, never the rule. Region palettes go in a table like the one in the art direction before any art is made.
- **Monsters must not be dark lumps.** Mid-tone bodies, large glowing eyes, one light signature shape. This was the main fault found in review 3.
- **The stage** keeps fighters as the strongest contrast: mid-ground props sit in the middle values, nothing darker than a monster or lighter than a crew face in the fight band, ground readable and sparse.
- **Forts and the enemy base** use the same paint as the figures and have three damage states that change the outline.
- **Screens** use the wood, brass, canvas and chart-paper skin in `src/ui/style.css`. A new mechanic gets one HUD element on the rail, not a floating widget.
- **Feel:** every new attack, spawn and death gets a visible wind-up, an impact effect and a sound cue, checked in a paused frame (`tools/impact.mjs`, `tools/moment.mjs`).
- **Checks before publishing:** play-through and save tests, the balance grid inside the curve in `docs/balance.md`, screenshots at iPhone SE and a notched size, download size and frame time noted, and one fresh reviewer comparing against the previous build.
- **Helpers** get `docs/design/helper-brief.md`, one narrow list of characters, and their own files only.

## Region 2: The Fogbanks (9 stages: 6 + boss + 1 side + 1 challenge)
- **Setting:** a sea of standing fog over drowned sandbars; ghost lights lead ships onto the rocks. Key light: a low white sun through fog; monster glow: cold blue-white.
- **New crew:** **Boathook** (anti-large, double damage to big monsters), **Powder Monkey** (runs to the enemy base and blows a hole in it, only hits buildings), **Gull-rider** (first flyer, ignores the ground line).
- **New monsters:** Will-o'-wisp (flying light that forces flyers and musketeers into play), Bog Drowner (slows on hit), plus fog variants of the region 1 Deep.
- **New mechanic:** fog banks drift across the beach and hide anything inside them. Flares and the Shantyman's song reveal them.
- **Boss: the Three Lanterns.** Three linked wisps. Hit one and the others heal it, so damage must be split. Warnings: a rising chime before a sound cone, lanterns that brighten before a heal pulse.
- **Side stage:** Night Watch (no Captain, permanent fog). **Challenge:** Endless Tide, wave after wave with a star track for score.

## Region 3: The Cutthroat Isles (10 stages)
- **Setting:** the wrecks of the Drowned Fleet on black rock, tattered colours, treasure chests in the shallows. Key light: stormy noon breaking through cloud; glow: ghost-green lantern light.
- **New crew:** **Fire-eater** (cone of flame against swarms), **Grapnel** (pulls one monster forward out of its line), **Swivel Gun** (long-range cart gun that pierces a line).
- **New monsters (ghost pirates):** Drowned Pikeman (armoured), Drowned Gunner (outranges your Blackpowders), Ghost Bosun (heals other ghosts, armoured). These are the first enemies that punish spamming one unit.
- **New mechanic:** armour. A shield mark shows reduced damage, so Boathooks and Powder Monkeys matter.
- **Boss: Purser Gallow.** He buys ghost crew mid-fight from a chest you can see emptying, and throws a gold ward on allies. Breaking the chest stops the hiring.

## Region 4: Sunken Bell Reef (10 stages)
- **Setting:** a reef at low tide with a drowned church bell, tide pools and coral arches. Key light: pale dawn; glow: pearl and pink. Darker stages are lit mostly by your own lanterns.
- **New crew:** **Chaplain** (brings one fallen crew member back), **Colour Sergeant** (flag aura, +20% damage), **Diver** (big armoured tank in a brass helmet).
- **New monsters:** Reef Hound (fast pack beast), Coral Golem (tank that leaves burning brine), Selkie Rider (rides a wave down the beach; shoot it with Long Tom before it lands).
- **New mechanic:** the tide. Waves roll up the beach on a schedule and push both sides, so timing your sends matters.
- **Boss: the Bell Mother.** She rises from a tide pool and splits the beach with channels of deep water that block walking for a few seconds (shown on the sand first).

## Steady unlock pace (whole game)
3 new crew per region in regions 2–5, 2 in region 6 (20 in total). Each first clear unlocks something: a crew member, a power tier, or a new Quartermaster row (hull planks tier 2, a second cannonball type in region 3).

## What I need from you
- Play region 1 on your phone and say what feels too hard, too easy or unclear. Balance is tuned with a test player, not a human.
- Whether the sound is good. Nobody has heard it.
- Optional: names you would like changed.
