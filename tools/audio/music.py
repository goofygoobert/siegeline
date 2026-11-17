"""Siegeline music. Run: .venv/bin/python tools/audio/music.py [id ...]

Loops are rendered into a circular buffer: any note or reverb tail running past the loop end
wraps around onto the head, so the end flows into the start sample-for-sample. IIR stages
(high-pass, limiter) run over [tail warm-up + loop] so they are seamless too. The shipped file
is the loop followed by POST seconds of the loop head (padding against AAC end padding), with
loopStart = 0 and loopEnd = loop length.
"""
import sys
import json
import numpy as np
from scipy.ndimage import maximum_filter1d

from synth import (SR, n_of, tvec, noise, fade, mtof, lp, hp, make_ir, reverb_circular, reverb,
                   circular_filter, mix_wrap, mix_at, pan_gains, undb, db, peak, softclip)
from instruments import (brass, strings, staccato, choir, bell, pluck, taiko, frame_drum, snare,
                         field_snare, hat, cymbal, boom, flute, drone)
import audioio as A

MUSIC_BITRATE = 88000
POST = 0.5  # seconds of loop-head appended after loopEnd

# ------------------------------------------------------------------ harmony helpers
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
CHORDS = {
    "Dm": ("D", [0, 3, 7]), "D": ("D", [0, 4, 7]), "Bb": ("Bb", [0, 4, 7]), "Gm": ("G", [0, 3, 7]),
    "A": ("A", [0, 4, 7]), "A7": ("A", [0, 4, 7, 10]), "F": ("F", [0, 4, 7]), "C": ("C", [0, 4, 7]),
    "Am": ("A", [0, 3, 7]), "Eb": ("Eb", [0, 4, 7]), "G": ("G", [0, 4, 7]), "Em": ("E", [0, 3, 7]),
    "Bm": ("B", [0, 3, 7]), "Cm": ("C", [0, 3, 7]),
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

    def beats_to_sec(self, beats):
        return beats * self.spb()

    # convenience
    def melody(self, busname, mel, start_beat, inst, gain=1.0, pan=0.0, legato=1.0, **kw):
        b = start_beat
        for i, (m, d) in enumerate(mel):
            if m is not None:
                x = inst(mtof(m), self.beats_to_sec(d) * legato, seed=i + int(start_beat), **kw)
                self.add(busname, x, b, gain, pan)
            b += d
        return b

    def mixdown(self, sends, ir, target_rms_db=-17.0, hp_hz=32.0):
        """sends: {bus: (wet, gain)}"""
        out = np.zeros((2, self.L))
        for name, x in self.buses.items():
            wet, g = sends.get(name, (0.2, 1.0))
            if wet > 0:
                if self.loop:
                    y = reverb_circular(x, ir, wet)
                else:
                    y = reverb(x, ir, wet)[:, : self.L]
            else:
                y = x
            out += g * y
        self.buses.clear()
        proc = lambda z: hp(z, hp_hz, 2)
        out = circular_filter(out, proc, warm=n_of(2.0)) if self.loop else proc(out)
        rms = np.sqrt(np.mean(out ** 2))
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
    # smooth release with a one-pole on the envelope (applied forward)
    env = np.maximum(env, lp(env, 1.0 / release, 1))
    g = np.minimum(1.0, thr / np.maximum(env, 1e-9))
    g = maximum_filter1d(g * -1, n_of(0.004)) * -1  # keep min gain around peaks
    return x * g[None, :]


def finish_loop(name, x, bitrate):
    L = x.shape[1]
    full = np.concatenate([x, x[:, : n_of(POST)]], axis=1)
    A.write_wav(full, "mus_" + name)
    A.encode_safe(full, name, bitrate)
    return {"loopStart": 0.0, "loopEnd": round(L / SR, 6), "samples": L}


def finish_sting(name, x, bitrate):
    xx = np.stack([fade(x[0], 0.002, 0.6), fade(x[1], 0.002, 0.6)])
    A.write_wav(xx, "mus_" + name)
    A.encode_safe(xx, name, bitrate)
    return {"samples": xx.shape[1]}


HALL = None


def hall():
    global HALL
    if HALL is None:
        HALL = make_ir(2.8, 2.2, seed=21, damp=5200)
    return HALL


# ================================================================== shared material
# Siegeline leitmotif (8 bars, 4/4) in D minor
THEME_A = parse_mel("D4:1.5 A4:.5 G4:1 F4:1  E4:1 F4:.5 G4:.5 A4:2  Bb4:1.5 A4:.5 G4:1 F4:1  E4:1 C#4:1 D4:2")
THEME_B = parse_mel("F4:1.5 G4:.5 A4:1 D5:1  C5:1.5 Bb4:.5 A4:2  G4:1 Bb4:1 A4:1 G4:1  F4:1 E4:1 E4:2")
THEME_CHORDS = ["Dm", "C", "Bb", ("A", "Dm"), "F", "Am", "Gm", "A"]


def bar_chords(seq):
    """Expand to list of (chord, start_beat_in_bar, beats)."""
    out = []
    for bi, c in enumerate(seq):
        if isinstance(c, tuple):
            out.append((c[0], bi * 4, 2))
            out.append((c[1], bi * 4 + 2, 2))
        else:
            out.append((c, bi * 4, 4))
    return out


def pad_chords(tr, seq, bar0, inst, center=60, gain=0.3, n=3, spread=0.5, overlap=0.4, **kw):
    for ch, b, d in bar_chords(seq):
        for k, m in enumerate(voicing(ch, center, n)):
            x = inst(mtof(m), tr.beats_to_sec(d) + overlap, seed=m + b, **kw)
            tr.add("pad", x, bar0 * 4 + b, gain, pan=spread * (k - (n - 1) / 2) / max(1, (n - 1) / 2))


# ================================================================== MENU
def menu():
    tr = Track(76, 16, seed=1)
    prog_intro = ["Dm", "Bb", "Gm", "A"]
    # low drone D2+A2 under all, slowly breathing
    n = tr.L
    t = tvec(n)
    dr = drone(mtof(38), n) + 0.6 * drone(mtof(45), n)
    dr *= 0.7 + 0.3 * np.sin(2 * np.pi * t / (n / SR) * 4) ** 2  # 4 swells per loop (seamless)
    tr.add("pad", dr, 0, 0.18, 0, human=0)
    # strings pad on all 16 bars
    seq = prog_intro + THEME_CHORDS + prog_intro
    pad_chords(tr, seq, 0, strings, center=57, gain=0.22, n=3, a=0.8, r=1.2, cutoff=1800)
    # bass strings roots
    for bi, ch in enumerate(seq):
        c = ch[0] if isinstance(ch, tuple) else ch
        tr.add("pad", strings(mtof(root_midi(c, 2)), tr.beats_to_sec(4) + 0.5, a=0.5, r=1.0,
                              cutoff=900, voices=3, seed=bi), bi * 4, 0.3, 0)
    # harp arpeggios bars 1-4 and 13-16
    for bar0 in (0, 12):
        for bi, ch in enumerate(prog_intro):
            vs = voicing(ch, 62, 3)
            pat = [vs[0] - 12, vs[0], vs[1], vs[2], vs[1] + 12 if False else vs[2] + 5 - 5, vs[1], vs[0], vs[1]]
            for k, m in enumerate(pat):
                tr.add("inst", pluck(mtof(m), 1.6, bright=0.35, seed=k + bi), (bar0 + bi) * 4 + k * 0.5,
                       0.22, pan=-0.3 + 0.08 * k)
    # horn theme bars 5-12
    tr.melody("lead", THEME_A + THEME_B, 16, brass, gain=0.34, pan=0.1, legato=1.02, a=0.12, r=0.35,
              bright=0.45, vel=0.8)
    # soft octave-down doubling on cello-ish strings
    tr.melody("inst", [(m - 12 if m else None, d) for m, d in THEME_A + THEME_B], 16, strings, gain=0.12,
              pan=-0.15, a=0.1, r=0.3, voices=3, cutoff=1500)
    # choir "oo" bars 9-12
    for ch, b, d in bar_chords(THEME_CHORDS[4:]):
        for k, m in enumerate(voicing(ch, 64, 3)):
            tr.add("pad", choir(mtof(m), tr.beats_to_sec(d) + 0.3, vowel="oo", a=0.6, r=0.9, voices=5,
                                seed=m), 32 + b, 0.14, pan=0.4 * (k - 1))
    # flute fragment bars 13-16 (theme head, high & distant)
    frag = parse_mel("D5:1.5 A5:.5 G5:1 F5:1  E5:3 r:1  F5:1.5 E5:.5 D5:1 C#5:1  D5:2 E5:2")
    tr.melody("lead", frag, 48, flute, gain=0.2, pan=-0.2)
    # bells: keep bell at bar 1 and 9, small bell answers
    tr.add("inst", bell(mtof(50), 4.0, decay=1.2, seed=3, strike=0.5), 0, 0.22, 0.2)
    tr.add("inst", bell(mtof(57), 3.0, decay=1.0, seed=4, strike=0.4), 32, 0.16, -0.2)
    tr.add("inst", bell(mtof(50), 4.0, decay=1.2, seed=5, strike=0.5), 48, 0.18, 0.2)
    # distant timpani-like taiko on bar downbeats 5-16 (+ pickup into bar 1)
    for bi in range(4, 16):
        tr.add("drums", taiko(52, 1.2, seed=bi, skin=0.6), bi * 4, 0.35 if bi % 4 == 0 else 0.22)
    tr.add("drums", taiko(52, 1.0, seed=99, skin=0.6), 63, 0.16)
    tr.add("drums", taiko(52, 1.0, seed=98, skin=0.6), 63.5, 0.2)
    return tr.mixdown({"pad": (0.45, 1.0), "inst": (0.4, 1.0), "lead": (0.35, 1.0), "drums": (0.4, 1.0)},
                      hall(), target_rms_db=-19.0)


# ================================================================== MAP
MAP_MEL_A = parse_mel("A4:1 C5:1 F5:1.5 E5:.5  D5:1 C5:1 G4:2  A4:1 Bb4:.5 C5:.5 D5:1 A4:1  Bb4:1.5 A4:.5 G4:2")
MAP_MEL_B = parse_mel("A4:1 C5:1 F5:1.5 G5:.5  A5:1 G5:.5 F5:.5 D5:2  Bb4:1 D5:1 C5:1 Bb4:1  A4:1 G4:1 C5:2")
MAP_CH = ["F", "C", "Dm", "Bb", "F", "Dm", "Bb", "C"]


def map_():
    tr = Track(84, 16, seed=2)
    seq = MAP_CH + MAP_CH
    pad_chords(tr, seq, 0, strings, center=60, gain=0.14, n=3, a=0.5, r=0.8, cutoff=2000)
    # pizzicato walking bass: root, fifth, octave, fifth
    for bi, ch in enumerate(seq):
        r = root_midi(ch, 2)
        for k, iv in enumerate((0, 7, 12, 7)):
            tr.add("inst", pluck(mtof(r + iv), 0.7, bright=0.25, seed=bi * 4 + k, damp=0.99), bi * 4 + k,
                   0.42 if k == 0 else 0.3, pan=-0.1)
    # lute 8th-note broken chords (offbeat) second half
    for bi, ch in enumerate(seq[8:]):
        vs = voicing(ch, 67, 3)
        for k in range(8):
            if k % 2 == 1:
                tr.add("inst", pluck(mtof(vs[(k // 2) % 3]), 0.5, bright=0.6, seed=k + bi), (8 + bi) * 4 + k * 0.5,
                       0.16, pan=0.35)
    # flute melody bars 1-8, horn bars 9-16 with flute descant
    tr.melody("lead", MAP_MEL_A + MAP_MEL_B, 0, flute, gain=0.3, pan=0.15)
    tr.melody("lead", [(m - 12 if m else None, d) for m, d in MAP_MEL_A + MAP_MEL_B], 32, brass, gain=0.24,
              pan=-0.1, a=0.08, r=0.25, bright=0.35, vel=0.7)
    desc = parse_mel("F5:4 E5:4 F5:4 D5:4 C5:4 D5:4 D5:2 C5:2 E5:4")
    tr.melody("lead", desc, 32, flute, gain=0.12, pan=0.35)
    # march: field snare + frame drum
    for bi in range(16):
        b0 = bi * 4
        tr.add("drums", frame_drum(90, 0.5, seed=bi), b0, 0.45)
        tr.add("drums", frame_drum(90, 0.5, seed=bi + 50), b0 + 2, 0.35)
        for k, (pos, v) in enumerate(((1, 0.32), (1.75, 0.14), (2.5, 0.18), (3, 0.3), (3.5, 0.16), (3.75, 0.12))):
            tr.add("drums", field_snare(0.25, seed=bi * 8 + k), b0 + pos, v, pan=0.15)
        if bi % 4 == 3:  # little roll into the next phrase
            for k in range(6):
                tr.add("drums", field_snare(0.2, seed=900 + bi * 10 + k), b0 + 3 + k / 6, 0.08 + 0.03 * k, 0.15)
    return tr.mixdown({"pad": (0.35, 1.0), "inst": (0.25, 1.0), "lead": (0.3, 1.0), "drums": (0.22, 1.0)},
                      hall(), target_rms_db=-19.5)


# ================================================================== BATTLE
def ostinato(tr, chords, bar0, gain=0.3, octave=2, pat=(0, 0, 12, 0, 10, 0, 12, 7), cutoff=1600):
    for bi, ch in enumerate(chords):
        r = root_midi(ch, octave)
        for k, iv in enumerate(pat):
            v = 1.0 if k in (0, 3, 6) else 0.75
            tr.add("inst", staccato(mtof(r + iv), tr.beats_to_sec(0.42), vel=v, seed=k, cutoff=cutoff),
                   (bar0 + bi) * 4 + k * 0.5, gain, pan=-0.2)


def battle_drums(tr, bar0, bars, fill_every=8, intensity=1.0):
    for bi in range(bars):
        b0 = (bar0 + bi) * 4
        # taiko: X . x . X x . x
        for pos, v in ((0, 1.0), (1, 0.55), (2, 0.9), (2.5, 0.6), (3.5, 0.5)):
            tr.add("drums", taiko(56, 0.8, seed=bi * 7 + int(pos * 2)), b0 + pos, 0.55 * v * intensity)
        for pos in (1, 3):
            tr.add("drums", snare(0.25, seed=bi * 3 + pos, snappy=0.8), b0 + pos, 0.3 * intensity, pan=0.1)
        for k in range(8):
            tr.add("drums", hat(seed=bi * 8 + k), b0 + k * 0.5, (0.12 if k % 2 else 0.07) * intensity, pan=0.3)
        if (bi + 1) % fill_every == 0:
            for k in range(8):
                f = 120 - 8 * k
                tr.add("drums", taiko(f, 0.4, seed=500 + bi * 10 + k, skin=0.8), b0 + 2 + k * 0.25,
                       0.25 + 0.04 * k, pan=0.3 - 0.08 * k)


def battle():
    tr = Track(132, 32, seed=3)
    A_ch = ["Dm", "Dm", "Bb", "C", "Dm", "Dm", "Gm", "A"]
    C_ch = ["Bb", "C", "Dm", "Dm", "Bb", "C", "A", "A"]
    flat = lambda seq: [c if not isinstance(c, tuple) else c[0] for c in seq]
    sections = [(0, A_ch), (8, THEME_CHORDS), (16, C_ch), (24, THEME_CHORDS)]
    for bar0, chs in sections:
        ostinato(tr, flat(chs), bar0, gain=0.3)
        pad_chords(tr, chs, bar0, strings, center=57, gain=0.12 if bar0 < 16 else 0.16, n=3, a=0.2, r=0.4,
                   cutoff=2200)
        # brass bass on roots, half notes
        for ch, b, d in bar_chords(chs):
            tr.add("pad", brass(mtof(root_midi(ch, 2)), tr.beats_to_sec(min(d, 2)) * 0.9, vel=0.7, a=0.03,
                                r=0.15, bright=0.3, seed=b), bar0 * 4 + b, 0.16, 0)
    battle_drums(tr, 0, 32)
    # brass stabs in section A: offbeat chord hits
    for bi, ch in enumerate(A_ch):
        for pos in (1.5, 3.5) if bi % 2 else (3.5,):
            for k, m in enumerate(voicing(ch, 62, 3)):
                tr.add("lead", brass(mtof(m), 0.16, vel=0.9, a=0.01, r=0.1, seed=k), bi * 4 + pos, 0.12,
                       pan=0.3 * (k - 1))
    # theme on brass (section B), octave doubled with strings (section D)
    tr.melody("lead", THEME_A + THEME_B, 32, brass, gain=0.3, pan=0.05, a=0.03, r=0.15, bright=0.8, vel=0.95)
    tr.melody("lead", THEME_A + THEME_B, 96, brass, gain=0.3, pan=0.05, a=0.03, r=0.15, bright=0.9, vel=1.0)
    tr.melody("lead", [(m + 12 if m else None, d) for m, d in THEME_A + THEME_B], 96, strings, gain=0.14,
              pan=-0.25, a=0.04, r=0.2, voices=4, cutoff=4000)
    # section C: choir "ah" pads + strings counter-line
    for ch, b, d in bar_chords(C_ch):
        for k, m in enumerate(voicing(ch, 62, 3)):
            tr.add("pad", choir(mtof(m), tr.beats_to_sec(d) + 0.2, vowel="ah", a=0.25, r=0.5, voices=5,
                                seed=m + b), 64 + b, 0.13, pan=0.5 * (k - 1))
    counter = parse_mel("D5:2 F5:2  E5:2 G5:2  A5:3 G5:.5 F5:.5  E5:2 D5:2  D5:2 F5:2  E5:2 G5:2  "
                        "A5:2 G5:1 F5:1  E5:4")
    tr.melody("lead", counter, 64, strings, gain=0.17, pan=0.25, a=0.05, r=0.25, voices=4, cutoff=4500)
    # cymbal swells into sections, crash at section starts
    for bar0 in (8, 16, 24):
        tr.add("drums", cymbal(1.8, seed=bar0, swell=True), bar0 * 4 - tr.beats_to_sec(0) - 1.8 / tr.spb(), 0.12)
        tr.add("drums", cymbal(2.0, seed=bar0 + 1), bar0 * 4, 0.12)
    tr.add("drums", cymbal(1.8, seed=77, swell=True), 128 - 1.8 / tr.spb(), 0.12)
    tr.add("drums", cymbal(2.0, seed=78), 0, 0.12)
    return tr.mixdown({"pad": (0.3, 1.0), "inst": (0.15, 1.0), "lead": (0.28, 1.0), "drums": (0.15, 1.0)},
                      hall(), target_rms_db=-16.5)


# ================================================================== BOSS
def boss():
    tr = Track(150, 36, seed=4)
    P1 = ["Dm", "Eb", "Dm", "C", "Dm", "Eb", "Bb", "A"]
    P2 = ["Gm", "Eb", "Dm", "Dm", "Gm", "Eb", "A", "A"]
    form = [(0, P1), (8, P1), (16, P2), (24, P1), (32, ["Dm", "Eb", "Dm", "A"])]
    for bar0, chs in form:
        for bi, ch in enumerate(chs):
            r = root_midi(ch, 2)
            # driving 16th low strings: r r r r+1? (menace) -> root pulses with octave kicks
            for k in range(16):
                iv = 12 if k in (6, 14) else (1 if (k == 11 and ch == "Dm") else 0)
                tr.add("inst", staccato(mtof(r + iv), tr.beats_to_sec(0.22), vel=1.0 if k % 4 == 0 else 0.7,
                                        seed=k, cutoff=1300), (bar0 + bi) * 4 + k * 0.25, 0.24, pan=-0.2)
            # sub brass on root
            tr.add("pad", brass(mtof(r - 12 + 12), tr.beats_to_sec(3.6), vel=0.8, a=0.05, r=0.2, bright=0.25,
                                seed=bi), (bar0 + bi) * 4, 0.14, 0)
        # choir sustained chords on everything after bar 8
        if bar0 >= 8:
            for bi, ch in enumerate(chs):
                for k, m in enumerate(voicing(ch, 60, 4 if ch != "A" else 3)):
                    tr.add("pad", choir(mtof(m), tr.beats_to_sec(4) + 0.25, vowel="ah" if bar0 != 16 else "oh",
                                        a=0.2, r=0.4, voices=5, seed=m + bi), (bar0 + bi) * 4, 0.1,
                           pan=0.6 * (k / 3 - 0.5))
    # heavy drums: taiko 8ths with accents + low booms
    for bi in range(36):
        b0 = bi * 4
        brk = bi >= 32
        pat = ((0, 1.0), (0.75, 0.5), (1.5, 0.8), (2, 1.0), (2.75, 0.5), (3, 0.7), (3.5, 0.8), (3.75, 0.5))
        for pos, v in pat if not brk else ((0, 1.0), (2, 0.9)):
            tr.add("drums", taiko(50, 0.9, seed=bi * 11 + int(pos * 4)), b0 + pos, 0.5 * v)
        if not brk:
            for pos in (1, 3):
                tr.add("drums", snare(0.3, seed=bi * 5 + pos, tone=160), b0 + pos, 0.3, pan=0.1)
            for k in range(8):
                tr.add("drums", hat(seed=bi * 8 + k), b0 + k * 0.5 + 0.25, 0.08, pan=0.35)
        if bi % 4 == 0:
            tr.add("drums", boom(36, 1.5, seed=bi, drop=1.4, tau=0.5), b0, 0.4)
    # build in bars 33-36: rising taiko 16ths + swell
    for k in range(32):
        tr.add("drums", taiko(60 + k * 2, 0.35, seed=700 + k, skin=0.7), 33 * 4 + k * 0.25 + 4 * 0, 0.12 + 0.012 * k,
               pan=0.3 * np.sin(k))
    tr.add("drums", cymbal(3.0, seed=5, swell=True), 144 - 3.0 / tr.spb(), 0.16)
    for bar0 in (0, 8, 16, 24):
        tr.add("drums", cymbal(2.4, seed=bar0 + 9), bar0 * 4, 0.13)
    # menace motif on low brass bars 1-8 and 17-24: D Eb D C | D ...
    menace = parse_mel("D3:1.5 Eb3:.5 D3:1 C3:1  D3:4  D3:1.5 Eb3:.5 F3:1 Eb3:1  D3:3 A2:1")
    for bar0 in (0, 4, 16, 20):
        tr.melody("lead", menace, bar0 * 4, brass, gain=0.26, pan=0.0, a=0.03, r=0.15, bright=0.7, vel=1.0)
    # leitmotif twisted (Eb for E) on high brass bars 9-16 and 25-32, strings an octave up
    twist = [(m - 1 if m and m % 12 == 4 else m, d) for m, d in THEME_A + THEME_B]
    for bar0 in (8, 24):
        tr.melody("lead", twist, bar0 * 4, brass, gain=0.28, pan=0.1, a=0.02, r=0.12, bright=1.0, vel=1.0)
        tr.melody("lead", [(m + 12 if m else None, d) for m, d in twist], bar0 * 4, strings, gain=0.13,
                  pan=-0.3, a=0.03, r=0.2, voices=4, cutoff=4500)
    return tr.mixdown({"pad": (0.35, 1.0), "inst": (0.15, 1.0), "lead": (0.28, 1.0), "drums": (0.18, 1.0)},
                      hall(), target_rms_db=-16.0)


# ================================================================== STINGS
def victory():
    tr = Track(100, 2, loop=False, tail=3.0, seed=5)
    fan = parse_mel("D4:.75 A4:.25 G4:.5 F#4:.5  E4:.5 F#4:.25 G4:.25 A4:4")
    tr.melody("lead", fan, 0, brass, gain=0.4, pan=0.05, a=0.02, r=0.4, bright=0.9, vel=1.0)
    tr.melody("lead", [(m + 12, d) for m, d in fan], 0, strings, gain=0.15, pan=-0.25, a=0.03, r=0.4, voices=4,
              cutoff=5000)
    # final chord at beat 4: D major full
    for k, m in enumerate([38, 50, 57, 62, 66, 69, 74]):
        inst = brass if m < 60 else strings
        tr.add("pad", inst(mtof(m), 2.6, vel=0.9, seed=m) if inst is brass else strings(mtof(m), 2.6, seed=m,
               a=0.08, r=1.0, voices=4, cutoff=4500), 4, 0.15, pan=0.5 * np.sin(k))
    for k, m in enumerate((62, 66, 69)):
        tr.add("pad", choir(mtof(m), 2.6, vowel="ah", a=0.15, r=1.0, seed=k), 4, 0.12, pan=0.4 * (k - 1))
    for b in (0, 1, 2, 3):
        tr.add("drums", taiko(58, 0.8, seed=b), b, 0.4 if b else 0.6)
    tr.add("drums", taiko(50, 1.5, seed=9), 4, 0.8)
    tr.add("drums", cymbal(3.0, seed=3), 4, 0.2)
    tr.add("inst", bell(mtof(74), 3.0, decay=1.0, seed=2, strike=0.3), 4, 0.18, 0.3)
    return tr.mixdown({"pad": (0.35, 1.0), "inst": (0.4, 1.0), "lead": (0.3, 1.0), "drums": (0.25, 1.0)},
                      hall(), target_rms_db=-17.0)


def defeat():
    tr = Track(60, 1, loop=False, tail=2.4, seed=6)
    mel = parse_mel("A4:.75 G4:.25 F4:1 E4:1 D4:3")
    tr.melody("lead", mel, 0, brass, gain=0.3, pan=0.05, a=0.12, r=0.8, bright=0.35, vel=0.65)
    for ch, b, d in (("Dm", 0, 1), ("Bb", 1, 1), ("A", 2, 1), ("Dm", 3, 3)):
        for k, m in enumerate(voicing(ch, 55, 3)):
            tr.add("pad", strings(mtof(m), d + 0.4, a=0.25, r=1.2 if b == 3 else 0.4, voices=4, cutoff=1500,
                                  seed=m), b, 0.17, pan=0.4 * (k - 1))
        tr.add("pad", strings(mtof(root_midi(ch, 1)), d + 0.4, a=0.2, r=1.0, voices=3, cutoff=700, seed=b), b, 0.28)
    tr.add("inst", bell(mtof(38), 4.0, decay=1.4, seed=8, strike=0.4), 3, 0.25, -0.2)
    tr.add("drums", taiko(45, 1.6, seed=3), 3, 0.5)
    tr.add("drums", taiko(45, 1.0, seed=4), 0, 0.3)
    return tr.mixdown({"pad": (0.4, 1.0), "inst": (0.45, 1.0), "lead": (0.35, 1.0), "drums": (0.3, 1.0)},
                      hall(), target_rms_db=-19.0)


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
        meta = finish_loop(mid, x, bitrate) if looped else finish_sting(mid, x, bitrate)
        meta["vol"] = vol
        info[mid] = meta
        an = A.analyse(x)
        print(mid, meta, {k: round(v, 3) for k, v in an.items()}, flush=True)
        del x
    import os
    mp = os.path.join(A.WAVDIR, "music_meta.json")
    allm = json.load(open(mp)) if os.path.exists(mp) else {}
    allm.update(info)
    json.dump(allm, open(mp, "w"), indent=1)
    return info


if __name__ == "__main__":
    build(sys.argv[1:] or None)
