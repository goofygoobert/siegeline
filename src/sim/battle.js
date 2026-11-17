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
    const s = unitStats(unitDefs[id], (progress?.unitLevels || {})[id] || 1, content.units.levels);
    return { id, stats: s, cd: 0 };
  });
  const keepMax = g.keep.hp + g.keep.hpPerLevel * (lv("keep") - 1);
  const B = {
    t: 0, dt: DT_DEFAULT, tick: 0, rand: rng(seed), stage, content, F, g,
    energy: g.energy.start, energyMax: g.energy.max + g.energy.maxPerLevel * (lv("energyMax") - 1),
    regen: g.energy.regen + g.energy.regenPerLevel * (lv("energyRegen") - 1),
    keep: { hp: keepMax, max: keepMax, x: F.playerCastleX, front: F.playerCastleX + 70, hitT: 0 },
    gate: { hp: stage.enemyCastleHp, max: stage.enemyCastleHp, x: F.enemyCastleX, front: F.enemyCastleX - 80, hitT: 0,
            sealed: stage.winOn === "boss" },
    cards, unitDefs, enemyDefs,
    ents: [], nextId: 1, projs: [], patches: [], marks: [], scheduled: [],
    ballista: { reload: 0, maxReload: Math.max(1.2, g.ballista.reload - g.ballista.reloadPerLevel * (lv("ballista") - 1)),
                dmg: g.ballista.dmg * (1 + g.ballista.dmgPerLevel * (lv("ballista") - 1)), x: F.playerCastleX + 10, y: F.groundY - 230 },
    abilities: (stage.abilities || []).map((id) => ({ id, cfg: g.abilities[id], level: (progress?.abilities || {})[id] || 1, cd: 6 })),
    hero: stage.hero ? { charge: 0, need: g.hero.charge, called: false, ent: null, level: lv("hero") } : null,
    rally: 0, waveHold: false, waveClock: 0, waves: (stage.waves || []).map((w) => ({ ...w, done: 0, next: w.t })),
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
      B.projs.push({ kind: "bolt", x: B.ballista.x + 40, y: B.ballista.y, vx: i.vx, vy: i.vy, side: 1, dmg: B.ballista.dmg,
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
function powered(B, s, m) { if (m !== 1) { s.hp *= m; s.dmg *= Math.pow(m, 0.75); } return s; }

function spawn(B, s, side, x) {
  let e = null;
  for (const o of B.ents) if (!o.alive && o.gone) { e = o; break; }   // reuse dead slots (no per-spawn garbage)
  if (!e) { e = {}; B.ents.push(e); }
  e.uid = B.nextId++; e.s = s; e.id = s.id; e.kind = s.kind; e.side = side; e.sprite = s.sprite;
  e.x = x; e.px = x; e.lane = (B.rand() - 0.5) * 2 * B.F.laneJitter; e.hp = s.hp; e.maxHp = s.hp;
  e.alive = true; e.gone = false; e.state = "walk"; e.stateT = 0; e.atkCd = 0.2 + B.rand() * 0.3; e.hitAt = -1;
  e.target = null; e.slow = 0; e.slowT = 0; e.stun = 0; e.burn = 0; e.burnT = 0; e.kb = 0; e.dieT = 0;
  e.flash = 0; e.firstDone = false; e.healCd = 0; e.elite = !!s.elite; e.flareT = 0;
  e.bossT = null; e.windup = null; e.enraged = false;
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
  let d = amt;
  if (e.s.traits && e.s.traits.meleeGuard && opts && opts.melee) d *= 1 - e.s.traits.meleeGuard;
  if (e.s.traits && e.s.traits.armor) d *= 1 - e.s.traits.armor;
  e.hp -= d; e.flash = 0.12;
  if (src && src.side === 1) B.stats.dmgDealt += d;
  ev(B, "dmg", { e, amt: d, crit: opts && opts.crit, kind: opts && opts.kind });
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
    explode(B, e.x, db.radius, db.dmg, null, "both");
    ev(B, "burst", { x: e.x, r: db.radius });
  }
  if (e.kind === "boss") { ev(B, "bossDead", { e }); if (B.stage.winOn === "boss") end(B, "win"); }
}

function explode(B, x, r, dmg, src, who, opts) {
  for (const o of B.ents) {
    if (!o.alive) continue;
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

/** Nearest living opponent in front of e (in its walking direction) within reach, else null. */
function findTarget(B, e, reach) {
  let best = null, bd = 1e9;
  for (const o of B.ents) {
    if (!o.alive || o.side === e.side) continue;
    const d = (o.x - e.x) * e.side;            // distance ahead
    if (d < -(e.s.size + o.s.size) * 0.5) continue;  // behind
    const gap = Math.abs(d) - (e.s.size + o.s.size) * 0.5;
    if (gap <= reach && gap < bd) { bd = gap; best = o; }
  }
  return best;
}

function speedMul(B, e) {
  let m = 1;
  if (e.slowT > 0) m *= 1 - e.slow;
  if (e.side === 1 && B.rally > 0) m *= B.g.abilities.rally.speedMul;
  if (e.enraged) m *= e.s.traits.enrage.speed;
  if (e.kind === "boss" && e.phase2) m *= e.s.boss.phase2.speedMul;
  return m;
}

function rateMul(B, e) {
  let m = 1;
  if (e.slowT > 0) m /= 1 - e.slow * 0.5;
  if (e.side === 1 && B.rally > 0) m *= B.g.abilities.rally.rateMul;
  if (e.enraged) m *= e.s.traits.enrage.rate;
  return m;
}

function strike(B, e) {
  const s = e.s, T = s.traits || {};
  // ranged attackers fire a projectile; melee hits now
  const reach = s.range;
  const tgt = (e.target && e.target.alive) ? e.target : findTarget(B, e, reach + 8);
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
    B.projs.push({ kind: T.projectile, x: e.x + 18 * e.side, y: B.F.groundY - 50, tx, target: tgt, side: e.side,
      dmg: s.dmg, t: 0, dur: 0.35 + Math.abs(tx - e.x) / 700, sx: e.x + 18 * e.side, alive: true, lob: !!T.lob,
      burn: T.burn, pierce: T.pierce || 0, toCastle: !tgt, splash: T.lob ? 30 : 0, px: 0, py: 0 });
    ev(B, "shoot", { e, kind: T.projectile });
    return;
  }
  let dmg = s.dmg;
  if (T.firstStrike && !e.firstDone) { dmg *= T.firstStrike; e.firstDone = true; }
  if (tgt) {
    const big = tgt.s.large ? (T.bonusVsLarge || 1) : 1;
    if (T.splash) {
      const cx = tgt.x;
      explode(B, cx, T.splash, dmg * big, e, e.side === 1 ? "enemies" : "players", { melee: true, kb: T.knockback || 0, kind: "blunt" });
      ev(B, "slam", { x: cx, r: T.splash, side: e.side });
    } else damage(B, tgt, dmg * big, e, { melee: true, kb: T.knockback || 0, kind: e.side === 1 ? "blade" : "claw", crit: dmg > s.dmg });
  } else if (castleGap <= reach + 4) {
    hitCastle(B, e.side, dmg);
  }
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
        if (e.phase2) B.patches.push({ x: cx, r: 60, dps: 14, t: 4, side: -1 });
      } else if (w.kind === "summon") {
        for (let k = 0; k < b.summon.n; k++) spawn(B, powered(B, enemyStats(B.enemyDefs[b.summon.id], false, B.content.enemies.elite), B.emul), -1, e.x - 30 - k * 12);
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
    if (e.dieT > 1.6) e.gone = true;
    return;
  }
  if (e.slowT > 0) e.slowT -= dt;
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
  const tgt = T.heal ? null : findTarget(B, e, reach);
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
  const lo = B.keep.front - 20, hi = B.gate.front + 20;
  if (e.x < lo) e.x = lo; if (e.x > hi) e.x = hi;
}

function stepProjectiles(B, dt) {
  const G = B.g.ballista.gravity, ground = B.F.groundY;
  for (const p of B.projs) {
    if (!p.alive) continue;
    p.t += dt; p.px = p.x; p.py = p.y;
    if (p.kind === "bolt") {
      p.vy += G * dt; p.x += p.vx * dt; p.y += p.vy * dt;
      let hit = p.y >= ground - 4;
      if (!hit) for (const o of B.ents) {
        if (!o.alive || o.side !== -1) continue;
        const h = o.s.size * (o.kind === "boss" ? 5 : 4);
        if (Math.abs(o.x - p.x) < o.s.size * 0.7 + 6 && p.y > ground - h) { hit = true; break; }
      }
      if (!hit && p.x > B.gate.front - 10 && p.y > ground - 260) {
        hit = true; hitCastle(B, 1, p.dmg * 0.5);
      }
      if (hit || p.x > B.F.width + 50 || p.t > 6) {
        p.alive = false;
        if (hit) {
          const before = B.stats.kills; let hits = 0;
          for (const o of B.ents) if (o.alive && o.side === -1 && Math.abs(o.x - p.x) <= p.splash + o.s.size * 0.5) hits++;
          explode(B, p.x, p.splash, p.dmg, { side: 1 }, "enemies", { kb: 18, kind: "fire" });
          if (hits) B.stats.shotHits++;
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
      if (p.splash) explode(B, p.x, p.splash, p.dmg, { side: p.side }, p.side === 1 ? "enemies" : "players", { kind: p.kind });
      else if (tgt) {
        damage(B, tgt, p.dmg, { side: p.side }, { kind: p.kind });
        if (p.burn && tgt.alive) { tgt.burn = p.burn.dps; tgt.burnT = p.burn.time; }
        if (p.pierce) for (const o of B.ents) if (o.alive && o !== tgt && o.side !== p.side && (o.x - tgt.x) * p.side > 0 && (o.x - tgt.x) * p.side < 70) { damage(B, o, p.dmg * 0.6, { side: p.side }, { kind: p.kind }); break; }
      }
      ev(B, "projHit", { kind: p.kind, x: p.x, y: B.F.groundY - 30 });
    }
  }
  if (B.projs.length > 64) B.projs = B.projs.filter((p) => p.alive);
}

function stepWaves(B, dt) {
  if (B.waveHold) return;
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
      const n = pick === "gnawer" ? 2 : 1;
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
  const G = B.g.ballista.gravity, x0 = B.ballista.x + 40, y0 = B.ballista.y;
  const dx = Math.max(40, targetX - x0), dy = B.F.groundY - 20 - y0, u = Math.tan(angleDeg * Math.PI / 180);
  const v = Math.sqrt(G * dx * dx * (1 + u * u) / (2 * (dy + dx * u)));
  const a = angleDeg * Math.PI / 180;
  return { vx: Math.cos(a) * v, vy: -Math.sin(a) * v, speed: v };
}

export function stars(B) {
  if (B.result !== "win") return 0;
  let s = 1;
  if (B.keep.hp >= B.keep.max * B.g.stars.keepHp) s++;
  if (B.endT <= B.stage.par) s++;
  return s;
}
