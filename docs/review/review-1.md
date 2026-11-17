# Siegeline: playtest review 1

Fresh player, phone landscape. Sources: `docs/shots/playthrough` (pt), `docs/shots/se`, `docs/shots/notch`, `docs/review/rec_*`.

## Blocker

1. **Battle HUD draws over the result modal.** Where: Victory, pt/21, pt/23. The cost tags from the card row ("50", "80", "40") sit on top of the Next stage and Retry buttons, so a player can't read them and may mis-tap. Fix: give the result overlay its own top layer above the whole HUD (or hide the HUD row while it shows), and block pointer events underneath.
2. **Victory buttons are cut off.** Where: pt/07, 13, 19, 21. When the "Unlocked: …" line appears, Next stage / Retry / Map run past the bottom of the modal and are clipped by about a third. Fix: shrink the stars and title on short screens, or put the unlock line in a compact chip, so the modal fits in 390 px. The buttons must always be fully visible.

## Major

3. **Stage sheet hides content.** Where: region sheet, pt/03, se/03, notch/03. The "First clear … 120" reward is cut in half behind Fight, and on SE the third star goal is gone completely. Nothing shows that the sheet scrolls. The sheet is also see-through, so the header's Armoury button and coin count, plus the locked stage nodes, ghost through it. Fix: make the sheet opaque, size the content to fit (two-column stars and reward), and pin Fight below the content rather than over it.
4. **Settings overflows.** Where: pt/27, se/05. The "Settings" title and close button press against the top edge, and on SE the Export / Import / Reset buttons are below the fold with no scroll cue. In pt/28 the error toast covers the Import and Choose file buttons. Fix: give the header a fixed height inside a scroll body, and raise the toast above the sheet or show the error inline under the textarea.
5. **Old scenes show behind later screens.** Where: pt/11 and 17 (Armoury reached from a loss) show the fallen keep, smoke and a horde through translucent cards, which makes the locked rows unreadable. pt/26 (map after the boss) shows the keep and night sky around the map frame. Fix: tear down or fully cover the battle canvas when leaving a battle, and give those screens a solid background, as se/04 already does.
6. **Clearing the region unlocks nothing visibly.** Where: pt/25 → pt/26. The primary button reads "Region cleared", which is a label, not an action. The map then looks exactly as it did before, with The Bell Marshes still grey and no message. A new player will think the game is over or broken. Fix: rename the button "Continue"; on the map, animate the path to the next region and show a "New region unlocked" or "More regions coming" message.
7. **Hits read as white blobs.** Where: pt/12, 20, 22, rec_06–13 (boss). The hit flash turns whole sprites, and the boss, solid white for many frames. In a crowd the fight becomes a white smear, and damage numbers stack into nonsense ("2246", "1245 45", "15 15 15"). Fix: flash for about 60 ms at about 60% tint, merge damage numbers per target within 150 ms, and offset stacked numbers sideways.
8. **Unit cards are hard to tell apart.** Where: the card row in every battle shot. Cards have no names, and when you can't afford one it becomes a grey silhouette. Torchbow and Bellringer have almost the same red-haired portrait (see notch/04). The tutorial says "Tap the Ashguard card" but no card says Ashguard. Fix: put a short name or role icon on each card, give each unit a distinct colour or prop, and keep unaffordable cards in colour, just dimmed.
9. **Boss fight is a long grind.** Where: rec_05–13 (about 3.5 min, bar moves slowly), pt/24. Units walk into the Matron and die in a loop. There is no visible telegraph or phase change, and the boss bar is clipped by the boss's own crown (pt/24). Fix: cut boss HP about 30% or add a clear damage window. Make the red warning zones and the phase-2 change obvious. Move the boss bar under the top HUD row, clear of the sprite.

## Minor

10. **Dead opening on stage 3.** Where: rec_00–01. For about 13 s the screen is empty: the camera pans away from the keep and no enemy appears. Fix: spawn the first wave at 2–3 s, or keep the camera on the keep until contact.
11. **The tutorial points at a card you can't afford.** Where: pt/04. At 46 of 50 embers the Ashguard card is grey while the tip says to tap it. Fix: start the tutorial at 50+ embers, or hold the tip until the card lights up. The "DEFEND THE KEEP" banner also shows through behind the tip box, so sequence the two.
12. **Time star never earned.** Where: pt/07, 13, 19, 21, 23, 25. The time star was missed on every stage, often by 5–20 s, and stage 1's 1:50 includes tutorial pauses. Fix: loosen par times by about 15%, and don't count time while a tutorial prompt is up.
13. **Same loss tip for different stages.** Where: pt/10, pt/16. Both show the identical Spitters tip, but stage 3's threat is bloaters. The loss screen also doesn't say why you lost. Fix: pick the tip per stage and per what killed you, and add one line such as "Gate at 96 HP. So close!" (pt/10 lost at 96).
14. **Coin pill covers the enemy HP label.** Where: pt/07, 10, 25 ("MAW GATE · SEALED"). Fix: place the pill below the HUD, or hide the HUD labels under the modal.
15. **Small-screen HUD issues on SE.** Where: se/06–09. "LANTERN KEEP" wraps to two lines, and the ember meter sits over the battlefield where units walk behind it (se/08). Fix: shorten the label to "KEEP" under 700 px, and anchor the meter in the bottom bar.
16. **Right-side buttons crowd the gate.** Where: pt/20, 22, 24. With two powers and the hero, the round buttons stack upward over the Maw Gate. Fix: put them all in one bottom row, and drop a card column if needed.
17. **Locked items don't say how to unlock them.** Where: Armoury, pt/11, notch/04. Locked rows show "Next: …" upgrade stats. Fix: replace that with "Unlocks after Stage 3".

## Polish

18. Title screen (pt/01): the tagline runs over the tower art, so put a soft scrim behind it. The version text sits on lava cracks.
19. Map (pt/02): the terrain looks pixelated, with stair-step edges. Locked regions have no lock icon.
20. "+ 150  marks" has double spaces. "Under 1:50 (you: 1:56)" would read better as "Win under 1:50 — you took 1:56".
21. Stage stars under the nodes (pt/03) are dark grey on brown and nearly invisible.
22. Recording (rec_00): picking the Stage 1 sheet then loaded "Pyre Fields" (Stage 3). Check that the selected stage is the one that launches, or whether this came from a debug jump.

## What works

The art direction is strong and consistent: the ash-red sky, the chunky Wardens against the spiky Hollows, and the Maw Gate with its skull. The tutorial copy is short and clear. Loss → Upgrade → Retry is a good loop. The save-repair and bad-import messages are clear and kind. The boss intro ("THE MATRON RISES", night sky) has a real sense of occasion.
