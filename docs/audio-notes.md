# Audio notes (Siegeline / The Ashen Marches)

All sound effects and music are our own work. They were synthesised from scratch in Python
(numpy/scipy) by the scripts in `tools/audio/`. No samples, loops or downloaded sounds were used.

## Pipeline

| Step | Tool |
|---|---|
| DSP toolkit: oscillators (polyBLEP saw/square), filters, envelopes, synthetic hall IR, circular reverb | `tools/audio/synth.py` |
| Instruments: brass, strings, staccato low strings, formant choir, bells, Karplus-Strong pluck, taiko, frame drum, snares, hats, cymbals, boom, flute, drone | `tools/audio/instruments.py` |
| 33 sound effects | `tools/audio/sfx.py` |
| 6 music cues | `tools/audio/music.py` |
| Writes `manifest.json` and runs the checks on the decoded AAC | `tools/audio/check.py` |
| Reports spectral balance, stereo width and level over time | `tools/audio/analyse.py` |
| Spectrogram PNG for visual sanity checks | `tools/audio/spectro.py` |

To rebuild everything (about 4 minutes on the Jetson, one process at a time):

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
| menu | 0.789478 | 51.315805 | 50.526 s | 76 bpm, 16 bars |
| map | 0.714286 | 46.428571 | 45.714 s | 84 bpm, 16 bars |
| battle | 0.454535 | 58.636349 | 58.182 s | 132 bpm, 32 bars |
| boss | 0.400000 | 58.000000 | 57.600 s | 150 bpm, 36 bars |

## Checks (listen-check proxy), all passing

`check.py` decodes every shipped `.m4a` and checks the following:

- **Peak:** at or below -1 dBFS. The actual range is -1.3 to -4.7 dBFS.
- **DC offset:** under 0.005. The actual maximum is 0.0045, a mean offset on the shortest UI clicks rather than true DC; everything is high-passed at 25 Hz.
- **Not silent:** RMS above -45 dBFS.
- **Length:** decoded length equals rendered length, with a decode/render offset of 0 samples.
- **Loop seams:**
  - The jump from sample `loopEnd-1` to sample `loopStart` is smaller than the loop's own
    99.9th-percentile sample-to-sample step. For example, battle is 0.041 against 0.133.
  - Energy above 6 kHz in a 10 ms window across the played seam is no higher than in the rendered
    source at that point (−0.9 to −6.5 dB), so the seam adds no click.
  - The decoded post-pad matches the decoded head to within normal AAC coding error
    (about −13 to −18 dB).
  - The first sample is about 0, so playback starts without a click.

`analyse.py` showed that battle and boss originally carried most of their energy below 60 Hz,
which a phone speaker throws away. The fixes were:

- Taiko retuned from 50–56 Hz to 70–96 Hz, with a 280–1600 Hz "slap" layer.
- Booms reduced.
- Music high-passed at 38–45 Hz.
- About −3 dB low shelf below 150 Hz.
- Parallel presence lift above 2 kHz.
- Lead bus raised.

Sub-60 Hz content in battle and boss is now −24 to −26 dB of the total.

## Files and sizes

Duration includes pre-roll and padding for the loops. Peak is the decoded peak.

| id | duration | size | peak dBFS | how it was made |
|---|---|---|---|---|
| `ui_tap` | 0.09 s | 2.1 KB | -2.2 | 1.65 kHz + 2.48 kHz sine blips (12 / 6 ms decay), a high-passed noise click and a short band-passed tick |
| `ui_back` | 0.16 s | 2.8 KB | -1.6 | Two descending blips (1250 → 830 Hz) with soft clicks |
| `ui_upgrade` | 0.70 s | 9.5 KB | -1.5 | Rising A–D–F#–A bell arpeggio, each note doubled an octave down by a sine, with a hiss shimmer and a small room |
| `ui_locked` | 0.26 s | 3.8 KB | -1.4 | Two dull low-passed square/saw buzzes (98 / 147 Hz) with a muffled knock |
| `unit_send` | 0.50 s | 7.0 KB | -1.3 | Short D3 + A3 brass horn blip over a frame drum and a field-drum tap |
| `energy_full` | 0.60 s | 8.4 KB | -1.5 | Upward sine sweep (fifth stacked), two high bell pings and an air shimmer |
| `hit_blade` | 0.32 s | 5.0 KB | -3.1 | High band-passed slice hiss, 5 inharmonic metal partials (2.1–6.2 kHz), a 170 Hz body thump and a click |
| `hit_blunt` | 0.32 s | 5.0 KB | -1.8 | 105 Hz pitch-dropping body, low-passed noise thud, woody band and a click; soft-clipped |
| `hit_claw` | 0.34 s | 5.3 KB | -1.6 | Three quick descending rasped noise scratches (90 Hz AM) and a fleshy low thump |
| `arrow_fire` | 0.38 s | 4.8 KB | -1.5 | Karplus-Strong bowstring twang (98 Hz, fast damping) and a Gaussian whoosh |
| `arrow_hit` | 0.22 s | 3.9 KB | -2.4 | Wood "thock": band-passed noise, 420 Hz and 230 Hz decaying tones and a shaft-wobble tremolo |
| `bolt_fire` | 0.62 s | 8.6 KB | -2.1 | Deep 72 Hz thunk, wood-noise thump and a clack, then a falling 2.6 kHz whistle with noise (the bolt flying away) |
| `bolt_hit` | 0.95 s | 12.5 KB | -3.9 | Fiery explosion: 50 Hz sub boom, a noise roar with its low-pass sweeping 4.5 kHz → 250 Hz, and 40 ember crackles |
| `ballista_reload` | 0.62 s | 9.1 KB | -1.5 | Five rising ratchet clicks, an AM saw rope creak and a latch clunk |
| `spit` | 0.32 s | 5.0 KB | -2.2 | Band-passed wet burst, a falling "ptoo" tone and rising-pitch bubbles |
| `bloater_burst` | 0.65 s | 8.8 KB | -4.1 | 70 Hz boom, a descending low-passed squelch and ten bubbly pops |
| `warden_die` | 0.65 s | 8.9 KB | -1.4 | Three armour clatters (random metal partials), a body-fall thud and a faint falling lantern tone |
| `hollow_die` | 0.65 s | 8.9 KB | -1.6 | Formant-filtered saw moan gliding down, ash-crumble crackle bed and a low puff |
| `castle_hit` | 0.65 s | 8.9 KB | -2.1 | 48 Hz stone boom, low-passed grit noise, a mid knock and 14 debris ticks |
| `castle_crumble` | 1.60 s | 20.7 KB | -2.0 | Long low rumble, a deep boom, nine falling chunks and 50 decaying debris ticks in a hall reverb |
| `coin` | 0.30 s | 4.7 KB | -3.3 | Two-hit metallic clink (2.6/4.0/5.9/7.4 kHz partials). The engine varies playback rate to pitch it up on repeats |
| `star` | 0.70 s | 9.7 KB | -1.3 | D6 + A6 bells, a sparkling AM hiss and a soft D5 bed |
| `ember_rain` | 0.95 s | 12.5 KB | -1.4 | Rising band-passed fire whoosh, 70 crackles and eight small ember impacts |
| `rally` | 1.10 s | 14.4 KB | -1.4 | Hand bell struck twice (D5) over D4/A4 brass hits and a taiko |
| `bell` | 1.60 s | 19.6 KB | -3.2 | Keep tower bell: D3 additive bell (10 inharmonic partials with beating), D4 overtone bell and a hall |
| `heal` | 0.75 s | 10.2 KB | -1.7 | Soft rising D–F#–A–D sine/octave arpeggio, "oo" choir and air |
| `hero_call` | 0.95 s | 12.5 KB | -1.6 | Heroic D4 → A4 horn call over an A3 horn with two taiko hits |
| `hero_flare` | 0.65 s | 8.9 KB | -1.6 | Opening noise whoosh (400 Hz → 8 kHz), a bright 880/1320/1760 Hz burst and a soft boom |
| `boss_roar` | 1.50 s | 19.2 KB | -1.4 | Saw/square growl (62 Hz, swelling pitch, 13 Hz flutter, noise roughness) through three formants, plus grit and sub; saturated |
| `boss_warn` | 1.30 s | 16.9 KB | -1.5 | Horn rising an octave from A2, 6 Hz pulsing, four accelerating taiko and a cymbal swell |
| `boss_slam` | 0.95 s | 12.5 KB | -2.6 | 38 Hz pitch-drop sub boom, a crash and 20 debris ticks; saturated |
| `win` | 1.25 s | 16.1 KB | -1.7 | Brass D–F#–A–D fanfare landing on a full D major brass chord, with taiko, cymbal and a bell |
| `lose` | 1.50 s | 19.1 KB | -2.6 | Soft, dark horn falling A3 → F3 → D3 over low D strings and a muffled taiko |
| `menu` | 51.82 s | 568.6 KB | -3.8 | D minor, 76 bpm. D/A drone and string pad, harp arpeggios, Siegeline theme on soft horn (bars 5–12), "oo" choir, flute fragment, tolling bells, distant taiko |
| `map` | 46.93 s | 517.7 KB | -4.7 | F major / D minor, 84 bpm march. Pizzicato walking bass, field snare and frame drum, flute travel tune, then horn with flute descant and lute offbeats |
| `battle` | 59.14 s | 656.5 KB | -1.6 | D minor, 132 bpm. Taiko/snare/hat groove, 8th-note low-string ostinato, brass stabs and a horn call, then the theme on brass, then a choir "ah" section with string counter-line, then the theme on brass plus strings; fills every 8 bars |
| `boss` | 58.50 s | 655.9 KB | -1.4 | D minor/Phrygian (Eb), 150 bpm. 16th-note low strings, heavy taiko and sub booms, half-step "menace" brass motif, theme bent to Eb on high brass, choir pads, then a 4-bar rising-taiko build back into the top |
| `victory` | 6.00 s | 85.0 KB | -1.9 | D major fanfare on the theme head (brass and strings), then a full D major brass/strings/choir chord, taiko, cymbal and bell |
| `defeat` | 5.60 s | 70.6 KB | -1.9 | 60 bpm. Horn sighs A–G–F–E–D over Dm–Bb–A–Dm strings, with a low bell toll and a soft taiko |

**Total: 2,920,681 bytes (2.92 MB).**

The 33 SFX come to about 0.33 MB and the 6 music files to about 2.59 MB.

## Known weaknesses

- Nothing has been listened to by a human yet. The checks are analytic.
- The instruments are subtractive and additive synths. Brass and choir sound clearly synthetic
  next to sampled orchestras.
- Music at 88 kbps can soften cymbals and hats a little.
- Victory and defeat use the same leitmotif material as the loops, which is intentional. The stings
  are 6.0 s and 5.6 s.
- Several "event" SFX run longer than 0.6 s: `castle_crumble`, `bell`, `boss_*`, `win`, `lose`,
  `rally`, `hero_call`, `bolt_hit` and `ember_rain`.
