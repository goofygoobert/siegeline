// Sim tests: determinism, every stage can end, bot can win stage 1 with no upgrades.
import { loadContent } from "./content_node.mjs";
import { createBattle, step } from "../src/sim/battle.js";
import { makeBot } from "../src/sim/bot.js";
import { withLoadout, right } from "./loadouts.mjs";

const C = loadContent();
let fail = 0;
const ok = (c, m) => { if (!c) { fail++; console.log("FAIL", m); } else console.log("ok  ", m); };

function run(stage, seed, prog = {}, skill = 0.7, maxT = 600) {
  const k = C.stages.indexOf(stage);
  const B = createBattle(C, withLoadout(stage, k, right(k)), prog, seed); const bot = makeBot({ skill });
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
// save migration: a version-2 save from the six-stage region loads with its progress moved, nothing lost
{
  const { unwrap } = await import("../src/save/save.js");
  const body = JSON.stringify({ marks: 777, stages: { r1s1: { stars: [true, true, false], best: 90, clears: 2 }, r1s2: { stars: [true, false, false], best: 120, clears: 1 },
    r1s3: { stars: [true, true, true], best: 100, clears: 1 }, r1s4: { stars: [true, false, false], best: 150, clears: 1 } },
    unitLevels: { ashguard: 4, torchbow: 3, cinder_runner: 2, maulwright: 1, bellringer: 1, lamplighter: 1 }, unlocked: { units: ["ashguard", "torchbow", "cinder_runner", "maulwright", "bellringer", "lamplighter"], hero: true, abilities: ["ember_rain", "rally"] } });
  let h = 2166136261; for (let i = 0; i < body.length; i++) { h ^= body.charCodeAt(i); h = Math.imul(h, 16777619); }
  const r = unwrap(JSON.stringify({ v: 2, ts: 1, sum: (h >>> 0).toString(36), data: body }));
  const d = r.data;
  ok(!r.error && d.marks === 777 && d.unitLevels.ashguard === 4 && d.unlocked.units.length === 6, "v2 save loads: doubloons, levels and crew kept");
  ok(d.stages.r1s5 && d.stages.r1s5.stars[2] && !d.stages.r1s3 && d.stages.r1s4.clears === 1 && d.stages.r1s1.clears === 2, "v2 stage progress moves to the matching new stage (old 3 -> new 5)");
  ok(Array.isArray(d.tavern) && d.loadouts && d.skills, "v3 fields added to old saves");
}
const t0 = Date.now(); let ticks = 0;
for (let i = 0; i < 5; i++) { const B = run(C.stages[4], 900 + i); ticks += B.tick; }
const ms = Date.now() - t0;
ok(true, `speed: ${(ticks / 30 / (ms / 1000)).toFixed(0)}x real time headless`);
process.exit(fail ? 1 : 0);
