// Canvas 2D battle renderer: parallax backgrounds, atlased sprites, pooled particles and numbers, shake.
// Reads sim state, never changes it. Turns sim events into visuals and sounds ("feel").
import { sprites, frameAt, bg as BG, atlases } from "./assets.js";

const H = 540;                 // logical height
const MAXP = 360, MAXN = 48;
const CH = 1.3;              // characters drawn 1.3x the contract scale so they read on a phone next to the keep   // particle / number pools (fixed, reused: no per-frame garbage)

export function createRenderer(canvas, hooks) {
  const g = canvas.getContext("2d", { alpha: false });
  const R = {
    g, canvas, W: 960, scale: 1, dpr: 1, dprCap: 2, camX: 0, camTarget: null, shake: 0, shakeX: 0, shakeY: 0,
    flashA: 0, flashC: "#fff", slowmo: 0, quality: 2, reduced: false, sfx: hooks.sfx || (() => {}),
    parts: Array.from({ length: MAXP }, () => ({ life: 0 })), pi: 0,
    nums: Array.from({ length: MAXN }, () => ({ life: 0 })), ni: 0,
    fx: Array.from({ length: 24 }, () => ({ t: -1 })), fxi: 0,
    aim: null, target: null, region: "r1", t: 0, frameMs: 16, fpsAvg: 60, lowFrames: 0,
    coinBurst: [],
  };

  R.resize = () => {
    const vw = window.innerWidth, vh = window.innerHeight;
    R.dpr = Math.min(window.devicePixelRatio || 1, R.dprCap);
    canvas.width = Math.round(vw * R.dpr); canvas.height = Math.round(vh * R.dpr);
    canvas.style.width = vw + "px"; canvas.style.height = vh + "px";
    R.scale = canvas.height / H; R.W = canvas.width / R.scale;
  };
  R.resize();

  /** Screen (css px) -> world x. */
  R.toWorldX = (cssX) => (cssX * R.dpr) / R.scale + R.camX;
  R.toWorldY = (cssY) => (cssY * R.dpr) / R.scale;
  R.toCss = (wx, wy) => [((wx - R.camX) * R.scale) / R.dpr, (wy * R.scale) / R.dpr];
  R.clampCam = (B) => { const max = Math.max(0, B.F.width - R.W); R.camX = Math.max(0, Math.min(max, R.camX)); };

  // ---------------------------------------------------------------- particles & numbers
  function part(x, y, vx, vy, life, size, color, kind = 0, grav = 600) {
    if (R.quality === 0 && kind !== 3 && Math.random() < 0.5) return;
    const p = R.parts[R.pi]; R.pi = (R.pi + 1) % MAXP;
    p.x = x; p.y = y; p.vx = vx; p.vy = vy; p.life = life; p.max = life; p.size = size; p.c = color; p.k = kind; p.gr = grav;
  }
  R.part = part;
  function burst(x, y, n, color, speed = 160, size = 3, kind = 0, grav = 600, life = 0.6) {
    const m = R.quality === 2 ? n : Math.ceil(n * 0.5);
    for (let i = 0; i < m; i++) {
      const a = Math.random() * Math.PI * 2, s = speed * (0.3 + Math.random() * 0.7);
      part(x, y, Math.cos(a) * s, Math.sin(a) * s - speed * 0.4, life * (0.6 + Math.random() * 0.6), size * (0.6 + Math.random() * 0.8), color, kind, grav);
    }
  }
  R.burst = burst;
  function fxAt(id, x, y, scale = 1) {
    if (!sprites[id]) return; const f = R.fx[R.fxi]; R.fxi = (R.fxi + 1) % R.fx.length;
    f.id = id; f.x = x; f.y = y; f.t = 0; f.s = scale;
  }
  function num(x, y, text, color, big = false, key = 0, amt = 0) {
    if (key) for (const m of R.nums) if (m.life > 0.65 && m.key === key) { m.amt += amt; m.t = String(Math.round(m.amt)); m.big = m.big || m.amt >= 60; m.life = 0.9; return; }
    const n = R.nums[R.ni]; R.ni = (R.ni + 1) % MAXN;
    let ny = y - Math.random() * 6; const nx = x + (Math.random() - 0.5) * 16;
    for (let pass = 0; pass < 4; pass++) {           // stack above any number already near this spot
      let bump = false;
      for (const m of R.nums) if (m !== n && m.life > 0.4 && Math.abs(m.x - nx) < 34 && Math.abs(m.y - ny) < 16) { ny = m.y - 17; bump = true; }
      if (!bump) break;
    }
    n.x = nx; n.y = ny; n.t = text; n.c = color; n.life = 0.9; n.big = big; n.key = key; n.amt = amt;
  }
  // ground decals (craters, ink), hit sparks, shock rings: small fixed pools
  R.decals = Array.from({ length: 24 }, () => ({ t: 0 })); R.di = 0;
  R.sparks = Array.from({ length: 24 }, () => ({ t: 0 })); R.si = 0;
  R.rings = Array.from({ length: 8 }, () => ({ t: 0 })); R.ri = 0;
  R.births = new WeakMap(); R.hitstop = 0; R.recoil = 0; R.muzzle = 0; R.kick = 0;
  function decal(x, r, life, color, glow) { const d = R.decals[R.di]; R.di = (R.di + 1) % R.decals.length; d.x = x; d.r = r; d.t = life; d.max = life; d.c = color; d.glow = glow; }
  function spark(x, y, size, color = "#fff6d8") { const k = R.sparks[R.si]; R.si = (R.si + 1) % R.sparks.length; k.x = x; k.y = y; k.t = 0.11; k.s = size; k.c = color; k.rot = Math.random() * 1.6; }
  function ring(x, y, r, color = "rgba(255,236,190,") { const k = R.rings[R.ri]; R.ri = (R.ri + 1) % R.rings.length; k.x = x; k.y = y; k.r = r; k.t = 0.32; k.c = color; }
  function hitstop(t) { if (!R.reduced) R.hitstop = Math.max(R.hitstop, t); }
  function addShake(a) { if (!R.reduced) R.shake = Math.min(1, R.shake + a); }
  R.addShake = addShake;
  function flash(a, c = "#fff") { if (!R.reduced) { R.flashA = Math.max(R.flashA, a); R.flashC = c; } }

  const TH = hooks.theme || {};
  const SAND = TH.sand || "#d9b488", INKC = TH.enemyBlood || "#1f3b36";
  const BLOOD_W = TH.crewBlood || "#7a1714", ICHOR = TH.enemyBlood || "#2b2523", EMBER = TH.fire || "#ff8a2a", GLOWE = TH.enemyGlow || EMBER;
  const panOf = (x) => Math.max(-1, Math.min(1, ((x - R.camX) / R.W) * 2 - 1)) * 0.6;
  const onScreen = (x) => x > R.camX - 80 && x < R.camX + R.W + 80;

  /** Drain sim events into effects + sounds. */
  R.consume = (B) => {
    const gy = B.F.groundY;
    for (const e of B.events) {
      switch (e.type) {
        case "dmg": {
          const t = e.e; if (!onScreen(t.x)) break;
          if (e.kind === "burn") { if (Math.random() < 0.15) part(t.x + (Math.random() - 0.5) * 16, gy - 30, 0, -40, 0.6, 3, EMBER, 1, -60); break; }
          const enemy = t.side === -1;
          if (R.quality === 2 || e.amt >= 25) num(t.x, gy - (Math.min(170, t.s.size * 4.6) + 26), Math.max(1, Math.round(e.amt)) + "", enemy ? "#ffd27a" : "#ff6a5a", e.amt >= 60, t.uid, e.amt);
          burst(t.x - t.side * 6, gy - t.s.size * 2.8, e.amt > 40 ? 10 : 5, enemy ? ICHOR : BLOOD_W, 150, 3.2, 0);
          if (e.kind !== "fire") spark(t.x + t.side * t.s.size * 0.7, gy - t.s.size * (2.2 + Math.random()), e.amt >= 40 ? 26 : 17);
          if (enemy && Math.random() < 0.6) burst(t.x, gy - t.s.size * 2.2, 3, GLOWE, 120, 2, 1, 200, 0.5);
          if (e.kind === "blade") R.sfx("hit_blade", { pan: panOf(t.x), gain: 0.8 });
          else if (e.kind === "claw") R.sfx("hit_claw", { pan: panOf(t.x), gain: 0.8 });
          else if (e.kind === "blunt") { R.sfx("hit_blunt", { pan: panOf(t.x) }); addShake(0.12); }
          else if (e.kind === "arrow") R.sfx("arrow_hit", { pan: panOf(t.x), gain: 0.7 });
          if (e.amt >= 60) addShake(0.08);
          break;
        }
        case "die": {
          const t = e.e; if (!onScreen(t.x)) break;
          const enemy = t.side === -1;
          burst(t.x, gy - t.s.size * 2, enemy ? 14 : 10, enemy ? ICHOR : BLOOD_W, 200, 3.5, 0);
          if (enemy) { burst(t.x, gy - t.s.size * 2, 8, GLOWE, 160, 2.4, 1, -40, 0.9); burst(t.x, gy - 6, 6, "#6b6260", 70, 6, 2, -10, 1.1); decal(t.x, t.s.size * 1.5, 7, INKC, true); }
          else burst(t.x, gy - 4, 6, SAND, 90, 5, 2, -10, 0.8);
          if (t.s.large) hitstop(0.06);
          R.sfx(enemy ? "hollow_die" : "warden_die", { pan: panOf(t.x), gain: 0.8, minGap: 0.06 });
          if (t.s.large) addShake(0.25);
          break;
        }
        case "burst": fxAt("blast", e.x, gy - 30, 1.2); burst(e.x, gy - 30, 26, EMBER, 260, 4, 1, 300, 0.8); burst(e.x, gy - 20, 10, "#3a2b28", 120, 8, 2, -20, 1.2); addShake(0.3); flash(0.15, "#ff9a40"); R.sfx("bloater_burst", { pan: panOf(e.x) }); break;
        case "fire": {     // Long Tom: recoil, muzzle flash, smoke, a low kick of the whole view
          R.sfx("bolt_fire"); addShake(0.3); R.recoil = 1; R.muzzle = 1; R.kick = 1;
          const mx = B.ballista.x + 62, my = B.ballista.y - 22;
          burst(mx, my, 14, "#ffd58a", 320, 3.5, 1, 200, 0.35); burst(mx, my, 9, "#6f6470", 130, 11, 2, -30, 1.3);
          break;
        }
        case "spawn": {
          const t = e.e; R.births.set(t, R.t);
          if (!onScreen(t.x)) break;
          if (t.side === 1) burst(t.x, gy - 2, 7, SAND, 110, 5, 2, -10, 0.6);
          else { R.sfx("spit", { pan: panOf(t.x), rate: 0.6, gain: 0.35, minGap: 0.25 }); burst(t.x, gy - 30, 8, GLOWE, 150, 2.6, 1, -60, 0.8); burst(t.x, gy - 4, 5, "#27484a", 80, 8, 2, -15, 0.9); }
          break;
        }
        case "salvage": R.sfx("coin", { rate: 0.8, gain: 0.8 }); hooks.onSalvage && hooks.onSalvage(e.amt); break;     // shown at the powder counter, not in the fight
        case "directHit": num(e.x, e.y - 150, TH.directWord || "Direct hit!", "#fff1c8", true); spark(e.x, e.y, 46); hitstop(0.09); R.sfx("hit_blunt", { pan: panOf(e.x), rate: 0.7, gain: 1 }); break;
        case "boltHit":
          burst(e.x, e.y - 6, 22, EMBER, 280, 4, 1, 400, 0.7); burst(e.x, e.y, 10, "#4a3a35", 140, 9, 2, -30, 1.1);
          for (let i = 0; i < 16; i++) { const a = -Math.PI * (0.15 + 0.7 * Math.random()), v = 180 + Math.random() * 260; part(e.x, gy - 4, Math.cos(a) * v, Math.sin(a) * v, 0.5 + Math.random() * 0.5, 3 + Math.random() * 3, SAND, 0, 900); }
          decal(e.x, B.g.ballista.splash * 0.8, 5, "#3a2630", false); ring(e.x, gy, B.g.ballista.splash * 1.25);
          addShake(e.hits ? 0.5 : 0.22); if (e.hits) hitstop(e.kills ? 0.08 : 0.05); if (e.kills >= 2) flash(0.14, "#ffe2a0");
          R.sfx("bolt_hit", { pan: panOf(e.x) }); fxAt("blast", e.x, e.y - 20, 1.15);
          if (e.kills >= 2) num(e.x, e.y - 118, e.kills + " down!", "#ffe28a", true);
          break;
        case "reloaded": R.sfx("ballista_reload", { gain: 0.6 }); break;
        case "shoot": if (onScreen(e.e.x)) R.sfx(e.kind === "spit" ? "spit" : "arrow_fire", { pan: panOf(e.e.x), gain: 0.6, minGap: 0.08 }); break;
        case "send": R.sfx("unit_send"); burst(B.keep.front, gy - 4, 8, "#8a7a70", 90, 5, 2, -10, 0.7); break;
        case "denied": R.sfx("ui_locked", { gain: 0.6 }); break;
        case "castleHit": {
          const c = e.side === 1 ? B.keep : B.gate;
          burst(c.front + (e.side === 1 ? 10 : -10), gy - 80 - Math.random() * 120, 6, "#8d8078", 180, 4, 0);
          R.sfx("castle_hit", { gain: 0.7, minGap: 0.12 }); if (e.side === 1) addShake(0.1);
          break;
        }
        case "stone": fxAt("blast", e.x, gy - 16, 0.7); burst(e.x, gy - 6, 16, EMBER, 240, 3.5, 1, 400, 0.7); addShake(0.12); R.sfx("bolt_hit", { gain: 0.6, rate: 1.2, minGap: 0.05 }); break;
        case "ember_rain": R.sfx("ember_rain"); break;
        case "rally": R.sfx("rally"); flash(0.12, "#ffcf7a"); break;
        case "hero": R.sfx("hero_call"); flash(0.15, "#ffcf7a"); addShake(0.2); break;
        case "heroReady": R.sfx("energy_full", { rate: 0.8 }); break;
        case "flare": fxAt("flare", e.e.x, gy - 50, e.r / 120); burst(e.e.x, gy - 60, 30, "#ffe09a", 320, 3, 1, 0, 0.6); flash(0.25, "#ffe9b0"); R.sfx("hero_flare"); break;
        case "heal": if (onScreen(e.e.x)) { num(e.e.x, gy - Math.min(170, e.e.s.size * 4.6) - 26, "+" + Math.round(e.amt), "#9cf08a"); part(e.e.x, gy - 60, 0, -50, 0.8, 3, "#c8ff9a", 1, -30); } break;
        case "healBeam": R.sfx("heal", { gain: 0.5, minGap: 0.3 }); break;
        case "slam": burst(e.x, gy - 4, 12, "#6e625c", 160, 6, 2, -10, 0.8); break;
        case "bossSpawn": R.sfx("boss_roar"); hooks.duck && hooks.duck(0.3, 2.5); addShake(0.6); flash(0.2, "#ff6a2a"); hooks.onBoss && hooks.onBoss(e.e); break;
        case "bossWarn": hooks.onBossWarn && hooks.onBossWarn(e.kind); R.sfx(e.kind === "summon" ? "boss_roar" : "boss_warn", { gain: e.kind === "summon" ? 0.6 : 1 }); break;
        case "bossSlam": burst(e.x, gy - 6, 30, "#6e625c", 300, 8, 2, -20, 1.0); burst(e.x, gy - 10, 16, EMBER, 260, 3, 1, 300, 0.7); addShake(0.55); R.sfx("boss_slam"); break;
        case "bossSpitHit": fxAt("blast", e.x, gy - 24, 1.4); burst(e.x, gy - 6, 26, EMBER, 300, 4, 1, 400, 0.8); addShake(0.35); R.sfx("bolt_hit", { rate: 0.8 }); break;
        case "bossWinded": hooks.onBossWarn && hooks.onBossWarn("winded"); break;
        case "bossPhase": flash(0.3, "#ff5020"); addShake(0.5); R.sfx("boss_roar", { rate: 0.85 }); break;
        case "bossDead": R.slowmo = 1.6; flash(0.5, "#fff1c8"); addShake(1); R.sfx("castle_crumble"); break;
        case "enrage": burst(e.e.x, gy - 80, 18, "#ff4a20", 200, 3, 1, 0, 0.7); R.sfx("boss_roar", { rate: 1.3, gain: 0.6 }); break;
        case "rush": hooks.onRush && hooks.onRush(); break;
        case "angry": hooks.onAngry && hooks.onAngry(); R.sfx("boss_warn", { rate: 0.7 }); break;
        case "sealed": break;
        case "win": if (B.stage.winOn !== "boss") { R.slowmo = 1.2; addShake(0.8); flash(0.35, "#fff1c8"); R.sfx("castle_crumble"); } break;
        case "lose": R.slowmo = 1.2; addShake(0.9); flash(0.3, "#ff6a4a"); R.sfx("castle_crumble", { rate: 0.8 }); break;
      }
    }
    B.events.length = 0;
  };

  // ---------------------------------------------------------------- drawing helpers
  /** Background layers are pre-scaled once to screen resolution, so each frame is a plain unscaled copy. */
  const layerCache = new Map();
  function scaledLayer(L) {
    const key = L.img.src + "@" + R.scale.toFixed(3) + "x" + Math.round(R.W);
    let c = layerCache.get(key);
    if (!c) {
      const f = L.parallax || 0, wLog = f === 0 ? R.W : 1170 + (2600 - 1170) * f;
      c = document.createElement("canvas"); c.width = Math.ceil(wLog * R.scale); c.height = Math.ceil(H * R.scale);
      const cg = c.getContext("2d"); cg.imageSmoothingQuality = "high"; cg.drawImage(L.img, 0, 0, c.width, c.height);
      if (layerCache.size > 12) layerCache.clear();
      layerCache.set(key, c);
    }
    return c;
  }
  function drawLayer(L, camX) {
    if (!L || !L.img) return;
    const c = scaledLayer(L), f = L.parallax || 0;
    const sx = Math.max(0, Math.min(c.width - 1, Math.round(camX * f * R.scale)));
    const sw = Math.min(c.width - sx, Math.ceil(R.W * R.scale));
    g.setTransform(1, 0, 0, 1, Math.round(R.shakeX * R.scale), Math.round(R.shakeY * R.scale));
    g.drawImage(c, sx, 0, sw, c.height, 0, 0, sw, c.height);
    g.setTransform(R.scale, 0, 0, R.scale, R.shakeX * R.scale, R.shakeY * R.scale);
  }

  function spriteDraw(id, anim, t, x, y, opts = {}) {
    const sp = sprites[id];
    if (!sp) return false;
    const fr = frameAt(sp, anim, t, opts.fps); if (!fr) return false;
    const a = sp.atlas, s = a.scale * (opts.scale || 1);
    const [fx, fy, fw, fh, ax, ay] = fr;
    const src = opts.white && a.white ? a.white : a.img;
    const vy = opts.sy || 1;
    const dx = x - ax * s, dy = y - ay * s * vy;
    if (vy !== 1) { g.drawImage(src, fx, fy, fw, fh, dx, dy, fw * s, fh * s * vy); return true; }
    if (opts.rot) {
      g.save(); g.translate(x, y); g.rotate(opts.rot); g.drawImage(src, fx, fy, fw, fh, -ax * s, -ay * s, fw * s, fh * s); g.restore();
    } else g.drawImage(src, fx, fy, fw, fh, dx, dy, fw * s, fh * s);
    return true;
  }
  R.spriteDraw = spriteDraw;

  const colorOf = { ashguard: "#8c2a1e", torchbow: "#a6582a", cinder_runner: "#c4772f", bellringer: "#b08a3a", maulwright: "#5e6068", lamplighter: "#d8cdb8",
    marshal: "#c23a24", husk: "#4a4646", gnawer: "#3a3636", spitter: "#5a4a40", bloater: "#6a3a2a", brute: "#2e2a2a", husk_warden: "#55443a", cinder_matron: "#2a1a1a" };
  function placeholder(e, x, y, h, flashOn) {
    const w = e.s.size * 1.4;
    g.fillStyle = flashOn ? "#fff" : (colorOf[e.id] || (e.side === 1 ? "#8c2a1e" : "#3a3838"));
    const lean = e.side === -1 ? 6 : 0;
    g.beginPath(); g.moveTo(x - w / 2, y); g.lineTo(x + w / 2, y); g.lineTo(x + w / 2 - lean, y - h); g.lineTo(x - w / 2 - lean, y - h); g.fill();
    g.beginPath(); g.arc(x - lean, y - h - w * 0.35, w * 0.45, 0, 7); g.fill();
    if (e.side === -1) { g.fillStyle = "#ff7a1a"; g.fillRect(x - lean - w * 0.35, y - h - w * 0.4, 4, 3); }
    else { g.fillStyle = "#d49a3a"; g.fillRect(x - w / 2, y - h * 0.55, w, 4); }
  }

  function animFor(e) {
    switch (e.state) {
      case "walk": return "walk"; case "attack": return "attack"; case "hit": return "hit"; case "die": return "die";
      case "special": return "special"; case "sweep": return "sweep"; case "summon": return "summon"; case "spit": return "spit";
      case "windup": return (e.windup && e.windup.kind === "summon") ? "summon" : (e.windup && e.windup.kind.startsWith("spit")) ? "spit" : "sweep";
      default: return "idle";
    }
  }

  // soft shadow + ember glow pre-rendered once; drawn as images instead of path fills per entity
  const blob = (r, g2, b2, a) => { const c = document.createElement("canvas"); c.width = 64; c.height = 64; const cg = c.getContext("2d");
    const gr = cg.createRadialGradient(32, 32, 4, 32, 32, 32); gr.addColorStop(0, `rgba(${r},${g2},${b2},${a})`); gr.addColorStop(1, `rgba(${r},${g2},${b2},0)`);
    cg.fillStyle = gr; cg.fillRect(0, 0, 64, 64); return c; };
  const hx = (c) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
  const FLASHB = blob(255, 214, 140, 0.95);
  const SHADOW = blob(0, 0, 0, 0.55), GLOW = blob(...hx(TH.elite || "#ff6a1a"), 0.6);
  function drawEntity(B, e, alpha) {
    const x = e.px + (e.x - e.px) * alpha;
    if (x < R.camX - 160 || x > R.camX + R.W + 160) return;          // off-screen skip
    let sx = x - R.camX; const y = B.F.groundY + e.lane * 0.35;
    const big = e.kind === "boss" ? 1 : 1;
    const lie = e.side === -1 ? 3.4 : 2.3;
    const fadeOut = !e.alive && e.dieT > lie ? Math.max(0, 1 - (e.dieT - lie) / 0.7) : 1;
    if (fadeOut <= 0) return;
    // shadow
    g.globalAlpha = 0.8 * fadeOut;
    g.drawImage(SHADOW, sx - e.s.size * 1.5, y - e.s.size * 0.45, e.s.size * 3, e.s.size * 0.9);
    // elite / enrage glow
    if ((e.elite || e.enraged || (e.kind === "boss" && e.phase2)) && e.alive) {
      g.globalAlpha = 0.55 + 0.25 * Math.sin(R.t * 6);
      g.drawImage(GLOW, sx - e.s.size * 2, y - e.s.size * 4.8, e.s.size * 4, e.s.size * 5.4);
    }
    g.globalAlpha = fadeOut;
    let anim = animFor(e), t = e.stateT, fps;
    if (e.state === "attack") {           // play so the anim's hit frame lands on the sim's hit moment
      const sp = sprites[e.sprite]; const a = sp && sp.anims.attack;
      if (a) fps = (a.hit != null ? a.hit : 4) / Math.max(0.12, Math.min(0.32, e.s.rate * 0.35));
    }
    if (e.state === "windup" && e.windup) {   // hold the raised pose for the whole warning
      const sp = sprites[e.sprite]; const a = sp && sp.anims[anim];
      if (a) { const hf = a.hit != null ? a.hit : 3; t = Math.min(e.stateT, (hf - 1) / (a.fps || 10)); }
    }
    if (e.stun > 0) { anim = "hit"; t = 0.05; }
    let scale = (e.elite ? 1.12 : 1) * (e.kind === "boss" ? 1 : CH), sy = 1, lx = 0;
    const born = R.births.get(e);
    if (born != null) { const k = (R.t - born) / 0.28; if (k < 1) { const o = 1 - Math.pow(1 - k, 3); sy = 0.55 + 0.45 * o + 0.18 * Math.sin(k * Math.PI); scale *= 0.8 + 0.2 * o; } else R.births.delete(e); }
    if (e.flash > 0 && e.alive && !R.reduced) lx = -e.side * 5 * (e.flash / 0.12);
    const sx0 = sx; sx += lx;
    const ok = spriteDraw(e.sprite, anim, t, sx, y, { fps, scale, sy }) || spriteDraw(e.s.baseSprite || e.id, anim, t, sx, y, { fps, scale });
    if (ok && e.flash > 0) { g.globalAlpha = Math.min(1, e.flash / 0.12) * 0.5 * fadeOut; spriteDraw(e.sprite, anim, t, sx, y, { fps, scale, white: true }) || spriteDraw(e.s.baseSprite || e.id, anim, t, sx, y, { fps, scale, white: true }); }
    if (!ok) placeholder(e, sx, y, e.s.size * 4.4 * (e.alive ? 1 : 0.4), e.flash > 0);
    g.globalAlpha = 1;
    // health bar when hurt (not for boss: boss has its own bar)
    if (e.alive && e.hp < e.maxHp && e.kind !== "boss") {
      const w = Math.max(22, e.s.size * 1.6), hy = y - Math.min(170, e.s.size * 4.6) - 14;
      g.fillStyle = "rgba(0,0,0,.55)"; g.fillRect(sx - w / 2 - 1, hy - 1, w + 2, 5);
      g.fillStyle = e.side === 1 ? "#7fd36b" : "#ff7a3a"; g.fillRect(sx - w / 2, hy, w * Math.max(0, e.hp / e.maxHp), 3);
    }
    if (e.vuln > 0 && e.alive) { g.fillStyle = "#ffe9a0"; for (let i = 0; i < 4; i++) { const a = R.t * 4 + i * 1.57; g.fillRect(sx + Math.cos(a) * 26 - 3, y - 250 + Math.sin(a) * 5, 6, 6); } }
    if (e.stun > 0 && e.alive) { g.fillStyle = "#ffe9a0"; for (let i = 0; i < 3; i++) { const a = R.t * 5 + i * 2.1; g.fillRect(sx + Math.cos(a) * 12 - 2, y - Math.min(170, e.s.size * 4.6) - 4 + Math.sin(a) * 3, 4, 4); } }
  }

  function drawCastle(B, c, side) {
    const sx = c.x - R.camX; if (sx < -400 || sx > R.W + 400) return;
    const f = c.hp / c.max, st = f > 0.6 ? 0 : f > 0.25 ? 1 : 2;
    const id = (side === 1 ? "keep_" : "maw_") + st;
    const y = B.F.groundY + 4;
    const shakeX = c.hitT > 0 ? (Math.random() - 0.5) * 4 : 0;
    if (!spriteDraw(id, "idle", R.t, sx + shakeX, y)) {
      g.fillStyle = side === 1 ? "#4b4440" : "#2a2222";
      g.fillRect(sx - 70 + shakeX, y - 260 * (1 - st * 0.18), 140, 260 * (1 - st * 0.18));
      g.fillStyle = side === 1 ? "#ffb347" : "#ff6a1a"; g.fillRect(sx - 12, y - 250 * (1 - st * 0.18), 24, 22);
    }
    if (c.hitT > 0 && atlases.castles) { g.globalAlpha = c.hitT / 0.15 * 0.5; spriteDraw(id, "idle", R.t, sx + shakeX, y, { white: true }); g.globalAlpha = 1; }
    if (st >= 1 && R.quality > 0 && Math.random() < 0.25) part(c.x + (Math.random() - 0.5) * 100, y - 120 - Math.random() * 100, (Math.random() - 0.5) * 10, -30, 1.6, 9, "#3c3533", 2, -15);
    if (c === B.gate && c.sealed) { g.globalAlpha = 0.18 + 0.08 * Math.sin(R.t * 3); g.fillStyle = TH.enemyGlow || "#ff5a1a"; g.beginPath(); g.ellipse(sx, y - 120, 110, 150, 0, 0, 7); g.fill(); g.globalAlpha = 1; }
  }

  function drawProj(B, p, alpha) {
    const x = p.px ? p.px + (p.x - p.px) * alpha : p.x, y = p.py ? p.py + (p.y - p.py) * alpha : p.y;
    const sx = x - R.camX; if (sx < -50 || sx > R.W + 50) return;
    const ang = Math.atan2(p.y - (p.py || p.y), p.x - (p.px || p.x));
    const id = p.kind === "bolt" ? "bolt" : p.kind === "spit" ? "spit" : "arrow";
    if (!spriteDraw(id, "idle", R.t, sx, y, { rot: id === "spit" ? 0 : ang })) {
      g.save(); g.translate(sx, y); g.rotate(ang);
      g.fillStyle = p.kind === "spit" ? "#ff7a1a" : p.kind === "bolt" ? "#e8d0a0" : "#d8c8a8";
      g.fillRect(p.kind === "bolt" ? -26 : -10, -1.5, p.kind === "bolt" ? 30 : 14, p.kind === "bolt" ? 4 : 2); g.restore();
    }
    if ((p.kind === "bolt" || p.kind === "spit") && R.quality > 0 && Math.random() < 0.7) part(x, y, (Math.random() - 0.5) * 30, -10, 0.4, 2.5, "#ffa040", 1, -40);
  }

  function drawPatches(B) {
    for (const p of B.patches) {
      if (p.t <= 0) continue; const sx = p.x - R.camX; if (sx < -80 || sx > R.W + 80) continue;
      const a = Math.min(1, p.t);
      if (!spriteDraw("fire_patch", "idle", R.t + p.x, sx, B.F.groundY + 6, { scale: p.r / 45 })) {
        g.globalAlpha = 0.45 * a; g.fillStyle = "#ff6a1a"; g.beginPath(); g.ellipse(sx, B.F.groundY + 4, p.r, 8, 0, 0, 7); g.fill(); g.globalAlpha = 1;
      }
      if (R.quality > 0 && Math.random() < 0.4) part(p.x + (Math.random() - 0.5) * p.r * 1.6, B.F.groundY, 0, -60, 0.7, 3, "#ffb050", 1, -80);
    }
  }

  function drawMarks(B) {   // boss attack warnings on the ground
    for (const m of B.marks) {
      if (m.t <= 0) continue; const sx = m.x - R.camX;
      const k = 1 - m.t / m.max, pulse = 0.5 + 0.5 * Math.sin(R.t * 18);
      g.strokeStyle = `rgba(255,70,30,${0.5 + 0.4 * pulse})`; g.lineWidth = 3;
      g.beginPath(); g.ellipse(sx, B.F.groundY + 2, m.r, 12, 0, 0, 7); g.stroke();
      g.fillStyle = `rgba(255,70,30,${0.15 + 0.25 * k})`; g.beginPath(); g.ellipse(sx, B.F.groundY + 2, m.r * k, 12 * k, 0, 0, 7); g.fill();
    }
    const boss = B.boss;
    if (boss && boss.alive && boss.windup && boss.windup.kind === "sweep") {
      const r = boss.s.boss.sweep.radius, sx = boss.x - R.camX - r * 0.5, pulse = 0.5 + 0.5 * Math.sin(R.t * 20);
      g.fillStyle = `rgba(255,60,20,${0.18 + 0.22 * pulse})`;
      g.beginPath(); g.ellipse(sx, B.F.groundY + 2, r * 0.75, 16, 0, 0, 7); g.fill();
    }
  }

  function drawAim(B) {
    const a = R.aim; if (!a) return;
    const G = B.g.ballista.gravity; let x = B.ballista.x + 30, y = B.ballista.y - 4, vx = a.vx, vy = a.vy;
    g.fillStyle = "rgba(255,226,160,0.9)";
    for (let i = 0; i < 60; i++) {
      const dt = 0.05; vy += G * dt; x += vx * dt; y += vy * dt;
      if (y > B.F.groundY - 4) break;
      if (i % 2 === 0) { const r = 3.2 - i * 0.03; g.beginPath(); g.arc(x - R.camX, y, Math.max(1.2, r), 0, 7); g.fill(); }
    }
    a.landX = x;
    g.strokeStyle = "rgba(255,200,120,0.9)"; g.lineWidth = 2.5;
    g.beginPath(); g.ellipse(x - R.camX, B.F.groundY, B.g.ballista.splash, 9, 0, 0, 7); g.stroke();
  }

  function drawBallista(B) {
    const sx = B.ballista.x - R.camX; if (sx < -100) return;
    if (B.keep.hp / B.keep.max <= 0.25 && sprites.keep_2) return;      // platform collapsed on the ruined keep
    const ang = R.aim ? Math.atan2(R.aim.vy, R.aim.vx) : (R.lastAng != null ? R.lastAng : -0.35);
    if (R.aim) R.lastAng = ang;
    const rc = R.recoil * R.recoil * 16, bx = sx - Math.cos(ang) * rc, by = B.ballista.y - Math.sin(ang) * rc;
    if (R.muzzle > 0) {
      const mx = sx + Math.cos(ang) * 78, my = B.ballista.y + Math.sin(ang) * 78 - 14, r = 46 + 60 * (1 - R.muzzle);
      g.globalCompositeOperation = "lighter"; g.globalAlpha = R.muzzle; g.drawImage(FLASHB, mx - r, my - r, r * 2, r * 2);
      g.globalAlpha = 1; g.globalCompositeOperation = "source-over";
    }
    if (!spriteDraw("ballista", "idle", 0, bx, by, { rot: ang })) {
      g.save(); g.translate(sx, B.ballista.y); g.rotate(ang); g.fillStyle = "#6a4a2a"; g.fillRect(-10, -5, 60, 10);
      g.fillStyle = "#b08a3a"; g.fillRect(0, -18, 6, 36); g.restore();
    }
  }

  // ---------------------------------------------------------------- frame
  R.draw = (B, alpha, dtReal) => {
    R.t += dtReal;
    // adaptive quality: watch frame time, step effects (and resolution) down if the phone struggles
    R.fpsAvg = R.fpsAvg * 0.95 + (1 / Math.max(0.001, dtReal)) * 0.05;
    if (R.fpsAvg < 45) R.lowFrames++; else R.lowFrames = Math.max(0, R.lowFrames - 2);
    if (R.lowFrames > 90 && R.quality > 0) { R.quality--; R.lowFrames = 0; if (R.quality === 0 && R.dprCap > 1.5) { R.dprCap = 1.5; R.resize(); } }
    if (R.camTarget != null) { R.camX += (R.camTarget - R.camX) * Math.min(1, dtReal * 6); if (Math.abs(R.camTarget - R.camX) < 1) R.camTarget = null; }
    R.clampCam(B);
    g.setTransform(1, 0, 0, 1, 0, 0);
    // shake (trauma squared), applied as a translate
    R.shake = Math.max(0, R.shake - dtReal * 1.6);
    const tr = R.shake * R.shake * 14;
    R.shakeX = (Math.random() - 0.5) * tr - R.kick * R.kick * 7; R.shakeY = (Math.random() - 0.5) * tr;
    g.setTransform(R.scale, 0, 0, R.scale, R.shakeX * R.scale, R.shakeY * R.scale);
    const L = BG[B.stage.bg] || BG[R.region] || {};
    if (L.sky) drawLayer(L.sky, 0); else { const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, "#2a1418"); gr.addColorStop(1, "#c9602a"); g.fillStyle = gr; g.fillRect(-20, -20, R.W + 40, H + 40); }
    drawLayer(L.far || (BG.r1 && BG.r1.far), R.camX); drawLayer(L.mid || (BG.r1 && BG.r1.mid), R.camX);
    if (L.near || (BG.r1 && BG.r1.near)) drawLayer(L.near || BG.r1.near, R.camX);
    else { g.fillStyle = "#2b2023"; g.fillRect(-20, B.F.groundY - 6, R.W + 40, H); }
    R.recoil = Math.max(0, R.recoil - dtReal * 3.2); R.muzzle = Math.max(0, R.muzzle - dtReal * 9); R.kick = Math.max(0, R.kick - dtReal * 7);
    for (const d of R.decals) {       // craters and ink on the sand
      if (d.t <= 0) continue; d.t -= dtReal; const dx = d.x - R.camX; if (dx < -120 || dx > R.W + 120) continue;
      const a = Math.min(1, d.t / 2.5) * 0.5, gr = Math.min(1, (d.max - d.t) / 0.25);
      g.globalAlpha = a; g.fillStyle = d.c; g.beginPath(); g.ellipse(dx, B.F.groundY + 3, d.r * gr, d.r * 0.2 * gr, 0, 0, 7); g.fill();
      if (d.glow) { g.globalAlpha = a * 0.7; g.fillStyle = TH.enemyGlow || "#8dffad"; g.beginPath(); g.ellipse(dx - d.r * 0.2, B.F.groundY + 2, d.r * 0.22 * gr, d.r * 0.05 * gr, 0, 0, 7); g.fill(); }
      g.globalAlpha = 1;
    }
    drawCastle(B, B.keep, 1); drawCastle(B, B.gate, -1); drawBallista(B);
    drawPatches(B); drawMarks(B);
    // entities sorted by lane (back to front) — reuse one array
    const list = R._list || (R._list = []); list.length = 0;
    for (const e of B.ents) if (!e.gone) list.push(e);
    list.sort((a, b) => a.lane - b.lane || (b.alive ? 1 : 0) - (a.alive ? 1 : 0));
    for (const e of list) drawEntity(B, e, alpha);
    for (const p of B.projs) if (p.alive) drawProj(B, p, alpha);
    if (R.grade) {      // night stages: moonlight grade over the sunset-lit figures and forts (one fill)
      g.globalCompositeOperation = "multiply"; g.fillStyle = R.grade; g.fillRect(-30, -30, R.W + 60, H + 60); g.globalCompositeOperation = "source-over";
    }
    drawAim(B);
    for (const k of R.rings) {        // shock rings on the ground
      if (k.t <= 0) continue; k.t -= dtReal; const q = 1 - Math.max(0, k.t) / 0.32;
      g.strokeStyle = k.c + (0.75 * (1 - q)).toFixed(2) + ")"; g.lineWidth = 5 * (1 - q) + 1;
      g.beginPath(); g.ellipse(k.x - R.camX, k.y + 2, k.r * (0.35 + 0.65 * q), k.r * 0.2 * (0.35 + 0.65 * q), 0, 0, 7); g.stroke();
    }
    for (const k of R.sparks) {       // four-point hit sparks, two frames long
      if (k.t <= 0) continue; k.t -= dtReal; const q = Math.max(0, k.t) / 0.11, r = k.s * (1.25 - 0.5 * q);
      g.save(); g.translate(k.x - R.camX, k.y); g.rotate(k.rot); g.fillStyle = k.c; g.globalAlpha = 0.35 + 0.65 * q;
      g.beginPath(); g.moveTo(0, -r); g.lineTo(r * 0.16, -r * 0.16); g.lineTo(r, 0); g.lineTo(r * 0.16, r * 0.16); g.lineTo(0, r); g.lineTo(-r * 0.16, r * 0.16); g.lineTo(-r, 0); g.lineTo(-r * 0.16, -r * 0.16); g.closePath(); g.fill();
      g.restore(); g.globalAlpha = 1;
    }
    for (const f of R.fx) {          // one-shot flipbooks (explosions, flare ring)
      if (f.t < 0) continue; f.t += dtReal; const sp = sprites[f.id]; const a = sp && sp.anims.idle;
      if (!a || f.t * (a.fps || 14) >= a.frames.length) { f.t = -1; continue; }
      g.globalCompositeOperation = "lighter"; spriteDraw(f.id, "idle", f.t, f.x - R.camX, f.y, { scale: f.s }); g.globalCompositeOperation = "source-over";
    }
    // particles: update + draw normal ones, then all glowing ones in a single additive pass
    const dt = dtReal;
    for (let pass = 0; pass < 2; pass++) {
      if (pass === 1) g.globalCompositeOperation = "lighter";
      for (const p of R.parts) {
        if (p.life <= 0 || (pass === 1) !== (p.k === 1)) continue;
        p.life -= dt; p.vy += p.gr * dt; p.x += p.vx * dt; p.y += p.vy * dt;
        if (p.k === 0 && p.y > B.F.groundY + 8) { p.y = B.F.groundY + 8; p.vx *= 0.5; p.vy = 0; }
        const sx = p.x - R.camX; if (sx < -20 || sx > R.W + 20) continue;
        const a = Math.max(0, p.life / p.max);
        if (p.k === 1) { g.globalAlpha = a; g.fillStyle = p.c; g.fillRect(sx - p.size / 2, p.y - p.size / 2, p.size, p.size); }
        else if (p.k === 2) { g.globalAlpha = a * 0.5; g.fillStyle = p.c; g.beginPath(); g.arc(sx, p.y, p.size * (1.6 - a * 0.6), 0, 7); g.fill(); }
        else if (p.k === 3) { g.globalAlpha = Math.min(0.5, a) * 0.6; g.fillStyle = p.c; g.fillRect(sx - 1, p.y - 1, 2, 2); }
        else { g.globalAlpha = Math.min(1, a * 1.5); g.fillStyle = p.c; g.fillRect(sx - p.size / 2, p.y - p.size / 2, p.size, p.size); }
      }
    }
    g.globalCompositeOperation = "source-over";
    g.globalAlpha = 1;
    // ambient embers drifting up (the Ashen Marches feel)
    if (R.quality > 1 && Math.random() < 0.25) part(R.camX + Math.random() * R.W, TH.ambientGlow === false ? Math.random() * H * 0.7 : H + 4, TH.ambientGlow === false ? 20 + Math.random() * 25 : (Math.random() - 0.5) * 20, TH.ambientGlow === false ? 4 - Math.random() * 8 : -30 - Math.random() * 30, 6, 2, TH.ambient || "#ff9a40", TH.ambientGlow === false ? 3 : 1, -2);
    // damage numbers
    g.textAlign = "center"; g.lineWidth = 3; g.strokeStyle = "rgba(20,10,10,.85)";
    for (const n of R.nums) {
      if (n.life <= 0) continue; n.life -= dt; n.y -= 34 * dt;
      const a = Math.min(1, n.life / 0.35), sx = n.x - R.camX, pop = n.life > 0.75 ? 1 + (n.life - 0.75) * 2 : 1;
      g.globalAlpha = a; g.font = `800 ${Math.round((n.big ? 22 : 15) * pop)}px system-ui, sans-serif`;
      g.strokeText(n.t, sx, n.y); g.fillStyle = n.c; g.fillText(n.t, sx, n.y);
    }
    g.globalAlpha = 1;
    if (B.rally > 0) { g.fillStyle = `rgba(255,190,90,${0.06 + 0.03 * Math.sin(R.t * 6)})`; g.fillRect(-20, -20, R.W + 40, H + 40); }
    if (R.flashA > 0) { g.globalAlpha = R.flashA; g.fillStyle = R.flashC; g.fillRect(-20, -20, R.W + 40, H + 40); g.globalAlpha = 1; R.flashA = Math.max(0, R.flashA - dtReal * 2.2); }
    // edge vignette for depth
    if (R.quality > 0) {
      if (!R._vg) {   // vignette rendered once at low resolution, stretched (soft by nature)
        const c = document.createElement("canvas"); c.width = 256; c.height = 128; const cg = c.getContext("2d");
        const v = cg.createRadialGradient(128, 64, 40, 128, 64, 150); v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, "rgba(10,4,4,.45)");
        cg.fillStyle = v; cg.fillRect(0, 0, 256, 128); R._vg = c;
      }
      g.drawImage(R._vg, 0, 0, R.W, H);
    }
  };
  R.resetForBattle = () => { for (const p of R.parts) p.life = 0; for (const n of R.nums) n.life = 0; for (const d of R.decals) d.t = 0; for (const k of R.sparks) k.t = 0; for (const k of R.rings) k.t = 0; R.hitstop = 0; R.recoil = 0; R.muzzle = 0; R.kick = 0; R.lastAng = null; R.camX = 0; R.shake = 0; R.flashA = 0; R.aim = null; R.slowmo = 0; R._vg = null; };
  return R;
}
