import "./ui/style.css";
import units from "../data/units.json";
import enemies from "../data/enemies.json";
import game from "../data/game.json";
import regions from "../data/regions.json";
import r1 from "../data/stages/r1.json";
import { createBattle, step, input, canSend, stars as starCount } from "./sim/battle.js";
import { unitStats, upgradeCost, tierFor } from "./sim/stats.js";
import { load, save, saveSoon, exportCode, importCode, wipe, freshData } from "./save/save.js";
import { initAudio, sfx, playMusic, setVolumes, duck, preload } from "./audio/audio.js";
import { createRenderer } from "./render/renderer.js";
import { loadAtlas, loadBackgrounds, loadImageAsset, sprites } from "./render/assets.js";

const content = { units, enemies, game, regions, stages: r1.stages, tutorials: r1.tutorials };
const stageById = Object.fromEntries(content.stages.map((s) => [s.id, s]));
const unitById = Object.fromEntries(units.units.map((u) => [u.id, u]));
const enemyById = Object.fromEntries(enemies.enemies.map((e) => [e.id, e]));
const abilityNames = { ember_rain: "Ember Rain", rally: "Rally Bell" };

const ui = document.getElementById("ui");
const canvas = document.getElementById("game");
let S = load();                       // { data, note }
let D = S.data;
const R = createRenderer(canvas, { sfx: (id, o) => sfx(id, o), duck, onBoss: (e) => battle && battle.onBoss(e), onRush: () => battle && battle.callout("They're rushing!") });
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
const I = {
  back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>',
  gear: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v3M12 18.5v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2.5 12h3M18.5 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/></svg>',
  pause: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4.5" width="4" height="15" rx="1.2"/><rect x="14" y="4.5" width="4" height="15" rx="1.2"/></svg>',
  lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 018 0v2.5"/></svg>',
  hammer: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M14 4l6 6-3 3-6-6zM11 7L3.5 14.5a2 2 0 000 2.8l3.2 3.2a2 2 0 002.8 0L17 13"/></svg>',
  ballista: '<svg viewBox="0 0 48 48" fill="none" stroke="#f3d9a8" stroke-width="3.2" stroke-linecap="round"><path d="M8 36L38 12"/><path d="M14 18c8-2 16 6 14 14" stroke="#d49a3a"/><path d="M33 10l7-2-2 7" fill="#f3d9a8"/></svg>',
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
function show(el) {
  const old = current; current = el; ui.append(el);
  if (old) { old.classList.add("out"); setTimeout(() => old.remove(), 220); }
  for (const m of ui.querySelectorAll(".modal")) m.remove();
}
function tap(fn, sound = "ui_tap") { return (e) => { sfx(sound); fn(e); }; }
function topbar(title, backFn, extra = []) {
  return h("div", { class: "topbar" },
    backFn ? h("button", { class: "btn icon", "aria-label": "Back", onclick: tap(backFn, "ui_back") }, icon(I.back)) : null,
    h("div", { class: "title-s" }, title), h("div", { class: "spacer" }), ...extra,
    h("div", { class: "marks", "aria-label": "Marks" }, coin(), h("span", { id: "markval" }, D.marks + "")),
    h("button", { class: "btn icon", "aria-label": "Settings", onclick: tap(() => openSettings()) }, icon(I.gear)));
}

// ---------------------------------------------------------------- progress helpers
const regionStages = content.stages.filter((s) => s.region === "r1");
const cleared = (id) => !!(D.stages[id] && D.stages[id].clears > 0);
const stageOpen = (i) => i === 0 || cleared(regionStages[i - 1].id);
const starsOf = (id) => (D.stages[id] && D.stages[id].stars) || [false, false, false];
const totalStars = () => regionStages.reduce((n, s) => n + starsOf(s.id).filter(Boolean).length, 0);

// ---------------------------------------------------------------- title
async function titleScreen() {
  playMusic("menu");
  const img = await loadImageAsset("title.webp");
  const el = h("div", { class: "screen" },
    h("div", { class: "bgimg", style: img ? `background-image:url(${img.src})` : "background:radial-gradient(ellipse at 70% 60%, #5a2414, #120c0c)" }),
    h("div", { class: "title-wrap" },
      h("h1", { class: "logo" }, "SIEGELINE"),
      h("p", { class: "tagline" }, "Hold the Lantern Keep. Break the Maw. The ash is coming over the ridge."),
      h("div", { class: "row" },
        h("button", { class: "btn primary big", onclick: tap(() => worldMap()) }, cleared("r1s1") ? "Continue" : "Play"),
        h("button", { class: "btn icon big", "aria-label": "Settings", onclick: tap(() => openSettings()) }, icon(I.gear)))),
    h("div", { class: "foot" }, "v" + (import.meta.env.VITE_VERSION || "0.1") + " · saves stay on this device"));
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
      h("span", { class: "dot" }), h("span", { class: "lbl" }, open ? `${r.name} · ${totalStars()}/18` : r.name)));
  });
  show(h("div", { class: "screen" },
    topbar("The Ashen Marches", titleScreen, [h("button", { class: "btn", onclick: tap(() => armoury(worldMap)) }, icon(I.hammer), "Armoury")]),
    map));
}

// ---------------------------------------------------------------- region / stage select
async function regionScreen(region) {
  playMusic("map");
  await loadAtlas("ui", { white: false });
  const bgs = await loadBackgrounds("r1");
  const pts = [[0.1, 0.72], [0.25, 0.4], [0.4, 0.68], [0.55, 0.36], [0.7, 0.66], [0.87, 0.42]];
  const path = h("div", { class: "path" });
  const svgPts = pts.map(([x, y]) => `${x * 100},${y * 100}`).join(" ");
  path.append(h("svg", { class: "pathline", viewBox: "0 0 100 100", preserveAspectRatio: "none", html: `<polyline points="${svgPts}" fill="none" stroke="rgba(255,200,140,.35)" stroke-width="0.8" stroke-dasharray="1.5 1.5"/>` }));
  let nextIdx = regionStages.findIndex((s, i) => stageOpen(i) && !cleared(s.id));
  regionStages.forEach((s, i) => {
    const open = stageOpen(i), st = starsOf(s.id);
    const node = h("button", { class: "node" + (s.boss ? " boss" : "") + (open ? "" : " locked") + (i === nextIdx ? " next" : ""),
      style: `left:${pts[i][0] * 100}%;top:${pts[i][1] * 100}%`, "aria-label": `${s.name}${open ? "" : " (locked)"}`,
      onclick: open ? tap(() => stageSheet(s, region)) : tap(() => toast("Clear the stage before this one first."), "ui_locked") },
      s.boss ? "☠︎" : String(i + 1),
      h("span", { class: "st" }, ...st.map((on) => h("i", { class: on ? "on" : "" }))));
    if (!open) node.prepend(icon(I.lock));
    if (!open) node.childNodes[1].remove();
    path.append(node);
  });
  const back = bgs && (bgs.mid || bgs.far);
  show(h("div", { class: "screen" },
    h("div", { class: "bgimg", style: back ? `background-image:url(${(bgs.sky || back).img.src})` : "background:linear-gradient(#2a1418,#8a3a1a)" }),
    topbar(region.name, worldMap, [h("button", { class: "btn", onclick: tap(() => armoury(() => regionScreen(region))) }, icon(I.hammer), "Armoury")]),
    path));
  if (nextIdx >= 0 && !D.seen.firstSheet) { D.seen.firstSheet = true; stageSheet(regionStages[nextIdx], region); }
}

function stageSheet(s, region) {
  for (const m of ui.querySelectorAll(".sheet")) m.remove();
  const foes = new Set(); for (const w of s.waves) foes.add(w.id); for (const [id] of (s.loop ? s.loop.pool : [])) foes.add(id); if (s.boss) foes.add(s.boss);
  const st = starsOf(s.id), first = !cleared(s.id);
  const reward = first ? s.reward : Math.round(s.reward * game.rewards.replayFraction);
  const sheet = h("div", { class: "sheet", role: "dialog", "aria-label": s.name },
    h("div", { class: "row" }, h("div", { class: "muted", style: "font-weight:700" }, s.boss ? "Boss battle" : `Stage ${regionStages.indexOf(s) + 1}`), h("div", { class: "spacer" }),
      h("button", { class: "btn icon", "aria-label": "Close", onclick: tap(() => sheet.remove(), "ui_back") }, h("span", { html: "&#x2715;" }))),
    h("h2", {}, s.name),
    s.boss ? h("p", { class: "note", style: "margin:0" }, enemyById[s.boss].desc) : null,
    h("div", { class: "muted", style: "font-size:13px;font-weight:700" }, "You'll face"),
    h("div", { class: "chips" }, ...[...foes].map((id) => h("span", { class: "chip" }, h("span", { class: "dot", style: "width:10px;height:10px;border-radius:50%;background:#ff7a3a;margin-left:6px" }), enemyById[id].name))),
    h("div", { class: "starrow" }, ...game.stars.desc.map((d, i) => h("div", {}, h("span", { class: "star" + (st[i] ? " on" : "") }), i === 2 ? `Win in under ${Math.floor(s.par / 60)}:${String(s.par % 60).padStart(2, "0")}` : d))),
    h("div", { class: "row" }, h("span", { class: "muted" }, first ? "First clear" : "Replay"), h("div", { class: "spacer" }), coin(), h("b", {}, reward + "")),
    h("div", { class: "spacer" }),
    h("button", { class: "btn primary big", onclick: tap(() => startBattle(s)) }, "Fight"));
  current.append(sheet);
}

// ---------------------------------------------------------------- armoury (upgrades)
let armouryTab = "units";
async function armoury(backFn) {
  await loadAtlas("ui", { white: false });
  const tabs = h("div", { class: "tabs", role: "tablist" });
  const list = h("div", { class: "list" });
  const setTab = (t) => { armouryTab = t; render(); };
  const mkTab = (id, label) => h("button", { class: "tab" + (armouryTab === id ? " on" : ""), role: "tab", "aria-selected": armouryTab === id, onclick: tap(() => setTab(id)) }, label);
  function upRow(pic, title, lvl, max, det, next, cost, onBuy, locked) {
    const can = !locked && lvl < max && D.marks >= cost;
    const btn = h("button", { class: "btn upbtn" + (can ? " primary" : ""), disabled: locked || lvl >= max || null,
      onclick: () => { if (D.marks < cost) { sfx("ui_locked"); toast("Not enough marks. Replay stages for more."); return; } D.marks -= cost; onBuy(); sfx("ui_upgrade"); persist(); render(); const c = list.querySelector(`[data-k="${title}"]`); if (c) c.classList.add("pop"); } },
      lvl >= max ? "Max" : "Upgrade", lvl >= max ? null : h("small", {}, coin(), cost + ""));
    return h("div", { class: "card" + (locked ? " locked" : ""), "data-k": title },
      h("div", { class: "pic" }, pic),
      h("div", {}, h("h3", {}, title, " ", h("span", { class: "lv" }, locked ? "Locked" : `Lv ${lvl}`)), h("div", { class: "det" }, det), next ? h("div", { class: "next" }, next) : null),
      locked ? icon(I.lock) : btn);
  }
  function render() {
    tabs.replaceChildren(mkTab("units", "Units"), mkTab("keep", "Keep & Ballista"), mkTab("hero", "Hero & Powers"));
    list.replaceChildren();
    document.getElementById("markval") && (document.getElementById("markval").textContent = D.marks);
    if (armouryTab === "units") {
      for (const u of units.units.filter((u) => u.region === 1)) {
        const locked = !D.unlocked.units.includes(u.id), L = D.unitLevels[u.id] || 1;
        const a = unitStats(u, L, units.levels), b = unitStats(u, L + 1, units.levels);
        const nextTier = L < 5 ? `Lv 5: ${u.tiers["5"]}` : L < 10 ? `Lv 10: ${u.tiers["10"]}` : u.tiers["10"];
        list.append(upRow(portrait(u.id), u.name, L, 10,
          `${u.role} · ${u.cost} embers · HP ${Math.round(a.hp)} · ${u.id === "lamplighter" ? "heal " + Math.round(a.traits.heal) : "DMG " + Math.round(a.dmg)}`,
          L < 10 ? `Next: HP ${Math.round(b.hp)}, ${u.id === "lamplighter" ? "heal " + Math.round(b.traits.heal) : "DMG " + Math.round(b.dmg)} · ${nextTier}` : nextTier,
          upgradeCost("unit", L, game), () => (D.unitLevels[u.id] = L + 1), locked));
      }
    } else if (armouryTab === "keep") {
      const k = D.keep, bl = D.ballista, em = D.energyMax, er = D.energyRegen;
      list.append(upRow(h("span", { html: I.lock.replace("currentColor", "#d49a3a") }), "Keep walls", k, 10, `Keep health ${game.keep.hp + game.keep.hpPerLevel * (k - 1)}`, `Next: ${game.keep.hp + game.keep.hpPerLevel * k}`, upgradeCost("keep", k, game), () => D.keep++));
      list.append(upRow(icon(I.ballista), "Ballista", bl, 10, `Bolt damage ${Math.round(game.ballista.dmg * (1 + game.ballista.dmgPerLevel * (bl - 1)))} · reload ${Math.max(1.2, game.ballista.reload - game.ballista.reloadPerLevel * (bl - 1)).toFixed(2)}s`, `Next: ${Math.round(game.ballista.dmg * (1 + game.ballista.dmgPerLevel * bl))} dmg, ${Math.max(1.2, game.ballista.reload - game.ballista.reloadPerLevel * bl).toFixed(2)}s`, upgradeCost("ballista", bl, game), () => D.ballista++));
      list.append(upRow(h("span", { class: "fl", style: "width:22px;height:28px;background:#ff8a3a;clip-path:polygon(50% 0,90% 55%,75% 100%,25% 100%,10% 55%)" }), "Ember store", em, game.energy.maxLevel, `Hold up to ${game.energy.max + game.energy.maxPerLevel * (em - 1)} embers`, `Next: ${game.energy.max + game.energy.maxPerLevel * em}`, upgradeCost("energyMax", em, game), () => D.energyMax++));
      list.append(upRow(h("span", { class: "fl", style: "width:22px;height:28px;background:#ffcf6a;clip-path:polygon(50% 0,90% 55%,75% 100%,25% 100%,10% 55%)" }), "Ember flow", er, game.energy.maxLevel, `${(game.energy.regen + game.energy.regenPerLevel * (er - 1)).toFixed(1)} embers per second`, `Next: ${(game.energy.regen + game.energy.regenPerLevel * er).toFixed(1)}/s`, upgradeCost("energyRegen", er, game), () => D.energyRegen++));
    } else {
      const hl = D.hero, hg = game.hero;
      list.append(upRow(portrait("marshal"), hg.name, hl, hg.maxLevel, `HP ${Math.round(hg.hp * (1 + hg.hpPerLevel * (hl - 1)))} · DMG ${Math.round(hg.dmg * (1 + hg.dmgPerLevel * (hl - 1)))} · Flare stuns nearby Hollows`, `Next: HP ${Math.round(hg.hp * (1 + hg.hpPerLevel * hl))}, DMG ${Math.round(hg.dmg * (1 + hg.dmgPerLevel * hl))}`, upgradeCost("hero", hl, game), () => D.hero++, !D.unlocked.hero));
      for (const id of ["ember_rain", "rally"]) {
        const a = game.abilities[id], L = D.abilities[id] || 1;
        const det = id === "ember_rain" ? `${a.stones} burning stones, ${Math.round(a.dmg * (1 + a.dmgPerLevel * (L - 1)))} dmg each · ${a.cooldown}s` : `+35% speed, faster attacks, heals 15% · ${(a.time + a.timePerLevel * (L - 1)).toFixed(1)}s · ${a.cooldown}s`;
        const nx = id === "ember_rain" ? `Next: ${Math.round(a.dmg * (1 + a.dmgPerLevel * L))} dmg each` : `Next: lasts ${(a.time + a.timePerLevel * L).toFixed(1)}s`;
        list.append(upRow(iconImg("i_" + id, id === "rally" ? I.bell : I.rain), abilityNames[id], L, a.maxLevel, det, nx, upgradeCost("ability", L, game), () => (D.abilities[id] = L + 1), !D.unlocked.abilities.includes(id)));
      }
    }
  }
  render();
  show(h("div", { class: "screen" }, topbar("Armoury", backFn), tabs, list));
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
    h("div", { class: "panel", role: "dialog", "aria-label": "Settings" },
      h("div", { class: "row" }, h("h2", {}, "Settings"), h("div", { class: "spacer" }), h("button", { class: "btn icon", "aria-label": "Close", onclick: tap(() => close(), "ui_back") }, h("span", { html: "&#x2715;" }))),
      slider("music", "Music"), slider("sfx", "Sound effects"), tgl("reducedMotion", "Reduced motion (no shake or flashes)"), tgl("largeText", "Larger text"),
      h("div", { class: "row", style: "flex-wrap:wrap" },
        h("button", { class: "btn", onclick: tap(() => exportUI(io)) }, "Export save"),
        h("button", { class: "btn", onclick: tap(() => importUI(io)) }, "Import save"),
        h("button", { class: "btn", style: "color:#ff9a8a", onclick: tap(() => resetUI(io)) }, "Reset progress")),
      io,
      h("p", { class: "note", style: "margin:0" }, "Progress saves automatically on this device. Export a code or file to move it to another phone or keep a backup.")));
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
  box.replaceChildren(h("p", { class: "note", style: "margin:0" }, "This deletes all stars, marks and upgrades on this device. Export first if you might want them back."),
    h("div", { class: "row" }, h("button", { class: "btn", style: "background:#7a1a14", onclick: tap(() => { wipe(); D = freshData(); S.data = D; save(D); applySettings(); for (const m of ui.querySelectorAll(".modal")) m.remove(); toast("Progress reset."); titleScreen(); }) }, "Delete my progress"),
      h("button", { class: "btn", onclick: tap(() => box.replaceChildren()) }, "Keep it")));
}

// ---------------------------------------------------------------- battle
let battle = null;

async function startBattle(stage) {
  const loading = h("div", { class: "screen loading" }, h("div", { style: "text-align:center" }, h("div", { class: "title-s", style: "margin-bottom:12px" }, stage.name), h("div", { class: "bar" }, h("i", { style: "transform:scaleX(.1)" }))));
  show(loading);
  const bar = loading.querySelector(".bar > i");
  const groups = ["units", "enemies", "castles", "fx", "ui"]; if (D.unlocked.hero) groups.push("hero"); if (stage.boss) groups.push("boss");
  let n = 0; const tick = () => { n++; bar.style.transform = `scaleX(${0.1 + 0.9 * n / (groups.length + 1)})`; };
  await Promise.all([...groups.map((g) => loadAtlas(g, { white: g !== "ui" }).then(tick)), loadBackgrounds(stage.bg).then(tick), stage.bg !== "r1" ? loadBackgrounds("r1") : null]);
  preload(["hit_blade", "hit_claw", "hit_blunt", "arrow_fire", "arrow_hit", "bolt_fire", "bolt_hit", "hollow_die", "warden_die", "castle_hit", "spit", "ballista_reload", "denied", "bloater_burst", "boss_roar", "boss_warn", "boss_slam", "win", "lose", "star", "coin", "hero_call", "hero_flare", "rally", "ember_rain", "heal", "energy_full", "castle_crumble"]);
  const st = { ...stage, available: D.unlocked.units.slice(0, 6), hero: D.unlocked.hero, abilities: D.unlocked.abilities.slice() };
  const prog = { unitLevels: D.unitLevels, keep: D.keep, ballista: D.ballista, energyMax: D.energyMax, energyRegen: D.energyRegen, hero: D.hero, abilities: D.abilities };
  const B = createBattle(content, st, prog, (Math.random() * 1e9) | 0);
  R.resetForBattle(); R.region = stage.bg;
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
    this.callout(stage.boss ? "Hold the line" : "Defend the Keep");
    this.raf = requestAnimationFrame((t) => this.frame(t));
    this.vis = () => { if (document.hidden && !this.over) this.pause(true); };
    document.addEventListener("visibilitychange", this.vis);
  }
  buildHud() {
    const B = this.B;
    this.hpKeep = h("div", { class: "hp" }, h("div", { class: "lbl" }, h("span", {}, "Lantern Keep"), h("span", { class: "v" })), h("div", { class: "bar" }, h("i")));
    this.hpGate = h("div", { class: "hp enemy" }, h("div", { class: "lbl" }, h("span", {}, B.gate.sealed ? "Maw Gate · sealed" : "Maw Gate"), h("span", { class: "v" })), h("div", { class: "bar" }, h("i")));
    this.speedBtn = h("button", { class: "pill", "aria-label": "Game speed", onclick: tap(() => { this.speed = this.speed === 1 ? 2 : 1; D.settings.speed = this.speed; persist(); this.speedBtn.innerHTML = I.speed(this.speed); }) });
    this.speedBtn.innerHTML = I.speed(this.speed);
    this.timer = h("div", { class: "pill", style: "pointer-events:none", "aria-label": "Battle time" }, "0:00");
    const top = h("div", { class: "hud-top" }, this.hpKeep, h("div", { class: "spacer" }), h("div", { class: "hud-mid" }, this.timer, this.speedBtn,
      h("button", { class: "pill", "aria-label": "Pause", onclick: tap(() => this.pause(true)) }, icon(I.pause))), h("div", { class: "spacer" }), this.hpGate);
    // ballista (hold + drag back to aim)
    this.weapon = h("button", { class: "weapon", "aria-label": "Ballista: hold and drag back to aim, release to fire" }, icon(I.ballista), h("span", { class: "ring" }));
    this.bindWeapon();
    this.energy = h("div", { class: "energy" }, h("div", { class: "val" }, h("span", { class: "fl" }), h("span", { class: "n" }, "0"), h("span", { class: "muted", style: "font-size:13px" }, h("span", { class: "mx" }, "/100"))), h("div", { class: "bar" }, h("i")));
    this.cardEls = B.cards.map((c) => {
      const el = h("button", { class: "ucard", "aria-label": `Send ${unitById[c.id].name}, ${c.stats.cost} embers`, "data-id": c.id,
        onpointerdown: (e) => { e.preventDefault(); this.send(c.id, el); } },
        portrait(c.id), h("span", { class: "cd" }), h("span", { class: "cost" }, h("span", { class: "fl" }), c.stats.cost + ""));
      return el;
    });
    const cards = h("div", { class: "cards" }, ...this.cardEls);
    this.abilEls = B.abilities.map((a) => {
      const el = h("button", { class: "abil", "aria-label": abilityNames[a.id], "data-id": a.id, onpointerdown: (e) => { e.preventDefault(); this.useAbility(a, el); } },
        iconImg("i_" + a.id, a.id === "rally" ? I.bell : I.rain), h("span", { class: "cdtxt" }));
      return el;
    });
    this.heroEl = B.hero ? h("button", { class: "abil herobtn", "aria-label": "Call the Marshal", onpointerdown: (e) => { e.preventDefault(); this.callHero(); } }, portrait("marshal", 60), h("span", { class: "cdtxt" })) : null;
    const side = h("div", { class: "side" }, ...this.abilEls);
    const bottom = h("div", { class: "hud-bottom" }, this.weapon, this.energy, cards, this.heroEl, side);
    this.bossBar = null;
    return h("div", { class: "screen hud" }, top, bottom);
  }
  callout(text) { const c = h("div", { class: "callout" }, text); this.el.append(c); setTimeout(() => c.remove(), 1900); }
  onBoss(e) {
    this.bossBar = h("div", { class: "bossbar" }, h("div", { class: "name" }, enemyById[e.id].name), h("div", { class: "bar" }, h("i")));
    this.el.append(this.bossBar); this.callout("The Matron rises"); R.camTarget = Math.max(0, e.x - R.W * 0.6);
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
    this.armBanner = h("div", { class: "banner" }, "Tap the field to drop Ember Rain", h("button", { class: "btn icon", style: "min-height:36px;width:36px", "aria-label": "Cancel", onclick: tap(() => this.disarm(), "ui_back") }, h("span", { html: "&#x2715;" })));
    this.el.append(this.armBanner);
  }
  disarm() { if (this.armed) { this.abilEls.forEach((e) => e.classList.remove("armed")); this.armed = null; this.armBanner && this.armBanner.remove(); } }
  callHero() {
    const hr = this.B.hero; if (this.paused || this.over || !hr || hr.called) return;
    if (hr.charge < hr.need) { sfx("ui_locked", { gain: 0.5 }); return; }
    input.hero(this.B); this.flag("hero"); this.callout("The Marshal rides!");
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
    if (R.aim.landX) R.camTarget = Math.max(0, Math.min(this.B.F.width - R.W, R.aim.landX - R.W * 0.55));
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
    this.hpKeep.querySelector(".bar > i").style.transform = `scaleX(${kf})`; this.hpKeep.querySelector(".v").textContent = Math.ceil(B.keep.hp);
    this.hpGate.querySelector(".bar > i").style.transform = `scaleX(${gf})`; this.hpGate.querySelector(".v").textContent = B.gate.sealed ? "" : Math.ceil(B.gate.hp);
    if (B.keep.hitT > 0.12) { this.hpKeep.classList.remove("hit"); void this.hpKeep.offsetWidth; this.hpKeep.classList.add("hit"); }
    const en = Math.floor(B.energy);
    if (en !== this._en) { this._en = en; this.energy.querySelector(".n").textContent = en; this.energy.querySelector(".mx").textContent = "/" + B.energyMax; this.energy.classList.toggle("full", B.energy >= B.energyMax); }
    this.energy.querySelector(".bar > i").style.transform = `scaleX(${B.energy / B.energyMax})`;
    B.cards.forEach((c, i) => {
      const el = this.cardEls[i], cdf = Math.max(0, c.cd / c.stats.cooldown), poor = B.energy < c.stats.cost;
      el.children[1].style.transform = `scaleY(${cdf})`;
      el.classList.toggle("poor", poor); el.classList.toggle("ready", !poor && cdf <= 0);
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
    const t = Math.floor(B.t); if (t !== this._t) { this._t = t; this.timer.textContent = `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`; }
    if (this.bossBar && B.boss) this.bossBar.querySelector(".bar > i").style.transform = `scaleX(${Math.max(0, B.boss.hp / B.boss.maxHp)})`;
  }
  frame(now) {
    if (this.over && !this.ending) return;
    this.raf = requestAnimationFrame((t) => this.frame(t));
    let dt = Math.min(0.1, (now - this.last) / 1000); this.last = now;
    const B = this.B;
    if (!this.paused) {
      let scale = this.speed;
      if (R.slowmo > 0) { R.slowmo -= dt; scale *= 0.25; }
      this.acc += dt * scale;
      let steps = 0;
      while (this.acc >= B.dt && steps < 8) { step(B); this.acc -= B.dt; steps++; }
      if (steps === 8) this.acc = 0;
      this.tutorialTick();
    }
    this.followFight(now);
    R.consume(B);
    R.draw(B, this.paused ? 1 : Math.min(1, this.acc / B.dt), this.paused ? 0 : dt);
    this.updateHud();
    if (B.result && !this.ending) { this.ending = true; setTimeout(() => this.finish(), B.result === "win" ? 1700 : 1500); }
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
      const n = starCount(B); got[0] = true; got[1] = B.keep.hp >= B.keep.max * game.stars.keepHp; got[2] = B.endT <= s.par;
      for (let i = 0; i < 3; i++) if (got[i] && !rec.stars[i]) { rec.stars[i] = true; newStars++; }
      earned = (rec.clears === 0 ? s.reward : Math.round(s.reward * game.rewards.replayFraction)) + newStars * game.rewards.perNewStar;
      rec.best = rec.best ? Math.min(rec.best, Math.round(B.endT)) : Math.round(B.endT);
      if (rec.clears === 0) for (const u of s.unlocks) {
        if (unitById[u] && !D.unlocked.units.includes(u)) { D.unlocked.units.push(u); D.unitLevels[u] = D.unitLevels[u] || 1; unlocks.push(unitById[u].name); }
        else if (u === "hero" && !D.unlocked.hero) { D.unlocked.hero = true; unlocks.push(game.hero.name + " (hero)"); }
        else if (game.abilities[u] && !D.unlocked.abilities.includes(u)) { D.unlocked.abilities.push(u); D.abilities[u] = D.abilities[u] || 1; unlocks.push(abilityNames[u]); }
      }
      rec.clears++;
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
    const marks = h("div", { class: "marks", style: "position:absolute;top:calc(var(--sat) + 16px);right:calc(var(--sar) + 24px)" }, coin(), h("span", {}, String(D.marks - earned)));
    const panel = h("div", { class: "panel result " + (win ? "win" : "lose"), role: "dialog", "aria-label": win ? "Victory" : "Defeat" },
      h("h2", {}, win ? (s.boss ? "The Matron falls" : "Victory") : "The Keep has fallen"),
      win ? starsEl : h("p", { class: "note", style: "text-align:center;margin:0;font-size:var(--fs-m)" }, tip),
      win ? h("div", { class: "starrow", style: "align-self:center" }, ...game.stars.desc.map((d, i) => h("div", {}, h("span", { class: "star" + (got[i] ? " on" : "") }), i === 2 ? `Under ${Math.floor(s.par / 60)}:${String(s.par % 60).padStart(2, "0")} (you: ${Math.floor(this.B.endT / 60)}:${String(Math.floor(this.B.endT % 60)).padStart(2, "0")})` : d))) : null,
      h("div", { class: "earn" }, coin(), "+", earnN, " marks"),
      unlocks.length ? h("div", { style: "text-align:center;font-weight:800;color:var(--accent-2)" }, "Unlocked: " + unlocks.join(", ")) : null,
      h("div", { class: "btnrow" },
        win && next ? h("button", { class: "btn primary big", onclick: tap(() => startBattle(next)) }, "Next stage") : null,
        win && !next ? h("button", { class: "btn primary big", onclick: tap(() => worldMap()) }, "Region cleared") : null,
        !win ? h("button", { class: "btn primary big", onclick: tap(() => armoury(() => regionScreen(regions.regions[0]))) }, "Upgrade") : null,
        h("button", { class: "btn big", onclick: tap(() => startBattle(s)) }, "Retry"),
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

function loseTip(B) {
  const alive = B.ents.filter((e) => e.alive && e.side === -1);
  const has = (id) => alive.some((e) => e.id === id);
  if (B.stats.shots < 3) return "Tip: the ballista reloads on its own. Fire it often, every bolt can hit a whole pack.";
  if (has("brute") || has("husk_warden")) return "Tip: big Hollows hit hard. Hold them with Ashguards while Torchbows and the ballista wear them down.";
  if (has("spitter")) return "Tip: Spitters hide behind the horde. Cinder Runners reach them fast.";
  if (B.stats.sent < 8) return "Tip: send soldiers steadily. Embers you don't spend are wasted when the store is full.";
  return "Tip: upgrades in the Armoury carry over to every stage. Replays earn marks too.";
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
  const g = canvas.getContext("2d"); g.fillStyle = "#120c0c"; g.fillRect(0, 0, canvas.width, canvas.height);
  setInterval(() => { D.playTime = D.playTime || 0; }, 60000);
  if ("serviceWorker" in navigator && import.meta.env.PROD) navigator.serviceWorker.register("sw.js").catch(() => {});
  window.__siegeline = { get D() { return D; }, get battle() { return battle; }, startBattle: (id) => startBattle(stageById[id]), worldMap, regionScreen: () => regionScreen(regions.regions[0]), armoury: () => armoury(worldMap), titleScreen, openSettings, R };
  titleScreen();
}
boot();
