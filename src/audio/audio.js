// Web Audio: decoded buffers for SFX, looping music with crossfade. Unlocks on first touch (iOS rule).
const BASE = "assets/audio/";
let ctx = null, master = null, sfxBus = null, musicBus = null, manifest = null;
const buffers = new Map(), loading = new Map();
let music = null, wantMusic = null, vol = { music: 0.6, sfx: 0.85 };
const lastPlay = new Map();

export function initAudio(settings) {
  vol.music = settings.music; vol.sfx = settings.sfx;
  const unlock = () => {
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      ctx = new AC(); master = ctx.createGain(); master.connect(ctx.destination);
      sfxBus = ctx.createGain(); sfxBus.gain.value = vol.sfx; sfxBus.connect(master);
      musicBus = ctx.createGain(); musicBus.gain.value = vol.music; musicBus.connect(master);
      loadManifest();
    }
    if (ctx.state !== "running") ctx.resume();
  };
  window.addEventListener("pointerdown", unlock, { capture: true });
  window.addEventListener("keydown", unlock, { capture: true });
  document.addEventListener("visibilitychange", () => {
    if (!ctx) return;
    if (document.hidden) ctx.suspend(); else ctx.resume();
  });
}

async function loadManifest() {
  try {
    manifest = await (await fetch(BASE + "manifest.json")).json();
    // warm the small UI sounds and the wanted music first
    for (const id of ["ui_tap", "ui_back", "unit_send", "coin"]) get("sfx", id);
    if (wantMusic) playMusic(wantMusic, true);
  } catch { manifest = { sfx: {}, music: {} }; }
}

function get(kind, id) {
  const entry = manifest && manifest[kind] && manifest[kind][id];
  if (!entry || !ctx) return null;
  const key = kind + ":" + id;
  if (buffers.has(key)) return buffers.get(key);
  if (!loading.has(key)) {
    loading.set(key, fetch(BASE + entry.file).then((r) => r.arrayBuffer())
      .then((ab) => new Promise((res, rej) => ctx.decodeAudioData(ab, res, rej)))
      .then((buf) => { buffers.set(key, buf); return buf; }).catch(() => null));
  }
  return null;
}

export function preload(ids) { if (manifest) for (const id of ids) get("sfx", id); }

/** Play an SFX. rate varies pitch (coin streaks), minGap stops machine-gun stacking. */
export function sfx(id, { rate = 1, gain = 1, minGap = 0.04, pan = 0 } = {}) {
  if (!ctx || ctx.state !== "running" || vol.sfx <= 0) return;
  const buf = get("sfx", id); if (!buf) return;
  const now = ctx.currentTime, last = lastPlay.get(id) || 0;
  if (now - last < minGap) return; lastPlay.set(id, now);
  const src = ctx.createBufferSource(); src.buffer = buf; src.playbackRate.value = rate * (0.97 + Math.random() * 0.06);
  const g = ctx.createGain(); g.gain.value = gain * ((manifest.sfx[id] && manifest.sfx[id].vol) || 1);
  let node = g;
  if (pan && ctx.createStereoPanner) { const p = ctx.createStereoPanner(); p.pan.value = Math.max(-1, Math.min(1, pan)); g.connect(p); node = p; }
  src.connect(g); node.connect(sfxBus); src.start();
}

export function playMusic(id, force = false) {
  if (wantMusic === id && !force && music) return;
  wantMusic = id;
  if (!ctx || !manifest) return;
  const entry = manifest.music[id]; if (!entry) return;
  const buf = get("music", id);
  if (!buf) { loading.get("music:" + id)?.then(() => { if (wantMusic === id) playMusic(id, true); }); return; }
  const now = ctx.currentTime;
  if (music) { const old = music; old.g.gain.setTargetAtTime(0, now, 0.25); setTimeout(() => { try { old.src.stop(); } catch {} }, 1500); }
  const src = ctx.createBufferSource(); src.buffer = buf;
  const loop = entry.loop !== false && entry.loopEnd;
  if (loop) { src.loop = true; src.loopStart = entry.loopStart || 0; src.loopEnd = entry.loopEnd; }
  const g = ctx.createGain(); g.gain.value = 0; g.gain.setTargetAtTime(entry.vol || 0.5, now, 0.3);
  src.connect(g); g.connect(musicBus); src.start();
  music = { src, g, id };
  if (!loop) src.onended = () => { if (music && music.src === src) music = null; };
}

export function stopMusic() { wantMusic = null; if (music && ctx) { music.g.gain.setTargetAtTime(0, ctx.currentTime, 0.2); const m = music; setTimeout(() => { try { m.src.stop(); } catch {} }, 900); music = null; } }

export function setVolumes(m, s) {
  vol.music = m; vol.sfx = s;
  if (musicBus) musicBus.gain.setTargetAtTime(m, ctx.currentTime, 0.05);
  if (sfxBus) sfxBus.gain.setTargetAtTime(s, ctx.currentTime, 0.05);
}

/** Duck the music briefly (boss roar, big moments). */
export function duck(amount = 0.4, time = 1.2) {
  if (!musicBus) return; const t = ctx.currentTime;
  musicBus.gain.cancelScheduledValues(t); musicBus.gain.setTargetAtTime(vol.music * amount, t, 0.05);
  musicBus.gain.setTargetAtTime(vol.music, t + time, 0.4);
}
