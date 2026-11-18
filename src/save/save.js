// Save system: on-device only. Versioned, checksummed, with a backup slot, migration and export/import.
// The design preview (served under /preview/) keeps its own save so it can never damage the live game's progress.
// On first run it starts from a copy of the live save, so existing progress carries in.
const PREVIEW = typeof location !== "undefined" && /\/preview\//.test(location.pathname);
const KEY = PREVIEW ? "siegeline.preview.save" : "siegeline.save", BAK = KEY + ".bak";
if (PREVIEW) try { const ls = window.localStorage; if (!ls.getItem(KEY) && ls.getItem("siegeline.save")) ls.setItem(KEY, ls.getItem("siegeline.save")); } catch {}
export const SAVE_VERSION = 3;

export function freshData() {
  return {
    marks: 0, totalMarks: 0,
    stages: {},                      // id -> { stars: [bool,bool,bool], best: seconds, clears: n }
    unitLevels: { ashguard: 1, torchbow: 1 },
    unlocked: { units: ["ashguard", "torchbow"], hero: false, abilities: [] },
    keep: 1, ballista: 1, energyMax: 1, energyRegen: 1, hero: 1, abilities: {},
    tutorials: [], seen: {},
    loadouts: {},                    // stage id -> last crew taken in
    skills: {},                      // crew id -> level-10 skill choice (0 or 1)
    tavern: [],                      // crew offered in the Tavern so far (bought ones move to unlocked.units)
    settings: { music: 0.6, sfx: 0.85, reducedMotion: false, largeText: false, speed: 1 },
    playTime: 0,
  };
}

// v1 -> v2: v1 stored stars as a number; v2 stores which of the three stars were earned.
const MIGRATIONS = {
  1: (d) => {
    for (const id in d.stages || {}) {
      const s = d.stages[id];
      if (typeof s.stars === "number") s.stars = [s.stars >= 1, s.stars >= 2, s.stars >= 3];
    }
    return d;
  },
  // v2 -> v3: region 1 grew from six stages to eight. Old progress moves to the stage that teaches the same thing
  // (old 3 Pufferghast Shoals is now 5, old 5 Wreckers' Reef is now 6); new stages 3 and 7 start unplayed but open.
  // Crew owned stay owned, and any free recruit already earned by a cleared stage is given.
  2: (d) => {
    const old = d.stages || {}, map = { r1s1: "r1s1", r1s2: "r1s2", r1s3: "r1s5", r1s4: "r1s4", r1s5: "r1s6", r1boss: "r1boss" }, out = {};
    for (const [o, n] of Object.entries(map)) if (old[o]) out[n] = old[o];
    d.stages = out;
    d.migratedFrom2 = true;
    return d;
  },
};

function checksum(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(36);
}

function wrap(data) {
  const body = JSON.stringify(data);
  return JSON.stringify({ v: SAVE_VERSION, ts: Date.now(), sum: checksum(body), data: body });
}

/** Returns {data, error} — error is null, or "invalid" when the text is not a usable save. */
export function unwrap(text) {
  try {
    const o = JSON.parse(text);
    if (!o || typeof o.data !== "string" || checksum(o.data) !== o.sum) return { data: null, error: "invalid" };
    let d = JSON.parse(o.data), v = o.v | 0;
    if (v > SAVE_VERSION) return { data: null, error: "newer" };
    while (v < SAVE_VERSION) { d = (MIGRATIONS[v] || ((x) => x))(d); v++; }
    return { data: repair(d), error: null };
  } catch { return { data: null, error: "invalid" }; }
}

/** Fill any missing fields from a fresh save so older or partial saves never crash the game. */
function repair(d) {
  const f = freshData();
  const out = { ...f, ...d };
  out.unlocked = { ...f.unlocked, ...(d.unlocked || {}) };
  out.settings = { ...f.settings, ...(d.settings || {}) };
  out.unitLevels = { ...f.unitLevels, ...(d.unitLevels || {}) };
  out.abilities = { ...(d.abilities || {}) };
  out.stages = d.stages || {};
  out.loadouts = { ...(d.loadouts || {}) };
  out.skills = { ...(d.skills || {}) };
  out.tavern = Array.isArray(d.tavern) ? d.tavern : [];
  if (!(out.marks >= 0)) out.marks = 0;
  return out;
}

function store() { try { return window.localStorage; } catch { return null; } }

export function load() {
  const ls = store();
  if (!ls) return { data: freshData(), note: "storage-off" };
  const main = ls.getItem(KEY);
  if (!main) return { data: freshData(), note: "new" };
  const a = unwrap(main);
  if (a.data) return { data: a.data, note: null };
  const b = unwrap(ls.getItem(BAK) || "");
  if (b.data) { ls.setItem(KEY, wrap(b.data)); return { data: b.data, note: "restored" }; }
  ls.setItem(KEY + ".broken", main);             // keep the damaged copy for rescue, start fresh
  return { data: freshData(), note: "corrupt" };
}

let pending = null;
export function save(data) {
  const ls = store(); if (!ls) return false;
  try {
    const prev = ls.getItem(KEY);
    if (prev && unwrap(prev).data) ls.setItem(BAK, prev);
    ls.setItem(KEY, wrap(data));
    return true;
  } catch { return false; }
}
/** Coalesce rapid saves (e.g. several upgrades in a row). */
export function saveSoon(data) { clearTimeout(pending); pending = setTimeout(() => save(data), 250); }

export function exportCode(data) {
  const raw = wrap(data);
  return "SGL" + SAVE_VERSION + ":" + btoa(unescape(encodeURIComponent(raw)));
}

export function importCode(text) {
  const t = (text || "").trim();
  let raw = t;
  const m = t.match(/^SGL\d+:(.+)$/s);
  if (m) { try { raw = decodeURIComponent(escape(atob(m[1].replace(/\s+/g, "")))); } catch { return { data: null, error: "invalid" }; } }
  return unwrap(raw);
}

export function wipe() { const ls = store(); if (ls) { ls.removeItem(KEY); ls.removeItem(BAK); } }
