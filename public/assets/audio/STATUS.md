# Audio status

**First pass complete** (2026-11-17): all 33 SFX ids and all 6 music ids from
`docs/asset-contract.md` are present as AAC `.m4a`, listed in `manifest.json`.

- Total size: ~2.93 MB (target <= 3 MB).
- Checks (decoded AAC): peaks <= -1.3 dBFS, no DC, none silent, decoded length == rendered length,
  zero encoder-delay offset (mp4 edit list), loop seams continuous. See `docs/audio-notes.md`.
- Loops: `loopStart` 0, `loopEnd` = exact loop length; each file carries 0.5 s of the loop head after
  `loopEnd` as padding, so set `source.loop = true` with `loopStart`/`loopEnd` from the manifest.
- Rebuild: `.venv/bin/python tools/audio/sfx.py && .venv/bin/python tools/audio/music.py && .venv/bin/python tools/audio/check.py`
  (needs `numpy scipy av` in `.venv`; PyAV is used because the system ffmpeg has no AAC codec).
- Music still being refined (second pass); file names, ids and manifest format will not change.
