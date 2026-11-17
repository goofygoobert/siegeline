// Find each stage's enemy power so an average, unupgraded test player hits the target win rate.
// Writes "power" (and "bossPower" for the boss stage) into data/stages/r1.json.
import { loadContent } from "./content_node.mjs";
import { createBattle, step } from "../src/sim/battle.js";
import { makeBot } from "../src/sim/bot.js";
import { readFileSync, writeFileSync } from "node:fs";
const C = loadContent();
const TARGET = { r1s1: 0.97, r1s2: 0.88, r1s3: 0.75, r1s4: 0.62, r1s5: 0.5, r1boss: 0.3 };
const N = 60;
const lv = {}; for (const u of C.units.units) lv[u.id] = 1;
const prog = { unitLevels: lv, keep: 1, ballista: 1, energyMax: 1, energyRegen: 1, hero: 1, abilities: {} };
function rate(st) {
  let w = 0;
  for (let i = 0; i < N; i++) { const B = createBattle(C, st, prog, 5000 + i * 104729); const bot = makeBot({ skill: 0.6 });
    while (!B.result && B.t < 900) { bot(B); step(B); B.events.length = 0; } if (B.result === "win") w++; }
  return w / N;
}
const file = JSON.parse(readFileSync("data/stages/r1.json", "utf8"));
for (const st of file.stages) {
  if (process.argv[2] && st.id !== process.argv[2]) continue;
  const key = st.boss ? "bossPower" : "power";
  if (st.boss && !st.power) st.power = file.stages.find((s) => s.id === "r1s5").power || 1;
  let lo = 0.5, hi = 16;
  for (let it = 0; it < 10; it++) {
    const mid = Math.sqrt(lo * hi); st[key] = +mid.toFixed(2);
    const r = rate(st);
    if (r > TARGET[st.id]) lo = mid; else hi = mid;
    process.stderr.write(`${st.id} ${key}=${mid.toFixed(2)} win=${(r * 100).toFixed(0)}%\n`);
  }
  st[key] = +Math.sqrt(lo * hi).toFixed(2);
  console.log(st.id, key, st[key], "win", rate(st));
}
writeFileSync("data/stages/r1.json", JSON.stringify(file, null, 1));
