// Sim tests: determinism, every stage can end, bot can win stage 1 with no upgrades.
import { loadContent } from "./content_node.mjs";
import { createBattle, step } from "../src/sim/battle.js";
import { makeBot } from "../src/sim/bot.js";

const C = loadContent();
let fail = 0;
const ok = (c, m) => { if (!c) { fail++; console.log("FAIL", m); } else console.log("ok  ", m); };

function run(stage, seed, prog = {}, skill = 0.7, maxT = 600) {
  const B = createBattle(C, stage, prog, seed); const bot = makeBot({ skill });
  while (!B.result && B.t < maxT) { bot(B); step(B); B.events.length = 0; }
  return B;
}

const s1 = C.stages[0];
const a = run(s1, 42), b = run(s1, 42);
ok(a.t === b.t && a.result === b.result && a.keep.hp === b.keep.hp, `deterministic (${a.result} at ${a.t.toFixed(1)}s both runs)`);
let wins = 0; for (let i = 0; i < 20; i++) if (run(s1, 100 + i).result === "win") wins++;
ok(wins >= 14, `stage 1 winnable with no upgrades (bot won ${wins}/20)`);
for (const st of C.stages) {
  const B = run(st, 7, {}, 0.7, 900);
  ok(!!B.result, `${st.id} ends (${B.result || "none"} at ${B.t.toFixed(0)}s, kills ${B.stats.kills})`);
}
const t0 = Date.now(); let ticks = 0;
for (let i = 0; i < 5; i++) { const B = run(C.stages[4], 900 + i); ticks += B.tick; }
const ms = Date.now() - t0;
ok(true, `speed: ${(ticks / 30 / (ms / 1000)).toFixed(0)}x real time headless`);
process.exit(fail ? 1 : 0);
