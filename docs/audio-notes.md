# Audio notes (Siegeline / The Gullwake: pirates vs. the Deep)

All sound effects and music are our own work. They were synthesised from scratch in Python
(numpy/scipy) by the scripts in `tools/audio/`. No samples, loops or downloaded sounds were used.
All melodies are original. None of them quotes or imitates a known pirate film theme or a
traditional shanty tune.

**Re-theme (2026-11-17).** The audio was remade for the pirate world in `docs/world-pirates.md`.
The ids, file format and manifest format are unchanged. The UI sounds, `hit_blade` (cutlass),
`hit_blunt` (anchor), `star` and `heal` still fit and were kept as they were. Every other id
was remade. `warden_die` is the player's crew death; the Kelpie and every other monster use `hollow_die`.

## Pipeline

| Step | Tool |
|---|---|
| DSP toolkit: oscillators (polyBLEP saw/square), filters, envelopes, synthetic hall IR, circular reverb | `tools/audio/synth.py` |
| Instruments: brass, strings, staccato low strings, formant choir, bells, Karplus-Strong pluck, taiko, frame drum, snares, hats, cymbals, boom, flute, drone | `tools/audio/instruments.py` |
| Sea/shanty kit: accordion (2–3 detuned narrow-pulse reeds with musette beating and reed-body resonances), fiddle (saw, bow noise and violin-body resonances, delayed vibrato), deck stomp, crew clap, wordless crew shout ("hey!"/"oh!" vowel barks, formant-filtered), whale moan (gliding tonal moan with a formant growl), wave wash, wood/rope creak (stick-slip pulses through wood resonances), splash, fizz, squelch, wood crack, black-powder cannon, bosun's whistle | `tools/audio/instruments.py` |
| 33 sound effects | `tools/audio/sfx.py` |
| 6 music cues | `tools/audio/music.py` |
| Writes `manifest.json` and runs the checks on the decoded AAC | `tools/audio/check.py` |
| Reports spectral balance, stereo width and level over time | `tools/audio/analyse.py` |
| Spectrogram PNG for visual sanity checks | `tools/audio/spectro.py` |

To rebuild everything (about 2 minutes on the Jetson, one process at a time):

```
.venv/bin/pip install numpy scipy av
.venv/bin/python tools/audio/sfx.py
.venv/bin/python tools/audio/music.py
.venv/bin/python tools/audio/check.py
```

**Encoder.** The system ffmpeg on the Jetson is built without AAC, so it can neither encode nor
decode it. Encoding and decoding go through PyAV (`av`), which bundles its own FFmpeg and uses the
native `aac` encoder. Output is an `.m4a` (ipod/mp4) container at 44.1 kHz:

- SFX: mono, 96 kbps.
- Music: stereo, 88 kbps. This is slightly under the ~96 kbps in the brief, chosen so the total
  stays under the 3 MB budget. At 96 kbps the total was 3.19 MB.

Intermediate WAVs and the JSON check report live in `tools/audio/wav/`, which is gitignored.

**Atomic writes.** Each `.m4a` is encoded to a hidden temp file (`.<id>.tmp.m4a`) in
`public/assets/audio/`. The temp file is decoded and checked, and only then renamed into place
with `os.replace`. `manifest.json` and the intermediate WAVs are written the same way. A running
game never reads a half-written file.

**Loudness.**

- **SFX:** each sound is low-passed at 15 kHz and high-passed at 25 Hz. It is then normalised to
  a 300 ms short-term RMS of -12 dBFS. A soft peak limiter applies at most 7 dB of gain reduction.
- **AAC overshoot:** AAC reconstruction can push peaks above the source, by up to +3 dB on sharp
  transients. `encode_safe` therefore encodes the file, decodes it, measures the peak and lowers
  the gain until the decoded peak is at or below -1.3 dBFS.
- **Manifest `vol`:** final balance comes from `vol` in the manifest:
  - UI: 0.5–0.6
  - Small hits and arrows: 0.45–0.6
  - Ballista and castle: 0.7–0.9
  - Boss: 0.8–0.9
  - Outcome stings: 0.75–0.8
- **Music:** RMS is set to between -16 dBFS (battle, boss) and -19.5 dBFS (menu, map). A
  stereo-linked limiter peaks at -2 dBFS. The music `vol` values are 0.45–0.6.

## Loops

Loops are rendered so that the end flows straight into the start:

- **Circular render.** Each loop is rendered into a circular buffer. Notes, reverb tails and the
  convolution reverb wrap from the end of the buffer back onto its head. The reverb uses an FFT
  circular convolution.
- **Seamless filters.** The IIR stages are the high-pass, the low shelf, the presence lift and
  the limiter. They run over [warm-up copy of the tail + loop], so they are seamless too.
- **File layout.** Each shipped file is laid out as follows:
  1. One beat of pre-roll: the loop's own last beat, faded in over 30 ms. It works as a pickup,
     and it means the first play starts from silence with no click.
  2. The loop.
  3. 0.5 s of the loop head, as padding against AAC end padding.
- **Loop points.** `loopStart` and `loopEnd` in the manifest bracket the loop exactly. The engine
  should play with `loop = true` and those points, starting from 0 or from `loopStart`.
- **Encoder delay.** The mp4 edit list compensates for the AAC priming delay of 1024 samples.
  `check.py` verifies this:
  - The decoded length equals the rendered length.
  - The decoded and rendered audio line up with a cross-correlation offset of 0 samples.
  - Decoders that respect edit lists include Safari, Chrome and FFmpeg.

| id | loopStart (s) | loopEnd (s) | loop length | tempo / bars |
|---|---|---|---|---|
| menu | 0.937506 | 45.937506 | 45.000 s | 6/8, dotted quarter = 64, 24 bars (pre-roll is one dotted quarter) |
| map | 0.500000 | 48.500000 | 48.000 s | 3/4, 120 bpm, 32 bars |
| battle | 0.434785 | 56.086961 | 55.652 s | 4/4, 138 bpm, 32 bars |
| boss | 0.476190 | 61.428571 | 60.952 s | 4/4, 126 bpm, 32 bars |

## Checks (listen-check proxy), all passing

`check.py` decodes every shipped `.m4a` and checks the following:

- **Peak:** at or below -1 dBFS. The actual range is -1.3 to -6.4 dBFS.
- **DC offset:** under 0.005. The actual maximum is 0.0045, a mean offset on the shortest UI clicks rather than true DC; everything is high-passed at 25 Hz.
- **Not silent:** RMS above -45 dBFS.
- **Length:** decoded length equals rendered length, with a decode/render offset of 0 samples.
- **Loop seams:**
  - The jump from sample `loopEnd-1` to sample `loopStart` is smaller than the loop's own
    99.9th-percentile sample-to-sample step. For example, battle is 0.052 against 0.188.
  - Energy above 6 kHz in a 10 ms window across the played seam is no higher than in the rendered
    source at that point (−2.2 to −7.3 dB), so the seam adds no click.
  - The decoded post-pad matches the decoded head to within normal AAC coding error
    (about −13 to −15 dB; −9.7 dB for map, whose loop head is quiet).
  - The first sample is about 0, so playback starts without a click.

**Phone speakers.** Battle and boss are kept audible on phone speakers:

- Stomps and taiko are tuned to 78–92 Hz, with board-knock and slap layers at 250–1600 Hz.
- The music is high-passed at 45–50 Hz, with a −3 dB low shelf below 150 Hz and a parallel
  presence lift above 2 kHz.
- The lead bus (fiddle, accordion, brass) sits 1–3 dB under the full mix, and the drums sit 5–7 dB under it.

Sub-60 Hz energy is −32 to −35 dB of the total in battle and boss. The cannon SFX are
high-passed at 55 Hz and carry a 160–2200 Hz "blast" layer, so the boom also reads on small
speakers.

## Files and sizes

Duration includes pre-roll and padding for the loops. Peak is the decoded peak.

| id | duration | size | peak dBFS | how it was made |
|---|---|---|---|---|
| `ui_tap` | 0.09 s | 2.1 KB | -2.2 | Kept. 1.65 kHz + 2.48 kHz sine blips, a noise click and a band-passed tick |
| `ui_back` | 0.16 s | 2.8 KB | -1.6 | Kept. Two descending blips (1250 → 830 Hz) with soft clicks |
| `ui_upgrade` | 0.70 s | 9.5 KB | -1.5 | Kept. Rising A–D–F#–A bell arpeggio with a hiss shimmer |
| `ui_locked` | 0.26 s | 3.8 KB | -1.4 | Kept. Two dull low-passed square/saw buzzes with a muffled knock |
| `unit_send` | 0.50 s | 7.1 KB | -2.5 | Squeezebox D-major chord squeeze, a deck stomp and a two-hand clap |
| `energy_full` | 0.60 s | 8.3 KB | -1.7 | Gunpowder keg: two hollow wooden knocks (235/590/1130 Hz modes), then two small brass chimes |
| `hit_blade` | 0.32 s | 5.0 KB | -3.1 | Kept (cutlass). Slice hiss, five metal partials, a body thump |
| `hit_blunt` | 0.32 s | 5.0 KB | -1.8 | Kept (anchor). Pitch-dropping body, thud, woody band |
| `hit_claw` | 0.34 s | 5.3 KB | -1.4 | Wet slash: falling swish, two raking scratches, a slimy squelch (AM-gurgled resonant noise) and a fleshy thump |
| `arrow_fire` | 0.50 s | 6.9 KB | -1.4 | Flintlock: flint snap with metal ping, pan-flash fizz, then the bang (crack, closing blast, 150 Hz body), soft-clipped, with a 110 ms slap echo |
| `arrow_hit` | 0.24 s | 4.2 KB | -1.4 | Musket ball hit: band-passed thwack, 190 Hz body, small squelch, three droplet chirps |
| `bolt_fire` | 1.10 s | 14.3 KB | -2.2 | Long Tom cannon: crack, 160–2200 Hz blast, roar closing 6 kHz → 350 Hz, 74 Hz pitch-drop boom, rumble, tanh saturation, 190 ms coastal echo, hall |
| `bolt_hit` | 1.00 s | 13.0 KB | -2.8 | Flaming cannonball lands: boom and roar, a seven-snap timber crack, 18 flying splinters, a splash with bubbles, a tar-sizzle fizz |
| `ballista_reload` | 0.72 s | 9.7 KB | -1.5 | Cannon reload: ramrod scrape in and out (swept band noise), two thuds as the charge is rammed home, an iron clank |
| `spit` | 0.42 s | 6.2 KB | -1.5 | Ink spit: formant throat gurgle, wet "ptoo" burst with a falling tone, squelch, six droplets |
| `bloater_burst` | 0.90 s | 12.0 KB | -2.2 | Puffer burst: tight pop, wet squelch, small splash, 0.85 s carbonated fizz, rising bubbles |
| `warden_die` | 0.65 s | 8.9 KB | -1.3 | Pirate crew member dies (plays often, manifest vol 0.45): a short wordless "oof" grunt (soft low-passed glottal source through "uh" formants, falling 150 → 105 Hz, with an "h" breath), a body thump on deck or sand, and a dropped-cutlass clank with a bounce |
| `hollow_die` | 0.80 s | 10.8 KB | -1.6 | Drowner dies: gurgling formant moan sinking, squelch, then a splash and plunge |
| `castle_hit` | 0.80 s | 10.7 KB | -1.5 | Hull struck: timber crack, hollow hull boom (88 Hz + 180/265/410 Hz body modes), groaning creak, splinters |
| `castle_crumble` | 1.90 s | 23.9 KB | -2.0 | The Gullwake breaks: long timber groan, seven cracks, six beams crashing, debris, a final splash, hall |
| `coin` | 0.32 s | 5.0 KB | -1.9 | Doubloon clink: two touches of heavier gold partials (2.38–8.45 kHz). The engine varies playback rate on repeats |
| `star` | 0.70 s | 9.7 KB | -1.3 | Kept. D6 + A6 bells, sparkling AM hiss |
| `ember_rain` | 1.30 s | 16.6 KB | -3.7 | Broadside: seven distant cannons (low-passed by distance) rolling along the line over 0.6 s, with a rumble bed and hall |
| `rally` | 1.10 s | 14.5 KB | -1.4 | Ship's bell "ding-ding" (A5), two deck stomps, a wordless crew "hey!" bark and a crew clap |
| `bell` | 1.60 s | 20.2 KB | -1.5 | Ship's bell in two pairs (G5, ding-ding ding-ding), a deck stomp and a short crew "hey" |
| `heal` | 0.75 s | 10.2 KB | -1.7 | Kept. Soft rising D–F#–A–D arpeggio, "oo" choir and air |
| `hero_call` | 1.25 s | 16.1 KB | -1.6 | Bosun's pipe (1.1 → 2.3 kHz glide, hold, warble trill), then a swelling crew cheer (ten rising vowel voices), stomp and claps |
| `hero_flare` | 0.85 s | 11.5 KB | -2.9 | Flare pistol: pop, fizzing whoosh climbing to 8 kHz, then a crackling burst |
| `boss_roar` | 1.70 s | 21.7 KB | -1.8 | Mother Fathom: 62–96 Hz gliding saw/square bellow through four formants, a whale-moan overtone, a bubbling gurgle and bubbles, saturated, hall |
| `boss_warn` | 1.50 s | 19.2 KB | -2.5 | Rising eerie warning: A/Bb/E "oo" choir cluster, a theremin-like wail climbing a fifth, a whale growl, accelerating taiko and stomps, cymbal swell |
| `boss_slam` | 1.30 s | 16.6 KB | -3.6 | Tentacle slam: wet whoosh, a massive slap on the deck (slap, 76 Hz body, thud), squelch, timber crack, big splash |
| `win` | 1.40 s | 18.0 KB | -1.4 | Fiddle + squeezebox A–D–F#–A run landing on a D-major brass chord, crew "oh!", stomp, claps, ship's bell ding-ding |
| `lose` | 1.70 s | 21.5 KB | -3.4 | Sagging squeezebox/fiddle A–F–D line over a low drone, timber creak, a wave washing over, a muffled drum |
| `menu` | 46.44 s | 510.4 KB | -1.9 | "The Gullwake" theme, D dorian 6/8 jig-shanty. Intro: D/A drone, held squeezebox chords, low fiddle, creaks, ship's bell, waves. Theme A on accordion with an oom-pah left hand, stomps and claps. Theme B on fiddle with a thirds counterline and a low men's hum. Call-and-answer breakdown with a crew stomp pickup |
| `map` | 49.00 s | 539.1 KB | -2.6 | "Fair Wind", G major/mixolydian 3/4 travel waltz. Plucked bass and chords, tin whistle tune with cuts, squeezebox pads, then the tune on accordion with a whistle descant. Bodhran, shaker, slow wave swells, rigging creaks |
| `battle` | 56.59 s | 621.5 KB | -1.6 | D minor 4/4, 138 bpm. Deck stomps on 1 and 3, crew claps on 2 and 4, bodhran 8ths, low-string ostinato, accordion offbeat chops. A: squeezebox riff, brass stabs, fiddle hooks. B: battle tune on fiddle + accordion. C: brass call, wordless crew shouts, fiddle 16th-note runs, a distant cannon. D: tune on brass + fiddle, crew "oh" pad |
| `boss` | 61.93 s | 681.3 KB | -1.9 | D Phrygian 4/4, 126 bpm, sea-cave reverb. Pounding taiko + stomps, 8th-note low strings, whale moans, choir drones. A: low-brass menace motif. B/D: boss theme on high brass (fiddle an octave up in D), dissonant D/Eb squeezebox stabs. C: half-time breakdown, tolling sunken bell, high fiddle tremolo cluster, rising tom build |
| `victory` | 6.04 s | 66.9 KB | -1.7 | "Yo-ho" cadence: fiddle run, two wordless crew "oh!" hits on A then D with brass stabs and stomps, fiddle/accordion tag, full D-major landing (brass, squeezebox, crew), ship's bell |
| `defeat` | 7.46 s | 81.6 KB | -6.4 | Sea lament, 3/4 at 66: solo fiddle A–G–F–E–D over Dm–Bb–A–Dm squeezebox and a D/A drone. A wave, a creak, a distant bell and a muffled drum |

**Total: 2,940,441 bytes (2.94 MB).**

The 33 SFX come to about 0.38 MB and the 6 music files to about 2.56 MB.

## Known weaknesses

- Nothing has been listened to by a human yet. The checks are analytic: spectra, levels,
  seams and pitch.
- The accordion, fiddle and brass are subtractive synths. They read as "squeezebox" and
  "fiddle" but sound clearly synthetic next to recordings.
- The crew shouts and cheers are formant-filtered saw stacks. They may sound buzzy rather than
  human.
- Music at 88 kbps can soften claps and hats a little.
- `defeat` is 7.5 s, longer than the old 5.6 s, because the lament needs its tail.
- Several event SFX run longer than 1 s: `castle_crumble`, `bell`, `boss_*`, `win`, `lose`,
  `rally`, `hero_call`, `bolt_fire` and `ember_rain`.
