# Cast data — PURE PYTHON (no bpy). Bundled into the Blender scripts and imported by tools/pack_sprites.py.
# Render jobs put many characters on one grid so a whole group renders in one gpu5070 job.

# anim sets: (name, frames, fps, loop, hit_frame_index or None)
ANIMSETS = {
    "std": [("idle", 6, 8, True, None), ("walk", 8, 10, True, None), ("attack", 8, 12, False, 4),
            ("hit", 4, 12, False, None), ("die", 8, 10, False, None)],
    "fast": [("idle", 6, 8, True, None), ("walk", 8, 15, True, None), ("attack", 8, 14, False, 4),
             ("hit", 4, 12, False, None), ("die", 8, 10, False, None)],
    "slow": [("idle", 6, 6, True, None), ("walk", 8, 7, True, None), ("attack", 8, 10, False, 4),
             ("hit", 4, 12, False, None), ("die", 8, 10, False, None)],
    "hero": [("idle", 6, 8, True, None), ("walk", 8, 10, True, None), ("attack", 8, 12, False, 4),
             ("hit", 4, 12, False, None), ("die", 8, 10, False, None), ("special", 8, 10, False, 4)],
    "boss": [("idle", 6, 6, True, None), ("walk", 6, 6, True, None), ("sweep", 12, 10, False, 8),
             ("summon", 8, 8, False, 5), ("spit", 8, 10, False, 5), ("hit", 3, 10, False, None),
             ("die", 9, 7, False, None)],
    "still": [("idle", 1, 1, True, None)],
}

UNITS = ["ashguard", "torchbow", "cinder_runner", "bellringer", "maulwright", "lamplighter"]
ENEMIES = ["husk", "gnawer", "spitter", "bloater", "brute", "husk_warden"]
ICONS = ["i_ember_rain", "i_rally", "i_mark", "i_star", "i_star_empty", "i_energy", "i_lock"]
PORTRAITS = ["p_" + u for u in UNITS] + ["p_marshal"]

ANIMSET_OF = {"marshal": "hero", "cinder_matron": "boss", "cinder_runner": "fast", "cinder_runner_t2": "fast",
              "cinder_runner_t3": "fast", "gnawer": "fast", "bloater": "slow", "brute": "slow"}

# ax: anchor x as a fraction of the cell (players; enemies use 1-ax), gy: ground px above the cell bottom
JOBS = {
    "units": dict(cell=(560, 480), cols=6, ppu=96, ax=0.48, gy=88, yaw=25, mode="anim",
                  ids=UNITS + [u + "_t2" for u in UNITS] + [u + "_t3" for u in UNITS]),
    "field": dict(cell=(672, 672), cols=4, ppu=96, ax=0.5, gy=100, yaw=25, mode="anim",
                  ids=["marshal"] + ENEMIES),
    "boss": dict(cell=(1024, 1024), cols=1, ppu=96, ax=0.44, gy=150, yaw=20, mode="anim", ids=["cinder_matron"]),
    # ui: blanks ("_") between cells and an empty row so portrait bodies/props never spill into a neighbour
    "ui": dict(cell=(192, 192), cols=14, ppu=128, ax=0.5, gy=96, yaw=48, mode="still",
               ids=[x for p in PORTRAITS for x in (p, "_")] + ["_"] * 14 + [x for p in ICONS for x in (p, "_")]),
}

# atlas groups: name -> (job, ids, ppu, out_scale). out_scale only for ui (render px -> atlas px).
ATLASES = {
    "units": dict(job="units", ids=JOBS["units"]["ids"], ppu=72,   # pages: units = base, units2 = _t2, units3 = _t3
                  pages=[UNITS, [u + "_t2" for u in UNITS], [u + "_t3" for u in UNITS]]),
    "hero": dict(job="field", ids=["marshal"], ppu=72),
    "enemies": dict(job="field", ids=ENEMIES, ppu=72),
    "boss": dict(job="boss", ids=["cinder_matron"], ppu=72),
    "ui": dict(job="ui", ids=PORTRAITS + ICONS, ppu=72, out_scale=0.5),
}


def anims_of(sid):
    return ANIMSETS["still"] if sid.startswith(("p_", "i_", "_")) else ANIMSETS[ANIMSET_OF.get(sid, "std")]


def is_enemy(sid):
    base = sid.split("_t")[0] if sid.endswith(("_t2", "_t3")) else sid
    return base in ENEMIES or base == "cinder_matron"


def cell_anchor(job, sid):
    """Anchor (feet point) in cell px — multiples of 4 so the 0.75 downscale stays integral."""
    J = JOBS[job]; cw, ch = J["cell"]
    if J["mode"] == "still":
        return (cw // 2, ch // 2)
    fx = J["ax"] if not is_enemy(sid) else 1 - J["ax"]
    return (int(cw * fx) // 4 * 4, (ch - J["gy"]) // 4 * 4)


def job_frames(job):
    return max(sum(a[1] for a in anims_of(s)) for s in JOBS[job]["ids"] if s != "_")
