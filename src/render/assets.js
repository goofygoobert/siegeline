// Atlas + background loading per the asset contract. Missing files fall back to placeholders, never crash.
const BASE = "assets/";
export const atlases = {};          // group -> {img, white, json}
export const sprites = {};          // spriteId -> {atlas, anims}
export const bg = {};               // regionId -> {sky, far:{img,parallax}, ...}
export const images = {};
const done = new Set();

function loadImage(src) {
  return new Promise((res) => {
    const im = new Image(); im.decoding = "async";
    im.onload = () => res(im); im.onerror = () => res(null); im.src = src;
  });
}

/** Pre-tinted white copy of an atlas for hit flashes (one drawImage instead of per-frame filters). */
function whiteCopy(img) {
  const c = document.createElement("canvas"); c.width = img.width; c.height = img.height;
  const g = c.getContext("2d"); g.drawImage(img, 0, 0);
  g.globalCompositeOperation = "source-atop"; g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height);
  return c;
}

export async function loadAtlas(group, { white = true } = {}) {
  if (done.has(group)) return atlases[group];
  done.add(group);
  try {
    const r = await fetch(BASE + group + ".json", { cache: "no-cache" }); if (!r.ok) throw 0;
    const json = await r.json(); const img = await loadImage(BASE + json.image); if (!img) throw 0;
    const a = { img, json, white: white ? whiteCopy(img) : null, scale: 44 / (json.ppu || 72) };
    atlases[group] = a;
    // a sprite's animations may be spread over several pages of the same group: merge, and let each anim keep its page
    for (const [id, sp] of Object.entries(json.sprites)) {
      for (const an of Object.values(sp.anims)) an.atlas = a;
      const cur = sprites[id];
      if (cur && cur.group === group.replace(/\d+$/, "")) Object.assign(cur.anims, sp.anims);
      else sprites[id] = { atlas: a, anims: sp.anims, id, group: group.replace(/\d+$/, "") };
    }
    return a;
  } catch { done.delete(group); return null; }
}

/** A group may be split across numbered atlases (units, units2, units3...). Load all that exist. */
let pageList = null;
export async function loadGroup(group, opts) {
  if (!pageList) pageList = fetch(BASE + "atlases.json").then((r) => r.json()).catch(() => null);
  const list = await pageList;
  const names = list ? list.filter((n) => n === group || new RegExp("^" + group + "\\d+$").test(n)) : [group];
  const res = await Promise.all(names.map((n) => loadAtlas(n, opts)));
  return res.filter(Boolean).length;
}

export async function loadBackgrounds(regionId) {
  if (bg[regionId]) return bg[regionId];
  try {
    const man = await (await fetch(BASE + "bg/manifest.json", { cache: "no-cache" })).json();
    const m = man[regionId]; if (!m) return null;
    const out = {};
    await Promise.all(Object.entries(m).map(async ([layer, v]) => {
      const file = typeof v === "string" ? v : v.file;
      const img = await loadImage(BASE + "bg/" + file);
      if (img) out[layer] = { img, parallax: typeof v === "string" ? (layer === "sky" ? 0 : 1) : v.parallax };
    }));
    bg[regionId] = out; return out;
  } catch { return null; }
}

export async function loadImageAsset(name) {
  if (images[name] !== undefined) return images[name];
  images[name] = await loadImage(BASE + name); return images[name];
}

/** Frame for sprite/anim at time t (seconds into the anim). Returns [x,y,w,h,ax,ay] or null. */
export function frameAt(sp, anim, t, fpsOverride) {
  const a = sp.anims[anim] || sp.anims.idle || sp.anims.walk; if (!a) return null;
  const n = a.frames.length, fps = fpsOverride || a.fps || 10;
  let i = Math.floor(t * fps);
  i = a.loop === false ? Math.min(n - 1, i) : ((i % n) + n) % n;
  return a.frames[i];
}

export function hitTime(sp, anim) {
  const a = sp && sp.anims[anim]; if (!a) return 0.3;
  return (a.hit != null ? a.hit : Math.floor(a.frames.length / 2)) / (a.fps || 10);
}
