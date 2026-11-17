# Siegeline — game design

World: **Tales of the Brine**, pirates against the monsters of sea folklore (full cast, places and palette in docs/world-pirates.md). The previous world, The Ashen Marches, is kept as git tag `ashen-marches-v1`. Mechanics and numbers didn't change with the re-theme; internal ids (e.g. `ashguard` = Hatchguard) stayed so saves and tools keep working. Every world-specific word in the interface lives in `data/world.json`.

Numbers live in `data/`. The tables at the end are generated from those files (`node tools/gen_tables.mjs`), so they can't drift.

## 1. The pitch in one line
The tide turned green and the drowned came back: send your pirate crew down the beach, fire the fort's great cannon with your thumb, and sink the Drowned Grotto before the monsters of the deep take the Gullwake.

## 2. Battle

**Field.** One wide lane, 2600 px long (about 2.2 phone screens). Your **Gullwake** stands on the left and the enemy **Drowned Grotto** on the right. The camera pans with a drag and follows the fight when you leave it alone.

**Powder (energy).** You start each battle with 55 powder. It refills at 7 per second (upgradable) up to a store of 100 (upgradable). Every unit card has a powder cost and a cooldown. A full store wastes powder, which nudges you to keep sending.

**Sending units.** Tap a card and the unit marches out of the keep. Units walk until an enemy is within their range, then fight. Friendly units pass through each other, enemies block. Ranged units fire arcing shots; healers and supports hang back.

**The castle weapon: Long Tom, the fort cannon.** Hold the cannon button, drag back like a slingshot, and release. A dotted arc and a landing ring show where it will hit, and the camera slides to show the landing point. Each cannonball explodes for area damage, knocks enemies back and leaves a burning patch for 3 s. It reloads in 3.5 s (upgradable). Bolts that reach the Drowned Grotto do half damage to it.

**Powers (abilities with cooldowns).**
- *Broadside* (unlocked after stage 1): tap the icon, then tap the field. Eight burning stones fall around that spot over 1.2 s. 40 s cooldown.
- *Sea Shanty* (unlocked after stage 3): all your units move 35% faster, attack faster and heal 15% for 7 s. 50 s cooldown.

**The hero: Captain Rook Halloran** (unlocked after stage 2). His banner charges for 25 s, then you tap it to call him in once per battle. He is a heavy melee fighter with a cleave. Every 12 s he raises his flare pistol in a **Flare pistol** that burns and stuns nearby monsters for 1.5 s. When he falls, he's gone for that battle.

**Win and loss.** Bring the Drowned Grotto to zero to win; lose if the Gullwake falls. In the boss stage the gate is sealed and you win by killing the boss. When the gate drops below half health the Host sends a rush wave, announced with a callout, so the end of a battle builds to a climax.

**Stars** (per stage, earned separately so replays still pay): 1 for winning, 1 for keeping the Gullwake above 60% health, and 1 for winning under the par time. Each new star pays 30 doubloons.

## 3. Player units (20 in the full game, 6 in region 1)
Every unit has a role, a cost, a cooldown, a clear counter, and levels 1–10. At **level 5** and **level 10** it gets a new look (re-rendered sprites: extra gear, then gold trim and a glowing cursed-gold weapon) and a perk. Region 1's six:

| Unit | Job | Beats | Beaten by |
|---|---|---|---|
| Hatchguard | cheap shield wall; takes 25% less melee damage | drowners, scuttlers | spitters, bloater blasts |
| Blackpowder | archer; arrows set targets burning | bloaters (kill them at range), spitters | gnawers rushing past the line |
| Rope Rat | fast and cheap; double damage first strike | spitters in the back line | brutes |
| Anchorman | slow heavy; area slam with knockback | brutes, packs | gnawer swarms, ranged chip damage |
| Shantyman | aura slows monsters by 30% | brutes, swarms | spitters out of bell range |
| Sawbones | heals the most wounded ally every 2.2 s | long fights, the boss | anything reaching the back line |

The other 14 (Boarding Pike, Powder Monkey, Gull Rider, Fire-Eater, Grappler, Swivel Gun, Sea Priest, First Mate, Ironhull, Mortar Crew, Ship's Dogs, Hedge Witch, Harpooner, The Iron Figurehead) cover anti-large, siege, flying, area, pull, revive, buff, tank, artillery, swarm, curse, anti-air and an ultimate. They arrive at a steady pace through regions 2–6 (table below).

## 4. Enemies
Three factions with distinct behaviour:
- **The Deep** (regions 1, 4, 6): monsters of sea folklore. They come in numbers, are individually weak, and bring plenty of tricks: drowned sailors, fast crab-things, ink-lobbing squid-folk, bursting pufferghasts and huge barnacle trolls, then merfolk and selkies on Sunken Bell Reef.
- **The Drowned Fleet** (region 3): ghost pirates. Few but armoured, with long-range spectral muskets, and ghost captains who heal each other. They punish spamming and reward the siege and anti-armour units.
- **The Fog-Fae and serpents** (regions 2 and 5): will-o'-wisps that fly and lure, and leaping sea serpents. They push you toward anti-air, slows and burst damage.

**Elites** appear from stage 5 on: more health and damage, a sickly green glow and a slightly bigger body. **Mini-bosses** (the Kelpie in region 1) enrage below half health. Each region ends with a **boss** that has its own attack pattern and readable warnings.

### Region 1 boss: Mother Fathom
7000 HP (before stage power). She walks in 20 s after the battle starts while the Host keeps coming. Her attacks, each with a warning:
1. **Tentacle Sweep** (every 7 s when someone is near): she raises the tentacle for 1.3 s while a red zone pulses on the ground in front of her. Then she swings for 90 damage with heavy knockback. Pull back or let Hatchguards take it.
2. **Scuttler Call** (every 18 s): she throws her arms up and screams for 1 s, then four Gnawers burst out beside her.
3. **Ink Bomb** (every 11 s): she targets your furthest-back unit (usually healers or archers) or the Gullwake. A red ring marks the spot for 1.5 s before a ink bomb lands for 70 area damage and leaves a fire patch.
4. **Winded**: after every sweep she is winded for 2.5 s (stars circle her head, a callout says so) and takes 50% more damage. This is the moment to fire the cannon and drop Broadside.
5. **Phase two** below 50% health: a flash and a roar, after which she is 20% faster with 30% shorter cooldowns, and her sweep leaves burning tar behind.

When she dies, the game drops into slow motion for 1.6 s with a white-gold flash and a big shake.

## 5. World and stages (~60 stages)
| Region | Stages | Faction | Boss | New for the player |
|---|---|---|---|---|
| r1 Saltwick Cove | 5 + boss | the Deep | Mother Fathom | 6 crew, the Captain, Broadside, Sea Shanty |
| r2 The Fogbanks | 6 + boss + 1 side + 1 challenge | Fog-Fae (flyers) | the Wisp Mother | Boarding Pike, Powder Monkey, Gull Rider |
| r3 The Cutthroat Isles | 7 + boss + 1 side + 1 challenge | the Drowned Fleet | Captain Barnaby Dread | Fire-Eater, Grappler, Swivel Gun |
| r4 Sunken Bell Reef | 7 + boss + 1 side + 1 challenge | the Deep (merfolk, selkies) | the Selkie Queen | Sea Priest, First Mate, Ironhull |
| r5 Leviathan's Reach | 7 + boss + 1 side + 1 challenge | sea serpents | the Leviathan | Mortar Crew, Ship's Dogs, Hedge Witch |
| r6 The Maelstrom | 11 + boss + 2 side + 1 challenge | all three | the Kraken | Harpooner, The Iron Figurehead |

Total: 6 + 9 + 10 + 10 + 10 + 15 = 60. Each region has its own background set, music variation, enemy mix and boss. **Side stages** are optional and pay extra doubloons with an odd rule (night only, no hero). **Challenge stages** are replayable endless waves with a high-score star track.

## 6. Progress
- **Doubloons** are the only currency, earned only by playing. First clear pays the full reward (120 to 400 in region 1), a replay pays 35%, each new star pays 30, and a loss pays 2 per kill up to 40.
- **The Quartermaster** spends doubloons on unit levels (1–10), hull planks, Long Tom, the powder store and flow, the hero, and each power. Costs grow ×1.4–1.6 per level.
- **Unlocks arrive steadily**: in region 1, every first clear unlocks something (Runner and Broadside, then Anchorman and the hero, then Shantyman and Rally, then Sawbones).
- **No purchases, no ads, no timers, no energy-to-play.**

## 7. Difficulty
- Stage 1 is a tutorial taught by doing: four one-line prompts that pause the enemy waves until you've done the thing (send, aim and fire). It's winnable without upgrades.
- Stages 2–3 are winnable without upgrades by a decent player. Stages 4–5 and the boss reward a few sensible upgrades (about what first clears plus a replay or two pay for).
- The curve is checked with the headless test player at several skill and upgrade levels (docs/balance.md). Targets: an unupgraded average player wins stage 1 ~95% and stage 3 ~70%, and the boss ~30% unupgraded vs ~75% with modest upgrades. No stage should be impossible or trivial.
- Losses are fair: every boss hit is warned, the results screen gives a tip based on what killed you, and the Upgrade button is one tap away.

## 8. Feel (the touches that make it land)
| Moment | Touches | Sound |
|---|---|---|
| Any hit | white hit-flash on the sprite, splatter (dark red for Wardens, ash and powder for monsters), damage number that pops and rises | blade / claw / blunt hit |
| Heavy hit / slam | knockback slide, dust ring, small screen shake | blunt hit |
| Cannon shot | aim arc and landing ring, camera slides to the landing point, explosion of powder and smoke, burning patch, shake scaled to hits, "3 down!" callout on multi-kills | cannonball fire (thunk and whistle), cannonball hit, reload click |
| Death | body collapses and fades; monsters burst into powder and ash | hollow / warden death |
| Bloater | fiery burst that hurts both sides, orange flash, shake | bloater burst |
| Hero call | gold flash, shake, "The Marshal rides!" callout | horn |
| Flare | gold ring and flash, stunned stars over enemies | flare |
| Boss | entrance roar with music duck and shake; pulsing red warning zones; phase-2 flash; slow motion on the kill | roar, warning, slam |
| Gate under half | "They're rushing!" callout | — |
| Win | slow motion and flash as the gate falls, stars pop in one by one, coins fly to the counter and tick it up with rising pitch | crumble, win sting, star, coin |
| Loss | heavy shake, low sting, specific tip, Upgrade button | lose sting |
| Powder full | the counter turns gold | soft chime |
| UI | every button presses in (scale .96) and has a tap sound; screens ease in | tap / back / upgrade / locked |

Reduced motion turns off shake, flashes and slow animation, but keeps the information.

## 9. Region 1 in detail — Saltwick Cove
A sunset harbour cove with wrecks, jetties and a lighthouse on the cliffs. Sunset backgrounds for stages 1–5, and the cove under a green moon for the boss.

| # | Stage | What it teaches | Enemy mix |
|---|---|---|---|
| 1 | Tide Turns Green | sending, powder, aiming the cannon | drowners, a few scuttlers |
| 2 | The Smugglers' Steps | Broadside on clumps; spitters need a fast answer | + inkspitters |
| 3 | Pufferghast Shoals | keep melee away from bloaters, let archers pop them; call the hero | + pufferghasts, first barnacle troll |
| 4 | The Broken Lighthouse | the Shantyman slows big things; first mini-boss | + the Kelpie, trolls |
| 5 | Wreckers' Reef | full mix with elites; the Sawbones keeps a push alive | everything, elites |
| B | Mother Fathom | read the warnings, protect the back line | boss + steady Host |

## 10. Data tables (generated)
<!-- GENERATED -->
### All player units (Lantern Wardens)

| # | Unit | Role | Region | Cost | Cooldown s | HP | DMG | Atk every s | Range | Speed | Special | Countered by | Level 5 look | Level 10 look |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hatchguard | front line | r1 | 50 | 3 | 260 | 16 | 1.1 | 28 | 44 | meleeGuard | Inkspitters and Pufferghast bursts wear it down | Iron-banded hatch: guard 35% | Gilded hatch and cursed-gold cutlass: guard 45%, +15% damage |
| 2 | Blackpowder | ranged | r1 | 80 | 5 | 95 | 20 | 1.5 | 240 | 40 | projectile, burn | Scuttlers rush past the front line | Leather jerkin: +1 s burn | Gilded flintlock: shots pierce one monster |
| 3 | Rope Rat | fast | r1 | 40 | 2 | 75 | 11 | 0.55 | 24 | 95 | firstStrike | Barnacle Trolls crush it in one blow | Studded vest: +20% hp | Cursed-gold knives: first strike x3 |
| 4 | Shantyman | support | r1 | 100 | 14 | 140 | 6 | 1 | 30 | 40 | slowAura | Inkspitters out-range the song | Brass-buttoned squeezebox: slow 35% | Gilded squeezebox: slow 40%, reach 210 |
| 5 | Anchorman | heavy | r1 | 160 | 15 | 600 | 64 | 2.3 | 36 | 30 | splash, knockback | Slow: Scuttler swarms and ink chip it down | Chain-mail sleeves: +20% hp | Cursed-gold anchor: splash 75, leaves embers |
| 6 | Sawbones | healer | r1 | 120 | 16 | 110 | 0 | 2.2 | 200 | 38 | heal | Anything that reaches the back line | Second lantern: heals 2 crew | Golden lamp: heal +50% |
| 7 | Boarding Pike | anti-large | r2 | 70 | 5 | 180 | 14 | 1.2 | 44 | 40 | bonusVsLarge | Swarms | +reach | x2.5 vs large |
| 8 | Powder Monkey | siege | r2 | 120 | 12 | 120 | 300 | 3 | 20 | 50 | structureOnly, suicide | Any defender | +blast | double charge |
| 9 | Gull Rider | flying | r2 | 140 | 10 | 160 | 24 | 1 | 30 | 70 | flying | Archers | dive | talon rend |
| 10 | Fire-Eater | area | r3 | 130 | 10 | 150 | 18 | 1.2 | 90 | 36 | cone | Heavies | wider | lingering fire |
| 11 | Grappler | control | r3 | 110 | 10 | 200 | 15 | 2 | 160 | 38 | pull | Fast units | longer chain | double pull |
| 12 | Swivel Gun | siege | r3 | 180 | 18 | 260 | 70 | 2.8 | 360 | 22 | pierce | Rushers | armour | twin bolts |
| 13 | Sea Priest | revive | r4 | 150 | 20 | 130 | 8 | 1.5 | 180 | 36 | revive | Ranged focus | 2 revives | revive at full |
| 14 | First Mate | buffer | r4 | 140 | 14 | 320 | 22 | 1.2 | 30 | 40 | dmgAura | Splash | +aura | +armour aura |
| 15 | Ironhull | tank | r4 | 220 | 20 | 1400 | 30 | 1.8 | 30 | 24 | armor | Curses | +armour | taunt |
| 16 | Mortar Crew | artillery | r5 | 200 | 18 | 150 | 80 | 3.5 | 420 | 24 | splash, lob | Flyers | faster | incendiary |
| 17 | Ship's Dogs | swarm | r5 | 90 | 8 | 70 | 10 | 0.7 | 22 | 90 | count | Splash | 4 hounds | bleeding bites |
| 18 | Hedge Witch | curse | r5 | 150 | 16 | 120 | 12 | 1.6 | 200 | 34 | curse | Rushers | wider curse | curse spreads |
| 19 | Harpooner | anti-air | r6 | 100 | 8 | 170 | 26 | 1.2 | 150 | 40 | bonusVsFlying | Ground heavies | faster | chain throw |
| 20 | The Iron Figurehead | ultimate | r6 | 400 | 45 | 3200 | 120 | 2.6 | 50 | 20 | splash, knockback | Its own cost | burning aura | beacon beam |

Levels 1–10: +8% HP and +7.000000000000001% damage per level; new look and perk at levels 5 and 10.

### All enemies

| Enemy | Faction | Region | HP | DMG | Atk every s | Range | Speed | Behaviour |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Drowner | hollow | r1 | 165 | 16 | 1.2 | 26 | 34 | A drowned sailor come back up the beach. Slow, many, relentless. |
| Scuttler | hollow | r1 | 80 | 10 | 0.6 | 22 | 80 | A crab-thing with too many legs. Scuttles past slow defenders. |
| Inkspitter | hollow | r1 | 135 | 24 | 1.8 | 210 | 30 | Squid-headed and patient. Lobs glowing ink from behind the horde. |
| Pufferghast | hollow | r1 | 350 | 12 | 1.4 | 26 | 22 | A swollen spined puffer on stubby legs. Bursts when killed, hurting everyone nearby. |
| Barnacle Troll | hollow | r1 | 870 | 68 | 2.4 | 34 | 24 | A sea troll crusted in coral. Every swing sends sailors flying. |
| The Kelpie (mini-boss) | hollow | r1 | 2340 | 81 | 1.8 | 40 | 26 | A ghastly water-horse with a kelp mane. Rears up and rages when wounded. |
| Mother Fathom (boss) | hollow | r1 | 5600 | 123 | 2 | 60 | 18 | The sea hag of the deep. Raises her tentacle before she sweeps: get clear. |
| Will-o'-Wisp | hollow | r2 | 150 | 18 | 1.4 | 120 | 40 | A drifting ghost light that leads sailors astray. |
| Drowned Boarder | tithe | r3 | 400 | 29 | 1.2 | 44 | 36 | A ghost pirate of the Drowned Fleet, armoured in barnacles. |
| Ghost Gunner | tithe | r3 | 235 | 41 | 2.2 | 280 | 30 | Long-range spectral musketeer. |
| Ghost Captain | tithe | r3 | 1505 | 59 | 1.6 | 34 | 28 | Heals the Drowned Fleet around him. |
| Selkie Raider | mawborn | r4 | 265 | 26 | 0.8 | 24 | 85 | Seal-skinned raider, fast on sand. |
| Coral Golem | mawborn | r4 | 2670 | 88 | 2.6 | 36 | 18 | A walking reef. Armoured, crushing. |
| Sea Serpent | mawborn | r5 | 1170 | 51 | 1.6 | 160 | 40 | Leaps from the waves and spits brine. |

Elite versions: HP x2.2, damage x1.4, speed x1.1, green glow and 12% larger.

### Region 1 stages

| Stage | Name | Enemy gate HP | Enemy power | Par time | First-clear marks | Unlocks | Scripted waves |
| --- | --- | --- | --- | --- | --- | --- | --- |
| r1s1 | Tide Turns Green | 1200 | x2.42 | 110 s | 120 | cinder_runner, ember_rain | 2s 2x husk; 20s 3x husk; 38s 2x gnawer; 52s 4x husk |
| r1s2 | The Smugglers' Steps | 1600 | x2.38 | 140 s | 150 | maulwright, hero | 2s 3x husk; 22s 1x spitter; 26s 3x husk; 45s 4x gnawer; 60s 2x spitter; 64s 4x husk |
| r1s3 | Pufferghast Shoals | 2000 | x1.99 | 155 s | 180 | bellringer, rally | 2s 4x husk; 22s 1x bloater; 30s 2x spitter; 45s 5x gnawer; 60s 2x bloater; 75s 6x husk; 90s 1x brute |
| r1s4 | The Broken Lighthouse | 2500 | x1.18 | 190 s | 210 | lamplighter | 2s 4x husk; 18s 2x spitter; 32s 1x brute; 34s 3x husk; 55s 6x gnawer; 70s 2x bloater; 85s 1x husk_warden; 88s 4x husk |
| r1s5 | Wreckers' Reef | 3000 | x0.97 | 205 s | 240 | - | 2s 5x husk; 15s 4x gnawer; 28s 1x brute; 30s 3x spitter; 50s 3x bloater; 65s 4x husk (elite); 80s 2x brute; 100s 1x husk_warden; 102s 6x gnawer |
| r1boss | Mother Fathom | sealed (defeat the boss) | x0.97, boss x1.64 | 215 s | 400 | - | 2s 4x husk; 12s 2x spitter |
<!-- /GENERATED -->
