# Art direction: Tales of the Brine (version 2)

Rewritten after the owner's verdict on the first redesign: the frame improved and the art did not. This version is
organised around one question: **can you read it on a phone held at arm's length?** World facts stay in
`docs/world-pirates.md`; file formats in `docs/asset-contract.md`; helpers also get `docs/design/helper-brief.md`.

## The five tests every battle frame must pass

1. **Squint test.** Blur the screenshot until text is unreadable. You must still count the fighters and tell which
   side each is on.
2. **Thumbnail test.** At 160 px wide the frame still shows two forts, a beach and who is winning.
3. **Line-up test.** Each crew member, filled black at 60 px tall, is named correctly by someone who knows the cast.
4. **Night test.** The same three tests pass on the night stage.
5. **Still test.** A paused frame never looks frozen by accident: something in it implies motion (a pose mid-swing, a
   wave lip, a leaning mast).

## Size

- A standing crew member is **a quarter of the screen height** (about 100 points on a 390-point-high phone). The old
  figures were a sixth.
- The whole beach, both forts included, fits in **about one screen and a fifth**. The Gullwake is on screen in every
  frame of every battle. (The field was 2.2 screens wide; you could not see your own fort.)
- Heads are a third of the figure. The face is the largest light shape on a crew member.
- Sprites are packed so one sprite pixel is one screen pixel at that size. Nothing is scaled up.

## Value: three bands, never mixed

| Band | What lives there | Rule |
|---|---|---|
| Light | crew faces, shirts, the cannon flash, foam | nothing in the background is this light inside the fight band |
| Middle | sky, sea, sand, pier, haze | the background lives here, low contrast, no pure dark and no pure light behind fighters |
| Dark | monsters' bodies, the Grotto, the foreground, the ink line | monsters are dark but carry their own light (below) |

The fight band is the strip from head height to the feet. Mid-ground props that cross it are pushed back with haze
until they sit in the middle band.

## Edges: how a figure separates from what is behind it

Every figure has all three, always:

1. **Ink contour.** A heavy dark line round the whole figure (2 px at phone size), added when packing so its weight
   never varies.
2. **Rim light.** The side away from the camera and toward the sun carries a hot orange edge. On monsters it runs down
   the whole back, because the sun is behind them.
3. **Halo for monsters.** Outside the ink, a thin sick-green glow. A dark monster against a dark Grotto or a night sky
   still has a bright outline. Crew never have a halo.

And on the ground:

4. **Two shadows.** A tight dark contact shadow under the feet and a long soft one thrown away from the sun. A figure
   without a shadow floats.

## Faces and attitude

- Eyes are big enough to see at game size: whites a quarter of the head wide, dark pupils, one heavy brow that tilts
  (down to attack, up when hit).
- Mouths change shape: set, shouting, grimacing.
- Every character has an attitude you could name in one word (stubborn, sly, jolly, grim, fussy, hungry). The idle
  pose shows it.
- Monsters' faces are a pale skull-shape or a glow, with large glowing eyes. Never a dark face on a dark body: that
  was the first Drowner's fault.

## Animation

Rendered at 12 frames a second or more. Every action has three beats, and the first is the one amateurs skip:

1. **Anticipation**: the body moves the wrong way first (lean back before the swing, squash before the jump) and
   **holds** for two frames.
2. **Action**: one or two frames, the fastest in the cycle, with the body stretched along the line of motion and a
   smear (swipe arc, muzzle flash).
3. **Settle**: overshoot, then return. Loose things (bandana tails, coat tails, kelp, rags) arrive late.

Idle is never still: breathing through the chest, a weight shift, one fidget. Walks bob and lean. Hits squash away
from the blow. Deaths have a stagger before the fall; monsters melt into a puddle that stays on the sand.

## The rig

Figures are built in Blender from code with `art/blender/kit2.py`: lofted body parts, two-bone limbs, a three-part
spine, built faces, chains for cloth and kelp, per-frame squash and stretch on the root. The first rigid rig (one box
per limb, no elbows, no faces) is retired and must not be used for anything new. If a character needs something the
kit cannot do (a tentacle, a horse neck), build that part as its own jointed chain in the character's file.

## The battlefield

Back to front, and what each layer is for:

| Layer | Content | Moves | Purpose |
|---|---|---|---|
| Sky | gradient, sun or moon, clouds | no | mood and the light direction |
| Far | sea, islands, lighthouse, ships | slowly | depth |
| Water | glints that twinkle, a wash that slides up the sand and back, a foam lip | always | the still test; it is a shore |
| Haze 1 | warm air between far and mid | – | pushes the far shore back |
| Mid | pier, hut, nets, wreck | with the camera | place |
| Haze 2 | mist at the foot of the mid-ground | – | lifts the fight band into the middle values |
| Beach | dry sand at the fort, wet sand mirroring the sky, tide marks, shells, kelp, footprints | with the camera | where the fight is |
| Forts | the Gullwake on the left, always in view; the Drowned Grotto on the right | – | whose side is whose |
| Fighters | crew, monsters, shadows, effects | – | the subject |
| Foreground | dune grass, mooring posts and rope, dark and soft | faster than the beach | frames the bottom edge, sells depth |

**Night.** The sky and sea go dark green; the beach stays in the middle band, lit by the moon. Characters are **not**
washed with the night colour: they keep their own colours with a light cool grade, crew stand in pools of warm lantern
light, and monsters' halos and eyes do the rest. A night frame must pass the same squint test as a day frame.

**The Gullwake** is a wrecked galleon bow-up on rocks, a third of the screen wide, with Long Tom on the bow. It shows
damage in three steps that change its outline. It needs a re-model with crew on deck and a gangplank (open).

## Interface

- **Palette.** Surfaces are deep sea-ink (`#0e1b29` to `#18304a`). Content sits on chart paper (`#f5ead0`) with dark
  ink text. Text contrast is at least 7:1 on paper and on ink.
- **One accent.** Orange-gold `#ffab1c` means "you can press this" and is used for nothing else: primary buttons,
  ready cards, the cannon ring when loaded. Green is health. Red is danger and "cannot afford". Violet is the enemy's
  health.
- **Type.** The display face (engraved capitals) is for screen titles and the big battle callouts only. Every label,
  number and button is the system sans, bold, 13 px or larger, in sentence case.
- **Crew cards** are 82 × 108 points: the portrait fills the card so a crew member is recognised by picture alone.
  Three states, told apart by more than colour:
  - *Ready*: full colour, lifted, orange ring.
  - *Cooling down*: dark shade over the portrait with the seconds left in large numerals.
  - *Cannot afford*: portrait dimmed, cost in red, and a bar filling toward the cost.
- **Damage feedback is merged and ranked, never stacked.** A cannon blast shows **one** headline: the total, with
  "Direct hit!" and the kill count on the same line. Ordinary blows show a spark and the health pip, no number. Only a
  single heavy blow (40 or more) gets its own number. A new headline replaces the old one.
- **Callouts never cover the fight.** Warnings are a small red pill under the top bars. The large centre callout is
  for the start and end of a battle only.
- **Destructive actions sit apart** from ordinary ones (Reset progress is a separate link below Export and Import).
- **Nothing over the art that is not needed to play**: the version line lives in Settings.

## What "finished" means for one asset

A sprite is finished when it has: a silhouette hook named in its file, a readable face, contour + rim (+ halo for
monsters), all animations with the three beats, no part poking through another in any frame, clean edges on dark,
light and magenta backgrounds at 1x and 3x, and it has been looked at in a real battle frame at phone size, day and
night.

## Sound (direction only; not heard by me)

Each event gets a low thump for weight and a top click for clarity; the cannon is the loudest sound in the game. The
owner must listen and confirm. Until then sound is unverified.
