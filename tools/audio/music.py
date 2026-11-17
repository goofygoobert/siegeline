"""Siegeline music, pirate re-theme (The Gullwake vs. the Deep).
Run: .venv/bin/python tools/audio/music.py [id ...]

All melodies are original. Instruments are synthesised (accordion/squeezebox, fiddle, deck
stomps, crew claps and wordless shouts, low brass, choir, whale-like moans, waves).

Loops are rendered into a circular buffer: any note or reverb tail running past the loop end
wraps around onto the head, so the end flows into the start sample-for-sample. IIR stages
(high-pass, shelf, limiter) run over [tail warm-up + loop] so they are seamless too. The shipped
file is [one-beat pre-roll (loop tail, faded in)] + loop + [POST s of loop head]; loopStart and
loopEnd in the manifest bracket the loop exactly (see finish_loop).
"""
import os
import sys
import json
import numpy as np
from scipy.ndimage import maximum_filter1d

from synth import (SR, n_of, tvec, noise, fade, mtof, lp, hp, bp, make_ir, reverb_circular, reverb,
                   circular_filter, mix_wrap, mix_at, pan_gains, undb, db, peak, sine)
from instruments import (brass, strings, staccato, choir, bell, pluck, taiko, frame_drum, snare,
                         hat, cymbal, flute, drone, accordion, fiddle, stomp, clap, shout, whale,
                         wave_wash, creak, cannon)
import audioio as A

MUSIC_BITRATE = 88000
POST = 0.5  # seconds of loop-head appended after loopEnd
VERBOSE = os.environ.get("MUSIC_VERBOSE", "1") == "1"

# ------------------------------------------------------------------ harmony helpers
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
CHORDS = {
    "Dm": ("D", [0, 3, 7]), "D": ("D", [0, 4, 7]), "Bb": ("Bb", [0, 4, 7]), "Gm": ("G", [0, 3, 7]),
    "A": ("A", [0, 4, 7]), "A7": ("A", [0, 4, 7, 10]), "F": ("F", [0, 4, 7]), "C": ("C", [0, 4, 7]),
    "Am": ("A", [0, 3, 7]), "Eb": ("Eb", [0, 4, 7]), "G": ("G", [0, 4, 7]), "Em": ("E", [0, 3, 7]),
    "Bm": ("B", [0, 3, 7]), "Cm": ("C", [0, 3, 7]), "D7": ("D", [0, 4, 7, 10]),
}


def root_midi(ch, octave=2):
    r, _ = CHORDS[ch]
    return 12 * (octave + 1) + NOTE[r]


def voicing(ch, center=60, n=3):
    """Chord tones nearest to center (simple voice leading)."""
    r, iv = CHORDS[ch]
    pcs = [(NOTE[r] + i) % 12 for i in iv]
    cands = sorted(m for m in range(center - 12, center + 13) if m % 12 in pcs)
    cands.sort(key=lambda m: abs(m - center))
    return sorted(cands[:n])


def parse_mel(s, octave_default=4):
    """'D4:1.5 A4:.5 r:1' -> [(midi|None, beats)]"""
    out = []
    for tok in s.split():
        nm, d = tok.split(":")
        d = float(d)
        if nm == "r":
            out.append((None, d))
            continue
        if nm[-1].isdigit():
            pitch, octv = nm[:-1], int(nm[-1])
        else:
            pitch, octv = nm, octave_default
        out.append((12 * (octv + 1) + NOTE[pitch], d))
    return out


def shift(mel, k):
    return [(m + k if m is not None else None, d) for m, d in mel]


def mel_len(mel):
    return sum(d for _, d in mel)


# ------------------------------------------------------------------ track
class Track:
    def __init__(self, bpm, bars, beats_per_bar=4, loop=True, tail=0.0, seed=0):
        self.bpm = bpm
        self.bpb = beats_per_bar
        self.loop = loop
        self.L = n_of(bars * beats_per_bar * 60.0 / bpm) + (0 if loop else n_of(tail))
        self.bars = bars
        self.buses = {}
        self.rng = np.random.default_rng(seed)

    def spb(self):
        return 60.0 / self.bpm

    def s(self, beat):
        return int(round(beat * self.spb() * SR))

    def bus(self, name):
        if name not in self.buses:
            self.buses[name] = np.zeros((2, self.L), dtype=np.float64)
        return self.buses[name]

    def add(self, busname, x, beat, gain=1.0, pan=0.0, human=0.004):
        b = self.bus(busname)
        st = self.s(beat) + int(self.rng.normal(0, human * SR)) if human else self.s(beat)
        st = max(st, 0) if not self.loop else st
        gl, gr = pan_gains(pan)
        if self.loop:
            mix_wrap(b[0], x, st, gain * gl)
            mix_wrap(b[1], x, st, gain * gr)
        else:
            mix_at(b[0], x, st, gain * gl)
            mix_at(b[1], x, st, gain * gr)

    def sec(self, beats):
        return beats * self.spb()

    beats_to_sec = sec

    def melody(self, busname, mel, start_beat, inst, gain=1.0, pan=0.0, legato=1.0, grace=None, **kw):
        """grace: (min_beats, interval) adds a quick ornamental cut above long notes."""
        b = start_beat
        for i, (m, d) in enumerate(mel):
            if m is not None:
                x = inst(mtof(m), self.sec(d) * legato, seed=i + int(start_beat), **kw)
                self.add(busname, x, b, gain, pan)
                if grace and d >= grace[0]:
                    g = inst(mtof(m + grace[1]), 0.045, seed=900 + i, **kw)
                    self.add(busname, g, b - 0.05 / self.spb(), gain * 0.6, pan)
            b += d
        return b

    def mixdown(self, sends, ir, target_rms_db=-17.0, hp_hz=32.0, presence=0.0, lowshelf=0.0):
        """sends: {bus: (wet, gain)}"""
        out = np.zeros((2, self.L))
        levels = {}
        for name in list(self.buses):
            x = self.buses.pop(name)
            wet, g = sends.get(name, (0.2, 1.0))
            if wet > 0:
                if self.loop:
                    y = reverb_circular(x, ir, wet)
                else:
                    y = reverb(x, ir, wet)[:, : self.L]
            else:
                y = x
            levels[name] = db(float(np.sqrt(np.mean((g * y) ** 2))))
            out += g * y
            del x, y
        def proc(z):
            z = hp(z, hp_hz, 2)
            if lowshelf:  # ~ -3 dB shelf below 150 Hz at 0.3: phone speakers can't use that energy
                z = z - lowshelf * lp(z, 150, 2)
            if presence:  # parallel high band lift above 2 kHz for small speakers
                z = z + presence * hp(z, 2000, 2)
            return z
        out = circular_filter(out, proc, warm=n_of(2.0)) if self.loop else proc(out)
        rms = np.sqrt(np.mean(out ** 2))
        if VERBOSE:
            tot = db(rms)
            print("   bus levels (dB rel. mix):", {k: round(v - tot, 1) for k, v in levels.items()}, flush=True)
        out *= undb(target_rms_db) / max(rms, 1e-9)
        lim = lambda z: limiter(z, undb(-2.0))
        out = circular_filter(out, lim, warm=n_of(1.0)) if self.loop else lim(out)
        pk = peak(out)
        if pk > undb(-1.2):
            out *= undb(-1.2) / pk
        return out


def limiter(x, thr, release=0.12):
    """Stereo-linked smooth limiter (look-around envelope)."""
    a = np.max(np.abs(x), axis=0)
    env = maximum_filter1d(a, n_of(0.006))
    env = np.maximum(env, lp(env, 1.0 / release, 1))
    g = np.minimum(1.0, thr / np.maximum(env, 1e-9))
    g = maximum_filter1d(g * -1, n_of(0.004)) * -1  # keep min gain around peaks
    return x * g[None, :]


def finish_loop(name, x, bitrate, pre_sec):
    """File = [pre-roll: last pre_sec of the loop, faded in] + loop + [POST s of loop head].
    The pre-roll is a one-beat pickup that flows seamlessly into the loop head, and lets the
    first play start from silence (no start click). loopStart/loopEnd bracket the loop exactly."""
    L = x.shape[1]
    P = n_of(pre_sec)
    pre = x[:, L - P:].copy()
    k = n_of(0.03)
    pre[:, :k] *= np.linspace(0, 1, k) ** 2
    full = np.concatenate([pre, x, x[:, : n_of(POST)]], axis=1)
    A.write_wav(full, "mus_" + name)
    A.encode_safe(full, name, bitrate)
    return {"loopStart": round(P / SR, 6), "loopEnd": round((P + L) / SR, 6), "samples": L,
            "preroll_samples": P}


def finish_sting(name, x, bitrate):
    xx = np.stack([fade(x[0], 0.002, 1.0), fade(x[1], 0.002, 1.0)])
    A.write_wav(xx, "mus_" + name)
    A.encode_safe(xx, name, bitrate)
    return {"samples": xx.shape[1]}


_IRS = {}


def hall():
    if "hall" not in _IRS:
        _IRS["hall"] = make_ir(2.6, 2.0, seed=21, damp=5200)
    return _IRS["hall"]


def cabin():
    """Smaller, woodier room (below-decks / tavern)."""
    if "cabin" not in _IRS:
        _IRS["cabin"] = make_ir(1.4, 0.9, seed=33, damp=4200)
    return _IRS["cabin"]


def cave():
    """Big dark sea-cave for the boss."""
    if "cave" not in _IRS:
        _IRS["cave"] = make_ir(3.4, 3.0, seed=41, damp=3500)
    return _IRS["cave"]


# ------------------------------------------------------------------ chord / pattern helpers
def bar_chords(seq, bpb=4):
    """Expand to list of (chord, start_beat_in_section, beats). A tuple splits the bar in half."""
    out = []
    for bi, c in enumerate(seq):
        if isinstance(c, tuple):
            h = bpb / 2
            out.append((c[0], bi * bpb, h))
            out.append((c[1], bi * bpb + h, h))
        else:
            out.append((c, bi * bpb, bpb))
    return out


def first(c):
    return c[0] if isinstance(c, tuple) else c


def chord_at(seq, bpb, beat):
    for ch, b, d in bar_chords(seq, bpb):
        if b <= beat < b + d:
            return ch
    return first(seq[-1])


def pad_chords(tr, seq, bar0, inst, center=60, gain=0.3, n=3, spread=0.5, overlap=0.4, bus="pad", **kw):
    for ch, b, d in bar_chords(seq, tr.bpb):
        for k, m in enumerate(voicing(ch, center, n)):
            x = inst(mtof(m), tr.sec(d) + overlap, seed=m + int(b), **kw)
            tr.add(bus, x, bar0 * tr.bpb + b, gain, pan=spread * (k - (n - 1) / 2) / max(1, (n - 1) / 2))


def squeeze_chords(tr, seq, bar0, hits, center=62, gain=0.1, dur=0.16, pan=-0.25, bass=None, bass_gain=0.2,
                   bus="inst", **kw):
    """Accordion left-hand 'oom-pah': hits = [(beat_in_bar, 'b'|'f'|'c')] where b = bass root,
    f = bass fifth, c = chord chop."""
    for bi, c in enumerate(seq):
        for pos, kind in hits:
            beat = (bar0 + bi) * tr.bpb + pos
            ch = chord_at(seq, tr.bpb, bi * tr.bpb + pos)
            if kind == "c":
                for k, m in enumerate(voicing(ch, center, 3)):
                    tr.add(bus, accordion(mtof(m), dur, seed=m + bi, reeds=2, a=0.008, r=0.05, **kw), beat,
                           gain, pan=pan + 0.08 * (k - 1))
            else:
                r = root_midi(ch, 2) + (7 if kind == "f" else 0)
                if r < 43:
                    r += 12
                tr.add(bus, accordion(mtof(r), dur * 1.4, seed=r + bi, reeds=2, a=0.006, r=0.06, bright=0.6),
                       beat, bass_gain, pan=pan * 0.5)


DM = [62, 64, 65, 67, 69, 70, 72]  # D natural minor from D4, pitch classes used for runs


def scale_run(start, steps, direction=1, sharp7=False):
    """Diatonic D-minor run of `steps` notes starting at midi `start` (snapped to the scale)."""
    pcs = sorted(({p % 12 for p in DM} | ({1} if sharp7 else set())) - ({0} if sharp7 else set()))
    notes = [m for m in range(30, 100) if m % 12 in pcs]
    i = min(range(len(notes)), key=lambda j: abs(notes[j] - start))
    return [notes[i + direction * k] for k in range(steps)]


def tremolo(x, rate=11.0, depth=0.8):
    t = tvec(len(x))
    return x * (1 - depth * 0.5 + depth * 0.5 * np.sin(2 * np.pi * rate * t))


# ================================================================== MENU
# "The Gullwake" theme: D dorian, 6/8 jig-shanty (beat = eighth note).
MENU_A = parse_mel("D4:2 A4:1 A4:2 G4:1  F4:2 E4:1 D4:3  C4:2 E4:1 G4:2 E4:1  A4:3 G4:2 E4:1  "
                   "D4:2 A4:1 A4:2 B4:1  C5:2 B4:1 A4:2 G4:1  F4:2 G4:1 A4:2 E4:1  D4:6")
MENU_A_CH = ["Dm", "Dm", "C", "Am", "Dm", ("C", "G"), ("F", "C"), "Dm"]
MENU_B = parse_mel("A4:1 D5:2 D5:1 E5:1 F5:1  E5:2 D5:1 C5:3  G4:1 C5:2 C5:1 D5:1 E5:1  D5:2 C5:1 A4:3  "
                   "F5:2 E5:1 D5:2 C5:1  D5:2 A4:1 B4:2 C5:1  A4:2 G4:1 E4:2 G4:1  D4:3 A3:3")
MENU_B_CH = ["Dm", "Am", "C", "Dm", "Dm", ("Dm", "G"), ("Am", "C"), "Dm"]
MENU_INTRO_CH = ["Dm", "C", "Dm", ("C", "A")]
MENU_BRK_CH = ["Dm", "C", "Dm", "A"]
JIG_HITS = [(0, "b"), (2, "c"), (3, "f"), (5, "c")]


def menu():
    tr = Track(192, 24, beats_per_bar=6, seed=11)   # dotted quarter = 64
    bpb = 6
    n = tr.L
    t = tvec(n)
    # low drone D2+A2 (hurdy-gurdy-like), breathing 3 times per loop (seamless)
    dr = drone(mtof(38), n) + 0.7 * drone(mtof(45), n) + 0.25 * drone(mtof(50), n)
    dr *= 0.65 + 0.35 * np.sin(np.pi * t / (n / SR) * 3) ** 2
    tr.add("pad", dr, 0, 0.13, 0, human=0)
    del dr
    # waves on the hull, every two bars
    for k in range(12):
        tr.add("sea", wave_wash(5.0, seed=500 + k, bright=0.7, peak_at=0.45), k * 12 + 1, 0.5,
               pan=0.5 * np.sin(k * 1.7), human=0)
    # intro: held bellows chords + creaking timbers + ship's bell
    pad_chords(tr, MENU_INTRO_CH, 0, accordion, center=57, gain=0.1, n=3, overlap=0.3, bus="pad",
               bellows=0.6, a=0.25, r=0.4, reeds=3)
    tr.add("sea", creak(1.4, 30, 70, seed=3), 4, 0.25, pan=-0.6)
    tr.add("sea", creak(1.1, 45, 25, seed=4), 15, 0.2, pan=0.6)
    for k, b in enumerate((0, 1.6)):
        tr.add("inst", bell(mtof(74), 2.2, decay=0.7, seed=40 + k, strike=0.6), b, 0.13 - 0.02 * k, 0.35)
    # fiddle long low notes in the intro (mysterious, sul tasto)
    tr.melody("lead", parse_mel("A3:9 r:3 G3:6 A3:6"), 0, fiddle, gain=0.15, pan=0.3, a=0.4, r=0.5,
              bright=0.35, vdepth=0.004)
    # A theme on accordion (bars 5-12)
    tr.melody("lead", MENU_A, 4 * bpb, accordion, gain=0.32, pan=-0.12, legato=0.92, a=0.015, r=0.06,
              bright=0.9)
    squeeze_chords(tr, MENU_A_CH, 4, JIG_HITS, center=57, gain=0.06, bass_gain=0.12, pan=-0.3)
    # B theme on fiddle (bars 13-20), accordion now plays chords + a thirds counterline
    tr.melody("lead", MENU_B, 12 * bpb, fiddle, gain=0.3, pan=0.15, legato=0.96, a=0.03, r=0.1,
              grace=(3, 2))
    squeeze_chords(tr, MENU_B_CH, 12, JIG_HITS, center=57, gain=0.07, bass_gain=0.13, pan=-0.3)
    tr.melody("inst", shift(parse_mel("F4:6 E4:6 E4:6 F4:6 A4:6 F4:3 G4:3 E4:3 E4:3 F4:6"), 0), 12 * bpb,
              accordion, gain=0.08, pan=-0.35, a=0.2, r=0.3, bellows=0.4, reeds=3)
    # low men's hum on the B section
    for ch, b, d in bar_chords(MENU_B_CH, bpb):
        for k, m in enumerate(voicing(ch, 50, 3)):
            tr.add("pad", choir(mtof(m), tr.sec(d) + 0.2, vowel="oh_lo", a=0.35, r=0.6, voices=5, seed=m + int(b)),
                   12 * bpb + b, 0.07, pan=0.45 * (k - 1))
    # breakdown/build (bars 21-24): call on accordion, answer on fiddle, pickup into the top
    tr.melody("lead", parse_mel("D4:2 A4:1 A4:2 G4:1  F4:2 E4:1 D4:3"), 20 * bpb, accordion, gain=0.3,
              pan=-0.12, legato=0.92, a=0.015, r=0.06)
    tr.melody("lead", parse_mel("D5:2 A4:1 C5:2 A4:1  E4:3 r:1 A3:1 C#4:1"), 22 * bpb, fiddle, gain=0.28,
              pan=0.15, legato=0.95)
    squeeze_chords(tr, MENU_BRK_CH, 20, JIG_HITS, center=57, gain=0.06, bass_gain=0.12, pan=-0.3)
    # low brass on bar downbeats from bar 5 (soft tuba/horn bed)
    for bar0, seq in ((4, MENU_A_CH), (12, MENU_B_CH), (20, MENU_BRK_CH)):
        for ch, b, d in bar_chords(seq, bpb):
            tr.add("pad", brass(mtof(root_midi(ch, 2) + 12), tr.sec(d) * 0.85, vel=0.6, a=0.06, r=0.25,
                                bright=0.25, seed=int(b)), bar0 * bpb + b, 0.07)
    # stomps (dotted-quarter beats) and claps
    for bar in range(24):
        b0 = bar * bpb
        if bar < 4:
            if bar in (2, 3):
                tr.add("drums", stomp(seed=bar, f=80), b0, 0.3)
            continue
        full = bar >= 12
        tr.add("drums", stomp(seed=bar * 3, f=82), b0, 0.5)
        tr.add("drums", stomp(seed=bar * 3 + 1, f=86), b0 + 3, 0.38)
        tr.add("drums", clap(seed=bar, people=3 if full else 2), b0 + 3, 0.32 if full else 0.24, pan=0.2)
        if full:
            for p, v in ((1, 0.12), (2, 0.18), (4, 0.12), (5, 0.18)):
                tr.add("drums", frame_drum(105, 0.3, seed=bar * 9 + p), b0 + p, v, pan=-0.2)
        if bar == 23:  # crew pickup into the top
            tr.add("drums", stomp(seed=777, f=82), b0 + 4, 0.35)
            tr.add("drums", stomp(seed=778, f=86), b0 + 5, 0.4)
    # ship's bell answers at B
    tr.add("inst", bell(mtof(74), 2.0, decay=0.6, seed=44, strike=0.5), 12 * bpb, 0.08, 0.35)
    return tr.mixdown({"pad": (0.3, 1.0), "inst": (0.25, 1.0), "lead": (0.24, 1.0), "drums": (0.16, 1.0),
                       "sea": (0.2, 1.0)},
                      cabin(), target_rms_db=-19.0, hp_hz=45, presence=0.25, lowshelf=0.25)


# ================================================================== MAP
# "Fair Wind": G major / mixolydian travel waltz (3/4).
MAP_A = parse_mel("D4:1 G4:1 A4:1  B4:2 A4:1  G4:1 E4:1 D4:1  E4:3  D4:1 G4:1 A4:1  B4:1 D5:1 C5:1  "
                  "C5:1 A4:1 F4:1  G4:3")
MAP_A_CH = ["G", "G", "C", "Em", "G", "D", "F", "G"]
MAP_B = parse_mel("B4:1 D5:1 G5:1  F5:2 D5:1  E5:1 D5:1 C5:1  D5:3  B4:1 D5:1 G5:1  A5:2 G5:1  "
                  "F#5:1 E5:1 D5:1  G5:3")
MAP_B_CH = ["G", "F", "C", "G", "G", "Am", "D", "G"]
MAP_INTRO = ["G", "C", "G", "D"]
MAP_TAG = ["Em", "C", "D", "D"]


def whistle(f0, dur, vel=1.0, seed=0):
    """Tin whistle: a breathier, brighter flute."""
    x = flute(f0, dur, vel=vel, seed=seed)
    n = len(x)
    t = tvec(n)
    chiff = bp(noise(n, seed + 7), f0 * 2, min(f0 * 6, 15000)) * np.exp(-t / 0.03) * 0.25
    return x + chiff + 0.06 * sine(3 * f0, n) * (np.abs(x) > 0)


def map_():
    tr = Track(120, 32, beats_per_bar=3, seed=12)
    bpb = 3
    form = [(0, MAP_INTRO), (4, MAP_A_CH), (12, MAP_B_CH), (20, MAP_A_CH), (28, MAP_TAG)]
    # waltz accompaniment: plucked bass on 1, plucked chord on 2 and 3 (guitar / mandolin)
    for bar0, seq in form:
        for bi, ch in enumerate(seq):
            b0 = (bar0 + bi) * bpb
            r = root_midi(ch, 2)
            if r < 43:
                r += 12
            tr.add("inst", pluck(mtof(r), 1.2, bright=0.3, seed=bi + bar0, damp=0.993), b0, 0.33, pan=-0.1)
            vs = voicing(ch, 64, 3)
            for p in (1, 2):
                for k, m in enumerate(vs):
                    tr.add("inst", pluck(mtof(m), 0.7, bright=0.55, seed=m + p + bi, damp=0.99),
                           b0 + p + 0.012 * k / tr.spb(), 0.09, pan=0.3)
    # intro: soft held squeezebox chords under a plucked arpeggio sparkle
    pad_chords(tr, MAP_INTRO, 0, accordion, center=60, gain=0.04, n=3, overlap=0.3, bellows=0.6, a=0.3,
               r=0.4, reeds=3)
    for bi, ch in enumerate(MAP_INTRO):
        vs = voicing(ch, 72, 3)
        for k, m in enumerate([vs[0], vs[1], vs[2], vs[1] + 12 if vs[1] + 12 < 90 else vs[1], vs[2], vs[1]]):
            tr.add("inst", pluck(mtof(m), 1.0, bright=0.6, seed=k + bi * 7), bi * bpb + k * 0.5, 0.11,
                   pan=0.4 - 0.12 * k)
    # A on tin whistle, B on whistle with accordion pads, A' on accordion with whistle descant
    tr.melody("lead", shift(MAP_A, 12), 4 * bpb, whistle, gain=0.2, pan=0.15, grace=(2, 2))
    tr.melody("lead", MAP_B, 12 * bpb, whistle, gain=0.2, pan=0.15, grace=(2, 2))
    pad_chords(tr, MAP_B_CH, 12, accordion, center=60, gain=0.045, n=3, overlap=0.2, bellows=0.5, a=0.15,
               r=0.3, reeds=3)
    tr.melody("lead", MAP_A, 20 * bpb, accordion, gain=0.26, pan=-0.12, legato=0.95, a=0.02, r=0.08)
    tr.melody("lead", parse_mel("B5:6 G5:3 E5:3 D5:3 B5:3 C6:3 B5:3"), 20 * bpb, whistle, gain=0.1, pan=0.35)
    tr.melody("lead", parse_mel("E5:2 B4:1  C5:2 E5:1  D5:3  D5:1 C5:1 A4:1"), 28 * bpb, whistle, gain=0.18,
              pan=0.15)
    # gentle drum: bodhran on 1 (+ soft 3), shaker 8ths after the intro
    for bar in range(32):
        b0 = bar * bpb
        if bar >= 4:
            tr.add("drums", frame_drum(100, 0.4, seed=bar), b0, 0.26)
            tr.add("drums", frame_drum(120, 0.3, seed=bar + 99), b0 + 2, 0.1)
            for k in range(6):
                tr.add("drums", hat(0.05, seed=bar * 6 + k), b0 + k * 0.5, 0.035 if k % 2 else 0.055, pan=0.4)
    # sea: long slow swells every 4 bars, rigging creaks, a distant bell
    for k in range(8):
        tr.add("sea", wave_wash(7.0, seed=600 + k, bright=0.8, peak_at=0.4), k * 12, 0.55,
               pan=0.6 * np.sin(k * 2.1), human=0)
    tr.add("sea", creak(1.2, 30, 60, seed=11), 10, 0.22, pan=-0.6)
    tr.add("sea", creak(0.9, 50, 30, seed=12), 58, 0.2, pan=0.6)
    tr.add("inst", bell(mtof(79), 2.0, decay=0.6, seed=7, strike=0.4), 0, 0.06, -0.5)
    return tr.mixdown({"pad": (0.3, 1.8), "inst": (0.22, 1.35), "lead": (0.25, 0.75), "drums": (0.15, 1.1),
                       "sea": (0.15, 1.0)},
                      hall(), target_rms_db=-19.5, hp_hz=40, presence=0.2, lowshelf=0.2)


# ================================================================== BATTLE
BATTLE_TUNE = parse_mel("D4:.5 D4:.5 F4:.5 A4:.5 D5:1 C5:.5 A4:.5  G4:.75 A4:.25 F4:.5 E4:.5 D4:2  "
                        "C4:.5 C4:.5 E4:.5 G4:.5 C5:1 Bb4:.5 G4:.5  A4:.75 G4:.25 F4:.5 E4:.5 A4:2  "
                        "D5:.5 C5:.5 A4:.5 F4:.5 G4:.5 A4:.5 Bb4:1  A4:.5 G4:.5 F4:.5 D4:.5 E4:1 C4:1  "
                        "D4:.5 F4:.5 A4:.5 D5:.5 C5:.5 A4:.5 G4:.5 E4:.5  D4:1.5 A3:.5 D4:2")
BATTLE_TUNE_CH = ["Dm", ("Gm", "Dm"), "C", ("Dm", "A"), ("Dm", "Gm"), ("Dm", "C"), ("Dm", "C"), "Dm"]
BATTLE_A_CH = ["Dm", "Dm", "Bb", "C", "Dm", "Dm", "Gm", "A"]
BATTLE_C_CH = ["Bb", "C", "Dm", "Dm", "Bb", "C", "A", "A"]


def ostinato(tr, chords, bar0, gain=0.3, octave=2, pat=(0, 0, 12, 0, 10, 0, 12, 7), cutoff=1600):
    for bi, ch in enumerate(chords):
        r = root_midi(ch, octave)
        if r < 40:
            r += 12
        for k, iv in enumerate(pat):
            v = 1.0 if k in (0, 3, 6) else 0.75
            tr.add("inst", staccato(mtof(r + iv), tr.sec(0.42), vel=v, seed=k, cutoff=cutoff),
                   (bar0 + bi) * 4 + k * 0.5, gain, pan=-0.2)


def shanty_drums(tr, bar0, bars, fill_every=8, intensity=1.0, heavy=False):
    """Deck stomps on 1 and 3, crew claps on 2 and 4, bodhran 8ths, tom fills."""
    for bi in range(bars):
        b0 = (bar0 + bi) * 4
        for pos, v in ((0, 1.0), (2, 0.9), (2.5, 0.45) if bi % 2 else (3.75, 0.0)):
            if v:
                tr.add("drums", stomp(seed=bi * 7 + int(pos * 4), f=80 if pos != 2.5 else 88), b0 + pos,
                       0.55 * v * intensity)
        for pos, v in ((0, 0.9), (2, 0.8)):
            tr.add("drums", taiko(84, 0.5, seed=bi * 5 + pos, skin=1.0), b0 + pos, 0.28 * v * intensity)
        for pos in (1, 3):
            tr.add("drums", clap(seed=bi * 3 + pos, people=3), b0 + pos, 0.36 * intensity, pan=0.15)
            tr.add("drums", snare(0.2, seed=bi * 3 + pos, snappy=0.6, tone=200), b0 + pos, 0.14 * intensity, pan=0.1)
        for k in range(8):
            acc = k in (0, 3, 6)
            tr.add("drums", frame_drum(115 if acc else 140, 0.25, seed=bi * 8 + k), b0 + k * 0.5,
                   (0.16 if acc else 0.09) * intensity, pan=-0.25)
            tr.add("drums", hat(seed=bi * 8 + k), b0 + k * 0.5 + 0.25 * (k % 2 == 1) * 0, 0.05, pan=0.35)
        if (bi + 1) % fill_every == 0:
            for k in range(8):
                tr.add("drums", taiko(130 - 7 * k, 0.4, seed=500 + bi * 10 + k, skin=0.9), b0 + 2 + k * 0.25,
                       0.22 + 0.035 * k, pan=0.35 - 0.1 * k)


def battle():
    tr = Track(138, 32, seed=13)
    flat = lambda seq: [first(c) for c in seq]
    sections = [(0, BATTLE_A_CH), (8, BATTLE_TUNE_CH), (16, BATTLE_C_CH), (24, BATTLE_TUNE_CH)]
    for bar0, chs in sections:
        ostinato(tr, flat(chs), bar0, gain=0.24)
        # accordion offbeat chops (the shanty 'chk')
        squeeze_chords(tr, chs, bar0, [(0.5, "c"), (1.5, "c"), (2.5, "c"), (3.5, "c")], center=62,
                       gain=0.065, dur=0.12, pan=-0.35)
        # low brass on chord roots
        for ch, b, d in bar_chords(chs):
            tr.add("pad", brass(mtof(root_midi(ch, 2) + 12), tr.sec(min(d, 2)) * 0.85, vel=0.75, a=0.03,
                                r=0.15, bright=0.35, seed=int(b)), bar0 * 4 + b, 0.1, 0)
    shanty_drums(tr, 0, 32)
    # A: brass stabs on the offbeats + a fiddle hook answering
    for bi, ch in enumerate(BATTLE_A_CH):
        for pos in ((1.5, 3.5) if bi % 2 else (3.5,)):
            for k, m in enumerate(voicing(ch, 60, 3)):
                tr.add("lead", brass(mtof(m), 0.15, vel=1.0, a=0.008, r=0.09, bright=0.9, seed=k), bi * 4 + pos,
                       0.15, pan=0.3 * (k - 1))
    # driving squeezebox riff through section A (chord-tone 8ths)
    for bi, ch in enumerate(BATTLE_A_CH):
        r = root_midi(ch, 3)
        if r < 55:
            r += 12
        third = CHORDS[ch][1][1]
        for k, iv in enumerate((0, 0, third, 0, 7, 0, 12, 7)):
            if bi % 4 == 3 and k >= 6:
                continue
            tr.add("lead", accordion(mtof(r + iv), tr.sec(0.4), seed=bi * 8 + k, a=0.006, r=0.04, reeds=3),
                   bi * 4 + k * 0.5, 0.15 if k in (0, 3, 6) else 0.11, pan=-0.2)
    hook = parse_mel("D5:.25 E5:.25 F5:.25 G5:.25 A5:1 r:2.5  A5:.25 G5:.25 F5:.25 E5:.25 D5:1 r:2.5")
    for bar0 in (0, 4):
        tr.melody("lead", hook, bar0 * 4 + 4, fiddle, gain=0.14, pan=0.3, a=0.008, r=0.06, vdepth=0.003)
    # B: tune on fiddle, accordion doubling an octave below
    tr.melody("lead", shift(BATTLE_TUNE, 12), 32, fiddle, gain=0.22, pan=0.2, legato=0.95, a=0.012, r=0.07,
              vdepth=0.004)
    tr.melody("lead", BATTLE_TUNE, 32, accordion, gain=0.2, pan=-0.15, legato=0.9, a=0.01, r=0.05)
    # C: brass call and crew-shout answers, fiddle 16th-note runs
    call = parse_mel("D4:.5 D4:.5 F4:1 D4:.5 C4:.5 D4:1  r:4  F4:.5 F4:.5 A4:1 G4:.5 F4:.5 E4:1  r:4")
    tr.melody("lead", call, 64, brass, gain=0.2, pan=-0.05, a=0.015, r=0.1, bright=0.8, vel=1.0)
    for bar in (17, 19, 21, 23):
        for k, pos in enumerate((1, 2, 3)):
            tr.add("lead", shout(f0=180, dur=0.2, voices=7, seed=bar * 3 + k), bar * 4 + pos, 0.11, pan=0.1 * k)
    for bar in range(16, 24):
        ch = BATTLE_C_CH[bar - 16]
        rt = root_midi(ch, 4)
        up = scale_run(rt, 8, 1, sharp7=(ch == "A"))
        dn = scale_run(up[-1] + 2, 8, -1, sharp7=(ch == "A"))
        for k, m in enumerate(up + dn):
            tr.add("lead", fiddle(mtof(m), tr.sec(0.25) * 0.95, seed=k, a=0.006, r=0.04, vdepth=0.0, scoop=0.0),
                   bar * 4 + k * 0.25, 0.1 if bar % 2 else 0.12, pan=0.3)
    tr.add("drums", cannon(seed=5, size=1.0, dist=0.55), 64, 0.35, pan=-0.4)
    # D: tune on brass + fiddle an octave up + crew "oh" pads
    tr.melody("lead", BATTLE_TUNE, 96, brass, gain=0.22, pan=0.0, a=0.02, r=0.12, bright=0.9, vel=1.0)
    tr.melody("lead", shift(BATTLE_TUNE, 12), 96, fiddle, gain=0.17, pan=0.25, legato=0.95, a=0.012, r=0.07)
    pad_chords(tr, BATTLE_TUNE_CH, 24, choir, center=57, gain=0.05, n=3, overlap=0.2, vowel="oh_lo", a=0.1,
               r=0.3, voices=5)
    for bar0 in (8, 16, 24, 0):
        tr.add("drums", cymbal(1.8, seed=bar0, swell=True), bar0 * 4 - 1.8 / tr.spb(), 0.08)
        tr.add("drums", cymbal(1.6, seed=bar0 + 1), bar0 * 4, 0.08)
    return tr.mixdown({"pad": (0.25, 1.3), "inst": (0.14, 1.0), "lead": (0.22, 2.1), "drums": (0.14, 0.62)},
                      cabin(), target_rms_db=-16.5, hp_hz=50, presence=0.35, lowshelf=0.3)


# ================================================================== BOSS
# Mother Fathom: D Phrygian (Eb), heavy and eerie.
BOSS_P1 = ["Dm", "Eb", "Dm", "C", "Dm", "Eb", "Bb", "A"]
BOSS_B = ["Dm", "Eb", "Cm", "Dm", "Dm", "Cm", "F", "A"]
BOSS_C = ["Dm", "Eb", "Dm", "Eb", "Gm", "Eb", "A", "A"]
BOSS_THEME = parse_mel("D4:1.5 A4:.5 A4:1 G4:1  F4:1.5 Eb4:.5 D4:2  C4:1.5 Eb4:.5 G4:1 Eb4:1  D4:4  "
                       "D4:1.5 A4:.5 A4:1 Bb4:1  C5:1.5 Bb4:.5 A4:1 G4:1  F4:1 G4:1 A4:1 F4:1  E4:2 C#4:2")


def boss():
    tr = Track(126, 32, seed=14)
    form = [(0, BOSS_P1, "A"), (8, BOSS_B, "B"), (16, BOSS_C, "C"), (24, BOSS_B, "D")]
    for bar0, chs, sec_ in form:
        for bi, ch in enumerate(chs):
            r = root_midi(ch, 2)
            if r < 40:
                r += 12
            b0 = (bar0 + bi) * 4
            if sec_ != "C":
                for k in range(8):  # driving 8ths, octave kicks and a Phrygian half-step lean
                    iv = 12 if k in (3, 6) else (1 if (k == 7 and ch == "Dm") else 0)
                    tr.add("inst", staccato(mtof(r + iv), tr.sec(0.4), vel=1.0 if k % 2 == 0 else 0.75,
                                            seed=k, cutoff=1400), b0 + k * 0.5, 0.26, pan=-0.2)
            else:
                tr.add("inst", strings(mtof(r), tr.sec(4) + 0.3, a=0.4, r=0.6, voices=4, cutoff=900, seed=bi),
                       b0, 0.22)
            tr.add("pad", brass(mtof(r), tr.sec(3.6), vel=0.75, a=0.08, r=0.3, bright=0.25, seed=bi), b0, 0.1)
        # choir: low "oo" drone in A, "ah" chords in B/D, "oh" in C
        vowel = {"A": "oo", "B": "ah", "C": "oh", "D": "ah"}[sec_]
        for ch, b, d in bar_chords(chs):
            vs = voicing(ch, 57 if sec_ == "A" else 62, 3 if sec_ == "A" else 4)
            for k, m in enumerate(vs):
                tr.add("pad", choir(mtof(m), tr.sec(d) + 0.3, vowel=vowel, a=0.3, r=0.6, voices=5, seed=m + int(b)),
                       bar0 * 4 + b, 0.08 if sec_ != "A" else 0.065, pan=0.6 * (k / max(1, len(vs) - 1) - 0.5))
    # whale-like moans, deep and gliding
    moans = [(0, [78, 96, 140, 118, 88], 6.0, -0.5), (16, [92, 150, 128, 104], 5.5, 0.5),
             (64, [70, 88, 132, 160, 120, 84], 7.5, -0.3), (80, [110, 165, 140, 92], 6.0, 0.4),
             (92, [80, 120, 98, 76], 4.5, 0.0), (112, [90, 140, 120, 86], 5.5, -0.5)]
    for beat, knots, dur, pan in moans:
        tr.add("sea", whale(knots, dur, seed=int(beat), a=0.6, r=0.9, growl=0.45), beat, 0.16, pan=pan, human=0)
    # drums: pounding stomps + taiko on a heavy pattern, half-time in C
    for bi in range(32):
        b0 = bi * 4
        sec_ = "ABCD"[bi // 8]
        if sec_ == "C":
            pat = ((0, 1.0), (2.5, 0.8))
        else:
            pat = ((0, 1.0), (0.75, 0.55), (1.5, 0.8), (2, 1.0), (2.75, 0.5), (3, 0.7), (3.5, 0.8))
        for pos, v in pat:
            tr.add("drums", taiko(76 if v >= 0.8 else 92, 0.8, seed=bi * 11 + int(pos * 4)), b0 + pos, 0.42 * v)
            if v >= 0.8:
                tr.add("drums", stomp(seed=bi * 13 + int(pos * 4), f=78), b0 + pos, 0.4 * v)
        if sec_ != "C":
            for pos in (1, 3):
                tr.add("drums", snare(0.3, seed=bi * 5 + pos, tone=150), b0 + pos, 0.2, pan=0.1)
                tr.add("drums", clap(seed=bi * 5 + pos, people=4), b0 + pos, 0.22, pan=-0.1)
            for k in range(4):
                tr.add("drums", hat(seed=bi * 8 + k), b0 + k + 0.5, 0.05, pan=0.35)
    # C build: rising toms over the last two bars of the breakdown
    for k in range(32):
        tr.add("drums", taiko(80 + k * 2.5, 0.35, seed=700 + k, skin=0.8), 88 + k * 0.25, 0.1 + 0.011 * k,
               pan=0.3 * np.sin(k))
    tr.add("drums", cymbal(2.6, seed=5, swell=True), 96 - 2.6 / tr.spb(), 0.1)
    for bar0 in (0, 8, 24):
        tr.add("drums", cymbal(2.4, seed=bar0 + 9), bar0 * 4, 0.09)
    # C: tolling sunken bell + eerie high fiddle tremolo cluster (D6/Eb6)
    for k, beat in enumerate((64, 72, 80, 88)):
        tr.add("inst", bell(mtof(50), 3.5, decay=1.1, seed=60 + k, strike=0.5), beat, 0.14, -0.3)
    for m, pan in ((86, 0.5), (87, -0.5)):
        x = tremolo(fiddle(mtof(m), tr.sec(14), seed=m, a=1.5, r=1.0, vdepth=0.002, bright=0.6), 10.5)
        tr.add("lead", x, 66, 0.035, pan=pan)
    # menace motif on low brass (A section)
    menace = parse_mel("D3:1.5 Eb3:.5 D3:1 C3:1  D3:4  D3:1.5 Eb3:.5 F3:1 Eb3:1  D3:3 A2:1")
    for bar0 in (0, 4):
        tr.melody("lead", menace, bar0 * 4, brass, gain=0.22, pan=0.0, a=0.03, r=0.15, bright=0.7, vel=1.0)
    # theme on high brass (B) and brass + fiddle octave (D)
    tr.melody("lead", BOSS_THEME, 32, brass, gain=0.24, pan=0.1, a=0.02, r=0.12, bright=1.0, vel=1.0)
    tr.melody("lead", BOSS_THEME, 96, brass, gain=0.24, pan=0.1, a=0.02, r=0.12, bright=1.0, vel=1.0)
    tr.melody("lead", shift(BOSS_THEME, 12), 96, fiddle, gain=0.15, pan=-0.3, legato=0.97, a=0.02, r=0.1)
    # sea-hag accordion: dissonant D+Eb cluster stabs in D
    for bar in range(24, 32):
        for pos in (1.5, 3.5):
            for k, m in enumerate((62, 63, 69)):
                tr.add("inst", accordion(mtof(m), 0.12, seed=bar + k, reeds=3, musette=0.006, a=0.005, r=0.05),
                       bar * 4 + pos, 0.05, pan=-0.35 + 0.1 * k)
    return tr.mixdown({"pad": (0.32, 1.3), "inst": (0.16, 1.0), "lead": (0.26, 2.4), "drums": (0.16, 0.6),
                       "sea": (0.4, 1.0)},
                      cave(), target_rms_db=-16.0, hp_hz=50, presence=0.35, lowshelf=0.3)


# ================================================================== STINGS
def victory():
    """'Yo-ho' cadence: fiddle run, two crew 'oh!' hits, accordion/fiddle tag, big D major landing."""
    tr = Track(132, 2, loop=False, tail=2.4, seed=15)
    run = parse_mel("A4:.25 B4:.25 C#5:.25 D5:.25")
    tr.melody("lead", run, 0, fiddle, gain=0.3, pan=0.2, a=0.006, r=0.04, vdepth=0.0)
    for beat, ch, f0, dur in ((1, "A", 220, 0.25), (2, "D", 147, 0.5)):
        tr.add("lead", shout(f0=f0, dur=dur, voices=8, seed=beat, vowel="oh_lo", fall=0.05), beat, 0.22)
        for k, m in enumerate(voicing(ch, 62, 3)):
            tr.add("pad", brass(mtof(m), tr.sec(0.5 if beat == 1 else 0.9), vel=1.0, a=0.01, r=0.15, bright=0.9,
                                seed=k), beat, 0.12, pan=0.3 * (k - 1))
        tr.add("drums", stomp(seed=beat, f=80), beat, 0.7)
        tr.add("drums", clap(seed=beat, people=5), beat, 0.4)
    tag = parse_mel("F#5:.5 E5:.5 D5:.5 C#5:.5  B4:.5 C#5:.5 A4:1")
    tr.melody("lead", tag, 3, fiddle, gain=0.25, pan=0.2, a=0.01, r=0.06)
    tr.melody("lead", shift(tag, -12), 3, accordion, gain=0.22, pan=-0.2, a=0.01, r=0.05)
    for p in (3, 4, 5, 6):
        tr.add("drums", stomp(seed=10 + p, f=84), p, 0.4)
    for p in (4, 6):
        tr.add("drums", clap(seed=20 + p, people=4), p, 0.3)
    # landing at beat 7
    for k, m in enumerate([50, 57, 62, 66, 69, 74]):
        tr.add("pad", brass(mtof(m), 2.4, vel=0.95, a=0.02, r=0.9, bright=0.8, seed=m), 7, 0.1, pan=0.5 * np.sin(k))
        tr.add("pad", accordion(mtof(m + 12 if m < 60 else m), 2.2, seed=m, reeds=3, a=0.02, r=0.8), 7, 0.06,
               pan=-0.5 * np.sin(k))
    tr.add("lead", fiddle(mtof(74), 2.2, seed=3, a=0.02, r=0.8), 7, 0.22, 0.2)
    tr.add("lead", shout(f0=147, dur=0.9, voices=9, seed=77, vowel="oh_lo", fall=0.08), 7, 0.2)
    tr.add("drums", stomp(seed=99, f=78), 7, 0.85)
    tr.add("drums", taiko(84, 1.2, seed=9), 7, 0.5)
    tr.add("drums", cymbal(2.6, seed=3), 7, 0.15)
    for k, b in enumerate((7, 7.45)):
        tr.add("inst", bell(mtof(74), 2.4, decay=0.7, seed=k, strike=0.5), b, 0.16, 0.35)
    return tr.mixdown({"pad": (0.25, 1.0), "inst": (0.3, 1.0), "lead": (0.24, 1.2), "drums": (0.18, 1.0)},
                      cabin(), target_rms_db=-17.0, hp_hz=45, presence=0.3, lowshelf=0.3)


def defeat():
    """Slow sea lament: solo fiddle over a low drone and soft squeezebox, waves, a distant bell."""
    tr = Track(66, 2, beats_per_bar=3, loop=False, tail=2.0, seed=16)
    mel = parse_mel("A4:1 G4:.5 F4:.5 E4:1  D4:3")
    tr.melody("lead", mel, 0, fiddle, gain=0.3, pan=0.1, legato=1.03, a=0.12, r=0.9, vdepth=0.007, bright=0.6)
    for ch, b, d in (("Dm", 0, 1), ("Bb", 1, 1), ("A", 2, 1), ("Dm", 3, 3)):
        for k, m in enumerate(voicing(ch, 55, 3)):
            tr.add("pad", accordion(mtof(m), tr.sec(d) + 0.2, seed=m, reeds=3, a=0.25, r=1.0 if b == 3 else 0.3,
                                    bellows=0.5, bright=0.5), b, 0.07, pan=0.4 * (k - 1))
    n = tr.L
    tr.add("pad", fade(drone(mtof(38), n) + 0.6 * drone(mtof(45), n), 0.8, 2.0), 0, 0.12, human=0)
    tr.add("sea", wave_wash(5.5, seed=88, bright=0.6, peak_at=0.35), 0, 0.5, 0.3, human=0)
    tr.add("sea", creak(1.4, 40, 22, seed=5), 1.5, 0.15, -0.5)
    tr.add("inst", bell(mtof(62), 3.5, decay=1.2, seed=8, strike=0.4), 3, 0.14, -0.3)
    tr.add("drums", taiko(70, 1.6, seed=3, skin=0.6), 3, 0.35)
    return tr.mixdown({"pad": (0.3, 1.0), "inst": (0.35, 1.0), "lead": (0.3, 1.2), "drums": (0.22, 1.0),
                       "sea": (0.2, 1.0)},
                      hall(), target_rms_db=-19.0, hp_hz=40, presence=0.25, lowshelf=0.3)


# pre-roll = one beat (menu: one dotted quarter)
BEAT = {"menu": 3 * 60 / 192, "map": 60 / 120, "battle": 60 / 138, "boss": 60 / 126}

MUSIC = {
    "menu": (menu, True, 0.5), "map": (map_, True, 0.45), "battle": (battle, True, 0.45),
    "boss": (boss, True, 0.45), "victory": (victory, False, 0.6), "defeat": (defeat, False, 0.6),
}


def build(ids=None, bitrate=MUSIC_BITRATE):
    info = {}
    for mid in ids or MUSIC:
        fn, looped, vol = MUSIC[mid]
        x = fn()
        x = x - x.mean(axis=1, keepdims=True)
        meta = finish_loop(mid, x, bitrate, BEAT[mid]) if looped else finish_sting(mid, x, bitrate)
        meta["vol"] = vol
        info[mid] = meta
        an = A.analyse(x)
        print(mid, meta, {k: round(v, 3) for k, v in an.items()}, flush=True)
        del x
    mp = os.path.join(A.WAVDIR, "music_meta.json")
    allm = json.load(open(mp)) if os.path.exists(mp) else {}
    allm.update(info)
    A.write_json_atomic(allm, mp)
    return info


if __name__ == "__main__":
    build(sys.argv[1:] or None)
