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
            L = int(round(manifest["music"][key]["loopEnd"] * sr))
            m = y.mean(axis=0)
            steps = np.abs(np.diff(m[:L]))
            typical = float(np.percentile(steps, 99.9))
            seam = float(abs(m[L] - m[L - 1]))  # what plays: ... y[L-1] then y[loopStart=0]
            seam_wrap = float(abs(m[0] - m[L - 1]))
            n = int(0.25 * sr)
            post_err = float(np.sqrt(np.mean((y[:, L:L + n] - y[:, :n]) ** 2)))
            head_rms = float(np.sqrt(np.mean(y[:, :n] ** 2)))
            # click detector: >6 kHz energy in a 10 ms window straddling the played seam,
            # compared with the same measure over every 10 ms window of the loop
            from synth import hp as _hp
            w = int(0.005 * sr)
            seam_seg = np.concatenate([m[L - 4 * w:L], m[:4 * w]])
            hf_seam = _hp(seam_seg, 6000, 4)[3 * w:5 * w]
            hf_all = _hp(m[:L], 6000, 4)
            k = len(hf_all) // (2 * w)
            win_e = np.sqrt(np.mean(hf_all[: k * 2 * w].reshape(k, 2 * w) ** 2, axis=1))
            e_seam = float(np.sqrt(np.mean(hf_seam ** 2)))
            pct = float((win_e < e_seam).mean() * 100)
            r.update({"seam_jump": round(seam_wrap, 5), "p999_step": round(typical, 5),
                      "seam_hf_percentile": round(pct, 1),
                      "postpad_vs_head_err_db": round(db(post_err) - db(head_rms), 1)})
            if seam_wrap > typical:
                fails.append(f"{key}: seam jump {seam_wrap:.4f} > 99.9th pct step {typical:.4f}")
            if pct > 99.0:
                fails.append(f"{key}: seam HF energy at {pct:.1f}th percentile (possible click)")
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
