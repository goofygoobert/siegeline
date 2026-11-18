// Headless balance: every stage x skill x upgrade profile, many seeds. Writes docs/balance-latest.md (tables).
import { loadContent } from "./content_node.mjs";
import { createBattle, step, stars } from "../src/sim/battle.js";
import { makeBot } from "../src/sim/bot.js";
import { writeFileSync } from "node:fs";
import { withLoadout, right } from "./loadouts.mjs";

const C = loadContent();
const N = +(process.argv[2] || 100);
const PROFILES = {
  none: { u: 1, keep: 1, ballista: 1, energyMax: 1, energyRegen: 1, hero: 1, ab: 1 },
  light: { u: 2, keep: 2, ballista: 2, energyMax: 1, energyRegen: 1, hero: 1, ab: 1 },
  modest: { u: 3, keep: 3, ballista: 3, energyMax: 2, energyRegen: 2, hero: 2, ab: 2 },
  strong: { u: 6, keep: 6, ballista: 6, energyMax: 4, energyRegen: 4, hero: 5, ab: 5 },
};
const SKILLS = { sloppy: 0.35, average: 0.6, sharp: 0.9 };
function prog(p) {
  const lv = {}; for (const u of C.units.units) lv[u.id] = p.u;
  return { unitLevels: lv, keep: p.keep, ballista: p.ballista, energyMax: p.energyMax, energyRegen: p.energyRegen, hero: p.hero, abilities: { ember_rain: p.ab, rally: p.ab } };
}
const rows = [];
const t0 = Date.now();
const only = process.argv[3];
for (const st of C.stages) {
  if (only && st.id !== only) continue;
  for (const [pn, p] of Object.entries(PROFILES)) for (const [sn, sk] of Object.entries(SKILLS)) {
    let w = 0, tsum = 0, hp = 0, s3 = 0, sall = 0;
    for (let i = 0; i < N; i++) {
      const k = C.stages.indexOf(st); const B = createBattle(C, withLoadout(st, k, right(k)), prog(p), 1000 + i * 7919); const bot = makeBot({ skill: sk });
      while (!B.result && B.t < 900) { bot(B); step(B); B.events.length = 0; }
      if (B.result === "win") { w++; tsum += B.t; hp += B.keep.hp / B.keep.max; const s = stars(B); sall += s; if (s === 3) s3++; }
    }
    rows.push({ st: st.id, pn, sn, win: w / N, t: w ? tsum / w : 0, hp: w ? hp / w : 0, s3: s3 / N, stars: w ? sall / w : 0 });
  }
  process.stderr.write(`${st.id} done ${((Date.now() - t0) / 1000).toFixed(0)}s\n`);
}
const pct = (x) => Math.round(x * 100) + "%";
let md = `Each stage played with its intended loadout (data/design/roster.json). Runs per cell: ${N}. Skill = bot reaction speed and aim error (sloppy 0.35, average 0.6, sharp 0.9). Profiles: none = all level 1; light = units 2, keep/ballista 2; modest = units 3, keep/ballista 3, ember 2/2, hero 2, powers 2; strong = units 6, keep/ballista 6, ember 4/4, hero 5, powers 5.\n\n`;
md += "| Stage | Upgrades | Sloppy win | Average win | Sharp win | Avg win time (average) | Keep HP left (average) | 3-star rate (average) |\n|---|---|---|---|---|---|---|---|\n";
for (const st of C.stages) for (const pn of Object.keys(PROFILES)) {
  const r = (sn) => rows.find((x) => x.st === st.id && x.pn === pn && x.sn === sn); if (!r("average")) continue;
  md += `| ${st.id} | ${pn} | ${pct(r("sloppy").win)} | ${pct(r("average").win)} | ${pct(r("sharp").win)} | ${r("average").t.toFixed(0)} s (par ${st.par}) | ${pct(r("average").hp)} | ${pct(r("average").s3)} |\n`;
}
writeFileSync("docs/balance-latest.md", md);
console.log(md);
console.error(`total ${((Date.now() - t0) / 1000).toFixed(0)}s`);
