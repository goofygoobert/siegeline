# World: Tales of the Brine (pirates vs. monsters of sea folklore)

Replaces The Ashen Marches (kept as git tag `ashen-marches-v1`). The mechanics, balance and data ids stay the same; names, looks, sounds and places change. Internal ids (e.g. `ashguard`) stay as they are, so code, saves and atlases keep working. Only the display names and art change.

**Tone:** a rollicking but spooky pirate tale. Lantern-lit coves, sea-fog, moonlight on black water, old sailors' superstitions come true. Some menace and a little gore (ink, slime, splintered wood, a bit of blood), but not horror. Original names only: nothing from existing pirate films or games. Folklore creatures (kraken, sea hag, kelpie, selkie, will-o'-wisp, troll, mermaid) are public domain; our versions must be our own designs.

**Premise:** the cursed tide has turned. When the moon went green over Saltwick Cove, everything the sea had swallowed came crawling back up the beach. The crew of the *Gullwake* (a galleon wrecked on the rocks and rebuilt into a fort) is all that stands between the monsters and the harbour town.

## Player faction: the Gullwake Crew (pirates)
Look: weathered sailors, striped shirts, sashes, bandanas, tricorns, brass buttons and buckles, rope, patched coats. **Palette:** deep navy (~#1f3a5a), sea-red sashes (~#b0302a), sun-bleached canvas (~#e8dcc0), brass (~#d4a23a), tar-black (~#2a2420), warm lantern glow (~#ffb347). Upright, sturdy, square shapes, faces right.

| id | Display name | Role | Look |
|---|---|---|---|
| ashguard | **Hatchguard** | front line | burly deckhand holding a ship's hatch door as a shield, short cutlass, bandana |
| torchbow | **Blackpowder** | ranged, sets on fire | musketeer with a long flintlock, tricorn, powder horn; shots trail sparks |
| cinder_runner | **Rope Rat** | fast | wiry cabin hand, bare feet, striped shirt, a knife in each hand, leaning run |
| bellringer | **Shantyman** | support, slows monsters | big singer with a squeezebox (accordion) whose sea-shanty slows monsters |
| maulwright | **Anchorman** | heavy | huge sailor swinging a ship's anchor on a chain |
| lamplighter | **Sawbones** | healer | ship's surgeon with a lantern and a bottle of grog, apron, spectacles |
| hero: marshal | **Captain Rook Halloran** | hero | long coat, big feathered tricorn, cutlass + flintlock pistol; special: fires a **flare pistol** (the "Flare" stun) |
| level 5 / 10 looks | | | t2: extra gear (leather jerkin, bracers, hat with a feather); t3: gold trim, coins and a glowing green-gold "cursed treasure" weapon |

## Enemies: the Deep (sea-folklore monsters), faces left
Look: wet, slimy, barnacled, kelp-draped. Hunched and lopsided, with tentacles, fins and claws. **Palette:** drowned green-grey (~#4a6a5e), deep teal (~#1e4a4e), bone/shell (~#d8cfb5), **sickly green glow** in the eyes and cracks (~#7dff9a), ink-purple (~#3a1e4a). Never colour alone: the monsters are hunched, finned and tentacled, while the crew is upright and square.

| id | Display name | Behaviour | Look |
|---|---|---|---|
| husk | **Drowner** | basic | a drowned sailor come back: grey-green, kelp hair, barnacles, glowing eyes, claw hands |
| gnawer | **Scuttler** | fast crawler | dog-sized crab-thing with too many legs and a snapping claw |
| spitter | **Inkspitter** | lobs ink from the back | squid-headed creature with a bulging throat sac; lobs glowing ink |
| bloater | **Pufferghast** | bursts when killed | swollen spiny puffer-fish monster on stubby legs, glowing green cracks |
| brute | **Barnacle Troll** | big brute | hulking sea troll crusted in barnacles and coral, driftwood club |
| husk_warden | **The Kelpie** (mini-boss) | enrages | a ghastly water-horse rearing on its hind legs, kelp mane, glowing eyes (can stay humanoid-on-hind-legs to fit the rig) |
| cinder_matron | **Mother Fathom** (boss) | sweep, summon, ink spit | a towering sea hag: hunched old crone in rotted sailcloth, fish-scale skin, crown of coral and whale bone, a **tentacle arm** for the sweep, lantern-fish lure glowing over her head. Summons Scuttlers; spits a huge ink bomb |

## Places and objects
| Old | New |
|---|---|
| Lantern Keep | **The Gullwake** (wrecked galleon fort on the rocks; bow on the beach, crow's nest and a big lantern) |
| Maw Gate | **The Drowned Grotto** (sea cave shaped like a gaping fish/skull mouth of coral and bone, green glow inside) |
| Beacon Ballista | **Long Tom**, the fort's great cannon: fires **flaming cannonballs** that splash burning tar |
| Embers (energy) | **Powder** (gunpowder kegs) |
| Marks (currency) | **Doubloons** |
| Ember Rain | **Broadside** (a volley of cannonballs from the ships in the bay) |
| Rally Bell | **Sea Shanty** (the whole crew sings: faster, harder, heals) |
| Region r1 Cinderfold Vale | **Saltwick Cove** (sunset harbour cove, rocks, wrecks, a lighthouse) |
| r2 The Bell Marshes | **The Fogbanks** (will-o'-wisps, ghost lights) |
| r3 Gilded Causeway | **The Cutthroat Isles** (the Drowned Fleet: ghost pirates) |
| r4 Hollowdeep Mines | **Sunken Bell Reef** (merfolk and selkies) |
| r5 The Ember Wastes | **Leviathan's Reach** (sea serpents) |
| r6 The Cinder Maw | **The Maelstrom** (the great whirlpool; final boss: the Kraken) |
| Boss night (r1n) | the cove under a **green moon** |

## Stage names (region 1)
1 *Tide Turns Green* · 2 *The Smugglers' Steps* · 3 *Pufferghast Shoals* · 4 *The Broken Lighthouse* · 5 *Wreckers' Reef* · Boss *Mother Fathom*

## Sound
Same ids. New feel: shanty-ish (fiddle/accordion-like synth, stomps and claps, low brass), creaking wood and sea ambience. Cannon booms for the castle weapon and Broadside, a ship's bell, splashes, squelches and shell-cracks for monster hits and deaths, deep whale-like moans for the boss.
