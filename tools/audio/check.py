"""Write public/assets/audio/manifest.json and run the listen-check proxy on the shipped .m4a files.

Run after sfx.py and music.py:  .venv/bin/python tools/audio/check.py
Checks (on the DECODED AAC, since AAC can overshoot peaks):
  peak <= -1 dBFS, |DC| < 0.005, not silent, decoded length == rendered WAV length,
  decoded vs rendered alignment (encoder delay compensated by the mp4 edit list),
  loop seam: jump across loopEnd->loopStart vs typical sample-to-sample step, and
  decoded post-pad (after loopEnd) matches decoded head (after loopStart).
"""
import os
import json
import numpy as np
from scipy.io import wavfile

import audioio as A
from synth import db, peak, SR
from sfx import SFX
from music import MUSIC


def load_wav(name):
    sr, x = wavfile.read(os.path.join(A.WAVDIR, name + ".wav"))
    x = x.astype(np.float32) / 32767
    return (x.T if x.ndim == 2 else x[None, :]), sr


def main():
    meta = json.load(open(os.path.join(A.WAVDIR, "music_meta.json")))
    manifest = {"sfx": {}, "music": {}}
    for sid, (_, vol) in SFX.items():
        manifest["sfx"][sid] = {"file": sid + ".m4a", "vol": vol}
    for mid, (_, looped, vol) in MUSIC.items():
        e = {"file": mid + ".m4a", "vol": vol}
        if looped:
            e["loopStart"] = meta[mid]["loopStart"]
            e["loopEnd"] = meta[mid]["loopEnd"]
        manifest["music"][mid] = e
    with open(os.path.join(A.OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    rows, fails, total = [], [], 0
    items = [("sfx", k, "sfx_" + k) for k in SFX] + [("music", k, "mus_" + k) for k in MUSIC]
    for kind, key, wavname in items:
        path = os.path.join(A.OUT, key + ".m4a")
        size = os.path.getsize(path)
        total += size
        y, sr = A.decode(path)
        ref, _ = load_wav(wavname)
        an = A.analyse(y, sr)
        r = {"id": key, "kind": kind, "bytes": size, "dur": round(an["dur"], 3),
             "peak_db": round(an["peak_db"], 2), "dc": round(an["dc"], 5), "rms_db": round(an["rms_db"], 1),
             "len_ok": y.shape[1] == ref.shape[1]}
        lag = A.align_offset(ref, y, search=2048)
        r["lag"] = lag
        if an["peak_db"] > -1.0:
            fails.append(f"{key}: peak {an['peak_db']:.2f} dBFS")
        if an["dc"] > 0.005:
            fails.append(f"{key}: DC {an['dc']}")
        if an["rms_db"] < -45:
            fails.append(f"{key}: near-silent {an['rms_db']}")
        if not r["len_ok"]:
            fails.append(f"{key}: decoded {y.shape[1]} vs wav {ref.shape[1]} samples")
        if lag != 0:
            fails.append(f"{key}: decoded offset {lag} samples")
        if kind == "music" and "loopEnd" in manifest["music"][key]:
            S = int(round(manifest["music"][key]["loopStart"] * sr))
            E = int(round(manifest["music"][key]["loopEnd"] * sr))
            m = y.mean(axis=0)
            steps = np.abs(np.diff(m[S:E]))
            typical = float(np.percentile(steps, 99.9))
            seam_jump = float(abs(m[S] - m[E - 1]))  # played: ... m[E-1] then m[S]
            n = int(0.25 * sr)
            post_err = float(np.sqrt(np.mean((y[:, E:E + n] - y[:, S:S + n]) ** 2)))
            head_rms = float(np.sqrt(np.mean(y[:, S:S + n] ** 2)))
            # click detector: >6 kHz energy in a 10 ms window straddling the played seam, vs every
            # 10 ms window of the loop, and vs the same seam where it is continuous in the file
            from synth import hp as _hp
            w = int(0.005 * sr)
            seam_seg = np.concatenate([m[E - 4 * w:E], m[S:S + 4 * w]])
            hf_seam = _hp(seam_seg, 6000, 4)[3 * w:5 * w]
            hf_all = _hp(m[S:E], 6000, 4)
            k = len(hf_all) // (2 * w)
            win_e = np.sqrt(np.mean(hf_all[: k * 2 * w].reshape(k, 2 * w) ** 2, axis=1))
            e_seam = float(np.sqrt(np.mean(hf_seam ** 2)))
            pct = float((win_e < e_seam).mean() * 100)
            nat = _hp(m[E - 4 * w:E + 4 * w], 6000, 4)[3 * w:5 * w]
            ratio_db = db(e_seam) - db(float(np.sqrt(np.mean(nat ** 2))))
            r.update({"loopStart": S / sr, "loopEnd": E / sr, "first_sample": round(float(abs(m[0])), 5),
                      "seam_jump": round(seam_jump, 5), "p999_step": round(typical, 5),
                      "seam_hf_percentile": round(pct, 1), "seam_vs_continuous_hf_db": round(ratio_db, 2),
                      "postpad_vs_head_err_db": round(db(post_err) - db(head_rms), 1)})
            if seam_jump > typical:
                fails.append(f"{key}: seam jump {seam_jump:.4f} > 99.9th pct step {typical:.4f}")
            if ratio_db > 1.5:
                fails.append(f"{key}: seam HF {ratio_db:.1f} dB above the continuous version")
            if abs(m[0]) > 0.01:
                fails.append(f"{key}: starts with a non-zero sample ({m[0]:.3f})")
        rows.append(r)
    report = {"total_bytes": total, "files": rows, "fails": fails}
    with open(os.path.join(A.WAVDIR, "check_report.json"), "w") as f:
        json.dump(report, f, indent=1)
    for r in rows:
        print(r)
    print("TOTAL", total, "bytes", f"{total/1e6:.3f} MB")
    print("FAILS:", fails or "none")


if __name__ == "__main__":
    main()
