// For each stage: find the stage power at which the intended loadout wins ~TARGET of the time (average bot, no
// upgrades), then report how the listed wrong loadout does at that power. Prints suggested powers; writes nothing.
// usage: node tools/tune_loadouts.mjs [N=40] [stageId]
import { loadContent } from "./content_node.mjs";
import { createBattle, step } from "../src/sim/battle.js";
import { makeBot } from "../src/sim/bot.js";
import { readFileSync } from "node:fs";
const R = JSON.parse(readFileSync(new URL("../data/design/roster.json", import.meta.url)));
const C = loadContent(); const N = +(process.argv[2] || 40), only = process.argv[3], TARGET = 0.85;
import { kit } from "./loadouts.mjs";
function rate(st, k, lo, mul) {
  let w = 0;
  for (let i = 0; i < N; i++) {
    const s = { ...st, available: lo, ...kit(k), power: st.power * mul, bossPower: (st.bossPower || 1) * mul };
    const B = createBattle(C, s, {}, 500 + i * 7919); const bot = makeBot({ skill: 0.6 });
    while (!B.result && B.t < 900) { bot(B); step(B); B.events.length = 0; }
    if (B.result === "win") w++;
  }
  return w / N;
}
for (const [k, st] of C.stages.entries()) {
  if (only && st.id !== only) continue;
  const plan = R.stages[k]; let lo = 0.3, hi = 3;
  for (let it = 0; it < 7; it++) { const m = Math.sqrt(lo * hi); if (rate(st, k, plan.right, m) >= TARGET) lo = m; else hi = m; }
  const m = lo, r = rate(st, k, plan.right, m), w = rate(st, k, plan.wrongIds, m), wall = rate(st, k, ["ashguard"], m);
  console.log(`${st.id}: power ${st.power} x${m.toFixed(2)} = ${(st.power * m).toFixed(2)}${st.bossPower ? " boss " + (st.bossPower * m).toFixed(2) : ""}  right ${Math.round(r * 100)}%  wrong ${Math.round(w * 100)}%  hatchguards-only ${Math.round(wall * 100)}%`);
}
