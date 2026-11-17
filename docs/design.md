# Siegeline — game design

World: **The Ashen Marches** (see docs/worlds). Tone: grim ember-dusk fantasy, a little gruesome, never horror.
Numbers live in `data/`. The tables at the end are generated from those files (`node tools/gen_tables.mjs`), so they can't drift.

## 1. The pitch in one line
Send lantern-carrying soldiers down an ash-choked valley, fling burning bolts from your keep's ballista with your thumb, and break the Maw Gate before the Hollow Host breaks you.

## 2. Battle

**Field.** One wide lane, 2600 px long (about 2.2 phone screens). Your **Lantern Keep** stands on the left and the enemy **Maw Gate** on the right. The camera pans with a drag and follows the fight when you leave it alone.

**Embers (energy).** You start each battle with 40 embers. They refill at 7 per second (upgradable) up to a store of 100 (upgradable). Every unit card has an ember cost and a cooldown. A full store wastes embers, which nudges you to keep sending.

**Sending units.** Tap a card and the unit marches out of the keep. Units walk until an enemy is within their range, then fight. Friendly units pass through each other, enemies block. Ranged units fire arcing shots; healers and supports hang back.

**The castle weapon: the Beacon Ballista.** Hold the ballista button, drag back like a slingshot, and release. A dotted arc and a landing ring show where it will hit, and the camera slides to show the landing point. Each bolt explodes for area damage, knocks enemies back and leaves a burning patch for 3 s. It reloads in 3.5 s (upgradable). Bolts that reach the Maw Gate do half damage to it.

**Powers (abilities with cooldowns).**
- *Ember Rain* (unlocked after stage 1): tap the icon, then tap the field. Eight burning stones fall around that spot over 1.2 s. 40 s cooldown.
- *Rally Bell* (unlocked after stage 3): all your units move 35% faster, attack faster and heal 15% for 7 s. 50 s cooldown.

**The hero: Marshal Edrin Vael** (unlocked after stage 2). His banner charges for 25 s, then you tap it to call him in once per battle. He is a heavy melee fighter with a cleave. Every 12 s he raises his lantern in a **Flare** that burns and stuns nearby Hollows for 1.5 s. When he falls, he's gone for that battle.

**Win and loss.** Bring the Maw Gate to zero to win; lose if your Keep falls. In the boss stage the gate is sealed and you win by killing the boss. When the gate drops below half health the Host sends a rush wave, announced with a callout, so the end of a battle builds to a climax.

**Stars** (per stage, earned separately so replays still pay): 1 for winning, 1 for keeping the Keep above 60% health, and 1 for winning under the par time. Each new star pays 30 marks.

## 3. Player units (20 in the full game, 6 in region 1)
Every unit has a role, a cost, a cooldown, a clear counter, and levels 1–10. At **level 5** and **level 10** it gets a new look (re-rendered sprites: extra armour, then gilded trim and an ember-glowing weapon) and a perk. Region 1's six:

| Unit | Job | Beats | Beaten by |
|---|---|---|---|
| Ashguard | cheap shield wall; takes 25% less melee damage | husks, gnawers | spitters, bloater blasts |
| Torchbow | archer; arrows set targets burning | bloaters (kill them at range), spitters | gnawers rushing past the line |
| Cinder Runner | fast and cheap; double damage first strike | spitters in the back line | brutes |
| Maulwright | slow heavy; area slam with knockback | brutes, packs | gnawer swarms, ranged chip damage |
| Bellringer | aura slows Hollows by 30% | brutes, swarms | spitters out of bell range |
| Lamplighter | heals the most wounded ally every 2.2 s | long fights, the boss | anything reaching the back line |

The other 14 (pikewall, sapper, kestrel rider, flame monk, chain warden, crossbow cart, grave priest, banner knight, ironclad, mortar crew, hound pack, ash witch, skyward lancer, lantern colossus) cover anti-large, siege, flying, area, pull, revive, buff, tank, artillery, swarm, curse, anti-air and an ultimate. They arrive at a steady pace through regions 2–6 (table below).

## 4. Enemies
Three factions with distinct behaviour:
- **The Hollow Host** (regions 1, 2, 6): the risen dead. They come in numbers, are cheap and individually weak, and use plenty of tricks: fast crawlers, lobbing spitters, exploding bloaters, giant brutes, and flying wailers in region 2.
- **The Gilded Tithe** (region 3): mercenary knights. Few but armoured, with long-range crossbows, and paladins who heal each other. They punish spam and reward the siege and anti-armour units.
- **The Mawborn** (regions 4–5): furnace beasts. Fast hounds, molten golems with armour and splash, and fire-breathing drakes that fly. They push you toward anti-air, slows and burst damage.

**Elites** appear from stage 5 on: more health and damage, an ember glow and a slightly bigger body. **Mini-bosses** (the Husk Warden in region 1) enrage below half health. Each region ends with a **boss** that has its own attack pattern and readable warnings.

### Region 1 boss: The Cinder Matron
7000 HP (before stage power). She walks in 20 s after the battle starts while the Host keeps coming. Her attacks, each with a warning:
1. **Censer Sweep** (every 7 s when someone is near): she raises the glowing censer for 1.3 s while a red zone pulses on the ground in front of her. Then she swings for 90 damage with heavy knockback. Pull back or let Ashguards take it.
2. **Ash Choir** (every 18 s): she throws her arms up and screams for 1 s, then four Gnawers burst out beside her.
3. **Ember Spit** (every 11 s): she targets your furthest-back unit (usually healers or archers) or the Keep. A red ring marks the spot for 1.5 s before a fireball lands for 70 area damage and leaves a fire patch.
4. **Winded**: after every sweep she is winded for 2.5 s (stars circle her head, a callout says so) and takes 50% more damage. This is the moment to fire the ballista and drop Ember Rain.
5. **Phase two** below 50% health: a flash and a roar, after which she is 20% faster with 30% shorter cooldowns, and her sweep leaves fire behind.

When she dies, the game drops into slow motion for 1.6 s with a white-gold flash and a big shake.

## 5. World and stages (~60 stages)
| Region | Stages | Faction | Boss | New for the player |
|---|---|---|---|---|
| r1 Cinderfold Vale | 5 + boss | Hollow | The Cinder Matron | 6 units, hero, Ember Rain, Rally |
| r2 The Bell Marshes | 6 + boss + 1 side + 1 challenge | Hollow (flyers) | The Mire Choir | Pikewall, Sapper, Kestrel Rider |
| r3 Gilded Causeway | 7 + boss + 1 side + 1 challenge | Tithe | Abbot-Banker Corvane | Flame Monk, Chain Warden, Crossbow Cart |
| r4 Hollowdeep Mines | 7 + boss + 1 side + 1 challenge | Mawborn | The Slag Mother | Grave Priest, Banner Knight, Ironclad |
| r5 The Ember Wastes | 7 + boss + 1 side + 1 challenge | Mawborn | Ashwing | Mortar Crew, Hound Pack, Ash Witch |
| r6 The Cinder Maw | 11 + boss + 2 side + 1 challenge | all three | The Maw | Skyward Lancer, Lantern Colossus |

Total: 6 + 9 + 10 + 10 + 10 + 15 = 60. Each region has its own background set, music variation, enemy mix and boss. **Side stages** are optional and pay extra marks with an odd rule (night only, no hero). **Challenge stages** are replayable endless waves with a high-score star track.

## 6. Progress
- **Marks** are the only currency, earned only by playing. First clear pays the full reward (120 to 400 in region 1), a replay pays 35%, each new star pays 30, and a loss pays 2 per kill up to 40.
- **The Armoury** spends marks on unit levels (1–10), Keep walls, the ballista, the ember store and flow, the hero, and each power. Costs grow ×1.4–1.6 per level.
- **Unlocks arrive steadily**: in region 1, every first clear unlocks something (Runner and Ember Rain, then Maulwright and the hero, then Bellringer and Rally, then Lamplighter).
- **No purchases, no ads, no timers, no energy-to-play.**

## 7. Difficulty
- Stage 1 is a tutorial taught by doing: four one-line prompts that pause the enemy waves until you've done the thing (send, aim and fire). It's winnable without upgrades.
- Stages 2–3 are winnable without upgrades by a decent player. Stages 4–5 and the boss reward a few sensible upgrades (about what first clears plus a replay or two pay for).
- The curve is checked with the headless test player at several skill and upgrade levels (docs/balance.md). Targets: an unupgraded average player wins stage 1 ~95% and stage 3 ~70%, and the boss ~30% unupgraded vs ~75% with modest upgrades. No stage should be impossible or trivial.
- Losses are fair: every boss hit is warned, the results screen gives a tip based on what killed you, and the Upgrade button is one tap away.

## 8. Feel (the touches that make it land)
| Moment | Touches | Sound |
|---|---|---|
| Any hit | white hit-flash on the sprite, splatter (dark red for Wardens, ash and embers for Hollows), damage number that pops and rises | blade / claw / blunt hit |
| Heavy hit / slam | knockback slide, dust ring, small screen shake | blunt hit |
| Ballista shot | aim arc and landing ring, camera slides to the landing point, explosion of embers and smoke, burning patch, shake scaled to hits, "3 down!" callout on multi-kills | bolt fire (thunk and whistle), bolt hit, reload click |
| Death | body collapses and fades; Hollows burst into embers and ash | hollow / warden death |
| Bloater | fiery burst that hurts both sides, orange flash, shake | bloater burst |
| Hero call | gold flash, shake, "The Marshal rides!" callout | horn |
| Flare | gold ring and flash, stunned stars over enemies | flare |
| Boss | entrance roar with music duck and shake; pulsing red warning zones; phase-2 flash; slow motion on the kill | roar, warning, slam |
| Gate under half | "They're rushing!" callout | — |
| Win | slow motion and flash as the gate falls, stars pop in one by one, coins fly to the counter and tick it up with rising pitch | crumble, win sting, star, coin |
| Loss | heavy shake, low sting, specific tip, Upgrade button | lose sting |
| Embers full | the counter turns gold | soft chime |
| UI | every button presses in (scale .96) and has a tap sound; screens ease in | tap / back / upgrade / locked |

Reduced motion turns off shake, flashes and slow animation, but keeps the information.

## 9. Region 1 in detail — Cinderfold Vale
Vineyards and chapels buried in ash, with ruined watchtowers on the ridge. Dusk backgrounds for stages 1–5 and a night variant with a cracked ember moon for the boss.

| # | Stage | What it teaches | Enemy mix |
|---|---|---|---|
| 1 | Smoke on the Vines | sending, embers, aiming the ballista | husks, a few gnawers |
| 2 | The Chapel Road | Ember Rain on clumps; spitters need a fast answer | + spitters |
| 3 | Pyre Fields | keep melee away from bloaters, let archers pop them; call the hero | + bloaters, first brute |
| 4 | The Broken Watch | the Bellringer slows big things; first mini-boss | + Husk Warden, brutes |
| 5 | Ashfall Ridge | full mix with elites; the Lamplighter keeps a push alive | everything, elites |
| B | The Cinder Matron | read the warnings, protect the back line | boss + steady Host |

## 10. Data tables (generated)
<!-- GENERATED -->
### All player units (Lantern Wardens)

| # | Unit | Role | Region | Cost | Cooldown s | HP | DMG | Atk every s | Range | Speed | Special | Countered by | Level 5 look | Level 10 look |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ashguard | front line | r1 | 50 | 3 | 260 | 16 | 1.1 | 28 | 44 | meleeGuard | Spitters and Bloater blasts wear it down | Iron-banded shield: guard 35% | Gilded shield and ember blade: guard 45%, +15% damage |
| 2 | Torchbow | ranged | r1 | 80 | 5 | 95 | 20 | 1.5 | 240 | 40 | projectile, burn | Gnawers rush past the front line | Leather cowl: +1 s burn | Gilded bow: shots pierce one enemy |
| 3 | Cinder Runner | fast | r1 | 40 | 2 | 75 | 11 | 0.55 | 24 | 95 | firstStrike | Brutes crush it in one blow | Studded vest: +20% hp | Ember knives: first strike x3 |
| 4 | Bellringer | support | r1 | 100 | 14 | 140 | 6 | 1 | 30 | 40 | slowAura | Spitters outrange the bell | Bronze bell: slow 35% | Gilded bell: slow 40%, aura 210 |
| 5 | Maulwright | heavy | r1 | 160 | 15 | 600 | 64 | 2.3 | 36 | 30 | splash, knockback | Slow: gnawer swarms and ranged fire whittle it | Plated pauldrons: +20% hp | Ember maul: splash 75, leaves embers |
| 6 | Lamplighter | healer | r1 | 120 | 16 | 110 | 0 | 2.2 | 200 | 38 | heal | Anything that reaches the back line | Twin wick: heals 2 allies | Sun lamp: heal +50% |
| 7 | Pikewall | anti-large | r2 | 70 | 5 | 180 | 14 | 1.2 | 44 | 40 | bonusVsLarge | Swarms | +reach | x2.5 vs large |
| 8 | Sapper | siege | r2 | 120 | 12 | 120 | 300 | 3 | 20 | 50 | structureOnly, suicide | Any defender | +blast | double charge |
| 9 | Kestrel Rider | flying | r2 | 140 | 10 | 160 | 24 | 1 | 30 | 70 | flying | Archers | dive | talon rend |
| 10 | Flame Monk | area | r3 | 130 | 10 | 150 | 18 | 1.2 | 90 | 36 | cone | Heavies | wider | lingering fire |
| 11 | Chain Warden | control | r3 | 110 | 10 | 200 | 15 | 2 | 160 | 38 | pull | Fast units | longer chain | double pull |
| 12 | Crossbow Cart | siege | r3 | 180 | 18 | 260 | 70 | 2.8 | 360 | 22 | pierce | Rushers | armour | twin bolts |
| 13 | Grave Priest | revive | r4 | 150 | 20 | 130 | 8 | 1.5 | 180 | 36 | revive | Ranged focus | 2 revives | revive at full |
| 14 | Banner Knight | buffer | r4 | 140 | 14 | 320 | 22 | 1.2 | 30 | 40 | dmgAura | Splash | +aura | +armour aura |
| 15 | Ironclad | tank | r4 | 220 | 20 | 1400 | 30 | 1.8 | 30 | 24 | armor | Curses | +armour | taunt |
| 16 | Mortar Crew | artillery | r5 | 200 | 18 | 150 | 80 | 3.5 | 420 | 24 | splash, lob | Flyers | faster | incendiary |
| 17 | Hound Pack | swarm | r5 | 90 | 8 | 70 | 10 | 0.7 | 22 | 90 | count | Splash | 4 hounds | bleeding bites |
| 18 | Ash Witch | curse | r5 | 150 | 16 | 120 | 12 | 1.6 | 200 | 34 | curse | Rushers | wider curse | curse spreads |
| 19 | Skyward Lancer | anti-air | r6 | 100 | 8 | 170 | 26 | 1.2 | 150 | 40 | bonusVsFlying | Ground heavies | faster | chain throw |
| 20 | Lantern Colossus | ultimate | r6 | 400 | 45 | 3200 | 120 | 2.6 | 50 | 20 | splash, knockback | Its own cost | burning aura | beacon beam |

Levels 1–10: +8% HP and +7.000000000000001% damage per level; new look and perk at levels 5 and 10.

### All enemies

| Enemy | Faction | Region | HP | DMG | Atk every s | Range | Speed | Behaviour |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Husk | hollow | r1 | 165 | 16 | 1.2 | 26 | 34 | The risen dead of the Vale. Slow, numerous, relentless. |
| Gnawer | hollow | r1 | 80 | 10 | 0.6 | 22 | 80 | Scuttles on all fours past slow defenders. |
| Ash Spitter | hollow | r1 | 135 | 24 | 1.8 | 210 | 30 | Lobs burning ash from behind the horde. |
| Pyre Bloater | hollow | r1 | 350 | 12 | 1.4 | 26 | 22 | Swollen with embers. Bursts when killed, burning everyone nearby. |
| Bonecage Brute | hollow | r1 | 870 | 68 | 2.4 | 34 | 24 | A giant split open to the ribs. Every swing sends soldiers flying. |
| Husk Warden (mini-boss) | hollow | r1 | 2340 | 81 | 1.8 | 40 | 26 | Once a captain of the Vale. Enrages when wounded. |
| The Cinder Matron (boss) | hollow | r1 | 7000 | 103 | 2 | 60 | 18 | Mother of the Hollow Host. Raises her censer before she swings — get clear. |
| Wailer | hollow | r2 | 150 | 18 | 1.4 | 120 | 40 | Flying shade. |
| Tithe Spearman | tithe | r3 | 400 | 29 | 1.2 | 44 | 36 | Mercenary knight-spear. |
| Tithe Crossbow | tithe | r3 | 235 | 41 | 2.2 | 280 | 30 | Long-range mercenary. |
| Gilded Paladin | tithe | r3 | 1505 | 59 | 1.6 | 34 | 28 | Heals nearby Tithe. |
| Maw Hound | mawborn | r4 | 265 | 26 | 0.8 | 24 | 85 | Furnace beast. |
| Slag Golem | mawborn | r4 | 2670 | 88 | 2.6 | 36 | 18 | Molten tank. |
| Cinder Drake | mawborn | r5 | 1170 | 51 | 1.6 | 160 | 40 | Fire-breathing flyer. |

Elite versions: HP x2.2, damage x1.4, speed x1.1, ember glow and 12% larger.

### Region 1 stages

| Stage | Name | Enemy gate HP | Enemy power | Par time | First-clear marks | Unlocks | Scripted waves |
| --- | --- | --- | --- | --- | --- | --- | --- |
| r1s1 | Smoke on the Vines | 1200 | x2.42 | 110 s | 120 | cinder_runner, ember_rain | 2s 2x husk; 20s 3x husk; 38s 2x gnawer; 52s 4x husk |
| r1s2 | The Chapel Road | 1600 | x2.38 | 140 s | 150 | maulwright, hero | 2s 3x husk; 22s 1x spitter; 26s 3x husk; 45s 4x gnawer; 60s 2x spitter; 64s 4x husk |
| r1s3 | Pyre Fields | 2000 | x1.99 | 155 s | 180 | bellringer, rally | 2s 4x husk; 22s 1x bloater; 30s 2x spitter; 45s 5x gnawer; 60s 2x bloater; 75s 6x husk; 90s 1x brute |
| r1s4 | The Broken Watch | 2500 | x1.18 | 190 s | 210 | lamplighter | 2s 4x husk; 18s 2x spitter; 32s 1x brute; 34s 3x husk; 55s 6x gnawer; 70s 2x bloater; 85s 1x husk_warden; 88s 4x husk |
| r1s5 | Ashfall Ridge | 3000 | x0.97 | 205 s | 240 | - | 2s 5x husk; 15s 4x gnawer; 28s 1x brute; 30s 3x spitter; 50s 3x bloater; 65s 4x husk (elite); 80s 2x brute; 100s 1x husk_warden; 102s 6x gnawer |
| r1boss | The Cinder Matron | sealed (defeat the boss) | x0.97, boss x1.43 | 240 s | 400 | - | 2s 4x husk; 12s 2x spitter |
<!-- /GENERATED -->
