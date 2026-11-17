// Pure stat resolution: data + player progress -> numbers used by the battle. No DOM.

export function rng(seed) {
  let a = seed >>> 0 || 1;
  return function () {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function tierFor(level, tierLevels = [5, 10]) {
  return level >= tierLevels[1] ? 3 : level >= tierLevels[0] ? 2 : 1;
}

/** Player unit stats at a level, including tier perks. */
export function unitStats(def, level, levels) {
  const L = Math.max(1, level | 0);
  const tier = tierFor(L, levels.tierLevels);
  const s = {
    id: def.id, kind: "unit", hp: def.hp * (1 + levels.hpPerLevel * (L - 1)),
    dmg: def.dmg * (1 + levels.dmgPerLevel * (L - 1)), rate: def.rate, range: def.range, speed: def.speed,
    size: def.size, cost: def.cost, cooldown: def.cooldown, level: L, tier, traits: JSON.parse(JSON.stringify(def.traits || {})),
    sprite: tier > 1 ? `${def.id}_t${tier}` : def.id, baseSprite: def.id,
  };
  const t = s.traits;
  // Tier perks (visible change at level 5 and 10). Kept here so data stays simple to read.
  switch (def.id) {
    case "ashguard": t.meleeGuard = tier === 3 ? 0.45 : tier === 2 ? 0.35 : 0.25; if (tier === 3) s.dmg *= 1.15; break;
    case "torchbow": if (tier >= 2) t.burn.time += 1; if (tier === 3) t.pierce = 1; break;
    case "cinder_runner": if (tier >= 2) s.hp *= 1.2; if (tier === 3) t.firstStrike = 3; break;
    case "bellringer": t.slowAura.slow = tier === 3 ? 0.4 : tier === 2 ? 0.35 : 0.3; if (tier === 3) t.slowAura.radius = 210; break;
    case "maulwright": if (tier >= 2) s.hp *= 1.2; if (tier === 3) { t.splash = 75; t.embers = true; } break;
    case "lamplighter": t.healTargets = tier >= 2 ? 2 : 1; if (tier === 3) t.heal *= 1.5; break;
  }
  if (t.heal && def.id === "lamplighter") t.heal *= 1 + 0.08 * (L - 1);
  return s;
}

export function enemyStats(def, elite, eliteCfg) {
  const m = elite ? eliteCfg : { hpMul: 1, dmgMul: 1, speedMul: 1 };
  return {
    id: def.id, kind: def.boss ? "boss" : "enemy", hp: def.hp * m.hpMul, dmg: def.dmg * m.dmgMul, rate: def.rate,
    range: def.range, speed: def.speed * m.speedMul, size: def.size, traits: def.traits || {}, elite: !!elite,
    large: !!def.large, boss: def.boss || null, miniboss: !!def.miniboss, sprite: def.id,
  };
}

export function heroStats(h, level) {
  const L = Math.max(1, level | 0);
  return {
    id: h.id, kind: "hero", hp: h.hp * (1 + h.hpPerLevel * (L - 1)), dmg: h.dmg * (1 + h.dmgPerLevel * (L - 1)),
    rate: h.rate, range: h.range, speed: h.speed, size: h.size, traits: { splash: h.splash, flare: h.flare },
    sprite: h.id, level: L,
  };
}

export function upgradeCost(kind, level, game) {
  const [base, mul] = game.upgradeCost[kind];
  return Math.round(base * Math.pow(mul, level - 1) / 5) * 5;
}
