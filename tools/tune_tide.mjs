// Black Tide tuning: for each stage find the tide strength factor at which an average player whose crew, fort and
// cannon are level 5 wins about half the time. Prints suggested data/stages/r1.json "tide.power" values.
import { loadContent } from "./content_node.mjs";
import { createBattle, step } from "../src/sim/battle.js";
import { makeBot } from "../src/sim/bot.js";
import { kit, ROSTER, tideOf } from "./loadouts.mjs";
const C = loadContent(), LV = 5, N = +(process.argv[2] || 24), TARGET = 0.5;
function rate(st0, k, f) {
  const st = tideOf({ ...st0, tide: { ...st0.tide, power: f } }), crew = ROSTER.stages[k].right.slice(0, st.slots), lv = {};
  for (const u of crew) lv[u] = LV;
  let w = 0;
  for (let i = 0; i < N; i++) {
    const B = createBattle(C, { ...st, available: crew, hero: !st.noCaptain, abilities: kit(7).abilities }, { unitLevels: lv, keep: LV, ballista: LV, abilities: { ember_rain: 3, rally: 3 }, hero: 3 }, 9 + i * 7919);
    const bot = makeBot({ skill: 0.6 }); while (!B.result && B.t < 900) { bot(B); step(B); B.events.length = 0; } if (B.result === "win") w++;
  }
  return w / N;
}
const out = {};
for (const [k, st] of C.stages.entries()) {
  let lo = 0.4, hi = 3;
  for (let it = 0; it < 7; it++) { const m = Math.sqrt(lo * hi); if (rate(st, k, m) >= TARGET) lo = m; else hi = m; }
  out[st.id] = +lo.toFixed(2); console.log(st.id, st.tide.mods.join("+"), "tide factor", lo.toFixed(2), "win", Math.round(rate(st, k, lo) * 100) + "%");
}
console.log(JSON.stringify(out));
