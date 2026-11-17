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
    for (const [id, sp] of Object.entries(json.sprites)) sprites[id] = { atlas: a, anims: sp.anims, id };
    return a;
  } catch { done.delete(group); return null; }
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
