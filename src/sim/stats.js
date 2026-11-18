// Pure stat resolution: data + player progress -> numbers used by the battle. No DOM.

/** The skills a crew member has at a level: the level-5 skill, plus the chosen level-10 one. */
export function skillsAt(def, level, choice) {
  const S = def.skills; if (!S) return [];
  const out = []; if (level >= 5 && S["5"]) out.push(S["5"]);
  if (level >= 10 && S["10"] && (choice === 0 || choice === 1)) out.push(S["10"][choice]);
  return out;
}
/** A skill sets or multiplies values: "set" keys are trait paths ("net.radius"), "mul" keys are stats or "traits.x". */
export function applySkill(s, sk) {
  const at = (root, path) => { const k = path.split("."); let o = root; for (let i = 0; i < k.length - 1; i++) o = o[k[i]] = o[k[i]] || {}; return [o, k[k.length - 1]]; };
  for (const [path, v] of Object.entries(sk.set || {})) { const [o, k] = at(s.traits, path); o[k] = v; }
  for (const [path, v] of Object.entries(sk.mul || {})) { const [o, k] = path.startsWith("traits.") ? at(s.traits, path.slice(7)) : [s, path]; o[k] = (o[k] || 0) * v; }
}

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
export function unitStats(def, level, levels, choice) {
  const L = Math.max(1, level | 0);
  const tier = tierFor(L, levels.tierLevels);
  const s = {
    id: def.id, kind: "unit", hp: def.hp * (1 + levels.hpPerLevel * (L - 1)),
    dmg: def.dmg * (1 + levels.dmgPerLevel * (L - 1)), rate: def.rate, range: def.range, speed: def.speed,
    size: def.size, cost: def.cost, cooldown: def.cooldown, level: L, tier, traits: JSON.parse(JSON.stringify(def.traits || {})),
    sprite: tier > 1 ? `${def.id}_t${tier}` : def.id, baseSprite: def.id,
  };
  const t = s.traits;
  if (t.heal && def.id === "lamplighter") t.heal *= 1 + 0.08 * (L - 1);
  // Skills: one learned at level 5, one of two chosen at level 10 (choice: 0 or 1; unchosen = none yet)
  for (const sk of skillsAt(def, L, choice)) applySkill(s, sk);
  return s;
}

export function enemyStats(def, elite, eliteCfg) {
  const m = elite ? eliteCfg : { hpMul: 1, dmgMul: 1, speedMul: 1 };
  return {
    id: def.id, kind: def.boss ? "boss" : "enemy", hp: def.hp * m.hpMul, dmg: def.dmg * m.dmgMul, rate: def.rate,
    range: def.range, speed: def.speed * m.speedMul, size: def.size, traits: def.traits || {}, elite: !!elite,
    large: !!def.large, boss: def.boss || null, miniboss: !!def.miniboss, sprite: def.id,
    bounty: (def.bounty || 0) * (elite ? (eliteCfg.bountyMul || 1.5) : 1),      // powder paid on death
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
