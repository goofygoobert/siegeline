import "./ui/style.css";
import units from "../data/units.json";
import enemies from "../data/enemies.json";
import game from "../data/game.json";
import regions from "../data/regions.json";
import r1 from "../data/stages/r1.json";
import W from "../data/world.json";
import ROSTER from "../data/design/roster.json";
import { createBattle, step, input, canSend, stars as starCount } from "./sim/battle.js";
import { makeBot } from "./sim/bot.js";
import { unitStats, upgradeCost, tierFor } from "./sim/stats.js";
import { load, save, saveSoon, exportCode, importCode, wipe, freshData } from "./save/save.js";
import { initAudio, sfx, playMusic, setVolumes, duck, preload } from "./audio/audio.js";
import { createRenderer } from "./render/renderer.js";
import { loadGroup, loadAtlas as loadOne, loadBackgrounds, loadImageAsset, sprites } from "./render/assets.js";
const loadAtlas = (g, o) => loadGroup(g, o);

const content = { units, enemies, game, regions, stages: r1.stages, tutorials: r1.tutorials };
const stageById = Object.fromEntries(content.stages.map((s) => [s.id, s]));
const unitById = Object.fromEntries(units.units.map((u) => [u.id, u]));
const enemyById = Object.fromEntries(enemies.enemies.map((e) => [e.id, e]));
const abilityNames = W.abilities;
const SHORT = W.short;
const fill = (t, o) => t.replace(/\{(\w+)\}/g, (_, k) => o[k]);
const crewPlan = Object.fromEntries(ROSTER.crew.map((c) => [c.id, c]));        // strong / weak traits per crew member
const TRAITS = ROSTER.traits;

const ui = document.getElementById("ui");
const TEST = new URLSearchParams(location.search).has("test");
let testSpeed = 1, autoBot = null;
const canvas = document.getElementById("game");
let S = load();                       // { data, note }
let D = S.data;
const R = createRenderer(canvas, { theme: W.fx, sfx: (id, o) => sfx(id, o), duck, onBoss: (e) => battle && battle.onBoss(e), onSalvage: (n) => { if (battle) { const el = battle.energy; el.classList.remove("gain"); void el.offsetWidth; el.classList.add("gain"); const f = h("span", { class: "gainfx" }, "+" + n); el.append(f); setTimeout(() => f.remove(), 900); } }, onRush: () => battle && battle.callout(W.callouts.rush), onAngry: () => battle && battle.callout(W.callouts.angry), onBossWarn: (k) => battle && battle.bossWarn(k) });
initAudio(D.settings);
applySettings();

// ---------------------------------------------------------------- tiny DOM helpers
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") el.className = v; else if (k === "style") el.style.cssText = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v); else if (k === "html") el.innerHTML = v;
    else if (v !== false && v != null) el.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k.nodeType ? k : document.createTextNode(k));
  return el;
}
// rendered interface art (art/blender/bg/ui_art.py) and material textures (tools/ui_textures.py), exposed to the CSS
for (const [k, f] of Object.entries({ coin: "icons/coin.webp", cannon: "icons/cannon.webp", keg: "icons/keg.webp", wood: "ui/wood.webp", paper: "ui/parchment.webp" }))
  document.documentElement.style.setProperty("--img-" + k, `url("${new URL("assets/" + f, document.baseURI).href}")`);   // absolute: a url() inside a custom property resolves against the stylesheet that uses it
const artIcon = (k, cls = "art") => h("span", { class: cls + " art-" + k, "aria-hidden": "true" });
const I = {
  mug: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"><path d="M4 7h11v11a3 3 0 01-3 3H7a3 3 0 01-3-3z"/><path d="M15 10h2.5a2.5 2.5 0 010 5H15"/><path d="M5 4.5c1.5-1.5 3-1.5 4.5 0s3 1.5 4.5 0"/></svg>',
  back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
  gear: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M10.3 2.5h3.4l.5 2.6 1.9.8 2.2-1.5 2.4 2.4-1.5 2.2.8 1.9 2.6.5v3.4l-2.6.5-.8 1.9 1.5 2.2-2.4 2.4-2.2-1.5-1.9.8-.5 2.6h-3.4l-.5-2.6-1.9-.8-2.2 1.5-2.4-2.4 1.5-2.2-.8-1.9-2.6-.5v-3.4l2.6-.5.8-1.9-1.5-2.2 2.4-2.4 2.2 1.5 1.9-.8z"/><circle cx="12" cy="12" r="3.3"/></svg>',
  pause: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4.5" width="4" height="15" rx="1.2"/><rect x="14" y="4.5" width="4" height="15" rx="1.2"/></svg>',
  lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 018 0v2.5"/></svg>',
  hammer: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M14 4l6 6-3 3-6-6zM11 7L3.5 14.5a2 2 0 000 2.8l3.2 3.2a2 2 0 002.8 0L17 13"/></svg>',
  ballista: '<svg viewBox="0 0 48 48"><g transform="rotate(-22 22 26)"><path d="M6 20h6l2-2h20c4 0 7 1 9 3v6c-2 2-5 3-9 3H14l-2-2H6z" fill="#3b4048" stroke="#14161a" stroke-width="2" stroke-linejoin="round"/><rect x="15" y="17.5" width="3.5" height="13" rx="1" fill="currentColor"/><rect x="27" y="17.5" width="3.5" height="13" rx="1" fill="currentColor"/><rect x="39" y="19.5" width="3.5" height="9" rx="1" fill="currentColor"/><circle cx="5" cy="24" r="3.4" fill="currentColor" stroke="#14161a" stroke-width="1.5"/></g><path d="M10 33h20l3 6H7z" fill="#6a4426" stroke="#14161a" stroke-width="2" stroke-linejoin="round"/><circle cx="13" cy="40" r="5" fill="#8a5a2e" stroke="#14161a" stroke-width="2"/><circle cx="28" cy="40" r="5" fill="#8a5a2e" stroke="#14161a" stroke-width="2"/></svg>',
  rain: '<svg viewBox="0 0 48 48"><g fill="#ff9a40"><circle cx="14" cy="30" r="5"/><circle cx="28" cy="20" r="6"/><circle cx="36" cy="34" r="4.5"/></g><g stroke="#ffcf7a" stroke-width="2.4" stroke-linecap="round"><path d="M10 22l4 6M24 10l4 8M33 25l3 7"/></g></svg>',
  bell: '<svg viewBox="0 0 48 48"><path d="M24 8c-7 0-11 6-11 13v8l-4 6h30l-4-6v-8c0-7-4-13-11-13z" fill="#e0a84a" stroke="#6a4214" stroke-width="2"/><circle cx="24" cy="38" r="3.5" fill="#6a4214"/></svg>',
  speed: (s) => `<span style="font-size:14px">${s}×</span>`,
  phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="7" y="2.5" width="10" height="19" rx="2"/></svg>',
};
const icon = (svg, cls = "") => h("span", { class: "icon " + cls, html: svg });

function toast(text, ms = 2200) { const t = h("div", { class: "toast", role: "status" }, text); ui.append(t); setTimeout(() => t.remove(), ms); }

/** Portrait <img> cut from the ui atlas, or a coloured placeholder until art arrives. */
const portraitCache = {};
function portrait(id, size = 64) {
  const sp = sprites["p_" + id];
  if (sp) {
    if (!portraitCache[id]) {
      const fr = (sp.anims.idle || Object.values(sp.anims)[0]).frames[0];
      const c = document.createElement("canvas"); c.width = fr[2]; c.height = fr[3];
      c.getContext("2d").drawImage(sp.atlas.img, fr[0], fr[1], fr[2], fr[3], 0, 0, fr[2], fr[3]);
      portraitCache[id] = c.toDataURL();
    }
    return h("img", { src: portraitCache[id], alt: "", width: size, height: size, draggable: "false" });
  }
  const col = { ashguard: "#8c2a1e", torchbow: "#a6582a", cinder_runner: "#c4772f", bellringer: "#b08a3a", maulwright: "#5e6068", lamplighter: "#d8cdb8", marshal: "#c23a24" }[id] || "#5a4a40";
  return h("span", { class: "ph", style: `background:${col}` });
}
function iconImg(id, fallbackSvg) {
  const sp = sprites[id];
  if (sp) { const fr = sp.anims.idle.frames[0]; const c = document.createElement("canvas"); c.width = fr[2]; c.height = fr[3]; c.getContext("2d").drawImage(sp.atlas.img, fr[0], fr[1], fr[2], fr[3], 0, 0, fr[2], fr[3]); return h("img", { src: c.toDataURL(), alt: "" }); }
  return icon(fallbackSvg);
}
const coin = () => h("span", { class: "coin", "aria-hidden": "true" });

function applySettings() {
  document.documentElement.classList.toggle("large-text", !!D.settings.largeText);
  document.documentElement.classList.toggle("reduced", !!D.settings.reducedMotion);
  R.reduced = !!D.settings.reducedMotion || matchMedia("(prefers-reduced-motion: reduce)").matches;
  setVolumes(D.settings.music, D.settings.sfx);
}
function persist(now = false) { if (now) save(D); else saveSoon(D); }

// ---------------------------------------------------------------- screen manager
let current = null;
function clearCanvas() { const g = canvas.getContext("2d"); g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = "#0b1118"; g.fillRect(0, 0, canvas.width, canvas.height); }
function show(el) {
  if (!el.classList.contains("hud") && !el.classList.contains("loading")) clearCanvas();
  const old = current; current = el; ui.append(el);
  if (old) { old.classList.add("out"); setTimeout(() => old.remove(), 220); }
  for (const m of ui.querySelectorAll(".modal")) m.remove();
}
function tap(fn, sound = "ui_tap") { return (e) => { sfx(sound); fn(e); }; }
function topbar(title, backFn, extra = []) {
  return h("div", { class: "topbar" },
    backFn ? h("button", { class: "btn icon", "aria-label": "Back", onclick: tap(backFn, "ui_back") }, icon(I.back)) : null,
    h("div", { class: "title-s" }, title), h("div", { class: "spacer" }), ...extra,
    h("div", { class: "marks", "aria-label": W.currency }, coin(), h("span", { id: "markval" }, D.marks + "")),
    h("button", { class: "btn icon", "aria-label": "Settings", onclick: tap(() => openSettings()) }, icon(I.gear)));
}

// ---------------------------------------------------------------- progress helpers
const regionStages = content.stages.filter((s) => s.region === "r1");
const cleared = (id) => !!(D.stages[id] && D.stages[id].clears > 0);
const stageOpen = (i) => i === 0 || cleared(regionStages[i].id) || cleared(regionStages[i - 1].id);
const starsOf = (id) => (D.stages[id] && D.stages[id].stars) || [false, false, false];
const totalStars = () => regionStages.reduce((n, s) => n + starsOf(s.id).filter(Boolean).length, 0);
const owned = (id) => D.unlocked.units.includes(id);
/** Monsters of a stage in the order they first arrive (waves, then the loop, then the boss). */
function foesOf(s) {
  const seen = new Map();
  for (const w of [...s.waves].sort((a, b) => a.t - b.t)) if (!seen.has(w.id)) seen.set(w.id, w.t);
  for (const [id] of (s.loop ? s.loop.pool : [])) if (!seen.has(id)) seen.set(id, 1e3);
  const out = [...seen.keys()]; if (s.boss) out.unshift(s.boss);
  return out;
}
const tagsOf = (id) => enemyById[id].tags || [];
/** The first stage in the region where a trait appears: that stage introduces it. */
function firstWithTrait(tag) { return regionStages.find((st) => foesOf(st).some((f) => tagsOf(f).includes(tag))); }
/** Give every free recruit and Tavern offer earned by cleared stages (also repairs migrated saves). Returns new names. */
function syncRecruits() {
  const got = [];
  for (const st of regionStages) {
    if (!cleared(st.id)) continue;
    for (const u of st.unlocks) {
      if (unitById[u] && !owned(u)) { D.unlocked.units.push(u); D.unitLevels[u] = D.unitLevels[u] || 1; got.push({ id: u, how: "free" }); }
      else if (u === "hero" && !D.unlocked.hero) D.unlocked.hero = true;
      else if (game.abilities[u] && !D.unlocked.abilities.includes(u)) { D.unlocked.abilities.push(u); D.abilities[u] = D.abilities[u] || 1; }
    }
    for (const u of st.tavern || []) if (!owned(u) && !D.tavern.includes(u)) { D.tavern.push(u); got.push({ id: u, how: "tavern" }); }
  }
  return got;
}
const TICON = {
  plain: '<circle cx="12" cy="12" r="5"/>',
  swarm: '<circle cx="6" cy="15" r="3"/><circle cx="12" cy="9" r="3"/><circle cx="18" cy="15" r="3"/>',
  flying: '<path d="M2 14c4-6 8-7 10-3 2-4 6-3 10 3-4-2-7-1-10 3-3-4-6-5-10-3z"/>',
  siege: '<path d="M3 20c2-10 9-15 18-14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><circle cx="19" cy="7" r="3.2"/><rect x="2" y="17" width="7" height="5" rx="1"/>',
  exploder: '<path d="M12 2l2.2 6.2L20 5l-2.6 6.2L22 14l-6.3.6L16 22l-4-5-4 5 .3-7.4L2 14l4.6-2.8L4 5l5.8 3.2z"/>',
  armoured: '<path d="M12 2l8 3v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5z"/>',
  shelled: '<path d="M6 17c0-6 2-12 6-12s6 6 6 12z"/><rect x="4" y="17" width="16" height="3" rx="1.5"/><circle cx="12" cy="21.5" r="1.5"/>',
  healer: '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12 6c2.5 3.5 4 5.5 4 7.5a4 4 0 01-8 0c0-2 1.5-4 4-7.5z"/>',
  boss: '<path d="M3 18l2-11 4.5 5L12 5l2.5 7L19 7l2 11z"/><rect x="3" y="19" width="18" height="2.5" rx="1"/>',
};
const traitIcon = (tag) => h("span", { class: "ticon t-" + tag, "aria-hidden": "true", html: `<svg viewBox="0 0 24 24" fill="currentColor">${TICON[tag] || TICON.plain}</svg>` });
const traitName = (tag) => (TRAITS[tag] ? TRAITS[tag].name : tag === "boss" ? "Boss" : tag);
/** A still of any fighter (first idle frame), for monster portraits on the scouting strip. */
const figCache = {};
function figure(id) {
  const sp = sprites[id];
  if (!sp) return h("span", { class: "ph" });
  if (!figCache[id]) {
    const fr = (sp.anims.idle || Object.values(sp.anims)[0]).frames[0];
    const c = document.createElement("canvas"); c.width = fr[2]; c.height = fr[3];
    c.getContext("2d").drawImage(sp.atlas.img, fr[0], fr[1], fr[2], fr[3], 0, 0, fr[2], fr[3]);
    figCache[id] = c.toDataURL();
  }
  return h("img", { src: figCache[id], alt: "", draggable: "false" });
}

// ---------------------------------------------------------------- title
async function titleScreen() {
  playMusic("menu");
  const img = await loadImageAsset("title.webp");
  const el = h("div", { class: "screen" },
    h("div", { class: "bgimg", style: img ? `background-image:url(${img.src})` : "background:radial-gradient(ellipse at 70% 60%, #5a2414, #0b1118)" }),
    h("div", { class: "title-wrap" },
      h("h1", { class: "logo" }, W.title),
      h("p", { class: "tagline" }, W.tagline),
      h("div", { class: "row" },
        h("button", { class: "btn primary big", onclick: tap(() => worldMap()) }, cleared("r1s1") ? "Continue" : "Play"),
        h("button", { class: "btn icon big", "aria-label": "Settings", onclick: tap(() => openSettings()) }, icon(I.gear)))),
    null);
  show(el);
  if (S.note === "restored") toast("Your save was damaged. Restored the last good copy.", 4000);
  if (S.note === "corrupt") toast("Your save could not be read. Started fresh (the old copy was kept).", 5000);
  S.note = null;
}

// ---------------------------------------------------------------- world map
async function worldMap() {
  playMusic("map");
  const [img, wm] = await Promise.all([loadImageAsset("worldmap.webp"), fetch("assets/worldmap.json").then((r) => r.json()).catch(() => null)]);
  const pos = {}; (wm ? wm.regions : []).forEach((r) => (pos[r.id] = r));
  const fallback = [[0.16, 0.66], [0.3, 0.38], [0.46, 0.62], [0.6, 0.34], [0.74, 0.6], [0.87, 0.3]];
  const map = h("div", { class: "map", style: img ? `background-image:url(${img.src})` : "" });
  regions.regions.forEach((r, i) => {
    const p = pos[r.id] || { x: fallback[i][0], y: fallback[i][1] };
    const open = !!r.playable;
    map.append(h("button", { class: "pin" + (open ? "" : " locked"), style: `left:${p.x * 100}%;top:${p.y * 100}%`, "aria-label": r.name + (open ? "" : " (locked)"),
      onclick: open ? tap(() => regionScreen(r)) : tap(() => toast(`${r.name}: ${r.blurb.split(".")[0]}. Coming in a later update.`, 3200), "ui_locked") },
      h("span", { class: "dot" }), h("span", { class: "lbl" }, open ? `${r.name} · ${totalStars()}/${regionStages.length * 3}` : h("span", { style: "display:inline-flex;align-items:center;gap:4px" }, h("span", { class: "icon", style: "width:12px;height:12px;display:inline-block;margin-right:3px", html: I.lock.replace('<svg', '<svg width="12" height="12"') }), r.name)),
      open && cleared("r1boss") ? h("span", { class: "cleared" }, "Cleared") : null));
  });
  const ann = D.seen.regionCleared === "new" ? h("div", { class: "announce", role: "status" }, h("b", {}, W.regionCleared.title),
    W.regionCleared.text,
    h("div", { style: "margin-top:10px" }, h("button", { class: "btn primary", onclick: tap(() => ann.remove()) }, "Aye"))) : null;
  if (ann) { D.seen.regionCleared = "shown"; persist(); }
  show(h("div", { class: "screen" }, ann,
    topbar(W.mapTitle, titleScreen, [h("button", { class: "btn", onclick: tap(() => armoury(worldMap)) }, icon(I.hammer), W.armoury.title)]),
    map));
}

// ---------------------------------------------------------------- region / stage select
async function regionScreen(region) {
  playMusic("map");
  await loadAtlas("ui", { white: false });
  const bgs = await loadBackgrounds("r1");
  const pts = [[0.08, 0.72], [0.19, 0.42], [0.31, 0.7], [0.43, 0.4], [0.55, 0.7], [0.67, 0.4], [0.78, 0.68], [0.9, 0.38]];
  const path = h("div", { class: "path" });
  const svgPts = pts.map(([x, y]) => `${x * 100},${y * 100}`).join(" ");
  path.append(h("svg", { class: "pathline", viewBox: "0 0 100 100", preserveAspectRatio: "none", html: `<polyline points="${svgPts}" fill="none" stroke="#2a1b11" stroke-width="2.2" stroke-linecap="round" vector-effect="non-scaling-stroke" style="stroke-width:9px"/><polyline points="${svgPts}" fill="none" stroke="#d9bb82" stroke-linecap="round" stroke-dasharray="7 5" vector-effect="non-scaling-stroke" style="stroke-width:5px"/>` }));
  let nextIdx = regionStages.findIndex((s, i) => stageOpen(i) && !cleared(s.id));
  regionStages.forEach((s, i) => {
    const open = stageOpen(i), st = starsOf(s.id);
    const node = h("button", { class: "node" + (s.boss ? " boss" : "") + (open ? "" : " locked") + (i === nextIdx ? " next" : ""),
      style: `left:${pts[i][0] * 100}%;top:${pts[i][1] * 100}%`, "aria-label": `${s.name}${open ? "" : " (locked)"}`,
      onclick: open ? tap(() => prepScreen(s, region)) : tap(() => toast("Clear the stage before this one first."), "ui_locked") },
      s.boss ? "☠︎" : String(i + 1),
      h("span", { class: "st" }, ...st.map((on) => h("i", { class: on ? "on" : "" }))),
      open ? h("span", { class: "nm" }, s.name) : null);
    if (!open) node.prepend(icon(I.lock));
    if (!open) node.childNodes[1].remove();
    path.append(node);
  });
  const back = bgs && (bgs.mid || bgs.far);
  show(h("div", { class: "screen" },
    h("div", { class: "bgimg cove", style: back ? `background-image:${["near", "mid", "far", "sky"].filter((k) => bgs[k]).map((k) => `url(${bgs[k].img.src})`).join(",")}` : "background:linear-gradient(#2a1418,#8a3a1a)" }),
    topbar(region.name, worldMap, [
      D.tavern.length || regionStages.some((st) => st.tavern) ? h("button", { class: "btn" + (D.tavern.some((u) => !owned(u)) ? " has-new" : ""), "aria-label": W.tavern.title, onclick: tap(() => tavern(() => regionScreen(region))) }, icon(I.mug), h("span", { class: "lbl" }, W.tavern.title)) : null,
      h("button", { class: "btn", "aria-label": W.armoury.title, onclick: tap(() => armoury(() => regionScreen(region))) }, icon(I.hammer), h("span", { class: "lbl" }, W.armoury.title))]),
    path));
}

/** Scouting + loadout: who you will face (in arrival order, with their traits) and who you take in. Tapping a
 *  monster lights the crew who answer it and dims the ones it beats, straight from the counter data. */
async function prepScreen(s, region, preset) {
  await Promise.all([loadAtlas("ui", { white: false }), loadAtlas("enemies", { white: false }), s.boss ? loadAtlas("boss", { white: false }) : null]);
  const idx = regionStages.indexOf(s), slots = s.slots || 5, first = !cleared(s.id);
  const reward = first ? s.reward : Math.round(s.reward * game.rewards.replayFraction);
  const crew = units.units.filter((u) => owned(u.id));
  let pick = (preset || D.loadouts[s.id] || D.loadouts._last || []).filter(owned).slice(0, slots);
  if (!pick.length) pick = crew.slice(0, slots).map((u) => u.id);
  const foes = foesOf(s);
  let focus = null;
  const strip = h("div", { class: "scout", role: "list", "aria-label": "Monsters in this battle, in the order they arrive" });
  const roster = h("div", { class: "roster" });
  const fightBtn = h("button", { class: "btn primary big", onclick: tap(() => { if (!pick.length) return; D.loadouts[s.id] = pick.slice(); D.loadouts._last = pick.slice(); persist(); startBattle(s, pick); }),
    "aria-label": `Fight. ${first ? "First clear" : "Replay"} pays ${reward} ${W.currency}` }, "Fight", h("span", { class: "reward" }, "+", coin(), reward + ""));
  const verdict = (u) => {
    if (!focus) return "";
    const tags = tagsOf(focus), c = crewPlan[u];
    if (!c) return "";
    if (tags.some((t) => c.strong.includes(t))) return "good";
    if (tags.some((t) => c.weak.includes(t))) return "bad";
    return "";
  };
  function render() {
    strip.replaceChildren(...foes.map((f) => {
      const tags = tagsOf(f), isNew = tags.some((t) => t !== "plain" && t !== "boss" && firstWithTrait(t) === s);
      return h("button", { class: "foe" + (focus === f ? " on" : "") + (isNew ? " new" : ""), role: "listitem", "aria-pressed": focus === f,
        "aria-label": `${enemyById[f].name}: ${tags.map(traitName).join(", ")}. Show who answers it.`, onclick: tap(() => { focus = focus === f ? null : f; render(); }) },
        h("span", { class: "pic" }, figure(f)), h("b", {}, enemyById[f].name),
        h("span", { class: "tags" }, ...tags.filter((t) => t !== "plain").map((t) => h("span", { class: "tag" }, traitIcon(t), traitName(t)))),
        isNew ? h("span", { class: "newflag" }, "New") : null);
    }));
    const ft = focus ? tagsOf(focus).filter((t) => TRAITS[t] && t !== "plain") : [];
    const newTag = foes.flatMap(tagsOf).find((t) => TRAITS[t] && t !== "plain" && firstWithTrait(t) === s);
    hint.replaceChildren(...(ft.length ? [h("b", {}, traitName(ft[0]) + ": "), TRAITS[ft[0]].rule]
      : newTag ? [h("b", {}, "New: " + traitName(newTag) + ". "), TRAITS[newTag].rule] : [s.teaches || ""]));
    roster.replaceChildren(...crew.map((u) => {
      const inT = pick.includes(u.id), v = verdict(u.id);
      return h("button", { class: "rcard" + (inT ? " in" : "") + (v ? " " + v : ""), "aria-pressed": inT,
        "aria-label": `${u.name}, ${u.cost} ${W.energy}${v === "good" ? ", answers it" : v === "bad" ? ", weak against it" : ""}. ${inT ? "Remove from" : "Add to"} the crew.`,
        onclick: tap(() => { if (inT) pick = pick.filter((x) => x !== u.id); else if (pick.length < slots) pick.push(u.id); else { sfx("ui_locked"); toast(`Only ${slots} places on this stage. Tap a crew member above to take them out.`); return; } render(); }) },
        h("span", { class: "pic" }, portrait(u.id, 56), h("span", { class: "lvb" }, (D.unitLevels[u.id] || 1) + "")),
        h("b", {}, SHORT[u.id] || u.name), h("span", { class: "cost" }, h("span", { class: "fl" }), u.cost + ""),
        v === "good" ? h("span", { class: "verdict" }, "Answers it") : v === "bad" ? h("span", { class: "verdict" }, "Weak to it") : null);
    }));
    fightBtn.disabled = !pick.length || null;
    count.textContent = pick.length ? `${pick.length} of ${slots} places filled` : "Tap crew to take them in";
  }
  const hint = h("p", { class: "scout-hint", role: "status" });
  const count = h("span", { class: "muted count", role: "status" });
  render();
  const st = starsOf(s.id);
  show(h("div", { class: "screen prep" },
    topbar(s.boss ? "Boss · " + s.name : `Stage ${idx + 1} · ${s.name}`, () => regionScreen(region)),
    h("div", { class: "prep-body" },
      h("section", { class: "panel paper scouting" }, h("h3", {}, "You'll face"), strip, hint),
      h("section", { class: "panel paper loadout" },
        h("div", { class: "row" }, h("h3", {}, "Your crew"), h("div", { class: "spacer" }),
          h("span", { class: "starmini", "aria-label": `${st.filter(Boolean).length} of 3 stars` }, ...st.map((on) => h("i", { class: on ? "on" : "" })))),
        roster,
        h("div", { class: "row prep-foot" }, count, h("div", { class: "spacer" }), fightBtn)))));
}

// ---------------------------------------------------------------- tavern (crew bought with doubloons)
async function tavern(backFn) {
  await loadAtlas("ui", { white: false });
  const list = h("div", { class: "list" });
  function render() {
    const offers = D.tavern.map((id) => unitById[id]).filter(Boolean);
    document.getElementById("markval") && (document.getElementById("markval").textContent = D.marks);
    list.replaceChildren(...(offers.length ? offers.map((u) => {
      const have = owned(u.id), c = crewPlan[u.id] || { strong: [], weak: [] }, price = u.price || 400, can = D.marks >= price;
      return h("div", { class: "card tav" + (have ? " owned" : can ? " can" : "") },
        h("div", { class: "pic" }, portrait(u.id)),
        h("div", {}, h("h3", {}, u.name), h("div", { class: "role" }, `${u.role} · ${u.cost} ${W.energy}`),
          h("p", { class: "job" }, c.job || ""),
          h("div", { class: "tags" }, h("small", {}, "Answers"), ...c.strong.map((t) => h("span", { class: "tag" }, traitIcon(t), traitName(t))))),
        have ? h("span", { class: "owned-mark" }, "Aboard")
          : h("button", { class: "btn upbtn" + (can ? " primary" : " short"), "aria-label": `Recruit ${u.name} for ${price} ${W.currency}`,
            onclick: () => { if (!can) { sfx("ui_locked"); toast(`${price - D.marks} more ${W.currency} needed. Replays earn them too.`); return; }
              D.marks -= price; D.unlocked.units.push(u.id); D.unitLevels[u.id] = D.unitLevels[u.id] || 1; sfx("ui_upgrade"); persist(); toast(`${u.name} joins the crew.`); render(); } },
            "Recruit", h("small", {}, coin(), price + ""), can ? null : h("em", {}, `need ${price - D.marks} more`)));
    }) : [h("p", { class: "note empty" }, W.tavern.empty)]));
  }
  render();
  show(h("div", { class: "screen qm tavern" }, topbar(W.tavern.title, backFn), h("p", { class: "note tav-note" }, W.tavern.note), list));
}

// ---------------------------------------------------------------- armoury (upgrades)
let armouryTab = "units";
let lastCrew = null;
async function armoury(backFn) {
  await loadAtlas("ui", { white: false });
  const tabs = h("div", { class: "tabs", role: "tablist" });
  const list = h("div", { class: "list" });
  const setTab = (t) => { armouryTab = t; render(); };
  const mkTab = (id, label, can) => h("button", { class: "tab" + (armouryTab === id ? " on" : ""), role: "tab", "aria-selected": armouryTab === id, onclick: tap(() => setTab(id)) }, label, can ? h("span", { class: "dot", "aria-label": can + " upgrades you can afford" }, can + "") : null);
  /** One upgrade row. o: {pic, title, role, lvl, max, stats: [[label, now, next]], miles, note, cost, buy, locked, hint} */
  function upRow(o) {
    const maxed = o.lvl >= o.max, can = !o.locked && !maxed && D.marks >= o.cost, shortBy = o.cost - D.marks;
    const btn = h("button", { class: "btn upbtn" + (can ? " primary" : maxed ? " maxed" : " short"), disabled: maxed || null,
      "aria-label": maxed ? `${o.title} is at its highest level` : `Upgrade ${o.title} for ${o.cost} ${W.currency}`,
      onclick: () => { if (D.marks < o.cost) { sfx("ui_locked"); toast(`${shortBy} more ${W.currency} needed. Replay a stage to earn them.`); return; }
        D.marks -= o.cost; o.buy(); sfx("ui_upgrade"); persist(); render(); const c = list.querySelector(`[data-k="${o.title}"]`); if (c) c.classList.add("pop"); } },
      maxed ? "Highest level" : "Upgrade", maxed ? null : h("small", {}, coin(), o.cost + ""), !maxed && !can ? h("em", {}, `need ${shortBy} more`) : null);
    const pips = h("div", { class: "pips", "aria-label": `Level ${o.lvl} of ${o.max}` });
    for (let i = 1; i <= o.max; i++) pips.append(h("i", { class: (i <= o.lvl ? "on" : "") + (o.miles && (i === 5 || i === 10) ? " mile" : "") }));

    const choose = o.choose ? h("div", { class: "choose", role: "group", "aria-label": "Choose a level 10 skill" }, h("small", {}, "Choose a skill (for good):"),
      ...o.choose.opts.map((x, i) => h("button", { class: "btn skillbtn", onclick: tap(() => { D.skills[o.choose.id] = i; sfx("ui_upgrade"); persist(); render(); }) }, h("b", {}, x.name), h("span", {}, x.text)))) : null;
    return h("div", { class: "card" + (o.locked ? " locked" : can ? " can" : ""), "data-k": o.title },
      h("div", { class: "pic" }, o.pic, o.locked ? null : h("span", { class: "lvb" }, o.lvl + "")),
      h("div", {}, h("h3", {}, o.title), o.role ? h("div", { class: "role" }, o.role) : null,
        o.locked ? h("div", { class: "hint" }, o.hint) : h("div", { class: "stats" }, ...o.stats.map(([k, a, b]) => h("span", { class: "stat" }, h("small", {}, k), a + "", !maxed && b != null && b + "" !== a + "" ? h("b", {}, "→ " + b) : null))),
        o.locked ? null : pips, o.locked || !o.note ? null : h("div", { class: "skill" }, o.note), choose),
      o.locked ? icon(I.lock) : btn);
  }
  function rows(tab) {
    const out = [];
    if (tab === "units") {
      for (const u of units.units.filter((u) => u.region === 1)) {
        const locked = !D.unlocked.units.includes(u.id), L = D.unitLevels[u.id] || 1;
        const a = unitStats(u, L, units.levels), b = unitStats(u, L + 1, units.levels), heal = u.id === "lamplighter";
        const sk = u.skills || {}, ch = D.skills[u.id];
        const skill = L < 5 ? (sk["5"] ? `Level 5: learns ${sk["5"].name}` : "") : L < 10 ? `${sk["5"].name}: ${sk["5"].text} Level 10: choose ${sk["10"].map((x) => x.name).join(" or ")}` : `${sk["5"].name}${ch != null ? " · " + sk["10"][ch].name : ""}`;
        out.push({ pic: portrait(u.id), title: u.name, role: `${u.role} · ${u.cost} ${W.energy}`, lvl: L, max: 10, miles: true,
          stats: [["HP", Math.round(a.hp), Math.round(b.hp)], [heal ? "Heal" : "Dmg", Math.round(heal ? a.traits.heal : a.dmg), Math.round(heal ? b.traits.heal : b.dmg)]],
          note: skill, choose: L >= 10 && ch == null && sk["10"] ? { id: u.id, opts: sk["10"] } : null,
          cost: upgradeCost("unit", L, game), buy: () => (D.unitLevels[u.id] = L + 1), locked, hint: unlockHint(u.id) });
      }
    } else if (tab === "keep") {
      const k = D.keep, bl = D.ballista, em = D.energyMax, er = D.energyRegen, gb = game.ballista, ge = game.energy;
      const keg = (c) => h("span", { style: `display:block;width:30px;height:36px;border-radius:8px/14px;background:linear-gradient(90deg,#5a3516,${c} 45%,#6a421c);box-shadow:inset 0 9px 0 -6px #2a1a10,inset 0 -9px 0 -6px #2a1a10` });
      out.push({ pic: icon(I.shield || I.lock), title: W.armoury.keepWalls, role: `The ${W.keep} takes more of a beating`, lvl: k, max: 10, stats: [["Fort HP", game.keep.hp + game.keep.hpPerLevel * (k - 1), game.keep.hp + game.keep.hpPerLevel * k]], cost: upgradeCost("keep", k, game), buy: () => D.keep++ });
      out.push({ pic: artIcon("cannon"), title: W.armoury.weapon, role: "Your cannon: harder hits, faster reload", lvl: bl, max: 10,
        stats: [["Dmg", Math.round(gb.dmg * (1 + gb.dmgPerLevel * (bl - 1))), Math.round(gb.dmg * (1 + gb.dmgPerLevel * bl))], ["Reload", Math.max(1.2, gb.reload - gb.reloadPerLevel * (bl - 1)).toFixed(2) + "s", Math.max(1.2, gb.reload - gb.reloadPerLevel * bl).toFixed(2) + "s"]],
        cost: upgradeCost("ballista", bl, game), buy: () => D.ballista++ });
      out.push({ pic: artIcon("keg"), title: W.armoury.store, role: `Hold more ${W.energy} between sends`, lvl: em, max: ge.maxLevel, stats: [["Holds", ge.max + ge.maxPerLevel * (em - 1), ge.max + ge.maxPerLevel * em]], cost: upgradeCost("energyMax", em, game), buy: () => D.energyMax++ });
      out.push({ pic: h("span", { class: "kegs" }, artIcon("keg"), artIcon("keg")), title: W.armoury.flow, role: `${W.energy[0].toUpperCase() + W.energy.slice(1)} arrives faster`, lvl: er, max: ge.maxLevel, stats: [["Per second", (ge.regen + ge.regenPerLevel * (er - 1)).toFixed(1), (ge.regen + ge.regenPerLevel * er).toFixed(1)]], cost: upgradeCost("energyRegen", er, game), buy: () => D.energyRegen++ });
    } else {
      const hl = D.hero, hg = game.hero;
      out.push({ pic: portrait("marshal"), title: hg.name, role: "Hero · flare pistol stuns nearby monsters", lvl: hl, max: hg.maxLevel,
        stats: [["HP", Math.round(hg.hp * (1 + hg.hpPerLevel * (hl - 1))), Math.round(hg.hp * (1 + hg.hpPerLevel * hl))], ["Dmg", Math.round(hg.dmg * (1 + hg.dmgPerLevel * (hl - 1))), Math.round(hg.dmg * (1 + hg.dmgPerLevel * hl))]],
        cost: upgradeCost("hero", hl, game), buy: () => D.hero++, locked: !D.unlocked.hero, hint: unlockHint("hero") });
      for (const id of ["ember_rain", "rally"]) {
        const a = game.abilities[id], L = D.abilities[id] || 1, rain = id === "ember_rain";
        out.push({ pic: iconImg("i_" + id, rain ? I.rain : I.bell), title: abilityNames[id], role: rain ? `${a.stones} cannonballs where you tap · every ${a.cooldown}s` : `Crew fights faster and heals · every ${a.cooldown}s`, lvl: L, max: a.maxLevel,
          stats: rain ? [["Dmg each", Math.round(a.dmg * (1 + a.dmgPerLevel * (L - 1))), Math.round(a.dmg * (1 + a.dmgPerLevel * L))]] : [["Lasts", (a.time + a.timePerLevel * (L - 1)).toFixed(1) + "s", (a.time + a.timePerLevel * L).toFixed(1) + "s"]],
          cost: upgradeCost("ability", L, game), buy: () => (D.abilities[id] = L + 1), locked: !D.unlocked.abilities.includes(id), hint: unlockHint(id) });
      }
    }
    return out;
  }
  const affordable = (tab) => rows(tab).filter((o) => !o.locked && o.lvl < o.max && D.marks >= o.cost).length;
  function render() {
    tabs.replaceChildren(mkTab("units", "Crew", affordable("units")), mkTab("keep", `${W.keep} & ${W.weapon}`, affordable("keep")), mkTab("hero", "Captain & Powers", affordable("hero")));
    document.getElementById("markval") && (document.getElementById("markval").textContent = D.marks);
    list.replaceChildren(...rows(armouryTab).map(upRow));
  }
  render();
  show(h("div", { class: "screen qm" }, topbar(W.armoury.title, backFn), tabs, list));
}

// ---------------------------------------------------------------- settings
function openSettings(onClose) {
  const tgl = (key, label) => {
    const b = h("button", { class: "toggle" + (D.settings[key] ? " on" : ""), role: "switch", "aria-checked": !!D.settings[key], "aria-label": label,
      onclick: tap(() => { D.settings[key] = !D.settings[key]; b.classList.toggle("on", D.settings[key]); b.setAttribute("aria-checked", D.settings[key]); applySettings(); persist(); }) });
    return h("div", { class: "setting" }, h("span", {}, label), b);
  };
  const slider = (key, label) => h("div", { class: "setting" }, h("span", {}, label),
    h("input", { type: "range", min: 0, max: 1, step: 0.05, value: D.settings[key], "aria-label": label,
      oninput: (e) => { D.settings[key] = +e.target.value; applySettings(); }, onchange: () => { persist(); sfx("ui_tap"); } }));
  const io = h("div", { style: "display:flex;flex-direction:column;gap:8px" });
  const m = h("div", { class: "modal", onclick: (e) => { if (e.target === m) close(); } },
    h("div", { class: "panel settings-panel", role: "dialog", "aria-label": "Settings" },
      h("div", { class: "row" }, h("h2", {}, "Settings"), h("div", { class: "spacer" }), h("button", { class: "btn icon", "aria-label": "Close", onclick: tap(() => close(), "ui_back") }, h("span", { html: "&#x2715;" }))),
      slider("music", "Music"), slider("sfx", "Sound effects"), tgl("reducedMotion", "Reduced motion (no shake or flashes)"), tgl("largeText", "Larger text"),
      h("div", { class: "row", style: "flex-wrap:wrap" },
        h("button", { class: "btn", onclick: tap(() => exportUI(io)) }, "Export save"),
        h("button", { class: "btn", onclick: tap(() => importUI(io)) }, "Import save")),
      io,
      h("button", { class: "danger-link", onclick: tap(() => resetUI(io)) }, "Reset progress\u2026"),
      h("p", { class: "note", style: "margin:0" }, "Progress saves automatically on this device. Export a code or file to move it to another phone or keep a backup."),
      h("p", { class: "note ver", style: "margin:0" }, "Version " + (import.meta.env.VITE_VERSION || "0.1"))));
  function close() { m.remove(); onClose && onClose(); }
  ui.append(m);
}
function exportUI(box) {
  const code = exportCode(D);
  const ta = h("textarea", { readonly: true, "aria-label": "Save code" }, code);
  const blob = new Blob([code], { type: "text/plain" });
  box.replaceChildren(ta, h("div", { class: "row" },
    h("button", { class: "btn", onclick: tap(async () => { try { await navigator.clipboard.writeText(code); toast("Save code copied."); } catch { ta.select(); toast("Select the code and copy it."); } }) }, "Copy code"),
    h("a", { class: "btn", href: URL.createObjectURL(blob), download: `siegeline-save-${new Date().toISOString().slice(0, 10)}.txt` }, "Download file")));
}
function importUI(box) {
  const ta = h("textarea", { placeholder: "Paste a save code here", "aria-label": "Save code to import" });
  const file = h("input", { type: "file", accept: ".txt,.json,text/plain", style: "display:none", onchange: async (e) => { const f = e.target.files[0]; if (f) { ta.value = await f.text(); doImport(); } } });
  function doImport() {
    const r = importCode(ta.value);
    if (!r.data) { sfx("ui_locked"); toast(r.error === "newer" ? "That save is from a newer version of the game." : "That code isn't a valid Siegeline save. Check it was copied in full."); return; }
    D = r.data; S.data = D; save(D, true); applySettings(); sfx("ui_upgrade"); toast("Save imported."); for (const m of ui.querySelectorAll(".modal")) m.remove(); worldMap();
  }
  box.replaceChildren(ta, file, h("div", { class: "row" }, h("button", { class: "btn primary", onclick: tap(doImport) }, "Import"), h("button", { class: "btn", onclick: tap(() => file.click()) }, "Choose file")));
}
function resetUI(box) {
  box.replaceChildren(h("p", { class: "note", style: "margin:0" }, `This deletes all stars, ${W.currency} and upgrades on this device. Export first if you might want them back.`),
    h("div", { class: "row" }, h("button", { class: "btn", style: "background:#7a1a14", onclick: tap(() => { wipe(); D = freshData(); S.data = D; save(D); applySettings(); for (const m of ui.querySelectorAll(".modal")) m.remove(); toast("Progress reset."); titleScreen(); }) }, "Delete my progress"),
      h("button", { class: "btn", onclick: tap(() => box.replaceChildren()) }, "Keep it")));
}

// ---------------------------------------------------------------- battle
let battle = null;

async function startBattle(stage, crew) {
  crew = (crew || D.loadouts[stage.id] || D.loadouts._last || D.unlocked.units).filter(owned).slice(0, stage.slots || 5);
  lastCrew = crew;
  const loading = h("div", { class: "screen loading" }, h("div", { style: "text-align:center" }, h("div", { class: "title-s", style: "margin-bottom:12px" }, stage.name), h("div", { class: "bar" }, h("i", { style: "transform:scaleX(.1)" }))));
  show(loading);
  const bar = loading.querySelector(".bar > i");
  // load only what this battle needs: upgrade-look pages only once a unit reaches level 5 / 10
  const groups = ["units", "enemies", "castles", "fx", "ui"]; if (D.unlocked.hero) groups.push("hero"); if (stage.boss) groups.push("boss");
  const tiers = crew.map((u) => tierFor(D.unitLevels[u] || 1));
  const pages = groups.map((g) => [g, true]);
  if (tiers.some((t) => t >= 2)) pages.push(["unitsb", true]); if (tiers.some((t) => t >= 3)) pages.push(["unitsc", true]);
  let n = 0; const tick = () => { n++; bar.style.transform = `scaleX(${0.1 + 0.9 * n / (pages.length + 1)})`; };
  await Promise.all([...pages.map(([g, all]) => (all ? loadAtlas(g, { white: false }) : loadOne(g)).then(tick)), loadBackgrounds(stage.bg).then(tick), stage.bg !== "r1" ? loadBackgrounds("r1") : null]);
  preload(["hit_blade", "hit_claw", "hit_blunt", "arrow_fire", "arrow_hit", "bolt_fire", "bolt_hit", "hollow_die", "warden_die", "castle_hit", "spit", "ballista_reload", "denied", "bloater_burst", "boss_roar", "boss_warn", "boss_slam", "win", "lose", "star", "coin", "hero_call", "hero_flare", "rally", "ember_rain", "heal", "energy_full", "castle_crumble"]);
  const st = { ...stage, available: crew, hero: D.unlocked.hero, abilities: D.unlocked.abilities.slice() };
  const prog = { unitLevels: D.unitLevels, keep: D.keep, ballista: D.ballista, energyMax: D.energyMax, energyRegen: D.energyRegen, hero: D.hero, abilities: D.abilities, skills: D.skills };
  const seedQ = new URLSearchParams(location.search).get("seed");
  const B = createBattle(content, st, prog, seedQ ? +seedQ : (Math.random() * 1e9) | 0);
  R.resetForBattle(); R.region = stage.bg; R.grade = (W.fx.grades || {})[stage.bg] || null;
  battle = new BattleView(B, stage);
  playMusic(stage.music || "battle");
}

class BattleView {
  constructor(B, stage) {
    this.B = B; this.stage = stage; this.acc = 0; this.last = performance.now(); this.paused = false; this.speed = D.settings.speed || 1; this.over = false;
    this.armed = null; this.tutor = null;
    this.el = this.buildHud(); show(this.el);
    this.bindCanvas();
    const tut = stage.tutorial && !D.tutorials.includes(stage.tutorial) ? content.tutorials[stage.tutorial] : null;
    if (tut) this.tutor = { steps: tut, i: 0, shown: null, t0: 0, flags: {} };
    if (!this.tutor) this.callout(stage.boss ? W.callouts.bossStart : W.callouts.start);
    this.raf = requestAnimationFrame((t) => this.frame(t));
    this.vis = () => { if (document.hidden && !this.over) this.pause(true); };
    document.addEventListener("visibilitychange", this.vis);
  }
  buildHud() {
    const B = this.B;
    this.hpKeep = h("div", { class: "hp" }, h("div", { class: "lbl" }, h("span", {}, W.keep), h("span", { class: "v" })), h("div", { class: "bar" }, h("u"), h("i")));
    this.hpGate = h("div", { class: "hp enemy" }, h("div", { class: "lbl" }, h("span", {}, B.gate.sealed ? W.gate + " · sealed" : W.gate), h("span", { class: "v" })), h("div", { class: "bar" }, h("u"), h("i")));
    this.speedBtn = h("button", { class: "pill", "aria-label": "Game speed", onclick: tap(() => { this.speed = this.speed === 1 ? 2 : 1; D.settings.speed = this.speed; persist(); this.speedBtn.innerHTML = I.speed(this.speed); }) });
    this.speedBtn.innerHTML = I.speed(this.speed);
    this.timer = h("div", { class: "pill", style: "pointer-events:none", "aria-label": "Battle time" }, "0:00");
    const top = h("div", { class: "hud-top" }, this.hpKeep, h("div", { class: "spacer" }), h("div", { class: "hud-mid" }, this.timer, this.speedBtn,
      h("button", { class: "pill", "aria-label": "Pause", onclick: tap(() => this.pause(true)) }, icon(I.pause))), h("div", { class: "spacer" }), this.hpGate);
    // ballista (hold + drag back to aim)
    this.weapon = h("button", { class: "weapon", "aria-label": W.weaponHelp }, artIcon("cannon"), h("span", { class: "ring" }));
    this.bindWeapon();
    this.energy = h("div", { class: "energy" }, h("div", { class: "val" }, h("span", { class: "fl" }), h("span", { class: "n" }, "0"), h("span", { class: "muted", style: "font-size:13px" }, h("span", { class: "mx" }, "/100"))), h("div", { class: "bar" }, h("i")));
    this.cardEls = B.cards.map((c) => {
      const el = h("button", { class: "ucard", "aria-label": `Send ${unitById[c.id].name}, ${c.stats.cost} ${W.energy}`, "data-id": c.id,
        onpointerdown: (e) => { e.preventDefault(); this.send(c.id, el); } },
        portrait(c.id), h("span", { class: "nm" }, SHORT[c.id] || unitById[c.id].name), h("span", { class: "cd" }), h("span", { class: "cdn" }), h("span", { class: "afm" }), h("span", { class: "cost" }, h("span", { class: "fl" }), c.stats.cost + ""));
      return el;
    });
    const empty = Math.max(0, (this.stage.slots || 5) - this.cardEls.length);       // empty places this stage allows: the tray shows them all
    const cards = h("div", { class: "cards" }, ...this.cardEls, ...Array.from({ length: empty }, () => h("span", { class: "slot", "aria-hidden": "true" })));
    this.abilEls = B.abilities.map((a) => {
      const el = h("button", { class: "abil", "aria-label": abilityNames[a.id], "data-id": a.id, onpointerdown: (e) => { e.preventDefault(); this.useAbility(a, el); } },
        iconImg("i_" + a.id, a.id === "rally" ? I.bell : I.rain), h("span", { class: "cdtxt" }));
      return el;
    });
    this.heroEl = B.hero ? h("button", { class: "abil herobtn", "aria-label": W.heroCall, onpointerdown: (e) => { e.preventDefault(); this.callHero(); } }, portrait("marshal", 60), h("span", { class: "cdtxt" })) : null;
    const side = h("div", { class: "side row-side" }, this.heroEl, ...this.abilEls);
    const bottom = h("div", { class: "hud-bottom" }, h("div", { class: "left" }, this.weapon, this.energy), cards, side);
    this.bossBar = null;
    return h("div", { class: "screen hud" }, top, bottom);
  }
  bossWarn(kind) {
    const t = W.callouts[kind];
    if (t) this.callout(t, true);
  }
  /** One callout at a time: urgent ones (boss warnings) replace the current one, others wait their turn. */
  callout(text, urgent = false) {
    this._cq = this._cq || [];
    if (urgent) { this._cq.length = 0; if (this._co) { this._co.remove(); this._co = null; clearTimeout(this._coT); } }
    else if (this._co) { if (this._cq.length < 2) this._cq.push(text); return; }
    const c = h("div", { class: urgent ? "callout warn" : "callout" }, text); this.el.append(c); this._co = c;
    this._coT = setTimeout(() => { c.remove(); this._co = null; const n = this._cq.shift(); if (n) this.callout(n); }, urgent ? 1500 : 1900);
  }
  onBoss(e) {
    this.bossBar = h("div", { class: "bossbar" }, h("div", { class: "name" }, enemyById[e.id].name), h("div", { class: "bar" }, h("i")));
    this.el.append(this.bossBar); this.callout(W.callouts.bossRises); R.camTarget = Math.max(0, e.x - R.W * 0.6);
  }
  send(id, el) {
    if (this.paused || this.over) return;
    if (!canSend(this.B, id)) { sfx("ui_locked", { gain: 0.6 }); el.classList.remove("sent"); return; }
    input.send(this.B, id); el.classList.remove("sent"); void el.offsetWidth; el.classList.add("sent");
    this.flag("sent");
  }
  useAbility(a, el) {
    if (this.paused || this.over || a.cd > 0) { sfx("ui_locked", { gain: 0.5 }); return; }
    if (a.id === "rally") { input.ability(this.B, a.id, 0); this.flag("ability"); return; }
    // targeted: arm, then tap the field
    if (this.armed === a) { this.disarm(); return; }
    this.armed = a; el.classList.add("armed"); sfx("ui_tap");
    this.armBanner = h("div", { class: "banner" }, W.armTarget, h("button", { class: "btn icon", style: "min-height:36px;width:36px", "aria-label": "Cancel", onclick: tap(() => this.disarm(), "ui_back") }, h("span", { html: "&#x2715;" })));
    this.el.append(this.armBanner);
  }
  disarm() { if (this.armed) { this.abilEls.forEach((e) => e.classList.remove("armed")); this.armed = null; this.armBanner && this.armBanner.remove(); } }
  callHero() {
    const hr = this.B.hero; if (this.paused || this.over || !hr || hr.called) return;
    if (hr.charge < hr.need) { sfx("ui_locked", { gain: 0.5 }); return; }
    input.hero(this.B); this.flag("hero"); this.callout(W.callouts.hero);
  }
  bindWeapon() {
    const w = this.weapon; let start = null, id = null;
    const k = 6.2;   // css px of pull -> speed
    w.addEventListener("pointerdown", (e) => {
      if (this.paused || this.over) return;
      e.preventDefault(); w.setPointerCapture(e.pointerId); id = e.pointerId;
      const r = w.getBoundingClientRect(); start = [r.left + r.width / 2, r.top + r.height / 2];
      w.classList.add("aiming"); this.aimFrom = start; this.updateAim(e.clientX, e.clientY);
    });
    w.addEventListener("pointermove", (e) => { if (e.pointerId === id && start) this.updateAim(e.clientX, e.clientY); });
    const up = (e) => {
      if (e.pointerId !== id || !start) return;
      w.classList.remove("aiming");
      const a = R.aim; start = null; id = null; R.aim = null;
      if (!a || a.pull < 18 || this.B.ballista.reload > 0) { if (a && this.B.ballista.reload > 0) sfx("ui_locked", { gain: 0.5 }); return; }
      input.fire(this.B, a.vx, a.vy); this.flag("fired");
      R.camTarget = null;
    };
    w.addEventListener("pointerup", up); w.addEventListener("pointercancel", (e) => { R.aim = null; start = null; w.classList.remove("aiming"); });
  }
  updateAim(cx, cy) {
    const [sx, sy] = this.aimFrom; let dx = sx - cx, dy = sy - cy;     // pull back = fire forward
    const pull = Math.hypot(dx, dy); const g = game.ballista;
    // slingshot: pull back-and-down to fire forward-and-up. A tap without dragging gives a gentle lob.
    if (pull < 6) { dx = 1; dy = -0.7; }
    const up = Math.max(0.05, Math.min(1.35, Math.atan2(-dy, Math.max(4, dx))));
    const k = 6.2;   // css px of pull -> launch speed
    const speed = Math.max(g.minSpeed, Math.min(g.maxSpeed, g.minSpeed + pull * k));
    R.aim = { vx: Math.cos(up) * speed, vy: -Math.sin(up) * speed, pull };
    // keep the landing point in view while aiming
    // keep the ballista in view; only slide right when the landing point would leave the screen
    if (R.aim.landX && (R.aim.landX > R.camX + R.W * 0.9 || R.aim.landX < R.camX + 60)) R.camTarget = Math.max(0, Math.min(this.B.F.width - R.W, R.aim.landX - R.W * 0.75));
  }
  bindCanvas() {
    let pan = null;
    this.onDown = (e) => {
      if (this.paused || this.over) return;
      if (this.armed) {
        const x = R.toWorldX(e.clientX); input.ability(this.B, this.armed.id, x); this.flag("ability"); this.disarm(); return;
      }
      pan = { x: e.clientX, cam: R.camX, id: e.pointerId }; R.camTarget = null; this.lastPan = performance.now();
    };
    this.onMove = (e) => { if (pan && e.pointerId === pan.id) { this.lastPan = performance.now(); R.camX = pan.cam - (e.clientX - pan.x) * R.dpr / R.scale; R.clampCam(this.B); } };
    this.onUp = (e) => { if (pan && e.pointerId === pan.id) pan = null; };
    canvas.addEventListener("pointerdown", this.onDown); window.addEventListener("pointermove", this.onMove); window.addEventListener("pointerup", this.onUp);
  }
  unbind() {
    canvas.removeEventListener("pointerdown", this.onDown); window.removeEventListener("pointermove", this.onMove); window.removeEventListener("pointerup", this.onUp);
    document.removeEventListener("visibilitychange", this.vis); cancelAnimationFrame(this.raf);
  }
  flag(f) { if (this.tutor) this.tutor.flags[f] = true; }
  tutorialTick() {
    const T = this.tutor; if (!T) return;
    const B = this.B, s = T.steps[T.i];
    if (!s) { this.endTutor(true); return; }
    if (!T.shown) {
      if (s.when) {
        if (s.when.startsWith("enemies:") && B.ents.filter((e) => e.alive && e.side === -1).length < +s.when.split(":")[1]) return;
        if (s.when === "heroReady" && !(B.hero && B.hero.charge >= B.hero.need)) return;
      }
      T.flags = {}; T.t0 = B.t;
      T.shown = h("div", { class: "tut", role: "status" }, s.text); this.el.append(T.shown);
      T.hl = this.targetEl(s.target); if (T.hl) T.hl.classList.add("hl");
      if (s.holdWaves) B.waveHold = true;
    }
    const u = s.until; let done = false;
    if (u === "sent") done = T.flags.sent; else if (u === "fired") done = T.flags.fired; else if (u === "ability") done = T.flags.ability; else if (u === "hero") done = T.flags.hero;
    else if (u.startsWith("time:")) done = B.t - T.t0 >= +u.split(":")[1];
    if (done) {
      sfx("ui_tap", { rate: 1.3 }); T.shown.remove(); if (T.hl) T.hl.classList.remove("hl"); T.shown = null; B.waveHold = false; T.i++;
      if (T.i >= T.steps.length) this.endTutor(true);
    }
  }
  endTutor(finished) {
    if (!this.tutor) return;
    if (this.tutor.shown) this.tutor.shown.remove(); if (this.tutor.hl) this.tutor.hl.classList.remove("hl");
    this.B.waveHold = false;
    if (finished && !D.tutorials.includes(this.stage.tutorial)) { D.tutorials.push(this.stage.tutorial); persist(); }
    this.tutor = null;
  }
  targetEl(t) {
    if (!t) return null;
    if (t.startsWith("unit:")) return this.cardEls.find((c) => c.dataset.id === t.slice(5));
    if (t.startsWith("ability:")) return this.abilEls.find((c) => c.dataset.id === t.slice(8));
    if (t === "weapon") return this.weapon; if (t === "energy") return this.energy; if (t === "hero") return this.heroEl;
    if (t === "enemyCastle") return this.hpGate;
    return null;
  }
  pause(on) {
    if (this.over) return;
    this.paused = on;
    if (on) {
      R.aim = null;
      const m = h("div", { class: "modal" }, h("div", { class: "panel", role: "dialog", "aria-label": "Paused", style: "width:min(380px,100%)" },
        h("h2", {}, "Paused"),
        h("button", { class: "btn primary big", onclick: tap(() => { m.remove(); this.pause(false); }) }, "Resume"),
        h("button", { class: "btn", onclick: tap(() => openSettings()) }, "Settings"),
        h("div", { class: "row" },
          h("button", { class: "btn", style: "flex:1", onclick: tap(() => { m.remove(); this.quit(); startBattle(this.stage); }) }, "Restart"),
          h("button", { class: "btn", style: "flex:1", onclick: tap(() => { m.remove(); this.quit(); regionScreen(regions.regions[0]); }, "ui_back") }, "Leave battle"))));
      this.el.append(m);
    } else { this.last = performance.now(); }
  }
  quit() { this.over = true; this.endTutor(false); this.unbind(); battle = null; }
  updateHud() {
    const B = this.B;
    const kf = B.keep.hp / B.keep.max, gf = B.gate.hp / B.gate.max;
    this.hpKeep.querySelector(".bar > i").style.transform = this.hpKeep.querySelector(".bar > u").style.transform = `scaleX(${kf})`; this.hpKeep.querySelector(".v").textContent = Math.ceil(B.keep.hp);
    this.hpGate.querySelector(".bar > i").style.transform = this.hpGate.querySelector(".bar > u").style.transform = `scaleX(${gf})`; this.hpGate.querySelector(".v").textContent = B.gate.sealed ? "" : Math.ceil(B.gate.hp);
    if (B.keep.hitT > 0.12) { this.hpKeep.classList.remove("hit"); void this.hpKeep.offsetWidth; this.hpKeep.classList.add("hit"); }
    const en = Math.floor(B.energy);
    if (en !== this._en) { this._en = en; this.energy.querySelector(".n").textContent = en; this.energy.querySelector(".mx").textContent = "/" + B.energyMax; const full = B.energy >= B.energyMax; if (full && !this._full) sfx("energy_full", { gain: 0.5 }); this._full = full; this.energy.classList.toggle("full", full); }
    this.energy.querySelector(".bar > i").style.transform = `scaleX(${B.energy / B.energyMax})`;
    B.cards.forEach((c, i) => {
      const el = this.cardEls[i], cdf = Math.max(0, c.cd / c.stats.cooldown), poor = B.energy < c.stats.cost;
      (el._cd || (el._cd = el.querySelector(".cd"))).style.transform = `scaleY(${cdf})`;
      el.classList.toggle("poor", poor); el.classList.toggle("ready", !poor && cdf <= 0); el.classList.toggle("cool", cdf > 0);
      const aff = Math.min(1, B.energy / c.stats.cost); if (el._aff !== aff) { el._aff = aff; el.style.setProperty("--aff", aff.toFixed(3)); }
      const cs = cdf > 0 ? Math.ceil(c.cd) + "" : ""; if (el._cs !== cs) { el._cs = cs; (el._cdn || (el._cdn = el.querySelector(".cdn"))).textContent = cs; }
    });
    B.abilities.forEach((a, i) => {
      const el = this.abilEls[i], t = el.querySelector(".cdtxt");
      t.textContent = a.cd > 0 ? Math.ceil(a.cd) : ""; t.style.display = a.cd > 0 ? "grid" : "none"; el.classList.toggle("ready", a.cd <= 0);
    });
    if (this.heroEl) {
      const hr = B.hero, t = this.heroEl.querySelector(".cdtxt");
      if (hr.called) { this.heroEl.classList.add("used"); t.style.display = "none"; }
      else { const ready = hr.charge >= hr.need; t.style.display = ready ? "none" : "grid"; t.textContent = Math.ceil(hr.need - hr.charge); this.heroEl.classList.toggle("ready", ready); }
    }
    this.weapon.classList.toggle("reloading", B.ballista.reload > 0);
    const r = this.weapon.querySelector(".ring"); const rf = B.ballista.reload > 0 ? 1 - B.ballista.reload / B.ballista.maxReload : 1;
    r.style.background = rf < 1 ? `conic-gradient(rgba(255,200,120,.9) ${rf * 360}deg, transparent 0)` : "none";
    r.style.mask = r.style.webkitMask = "radial-gradient(circle, transparent 62%, #000 64%)";
    const t = Math.floor(B.t - B.heldT); if (t !== this._t) { this._t = t; this.timer.textContent = `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`; }
    if (this.bossBar && B.boss) this.bossBar.querySelector(".bar > i").style.transform = `scaleX(${Math.max(0, B.boss.hp / B.boss.maxHp)})`;
  }
  frame(now) {
    if (this.over && !this.ending) return;
    this.raf = requestAnimationFrame((t) => this.frame(t));
    const w0 = performance.now();
    let dt = Math.min(0.1, (now - this.last) / 1000); this.last = now;
    const B = this.B;
    if (!this.paused) {
      let scale = this.speed * testSpeed;
      if (R.slowmo > 0) { R.slowmo -= dt; scale *= 0.25; }
      if (R.hitstop > 0) { R.hitstop -= dt; scale = 0; }      // a held frame on heavy impacts
      this.acc += dt * scale;
      let steps = 0;
      const s0 = performance.now();
      const maxSteps = 8 * testSpeed;
      while (this.acc >= B.dt && steps < maxSteps) { if (autoBot && !(this.tutor && this.tutor.shown)) autoBot(B); step(B); this.acc -= B.dt; steps++; }
      if (steps === maxSteps) this.acc = 0;
      (this.simWork || (this.simWork = [])).push(performance.now() - s0); if (this.simWork.length > 600) this.simWork.shift();
      this.tutorialTick();
    }
    this.followFight(now);
    R.consume(B);
    R.draw(B, this.paused ? 1 : Math.min(1, this.acc / B.dt), this.paused ? 0 : dt);
    this.updateHud();
    const work = performance.now() - w0; (this.work || (this.work = [])).push(work); if (this.work.length > 600) this.work.shift();
    if (B.result && !this.ending) {     // watch the fall before the tally: pan to the loser, name the moment
      R.camTarget = B.result === "win" ? Math.max(0, B.F.width - R.W) : 0; this.lastPan = now + 5000;
      this.callout(B.result === "win" ? (this.stage.boss ? W.results.bossWin : W.results.win) : W.results.lose, true);
    }
    if (B.result && !this.ending) { this.ending = true; setTimeout(() => this.finish(), B.result === "win" ? 2300 : 2100); }
  }
  /** When the player isn't panning or aiming, ease the camera toward where the armies meet. */
  followFight(now) {
    if (R.aim || this.paused || now - (this.lastPan || -1e9) < 3500 || now - (this._lastFollow || 0) < 400) return;
    this._lastFollow = now;
    const B = this.B; let pf = B.keep.front, ef = 1e9;
    for (const e of B.ents) { if (!e.alive) continue; if (e.side === 1) pf = Math.max(pf, e.x); else ef = Math.min(ef, e.x); }
    if (B.boss && B.boss.alive) ef = Math.min(ef, B.boss.x);
    const focus = ef < 1e9 ? (Math.min(pf, ef) + ef) / 2 : pf;
    const want = Math.max(0, Math.min(B.F.width - R.W, focus - R.W * 0.5));
    if (Math.abs(want - R.camX) > 90) R.camTarget = want;
  }
  finish() {
    const B = this.B; this.over = true; this.endTutor(B.result === "win"); this.unbind(); battle = null;
    const s = this.stage, win = B.result === "win";
    const rec = D.stages[s.id] || (D.stages[s.id] = { stars: [false, false, false], best: 0, clears: 0 });
    let earned = 0, newStars = 0; const got = [false, false, false]; const unlocks = [];
    if (win) {
      const n = starCount(B); got[0] = true; got[1] = B.keep.hp >= B.keep.max * game.stars.keepHp; got[2] = B.endT - B.heldT <= s.par;
      for (let i = 0; i < 3; i++) if (got[i] && !rec.stars[i]) { rec.stars[i] = true; newStars++; }
      earned = (rec.clears === 0 ? s.reward : Math.round(s.reward * game.rewards.replayFraction)) + newStars * game.rewards.perNewStar;
      rec.best = rec.best ? Math.min(rec.best, Math.round(B.endT)) : Math.round(B.endT);
      const firstClear = rec.clears === 0;
      const hadHero = D.unlocked.hero, hadAb = D.unlocked.abilities.slice();
      rec.clears++;
      if (firstClear) {
        for (const r of syncRecruits()) unlocks.push(r);
        if (!hadHero && D.unlocked.hero) unlocks.push({ name: game.hero.name, how: "hero" });
        for (const a of D.unlocked.abilities) if (!hadAb.includes(a)) unlocks.push({ name: abilityNames[a], how: "power" });
      }
    } else earned = Math.round(Math.min(40, B.stats.kills * 2));      // a little for trying: losses still move you forward
    D.marks += earned; D.totalMarks += earned; D.playTime += Math.round(B.t);
    persist(true);
    playMusic(win ? "victory" : "defeat");
    sfx(win ? "win" : "lose");
    this.results(win, got, earned, unlocks);
  }
  results(win, got, earned, unlocks) {
    const s = this.stage, idx = regionStages.indexOf(s), next = regionStages[idx + 1];
    const starsEl = h("div", { class: "bigstars", "aria-label": `${got.filter(Boolean).length} of 3 stars` }, ...got.map((g) => h("span", { class: "star" + (g ? " on" : " miss") })));
    const earnN = h("b", {}, "0");
    const tip = win ? null : loseTip(this.B);
    const marks = h("div", { class: "marks", style: "position:absolute;top:calc(var(--sat) + 60px);right:calc(var(--sar) + 16px)" }, coin(), h("span", {}, String(D.marks - earned)));
    const panel = h("div", { class: "panel result " + (win ? "win" : "lose") + (unlocks.length ? " has-news" : ""), role: "dialog", "aria-label": win ? "Victory" : "Defeat" },
      h("h2", {}, win ? (s.boss ? W.results.bossWin : W.results.win) : W.results.lose),
      win ? starsEl : h("p", { class: "note", style: "text-align:center;margin:0;font-size:var(--fs-m)" },
        this.B.gate.max && this.B.gate.hp / this.B.gate.max < 0.25 && !this.B.gate.sealed ? h("b", { style: "display:block;color:var(--accent-2);margin-bottom:4px" }, fill(W.results.closeGate, { hp: Math.ceil(this.B.gate.hp) })) : null,
        this.B.boss && this.B.boss.alive && this.B.boss.hp / this.B.boss.maxHp < 0.3 ? h("b", { style: "display:block;color:var(--accent-2);margin-bottom:4px" }, fill(W.results.closeBoss, { pct: Math.round(this.B.boss.hp / this.B.boss.maxHp * 100) })) : null,
        tip),
      win ? h("div", { class: "starrow", style: "align-self:center" }, ...game.stars.desc.map((d, i) => h("div", {}, h("span", { class: "star" + (got[i] ? " on" : "") }), i === 2 ? `Win under ${fmt(s.par)} — you took ${fmt(this.B.endT - this.B.heldT)}` : d))) : null,
      h("div", { class: "earn" }, coin(), h("span", {}, "+", earnN, " " + W.currency)),
      ...unlocks.filter((u) => u.how === "free").map((u) => h("div", { class: "recruit" }, h("span", { class: "pic" }, portrait(u.id, 72)),
        h("span", {}, h("small", {}, W.tavern.joins), h("b", {}, unitById[u.id].name), (crewPlan[u.id] || {}).job || ""))),
      ...unlocks.filter((u) => u.how === "tavern").map((u) => h("div", { class: "unlock" }, icon(I.mug), h("span", {}, h("small", {}, W.tavern.opened), `${unitById[u.id].name} will sign on for ${unitById[u.id].price} ${W.currency}`))),
      unlocks.some((u) => u.how === "hero" || u.how === "power") ? h("div", { class: "unlock" }, h("span", { class: "star on", style: "width:26px;height:26px" }), h("span", {}, h("small", {}, "Unlocked"), unlocks.filter((u) => u.name).map((u) => u.name).join(" · "))) : null,
      h("div", { class: "btnrow" },
        win && next ? h("button", { class: "btn primary big", onclick: tap(() => prepScreen(next, regions.regions[0])) }, "Next stage") : null,
        win && !next ? h("button", { class: "btn primary big", onclick: tap(() => { D.seen.regionCleared = D.seen.regionCleared || "new"; worldMap(); }) }, "Continue") : null,
        win && next ? null : null,
        !win ? h("button", { class: "btn primary big", onclick: tap(() => prepScreen(s, regions.regions[0])) }, "Change crew") : null,
        h("button", { class: "btn big", onclick: tap(() => startBattle(s, lastCrew)) }, "Retry"),
        h("button", { class: "btn big", onclick: tap(() => regionScreen(regions.regions[0]), "ui_back") }, "Map")));
    const m = h("div", { class: "modal" }, panel, marks);
    this.el.append(m);
    // stars one by one, then coins fly to the counter
    const delay = D.settings.reducedMotion ? 0 : 1;
    [...starsEl.children].forEach((el, i) => setTimeout(() => { el.classList.add("show"); if (got[i]) sfx("star", { rate: 1 + i * 0.12, minGap: 0 }); }, (350 + i * 380) * delay));
    const startCoins = (350 + 3 * 380) * delay;
    setTimeout(() => {
      const from = earnN.getBoundingClientRect(), to = marks.getBoundingClientRect(); const n = Math.min(14, Math.ceil(earned / 15)); let shown = 0;
      const step = Math.max(1, Math.ceil(earned / Math.max(1, n)));
      for (let i = 0; i < n; i++) setTimeout(() => {
        const c = h("span", { class: "coin flycoin", style: `left:${from.left}px;top:${from.top}px` }); document.body.append(c);
        c.animate([{ transform: "translate(0,0) scale(1)" }, { transform: `translate(${(to.left - from.left) * 0.5}px,${-60}px) scale(1.2)`, offset: 0.4 }, { transform: `translate(${to.left - from.left + 10}px,${to.top - from.top + 8}px) scale(.8)` }], { duration: 650 * delay || 1, easing: "cubic-bezier(.3,.6,.4,1)" }).onfinish = () => {
          c.remove(); shown = Math.min(earned, shown + step); earnN.textContent = shown; marks.lastChild.textContent = D.marks - earned + shown; sfx("coin", { rate: 1 + i * 0.05, minGap: 0 });
          if (i === n - 1) { earnN.textContent = earned; marks.lastChild.textContent = D.marks; }
        };
      }, i * 70 * delay);
      if (n === 0) { earnN.textContent = earned; marks.lastChild.textContent = D.marks; }
    }, startCoins);
  }
}

/** "Unlocks when you clear <stage> (stage N)", read from stage data so it follows any world. */
function unlockHint(id) {
  const st = content.stages.find((x) => x.unlocks.includes(id));
  if (st) return `Joins free when you clear ${st.name} (stage ${regionStages.indexOf(st) + 1})`;
  const tv = content.stages.find((x) => (x.tavern || []).includes(id));
  return tv ? `In the Tavern after ${tv.name} (stage ${regionStages.indexOf(tv) + 1}), for ${unitById[id].price} ${W.currency}` : "Joins later";
}
function fmt(t) { t = Math.floor(t); return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`; }
function loseTip(B) {
  // name the trait that beat you and one crew member you own (or can get) who answers it
  const crew = B.cards.map((c) => c.id), foes = foesOf(B.stage);
  for (const tag of foes.flatMap(tagsOf)) {
    if (!TRAITS[tag] || tag === "plain") continue;
    if (crew.some((c) => crewPlan[c] && crewPlan[c].strong.includes(tag))) continue;
    const ans = units.units.find((u) => crewPlan[u.id] && crewPlan[u.id].strong.includes(tag) && (owned(u.id) || D.tavern.includes(u.id)));
    if (ans) return h("span", {}, h("b", {}, `${traitName(tag)} beat you. `), TRAITS[tag].rule + " ", h("b", {}, `Try ${ans.name}${owned(ans.id) ? "" : " (in the Tavern)"}.`));
  }
  const alive = B.ents.filter((e) => e.alive && e.side === -1);
  const has = (id) => alive.some((e) => e.id === id);
  if (B.stats.shots < 3) return W.tips.weapon;
  if (has("brute") || has("husk_warden")) return W.tips.big;
  if (has("bloater")) return W.tips.bloater;
  if (has("spitter")) return W.tips.spitter;
  if (B.stats.sent < 8) return W.tips.send;
  return W.tips.general;
}

// ---------------------------------------------------------------- boot
function boot() {
  const prevent = (e) => e.preventDefault();
  document.addEventListener("gesturestart", prevent); document.addEventListener("dblclick", prevent, { passive: false });
  document.addEventListener("contextmenu", prevent);
  window.addEventListener("resize", () => { R.resize(); R._vg = null; });
  window.addEventListener("orientationchange", () => setTimeout(() => { R.resize(); R._vg = null; }, 200));
  document.body.append(h("div", { class: "rotate" }, h("div", {}, h("div", { html: I.phone }), h("div", { class: "title-s" }, "Turn your phone sideways"), h("div", { class: "muted" }, "Siegeline plays in landscape."))));
  // idle canvas behind menus: a quiet ember backdrop
  const g = canvas.getContext("2d"); g.fillStyle = "#0b1118"; g.fillRect(0, 0, canvas.width, canvas.height);
  setInterval(() => { D.playTime = D.playTime || 0; }, 60000);
  // register the offline cache after first load settles, so it never competes with the first screen
  if ("serviceWorker" in navigator && import.meta.env.PROD && !/\/preview\//.test(location.pathname)) window.addEventListener("load", () => setTimeout(() => navigator.serviceWorker.register("sw.js").catch(() => {}), 4000));
  if (syncRecruits().length) persist(true);
  window.__siegeline = { prepScreen: (id) => prepScreen(stageById[id], regions.regions[0]), tavern: () => tavern(worldMap), get D() { return D; }, get battle() { return battle; }, startBattle: (id, crew) => startBattle(stageById[id], crew), worldMap, regionScreen: () => regionScreen(regions.regions[0]), armoury: () => armoury(worldMap), titleScreen, openSettings, R,
    ...(TEST ? { setSpeed: (x) => (testSpeed = x), autoplay: (skill) => (autoBot = skill == null ? null : makeBot({ skill })), save: () => save(D), reload: () => { S = load(); D = S.data; } } : {}) };
  titleScreen();
}
boot();
