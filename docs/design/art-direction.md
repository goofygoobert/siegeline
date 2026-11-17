# Art direction: Tales of the Brine

The standard every asset is held to. Helpers building art get this file and one narrow brief.
World facts (names, cast) stay in `docs/world-pirates.md`. Technical formats stay in `docs/asset-contract.md`.

## The one idea

**The crew faces the light. The monsters walk out of it.**

The sun sets behind the Drowned Grotto, on the right. Crew look right, so their faces and fronts are
lit warm and you can read their colours. Monsters look left with the sun at their backs, so they are
dark, cool shapes with an orange edge and their own green glow. Side is readable from light alone,
before colour or shape. Every sprite, prop and screen follows from this.

## Look: carved and painted ship's figures

Characters look like painted wooden carvings come to life: the figureheads and tavern signs of a
harbour town. Chunky, hand-cut, slightly asymmetric, with paint that has worn at the edges. This
keeps what was good about the toy figures (bold, readable, cheap to animate) and drops what was bad
(identical bodies, no joints, no faces).

- **Not** smooth plastic, not pixel art, not realistic. No borrowed pirate-film or game designs.
- Gruesome through wetness, rot and ink, never through gore on the crew.

## Shape language

| | Crew | Monsters |
|---|---|---|
| Base shapes | squares, barrels, wedges that stand on a wide base | hooks, drips, crescents that hang forward |
| Posture | upright or leaning back on the heels, chest out | hunched, head ahead of the feet, one side lower |
| Symmetry | near-symmetric, one worn detail | lopsided: one big arm, one small |
| Ends | blunt: boots, fists, hat brims | sharp or trailing: claws, kelp, fins, drips |
| Head | 1/3 of body height, big hat or hair shape | sunk between the shoulders, no neck |

Proportions: 3 heads tall. Hands and feet oversized (a fist is half a head). The weapon or signature
prop is at least as long as the torso and breaks the outline.

**Silhouette test:** filled black at 40 px tall, each unit must be named by someone who knows the
cast. Each unit gets one silhouette hook nobody else has:
Hatchguard = door-sized square shield; Blackpowder = long diagonal musket and tricorn points;
Rope Rat = low forward lean and two knives; Shantyman = wide squeezebox; Anchorman = anchor overhead;
Sawbones = lantern on a pole; Captain = coat tails and plume. Drowner = hanging claw arms and kelp
hair; Scuttler = flat and wide with one raised claw; Inkspitter = tall bulb head; Pufferghast = spiky
ball; Barnacle Troll = hump higher than head; Kelpie = rearing horse neck; Mother Fathom = lure light
above a cloak triangle, three crew tall.

## Build (Blender, from code)

Decision changed from the first night: figures are no longer one rigid box per limb.

- **Segments are lofted, not primitives.** Each body part is a loft through oval cross-sections, so a
  thigh tapers, a chest barrels, a belly hangs. Carved facets come from a low segment count plus a
  light bevel, shaded flat on big planes.
- **Limbs have two bones** (upper and lower arm, thigh and shin) plus hand and foot. The spine is
  three parts: hips, chest, head. Joints overlap with a ball so no gap opens when they bend.
- **Faces are built:** brow ridge, nose, eye whites with pupils, mouth that changes shape by action
  (set jaw, open shout, grimace). Crew eyes look where they are going. Monster eyes are glow only.
- **Loose bits lag behind.** Bandana tails, coat tails, kelp, rags and sashes are short chains that
  trail the body by a few frames.
- Camera stays fixed and orthographic for the whole cast so scale is consistent.

## Animation

10 fps drawn on twos would look cheap; we render at 12 fps and the engine blends nothing.

- **Idle** (8 frames): breathing through the chest, weight shift, one fidget unique to the unit.
- **Walk** (8): the body bobs and leans into the step; arms counter-swing; props bounce late.
- **Attack** (8–10): anticipation (2 frames back) → strike (1–2 frames, the fastest in the cycle,
  with a stretched pose and a swipe arc) → hold on impact → recover. The `hit` frame is the strike.
- **Hit** (4): squash away from the blow, head snaps, then spring back.
- **Die** (10): crew stagger and drop their prop, ending as a body on the sand. Monsters come apart
  wetly: they slump into a puddle of kelp and ink that the engine leaves on the beach for a while.

## Colour

Scene palette (sunset cove):

| Role | Hex |
|---|---|
| Sky top / mid / horizon | `#3b2a5c` / `#b4476a` / `#ffb45e` |
| Sun and sun-streak on water | `#ffe2a0` |
| Sea | `#5a3d6e` to `#27213f` |
| Dry sand / wet sand | `#c79a6b` / `#7a5a5e` |
| Far land | `#6b4a78` |
| Mid props (pier, hut, wreck) | `#4a3558`, never darker than this in the fight band |
| Foreground silhouettes | `#1b1426` |

Crew: navy `#27456e`, sea-red `#c23a2e`, canvas `#eadfc4`, brass `#e0a93b`, skin tones varied per
unit, tar `#2a2420`. Saturated and warm, lit side pushed toward yellow, shadow side toward plum.

Monsters: drowned teal `#2f5a5c`, deep `#17303a`, bone `#d8cfb5` (small amounts), ink `#3a1e4a`,
glow `#7dffa8` (eyes, cracks, drips only). Low saturation except the glow.

Value rule in the fight band (the strip from head height to feet): background sits in the middle
values, crew are the lightest things, monsters the darkest, glow the brightest small points. Nothing
in the mid layer may be darker than a monster or lighter than a crew face.

## Lighting

- **Key:** warm sunset `#ffc27a` from the right, low (20° above the horizon), slightly toward camera.
- **Fill:** cool plum `#6a5a9a` from the upper left, about a third of the key.
- **Rim:** orange edge on anything facing away from the sun (all monsters, the back of the fort).
- Shading is three bands with a soft break, and shadows shift hue toward plum, not toward black.
- Every figure gets a soft contact shadow stretched to the left, away from the sun.
- Night cove: the moon replaces the sun at the same place. Key turns green-white `#bfffd0`, fill deep
  teal, lanterns on the fort and pier become the warm accents. Same rule, new colours.

## Line

- Outer contour: one heavy dark line around the whole figure, 2.5 px at phone size, so figures read
  like stickers against any background. Crew ink is plum-black `#22152b`; monster ink is `#0c1a1e`.
- Inner lines: thin, only where parts overlap. No line on painted details.
- Scenery has no lines. That is what separates fighters from the stage.

## Readability at 40 px

- A unit is drawn about 100 px tall on a 390 px-high phone screen (a quarter of the height). 40 px
  is the worst case (far zoom, HUD portrait) and must still pass the silhouette test.
- At most three colour areas visible at 40 px: body, accent, prop.
- Faces read as one dark brow shape plus a light eye spot, nothing finer.
- Health pips sit above the head only when damaged.

## The stage

- **Beach (near layer):** dry sand at the fort, wet reflective sand through the middle, a foam line,
  shallow water toward the grotto. The sun streak crosses the wet sand. Details are low contrast and
  sparse: shells, kelp, footprints, a half-buried keg.
- **Mid layer:** pier, hut, nets and wreck ribs pushed back by haze: lighter and lower-contrast than
  now, and placed above head height or between fight zones, never as a black slab behind fighters.
- **Foreground layer (new, parallax 1.25):** a few dark, soft shapes at the bottom corners (rope
  post, grass, a gull on a pile) that frame the beach and hide the plain strip under the HUD.
- **The Gullwake:** a wrecked galleon bow-up on rocks, as tall as two-thirds of the screen. Stern
  lantern lit, patched sails, a gun deck with Long Tom in an obvious cradle on the bow, a gangplank
  the crew come down. Three damage states that change the outline (mast snaps, hull opens, fire).
- **Long Tom:** a fat brass-banded iron cannon, the biggest metal object in the game. Separate
  sprite so it tilts, recoils and flashes.
- **The Drowned Grotto:** a sea cave whose mouth is the jaw of something long dead: whale-bone
  arches and coral teeth, kelp curtains, green light and mist from inside. No eyes. It should feel
  like a place, and it must be the darkest large shape on screen with the brightest glow inside it.

## Screens

Materials: tarred wood, brass, rope, sailcloth and chart paper. Navy stays as the night-sky backing.

- **Type:** a heavy condensed slab-style display face for titles and numbers, set tight and in caps;
  the system text face for reading. Display type is drawn by us (letter shapes from system fonts with
  our own treatment: brass fill, dark bevel, drop shadow), so no font licence is involved.
- **Hierarchy:** one loud thing per screen. In battle it is the field. In the Quartermaster it is the
  item you can afford next.
- **Spacing:** 4 px base; gaps of 8, 12, 16, 24. Touch targets at least 44 pt.
- **Motion:** 120–200 ms, ease-out, things come from where they were triggered. Coins fly to the
  purse, cards lift when affordable, bars drain with a lighter trail. Reduced-motion turns slides
  into fades.
- **Colour in UI:** brass `#e9a23b` means "you can act". Green means health only. Red means danger
  only. Locked things are desaturated, not hidden.

## Sound (direction only; not heard by me)

Each event gets a cue with a low thump for weight and a top click for clarity. The cannon is the
loudest sound in the game. The owner must listen and confirm; until then sound is marked unverified.
