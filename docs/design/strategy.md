# Strategy design: choosing the right crew is the game

Status: **design, waiting for the owner's OK.** Nothing here is built yet except the generator that makes the tables.
All names and designs are our own. Tables between `GEN` markers are written by `node tools/gen_counters.mjs` from
`data/design/roster.json`; do not edit them by hand. The generator also runs the design checks at the bottom.

## The problem today

Any crew wins any stage. The test player beats every stage sending whatever is affordable, upgrades push through
anything, and the only real decision is where to point the cannon. Enemies differ in health and speed, not in what they
ask of you.

## The idea in one paragraph

Every monster has a **trait** you can read from its outline. Every trait shuts down some crew and is shut down by
others. Before a stage you **scout** the monsters that are coming and pick a small **loadout** from a larger roster.
A sensible but wrong loadout loses; the right one wins and feels clever. Upgrades make a right answer safer, they never
turn a wrong answer into a right one.

## Traits (what a monster demands)

<!-- GEN:TRAITS -->
| Trait | Icon | Read it from the silhouette | Rule | Answers (from the data) |
|---|---|---|---|---|
| **Swarm** | three dots | small, low and many, arriving in packs of 5-8 | Fast and weak; arrive in packs that surround single-target crew. | Shantyman, Netcaster, Fire-eater, Powder Monkey, Swivel Gun, Cooper, Storm-caller |
| **Flying** | wing | off the ground with a shadow below it | Melee cannot hit it. It flies over the front line to the back line and the fort. | Blackpowder, Netcaster, Gull-rider, Storm-caller |
| **Siege** | arc over a wall | tall, stays at the back, lobs glowing globs | Out-ranges every crew shooter. Targets the back line, then the fort. | Rope Rat, Harpooner, Gull-rider, Grapnel |
| **Exploder** | burst | round, swollen, glowing cracks | Bursts when it dies and hurts everyone close, crew and monsters. | Hatchguard, Blackpowder, Powder Monkey, Diver, Cooper |
| **Armoured** | plate | huge, crusted in barnacle plates | Takes 12 less damage from every hit, so many small hits do almost nothing. | Anchorman, Harpooner, Boathook, Swivel Gun, Colour Sergeant |
| **Shelled** | shell | carries a ship's bell or shell in front of it | The shell soaks the first 300 damage from the front. Blunt and blast hits break it at once. | Rope Rat, Anchorman, Powder Monkey, Grapnel |
| **Healer** | drop in a ring | soft glowing bell-shape floating low, a beam to whoever it mends | Mends the most hurt monster nearby. A fight in front of it never ends. | Rope Rat, Harpooner, Fire-eater, Gull-rider, Grapnel, Storm-caller |
| **Venomous** | green drop | covered in long thin spines | Each hit adds a stack of poison. | Hatchguard, Sawbones, Chaplain, Diver |
| **Submerged** | fin | a moving ripple and fin in the sand | Cannot be targeted while under the sand. Surfaces at the first crew member it passes, behind the front line. | Shantyman, Anchorman, Lookout, Diver |
| **Ghostly** | wisp | see-through, no feet, pale blue | Blades, shot and cannonballs pass through. Only fire and light hurt it; in lantern light it turns solid. | Blackpowder, Sawbones, Fire-eater, Lookout, Chaplain |
<!-- /GEN:TRAITS -->

How a trait is shown: the silhouette first (a flier is off the ground, a shelled thing carries its shell in front),
then a small icon on the scouting card and above the monster the first time it appears in a stage. A monster has at
most two traits.

Cut from the starting list: none, but **burrowing** and **submerged** are one trait (Submerged), and **poisonous** is
Venomous. Added from the world: nothing extra; ten is already the most a player can hold in their head.

## Crew (20 in the full game, 8 in region 1)

Each has one job and at least two things they are bad at. Nobody is the best pick everywhere.

<!-- GEN:CREW -->
| Crew | From | Job | Weakness |
|---|:-:|---|---|
| **Hatchguard** | R1 | Wall. His door blocks blasts and poison from the front. | Hits lightly, cannot reach the air, out-ranged. |
| **Blackpowder** | R1 | Shooter. Burning shot reaches the air, burn ignores armour, fire hurts ghosts. | Slow reload: packs swamp him. Shells soak his shots. |
| **Rope Rat** | R1 | Diver. Vaults the front line to knife whatever hides at the back, and gets behind shells. | Fragile: dies to blasts, poison and big hits. |
| **Shantyman** | R1 | Crowd control. His song slows everything in earshot. | Does no damage himself; siege out-ranges the song. |
| **Anchorman** | R1 | Breaker. One huge blunt hit: cracks armour, smashes shells, and the slam drives the buried up. | Slow swing: packs and fliers ignore him. |
| **Sawbones** | R1 | Mender. Heals crew, cleans off poison, and his lantern makes ghosts solid. | Cannot fight; dies to anything that reaches him. |
| **Harpooner** | R1 | Sniper. One long, slow, piercing shot that ignores armour and out-ranges siege. | One target at a time; useless against packs. |
| **Netcaster** | R1 | Catcher. Nets drag fliers to the ground and pin whatever they land on. | No damage; ghosts drift through the net. |
| **Fire-eater** | R2 | Burner. A short cone of flame. | Must stand close; shells and armour shrug it off until they burn. |
| **Lookout** | R2 | Spotter. Marks the buried and the unseen so everyone can hit them; marked monsters take more damage. | Barely fights. |
| **Boathook** | R2 | Giant-killer. Long reach, double damage to anything big. | Clumsy against small fast things. |
| **Powder Monkey** | R3 | Bomber. Lobs a keg: blast damage in a circle, breaks shells. | Long fuse; fast things are gone before it lands. |
| **Gull-rider** | R3 | Flier. Crosses the field in the air to hit siege and menders, and duels other fliers. | Thin; one shooter brings her down. |
| **Chaplain** | R3 | Blesser. A ring of light: ghosts inside are solid and burn. | Slow, short reach. |
| **Diver** | R4 | Brass-suit tank. Immune to poison, fights the buried under the sand. | Very slow, very dear. |
| **Grapnel** | R4 | Puller. Hooks one monster out of its line and drags it to the crew. | One at a time; cannot pull the big ones. |
| **Swivel Gun** | R4 | Line gun. A shot that passes through a whole row. | Cannot aim up; needs a wall in front. |
| **Cooper** | R5 | Builder. Rolls out a barrel wall that blocks the beach for a while. | The wall does nothing to what goes over or under it. |
| **Colour Sergeant** | R5 | Flag. Crew near the colours hit harder and cannot be stunned. | Useless alone. |
| **Storm-caller** | R6 | Weather. Calls lightning that chains through wet monsters and strikes the air first. | Long wait between strikes. |
<!-- /GEN:CREW -->

Two are new in region 1: the **Harpooner** and the **Netcaster**. The other six keep their looks; their numbers and
rules change to fit the jobs above. The Captain stays a once-per-battle hero and is not a loadout pick. Long Tom is the
player's own answer on top of the loadout: its direct hit is strong against Armoured and Flying, its splash against
Swarm, and it cannot hurt Ghostly or Submerged monsters.

## Counter table: region 1

**+** strong, · even, − weak. Strong means the crew member has an answer to one of the monster's traits and no weakness
to another; weak is the reverse.

<!-- GEN:COUNTERS_R1 -->
| Crew \ Enemy | Drowner | Scuttler | Gallows Gull | Inkspitter | Pufferghast | Barnacle Troll | Bellback | Tide Nurse | The Kelpie |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **Hatchguard** | **+** | · | − | − | **+** | − | · | · | − |
| **Blackpowder** | · | − | **+** | − | **+** | · | − | · | · |
| **Rope Rat** | · | · | − | **+** | − | − | **+** | **+** | − |
| **Shantyman** | · | **+** | · | − | · | · | · | − | · |
| **Anchorman** | · | − | − | · | · | **+** | **+** | · | **+** |
| **Sawbones** | · | · | − | − | · | · | · | · | · |
| **Harpooner** | · | − | · | **+** | · | **+** | − | **+** | **+** |
| **Netcaster** | · | **+** | **+** | − | · | − | · | · | − |
<!-- /GEN:COUNTERS_R1 -->

## Counter table: full game

<!-- GEN:COUNTERS_ALL -->
| Crew \ Enemy | Drowner | Scuttler | Gallows Gull | Inkspitter | Pufferghast | Barnacle Troll | Bellback | Tide Nurse | The Kelpie | Spinefoot | Sandjaw | Will-o'-wisp | Drowned Pikeman | Drowned Gunner | Ghost Bosun | Reef Hound | Coral Golem | Selkie Rider |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **Hatchguard** | **+** | · | − | − | **+** | − | · | · | − | **+** | · | − | − | − | − | **+** | − | **+** |
| **Blackpowder** | · | − | **+** | − | **+** | · | − | · | · | · | − | **+** | **+** | · | **+** | − | − | · |
| **Rope Rat** | · | · | − | **+** | − | − | **+** | **+** | − | − | · | − | − | **+** | **+** | − | · | − |
| **Shantyman** | · | **+** | · | − | · | · | · | − | · | · | **+** | − | − | − | − | **+** | · | **+** |
| **Anchorman** | · | − | − | · | · | **+** | **+** | · | **+** | · | **+** | − | · | − | − | − | **+** | **+** |
| **Sawbones** | · | · | − | − | · | · | · | · | · | **+** | − | · | **+** | · | **+** | **+** | · | − |
| **Harpooner** | · | − | · | **+** | · | **+** | − | **+** | **+** | · | · | − | · | · | · | − | · | · |
| **Netcaster** | · | **+** | **+** | − | · | − | · | · | − | · | · | · | − | − | − | **+** | − | · |
| **Fire-eater** | · | **+** | − | − | · | · | − | **+** | · | · | · | · | **+** | · | **+** | **+** | − | · |
| **Lookout** | · | − | · | · | − | − | · | · | − | · | **+** | **+** | · | **+** | **+** | − | − | · |
| **Boathook** | **+** | − | − | · | · | **+** | · | · | **+** | − | · | − | **+** | · | · | − | **+** | · |
| **Powder Monkey** | · | **+** | − | · | **+** | · | **+** | · | · | · | − | − | − | − | − | **+** | **+** | · |
| **Gull-rider** | · | · | **+** | **+** | · | − | − | **+** | − | − | · | **+** | − | **+** | **+** | − | − | · |
| **Chaplain** | · | − | − | − | · | · | · | · | · | **+** | · | · | **+** | · | **+** | · | · | · |
| **Diver** | · | · | − | − | **+** | · | · | · | · | **+** | **+** | − | − | − | − | **+** | · | **+** |
| **Grapnel** | · | − | · | **+** | · | − | **+** | **+** | − | · | · | − | − | · | · | − | · | · |
| **Swivel Gun** | **+** | **+** | − | · | · | **+** | · | · | **+** | · | − | − | · | − | − | **+** | **+** | − |
| **Cooper** | **+** | **+** | − | − | **+** | · | · | · | · | · | − | − | · | − | · | **+** | · | · |
| **Colour Sergeant** | **+** | · | · | − | − | **+** | · | · | **+** | · | − | · | **+** | − | · | · | **+** | − |
| **Storm-caller** | · | **+** | **+** | · | · | − | − | **+** | − | · | − | **+** | − | · | **+** | **+** | − | − |
<!-- /GEN:COUNTERS_ALL -->

## Loadout and scouting

- **Roster:** 8 crew in region 1, growing by 2–3 a region to 20.
- **Slots:** 4 in stages 1–3, 5 from stage 4 to the end of region 1, 6 for the rest of the game. With 8 crew and 5
  slots there are 56 loadouts in region 1; with 20 and 6 there are 38,760. Enough that no list of "best teams" covers
  it.
- **Scouting screen** (replaces today's stage sheet): the monsters of the stage as large portraits with their trait
  icons, in the order they first arrive, and one line on the new one ("Flying: melee cannot reach it"). No numbers.
- **Loadout screen:** the roster as large cards. Tapping a monster on the scouting strip lights the crew who are
  strong against it and dims the ones who are weak, straight from the counter data. You fill the slots and press Fight.
  The game remembers the last loadout per stage.
- **No hard locks:** you may take a wrong loadout in. You will lose, and the defeat screen names the trait that beat
  you and one crew member who answers it.
- After a loss you can change the loadout and retry without going back to the map.

## Status effects

| Effect | Rule | Stacking | How the player sees it |
|---|---|---|---|
| **Poison** | 4 damage a second for 6 s. Healing received is halved while poisoned. | Up to 3 stacks; a new stack refreshes the timer. | Green bubbles rising from the figure; health pip turns green; a small number of drops (1–3) by the pip. |
| **Burn** | 8 damage a second for 4 s. Ignores armour. Shells do not block it. | Does not stack; re-applying refreshes. | Small flames on the figure; orange flicker on the outline. |
| **Slow** | Movement and attack speed −35%. | Does not stack; the strongest applies. | Blue-grey tint on the legs, music notes or net over the figure. |
| **Stun** | Cannot move or attack for 1.2 s. | Cannot be stunned again for 3 s after. | Stars circling the head; figure held in its "hit" pose. |
| **Shell break** | A Shelled monster loses its shell for good; an Armoured one loses half its armour for 6 s. | Refreshes. | The shell bursts into pieces that stay on the sand; a cracked-plate mark over the monster. |
| **Solid** (ghosts only) | Inside lantern or blessing light a Ghostly monster can be hit by anything. | – | The ghost turns opaque and gains an outline while in the light; the light's edge is drawn on the sand. |

Rules that keep it readable: a figure shows at most two effect marks (the two most recent), effects never change a
silhouette, and every effect has one colour used for nothing else.

## Difficulty

- **Target for the intended loadout:** 75–90% wins for an average player with no upgrades.
- **Target for a sensible wrong loadout** (a reasonable team that lacks the answer to the stage's new trait): under 25%.
- **Random loadout:** somewhere between, by how many of its picks happen to answer the stage.
- **Upgrades cannot brute-force a stage:** a wrong loadout with upgrades two tiers ahead of the stage must still be
  under 50%. This works because most traits are rules, not numbers: melee never reaches a flier, shot never hurts a
  ghost, and 12 armour removes a small hit entirely however many of them you buy.
- Stage power is tuned so the right loadout is at the top of its target; stars reward doing it cleanly.

## Region 1, reworked: one new idea per stage

Region 1 grows from six battles to eight so each stage can teach one thing by making you lose to it once.

<!-- GEN:STAGES -->
| # | Stage | Slots | New idea, taught by playing | You'll face | A right loadout | A sensible wrong one |
|---|---|:-:|---|---|---|---|
| 1 | Tide Turns Green | 4 | Hold a line: a wall in front, a shooter behind. | Drowner | Hatchguard, Blackpowder | Only shooters: nothing holds the Drowners off them. |
| 2 | The Smugglers' Steps | 4 | Swarm: packs beat single hits. Slow them or net them, and aim the cannon at the pack. | Drowner, Scuttler | Hatchguard, Shantyman, Netcaster | Wall and shooters: Scuttlers run round the wall and eat the shooters. |
| 3 | Gallows Roost | 4 | Flying: melee cannot reach. Bring shooters or nets. | Drowner, Gallows Gull | Hatchguard, Blackpowder, Netcaster | All melee: the Gulls pass overhead and peck the fort down. |
| 4 | The Broken Lighthouse | 5 | Siege: something at the back out-ranges you. Send a diver or a sniper. | Drowner, Scuttler, Inkspitter | Hatchguard, Rope Rat, Harpooner | Wall and Blackpowders: ink falls on them from out of range all fight. |
| 5 | Pufferghast Shoals | 5 | Exploder: kill it at range or behind a door, never in a crowd. | Drowner, Pufferghast, Gallows Gull | Hatchguard, Blackpowder, Harpooner | Rope Rats and Anchormen: each burst wipes the melee pile. |
| 6 | Wreckers' Reef | 5 | Armoured: small hits bounce. Bring one big hit or burn. | Drowner, Scuttler, Barnacle Troll | Hatchguard, Anchorman, Harpooner, Shantyman | Rope Rats and Netcasters: nothing they have gets through the plates. |
| 7 | The Bell Ground | 5 | Shelled and Healer together: break the shell, reach the mender. | Bellback, Tide Nurse, Drowner, Scuttler | Anchorman, Rope Rat, Shantyman, Netcaster | Blackpowders and Harpooners: shells soak the shot and the Nurse undoes the rest. |
| 8 | Mother Fathom | 5 | The exam: she calls packs, spits ink and sends Gulls. No single answer. | cinder_matron, Scuttler, Gallows Gull, Inkspitter | Hatchguard, Netcaster, Blackpowder, Harpooner, Sawbones | Any four of one kind. |
<!-- /GEN:STAGES -->

The first time a new trait appears the battle pauses once, for one line and one arrow at the monster. After that the
scouting screen carries it.

## How part 3 proves it

`tools/balance.mjs` will run, for each stage: the intended loadout, the listed wrong loadout and 50 random loadouts,
200 battles each at three skill levels and two upgrade levels, and record in `docs/balance.md`:

- win rate for right, wrong and random per stage (right must beat wrong by at least 40 points);
- that no single loadout wins every stage above 50%;
- that every crew member appears in between 10% and 90% of winning loadouts across the region.

A failing check blocks publishing, like the play-through.

## Design checks (from the data, today)

<!-- GEN:CHECKS -->
- All design checks pass: every trait has 2+ answers (and 2+ inside region 1 for region 1 traits), every crew member has 2+ weaknesses, nobody is strong against more than half the enemies, every region 1 crew member is in at least one intended loadout and none is in all of them.
<!-- /GEN:CHECKS -->

## Recruiting (owner's request: some crew free, some to buy)

- **Free recruits.** Some first clears give a crew member for nothing. They walk up the beach on the results screen
  and join the roster.
- **The Tavern.** Others appear in the Tavern after a given clear and cost doubloons. The Tavern also offers one crew
  member from a later region early, at a high price, changing after each stage you clear.
- **No real money**, ever. Every crew member can be earned by playing; buying only spends doubloons sooner.

Region 1 plan (from `data/design/roster.json`):

| Crew | How you get them |
|---|---|
| Hatchguard, Blackpowder | from the start |
| Rope Rat | free after stage 2 |
| Netcaster | Tavern after stage 2, 350 doubloons |
| Shantyman | free after stage 3 |
| Harpooner | Tavern after stage 4, 600 doubloons |
| Anchorman | free after stage 5 |
| Sawbones | Tavern after stage 6, 500 doubloons |

The stage plan is built so a stage never needs a crew member you could not have yet: each stage's intended loadout
uses only crew available by then, with the Tavern ones being the clever choice, not the only one.

## Skills (owner's request: new abilities)

Each crew member learns one skill at level 5 and picks one of two at level 10 (the level 5 and 10 looks already
exist). A skill changes what they do, not just a number, so it opens new answers to traits. Examples:

| Crew | Level 5 | Level 10: pick one |
|---|---|---|
| Hatchguard | Brace: standing still, the door blocks shots for those behind him | Shove: every third block knocks back · Taunt: nearby monsters must attack him |
| Blackpowder | Tar shot: leaves a small fire patch | Long barrel: +40% range · Grapeshot: every fourth shot splits in three |
| Netcaster | Weighted net: netted fliers fall and are stunned | Wide net: two targets · Hooked net: netted monsters take +25% |

The rest are written in part 3. Skills never remove a crew member's weakness; they widen what the crew member is
good for.

## Saves

Old saves keep loading. Unlocked crew, levels and stars carry over; the two new stages appear as not yet played; a
default loadout is filled in for each stage from the crew the save already owns.
