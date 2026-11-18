# Strategy summary (one page)

Full design: `docs/design/strategy.md`. Tables here are copied from the generated ones (`node tools/gen_counters.mjs`).

**The idea.** Every monster has a trait you can read from its outline. Before a stage you see what is coming and pick a
small crew from a larger roster. A sensible but wrong pick loses; the right one wins; upgrades cannot brute-force it.

**Slots and roster.** Region 1: 8 crew to choose from, 4 slots in stages 1-3 and 5 slots after. Full game: 20 crew, 6 slots.

## Region 1 roster (8)
| Crew | Job | Weakness |
|---|---|---|
| **Hatchguard** | Wall. His door blocks blasts and poison from the front. | Hits lightly, cannot reach the air, out-ranged. |
| **Blackpowder** | Shooter. Burning shot reaches the air, burn ignores armour, fire hurts ghosts. | Slow reload: packs swamp him. Shells soak his shots. |
| **Rope Rat** | Diver. Vaults the front line to knife whatever hides at the back, and gets behind shells. | Fragile: dies to blasts, poison and big hits. |
| **Shantyman** | Crowd control. His song slows everything in earshot. | Does no damage himself; siege out-ranges the song. |
| **Anchorman** | Breaker. One huge blunt hit: cracks armour, smashes shells, and the slam drives the buried up. | Slow swing: packs and fliers ignore him. |
| **Sawbones** | Mender. Heals crew, cleans off poison, and his lantern makes ghosts solid. | Cannot fight; dies to anything that reaches him. |
| **Harpooner** | Sniper. One long, slow, piercing shot that ignores armour and out-ranges siege. | One target at a time; useless against packs. |
| **Netcaster** | Catcher. Nets drag fliers to the ground and pin whatever they land on. | No damage; ghosts drift through the net. |

New in region 1: **Harpooner** and **Netcaster**. Later regions add: Fire-eater, Lookout, Boathook, Powder Monkey, Gull-rider, Chaplain, Diver, Grapnel, Swivel Gun, Cooper, Colour Sergeant, Storm-caller.

## Traits
| Trait | You see | It means | Answers |
|---|---|---|---|
| **Swarm** | small, low and many, arriving in packs of 5-8 | Fast and weak; arrive in packs that surround single-target crew. | Shantyman, Netcaster, Fire-eater, Powder Monkey, Swivel Gun, Cooper, Storm-caller |
| **Flying** | off the ground with a shadow below it | Melee cannot hit it. It flies over the front line to the back line and the fort. | Blackpowder, Netcaster, Gull-rider, Storm-caller |
| **Siege** | tall, stays at the back, lobs glowing globs | Out-ranges every crew shooter. Targets the back line, then the fort. | Rope Rat, Harpooner, Gull-rider, Grapnel |
| **Exploder** | round, swollen, glowing cracks | Bursts when it dies and hurts everyone close, crew and monsters. | Hatchguard, Blackpowder, Powder Monkey, Diver, Cooper |
| **Armoured** | huge, crusted in barnacle plates | Takes 12 less damage from every hit, so many small hits do almost nothing. | Anchorman, Harpooner, Boathook, Swivel Gun, Colour Sergeant |
| **Shelled** | carries a ship's bell or shell in front of it | The shell soaks the first 300 damage from the front. Blunt and blast hits break it at once. | Rope Rat, Anchorman, Powder Monkey, Grapnel |
| **Healer** | soft glowing bell-shape floating low, a beam to whoever it mends | Mends the most hurt monster nearby. A fight in front of it never ends. | Rope Rat, Harpooner, Fire-eater, Gull-rider, Grapnel, Storm-caller |
| **Venomous** | covered in long thin spines | Each hit adds a stack of poison. | Hatchguard, Sawbones, Chaplain, Diver |
| **Submerged** | a moving ripple and fin in the sand | Cannot be targeted while under the sand. Surfaces at the first crew member it passes, behind the front line. | Shantyman, Anchorman, Lookout, Diver |
| **Ghostly** | see-through, no feet, pale blue | Blades, shot and cannonballs pass through. Only fire and light hurt it; in lantern light it turns solid. | Blackpowder, Sawbones, Fire-eater, Lookout, Chaplain |

Region 1 teaches Swarm, Flying, Siege, Exploder, Armoured, Shelled and Healer. Venomous, Submerged and Ghostly arrive in regions 2-3.

## Counter table, region 1 (+ strong, · even, − weak)
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

## Region 1: one new idea per stage
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

## Status effects
Poison (stacks to 3, halves healing), Burn (ignores armour and shells), Slow, Stun (3 s immunity after), Shell break, and Solid (light makes ghosts hittable). Each has one colour and one mark.

## Proof planned for part 3
Per stage: win rate with the right loadout, the listed wrong one and random ones. Right must beat wrong by 40 points or more; no loadout wins every stage; every crew member appears in 10-90% of winning loadouts.
