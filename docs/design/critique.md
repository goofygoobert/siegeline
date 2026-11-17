# Critique: why Siegeline reads as an outline

Played on the live build (v0.1-ae17212) at 844×390 landscape, title to boss, with scripted touches.
Screens are in `docs/design/before/` and every point below names the file it is visible in.
**Sound was not heard.** I can only read waveforms and file names, so nothing here judges how it sounds.

Ranked inside each area by how much it hurts.

## 1. Characters and monsters (hurts most)

1. **Every body is the same peg doll.** A box torso, two cylinder legs, two cylinder arms, a ball head.
   Hatchguard, Blackpowder, Shantyman and Sawbones are one figure with a different hat and prop
   (`08-r1s1-battle.png`, HUD cards in `21-r1s5-battle.png`). At battle size the hat is 8 px wide, so the
   crew is told apart by the name label, not the shape. Anchorman is the only one with his own outline.
2. **No faces, no attitude.** Crew faces are two dots and a moustache bar; the cards show a blank ball
   with a hat (`21-r1s5-battle.png`: Anchorman is a bald sphere, Sawbones a grey sphere). Nothing looks
   brave, mean, scared or drunk. Monsters have two glow dots.
3. **Poses are stiff because limbs cannot bend.** Arms are single straight rods from the shoulder. The
   Blackpowder holds his musket with a rod arm (`08-r1s1-battle.png`); the Drowner "claws" by rotating a
   stick. There is no elbow, knee, spine curve, squash or follow-through, so attack and walk look like
   a turnstile.
4. **Flat single-colour fills.** Each part is one colour with a faint band. No cloth folds, wood grain,
   wet shine, stitching or wear. The Barnacle Troll (`21-r1s5-battle.png`) is a teal bean with dots.
5. **Monsters and crew share proportions.** The Drowner is a crew body painted teal with a wedge head.
   The brief says "hunched, lopsided, finned"; on screen they stand as upright as the pirates.
6. **Scale is timid.** Units stand about 65 px tall on a 390 px screen and the beach is 60% empty
   (`06-r1s1-tutorial-aim.png`). Weapons are thin sticks that vanish against the pier.
7. **Death is a fall-over.** Rigid figure rotates 90° and fades. No pieces, no splash, no body left.
8. **Mother Fathom is a cone with a crown** (`23-r1boss-battle.png`). She is barely taller than the hut
   behind her, and her tentacle arm reads as a thin grey tail.

## 2. Backgrounds and the forts

1. **The battle has no stage.** The far layers (sky, lighthouse, clouds) are the best art in the game,
   but the ground the fight happens on is a flat brown strip with dark pebbles and then a black fade
   (`06-r1s1-tutorial-aim.png`). No tide line, no wet sand, no foreground. The beach is the place the
   story is about and it is the emptiest part of the frame.
2. **Mid-ground props are black cut-outs.** Pier, hut, nets, wreck ribs and anchor are near-solid dark
   shapes at the same value (`04-r1s1-tutorial-send.png`). They sit exactly where units fight, so dark
   crew and dark-teal monsters lose their outline against them (`08-r1s1-battle.png`: the Drowner is
   inside the hut silhouette).
3. **The Gullwake is small and not a fort.** A toy boat on grey pebbles, the same height as the hut
   (`04-r1s1-tutorial-send.png`). No crew on deck, no damage you can read, no light. The cannon is a
   yellow tube stuck on the rail and does not look like the thing you aim.
4. **The Drowned Grotto is a googly-eyed fish** (`21-r1s5-battle.png`). The round eyes with white pupils
   are comedic and fight the tone you asked for. It also has more detail and contrast than anything
   else, so it looks like it came from a different game than the units.
5. **Two art styles collide.** Scenery is flat vector-like shapes with soft gradients; characters are
   outlined 3D toys with hard shading. Nothing ties them: no shared light direction on characters, no
   shadows that sit on the ground texture, no colour from the sunset on the figures.
6. **Lighting is a wash.** The sun sets behind the Grotto, so everything should be rim-lit orange from
   the right and cool from the left. Characters are lit from the upper left with white light.
7. **Night cove is a green filter** (`23-r1boss-battle.png`). Same props recoloured; the moon sits behind
   the boss bar and the callout.

## 3. Menus and screens

1. **System UI on top of a game.** Every panel is the same dark navy rounded rectangle with a 1 px
   border and a default sans font (`13-armoury-after-buying.png`, `26-settings-export.png`). It could be
   a banking app. Nothing is wood, rope, brass, canvas or paper. The only authored element is the
   title wordmark.
2. **Quartermaster has no hierarchy** (`13-armoury-after-buying.png`). Three pill tabs; cards that are
   paragraphs of grey stats; a "Next:" line in green and an "Unlocks when…" line in the same green;
   a lock icon floating in space; the Upgrade button the same weight as everything else. You cannot
   see what you own, what is best to buy, or what changed after buying.
3. **Battle HUD is a set of unrelated widgets** (`21-r1s5-battle.png`). Health bars are thin lines in
   the corners with small caps text over clouds; timer, speed and pause are three black circles; the
   powder counter is a grey box floating over the beach; the cannon is a blue circle with a line icon;
   cards are small dark slabs whose portraits are too dark to read; hero and powers are three more
   circles. Six different shapes, none sharing a material.
4. **Cards do not show state.** Affordable and not-affordable differ by a thin gold line
   (`21-r1s5-battle.png`: three of six are lit and it takes a moment to see which). The cost sits in a
   black box over the portrait's chin.
5. **Stage select is circles on a blur** (`03-region.png`). Numbered discs with padlocks over a
   blurred copy of the sky. No path, no place, no sense of travelling along a coast.
6. **Sea chart labels cover the art** (`02-worldmap.png`). Black pills with lock icons sit on top of
   each island; the pins float above them. The chart itself is a pleasant drawing with stair-stepped
   edges.
7. **Results are a list** (`09-r1s1-win.png`, `12-r1s2-loss.png`). "Victory" in a dark box with bullet
   points. The unlock, which is the real reward, is one orange text line. Defeat looks the same as
   victory with different words.
8. **Tutorial is a text box in the middle of the screen** (`04-r1s1-tutorial-send.png`), covering the
   field it is talking about, with no pointer to the control.
9. **Small faults:** build stamp over the title art (`01-title.png`); "Blackpowder" label clipped on its
   card (`08-r1s1-battle.png`); settings sheet cut off at the bottom (`26-settings-export.png`).

## 4. Gameplay feel

1. **Nothing has weight.** A 90-damage cannonball produces a small orange triangle fire and pale
   numbers (`08-r1s1-battle.png`). No recoil on the fort, no flash, no crater, no bodies thrown. Melee
   hits are a number popping up.
2. **The cannon, your one hands-on verb, is hidden.** You aim by dragging a HUD button while the
   camera is usually away from the Gullwake (`08-r1s1-battle.png`: fort not on screen). You never see
   the gun you fire.
3. **Few decisions per minute.** Stage 1 is: tap Hatchguard when 50 powder, tap Blackpowder when 80,
   fire the cannon whenever it is ready. Powder trickles in, so most of the time you wait. The test
   player wins with no positioning or timing choices.
4. **Units arrive from nowhere.** A sent unit appears at the fort edge with no door, shout or puff.
   Monsters walk out of the grotto mouth with no warning of what is coming next.
5. **Victory and defeat have no moment.** The enemy base goes grey with a smoke column and a panel
   appears at once (`09-r1s1-win.png`). No slow-down, no cheer, no collapse you watch.
6. **Stalemate in the middle.** Fights settle into two clumps trading numbers at one spot
   (`21-r1s5-battle.png`). There is no knock-back, no push, no line that visibly advances or breaks.
7. **Damage numbers carry the feedback.** Because the sprites barely react, the only proof of a hit
   is floating text, and it is pale yellow on a yellow sky.

## What this adds up to

The game is built like a spec sheet: every required thing exists once, at the same size, in the same
box. A finished game makes a few things big and lets the rest be quiet. The slice should make four
things big: **the silhouette of each fighter, the beach they fight on, the cannon in your hand, and the
moment something dies.**
