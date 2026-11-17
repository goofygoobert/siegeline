# Audio status

**Pirate re-theme complete** (2026-11-17). All 33 SFX ids and all 6 music ids from
`docs/asset-contract.md` are present as AAC `.m4a`, listed in `manifest.json`. The ids and the
manifest format are unchanged.

- Total size: 2.94 MB (target <= 3 MB).
- Checks (decoded AAC):
  - Peaks <= -1.3 dBFS.
  - No DC.
  - Nothing silent.
  - Decoded length == rendered length.
  - Zero encoder-delay offset.
  - Loop seams are continuous.
- Loops: one-beat pre-roll before `loopStart`, then 0.5 s of the loop head after `loopEnd`.
  Use `source.loop = true` with `loopStart` and `loopEnd` from the manifest.
- Files are written atomically: each is built under a temp name, then renamed into place.
- Rebuild: `.venv/bin/python tools/audio/sfx.py && .venv/bin/python tools/audio/music.py && .venv/bin/python tools/audio/check.py`
- Details: `docs/audio-notes.md`.
