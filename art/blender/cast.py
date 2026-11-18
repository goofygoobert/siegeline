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
    # carved figures (kit2): more frames, a held anticipation, the strike on frame 5
    "v2": [("idle", 8, 8, True, None), ("walk", 8, 12, True, None), ("attack", 10, 14, False, 5),
           ("hit", 4, 12, False, None), ("die", 10, 12, False, None)],
    "v2fast": [("idle", 8, 8, True, None), ("walk", 8, 16, True, None), ("attack", 10, 16, False, 5),
               ("hit", 4, 12, False, None), ("die", 10, 12, False, None)],
    "v2slow": [("idle", 8, 7, True, None), ("walk", 8, 9, True, None), ("attack", 10, 11, False, 5),
               ("hit", 4, 12, False, None), ("die", 10, 11, False, None)],
    "v2hero": [("idle", 8, 8, True, None), ("walk", 8, 12, True, None), ("attack", 10, 14, False, 5),
               ("hit", 4, 12, False, None), ("die", 10, 12, False, None), ("special", 10, 12, False, 5)],
    "v2boss": [("idle", 8, 7, True, None), ("walk", 8, 7, True, None), ("sweep", 12, 10, False, 8),
               ("summon", 10, 10, False, 6), ("spit", 10, 10, False, 6), ("hit", 4, 10, False, None),
               ("die", 14, 9, False, None)],
}

UNITS = ["ashguard", "torchbow", "cinder_runner", "bellringer", "maulwright", "lamplighter"]
ENEMIES = ["husk", "gnawer", "spitter", "bloater", "brute", "husk_warden"]
ICONS = ["i_ember_rain", "i_rally", "i_mark", "i_star", "i_star_empty", "i_energy", "i_lock"]
PORTRAITS = ["p_" + u for u in UNITS] + ["p_marshal"]

TIERED = UNITS + [u + "_t2" for u in UNITS] + [u + "_t3" for u in UNITS]
NEW_UNITS = ["harpooner", "netcaster"]; NEW_ENEMIES = ["gallows_gull", "bellback", "tide_nurse"]   # part 3 cast
V2_IDS = TIERED + ENEMIES + ["marshal", "cinder_matron"] + NEW_UNITS + [u + t for u in NEW_UNITS for t in ("_t2", "_t3")] + NEW_ENEMIES
ANIMSET_OF = {i: "v2" for i in V2_IDS}
ANIMSET_OF.update({"marshal": "v2hero", "cinder_matron": "v2boss", "cinder_runner": "v2fast", "cinder_runner_t2": "v2fast",
                   "cinder_runner_t3": "v2fast", "gnawer": "v2fast", "bloater": "v2slow", "brute": "v2slow",
                   "gallows_gull": "v2fast", "bellback": "v2slow"})

# ax: anchor x as a fraction of the cell (players; enemies use 1-ax), gy: ground px above the cell bottom
_FIELD = dict(cell=(1152, 912), cols=4, ppu=144, ax=0.5, gy=120, yaw=25, mode="anim")
_BOSS = dict(cell=(1568, 1232), cols=1, ppu=112, ax=0.45, gy=168, yaw=20, mode="anim")
JOBS = {
    # carved figures (kit2). Rendered at 144 px/u, packed at 96.
    "v2": dict(cell=(840, 624), cols=6, ppu=144, ax=0.5, gy=96, yaw=25, mode="anim", ids=TIERED),
    "v2field": dict(_FIELD, ids=["marshal"] + ENEMIES),
    "v2boss": dict(_BOSS, ids=["cinder_matron"]),
    # helpers' test jobs (same cells as the final jobs)
    "look_h1": dict(cell=(840, 624), cols=3, ppu=144, ax=0.5, gy=96, yaw=25, mode="anim", ids=["torchbow", "cinder_runner", "bellringer"]),
    "look_h2": dict(_FIELD, cols=3, ids=["maulwright", "lamplighter", "marshal"]),
    "look_h3": dict(_FIELD, cols=3, ids=["gnawer", "spitter", "bloater"]),
    "look_h4": dict(_FIELD, cols=2, ids=["brute", "husk_warden"]),
    "look_boss": dict(_BOSS, ids=["cinder_matron"]),
    "look_n1": dict(cell=(840, 624), cols=3, ppu=144, ax=0.5, gy=96, yaw=25, mode="anim", ids=["harpooner", "netcaster", "harpooner_t2", "netcaster_t2", "harpooner_t3", "netcaster_t3"]),
    "look_n2": dict(_FIELD, cols=3, ids=["gallows_gull", "bellback", "tide_nurse"]),
    "look": dict(cell=(840, 624), cols=2, ppu=144, ax=0.5, gy=96, yaw=25, mode="anim", ids=["ashguard", "husk"]),
    # ui: blanks ("_") between cells and an empty row so portrait bodies/props never spill into a neighbour
    "ui": dict(cell=(192, 192), cols=14, ppu=128, ax=0.5, gy=96, yaw=48, mode="still",
               ids=[x for p in PORTRAITS for x in (p, "_")] + ["_"] * 14 + [x for p in ICONS for x in (p, "_")]),
}

# atlas groups: name -> (job, ids, ppu). Pages overflow to <group>2, <group>3... Upgrade looks live in their own groups
# (unitsb = level 5, unitsc = level 10) so they load only when a unit has reached that level.
ATLASES = {
    "units": dict(job="v2", ids=UNITS, ppu=80, contour=0),
    "unitsb": dict(job="v2", ids=[u + "_t2" for u in UNITS], ppu=80, contour=0),
    "unitsc": dict(job="v2", ids=[u + "_t3" for u in UNITS], ppu=80, contour=0),
    "hero": dict(job="v2field", ids=["marshal"], ppu=80, contour=0),
    "enemies": dict(job="v2field", ids=ENEMIES, ppu=80, contour=0),
    "boss": dict(job="v2boss", ids=["cinder_matron"], ppu=64, contour=0),
    "ui": dict(job="ui", ids=PORTRAITS + ICONS, ppu=72, out_scale=1.0),
}


def anims_of(sid):
    return ANIMSETS["still"] if sid.startswith(("p_", "i_", "_")) else ANIMSETS[ANIMSET_OF.get(sid, "std")]


def is_enemy(sid):
    base = sid.split("_t")[0] if sid.endswith(("_t2", "_t3")) else sid
    return base in ENEMIES or base in NEW_ENEMIES or base == "cinder_matron"


def cell_anchor(job, sid):
    """Anchor (feet point) in cell px — multiples of 4 so the 0.75 downscale stays integral."""
    J = JOBS[job]; cw, ch = J["cell"]
    if J["mode"] == "still":
        return (cw // 2, ch // 2)
    fx = J["ax"] if not is_enemy(sid) else 1 - J["ax"]
    return (int(cw * fx) // 4 * 4, (ch - J["gy"]) // 4 * 4)


def job_frames(job):
    return max(sum(a[1] for a in anims_of(s)) for s in JOBS[job]["ids"] if s != "_")
