// Scripted test player. Uses only the public inputs a human has (send, fire, ability, hero).
import { input, canSend, solveShot } from "./battle.js";

// how many of each the bot likes on the beach: it knows roles, not which crew answers which monster
const WANT = { ashguard: 3, torchbow: 2, cinder_runner: 1.2, maulwright: 1, bellringer: 0.8, lamplighter: 0.8, harpooner: 1.2, netcaster: 1.2 };

export function makeBot(opts = {}) {
  const skill = opts.skill ?? 0.7;          // 0 = sloppy and slow, 1 = sharp
  let nextThink = 0;
  return function think(B) {
    if (B.result || B.t < nextThink) return;
    nextThink = B.t + (0.9 - 0.6 * skill) * (0.7 + B.rand() * 0.6);
    const enemies = B.ents.filter((e) => e.alive && e.side === -1);
    const mine = B.ents.filter((e) => e.alive && e.side === 1);
    const front = enemies.reduce((m, e) => Math.min(m, e.x), 1e9);
    // hero
    if (B.hero && !B.hero.called && B.hero.charge >= B.hero.need && (front < 1500 || B.t > 45)) input.hero(B);
    // abilities
    for (const a of B.abilities) {
      if (a.cd > 0) continue;
      if (a.id === "ember_rain") {
        let bestX = 0, bestN = 0;
        for (const e of enemies) { const n = enemies.filter((o) => Math.abs(o.x - e.x) < 150).length + (e.kind === "boss" ? 4 : 0); if (n > bestN) { bestN = n; bestX = e.x; } }
        if (bestN >= 4) input.ability(B, a.id, bestX);
      } else if (a.id === "rally") {
        const engaged = mine.filter((m) => m.state === "attack").length;
        if (engaged >= 3) input.ability(B, a.id, 0);
      }
    }
    // ballista: shoot the closest threat, with aim error that shrinks with skill
    if (B.ballista.reload <= 0 && enemies.length) {
      const tgt = enemies.reduce((a, b) => (a.x < b.x ? a : b));
      const lead = tgt.s.speed * 1.0 * (tgt.state === "walk" ? -1 : 0);
      const err = (B.rand() - 0.5) * 2 * (1 - skill) * 170;       // an average thumb misses the pack about a third of the time
      const shot = solveShot(B, tgt.x + lead + err, 32 + B.rand() * 14);
      input.fire(B, shot.vx, shot.vy);
    }
    // sending: fill the composition, cheapest-needed when embers are capped
    const count = {};
    for (const m of mine) count[m.s.baseSprite || m.id] = (count[m.s.baseSprite || m.id] || 0) + 1;
    // anyone the bot has none of on the beach comes first (in a random order), then the most under-filled role
    const ranked = B.cards.map((c) => ({ c, need: count[c.id] ? count[c.id] / (WANT[c.id] || 1) : -1 + B.rand() * 0.5 })).sort((a, b) => a.need - b.need);
    const threat = front < 900;
    for (const { c } of ranked) {
      if (threat && c.id !== "ashguard" && c.id !== "cinder_runner" && canSend(B, "ashguard") && (count.ashguard || 0) < 1) { input.send(B, "ashguard"); break; }
      if (canSend(B, c.id)) { input.send(B, c.id); break; }
      if (B.energy < B.energyMax * 0.95) break;   // save up for the unit we want most
    }
  };
}
