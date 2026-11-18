// Battle simulation. Fixed step, deterministic for a given seed and input list, no DOM, no drawing.
// The renderer reads state and drains `events`; the headless balance runner just calls step().
import { rng, unitStats, enemyStats, heroStats } from "./stats.js";

const DT_DEFAULT = 1 / 30;

/**
 * @param content {units, enemies, game, stage}
 * @param progress {unitLevels:{id:lv}, keep, ballista, energyMax, energyRegen, hero, abilities:{id:lv}}
 */
export function createBattle(content, stage, progress, seed = 1) {
  const g = content.game, F = g.field;
  const lv = (k, d = 1) => (progress && progress[k]) || d;
  const unitDefs = Object.fromEntries(content.units.units.map((u) => [u.id, u]));
  const enemyDefs = Object.fromEntries(content.enemies.enemies.map((e) => [e.id, e]));
  const cards = (stage.available || []).map((id) => {
    const s = unitStats(unitDefs[id], (progress?.unitLevels || {})[id] || 1, content.units.levels, (progress?.skills || {})[id]);
    return { id, stats: s, cd: 0 };
  });
  const keepMax = g.keep.hp + g.keep.hpPerLevel * (lv("keep") - 1);
  const B = {
    t: 0, dt: DT_DEFAULT, tick: 0, rand: rng(seed), stage, content, F, g,
    energy: g.energy.start, energyMax: g.energy.max + g.energy.maxPerLevel * (lv("energyMax") - 1),
    regen: g.energy.regen + g.energy.regenPerLevel * (lv("energyRegen") - 1),
    keep: { hp: keepMax, max: keepMax, x: F.playerCastleX, front: F.playerCastleX + 110, hitT: 0 },
    gate: { hp: stage.enemyCastleHp, max: stage.enemyCastleHp, x: F.enemyCastleX, front: F.enemyCastleX - 190, hitT: 0,     // monsters gather on open sand, not inside the Grotto mouth
            sealed: stage.winOn === "boss" },
    cards, unitDefs, enemyDefs,
    ents: [], nextId: 1, projs: [], patches: [], marks: [], scheduled: [],
    ballista: { reload: 0, maxReload: Math.max(1.2, g.ballista.reload - g.ballista.reloadPerLevel * (lv("ballista") - 1)),
                dmg: g.ballista.dmg * (1 + g.ballista.dmgPerLevel * (lv("ballista") - 1)), x: F.playerCastleX + 118, y: F.groundY - 223 },     // Long Tom's pivot on the (1.2x) Gullwake
    abilities: (stage.abilities || []).map((id) => ({ id, cfg: g.abilities[id], level: (progress?.abilities || {})[id] || 1, cd: 6 })),
    hero: stage.hero ? { charge: 0, need: g.hero.charge, called: false, ent: null, level: lv("hero") } : null,
    rally: 0, heldT: 0, waveHold: false, waveClock: 0, waves: (stage.waves || []).map((w) => ({ ...w, done: 0, next: w.t })),
    loop: stage.loop ? { ...stage.loop, timer: stage.loop.start } : null,
    triggers: (stage.triggers || []).map((t) => ({ ...t, fired: false })),
    boss: null, bossSpawned: false, result: null, endT: 0, emul: stage.power || 1, bmul: stage.bossPower || 1,
    stats: { sent: 0, kills: 0, shots: 0, shotHits: 0, dmgDealt: 0, abilityUses: 0 },
    events: [], inputs: [],
  };
  return B;
}

// ------------------------------------------------------------------ inputs (queued, applied at next tick)
export const input = {
  send: (B, id) => B.inputs.push({ k: "send", id }),
  fire: (B, vx, vy) => B.inputs.push({ k: "fire", vx, vy }),
  ability: (B, id, x) => B.inputs.push({ k: "ability", id, x }),
  hero: (B) => B.inputs.push({ k: "hero" }),
};

export function canSend(B, id) {
  const c = B.cards.find((c) => c.id === id);
  return !!c && c.cd <= 0 && B.energy >= c.stats.cost && !B.result;
}

function ev(B, type, a = {}) { a.type = type; B.events.push(a); }

function applyInputs(B) {
  for (const i of B.inputs) {
    if (B.result) break;
    if (i.k === "send") {
      const c = B.cards.find((c) => c.id === i.id);
      if (!c || c.cd > 0 || B.energy < c.stats.cost) { ev(B, "denied", { id: i.id }); continue; }
      B.energy -= c.stats.cost; c.cd = c.stats.cooldown; B.stats.sent++;
      const n = c.stats.traits.count || 1;
      for (let k = 0; k < n; k++) spawn(B, c.stats, 1, B.keep.front - 10 - k * 14);
      ev(B, "send", { id: i.id });
    } else if (i.k === "fire") {
      if (B.ballista.reload > 0) continue;
      B.ballista.reload = B.ballista.maxReload; B.stats.shots++;
      B.projs.push({ kind: "bolt", x: B.ballista.x + 30, y: B.ballista.y - 4, vx: i.vx, vy: i.vy, side: 1, dmg: B.ballista.dmg,
        splash: B.g.ballista.splash, alive: true, t: 0, px: 0, py: 0 });
      ev(B, "fire", {});
    } else if (i.k === "ability") {
      const a = B.abilities.find((a) => a.id === i.id);
      if (!a || a.cd > 0) continue;
      a.cd = a.cfg.cooldown; B.stats.abilityUses++;
      if (a.id === "ember_rain") {
        const mul = 1 + a.cfg.dmgPerLevel * (a.level - 1);
        for (let s = 0; s < a.cfg.stones; s++) {
          const x = i.x + (B.rand() - 0.5) * a.cfg.spread * 2;
          const at = B.t + (s / a.cfg.stones) * a.cfg.duration + 0.5;
          B.scheduled.push({ at, kind: "stone", x, dmg: a.cfg.dmg * mul, splash: a.cfg.splash });
        }
        ev(B, "ember_rain", { x: i.x });
      } else if (a.id === "rally") {
        B.rally = a.cfg.time + a.cfg.timePerLevel * (a.level - 1);
        for (const e of B.ents) if (e.alive && e.side === 1) { heal(B, e, e.maxHp * a.cfg.heal); }
        ev(B, "rally", {});
      }
    } else if (i.k === "hero") {
      const h = B.hero;
      if (!h || h.called || h.charge < h.need) continue;
      h.called = true;
      h.ent = spawn(B, heroStats(B.g.hero, h.level), 1, B.keep.front);
      h.ent.flareT = 3;
      ev(B, "hero", {});
    }
  }
  B.inputs.length = 0;
}

// ------------------------------------------------------------------ entities
/** Stage difficulty: scales enemy health and damage (tuned by tools/tune.mjs). */
function powered(B, s, m) { if (m !== 1) { s.hp *= m; s.dmg *= Math.pow(m, 0.75); s.shellMul = m; } return s; }

function spawn(B, s, side, x) {
  let e = null;
  for (const o of B.ents) if (!o.alive && o.gone) { e = o; break; }   // reuse dead slots (no per-spawn garbage)
  if (!e) { e = {}; B.ents.push(e); }
  e.uid = B.nextId++; e.s = s; e.id = s.id; e.kind = s.kind; e.side = side; e.sprite = s.sprite;
  e.x = x; e.px = x; e.lane = (B.rand() - 0.5) * 2 * B.F.laneJitter; e.hp = s.hp; e.maxHp = s.hp;
  e.alive = true; e.gone = false; e.state = "walk"; e.stateT = 0; e.atkCd = 0.2 + B.rand() * 0.3; e.hitAt = -1;
  e.target = null; e.slow = 0; e.slowT = 0; e.stun = 0; e.burn = 0; e.burnT = 0; e.kb = 0; e.dieT = 0;
  e.flash = 0; e.firstDone = false; e.healCd = 0; e.elite = !!s.elite; e.flareT = 0;
  e.bossT = null; e.windup = null; e.enraged = false; e.vuln = 0; e.phase2 = false;
  e.shell = ((s.traits && s.traits.shell) || 0) * (s.shellMul || 1); e.crackT = 0; e.netT = 0; e.stunImm = 0; e.leap = null; e.vaulted = false; e.lock = null;
  e.shots = 0; e._atk = 0;
  if (s.boss) e.bossT = { sweep: 4, summon: 10, spit: 6 };
  ev(B, "spawn", { e });
  return e;
}

function heal(B, e, amt) {
  const before = e.hp; e.hp = Math.min(e.maxHp, e.hp + amt);
  if (e.hp > before + 0.5) ev(B, "heal", { e, amt: e.hp - before });
}

function damage(B, e, amt, src, opts) {
  if (!e.alive) return 0;
  let d = amt; const T = e.s.traits || {}, o = opts || {}, kind = o.kind;
  if (T.meleeGuard && (o.melee || (o.blast && T.blastGuard)) && !(src && src.s && src.s.traits.underGuard)) d *= 1 - T.meleeGuard;     // the hatch door takes blows and blasts (Scuttlers bite under it)
  if (T.armor) d *= 1 - T.armor;
  if (e.vuln > 0) d *= 1.6;
  if (e.netT > 0 && e.netHook) d *= 1 + e.netHook;
  // Shelled: the shell soaks hits from the front until it breaks; a blunt hit shatters it at once; burn already on it keeps burning
  if (e.shell > 0 && kind !== "burn") {
    if (o.blunt) { e.shell = 0; ev(B, "shellBreak", { e }); }
    else if (!o.behind) {
      const soak = Math.min(e.shell, d); e.shell -= o.blast ? soak * 0.5 : soak; d -= soak;     // blasts ring off the bronze
      if (e.shell <= 0) ev(B, "shellBreak", { e });
      if (d <= 0) { ev(B, "shellHit", { e }); return 0; }
    }
  }
  // Armoured: plates take a fixed amount off every hit (halved while cracked); burn and harpoons go through
  if (T.plate && kind !== "burn" && !o.pierceArmor) {
    const before = d; d = Math.max(0, d - T.plate * (e.crackT > 0 ? 0.5 : 1));
    if (d < before * 0.5) ev(B, "plateHit", { e });
  }
  if (T.plate && o.blunt) { if (!(e.crackT > 0)) ev(B, "crack", { e }); e.crackT = 6; }
  if (d <= 0) return 0;
  e.hp -= d; if (!opts || opts.kind !== "burn") e.flash = 0.12;   // damage-over-time never flashes
  if (src && src.side === 1) B.stats.dmgDealt += d;
  ev(B, "dmg", { e, amt: d, crit: o.crit, kind });
  if (e.hp <= 0) kill(B, e);
  else if (opts && opts.kb) { e.kb = opts.kb * -e.side; e.state = "hit"; e.stateT = 0; e.hitAt = -1; }
  return d;
}

function kill(B, e) {
  e.alive = false; e.state = "die"; e.stateT = 0; e.dieT = 0; e.hitAt = -1;
  if (e.side === -1) B.stats.kills++;
  ev(B, "die", { e });
  const db = e.s.traits && e.s.traits.deathBlast;
  if (db) {
    explode(B, e.x, db.radius, db.dmg, null, "both", { blast: true, kind: "blast" });
    ev(B, "burst", { x: e.x, r: db.radius });
  }
  if (e.kind === "boss") { ev(B, "bossDead", { e }); if (B.stage.winOn === "boss") end(B, "win"); }
}

function explode(B, x, r, dmg, src, who, opts) {
  for (const o of B.ents) {
    if (!o.alive) continue;
    if (airborne(o) && !(opts && opts.air)) continue;        // a blast on the sand passes under a flier
    if (opts && opts.lob && o.s.traits && o.s.traits.nimble) continue;      // a lobbed glob is too slow to catch a running Rope Rat
    if (who === "enemies" && o.side !== -1) continue;
    if (who === "players" && o.side !== 1) continue;
    if (Math.abs(o.x - x) <= r + o.s.size * 0.5) damage(B, o, dmg, src, opts);
  }
}

function castleOf(B, side) { return side === 1 ? B.gate : B.keep; }

function hitCastle(B, side, amt) {
  const c = castleOf(B, side);
  if (c === B.gate && c.sealed) { ev(B, "sealed", {}); return; }
  c.hp -= amt; c.hitT = 0.15;
  if (side === 1) B.stats.dmgDealt += amt;
  ev(B, "castleHit", { side: -side, amt });
  if (c.hp <= 0) { c.hp = 0; end(B, side === 1 ? "win" : "lose"); }
}

function end(B, r) {
  if (B.result) return;
  B.result = r; B.endT = B.t;
  ev(B, r === "win" ? "win" : "lose", {});
}

// ------------------------------------------------------------------ traits that change who can fight whom
/** In the air: a Flying monster that is not netted. Melee cannot reach it and ground blasts pass under it. */
export function airborne(e) { return !!(e.s.traits && e.s.traits.flying) && !(e.netT > 0) && e.alive; }
/** Fights hand to hand (no projectile, not a mender). */
function melee(e) { const T = e.s.traits || {}; return !T.projectile && !T.heal; }
function canHit(a, o) { return !airborne(o) || !melee(a); }
const PRIORITY = (o) => { const T = o.s.traits || {}; return T.siege || T.heal ? 2 : o.s.large ? 1 : 0; };

/** Nearest living opponent in front of e (in its walking direction) within reach, else null.
 *  Fliers ignore hand-to-hand crew and go for shooters, menders and the fort; siege picks the furthest crew it can
 *  reach; snipers pick siege and menders first; swarm monsters slip past a crew member who is already surrounded. */
function findTarget(B, e, reach) {
  let best = null, bd = 1e9;
  const T = e.s.traits || {}, fly = airborne(e);
  for (const o of B.ents) {
    if (!o.alive || o.side === e.side) continue;
    if (!canHit(e, o)) continue;
    if (e.side === 1 && o.s.traits.siege && o.x > B.gate.front + 30 && !T.sniper) continue;     // inside the Grotto's mouth: only a leap or a harpoon reaches it
    if (fly && melee(o)) continue;
    const d = (o.x - e.x) * e.side;            // distance ahead
    if (d < -(e.s.size + o.s.size) * 0.5) continue;  // behind
    const gap = Math.abs(d) - (e.s.size + o.s.size) * 0.5;
    if (gap > reach) continue;
    if (T.slip && o._atk >= 1 && !(e.slowT > 0) && !(e.netT > 0)) continue;     // held by the song or a net, a swarm cannot slip round
    let score = gap;
    if (T.siege) score = -gap;                         // lob over the front line onto the back line
    if (T.sniper) score = gap - PRIORITY(o) * 1000;
    if (o.s.traits.taunt && !T.siege && !fly) score -= 500;
    if (score < bd) { bd = score; best = o; }
  }
  return best;
}

function speedMul(B, e) {
  let m = 1;
  if (e.slowT > 0) m *= 1 - e.slow;
  if (e.netT > 0) m *= 1 - (e.netSlow || 0.5);
  if (e.side === 1 && B.rally > 0) m *= B.g.abilities.rally.speedMul;
  if (e.enraged) m *= e.s.traits.enrage.speed;
  if (e.kind === "boss" && e.phase2) m *= e.s.boss.phase2.speedMul;
  return m;
}

function rateMul(B, e) {
  let m = 1;
  if (e.slowT > 0) m /= 1 - e.slow;          // slowed monsters strike as much slower as they walk
  if (e.side === 1 && B.rally > 0) m *= B.g.abilities.rally.rateMul;
  if (e.hasteT > 0) m *= 1 - e.haste;
  if (e.enraged) m *= e.s.traits.enrage.rate;
  return m;
}

function strike(B, e) {
  const s = e.s, T = s.traits || {};
  // ranged attackers fire a projectile; melee hits now
  const reach = s.range;
  const tgt = (e.target && e.target.alive && canHit(e, e.target)) ? e.target : findTarget(B, e, reach + 8);
  const castle = castleOf(B, e.side);
  const castleGap = (castle.front - e.x) * e.side;
  if (T.heal) {   // healer: heal the most injured allies in range
    const n = T.healTargets || 1;
    for (let k = 0; k < n; k++) {
      let best = null, bf = 0.999;
      for (const o of B.ents) {
        if (!o.alive || o.side !== e.side || o === e) continue;
        if (Math.abs(o.x - e.x) > reach) continue;
        const f = o.hp / o.maxHp; if (f < bf && !o._healed) { bf = f; best = o; }
      }
      if (best) { best._healed = true; heal(B, best, T.heal); ev(B, "healBeam", { from: e, to: best }); }
    }
    for (const o of B.ents) o._healed = false;
    return;
  }
  if (T.projectile) {
    const tx = tgt ? tgt.x : castle.front;
    e.shots++;
    const grape = T.grape && e.shots % T.grape === 0;
    B.projs.push({ kind: T.projectile, x: e.x + 18 * e.side, y: B.F.groundY - 50, tx, target: tgt, side: e.side,
      dmg: s.dmg, t: 0, dur: (T.projSpeed ? 0.15 : 0.35) + Math.abs(tx - e.x) / (T.projSpeed || 700), sx: e.x + 18 * e.side, alive: true, lob: !!T.lob,
      burn: T.burn, pierce: T.pierce || 0, toCastle: !tgt, splash: T.lob ? (T.lobSplash || 30) : grape ? 40 : 0, px: 0, py: 0,
      net: T.net || null, pierceArmor: !!T.pierceArmor, air: tgt ? airborne(tgt) : false, tar: T.tar || null, barb: T.barb || 0 });
    ev(B, "shoot", { e, kind: T.projectile });
    return;
  }
  let dmg = s.dmg;
  if (T.firstStrike && !e.firstDone) { dmg *= T.firstStrike; e.firstDone = true; }
  if (T.assassin && tgt && PRIORITY(tgt) >= 2) dmg *= T.assassin;      // the Rope Rat knifes the back line: siege and menders
  if (tgt) {
    const big = tgt.s.large ? (T.bonusVsLarge || 1) : 1;
    if (T.splash) {
      const cx = tgt.x;
      explode(B, cx, T.splash, dmg * big, e, e.side === 1 ? "enemies" : "players", { melee: true, kb: T.knockback || 0, kind: "blunt", blunt: !!T.blunt });
      if (T.quake) for (const o of B.ents) if (o.alive && o.side !== e.side && Math.abs(o.x - cx) <= T.splash && o.kind !== "boss") stunIt(o, T.quake);
      if (T.embers) B.patches.push({ x: cx, r: 40, dps: 10, t: 3, side: e.side });
      ev(B, "slam", { x: cx, r: T.splash, side: e.side });
    } else {
      const behind = (e.x - tgt.x) * tgt.side < 0;
      e.hits = (e.hits || 0) + 1;
      damage(B, tgt, dmg * big, e, { melee: true, behind, kb: (T.knockback || 0) + (T.shove && e.hits % 3 === 0 ? T.shove : 0), kind: e.side === 1 ? "blade" : "claw", crit: dmg > s.dmg });
      if (T.venomBlade && tgt.alive) { tgt.burn = Math.max(tgt.burn, T.venomBlade); tgt.burnT = 3; }
    }
  } else if (castleGap <= reach + 4) {
    hitCastle(B, e.side, dmg);
  }
}

/** Stun with a short immunity after, so nets and slams cannot chain-lock a monster. */
function stunIt(o, t) { if (o.stunImm > 0) return; o.stun = Math.max(o.stun, t); o.stunImm = t + 3; }

/** Rope Rat: on first contact, vault the front line and land behind the best target further back. */
function tryVault(B, e, front) {
  const V = e.s.traits.vault; e.vaulted = true;
  let dest = null, bs = -1e9;
  for (const o of B.ents) {
    if (!o.alive || o.side === e.side || o === front || airborne(o) || o.kind === "boss") continue;
    const d = (o.x - e.x) * e.side; if (d <= 0 || d > V.reach) continue;
    const sc = PRIORITY(o) * 1000 + (o.s.traits.shell ? 600 : 0) + d;
    if (sc > bs) { bs = sc; dest = o; }
  }
  if (!dest) return false;
  const to = dest.x + e.side * (dest.s.size * 0.5 + e.s.size * 0.5 + 4);
  e.leap = { from: e.x, to: Math.min(B.gate.front + 10, to), t: 0, dur: 0.45 }; e.lock = dest; e.state = "walk"; e.stateT = 0;
  ev(B, "vault", { e });
  return true;
}

function bossThink(B, e, dt) {
  const b = e.s.boss, T = e.bossT;
  if (!e.phase2 && e.hp < e.maxHp * b.phase2.below) { e.phase2 = true; ev(B, "bossPhase", { e }); }
  const cm = e.phase2 ? b.phase2.cooldownMul : 1;
  if (e.windup) {
    e.windup.t -= dt;
    if (e.windup.t <= 0) {
      const w = e.windup; e.windup = null; e.state = w.kind; e.stateT = 0; e.hitAt = 0.25;
      if (w.kind === "sweep") {
        const cx = e.x - b.sweep.radius * 0.5;
        explode(B, cx, b.sweep.radius * 0.6, b.sweep.dmg, e, "players", { kb: b.sweep.knockback, kind: "blunt" });
        if (Math.abs(B.keep.front - e.x) < b.sweep.radius) hitCastle(B, -1, b.sweep.dmg);
        ev(B, "bossSlam", { x: cx, r: b.sweep.radius });
        e.vuln = 3; ev(B, "bossWinded", { e });          // the swing leaves her open: a window to punish
        if (e.phase2) B.patches.push({ x: cx, r: 60, dps: 14, t: 4, side: -1 });
      } else if (w.kind === "summon") {
        const ids = b.summon.ids || [b.summon.id]; e.summons = (e.summons || 0) + 1;
        const sid = ids[(e.summons - 1) % ids.length], n = sid === b.summon.id ? b.summon.n : Math.max(2, b.summon.n - 1);
        for (let k = 0; k < n; k++) spawn(B, powered(B, enemyStats(B.enemyDefs[sid], false, B.content.enemies.elite), B.emul), -1, e.x - 30 - k * 12);
        ev(B, "bossSummon", { x: e.x });
      } else if (w.kind === "spit") {
        B.scheduled.push({ at: B.t + 0.01, kind: "bossSpit", x: w.x, dmg: b.spit.dmg, splash: b.spit.radius });
      }
    }
    return true;
  }
  T.sweep -= dt; T.summon -= dt; T.spit -= dt;
  // choose an attack: sweep if anyone is close, else summon / spit on timers
  const near = findTarget(B, e, b.sweep.radius * 0.8);
  const keepNear = (e.x - B.keep.front) < b.sweep.radius * 0.8;
  if (T.sweep <= 0 && (near || keepNear)) {
    T.sweep = b.sweep.every * cm; e.windup = { kind: "sweep", t: b.sweep.windup * (e.phase2 ? 0.85 : 1) };
    e.state = "windup"; e.stateT = 0;
    ev(B, "bossWarn", { kind: "sweep", x: e.x - b.sweep.radius * 0.5, r: b.sweep.radius, t: e.windup.t, e });
    return true;
  }
  if (T.summon <= 0) {
    T.summon = b.summon.every * cm; e.windup = { kind: "summon", t: b.summon.windup };
    e.state = "windup"; e.stateT = 0; ev(B, "bossWarn", { kind: "summon", x: e.x, t: b.summon.windup, e });
    return true;
  }
  if (T.spit <= 0) {
    // aim at the furthest-back warden (healers, archers), else the keep
    let tx = B.keep.front, best = -1;
    for (const o of B.ents) if (o.alive && o.side === 1) { const d = e.x - o.x; if (d > best && d < 900) { best = d; tx = o.x; } }
    T.spit = b.spit.every * cm; e.windup = { kind: "spit", t: 0.6, x: tx };
    e.state = "windup"; e.stateT = 0;
    B.marks.push({ x: tx, r: b.spit.radius, t: b.spit.warn + 0.6, max: b.spit.warn + 0.6 });
    ev(B, "bossWarn", { kind: "spit", x: tx, t: b.spit.warn, e });
    B.scheduled.push({ at: B.t + b.spit.warn + 0.6, kind: "bossSpit", x: tx, dmg: b.spit.dmg, splash: b.spit.radius });
    e.windup.kind = "spitDone";
    return true;
  }
  return false;
}

function stepEntity(B, e, dt) {
  e.px = e.x;
  e.stateT += dt;
  if (e.flash > 0) e.flash -= dt;
  if (!e.alive) {
    e.dieT += dt;
    if (e.dieT > (e.side === -1 ? 4.2 : 3.0)) e.gone = true;      // bodies lie on the beach for a moment
    return;
  }
  if (e.slowT > 0) e.slowT -= dt;
  if (e.vuln > 0) e.vuln -= dt;
  if (e.crackT > 0) e.crackT -= dt;
  if (e.hasteT > 0) e.hasteT -= dt;
  if (e.stunImm > 0) e.stunImm -= dt;
  if (e.netT > 0) { e.netT -= dt; if (e.netT <= 0) ev(B, "netFree", { e }); }
  if (e.leap) {             // mid-vault: fly over the line, nothing else happens
    const L = e.leap; L.t += dt; const k = Math.min(1, L.t / L.dur);
    e.x = L.from + (L.to - L.from) * k; e.leapK = Math.sin(k * Math.PI);
    if (k >= 1) { e.leap = null; e.leapK = 0; e.atkCd = 0; ev(B, "land", { e }); }
    return;
  }
  if (e.burnT > 0) { e.burnT -= dt; damage(B, e, e.burn * dt, null, { kind: "burn" }); if (!e.alive) return; }
  if (e.kb !== 0) {         // knockback slide
    const step = Math.sign(e.kb) * Math.min(Math.abs(e.kb), 260 * dt);
    e.x += step; e.kb -= step; if (Math.abs(e.kb) < 0.5) e.kb = 0;
    clampX(B, e); return;
  }
  if (e.stun > 0) { e.stun -= dt; return; }
  if (e.state === "hit" && e.stateT < 0.25) return;
  const s = e.s, T = s.traits || {};
  if (T.enrage && !e.enraged && e.hp < e.maxHp * T.enrage.below) { e.enraged = true; ev(B, "enrage", { e }); }
  // auras
  if (T.slowAura) {
    for (const o of B.ents) if (o.alive && o.side !== e.side && Math.abs(o.x - e.x) <= T.slowAura.radius) { o.slow = T.slowAura.slow; o.slowT = 0.25; }
    if (T.rateAura) for (const o of B.ents) if (o.alive && o.side === e.side && Math.abs(o.x - e.x) <= T.slowAura.radius) { o.haste = T.rateAura; o.hasteT = 0.25; }
  }
  // hero flare
  if (e.kind === "hero") {
    e.flareT -= dt;
    if (e.flareT <= 0 && findTarget(B, e, 120)) {
      const f = s.traits.flare; e.flareT = f.every;
      for (const o of B.ents) if (o.alive && o.side === -1 && Math.abs(o.x - e.x) <= f.radius) {
        damage(B, o, f.dmg, e, { kind: "fire" }); if (o.alive && o.kind !== "boss") o.stun = f.stun;
      }
      e.state = "special"; e.stateT = 0; ev(B, "flare", { e, r: f.radius }); return;
    }
    if (e.state === "special" && e.stateT < 0.6) return;
  }
  if (e.kind === "boss" && bossThink(B, e, dt)) return;
  if (e.state === "windup") return;
  // attacking: wait for the hit moment, then strike
  e.atkCd -= dt;
  if (e.state === "attack" || e.state === "sweep" || e.state === "summon" || e.state === "spit") {
    if (e.hitAt >= 0 && e.stateT >= e.hitAt) { e.hitAt = -1; if (e.state === "attack") strike(B, e); }
    if (e.stateT < Math.min(0.7, s.rate * 0.8)) return;
    e.state = "walk"; e.stateT = 0;
  }
  const reach = s.range;
  if (e.lock && (!e.lock.alive || Math.abs(e.lock.x - e.x) - (e.s.size + e.lock.s.size) * 0.5 > reach + 30)) e.lock = null;
  let tgt = T.heal ? null : (e.lock || findTarget(B, e, reach));
  if (tgt && T.vault && !e.vaulted && !e.lock && tryVault(B, e, tgt)) return;
  const castle = castleOf(B, e.side);
  const castleGap = (castle.front - e.x) * e.side;
  let wantsAttack = !!tgt || (castleGap <= reach && !T.heal);
  if (T.heal) {  // healers stop behind the front line when someone needs healing, else follow
    let need = false, front = -1e9;
    for (const o of B.ents) if (o.alive && o.side === e.side && o !== e) {
      if (Math.abs(o.x - e.x) <= reach && o.hp < o.maxHp * 0.98) need = true;
      front = Math.max(front, o.x * e.side);
    }
    const ahead = (front - e.x * e.side);
    if (need && e.atkCd <= 0) wantsAttack = true;
    else if (ahead < 70 || findTarget(B, e, 120)) { e.state = "idle"; return; }
  }
  if (T.siege && !e.lock) {   // siege keeps its distance: it backs toward its own fort when crew come close (only a leap or a long shot reaches it)
    let near = false;
    for (const o of B.ents) if (o.alive && o.side !== e.side && !airborne(o) && (o.x - e.x) * e.side > -e.s.size && (o.x - e.x) * e.side < T.siege.keep) { near = true; break; }
    const home = castleOf(B, -e.side);
    if (near && (e.x - home.front) * -e.side < T.siege.hide - 2) { e.state = "walk"; e.target = null; e.x -= e.side * s.speed * speedMul(B, e) * dt * (B.g.speedScale || 1); clampX(B, e); return; }
  }
  if (T.slowAura && !tgt) {   // the singer keeps a step behind the front so the song covers the line, not the singer
    let front = -1e9; for (const o of B.ents) if (o.alive && o.side === e.side && o !== e && !o.s.traits.slowAura && !o.s.traits.heal) front = Math.max(front, o.x * e.side);
    if (front > -1e9 && front - e.x * e.side < 60) { e.state = "idle"; return; }
  }
  if (wantsAttack) {
    e.target = tgt;
    if (e.atkCd <= 0) {
      e.atkCd = s.rate * rateMul(B, e); e.state = "attack"; e.stateT = 0;
      e.hitAt = Math.min(0.32, s.rate * 0.35);
      ev(B, "attack", { e });
    } else if (e.state !== "attack") e.state = "idle";
    return;
  }
  e.target = null;
  e.state = "walk";
  e.x += e.side * s.speed * speedMul(B, e) * dt * (B.g.speedScale || 1);
  clampX(B, e);
}

function clampX(B, e) {
  const sg = e.s.traits && e.s.traits.siege;
  const lo = B.keep.front - 20, hi = B.gate.front + (sg && e.side === -1 ? sg.hide : 20);     // siege can back into the Grotto's mouth
  if (e.x < lo) e.x = lo; if (e.x > hi) e.x = hi;
}

function stepProjectiles(B, dt) {
  const G = B.g.ballista.gravity, ground = B.F.groundY;
  for (const p of B.projs) {
    if (!p.alive) continue;
    p.t += dt; p.px = p.x; p.py = p.y;
    if (p.kind === "bolt") {
      p.vy += G * dt; p.x += p.vx * dt; p.y += p.vy * dt;
      let hit = p.y >= ground - 4, direct = null;
      if (!hit) for (const o of B.ents) {
        if (!o.alive || o.side !== -1) continue;
        if (airborne(o)) { const fy = ground - (o.s.traits.flyH || 90); if (Math.abs(o.x - p.x) < o.s.size + 10 && Math.abs(p.y - fy) < 40) { hit = true; direct = o; break; } continue; }
        const h = Math.min(260, o.s.size * (o.kind === "boss" ? 5 : 5.4));
        if (Math.abs(o.x - p.x) < o.s.size * 0.7 + 6 && p.y > ground - h) { hit = true; direct = o; break; }
      }
      if (!hit && p.x > B.gate.front - 10 && p.y > ground - 260) {
        hit = true; hitCastle(B, 1, p.dmg * 0.5);
      }
      if (hit || p.x > B.F.width + 50 || p.t > 6) {
        p.alive = false;
        if (hit) {
          const before = B.stats.kills; let hits = 0;
          for (const o of B.ents) if (o.alive && o.side === -1 && Math.abs(o.x - p.x) <= p.splash + o.s.size * 0.5) hits++;
          // a ball that strikes a body (not the sand) hits that monster half again as hard
          const bl = B.g.ballista;
          if (direct && direct.alive && airborne(direct)) damage(B, direct, p.dmg * (1 + (bl.directBonus || 0)), { side: 1 }, { kind: "fire", blast: true });
          else if (direct && direct.alive && direct.kind !== "boss") damage(B, direct, p.dmg * (bl.directBonus || 0), { side: 1 }, { kind: "fire" });
          explode(B, p.x, p.splash, p.dmg, { side: 1 }, "enemies", { kb: bl.knockback || 18, kind: "fire", blast: true });
          if (hits) B.stats.shotHits++;
          // salvage: every monster the cannon kills pays powder back, so a shot into a pack buys the next deckhand
          const got = (B.stats.kills - before) * (bl.salvage || 0);
          if (got > 0) { B.energy = Math.min(B.energyMax, B.energy + got); B.stats.salvage = (B.stats.salvage || 0) + got; ev(B, "salvage", { x: p.x, amt: got }); }
          if (direct && direct.kind !== "boss") ev(B, "directHit", { x: p.x, y: p.y });
          const fp = B.g.ballista.firePatch;
          B.patches.push({ x: p.x, r: fp.radius, dps: fp.dps, t: fp.time, side: 1 });
          ev(B, "boltHit", { x: p.x, y: Math.min(p.y, ground), hits, kills: B.stats.kills - before });
        }
      }
      continue;
    }
    // unit projectiles: travel from sx to tx over dur (arc drawn by the renderer)
    if (p.target && p.target.alive) p.tx = p.target.x;
    const k = Math.min(1, p.t / p.dur);
    p.x = p.sx + (p.tx - p.sx) * k;
    const arc = p.lob ? 160 : 40;
    p.y = B.F.groundY - 50 - Math.sin(k * Math.PI) * arc * Math.min(1, Math.abs(p.tx - p.sx) / 300) + k * 20;
    if (k >= 1) {
      p.alive = false;
      if (p.toCastle) { hitCastle(B, p.side, p.dmg); continue; }
      let tgt = p.target && p.target.alive ? p.target : null;
      if (!tgt) for (const o of B.ents) if (o.alive && o.side !== p.side && Math.abs(o.x - p.x) < 24) { tgt = o; break; }
      // a Bellback's bell shields whatever walks behind it: a straight shot past it hits the bell instead
      if (tgt && !p.lob && !p.net && !airborne(tgt)) for (const o of B.ents) {
        if (!o.alive || o === tgt || o.side === p.side || !(o.shell > 0)) continue;
        if ((o.x - p.sx) * p.side > 0 && (tgt.x - o.x) * p.side > 0) { tgt = o; p.x = o.x; break; }
      }
      const po = { kind: p.kind, pierceArmor: p.pierceArmor, air: p.air, lob: p.lob };
      if (p.net) {             // a net: everything under it is pinned and slowed; fliers are dragged down to the sand
        const N = p.net;
        for (const o of B.ents) if (o.alive && o.side !== p.side && o.kind !== "boss" && Math.abs(o.x - p.x) <= N.radius + o.s.size * 0.5) {
          const wasAir = airborne(o);
          o.netT = N.time; o.netSlow = N.slow; o.netHook = N.hook || 0;
          if (wasAir && N.stun) stunIt(o, N.stun);
          if (p.dmg > 0) damage(B, o, p.dmg, { side: p.side }, { kind: "net" });
          ev(B, "netted", { e: o, air: wasAir });
          if (N.targets === 1) break;
        }
      } else if (p.splash) explode(B, p.x, p.splash, p.dmg, { side: p.side }, p.side === 1 ? "enemies" : "players", po);
      else if (tgt) {
        const dealt = damage(B, tgt, p.dmg, { side: p.side }, po);
        if (p.burn && tgt.alive && dealt > 0) { tgt.burn = p.burn.dps; tgt.burnT = p.burn.time; }     // a shot the bell soaks sets nothing alight
        if (p.barb && tgt.alive) { tgt.slow = Math.max(tgt.slowT > 0 ? tgt.slow : 0, 0.4); tgt.slowT = p.barb; }
        if (p.tar) B.patches.push({ x: tgt.x, r: 26, dps: p.tar, t: 2.5, side: p.side });
        if (p.pierce) { let left = p.pierce; for (const o of B.ents) if (left > 0 && o.alive && o !== tgt && o.side !== p.side && (o.x - tgt.x) * p.side > 0 && (o.x - tgt.x) * p.side < 90) { damage(B, o, p.dmg * 0.6, { side: p.side }, po); left--; } }
      }
      ev(B, "projHit", { kind: p.kind, x: p.x, y: B.F.groundY - 30 });
    }
  }
  if (B.projs.length > 64) B.projs = B.projs.filter((p) => p.alive);
}

function stepWaves(B, dt) {
  if (B.waveHold) { B.heldT += dt; return; }      // tutorial pauses don't count against the par time
  B.waveClock += dt;
  const T = B.waveClock;
  const eliteCfg = B.content.enemies.elite;
  const spawnEnemy = (id, elite) => {
    const d = B.enemyDefs[id]; if (!d) return;
    spawn(B, powered(B, enemyStats(d, elite, eliteCfg), B.emul), -1, B.gate.front - 10);
  };
  for (const w of B.waves) {
    while (w.done < w.n && T >= w.next) { spawnEnemy(w.id, w.elite); w.done++; w.next += w.gap; }
  }
  for (const tr of B.triggers) {
    if (!tr.fired && B.gate.hp < B.gate.max * tr.below) {
      tr.fired = true; ev(B, "rush", {});
      for (const w of tr.waves) B.waves.push({ ...w, done: 0, next: T + w.t });
    }
  }
  if (B.loop && T >= B.loop.start) {
    B.loop.timer -= dt;
    if (B.loop.timer <= 0) {
      const minutes = (T - B.loop.start) / 60;
      B.loop.timer = Math.max(B.loop.min, B.loop.every * (1 - B.loop.ramp * minutes * 4));
      // the Maw grows angry after par time: faster spawns and more elites, so no battle stalls forever
      const over = Math.max(0, B.t - (B.stage.par || 180));
      if (over > 0) B.loop.timer = Math.max(0.9, B.loop.timer * Math.max(0.3, 1 - over / 200));
      if (over > 0 && !B.angry) { B.angry = true; ev(B, "angry", {}); }
      const pool = B.loop.pool; let tot = 0; for (const [, w] of pool) tot += w;
      let r = B.rand() * tot, pick = pool[0][0];
      for (const [id, w] of pool) { r -= w; if (r <= 0) { pick = id; break; } }
      const n = (B.enemyDefs[pick].traits || {}).pack || 1;
      const over2 = Math.max(0, B.t - (B.stage.par || 180));
      for (let k = 0; k < n; k++) spawnEnemy(pick, B.rand() < (B.loop.eliteChance || 0) + over2 / 240);
    }
  }
  if (B.stage.boss && !B.bossSpawned && T >= B.stage.bossAt) {
    B.bossSpawned = true;
    B.boss = spawn(B, powered(B, enemyStats(B.enemyDefs[B.stage.boss], false, eliteCfg), B.bmul), -1, B.gate.front - 20);
    ev(B, "bossSpawn", { e: B.boss });
  }
}

export function step(B) {
  const dt = B.dt;
  applyInputs(B);
  if (B.result) { B.t += dt; for (const e of B.ents) stepEntity(B, e, dt); B.tick++; return; }
  B.t += dt; B.tick++;
  B.energy = Math.min(B.energyMax, B.energy + B.regen * dt);
  for (const c of B.cards) if (c.cd > 0) c.cd -= dt;
  for (const a of B.abilities) if (a.cd > 0) a.cd -= dt;
  if (B.ballista.reload > 0) { B.ballista.reload -= dt; if (B.ballista.reload <= 0) ev(B, "reloaded", {}); }
  if (B.rally > 0) B.rally -= dt;
  if (B.keep.hitT > 0) B.keep.hitT -= dt; if (B.gate.hitT > 0) B.gate.hitT -= dt;
  const h = B.hero;
  if (h && !h.called) { const was = h.charge >= h.need; h.charge = Math.min(h.need, h.charge + dt); if (!was && h.charge >= h.need) ev(B, "heroReady", {}); }
  stepWaves(B, dt);
  for (const e of B.ents) e._atk = 0;          // how many monsters are on each crew member (swarms slip round a surrounded one)
  for (const e of B.ents) if (e.alive && e.target && e.target.alive) e.target._atk++;
  for (let i = 0; i < B.ents.length; i++) stepEntity(B, B.ents[i], dt);
  stepProjectiles(B, dt);
  // fire patches
  for (const p of B.patches) {
    if (p.t <= 0) continue; p.t -= dt;
    for (const o of B.ents) if (o.alive && o.side !== p.side && Math.abs(o.x - p.x) <= p.r) damage(B, o, p.dps * dt, null, { kind: "burn" });
  }
  if (B.patches.length > 24) B.patches = B.patches.filter((p) => p.t > 0);
  for (const m of B.marks) m.t -= dt;
  if (B.marks.length > 8) B.marks = B.marks.filter((m) => m.t > 0);
  // scheduled impacts (ember rain stones, boss spit)
  for (const s of B.scheduled) {
    if (s.done || B.t < s.at) continue;
    s.done = true;
    if (s.kind === "stone") { explode(B, s.x, s.splash, s.dmg, { side: 1 }, "enemies", { kind: "fire" }); ev(B, "stone", { x: s.x }); }
    else if (s.kind === "bossSpit") {
      explode(B, s.x, s.splash, s.dmg, null, "players", { kind: "fire" });
      if (Math.abs(s.x - B.keep.front) < s.splash + 30) hitCastle(B, -1, s.dmg);
      ev(B, "bossSpitHit", { x: s.x, r: s.splash });
      B.patches.push({ x: s.x, r: s.splash * 0.7, dps: 10, t: 3, side: -1 });
    }
  }
  if (B.scheduled.length > 40) B.scheduled = B.scheduled.filter((s) => !s.done);
}

/** Launch velocity for the ballista so a bolt fired at `angleDeg` lands at world x (aim preview + test player). */
export function solveShot(B, targetX, angleDeg = 35) {
  const G = B.g.ballista.gravity, x0 = B.ballista.x + 30, y0 = B.ballista.y - 4;
  const dx = Math.max(40, targetX - x0), dy = B.F.groundY - 20 - y0, u = Math.tan(angleDeg * Math.PI / 180);
  const v = Math.sqrt(G * dx * dx * (1 + u * u) / (2 * (dy + dx * u)));
  const a = angleDeg * Math.PI / 180;
  return { vx: Math.cos(a) * v, vy: -Math.sin(a) * v, speed: v };
}

export function stars(B) {
  if (B.result !== "win") return 0;
  let s = 1;
  if (B.keep.hp >= B.keep.max * B.g.stars.keepHp) s++;
  if (B.endT - B.heldT <= B.stage.par) s++;
  return s;
}
